from __future__ import annotations

import httpx
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from .base import BaseProvider, ProviderError

_DEFAULT_TIMEOUT = 60


class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str, model: str, timeout: int = _DEFAULT_TIMEOUT) -> None:
        self._api_key = api_key
        self._client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=timeout),
        )
        self._model = model

    def transcribe(self, image_bytes: bytes, prompt: str) -> str:
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    prompt,
                ],
            )
            return response.text or ""
        except Exception as exc:
            raise ProviderError(f"Gemini transcribe failed: {exc}") from exc

    def correct(self, text: str, prompt: str) -> str:
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=f"{prompt}\n\n{text}",
            )
            return response.text or ""
        except Exception as exc:
            raise ProviderError(f"Gemini correct failed: {exc}") from exc

    def validate_key(self) -> None:
        if not self._api_key:
            raise ProviderError("Gemini API key is empty — open Settings and paste your key.")
        try:
            next(iter(self._client.models.list()), None)
        except genai_errors.ClientError as exc:
            raise ProviderError(
                f"Gemini API key rejected (HTTP {exc.code}) — check the key in Settings."
            ) from exc
        except (httpx.TimeoutException, TimeoutError) as exc:
            raise ProviderError(
                "Connection to Gemini timed out — check your internet connection or firewall."
            ) from exc
        except Exception as exc:
            raise ProviderError(f"Cannot reach Gemini: {exc}") from exc
