"""Complete the fixed target before releasing its captured local selection."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import json
from typing import TYPE_CHECKING

from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.application.scope_query import load_scope_views
from spec_dock.runtime.application.start_snapshot import capture_local_inputs, verify_local_inputs
from spec_dock.runtime.application.worktree_observation import ancestors_for, read_selection, resolve_scope
from spec_dock.runtime.domain.lifecycle import (
    GithubBackend,
    LocalBackend,
    LocalLifecycle,
    decode_scope_metadata,
    encode_scope_metadata,
)
from spec_dock.runtime.infra.direct_json import MetadataPublicationIncomplete, replace_existing_json
from spec_dock.runtime.infra.git_process import run_git
from spec_dock.runtime.infra.github_lifecycle import GithubIssueGateway, RemoteIssueError
from spec_dock.runtime.infra.work_target_store import SelectionRemovalUnknown, WorkTargetStore
from spec_dock.runtime.presentation.command_data import DiagnosticData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult

if TYPE_CHECKING:
    import argparse
    from pathlib import Path

    from spec_dock.runtime.application.project_context import ProjectContext


@dataclass(frozen=True)
class FinishData:
    scope_id: str
    completed: bool
    branch_before: str | None
    branch_after: str | None
    selection_token: str | None
    kind: str = "work-finish"


def finish_work(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    context.require_writer()
    if not namespace.yes and not namespace.dry_run:
        raise ValueError("work finish requires --yes")
    views = load_scope_views(context.root / "spec-dock")
    captured = read_selection(context, views)
    target = resolve_scope(context, views, namespace.target, selection=captured)
    inputs = capture_local_inputs(context, views)
    if namespace.expect_backend is not None and target.backend.kind != namespace.expect_backend:
        raise ValueError("target backend does not match --expect-backend")
    if namespace.expect_current is not None:
        expected = resolve_scope(context, views, namespace.expect_current, selection=captured).id
        if captured.status != "selected" or captured.record is None or captured.record.scope_id != expected:
            raise ValueError("direct target does not match --expect-current")
    backend = target.backend
    descendants = tuple(view for view in views if target.id in {ancestor.id for ancestor in ancestors_for(views, view)})
    clear_handle = (
        captured.handle
        if captured.status == "selected"
        and captured.record is not None
        and captured.record.scope_id in {target.id, *(child.id for child in descendants)}
        else None
    )
    if namespace.offline and any(isinstance(view.backend, GithubBackend) for view in (target, *descendants)):
        raise ValueError("offline mode cannot fetch required GitHub state")
    gateway = GithubIssueGateway(timeout=namespace.timeout)
    try:
        observed_state = (
            gateway.get(context.root, f"{backend.repo_owner}/{backend.repo_name}", backend.issue_number).state
            if isinstance(backend, GithubBackend)
            else target.status.state
        )
        for child in descendants:
            child_backend = child.backend
            state = (
                gateway.get(
                    context.root, f"{child_backend.repo_owner}/{child_backend.repo_name}", child_backend.issue_number
                ).state
                if isinstance(child_backend, GithubBackend)
                else child.status.state
            )
            if state != "completed":
                raise ValueError("DESCENDANT_NOT_COMPLETED")
    except RemoteIssueError as error:
        return OperationResult(
            "work finish", "failed", DiagnosticData(), 5, error=Diagnostic(error.code, str(error), {})
        )
    if observed_state == "unknown":
        raise ValueError("SCOPE_STATUS_UNKNOWN")
    if observed_state == "not-planned":
        raise ValueError("TERMINAL_REASON_CONFLICT: reopen is required")
    effect_kind = "github.issue.close" if isinstance(backend, GithubBackend) else "scope.lifecycle"
    effect_target = target.github_ref if isinstance(backend, GithubBackend) else target.id
    if namespace.dry_run:
        planned = [Effect(effect_kind, "planned", effect_target)]
        if clear_handle is not None:
            planned.append(Effect("selection.clear", "planned", clear_handle.token))
        return OperationResult(
            "work finish",
            "planned",
            FinishData(
                target.id,
                observed_state == "completed",
                context.branch,
                context.branch,
                captured.handle.token if captured.handle else None,
            ),
            0,
            effects=tuple(planned),
        )

    def verify_source() -> ProjectContext:
        fresh = resolve_context(str(context.root), context.root, timeout=namespace.timeout)
        if fresh.clone_identity != context.clone_identity or fresh.worktree_identity != context.worktree_identity:
            raise ValueError("Git project physical identity changed")
        fresh.require_writer()
        verify_local_inputs(fresh, inputs)
        return fresh

    verify_source()
    already_completed = observed_state == "completed"
    change_requested = False

    def before_change() -> None:
        nonlocal change_requested
        verify_source()
        change_requested = True

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

    effects: list[Effect] = []
    completed = False
    try:
        if not already_completed and isinstance(backend, GithubBackend):
            try:
                gateway.set_state(
                    context.root,
                    f"{backend.repo_owner}/{backend.repo_name}",
                    backend.issue_number,
                    state="closed",
                    reason="completed",
                    before_change=before_change,
                )
            except RemoteIssueError as error:
                effects.append(
                    Effect("github.issue.close", "unknown" if error.uncertain else "failed", target.github_ref)
                )
                raise
        elif not already_completed and isinstance(backend, LocalBackend):
            relative = (target.path / ".meta.json").relative_to(context.root).as_posix()
            captured_input = next(item for item in inputs if item.relative_path == relative)
            metadata = decode_scope_metadata(json.loads(captured_input.payload))
            updated = replace(
                metadata,
                revision=metadata.revision + 1,
                backend=LocalBackend(
                    LocalLifecycle(
                        "completed",
                        backend.lifecycle.revision + 1,
                        datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    )
                ),
            )
            try:
                published = replace_existing_json(
                    target.path / ".meta.json",
                    encode_scope_metadata(updated),
                    expected_bytes=captured_input.payload,
                    expected_identity=captured_input.identity,
                    staging_dir=context.root / "spec-dock/.agent/staging",
                    before_replace=verify_source,
                    before_stage=verify_stage,
                )
            except MetadataPublicationIncomplete as error:
                completed = error.published is not None
                effects.append(Effect(effect_kind, "succeeded" if completed else "unknown", effect_target))
                raise
            inputs = tuple(
                replace(item, payload=published.payload, identity=published.identity)
                if item == captured_input
                else item
                for item in inputs
            )
            change_requested = True
        completed = True
        effects.append(Effect(effect_kind, "succeeded" if change_requested else "unchanged", effect_target))
        verify_source()
        if clear_handle is not None:
            with WorkTargetStore(context.root) as store:
                try:
                    outcome = store.remove_observed(clear_handle)
                except SelectionRemovalUnknown:
                    effects.append(Effect("selection.clear", "unknown", clear_handle.token))
                    raise
                except (OSError, ValueError, RuntimeError):
                    effects.append(Effect("selection.clear", "failed", clear_handle.token))
                    raise
                if outcome == "conflict":
                    effects.append(Effect("selection.clear", "failed", clear_handle.token))
                    raise ValueError("captured selection changed")
                effects.append(
                    Effect("selection.clear", "succeeded" if outcome == "removed" else "unchanged", clear_handle.token)
                )
        after_context = verify_source()
        after = read_selection(after_context, load_scope_views(context.root / "spec-dock"))
    except (ValueError, OSError, RuntimeError) as error:
        if effects and clear_handle is not None and not any(effect.kind == "selection.clear" for effect in effects):
            effects.append(Effect("selection.clear", "not_attempted", clear_handle.token))
        applied = any(effect.status in ("succeeded", "unknown") for effect in effects)
        branch, token = None, None
        try:
            current = resolve_context(str(context.root), context.root, timeout=namespace.timeout)
            if (
                current.clone_identity == context.clone_identity
                and current.worktree_identity == context.worktree_identity
            ):
                branch = current.branch
                observed = read_selection(current, load_scope_views(context.root / "spec-dock"))
                token = observed.handle.token if observed.status == "selected" and observed.handle else None
        except (ValueError, OSError, RuntimeError):
            pass
        return OperationResult(
            "work finish",
            "partial" if applied else "failed",
            FinishData(target.id, completed, context.branch, branch, token),
            6 if applied else 5 if isinstance(error, (OSError, RuntimeError)) else 3,
            effects=tuple(effects),
            error=Diagnostic(
                error.code if isinstance(error, RemoteIssueError) else "WORK_FINISH_INCOMPLETE", str(error), {}
            ),
        )
    return OperationResult(
        "work finish",
        "succeeded" if any(effect.status == "succeeded" for effect in effects) else "unchanged",
        FinishData(
            target.id,
            True,
            context.branch,
            after_context.branch,
            after.handle.token if after.status == "selected" and after.handle else None,
        ),
        0,
        effects=tuple(effects),
    )
