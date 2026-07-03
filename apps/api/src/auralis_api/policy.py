import re

from fastapi import HTTPException

LIVING_ARTIST_PATTERNS = (
    r"sound exactly like\s+([\w\s.'-]+)",
    r"in the exact voice of\s+([\w\s.'-]+)",
    r"clone\s+([\w\s.'-]+)'s voice",
)


def enforce_prompt_policy(prompt: str, acknowledged: bool = False) -> None:
    for pattern in LIVING_ARTIST_PATTERNS:
        if re.search(pattern, prompt, flags=re.IGNORECASE):
            if not acknowledged:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        "Exact artist or voice imitation is not supported. Rephrase using broad "
                        "musical traits, or acknowledge the style-inspiration policy."
                    ),
                )


def require_rights(confirmed: bool) -> None:
    if not confirmed:
        raise HTTPException(status_code=422, detail="Rights confirmation is required.")
