"""The dashboard service's job files: a launchd agent or a systemd user unit kept alive (iss-00530 D-01; Epic D-14).

The service runs `spec-dock dashboard serve --service` with the port, the Tailscale choice and the state root
written into its command line, under its own label so it never shares a file with the periodic sync job.
"""

from __future__ import annotations

from dataclasses import dataclass
import plistlib
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.domain.canonical_scheduler import (
    LAUNCHD_PATH_TAIL,
    SYSTEMD_PATH_TAIL,
    SchedulerSpec,
    state_root_argument,
    systemd_quote,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

DASHBOARD_LAUNCHD_LABEL: Final = "io.github.chemitaro.spec-dock.dashboard"
DASHBOARD_SYSTEMD_SERVICE: Final = "spec-dock-dashboard.service"
SERVICE_LOG: Final = "dashboard/service.log"
DEFAULT_SERVICE_PORT: Final = 47800
VERSION_CHANGED_EXIT: Final = 75  # EX_TEMPFAIL: the service manager starts the new version
RESTART_SECONDS: Final = 10
LOCK_RETRY_SECONDS: Final = 30.0
TAILSCALE_RETRY_SECONDS: Final = 30.0
VERSION_CHECK_SECONDS: Final = 60.0
_SERVE: Final = ("dashboard", "serve", "--service")


@dataclass(frozen=True)
class DashboardServiceSpec(SchedulerSpec):
    """The periodic job's spec, with the server's port, Tailscale choice and the directory of `tailscale`."""

    port: int = DEFAULT_SERVICE_PORT
    tailscale: bool = False
    tailscale_dir: Path | None = None
    # The install's absolute XDG_CONFIG_HOME, so the server reads the same settings file as the CLI (iss-00552).
    config_home: Path | None = None

    def environment(self, tail: str) -> dict[str, str]:
        values = {"PATH": self.search_path(tail)}
        if self.config_home is not None:
            values["XDG_CONFIG_HOME"] = str(self.config_home)
        return values

    def search_path(self, tail: str) -> str:
        directories = [str(self.git_dir)]
        if self.tailscale_dir is not None and self.tailscale_dir != self.git_dir:
            directories.append(str(self.tailscale_dir))
        return ":".join([*directories, tail])

    @property
    def log(self) -> Path:
        return self.state_root / SERVICE_LOG

    def arguments(self) -> tuple[str, ...]:
        return (
            str(self.executable),
            *_SERVE,
            "--port",
            str(self.port),
            *(("--tailscale",) if self.tailscale else ()),
            "--state-root",
            str(self.state_root),
        )


@dataclass(frozen=True)
class ServiceSettings:
    port: int
    tailscale: bool
    state_root: Path | None


def dashboard_launchd_plist(spec: DashboardServiceSpec, *, label: str = DASHBOARD_LAUNCHD_LABEL) -> bytes:
    return plistlib.dumps({
        "Label": label,
        "ProgramArguments": list(spec.arguments()),
        "WorkingDirectory": str(spec.home),
        "RunAtLoad": True,
        "KeepAlive": True,
        "ThrottleInterval": RESTART_SECONDS,
        "StandardOutPath": str(spec.log),
        "StandardErrorPath": str(spec.log),
        "EnvironmentVariables": spec.environment(LAUNCHD_PATH_TAIL),
    })


def dashboard_systemd_unit(spec: DashboardServiceSpec) -> str:
    """One long-running service; its output goes to the journal (`journalctl --user -u spec-dock-dashboard`)."""
    command = " ".join(systemd_quote(argument, command=True) for argument in spec.arguments())
    environment = "".join(
        f"Environment={systemd_quote(f'{key}={value}')}\n" for key, value in spec.environment(SYSTEMD_PATH_TAIL).items()
    )
    return (
        "[Unit]\n"
        "Description=SpecDock dashboard server\n"
        "[Service]\n"
        "Type=simple\n"
        "WorkingDirectory=%h\n"
        f"{environment}"
        f"ExecStart={command}\n"
        "Restart=always\n"
        f"RestartSec={RESTART_SECONDS}\n"
        "[Install]\n"
        "WantedBy=default.target\n"
    )


def service_settings(arguments: Sequence[object]) -> ServiceSettings | None:
    """The port, Tailscale choice and state root of a recorded `dashboard serve --service` command line."""
    words = list(arguments)
    if tuple(words[1:4]) != _SERVE:
        return None
    port = DEFAULT_SERVICE_PORT
    if "--port" in words:
        index = words.index("--port")
        value = words[index + 1] if index + 1 < len(words) else None
        if not isinstance(value, str) or not value.isdigit():
            return None
        port = int(value)
    return ServiceSettings(port, "--tailscale" in words, state_root_argument(words))
