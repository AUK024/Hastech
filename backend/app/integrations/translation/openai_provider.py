from app.core.config import get_settings
from app.integrations.openai_chat_client import OpenAIChatClient
from app.integrations.translation.base import TranslationProvider


class OpenAITranslationProvider(TranslationProvider):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = OpenAIChatClient(
            api_key=self.settings.openai_api_key,
            base_url=self.settings.openai_base_url,
            timeout_seconds=self.settings.openai_timeout_seconds,
        )

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        body = (text or '').strip()
        source = (source_language or '').strip().lower()
        target = (target_language or '').strip().lower()

        if not body or not target or source == target:
            return text

        source_label = source if source and source not in {'auto', 'unknown'} else 'auto'
        prompt = (
            f'Source language: {source_label}\n'
            f'Target language: {target}\n\n'
            'Text:\n'
            f'{text}'
        )
        translated = self.client.complete(
            model=self.settings.openai_translation_model,
            messages=[
                {
                    'role': 'system',
                    'content': (
                        'You are a translation engine. Translate the user text to the target language. '
                        'Keep the original meaning, tone, line breaks and placeholders. '
                        'Return only the translated text.'
                    ),
                },
                {'role': 'user', 'content': prompt},
            ],
            temperature=0.0,
        )

        if not translated:
            return text
        normalized = translated.strip()
        return normalized if normalized else text
