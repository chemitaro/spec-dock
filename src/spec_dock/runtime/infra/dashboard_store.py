"""The writers of the dashboard's per-user files (epic-00427 D-06, D-13, D-18; iss-00529 D-07, D-08).

Every write re-reads its file under a flock on `<state_root>/dashboard` and replaces it by rename. The hidden
marks are never overwritten when unreadable (losing them would silently show hidden repositories); an
unreadable "seen" file only loses change marks, so it is rebuilt. Nothing here sends a request.
"""

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
import json
import secrets
from typing import TYPE_CHECKING, Final, cast

from spec_dock.runtime.domain.dashboard_model import SeenScope
from spec_dock.runtime.infra.canonical_state import directory_lock, write_json_atomic
from spec_dock.runtime.infra.dashboard_files import (
    DASHBOARD_DIRECTORY,
    REPOSITORIES_FILE,
    REPOSITORIES_SCHEMA,
    SERVER_FILE,
    SERVER_SCHEMA,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from datetime import datetime
    from pathlib import Path

    from spec_dock.runtime.infra.github_structure import GithubRepository

SEEN_FILE: Final = "seen.json"
SEEN_SCHEMA: Final = "specdock.dashboard-seen/v1"
SERVER_LOCK_FILE: Final = "server.lock"
SEEN_KEEP: Final = 5
_STATES: Final = frozenset({"done", "doing", "blocked", "ready", "unknown"})
_PHASES: Final = frozenset({"none", "draft", "open", "needs_fix", "merged", "closed"})


class DashboardStateUnreadable(Exception):
    """A dashboard file that must not be overwritten is unreadable or of another schema."""

    def __init__(self, path: Path, reason: str) -> None:
        super().__init__(f"{path}: {reason}")
        self.path = path
        self.reason = reason


@dataclass(frozen=True)
class SeenRecord:
    seen_id: str
    seen_at: str
    scopes: Mapping[str, SeenScope]


def dashboard_dir(state_root: Path) -> Path:
    return state_root / DASHBOARD_DIRECTORY


def _utc(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path) -> object | None:
    """The parsed file; None when absent. Raises ValueError (or OSError) when it cannot be read."""
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return None
    return json.loads(raw.decode("utf-8"))


# --- Hidden marks (D-13) -------------------------------------------------------------------------------------


def _marks(path: Path) -> dict[str, object]:
    try:
        payload = _load(path)
    except (OSError, UnicodeDecodeError, ValueError) as error:
        raise DashboardStateUnreadable(path, str(error)) from error
    if payload is None:
        return {}
    if not isinstance(payload, dict) or payload.get("schema") != REPOSITORIES_SCHEMA:
        raise DashboardStateUnreadable(path, f"not a {REPOSITORIES_SCHEMA} document")
    marks = cast("dict[str, object]", payload).get("repositories")
    if not isinstance(marks, dict):
        raise DashboardStateUnreadable(path, "repositories is not an object")
    return dict(cast("dict[str, object]", marks))


def _write_marks(state_root: Path, marks: Mapping[str, object]) -> None:
    write_json_atomic(
        dashboard_dir(state_root), REPOSITORIES_FILE, {"schema": REPOSITORIES_SCHEMA, "repositories": dict(marks)}
    )


def hide_repository(state_root: Path, repository: GithubRepository, *, now: datetime, timeout: float = 10.0) -> bool:
    """Mark the repository hidden; False when it already was."""
    directory = dashboard_dir(state_root)
    with directory_lock(directory, timeout=timeout):
        marks = _marks(directory / REPOSITORIES_FILE)
        if repository.key in marks:
            return False
        marks[repository.key] = {"hidden_at": _utc(now)}
        _write_marks(state_root, marks)
        return True


def show_repository(state_root: Path, repository: GithubRepository, *, timeout: float = 10.0) -> bool:
    """Remove the hidden mark; False when there was none."""
    directory = dashboard_dir(state_root)
    with directory_lock(directory, timeout=timeout):
        marks = _marks(directory / REPOSITORIES_FILE)
        if repository.key not in marks:
            return False
        del marks[repository.key]
        _write_marks(state_root, marks)
        return True


def hidden_repositories(state_root: Path) -> frozenset[str] | None:
    """The hidden keys; None when the file is unreadable (the server then keeps its last readable marks)."""
    try:
        return frozenset(_marks(dashboard_dir(state_root) / REPOSITORIES_FILE))
    except DashboardStateUnreadable:
        return None


# --- Server location record (D-06) ---------------------------------------------------------------------------


def write_server_record(
    state_root: Path, *, local: str, tailscale: str | None, pid: int, version: str, started_at: str
) -> dict[str, object]:
    record: dict[str, object] = {
        "schema": SERVER_SCHEMA,
        "urls": {"local": local, "tailscale": tailscale},
        "pid": pid,
        "version": version,
        "started_at": started_at,
    }
    write_json_atomic(dashboard_dir(state_root), SERVER_FILE, record)
    return record


def read_server_record(state_root: Path) -> dict[str, object] | None:
    try:
        payload = _load(dashboard_dir(state_root) / SERVER_FILE)
    except (OSError, UnicodeDecodeError, ValueError):
        return None
    if not isinstance(payload, dict) or payload.get("schema") != SERVER_SCHEMA:
        return None
    return cast("dict[str, object]", payload)


def remove_server_record(state_root: Path, *, pid: int, timeout: float = 10.0) -> bool:
    """Remove the record only when it is this process's own (a newer server may have replaced it)."""
    directory = dashboard_dir(state_root)
    with directory_lock(directory, timeout=timeout):
        record = read_server_record(state_root)
        if record is None or record.get("pid") != pid:
            return False
        with suppress(FileNotFoundError):
            (directory / SERVER_FILE).unlink()
        return True


# --- "Seen" records (D-18) -----------------------------------------------------------------------------------


def _seen_document(path: Path) -> dict[str, list[dict[str, object]]]:
    """{key: [record, …]} oldest first; anything unreadable reads as no records."""
    try:
        payload = _load(path)
    except (OSError, UnicodeDecodeError, ValueError):
        return {}
    if not isinstance(payload, dict) or payload.get("schema") != SEEN_SCHEMA:
        return {}
    repositories = cast("dict[str, object]", payload).get("repositories")
    if not isinstance(repositories, dict):
        return {}
    found: dict[str, list[dict[str, object]]] = {}
    for key, value in cast("dict[str, object]", repositories).items():
        records = value.get("records") if isinstance(value, dict) else None
        if isinstance(records, list):
            found[key] = [item for item in records if isinstance(item, dict)]
    return found


def _parse_record(item: Mapping[str, object]) -> SeenRecord | None:
    seen_id, seen_at, scopes = item.get("seen_id"), item.get("seen_at"), item.get("scopes")
    if not isinstance(seen_id, str) or not isinstance(seen_at, str) or not isinstance(scopes, dict):
        return None
    parsed: dict[str, SeenScope] = {}
    for scope_id, value in cast("dict[str, object]", scopes).items():
        if not isinstance(value, dict):
            return None
        state, pr = value.get("state"), value.get("pr")
        if state not in _STATES or (pr is not None and pr not in _PHASES):
            return None
        parsed[scope_id] = SeenScope(state, pr)  # type: ignore[arg-type]
    return SeenRecord(seen_id, seen_at, parsed)


def find_seen(state_root: Path, repository: GithubRepository, seen_id: str | None) -> SeenRecord | None:
    """The record with `seen_id`, or the latest one when `seen_id` is None; None when there is none."""
    records = _seen_document(dashboard_dir(state_root) / SEEN_FILE).get(repository.key, [])
    candidates = reversed(records) if seen_id is None else (item for item in records if item.get("seen_id") == seen_id)
    for item in candidates:
        record = _parse_record(item)
        if record is not None:
            return record
    return None


def append_seen(
    state_root: Path,
    repository: GithubRepository,
    scopes: Mapping[str, SeenScope],
    *,
    now: datetime,
    timeout: float = 10.0,
) -> SeenRecord:
    record = SeenRecord(secrets.token_hex(8), _utc(now), dict(scopes))
    directory = dashboard_dir(state_root)
    with directory_lock(directory, timeout=timeout):
        document = _seen_document(directory / SEEN_FILE)
        records = [*document.get(repository.key, []), _record_json(record)][-SEEN_KEEP:]
        document[repository.key] = records
        write_json_atomic(
            directory,
            SEEN_FILE,
            {"schema": SEEN_SCHEMA, "repositories": {key: {"records": value} for key, value in document.items()}},
        )
    return record


def _record_json(record: SeenRecord) -> dict[str, object]:
    return {
        "seen_id": record.seen_id,
        "seen_at": record.seen_at,
        "scopes": {key: {"state": value.state, "pr": value.pr} for key, value in record.scopes.items()},
    }
