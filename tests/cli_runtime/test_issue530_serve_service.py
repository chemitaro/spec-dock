"""`dashboard serve --service`: lock wait, late Tailscale address, upgrade exit 75 (iss-00530 T-07〜T-09, T-11)."""

from __future__ import annotations

import argparse
import functools
import json
import os
import signal
import subprocess
import sys
import threading
import time
from typing import TYPE_CHECKING, Any, ClassVar
import urllib.request

import pytest

from spec_dock.runtime.application.dashboard_commands import ServeTiming, serve
from spec_dock.runtime.application.dashboard_http import Request
from spec_dock.runtime.infra import dashboard_server
from spec_dock.runtime.infra.dashboard_server import DashboardServer
from spec_dock.runtime.infra.dashboard_store import read_server_record
from tests.support.canonical_repo import isolate_user_state
from tests.support.dashboard_site import register, sample, write_snapshot

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

FAST = ServeTiming(lock_retry=0.05, tailscale_retry=0.05, version_check=0.05, tick=0.02)


@pytest.fixture
def state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    isolate_user_state(monkeypatch, tmp_path)
    monkeypatch.chdir(tmp_path)
    root = tmp_path / "state" / "spec-dock"
    register(root, "github.com/o/r", tmp_path / "r" / "c")
    write_snapshot(root, sample("github.com/o/r"))
    return root


class Probe:
    def __init__(self, *answers: str | None) -> None:
        self.answers = list(answers)

    def ipv4(self) -> str | None:
        return self.answers.pop(0) if len(self.answers) > 1 else self.answers[0]

    def dns_name(self) -> str | None:
        return "mac.tail1.ts.net"


def _namespace(*, service: bool, tailscale: bool = False) -> argparse.Namespace:
    return argparse.Namespace(
        command_path="dashboard serve",
        project=None,
        timeout=30.0,
        port=0,
        tailscale=tailscale,
        service=service,
        state_root=None,
    )


