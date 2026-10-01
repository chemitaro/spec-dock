"""Validate working metadata or a fixed HEAD without installation or execution state."""

from __future__ import annotations

from typing import TYPE_CHECKING

from spec_dock.runtime.application.project_context import read_workspace_declaration
from spec_dock.runtime.application.scope_expectations import check_scope_expectations
from spec_dock.runtime.application.workspace_structure import inspect_structure
from spec_dock.runtime.application.worktree_observation import read_selection
from spec_dock.runtime.infra.committed_validation import CommittedStructureInvalid, committed_validation
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.project_context import GitContext, ProjectContext


def validate_workspace(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    views, findings = inspect_structure(context.root)
    if findings and namespace.expect_current:
        raise ValueError("--expect-current cannot be verified from invalid workspace structure")
    check_scope_expectations(
        context,
        views,
        read_selection(context, views) if namespace.expect_current else None,
        target=None,
        expected_current=namespace.expect_current,
        expected_backend=namespace.expect_backend,
    )
    return _result(namespace, findings, len(views), "working-tree", None)


def validate_committed_workspace(namespace: argparse.Namespace, context: GitContext) -> OperationResult[object]:
    if namespace.expect_current is not None or namespace.expect_backend is not None:
        raise ValueError("--ci cannot verify live --expect-current or --expect-backend state")
    if context.head is None:
        raise ValueError("--ci requires an existing HEAD commit")
    findings: tuple[Diagnostic, ...]
    node_count = 0
    try:
        with committed_validation(context.root, context.head, timeout=namespace.timeout) as snapshot:
            try:
                read_workspace_declaration(snapshot / "spec-dock/workspace.json")
            except ValueError:
                findings = (
                    Diagnostic("WORKSPACE_DECLARATION_INVALID", "committed workspace declaration is invalid", {}),
                )
            else:
                views, findings = inspect_structure(snapshot)
                node_count = len(views)
    except CommittedStructureInvalid:
        findings = (
            Diagnostic("COMMITTED_STRUCTURE_INVALID", "committed structural entries cannot be read safely", {}),
        )
    return _result(namespace, findings, node_count, "HEAD", context.head)


def _result(
    namespace: argparse.Namespace,
    findings: tuple[Diagnostic, ...],
    node_count: int,
    source: str,
    oid: str | None,
) -> OperationResult[object]:
    if namespace.require_nodes and not node_count:
        findings += (Diagnostic("NODES_REQUIRED", "at least one safely validated Scope is required", {}),)
    valid = not findings
    return OperationResult(
        namespace.command_path,
        "succeeded" if valid else "failed",
        FamilyData(
            "validation",
            {
                "valid": valid,
                "findings": findings,
                "snapshot_source": source,
                "snapshot_oid": oid,
                "node_count": node_count,
            },
        ),
        0 if valid else 7,
        error=None
        if valid
        else Diagnostic("WORKSPACE_VALIDATION_FAILED", "workspace structure is invalid or incomplete", {}),
    )
