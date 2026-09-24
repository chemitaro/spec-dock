"""Thin vNext adapter for derived workspace synchronization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from spec_dock_runtime.application.workspace_sync_vnext import preview_sync_workspace, sync_workspace
from spec_dock_runtime.presentation.envelope import Diagnostic, Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock_runtime.commands.work_vnext import WorkContext


@dataclass(frozen=True)
class WorkspaceSyncData:
    generation_id: str | None
    node_count: int
    source: str
    valid: bool
    complete: bool
    projection_stale: bool
    remote_count: int | None
    findings: tuple[str, ...]


def run_workspace_sync(
    ns: argparse.Namespace, context: WorkContext, *, gateway: Any
) -> OperationResult[WorkspaceSyncData]:
    if ns.dry_run:
        preview = preview_sync_workspace(
            repo_root=context.repo_root,
            source=ns.source,
            allow_invalid=ns.allow_invalid,
            offline=ns.offline,
        )
        return OperationResult(
            command=ns.command_path,
            status="planned",
            data=WorkspaceSyncData(
                None,
                preview.node_count,
                preview.source,
                preview.valid,
                True,
                False,
                preview.remote_count,
                preview.findings,
            ),
            exit_code=0,
            effects=(Effect("generation-publish", "planned", None),),
        )
    result = sync_workspace(
        repo_root=context.repo_root,
        common_dir=context.common_dir,
        worktree_id=context.worktree_id,
        engine_digest=context.engine_digest,
        expected_epoch=context.expected_epoch,
        source=ns.source,
        allow_invalid=ns.allow_invalid,
        offline=ns.offline,
        gateway=gateway,
        lock_timeout=ns.lock_timeout,
    )
    partial = not result.complete or result.projection_stale
    return OperationResult(
        command=ns.command_path,
        status="partial" if partial else "succeeded",
        data=WorkspaceSyncData(
            result.generation.id,
            result.node_count,
            result.generation.source,
            result.generation.valid,
            result.complete,
            result.projection_stale,
            None,
            result.findings,
        ),
        exit_code=6 if partial else 0,
        effects=(Effect("generation-publish", "succeeded", result.generation.id),),
        error=Diagnostic("SYNC_INCOMPLETE", "workspace projection or GitHub refresh was incomplete", {})
        if partial
        else None,
    )
