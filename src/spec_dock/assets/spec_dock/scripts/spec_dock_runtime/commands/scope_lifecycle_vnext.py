"""Thin vNext adapters for explicit Scope close and reopen."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from spec_dock_runtime.application.active_selection import show_active_selection
from spec_dock_runtime.application.scope_completion import (
    change_scope_lifecycle,
    preview_scope_lifecycle,
    resume_scope_lifecycle,
)
from spec_dock_runtime.application.scope_query import load_scope_views, show_scope
from spec_dock_runtime.commands.scope_result_vnext import ScopeData, ScopeStatusData, project_scope
from spec_dock_runtime.presentation.envelope import Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock_runtime.application.scope_completion import GithubIssueGateway
    from spec_dock_runtime.commands.work_vnext import WorkContext


@dataclass(frozen=True)
class ScopeLifecycleData:
    target_id: str
    before: object
    after: str
    changed: bool
    descendants: tuple[str, ...]
    scope: ScopeData
    status: ScopeStatusData
    project: str
    worktree: str
    snapshot_id: str


def run_scope_lifecycle(
    ns: argparse.Namespace, context: WorkContext, *, gateway: GithubIssueGateway
) -> OperationResult[object]:
    if not ns.dry_run and not ns.yes:
        raise ValueError("Scope close/reopen requires --yes after reviewing the target and effects")
    action = "close" if ns.command_path == "scope close" else "reopen"
    reason = ns.reason if action == "close" else "completed"
    if ns.resume is not None:
        if ns.dry_run or ns.offline:
            raise ValueError("Scope lifecycle recovery cannot change or preview the recorded request")
        target_id = ns.target
    else:
        views = load_scope_views(context.repo_root / "spec-dock")
        selection = show_active_selection(repo_root=context.repo_root, worktree_id=context.worktree_id)
        target = show_scope(views, ns.target, selection=selection)
        if ns.offline and target.backend.kind == "github":
            raise ValueError("offline mode cannot observe GitHub lifecycle")
        target_id = target.id
    common = {
        "repo_root": context.repo_root,
        "common_dir": context.common_dir,
        "worktree_id": context.worktree_id,
        "engine_digest": context.engine_digest,
        "expected_epoch": context.expected_epoch,
    }
    if ns.resume is not None:
        outcome = resume_scope_lifecycle(
            **common,
            operation_id=ns.resume,
            expected_scope_id=target_id,
            expected_action=action,
            expected_reason=reason if action == "close" else None,
            gateway=gateway,
            lock_timeout=ns.lock_timeout,
        )
        decision = outcome.decision
        operation_id = outcome.operation_id
        changed = outcome.changed
    elif ns.dry_run:
        decision = preview_scope_lifecycle(**common, target_id=target_id, action=action, reason=reason, gateway=gateway)
        operation_id = None
        changed = decision.changed
    else:
        outcome = change_scope_lifecycle(
            **common,
            target_id=target_id,
            action=action,
            reason=reason,
            updated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            gateway=gateway,
            lock_timeout=ns.lock_timeout,
        )
        decision = outcome.decision
        operation_id = outcome.operation_id
        changed = outcome.changed
    projection = project_scope(context, target_id, requested=ns.target)
    status = projection.status
    if changed and not ns.dry_run and projection.scope.backend == "github":
        status = ScopeStatusData(decision.after, "github", False)
    return OperationResult(
        command=ns.command_path,
        status="planned" if ns.dry_run else "succeeded" if changed else "unchanged",
        data=ScopeLifecycleData(
            decision.target_id,
            decision.before,
            decision.after,
            decision.changed,
            decision.descendants,
            projection.scope,
            status,
            projection.project,
            projection.worktree,
            projection.snapshot_id,
        ),
        exit_code=0,
        operation_id=operation_id,
        target=projection.target,
        effects=(Effect("lifecycle", "planned" if ns.dry_run else "succeeded", target_id),) if changed else (),
    )
