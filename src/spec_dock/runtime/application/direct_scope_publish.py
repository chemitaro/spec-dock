"""Create a GitHub-numbered Scope without shared control or an operation journal."""

from __future__ import annotations

from datetime import datetime, timezone
import secrets
import sys
from typing import TYPE_CHECKING, cast

from spec_dock.runtime.application.create_github_scope import _parent_records, _require_open_ancestors
from spec_dock.runtime.application.create_node import (
    _create_relative_symlink_at,
    _precheck_pre_github_create_rules_sources,
    _rules_scaffold_specs,
    _scaffold_file_paths,
)
from spec_dock.runtime.application.github_scope_scaffold import build_github_scope_scaffold
from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.application.scope_query import load_scope_views, show_scope
from spec_dock.runtime.application.start_snapshot import capture_local_inputs, verify_local_inputs
from spec_dock.runtime.application.worktree_observation import resolve_scope
from spec_dock.runtime.domain.ids import format_id, resolve_input_title_and_slug
from spec_dock.runtime.infra import fs_repo, template_scaffolder
from spec_dock.runtime.infra.directory_publication import DirectoryPublicationIncomplete, publish_directory
from spec_dock.runtime.infra.git_process import GitProcessError, run_git
from spec_dock.runtime.infra.github_lifecycle import GithubIssueGateway, RemoteIssueError
from spec_dock.runtime.infra.github_remote import github_publication_repository
from spec_dock.runtime.presentation.command_data import DiagnosticData, FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    import argparse
    from pathlib import Path

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.domain.selectors import ScopeKind
    from spec_dock.runtime.presentation.envelope import EffectStatus


