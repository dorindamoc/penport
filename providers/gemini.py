from __future__ import annotations

from google import genai
from google.genai import types

from .base import BaseProvider, ProviderError

_DEFAULT_TIMEOUT = 60


class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str, model: str, timeout: int = _DEFAULT_TIMEOUT) -> None:
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
