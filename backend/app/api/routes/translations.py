from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.repositories.settings_repository import SettingsRepository
from app.services.provider_factory import ProviderFactory
from app.services.settings_service import SettingsService

router = APIRouter()


class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str


@router.post('/test')
def test_translation(payload: TranslationRequest, db: Session = Depends(db_session)) -> dict:
    settings_service = SettingsService(SettingsRepository(db))
    provider = ProviderFactory(settings_service).build_translation_provider()
    text = provider.translate(payload.text, payload.source_language, payload.target_language)
    return {'translated_text': text}
