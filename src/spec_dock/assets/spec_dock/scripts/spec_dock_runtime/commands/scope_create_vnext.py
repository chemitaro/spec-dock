"""Thin CLI adapter for Scope creation."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Literal, cast

from spec_dock_runtime.application.create_github_scope import create_github_scope, preview_github_scope_create
from spec_dock_runtime.application.resume_github_scope import resume_github_scope_create
from spec_dock_runtime.application.scope_create_vnext import create_local_scope_command
from spec_dock_runtime.commands.scope_result_vnext import ScopeWriteData, project_scope
from spec_dock_runtime.presentation.envelope import Diagnostic, Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock_runtime.application.create_github_scope import GithubScopeGateway
    from spec_dock_runtime.commands.work_vnext import WorkContext


def run_scope_create(
    ns: argparse.Namespace, context: WorkContext, *, gateway: GithubScopeGateway
) -> OperationResult[object]:
    kind = cast("Literal['initiative', 'epic', 'issue']", ns.command_path.rsplit(" ", 1)[-1])
    if ns.backend == "github":
        if ns.offline:
            raise ValueError("GitHub Scope creation requires an online repository")
        parent_id = getattr(ns, "parent", None)
        if ns.resume is not None and ns.dry_run:
            raise ValueError("Scope create recovery cannot be previewed")
        if ns.resume is None and ns.dry_run:
            preview = preview_github_scope_create(
                repo_root=context.repo_root,
                kind=kind,
                title=ns.title,
                parent_id=parent_id,
                slug=ns.slug,
                gateway=gateway,
            )
            return OperationResult(
                command=ns.command_path,
                status="planned",
                data=preview,
                exit_code=0,
                effects=(Effect("github-create", "planned", preview.repository), Effect("scaffold", "planned", None)),
            )
        if ns.resume is None and not ns.yes:
            raise ValueError("GitHub Scope creation requires --yes")
        common = {
            "repo_root": context.repo_root,
            "common_dir": context.common_dir,
            "worktree_id": context.worktree_id,
            "engine_digest": context.engine_digest,
            "expected_epoch": context.expected_epoch,
            "kind": kind,
            "title": ns.title,
            "parent_id": parent_id,
            "slug": ns.slug,
            "gateway": gateway,
            "lock_timeout": ns.lock_timeout,
        }
        if ns.resume is not None:
            created = resume_github_scope_create(**common, operation_id=ns.resume)
        else:
            created = create_github_scope(
                **common,
                updated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            )
        projection = project_scope(context, created.id)
        return OperationResult(
            command=ns.command_path,
            status="succeeded",
            data=ScopeWriteData(
                created.id,
                str(created.path),
                created.github_ref,
                projection.scope,
                projection.status,
                projection.project,
                projection.worktree,
                projection.snapshot_id,
            ),
            exit_code=0,
            operation_id=created.operation_id,
            target=projection.target,
            effects=(
                Effect("github-create", "succeeded", created.github_ref),
                Effect("scaffold", "succeeded", created.id),
            ),
        )
    result = create_local_scope_command(
        repo_root=context.repo_root,
        common_dir=context.common_dir,
        worktree_id=context.worktree_id,
        engine_digest=context.engine_digest,
        expected_epoch=context.expected_epoch,
        kind=kind,
        title=ns.title,
        parent_target=getattr(ns, "parent", None),
        slug=ns.slug,
        updated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        dry_run=ns.dry_run,
        resume_id=ns.resume,
        lock_timeout=ns.lock_timeout,
    )
    projection = project_scope(context, result.scope_id) if result.scope_id is not None and not ns.dry_run else None
    return OperationResult(
        command=ns.command_path,
        status="planned" if ns.dry_run else "succeeded",
        data=(
            ScopeWriteData(
                result.scope_id,
                result.path or projection.scope.path,
                None,
                projection.scope,
                projection.status,
                projection.project,
                projection.worktree,
                projection.snapshot_id,
            )
            if projection is not None and result.scope_id is not None
            else result
        ),
        exit_code=0,
        operation_id=result.operation_id,
        target=projection.target if projection is not None else None,
        effects=(Effect("scope-create", "planned" if ns.dry_run else "succeeded", result.scope_id),),
        warnings=tuple(Diagnostic("STALE_ANCESTOR", warning, {}) for warning in result.warnings),
    )
