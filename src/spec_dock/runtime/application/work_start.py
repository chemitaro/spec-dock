"""Start alone holds clone exclusion through checkout and direct publication."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Literal

from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.infra.git_process import GitProcessError, run_git

if TYPE_CHECKING:
    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.worktree_observation import WorktreeSelection
    from spec_dock.runtime.infra.identity import DirectoryIdentity
    from spec_dock.runtime.infra.start_lock import StartLock


class StartPrecondition(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class StartGitFailure(GitProcessError):
    def __init__(
        self,
        error: GitProcessError,
        branch_after: str | None,
        effect_status: Literal["succeeded", "failed", "unknown"],
    ) -> None:
        super().__init__(
            error.argv,
            error.stderr,
            error.returncode,
            uncertain=error.uncertain,
            stdout=error.stdout,
            timed_out=error.timed_out,
        )
        self.branch_after = branch_after
        self.effect_status = effect_status


def _resolve_bound_context(
    context: ProjectContext, root_handle: DirectoryIdentity, lock: StartLock, *, timeout: float
) -> ProjectContext:
    root_handle.verify()
    lock.verify()
    fresh = resolve_context(str(context.root), context.root, timeout=timeout)
    root_handle.verify()
    lock.verify()
    if fresh.worktree_identity != root_handle.identity or fresh.clone_identity != lock.identity:
        raise StartPrecondition("PROJECT_IDENTITY_CHANGED", "fresh Git context differs from held root/common identity")
    return fresh


def _verify_inventory(
    context: ProjectContext,
    before: tuple[WorktreeSelection, ...],
    after: tuple[WorktreeSelection, ...],
    *,
    checkout: bool = False,
    cleared: bool = False,
    refresh_other: bool = False,
) -> None:
    old = {row.path: row for row in before}
    current = {row.path: row for row in after}
    if old.keys() != current.keys():
        raise StartPrecondition("WORKTREE_INVENTORY_CHANGED", "Git worktree inventory changed during Start")
    for path, row in current.items():
        expected = old[path]
        if refresh_other and row.worktree_identity != context.worktree_identity:
            row = replace(
                row,
                git=replace(
                    row.git, head=expected.git.head, branch=expected.git.branch, detached=expected.git.detached
                ),
                selection=expected.selection,
                views=expected.views,
                error=expected.error,
            )
        if checkout and row.worktree_identity == context.worktree_identity:
            if row.selection.record != expected.selection.record or row.selection.handle != expected.selection.handle:
                raise StartPrecondition("SELECTION_CHANGED", "captured direct target changed during checkout")
            row = replace(
                row,
                git=replace(
                    row.git, head=expected.git.head, branch=expected.git.branch, detached=expected.git.detached
                ),
                selection=expected.selection,
                views=expected.views,
            )
        if cleared and row.worktree_identity == context.worktree_identity:
            if row.selection.status != "empty" or row.selection.record is not None or row.selection.handle is not None:
                raise StartPrecondition("SELECTION_CHANGED", "direct target appeared after captured target removal")
            row = replace(row, selection=expected.selection, views=expected.views)
        if row != expected:
            raise StartPrecondition("WORKTREE_INVENTORY_CHANGED", "Git worktree or direct target changed during Start")


def _check_private_state(context: ProjectContext, timeout: float, proposed_token: str) -> None:
    if run_git(context.root, "ls-files", "-z", "--", "spec-dock/.agent/work-target", timeout=timeout):
        raise ValueError("work target state must not be tracked by Git")
    for basename in (f"target-{proposed_token}.json", f".stage-{proposed_token}"):
        if not run_git(
            context.root,
            "check-ignore",
            "--no-index",
            "--",
            f"spec-dock/.agent/work-target/{basename}",
            timeout=timeout,
            missing_ok=True,
        ):
            raise StartPrecondition("WORK_TARGET_PATH_NOT_IGNORED", "work target state must be ignored by Git")


@dataclass(frozen=True)
class StartData:
    scope_id: str
    started: bool
    branch_before: str | None
    branch_after: str | None
    selection_token: str | None
    kind: str = "work-start"
