from __future__ import annotations

import base64

import anthropic as sdk

from .base import BaseProvider, ProviderError

_DEFAULT_TIMEOUT = 60


class AnthropicProvider(BaseProvider):
    def __init__(self, api_key: str, model: str, timeout: int = _DEFAULT_TIMEOUT) -> None:
        self._client = sdk.Anthropic(api_key=api_key, timeout=timeout)
        self._model = model

    def transcribe(self, image_bytes: bytes, prompt: str) -> str:
        try:
            b64 = base64.b64encode(image_bytes).decode()
            response = self._client.messages.create(
                model=self._model,
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": b64,
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
            )
            block = response.content[0]
            if isinstance(block, sdk.types.TextBlock):
                return block.text
            raise ProviderError("Unexpected response block type")
        except Exception as exc:
            raise ProviderError(f"Anthropic transcribe failed: {exc}") from exc

    def correct(self, text: str, prompt: str) -> str:
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": f"{prompt}\n\n{text}"},
                ],
            )
            block = response.content[0]
            if isinstance(block, sdk.types.TextBlock):
                return block.text
            raise ProviderError("Unexpected response block type")
        except Exception as exc:
            raise ProviderError(f"Anthropic correct failed: {exc}") from exc
