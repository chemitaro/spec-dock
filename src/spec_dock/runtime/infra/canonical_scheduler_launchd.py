"""launchd (macOS): ~/Library/LaunchAgents/<label>.plist, bootstrap, kickstart, bootout (Epic ch. 5)."""

from __future__ import annotations

import os
from pathlib import Path
import plistlib
import subprocess
import time
from typing import TYPE_CHECKING, Final, Literal

from spec_dock.runtime.domain.canonical_scheduler import LAUNCHD_LABEL, launchd_plist
from spec_dock.runtime.infra.canonical_scheduling import (
    EnsureOutcome,
    SchedulerError,
    SchedulerObservation,
    write_atomic,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from spec_dock.runtime.domain.canonical_scheduler import SchedulerSpec

NOT_FOUND: Final = 113  # launchctl print: "Could not find service"
BOOTSTRAP_ATTEMPTS: Final = 3


class LaunchdScheduler:
    @property
    def kind(self) -> Literal["launchd"]:
        return "launchd"

    def __init__(
        self,
        *,
        agents_dir: Path,
        label: str = LAUNCHD_LABEL,
        uid: int | None = None,
        runner: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.sleep = sleep
        self.agents_dir = agents_dir
        self.label = label
        self.uid = os.getuid() if uid is None else uid
        self.runner = runner

    @property
    def plist(self) -> Path:
        return self.agents_dir / f"{self.label}.plist"

    def _launchctl(self, *args: str) -> subprocess.CompletedProcess[bytes]:
        try:
            return self.runner(["launchctl", *args], capture_output=True, check=False, timeout=30)
        except (OSError, subprocess.SubprocessError) as error:
            raise SchedulerError(f"launchctl {' '.join(args)}: {error}") from error

    def _loaded(self) -> bool | None:
        completed = self._launchctl("print", f"gui/{self.uid}/{self.label}")
        if completed.returncode == 0:
            return True
        return False if completed.returncode == NOT_FOUND else None

    def needs_change(self, spec: SchedulerSpec) -> bool:
        try:
            if self.plist.read_bytes() != launchd_plist(spec, label=self.label):
                return True
        except FileNotFoundError:
            return True
        # A sandbox may refuse `print`; only an explicit "not found" makes an identical plist need loading.
        return self._loaded() is False

    def write_paths(self, spec: SchedulerSpec) -> tuple[Path, ...]:
        del spec
        return (self.agents_dir,)

    def recorded_executable(self, spec: SchedulerSpec) -> Path | None:
        del spec
        try:
            arguments = plistlib.loads(self.plist.read_bytes()).get("ProgramArguments")
        except (OSError, ValueError, plistlib.InvalidFileException):
            return None
        return (
            Path(arguments[0]) if isinstance(arguments, list) and arguments and isinstance(arguments[0], str) else None
        )

    def ensure(self, spec: SchedulerSpec) -> EnsureOutcome:
        existed = self.plist.exists()
        changed = write_atomic(self.plist, launchd_plist(spec, label=self.label))
        loaded = self._loaded()
        if not changed and loaded is not False:
            return "unchanged"
        if loaded is not False:
            self._bootout()  # also when `print` could not tell: bootstrapping a loaded job fails
        for attempt in range(BOOTSTRAP_ATTEMPTS):
            completed = self._launchctl("bootstrap", f"gui/{self.uid}", str(self.plist))
            if completed.returncode == 0:
                return "updated" if existed else "created"
            if attempt < BOOTSTRAP_ATTEMPTS - 1:
                self.sleep(1.0)  # right after a bootout launchd may still answer EIO
        raise SchedulerError(f"launchctl bootstrap failed: {completed.stderr.decode(errors='replace').strip()}")

    def _bootout(self) -> None:
        completed = self._launchctl("bootout", f"gui/{self.uid}/{self.label}")
        if completed.returncode not in (0, 3, NOT_FOUND):  # 3: no such process, 113: not loaded
            raise SchedulerError(f"launchctl bootout failed: {completed.stderr.decode(errors='replace').strip()}")

    def kick(self, spec: SchedulerSpec) -> None:
        del spec
        completed = self._launchctl("kickstart", f"gui/{self.uid}/{self.label}")
        if completed.returncode != 0:
            raise SchedulerError(f"launchctl kickstart failed: {completed.stderr.decode(errors='replace').strip()}")

    def remove(self, spec: SchedulerSpec) -> bool:
        del spec
        existed = self.plist.exists() or self._loaded() is True
        self._bootout()  # a refused bootout keeps the plist, so the same command can retry
        self.plist.unlink(missing_ok=True)
        return existed

    def observe(self, spec: SchedulerSpec) -> SchedulerObservation:
        del spec
        installed = self.plist.is_file()
        try:
            loaded = self._loaded()
        except SchedulerError as error:
            return SchedulerObservation(installed, None, str(error))
        return SchedulerObservation(installed, loaded, None if loaded is not None else "launchctl print failed")
