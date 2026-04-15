from app.integrations.language_detection.azure_translator_provider import AzureTranslatorLanguageDetectionProvider
from app.integrations.language_detection.mock_provider import MockLanguageDetectionProvider
from app.integrations.language_detection.openai_provider import OpenAILanguageDetectionProvider
from app.integrations.translation.azure_translator_provider import AzureTranslatorProvider
from app.integrations.translation.mock_provider import MockTranslationProvider
from app.integrations.translation.openai_provider import OpenAITranslationProvider
from app.services.provider_factory import ProviderFactory


class FakeSettingsService:
    def __init__(self, values: dict[str, str]):
        self.values = values

    def get_value(self, key: str, default: str) -> str:
        return self.values.get(key, default)


def test_provider_factory_uses_mock_by_default() -> None:
    factory = ProviderFactory(FakeSettingsService(values={}))

    assert isinstance(factory.build_language_detection_provider(), MockLanguageDetectionProvider)
    assert isinstance(factory.build_translation_provider(), MockTranslationProvider)


def test_provider_factory_uses_azure_translator_when_configured() -> None:
    factory = ProviderFactory(
        FakeSettingsService(
            values={
                'language_detection_provider': 'azure_translator',
                'translation_provider': 'azure_translator',
            }
        )
    )

    assert isinstance(factory.build_language_detection_provider(), AzureTranslatorLanguageDetectionProvider)
    assert isinstance(factory.build_translation_provider(), AzureTranslatorProvider)


def test_provider_factory_uses_openai_when_configured() -> None:
    factory = ProviderFactory(
        FakeSettingsService(
            values={
                'language_detection_provider': 'openai',
                'translation_provider': 'openai',
            }
        )
    )

    assert isinstance(factory.build_language_detection_provider(), OpenAILanguageDetectionProvider)
    assert isinstance(factory.build_translation_provider(), OpenAITranslationProvider)


def test_provider_factory_falls_back_to_mock_for_unknown_provider() -> None:
    factory = ProviderFactory(
        FakeSettingsService(
            values={
                'language_detection_provider': 'unknown',
                'translation_provider': 'unknown',
            }
        )
    )

    assert isinstance(factory.build_language_detection_provider(), MockLanguageDetectionProvider)
    assert isinstance(factory.build_translation_provider(), MockTranslationProvider)
