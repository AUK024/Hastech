from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app


def test_mailbox_create_writes_domain_audit_log() -> None:
    client = TestClient(app)
    tenant_code = f'audit-{uuid4().hex[:6]}'
    email = f'{uuid4().hex[:8]}@example.com'
    create_response = client.post(
        '/api/v1/mailboxes/',
        headers={'X-Tenant-Code': tenant_code},
        json={
            'email': email,
            'graph_user_id': None,
            'display_name': 'Audit Mailbox',
            'mailbox_type': 'support',
            'is_active': True,
            'auto_reply_enabled': True,
            'description': None,
        },
    )
    assert create_response.status_code == 201

    logs_response = client.get('/api/v1/logs/audit?limit=200', headers={'X-Tenant-Code': tenant_code})
    assert logs_response.status_code == 200
    rows = logs_response.json()
    assert any(
        row.get('module_name') == 'mailboxes'
        and row.get('action_name') == 'create_mailbox'
        and row.get('payload', {}).get('email') == email
        for row in rows
    )
