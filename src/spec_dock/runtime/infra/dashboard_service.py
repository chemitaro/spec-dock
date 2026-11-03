"""The dashboard service on launchd and systemd, built on the periodic job's schedulers (iss-00530 D-02; Epic D-14).

Only the job file differs from the sync job: a launchd agent kept alive, or one systemd user service with
`Restart=always` (no timer). launchctl/systemctl handling, atomic writes and errors are the schedulers'.
dashboard_service_for() is the single factory (tests replace it); installed_version() reads the installed
package's version again, so a running server can see an upgrade.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
import plistlib
import shlex
import subprocess
import time
from typing import TYPE_CHECKING, Literal

from spec_dock.runtime.domain.dashboard_service import (
    DASHBOARD_LAUNCHD_LABEL,
    DASHBOARD_SYSTEMD_SERVICE,
    DashboardServiceSpec,
    ServiceSettings,
    dashboard_launchd_plist,
    dashboard_systemd_unit,
    service_settings,
)
from spec_dock.runtime.infra.canonical_scheduler_launchd import LaunchdScheduler
from spec_dock.runtime.infra.canonical_scheduler_systemd import SystemdScheduler
from spec_dock.runtime.infra.canonical_scheduling import (
    EnsureOutcome,
    SchedulerError,
    SchedulerObservation,
    write_atomic,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from spec_dock.runtime.domain.canonical_scheduler import SchedulerSpec
    from spec_dock.runtime.infra.runtime_environment import RuntimeEnvironment

ServiceKind = Literal["launchd", "systemd"]


def _dashboard(spec: SchedulerSpec) -> DashboardServiceSpec:
    if not isinstance(spec, DashboardServiceSpec):
        raise TypeError("the dashboard service needs a DashboardServiceSpec")
    return spec


class DashboardLaunchdService(LaunchdScheduler):
    """~/Library/LaunchAgents/io.github.chemitaro.spec-dock.dashboard.plist, kept alive by launchd."""

    def __init__(
        self,
        *,
        agents_dir: Path,
        uid: int | None = None,
        runner: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        super().__init__(agents_dir=agents_dir, label=DASHBOARD_LAUNCHD_LABEL, uid=uid, runner=runner, sleep=sleep)

    @property
    def path(self) -> Path:
        return self.plist

    def _payload(self, spec: SchedulerSpec) -> bytes:
        return dashboard_launchd_plist(_dashboard(spec), label=self.label)

    def recorded_settings(self) -> ServiceSettings | None:
        try:
            arguments = plistlib.loads(self.plist.read_bytes()).get("ProgramArguments")
        except (OSError, ValueError, plistlib.InvalidFileException):
            return None
        return service_settings(arguments) if isinstance(arguments, list) else None


class DashboardSystemdService(SystemdScheduler):
    """~/.config/systemd/user/spec-dock-dashboard.service: one service restarted always, enabled for login."""

    def __init__(
        self,
        *,
        unit_dir: Path,
        runner: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
    ) -> None:
        # One unit and no timer: `timer` names the service so inherited lookups never reach a timer file.
        super().__init__(
            unit_dir=unit_dir, service=DASHBOARD_SYSTEMD_SERVICE, timer=DASHBOARD_SYSTEMD_SERVICE, runner=runner
        )

    @property
    def path(self) -> Path:
        return self.unit_dir / self.service

    def _active(self) -> bool | None:
        completed = self._systemctl("is-active", self.service)
        state = completed.stdout.decode(errors="replace").strip()
        return state == "active" if state else None

    def _unit(self, spec: SchedulerSpec) -> bytes:
        return dashboard_systemd_unit(_dashboard(spec)).encode()

    def needs_change(self, spec: SchedulerSpec) -> bool:
        try:
            if self.path.read_bytes() != self._unit(spec):
                return True
        except FileNotFoundError:
            return True
        return self._active() is False

    def ensure(self, spec: SchedulerSpec) -> EnsureOutcome:
        existed = self.path.exists()
        was_active = self._active()
        changed = write_atomic(self.path, self._unit(spec))
        if not changed and was_active:
            return "unchanged"
        self._systemctl("daemon-reload", check=True)
        self._systemctl("enable", "--now", self.service, check=True)
        if changed and was_active:
            self._systemctl("restart", self.service, check=True)  # enable --now leaves a running old one
        return "updated" if existed else "created"

    def kick(self, spec: SchedulerSpec) -> None:
        del spec
        self._systemctl("restart", self.service, check=True)

    def remove(self, spec: SchedulerSpec) -> bool:
        del spec
        existed = self.path.exists()
        disabled = self._systemctl("disable", "--now", self.service)
        if disabled.returncode != 0 and existed:
            raise SchedulerError(
                f"systemctl --user disable --now failed: {disabled.stderr.decode(errors='replace').strip()}"
            )
        self.path.unlink(missing_ok=True)
        self._systemctl("daemon-reload")
        return existed

    def observe(self, spec: SchedulerSpec) -> SchedulerObservation:
        del spec
        installed = self.path.is_file()
        try:
            active = self._active()
        except SchedulerError as error:
            return SchedulerObservation(installed, None, str(error))
        return SchedulerObservation(installed, active)

    def recorded_settings(self) -> ServiceSettings | None:
        try:
            text = self.path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None
        for line in text.splitlines():
            if line.startswith("ExecStart="):
                try:
                    return service_settings(shlex.split(line.removeprefix("ExecStart=").replace("%%", "%")))
                except ValueError:
                    return None
        return None


DashboardService = DashboardLaunchdService | DashboardSystemdService


def dashboard_service_for(kind: ServiceKind, *, environment: RuntimeEnvironment) -> DashboardService:
    """The production dashboard service of `kind`; tests replace this function."""
    from pathlib import Path

    home = environment.home or Path.home()
    if kind == "launchd":
        return DashboardLaunchdService(agents_dir=home / "Library/LaunchAgents")
    config = environment.environ.get("XDG_CONFIG_HOME", "")
    base = Path(config) if config and Path(config).is_absolute() else home / ".config"
    return DashboardSystemdService(unit_dir=base / "systemd/user")


def installed_version() -> str | None:
    """The installed spec-dock package's version now (it changes when the tool is upgraded), or None."""
    try:
        return version("spec-dock")
    except (PackageNotFoundError, ValueError, OSError):
        return None
