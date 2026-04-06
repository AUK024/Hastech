from app.integrations.language_detection.base import LanguageDetectionProvider


class MockLanguageDetectionProvider(LanguageDetectionProvider):
    def detect_language(self, text: str) -> dict[str, float | str]:
        sample = text.lower()
        if 'merhaba' in sample:
            return {'language': 'tr', 'confidence': 0.95}
        if 'hola' in sample:
            return {'language': 'es', 'confidence': 0.90}
        return {'language': 'en', 'confidence': 0.80}
