from __future__ import annotations

import base64

import requests

from .base import BaseProvider, ProviderError

_DEFAULT_TIMEOUT = 120
_OLLAMA_URL = "http://localhost:11434/api/generate"


class OllamaProvider(BaseProvider):
    def __init__(self, api_key: str, model: str, timeout: int = _DEFAULT_TIMEOUT) -> None:
        # api_key unused for Ollama; kept for interface consistency
        self._model = model
        self._timeout = timeout

    def transcribe(self, image_bytes: bytes, prompt: str) -> str:
        try:
            b64 = base64.b64encode(image_bytes).decode()
            payload = {
                "model": self._model,
                "prompt": prompt,
                "images": [b64],
                "stream": False,
            }
            resp = requests.post(_OLLAMA_URL, json=payload, timeout=self._timeout)
            resp.raise_for_status()
            return resp.json().get("response", "")
        except Exception as exc:
            raise ProviderError(f"Ollama transcribe failed: {exc}") from exc

    def correct(self, text: str, prompt: str) -> str:
        try:
            payload = {
                "model": self._model,
                "prompt": f"{prompt}\n\n{text}",
                "stream": False,
            }
            resp = requests.post(_OLLAMA_URL, json=payload, timeout=self._timeout)
            resp.raise_for_status()
            return resp.json().get("response", "")
        except Exception as exc:
            raise ProviderError(f"Ollama correct failed: {exc}") from exc
