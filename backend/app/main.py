from fastapi import FastAPI
from app.api.router import api_router
from app.core.config import get_settings
from app.core.middleware import register_middlewares
from app.db.session import SessionLocal
from app.repositories.settings_repository import SettingsRepository
from app.services.settings_service import SettingsService

settings = get_settings()
app = FastAPI(title=settings.app_name)
register_middlewares(app)
app.include_router(api_router, prefix=settings.api_prefix)


@app.on_event('startup')
def startup_seed_settings() -> None:
    db = SessionLocal()
    try:
        SettingsService(SettingsRepository(db)).seed_defaults()
    finally:
        db.close()


@app.get('/health', tags=['health'])
def health() -> dict[str, str]:
    return {'status': 'ok'}
