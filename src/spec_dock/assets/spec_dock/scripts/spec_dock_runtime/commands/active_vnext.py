"""Active selection command adapters with read-only previews."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_dock_runtime.application.active_selection import (
    change_active_selection,
    preview_active_change,
    show_active_selection,
)
from spec_dock_runtime.presentation.envelope import Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock_runtime.application.active_selection import SelectionState
    from spec_dock_runtime.commands.work_vnext import WorkContext


@dataclass(frozen=True)
class ActiveData:
    worktree_id: str
    revision: int
    initiative_id: str | None
    epic_id: str | None
    issue_id: str | None
    focus_id: str | None


def _data(selection: SelectionState) -> ActiveData:
    return ActiveData(
        selection.worktree_id,
        selection.revision,
        selection.initiative_id,
        selection.epic_id,
        selection.issue_id,
        selection.focus_id,
    )


def run_active_show(context: WorkContext) -> OperationResult[ActiveData]:
    selection = show_active_selection(repo_root=context.repo_root, worktree_id=context.worktree_id)
    return OperationResult(command="active show", status="succeeded", data=_data(selection), exit_code=0)


def run_active_change(ns: argparse.Namespace, context: WorkContext) -> OperationResult[ActiveData]:
    if ns.command_path == "active set":
        options = {"target": ns.target, "from_branch": ns.from_branch}
    elif ns.command_path == "active clear":
        options = {"clear_from": ns.from_target, "clear_all": ns.all}
    else:
        raise ValueError("unsupported active action")
    common = {
        "repo_root": context.repo_root,
        "common_dir": context.common_dir,
        "worktree_id": context.worktree_id,
    }
    if ns.dry_run:
        outcome = preview_active_change(**common, **options)
        status = "planned"
        effects = (Effect("selection", "planned", outcome.selection.focus_id),) if outcome.changed else ()
    else:
        outcome = change_active_selection(
            **common,
            engine_digest=context.engine_digest,
            expected_epoch=context.expected_epoch,
            lock_timeout=ns.lock_timeout,
            **options,
        )
        status = "succeeded" if outcome.changed else "unchanged"
        effects = (Effect("selection", "succeeded", outcome.selection.focus_id),) if outcome.changed else ()
    return OperationResult(
        command=ns.command_path,
        status=status,
        data=_data(outcome.selection),
        exit_code=0,
        effects=effects,
    )
