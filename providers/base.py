from __future__ import annotations

from abc import ABC, abstractmethod


class ProviderError(Exception):
    pass


class BaseProvider(ABC):
    @abstractmethod
    def transcribe(self, image_bytes: bytes, prompt: str) -> str: ...

    @abstractmethod
    def correct(self, text: str, prompt: str) -> str: ...
