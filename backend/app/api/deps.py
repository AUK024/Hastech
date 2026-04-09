from collections.abc import Generator
from fastapi import Header, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import get_settings


def db_session() -> Generator[Session, None, None]:
    yield from get_db()


def require_admin_user(x_admin_email: str = Header(default='', alias='X-Admin-Email')) -> str:
    normalized = x_admin_email.strip().lower()
    if not normalized:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Admin kullanıcı doğrulaması gerekli')

    settings = get_settings()
    if not settings.is_admin_email(normalized):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Bu işlem sadece admin kullanıcıya açıktır')

    return normalized


def resolve_tenant_code(x_tenant_code: str = Header(default='', alias='X-Tenant-Code')) -> str:
    settings = get_settings()
    normalized = x_tenant_code.strip().lower()
    return normalized or settings.default_tenant_code.strip().lower()
