"""The dashboard server's listener (iss-00529 D-02; Epic D-02, D-06).

Standard library only: one `ThreadingHTTPServer` on 127.0.0.1 and, with `--tailscale`, one on the Tailscale
IPv4 address, both on the same port (never 0.0.0.0). The handler only turns a request into a `Request` for
`DashboardHttp` and writes the `Response`. Start: take `<state_root>/dashboard/server.lock` without waiting,
find the Tailscale address, listen, then write `server.json`; stop removes this process's record only.
"""

from __future__ import annotations

from contextlib import ExitStack
from dataclasses import dataclass
from datetime import datetime, timezone
import errno
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
import threading
from typing import TYPE_CHECKING, ClassVar, Final
from urllib.parse import parse_qs, urlsplit

from spec_dock import __version__
from spec_dock.runtime.application.dashboard_http import DashboardHttp, Request
from spec_dock.runtime.application.dashboard_site import DashboardSite
from spec_dock.runtime.infra.canonical_state import file_lock
from spec_dock.runtime.infra.dashboard_network import LocalTailscale
from spec_dock.runtime.infra.dashboard_store import (
    SERVER_LOCK_FILE,
    dashboard_dir,
    read_server_record,
    remove_server_record,
    write_server_record,
)

if TYPE_CHECKING:
    from pathlib import Path

    from spec_dock.runtime.infra.dashboard_network import TailscaleProbe

DEFAULT_PORT: Final = 47800
LOCAL_HOST: Final = "127.0.0.1"
MAX_BODY: Final = 64 * 1024


class DashboardServerError(Exception):
    def __init__(self, code: str, message: str, *, recovery: tuple[str, ...] = ()) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.recovery = recovery


class DashboardAlreadyRunning(Exception):
    """Another server holds the lock; `record` is its location record (None while it is starting)."""

    def __init__(self, record: dict[str, object] | None) -> None:
        super().__init__("a dashboard server is already running")
        self.record = record


class _LockBusy(TimeoutError):
    pass


class _Handler(BaseHTTPRequestHandler):
    app: ClassVar[DashboardHttp]
    server_version = "SpecDockDashboard"
    sys_version = ""

    def _dispatch(self) -> None:
        split = urlsplit(self.path)
        if self.path.startswith("//") or split.scheme or split.netloc:
            split = urlsplit("/" + self.path.lstrip("/"))  # never read an absolute-form target as a host
        body = b""
        if self.command == "POST":
            try:
                length = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                length = -1
            if length < 0 or length > MAX_BODY:
                self.send_error(413)
                return
            body = self.rfile.read(length)
        headers = {key.lower(): value for key, value in self.headers.items()}
        request = Request(self.command, split.path or "/", parse_qs(split.query, keep_blank_values=True), headers, body)
        response = self.app.handle(request)
        self.send_response(response.status)
        for key, value in response.headers:
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(response.body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(response.body)

    do_GET = do_HEAD = do_POST = do_PUT = do_DELETE = do_PATCH = do_OPTIONS = _dispatch

    def log_message(self, *_args: object) -> None:  # type: ignore[override]
        return  # requests are not logged (paths may name private Scopes)


class _Listener(ThreadingHTTPServer):
    daemon_threads = True
    # A screen loads about a dozen modules at once; the standard backlog of 5 makes macOS reset some of them
    # and the page fails to start (iss-00531).
    request_queue_size = 128
    allow_reuse_address = True


@dataclass(frozen=True)
class ServerUrls:
    local: str
    tailscale: str | None


def _utc(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


class DashboardServer:
    def __init__(
        self,
        state_root: Path,
        *,
        port: int = DEFAULT_PORT,
        tailscale: bool = False,
        probe: TailscaleProbe | None = None,
        version: str = __version__,
    ) -> None:
        self.state_root = state_root
        self.requested_port = port
        self.tailscale = tailscale
        self.probe = probe if probe is not None else LocalTailscale()
        self.version = version
        self.site = DashboardSite(state_root)
        self._stack = ExitStack()
        self._listeners: list[_Listener] = []
        self._threads: list[threading.Thread] = []
        self._stopped = threading.Event()
        self.port = 0
        self.urls: ServerUrls | None = None
        self.app: DashboardHttp | None = None

    def start(self) -> ServerUrls:
        try:
            self._stack.enter_context(file_lock(dashboard_dir(self.state_root) / SERVER_LOCK_FILE, error=_LockBusy))
        except _LockBusy:
            raise DashboardAlreadyRunning(read_server_record(self.state_root)) from None
        try:
            return self._start_locked()
        except BaseException:
            self._close()
            raise

    def _start_locked(self) -> ServerUrls:
        address: str | None = None
        dns: str | None = None
        if self.tailscale:
            address = self.probe.ipv4()
            if address is None:
                raise DashboardServerError(
                    "DASHBOARD_TAILSCALE_UNAVAILABLE",
                    "the Tailscale IPv4 address could not be read (`tailscale ip -4`)",
                    recovery=("tailscale status", "spec-dock dashboard serve  (without --tailscale)"),
                )
            dns = self.probe.dns_name()
        port = self.requested_port
        for host in (LOCAL_HOST, *([address] if address else [])):
            try:
                listener = _Listener((host, port), _Handler)
            except OSError as error:
                if error.errno == errno.EADDRINUSE:
                    raise DashboardServerError(
                        "DASHBOARD_PORT_IN_USE",
                        f"port {port} on {host} is already in use",
                        recovery=("spec-dock dashboard serve --port <another number>",),
                    ) from error
                raise DashboardServerError(
                    "DASHBOARD_LISTEN_FAILED", f"cannot listen on {host}:{port}: {error.strerror or error}"
                ) from error
            self._listeners.append(listener)
            port = listener.server_address[1]
        self.port = port
        local = f"http://{LOCAL_HOST}:{port}/"
        remote = f"http://{address}:{port}/" if address else None
        hosts = (LOCAL_HOST, "localhost", *([address] if address else []), *([dns] if dns else []))
        embed_hosts = (LOCAL_HOST, "localhost", *([address] if address else []))
        started = _utc(datetime.now(timezone.utc))
        self.app = DashboardHttp(
            self.site,
            hosts=hosts,
            port=port,
            embed_hosts=embed_hosts,
            local_url=local,
            version=self.version,
            started_at=started,
        )
        handler = type("DashboardHandler", (_Handler,), {"app": self.app})
        for listener in self._listeners:
            listener.RequestHandlerClass = handler
            thread = threading.Thread(target=listener.serve_forever, name="spec-dock-dashboard", daemon=True)
            thread.start()
            self._threads.append(thread)
        write_server_record(
            self.state_root, local=local, tailscale=remote, pid=os.getpid(), version=self.version, started_at=started
        )
        self.urls = ServerUrls(local, remote)
        return self.urls

    def wait(self, timeout: float | None = None) -> bool:
        return self._stopped.wait(timeout)

    def request_stop(self) -> None:
        """Safe from a signal handler: only sets the event that `wait` returns on."""
        self._stopped.set()

    def stop(self) -> None:
        self._stopped.set()
        for listener in self._listeners:
            listener.shutdown()
        for thread in self._threads:
            thread.join(timeout=5)
        if self.urls is not None:
            remove_server_record(self.state_root, pid=os.getpid())
        self._close()

    def _close(self) -> None:
        for listener in self._listeners:
            listener.server_close()
        self._listeners.clear()
        self._stack.close()
