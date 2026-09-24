"""Thin vNext adapters for Scope dependency inspection and mutation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_dock_runtime.application.dependency_vnext import (
    check_scope_readiness,
    list_scope_dependencies,
    mutate_scope_dependency,
    preview_mutate_scope_dependency,
)
from spec_dock_runtime.presentation.envelope import Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock_runtime.application.dependency_vnext import GithubStateGateway
    from spec_dock_runtime.commands.work_vnext import WorkContext


@dataclass(frozen=True)
class DependencyListData:
    scope_id: str
    view: str
    edges: tuple[object, ...]


def run_dependency_query(
    ns: argparse.Namespace, context: WorkContext, *, gateway: GithubStateGateway
) -> OperationResult[object]:
    specdock_dir = context.repo_root / "spec-dock"
    if ns.command_path == "dependency list":
        listing = list_scope_dependencies(specdock_dir, ns.target, worktree_id=context.worktree_id)
        view = ns.view or "declared"
        edges = listing.effective if view == "effective" else listing.declared
        data: object = DependencyListData(listing.scope_id, view, edges)
    elif ns.command_path == "dependency check":
        data = check_scope_readiness(
            specdock_dir,
            ns.target,
            source=ns.source,
            for_start=True,
            offline=ns.offline,
            gateway=gateway,
            worktree_id=context.worktree_id,
        )
    else:
        raise ValueError("dependency query is unsupported")
    return OperationResult(command=ns.command_path, status="succeeded", data=data, exit_code=0)


def run_dependency_change(ns: argparse.Namespace, context: WorkContext) -> OperationResult[object]:
    if ns.command_path not in {"dependency add", "dependency remove"}:
        raise ValueError("dependency change is unsupported")
    action = "add" if ns.command_path == "dependency add" else "remove"
    args = {
        "repo_root": context.repo_root,
        "common_dir": context.common_dir,
        "worktree_id": context.worktree_id,
        "engine_digest": context.engine_digest,
        "expected_epoch": context.expected_epoch,
        "from_target": ns.from_target,
        "to_target": ns.to_target,
        "action": action,
        "missing_ok": bool(getattr(ns, "missing_ok", False)),
    }
    if ns.dry_run:
        result = preview_mutate_scope_dependency(**args)
        status = "planned"
        effect = "planned"
    else:
        result = mutate_scope_dependency(**args, lock_timeout=ns.lock_timeout)
        status = "succeeded" if result.changed else "unchanged"
        effect = "succeeded" if result.changed else "unchanged"
    return OperationResult(
        command=ns.command_path,
        status=status,
        data=result,
        exit_code=0,
        effects=(Effect("dependency-edge", effect, f"{result.from_id}->{result.to_id}"),),
    )
