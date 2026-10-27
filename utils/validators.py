"""Input validation for job descriptions."""

from __future__ import annotations

import re

from config import MAX_CHARS, MIN_ALPHA_RATIO, MIN_WORDS
from exceptions import InvalidInputError


def validate_job_description(text: object) -> str:
    """Return a cleaned job description or raise InvalidInputError with a friendly message."""
    if text is None or not isinstance(text, str):
        raise InvalidInputError("Please provide the job description as text.")

    cleaned = text.replace("\r\n", "\n").strip()
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)

    if not cleaned:
        raise InvalidInputError("The job description is empty. Paste a job posting to analyze.")

    if len(cleaned) > MAX_CHARS:
        raise InvalidInputError(
            f"The job description is too long ({len(cleaned):,} characters). "
            f"Please keep it under {MAX_CHARS:,} characters."
        )

    words = cleaned.split()
    if len(words) < MIN_WORDS:
        raise InvalidInputError(
            f"That looks too short to be a job description ({len(words)} words). "
            f"Please paste at least {MIN_WORDS} words."
        )

    non_space = [c for c in cleaned if not c.isspace()]
    alpha_ratio = sum(c.isalpha() for c in non_space) / len(non_space)
    if alpha_ratio < MIN_ALPHA_RATIO:
        raise InvalidInputError(
            "The input doesn't look like a job description (mostly numbers or symbols)."
        )

    return cleaned
