"""Thin vNext adapter for planned Scope deletion and fixed recovery."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_dock_runtime.application.scope_delete_vnext import (
    delete_scope,
    preview_scope_delete,
    resume_scope_delete,
    rollback_scope_delete,
)
from spec_dock_runtime.presentation.envelope import Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock_runtime.commands.work_vnext import WorkContext


@dataclass(frozen=True)
class ScopeDeleteData:
    target_id: str
    deleted_ids: tuple[str, ...]
    quarantine_path: str | None


def run_scope_delete(ns: argparse.Namespace, context: WorkContext) -> OperationResult[ScopeDeleteData]:
    common = {
        "repo_root": context.repo_root,
        "common_dir": context.common_dir,
        "worktree_id": context.worktree_id,
        "engine_digest": context.engine_digest,
        "expected_epoch": context.expected_epoch,
    }
    if ns.dry_run:
        if ns.resume is not None or ns.rollback is not None:
            raise ValueError("Scope delete recovery cannot be previewed as a new request")
        plan = preview_scope_delete(
            **common,
            target=ns.target,
            recursive=ns.recursive,
            clear_active=ns.clear_active,
            detach_dependencies=ns.detach_dependencies,
        )
        return OperationResult(
            command="scope delete",
            status="planned",
            data=ScopeDeleteData(plan.target_id, plan.deleted_ids, None),
            exit_code=0,
            effects=(Effect("scope-delete", "planned", plan.target_id),),
        )
    if not ns.yes:
        raise ValueError("Scope delete requires --yes after reviewing the plan")
    if ns.resume is not None or ns.rollback is not None:
        if ns.recursive or ns.clear_active or ns.detach_dependencies:
            raise ValueError("Scope delete recovery cannot change the recorded request")
        if ns.resume is not None:
            outcome = resume_scope_delete(
                **common,
                operation_id=ns.resume,
                expected_scope_id=ns.target,
                lock_timeout=ns.lock_timeout,
            )
        else:
            outcome = rollback_scope_delete(
                **common,
                operation_id=ns.rollback,
                expected_scope_id=ns.target,
                lock_timeout=ns.lock_timeout,
            )
    else:
        outcome = delete_scope(
            **common,
            target=ns.target,
            recursive=ns.recursive,
            clear_active=ns.clear_active,
            detach_dependencies=ns.detach_dependencies,
            lock_timeout=ns.lock_timeout,
        )
    rolled_back = ns.rollback is not None
    return OperationResult(
        command="scope delete",
        status="succeeded",
        data=ScopeDeleteData(
            outcome.target_id,
            outcome.deleted_ids,
            outcome.quarantine_path.relative_to(context.repo_root).as_posix(),
        ),
        exit_code=0,
        operation_id=outcome.operation_id,
        effects=(Effect("scope-restore" if rolled_back else "scope-delete", "succeeded", outcome.target_id),),
    )
