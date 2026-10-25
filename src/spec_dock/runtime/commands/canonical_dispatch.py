"""Canonical-mode routing tables; dispatch() consults them at its single mode branch."""

from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path

from spec_dock.runtime.application.canonical_errors import canonical_not_implemented
from spec_dock.runtime.application.canonical_link import run_canonical_link
from spec_dock.runtime.application.canonical_refusals import refuse_workspace_migrate
from spec_dock.runtime.application.canonical_status import run_canonical_status
from spec_dock.runtime.application.canonical_worktrees import create_worktree_and_link
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
}

# Consulted before resolve_context: commands that work without a repository (canonical sync --registered)
# or that inspect the declaration themselves (canonical check). A handler returns None to decline.
REPOSITORY_INDEPENDENT_HANDLERS: dict[str, RepositoryIndependentHandler] = {}


def dispatch_repository_independent(namespace: argparse.Namespace, cwd: Path) -> OperationResult[object] | None:
    handler = REPOSITORY_INDEPENDENT_HANDLERS.get(namespace.command_path)
    return handler(namespace, cwd) if handler is not None else None


def dispatch_canonical(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    handler = CANONICAL_HANDLERS.get(namespace.command_path)
    if handler is None:
        return canonical_not_implemented(namespace.command_path)
    return handler(namespace, context)
