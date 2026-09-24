"""Fail-closed read of pending external installer group journals."""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

_ID = re.compile(r"[0-9a-f]{32}\Z")
_PHASES = {"preparing", "staged", "applying", "recovery-required", "committed", "rolled-back"}


def pending_installation_groups(common_dir: Path) -> tuple[str, ...]:
    """Return unfinished group IDs so ordinary writers stop until recovery."""
    root = common_dir / "spec-dock" / "control" / "installations"
    if root.is_symlink() or (root.exists() and not root.is_dir()):
        raise ValueError("installation group journal root is unsafe")
    if not root.exists():
        return ()
    pending: list[str] = []
    for directory in sorted(root.iterdir()):
        if directory.is_symlink() or not directory.is_dir() or _ID.fullmatch(directory.name) is None:
            raise ValueError("installation group journal directory is unsafe")
        path = directory / "group.json"
        if path.is_symlink():
            raise ValueError("installation group journal is redirected")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("installation group journal is unreadable") from error
        if (
            not isinstance(payload, dict)
            or payload.get("operation_id") != directory.name
            or payload.get("common_dir") != str(common_dir)
            or payload.get("action") not in {"init", "update", "uninstall"}
            or payload.get("phase") not in _PHASES
            or not isinstance(payload.get("targets"), list)
        ):
            raise ValueError("installation group journal identity is invalid")
        if payload["phase"] not in {"committed", "rolled-back"}:
            pending.append(directory.name)
    return tuple(pending)
