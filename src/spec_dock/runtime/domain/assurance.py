"""The assurance level given when a CUE Scope is created (epic-00425 R-C1, R-C3; contract K4).

The level and its reason are written once, into the template `requirement.cue`, between the quotes of its
`{{ASSURANCE_LEVEL}}` and `{{ASSURANCE_REASON}}` markers.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Final

ASSURANCE_LEVELS: Final = ("light", "standard", "strict", "critical")
LEVEL_MARKER: Final = "{{ASSURANCE_LEVEL}}"
REASON_MARKER: Final = "{{ASSURANCE_REASON}}"


@dataclass(frozen=True)
class Assurance:
    level: str
    reason: str  # stripped; never blank


def parse_assurance(level: str | None, reason: str | None) -> Assurance:
    """The level and the stripped reason; ValueError(message, argument) when either is missing or unusable.

    Blank follows `str.strip()`, the same range as the type's `#Text` and `scope show` (full-width spaces too).
    """
    if level is None:
        raise ValueError("--assurance is required (light, standard, strict or critical)", "--assurance")
    if level not in ASSURANCE_LEVELS:
        raise ValueError(f"--assurance must be one of {', '.join(ASSURANCE_LEVELS)}, not {level!r}", "--assurance")
    stripped = (reason or "").strip()
    if not stripped:
        raise ValueError("--assurance-reason is required and must not be blank", "--assurance-reason")
    try:
        stripped.encode("utf-8")
    except UnicodeEncodeError:
        raise ValueError("--assurance-reason must be valid UTF-8 text", "--assurance-reason") from None
    return Assurance(level, stripped)


def cue_string_body(text: str) -> str:
    """The text as the inside of a CUE double-quoted string.

    JSON string escapes mean the same in CUE, and `\\` becomes `\\\\`, so `\\(` stays text instead of an
    interpolation. `cue` refuses a byte order mark anywhere but the start of a file, so U+FEFF is escaped too.
    """
    return json.dumps(text, ensure_ascii=False)[1:-1].replace("\ufeff", "\\ufeff")


def assurance_replacements(assurance: Assurance) -> dict[str, str]:
    return {LEVEL_MARKER: assurance.level, REASON_MARKER: cue_string_body(assurance.reason)}
