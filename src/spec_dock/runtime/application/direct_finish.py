"""Complete the fixed target before releasing its captured local selection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.application.scope_query import load_scope_views
from spec_dock.runtime.application.start_snapshot import capture_local_inputs, verify_local_inputs
from spec_dock.runtime.application.worktree_observation import ancestors_for, read_selection, resolve_scope
from spec_dock.runtime.domain.lifecycle import GithubBackend
from spec_dock.runtime.infra.github_lifecycle import GithubIssueGateway, RemoteIssueError
from spec_dock.runtime.infra.work_target_store import SelectionRemovalUnknown, WorkTargetStore
from spec_dock.runtime.presentation.command_data import DiagnosticData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult

if TYPE_CHECKING:
    import argparse

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
    target = resolve_scope(context, views, namespace.target)
    inputs = capture_local_inputs(context, views)
    captured = read_selection(context, views)
    if namespace.expect_backend is not None and target.backend.kind != namespace.expect_backend:
        raise ValueError("target backend does not match --expect-backend")
    if namespace.expect_current is not None:
        expected = resolve_scope(context, views, namespace.expect_current).id
        if captured.status != "selected" or captured.record is None or captured.record.scope_id != expected:
            raise ValueError("direct target does not match --expect-current")
    backend = target.backend
    if not isinstance(backend, GithubBackend):
        raise ValueError("legacy local Finish is not connected yet")
    if namespace.offline:
        raise ValueError("offline mode cannot fetch required GitHub state")
    gateway = GithubIssueGateway(timeout=namespace.timeout)
    try:
        remote = gateway.get(context.root, f"{backend.repo_owner}/{backend.repo_name}", backend.issue_number)
        descendants = tuple(
            view for view in views if target.id in {ancestor.id for ancestor in ancestors_for(views, view)}
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
    if remote.state == "unknown":
        raise ValueError("SCOPE_STATUS_UNKNOWN")
    if remote.state == "not-planned":
        raise ValueError("TERMINAL_REASON_CONFLICT: reopen is required")
    if namespace.dry_run:
        planned = [Effect("github.issue.close", "planned", target.github_ref)]
        if (
            captured.status == "selected"
            and captured.record is not None
            and captured.record.scope_id in {target.id, *(child.id for child in descendants)}
            and captured.handle is not None
        ):
            planned.append(Effect("selection.clear", "planned", captured.handle.token))
        return OperationResult(
            "work finish",
            "planned",
            FinishData(
                target.id,
                remote.state == "completed",
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
    already_completed = remote.state == "completed"
    change_requested = False

    def before_change() -> None:
        nonlocal change_requested
        verify_source()
        change_requested = True

    effects: list[Effect] = []
    completed = False
    try:
        if not already_completed:
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
        completed = True
        effects.append(
            Effect("github.issue.close", "succeeded" if change_requested else "unchanged", target.github_ref)
        )
        verify_source()
        if (
            captured.status == "selected"
            and captured.record is not None
            and captured.record.scope_id in {target.id, *(child.id for child in descendants)}
            and captured.handle is not None
        ):
            with WorkTargetStore(context.root) as store:
                try:
                    outcome = store.remove_observed(captured.handle)
                except SelectionRemovalUnknown:
                    effects.append(Effect("selection.clear", "unknown", captured.handle.token))
                    raise
                except (OSError, ValueError, RuntimeError):
                    effects.append(Effect("selection.clear", "failed", captured.handle.token))
                    raise
                if outcome == "conflict":
                    effects.append(Effect("selection.clear", "failed", captured.handle.token))
                    raise ValueError("captured selection changed")
                effects.append(
                    Effect(
                        "selection.clear", "succeeded" if outcome == "removed" else "unchanged", captured.handle.token
                    )
                )
        after_context = verify_source()
        after = read_selection(after_context, load_scope_views(context.root / "spec-dock"))
    except (ValueError, OSError, RuntimeError) as error:
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
