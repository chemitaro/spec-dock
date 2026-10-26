"""The files SpecDock keeps at the root of the canonical branch, format 1 (contract C5)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Mapping

CANONICAL_FORMAT: Final = 1
FORMAT_FILE: Final = ".spec-dock-canonical.json"
RUNTIME_DIRECTORY: Final = ".runtime"
INITIAL_COMMIT_MESSAGE: Final = "spec-dock: create canonical"

_README: Final = """\
# spec-dock/canonical

このブランチ `spec-dock/canonical` は、仕様の内容（要件、設計、計画、報告、Artifact）の正本です。
コードのブランチ（main など）とは共通の祖先を持たず、コードのブランチにマージしません。

- 仕様は、各チェックアウトの `spec-dock/initiatives/` から、普通のファイルとして読み書きします。
- 保存、取り込み、push は、SpecDock の定期の同期が行います。このブランチを手で commit、rebase、強制 push しないでください。
- 構造（番号、種類、親子、依存、状態、題名）の正本は GitHub Issue です。
"""

CANONICAL_ROOT_FILES: Final[Mapping[str, bytes]] = {
    FORMAT_FILE: (json.dumps({"format": CANONICAL_FORMAT}) + "\n").encode("utf-8"),
    ".gitignore": b".runtime/\n**/.workbench/*\n!**/.workbench/README.md\n**/.workbench/README.md/**\n",
    "README.md": _README.encode("utf-8"),
}


def read_format(payload: bytes | None) -> int | None:
    """The integer format of a .spec-dock-canonical.json payload; missing or malformed gives None."""
    if payload is None:
        return None
    try:
        loaded = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    version = loaded.get("format") if isinstance(loaded, dict) else None
    return version if type(version) is int else None


def format_writable(version: int | None) -> bool:
    """SpecDock never writes a canonical format newer than the one it knows (R-A5)."""
    return version is not None and 1 <= version <= CANONICAL_FORMAT
