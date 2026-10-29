"""The periodic-sync parts of `canonical status` (iss-00430): sync, snapshot, state.json changes, registered git.

Everything here reads: the registry, state.json, probe.json and snapshot.json, the job (launchctl print,
systemctl is-active, the runner lock probe) and Git configuration. It never writes and never contacts GitHub
or the remote.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import os
from pathlib import Path
from typing import TYPE_CHECKING, Final, cast

from spec_dock.runtime.application.canonical_errors import (
    CANONICAL_DASHBOARD_OCCUPIED,
    CANONICAL_LINGER_DISABLED,
    CANONICAL_PAUSED,
    CANONICAL_PUSH_AUTH_FAILED,
    CANONICAL_REGISTRY_UNREADABLE,
    CANONICAL_RUNNER_STOPPED,
    CANONICAL_SAVE_HELD,
    CANONICAL_STATE_ROOT_MISMATCH,
    CANONICAL_STATE_UNREADABLE,
    CANONICAL_SYNC_BLOCKED,
    CANONICAL_SYNC_FAILED,
    CANONICAL_SYNC_NOT_CONFIRMED,
    CANONICAL_SYNC_NOT_SCHEDULED,
    CANONICAL_UNPUSHED_STALE,
    DASHBOARD_FAILED_NEXT_STEP,
    DASHBOARD_MISSING_NEXT_STEP,
    DASHBOARD_OCCUPIED_NEXT_STEP,
    LINGER_NEXT_STEP,
    PAUSED_NEXT_STEP,
    PRIVACY_NEXT_STEP,
    REGISTRY_UNREADABLE_RECOVERY,
    SAVE_HELD_NEXT_STEPS,
    STATE_ROOT_MISMATCH_NEXT_STEP,
    STATE_UNREADABLE_NEXT_STEP,
    STATUS_RECOVERY,
    SYNC_BLOCKED_NEXT_STEP,
    SYNC_LOG_NEXT_STEP,
    SYNC_NOT_SCHEDULED_NEXT_STEP,
    UNPUSHED_STALE_NEXT_STEP,
)
from spec_dock.runtime.domain.canonical_scheduler import SchedulerSpec, restart_line
from spec_dock.runtime.domain.canonical_structure import parse_timestamp
from spec_dock.runtime.infra import canonical_git, canonical_scheduling, runtime_environment
from spec_dock.runtime.infra.canonical_registry import RegistryUnreadable, read_registry
from spec_dock.runtime.infra.canonical_state import StateUnreadable, catalog_state_dir, read_catalog_state
from spec_dock.runtime.infra.git_process import GitProcessError
from spec_dock.runtime.infra.state_root import resolve_state_root

if TYPE_CHECKING:
    from datetime import datetime

    from spec_dock.runtime.application.canonical_status import Problem
    from spec_dock.runtime.domain.canonical_layout import CatalogLayout
    from spec_dock.runtime.domain.canonical_sync_state import CatalogSyncState, RegistryEntry, SyncRegistry
    from spec_dock.runtime.infra.runtime_environment import RuntimeEnvironment

UNPUSHED_LIMIT: Final = timedelta(minutes=10)
CYCLE_SILENCE_LIMIT: Final = timedelta(minutes=5)  # five missed 60-second cycles


def _silent(finished_at: str) -> bool:
    try:
        return _now() - parse_timestamp(finished_at) > CYCLE_SILENCE_LIMIT
    except ValueError:
        return False


def _now() -> datetime:
    from spec_dock.runtime.application import canonical_sync

    return canonical_sync.SYNC_CLOCK.now()


@dataclass
class SyncView:
    layout: CatalogLayout
    environment: RuntimeEnvironment
    problem: Problem
    state_root: Path
    catalog: str
    registry: SyncRegistry | None
    entry: RegistryEntry | None
    state: CatalogSyncState | None
    timeout: float

    @classmethod
    def read(
        cls, layout: CatalogLayout, environment: RuntimeEnvironment, problem: Problem, *, timeout: float
    ) -> SyncView:
        root = resolve_state_root(dict(environment.environ))
        catalog = os.path.realpath(layout.catalog)
        registry = None
        try:
            registry = read_registry(root)
        except RegistryUnreadable as error:
            problem(
                "sync",
                CANONICAL_REGISTRY_UNREADABLE,
                f"the sync registry cannot be read ({error.reason})",
                REGISTRY_UNREADABLE_RECOVERY,
                path=str(error.path),
            )
        state = None
        try:
            state = read_catalog_state(root, catalog)
        except StateUnreadable as error:
            problem(
                "sync",
                CANONICAL_STATE_UNREADABLE,
                f"the catalog's sync state cannot be read ({error.reason})",
                STATE_UNREADABLE_NEXT_STEP,
                path=str(error.path),
            )
        entry = registry.entry_for(catalog) if registry is not None else None
        return cls(layout, environment, problem, root, catalog, registry, entry, state, timeout)

    def sync_item(self) -> dict[str, object]:
        state, registry = self.state, self.registry
        kind = registry.scheduler if registry is not None and self.entry is not None else None
        item: dict[str, object] = {
            "status": "ok",
            "next_step": None,
            "state_root": str(self.state_root),
            "state_path": str(catalog_state_dir(self.state_root, self.catalog) / "state.json"),
            "registered": self.entry is not None,
            "scheduler": kind,
            "job": None,
            "linger": None,
            "push_auth": state.push_auth.to_json() if state and state.push_auth else None,
            "last_cycle": state.last_cycle.to_json() if state and state.last_cycle else None,
            "last_success_at": state.last_success_at if state else None,
            "last_error": state.last_error.to_json() if state and state.last_error else None,
            "paused": state.paused if state else None,
        }
        steps: list[str] = []

        def note(code: str, message: str, step: str, **details: object) -> None:
            steps.append(self.problem("sync", code, message, step, **details))

        if state is not None and state.paused is not None:
            # A pause that knows its own way out (held re-adoption, an incoming .runtime/) says it first.
            specific = state.last_error.next_step if state.last_error is not None else None
            note(
                CANONICAL_PAUSED,
                f"sync of this catalog is paused ({state.paused})",
                specific or PAUSED_NEXT_STEP,
                reason=state.paused,
            )
        if self.entry is None:
            reason = "linked with --no-schedule" if state is not None and state.schedule == "none" else "not registered"
            note(
                CANONICAL_SYNC_NOT_SCHEDULED,
                f"this catalog has no periodic sync ({reason})",
                SYNC_NOT_SCHEDULED_NEXT_STEP,
            )
        elif kind is not None:
            self._job(item, kind, note)
        if state is not None and state.push_auth is not None and state.push_auth.result == "failed":
            from spec_dock.runtime.application.canonical_sync import auth_next_step

            note(
                CANONICAL_PUSH_AUTH_FAILED,
                f"the periodic job could not authenticate its push ({state.push_auth.message})",
                auth_next_step(self._push_url()),
            )
        if state is not None and state.last_error is not None and state.paused is None:
            error = state.last_error
            note(
                CANONICAL_SYNC_FAILED,
                f"the last sync cycle failed: {error.code}: {error.message}",
                error.next_step or STATUS_RECOVERY,
                cause=error.code,
                program=list(error.program or ()),
            )
        if self.entry is not None:
            step = PRIVACY_NEXT_STEP if self.environment.system == "darwin" else SYNC_LOG_NEXT_STEP
            if state is None or state.last_cycle is None:
                note(
                    CANONICAL_SYNC_NOT_CONFIRMED, "the periodic job has not recorded a cycle for this catalog yet", step
                )
            elif _silent(state.last_cycle.finished_at):
                note(
                    CANONICAL_SYNC_NOT_CONFIRMED,
                    f"the periodic job has recorded no cycle since {state.last_cycle.finished_at}",
                    step,
                    last_cycle_at=state.last_cycle.finished_at,
                )
        if steps:
            item.update(status="problem", next_step=steps[0])
        return item

    def _job(self, item: dict[str, object], kind: str, note: object) -> None:
        assert callable(note)
        environment = self.environment
        if kind == "systemd":
            environment = runtime_environment.detect_service_manager(environment)
            item["linger"] = environment.linger
        spec = SchedulerSpec(Path("/"), self.state_root, Path("/"), environment.home or Path.home())
        try:
            scheduler = canonical_scheduling.scheduler_for(kind, state_root=self.state_root, environment=environment)  # type: ignore[arg-type]
            observed = scheduler.observe(spec)
        except canonical_scheduling.SchedulerError as error:
            item["job"] = {"installed": None, "active": None, "detail": str(error)}
            return
        item["job"] = {"installed": observed.installed, "active": observed.active, "detail": observed.detail}
        foreign = canonical_scheduling.foreign_state_root(scheduler, self.state_root, spec.home)
        if foreign is not None:
            note(
                CANONICAL_STATE_ROOT_MISMATCH,
                f"the installed {kind} job syncs the state root {foreign}, not this one",
                STATE_ROOT_MISMATCH_NEXT_STEP,
                recorded_state_root=str(foreign),
            )
            return
        if kind == "loop" and not observed.active:
            line = restart_line(self.state_root)
            note(CANONICAL_RUNNER_STOPPED, "the resident sync runner is not running", line, line=line)
        elif kind != "loop" and (observed.installed is False or observed.active is False):
            note(CANONICAL_SYNC_NOT_SCHEDULED, f"the {kind} job is missing or inactive", SYNC_NOT_SCHEDULED_NEXT_STEP)
        if kind == "systemd" and environment.linger is False:
            step = LINGER_NEXT_STEP.format(user=environment.user or "<user>")
            note(CANONICAL_LINGER_DISABLED, "sync stops while you are logged out (linger is off)", step)

    def _push_url(self) -> str | None:
        try:
            return canonical_git.push_url(self.layout.main_checkout, timeout=self.timeout)
        except (GitProcessError, OSError):
            return None

    def _repository(self) -> str | None:
        from spec_dock.runtime.application.canonical_sync import repository_of

        repository = self.entry.repository if self.entry is not None else None
        return repository or repository_of(self.layout.main_checkout, timeout=self.timeout)

    def dashboard_item(self) -> dict[str, object]:
        """The five files of the main checkout and state.json `dashboard` (iss-00438); nothing is written."""
        from spec_dock.runtime.application.canonical_dashboard import dashboard_directory
        from spec_dock.runtime.domain.canonical_dashboard import DASHBOARD_FILES
        from spec_dock.runtime.infra.canonical_files import is_regular_file

        directory = dashboard_directory(self.layout.main_checkout)
        files = {name: is_regular_file(directory / name) for name in DASHBOARD_FILES}
        recorded = dict(self.state.dashboard) if self.state is not None and self.state.dashboard else {}
        raw_error = recorded.get("error")
        error = cast("dict[str, object]", raw_error) if isinstance(raw_error, dict) else None
        item: dict[str, object] = {
            "status": "ok",
            "next_step": None,
            "directory": str(directory),
            "files": files,
            "written_at": recorded.get("written_at"),
            "error": error,
        }
        if error is not None:
            code = str(error.get("code"))
            step = DASHBOARD_OCCUPIED_NEXT_STEP if code == CANONICAL_DASHBOARD_OCCUPIED else DASHBOARD_FAILED_NEXT_STEP
            item["status"] = "problem"
            item["next_step"] = self.problem(
                "dashboard", code, str(error.get("message")), step, paths=error.get("paths") or []
            )
        elif self._repository() is None:
            item["status"] = "not_applicable"
        elif not all(files.values()):
            item.update(status="missing", next_step=DASHBOARD_MISSING_NEXT_STEP)
        return item

    def snapshot_item(self) -> dict[str, object]:
        """Where the structure snapshot is and how fresh; read from the state root only."""
        from spec_dock.runtime.infra.github_snapshot import SnapshotStore
        from spec_dock.runtime.infra.github_structure import GithubRepository

        repository = self._repository()
        item: dict[str, object] = {
            "status": "unknown",
            "next_step": None,
            "repository": repository,
            "path": None,
            "fetched_at": None,
            "checked_at": None,
            "anomalies": None,
            "last_error": None,
        }
        if repository is None:
            return item
        store = SnapshotStore(self.state_root, GithubRepository.parse(repository))
        snapshot, probe = store.load()
        item.update(
            path=str(store.directory),
            fetched_at=snapshot.fetched_at if snapshot else None,
            checked_at=probe.checked_at if probe else None,
            anomalies=len(snapshot.anomalies) if snapshot else None,
            last_error=dict(probe.last_error) if probe and probe.last_error else None,
            status="ok" if snapshot is not None else "unknown",
        )
        return item

    def extend_changes(self, item: dict[str, object]) -> None:
        """Holds and blocking paths from state.json, and the 10-minute unpushed warning (R-C6)."""
        state = self.state
        holds = []
        for hold in state.holds if state else ():
            holds.append({**hold.to_json(), "next_step": SAVE_HELD_NEXT_STEPS[hold.kind]})
        item["holds"] = holds
        item["blocking"] = [blocking.to_json() for blocking in state.blocking] if state else []
        item["unpushed_since"] = state.unpushed_since if state else None
        steps: list[str] = []
        for kind in sorted({hold.kind for hold in state.holds} if state else set()):
            paths = [hold.path for hold in state.holds if hold.kind == kind] if state else []
            steps.append(
                self.problem(
                    "changes",
                    CANONICAL_SAVE_HELD,
                    f"{len(paths)} change(s) held ({kind}): {', '.join(paths[:5])}",
                    SAVE_HELD_NEXT_STEPS[kind],
                    kind=kind,
                    paths=paths,
                )
            )
        if state is not None and state.blocking:
            paths = [blocking.path for blocking in state.blocking]
            steps.append(
                self.problem(
                    "changes",
                    CANONICAL_SYNC_BLOCKED,
                    f"incoming changes wait for files being edited: {', '.join(paths)}",
                    SYNC_BLOCKED_NEXT_STEP,
                    paths=paths,
                )
            )
        since = state.unpushed_since if state else None
        if since is None and item.get("unpushed"):
            since = item.get("oldest_unpushed_at")  # type: ignore[assignment]
        if isinstance(since, str) and _now() - parse_timestamp(since) > UNPUSHED_LIMIT:
            steps.append(
                self.problem(
                    "changes",
                    CANONICAL_UNPUSHED_STALE,
                    f"commits are waiting to be pushed since {since}",
                    UNPUSHED_STALE_NEXT_STEP,
                    since=since,
                )
            )
        if steps:
            item["status"] = "problem"
            item["next_step"] = item.get("next_step") or steps[0]

    def extend_git(self, item: dict[str, object]) -> None:
        """The git the periodic job uses (the registry's), next to this PATH's git."""
        if self.entry is None:
            item["registered"] = None
            return
        found = runtime_environment.probe_git(self.entry.git)
        item["registered"] = {"path": self.entry.git, "version": found.reported, "supported": found.supported}
