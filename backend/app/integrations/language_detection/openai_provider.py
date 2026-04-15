import json
import re

from app.core.config import get_settings
from app.integrations.language_detection.base import LanguageDetectionProvider
from app.integrations.openai_chat_client import OpenAIChatClient


class OpenAILanguageDetectionProvider(LanguageDetectionProvider):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = OpenAIChatClient(
            api_key=self.settings.openai_api_key,
            base_url=self.settings.openai_base_url,
            timeout_seconds=self.settings.openai_timeout_seconds,
        )

    def detect_language(self, text: str) -> dict[str, float | str]:
        sample = (text or '').strip()
        if not sample:
            return {'language': 'en', 'confidence': 0.0}

        response_text = self.client.complete(
            model=self.settings.openai_detection_model,
            messages=[
                {
                    'role': 'system',
                    'content': (
                        'Detect the primary language of the user text. '
                        'Return JSON only with keys "language" and "confidence". '
                        'language must be lowercase (ISO-639 code when possible). '
                        'confidence must be a float between 0 and 1.'
                    ),
                },
                {'role': 'user', 'content': sample[:5000]},
            ],
            temperature=0.0,
        )
        if not response_text:
            return {'language': 'en', 'confidence': 0.0}

        parsed = self._parse_json(response_text)
        if not isinstance(parsed, dict):
            return {'language': 'en', 'confidence': 0.0}

        language = self._normalize_language(parsed.get('language'))
        confidence = self._normalize_confidence(parsed.get('confidence'))
        return {'language': language, 'confidence': confidence}

    @staticmethod
    def _parse_json(content: str) -> dict | None:
        payload = content.strip()
        if not payload:
            return None
        try:
            value = json.loads(payload)
            return value if isinstance(value, dict) else None
        except Exception:
            pass

        match = re.search(r'\{.*\}', payload, flags=re.DOTALL)
        if not match:
            return None
        try:
            value = json.loads(match.group(0))
            return value if isinstance(value, dict) else None
        except Exception:
            return None

    @staticmethod
    def _normalize_language(value: object) -> str:
        if not isinstance(value, str):
            return 'en'
        language = value.strip().lower()
        if not language:
            return 'en'
        if re.fullmatch(r'[a-z]{2,3}(?:-[a-z0-9]{2,8})?', language):
            return language
        return 'en'

    @staticmethod
    def _normalize_confidence(value: object) -> float:
        try:
            confidence = float(value)
        except (TypeError, ValueError):
            return 0.0
        if confidence < 0:
            return 0.0
        if confidence > 1:
            return 1.0
        return confidence
