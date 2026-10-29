"""The per-user GitHub structure snapshot (contract C10): storage, freshness levels and write reflection.

Network calls happen outside the directory lock; inside it the store only re-reads, merges and renames.
A state root that cannot be written keeps the snapshot in this process's memory instead of failing.
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from datetime import timedelta
import errno
import json
import math
import os
import secrets
import time
from typing import TYPE_CHECKING, Final, Literal, TypeVar, cast

from spec_dock.runtime.domain.canonical_structure import (
    KIND_LABELS,
    SnapshotFormatError,
    StructureSnapshot,
    UpsertIssue,
    apply_changes_lenient,
    build_snapshot,
    format_timestamp,
    merge_refresh,
    parse_timestamp,
)
from spec_dock.runtime.infra.github_structure import (
    GITHUB_RESPONSE_INVALID,
    GITHUB_UNAVAILABLE,
    SYSTEM_CLOCK,
    GithubApi,
    GithubStructureClient,
    GithubStructureError,
)
from spec_dock.runtime.infra.state_root import resolve_state_root

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping, Sequence
    from pathlib import Path

    from spec_dock.runtime.domain.canonical_structure import StructureChange
    from spec_dock.runtime.infra.github_structure import GithubClock, GithubRepository

FreshnessLevel = Literal["display", "decision", "cycle"]
ProbeOutcome = Literal["unchanged", "changed", "skipped", "failed"]
PROBE_VERSION: Final = 1
PROBE_INTERVAL: Final = timedelta(seconds=60)
MAX_AGE: Final[Mapping[FreshnessLevel, timedelta]] = {
    "display": timedelta(minutes=30),
    "decision": timedelta(minutes=5),
    "cycle": timedelta(minutes=30),
}
GITHUB_SNAPSHOT_STALE: Final = "GITHUB_SNAPSHOT_STALE"
SNAPSHOT_FILE: Final = "snapshot.json"
PROBE_FILE: Final = "probe.json"

_T = TypeVar("_T")
_MEMORY: dict[str, tuple[StructureSnapshot | None, ProbeRecord | None]] = {}


def clear_memory() -> None:
    """Forget in-process snapshots; for tests that simulate a new process."""
    _MEMORY.clear()


@dataclass(frozen=True)
class Reflection:
    """A write reflection: the resulting snapshot and the changes it could not apply (they mark it stale)."""

    snapshot: StructureSnapshot | None
    skipped: tuple[StructureChange, ...]


@dataclass(frozen=True)
class ProbeRecord:
    checked_at: str | None
    etags: Mapping[str, str | None]
    last_error: Mapping[str, str] | None

    def to_json(self) -> dict[str, object]:
        return {
            "version": PROBE_VERSION,
            "checked_at": self.checked_at,
            "etags": {label: self.etags.get(label) for label in KIND_LABELS.values()},
            "last_error": dict(self.last_error) if self.last_error is not None else None,
        }

    @classmethod
    def from_json(cls, payload: object) -> ProbeRecord:
        if not isinstance(payload, dict) or set(payload) != {"version", "checked_at", "etags", "last_error"}:
            raise SnapshotFormatError("probe record has unexpected keys")
        if type(payload["version"]) is not int or payload["version"] != PROBE_VERSION:
            raise SnapshotFormatError("unknown probe record version")
        checked = payload["checked_at"]
        if checked is not None:
            if not isinstance(checked, str):
                raise SnapshotFormatError("checked_at must be a string")
            parse_timestamp(checked)
        etags = payload["etags"]
        if not isinstance(etags, dict) or any(
            not isinstance(key, str) or (value is not None and not isinstance(value, str))
            for key, value in etags.items()
        ):
            raise SnapshotFormatError("etags must map labels to strings")
        error = payload["last_error"]
        if error is not None and (
            not isinstance(error, dict)
            or set(error) != {"code", "message", "at"}
            or not all(isinstance(value, str) for value in error.values())
        ):
            raise SnapshotFormatError("last_error must have code, message and at")
        return cls(checked, dict(etags), dict(error) if error is not None else None)


class SnapshotStore:
    """One repository's snapshot.json and probe.json under the state root, or process memory."""

    def __init__(self, state_root: Path, repository: GithubRepository, *, lock_timeout: float = 10.0) -> None:
        if not math.isfinite(lock_timeout) or not 0 <= lock_timeout <= 300:
            raise ValueError("snapshot lock timeout must be finite and between 0 and 300 seconds")
        self.repository = repository
        self.directory = state_root / "github" / repository.host / repository.owner / repository.name
        self.lock_timeout = lock_timeout
        self.persisted = True

    def load(self) -> tuple[StructureSnapshot | None, ProbeRecord | None]:
        """Read without the lock (renames keep files whole); never raises."""
        return _choose(*self._sources())

    def _sources(
        self,
    ) -> tuple[StructureSnapshot | None, ProbeRecord | None, StructureSnapshot | None, ProbeRecord | None]:
        disk_snapshot = self._read(SNAPSHOT_FILE, StructureSnapshot.from_json)
        if disk_snapshot is not None and disk_snapshot.repository != self.repository.key:
            disk_snapshot = None
        disk_probe = self._read(PROBE_FILE, ProbeRecord.from_json)
        memory_snapshot, memory_probe = _MEMORY.get(str(self.directory), (None, None))
        return disk_snapshot, disk_probe, memory_snapshot, memory_probe

    def commit_refresh(self, fresh: StructureSnapshot, probe: ProbeRecord) -> StructureSnapshot:
        """Write a refetch after overlaying writes reflected since it started; never replace a newer refetch."""

        def change(
            current: StructureSnapshot | None, current_probe: ProbeRecord | None
        ) -> tuple[StructureSnapshot | None, ProbeRecord | None]:
            if current is not None and parse_timestamp(current.fetch_started_at) > parse_timestamp(
                fresh.fetch_started_at
            ):
                return current, current_probe
            return merge_refresh(current, fresh), probe

        snapshot, _ = self._update(change)
        return cast("StructureSnapshot", snapshot)

    def save_probe(self, probe: ProbeRecord) -> None:
        """Record a check unless another process already recorded a later one."""

        def change(
            current: StructureSnapshot | None, current_probe: ProbeRecord | None
        ) -> tuple[StructureSnapshot | None, ProbeRecord | None]:
            if _later(current_probe, probe):
                return current, current_probe
            return current, probe

        self._update(change)

    def record_probe_error(self, error: Mapping[str, str]) -> None:
        """Keep the latest ETags and check time; only the failure is recorded."""

        def change(
            current: StructureSnapshot | None, current_probe: ProbeRecord | None
        ) -> tuple[StructureSnapshot | None, ProbeRecord | None]:
            base = current_probe or ProbeRecord(None, {}, None)
            return current, ProbeRecord(base.checked_at, base.etags, dict(error))

        self._update(change)

    def reflect(self, changes: Sequence[StructureChange], *, command: str, at: str) -> StructureSnapshot | None:
        return self.reflect_writes(changes, command=command, at=at).snapshot

    def reflect_writes(self, changes: Sequence[StructureChange], *, command: str, at: str) -> Reflection:
        """Apply what fits; when a change is skipped, clear the check record so every level refetches next."""
        skipped: tuple[StructureChange, ...] = ()

        def change(
            current: StructureSnapshot | None, current_probe: ProbeRecord | None
        ) -> tuple[StructureSnapshot | None, ProbeRecord | None]:
            nonlocal skipped
            if current is None:
                skipped = tuple(changes)
                return None, current_probe
            applied, skipped = apply_changes_lenient(current, changes, at=at, command=command)
            if not skipped:
                return applied, current_probe
            error = current_probe.last_error if current_probe is not None else None
            return applied, ProbeRecord(None, {}, error)

        snapshot, _ = self._update(change)
        return Reflection(snapshot, skipped)

    def _update(
        self,
        change: Callable[
            [StructureSnapshot | None, ProbeRecord | None], tuple[StructureSnapshot | None, ProbeRecord | None]
        ],
    ) -> tuple[StructureSnapshot | None, ProbeRecord | None]:
        """Re-read under the lock, apply once, and write only what differs from the files."""
        computed: tuple[StructureSnapshot | None, ProbeRecord | None] | None = None
        try:
            with self._locked() as descriptor:
                disk_snapshot, disk_probe, memory_snapshot, memory_probe = self._sources()
                computed = change(*_choose(disk_snapshot, disk_probe, memory_snapshot, memory_probe))
                snapshot, probe = computed
                if snapshot is not None and snapshot is not disk_snapshot:
                    _write_json(descriptor, SNAPSHOT_FILE, snapshot.to_json())
                if probe is not None and probe is not disk_probe:
                    _write_json(descriptor, PROBE_FILE, probe.to_json())
        except OSError:
            if computed is None:
                computed = change(*self.load())
            _MEMORY[str(self.directory)] = computed
            self.persisted = False
            return computed
        _MEMORY.pop(str(self.directory), None)
        self.persisted = True
        return computed

    def _locked(self) -> _DirectoryLock:
        return _DirectoryLock(self.directory, self.lock_timeout)

    def _read(self, name: str, decode: Callable[[object], _T]) -> _T | None:
        try:
            with (self.directory / name).open("rb") as stream:
                return decode(json.load(stream))
        except (OSError, ValueError, RecursionError):
            return None


