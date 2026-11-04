"""Read-only access to the dashboard's per-user files (epic-00427 D-06, D-12, D-13).

The structure snapshot is read here directly, not through `SnapshotStore.load()`, so that a missing, an
unreadable and an unknown-version file can be told apart. The hidden marks and the server location record are
written by the dashboard server and `dashboard hide`/`show` (iss-00529); this module never writes and never
sends a request, not even to a running server: it only checks whether the recorded pid is alive.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import TYPE_CHECKING, Final, Literal

from spec_dock.runtime.domain.dashboard_snapshot import (
    ParsedSnapshot,
    SnapshotUnreadable,
    SnapshotUnsupported,
    parse_snapshot_document,
)
from spec_dock.runtime.infra.github_snapshot import SNAPSHOT_FILE

if TYPE_CHECKING:
    from pathlib import Path

    from spec_dock.runtime.infra.github_structure import GithubRepository

DASHBOARD_DIRECTORY: Final = "dashboard"
REPOSITORIES_FILE: Final = "repositories.json"
SERVER_FILE: Final = "server.json"
REPOSITORIES_SCHEMA: Final = "specdock.dashboard-repositories/v1"
SERVER_SCHEMA: Final = "specdock.dashboard-server/v1"

SnapshotReadStatus = Literal["ok", "missing", "unreadable", "unsupported"]


@dataclass(frozen=True)
class SnapshotRead:
    status: SnapshotReadStatus
    path: Path
    parsed: ParsedSnapshot | None = None
    detail: str | None = None


def snapshot_path(state_root: Path, repository: GithubRepository) -> Path:
    return state_root / "github" / repository.host / repository.owner / repository.name / SNAPSHOT_FILE


def read_snapshot_file(state_root: Path, repository: GithubRepository) -> SnapshotRead:
    path = snapshot_path(state_root, repository)
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return SnapshotRead("missing", path)
    except OSError as error:
        return SnapshotRead("unreadable", path, detail=f"{type(error).__name__}: {error.strerror or error}")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as error:
        return SnapshotRead("unreadable", path, detail=f"not JSON: {error}")
    try:
        return SnapshotRead("ok", path, parse_snapshot_document(payload, repository=repository.key))
    except SnapshotUnsupported as error:
        return SnapshotRead("unsupported", path, detail=str(error))
    except SnapshotUnreadable as error:
        return SnapshotRead("unreadable", path, detail=str(error))


def _read_object(path: Path) -> dict[str, object] | None:
    try:
        payload = json.loads(path.read_bytes().decode("utf-8"))
    except (OSError, UnicodeDecodeError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def read_server_url(state_root: Path) -> str | None:
    """The running server's local base URL when its record exists and its pid is alive; never a request."""
    payload = _read_object(state_root / DASHBOARD_DIRECTORY / SERVER_FILE)
    if payload is None or payload.get("schema") != SERVER_SCHEMA:
        return None
    pid = payload.get("pid")
    urls = payload.get("urls")
    local = urls.get("local") if isinstance(urls, dict) else None
    if type(pid) is not int or pid <= 0 or not isinstance(local, str) or not local:
        return None
    return local if pid_alive(pid) else None
