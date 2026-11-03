"""`dashboard serve`, `hide`, `show`, `list` and the live listener (iss-00529 T-10〜T-13, T-15)."""

from __future__ import annotations

import http.client
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
from typing import TYPE_CHECKING, Any
import urllib.request
import zipfile

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra import dashboard_server
from spec_dock.runtime.infra.dashboard_server import (
    DashboardAlreadyRunning,
    DashboardServer,
    DashboardServerError,
)
from tests.support.canonical_repo import bare_remote, clone, git, isolate_user_state
from tests.support.dashboard_site import register, sample, write_snapshot

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture
def state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    isolate_user_state(monkeypatch, tmp_path)
    monkeypatch.chdir(tmp_path)
    root = tmp_path / "state" / "spec-dock"
    register(root, "github.com/o/r", tmp_path / "r" / "c")
    register(root, "github.com/o/s", tmp_path / "s" / "c")
    write_snapshot(root, sample("github.com/o/r"))
    write_snapshot(root, sample("github.com/o/s"))
    return root


class Probe:
    def __init__(self, address: str | None, dns: str | None = None) -> None:
        self.address, self.dns = address, dns

    def ipv4(self) -> str | None:
        return self.address

    def dns_name(self) -> str | None:
        return self.dns


@pytest.fixture
def server(state: Path) -> Iterator[DashboardServer]:
    running = DashboardServer(state, port=0, probe=Probe(None))
    running.start()
    yield running
    running.stop()


def _get(url: str) -> tuple[int, dict[str, str], bytes]:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as error:
        return error.code, dict(error.headers), error.read()


def _raw(port: int, method: str, path: str, headers: dict[str, str], body: bytes = b"") -> tuple[int, bytes]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    connection.putrequest(method, path, skip_host=True)
    for key, value in headers.items():
        connection.putheader(key, value)
    connection.putheader("Content-Length", str(len(body)))
    connection.endheaders(body)
    response = connection.getresponse()
    result = response.status, response.read()
    connection.close()
    return result


# --- T-10 ----------------------------------------------------------------------------------------------------


def test_the_listener_serves_every_repository_and_new_registrations(
    server: DashboardServer, state: Path, tmp_path: Path
) -> None:
    assert server.urls is not None
    base = server.urls.local
    assert base == f"http://127.0.0.1:{server.port}/"
    record = json.loads((state / "dashboard" / "server.json").read_text())
    assert record["urls"] == {"local": base, "tailscale": None} and record["pid"] == os.getpid()
    status, _headers, body = _get(base + "api/v1/repositories")
    assert status == 200 and [item["repository"] for item in json.loads(body)["repositories"]] == [
        "github.com/o/r",
        "github.com/o/s",
    ]
    for repo in ("o/r", "o/s"):
        assert _get(f"{base}api/v1/r/github.com/{repo}/structure")[0] == 200
        status, headers, page = _get(f"{base}r/github.com/{repo}/board")
        assert status == 200 and b'id="view"' in page and headers["Content-Security-Policy"].endswith("'self'")
    register(state, "github.com/o/t", tmp_path / "t" / "c")
    body = _get(base + "api/v1/repositories")[2]
    assert "github.com/o/t" in [item["repository"] for item in json.loads(body)["repositories"]]
    head = _raw(server.port, "HEAD", "/", {"Host": f"127.0.0.1:{server.port}"})
    assert head == (200, b"")


