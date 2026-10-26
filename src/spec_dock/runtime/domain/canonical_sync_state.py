"""Version-1 records of the state root (contract C9): per-catalog sync state, the registry, accepts and the runner.

These are the JSON shapes of Epic ch. 5. A reader refuses an unknown version or a malformed field
(StateFormatError) so that nothing it does not understand is ever rewritten.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
import hashlib
from typing import TYPE_CHECKING, Final, Literal, cast

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

STATE_VERSION: Final = 1
REGISTRY_VERSION: Final = 1
ACCEPTED_VERSION: Final = 1
RUNNER_VERSION: Final = 1
CONSUMED_CHANGESETS_KEPT: Final = 100

SchedulerKind = Literal["launchd", "systemd", "loop"]
SCHEDULER_KINDS: Final[frozenset[str]] = frozenset({"launchd", "systemd", "loop"})
PauseReason = Literal["remote_rewritten", "remote_deleted", "merge_failed"]
PAUSE_REASONS: Final[frozenset[str]] = frozenset({"remote_rewritten", "remote_deleted", "merge_failed"})
CycleOutcome = Literal["ok", "skipped", "error", "paused"]
HOLD_KINDS: Final[frozenset[str]] = frozenset({"mass_delete", "secret", "too_large"})
BLOCKING_REASONS: Final[frozenset[str]] = frozenset({"local_edit", "held"})
PushAuthResult = Literal["ok", "failed", "unknown"]


class StateFormatError(ValueError):
    """A state-root file has an unknown version or a malformed field."""


def state_key(catalog: str) -> str:
    """The first 16 hex digits of the SHA-256 of the catalog's real path."""
    return hashlib.sha256(catalog.encode("utf-8", "surrogateescape")).hexdigest()[:16]


