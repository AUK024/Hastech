from abc import ABC, abstractmethod


class LanguageDetectionProvider(ABC):
    @abstractmethod
    def detect_language(self, text: str) -> dict[str, float | str]:
        raise NotImplementedError
