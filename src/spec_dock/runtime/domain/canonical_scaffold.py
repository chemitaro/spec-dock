"""Pure rules for Scope directories written in canonical mode (Epic design ch. 6)."""

from __future__ import annotations

from typing import Final

# GitHub is the only authority for a Scope's title and parent, so new canonical documents do not copy them.
STRUCTURE_FRONT_MATTER_KEYS: Final = ("タイトル:", "親:")
_FENCE: Final = "---"


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
