"""Thin CLI adapter for importing a GitHub Issue as a Scope."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Literal, cast

from spec_dock_runtime.application.import_github_scope import (
    import_github_scope,
    preview_import_github_scope,
    resume_github_scope_import,
)
from spec_dock_runtime.presentation.envelope import Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock_runtime.application.create_github_scope import GithubScopeGateway
    from spec_dock_runtime.commands.work_vnext import WorkContext


@dataclass(frozen=True)
class GithubScopeImportData:
    scope_id: str
    path: str
    github_ref: str


def run_scope_import(
    ns: argparse.Namespace, context: WorkContext, *, gateway: GithubScopeGateway
) -> OperationResult[object]:
    if ns.offline:
        raise ValueError("GitHub Scope import requires an online repository")
    if ns.github_ref is None:
        raise ValueError("GitHub Scope import requires a GitHub Issue reference")
    if ns.resume is not None and ns.dry_run:
        raise ValueError("Scope import recovery cannot be previewed")
    kind = cast("Literal['initiative', 'epic', 'issue']", ns.command_path.rsplit(" ", 1)[-1])
    parent_id = getattr(ns, "parent", None)
    if ns.dry_run:
        preview = preview_import_github_scope(
            repo_root=context.repo_root,
            kind=kind,
            github_ref=ns.github_ref,
            repo_hint=ns.github_repo,
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
            effects=(Effect("scaffold", "planned", preview.github_ref),),
        )
    common = {
        "repo_root": context.repo_root,
        "common_dir": context.common_dir,
        "worktree_id": context.worktree_id,
        "engine_digest": context.engine_digest,
        "expected_epoch": context.expected_epoch,
        "kind": kind,
        "github_ref": ns.github_ref,
        "repo_hint": ns.github_repo,
        "title": ns.title,
        "parent_id": parent_id,
        "slug": ns.slug,
        "gateway": gateway,
        "lock_timeout": ns.lock_timeout,
    }
    if ns.resume is not None:
        imported = resume_github_scope_import(**common, operation_id=ns.resume)
    else:
        imported = import_github_scope(
            **common,
            updated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        )
    return OperationResult(
        command=ns.command_path,
        status="succeeded",
        data=GithubScopeImportData(imported.id, str(imported.path), imported.github_ref),
        exit_code=0,
        operation_id=imported.operation_id,
        effects=(Effect("scaffold", "succeeded", imported.id),),
    )
