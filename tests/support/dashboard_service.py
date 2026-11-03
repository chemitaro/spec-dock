"""Fake launchctl/systemctl and a fake platform for the dashboard service (iss-00530).

The suite guard (tests/conftest.py) points `dashboard_service_for` at services whose job files live under a
temporary directory and whose launchctl/systemctl answers come from `ServiceCommands`; nothing reaches the
real service manager or the user's LaunchAgents.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
import subprocess
from typing import TYPE_CHECKING

from spec_dock.runtime.infra.dashboard_service import (
    DashboardLaunchdService,
    DashboardService,
    DashboardSystemdService,
)
from spec_dock.runtime.infra.runtime_environment import GitInstallation, RuntimeEnvironment

if TYPE_CHECKING:
    from pathlib import Path


class ServiceCommands:
    """launchctl and systemctl answered from memory; `answers` makes one verb fail with that exit code."""

    def __init__(self, answers: dict[str, int] | None = None) -> None:
        self.calls: list[list[str]] = []
        self.answers = answers or {}
        self.loaded = False

    def verbs(self) -> list[str]:
        return [" ".join(call[1:] if call[0] == "launchctl" else call[2:]).split(" /")[0] for call in self.calls]

    def __call__(self, argv: list[str], **_kwargs: object) -> subprocess.CompletedProcess[bytes]:
        self.calls.append(argv)
        verb = argv[1] if argv[0] == "launchctl" else argv[2]
        failed = self.answers.get(verb, 0)
        if argv[0] == "launchctl":
            if verb == "print":
                return subprocess.CompletedProcess(argv, 0 if self.loaded else 113, b"", b"")
            if verb == "bootstrap" and not failed:
                self.loaded = True
            if verb == "bootout" and not failed:
                self.loaded = False
        else:
            if verb == "is-active":
                return subprocess.CompletedProcess(argv, 0, b"active\n" if self.loaded else b"inactive\n", b"")
            if verb == "enable" and not failed:
                self.loaded = True
            if verb == "disable" and not failed:
                self.loaded = False
        return subprocess.CompletedProcess(argv, failed, b"", b"refused" if failed else b"")


@dataclass
class FakeServices:
    """The platform a test pretends to run on and the fake service manager behind it."""

    root: Path
    system: str = "linux"
    systemd: bool = False
    commands: ServiceCommands = field(default_factory=ServiceCommands)

    @property
    def agents_dir(self) -> Path:
        return self.root / "LaunchAgents"

    @property
    def unit_dir(self) -> Path:
        return self.root / "systemd-user"

    def environment(self) -> RuntimeEnvironment:
        import os

        base = RuntimeEnvironment(
            self.system,  # type: ignore[arg-type]
            (),
            GitInstallation(None, None, None),
            dict(os.environ),
        )
        return replace(base, systemd_present=self.systemd, systemd_user=self.systemd)

    def service_for(self, kind: str, **_kwargs: object) -> DashboardService:
        if kind == "launchd":
            return DashboardLaunchdService(
                agents_dir=self.agents_dir, uid=501, runner=self.commands, sleep=lambda _s: None
            )
        return DashboardSystemdService(unit_dir=self.unit_dir, runner=self.commands)
