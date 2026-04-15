from app.integrations.language_detection.openai_provider import OpenAILanguageDetectionProvider
from app.integrations.translation.openai_provider import OpenAITranslationProvider


def test_openai_language_detection_parses_and_normalizes_response(monkeypatch) -> None:
    provider = OpenAILanguageDetectionProvider()
    monkeypatch.setattr(
        provider.client,
        'complete',
        lambda **_: '{"language":"ES","confidence":1.4}',
    )

    result = provider.detect_language('hola')

    assert result == {'language': 'es', 'confidence': 1.0}


def test_openai_language_detection_falls_back_for_invalid_response(monkeypatch) -> None:
    provider = OpenAILanguageDetectionProvider()
    monkeypatch.setattr(provider.client, 'complete', lambda **_: 'not-json')

    result = provider.detect_language('hello')

    assert result == {'language': 'en', 'confidence': 0.0}


def test_openai_translation_returns_original_when_no_response(monkeypatch) -> None:
    provider = OpenAITranslationProvider()
    monkeypatch.setattr(provider.client, 'complete', lambda **_: None)

    text = provider.translate('Hello', source_language='en', target_language='tr')

    assert text == 'Hello'


def test_openai_translation_returns_normalized_response(monkeypatch) -> None:
    provider = OpenAITranslationProvider()
    monkeypatch.setattr(provider.client, 'complete', lambda **_: ' Merhaba ')

    text = provider.translate('Hello', source_language='en', target_language='tr')

    assert text == 'Merhaba'
