import msal
from app.core.config import get_settings


class GraphAuthService:
    def __init__(self) -> None:
        settings = get_settings()
        authority = f'https://login.microsoftonline.com/{settings.graph_tenant_id}'
        self.scope = [settings.graph_scope]
        self.client = msal.ConfidentialClientApplication(
            client_id=settings.graph_client_id,
            authority=authority,
            client_credential=settings.graph_client_secret,
        )

    def get_access_token(self) -> str:
        token_result = self.client.acquire_token_for_client(scopes=self.scope)
        access_token = token_result.get('access_token')
        if access_token:
            return access_token

        error = token_result.get('error') or 'unknown_error'
        description = token_result.get('error_description') or 'Failed to acquire access token for Microsoft Graph.'
        correlation_id = token_result.get('correlation_id') or ''
        raise RuntimeError(
            f'Graph token acquisition failed: {error} ({description})'
            + (f' [correlation_id={correlation_id}]' if correlation_id else '')
        )
