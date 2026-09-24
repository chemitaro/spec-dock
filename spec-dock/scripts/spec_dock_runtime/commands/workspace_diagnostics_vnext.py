"""Thin vNext adapters for read-only workspace diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_dock_runtime.application.workspace_diagnostics_vnext import (
    WorkspaceDiagnostics,
    doctor_workspace,
    validate_workspace,
)
from spec_dock_runtime.presentation.envelope import Diagnostic, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock_runtime.application.contracts import GitHubCapabilityDiagnostic
    from spec_dock_runtime.application.workspace_diagnostics_vnext import WorkspaceFinding
    from spec_dock_runtime.commands.work_vnext import WorkContext


@dataclass(frozen=True)
class WorkspaceDiagnosticsData:
    valid: bool
    node_count: int
    findings: tuple[WorkspaceFinding, ...]
    github: tuple[GitHubCapabilityDiagnostic, ...]


def _result(command: str, report: WorkspaceDiagnostics) -> OperationResult[WorkspaceDiagnosticsData]:
    return OperationResult(
        command=command,
        status="succeeded" if report.valid else "failed",
        data=WorkspaceDiagnosticsData(report.valid, report.node_count, report.findings, report.github),
        exit_code=report.exit_code,
        error=None if report.valid else Diagnostic("WORKSPACE_INVALID", "workspace diagnostics reported errors", {}),
    )


def run_workspace_diagnostics(
    ns: argparse.Namespace, context: WorkContext
) -> OperationResult[WorkspaceDiagnosticsData]:
    common = {
        "repo_root": context.repo_root,
        "common_dir": context.common_dir,
        "worktree_id": context.worktree_id,
        "engine_digest": context.engine_digest,
    }
    if ns.command_path == "workspace validate":
        report = validate_workspace(**common, require_nodes=ns.require_nodes)
    elif ns.command_path == "workspace doctor":
        try:
            github_pr = int(ns.github_pr) if ns.github_pr is not None else None
        except ValueError as error:
            raise ValueError("GitHub PR number must be an integer") from error
        report = doctor_workspace(
            **common,
            github_repo=ns.github_repo,
            github_pr=github_pr,
            github_head_sha=ns.github_head_sha,
            github_extended=ns.github_extended,
        )
    else:
        raise ValueError("workspace diagnostics command is unsupported")
    return _result(ns.command_path, report)
