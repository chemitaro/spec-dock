"""Pure rules for Scope directories and titles written in canonical mode (Epic design ch. 6 and 7)."""

from __future__ import annotations

from typing import Final
import unicodedata

# GitHub's Issue title limit; any language is accepted (Epic design ch. 7).
TITLE_MAX_LENGTH: Final = 256


def validate_canonical_title(value: str, *, field: str) -> str:
    """The stripped title: not empty, no control characters, at most 256 characters (ValueError otherwise)."""
    title = value.strip()
    if not title:
        raise ValueError(f"{field} must not be empty")
    if any(unicodedata.category(character) == "Cc" for character in title):
        raise ValueError(f"{field} must not contain control characters such as line breaks or tabs")
    if len(title) > TITLE_MAX_LENGTH:
        raise ValueError(f"{field} must be at most {TITLE_MAX_LENGTH} characters, not {len(title)}")
    return title
