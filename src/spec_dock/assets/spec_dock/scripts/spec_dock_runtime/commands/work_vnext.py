"""vNext work command adapters for all three Scope kinds."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from spec_dock_runtime.application.work_lifecycle import (
    finish_work,
    preview_finish_work,
    preview_start_work,
    resume_finish_work,
    resume_start_work,
    start_work,
)
from spec_dock_runtime.presentation.envelope import Effect, OperationResult

if TYPE_CHECKING:
    import argparse
    from pathlib import Path

    from spec_dock_runtime.application.work_lifecycle import GithubIssueGateway


@dataclass(frozen=True)
class WorkContext:
    repo_root: Path
    common_dir: Path
    worktree_id: str
    engine_digest: str
    expected_epoch: int


@dataclass(frozen=True)
class WorkStartData:
    scope_id: str
    branch: str
    selection_changed: bool


@dataclass(frozen=True)
class WorkFinishData:
    scope_id: str
    lifecycle_changed: bool
    selection_changed: bool


def run_work_start(
    ns: argparse.Namespace, context: WorkContext, *, gateway: GithubIssueGateway
) -> OperationResult[WorkStartData]:
    """Run or resume the recorded branch checkout and active selection."""
    if ns.dry_run:
        if ns.resume is not None:
            raise ValueError("work start recovery cannot be previewed as a new request")
        preview = preview_start_work(
            repo_root=context.repo_root,
            common_dir=context.common_dir,
            worktree_id=context.worktree_id,
            engine_digest=context.engine_digest,
            expected_epoch=context.expected_epoch,
            target=ns.target,
            base=ns.base,
            branch_name=ns.branch,
            switch_active=ns.switch_active,
            source=ns.source,
            allow_stale=ns.allow_stale,
            offline=ns.offline,
            gateway=gateway,
        )
        return OperationResult(
            command="work start",
            status="planned",
            data=WorkStartData(preview.target_id, preview.branch, preview.selection_changed),
            exit_code=0,
            effects=(
                Effect("branch", "planned", preview.branch),
                Effect("checkout", "planned", preview.branch),
                Effect("selection", "planned", preview.target_id),
            ),
        )
    common = {
        "repo_root": context.repo_root,
        "common_dir": context.common_dir,
        "worktree_id": context.worktree_id,
        "engine_digest": context.engine_digest,
        "expected_epoch": context.expected_epoch,
        "gateway": gateway,
        "lock_timeout": ns.lock_timeout,
    }
    if ns.resume is not None:
        if ns.base is not None or ns.branch is not None or ns.switch_active or ns.allow_stale:
            raise ValueError("work start recovery cannot change the recorded request")
        outcome = resume_start_work(operation_id=ns.resume, expected_scope_id=ns.target, **common)
    else:
        outcome = start_work(
            target=ns.target,
            base=ns.base,
            branch_name=ns.branch,
            switch_active=ns.switch_active,
            source=ns.source,
            allow_stale=ns.allow_stale,
            offline=ns.offline,
            **common,
        )
    return OperationResult(
        command="work start",
        status="succeeded",
        data=WorkStartData(outcome.target_id, outcome.branch, outcome.selection_changed),
        exit_code=0,
        operation_id=outcome.operation_id,
        effects=(
            Effect("branch", "succeeded" if outcome.branch_created else "unchanged", outcome.branch),
            Effect("checkout", "succeeded", outcome.branch),
            Effect("selection", "succeeded" if outcome.selection_changed else "unchanged", outcome.target_id),
        ),
    )


def run_work_finish(
    ns: argparse.Namespace, context: WorkContext, *, gateway: GithubIssueGateway
) -> OperationResult[WorkFinishData]:
    """Finish a selected Issue, Epic, or Initiative and clear its selection chain."""
    if ns.dry_run:
        if ns.resume is not None:
            raise ValueError("work finish recovery cannot be previewed as a new request")
        preview = preview_finish_work(
            repo_root=context.repo_root,
            common_dir=context.common_dir,
            worktree_id=context.worktree_id,
            engine_digest=context.engine_digest,
            expected_epoch=context.expected_epoch,
            target=ns.target,
            gateway=gateway,
        )
        selection_changed = preview.selection_changed
        return OperationResult(
            command="work finish",
            status="planned",
            data=WorkFinishData(preview.target_id, preview.completion.changed, selection_changed),
            exit_code=0,
            effects=(
                Effect("lifecycle", "planned", preview.target_id),
                Effect("selection", "planned", preview.target_id),
            ),
        )
    if not ns.yes:
        raise ValueError("work finish requires --yes after reviewing the target and effects")
    common = {
        "repo_root": context.repo_root,
        "common_dir": context.common_dir,
        "worktree_id": context.worktree_id,
        "engine_digest": context.engine_digest,
        "expected_epoch": context.expected_epoch,
        "gateway": gateway,
        "lock_timeout": ns.lock_timeout,
    }
    if ns.resume is not None:
        outcome = resume_finish_work(operation_id=ns.resume, expected_scope_id=ns.target, **common)
    else:
        outcome = finish_work(
            target=ns.target,
            updated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            **common,
        )
    changed = outcome.completion_changed or outcome.selection_changed
    return OperationResult(
        command="work finish",
        status="succeeded" if changed else "unchanged",
        data=WorkFinishData(outcome.target_id, outcome.completion_changed, outcome.selection_changed),
        exit_code=0,
        operation_id=outcome.operation_id,
        effects=(
            Effect("lifecycle", "succeeded" if outcome.completion_changed else "unchanged", outcome.target_id),
            Effect("selection", "succeeded" if outcome.selection_changed else "unchanged", outcome.target_id),
        ),
    )
