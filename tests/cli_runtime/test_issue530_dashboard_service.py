"""`dashboard service install`, `status`, `uninstall` with a fake service manager (iss-00530 T-04〜T-06)."""

from __future__ import annotations

import json
import os
import plistlib
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra import dashboard_service
from spec_dock.runtime.infra.dashboard_store import write_server_record
from tests.support.canonical_repo import isolate_user_state

if TYPE_CHECKING:
    from pathlib import Path

    from tests.support.dashboard_service import FakeServices

LABEL = "io.github.chemitaro.spec-dock.dashboard"


@pytest.fixture
def state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    isolate_user_state(monkeypatch, tmp_path)
    monkeypatch.chdir(tmp_path)
    return tmp_path / "state" / "spec-dock"


def _run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, Any]:
    code = main([*argv, "--json"])
    return code, json.loads(capsys.readouterr().out)


def test_launchd_install_status_and_uninstall(
    state: Path, dashboard_services: FakeServices, capsys: pytest.CaptureFixture[str]
) -> None:
    dashboard_services.system = "darwin"
    plist = dashboard_services.agents_dir / f"{LABEL}.plist"
    sync_plist = dashboard_services.agents_dir / "io.github.chemitaro.spec-dock.canonical-sync.plist"
    sync_plist.parent.mkdir(parents=True)
    sync_plist.write_bytes(b"sync job")

    code, before = _run(capsys, "dashboard", "service", "status")
    assert code == 0
    first = before["data"]["result"]
    assert (first["supported"], first["scheduler"], first["installed"]) == (True, "launchd", False)
    assert before["data"]["result"]["running"] is False

    code, installed = _run(capsys, "dashboard", "service", "install")
    result = installed["data"]["result"]
    assert code == 0 and result["outcome"] == "created" and result["scheduler"] == "launchd"
    assert result["path"] == str(plist) and result["url"] == "http://127.0.0.1:47800/"
    assert result["log"] == str(state / "dashboard" / "service.log")
    assert (state / "dashboard").is_dir()
    document = plistlib.loads(plist.read_bytes())
    assert document["KeepAlive"] is True
    assert document["ProgramArguments"][1:] == [
        "dashboard",
        "serve",
        "--service",
        "--port",
        "47800",
        "--state-root",
        str(state),
    ]
    assert dashboard_services.commands.verbs().count("bootstrap gui/501") == 1

    code, again = _run(capsys, "dashboard", "service", "install")
    assert code == 0 and again["data"]["result"]["outcome"] == "unchanged"
    assert again["effects"][0]["status"] == "unchanged"
    code, moved = _run(capsys, "dashboard", "service", "install", "--port", "47801", "--tailscale")
    assert code == 0 and moved["data"]["result"]["outcome"] == "updated"
    assert "bootout gui/501/" + LABEL in dashboard_services.commands.verbs()

    code, shown = _run(capsys, "dashboard", "service", "status")
    status = shown["data"]["result"]
    assert code == 0
    assert (status["installed"], status["loaded"], status["port"], status["tailscale"]) == (True, True, 47801, True)
    assert status["state_root"] == str(state) and status["running"] is False and status["server"] is None

    (state / "dashboard" / "service.log").write_text("log\n")
    code, removed = _run(capsys, "dashboard", "service", "uninstall")
    assert code == 0 and removed["data"]["result"] == {
        "scheduler": "launchd",
        "removed": True,
        "path": str(plist),
        "log_removed": True,
    }
    assert not plist.exists() and not (state / "dashboard" / "service.log").exists()
    code, twice = _run(capsys, "dashboard", "service", "uninstall")
    assert code == 0 and twice["data"]["result"]["removed"] is False
    assert twice["effects"][0]["status"] == "unchanged"
    assert sync_plist.read_bytes() == b"sync job"


def test_systemd_install_and_uninstall(
    state: Path, dashboard_services: FakeServices, capsys: pytest.CaptureFixture[str]
) -> None:
    dashboard_services.systemd = True
    unit = dashboard_services.unit_dir / "spec-dock-dashboard.service"

    code, installed = _run(capsys, "dashboard", "service", "install", "--tailscale")
    assert code == 0 and installed["data"]["result"]["scheduler"] == "systemd"
    assert installed["data"]["result"]["log"] is None
    text = unit.read_text()
    assert "Restart=always" in text and "--service" in text and "--tailscale" in text
    assert "enable --now spec-dock-dashboard.service" in dashboard_services.commands.verbs()

    code, removed = _run(capsys, "dashboard", "service", "uninstall")
    assert code == 0 and removed["data"]["result"]["removed"] is True and not unit.exists()


