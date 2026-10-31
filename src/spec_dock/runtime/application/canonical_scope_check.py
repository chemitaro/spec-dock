"""Canonical-mode `scope check <ID>` (iss-00473; contract K3 of epic-00425): read-only, offline-capable."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from spec_dock.runtime.application.canonical_scopes import (
    check_canonical_scope_expectations,
    load_canonical_scopes,
    resolve_canonical_scope,
)
from spec_dock.runtime.application.scope_check import check_scope_documents
from spec_dock.runtime.application.worktree_observation import read_selection
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.project_context import ProjectContext

SCOPE_CHECK_FAILED: Final = "SCOPE_CHECK_FAILED"


def check_scope(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    scopes = load_canonical_scopes(context, timeout=namespace.timeout, link=True, offline=namespace.offline)
    selection = read_selection(context, scopes.views)
    scope = resolve_canonical_scope(context, scopes, namespace.target, selection=selection)
    check_canonical_scope_expectations(
        context,
        scopes,
        selection,
        target=scope,
        expected_current=namespace.expect_current,
        expected_backend=namespace.expect_backend,
    )
    shown_path = scopes.require_directory(scope.id)
    directory = scopes.directories[scope.id].path
    shown = shown_path.relative_to(context.root).as_posix()
    report = check_scope_documents(
        directory, kind=scope.kind, shown=shown, repository_root=context.root, timeout=namespace.timeout
    )
    valid = not report.errors
    result: dict[str, object] = {
        "scope_id": scope.id,
        "kind": scope.kind,
        "path": shown,
        "format": report.format,
        "checked": report.checked,
        "valid": valid,
        "schema": report.schema,
        "assurance": report.assurance.payload(),
        "errors": report.errors,
        "warnings": report.warnings,
        "findings": report.findings,
        "cue": None if report.cue_version is None else {"version": report.cue_version},
        "cue_output": report.cue_output,
        "snapshot": scopes.snapshot_payload(),
    }
    warnings = (*scopes.warnings(), *report.warnings)
    data = FamilyData("scope-check", result)
    if valid:
        return OperationResult(namespace.command_path, "succeeded", data, 0, warnings=warnings)
    return OperationResult(
        namespace.command_path,
        "failed",
        data,
        7,
        warnings=warnings,
        error=Diagnostic(
            SCOPE_CHECK_FAILED,
            f"{scope.id} has {len(report.errors)} spec check error(s)",
            {"scope_id": scope.id, "count": len(report.errors)},
        ),
        recovery=RecoveryInstructions((
            f"Fix the errors shown (each names its file and a hint), then run spec-dock scope check {scope.id} again.",
        )),
    )
