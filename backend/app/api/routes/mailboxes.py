from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import db_session
from app.repositories.mailbox_repository import MailboxRepository
from app.schemas.common import MessageResponse
from app.schemas.monitored_mailbox import MonitoredMailboxCreate, MonitoredMailboxRead, MonitoredMailboxUpdate

router = APIRouter()


@router.get('/', response_model=list[MonitoredMailboxRead])
def list_mailboxes(db: Session = Depends(db_session)):
    return MailboxRepository(db).list()


@router.get('/{mailbox_id}', response_model=MonitoredMailboxRead)
def get_mailbox(mailbox_id: int, db: Session = Depends(db_session)):
    obj = MailboxRepository(db).get(mailbox_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Mailbox not found')
    return obj


@router.post('/', response_model=MonitoredMailboxRead, status_code=status.HTTP_201_CREATED)
def create_mailbox(payload: MonitoredMailboxCreate, db: Session = Depends(db_session)):
    return MailboxRepository(db).create(payload)


@router.put('/{mailbox_id}', response_model=MonitoredMailboxRead)
def update_mailbox(mailbox_id: int, payload: MonitoredMailboxUpdate, db: Session = Depends(db_session)):
    repo = MailboxRepository(db)
    obj = repo.get(mailbox_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Mailbox not found')
    return repo.update(obj, payload)


@router.delete('/{mailbox_id}', response_model=MessageResponse)
def delete_mailbox(mailbox_id: int, db: Session = Depends(db_session)):
    repo = MailboxRepository(db)
    obj = repo.get(mailbox_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Mailbox not found')
    repo.delete(obj)
    return {'message': 'Mailbox deleted'}
