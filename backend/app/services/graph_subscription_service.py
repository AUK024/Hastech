from __future__ import annotations

from datetime import datetime, timedelta, timezone
from app.core.config import get_settings
from app.integrations.microsoft_graph.client import GraphClient
from app.models.graph_subscription import GraphSubscription
from app.models.monitored_mailbox import MonitoredMailbox
from app.repositories.graph_subscription_repository import GraphSubscriptionRepository
from app.repositories.mailbox_repository import MailboxRepository
from app.schemas.graph_subscription import GraphSubscriptionCreate, GraphSubscriptionUpdate


class GraphSubscriptionService:
    def __init__(self, db, graph_client: GraphClient) -> None:
        self.db = db
        self.graph_client = graph_client
        self.settings = get_settings()
        self.mailbox_repo = MailboxRepository(db)
        self.subscription_repo = GraphSubscriptionRepository(db)

    @staticmethod
    def _utcnow() -> datetime:
        return datetime.now(timezone.utc)

    def _requested_expiration(self) -> datetime:
        requested_minutes = int(self.settings.graph_subscription_expiry_minutes)
        bounded_minutes = max(15, min(requested_minutes, 4230))
        return self._utcnow() + timedelta(minutes=bounded_minutes)

    def _renew_threshold_minutes(self, override: int | None = None) -> int:
        if override is not None:
            return max(1, override)
        configured = int(self.settings.graph_subscription_renew_threshold_minutes)
        return max(1, configured)

    @staticmethod
    def _parse_graph_datetime(raw_value: str | None) -> datetime | None:
        if not raw_value:
            return None
        normalized = str(raw_value).strip().replace('Z', '+00:00')
        try:
            return datetime.fromisoformat(normalized)
        except ValueError:
            return None

    def _notification_url(self) -> str:
        configured = self.settings.graph_webhook_notification_url.strip()
        if configured:
            return configured
        return f'http://localhost:8000{self.settings.api_prefix}/webhooks/graph'

    def _lifecycle_notification_url(self) -> str | None:
        configured = self.settings.graph_webhook_lifecycle_url.strip()
        return configured or None

    @staticmethod
    def _mailbox_resource(mailbox: MonitoredMailbox) -> str:
        principal = (mailbox.graph_user_id or mailbox.email).strip()
        return f'users/{principal}/messages'

    def _require_active_mailbox(self, mailbox_id: int, tenant_code: str = 'default') -> MonitoredMailbox:
        mailbox = self.mailbox_repo.get(mailbox_id, tenant_code=tenant_code)
        if not mailbox:
            raise LookupError('Mailbox not found')
        if not mailbox.is_active:
            raise RuntimeError('Mailbox is inactive')
        return mailbox

    def _upsert_from_graph_response(
        self,
        *,
        mailbox: MonitoredMailbox,
        graph_payload: dict,
        requested_expiration: datetime,
        resource: str,
        notification_url: str,
        lifecycle_notification_url: str | None,
        client_state: str | None,
    ) -> GraphSubscription:
        existing = self.subscription_repo.get_by_mailbox_id(mailbox.id, tenant_code=mailbox.tenant_code)
        graph_subscription_id = str(graph_payload.get('id', '')).strip() or (existing.graph_subscription_id if existing else None)
        resolved_resource = str(graph_payload.get('resource', '')).strip() or resource
        resolved_change_type = str(graph_payload.get('changeType', '')).strip() or 'created'
        expires_at = self._parse_graph_datetime(graph_payload.get('expirationDateTime')) or requested_expiration
        last_renewed_at = self._utcnow()

        if existing:
            return self.subscription_repo.update(
                existing,
                GraphSubscriptionUpdate(
                    graph_subscription_id=graph_subscription_id,
                    resource=resolved_resource,
                    change_type=resolved_change_type,
                    notification_url=notification_url,
                    lifecycle_notification_url=lifecycle_notification_url,
                    client_state=client_state,
                    expiration_datetime=expires_at,
                    is_active=True,
                    last_renewed_at=last_renewed_at,
                    error_message=None,
                ),
            )

        return self.subscription_repo.create(
            GraphSubscriptionCreate(
                tenant_code=mailbox.tenant_code,
                mailbox_id=mailbox.id,
                graph_subscription_id=graph_subscription_id,
                resource=resolved_resource,
                change_type=resolved_change_type,
                notification_url=notification_url,
                lifecycle_notification_url=lifecycle_notification_url,
                client_state=client_state,
                expiration_datetime=expires_at,
                is_active=True,
                last_renewed_at=last_renewed_at,
                error_message=None,
            )
        )

    def _save_error(self, mailbox_id: int, message: str, tenant_code: str = 'default') -> None:
        existing = self.subscription_repo.get_by_mailbox_id(mailbox_id, tenant_code=tenant_code)
        if existing:
            self.subscription_repo.update(
                existing,
                GraphSubscriptionUpdate(
                    is_active=False,
                    error_message=message[:4000],
                    last_renewed_at=self._utcnow(),
                ),
            )

    def subscribe_mailbox(
        self,
        mailbox_id: int,
        force_recreate: bool = False,
        tenant_code: str = 'default',
    ) -> GraphSubscription:
        mailbox = self._require_active_mailbox(mailbox_id, tenant_code=tenant_code)
        existing = self.subscription_repo.get_by_mailbox_id(mailbox.id, tenant_code=mailbox.tenant_code)

        requested_expiration = self._requested_expiration()
        notification_url = self._notification_url()
        lifecycle_notification_url = self._lifecycle_notification_url()
        client_state = self.settings.graph_webhook_client_state.strip() or None
        resource = self._mailbox_resource(mailbox)

        try:
            if existing and existing.graph_subscription_id and force_recreate:
                self.graph_client.delete_subscription(existing.graph_subscription_id)
                self.subscription_repo.update(
                    existing,
                    GraphSubscriptionUpdate(
                        graph_subscription_id=None,
                        expiration_datetime=None,
                        is_active=False,
                        error_message=None,
                    ),
                )
                existing = self.subscription_repo.get_by_mailbox_id(mailbox.id, tenant_code=mailbox.tenant_code)

            if existing and existing.graph_subscription_id and existing.is_active and not force_recreate:
                graph_payload = self.graph_client.renew_subscription(
                    existing.graph_subscription_id,
                    requested_expiration,
                )
                if not graph_payload.get('resource'):
                    graph_payload['resource'] = existing.resource or resource
                if not graph_payload.get('changeType'):
                    graph_payload['changeType'] = existing.change_type or 'created'
            else:
                graph_payload = self.graph_client.create_message_subscription(
                    resource=resource,
                    notification_url=notification_url,
                    expiration_datetime=requested_expiration,
                    client_state=client_state,
                    lifecycle_notification_url=lifecycle_notification_url,
                    change_type='created',
                )

            return self._upsert_from_graph_response(
                mailbox=mailbox,
                graph_payload=graph_payload,
                requested_expiration=requested_expiration,
                resource=resource,
                notification_url=notification_url,
                lifecycle_notification_url=lifecycle_notification_url,
                client_state=client_state,
            )
        except Exception as exc:
            self._save_error(mailbox_id, str(exc), tenant_code=mailbox.tenant_code)
            raise

    def renew_mailbox(self, mailbox_id: int, tenant_code: str = 'default') -> GraphSubscription:
        mailbox = self._require_active_mailbox(mailbox_id, tenant_code=tenant_code)
        existing = self.subscription_repo.get_by_mailbox_id(mailbox.id, tenant_code=mailbox.tenant_code)
        if not existing or not existing.graph_subscription_id:
            raise LookupError('Active subscription not found for mailbox')

        requested_expiration = self._requested_expiration()
        try:
            graph_payload = self.graph_client.renew_subscription(
                existing.graph_subscription_id,
                requested_expiration,
            )
            if not graph_payload.get('resource'):
                graph_payload['resource'] = existing.resource
            if not graph_payload.get('changeType'):
                graph_payload['changeType'] = existing.change_type
            return self._upsert_from_graph_response(
                mailbox=mailbox,
                graph_payload=graph_payload,
                requested_expiration=requested_expiration,
                resource=existing.resource,
                notification_url=existing.notification_url,
                lifecycle_notification_url=existing.lifecycle_notification_url,
                client_state=existing.client_state,
            )
        except Exception as exc:
            self._save_error(mailbox_id, str(exc), tenant_code=mailbox.tenant_code)
            raise

    def unsubscribe_mailbox(self, mailbox_id: int, tenant_code: str = 'default') -> GraphSubscription:
        existing = self.subscription_repo.get_by_mailbox_id(mailbox_id, tenant_code=tenant_code)
        if not existing:
            raise LookupError('Subscription not found for mailbox')

        if existing.graph_subscription_id:
            self.graph_client.delete_subscription(existing.graph_subscription_id)

        return self.subscription_repo.update(
            existing,
            GraphSubscriptionUpdate(
                graph_subscription_id=None,
                expiration_datetime=None,
                is_active=False,
                error_message=None,
                last_renewed_at=self._utcnow(),
            ),
        )

    def sync_active_mailboxes(self, force_recreate: bool = False, tenant_code: str = 'default') -> dict:
        active_mailboxes = self.mailbox_repo.list_active(tenant_code=tenant_code)
        results: list[dict] = []

        for mailbox in active_mailboxes:
            try:
                subscription = self.subscribe_mailbox(
                    mailbox.id,
                    force_recreate=force_recreate,
                    tenant_code=tenant_code,
                )
                results.append(
                    {
                        'mailbox_id': mailbox.id,
                        'mailbox_email': mailbox.email,
                        'status': 'ok',
                        'error': None,
                        'subscription_id': subscription.graph_subscription_id,
                        'expiration_datetime': subscription.expiration_datetime,
                    }
                )
            except Exception as exc:
                results.append(
                    {
                        'mailbox_id': mailbox.id,
                        'mailbox_email': mailbox.email,
                        'status': 'error',
                        'error': str(exc),
                        'subscription_id': None,
                        'expiration_datetime': None,
                    }
                )

        success_count = sum(1 for row in results if row['status'] == 'ok')
        return {
            'total': len(results),
            'success': success_count,
            'failed': len(results) - success_count,
            'results': results,
        }

    def renew_due(self, within_minutes: int | None = None, tenant_code: str = 'default') -> dict:
        threshold_minutes = self._renew_threshold_minutes(within_minutes)
        renew_before = self._utcnow() + timedelta(minutes=threshold_minutes)
        due_items = self.subscription_repo.list_due_for_renewal(renew_before, tenant_code=tenant_code)
        mailbox_lookup = {mailbox.id: mailbox for mailbox in self.mailbox_repo.list(tenant_code=tenant_code)}

        results: list[dict] = []
        for item in due_items:
            mailbox = mailbox_lookup.get(item.mailbox_id)
            mailbox_email = mailbox.email if mailbox else f'mailbox:{item.mailbox_id}'
            try:
                renewed = self.renew_mailbox(item.mailbox_id, tenant_code=tenant_code)
                results.append(
                    {
                        'mailbox_id': item.mailbox_id,
                        'mailbox_email': mailbox_email,
                        'status': 'ok',
                        'error': None,
                        'subscription_id': renewed.graph_subscription_id,
                        'expiration_datetime': renewed.expiration_datetime,
                    }
                )
            except Exception as exc:
                results.append(
                    {
                        'mailbox_id': item.mailbox_id,
                        'mailbox_email': mailbox_email,
                        'status': 'error',
                        'error': str(exc),
                        'subscription_id': item.graph_subscription_id,
                        'expiration_datetime': item.expiration_datetime,
                    }
                )

        success_count = sum(1 for row in results if row['status'] == 'ok')
        return {
            'total': len(results),
            'success': success_count,
            'failed': len(results) - success_count,
            'results': results,
        }
