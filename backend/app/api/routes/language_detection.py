from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.repositories.settings_repository import SettingsRepository
from app.services.provider_factory import ProviderFactory
from app.services.settings_service import SettingsService

router = APIRouter()


class LanguageDetectionRequest(BaseModel):
    text: str


@router.post('/test')
def test_detection(payload: LanguageDetectionRequest, db: Session = Depends(db_session)) -> dict:
    settings_service = SettingsService(SettingsRepository(db))
    provider = ProviderFactory(settings_service).build_language_detection_provider()
    return provider.detect_language(payload.text)
