"""Shared public identity and status projection for Scope command results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_dock_runtime.application.scope_query import list_scopes, load_scope_views, show_scope
from spec_dock_runtime.presentation.envelope import TargetRef

if TYPE_CHECKING:
    from spec_dock_runtime.application.scope_query import ScopeView
    from spec_dock_runtime.commands.work_vnext import WorkContext


@dataclass(frozen=True)
class ScopeData:
    id: str
    kind: str
    backend: str
    parent_id: str | None
    path: str | None
    revision: int | None


@dataclass(frozen=True)
class ScopeStatusData:
    state: str
    source: str
    stale: bool


@dataclass(frozen=True)
class ScopeProjection:
    target: TargetRef
    scope: ScopeData
    status: ScopeStatusData
    project: str
    worktree: str
    snapshot_id: str
    github_ref: str | None


@dataclass(frozen=True)
class ScopeWriteData:
    scope_id: str
    path: str
    github_ref: str | None
    scope: ScopeData
    status: ScopeStatusData
    project: str
    worktree: str
    snapshot_id: str


@dataclass(frozen=True)
class ScopeFailureData:
    message: str | None
    scope: ScopeData
    status: ScopeStatusData
    project: str
    worktree: str
    snapshot_id: str


def project_scope(context: WorkContext, scope_id: str, *, requested: str | None = None) -> ScopeProjection:
    views = load_scope_views(context.repo_root / "spec-dock")
    view = show_scope(views, scope_id, selection=None)
    snapshot_id = list_scopes(views).snapshot_id
    return project_scope_view(context, view, snapshot_id=snapshot_id, requested=requested)


def project_scope_view(
    context: WorkContext, view: ScopeView, *, snapshot_id: str, requested: str | None = None
) -> ScopeProjection:
    backend = "github" if view.github_ref is not None else "local"
    try:
        path = view.path.relative_to(context.repo_root).as_posix()
    except ValueError as error:
        raise ValueError("Scope path is outside the selected repository") from error
    return ScopeProjection(
        TargetRef(requested or view.id, view.id, view.kind, backend, snapshot_id),
        ScopeData(view.id, view.kind, backend, view.parent_id, path, view.revision),
        ScopeStatusData(view.status.state, view.status.source, view.status.stale),
        str(context.repo_root),
        context.worktree_id,
        snapshot_id,
        view.github_ref,
    )
