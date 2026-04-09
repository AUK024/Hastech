from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from app.services.graph_subscription_service import GraphSubscriptionService


class FakeGraphClient:
    def __init__(self):
        self.create_calls = []
        self.renew_calls = []
        self.delete_calls = []

    def create_message_subscription(
        self,
        *,
        resource: str,
        notification_url: str,
        expiration_datetime: datetime,
        client_state: str | None = None,
        lifecycle_notification_url: str | None = None,
        change_type: str = 'created',
    ) -> dict:
        self.create_calls.append(
            {
                'resource': resource,
                'notification_url': notification_url,
                'expiration_datetime': expiration_datetime,
                'client_state': client_state,
                'lifecycle_notification_url': lifecycle_notification_url,
                'change_type': change_type,
            }
        )
        return {
            'id': f'sub-{resource.replace("/", "-")}',
            'resource': resource,
            'changeType': change_type,
            'expirationDateTime': expiration_datetime.isoformat().replace('+00:00', 'Z'),
            'clientState': client_state,
        }

    def renew_subscription(self, subscription_id: str, expiration_datetime: datetime) -> dict:
        self.renew_calls.append({'subscription_id': subscription_id, 'expiration_datetime': expiration_datetime})
        return {
            'id': subscription_id,
            'expirationDateTime': expiration_datetime.isoformat().replace('+00:00', 'Z'),
        }

    def delete_subscription(self, subscription_id: str) -> None:
        self.delete_calls.append(subscription_id)


class FakeMailboxRepo:
    def __init__(self, items: list[SimpleNamespace]):
        self.items = items

    def get(self, mailbox_id: int, tenant_code: str = 'default'):
        for item in self.items:
            if item.id == mailbox_id and getattr(item, 'tenant_code', 'default') == tenant_code:
                return item
        return None

    def list(self, tenant_code: str = 'default'):
        return [item for item in self.items if getattr(item, 'tenant_code', 'default') == tenant_code]

    def list_active(self, tenant_code: str = 'default'):
        return [
            item
            for item in self.items
            if item.is_active and getattr(item, 'tenant_code', 'default') == tenant_code
        ]


class FakeSubscriptionRepo:
    def __init__(self):
        self.rows = {}
        self.sequence = 1

    def get_by_mailbox_id(self, mailbox_id: int, tenant_code: str = 'default'):
        row = self.rows.get(mailbox_id)
        if row and getattr(row, 'tenant_code', 'default') == tenant_code:
            return row
        return None

    def create(self, data):
        payload = data.model_dump()
        obj = SimpleNamespace(id=self.sequence, **payload)
        self.sequence += 1
        self.rows[obj.mailbox_id] = obj
        return obj

    def update(self, obj, data):
        payload = data.model_dump(exclude_unset=True)
        for key, value in payload.items():
            setattr(obj, key, value)
        self.rows[obj.mailbox_id] = obj
        return obj

    def list_due_for_renewal(self, renew_before: datetime, tenant_code: str = 'default'):
        due = []
        for row in self.rows.values():
            if (
                getattr(row, 'tenant_code', 'default') == tenant_code
                and row.is_active
                and row.graph_subscription_id
                and row.expiration_datetime
                and row.expiration_datetime <= renew_before
            ):
                due.append(row)
        return due


def build_service(mailboxes: list[SimpleNamespace]) -> tuple[GraphSubscriptionService, FakeGraphClient, FakeSubscriptionRepo]:
    graph_client = FakeGraphClient()
    service = GraphSubscriptionService(db=None, graph_client=graph_client)
    service.mailbox_repo = FakeMailboxRepo(mailboxes)
    sub_repo = FakeSubscriptionRepo()
    service.subscription_repo = sub_repo
    service.settings = SimpleNamespace(
        graph_subscription_expiry_minutes=120,
        graph_subscription_renew_threshold_minutes=30,
        graph_webhook_notification_url='https://admin.hascelik.com/api/v1/webhooks/graph',
        graph_webhook_lifecycle_url='https://admin.hascelik.com/api/v1/webhooks/lifecycle',
        graph_webhook_client_state='client-state-1',
        api_prefix='/api/v1',
    )
    return service, graph_client, sub_repo


