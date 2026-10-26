"""`canonical link` steps 6 and 7: register the catalog, record its baseline, install and kick the periodic job.

Order (design ch. 10): 6a registry -> 7 baseline -> 6b job -> 6c run now and wait up to 15 s. The state root
is locked from 6a to 6b so two links never race on the job. The recorded git and job executable are kept
while they still work, so an agent's PATH or a development venv never rewrites them. request_sync_now is
the public "run a cycle now" request that `work finish` (iss-00432) uses.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
import shutil
import time
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.application.canonical_errors import (
    CANONICAL_LINGER_DISABLED,
    CANONICAL_PUSH_AUTH_FAILED,
    CANONICAL_RUNNER_RESTART,
    CANONICAL_SCHEDULER_FAILED,
    CANONICAL_STATE_UNREADABLE,
    CANONICAL_SYNC_NOT_CONFIRMED,
    LINGER_NEXT_STEP,
    OS_ACCESS_DENIED,
    PRIVACY_NEXT_STEP,
    SCHEDULER_FAILED_RECOVERY,
    STATE_UNREADABLE_NEXT_STEP,
    SYNC_LOG_NEXT_STEP,
)
from spec_dock.runtime.domain.canonical_layout import git_supported
from spec_dock.runtime.domain.canonical_scheduler import SchedulerSpec, restart_line, select_scheduler
from spec_dock.runtime.domain.canonical_structure import format_timestamp, parse_timestamp
from spec_dock.runtime.domain.canonical_sync_state import CatalogSyncState, RegistryEntry, SyncRegistry
from spec_dock.runtime.infra import canonical_git, canonical_scheduling, runtime_environment
from spec_dock.runtime.infra.canonical_registry import (
    RegistryUnreadable,
    read_registry,
    registry_path,
    write_registry_locked,
)
from spec_dock.runtime.infra.canonical_state import (
    StateUnreadable,
    catalog_state_dir,
    cycle_lock,
    directory_lock,
    move_catalog_state,
    read_catalog_state,
    update_catalog_state,
)
from spec_dock.runtime.infra.state_root import resolve_state_root
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect

if TYPE_CHECKING:
    from datetime import datetime

    from spec_dock.runtime.domain.canonical_layout import CatalogLayout
    from spec_dock.runtime.domain.canonical_sync_state import SchedulerKind
    from spec_dock.runtime.infra.canonical_scheduling import Scheduler
    from spec_dock.runtime.infra.runtime_environment import RuntimeEnvironment

FIRST_RUN_WAIT = 15.0  # seconds canonical link waits for the first cycle's record (tests set 0)
FIRST_RUN_POLL: Final = 0.25


class ScheduleFailed(Exception):
    """Step 6 or 7 failed after earlier effects; canonical link reports partial with these effects."""

    def __init__(self, code: str, message: str, recovery: str, effects: list[Effect]) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.recovery = recovery
        self.effects = effects


class JobServesAnotherRoot(Exception):
    """The one installed job syncs the catalogs of another state root; a link here must not repoint it."""

    def __init__(self, recorded: Path, state_root: Path) -> None:
        super().__init__(f"the installed periodic job syncs the state root {recorded}, not {state_root}")
        self.recorded = recorded
        self.state_root = state_root


@dataclass
class SchedulePlan:
    """What steps 6 and 7 would write, decided before anything is written (for the writability check)."""

    state_root: Path
    catalog: str
    main_checkout: Path
    schedule: bool
    environment: RuntimeEnvironment
    registry: SyncRegistry | None = None
    entry: RegistryEntry | None = None
    moved_from: str | None = None
    kind: SchedulerKind | None = None
    spec: SchedulerSpec | None = None
    registry_change: bool = False
    scheduler_change: bool = False
    baseline_change: bool = False
    scheduler_paths: tuple[Path, ...] = ()
    effects: list[Effect] = field(default_factory=list)

    def write_paths(self) -> tuple[Path, ...]:
        paths: list[Path] = []
        if self.registry_change or self.baseline_change or self.moved_from is not None:
            paths.append(self.state_root)
        if self.scheduler_change:
            paths.extend(self.scheduler_paths)
        return tuple(paths)

    def planned(self) -> tuple[Effect, ...]:
        effects = []
        if self.registry_change:
            effects.append(Effect("canonical.registry", "planned", str(registry_path(self.state_root))))
        if self.baseline_change:
            effects.append(
                Effect("canonical.baseline", "planned", str(catalog_state_dir(self.state_root, self.catalog)))
            )
        if self.scheduler_change and self.kind is not None:
            effects.append(Effect("canonical.scheduler", "planned", self.kind))
        return tuple(effects)


def _recorded_git(entry: RegistryEntry | None, environment: RuntimeEnvironment) -> str:
    """Keep the registered git while it exists and is 2.38 or later; otherwise this PATH's git."""
    if entry is not None and git_supported(runtime_environment.probe_git(entry.git).version):
        return entry.git
    return environment.git.path or "git"


