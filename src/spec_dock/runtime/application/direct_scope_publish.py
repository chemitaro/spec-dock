"""Create a GitHub-numbered Scope without shared control or an operation journal."""

from __future__ import annotations

from contextlib import suppress
from dataclasses import replace
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
from spec_dock.runtime.application.worktree_observation import read_selection, resolve_scope
from spec_dock.runtime.domain.ids import format_id, resolve_input_title_and_slug
from spec_dock.runtime.domain.lifecycle import StatusObservation
from spec_dock.runtime.domain.selectors import parse_github_ref
from spec_dock.runtime.infra import fs_repo, template_scaffolder
from spec_dock.runtime.infra.directory_publication import DirectoryPublicationIncomplete, publish_directory
from spec_dock.runtime.infra.git_process import GitProcessError, run_git
from spec_dock.runtime.infra.github_lifecycle import GithubIssueGateway, RemoteIssueError
from spec_dock.runtime.infra.github_remote import github_publication_repository
from spec_dock.runtime.infra.scope_metadata import write_new_scope_metadata_at
from spec_dock.runtime.infra.scope_tree import ScopeIdentityConflict
from spec_dock.runtime.presentation.command_data import DiagnosticData, FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    import argparse
    from pathlib import Path

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.scope_query import ScopeView
    from spec_dock.runtime.domain.selectors import ScopeKind
    from spec_dock.runtime.presentation.envelope import EffectStatus