def test_subscribe_mailbox_creates_graph_subscription() -> None:
    mailbox = SimpleNamespace(id=1, tenant_code='default', email='sales@hascelik.com', graph_user_id='guid-1', is_active=True)
    service, graph_client, _ = build_service([mailbox])

    created = service.subscribe_mailbox(1)

    assert created.graph_subscription_id == 'sub-users-guid-1-messages'
    assert created.mailbox_id == 1
    assert created.is_active is True
    assert len(graph_client.create_calls) == 1
    assert graph_client.create_calls[0]['resource'] == 'users/guid-1/messages'


def test_subscribe_mailbox_renews_existing_active_subscription() -> None:
    mailbox = SimpleNamespace(id=1, tenant_code='default', email='sales@hascelik.com', graph_user_id='guid-1', is_active=True)
    service, graph_client, sub_repo = build_service([mailbox])

    current = datetime.now(timezone.utc) + timedelta(minutes=5)
    sub_repo.rows[1] = SimpleNamespace(
        id=1,
        tenant_code='default',
        mailbox_id=1,
        graph_subscription_id='sub-existing',
        resource='users/guid-1/messages',
        change_type='created',
        notification_url='https://admin.hascelik.com/api/v1/webhooks/graph',
        lifecycle_notification_url='https://admin.hascelik.com/api/v1/webhooks/lifecycle',
        client_state='client-state-1',
        expiration_datetime=current,
        is_active=True,
        last_renewed_at=None,
        error_message=None,
    )

    renewed = service.subscribe_mailbox(1)

    assert renewed.graph_subscription_id == 'sub-existing'
    assert len(graph_client.create_calls) == 0
    assert len(graph_client.renew_calls) == 1
    assert graph_client.renew_calls[0]['subscription_id'] == 'sub-existing'
    assert renewed.expiration_datetime > current


def test_renew_due_only_renews_expiring_subscriptions() -> None:
    mailbox = SimpleNamespace(id=1, tenant_code='default', email='sales@hascelik.com', graph_user_id='guid-1', is_active=True)
    service, graph_client, sub_repo = build_service([mailbox])

    now = datetime.now(timezone.utc)
    sub_repo.rows[1] = SimpleNamespace(
        id=1,
        tenant_code='default',
        mailbox_id=1,
        graph_subscription_id='sub-due',
        resource='users/guid-1/messages',
        change_type='created',
        notification_url='https://admin.hascelik.com/api/v1/webhooks/graph',
        lifecycle_notification_url='https://admin.hascelik.com/api/v1/webhooks/lifecycle',
        client_state='client-state-1',
        expiration_datetime=now + timedelta(minutes=2),
        is_active=True,
        last_renewed_at=None,
        error_message=None,
    )
    sub_repo.rows[2] = SimpleNamespace(
        id=2,
        tenant_code='default',
        mailbox_id=2,
        graph_subscription_id='sub-later',
        resource='users/ops/messages',
        change_type='created',
        notification_url='https://admin.hascelik.com/api/v1/webhooks/graph',
        lifecycle_notification_url='https://admin.hascelik.com/api/v1/webhooks/lifecycle',
        client_state='client-state-1',
        expiration_datetime=now + timedelta(minutes=90),
        is_active=True,
        last_renewed_at=None,
        error_message=None,
    )

    result = service.renew_due(within_minutes=30)

    assert result['total'] == 1
    assert result['success'] == 1
    assert result['failed'] == 0
    assert len(graph_client.renew_calls) == 1
    assert graph_client.renew_calls[0]['subscription_id'] == 'sub-due'