def _schedule_wanted(state_root: Path, catalog: str, *, schedule: bool, follow_up: bool) -> bool:
    """link_after_command keeps a `--no-schedule` catalog unregistered (judgment R1)."""
    if not schedule:
        return False
    if not follow_up:
        return True
    try:
        state = read_catalog_state(state_root, catalog)
    except StateUnreadable:
        return True
    return state is None or state.schedule != "none"


def plan_schedule(
    layout: CatalogLayout,
    environment: RuntimeEnvironment,
    *,
    moved_from: str | None,
    schedule: bool,
    follow_up: bool = False,
    timeout: float = 30.0,
) -> SchedulePlan:
    """Read the registry, state and job (no writes) and decide what steps 6 and 7 would change."""
    state_root = resolve_state_root(dict(environment.environ))
    catalog = os.path.realpath(layout.catalog)
    wanted = _schedule_wanted(state_root, catalog, schedule=schedule, follow_up=follow_up)
    plan = SchedulePlan(state_root, catalog, layout.main_checkout, wanted, environment)
    if moved_from is not None and moved_from != catalog and catalog_state_dir(state_root, moved_from).exists():
        plan.moved_from = moved_from  # the baseline moves with a moved main checkout, scheduled or not
    try:
        state = read_catalog_state(state_root, catalog)
    except StateUnreadable:
        state = None
        plan.baseline_change = True
    else:
        plan.baseline_change = (
            state is None or state.last_seen_remote is None or state.schedule != (None if wanted else "none")
        )
    if not wanted:
        return plan
    environment = runtime_environment.detect_service_manager(environment)
    plan.environment = environment
    registry = read_registry(state_root)
    plan.registry = registry
    previous = registry.entry_for(catalog)
    git = _recorded_git(previous, environment)
    from spec_dock.runtime.application.canonical_sync import repository_of

    repository = (previous.repository if previous is not None else None) or repository_of(
        layout.main_checkout, timeout=timeout
    )
    stamp = format_timestamp(_now())
    plan.entry = RegistryEntry(
        catalog, str(layout.main_checkout), repository, git, previous.registered_at if previous else stamp
    )
    if plan.moved_from is None and moved_from is not None and registry.entry_for(moved_from) is not None:
        plan.moved_from = moved_from
    plan.kind = select_scheduler(
        environment.system,
        systemd_present=environment.systemd_present,
        systemd_user=environment.systemd_user,
        previous=registry.scheduler,
    )
    plan.registry_change = previous != plan.entry or plan.moved_from is not None or registry.scheduler != plan.kind
    scheduler = canonical_scheduling.scheduler_for(plan.kind, state_root=state_root, environment=environment)
    foreign = canonical_scheduling.foreign_state_root(scheduler, state_root, environment.home or Path.home())
    if foreign is not None:
        raise JobServesAnotherRoot(foreign, state_root)
    git_dir = Path(git).parent if Path(git).is_absolute() else Path("/usr/bin")
    spec = SchedulerSpec(
        _job_executable(scheduler, state_root, environment),
        state_root,
        git_dir,
        environment.home or Path.home(),
        _gh_dir(scheduler, state_root, environment, git_dir),
    )
    plan.spec = spec
    plan.scheduler_change = scheduler.needs_change(spec) or (registry.scheduler not in (None, plan.kind))
    plan.scheduler_paths = scheduler.write_paths(spec)
    return plan


