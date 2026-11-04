"""`spec-dock dashboard summary [REPOSITORY]` (epic-00427 D-01, D-05, D-12; iss-00528).

It reads only per-user files (the structure snapshot, the hidden marks, the server location record) and never
sends a request to GitHub or to the dashboard server. With REPOSITORY it needs no checkout; without it the
repository comes from this checkout's origin remote, which is a local Git read.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.application import todo_common
from spec_dock.runtime.application.canonical_catalog import require_linked
from spec_dock.runtime.application.canonical_errors import CanonicalCommandError
from spec_dock.runtime.application.dashboard_site import read_visibility
from spec_dock.runtime.application.todo_aggregate import registry_summary_todos, summary_todos
from spec_dock.runtime.domain.dashboard_model import build_model
from spec_dock.runtime.infra.dashboard_files import read_server_url, read_snapshot_file
from spec_dock.runtime.infra.github_structure import GithubRepository, repository_for_checkout
from spec_dock.runtime.infra.state_root import resolve_state_root
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.dashboard_summary import summary_document
from spec_dock.runtime.presentation.envelope import OperationResult

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable
    from pathlib import Path

    from spec_dock.runtime.application.project_context import ProjectContext

DASHBOARD_REPOSITORY_INVALID: Final = "DASHBOARD_REPOSITORY_INVALID"
DASHBOARD_SNAPSHOT_MISSING: Final = "DASHBOARD_SNAPSHOT_MISSING"
DASHBOARD_SNAPSHOT_UNREADABLE: Final = "DASHBOARD_SNAPSHOT_UNREADABLE"
DASHBOARD_SNAPSHOT_UNSUPPORTED: Final = "DASHBOARD_SNAPSHOT_UNSUPPORTED"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _todo_now() -> datetime:
    return todo_common.utc_now()


def summarize(
    command: str,
    repository: GithubRepository,
    *,
    state_root: Path | None = None,
    now: Callable[[], datetime] = _utc_now,
    catalog: tuple[Path, str] | None = None,
    todo_now: Callable[[], datetime] = _todo_now,
) -> OperationResult[object]:
    """`catalog` is (catalog, main checkout) of a correctly linked checkout; otherwise the registry chooses."""
    root = state_root if state_root is not None else resolve_state_root()
    read = read_snapshot_file(root, repository)
    if read.status == "missing":
        raise CanonicalCommandError(
            DASHBOARD_SNAPSHOT_MISSING,
            f"there is no structure snapshot for {repository.slug}",
            recovery=("spec-dock canonical link", "spec-dock canonical status"),
            details={"repository": repository.key, "path": str(read.path)},
        )
    if read.status == "unsupported":
        raise CanonicalCommandError(
            DASHBOARD_SNAPSHOT_UNSUPPORTED,
            f"the structure snapshot of {repository.slug} has a version this SpecDock does not know",
            recovery=("update the spec-dock package", "spec-dock --version"),
            details={"repository": repository.key, "path": str(read.path), "reason": read.detail},
        )
    if read.status == "unreadable" or read.parsed is None:
        raise CanonicalCommandError(
            DASHBOARD_SNAPSHOT_UNREADABLE,
            f"the structure snapshot of {repository.slug} cannot be read",
            recovery=("spec-dock canonical status", "wait for the next periodic sync, or run spec-dock canonical sync"),
            details={"repository": repository.key, "path": str(read.path), "reason": read.detail},
        )
    current = now()
    model = build_model(read.parsed.snapshot, now=current, confirmed_at=read.confirmed_at(current))
    todos = (
        summary_todos(catalog[0], catalog[1], now=todo_now())
        if catalog is not None
        else registry_summary_todos(root, repository, now=todo_now())
    )
    hidden = read_visibility(root, repository, catalog[0] if catalog is not None else None).hidden
    summary = summary_document(model, hidden=hidden, server=read_server_url(root), todos=todos)
    return OperationResult(command, "succeeded", FamilyData("dashboard", summary), 0)


def parse_repository(value: str) -> GithubRepository:
    try:
        return GithubRepository.parse(value)
    except ValueError as error:
        raise CanonicalCommandError(
            DASHBOARD_REPOSITORY_INVALID,
            f"{value!r} is not owner/name or github.com/owner/name",
            exit_code=2,
            details={"repository": value},
        ) from error


def summarize_named(namespace: argparse.Namespace, cwd: Path) -> OperationResult[object] | None:
    """With REPOSITORY the summary needs no checkout; without it, decline to the checkout dispatch."""
    del cwd
    if not namespace.repository:
        return None
    return summarize(namespace.command_path, parse_repository(namespace.repository))


def summarize_checkout(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    try:
        repository = repository_for_checkout(context.root, timeout=namespace.timeout)
    except ValueError as error:
        raise CanonicalCommandError(
            DASHBOARD_REPOSITORY_INVALID,
            "this checkout's origin remote does not name a github.com repository; pass REPOSITORY",
            exit_code=2,
            details={"reason": str(error)},
        ) from error
    try:
        linked = require_linked(context, timeout=namespace.timeout)
        catalog: tuple[Path, str] | None = (linked.catalog, str(linked.layout.main_checkout))
    except CanonicalCommandError:  # not linked here: the registry chooses the catalog (Epic D-15)
        catalog = None
    return summarize(namespace.command_path, repository, catalog=catalog)
