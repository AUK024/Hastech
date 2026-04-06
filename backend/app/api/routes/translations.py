from fastapi import APIRouter
from pydantic import BaseModel
from app.integrations.translation.mock_provider import MockTranslationProvider

router = APIRouter()
provider = MockTranslationProvider()


class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str


@router.post('/test')
def test_translation(payload: TranslationRequest) -> dict:
    text = provider.translate(payload.text, payload.source_language, payload.target_language)
    return {'translated_text': text}
