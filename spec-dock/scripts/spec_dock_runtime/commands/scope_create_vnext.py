"""Thin CLI adapter for Scope creation."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from spec_dock_runtime.application.scope_create_vnext import create_local_scope_command
from spec_dock_runtime.presentation.envelope import Diagnostic, Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock_runtime.commands.work_vnext import WorkContext


def run_scope_create(ns: argparse.Namespace, context: WorkContext) -> OperationResult[object]:
    kind = ns.command_path.rsplit(" ", 1)[-1]
    if ns.resume is not None:
        raise ValueError("Scope create recovery is not yet connected")
    if ns.backend != "local":
        raise ValueError("GitHub Scope creation is not yet connected")
    result = create_local_scope_command(
        repo_root=context.repo_root,
        common_dir=context.common_dir,
        worktree_id=context.worktree_id,
        engine_digest=context.engine_digest,
        expected_epoch=context.expected_epoch,
        kind=kind,
        title=ns.title,
        parent_target=getattr(ns, "parent", None),
        slug=ns.slug,
        updated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        dry_run=ns.dry_run,
        lock_timeout=ns.lock_timeout,
    )
    return OperationResult(
        command=ns.command_path,
        status="planned" if ns.dry_run else "succeeded",
        data=result,
        exit_code=0,
        operation_id=result.operation_id,
        effects=(Effect("scope-create", "planned" if ns.dry_run else "succeeded", result.scope_id),),
        warnings=tuple(Diagnostic("STALE_ANCESTOR", warning, {}) for warning in result.warnings),
    )
