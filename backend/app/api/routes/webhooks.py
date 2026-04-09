from __future__ import annotations

import re
from urllib.parse import unquote
from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session
from app.api.deps import db_session
from app.core.config import get_settings
from app.models.monitored_mailbox import MonitoredMailbox
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.mailbox_repository import MailboxRepository
from app.repositories.webhook_log_repository import WebhookLogRepository
from app.workers.tasks import process_graph_mail_event

router = APIRouter()

GRAPH_RESOURCE_PATTERN = re.compile(
    r"users(?:\('([^']+)'\)|/([^/]+)).*?messages(?:\('([^']+)'\)|/([^/?]+))",
    re.IGNORECASE,
)


def _extract_graph_user_and_message(resource: str) -> tuple[str | None, str | None]:
    normalized_resource = unquote((resource or '').strip())
    match = GRAPH_RESOURCE_PATTERN.search(normalized_resource)
    if not match:
        return None, None

    user_identifier = match.group(1) or match.group(2)
    message_id = match.group(3) or match.group(4)

    if user_identifier:
        user_identifier = unquote(user_identifier.strip())
    if message_id:
        message_id = unquote(message_id.strip())
    return user_identifier, message_id


def _iter_graph_notifications(payload: dict) -> list[dict]:
    value = payload.get('value')
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]

    # Backward compatibility for existing internal payload format.
    if all(key in payload for key in ('mailbox_id', 'mailbox_email', 'message_id')):
        return [payload]
    return []


def _resolve_mailbox_for_graph_user(user_identifier: str, mailboxes: list[MonitoredMailbox]) -> MonitoredMailbox | None:
    normalized = unquote((user_identifier or '').strip()).lower()
    if not normalized:
        return None

    for mailbox in mailboxes:
        if mailbox.email.lower() == normalized:
            return mailbox

    for mailbox in mailboxes:
        if mailbox.graph_user_id and mailbox.graph_user_id.lower() == normalized:
            return mailbox

    return None


def _verify_client_state(client_state: str | None) -> bool:
    expected_client_state = get_settings().graph_webhook_client_state.strip()
    if not expected_client_state:
        return True
    return bool(client_state and client_state == expected_client_state)


def _queue_graph_event(db: Session, mailbox: MonitoredMailbox, message_id: str, source_payload: dict) -> None:
    WebhookLogRepository(db).create(
        event_type='graph_mail_event',
        payload=source_payload,
        status='queued',
        error_message=None,
    )
    AuditLogRepository(db).create(
        module_name='webhook',
        action_name='graph_event_received',
        payload={
            'mailbox_id': mailbox.id,
            'mailbox_email': mailbox.email,
            'message_id': message_id,
        },
        result='queued',
    )
    process_graph_mail_event.delay(mailbox_id=mailbox.id, mailbox_email=mailbox.email, message_id=message_id)


def _mark_ignored(db: Session, payload: dict, reason: str) -> None:
    WebhookLogRepository(db).create(
        event_type='graph_mail_event',
        payload=payload,
        status='ignored',
        error_message=reason,
    )
    AuditLogRepository(db).create(
        module_name='webhook',
        action_name='graph_event_ignored',
        payload=payload,
        result=reason,
    )


@router.get('/graph')
async def graph_validation(validationToken: str = Query(alias='validationToken')) -> Response:  # noqa: N803
    return Response(content=validationToken, media_type='text/plain')


@router.post('/graph', status_code=status.HTTP_202_ACCEPTED)
async def graph_webhook(request: Request, db: Session = Depends(db_session)) -> dict[str, int | str]:
    payload = await request.json()
    notifications = _iter_graph_notifications(payload)
    mailboxes = MailboxRepository(db).list_active()

    queued = 0
    ignored = 0

    if not notifications:
        _mark_ignored(db, payload, 'empty_or_unsupported_payload')
        return {'status': 'accepted', 'queued': 0, 'ignored': 1}

    for notification in notifications:
        # Backward compatibility path.
        if all(key in notification for key in ('mailbox_id', 'mailbox_email', 'message_id')):
            mailbox_id = int(notification.get('mailbox_id', 0))
            mailbox = MailboxRepository(db).get(mailbox_id)
            message_id = str(notification.get('message_id', '')).strip()
            if not mailbox or not message_id:
                _mark_ignored(db, notification, 'invalid_legacy_payload')
                ignored += 1
                continue
            _queue_graph_event(db, mailbox, message_id, notification)
            queued += 1
            continue

        change_type = str(notification.get('changeType', '')).lower()
        if change_type and change_type != 'created':
            _mark_ignored(db, notification, 'unsupported_change_type')
            ignored += 1
            continue

        client_state = notification.get('clientState')
        if not _verify_client_state(client_state):
            _mark_ignored(db, notification, 'invalid_client_state')
            ignored += 1
            continue

        resource = str(notification.get('resource', ''))
        user_identifier, message_id = _extract_graph_user_and_message(resource)

        resource_data = notification.get('resourceData')
        if isinstance(resource_data, dict):
            if not message_id:
                message_id = str(resource_data.get('id', '')).strip() or None
            if not user_identifier:
                odata_id = str(resource_data.get('@odata.id', '')).strip()
                if odata_id:
                    user_identifier, _ = _extract_graph_user_and_message(odata_id)

        if not user_identifier or not message_id:
            _mark_ignored(db, notification, 'unable_to_extract_graph_message_identity')
            ignored += 1
            continue

        mailbox = _resolve_mailbox_for_graph_user(user_identifier=user_identifier, mailboxes=mailboxes)
        if not mailbox:
            _mark_ignored(db, notification, f'mailbox_not_found:{user_identifier}')
            ignored += 1
            continue

        _queue_graph_event(db, mailbox, message_id, notification)
        queued += 1

    return {'status': 'accepted', 'queued': queued, 'ignored': ignored}
