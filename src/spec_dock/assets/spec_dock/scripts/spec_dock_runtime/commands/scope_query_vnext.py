"""Scope observations and title-only edit command adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_dock_runtime.application.active_selection import show_active_selection
from spec_dock_runtime.application.edit_scope import edit_scope_title
from spec_dock_runtime.application.scope_query import list_scopes, load_scope_views, show_scope
from spec_dock_runtime.commands.scope_result_vnext import (
    ScopeData,
    ScopeStatusData,
    project_scope,
    project_scope_view,
)
from spec_dock_runtime.presentation.envelope import Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock_runtime.application.scope_query import ScopeView
    from spec_dock_runtime.commands.work_vnext import WorkContext


@dataclass(frozen=True)
class ScopeSummary:
    id: str
    kind: str
    title: str
    parent_id: str | None
    backend: str
    state: str
    state_source: str
    github_ref: str | None
    path: str
    revision: int


@dataclass(frozen=True)
class ScopeListData:
    snapshot_id: str
    items: tuple[ScopeSummary, ...]


@dataclass(frozen=True)
class ScopeShowData:
    snapshot_id: str
    item: ScopeSummary
    scope: ScopeData
    status: ScopeStatusData
    project: str
    worktree: str


@dataclass(frozen=True)
class ScopeEditData:
    scope_id: str
    title: str
    revision: int
    changed: bool
    scope: ScopeData
    status: ScopeStatusData
    project: str
    worktree: str
    snapshot_id: str


def _summary(context: WorkContext, view: ScopeView) -> ScopeSummary:
    try:
        relative = view.path.relative_to(context.repo_root).as_posix()
    except ValueError as error:
        raise ValueError("Scope path is outside the selected repository") from error
    return ScopeSummary(
        view.id,
        view.kind,
        view.title,
        view.parent_id,
        "github" if view.github_ref is not None else "local",
        view.status.state,
        view.status.source,
        view.github_ref,
        relative,
        view.revision,
    )


def run_scope_query(ns: argparse.Namespace, context: WorkContext) -> OperationResult[ScopeListData | ScopeShowData]:
    views = load_scope_views(context.repo_root / "spec-dock")
    selection = show_active_selection(repo_root=context.repo_root, worktree_id=context.worktree_id)
    if ns.command_path == "scope list":
        parent = show_scope(views, ns.parent, selection=selection).id if ns.parent else None
        listed = list_scopes(views, kind=ns.kind, parent_id=parent, state=ns.state)
        data: ScopeListData | ScopeShowData = ScopeListData(
            listed.snapshot_id,
            tuple(_summary(context, item) for item in listed.items),
        )
        target = None
    elif ns.command_path == "scope show":
        shown = show_scope(views, ns.target, selection=selection)
        snapshot = list_scopes(views).snapshot_id
        projection = project_scope_view(context, shown, snapshot_id=snapshot, requested=ns.target)
        data = ScopeShowData(
            snapshot,
            _summary(context, shown),
            projection.scope,
            projection.status,
            projection.project,
            projection.worktree,
        )
        target = projection.target
    else:
        raise ValueError("unsupported Scope query")
    return OperationResult(command=ns.command_path, status="succeeded", data=data, exit_code=0, target=target)


def run_scope_edit(ns: argparse.Namespace, context: WorkContext) -> OperationResult[ScopeEditData]:
    views = load_scope_views(context.repo_root / "spec-dock")
    selection = show_active_selection(repo_root=context.repo_root, worktree_id=context.worktree_id)
    selected = show_scope(views, ns.target, selection=selection)
    title = ns.title.strip()
    if not title:
        raise ValueError("Scope title must not be empty")
    if ns.dry_run:
        changed = selected.title != title
        revision = selected.revision + int(changed)
    else:
        outcome = edit_scope_title(
            repo_root=context.repo_root,
            common_dir=context.common_dir,
            worktree_id=context.worktree_id,
            engine_digest=context.engine_digest,
            expected_epoch=context.expected_epoch,
            target_id=selected.id,
            title=title,
            lock_timeout=ns.lock_timeout,
        )
        changed = outcome.changed
        revision = outcome.revision
    projection = (
        project_scope_view(context, selected, snapshot_id=list_scopes(views).snapshot_id, requested=ns.target)
        if ns.dry_run
        else project_scope(context, selected.id, requested=ns.target)
    )
    return OperationResult(
        command="scope edit",
        status="planned" if ns.dry_run else "succeeded" if changed else "unchanged",
        data=ScopeEditData(
            selected.id,
            title,
            revision,
            changed,
            projection.scope,
            projection.status,
            projection.project,
            projection.worktree,
            projection.snapshot_id,
        ),
        exit_code=0,
        target=projection.target,
        effects=(Effect("metadata", "planned" if ns.dry_run else "succeeded", selected.id),) if changed else (),
    )
