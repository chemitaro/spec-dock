"""Canonical-mode `scope render <ID>` (iss-00476; contract K5 of epic-00425): one CUE Scope as HTML, read-only."""

from __future__ import annotations

from typing import TYPE_CHECKING

from spec_dock.runtime.application.canonical_scopes import (
    check_canonical_scope_expectations,
    load_canonical_scopes,
    resolve_canonical_scope,
)
from spec_dock.runtime.application.scope_render import (
    DESIGN_SYSTEM_MISSING,
    SCOPE_RENDER_INCOMPLETE,
    ScopeRenderSource,
    render_scope,
)
from spec_dock.runtime.application.worktree_observation import read_selection
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.project_context import ProjectContext


def render_scope_command(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
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
    shown = shown_path.relative_to(context.root).as_posix()
    design_system = context.root / "spec-dock" / "design-system"
    design_system_base = design_system.resolve().as_uri() + "/"
    rendered = render_scope(
        ScopeRenderSource(
            scope_id=scope.id,
            kind=scope.kind,
            title=scope.title,
            directory=scopes.directories[scope.id].path,
            repository_root=context.root,
            shown=shown,
        ),
        design_system_base=design_system_base,
        vendor_base=None,
        timeout=namespace.timeout,
    )
    warnings: list[Diagnostic] = list(scopes.warnings())
    if not rendered.complete:
        warnings.append(
            Diagnostic(
                SCOPE_RENDER_INCOMPLETE,
                f"{scope.id} cannot be evaluated; the page shows only its check results."
                f" Fix the errors, then run spec-dock scope check {scope.id}",
                {"scope_id": scope.id, "next_step": f"Fix the errors, then run spec-dock scope check {scope.id}."},
            )
        )
    if not (design_system / "ds.js").is_file():
        warnings.append(
            Diagnostic(
                DESIGN_SYSTEM_MISSING,
                "this checkout has no spec-dock/design-system/ds.js; the page cannot be drawn in a browser."
                " Run spec-dock installation update in this checkout",
                {"path": "spec-dock/design-system", "next_step": "Run spec-dock installation update in this checkout."},
            )
        )
    result: dict[str, object] = {
        "scope_id": scope.id,
        "kind": scope.kind,
        "path": shown,
        "format": rendered.report.format,
        "complete": rendered.complete,
        "valid": not [error for error in rendered.report.errors if not error.code.startswith("EXPLANATION_")],
        "errors": rendered.errors,
        "design_system_base": design_system_base,
        "vendor_base": None,
        "html": rendered.html,
        "snapshot": scopes.snapshot_payload(),
    }
    return OperationResult(
        namespace.command_path, "succeeded", FamilyData("scope-render", result), 0, warnings=tuple(warnings)
    )
