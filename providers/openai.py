from __future__ import annotations

import base64

from openai import OpenAI

from .base import BaseProvider, ProviderError

_DEFAULT_TIMEOUT = 60


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str, model: str, timeout: int = _DEFAULT_TIMEOUT) -> None:
        self._client = OpenAI(api_key=api_key, timeout=timeout)
        self._model = model

    def transcribe(self, image_bytes: bytes, prompt: str) -> str:
        try:
            b64 = base64.b64encode(image_bytes).decode()
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                            },
                        ],
                    }
                ],
                max_tokens=4096,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            raise ProviderError(f"OpenAI transcribe failed: {exc}") from exc

    def correct(self, text: str, prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "user", "content": f"{prompt}\n\n{text}"},
                ],
                max_tokens=4096,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            raise ProviderError(f"OpenAI correct failed: {exc}") from exc
