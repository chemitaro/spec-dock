"""On-demand direct selection and same-clone Git worktree observations."""

from __future__ import annotations

from dataclasses import dataclass
import stat
from typing import TYPE_CHECKING, Literal

from spec_dock.runtime.application.project_context import OLD_WRITER_PROTOCOL, resolve_context
from spec_dock.runtime.application.scope_query import show_scope
from spec_dock.runtime.domain.selectors import ActiveScopeSelector, parse_scope_selector
from spec_dock.runtime.infra.git_cli import worktree_list
from spec_dock.runtime.infra.work_target_store import WorkTargetStore

if TYPE_CHECKING:
    from spec_dock.runtime.application.contracts import GitWorktreeRecord
    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.scope_query import ScopeView
    from spec_dock.runtime.domain.work_target import PhysicalIdentity, WorkTarget
    from spec_dock.runtime.infra.work_target_store import SelectionHandle, StoredSelection


@dataclass(frozen=True)
class SelectionObservation:
    status: Literal["empty", "selected", "stale", "unavailable", "invalid"]
    record: WorkTarget | None
    handle: SelectionHandle | None
    current_branch: str | None
    ancestors: tuple[str, ...] = ()
    reason: str | None = None

    def view(self) -> dict[str, object]:
        return {
            "status": self.status,
            "scope_id": self.record.scope_id if self.record else None,
            "github_ref": self.record.github_ref if self.record else None,
            "selection_token": self.handle.token if self.handle else None,
            "selected_branch": self.record.selected_branch if self.record else None,
            "current_branch": self.current_branch,
            "branch_changed": bool(self.record and self.record.selected_branch != self.current_branch),
        }


def ancestors_for(views: tuple[ScopeView, ...], target: ScopeView) -> tuple[ScopeView, ...]:
    index = {view.id: view for view in views}
    chain: list[ScopeView] = []
    current = target
    visited = {target.id}
    while current.parent_id is not None:
        parent = index.get(current.parent_id)
        expected_kind = {"issue": "epic", "epic": "initiative"}.get(current.kind)
        if parent is None or parent.id in visited or parent.kind != expected_kind:
            raise ValueError("current Scope ancestor chain is missing or invalid")
        chain.append(parent)
        visited.add(parent.id)
        current = parent
    if current.kind != "initiative":
        raise ValueError("current Scope ancestor chain has no Initiative")
    return tuple(reversed(chain))


def read_selection(context: ProjectContext, views: tuple[ScopeView, ...]) -> SelectionObservation:
    with WorkTargetStore(context.root) as store:
        observation = store.read()
    if observation.status == "empty" and context.workspace.get("writer_protocol") == OLD_WRITER_PROTOCOL:
        try:
            value = (context.root / "spec-dock/.agent/active.json").lstat()
        except FileNotFoundError:
            pass
        except OSError as error:
            return SelectionObservation("unavailable", None, None, context.branch, reason=str(error))
        else:
            reason = (
                "legacy selection requires explicit migration"
                if stat.S_ISREG(value.st_mode)
                else "legacy selection path is redirected"
            )
            return SelectionObservation("unavailable", None, None, context.branch, reason=reason)
    record = observation.record
    if observation.status != "selected" or record is None:
        return SelectionObservation(
            observation.status, record, observation.handle, context.branch, reason=observation.reason
        )
    if record.clone_identity != context.clone_identity or record.worktree_identity != context.worktree_identity:
        return SelectionObservation(
            "invalid", record, observation.handle, context.branch, reason="selection physical identity mismatch"
        )
    matches = [view for view in views if view.id == record.scope_id]
    if len(matches) != 1 or matches[0].github_ref != record.github_ref:
        return SelectionObservation(
            "stale", record, observation.handle, context.branch, reason="selected Scope or linkage changed"
        )
    try:
        ancestors = ancestors_for(views, matches[0])
    except ValueError as error:
        return SelectionObservation("stale", record, observation.handle, context.branch, reason=str(error))
    return SelectionObservation(
        "selected", record, observation.handle, context.branch, tuple(view.id for view in ancestors)
    )


def resolve_scope(
    context: ProjectContext, views: tuple[ScopeView, ...], target: str, *, selection: SelectionObservation | None = None
) -> ScopeView:
    selector = parse_scope_selector(target)
    if not isinstance(selector, ActiveScopeSelector):
        return show_scope(views, target)
    selection = read_selection(context, views) if selection is None else selection
    if selection.status == "empty":
        raise LookupError("active selection is empty")
    if selection.status != "selected" or selection.record is None:
        raise ValueError(selection.reason or "active selection is not valid")
    direct = show_scope(views, selection.record.scope_id)
    if selector.role == "current":
        return direct
    for view in (*ancestors_for(views, direct), direct):
        if view.kind == selector.role:
            return view
    raise LookupError("active selection does not have the requested role")


@dataclass(frozen=True)
class WorktreeSelection:
    path: str
    selection: SelectionObservation
    views: tuple[ScopeView, ...]
    worktree_identity: PhysicalIdentity | None
    git: GitWorktreeRecord
    error: OSError | ValueError | RuntimeError | None = None


def observe_worktrees(context: ProjectContext, *, timeout: float = 30) -> tuple[WorktreeSelection, ...]:
    from spec_dock.runtime.application.scope_query import load_scope_views

    seen: set[object] = set()
    rows: list[WorktreeSelection] = []
    for entry in worktree_list(context.root, timeout=timeout):
        direct: StoredSelection | None = None
        identity: PhysicalIdentity | None = None
        try:
            if entry.bare:
                raise ValueError("bare repository is not a working tree")
            other = resolve_context(str(entry.path), context.root, timeout=timeout)
            identity = other.worktree_identity
            if other.clone_identity != context.clone_identity:
                raise ValueError("worktree common directory identity mismatch")
            if other.worktree_identity in seen:
                continue
            seen.add(other.worktree_identity)
            with WorkTargetStore(other.root) as store:
                direct = store.read()
            views = (
                load_scope_views(other.root / "spec-dock", target_id=direct.record.scope_id)
                if direct.record is not None
                else ()
            )
            selection = read_selection(other, views)
            rows.append(WorktreeSelection(str(entry.path), selection, views, identity, entry))
        except (OSError, ValueError, RuntimeError) as error:
            rows.append(
                WorktreeSelection(
                    str(entry.path),
                    SelectionObservation(
                        "unavailable",
                        direct.record if direct else None,
                        direct.handle if direct else None,
                        entry.branch,
                        reason=str(error),
                    ),
                    (),
                    identity,
                    entry,
                    error,
                )
            )
    return tuple(rows)
