from collections.abc import Callable
from pathlib import Path

from providers import get_provider

from .correct import correct
from .transcribe import transcribe


def run_pipeline(
    image_path: Path,
    cfg: dict,
    progress_cb: Callable[[str], None] | None = None,
) -> tuple[str, str]:
    """Return (raw_text, corrected_text). Raises on any failure."""

    def _progress(msg: str) -> None:
        if progress_cb is not None:
            progress_cb(msg)

    llm = cfg["llm"]
    languages = _languages_string(cfg)

    vision_provider = get_provider(
        name=llm["vision_provider"],
        api_key=llm["vision_api_key"],
        model=llm["vision_model"],
        timeout=60,
    )

    _progress("Transcribing…")
    raw = transcribe(vision_provider, image_path, languages)

    if not cfg["pipeline"].get("correction_enabled", True):
        return raw, raw

    correction_provider = get_provider(
        name=llm["correction_provider"],
        api_key=llm["correction_api_key"],
        model=llm["correction_model"],
        timeout=60,
    )

    _progress("Correcting…")
    corrected = correct(correction_provider, raw, languages)

    return raw, corrected


def _languages_string(cfg: dict) -> str:
    langs = [cfg["languages"]["primary"]] + cfg["languages"].get("additional", [])
    return ", ".join(language for language in langs if language)
