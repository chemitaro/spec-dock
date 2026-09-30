"""Start alone holds clone exclusion through checkout and direct publication."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import TYPE_CHECKING

from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.application.scope_query import load_scope_views
from spec_dock.runtime.application.worktree_observation import (
    ancestors_for,
    observe_worktrees,
    read_selection,
    resolve_scope,
)
from spec_dock.runtime.domain.lifecycle import GithubBackend
from spec_dock.runtime.domain.work_target import WorkTarget
from spec_dock.runtime.infra.git_process import GitProcessError, run_git
from spec_dock.runtime.infra.github_lifecycle import GithubIssueGateway, RemoteIssueError
from spec_dock.runtime.infra.identity import DirectoryIdentity
from spec_dock.runtime.infra.start_lock import StartLock, StartLockBusy
from spec_dock.runtime.infra.work_target_store import WorkTargetStore
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.scope_query import ScopeView
    from spec_dock.runtime.application.worktree_observation import SelectionObservation


class StartPrecondition(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _check_selection(context: ProjectContext, views: tuple[ScopeView, ...], target: ScopeView) -> SelectionObservation:
    for row in observe_worktrees(context):
        other = row.selection.record
        if (
            row.path != str(context.root)
            and other
            and (
                other.scope_id == target.id or (target.github_ref is not None and other.github_ref == target.github_ref)
            )
        ):
            raise StartPrecondition("SCOPE_ALREADY_SELECTED", "Scope is already selected by another worktree")
        if row.selection.status in ("invalid", "unavailable"):
            raise ValueError(row.selection.reason or "worktree selection is unavailable")
    selection = read_selection(context, views)
    if selection.status != "empty" and not (
        selection.status == "selected" and selection.record is not None and selection.record.scope_id == target.id
    ):
        raise ValueError("current worktree already has a direct target")
    return selection


def _check_private_state(context: ProjectContext, timeout: float) -> None:
    if run_git(context.root, "ls-files", "-z", "--", "spec-dock/.agent/work-target", timeout=timeout):
        raise ValueError("work target state must not be tracked by Git")
    for basename in ("target-" + "0" * 32 + ".json", ".stage-" + "0" * 32):
        if not run_git(
            context.root,
            "check-ignore",
            "--no-index",
            "--",
            f"spec-dock/.agent/work-target/{basename}",
            timeout=timeout,
            missing_ok=True,
        ):
            raise ValueError("work target state must be ignored by Git")


@dataclass(frozen=True)
class StartData:
    scope_id: str
    started: bool
    branch_before: str | None
    branch_after: str | None
    selection_token: str | None
    kind: str = "work-start"


def start_work(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[StartData]:
    effects: list[Effect] = []
    scope_id = namespace.target
    branch_after = context.branch
    token: str | None = None
    phase = "git.branch.create"
    mutation_started = False
    branch: str | None = None
    try:
        context.require_writer()
        _check_private_state(context, namespace.timeout)
        views = load_scope_views(context.root / "spec-dock")
        target = resolve_scope(context, views, namespace.target)
        scope_id = target.id
        if namespace.offline:
            raise ValueError("Start requires live GitHub readiness; --offline cannot start this Scope")
        gateway = GithubIssueGateway(timeout=namespace.timeout)
        for required in (*ancestors_for(views, target), target):
            if isinstance(required.backend, GithubBackend):
                backend = required.backend
                state = gateway.get(
                    context.root, f"{backend.repo_owner}/{backend.repo_name}", backend.issue_number
                ).state
            else:
                state = required.status.state
            if state != "open":
                raise ValueError(f"Scope is not open: {required.id}")
        metadata = (target.path / ".meta.json").read_bytes()
        slug = json.loads(metadata)["slug"]
        branch = namespace.branch or f"{target.id}-{slug}"
        run_git(context.root, "check-ref-format", "--branch", branch, timeout=namespace.timeout)
        existing = run_git(
            context.root,
            "rev-parse",
            "--verify",
            "--quiet",
            f"refs/heads/{branch}",
            timeout=namespace.timeout,
            missing_ok=True,
        )
        create_branch = not existing
        if not create_branch:
            if not namespace.branch:
                raise ValueError(f"existing branch requires explicit --branch {branch}")
            if namespace.base:
                raise ValueError("existing branch reuse does not accept --base")
            tip = existing.decode().removesuffix("\n")
        else:
            if not namespace.base:
                raise ValueError("a new branch requires --base")
            tip = (
                run_git(
                    context.root, "rev-parse", "--verify", f"{namespace.base}^{{commit}}", timeout=namespace.timeout
                )
                .decode()
                .removesuffix("\n")
            )
        if run_git(context.root, "status", "--porcelain", "-z", timeout=namespace.timeout):
            raise ValueError("worktree must be clean before Start")
        planned_selection = _check_selection(context, views, target)
        if namespace.dry_run:
            return OperationResult(
                "work start",
                "planned",
                StartData(scope_id, False, context.branch, branch, None),
                0,
                effects=(
                    Effect("git.branch.create", "planned", branch),
                    Effect("git.checkout", "planned", branch),
                    Effect("selection.publish", "planned", target.id),
                ),
            )
        with (
            DirectoryIdentity(context.root) as root_handle,
            StartLock(context.common_dir, timeout=namespace.lock_timeout) as lock,
        ):
            root_handle.verify()
            lock.verify()
            if root_handle.identity != context.worktree_identity or lock.identity != context.clone_identity:
                raise ValueError("project physical identity changed")
            current = resolve_context(str(context.root), context.root)
            if (
                current.head != context.head
                or current.branch != context.branch
                or (target.path / ".meta.json").read_bytes() != metadata
            ):
                raise ValueError("Start snapshot changed")
            if run_git(current.root, "status", "--porcelain", "-z", timeout=namespace.timeout):
                raise ValueError("worktree clean state changed before Start effects")
            selection = _check_selection(current, views, target)
            if selection != planned_selection:
                raise ValueError("direct selection changed before Start effects")
            _check_private_state(current, namespace.timeout)
            if (
                selection.record is not None
                and selection.handle is not None
                and selection.record.selected_branch == branch
                and current.branch == branch
                and current.head == tip
            ):
                return OperationResult(
                    "work start",
                    "unchanged",
                    StartData(scope_id, True, context.branch, branch, selection.handle.token),
                    0,
                )
            mutation_started = True
            if create_branch:
                run_git(context.root, "branch", branch, tip, timeout=namespace.timeout, mutation=True)
            effects.append(Effect(phase, "succeeded" if create_branch else "unchanged", branch))
            phase = "git.checkout"
            run_git(context.root, "checkout", branch, timeout=namespace.timeout, mutation=True)
            effects.append(Effect(phase, "succeeded", branch))
            after = resolve_context(str(context.root), context.root)
            branch_after = after.branch
            root_handle.verify()
            lock.verify()
            if after.branch != branch or after.head != tip or (target.path / ".meta.json").read_bytes() != metadata:
                raise ValueError("checkout target snapshot changed")
            _check_private_state(after, namespace.timeout)
            phase = "selection.publish"
            record = WorkTarget(
                "specdock.work-target/v1",
                target.id,
                target.github_ref,
                branch,
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                context.clone_identity,
                context.worktree_identity,
            )
            with WorkTargetStore(context.root) as store:
                handle = store.publish(record)
                token = handle.token
            effects.append(Effect(phase, "succeeded", target.id))
        return OperationResult(
            "work start",
            "succeeded",
            StartData(scope_id, True, context.branch, branch_after, token),
            0,
            effects=tuple(effects),
        )
    except (ValueError, OSError, RuntimeError) as error:
        if isinstance(error, GitProcessError):
            code, details, exit_code = "GIT_FAILED", error.details(), 5
            if mutation_started:
                effects.append(Effect(phase, "unknown" if error.uncertain else "failed", branch))
        elif isinstance(error, RemoteIssueError):
            code, details, exit_code = error.code, {}, error.exit_code
        elif isinstance(error, StartLockBusy):
            code, details, exit_code = "START_LOCK_BUSY", {}, 3
        elif isinstance(error, StartPrecondition):
            code, details, exit_code = error.code, {}, 3
        else:
            code, details, exit_code = "PRECONDITION_FAILED", {}, 3 if isinstance(error, ValueError) else 5
        if mutation_started:
            attempted = {effect.kind for effect in effects}
            for remaining in ("git.branch.create", "git.checkout", "selection.publish"):
                if remaining not in attempted:
                    effects.append(
                        Effect(remaining, "not_attempted", target.id if remaining == "selection.publish" else branch)
                    )
        partial = any(effect.status in ("succeeded", "unknown") for effect in effects)
        return OperationResult(
            "work start",
            "partial" if partial else "failed",
            StartData(scope_id, False, context.branch, branch_after, token),
            6 if partial else exit_code,
            effects=tuple(effects),
            error=Diagnostic(code, str(error), details),
        )
