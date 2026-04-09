from fastapi.testclient import TestClient
from app.main import app


def test_api_requests_are_written_to_audit_logs() -> None:
    client = TestClient(app)

    response = client.get('/api/v1/workers/status')
    assert response.status_code == 200

    logs_response = client.get('/api/v1/logs/audit?limit=100')
    assert logs_response.status_code == 200
    logs = logs_response.json()

    assert any(
        row.get('module_name') == 'api_request' and row.get('action_name') == 'GET /api/v1/workers/status'
        for row in logs
    )
