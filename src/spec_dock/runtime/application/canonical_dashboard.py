"""The legacy-shape dashboard of a canonical main checkout, redrawn by step 7 of the periodic sync (Epic ch. 13).

Only the periodic sync writes the five files, from the structure snapshot and only when its `issues` and
`external` changed or a file is missing. Each file is replaced by rename; a directory or symbolic link at a file's
place is left alone and recorded. Linked worktrees and legacy-mode (schema 3) checkouts get nothing. Failures go to
state.json `dashboard.error` and never change the sync result.
"""

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
import os
from pathlib import Path
import stat
from typing import TYPE_CHECKING

from spec_dock.runtime.application.canonical_errors import CANONICAL_DASHBOARD_FAILED, CANONICAL_DASHBOARD_OCCUPIED
from spec_dock.runtime.application.project_context import probe_workspace_mode
from spec_dock.runtime.domain.canonical_dashboard import DASHBOARD_FILES, dashboard_inputs, input_hash
from spec_dock.runtime.infra.canonical_registry import RegistryUnreadable, read_registry
from spec_dock.runtime.infra.canonical_state import CycleBusy, cycle_lock, read_catalog_state, update_catalog_state
from spec_dock.runtime.presentation.markdown import _render_dashboard_md
from spec_dock.runtime.presentation.puml import (
    render_deps_issues_puml,
    render_deps_raw_puml,
    render_tree_ready_board_puml,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from spec_dock.runtime.domain.canonical_structure import StructureSnapshot
    from spec_dock.runtime.domain.canonical_sync_state import CatalogSyncState, RegistryEntry

DASHBOARD_DIRECTORY = "spec-dock"
_LEGACY_INDEX_LINE = "- index: `spec-dock/.agent/index.json`"


@dataclass(frozen=True)
class DashboardOutcome:
    written: tuple[str, ...] = ()
    error: Mapping[str, object] | None = None
    skipped: str | None = None  # cycle_busy, unregistered, not_main, legacy_mode or no_state: state.json untouched


def dashboard_directory(main_checkout: Path) -> Path:
    return main_checkout / DASHBOARD_DIRECTORY


def render_dashboard_files(snapshot: StructureSnapshot, *, snapshot_path: Path) -> dict[str, str]:
    """The five files in DASHBOARD_FILES order, drawn by the unchanged legacy renderers."""
    inputs = dashboard_inputs(snapshot)
    markdown = _render_dashboard_md(inputs.index_nodes, active=None).replace(
        _LEGACY_INDEX_LINE, f"- snapshot: `{snapshot_path}`", 1
    )
    drawn = {
        "dashboard.md": markdown,
        "tree.puml": render_tree_ready_board_puml(inputs.tree, active=None, todo_only=True),
        "tree-all.puml": render_tree_ready_board_puml(inputs.tree, active=None, todo_only=False),
        "deps-issues.puml": render_deps_issues_puml(inputs.deps_issues),
        "deps-raw.puml": render_deps_raw_puml(inputs.deps_raw),
    }
    return {name: drawn[name] if drawn[name].endswith("\n") else drawn[name] + "\n" for name in DASHBOARD_FILES}


def is_regular_file(path: Path) -> bool:
    try:
        return stat.S_ISREG(os.lstat(path).st_mode)
    except OSError:
        return False


def refresh_dashboard(
    entry: RegistryEntry,
    snapshot: StructureSnapshot | None,
    *,
    snapshot_path: Path,
    state_root: Path,
    now: str,
    registered: bool,
) -> DashboardOutcome:
    """Step 7 for one catalog: redraw what changed under its cycle lock and record the result in state.json."""
    try:
        with cycle_lock(state_root, entry.catalog):
            if registered and _unregistered(state_root, entry.catalog):
                return DashboardOutcome(skipped="unregistered")
            main = Path(entry.main_checkout)
            if not (main / ".git").is_dir():  # a linked worktree: one clone has one structure (Epic ch. 13)
                return DashboardOutcome(skipped="not_main")
            if probe_workspace_mode(main) != "canonical":
                return DashboardOutcome(skipped="legacy_mode")
            return _redraw(entry, snapshot, main, snapshot_path=snapshot_path, state_root=state_root, now=now)
    except CycleBusy:
        return DashboardOutcome(skipped="cycle_busy")


def _unregistered(root: Path, catalog: str) -> bool:
    try:
        return read_registry(root).entry_for(catalog) is None
    except RegistryUnreadable:
        return False


def _error(code: str, message: str, now: str, paths: list[str]) -> dict[str, object]:
    return {"code": code, "message": message, "at": now, "paths": paths}


def _redraw(
    entry: RegistryEntry,
    snapshot: StructureSnapshot | None,
    main: Path,
    *,
    snapshot_path: Path,
    state_root: Path,
    now: str,
) -> DashboardOutcome:
    previous = read_catalog_state(state_root, entry.catalog)
    if previous is None:
        # Steps 1-6 create state.json with the catalog's baseline; a record made here would lack it.
        return DashboardOutcome(skipped="no_state")
    recorded = dict(previous.dashboard) if previous.dashboard is not None else {}
    directory = dashboard_directory(main)
    written: list[str] = []
    error: dict[str, object] | None = None
    digest = recorded.get("input_hash")
    if snapshot is None:
        error = _error(CANONICAL_DASHBOARD_FAILED, "no structure snapshot is available", now, [])
    else:
        digest = input_hash(snapshot, snapshot_path=str(snapshot_path))
        if digest != recorded.get("input_hash"):
            wanted = list(DASHBOARD_FILES)
        else:
            wanted = [name for name in DASHBOARD_FILES if not is_regular_file(directory / name)]
        if wanted:
            files = render_dashboard_files(snapshot, snapshot_path=snapshot_path)
            written, error = _write(directory, files, wanted, now)
        if error is not None and error["code"] == CANONICAL_DASHBOARD_FAILED:
            digest = recorded.get("input_hash")  # a file may hold old contents: redraw all next cycle
    dashboard = {
        "input_hash": digest,
        "written_at": now if written else recorded.get("written_at"),
        "error": error,
    }

    def mutate(current: CatalogSyncState | None) -> CatalogSyncState:
        return (current or previous).evolve(dashboard=dashboard)

    update_catalog_state(state_root, entry.catalog, mutate)
    return DashboardOutcome(tuple(written), error)


def _write(
    directory: Path, files: Mapping[str, str], wanted: list[str], now: str
) -> tuple[list[str], dict[str, object] | None]:
    try:
        is_directory = stat.S_ISDIR(os.lstat(directory).st_mode)
    except OSError:
        is_directory = False
    if not is_directory:
        message = f"{directory} is not a directory of the main checkout"
        return [], _error(CANONICAL_DASHBOARD_FAILED, message, now, [str(directory)])
    written: list[str] = []
    occupied: list[str] = []
    failed: list[str] = []
    reasons: list[str] = []
    for name in wanted:
        path = directory / name
        try:
            mode = os.lstat(path).st_mode
        except FileNotFoundError:
            mode = None
        except OSError as error:
            failed.append(str(path))
            reasons.append(f"{path}: {error.strerror or error}")
            continue
        if mode is not None and (stat.S_ISDIR(mode) or stat.S_ISLNK(mode)):
            occupied.append(str(path))
            continue
        try:
            _replace(path, files[name])
        except OSError as error:
            failed.append(str(path))
            reasons.append(f"{path}: {error.strerror or error}")
            continue
        written.append(name)
    if failed:
        return written, _error(CANONICAL_DASHBOARD_FAILED, "; ".join(reasons), now, failed + occupied)
    if occupied:
        message = "a directory or symbolic link is where a dashboard file goes: " + ", ".join(occupied)
        return written, _error(CANONICAL_DASHBOARD_OCCUPIED, message, now, occupied)
    return written, None


def _replace(path: Path, text: str) -> None:
    temporary = path.with_name(f".{path.name}.spec-dock-{os.getpid()}")
    with suppress(FileNotFoundError):
        temporary.unlink()  # a leftover of an interrupted cycle of this process id
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(text)
        Path(temporary).replace(path)
    finally:
        with suppress(FileNotFoundError):
            temporary.unlink()
