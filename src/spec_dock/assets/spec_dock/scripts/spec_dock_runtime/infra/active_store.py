from __future__ import annotations

from pathlib import Path
from typing import Any

from ..io_json import _load_json


def _active_entry_id(entry: Any) -> str | None:
    if not isinstance(entry, dict):
        return None
    value = entry.get("id")
    if isinstance(value, str) and value.strip():
        return value
    return None


def load_active_issue_id(specdock_dir: Path) -> str | None:
    candidates = (
        specdock_dir / ".agent" / "active.json",
        specdock_dir / ".work" / "active.json",
        specdock_dir / ".work" / "current.json",
    )
    for path in candidates:
        if not path.exists():
            continue
        try:
            current = _load_json(path)
        except RuntimeError:
            continue
        if isinstance(current, dict):
            return _active_entry_id(current.get("issue"))
    return None
