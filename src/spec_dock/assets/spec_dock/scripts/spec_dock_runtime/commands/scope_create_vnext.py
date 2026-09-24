"""Thin CLI adapter for Scope creation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Literal, cast

from spec_dock_runtime.application.create_github_scope import create_github_scope, preview_github_scope_create
from spec_dock_runtime.application.resume_github_scope import resume_github_scope_create
from spec_dock_runtime.application.scope_create_vnext import create_local_scope_command
from spec_dock_runtime.presentation.envelope import Diagnostic, Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock_runtime.application.create_github_scope import GithubScopeGateway
    from spec_dock_runtime.commands.work_vnext import WorkContext


@dataclass(frozen=True)
class GithubScopeCreateData:
    scope_id: str | None
    path: str | None
    github_ref: str | None


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
        return OperationResult(
            command=ns.command_path,
            status="succeeded",
            data=GithubScopeCreateData(created.id, str(created.path), created.github_ref),
            exit_code=0,
            operation_id=created.operation_id,
            effects=(
                Effect("github-create", "succeeded", created.github_ref),
                Effect("scaffold", "succeeded", created.id),
            ),
        )
    if ns.resume is not None:
        raise ValueError("local Scope create recovery is not yet connected")
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
        lock_timeout=ns.lock_timeout,
    )
    return OperationResult(
        command=ns.command_path,
        status="planned" if ns.dry_run else "succeeded",
        data=result,
        exit_code=0,
        operation_id=result.operation_id,
        effects=(Effect("scope-create", "planned" if ns.dry_run else "succeeded", result.scope_id),),
        warnings=tuple(Diagnostic("STALE_ANCESTOR", warning, {}) for warning in result.warnings),
    )
