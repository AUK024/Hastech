from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.audit import safe_audit_log
from app.api.deps import db_session, resolve_tenant_code
from app.repositories.graph_subscription_repository import GraphSubscriptionRepository
from app.repositories.mailbox_repository import MailboxRepository
from app.schemas.common import MessageResponse
from app.schemas.monitored_mailbox import MonitoredMailboxCreate, MonitoredMailboxRead, MonitoredMailboxUpdate

router = APIRouter()


@router.get('/', response_model=list[MonitoredMailboxRead])
def list_mailboxes(db: Session = Depends(db_session), tenant_code: str = Depends(resolve_tenant_code)):
    return MailboxRepository(db).list(tenant_code=tenant_code)


@router.get('/{mailbox_id}', response_model=MonitoredMailboxRead)
def get_mailbox(mailbox_id: int, db: Session = Depends(db_session), tenant_code: str = Depends(resolve_tenant_code)):
    obj = MailboxRepository(db).get(mailbox_id, tenant_code=tenant_code)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Mailbox not found')
    return obj


@router.post('/', response_model=MonitoredMailboxRead, status_code=status.HTTP_201_CREATED)
def create_mailbox(
    payload: MonitoredMailboxCreate,
    db: Session = Depends(db_session),
    tenant_code: str = Depends(resolve_tenant_code),
):
    created = MailboxRepository(db).create(payload, tenant_code=tenant_code)
    safe_audit_log(
        db,
        tenant_code=tenant_code,
        module_name='mailboxes',
        action_name='create_mailbox',
        payload={'mailbox_id': created.id, 'email': created.email},
        result='success',
    )
    return created


@router.put('/{mailbox_id}', response_model=MonitoredMailboxRead)
def update_mailbox(
    mailbox_id: int,
    payload: MonitoredMailboxUpdate,
    db: Session = Depends(db_session),
    tenant_code: str = Depends(resolve_tenant_code),
):
    repo = MailboxRepository(db)
    obj = repo.get(mailbox_id, tenant_code=tenant_code)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Mailbox not found')
    updated = repo.update(obj, payload)
    safe_audit_log(
        db,
        tenant_code=tenant_code,
        module_name='mailboxes',
        action_name='update_mailbox',
        payload={'mailbox_id': updated.id, 'email': updated.email},
        result='success',
    )
    return updated


@router.delete('/{mailbox_id}', response_model=MessageResponse)
def delete_mailbox(
    mailbox_id: int,
    db: Session = Depends(db_session),
    tenant_code: str = Depends(resolve_tenant_code),
):
    repo = MailboxRepository(db)
    obj = repo.get(mailbox_id, tenant_code=tenant_code)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Mailbox not found')
    GraphSubscriptionRepository(db).delete_by_mailbox_id(mailbox_id, tenant_code=tenant_code)
    repo.delete(obj)
    safe_audit_log(
        db,
        tenant_code=tenant_code,
        module_name='mailboxes',
        action_name='delete_mailbox',
        payload={'mailbox_id': mailbox_id, 'email': obj.email},
        result='success',
    )
    return {'message': 'Mailbox deleted'}
