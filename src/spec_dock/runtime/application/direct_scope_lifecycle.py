"""Change one captured Scope lifecycle without changing selection or Git checkout."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import json
import sys
from typing import TYPE_CHECKING, cast

from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.application.scope_completion import plan_close, plan_reopen
from spec_dock.runtime.application.scope_query import load_scope_views
from spec_dock.runtime.application.start_snapshot import capture_local_inputs, verify_local_inputs
from spec_dock.runtime.application.worktree_observation import ancestors_for, read_selection, resolve_scope
from spec_dock.runtime.domain.lifecycle import (
    GithubBackend,
    LocalBackend,
    LocalLifecycle,
    StatusObservation,
    decode_scope_metadata,
    encode_scope_metadata,
)
from spec_dock.runtime.infra.direct_json import MetadataPublicationIncomplete, replace_existing_json
from spec_dock.runtime.infra.git_process import GitProcessError, run_git
from spec_dock.runtime.infra.github_lifecycle import GithubIssueGateway, RemoteIssueError
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    import argparse
    from pathlib import Path

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.scope_completion import CompletionReason
    from spec_dock.runtime.application.scope_query import ScopeView
    from spec_dock.runtime.domain.lifecycle import ObservedState, ScopeMetadata


def lifecycle_scope(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    context.require_writer()
    if (
        not namespace.yes
        and not namespace.dry_run
        and (namespace.json or namespace.non_interactive or not sys.stdin.isatty())
    ):
        raise ValueError("Scope lifecycle mutation requires --yes")
    close = namespace.command_path == "scope close"
    reason = cast("CompletionReason", getattr(namespace, "reason", "completed"))
    views = load_scope_views(context.root / "spec-dock")
    selection = read_selection(context, views)
    target = resolve_scope(context, views, namespace.target, selection=selection)
    if namespace.expect_backend is not None and target.backend.kind != namespace.expect_backend:
        raise ValueError("target backend does not match --expect-backend")
    if namespace.expect_current is not None:
        expected = resolve_scope(context, views, namespace.expect_current, selection=selection).id
        if selection.status != "selected" or selection.record is None or selection.record.scope_id != expected:
            raise ValueError("direct target does not match --expect-current")
    backend = target.backend
    effect_kind = (
        ("github.issue.close" if close else "github.issue.reopen")
        if isinstance(backend, GithubBackend)
        else "scope.lifecycle"
    )
    effect_target = target.github_ref if isinstance(backend, GithubBackend) else target.id
    inputs = capture_local_inputs(context, views)
    gateway = GithubIssueGateway(timeout=namespace.timeout)
    relevant = (
        tuple(view for view in views if target.id in {parent.id for parent in ancestors_for(views, view)})
        if close
        else ancestors_for(views, target)
    )
    if namespace.offline and any(isinstance(view.backend, GithubBackend) for view in (target, *relevant)):
        raise ValueError("offline mode cannot fetch required GitHub state")
    states: dict[str, ObservedState] = {}
    for view in (target, *relevant):
        view_backend = view.backend
        if isinstance(view_backend, GithubBackend):
            remote = gateway.get(
                context.root, f"{view_backend.repo_owner}/{view_backend.repo_name}", view_backend.issue_number
            )
            status = _status(remote.state, remote.updated_at)
        else:
            status = view.status
        states[view.id] = status.state
        if view.id == target.id:
            target = replace(target, status=status)
    decision = plan_close(views, target.id, states, reason=reason) if close else plan_reopen(views, target.id, states)
    if namespace.dry_run:
        return OperationResult(
            namespace.command_path,
            "planned",
            FamilyData(
                "scope",
                {**_data(target, context, False, decision.descendants).result, "can_apply": True, "blockers": ()},
            ),
            0,
            effects=(Effect(effect_kind, "planned", effect_target),),
        )

    def verify_source() -> None:
        fresh = resolve_context(str(context.root), context.root, timeout=namespace.timeout)
        if fresh.clone_identity != context.clone_identity or fresh.worktree_identity != context.worktree_identity:
            raise ValueError("Git project physical identity changed")
        fresh.require_writer()
        verify_local_inputs(fresh, inputs)
        if not namespace.yes:
            observed = read_selection(fresh, views)
            if (observed.status, observed.record, observed.handle) != (
                selection.status,
                selection.record,
                selection.handle,
            ):
                raise ValueError("direct selection changed during confirmation")

    verify_source()
    if not namespace.yes:
        print(f"Target: {target.id} ({effect_target}); {decision.before} -> {decision.after}", file=sys.stderr)
        print(f"Writes: {effect_kind}; descendants: {', '.join(decision.descendants) or 'none'}", file=sys.stderr)
        print("Confirm [yes/no]: ", end="", file=sys.stderr, flush=True)
        if sys.stdin.readline().strip().lower() not in {"yes", "y"}:
            return OperationResult(
                namespace.command_path,
                "failed",
                _data(target, context, False, decision.descendants),
                3,
                error=Diagnostic("CONFIRMATION_DECLINED", "operation was not confirmed", {}),
            )
        verify_source()
    attempted = False

    def before_change() -> None:
        nonlocal attempted
        verify_source()
        attempted = True

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
            raise ValueError("metadata staging path must be ignored by Git")

    effects: tuple[Effect, ...] = ()
    changed = False
    try:
        if decision.changed and isinstance(backend, GithubBackend):
            remote = gateway.set_state(
                context.root,
                f"{backend.repo_owner}/{backend.repo_name}",
                backend.issue_number,
                state="closed" if close else "open",
                reason=("completed" if reason == "completed" else "not_planned") if close else None,
                before_change=before_change,
            )
            target = replace(target, status=_status(remote.state, remote.updated_at))
        elif decision.changed and isinstance(backend, LocalBackend):
            relative = (target.path / ".meta.json").relative_to(context.root).as_posix()
            captured = next(item for item in inputs if item.relative_path == relative)
            metadata = decode_scope_metadata(json.loads(captured.payload))
            updated = replace(
                metadata,
                revision=metadata.revision + 1,
                backend=LocalBackend(
                    LocalLifecycle(
                        decision.after, backend.lifecycle.revision + 1, datetime.now(timezone.utc).isoformat()
                    )
                ),
            )
            try:
                published = replace_existing_json(
                    target.path / ".meta.json",
                    encode_scope_metadata(updated),
                    expected_bytes=captured.payload,
                    expected_identity=captured.identity,
                    staging_dir=context.root / "spec-dock/.agent/staging",
                    before_replace=verify_source,
                    before_stage=verify_stage,
                )
            except MetadataPublicationIncomplete as error:
                changed = error.published is not None
                effects = (Effect(effect_kind, "succeeded" if changed else "unknown", effect_target),)
                if changed:
                    target = _local_view(target, updated)
                raise
            inputs = tuple(
                replace(item, payload=published.payload, identity=published.identity) if item == captured else item
                for item in inputs
            )
            target = _local_view(target, updated)
            attempted = True
        changed = attempted
        effects = (Effect(effect_kind, "succeeded" if changed else "unchanged", effect_target),)
        verify_source()
    except (ValueError, OSError, RuntimeError) as error:
        if not effects:
            effects = (
                Effect(
                    effect_kind,
                    "unknown"
                    if isinstance(error, RemoteIssueError) and error.uncertain
                    else "failed"
                    if attempted
                    else "not_attempted",
                    effect_target,
                ),
            )
        partial = any(effect.status in ("succeeded", "unknown") for effect in effects)
        if any(effect.status == "unknown" for effect in effects):
            target = replace(target, status=StatusObservation("unknown", backend.kind, "unknown", None, None, False))
        return OperationResult(
            namespace.command_path,
            "partial" if partial else "failed",
            _data(target, context, changed, decision.descendants),
            6 if partial else 5 if isinstance(error, (OSError, RuntimeError)) else 3,
            effects=effects,
            error=Diagnostic(
                error.code if isinstance(error, RemoteIssueError) else "SCOPE_LIFECYCLE_INCOMPLETE",
                str(error),
                error.details() if isinstance(error, GitProcessError) else {},
            ),
            recovery=RecoveryInstructions((
                f"Inspect the exact Scope {target.id} and its authority before a new explicit operation; do not blindly repeat a mutation.",
            )),
        )
    return OperationResult(
        namespace.command_path,
        "succeeded" if changed else "unchanged",
        _data(target, context, changed, decision.descendants),
        0,
        effects=effects,
    )


def _status(state: ObservedState, updated_at: str) -> StatusObservation:
    return StatusObservation(state, "github", "github", datetime.now(timezone.utc).isoformat(), updated_at, False)


def _local_view(target: ScopeView, metadata: ScopeMetadata) -> ScopeView:
    assert isinstance(metadata.backend, LocalBackend)
    lifecycle = metadata.backend.lifecycle
    return replace(
        target,
        backend=metadata.backend,
        revision=metadata.revision,
        status=StatusObservation(lifecycle.state, "local", "local", lifecycle.updated_at, None, False),
    )


def _data(target: ScopeView, context: ProjectContext, changed: bool, descendants: tuple[str, ...] = ()) -> FamilyData:
    return FamilyData(
        "scope",
        {
            "scope": {
                "id": target.id,
                "kind": target.kind,
                "title": target.title,
                "parent_id": target.parent_id,
                "backend": target.backend.kind,
                "github_ref": target.github_ref,
                "path": str(target.path.relative_to(context.root)),
                "revision": target.revision,
                "status": {
                    "state": target.status.state,
                    "authority": target.status.authority,
                    "source": target.status.source,
                    "observed_at": target.status.observed_at,
                },
            },
            "github_ref": target.github_ref,
            "changed": changed,
            "descendants": descendants,
        },
    )
