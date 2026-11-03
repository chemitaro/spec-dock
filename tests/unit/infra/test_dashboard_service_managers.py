"""The dashboard service on launchd and systemd, with fake launchctl/systemctl (iss-00530 D-02, T-02, T-03)."""

from __future__ import annotations

from pathlib import Path
import plistlib
import subprocess

import pytest

from spec_dock.runtime.domain.dashboard_service import DashboardServiceSpec, ServiceSettings
from spec_dock.runtime.infra.canonical_scheduling import SchedulerError
from spec_dock.runtime.infra.dashboard_service import DashboardLaunchdService, DashboardSystemdService


class Commands:
    """launchctl and systemctl answered from memory; `answers` makes one verb fail."""

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


@pytest.fixture
def spec(tmp_path: Path) -> DashboardServiceSpec:
    return DashboardServiceSpec(
        tmp_path / "bin/spec-dock", tmp_path / "state", Path("/usr/bin"), tmp_path / "home", port=47800
    )


def test_launchd_service_installs_once_restarts_on_change_and_removes(
    tmp_path: Path, spec: DashboardServiceSpec
) -> None:
    agents = tmp_path / "agents"
    sync_plist = agents / "io.github.chemitaro.spec-dock.canonical-sync.plist"
    sync_plist.parent.mkdir()
    sync_plist.write_bytes(b"sync")
    commands = Commands()
    service = DashboardLaunchdService(agents_dir=agents, uid=501, runner=commands, sleep=lambda _s: None)

    assert service.ensure(spec) == "created"
    plist = agents / "io.github.chemitaro.spec-dock.dashboard.plist"
    assert service.path == plist
    assert plistlib.loads(plist.read_bytes())["KeepAlive"] is True
    assert ["launchctl", "bootstrap", "gui/501", str(plist)] in commands.calls

    commands.calls.clear()
    assert service.ensure(spec) == "unchanged"
    assert all(call[1] == "print" for call in commands.calls)

    changed = DashboardServiceSpec(spec.executable, spec.state_root, spec.git_dir, spec.home, port=47801)
    commands.calls.clear()
    assert service.ensure(changed) == "updated"
    assert [call[1] for call in commands.calls] == ["print", "bootout", "bootstrap"]
    assert service.recorded_settings() == ServiceSettings(47801, False, spec.state_root)
    assert service.observe(changed).installed is True and service.observe(changed).active is True

    assert service.remove(changed) is True
    assert not plist.exists()
    assert ["launchctl", "bootout", "gui/501/io.github.chemitaro.spec-dock.dashboard"] in commands.calls
    assert service.remove(changed) is False
    assert service.recorded_settings() is None
    assert sync_plist.read_bytes() == b"sync"


def test_launchd_service_keeps_the_plist_when_bootout_is_refused(tmp_path: Path, spec: DashboardServiceSpec) -> None:
    commands = Commands()
    service = DashboardLaunchdService(agents_dir=tmp_path / "agents", uid=501, runner=commands, sleep=lambda _s: None)
    service.ensure(spec)
    commands.answers["bootout"] = 5

    with pytest.raises(SchedulerError, match="bootout"):
        service.remove(spec)
    assert service.path.exists()


def test_systemd_service_enables_restarts_on_change_and_removes(tmp_path: Path, spec: DashboardServiceSpec) -> None:
    units = tmp_path / "systemd/user"
    commands = Commands()
    service = DashboardSystemdService(unit_dir=units, runner=commands)

    assert service.ensure(spec) == "created"
    unit = units / "spec-dock-dashboard.service"
    assert service.path == unit
    assert "Restart=always" in unit.read_text()
    assert commands.verbs() == [
        "is-active spec-dock-dashboard.service",
        "daemon-reload",
        "enable --now spec-dock-dashboard.service",
    ]

    commands.calls.clear()
    assert service.ensure(spec) == "unchanged"
    assert commands.verbs() == ["is-active spec-dock-dashboard.service"]

    changed = DashboardServiceSpec(
        spec.executable, spec.state_root, spec.git_dir, spec.home, port=47801, tailscale=True
    )
    commands.calls.clear()
    assert service.ensure(changed) == "updated"
    assert commands.verbs()[-1] == "restart spec-dock-dashboard.service"
    assert service.recorded_settings() == ServiceSettings(47801, True, spec.state_root)
    observed = service.observe(changed)
    assert (observed.installed, observed.active) == (True, True)

    commands.calls.clear()
    assert service.remove(changed) is True
    assert not unit.exists()
    assert commands.verbs() == ["disable --now spec-dock-dashboard.service", "daemon-reload"]
    assert service.remove(changed) is False


def test_systemd_service_stops_when_disable_is_refused(tmp_path: Path, spec: DashboardServiceSpec) -> None:
    commands = Commands()
    service = DashboardSystemdService(unit_dir=tmp_path / "units", runner=commands)
    service.ensure(spec)
    commands.answers["disable"] = 1

    with pytest.raises(SchedulerError, match="disable"):
        service.remove(spec)
    assert service.path.exists()


def test_systemd_enable_failure_is_a_scheduler_error(tmp_path: Path, spec: DashboardServiceSpec) -> None:
    service = DashboardSystemdService(unit_dir=tmp_path / "units", runner=Commands({"enable": 1}))

    with pytest.raises(SchedulerError, match="enable"):
        service.ensure(spec)
