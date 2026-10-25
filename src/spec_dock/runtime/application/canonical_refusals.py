"""Canonical-mode answers for commands that do not apply to a schema-4 workspace."""

from __future__ import annotations

from typing import TYPE_CHECKING

from spec_dock.runtime.application.canonical_errors import (
    CANONICAL_NOT_APPLICABLE,
    MIGRATE_NOT_APPLICABLE_RECOVERY,
    canonical_failure,
)

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.presentation.envelope import OperationResult


def refuse_workspace_migrate(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    """Schema 4 has no writer-protocol migration; the declaration is never rewritten to schema 3."""
    return canonical_failure(
        namespace.command_path,
        CANONICAL_NOT_APPLICABLE,
        "workspace migrate switches schema-3 writer protocols; this workspace declares schema 4",
        3,
        (MIGRATE_NOT_APPLICABLE_RECOVERY,),
        {"schema_version": context.workspace.get("schema_version")},
    )
