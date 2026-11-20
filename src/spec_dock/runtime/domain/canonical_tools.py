"""The one setting line each tool needs to reach the catalog, and the read-only Claude Code check (R-B6)."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

CODEX_CONFIG_FILE: Final = "~/.codex/config.toml"
CODEX_SECTION: Final = "[sandbox_workspace_write]"
CLAUDE_USER_SETTINGS_FILE: Final = "~/.claude/settings.json"
CLAUDE_CONFIG_DIR: Final = "CLAUDE_CONFIG_DIR"
ANTIGRAVITY_USER_SETTINGS_FILE: Final = "~/.gemini/antigravity-cli/settings.json"
_ANTIGRAVITY_FILE_RULE: Final = re.compile(r"(read_file|write_file)\((.+)\)")


def claude_user_settings(environ: Mapping[str, str], home: Path | None) -> tuple[Path | None, str]:
    """Claude Code's user settings file and how to name it: $CLAUDE_CONFIG_DIR/settings.json when set, else ~/.claude.

    The path is None when it cannot be found (no absolute HOME, or a relative or ~ CLAUDE_CONFIG_DIR).
    """
    config = environ.get(CLAUDE_CONFIG_DIR, "")
    if config:
        path = Path(config) / "settings.json"
        return (path if path.is_absolute() else None), str(path)
    return (home / ".claude/settings.json" if home is not None else None), CLAUDE_USER_SETTINGS_FILE


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


def antigravity_user_settings(home: Path | None) -> Path | None:
    return home / ".gemini/antigravity-cli/settings.json" if home is not None else None


def antigravity_setting_line(catalog: Path) -> str:
    read = json.dumps(f"read_file({catalog})", ensure_ascii=False)
    write = json.dumps(f"write_file({catalog})", ensure_ascii=False)
    return f'{{ "permissions": {{ "allow": [{read}, {write}] }} }}'


def antigravity_allows(
    payload: object, catalog: Path, *, resolve: Callable[[Path], Path] = lambda path: path
) -> bool | None:
    """Judge whether user settings allow reading and writing the real catalog path."""
    if not isinstance(payload, dict):
        return None
    permissions = payload.get("permissions", {})
    if not isinstance(permissions, dict):
        return None
    actions: dict[str, set[str]] = {}
    for policy in ("deny", "ask", "allow"):
        rules = permissions.get(policy, [])
        if not isinstance(rules, list) or not all(isinstance(rule, str) for rule in rules):
            return None
        actions[policy] = _antigravity_covered_actions(rules, catalog, resolve)
    if actions["deny"] or actions["ask"]:
        return None
    return actions["allow"] == {"read_file", "write_file"}


def _antigravity_covered_actions(rules: list[str], catalog: Path, resolve: Callable[[Path], Path]) -> set[str]:
    actions: set[str] = set()
    for rule in rules:
        match = _ANTIGRAVITY_FILE_RULE.fullmatch(rule)
        if match is None:
            continue
        action, target = match.groups()
        if not Path(target).is_absolute() or "*" in target or "\0" in target:
            continue
        try:
            path = resolve(Path(os.path.normpath(target)))
        except UnicodeEncodeError:
            continue  # JSON can contain escapes that do not represent a filesystem path.
        if catalog == path or path in catalog.parents:
            actions.add(action)
    return actions
