"""Thin vNext adapters for Artifact catalog queries."""

from __future__ import annotations

from typing import TYPE_CHECKING

from spec_dock_runtime.application.active_selection import show_active_selection
from spec_dock_runtime.application.artifact_query import list_artifacts, show_artifact
from spec_dock_runtime.presentation.envelope import OperationResult

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
