import httpx
from app.core.config import get_settings
from app.integrations.language_detection.base import LanguageDetectionProvider


class AzureTranslatorLanguageDetectionProvider(LanguageDetectionProvider):
    def __init__(self) -> None:
        self.settings = get_settings()

    def _is_configured(self) -> bool:
        key = self.settings.azure_translator_key.strip()
        region = self.settings.azure_translator_region.strip()
        endpoint = self.settings.azure_translator_endpoint.strip()
        if not key or not region or not endpoint:
            return False
        placeholders = {'your-key', 'your-region', 'your-endpoint'}
        return not any(value.lower() in placeholders for value in (key, region, endpoint))

    def detect_language(self, text: str) -> dict[str, float | str]:
        sample = (text or '').strip()
        if not sample or not self._is_configured():
            return {'language': 'en', 'confidence': 0.0}

        endpoint = self.settings.azure_translator_endpoint.rstrip('/')
        url = f'{endpoint}/detect'
        headers = {
            'Ocp-Apim-Subscription-Key': self.settings.azure_translator_key,
            'Ocp-Apim-Subscription-Region': self.settings.azure_translator_region,
            'Content-Type': 'application/json',
        }
        params = {'api-version': '3.0'}
        payload = [{'Text': sample[:5000]}]

        try:
            with httpx.Client(timeout=20.0) as client:
                response = client.post(url, params=params, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
        except Exception:
            return {'language': 'en', 'confidence': 0.0}

        first = data[0] if isinstance(data, list) and data else {}
        language = str(first.get('language') or 'en')
        try:
            confidence = float(first.get('score') or 0.0)
        except (TypeError, ValueError):
            confidence = 0.0
        return {'language': language, 'confidence': confidence}
