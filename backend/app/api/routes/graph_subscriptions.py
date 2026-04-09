from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.audit import safe_audit_log
from app.api.deps import db_session, require_admin_user, resolve_tenant_code
from app.integrations.microsoft_graph.client import GraphClient
from app.repositories.graph_subscription_repository import GraphSubscriptionRepository
from app.repositories.mailbox_repository import MailboxRepository
from app.schemas.common import MessageResponse
from app.schemas.graph_subscription import (
    GraphSubscriptionActionResult,
    GraphSubscriptionBatchResponse,
    GraphSubscriptionRead,
)
from app.services.graph_subscription_service import GraphSubscriptionService

router = APIRouter()


def _action_result(
    *,
    mailbox_id: int,
    mailbox_email: str,
    status_text: str,
    subscription_id: str | None,
    expiration_datetime,
    error: str | None = None,
) -> GraphSubscriptionActionResult:
    return GraphSubscriptionActionResult(
        mailbox_id=mailbox_id,
        mailbox_email=mailbox_email,
        status=status_text,
        error=error,
        subscription_id=subscription_id,
        expiration_datetime=expiration_datetime,
    )


@router.get('/', response_model=list[GraphSubscriptionRead])
def list_graph_subscriptions(
    db: Session = Depends(db_session),
    _: str = Depends(require_admin_user),
    tenant_code: str = Depends(resolve_tenant_code),
):
    return GraphSubscriptionRepository(db).list(tenant_code=tenant_code)


@router.post('/sync', response_model=GraphSubscriptionBatchResponse)
def sync_graph_subscriptions(
    force_recreate: bool = Query(default=False),
    db: Session = Depends(db_session),
    admin_email: str = Depends(require_admin_user),
    tenant_code: str = Depends(resolve_tenant_code),
):
    service = GraphSubscriptionService(db=db, graph_client=GraphClient())
    result = service.sync_active_mailboxes(force_recreate=force_recreate, tenant_code=tenant_code)
    safe_audit_log(
        db,
        tenant_code=tenant_code,
        module_name='graph_subscriptions',
        action_name='sync',
        payload={
            'force_recreate': force_recreate,
            'admin_email': admin_email,
            'total': result['total'],
            'success': result['success'],
            'failed': result['failed'],
        },
        result='success' if result['failed'] == 0 else 'partial',
    )
    return result


@router.post('/renew-due', response_model=GraphSubscriptionBatchResponse)
def renew_due_graph_subscriptions(
    within_minutes: int | None = Query(default=None, ge=1, le=1440),
    db: Session = Depends(db_session),
    admin_email: str = Depends(require_admin_user),
    tenant_code: str = Depends(resolve_tenant_code),
):
    service = GraphSubscriptionService(db=db, graph_client=GraphClient())
    result = service.renew_due(within_minutes=within_minutes, tenant_code=tenant_code)
    safe_audit_log(
        db,
        tenant_code=tenant_code,
        module_name='graph_subscriptions',
        action_name='renew_due',
        payload={
            'within_minutes': within_minutes,
            'admin_email': admin_email,
            'total': result['total'],
            'success': result['success'],
            'failed': result['failed'],
        },
        result='success' if result['failed'] == 0 else 'partial',
    )
    return result


@router.post('/mailboxes/{mailbox_id}/subscribe', response_model=GraphSubscriptionActionResult)
def subscribe_mailbox(
    mailbox_id: int,
    force_recreate: bool = Query(default=False),
    db: Session = Depends(db_session),
    admin_email: str = Depends(require_admin_user),
    tenant_code: str = Depends(resolve_tenant_code),
):
    service = GraphSubscriptionService(db=db, graph_client=GraphClient())
    mailbox = MailboxRepository(db).get(mailbox_id, tenant_code=tenant_code)
    mailbox_email = mailbox.email if mailbox else f'mailbox:{mailbox_id}'

    try:
        subscription = service.subscribe_mailbox(mailbox_id, force_recreate=force_recreate, tenant_code=tenant_code)
        safe_audit_log(
            db,
            tenant_code=tenant_code,
            module_name='graph_subscriptions',
            action_name='subscribe_mailbox',
            payload={'mailbox_id': mailbox_id, 'mailbox_email': mailbox_email, 'admin_email': admin_email},
            result='success',
        )
        return _action_result(
            mailbox_id=mailbox_id,
            mailbox_email=mailbox_email,
            status_text='ok',
            subscription_id=subscription.graph_subscription_id,
            expiration_datetime=subscription.expiration_datetime,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post('/mailboxes/{mailbox_id}/renew', response_model=GraphSubscriptionActionResult)
def renew_mailbox_subscription(
    mailbox_id: int,
    db: Session = Depends(db_session),
    admin_email: str = Depends(require_admin_user),
    tenant_code: str = Depends(resolve_tenant_code),
):
    service = GraphSubscriptionService(db=db, graph_client=GraphClient())
    mailbox = MailboxRepository(db).get(mailbox_id, tenant_code=tenant_code)
    mailbox_email = mailbox.email if mailbox else f'mailbox:{mailbox_id}'

    try:
        subscription = service.renew_mailbox(mailbox_id, tenant_code=tenant_code)
        safe_audit_log(
            db,
            tenant_code=tenant_code,
            module_name='graph_subscriptions',
            action_name='renew_mailbox',
            payload={'mailbox_id': mailbox_id, 'mailbox_email': mailbox_email, 'admin_email': admin_email},
            result='success',
        )
        return _action_result(
            mailbox_id=mailbox_id,
            mailbox_email=mailbox_email,
            status_text='ok',
            subscription_id=subscription.graph_subscription_id,
            expiration_datetime=subscription.expiration_datetime,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.delete('/mailboxes/{mailbox_id}', response_model=MessageResponse)
def unsubscribe_mailbox(
    mailbox_id: int,
    db: Session = Depends(db_session),
    admin_email: str = Depends(require_admin_user),
    tenant_code: str = Depends(resolve_tenant_code),
):
    service = GraphSubscriptionService(db=db, graph_client=GraphClient())
    try:
        service.unsubscribe_mailbox(mailbox_id, tenant_code=tenant_code)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    safe_audit_log(
        db,
        tenant_code=tenant_code,
        module_name='graph_subscriptions',
        action_name='unsubscribe_mailbox',
        payload={'mailbox_id': mailbox_id, 'admin_email': admin_email},
        result='success',
    )
    return {'message': 'Graph subscription removed'}
