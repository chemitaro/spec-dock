"""Read-only access to the dashboard's per-user files (epic-00427 D-06, D-12, D-13).

The structure snapshot is read here directly, not through `SnapshotStore.load()`, so that a missing, an
unreadable and an unknown-version file can be told apart. The hidden marks and the server location record are
written by the dashboard server and `dashboard hide`/`show` (iss-00529); this module never writes and never
sends a request, not even to a running server: it only checks whether the recorded pid is alive.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import json
import os
from typing import TYPE_CHECKING, Final, Literal

from spec_dock.runtime.domain.canonical_structure import SnapshotFormatError
from spec_dock.runtime.domain.dashboard_snapshot import (
    ParsedSnapshot,
    SnapshotUnreadable,
    SnapshotUnsupported,
    parse_snapshot_document,
    structure_confirmed_at,
)
from spec_dock.runtime.infra.github_snapshot import PROBE_FILE, SNAPSHOT_FILE, ProbeRecord

if TYPE_CHECKING:
    from datetime import datetime
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
    probe_checked_at: str | None = None  # the periodic sync's last check (probe.json); None when absent or unreadable
    probe_failed: bool = False

    def confirmed_at(self, now: datetime) -> str | None:
        """When the structure was last confirmed against GitHub (iss-00568); None without a readable snapshot."""
        if self.parsed is None:
            return None
        return structure_confirmed_at(self.parsed.snapshot.fetched_at, self.probe_checked_at, self.probe_failed, now)


def snapshot_path(state_root: Path, repository: GithubRepository) -> Path:
    return state_root / "github" / repository.host / repository.owner / repository.name / SNAPSHOT_FILE


def probe_path(state_root: Path, repository: GithubRepository) -> Path:
    return snapshot_path(state_root, repository).with_name(PROBE_FILE)


def _read_probe(state_root: Path, repository: GithubRepository) -> tuple[str | None, bool]:
    """The probe's `checked_at` and whether it recorded an error; absent or unreadable gives (None, False)."""
    try:
        record = ProbeRecord.from_json(json.loads(probe_path(state_root, repository).read_bytes().decode("utf-8")))
    except (OSError, UnicodeDecodeError, ValueError, SnapshotFormatError):
        return None, False
    return record.checked_at, record.last_error is not None


def read_snapshot_file(state_root: Path, repository: GithubRepository) -> SnapshotRead:
    read = _read_snapshot(state_root, repository)
    if read.status != "ok":
        return read
    checked, failed = _read_probe(state_root, repository)
    return replace(read, probe_checked_at=checked, probe_failed=failed)


def _read_snapshot(state_root: Path, repository: GithubRepository) -> SnapshotRead:
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
