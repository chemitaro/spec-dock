"""Canonical-mode routing tables; dispatch() consults them at its single mode branch."""

from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path

from spec_dock.runtime.application.canonical_artifact_write import create_artifact
from spec_dock.runtime.application.canonical_branches import branch_operation
from spec_dock.runtime.application.canonical_check import check_canonical_commit
from spec_dock.runtime.application.canonical_dependency_write import mutate_dependency
from spec_dock.runtime.application.canonical_hold import run_canonical_accept, run_canonical_restore
from spec_dock.runtime.application.canonical_link import run_canonical_link
from spec_dock.runtime.application.canonical_refusals import refuse_workspace_migrate
from spec_dock.runtime.application.canonical_remove import run_canonical_remove
from spec_dock.runtime.application.canonical_resume import run_canonical_resume
from spec_dock.runtime.application.canonical_scope_change import delete_scope, edit_scope, lifecycle_scope, move_scope
from spec_dock.runtime.application.canonical_scope_check import check_scope
from spec_dock.runtime.application.canonical_scope_create import create_scope, import_scope
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
from spec_dock.runtime.application.canonical_sync import run_canonical_sync, run_registered_sync
from spec_dock.runtime.application.canonical_work import finish_work, start_work
from spec_dock.runtime.application.canonical_workspace import (
    diagnose_workspace,
    sync_workspace,
    validate_workspace,
)
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

# Keyed by public leaf path: every leaf that dispatch() does not route before the mode branch (Epic G7, iss-00436).
CANONICAL_HANDLERS: dict[str, CanonicalHandler] = {
    "workspace migrate": refuse_workspace_migrate,
    "canonical link": run_canonical_link,
    "canonical status": run_canonical_status,
    "worktree create": create_worktree_and_link,
    "canonical sync": run_canonical_sync,
    "canonical accept": run_canonical_accept,
    "canonical restore": run_canonical_restore,
    "canonical resume": run_canonical_resume,
    "canonical remove": run_canonical_remove,
    "scope show": show_scope,
    "scope check": check_scope,
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
    "workspace sync": sync_workspace,
    "workspace validate": validate_workspace,
    "workspace doctor": diagnose_workspace,
    "scope create initiative": create_scope,
    "scope create epic": create_scope,
    "scope create issue": create_scope,
    "scope import github initiative": import_scope,
    "scope import github epic": import_scope,
    "scope import github issue": import_scope,
    "scope edit": edit_scope,
    "scope move": move_scope,
    "scope close": lifecycle_scope,
    "scope reopen": lifecycle_scope,
    "scope delete": delete_scope,
    "dependency add": mutate_dependency,
    "dependency remove": mutate_dependency,
    "artifact create": create_artifact,
    "artifact import file": create_artifact,
    "work start": start_work,
    "work finish": finish_work,
}

# Consulted before resolve_context: commands that work without a repository (canonical sync --registered)
# or that inspect the declaration themselves (canonical check). A handler returns None to decline.
REPOSITORY_INDEPENDENT_HANDLERS: dict[str, RepositoryIndependentHandler] = {
    "canonical check": check_canonical_commit,
    "canonical sync": run_registered_sync,
}


def dispatch_repository_independent(namespace: argparse.Namespace, cwd: Path) -> OperationResult[object] | None:
    handler = REPOSITORY_INDEPENDENT_HANDLERS.get(namespace.command_path)
    return handler(namespace, cwd) if handler is not None else None


def dispatch_canonical(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    return CANONICAL_HANDLERS[namespace.command_path](namespace, context)
