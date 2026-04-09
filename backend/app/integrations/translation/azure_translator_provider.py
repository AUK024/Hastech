import httpx
from app.core.config import get_settings
from app.integrations.translation.base import TranslationProvider


class AzureTranslatorProvider(TranslationProvider):
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

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        body = (text or '').strip()
        source = (source_language or '').strip().lower()
        target = (target_language or '').strip().lower()

        if not body or not target or source == target:
            return text
        if not self._is_configured():
            return text

        endpoint = self.settings.azure_translator_endpoint.rstrip('/')
        url = f'{endpoint}/translate'
        headers = {
            'Ocp-Apim-Subscription-Key': self.settings.azure_translator_key,
            'Ocp-Apim-Subscription-Region': self.settings.azure_translator_region,
            'Content-Type': 'application/json',
        }
        params = {'api-version': '3.0', 'to': target}
        if source and source not in {'auto', 'unknown'}:
            params['from'] = source

        payload = [{'Text': body}]
        try:
            with httpx.Client(timeout=20.0) as client:
                response = client.post(url, params=params, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
        except Exception:
            return text

        if not isinstance(data, list) or not data:
            return text
        translations = data[0].get('translations') if isinstance(data[0], dict) else None
        if not isinstance(translations, list) or not translations:
            return text
        translated = translations[0].get('text') if isinstance(translations[0], dict) else None
        return translated if isinstance(translated, str) and translated else text
