"""Thin vNext adapters for inspecting and switching canonical Scope branches."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_dock_runtime.application.branch_vnext import (
    create_scope_branch_with_receipt,
    preview_scope_branch_create,
    preview_scope_branch_switch,
    resolve_branch_scope,
    resume_scope_branch_create,
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
    if ns.command_path == "branch create":
        common = {
            "repo_root": context.repo_root,
            "common_dir": context.common_dir,
            "worktree_id": context.worktree_id,
            "engine_digest": context.engine_digest,
            "expected_epoch": context.expected_epoch,
        }
        operation_id = ns.resume
        if ns.resume is not None:
            if ns.base is not None or ns.name is not None or ns.dry_run:
                raise ValueError("branch create recovery cannot change or preview the recorded request")
            binding = resume_scope_branch_create(
                **common,
                operation_id=ns.resume,
                expected_scope_id=scope_id,
                lock_timeout=ns.lock_timeout,
            )
        else:
            assert ns.base is not None
            if ns.dry_run:
                binding = preview_scope_branch_create(**common, scope_id=scope_id, base=ns.base, name=ns.name)
            else:
                receipt = create_scope_branch_with_receipt(
                    **common, scope_id=scope_id, base=ns.base, name=ns.name, lock_timeout=ns.lock_timeout
                )
                binding = receipt.binding
                operation_id = receipt.operation_id
        planned = bool(ns.dry_run)
        return OperationResult(
            command="branch create",
            status="planned" if planned else "succeeded",
            data=BranchData(binding.scope_id, binding.name, binding.initial_sha),
            exit_code=0,
            operation_id=operation_id,
            effects=(Effect("git-branch", "planned" if planned else "succeeded", binding.name),),
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
