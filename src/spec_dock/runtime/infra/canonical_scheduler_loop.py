"""The resident runner where systemd is unavailable (containers): one per environment, a cycle every 60 s.

`canonical sync --registered --loop` holds runner.lock for its whole life (a second one exits 0), writes
runner.json, runs a cycle, then waits up to 60 s checking every 2 s for a stop request or the kick file.
A SIGTERM or SIGINT during a cycle lets that cycle finish first.
"""

from __future__ import annotations

from contextlib import suppress
from datetime import datetime, timezone
import os
from pathlib import Path
import signal
import subprocess
import time
from typing import TYPE_CHECKING, Final, Literal

from spec_dock.runtime.domain.canonical_scheduler import INTERVAL_SECONDS
from spec_dock.runtime.domain.canonical_structure import format_timestamp
from spec_dock.runtime.domain.canonical_sync_state import RunnerRecord, StateFormatError
from spec_dock.runtime.infra.canonical_scheduling import (
    EnsureOutcome,
    SchedulerError,
    SchedulerObservation,
)
from spec_dock.runtime.infra.canonical_state import (
    append_log,
    kick_path,
    read_json,
    runner_lock_path,
    runner_record_path,
    write_json_atomic,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from spec_dock.runtime.domain.canonical_scheduler import SchedulerSpec

KICK_POLL: Final = 2.0
LOCK_ATTEMPTS: Final = 5
LOCK_RETRY: Final = 0.2


def runner_running(root: Path) -> bool:
    """True while some process holds runner.lock; the probe creates no file and releases at once."""
    import fcntl

    try:
        descriptor = os.open(runner_lock_path(root), os.O_RDONLY | getattr(os, "O_CLOEXEC", 0))
    except FileNotFoundError:
        return False
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return True
    finally:
        os.close(descriptor)
    return False


def read_runner(root: Path) -> RunnerRecord | None:
    try:
        payload = read_json(runner_record_path(root))
        return None if payload is None else RunnerRecord.from_json(payload)
    except (OSError, ValueError, StateFormatError):
        return None


def detach(root: Path, *, executable: Path, home: Path | None = None) -> int:
    """Start a detached runner in a new session with no terminal; return its process id without waiting."""
    argv = [str(executable), "canonical", "sync", "--registered", "--loop", "--state-root", str(root)]
    try:
        process = subprocess.Popen(
            argv,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(home or Path.home()),
            start_new_session=True,
            close_fds=True,
        )
    except OSError as error:
        raise SchedulerError(f"could not start the resident runner: {error}") from error
    return process.pid


def run_loop(
    root: Path,
    *,
    cycle: Callable[[], object],
    version: str,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
    install_signals: bool = True,
    interval: float = INTERVAL_SECONDS,
) -> Literal["stopped", "already_running"]:
    """Run cycles until SIGTERM/SIGINT; another runner holding runner.lock makes this return at once."""
    import fcntl

    root.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(runner_lock_path(root), os.O_RDWR | os.O_CREAT | getattr(os, "O_CLOEXEC", 0), 0o644)
    try:
        for attempt in range(LOCK_ATTEMPTS):
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if attempt == LOCK_ATTEMPTS - 1:
                    return "already_running"
                sleep(LOCK_RETRY)  # a status probe may hold it for an instant
        stop = {"requested": False}

        def request_stop(_signum: int, _frame: object) -> None:
            stop["requested"] = True

        previous = {}
        if install_signals:
            previous = {sig: signal.signal(sig, request_stop) for sig in (signal.SIGTERM, signal.SIGINT)}
        record = RunnerRecord(os.getpid(), format_timestamp(datetime.now(timezone.utc)), version)
        write_json_atomic(root, runner_record_path(root).name, record.to_json())
        try:
            while not stop["requested"]:
                try:
                    cycle()
                except Exception as error:  # the only sync of a container: log and keep running
                    with suppress(OSError, TimeoutError):
                        append_log(
                            root, f"{format_timestamp(datetime.now(timezone.utc))} runner cycle failed: {error!r}"
                        )
                deadline = monotonic() + interval
                while not stop["requested"]:
                    kick = kick_path(root)
                    if kick.exists():
                        with suppress(FileNotFoundError):
                            kick.unlink()
                        break
                    remaining = deadline - monotonic()
                    if remaining <= 0:
                        break
                    sleep(min(KICK_POLL, remaining))
        finally:
            for sig, handler in previous.items():
                signal.signal(sig, handler)
            with suppress(FileNotFoundError):
                runner_record_path(root).unlink()
        return "stopped"
    finally:
        os.close(descriptor)


class LoopScheduler:
    @property
    def kind(self) -> Literal["loop"]:
        return "loop"

    @property
    def path_tail(self) -> None:
        return None  # the runner inherits the PATH it was started with

    def __init__(self, state_root: Path, *, spawn: Callable[..., int] = detach) -> None:
        self.state_root = state_root
        self.spawn = spawn

    def needs_change(self, spec: SchedulerSpec) -> bool:
        del spec
        return not runner_running(self.state_root)

    def write_paths(self, spec: SchedulerSpec) -> tuple[Path, ...]:
        del spec
        return (self.state_root,)

    def recorded_executable(self, spec: SchedulerSpec) -> Path | None:
        del spec
        return None

    def recorded_state_root(self, spec: SchedulerSpec) -> Path | None:
        del spec
        return None  # every state root has its own runner

    def recorded_search_path(self, spec: SchedulerSpec) -> str | None:
        del spec
        return None

    def ensure(self, spec: SchedulerSpec) -> EnsureOutcome:
        if runner_running(self.state_root):
            return "unchanged"
        self.spawn(self.state_root, executable=spec.executable, home=spec.home)
        return "created"

    def kick(self, spec: SchedulerSpec) -> None:
        if runner_running(self.state_root):
            kick_path(self.state_root).touch()
        else:
            self.spawn(self.state_root, executable=spec.executable, home=spec.home)

    def remove(self, spec: SchedulerSpec) -> bool:
        del spec
        record = read_runner(self.state_root)
        if not runner_running(self.state_root) or record is None:
            return False
        try:
            os.kill(record.pid, signal.SIGTERM)
        except ProcessLookupError:
            return False
        except OSError as error:
            raise SchedulerError(f"could not stop the resident runner {record.pid}: {error}") from error
        return True

    def observe(self, spec: SchedulerSpec) -> SchedulerObservation:
        del spec
        running = runner_running(self.state_root)
        record = read_runner(self.state_root) if running else None
        detail = f"pid {record.pid} since {record.started_at}" if record else None
        return SchedulerObservation(running, running, detail)
