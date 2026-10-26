"""systemd user timer (Linux): the service and timer units, daemon-reload, enable --now, start --no-block."""

from __future__ import annotations

from pathlib import Path
import shlex
import subprocess
from typing import TYPE_CHECKING, Literal

from spec_dock.runtime.domain.canonical_scheduler import (
    SYSTEMD_PATH_TAIL,
    SYSTEMD_SERVICE,
    SYSTEMD_TIMER,
    state_root_argument,
    systemd_units,
)
from spec_dock.runtime.infra.canonical_scheduling import (
    EnsureOutcome,
    SchedulerError,
    SchedulerObservation,
    write_atomic,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from spec_dock.runtime.domain.canonical_scheduler import SchedulerSpec


class SystemdScheduler:
    @property
    def kind(self) -> Literal["systemd"]:
        return "systemd"

    @property
    def path_tail(self) -> str:
        return SYSTEMD_PATH_TAIL

    def __init__(
        self,
        *,
        unit_dir: Path,
        service: str = SYSTEMD_SERVICE,
        timer: str = SYSTEMD_TIMER,
        runner: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
    ) -> None:
        self.unit_dir = unit_dir
        self.service = service
        self.timer = timer
        self.runner = runner

    def _systemctl(self, *args: str, check: bool = False) -> subprocess.CompletedProcess[bytes]:
        try:
            completed = self.runner(["systemctl", "--user", *args], capture_output=True, check=False, timeout=30)
        except (OSError, subprocess.SubprocessError) as error:
            raise SchedulerError(f"systemctl --user {' '.join(args)}: {error}") from error
        if check and completed.returncode != 0:
            raise SchedulerError(
                f"systemctl --user {' '.join(args)} failed: {completed.stderr.decode(errors='replace').strip()}"
            )
        return completed

    def _active(self) -> bool | None:
        completed = self._systemctl("is-active", self.timer)
        state = completed.stdout.decode(errors="replace").strip()
        return state == "active" if state else None

    def _files(self, spec: SchedulerSpec) -> tuple[tuple[Path, bytes], tuple[Path, bytes]]:
        service, timer = systemd_units(spec)
        return (self.unit_dir / self.service, service.encode()), (self.unit_dir / self.timer, timer.encode())

    def needs_change(self, spec: SchedulerSpec) -> bool:
        for path, payload in self._files(spec):
            try:
                if path.read_bytes() != payload:
                    return True
            except FileNotFoundError:
                return True
        return self._active() is False

    def write_paths(self, spec: SchedulerSpec) -> tuple[Path, ...]:
        del spec
        return (self.unit_dir,)

    def recorded_executable(self, spec: SchedulerSpec) -> Path | None:
        del spec
        try:
            text = (self.unit_dir / self.service).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None
        for line in text.splitlines():
            if line.startswith("ExecStart="):
                try:
                    words = shlex.split(line.removeprefix("ExecStart=").replace("%%", "%"))
                except ValueError:
                    return None
                return Path(words[0]) if words else None
        return None

    def recorded_state_root(self, spec: SchedulerSpec) -> Path | None:
        del spec
        try:
            text = (self.unit_dir / self.service).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None
        for line in text.splitlines():
            if line.startswith("ExecStart="):
                try:
                    return state_root_argument(shlex.split(line.removeprefix("ExecStart=").replace("%%", "%")))
                except ValueError:
                    return None
        return None

    def recorded_search_path(self, spec: SchedulerSpec) -> str | None:
        del spec
        try:
            text = (self.unit_dir / self.service).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None
        for line in text.splitlines():
            if line.startswith("Environment="):
                try:
                    words = shlex.split(line.removeprefix("Environment=").replace("%%", "%"))
                except ValueError:
                    return None
                for word in words:
                    if word.startswith("PATH="):
                        return word.removeprefix("PATH=")
        return None

    def ensure(self, spec: SchedulerSpec) -> EnsureOutcome:
        existed = (self.unit_dir / self.service).exists()
        changed = False
        for path, payload in self._files(spec):
            changed = write_atomic(path, payload) or changed
        if not changed and self._active():
            return "unchanged"
        self._systemctl("daemon-reload", check=True)
        self._systemctl("enable", "--now", self.timer, check=True)
        return "updated" if existed else "created"

    def kick(self, spec: SchedulerSpec) -> None:
        del spec
        self._systemctl("start", "--no-block", self.service, check=True)

    def remove(self, spec: SchedulerSpec) -> bool:
        paths = [path for path, _payload in self._files(spec)]
        existed = any(path.exists() for path in paths)
        disabled = self._systemctl("disable", "--now", self.timer)
        if disabled.returncode != 0 and existed:
            raise SchedulerError(
                f"systemctl --user disable --now failed: {disabled.stderr.decode(errors='replace').strip()}"
            )
        for path in paths:
            path.unlink(missing_ok=True)
        self._systemctl("daemon-reload")
        return existed

    def observe(self, spec: SchedulerSpec) -> SchedulerObservation:
        del spec
        installed = (self.unit_dir / self.timer).is_file()
        try:
            active = self._active()
        except SchedulerError as error:
            return SchedulerObservation(installed, None, str(error))
        return SchedulerObservation(installed, active)