def test_status_shows_the_running_server_and_a_pending_restart(
    state: Path, dashboard_services: FakeServices, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    dashboard_services.system = "darwin"
    assert _run(capsys, "dashboard", "service", "install")[0] == 0
    write_server_record(
        state,
        local="http://127.0.0.1:47800/",
        tailscale=None,
        pid=os.getpid(),
        version="0.5.0",
        started_at="2026-11-04T00:00:00Z",
    )
    monkeypatch.setattr(dashboard_service, "installed_version", lambda: "0.5.0")
    status = _run(capsys, "dashboard", "service", "status")[1]["data"]["result"]
    assert status["running"] is True and status["restart_pending"] is False
    assert status["server"]["urls"] == {"local": "http://127.0.0.1:47800/", "tailscale": None}
    assert status["server"]["pid"] == os.getpid() and status["package_version"] == "0.5.0"

    monkeypatch.setattr(dashboard_service, "installed_version", lambda: "0.6.0")
    status = _run(capsys, "dashboard", "service", "status")[1]["data"]["result"]
    assert status["restart_pending"] is True and status["server"]["version"] == "0.5.0"


def test_without_a_service_manager_install_stops_and_the_others_succeed(
    state: Path, dashboard_services: FakeServices, capsys: pytest.CaptureFixture[str]
) -> None:
    code, refused = _run(capsys, "dashboard", "service", "install")
    assert code == 3 and refused["error"]["code"] == "DASHBOARD_SERVICE_UNSUPPORTED"
    assert "spec-dock dashboard serve" in json.dumps(refused["recovery"])
    assert not dashboard_services.root.exists() and not (state / "dashboard").exists()
    status = _run(capsys, "dashboard", "service", "status")[1]["data"]["result"]
    assert status["supported"] is False and status["installed"] is False
    code, removed = _run(capsys, "dashboard", "service", "uninstall")
    assert code == 0 and removed["data"]["result"]["removed"] is False
    assert dashboard_services.commands.calls == []


@pytest.mark.parametrize("port", ["0", "70000"])
def test_install_refuses_a_port_outside_1_to_65535(
    state: Path, dashboard_services: FakeServices, capsys: pytest.CaptureFixture[str], port: str
) -> None:
    dashboard_services.system = "darwin"
    code, refused = _run(capsys, "dashboard", "service", "install", "--port", port)
    assert code == 2 and refused["error"]["code"] == "DASHBOARD_PORT_INVALID"
    assert dashboard_services.commands.calls == []


def test_a_failing_service_manager_stops_with_the_job_path(
    state: Path, dashboard_services: FakeServices, capsys: pytest.CaptureFixture[str]
) -> None:
    dashboard_services.system = "darwin"
    dashboard_services.commands.answers["bootstrap"] = 5
    code, failed = _run(capsys, "dashboard", "service", "install")
    assert code == 3 and failed["error"]["code"] == "DASHBOARD_SERVICE_FAILED"
    assert failed["error"]["details"]["path"] == str(dashboard_services.agents_dir / f"{LABEL}.plist")

    dashboard_services.commands.answers.clear()
    assert _run(capsys, "dashboard", "service", "install")[0] == 0
    dashboard_services.commands.answers["bootout"] = 5
    code, failed = _run(capsys, "dashboard", "service", "uninstall")
    assert code == 3 and failed["error"]["code"] == "DASHBOARD_SERVICE_FAILED"
    assert (dashboard_services.agents_dir / f"{LABEL}.plist").exists()


def test_an_installed_unit_is_seen_and_removed_while_the_user_manager_is_unknown(
    state: Path, dashboard_services: FakeServices, capsys: pytest.CaptureFixture[str]
) -> None:
    dashboard_services.systemd = True
    assert _run(capsys, "dashboard", "service", "install")[0] == 0
    dashboard_services.systemd = False  # `systemctl --user` unreachable for now
    status = _run(capsys, "dashboard", "service", "status")[1]["data"]["result"]
    assert (status["supported"], status["scheduler"], status["installed"]) == (False, "systemd", True)
    code, removed = _run(capsys, "dashboard", "service", "uninstall")
    assert code == 0 and removed["data"]["result"]["removed"] is True
    assert not (dashboard_services.unit_dir / "spec-dock-dashboard.service").exists()


@pytest.mark.parametrize("leaf", ["install", "uninstall"])
def test_install_and_uninstall_have_no_plan_only_form(
    state: Path, dashboard_services: FakeServices, capsys: pytest.CaptureFixture[str], leaf: str
) -> None:
    dashboard_services.system = "darwin"
    code = main(["dashboard", "service", leaf, "--dry-run", "--json"])
    assert code == 2
    assert dashboard_services.commands.calls == [] and not dashboard_services.root.exists()