def _gh_dir(scheduler: Scheduler, state_root: Path, environment: RuntimeEnvironment, git_dir: Path) -> Path | None:
    """The gh directory the installed job already uses while gh is still there; else this PATH's gh."""
    probe = SchedulerSpec(Path("/"), state_root, Path("/"), environment.home or Path.home())
    recorded = scheduler.recorded_search_path(probe)
    if recorded:
        for directory in recorded.split(":"):
            if directory and Path(directory) != git_dir and os.access(Path(directory) / "gh", os.X_OK):
                return Path(directory)
        if os.access(git_dir / "gh", os.X_OK):
            return git_dir
    gh = shutil.which("gh", path=environment.environ.get("PATH", ""))
    return Path(gh).parent if gh else None


def _job_executable(scheduler: Scheduler, state_root: Path, environment: RuntimeEnvironment) -> Path:
    """The installed job's executable while it still runs; this spec-dock only for a new or broken job."""
    probe = SchedulerSpec(Path("/"), state_root, Path("/"), environment.home or Path.home())
    recorded = scheduler.recorded_executable(probe)
    if canonical_scheduling.usable_executable(recorded):
        assert recorded is not None
        return recorded
    try:
        return canonical_scheduling.spec_dock_executable()
    except canonical_scheduling.SchedulerError:
        return Path("spec-dock")


def _now() -> datetime:
    from spec_dock.runtime.application import canonical_sync

    return canonical_sync.SYNC_CLOCK.now()


def apply_schedule(plan: SchedulePlan, *, offline: bool = False) -> tuple[list[Effect], list[Diagnostic]]:
    """Run 6a -> 7 -> 6b -> 6c; a failure raises ScheduleFailed carrying the effects so far."""
    effects: list[Effect] = []
    warnings: list[Diagnostic] = []
    try:
        if not plan.schedule:
            if plan.moved_from is not None:
                _move_state(plan, effects)
            if plan.baseline_change or plan.moved_from is not None:
                _baseline(plan, effects)
            return effects, warnings
        assert plan.entry is not None and plan.kind is not None and plan.spec is not None
        if not (plan.registry_change or plan.baseline_change or plan.scheduler_change):
            # Everything is in place: write nothing (a sandbox that can only place links passes).
            warnings.extend(_standing_warnings(plan))
            return effects, warnings
        with directory_lock(plan.state_root, timeout=10.0):
            registered = _registry(plan, effects)
            if plan.baseline_change:
                _baseline(plan, effects)
            installed = _job(plan, effects)
        if (registered or installed) and not offline:  # --offline: no cycle (and its push) now
            warnings.extend(_kick_and_wait(plan))
    except StateUnreadable as error:  # the state of a moved main checkout, read before it moves
        raise ScheduleFailed(CANONICAL_STATE_UNREADABLE, str(error), STATE_UNREADABLE_NEXT_STEP, effects) from error
    except (OSError, TimeoutError, RegistryUnreadable) as error:
        raise ScheduleFailed("LOCAL_IO_FAILED", str(error), SCHEDULER_FAILED_RECOVERY, effects) from error
    warnings.extend(_standing_warnings(plan))
    return effects, warnings


def _registry(plan: SchedulePlan, effects: list[Effect]) -> bool:
    assert plan.entry is not None
    registry = read_registry(plan.state_root)
    updated = registry
    if plan.moved_from is not None:
        updated = updated.without(plan.moved_from)
        _move_state(plan, effects)
    updated = SyncRegistry(plan.kind, updated.with_entry(plan.entry).catalogs)
    if updated == registry:
        return False
    write_registry_locked(plan.state_root, updated)
    effects.append(Effect("canonical.registry", "succeeded", str(registry_path(plan.state_root))))
    return registry.entry_for(plan.catalog) != plan.entry