def create_scope(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    context.require_writer()
    if namespace.offline:
        raise ValueError("GitHub Scope creation requires an online repository")
    if (
        not namespace.yes
        and not namespace.dry_run
        and (namespace.json or namespace.non_interactive or not sys.stdin.isatty())
    ):
        return OperationResult(
            namespace.command_path,
            "failed",
            DiagnosticData(),
            3,
            error=Diagnostic("CONFIRMATION_REQUIRED", "GitHub Scope creation requires --yes", {}),
        )
    kind = cast("ScopeKind", namespace.command_path.rsplit(" ", 1)[-1])
    title, slug = resolve_input_title_and_slug(namespace.title, namespace.slug)
    workspace = context.root / "spec-dock"
    staging = workspace / ".agent/staging"
    stage_name = f".stage-{secrets.token_hex(16)}"
    if any(path.is_symlink() for path in (staging, *staging.parents)):
        raise ValueError("Scope staging path is redirected")
    views = load_scope_views(workspace)
    inputs = capture_local_inputs(context, views)
    repository = github_publication_repository(context.root, timeout=namespace.timeout)

    def verify_source() -> None:
        fresh = resolve_context(str(context.root), context.root, timeout=namespace.timeout)
        if fresh.clone_identity != context.clone_identity or fresh.worktree_identity != context.worktree_identity:
            raise ValueError("Git project physical identity changed")
        fresh.require_writer()
        if github_publication_repository(fresh.root, timeout=namespace.timeout) != repository:
            raise ValueError("GitHub repository changed during Scope creation")
        verify_local_inputs(fresh, inputs)

    def verify_stage(path: Path) -> None:
        verify_source()
        if not run_git(
            context.root,
            "check-ignore",
            "--no-index",
            "--",
            path.relative_to(context.root).as_posix(),
            missing_ok=True,
            timeout=namespace.timeout,
        ):
            raise ValueError("Scope staging path must be ignored by Git")

    verify_stage(staging / stage_name)
    gateway = GithubIssueGateway(timeout=namespace.timeout)
    parent_target = getattr(namespace, "parent", None)
    parent_id = resolve_scope(context, views, parent_target).id if parent_target else None
    records = {record.id: record for record in fs_repo.load_node_records(workspace)}
    ancestors = _parent_records(kind=kind, parent_id=parent_id, records=records)
    _require_open_ancestors(ancestors=ancestors, repo_root=context.root, repository=repository, gateway=gateway)
    _precheck_pre_github_create_rules_sources(kind=kind, specdock_dir=workspace)
    _scaffold_file_paths(workspace / "templates" / kind, workspace)
    verify_source()
    preview = FamilyData("scope", {"scope": None, "github_ref": None, "title": title, "slug": slug})
    if namespace.dry_run:
        return OperationResult(
            namespace.command_path,
            "planned",
            preview,
            0,
            effects=(Effect("github-create", "planned", repository), Effect("scaffold", "planned", None)),
        )
    if not namespace.yes:
        print(f"Target: {kind} {title}", file=sys.stderr)
        print(f"Repository: {repository}; local workspace: {workspace}", file=sys.stderr)
        print("Writes: github-create, scaffold", file=sys.stderr)
        print("Confirm [yes/no]: ", end="", file=sys.stderr, flush=True)
        if sys.stdin.readline().strip().lower() not in {"yes", "y"}:
            return OperationResult(
                namespace.command_path,
                "failed",
                preview,
                3,
                error=Diagnostic("CONFIRMATION_DECLINED", "operation was not confirmed", {}),
            )
        verify_source()
    try:
        remote = gateway.create(context.root, repository, title=title, body=f"Created by SpecDock.\n\nType: {kind}\n")
    except RemoteIssueError as error:
        return OperationResult(
            namespace.command_path,
            "partial" if error.uncertain else "failed",
            preview,
            6 if error.uncertain else 5,
            effects=(
                Effect("github-create", "unknown" if error.uncertain else "failed", repository),
                Effect("scaffold", "not_attempted", None),
            ),
            error=Diagnostic(error.code, str(error), {}),
            recovery=RecoveryInstructions((
                "Inspect the GitHub repository for the Issue created by this request; do not blindly repeat creation.",
                "After identifying an exact Issue, use a new explicit scope import github operation.",
            )),
        )
    ref = f"gh:{repository}#{remote.number}"
    scope_id = format_id({"initiative": "init", "epic": "epic", "issue": "iss"}[kind], remote.number)
    scaffold_attempted = False
    published = False
    try:
        verify_source()
        if any(view.id == scope_id or view.github_ref == ref for view in load_scope_views(workspace)):
            raise ValueError("GitHub Issue or Scope ID is already linked in the current tree")
        plan, metadata = build_github_scope_scaffold(
            specdock_dir=workspace,
            kind=kind,
            title=title,
            slug=slug,
            parent_id=parent_id,
            parent_record=ancestors[0] if ancestors else None,
            repository=repository,
            issue_number=remote.number,
            today=datetime.now(timezone.utc).date().isoformat(),
        )

        def populate(descriptor: int) -> None:
            template_scaffolder.copy_scaffolded_tree_at(
                workspace / "templates" / kind, plan.dest_dir, descriptor, plan.replacements
            )
            for link, target in _rules_scaffold_specs(kind=kind, dest_dir=plan.dest_dir, specdock_dir=workspace):
                _create_relative_symlink_at(descriptor, node_dir=plan.dest_dir, link_path=link, target_path=target)
            fs_repo.write_meta_payload_at(descriptor, metadata)

        scaffold_attempted = True
        publish_directory(
            plan.dest_dir,
            staging_dir=staging,
            populate=populate,
            before_stage=verify_stage,
            before_publish=verify_source,
            stage_name=stage_name,
        )
        published = True
        created = show_scope(load_scope_views(workspace), plan.meta.id)
    except (ValueError, OSError, RuntimeError) as error:
        published = published or (isinstance(error, DirectoryPublicationIncomplete) and error.confirmed)
        scaffold_status: EffectStatus = (
            "succeeded"
            if published
            else "unknown"
            if isinstance(error, DirectoryPublicationIncomplete) and not error.confirmed
            else "failed"
            if scaffold_attempted
            else "not_attempted"
        )
        return OperationResult(
            namespace.command_path,
            "partial",
            FamilyData("scope", {"scope": None, "github_ref": ref, "title": title, "slug": slug}),
            6,
            effects=(Effect("github-create", "succeeded", ref), Effect("scaffold", scaffold_status, scope_id)),
            error=Diagnostic(
                "SCOPE_PUBLICATION_INCOMPLETE",
                str(error),
                error.details() if isinstance(error, GitProcessError) else {},
            ),
            recovery=RecoveryInstructions((
                f"Inspect GitHub Issue {ref} and the local Scope paths; the confirmed Issue was not rolled back.",
                f"Use a new explicit scope import github {kind} {ref} operation after resolving any local conflict.",
            )),
        )
    return OperationResult(
        namespace.command_path,
        "succeeded",
        FamilyData(
            "scope",
            {
                "scope": {
                    "id": created.id,
                    "kind": created.kind,
                    "title": created.title,
                    "parent_id": created.parent_id,
                    "backend": created.backend.kind,
                    "github_ref": created.github_ref,
                    "path": str(created.path.relative_to(context.root)),
                    "revision": created.revision,
                    "status": {
                        "state": created.status.state,
                        "authority": created.status.authority,
                        "source": created.status.source,
                        "observed_at": created.status.observed_at,
                    },
                },
                "github_ref": ref,
                "changed": True,
            },
        ),
        0,
        effects=(Effect("github-create", "succeeded", ref), Effect("scaffold", "succeeded", created.id)),
    )
