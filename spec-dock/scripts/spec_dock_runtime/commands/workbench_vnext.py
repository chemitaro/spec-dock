"""Thin vNext adapter for an explicit Workbench copy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_dock_runtime.application.contracts import WorkbenchCopyError
from spec_dock_runtime.application.workbench_vnext import copy_workbench, preview_workbench_copy
from spec_dock_runtime.presentation.envelope import Diagnostic, Effect, OperationResult
from spec_dock_runtime.presentation.errors import CliMessageData

if TYPE_CHECKING:
    import argparse

    from spec_dock_runtime.commands.work_vnext import WorkContext


@dataclass(frozen=True)
class WorkbenchCopyData:
    scope_id: str
    source_worktree_id: str
    target_worktree_id: str
    target_path: str


def run_workbench_copy(ns: argparse.Namespace, context: WorkContext) -> OperationResult[object]:
    if ns.on_conflict == "overwrite" and not (ns.dry_run or ns.yes):
        raise ValueError("Workbench overwrite requires --yes")
    common = {
        "repo_root": context.repo_root,
        "common_dir": context.common_dir,
        "worktree_id": context.worktree_id,
        "scope": ns.scope,
        "to_worktree": ns.to_worktree,
        "on_conflict": ns.on_conflict,
    }
    try:
        if ns.dry_run:
            outcome = preview_workbench_copy(**common)
        else:
            outcome = copy_workbench(
                **common,
                engine_digest=context.engine_digest,
                expected_epoch=context.expected_epoch,
                lock_timeout=ns.lock_timeout,
            )
    except WorkbenchCopyError as error:
        partial = error.mutation_started
        return OperationResult(
            command=ns.command_path,
            status="partial" if partial else "failed",
            data=CliMessageData(None),
            exit_code=6 if partial else 3,
            effects=(Effect("workbench-copy", "unknown", ns.scope),) if partial else (),
            error=Diagnostic(error.code, str(error), {"side": error.side} if error.side else {}),
        )
    return OperationResult(
        command=ns.command_path,
        status="planned" if ns.dry_run else "succeeded",
        data=WorkbenchCopyData(
            outcome.scope_id,
            outcome.source_worktree_id,
            outcome.target_worktree_id,
            str(outcome.target_path),
        ),
        exit_code=0,
        effects=(Effect("workbench-copy", "planned" if ns.dry_run else "succeeded", outcome.scope_id),),
    )
