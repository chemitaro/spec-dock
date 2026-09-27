"""Thin vNext adapters for Artifact catalog queries."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal, cast

from spec_dock_runtime.application.active_selection import show_active_selection
from spec_dock_runtime.application.artifact_query import list_artifacts, show_artifact
from spec_dock_runtime.application.artifact_vnext import (
    create_scope_artifact,
    import_scope_file,
    preview_import_scope_file,
    preview_scope_artifact,
)
from spec_dock_runtime.presentation.envelope import Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock_runtime.commands.work_vnext import WorkContext


def run_artifact_query(ns: argparse.Namespace, context: WorkContext) -> OperationResult[object]:
    selection = show_active_selection(repo_root=context.repo_root, worktree_id=context.worktree_id)
    if ns.command_path == "artifact list":
        data: object = list_artifacts(repo_root=context.repo_root, scope=ns.scope, selection=selection)
    elif ns.command_path == "artifact show":
        data = show_artifact(
            repo_root=context.repo_root,
            scope=ns.scope,
            artifact_id=ns.artifact_id,
            selection=selection,
        )
    else:
        raise ValueError("artifact query is unsupported")
    return OperationResult(command=ns.command_path, status="succeeded", data=data, exit_code=0)


def run_artifact_change(
    ns: argparse.Namespace, context: WorkContext, *, invocation_cwd: Path
) -> OperationResult[object]:
    if ns.command_path == "artifact create":
        artifact_type = cast("Literal['blank', 'research', 'interview', 'disc', 'decision-candidate', 'adr']", ns.type)
        if ns.dry_run:
            preview = preview_scope_artifact(
                repo_root=context.repo_root,
                worktree_id=context.worktree_id,
                scope=ns.scope,
                artifact_type=artifact_type,
                title=ns.title,
            )
            return OperationResult(
                command=ns.command_path,
                status="planned",
                data=preview,
                exit_code=0,
                effects=(Effect("artifact-create", "planned", preview.scope_id),),
            )
        entry = create_scope_artifact(
            repo_root=context.repo_root,
            common_dir=context.common_dir,
            worktree_id=context.worktree_id,
            engine_digest=context.engine_digest,
            expected_epoch=context.expected_epoch,
            scope=ns.scope,
            artifact_type=artifact_type,
            title=ns.title,
            slug=ns.slug,
            lock_timeout=ns.lock_timeout,
        )
        effect_kind = "artifact-create"
    elif ns.command_path == "artifact import file":
        if ns.path is None:
            raise ValueError("Artifact import requires a source file")
        source_path = Path(ns.path).expanduser()
        if not source_path.is_absolute():
            source_path = invocation_cwd / source_path
        if ns.dry_run:
            preview = preview_import_scope_file(
                repo_root=context.repo_root,
                worktree_id=context.worktree_id,
                scope=ns.scope,
                source_path=source_path,
            )
            return OperationResult(
                command=ns.command_path,
                status="planned",
                data=preview,
                exit_code=0,
                effects=(Effect("artifact-import", "planned", preview.scope_id),),
            )
        entry = import_scope_file(
            repo_root=context.repo_root,
            common_dir=context.common_dir,
            worktree_id=context.worktree_id,
            engine_digest=context.engine_digest,
            expected_epoch=context.expected_epoch,
            scope=ns.scope,
            source_path=source_path,
            lock_timeout=ns.lock_timeout,
        )
        effect_kind = "artifact-import"
    else:
        raise ValueError("artifact change is unsupported")
    return OperationResult(
        command=ns.command_path,
        status="succeeded",
        data=entry,
        exit_code=0,
        effects=(Effect(effect_kind, "succeeded", entry.artifact_id),),
    )
