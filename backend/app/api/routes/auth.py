from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter()


@router.get('/login-url')
def login_url() -> dict[str, str]:
    settings = get_settings()
    auth_url = (
        f"https://login.microsoftonline.com/{settings.graph_tenant_id}/oauth2/v2.0/authorize"
        f"?client_id={settings.graph_client_id}&response_type=code&redirect_uri=http://localhost/callback"
    )
    return {'authorization_url': auth_url}