def _move_state(plan: SchedulePlan, effects: list[Effect]) -> None:
    assert plan.moved_from is not None
    with cycle_lock(plan.state_root, plan.moved_from, timeout=10.0):
        if move_catalog_state(plan.state_root, plan.moved_from, plan.catalog):
            effects.append(Effect("canonical.state.move", "succeeded", plan.catalog))


def _baseline(plan: SchedulePlan, effects: list[Effect]) -> None:
    """Step 7: record the baseline of a catalog without one (`initial_baseline`: the local HEAD, or the tracking ref)."""
    catalog = Path(plan.catalog)
    target = str(catalog_state_dir(plan.state_root, plan.catalog))
    marker = None if plan.schedule else "none"
    changed = {"value": False}

    def mutate(current: CatalogSyncState | None) -> CatalogSyncState:
        stamp = format_timestamp(_now())
        state = current or CatalogSyncState.new(plan.catalog, at=stamp)
        baseline = state.last_seen_remote
        if baseline is None:
            # The local HEAD: the first cycle never recreates a canonical GitHub deleted, nor pushes back a rewind.
            from spec_dock.runtime.application.canonical_sync import initial_baseline

            baseline = initial_baseline(catalog)
        updated = state.evolve(last_seen_remote=baseline, schedule=marker)
        changed["value"] = current is None or updated != current
        return updated.evolve(updated_at=stamp) if changed["value"] else updated

    try:
        update_catalog_state(plan.state_root, plan.catalog, mutate)
    except StateUnreadable as error:
        raise ScheduleFailed(CANONICAL_STATE_UNREADABLE, str(error), STATE_UNREADABLE_NEXT_STEP, effects) from error
    effects.append(Effect("canonical.baseline", "succeeded" if changed["value"] else "unchanged", target))


def _job(plan: SchedulePlan, effects: list[Effect]) -> bool:
    assert plan.kind is not None and plan.spec is not None and plan.registry is not None
    previous = plan.registry.scheduler
    try:
        if previous is not None and previous != plan.kind:
            old = canonical_scheduling.scheduler_for(previous, state_root=plan.state_root, environment=plan.environment)
            if old.remove(plan.spec):
                effects.append(Effect("canonical.scheduler.remove", "succeeded", previous))
        scheduler = canonical_scheduling.scheduler_for(
            plan.kind, state_root=plan.state_root, environment=plan.environment
        )
        outcome = scheduler.ensure(plan.spec)
    except canonical_scheduling.SchedulerError as error:
        # The job file may already be written even though loading it failed.
        effects.append(Effect("canonical.scheduler", "unknown", plan.kind))
        raise ScheduleFailed(CANONICAL_SCHEDULER_FAILED, str(error), SCHEDULER_FAILED_RECOVERY, effects) from error
    effects.append(Effect("canonical.scheduler", "unchanged" if outcome == "unchanged" else "succeeded", plan.kind))
    return outcome != "unchanged"


