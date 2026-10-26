"""Canonical-mode routing tables; dispatch() consults them at its single mode branch."""

from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path

from spec_dock.runtime.application.canonical_branches import branch_operation
from spec_dock.runtime.application.canonical_check import check_canonical_commit
from spec_dock.runtime.application.canonical_errors import canonical_not_implemented
from spec_dock.runtime.application.canonical_link import run_canonical_link
from spec_dock.runtime.application.canonical_refusals import refuse_workspace_migrate
from spec_dock.runtime.application.canonical_scope_read import (
    clear_active,
    list_scope,
    query_artifact,
    query_dependencies,
    set_active,
    show_active,
    show_scope,
)
from spec_dock.runtime.application.canonical_status import run_canonical_status
from spec_dock.runtime.application.canonical_worktrees import (
    bootstrap_worktree,
    create_worktree_and_link,
    list_worktrees,
    refuse_workbench_copy,
    remove_worktree,
    show_worktree,
)
from spec_dock.runtime.application.project_context import ProjectContext
from spec_dock.runtime.presentation.envelope import OperationResult

CanonicalHandler = Callable[[argparse.Namespace, ProjectContext], OperationResult[object]]
RepositoryIndependentHandler = Callable[[argparse.Namespace, Path], OperationResult[object] | None]

# Keyed by public leaf path. Later Issues add one entry per command they implement in canonical mode.
CANONICAL_HANDLERS: dict[str, CanonicalHandler] = {
    "workspace migrate": refuse_workspace_migrate,
    "canonical link": run_canonical_link,
    "canonical status": run_canonical_status,
    "worktree create": create_worktree_and_link,
    "scope show": show_scope,
    "scope list": list_scope,
    "dependency list": query_dependencies,
    "dependency check": query_dependencies,
    "active show": show_active,
    "active set": set_active,
    "active clear": clear_active,
    "artifact list": query_artifact,
    "artifact show": query_artifact,
    "branch show": branch_operation,
    "branch create": branch_operation,
    "branch switch": branch_operation,
    "worktree list": list_worktrees,
    "worktree show": show_worktree,
    "worktree remove": remove_worktree,
    "worktree bootstrap": bootstrap_worktree,
    "workbench copy": refuse_workbench_copy,
}

# Consulted before resolve_context: commands that work without a repository (canonical sync --registered)
# or that inspect the declaration themselves (canonical check). A handler returns None to decline.
REPOSITORY_INDEPENDENT_HANDLERS: dict[str, RepositoryIndependentHandler] = {
    "canonical check": check_canonical_commit,
}


def dispatch_repository_independent(namespace: argparse.Namespace, cwd: Path) -> OperationResult[object] | None:
    handler = REPOSITORY_INDEPENDENT_HANDLERS.get(namespace.command_path)
    return handler(namespace, cwd) if handler is not None else None


def dispatch_canonical(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    handler = CANONICAL_HANDLERS.get(namespace.command_path)
    if handler is None:
        return canonical_not_implemented(namespace.command_path)
    return handler(namespace, context)
