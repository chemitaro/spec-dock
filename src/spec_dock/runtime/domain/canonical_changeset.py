"""Changesets: what one SpecDock command wrote in the catalog, saved by the next sync as one commit (contract C4)."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import TYPE_CHECKING, Final, Literal, cast

from spec_dock.runtime.domain.canonical_content import RUNTIME_DIRECTORY
from spec_dock.runtime.domain.canonical_structure import format_timestamp

if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import datetime
    from pathlib import PurePosixPath

CHANGESET_VERSION: Final = 1
ChangesetOrigin = Literal["command", "finish"]
CHANGESET_ORIGINS: Final[frozenset[str]] = frozenset({"command", "finish"})

_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_TOKEN = re.compile(r"^[0-9a-f]{16}$")


def normalize_catalog_path(value: str | PurePosixPath) -> str:
    """A relative POSIX path inside the catalog content; `.runtime` and escapes are refused."""
    text = str(value)
    if not text or "\\" in text or "\0" in text or text.startswith("/"):
        raise ValueError(f"catalog path must be relative to the catalog root: {text!r}")
    parts = [part for part in text.split("/") if part not in ("", ".")]
    if not parts or ".." in parts:
        raise ValueError(f"catalog path must stay inside the catalog: {text!r}")
    if parts[0] == RUNTIME_DIRECTORY:
        raise ValueError(f"catalog path must not name the runtime area: {text!r}")
    return "/".join(parts)


def _normalized(paths: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted({normalize_catalog_path(path) for path in paths}))


@dataclass(frozen=True)
class Changeset:
    origin: ChangesetOrigin
    command: str
    created_at: str
    paths: tuple[str, ...]
    deletions: tuple[str, ...]
    version: int = field(default=CHANGESET_VERSION)

    def __post_init__(self) -> None:
        if type(self.version) is not int or self.version != CHANGESET_VERSION:
            raise ValueError("changeset version must be 1")
        if self.origin not in CHANGESET_ORIGINS:
            raise ValueError("changeset origin must be command or finish")
        if not isinstance(self.command, str) or not self.command.strip():
            raise ValueError("changeset command is required")
        if not isinstance(self.created_at, str) or _TIMESTAMP.fullmatch(self.created_at) is None:
            raise ValueError("changeset created_at must be a UTC timestamp")
        object.__setattr__(self, "paths", _normalized(self.paths))
        object.__setattr__(self, "deletions", _normalized(self.deletions))

    def to_json(self) -> dict[str, object]:
        return {
            "version": self.version,
            "origin": self.origin,
            "command": self.command,
            "created_at": self.created_at,
            "paths": list(self.paths),
            "deletions": list(self.deletions),
        }

    @classmethod
    def from_json(cls, payload: object) -> Changeset:
        if not isinstance(payload, dict):
            raise ValueError("changeset must be a JSON object")
        paths, deletions = payload.get("paths"), payload.get("deletions")
        if not isinstance(paths, list) or not isinstance(deletions, list):
            raise ValueError("changeset paths and deletions must be lists")
        if not all(isinstance(item, str) for item in (*paths, *deletions)):
            raise ValueError("changeset paths must be strings")
        version = payload.get("version")
        return cls(
            origin=cast("ChangesetOrigin", payload.get("origin")),
            command=cast("str", payload.get("command")),
            created_at=cast("str", payload.get("created_at")),
            paths=tuple(paths),
            deletions=tuple(deletions),
            version=version if type(version) is int else -1,
        )


def changeset_filename(created_at: datetime, token: str) -> str:
    """`<UTC YYYYMMDDTHHMMSSZ>-<16 hex>.json`, so names sort by creation time."""
    if _TOKEN.fullmatch(token) is None:
        raise ValueError("changeset token must be 16 lowercase hexadecimal digits")
    stamp = format_timestamp(created_at).replace("-", "").replace(":", "")
    return f"{stamp}-{token}.json"