def _kick_and_wait(plan: SchedulePlan) -> list[Diagnostic]:
    """Run one cycle now and wait up to FIRST_RUN_WAIT for its record; report what the job could not do."""
    assert plan.kind is not None and plan.spec is not None
    from spec_dock.runtime.application import canonical_sync

    asked = parse_timestamp(format_timestamp(canonical_sync.SYNC_CLOCK.now()))
    scheduler = canonical_scheduling.scheduler_for(plan.kind, state_root=plan.state_root, environment=plan.environment)
    try:
        scheduler.kick(plan.spec)
    except canonical_scheduling.SchedulerError as error:
        return [_not_confirmed(plan, f"the periodic job could not be started now: {error}")]
    deadline = time.monotonic() + FIRST_RUN_WAIT
    state: CatalogSyncState | None = None
    while True:
        try:
            state = read_catalog_state(plan.state_root, plan.catalog)
        except StateUnreadable:
            state = None
        finished = state.last_cycle.finished_at if state is not None and state.last_cycle is not None else None
        if finished is not None and parse_timestamp(finished) >= asked:
            break
        if time.monotonic() >= deadline:
            return [_not_confirmed(plan, f"the first periodic cycle left no record within {FIRST_RUN_WAIT:g} seconds")]
        time.sleep(FIRST_RUN_POLL)
    warnings: list[Diagnostic] = []
    assert state is not None
    last = state.last_error
    if last is not None and last.code == OS_ACCESS_DENIED:
        programs = list(last.program or ())
        warnings.append(
            Diagnostic(
                OS_ACCESS_DENIED,
                f"the periodic job could not read the catalog ({last.message}); next: {PRIVACY_NEXT_STEP}",
                {"item": "sync", "programs": programs, "next_step": PRIVACY_NEXT_STEP},
            )
        )
    if state.push_auth is not None and state.push_auth.result == "failed":
        step = canonical_sync.auth_next_step(canonical_git.push_url(Path(plan.catalog)))
        warnings.append(
            Diagnostic(
                CANONICAL_PUSH_AUTH_FAILED,
                f"the periodic job could not authenticate its push ({state.push_auth.message}); next: {step}",
                {"item": "sync", "next_step": step},
            )
        )
    return warnings


def _not_confirmed(plan: SchedulePlan, message: str) -> Diagnostic:
    import sys

    if plan.environment.system == "darwin":
        assert plan.entry is not None
        programs = [os.path.realpath(sys.executable), plan.entry.git]
        return Diagnostic(
            CANONICAL_SYNC_NOT_CONFIRMED,
            f"{message}; next: {PRIVACY_NEXT_STEP}",
            {"item": "sync", "programs": programs, "next_step": PRIVACY_NEXT_STEP},
        )
    return Diagnostic(
        CANONICAL_SYNC_NOT_CONFIRMED,
        f"{message}; next: {SYNC_LOG_NEXT_STEP}",
        {"item": "sync", "next_step": SYNC_LOG_NEXT_STEP},
    )


def _standing_warnings(plan: SchedulePlan) -> list[Diagnostic]:
    """Linger on a systemd host and the restart line of the loop runner are reported on every link."""
    warnings: list[Diagnostic] = []
    if plan.kind == "systemd" and plan.environment.linger is False:
        step = LINGER_NEXT_STEP.format(user=plan.environment.user or "<user>")
        warnings.append(
            Diagnostic(
                CANONICAL_LINGER_DISABLED,
                f"sync stops while you are logged out (linger is off); next: {step}",
                {"item": "sync", "next_step": step},
            )
        )
    if plan.kind == "loop":
        line = restart_line(plan.state_root)
        warnings.append(
            Diagnostic(
                CANONICAL_RUNNER_RESTART,
                "the resident runner stops when the container restarts; add this line to the container start "
                f"(devcontainer postStartCommand or start script): {line}",
                {"item": "sync", "line": line, "next_step": line},
            )
        )
    return warnings


def request_sync_now(state_root: Path, *, environment: RuntimeEnvironment | None = None) -> bool:
    """Ask the registered periodic job to run a cycle now; any failure is False, never an exception.

    The public "run now" request for `work finish` (iss-00432): at worst the next cycle comes within 60 s.
    """
    try:
        registry = read_registry(state_root)
        if registry.scheduler is None:
            return False
        current = environment or runtime_environment.detect_runtime_environment()
        scheduler = canonical_scheduling.scheduler_for(registry.scheduler, state_root=state_root, environment=current)
        executable = canonical_scheduling.spec_dock_executable()
        spec = SchedulerSpec(executable, state_root, Path("/usr/bin"), current.home or Path.home())
        scheduler.kick(spec)
    except Exception:  # a sandbox or a missing launchctl must never fail the caller
        return False
    return True
