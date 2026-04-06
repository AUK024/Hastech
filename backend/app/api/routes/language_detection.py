from fastapi import APIRouter
from pydantic import BaseModel
from app.integrations.language_detection.mock_provider import MockLanguageDetectionProvider

router = APIRouter()
provider = MockLanguageDetectionProvider()


class LanguageDetectionRequest(BaseModel):
    text: str


@router.post('/test')
def test_detection(payload: LanguageDetectionRequest) -> dict:
    return provider.detect_language(payload.text)
