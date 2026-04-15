from app.integrations.language_detection.azure_translator_provider import AzureTranslatorLanguageDetectionProvider
from app.integrations.language_detection.base import LanguageDetectionProvider
from app.integrations.language_detection.mock_provider import MockLanguageDetectionProvider
from app.integrations.language_detection.openai_provider import OpenAILanguageDetectionProvider
from app.integrations.translation.azure_translator_provider import AzureTranslatorProvider
from app.integrations.translation.base import TranslationProvider
from app.integrations.translation.mock_provider import MockTranslationProvider
from app.integrations.translation.openai_provider import OpenAITranslationProvider
from app.services.settings_service import SettingsService


class ProviderFactory:
    def __init__(self, settings_service: SettingsService) -> None:
        self.settings = settings_service

    def build_language_detection_provider(self) -> LanguageDetectionProvider:
        provider_name = self.settings.get_value('language_detection_provider', 'mock').strip().lower()
        if provider_name == 'azure_translator':
            return AzureTranslatorLanguageDetectionProvider()
        if provider_name == 'openai':
            return OpenAILanguageDetectionProvider()
        return MockLanguageDetectionProvider()

    def build_translation_provider(self) -> TranslationProvider:
        provider_name = self.settings.get_value('translation_provider', 'mock').strip().lower()
        if provider_name == 'azure_translator':
            return AzureTranslatorProvider()
        if provider_name == 'openai':
            return OpenAITranslationProvider()
        return MockTranslationProvider()
