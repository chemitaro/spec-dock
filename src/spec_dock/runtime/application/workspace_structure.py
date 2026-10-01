"""Read-only structural checks shared by Doctor and validation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from spec_dock.runtime.application.artifact_query import list_artifacts
from spec_dock.runtime.application.dependency_snapshot import read_raw_edges
from spec_dock.runtime.application.scope_query import load_scope_views
from spec_dock.runtime.application.worktree_observation import ancestors_for
from spec_dock.runtime.presentation.envelope import Diagnostic

if TYPE_CHECKING:
    from pathlib import Path

    from spec_dock.runtime.application.scope_query import ScopeView


def inspect_structure(root: Path) -> tuple[tuple[ScopeView, ...], tuple[Diagnostic, ...]]:
    try:
        views = load_scope_views(root / "spec-dock")
    except (OSError, ValueError, RuntimeError):
        return (), (Diagnostic("SCOPE_METADATA_UNREADABLE", "Scope metadata cannot be read safely", {}),)
    findings: list[Diagnostic] = []
    for view in views:
        try:
            ancestors_for(views, view)
        except ValueError:
            findings.append(
                Diagnostic("SCOPE_PARENT_INVALID", "Scope ancestor chain is missing or invalid", {"scope_id": view.id})
            )
    try:
        read_raw_edges(views)
    except (OSError, ValueError, RuntimeError):
        findings.append(Diagnostic("DEPENDENCY_INVALID", "Scope dependency graph cannot be verified", {}))
    for scope in ("@root", *(view.id for view in views)):
        try:
            list_artifacts(repo_root=root, scope=scope)
        except (OSError, ValueError, RuntimeError):
            findings.append(
                Diagnostic("ARTIFACT_INVALID", "Artifact catalog cannot be read safely", {"scope_id": scope})
            )
    return views, tuple(findings)