def test_the_listener_checks_host_and_seen_headers(server: DashboardServer, state: Path) -> None:
    port = server.port
    assert _raw(port, "GET", "/", {"Host": f"evil.example:{port}"})[0] == 421
    assert _raw(port, "GET", "/", {"Host": f"localhost:{port}"})[0] == 200
    seen = "/api/v1/r/github.com/o/r/seen"
    good = {
        "Host": f"127.0.0.1:{port}",
        "Origin": f"http://127.0.0.1:{port}",
        "X-SpecDock-Dashboard": "1",
        "Content-Type": "application/json",
    }
    assert _raw(port, "POST", seen, {**good, "Origin": "http://evil.example"}, b"{}")[0] == 403
    status, body = _raw(port, "POST", seen, good, b"{}")
    assert status == 200 and json.loads(body)["seen_id"]
    assert _raw(port, "POST", seen, good, b"x" * (64 * 1024 + 1))[0] == 413
    assert _raw(port, "DELETE", "/", {"Host": f"127.0.0.1:{port}"})[0] == 405


def test_a_second_server_reports_the_running_one_and_stop_removes_the_record(state: Path) -> None:
    first = DashboardServer(state, port=0, probe=Probe(None))
    first.start()
    try:
        with pytest.raises(DashboardAlreadyRunning) as raised:
            DashboardServer(state, port=0, probe=Probe(None)).start()
        assert raised.value.record is not None and raised.value.record["pid"] == os.getpid()
    finally:
        first.stop()
    assert not (state / "dashboard" / "server.json").exists()
    again = DashboardServer(state, port=0, probe=Probe(None))
    again.start()
    again.stop()


# --- T-11 ----------------------------------------------------------------------------------------------------


def test_a_used_port_and_a_missing_tailscale_address_stop_before_listening(state: Path) -> None:
    holder = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    holder.bind(("127.0.0.1", 0))
    holder.listen(1)
    try:
        with pytest.raises(DashboardServerError) as raised:
            DashboardServer(state, port=holder.getsockname()[1], probe=Probe(None)).start()
        assert raised.value.code == "DASHBOARD_PORT_IN_USE" and "--port" in raised.value.recovery[0]
    finally:
        holder.close()
    assert not (state / "dashboard" / "server.json").exists()
    with pytest.raises(DashboardServerError) as raised:
        DashboardServer(state, port=0, tailscale=True, probe=Probe(None)).start()
    assert raised.value.code == "DASHBOARD_TAILSCALE_UNAVAILABLE"
    assert not (state / "dashboard" / "server.json").exists()
    released = DashboardServer(state, port=0, probe=Probe(None))  # the lock was released
    released.start()
    released.stop()