def _object(value: object, what: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise StateFormatError(f"{what} must be a JSON object")
    return cast("dict[str, object]", value)


def _list(value: object, what: str) -> list[object]:
    if not isinstance(value, list):
        raise StateFormatError(f"{what} must be a JSON array")
    return value


def _text(value: object, what: str) -> str:
    if not isinstance(value, str):
        raise StateFormatError(f"{what} must be a string")
    return value


def _optional_text(value: object, what: str) -> str | None:
    return None if value is None else _text(value, what)


def _choice(value: object, choices: frozenset[str], what: str) -> str:
    if not isinstance(value, str) or value not in choices:
        raise StateFormatError(f"{what} must be one of {sorted(choices)}")
    return value


def _version(payload: dict[str, object], expected: int, what: str) -> None:
    version = payload.get("version")
    if type(version) is not int or version != expected:
        raise StateFormatError(f"{what} version must be {expected}")


@dataclass(frozen=True)
class LastCycle:
    started_at: str
    finished_at: str
    result: CycleOutcome

    def to_json(self) -> dict[str, object]:
        return {"started_at": self.started_at, "finished_at": self.finished_at, "result": self.result}

    @classmethod
    def from_json(cls, value: object) -> LastCycle:
        payload = _object(value, "last_cycle")
        result = _choice(payload.get("result"), frozenset({"ok", "skipped", "error", "paused"}), "last_cycle.result")
        return cls(
            _text(payload.get("started_at"), "last_cycle.started_at"),
            _text(payload.get("finished_at"), "last_cycle.finished_at"),
            cast("CycleOutcome", result),
        )


@dataclass(frozen=True)
class SyncError:
    code: str
    message: str
    next_step: str | None = None
    program: tuple[str, ...] | None = None
    at: str | None = None

    def to_json(self) -> dict[str, object]:
        payload: dict[str, object] = {"code": self.code, "message": self.message, "next_step": self.next_step}
        if self.program is not None:
            payload["program"] = list(self.program)
        payload["at"] = self.at
        return payload

    @classmethod
    def from_json(cls, value: object) -> SyncError:
        payload = _object(value, "last_error")
        program = payload.get("program")
        return cls(
            _text(payload.get("code"), "last_error.code"),
            _text(payload.get("message"), "last_error.message"),
            _optional_text(payload.get("next_step"), "last_error.next_step"),
            None if program is None else tuple(_text(item, "last_error.program") for item in _list(program, "program")),
            _optional_text(payload.get("at"), "last_error.at"),
        )


@dataclass(frozen=True)
class Hold:
    path: str
    kind: str
    since: str

    def to_json(self) -> dict[str, object]:
        return {"path": self.path, "kind": self.kind, "since": self.since}

    @classmethod
    def from_json(cls, value: object) -> Hold:
        payload = _object(value, "hold")
        return cls(
            _text(payload.get("path"), "hold.path"),
            _choice(payload.get("kind"), HOLD_KINDS, "hold.kind"),
            _text(payload.get("since"), "hold.since"),
        )


@dataclass(frozen=True)
class ConflictCopy:
    path: str
    copy: str
    at: str

    def to_json(self) -> dict[str, object]:
        return {"path": self.path, "copy": self.copy, "at": self.at}

    @classmethod
    def from_json(cls, value: object) -> ConflictCopy:
        payload = _object(value, "conflict")
        return cls(
            _text(payload.get("path"), "conflict.path"),
            _text(payload.get("copy"), "conflict.copy"),
            _text(payload.get("at"), "conflict.at"),
        )


@dataclass(frozen=True)
class Blocking:
    path: str
    reason: str

    def to_json(self) -> dict[str, object]:
        return {"path": self.path, "reason": self.reason}

    @classmethod
    def from_json(cls, value: object) -> Blocking:
        payload = _object(value, "blocking")
        return cls(
            _text(payload.get("path"), "blocking.path"), _choice(payload.get("reason"), BLOCKING_REASONS, "reason")
        )


@dataclass(frozen=True)
class PushAuth:
    result: PushAuthResult
    at: str | None
    message: str | None = None

    def to_json(self) -> dict[str, object]:
        return {"result": self.result, "at": self.at, "message": self.message}

    @classmethod
    def from_json(cls, value: object) -> PushAuth:
        payload = _object(value, "push_auth")
        result = _choice(payload.get("result"), frozenset({"ok", "failed", "unknown"}), "push_auth.result")
        return cls(
            cast("PushAuthResult", result),
            _optional_text(payload.get("at"), "push_auth.at"),
            _optional_text(payload.get("message"), "push_auth.message"),
        )


@dataclass(frozen=True)
class CatalogSyncState:
    """`<state root>/catalogs/<key>/state.json`; written only by the sync, canonical link and resume."""

    catalog: str
    updated_at: str
    last_cycle: LastCycle | None = None
    last_success_at: str | None = None
    last_error: SyncError | None = None
    paused: PauseReason | None = None
    head: str | None = None
    last_seen_remote: str | None = None
    remote_contains_head: bool | None = None
    unpushed_since: str | None = None
    pending_since: Mapping[str, str] = field(default_factory=dict)
    holds: tuple[Hold, ...] = ()
    conflicts: tuple[ConflictCopy, ...] = ()
    blocking: tuple[Blocking, ...] = ()
    consumed_changesets: tuple[str, ...] = ()
    push_auth: PushAuth | None = None
    dashboard: Mapping[str, object] | None = None  # iss-00438 owns its meaning; kept as read
    adopt_remote_pending: bool = False  # resume --adopt-remote: re-adopt on top of R with R as the only parent
    schedule: Literal["none"] | None = None  # canonical link --no-schedule: link_after_command skips step 6

    @classmethod
    def new(cls, catalog: str, *, at: str) -> CatalogSyncState:
        return cls(catalog, at, push_auth=PushAuth("unknown", at))

    def evolve(self, **changes: object) -> CatalogSyncState:
        return replace(self, **changes)  # type: ignore[arg-type]

    def to_json(self) -> dict[str, object]:
        return {
            "version": STATE_VERSION,
            "catalog": self.catalog,
            "updated_at": self.updated_at,
            "last_cycle": self.last_cycle.to_json() if self.last_cycle else None,
            "last_success_at": self.last_success_at,
            "last_error": self.last_error.to_json() if self.last_error else None,
            "paused": self.paused,
            "head": self.head,
            "last_seen_remote": self.last_seen_remote,
            "remote_contains_head": self.remote_contains_head,
            "unpushed_since": self.unpushed_since,
            "pending_since": dict(self.pending_since),
            "holds": [item.to_json() for item in self.holds],
            "conflicts": [item.to_json() for item in self.conflicts],
            "blocking": [item.to_json() for item in self.blocking],
            "consumed_changesets": list(self.consumed_changesets[-CONSUMED_CHANGESETS_KEPT:]),
            "push_auth": self.push_auth.to_json() if self.push_auth else None,
            "dashboard": dict(self.dashboard) if self.dashboard is not None else None,
            "adopt_remote_pending": self.adopt_remote_pending,
            "schedule": self.schedule,
        }

    @classmethod
    def from_json(cls, value: object) -> CatalogSyncState:
        payload = _object(value, "state")
        _version(payload, STATE_VERSION, "state")

        def optional(key: str, parse: Callable[[object], object]) -> object:
            item = payload.get(key)
            return None if item is None else parse(item)

        pending = _object(payload.get("pending_since", {}), "pending_since")
        contains = payload.get("remote_contains_head")
        if contains is not None and not isinstance(contains, bool):
            raise StateFormatError("remote_contains_head must be a boolean")
        allow = payload.get("adopt_remote_pending", False)
        if not isinstance(allow, bool):
            raise StateFormatError("adopt_remote_pending must be a boolean")
        dashboard = payload.get("dashboard")
        paused = payload.get("paused")
        schedule = payload.get("schedule")
        if schedule not in (None, "none"):
            raise StateFormatError('schedule must be "none" or null')
        return cls(
            catalog=_text(payload.get("catalog"), "catalog"),
            updated_at=_text(payload.get("updated_at"), "updated_at"),
            last_cycle=cast("LastCycle | None", optional("last_cycle", LastCycle.from_json)),
            last_success_at=_optional_text(payload.get("last_success_at"), "last_success_at"),
            last_error=cast("SyncError | None", optional("last_error", SyncError.from_json)),
            paused=None if paused is None else cast("PauseReason", _choice(paused, PAUSE_REASONS, "paused")),
            head=_optional_text(payload.get("head"), "head"),
            last_seen_remote=_optional_text(payload.get("last_seen_remote"), "last_seen_remote"),
            remote_contains_head=contains,
            unpushed_since=_optional_text(payload.get("unpushed_since"), "unpushed_since"),
            pending_since={_text(key, "path"): _text(item, "pending_since") for key, item in pending.items()},
            holds=tuple(Hold.from_json(item) for item in _list(payload.get("holds", []), "holds")),
            conflicts=tuple(ConflictCopy.from_json(item) for item in _list(payload.get("conflicts", []), "conflicts")),
            blocking=tuple(Blocking.from_json(item) for item in _list(payload.get("blocking", []), "blocking")),
            consumed_changesets=tuple(
                _text(item, "consumed_changesets") for item in _list(payload.get("consumed_changesets", []), "consumed")
            ),
            push_auth=cast("PushAuth | None", optional("push_auth", PushAuth.from_json)),
            dashboard=None if dashboard is None else _object(dashboard, "dashboard"),
            adopt_remote_pending=allow,
            schedule=cast("Literal['none'] | None", schedule),
        )


def holds_under(state: CatalogSyncState, prefix: str) -> tuple[Hold, ...]:
    """Holds at `prefix` or below it (a Scope directory relative to the catalog root)."""
    base = prefix.strip("/")
    return tuple(hold for hold in state.holds if hold.path == base or hold.path.startswith(base + "/"))


@dataclass(frozen=True)
class RegistryEntry:
    catalog: str
    main_checkout: str
    repository: str | None
    git: str
    registered_at: str

    def to_json(self) -> dict[str, object]:
        return {
            "catalog": self.catalog,
            "main_checkout": self.main_checkout,
            "repository": self.repository,
            "git": self.git,
            "registered_at": self.registered_at,
        }

    @classmethod
    def from_json(cls, value: object) -> RegistryEntry:
        payload = _object(value, "registry entry")
        return cls(
            _text(payload.get("catalog"), "catalog"),
            _text(payload.get("main_checkout"), "main_checkout"),
            _optional_text(payload.get("repository"), "repository"),
            _text(payload.get("git"), "git"),
            _text(payload.get("registered_at"), "registered_at"),
        )


@dataclass(frozen=True)
class SyncRegistry:
    """`<state root>/canonical-registry.json`: the catalogs this user's periodic job syncs."""

    scheduler: SchedulerKind | None
    catalogs: tuple[RegistryEntry, ...]

    def entry_for(self, catalog: str) -> RegistryEntry | None:
        return next((entry for entry in self.catalogs if entry.catalog == catalog), None)

    def with_entry(self, entry: RegistryEntry) -> SyncRegistry:
        if self.entry_for(entry.catalog) is None:
            return replace(self, catalogs=(*self.catalogs, entry))
        return replace(self, catalogs=tuple(entry if item.catalog == entry.catalog else item for item in self.catalogs))

    def without(self, catalog: str) -> SyncRegistry:
        return replace(self, catalogs=tuple(item for item in self.catalogs if item.catalog != catalog))

    def to_json(self) -> dict[str, object]:
        return {
            "version": REGISTRY_VERSION,
            "scheduler": self.scheduler,
            "catalogs": [entry.to_json() for entry in self.catalogs],
        }

    @classmethod
    def from_json(cls, value: object) -> SyncRegistry:
        payload = _object(value, "registry")
        _version(payload, REGISTRY_VERSION, "registry")
        scheduler = payload.get("scheduler")
        return cls(
            None if scheduler is None else cast("SchedulerKind", _choice(scheduler, SCHEDULER_KINDS, "scheduler")),
            tuple(RegistryEntry.from_json(item) for item in _list(payload.get("catalogs"), "catalogs")),
        )


@dataclass(frozen=True)
class AcceptedChanges:
    """`<catalog>/.runtime/accepted.json`: content the user allowed despite a hold."""

    paths: Mapping[str, str]
    deletions: tuple[str, ...]

    @classmethod
    def empty(cls) -> AcceptedChanges:
        return cls({}, ())

    def to_json(self) -> dict[str, object]:
        return {
            "version": ACCEPTED_VERSION,
            "paths": dict(sorted(self.paths.items())),
            "deletions": list(self.deletions),
        }

    @classmethod
    def from_json(cls, value: object) -> AcceptedChanges:
        payload = _object(value, "accepted")
        _version(payload, ACCEPTED_VERSION, "accepted")
        paths = _object(payload.get("paths"), "accepted.paths")
        return cls(
            {_text(key, "path"): _text(item, "blob") for key, item in paths.items()},
            tuple(_text(item, "deletion") for item in _list(payload.get("deletions"), "accepted.deletions")),
        )


@dataclass(frozen=True)
class RunnerRecord:
    """`<state root>/runner.json`, written by the resident runner while it holds runner.lock."""

    pid: int
    started_at: str
    spec_dock_version: str

    def to_json(self) -> dict[str, object]:
        return {
            "version": RUNNER_VERSION,
            "pid": self.pid,
            "started_at": self.started_at,
            "spec_dock_version": self.spec_dock_version,
        }

    @classmethod
    def from_json(cls, value: object) -> RunnerRecord:
        payload = _object(value, "runner")
        _version(payload, RUNNER_VERSION, "runner")
        pid = payload.get("pid")
        if type(pid) is not int or pid <= 0:
            raise StateFormatError("runner pid must be a positive integer")
        return cls(pid, _text(payload.get("started_at"), "started_at"), _text(payload.get("spec_dock_version"), "ver"))