def _until(condition: Callable[[], bool], timeout: float = 10.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(0.02)
    return False


def _local(state: Path) -> str | None:
    record: Any = read_server_record(state)
    return record["urls"]["local"] if record else None


def _tailnet(state: Path) -> str | None:
    record: Any = read_server_record(state)
    return record["urls"]["tailscale"] if record else None


def _later(action: Callable[[], object]) -> threading.Thread:
    thread = threading.Thread(target=action, daemon=True)
    thread.start()
    return thread


def _versions(*values: str | None) -> Callable[[], str | None]:
    answers = list(values)
    return lambda: answers.pop(0) if len(answers) > 1 else answers[0]


# --- T-07 ----------------------------------------------------------------------------------------------------


def test_the_service_waits_for_the_lock_and_takes_over(state: Path, tmp_path: Path) -> None:
    foreground = DashboardServer(state, port=0)
    foreground.start()
    stop = threading.Event()
    seen: dict[str, Any] = {}

    def drive() -> None:
        time.sleep(0.3)  # the service is waiting on the busy lock by now
        waiting = _local(state)
        foreground.stop()
        seen["took_over"] = _until(lambda: _local(state) not in (None, waiting))
        seen["local"] = _local(state)
        stop.set()

    thread = _later(drive)
    result = serve(_namespace(service=True), tmp_path, timing=FAST, version_reader=lambda: "1", stop=stop)
    thread.join(5)
    assert seen["took_over"] is True
    assert result.exit_code == 0 and result.data.result["stopped"] is True  # type: ignore[attr-defined]
    assert result.data.result["urls"]["local"] == seen["local"]  # type: ignore[attr-defined]
    assert read_server_record(state) is None


def test_a_waiting_service_ends_with_0_when_stopped(state: Path, tmp_path: Path) -> None:
    foreground = DashboardServer(state, port=0)
    foreground.start()
    stop = threading.Event()
    try:
        threading.Timer(0.2, stop.set).start()
        result = serve(_namespace(service=True), tmp_path, timing=FAST, version_reader=lambda: "1", stop=stop)
    finally:
        foreground.stop()
    assert result.exit_code == 0 and result.data.result["already_running"] is True  # type: ignore[attr-defined]


# --- T-08 ----------------------------------------------------------------------------------------------------


def test_the_service_exits_75_after_an_upgrade_and_removes_its_record(state: Path, tmp_path: Path) -> None:
    started: dict[str, bool] = {}
    _later(lambda: started.setdefault("record", _until(lambda: read_server_record(state) is not None)))
    with pytest.raises(SystemExit) as ended:
        serve(_namespace(service=True), tmp_path, timing=FAST, version_reader=_versions("0.5.0", "0.5.0", "0.6.0"))
    assert ended.value.code == 75
    assert started["record"] is True
    assert read_server_record(state) is None


def test_the_foreground_server_keeps_running_and_reports_the_upgrade(
    state: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    stop = threading.Event()
    seen: dict[str, Any] = {}

    def drive() -> None:
        _until(lambda: read_server_record(state) is not None)
        url = read_server_record(state)["urls"]["local"] + "api/v1/repositories"  # type: ignore[index]

        def upgraded() -> bool:
            with urllib.request.urlopen(url, timeout=5) as response:
                seen["server"] = json.loads(response.read())["server"]
            return seen["server"]["installed_version"] == "0.6.1"  # each read refreshes it

        seen["upgraded"] = _until(upgraded)
        stop.set()

    _later(drive)
    result = serve(
        _namespace(service=False), tmp_path, timing=FAST, version_reader=_versions("0.5.0", "0.6.0", "0.6.1"), stop=stop
    )
    assert seen["upgraded"] is True and seen["server"]["restart_required"] is True
    assert result.exit_code == 0 and result.data.result["stopped"] is True  # type: ignore[attr-defined]
    assert capsys.readouterr().err.count("is installed; restart") == 1


def test_the_foreground_server_clears_the_notice_when_the_started_version_returns(state: Path, tmp_path: Path) -> None:
    stop = threading.Event()
    seen: list[dict[str, Any]] = []
    installed = {"version": "0.5.0"}

    def drive() -> None:
        _until(lambda: _local(state) is not None)
        url = f"{_local(state)}api/v1/repositories"

        def read() -> dict[str, Any]:
            with urllib.request.urlopen(url, timeout=5) as response:
                server: dict[str, Any] = json.loads(response.read())["server"]
            seen.append(server)
            return server

        installed["version"] = "0.6.0"
        _until(lambda: read()["restart_required"] is True)
        installed["version"] = "0.5.0"
        _until(lambda: read()["restart_required"] is False)
        stop.set()

    _later(drive)
    serve(_namespace(service=False), tmp_path, timing=FAST, version_reader=lambda: installed["version"], stop=stop)
    assert any(item["restart_required"] for item in seen)
    assert seen[-1]["restart_required"] is False and seen[-1]["installed_version"] == "0.5.0"


# --- T-09 ----------------------------------------------------------------------------------------------------


class FakeListener:
    bound: ClassVar[list[tuple[str, int]]] = []

    def __init__(self, address: tuple[str, int], handler: object) -> None:
        FakeListener.bound.append(address)
        self.server_address = (address[0], address[1] or 47999)
        self.RequestHandlerClass = handler

    def serve_forever(self) -> None:
        return

    def shutdown(self) -> None:
        return

    def server_close(self) -> None:
        return


def test_the_service_starts_locally_and_adds_the_tailscale_address_later(
    state: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(dashboard_server, "_Listener", FakeListener)
    FakeListener.bound = []
    servers: list[DashboardServer] = []

    def factory(*args: Any, **kwargs: Any) -> DashboardServer:
        server = DashboardServer(*args, probe=Probe(None, None, "100.64.0.7"), **kwargs)
        servers.append(server)
        return server

    stop = threading.Event()
    seen: dict[str, Any] = {}

    def drive() -> None:
        _until(lambda: read_server_record(state) is not None)
        seen["first"] = read_server_record(state)
        seen["added"] = _until(lambda: _tailnet(state) is not None)
        seen["record"] = read_server_record(state)
        app = servers[0].app
        assert app is not None
        headers = {"host": "100.64.0.7:47999"}
        seen["status"] = app.handle(Request("GET", "/api/v1/repositories", {}, headers, b"")).status
        seen["hosts"], seen["embed"] = app.hosts, app.embed_hosts
        stop.set()

    _later(drive)
    result = serve(
        _namespace(service=True, tailscale=True),
        tmp_path,
        server_factory=factory,
        timing=FAST,
        version_reader=lambda: "1",
        stop=stop,
    )
    assert seen["first"]["urls"] == {"local": "http://127.0.0.1:47999/", "tailscale": None}
    assert seen["added"] is True
    assert seen["record"]["urls"]["tailscale"] == "http://100.64.0.7:47999/"
    assert FakeListener.bound == [("127.0.0.1", 0), ("100.64.0.7", 47999)]
    assert seen["status"] == 200
    assert "100.64.0.7" in seen["hosts"] and "mac.tail1.ts.net" in seen["hosts"]
    assert seen["embed"][-1] == "100.64.0.7"
    assert result.data.result["urls"]["tailscale"] == "http://100.64.0.7:47999/"  # type: ignore[attr-defined]


def test_the_foreground_server_still_stops_without_a_tailscale_address(state: Path, tmp_path: Path) -> None:
    factory = functools.partial(DashboardServer, probe=Probe(None))
    with pytest.raises(Exception, match="DASHBOARD_TAILSCALE_UNAVAILABLE"):
        serve(_namespace(service=False, tailscale=True), tmp_path, server_factory=factory, timing=FAST)


# --- T-11 ----------------------------------------------------------------------------------------------------


def test_a_service_process_waits_on_a_busy_lock_and_ends_0_on_sigterm(state: Path, tmp_path: Path) -> None:
    foreground = DashboardServer(state, port=0)
    foreground.start()
    try:
        process = subprocess.Popen(
            [
                sys.executable,
                "-c",
                "import sys; from spec_dock.cli import main; sys.exit(main(sys.argv[1:]))",
                "dashboard",
                "serve",
                "--service",
                "--port",
                "0",
                "--state-root",
                str(state),
                "--json",
            ],
            env={**os.environ, "XDG_STATE_HOME": str(tmp_path / "elsewhere")},
            cwd=tmp_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        time.sleep(1.5)
        assert process.poll() is None  # still waiting, not exiting into a launchd/systemd restart loop
        process.send_signal(signal.SIGTERM)
        stdout, stderr = process.communicate(timeout=30)
    finally:
        foreground.stop()
    assert process.returncode == 0, stderr
    assert json.loads(stdout)["data"]["result"]["already_running"] is True
    assert b"the service waits" in stderr
