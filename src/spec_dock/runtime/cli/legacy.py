"""Explicit diagnostics for removed v1 command roots."""

from __future__ import annotations


class LegacyCommandError(ValueError):
    code = 2
    error_code = "LEGACY_COMMAND_REMOVED"


LEGACY_ROOT_REPLACEMENTS: dict[str, str] = {
    "new": "scope create / artifact create",
    "delete": "scope delete",
    "close": "scope close",
    "update": "installation update",
    "uninstall": "installation uninstall",
    "issue": "work start / work finish",
    "sync": "workspace sync",
    "deps": "dependency check / add / remove",
    "import": "scope import github",
    "validate": "workspace validate",
    "doctor": "workspace doctor",
}


def reject_legacy_root(argv: list[str]) -> None:
    if argv and argv[0] in LEGACY_ROOT_REPLACEMENTS:
        root = argv[0]
        raise LegacyCommandError(f"{root} was removed; use {LEGACY_ROOT_REPLACEMENTS[root]}")
