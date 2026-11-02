"""Observe and change Git branches without persistent Scope bindings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_dock.runtime.application.project_context import physical_identity, resolve_context
from spec_dock.runtime.infra.git_cli import worktree_list
from spec_dock.runtime.infra.git_process import run_git
from spec_dock.runtime.infra.work_target_store import StoredSelection, WorkTargetStore

if TYPE_CHECKING:
    from spec_dock.runtime.application.project_context import ProjectContext


@dataclass(frozen=True)
class BranchData:
    result: dict[str, object]
    kind: str = "branch"


def _data(scope_id: str, name: str, tip: str | None, *, created: bool, switched: bool) -> BranchData:
    return BranchData({
        "scope_id": scope_id,
        "name": name,
        "tip": tip,
        "created": created,
        "switched": switched,
        "binding_persisted": False,
    })


def _check_switch_target(context: ProjectContext, name: str, *, timeout: float) -> None:
    for entry in worktree_list(context.root, timeout=timeout):
        if entry.branch == name and physical_identity(entry.path) != context.worktree_identity:
            raise ValueError("requested branch is checked out in another worktree")
    if run_git(context.root, "status", "--porcelain", "-z", timeout=timeout):
        raise ValueError("branch switch requires a clean worktree")


def _fresh_context(context: ProjectContext, timeout: float) -> ProjectContext:
    fresh = resolve_context(str(context.root), context.root, timeout=timeout)
    if fresh.clone_identity != context.clone_identity or fresh.worktree_identity != context.worktree_identity:
        raise ValueError("Git project physical identity changed")
    return fresh


def _capture_selection(context: ProjectContext) -> StoredSelection:
    with WorkTargetStore(context.root) as store:
        captured = store.read()
    if captured.status not in ("empty", "selected"):
        raise ValueError("direct selection cannot be captured for a Git branch mutation")
    return captured


def _verify_selection(context: ProjectContext, expected: StoredSelection) -> None:
    with WorkTargetStore(context.root) as store:
        observed = store.read()
    if observed != expected:
        raise ValueError("direct selection changed during the Git branch operation")
