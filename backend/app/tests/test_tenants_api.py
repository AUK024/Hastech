from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app


def test_tenant_crud_requires_admin_header_and_allows_management() -> None:
    client = TestClient(app)
    tenant_code = f'tenant-{uuid4().hex[:8]}'
    headers = {'X-Admin-Email': 'admin@hascelik.com'}

    create_response = client.post(
        '/api/v1/tenants/',
        headers=headers,
        json={
            'tenant_code': tenant_code,
            'display_name': 'Tenant Test',
            'is_active': True,
            'description': 'integration test tenant',
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    tenant_id = created['id']

    list_response = client.get('/api/v1/tenants/', headers=headers)
    assert list_response.status_code == 200
    tenants = list_response.json()
    assert any(row['tenant_code'] == tenant_code for row in tenants)

    update_response = client.put(
        f'/api/v1/tenants/{tenant_id}',
        headers=headers,
        json={'display_name': 'Tenant Test Updated', 'is_active': False},
    )
    assert update_response.status_code == 200
    assert update_response.json()['display_name'] == 'Tenant Test Updated'
    assert update_response.json()['is_active'] is False

    delete_response = client.delete(f'/api/v1/tenants/{tenant_id}', headers=headers)
    assert delete_response.status_code == 200
