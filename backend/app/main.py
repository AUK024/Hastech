from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from sqlalchemy.exc import OperationalError, ProgrammingError
from app.api.router import api_router
from app.core.config import get_settings
from app.core.middleware import register_middlewares
from app.db.session import SessionLocal
from app.repositories.settings_repository import SettingsRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.settings_service import SettingsService
from app.schemas.tenant import TenantCreate

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    db = SessionLocal()
    try:
        SettingsService(SettingsRepository(db)).seed_defaults()
        try:
            tenant_repo = TenantRepository(db)
            if not tenant_repo.get_by_code(settings.default_tenant_code):
                tenant_repo.create(
                    TenantCreate(
                        tenant_code=settings.default_tenant_code,
                        display_name='Default Tenant',
                        is_active=True,
                        description='Seeded default tenant',
                    )
                )
        except (ProgrammingError, OperationalError):
            # Migration may not be applied yet on fresh startup; keep app booting.
            db.rollback()
            logger.warning('Tenant table not ready during startup seed; skipping default tenant seed.')
        yield
    finally:
        db.close()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
register_middlewares(app)
app.include_router(api_router, prefix=settings.api_prefix)


@app.get('/health', tags=['health'])
def health() -> dict[str, str]:
    return {'status': 'ok'}
