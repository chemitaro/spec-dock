"""Pure Start decisions over a local snapshot and fixed live observations."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import TYPE_CHECKING

from spec_dock.runtime.application.start_selection import SelectionPlan, plan_selection
from spec_dock.runtime.domain.git_ref import parse_commit_oid

if TYPE_CHECKING:
    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.scope_query import ScopeView
    from spec_dock.runtime.application.start_snapshot import LocalInput
    from spec_dock.runtime.application.worktree_observation import SelectionObservation, WorktreeSelection
    from spec_dock.runtime.domain.dependency_vnext import ReadinessResult
    from spec_dock.runtime.infra.work_target_store import SelectionHandle


class StartPlanError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


@dataclass(frozen=True)
class StartRequest:
    target_id: str
    branch: str | None
    base: str | None
    switch_active: bool
    expected_current: str | None
    expected_backend: str | None


@dataclass(frozen=True)
class StartLocalSnapshot:
    target: ScopeView
    inputs: tuple[LocalInput, ...]
    selection: SelectionObservation
    inventory: tuple[WorktreeSelection, ...]


@dataclass(frozen=True)
class StartLiveObservations:
    branch: str
    resolved_tip: str
    create_branch: bool
    readiness: ReadinessResult


@dataclass(frozen=True)
class StartPlan:
    target_id: str
    github_ref: str | None
    branch: str
    resolved_tip: str
    create_branch: bool
    expected_local_hashes: tuple[tuple[str, str], ...]
    old_selection_handle: SelectionHandle | None
    switch_allowed: bool
    selection: SelectionPlan


def check_expectations(
    target: ScopeView, selection: SelectionObservation, expected_current: str | None, expected_backend: str | None
) -> None:
    if expected_backend is not None and target.backend.kind != expected_backend:
        raise StartPlanError("EXPECTATION_FAILED", "target backend does not match --expect-backend")
    current_id = selection.record.scope_id if selection.record is not None else None
    if expected_current is not None and current_id != expected_current:
        raise StartPlanError("EXPECTATION_FAILED", "direct target does not match --expect-current")


def check_inventory(context: ProjectContext, rows: tuple[WorktreeSelection, ...], target: ScopeView) -> None:
    for row in rows:
        other = row.selection.record
        if (
            row.worktree_identity != context.worktree_identity
            and other
            and (
                other.scope_id == target.id or (target.github_ref is not None and other.github_ref == target.github_ref)
            )
        ):
            raise StartPlanError("SCOPE_ALREADY_SELECTED", "Scope is already selected by another worktree")
        if row.selection.status in ("invalid", "unavailable"):
            if row.error is not None:
                raise row.error
            raise ValueError(row.selection.reason or "worktree selection is unavailable")
    if not any(row.worktree_identity == context.worktree_identity for row in rows):
        raise StartPlanError("WORKTREE_INVENTORY_CHANGED", "current worktree is missing from Git inventory")


def check_branch_occupancy(context: ProjectContext, rows: tuple[WorktreeSelection, ...], branch: str) -> None:
    if any(row.worktree_identity != context.worktree_identity and row.git.branch == branch for row in rows):
        raise StartPlanError("BRANCH_IN_USE", "requested branch is checked out by another worktree")


def plan_start(
    request: StartRequest,
    context: ProjectContext,
    local_snapshot: StartLocalSnapshot,
    live_observations: StartLiveObservations,
) -> StartPlan:
    target = local_snapshot.target
    observed = live_observations
    if request.target_id != target.id or observed.readiness.target_id != target.id:
        raise ValueError("Start observations do not belong to the requested Scope")
    if request.branch is not None and request.branch != observed.branch:
        raise StartPlanError("BRANCH_CHANGED", "observed branch differs from explicit request")
    parse_commit_oid(observed.resolved_tip.encode("ascii"))
    if observed.create_branch:
        if not request.base:
            raise ValueError("a new branch requires --base")
    elif not request.branch:
        raise ValueError(f"existing branch requires explicit --branch {observed.branch}")
    elif request.base:
        raise ValueError("existing branch reuse does not accept --base")
    if not observed.readiness.ready or observed.readiness.stale:
        blocked = ", ".join(blocker.scope_id for blocker in observed.readiness.blockers)
        raise StartPlanError("READINESS_NOT_SATISFIED", f"required Scope states are not satisfied: {blocked}")
    check_expectations(target, local_snapshot.selection, request.expected_current, request.expected_backend)
    check_inventory(context, local_snapshot.inventory, target)
    check_branch_occupancy(context, local_snapshot.inventory, observed.branch)
    selection = plan_selection(
        local_snapshot.selection,
        scope_id=target.id,
        branch=observed.branch,
        tip=observed.resolved_tip,
        current_branch=context.branch,
        current_head=context.head,
        switch_active=request.switch_active,
    )
    return StartPlan(
        target.id,
        target.github_ref,
        observed.branch,
        observed.resolved_tip,
        observed.create_branch,
        tuple((value.relative_path, hashlib.sha256(value.payload).hexdigest()) for value in local_snapshot.inputs),
        local_snapshot.selection.handle,
        request.switch_active,
        selection,
    )
