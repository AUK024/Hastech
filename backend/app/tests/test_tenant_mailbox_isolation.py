from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app


def test_mailboxes_are_isolated_by_tenant_header() -> None:
    client = TestClient(app)
    tenant_a = f'tenant-a-{uuid4().hex[:6]}'
    tenant_b = f'tenant-b-{uuid4().hex[:6]}'

    payload_a = {
        'email': f'{uuid4().hex[:8]}@example.com',
        'graph_user_id': None,
        'display_name': 'Tenant A Mailbox',
        'mailbox_type': 'support',
        'is_active': True,
        'auto_reply_enabled': True,
        'description': None,
    }
    payload_b = {
        'email': f'{uuid4().hex[:8]}@example.com',
        'graph_user_id': None,
        'display_name': 'Tenant B Mailbox',
        'mailbox_type': 'support',
        'is_active': True,
        'auto_reply_enabled': True,
        'description': None,
    }

    created_a = client.post('/api/v1/mailboxes/', headers={'X-Tenant-Code': tenant_a}, json=payload_a)
    created_b = client.post('/api/v1/mailboxes/', headers={'X-Tenant-Code': tenant_b}, json=payload_b)
    assert created_a.status_code == 201
    assert created_b.status_code == 201

    list_a = client.get('/api/v1/mailboxes/', headers={'X-Tenant-Code': tenant_a})
    list_b = client.get('/api/v1/mailboxes/', headers={'X-Tenant-Code': tenant_b})
    assert list_a.status_code == 200
    assert list_b.status_code == 200

    rows_a = list_a.json()
    rows_b = list_b.json()
    assert any(row['email'] == payload_a['email'] for row in rows_a)
    assert any(row['email'] == payload_b['email'] for row in rows_b)
    assert all(row['tenant_code'] == tenant_a for row in rows_a)
    assert all(row['tenant_code'] == tenant_b for row in rows_b)
