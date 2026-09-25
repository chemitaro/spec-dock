"""Thin vNext adapters for registered worktree inventory."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from spec_dock_runtime.application.worktree_bootstrap_vnext import bootstrap_worktree
from spec_dock_runtime.application.worktree_vnext import (
    WorktreeView,
    create_worktree,
    list_worktrees,
    preview_create_worktree,
    preview_remove_worktree,
    remove_worktree,
    show_worktree,
)
from spec_dock_runtime.presentation.envelope import Diagnostic, Effect, OperationResult

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


@dataclass(frozen=True)
class WorktreeCreatedData:
    id: str
    alias: str | None
    path: str
    branch: str
    commit: str
    control_epoch: int


@dataclass(frozen=True)
class WorktreeRemovedData:
    id: str
    path: str
    branch_deleted: bool
    control_epoch: int


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


def run_worktree_change(ns: argparse.Namespace, context: WorkContext) -> OperationResult[object]:
    if ns.command_path == "worktree create":
        root = Path(ns.root).expanduser() if ns.root is not None else None
        if ns.dry_run:
            preview = preview_create_worktree(
                repo_root=context.repo_root,
                common_dir=context.common_dir,
                base=ns.base,
                name=ns.name,
                root=root,
            )
            return OperationResult(
                command=ns.command_path,
                status="planned",
                data=preview,
                exit_code=0,
                effects=(Effect("worktree-create", "planned", preview.id),),
            )
        created = create_worktree(
            repo_root=context.repo_root,
            common_dir=context.common_dir,
            worktree_id=context.worktree_id,
            engine_digest=context.engine_digest,
            expected_epoch=context.expected_epoch,
            base=ns.base,
            name=ns.name,
            root=root,
            recover=ns.recover,
            lock_timeout=ns.lock_timeout,
        )
        return OperationResult(
            command=ns.command_path,
            status="succeeded",
            data=WorktreeCreatedData(
                created.id, created.alias, str(created.path), created.branch, created.commit, created.control_epoch
            ),
            exit_code=0,
            effects=(Effect("worktree-create", "succeeded", created.id),),
        )
    if ns.command_path == "worktree remove":
        if ns.dry_run:
            preview = preview_remove_worktree(
                repo_root=context.repo_root,
                common_dir=context.common_dir,
                reference=ns.worktree_ref,
                unlock=ns.unlock,
                discard_ignored=ns.discard_ignored,
            )
            return OperationResult(
                command=ns.command_path,
                status="planned",
                data=preview,
                exit_code=0,
                effects=(Effect("worktree-remove", "planned", preview.id),),
            )
        if not ns.yes:
            raise ValueError("worktree removal requires --yes")
        removed = remove_worktree(
            repo_root=context.repo_root,
            common_dir=context.common_dir,
            worktree_id=context.worktree_id,
            engine_digest=context.engine_digest,
            expected_epoch=context.expected_epoch,
            reference=ns.worktree_ref,
            unlock=ns.unlock,
            discard_ignored=ns.discard_ignored,
            lock_timeout=ns.lock_timeout,
        )
        return OperationResult(
            command=ns.command_path,
            status="succeeded",
            data=WorktreeRemovedData(removed.id, str(removed.path), removed.branch_deleted, removed.control_epoch),
            exit_code=0,
            effects=(Effect("worktree-remove", "succeeded", removed.id),),
        )
    if ns.command_path == "worktree bootstrap":
        if not ns.dry_run and not ns.yes:
            raise ValueError("worktree bootstrap requires --yes")
        outcome = bootstrap_worktree(
            repo_root=context.repo_root,
            common_dir=context.common_dir,
            worktree_id=context.worktree_id,
            engine_digest=context.engine_digest,
            expected_epoch=context.expected_epoch,
            reference=ns.worktree_ref,
            dry_run=ns.dry_run,
            offline=ns.offline,
            timeout=ns.timeout,
            lock_timeout=ns.lock_timeout,
        )
        if outcome.status == "planned":
            return OperationResult(
                command=ns.command_path,
                status="planned",
                data=outcome,
                exit_code=0,
                effects=(Effect("worktree-bootstrap", "planned", outcome.id),),
            )
        if outcome.status == "succeeded":
            return OperationResult(
                command=ns.command_path,
                status="succeeded",
                data=outcome,
                exit_code=0,
                effects=(Effect("worktree-bootstrap", "succeeded", outcome.id),),
            )
        partial = outcome.started
        return OperationResult(
            command=ns.command_path,
            status="partial" if partial else "failed",
            data=outcome,
            exit_code=6 if partial else 5,
            effects=(Effect("worktree-bootstrap", "unknown", outcome.id),) if partial else (),
            error=Diagnostic(
                "BOOTSTRAP_PARTIAL" if partial else "BOOTSTRAP_FAILED",
                outcome.diagnostic or "worktree bootstrap did not complete",
                {},
            ),
        )
    raise ValueError("worktree change is unsupported")
