from providers.base import BaseProvider

_PROMPT_TEMPLATE = (
    "You are a spelling corrector for transcribed handwritten text. "
    "The text was automatically transcribed from a handwritten image and may contain errors. "
    "Correct only words that are clearly misspelled or do not exist in any of the configured languages. "
    "Use surrounding context to determine the most likely intended word. "
    "Do NOT change proper nouns, names, places, or words that plausibly belong to any of the configured languages. "
    "Do NOT reword, rephrase, or alter punctuation. "
    "The text may be in one or more of the following languages: {languages}. "
    "Return only the corrected text, nothing else."
)


def correct(provider: BaseProvider, raw_text: str, languages: str) -> str:
    prompt = _PROMPT_TEMPLATE.format(languages=languages)
    return provider.correct(raw_text, prompt)
