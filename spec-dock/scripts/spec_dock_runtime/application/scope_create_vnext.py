"""Resolve an explicit parent chain for local Scope creation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_dock_runtime.application.active_selection import show_active_selection
from spec_dock_runtime.application.create_local_scope import (
    AncestorState,
    create_local_scope,
    plan_local_scope_create,
    resume_local_scope,
)
from spec_dock_runtime.application.scope_query import ScopeView, load_scope_views, show_scope

if TYPE_CHECKING:
    from pathlib import Path

    from spec_dock_runtime.domain.selectors import ScopeKind


@dataclass(frozen=True)
class LocalCreateOutcome:
    scope_id: str | None
    kind: ScopeKind
    title: str
    parent_id: str | None
    path: str | None
    operation_id: str | None
    warnings: tuple[str, ...]


def _ancestor_state(view: ScopeView) -> AncestorState:
    return AncestorState(
        view.id,
        view.kind,
        view.backend.kind,
        view.status.state,
        view.status.stale,
        view.parent_id,
    )


def create_local_scope_command(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    kind: ScopeKind,
    title: str,
    parent_target: str | None,
    slug: str | None,
    updated_at: str,
    dry_run: bool,
    resume_id: str | None,
    lock_timeout: float,
) -> LocalCreateOutcome:
    views = load_scope_views(repo_root / "spec-dock")
    parent = None
    ancestors: tuple[AncestorState, ...] = ()
    if parent_target is not None:
        selection = show_active_selection(repo_root=repo_root, worktree_id=worktree_id)
        selected = show_scope(views, parent_target, selection=selection)
        parent = _ancestor_state(selected)
        if kind == "issue":
            if selected.parent_id is None:
                raise ValueError("issue parent has no initiative ancestor")
            initiative = show_scope(views, selected.parent_id)
            ancestors = (_ancestor_state(initiative),)
    plan = plan_local_scope_create(kind=kind, title=title, parent=parent, ancestors=ancestors, slug=slug)
    if dry_run:
        if resume_id is not None:
            raise ValueError("local Scope create recovery cannot be previewed")
        return LocalCreateOutcome(None, kind, plan.title, plan.parent_id, None, None, plan.warnings)
    common = {
        "repo_root": repo_root,
        "common_dir": common_dir,
        "worktree_id": worktree_id,
        "engine_digest": engine_digest,
        "expected_epoch": expected_epoch,
        "kind": kind,
        "title": plan.title,
        "parent": parent,
        "ancestors": ancestors,
        "slug": plan.slug,
        "lock_timeout": lock_timeout,
    }
    created = (
        resume_local_scope(**common, operation_id=resume_id)
        if resume_id is not None
        else create_local_scope(**common, updated_at=updated_at)
    )
    path = created.path.relative_to(repo_root).as_posix()
    return LocalCreateOutcome(
        created.id, kind, plan.title, plan.parent_id, path, created.operation_id, created.warnings
    )
