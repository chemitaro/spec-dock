"""Canonical-mode Scope, dependency, selection and Artifact reads (iss-00431; Epic design ch. 6)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from spec_dock.runtime.application.canonical_scopes import load_canonical_scopes
from spec_dock.runtime.application.scope_expectations import check_scope_expectations
from spec_dock.runtime.application.scope_query import list_scopes
from spec_dock.runtime.application.worktree_observation import read_selection, resolve_scope
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.project_context import ProjectContext


def show_scope(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    scopes = load_canonical_scopes(context, timeout=namespace.timeout, link=True, offline=namespace.offline)
    selection = read_selection(context, scopes.views)
    scope = resolve_scope(context, scopes.views, namespace.target, selection=selection)
    check_scope_expectations(
        context,
        scopes.views,
        selection,
        target=scope,
        expected_current=namespace.expect_current,
        expected_backend=namespace.expect_backend,
    )
    result = {
        "scope": scopes.payload(scope),
        "github_ref": scope.github_ref,
        "changed": False,
        "snapshot": scopes.snapshot_payload(),
    }
    return OperationResult(
        namespace.command_path, "succeeded", FamilyData("scope", result), 0, warnings=scopes.warnings()
    )


def list_scope(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    scopes = load_canonical_scopes(context, timeout=namespace.timeout, link=True, offline=namespace.offline)
    selection = read_selection(context, scopes.views)
    check_scope_expectations(
        context,
        scopes.views,
        selection,
        target=None,
        expected_current=namespace.expect_current,
        expected_backend=namespace.expect_backend,
    )
    parent = (
        resolve_scope(context, scopes.views, namespace.parent, selection=selection).id if namespace.parent else None
    )
    listed = list_scopes(scopes.views, kind=namespace.kind, parent_id=parent, state=namespace.state)
    result = {
        "items": [scopes.payload(scope) for scope in listed.items],
        "unknown_filtered_count": 0,
        "snapshot": scopes.snapshot_payload(),
    }
    return OperationResult(
        namespace.command_path, "succeeded", FamilyData("scope-list", result), 0, warnings=scopes.warnings()
    )
