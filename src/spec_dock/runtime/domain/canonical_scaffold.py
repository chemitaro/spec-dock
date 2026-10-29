"""Pure rules for Scope directories and titles written in canonical mode (Epic design ch. 6 and 7)."""

from __future__ import annotations

import re
from typing import Final
import unicodedata

from spec_dock.runtime.domain.canonical_layout import SCOPE_TO_SPEC_DOCK

# GitHub is the only authority for a Scope's title and parent, so new canonical documents do not copy them.
STRUCTURE_FRONT_MATTER_KEYS: Final = ("タイトル:", "親:")
# GitHub's Issue title limit; any language is accepted (Epic design ch. 7).
TITLE_MAX_LENGTH: Final = 256
_FENCE: Final = "---"
# A Markdown link target climbing to spec-dock/docs/ from the legacy nested depth of a template.
_SPEC_DOCK_LINK: Final = re.compile(r"\]\((?:\.\./)+docs/")


def strip_structure_front_matter(text: str) -> str:
    """Drop the title and parent lines of a leading `---` front matter; the body and its headings stay."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != _FENCE:
        return text
    for index in range(1, len(lines)):
        if lines[index].rstrip("\r\n") == _FENCE:
            kept = [line for line in lines[1:index] if not line.startswith(STRUCTURE_FRONT_MATTER_KEYS)]
            return "".join((lines[0], *kept, *lines[index:]))
    return text


def rebase_spec_dock_links(text: str) -> str:
    """Point `spec-dock/docs/...` links at the depth of `<catalog>/<bucket>/<ID>/` (`../../../docs/...`)."""
    return _SPEC_DOCK_LINK.sub(f"]({SCOPE_TO_SPEC_DOCK.as_posix()}/docs/", text)


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
