from types import SimpleNamespace
from app.api.routes.webhooks import (
    _extract_graph_user_and_message,
    _iter_graph_notifications,
    _resolve_mailbox_for_graph_user,
)


def test_extract_graph_user_and_message_from_slash_resource() -> None:
    user, message = _extract_graph_user_and_message('/users/sales@hascelik.com/messages/AAMk123')
    assert user == 'sales@hascelik.com'
    assert message == 'AAMk123'


def test_extract_graph_user_and_message_from_odata_resource() -> None:
    user, message = _extract_graph_user_and_message("Users('guid-123')/mailFolders('Inbox')/Messages('AAMk456')")
    assert user == 'guid-123'
    assert message == 'AAMk456'


def test_iter_graph_notifications_supports_value_and_legacy_payload() -> None:
    payload = {'value': [{'resource': '/users/a/messages/b'}]}
    assert len(_iter_graph_notifications(payload)) == 1

    legacy_payload = {'mailbox_id': 1, 'mailbox_email': 'sales@hascelik.com', 'message_id': 'm-1'}
    assert len(_iter_graph_notifications(legacy_payload)) == 1


def test_resolve_mailbox_for_graph_user_prefers_email_and_graph_user_id() -> None:
    mailboxes = [
        SimpleNamespace(email='sales@hascelik.com', graph_user_id='guid-sales'),
        SimpleNamespace(email='ops@hascelik.com', graph_user_id=None),
    ]
    by_email = _resolve_mailbox_for_graph_user('sales@hascelik.com', mailboxes)
    by_graph_id = _resolve_mailbox_for_graph_user('guid-sales', mailboxes)

    assert by_email is not None
    assert by_graph_id is not None
    assert by_email.email == 'sales@hascelik.com'
    assert by_graph_id.email == 'sales@hascelik.com'
