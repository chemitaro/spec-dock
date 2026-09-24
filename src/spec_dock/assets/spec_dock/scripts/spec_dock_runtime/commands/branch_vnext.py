"""Thin vNext adapters for inspecting and switching canonical Scope branches."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_dock_runtime.application.branch_vnext import (
    preview_scope_branch_switch,
    resolve_branch_scope,
    show_scope_branch,
    switch_scope_branch,
)
from spec_dock_runtime.presentation.envelope import Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock_runtime.commands.work_vnext import WorkContext


@dataclass(frozen=True)
class BranchData:
    scope_id: str
    branch: str
    initial_sha: str


def run_branch_command(ns: argparse.Namespace, context: WorkContext) -> OperationResult[BranchData]:
    scope_id = resolve_branch_scope(context.repo_root, context.worktree_id, ns.target)
    if ns.command_path == "branch show":
        binding = show_scope_branch(context.repo_root, context.common_dir, scope_id)
        return OperationResult(
            command="branch show",
            status="succeeded",
            data=BranchData(binding.scope_id, binding.name, binding.initial_sha),
            exit_code=0,
        )
    if ns.command_path != "branch switch":
        raise ValueError("branch command is unsupported")
    common = {
        "repo_root": context.repo_root,
        "common_dir": context.common_dir,
        "worktree_id": context.worktree_id,
        "engine_digest": context.engine_digest,
        "expected_epoch": context.expected_epoch,
        "scope_id": scope_id,
    }
    if ns.dry_run:
        binding = preview_scope_branch_switch(**common)
        status = "planned"
        effect = Effect("checkout", "planned", binding.name)
    else:
        binding = switch_scope_branch(**common, lock_timeout=ns.lock_timeout)
        status = "succeeded"
        effect = Effect("checkout", "succeeded", binding.name)
    return OperationResult(
        command="branch switch",
        status=status,
        data=BranchData(binding.scope_id, binding.name, binding.initial_sha),
        exit_code=0,
        effects=(effect,),
    )
