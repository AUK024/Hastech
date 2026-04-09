from fastapi.testclient import TestClient
from app.main import app


def test_dashboard_returns_extended_metrics_shape() -> None:
    client = TestClient(app)
    response = client.get('/api/v1/dashboard/')

    assert response.status_code == 200
    payload = response.json()

    expected_keys = {
        'incoming_mail_count',
        'replied_mail_count',
        'daily_incoming',
        'daily_external',
        'daily_auto_reply_sent',
        'daily_errors',
        'language_distribution',
        'language_performance',
        'daily_trend',
        'top_domains',
        'top_mailboxes',
    }
    assert expected_keys.issubset(payload.keys())
    assert isinstance(payload['daily_trend'], list)
    assert isinstance(payload['language_performance'], list)