def _choose(
    disk_snapshot: StructureSnapshot | None,
    disk_probe: ProbeRecord | None,
    memory_snapshot: StructureSnapshot | None,
    memory_probe: ProbeRecord | None,
) -> tuple[StructureSnapshot | None, ProbeRecord | None]:
    return (
        _newer(disk_snapshot, memory_snapshot, lambda item: item.fetched_at),
        _newer(disk_probe, memory_probe, lambda item: item.checked_at),
    )


def _later(current: ProbeRecord | None, candidate: ProbeRecord) -> bool:
    """True when the stored check is strictly later than the candidate's."""
    if current is None or current.checked_at is None or candidate.checked_at is None:
        return False
    return parse_timestamp(current.checked_at) > parse_timestamp(candidate.checked_at)


def _newer(first: _T | None, second: _T | None, key: Callable[[_T], str | None]) -> _T | None:
    if first is None or second is None:
        return first if second is None else second
    first_key, second_key = key(first), key(second)
    if first_key is None or second_key is None:
        return first if second_key is None else second
    # Memory exists only after a failed write, so on a tie it holds the later reflection.
    return second if parse_timestamp(second_key) >= parse_timestamp(first_key) else first


class _DirectoryLock:
    """flock on the opened directory; no lock file is created."""

    def __init__(self, directory: Path, timeout: float) -> None:
        self.directory = directory
        self.timeout = timeout
        self.descriptor: int | None = None

    def __enter__(self) -> int:
        import fcntl

        self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        descriptor = os.open(self.directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        deadline = time.monotonic() + self.timeout
        try:
            while True:
                try:
                    fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError as error:
                    if time.monotonic() >= deadline:
                        raise OSError(errno.EWOULDBLOCK, "structure snapshot lock is busy") from error
                    time.sleep(0.05)
        except BaseException:
            os.close(descriptor)
            raise
        self.descriptor = descriptor
        return descriptor

    def __exit__(self, *exc: object) -> None:
        if self.descriptor is not None:
            import fcntl

            descriptor, self.descriptor = self.descriptor, None
            try:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
            finally:
                os.close(descriptor)


def _write_json(directory: int, name: str, payload: object) -> None:
    data = (json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    temporary = f".{name}.{secrets.token_hex(8)}.tmp"
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=directory)
    try:
        try:
            view = memoryview(data)
            while view:
                view = view[os.write(descriptor, view) :]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.replace(temporary, name, src_dir_fd=directory, dst_dir_fd=directory)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(temporary, dir_fd=directory)
        raise
    os.fsync(directory)


@dataclass(frozen=True)
class SnapshotWarning:
    code: str
    message: str
    details: Mapping[str, object]


@dataclass(frozen=True)
class FreshSnapshot:
    snapshot: StructureSnapshot | None
    stale: bool
    probe: ProbeOutcome
    refreshed: bool
    warning: SnapshotWarning | None = None
    graphql_cost: int | None = None

    def require(self) -> StructureSnapshot:
        if self.snapshot is None:
            raise GithubStructureError(GITHUB_UNAVAILABLE, "no structure snapshot is available")
        return self.snapshot

    def payload(self) -> dict[str, object]:
        """The `data.snapshot` object of commands that show structure."""
        return {"fetched_at": self.snapshot.fetched_at if self.snapshot else None, "stale": self.stale}


class StructureSnapshotService:
    """Decide probes and refetches per freshness level and keep the store in step with SpecDock writes."""

    def __init__(
        self,
        repository: GithubRepository,
        *,
        store: SnapshotStore,
        client: GithubStructureClient,
        clock: GithubClock = SYSTEM_CLOCK,
    ) -> None:
        self.repository = repository
        self.store = store
        self.client = client
        self.clock = clock

    def ensure_fresh(self, level: FreshnessLevel) -> FreshSnapshot:
        if level not in MAX_AGE:
            raise ValueError(f"unknown freshness level: {level!r}")
        snapshot, probe = self.store.load()
        now = self.clock.now()
        must_probe = (
            level != "display"
            or probe is None
            or probe.checked_at is None
            or now - parse_timestamp(probe.checked_at) > PROBE_INTERVAL
        )
        too_old = snapshot is None or now - parse_timestamp(snapshot.fetched_at) > MAX_AGE[level]
        if not must_probe and not too_old:
            return FreshSnapshot(snapshot, False, "skipped", False)
        return self._probe_and_fetch(level, snapshot, probe, force=too_old)

    def refresh(self) -> FreshSnapshot:
        """Refetch now (`--source github`); a failure stops like a decision."""
        snapshot, probe = self.store.load()
        return self._probe_and_fetch("decision", snapshot, probe, force=True)

    def reread(self, numbers: Iterable[int], *, command: str) -> StructureSnapshot:
        """Read the Issues a write decision depends on and reflect what GitHub reports now."""
        changes = [UpsertIssue(self.client.get_issue(number)) for number in numbers]
        try:
            reflected = self.reflect(changes, command=f"{command} (reread)")
        except ValueError as invalid:
            raise GithubStructureError(GITHUB_RESPONSE_INVALID, f"GitHub Issue is malformed: {invalid}") from invalid
        if reflected is None:
            raise GithubStructureError(GITHUB_UNAVAILABLE, "no structure snapshot is available to update")
        return reflected

    def reflect(self, changes: Sequence[StructureChange], *, command: str) -> StructureSnapshot | None:
        return self.reflect_writes(changes, command=command).snapshot

    def reflect_writes(self, changes: Sequence[StructureChange], *, command: str) -> Reflection:
        return self.store.reflect_writes(changes, command=command, at=format_timestamp(self.clock.now()))

    def _probe_and_fetch(
        self,
        level: FreshnessLevel,
        snapshot: StructureSnapshot | None,
        probe: ProbeRecord | None,
        *,
        force: bool,
    ) -> FreshSnapshot:
        etags = probe.etags if probe is not None else {}
        checked_at = format_timestamp(self.clock.now())
        try:
            result = self.client.probe(etags)
            if not result.changed and not force:
                self.store.save_probe(ProbeRecord(checked_at, result.etags, None))
                return FreshSnapshot(snapshot, False, "unchanged", False)
            started = format_timestamp(self.clock.now())
            fetched = self.client.fetch_structure()
            try:
                fresh = build_snapshot(
                    self.repository.key,
                    fetched,
                    fetched_at=format_timestamp(self.clock.now()),
                    fetch_started_at=started,
                )
            except ValueError as invalid:
                raise GithubStructureError(
                    GITHUB_RESPONSE_INVALID, f"GitHub structure is malformed: {invalid}"
                ) from invalid
        except GithubStructureError as error:
            return self._degrade(level, snapshot, error)
        written = self.store.commit_refresh(fresh, ProbeRecord(checked_at, result.etags, None))
        return FreshSnapshot(
            written,
            False,
            "changed" if result.changed else "unchanged",
            True,
            graphql_cost=self.client.last_graphql_cost,
        )

    def _degrade(
        self, level: FreshnessLevel, snapshot: StructureSnapshot | None, error: GithubStructureError
    ) -> FreshSnapshot:
        """Keep old ETags and the check time so the next probe still sees the change; record only the error."""
        self.store.record_probe_error({
            "code": error.code,
            "message": error.message,
            "at": format_timestamp(self.clock.now()),
        })
        if level == "cycle":
            return FreshSnapshot(snapshot, True, "failed", False)
        if level == "display" and snapshot is not None:
            warning = SnapshotWarning(
                GITHUB_SNAPSHOT_STALE,
                f"showing the structure snapshot fetched at {snapshot.fetched_at}; GitHub could not be read",
                {"fetched_at": snapshot.fetched_at, "cause": error.code},
            )
            return FreshSnapshot(snapshot, True, "failed", False, warning)
        raise error


def ensure_fresh(
    repository: GithubRepository,
    level: FreshnessLevel,
    *,
    state_root: Path | None = None,
    api: GithubApi | None = None,
) -> FreshSnapshot:
    """Default wiring for commands and the periodic cycle."""
    caller = api or GithubApi()
    service = StructureSnapshotService(
        repository,
        store=SnapshotStore(state_root or resolve_state_root(), repository),
        client=GithubStructureClient(repository, caller),
        clock=caller.clock,
    )
    return service.ensure_fresh(level)
