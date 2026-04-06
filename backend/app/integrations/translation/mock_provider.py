from app.integrations.translation.base import TranslationProvider


class MockTranslationProvider(TranslationProvider):
    def translate(self, text: str, source_language: str, target_language: str) -> str:
        if source_language == target_language:
            return text
        return f'[{target_language}] {text}'
