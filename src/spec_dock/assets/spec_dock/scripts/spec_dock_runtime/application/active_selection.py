"""Pure Scope-chain selection and partial-clear decisions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_dock_runtime.application.scope_query import show_scope
from spec_dock_runtime.cli.admission import admit_writer
from spec_dock_runtime.domain.lifecycle import SelectionState
from spec_dock_runtime.infra.active_store import load_selection_v3, save_selection_v3
from spec_dock_runtime.infra.control_store import load_control
from spec_dock_runtime.infra.writer_lock import WriterLock

if TYPE_CHECKING:
    from pathlib import Path

    from spec_dock_runtime.application.scope_query import ScopeView


@dataclass(frozen=True)
class ActiveChangeResult:
    selection: SelectionState
    changed: bool


def show_active_selection(*, repo_root: Path, worktree_id: str) -> SelectionState:
    """Observe the current worktree selection without repairing or writing it."""
    return load_selection_v3(repo_root / "spec-dock", worktree_id=worktree_id)[0]


def _parent(views: tuple[ScopeView, ...], child: ScopeView, expected_kind: str) -> ScopeView:
    if child.parent_id is None:
        raise ValueError("Scope ancestry is incomplete")
    parent = show_scope(views, child.parent_id)
    if parent.kind != expected_kind:
        raise ValueError("Scope ancestry has the wrong kind")
    return parent


def select_scope(views: tuple[ScopeView, ...], target: str, *, current: SelectionState) -> SelectionState:
    """Select a real Scope and its exact ancestors, including completed Scopes."""
    selected = show_scope(views, target, selection=current)
    if selected.kind == "initiative":
        ids = (selected.id, None, None)
    elif selected.kind == "epic":
        initiative = _parent(views, selected, "initiative")
        ids = (initiative.id, selected.id, None)
    else:
        epic = _parent(views, selected, "epic")
        initiative = _parent(views, epic, "initiative")
        ids = (initiative.id, epic.id, selected.id)
    if ids == (current.initiative_id, current.epic_id, current.issue_id):
        return current
    return SelectionState(current.worktree_id, current.revision + 1, *ids, selected.id)


def clear_selection(
    views: tuple[ScopeView, ...],
    *,
    current: SelectionState,
    from_target: str | None = None,
    all_scopes: bool = False,
) -> SelectionState:
    """Drop a selected Scope and its descendants while keeping surviving ancestors."""
    if all_scopes == (from_target is not None):
        raise ValueError("select exactly one active clear mode")
    if all_scopes:
        ids = (None, None, None)
    else:
        assert from_target is not None
        selected = show_scope(views, from_target, selection=current)
        if selected.id not in (current.initiative_id, current.epic_id, current.issue_id):
            return current
        if selected.kind == "initiative":
            ids = (None, None, None)
        elif selected.kind == "epic":
            ids = (current.initiative_id, None, None)
        else:
            ids = (current.initiative_id, current.epic_id, None)
    if ids == (current.initiative_id, current.epic_id, current.issue_id):
        return current
    focus = ids[2] or ids[1] or ids[0]
    return SelectionState(current.worktree_id, current.revision + 1, *ids, focus)


def _decide_selection(
    *,
    repo_root: Path,
    common_dir: Path,
    views: tuple[ScopeView, ...],
    current: SelectionState,
    target: str | None,
    from_branch: bool,
    clear_from: str | None,
    clear_all: bool,
) -> SelectionState:
    if sum((target is not None, from_branch, clear_from is not None, clear_all)) != 1:
        raise ValueError("select exactly one active mutation")
    if from_branch:
        from spec_dock_runtime.application.branch_vnext import scope_from_current_branch

        target = scope_from_current_branch(repo_root, common_dir)
    if target is not None:
        return select_scope(views, target, current=current)
    return clear_selection(views, current=current, from_target=clear_from, all_scopes=clear_all)


def preview_active_change(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    target: str | None = None,
    from_branch: bool = False,
    clear_from: str | None = None,
    clear_all: bool = False,
) -> ActiveChangeResult:
    """Preview one selection change without taking a writer lock or publishing state."""
    from spec_dock_runtime.application.scope_query import load_scope_views

    specdock_dir = repo_root / "spec-dock"
    views = load_scope_views(specdock_dir)
    current, _identity = load_selection_v3(specdock_dir, worktree_id=worktree_id)
    next_selection = _decide_selection(
        repo_root=repo_root,
        common_dir=common_dir,
        views=views,
        current=current,
        target=target,
        from_branch=from_branch,
        clear_from=clear_from,
        clear_all=clear_all,
    )
    return ActiveChangeResult(next_selection, next_selection != current)


def change_active_selection(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    target: str | None = None,
    from_branch: bool = False,
    clear_from: str | None = None,
    clear_all: bool = False,
    lock_timeout: float = 0.0,
) -> ActiveChangeResult:
    """Admit and commit one worktree-local selection change without network or Git effects."""
    from spec_dock_runtime.application.scope_query import load_scope_views

    specdock_dir = repo_root / "spec-dock"
    with WriterLock(common_dir, timeout=lock_timeout):
        admit_writer(
            load_control(common_dir),
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
        )
        views = load_scope_views(specdock_dir)
        current, identity = load_selection_v3(specdock_dir, worktree_id=worktree_id)
        next_selection = _decide_selection(
            repo_root=repo_root,
            common_dir=common_dir,
            views=views,
            current=current,
            target=target,
            from_branch=from_branch,
            clear_from=clear_from,
            clear_all=clear_all,
        )
        if next_selection == current:
            return ActiveChangeResult(current, False)
        save_selection_v3(specdock_dir, next_selection, views=views, expected_identity=identity)
        return ActiveChangeResult(next_selection, True)
