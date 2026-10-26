"""The periodic job of the canonical sync: one interface over launchd, systemd user timers and the loop runner.

scheduler_for() is the single factory (tests replace it); every implementation can say whether it would
write (needs_change), where (write_paths), install (ensure), run now (kick), uninstall (remove) and observe.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import sys
from typing import TYPE_CHECKING, Literal, Protocol

if TYPE_CHECKING:
    from spec_dock.runtime.domain.canonical_scheduler import SchedulerSpec
    from spec_dock.runtime.domain.canonical_sync_state import SchedulerKind
    from spec_dock.runtime.infra.runtime_environment import RuntimeEnvironment

EnsureOutcome = Literal["created", "updated", "unchanged"]


class SchedulerError(RuntimeError):
    """A launchctl, systemctl or process start failed; the message carries the command output."""


@dataclass(frozen=True)
class SchedulerObservation:
    installed: bool | None
    active: bool | None
    detail: str | None = None


class Scheduler(Protocol):
    @property
    def kind(self) -> SchedulerKind: ...

    @property
    def path_tail(self) -> str | None: ...  # the fixed end of the job's PATH; None when the job inherits PATH

    def needs_change(self, spec: SchedulerSpec) -> bool: ...

    def write_paths(self, spec: SchedulerSpec) -> tuple[Path, ...]: ...

    def recorded_executable(self, spec: SchedulerSpec) -> Path | None: ...

    def recorded_search_path(self, spec: SchedulerSpec) -> str | None: ...

    def recorded_state_root(self, spec: SchedulerSpec) -> Path | None: ...

    def ensure(self, spec: SchedulerSpec) -> EnsureOutcome: ...

    def kick(self, spec: SchedulerSpec) -> None: ...

    def remove(self, spec: SchedulerSpec) -> bool: ...

    def observe(self, spec: SchedulerSpec) -> SchedulerObservation: ...


def scheduler_for(kind: SchedulerKind, *, state_root: Path, environment: RuntimeEnvironment) -> Scheduler:
    """The production scheduler of `kind`; tests replace this function."""
    home = environment.home or Path.home()
    if kind == "launchd":
        from spec_dock.runtime.infra.canonical_scheduler_launchd import LaunchdScheduler

        return LaunchdScheduler(agents_dir=home / "Library/LaunchAgents")
    if kind == "systemd":
        from spec_dock.runtime.infra.canonical_scheduler_systemd import SystemdScheduler

        config = environment.environ.get("XDG_CONFIG_HOME", "")
        base = Path(config) if config and Path(config).is_absolute() else home / ".config"
        return SystemdScheduler(unit_dir=base / "systemd/user")
    from spec_dock.runtime.infra.canonical_scheduler_loop import LoopScheduler

    return LoopScheduler(state_root)


def foreign_state_root(scheduler: Scheduler, state_root: Path, home: Path) -> Path | None:
    """The other state root whose registered catalogs the one installed job still syncs, if any.

    The job of a user is one, so a link or remove from another root (another XDG_STATE_HOME) must not repoint
    or take it away while that root still has catalogs. A root with no registry, or an empty one, is free.
    """
    from spec_dock.runtime.domain.canonical_scheduler import SchedulerSpec
    from spec_dock.runtime.infra.canonical_registry import RegistryUnreadable, read_registry

    recorded = scheduler.recorded_state_root(SchedulerSpec(Path("/"), state_root, Path("/"), home))
    if recorded is None or os.path.realpath(recorded) == os.path.realpath(state_root):
        return None
    try:
        return recorded if read_registry(recorded).catalogs else None
    except (RegistryUnreadable, OSError):
        return recorded


def spec_dock_executable() -> Path:
    """The real path of the running spec-dock console script, or of `spec-dock` on PATH; tests replace it."""
    candidate = Path(os.path.realpath(sys.argv[0])) if sys.argv and sys.argv[0] else None
    if candidate is not None and candidate.is_file() and os.access(candidate, os.X_OK):
        return candidate
    found = shutil.which("spec-dock")
    if found is None:
        raise SchedulerError("the spec-dock executable could not be found for the periodic job")
    return Path(os.path.realpath(found))


def usable_executable(path: Path | None) -> bool:
    return path is not None and path.is_file() and os.access(path, os.X_OK)


def write_atomic(path: Path, payload: bytes) -> bool:
    """Write `path` through a temporary sibling; False when it already holds exactly `payload`."""
    try:
        if path.read_bytes() == payload:
            return False
    except FileNotFoundError:
        pass
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        with temporary.open("wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return True
