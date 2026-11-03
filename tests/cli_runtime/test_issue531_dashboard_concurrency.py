"""The dashboard listener accepts a page's burst of module requests (iss-00531).

A screen loads app.js and then about a dozen ES modules and style sheets at once; with the standard listen
backlog of 5, macOS resets some of those connections and the whole page fails to start.
"""

from __future__ import annotations

import concurrent.futures
from typing import TYPE_CHECKING
import urllib.request

from spec_dock.runtime.infra import dashboard_server
from spec_dock.runtime.infra.dashboard_server import DashboardServer
from tests.support.canonical_repo import isolate_user_state
from tests.support.dashboard_site import register, sample, write_snapshot

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

PATHS = (
    "/assets/app.js",
    "/assets/app.css",
    "/assets/core/ui.js",
    "/assets/views/board.js",
    "/assets/views/scope.js",
    "/assets/views/_shared/logic.js",
    "/assets/views/_shared/parts.js",
    "/assets/views/_shared/search.js",
)


class _NoTailscale:
    def ipv4(self) -> str | None:
        return None

    def dns_name(self) -> str | None:
        return None


def test_the_listen_backlog_is_larger_than_a_page_burst() -> None:
    assert dashboard_server._Listener.request_queue_size >= 64


def test_a_burst_of_parallel_requests_is_served_without_resets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    isolate_user_state(monkeypatch, tmp_path)
    root = tmp_path / "state" / "spec-dock"
    register(root, "github.com/o/r", tmp_path / "r" / "c")
    write_snapshot(root, sample("github.com/o/r"))
    server = DashboardServer(root, port=0, probe=_NoTailscale())
    urls = server.start()
    base = urls.local.rstrip("/")

    def get(path: str) -> object:
        try:
            with urllib.request.urlopen(base + path, timeout=10) as response:
                return response.status
        except OSError as error:  # a reset connection surfaces as URLError / ConnectionResetError
            return f"{type(error).__name__}: {error}"

    try:
        for _ in range(3):
            with concurrent.futures.ThreadPoolExecutor(64) as pool:
                results = list(pool.map(get, PATHS * 8))
            assert results == [200] * len(results), [item for item in results if item != 200][:3]
    finally:
        server.stop()
