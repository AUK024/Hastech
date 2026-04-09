import pytest
from app.integrations.microsoft_graph.auth import GraphAuthService


class FakeMsalClient:
    def __init__(self, response: dict):
        self.response = response

    def acquire_token_for_client(self, scopes):
        return self.response


def test_graph_auth_returns_access_token_when_available() -> None:
    auth = GraphAuthService.__new__(GraphAuthService)
    auth.scope = ['scope']
    auth.client = FakeMsalClient({'access_token': 'token-123'})

    assert auth.get_access_token() == 'token-123'


def test_graph_auth_raises_when_token_acquisition_fails() -> None:
    auth = GraphAuthService.__new__(GraphAuthService)
    auth.scope = ['scope']
    auth.client = FakeMsalClient({'error': 'invalid_client', 'error_description': 'Client credential is invalid.'})

    with pytest.raises(RuntimeError) as exc:
        auth.get_access_token()
    assert 'invalid_client' in str(exc.value)
