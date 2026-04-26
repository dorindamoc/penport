from __future__ import annotations

from abc import ABC, abstractmethod


class ProviderError(Exception):
    pass


class BaseProvider(ABC):
    @abstractmethod
    def transcribe(self, image_bytes: bytes, prompt: str) -> str: ...

    @abstractmethod
    def correct(self, text: str, prompt: str) -> str: ...

    def validate_key(self) -> None:
        """Raise ProviderError if the API key is missing or rejected. Override per provider."""
