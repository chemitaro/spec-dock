"""The one setting line each tool needs to reach the catalog, and the read-only Claude Code check (R-B6)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

CODEX_CONFIG_FILE: Final = "~/.codex/config.toml"
CODEX_SECTION: Final = "[sandbox_workspace_write]"
CLAUDE_USER_SETTINGS_FILE: Final = "~/.claude/settings.json"


def codex_setting_line(catalog: Path) -> str:
    return f"writable_roots = [{json.dumps(str(catalog), ensure_ascii=False)}]"


def claude_setting_line(catalog: Path) -> str:
    return f'{{ "permissions": {{ "additionalDirectories": [{json.dumps(str(catalog), ensure_ascii=False)}] }} }}'


def claude_allows(
    payloads: Sequence[tuple[Path, object]],
    catalog: Path,
    *,
    home: Path | None,
    resolve: Callable[[Path], Path] = lambda path: path,
) -> bool | None:
    """True when some settings list the catalog or a parent; None when an unreadable setting leaves it unknown.

    `catalog` is the catalog's real path. Each payload is (settings file, parsed JSON or None when unreadable).
    A relative entry resolves from the project root that owns the settings file (the parent of `.claude`);
    `resolve` maps an entry to its real path (the application passes the filesystem's).
    """
    unknown = False
    for source, payload in payloads:
        directories = _additional_directories(payload)
        if directories is None:
            unknown = True
            continue
        for entry in directories:
            entry_path = _entry_path(entry, source, home)
            resolved = resolve(entry_path) if entry_path is not None else None
            if resolved is None:
                unknown = True
            elif catalog == resolved or resolved in catalog.parents:
                return True
    return None if unknown else False


def _additional_directories(payload: object) -> list[str] | None:
    if not isinstance(payload, dict):
        return None
    permissions = payload.get("permissions", {})
    if not isinstance(permissions, dict):
        return None
    directories = permissions.get("additionalDirectories", [])
    if not isinstance(directories, list) or not all(isinstance(item, str) for item in directories):
        return None
    return directories


def _entry_path(entry: str, source: Path, home: Path | None) -> Path | None:
    if entry == "~" or entry.startswith("~/"):
        if home is None:
            return None
        text = str(home) + entry[1:]
    elif Path(entry).is_absolute():
        text = entry
    else:
        text = str(source.parent.parent / entry)
    return Path(os.path.normpath(text))