def test_tailscale_adds_the_address_to_the_listeners_hosts_and_record(
    state: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bound: list[tuple[str, int]] = []

    class FakeListener:
        def __init__(self, address: tuple[str, int], _handler: object) -> None:
            bound.append(address)
            self.server_address = (address[0], address[1] or 47999)
            self.RequestHandlerClass = _handler

        def serve_forever(self) -> None:
            return

        def shutdown(self) -> None:
            return

        def server_close(self) -> None:
            return

    monkeypatch.setattr(dashboard_server, "_Listener", FakeListener)
    running = DashboardServer(state, port=0, tailscale=True, probe=Probe("100.64.0.7", "mac.tail1.ts.net"))
    urls = running.start()
    try:
        assert bound == [("127.0.0.1", 0), ("100.64.0.7", 47999)]
        assert urls.tailscale == "http://100.64.0.7:47999/"
        assert running.app is not None
        assert running.app.hosts == ("127.0.0.1", "localhost", "100.64.0.7", "mac.tail1.ts.net")
        assert running.app.embed_hosts == ("127.0.0.1", "localhost", "100.64.0.7")
        record = json.loads((state / "dashboard" / "server.json").read_text())
        assert record["urls"] == {"local": "http://127.0.0.1:47999/", "tailscale": "http://100.64.0.7:47999/"}
    finally:
        running.stop()


# --- T-12 ----------------------------------------------------------------------------------------------------


def _console() -> list[str]:
    return [sys.executable, "-c", "import sys; from spec_dock.cli import main; sys.exit(main(sys.argv[1:]))"]


def test_serve_runs_in_the_foreground_and_stops_on_sigterm(state: Path, tmp_path: Path) -> None:
    env = {**os.environ, "XDG_STATE_HOME": str(tmp_path / "state")}
    process = subprocess.Popen(
        [*_console(), "dashboard", "serve", "--port", "0", "--json"],
        env=env,
        cwd=tmp_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    record_path = state / "dashboard" / "server.json"
    try:
        deadline = time.monotonic() + 20
        while not record_path.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        record = json.loads(record_path.read_text())
        assert record["pid"] == process.pid
        status = _get(record["urls"]["local"] + "api/v1/repositories")[0]
        assert status == 200
        second = subprocess.run(
            [*_console(), "dashboard", "serve", "--port", "0", "--json"],
            env=env,
            cwd=tmp_path,
            capture_output=True,
            timeout=30,
            check=False,
        )
        result = json.loads(second.stdout)
        assert second.returncode == 0 and result["data"]["result"]["already_running"] is True
        assert result["data"]["result"]["urls"]["local"] == record["urls"]["local"]
        summary = subprocess.run(
            [*_console(), "dashboard", "summary", "o/r", "--json"],
            env=env,
            cwd=tmp_path,
            capture_output=True,
            check=False,
        )
        assert json.loads(summary.stdout)["data"]["result"]["server"] == record["urls"]["local"]
    finally:
        process.send_signal(signal.SIGTERM)
        stdout, stderr = process.communicate(timeout=30)
    assert process.returncode == 0, stderr
    final = json.loads(stdout)
    assert final["data"]["result"]["stopped"] is True
    assert final["data"]["result"]["repositories"] == ["github.com/o/r", "github.com/o/s"]
    assert b"github.com/o/r" in stderr and b"stop with Ctrl-C" in stderr
    assert not record_path.exists()


def test_serve_rejects_a_bad_port(state: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["dashboard", "serve", "--port", "70000", "--json"]) == 2
    assert json.loads(capsys.readouterr().out)["error"]["code"] == "DASHBOARD_PORT_INVALID"


# --- T-13 ----------------------------------------------------------------------------------------------------


def _run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, Any]:
    code = main([*argv, "--json"])
    return code, json.loads(capsys.readouterr().out)


def test_hide_show_and_list_outside_a_checkout(state: Path, capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    registry = (state / "canonical-registry.json").read_bytes()
    register(state, None, tmp_path / "unknown" / "c")
    code, listed = _run(capsys, "dashboard", "list")
    rows = listed["data"]["result"]["repositories"]
    assert code == 0 and [(row["repository"], row["hidden"], row["served"]) for row in rows] == [
        ("github.com/o/r", False, True),
        ("github.com/o/s", False, True),
        (None, False, False),
    ]
    assert rows[2]["problem"] == "repository_unknown" and listed["data"]["result"]["server"] is None
    registry = (state / "canonical-registry.json").read_bytes()
    code, hidden = _run(capsys, "dashboard", "hide", "o/s")
    assert code == 0 and hidden["data"]["result"] == {
        "repository": "github.com/o/s",
        "hidden": True,
        "changed": True,
        "registered": True,
    }
    assert _run(capsys, "dashboard", "hide", "github.com/o/s")[1]["data"]["result"]["changed"] is False
    assert (state / "canonical-registry.json").read_bytes() == registry  # the sync keeps its registration
    rows = _run(capsys, "dashboard", "list")[1]["data"]["result"]["repositories"]
    assert (rows[1]["hidden"], rows[1]["served"]) == (True, False)
    assert main(["dashboard", "list"]) == 0
    text = capsys.readouterr().out
    assert "github.com/o/s hidden" in text and "(repository unknown) not served" in text
    code, shown = _run(capsys, "dashboard", "show", "o/s")
    assert code == 0 and shown["data"]["result"]["hidden"] is False and shown["data"]["result"]["changed"] is True
    assert _run(capsys, "dashboard", "hide", "x/y")[1]["data"]["result"]["registered"] is False
    assert _run(capsys, "dashboard", "hide", "not a repo")[0] == 2


def test_hide_inside_a_checkout_and_an_unreadable_marks_file(
    state: Path, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    checkout = clone(bare_remote(tmp_path / "remote.git"), tmp_path / "main")
    git(checkout, "remote", "set-url", "origin", "https://github.com/O/R.git")
    code, result = _run(capsys, "--project", str(checkout), "dashboard", "hide")
    assert code == 0, result
    assert result["data"]["result"]["repository"] == "github.com/o/r"
    (state / "dashboard" / "repositories.json").write_text("{broken")
    code, result = _run(capsys, "dashboard", "show", "o/r")
    assert (code, result["error"]["code"]) == (3, "DASHBOARD_STATE_UNREADABLE")
    assert (state / "dashboard" / "repositories.json").read_text() == "{broken"


def test_a_hidden_repository_leaves_a_running_server(
    server: DashboardServer, capsys: pytest.CaptureFixture[str]
) -> None:
    assert server.urls is not None
    base = server.urls.local
    assert _run(capsys, "dashboard", "hide", "o/s")[0] == 0
    listed = json.loads(_get(base + "api/v1/repositories")[2])
    assert [item["repository"] for item in listed["repositories"]] == ["github.com/o/r"]
    status, _headers, body = _get(base + "r/github.com/o/s/")
    assert status == 404 and b"spec-dock dashboard show o/s" in body and b"Scope" not in body
    rows = _run(capsys, "dashboard", "list")[1]["data"]["result"]
    assert rows["server"] == base and rows["repositories"][0]["url"] == f"{base}r/github.com/o/r/"
    assert _run(capsys, "dashboard", "show", "o/s")[0] == 0
    assert len(json.loads(_get(base + "api/v1/repositories")[2])["repositories"]) == 2


# --- T-15 ----------------------------------------------------------------------------------------------------

SCREEN_FILES = (
    "index.html",
    "app.css",
    "app.js",
    "core/api.js",
    "core/embed.js",
    "core/route.js",
    "core/topbar.js",
    "core/ui.js",
    "views/index.js",
    *(f"views/{name}.js" for name in ("graph", "board", "timeline", "scope", "overview")),
)
ASSETS = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "dashboard"


def test_the_screens_have_the_shell_and_five_slots() -> None:
    for name in SCREEN_FILES:
        assert (ASSETS / name).is_file(), name
    table = (ASSETS / "views" / "index.js").read_text()
    assert "export const VIEWS = { graph, board, timeline, scope, overview };" in table
    for name in ("graph", "board", "timeline", "scope", "overview"):
        assert f'import {name} from "./{name}.js";' in table
        source = (ASSETS / "views" / f"{name}.js").read_text()
        assert "export default" in source and f'id: "{name}"' in source, name
    app = (ASSETS / "app.js").read_text()
    assert 'from "./views/index.js"' in app and "markSeen" in app and "REFRESH_MS = 5000" in app
    api = (ASSETS / "core" / "api.js").read_text()
    assert '"X-SpecDock-Dashboard": "1"' in api and '"Content-Type": "application/json"' in api
    embed = (ASSETS / "core" / "embed.js").read_text()
    for mark in ('source: "specdock", v: 1', '"ready"', '"navigated"', "event.source !== window.parent"):
        assert mark in embed, mark
    assert '"*"' not in embed.replace('never "*"', "")


def test_the_wheel_contains_the_screens(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[2]
    subprocess.run(["uv", "build", "--wheel", "--out-dir", str(tmp_path)], cwd=root, check=True, capture_output=True)
    (wheel,) = tmp_path.glob("*.whl")
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        for name in SCREEN_FILES:
            assert f"spec_dock/assets/dashboard/{name}" in names, name
        assert archive.read("spec_dock/assets/dashboard/app.js") == (ASSETS / "app.js").read_bytes()