def create_scope(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    return _publish_scope(namespace, context, create=True)


def import_scope(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    return _publish_scope(namespace, context, create=False)


def _publish_scope(namespace: argparse.Namespace, context: ProjectContext, *, create: bool) -> OperationResult[object]:
    context.require_writer()
    if namespace.offline:
        raise ValueError("GitHub Scope publication requires an online repository")
    if (
        create
        and not namespace.yes
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
    selection = read_selection(context, views)
    if namespace.expect_backend is not None and namespace.expect_backend != "github":
        raise ValueError("target backend does not match --expect-backend")
    if namespace.expect_current is not None:
        expected = resolve_scope(context, views, namespace.expect_current, selection=selection).id
        if selection.status != "selected" or selection.record is None or selection.record.scope_id != expected:
            raise ValueError("direct target does not match --expect-current")
    inputs = capture_local_inputs(context, views)
    repository = github_publication_repository(context.root, timeout=namespace.timeout)
    imported = None if create else parse_github_ref(namespace.github_ref, repo_hint=namespace.github_repo)
    if imported is not None and f"{imported.owner}/{imported.repo}" != repository:
        raise ValueError("foreign GitHub Issue import is rejected")
    if imported is not None:
        import_id = format_id({"initiative": "init", "epic": "epic", "issue": "iss"}[kind], imported.issue_number)
        import_ref = f"gh:{repository}#{imported.issue_number}"
        if any(view.id == import_id or view.github_ref == import_ref for view in views):
            raise ValueError("GitHub Issue or Scope ID is already linked in the current tree")

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
    parent_id = resolve_scope(context, views, parent_target, selection=selection).id if parent_target else None
    records = {record.id: record for record in fs_repo.load_node_records(workspace)}
    ancestors = _parent_records(kind=kind, parent_id=parent_id, records=records)
    _require_open_ancestors(ancestors=ancestors, repo_root=context.root, repository=repository, gateway=gateway)
    _precheck_pre_github_create_rules_sources(kind=kind, specdock_dir=workspace)
    _scaffold_file_paths(workspace / "templates" / kind, workspace)
    verify_source()
    if imported is not None:
        remote = gateway.get(context.root, repository, imported.issue_number)
    ref = None if imported is None else f"gh:{repository}#{imported.issue_number}"
    preview = FamilyData("scope", {"scope": None, "github_ref": ref, "title": title, "slug": slug, "changed": False})
    if namespace.dry_run:
        return OperationResult(
            namespace.command_path,
            "planned",
            FamilyData("scope", {**preview.result, "can_apply": True, "blockers": ()}),
            0,
            effects=(
                *((Effect("github-create", "planned", repository),) if create else ()),
                Effect("scaffold", "planned", None),
            ),
        )
    if create and not namespace.yes:
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
    if create:
        try:
            remote = gateway.create(
                context.root, repository, title=title, body=f"Created by SpecDock.\n\nType: {kind}\n"
            )
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
    observed_at = datetime.now(timezone.utc).isoformat()
    ref = f"gh:{repository}#{remote.number}"
    scope_id = format_id({"initiative": "init", "epic": "epic", "issue": "iss"}[kind], remote.number)
    scaffold_attempted = False
    published = False
    created: ScopeView | None = None
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
            write_new_scope_metadata_at(descriptor, metadata)

        def read_published(*, targeted: bool = False) -> ScopeView:
            fresh = resolve_context(str(context.root), context.root, timeout=namespace.timeout)
            if fresh.clone_identity != context.clone_identity or fresh.worktree_identity != context.worktree_identity:
                raise ValueError("Git project physical identity changed after publication")
            fresh.require_writer()
            observed = show_scope(load_scope_views(workspace, target_id=scope_id if targeted else None), scope_id)
            if (
                observed.path != plan.dest_dir
                or observed.kind != kind
                or observed.parent_id != parent_id
                or observed.github_ref != ref
                or observed.backend.kind != "github"
                or observed.title != title
                or observed.revision != 0
            ):
                raise ValueError("published Scope identity or metadata changed")
            return replace(
                observed,
                status=StatusObservation(remote.state, "github", "github", observed_at, remote.updated_at, False),
            )

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
        created = read_published()
    except (ValueError, OSError, RuntimeError) as error:
        published = published or (isinstance(error, DirectoryPublicationIncomplete) and error.confirmed)
        if isinstance(error, DirectoryPublicationIncomplete) and error.confirmed:
            with suppress(LookupError, ValueError, OSError, RuntimeError):
                created = read_published(targeted=True)
        scaffold_status: EffectStatus = (
            "succeeded"
            if published
            else "unknown"
            if isinstance(error, DirectoryPublicationIncomplete) and not error.confirmed
            else "failed"
            if scaffold_attempted
            else "not_attempted"
        )
        partial = create or published or scaffold_status == "unknown"
        return OperationResult(
            namespace.command_path,
            "partial" if partial else "failed",
            FamilyData(
                "scope",
                {
                    "scope": _scope_payload(created, context) if created is not None else None,
                    "github_ref": ref,
                    "title": title,
                    "slug": slug,
                    "changed": published,
                },
            ),
            6 if partial else 5 if scaffold_attempted or isinstance(error, OSError) else 3,
            effects=(
                *((Effect("github-create", "succeeded", ref),) if create else ()),
                Effect("scaffold", scaffold_status, scope_id),
            ),
            error=Diagnostic(
                "SCOPE_PUBLICATION_INCOMPLETE",
                str(error),
                error.details()
                if isinstance(error, GitProcessError)
                else {"paths": [str(path) for path in error.paths]}
                if isinstance(error, ScopeIdentityConflict)
                else {},
            ),
            recovery=RecoveryInstructions((
                f"Inspect the confirmed GitHub Issue {ref} and the local Scope paths before a new explicit operation.",
                f"Use a new explicit scope import github {kind} {ref} operation after resolving any local conflict.",
            )),
        )
    assert created is not None
    return OperationResult(
        namespace.command_path,
        "succeeded",
        FamilyData(
            "scope",
            {
                "scope": _scope_payload(created, context),
                "github_ref": ref,
                "changed": True,
            },
        ),
        0,
        effects=(
            *((Effect("github-create", "succeeded", ref),) if create else ()),
            Effect("scaffold", "succeeded", created.id),
        ),
    )


def _scope_payload(scope: ScopeView, context: ProjectContext) -> dict[str, object]:
    return {
        "id": scope.id,
        "kind": scope.kind,
        "title": scope.title,
        "parent_id": scope.parent_id,
        "backend": scope.backend.kind,
        "github_ref": scope.github_ref,
        "path": str(scope.path.relative_to(context.root)),
        "revision": scope.revision,
        "status": {
            "state": scope.status.state,
            "authority": scope.status.authority,
            "source": scope.status.source,
            "observed_at": scope.status.observed_at,
        },
    }
