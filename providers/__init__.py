from __future__ import annotations

from .anthropic import AnthropicProvider
from .base import BaseProvider, ProviderError
from .gemini import GeminiProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider

_REGISTRY: dict[str, type[BaseProvider]] = {
    "gemini": GeminiProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "ollama": OllamaProvider,
}

PROVIDER_NAMES = list(_REGISTRY.keys())


def get_provider(name: str, api_key: str, model: str, timeout: int = 60) -> BaseProvider:
    cls = _REGISTRY.get(name)
    if cls is None:
        raise ProviderError(f"Unknown provider: {name!r}. Choose from {PROVIDER_NAMES}")
    return cls(api_key=api_key, model=model, timeout=timeout)


__all__ = [
    "BaseProvider",
    "ProviderError",
    "GeminiProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "OllamaProvider",
    "get_provider",
    "PROVIDER_NAMES",
]
