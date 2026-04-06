from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session
from app.api.deps import db_session
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.webhook_log_repository import WebhookLogRepository
from app.workers.tasks import process_graph_mail_event

router = APIRouter()


@router.get('/graph')
async def graph_validation(validationToken: str = Query(alias='validationToken')) -> Response:  # noqa: N803
    return Response(content=validationToken, media_type='text/plain')


@router.post('/graph', status_code=status.HTTP_202_ACCEPTED)
async def graph_webhook(request: Request, db: Session = Depends(db_session)) -> dict[str, str]:
    payload = await request.json()
    mailbox_id = int(payload.get('mailbox_id', 0))
    mailbox_email = payload.get('mailbox_email', '')
    message_id = payload.get('message_id', '')

    WebhookLogRepository(db).create(event_type='graph_mail_event', payload=payload, status='queued', error_message=None)
    AuditLogRepository(db).create(module_name='webhook', action_name='graph_event_received', payload=payload, result='queued')

    process_graph_mail_event.delay(mailbox_id=mailbox_id, mailbox_email=mailbox_email, message_id=message_id)
    return {'status': 'queued'}
