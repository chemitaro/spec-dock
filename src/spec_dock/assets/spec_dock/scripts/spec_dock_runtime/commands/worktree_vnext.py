"""Thin vNext adapters for registered worktree inventory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_dock_runtime.application.worktree_vnext import WorktreeView, list_worktrees, show_worktree
from spec_dock_runtime.presentation.envelope import OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock_runtime.commands.work_vnext import WorkContext


@dataclass(frozen=True)
class WorktreeSummary:
    id: str | None
    alias: str | None
    path: str
    head: str | None
    branch: str | None
    registered: bool
    locked: bool
    bare: bool
    detached: bool


@dataclass(frozen=True)
class WorktreeListData:
    items: tuple[WorktreeSummary, ...]


def _summary(view: WorktreeView) -> WorktreeSummary:
    return WorktreeSummary(
        view.id,
        view.alias,
        str(view.path),
        view.head,
        view.branch,
        view.registered,
        view.locked,
        view.bare,
        view.detached,
    )


def run_worktree_query(ns: argparse.Namespace, context: WorkContext) -> OperationResult[object]:
    if ns.command_path == "worktree list":
        data: object = WorktreeListData(
            tuple(_summary(item) for item in list_worktrees(repo_root=context.repo_root, common_dir=context.common_dir))
        )
    elif ns.command_path == "worktree show":
        data = _summary(
            show_worktree(repo_root=context.repo_root, common_dir=context.common_dir, reference=ns.worktree_ref)
        )
    else:
        raise ValueError("worktree query is unsupported")
    return OperationResult(command=ns.command_path, status="succeeded", data=data, exit_code=0)
