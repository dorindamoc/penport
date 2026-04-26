from pathlib import Path

from providers.base import BaseProvider

_PROMPT_TEMPLATE = (
    "Faithfully transcribe every word of the handwritten text visible in this image. "
    "Do not interpret, summarise, or paraphrase — output the text exactly as written. "
    "Preserve line breaks where they are clearly intentional. "
    "The text may be written in one or more of the following languages: {languages}. "
    "Output only the transcribed text, nothing else."
)


def transcribe(provider: BaseProvider, image_path: Path, languages: str) -> str:
    image_bytes = image_path.read_bytes()
    prompt = _PROMPT_TEMPLATE.format(languages=languages)
    return provider.transcribe(image_bytes, prompt)
