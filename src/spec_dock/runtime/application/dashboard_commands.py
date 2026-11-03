"""`spec-dock dashboard serve`, `hide`, `show` and `list` (iss-00529 D-01; Epic D-01, D-02, D-13).

`serve` runs in the foreground until Ctrl-C or SIGTERM. `hide`/`show` write only the per-user hidden marks;
the registry, the catalog and the periodic sync are untouched, so a hidden repository keeps syncing. `list`
reads the registry, the marks and the server location record (only whether its pid is alive). None of them
sends a request to GitHub.
"""

from __future__ import annotations

from datetime import datetime, timezone
import signal
import sys
from typing import TYPE_CHECKING

from spec_dock.runtime.application.canonical_errors import CanonicalCommandError
from spec_dock.runtime.application.dashboard_site import DashboardSite
from spec_dock.runtime.application.dashboard_summary import parse_repository
from spec_dock.runtime.application.project_context import require_migrated, resolve_git_context
from spec_dock.runtime.infra.dashboard_files import read_server_url
from spec_dock.runtime.infra.dashboard_server import (
    DEFAULT_PORT,
    DashboardAlreadyRunning,
    DashboardServer,
    DashboardServerError,
)
from spec_dock.runtime.infra.dashboard_store import DashboardStateUnreadable, hide_repository, show_repository
from spec_dock.runtime.infra.git_process import GitProcessError
from spec_dock.runtime.infra.github_structure import repository_for_checkout
from spec_dock.runtime.infra.state_root import resolve_state_root
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import OperationResult

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable
    from pathlib import Path

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.infra.github_structure import GithubRepository

DASHBOARD_STATE_UNREADABLE = "DASHBOARD_STATE_UNREADABLE"


def _stop_on_schema_three(namespace: argparse.Namespace, cwd: Path) -> None:
    """`serve` and `list` need no checkout, but inside a schema-3 one they stop like every command (0.5.0)."""
    try:
        root = resolve_git_context(namespace.project, cwd, timeout=namespace.timeout).root
    except (OSError, ValueError, GitProcessError):
        return  # outside any checkout: nothing to admit
    require_migrated(root)


def _result(command: str, data: dict[str, object]) -> OperationResult[object]:
    return OperationResult(command, "succeeded", FamilyData("dashboard", data), 0)


# --- serve -----------------------------------------------------------------------------------------------------


def _announce(server: DashboardServer, write: Callable[[str], object]) -> list[str]:
    assert server.urls is not None
    shown = [site.key for site in server.site.repositories()]
    lines = [f"dashboard: {server.urls.local}"]
    if server.urls.tailscale:
        lines.append(f"dashboard (tailnet): {server.urls.tailscale}")
        lines.append("the repositories below are readable from every device of this tailnet:")
    else:
        lines.append("only this PC can open it; the repositories shown:")
    lines.extend(f"  {key}  {server.urls.local.rstrip('/')}/r/{key}/" for key in shown)
    if not shown:
        lines.append("  (none: register one with `spec-dock canonical link`, or `spec-dock dashboard show`)")
    lines.append("stop with Ctrl-C")
    write("\n".join(lines) + "\n")
    return shown


def serve(
    namespace: argparse.Namespace,
    cwd: Path,
    *,
    state_root: Path | None = None,
    server_factory: Callable[..., DashboardServer] = DashboardServer,
) -> OperationResult[object]:
    _stop_on_schema_three(namespace, cwd)
    command = namespace.command_path
    port = namespace.port if namespace.port is not None else DEFAULT_PORT
    if not 0 <= port <= 65535:
        raise CanonicalCommandError("DASHBOARD_PORT_INVALID", f"{port} is not a port number", exit_code=2)
    root = state_root if state_root is not None else resolve_state_root()
    server = server_factory(root, port=port, tailscale=bool(namespace.tailscale))
    try:
        urls = server.start()
    except DashboardAlreadyRunning as running:
        record = running.record or {}
        return _result(command, {"already_running": True, "urls": record.get("urls"), "pid": record.get("pid")})
    except DashboardServerError as error:
        raise CanonicalCommandError(error.code, error.message, recovery=error.recovery) from None
    previous = {sig: signal.getsignal(sig) for sig in (signal.SIGTERM, signal.SIGINT)}

    def stop(_signum: int, _frame: object) -> None:
        server.request_stop()

    for sig in previous:
        signal.signal(sig, stop)
    try:
        shown = _announce(server, sys.stderr.write)
        sys.stderr.flush()
        while not server.wait(0.5):
            pass
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)
        server.stop()
    return _result(
        command,
        {
            "already_running": False,
            "stopped": True,
            "urls": {"local": urls.local, "tailscale": urls.tailscale},
            "repositories": shown,
        },
    )


# --- hide / show ---------------------------------------------------------------------------------------------


def _mark(command: str, repository: GithubRepository, root: Path) -> OperationResult[object]:
    hide = command == "dashboard hide"
    try:
        if hide:
            changed = hide_repository(root, repository, now=datetime.now(timezone.utc))
        else:
            changed = show_repository(root, repository)
    except DashboardStateUnreadable as error:
        raise CanonicalCommandError(
            DASHBOARD_STATE_UNREADABLE,
            "the dashboard's hidden marks cannot be read; they are not overwritten",
            recovery=(f"inspect or remove {error.path}",),
            details={"path": str(error.path), "reason": error.reason},
        ) from None
    registered = any(row.repository == repository.key for row in DashboardSite(root).rows())
    return _result(
        command,
        {"repository": repository.key, "hidden": hide, "changed": changed, "registered": registered},
    )


def mark_named(namespace: argparse.Namespace, cwd: Path) -> OperationResult[object] | None:
    del cwd
    if not namespace.repository:
        return None
    return _mark(namespace.command_path, parse_repository(namespace.repository), resolve_state_root())


def mark_checkout(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    try:
        repository = repository_for_checkout(context.root, timeout=namespace.timeout)
    except ValueError as error:
        raise CanonicalCommandError(
            "DASHBOARD_REPOSITORY_INVALID",
            "this checkout's origin remote does not name a github.com repository; pass REPOSITORY",
            exit_code=2,
            details={"reason": str(error)},
        ) from error
    return _mark(namespace.command_path, repository, resolve_state_root())


# --- list ------------------------------------------------------------------------------------------------------


def list_repositories(
    namespace: argparse.Namespace, cwd: Path, *, state_root: Path | None = None
) -> OperationResult[object]:
    _stop_on_schema_three(namespace, cwd)
    root = state_root if state_root is not None else resolve_state_root()
    site = DashboardSite(root)
    server = read_server_url(root)
    rows = []
    for row in site.rows():
        path = f"/r/{row.repository}/" if row.repository else None
        rows.append({
            "repository": row.repository,
            "catalog": row.catalog,
            "main_checkout": row.main_checkout,
            "hidden": row.hidden,
            "served": row.served,
            "problem": row.problem,
            "path": path,
            "url": f"{server.rstrip('/')}{path}" if server and path and row.served else None,
        })
    data: dict[str, object] = {"repositories": rows, "server": server, "registry_error": site.registry_error()}
    return _result(namespace.command_path, data)
