"""Start alone holds clone exclusion through checkout and direct publication."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import json
import secrets
from typing import TYPE_CHECKING, Literal

from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.application.scope_query import load_scope_views
from spec_dock.runtime.application.start_plan import (
    StartLiveObservations,
    StartLocalSnapshot,
    StartPlanError,
    StartRequest,
    check_branch_occupancy as _check_branch_occupancy,
    check_expectations as _check_expectations,
    check_inventory,
    plan_start,
)
from spec_dock.runtime.application.start_selection import StartSelectionError
from spec_dock.runtime.application.start_snapshot import (
    StartSnapshotError,
    capture_local_inputs,
    observe_readiness,
    read_candidate,
    verify_candidate,
    verify_local_inputs,
)
from spec_dock.runtime.application.worktree_observation import (
    observe_worktrees,
    read_selection,
    resolve_scope,
)
from spec_dock.runtime.domain.git_ref import parse_commit_oid
from spec_dock.runtime.domain.work_target import WorkTarget
from spec_dock.runtime.infra.git_process import GitProcessError, run_git
from spec_dock.runtime.infra.github_lifecycle import RemoteIssueError
from spec_dock.runtime.infra.identity import DirectoryIdentity
from spec_dock.runtime.infra.start_lock import StartLock, StartLockBusy
from spec_dock.runtime.infra.work_target_store import (
    SelectionPublicationUnknown,
    SelectionRemovalUnknown,
    WorkTargetStore,
)
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.scope_query import ScopeView
    from spec_dock.runtime.application.start_snapshot import CandidateSnapshot, LocalInput
    from spec_dock.runtime.application.worktree_observation import SelectionObservation, WorktreeSelection


class StartPrecondition(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class StartGitFailure(GitProcessError):
    def __init__(
        self,
        error: GitProcessError,
        branch_after: str | None,
        effect_status: Literal["succeeded", "failed", "unknown"],
    ) -> None:
        super().__init__(
            error.argv,
            error.stderr,
            error.returncode,
            uncertain=error.uncertain,
            stdout=error.stdout,
            timed_out=error.timed_out,
        )
        self.branch_after = branch_after
        self.effect_status = effect_status


def _resolve_bound_context(
    context: ProjectContext, root_handle: DirectoryIdentity, lock: StartLock, *, timeout: float
) -> ProjectContext:
    root_handle.verify()
    lock.verify()
    fresh = resolve_context(str(context.root), context.root, timeout=timeout)
    root_handle.verify()
    lock.verify()
    if fresh.worktree_identity != root_handle.identity or fresh.clone_identity != lock.identity:
        raise StartPrecondition("PROJECT_IDENTITY_CHANGED", "fresh Git context differs from held root/common identity")
    return fresh


def _mutate_git(
    context: ProjectContext,
    root_handle: DirectoryIdentity,
    lock: StartLock,
    candidate: CandidateSnapshot,
    source_inputs: tuple[LocalInput, ...],
    *,
    phase: str,
    branch: str,
    tip: str,
    timeout: float,
    args: tuple[str, ...],
) -> None:
    _resolve_bound_context(context, root_handle, lock, timeout=timeout)
    try:
        run_git(context.root, *args, timeout=timeout, mutation=True)
    except GitProcessError as error:
        observed_branch: str | None = None
        effect_status: Literal["succeeded", "failed", "unknown"] = "unknown"
        try:
            root_handle.verify()
            lock.verify()
            after = _resolve_bound_context(context, root_handle, lock, timeout=timeout)
            observed_branch = after.branch
            if phase == "git.branch.create":
                observed_tip = (
                    run_git(
                        context.root,
                        "rev-parse",
                        "--verify",
                        "--quiet",
                        f"refs/heads/{branch}",
                        timeout=timeout,
                        missing_ok=True,
                    )
                    .decode()
                    .removesuffix("\n")
                )
                if observed_tip == tip:
                    effect_status = "succeeded"
                elif not observed_tip and not error.uncertain:
                    effect_status = "failed"
            elif after.branch == branch and after.head == tip:
                verify_candidate(after, candidate)
                if not run_git(after.root, "status", "--porcelain", "-z", timeout=timeout):
                    effect_status = "succeeded"
            elif after.branch == context.branch and after.head == context.head and not error.uncertain:
                verify_local_inputs(after, source_inputs)
                if not run_git(after.root, "status", "--porcelain", "-z", timeout=timeout):
                    effect_status = "failed"
        except (OSError, ValueError, RuntimeError):
            pass
        raise StartGitFailure(error, observed_branch, effect_status) from error


def _check_selection(
    context: ProjectContext, views: tuple[ScopeView, ...], target: ScopeView, *, timeout: float
) -> tuple[SelectionObservation, tuple[WorktreeSelection, ...]]:
    rows = observe_worktrees(context, timeout=timeout)
    check_inventory(context, rows, target)
    return read_selection(context, views), rows


def _verify_inventory(
    context: ProjectContext,
    before: tuple[WorktreeSelection, ...],
    after: tuple[WorktreeSelection, ...],
    *,
    checkout: bool = False,
    cleared: bool = False,
    refresh_other: bool = False,
) -> None:
    old = {row.path: row for row in before}
    current = {row.path: row for row in after}
    if old.keys() != current.keys():
        raise StartPrecondition("WORKTREE_INVENTORY_CHANGED", "Git worktree inventory changed during Start")
    for path, row in current.items():
        expected = old[path]
        if refresh_other and row.worktree_identity != context.worktree_identity:
            row = replace(
                row,
                git=replace(
                    row.git, head=expected.git.head, branch=expected.git.branch, detached=expected.git.detached
                ),
                selection=expected.selection,
                views=expected.views,
                error=expected.error,
            )
        if checkout and row.worktree_identity == context.worktree_identity:
            if row.selection.record != expected.selection.record or row.selection.handle != expected.selection.handle:
                raise StartPrecondition("SELECTION_CHANGED", "captured direct target changed during checkout")
            row = replace(
                row,
                git=replace(
                    row.git, head=expected.git.head, branch=expected.git.branch, detached=expected.git.detached
                ),
                selection=expected.selection,
                views=expected.views,
            )
        if cleared and row.worktree_identity == context.worktree_identity:
            if row.selection.status != "empty" or row.selection.record is not None or row.selection.handle is not None:
                raise StartPrecondition("SELECTION_CHANGED", "direct target appeared after captured target removal")
            row = replace(row, selection=expected.selection, views=expected.views)
        if row != expected:
            raise StartPrecondition("WORKTREE_INVENTORY_CHANGED", "Git worktree or direct target changed during Start")


def _check_private_state(context: ProjectContext, timeout: float, proposed_token: str) -> None:
    if run_git(context.root, "ls-files", "-z", "--", "spec-dock/.agent/work-target", timeout=timeout):
        raise ValueError("work target state must not be tracked by Git")
    for basename in (f"target-{proposed_token}.json", f".stage-{proposed_token}"):
        if not run_git(
            context.root,
            "check-ignore",
            "--no-index",
            "--",
            f"spec-dock/.agent/work-target/{basename}",
            timeout=timeout,
            missing_ok=True,
        ):
            raise StartPrecondition("WORK_TARGET_PATH_NOT_IGNORED", "work target state must be ignored by Git")


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
    old_scope_id: str | None = None
    details: dict[str, object]
    try:
        context.require_writer()
        if context.head is not None:
            parse_commit_oid(context.head.encode("ascii"))
        proposed_token = secrets.token_hex(16)
        _check_private_state(context, namespace.timeout, proposed_token)
        views = load_scope_views(context.root / "spec-dock")
        local_inputs = capture_local_inputs(context, views)
        target = resolve_scope(context, views, namespace.target)
        scope_id = target.id
        expected_current = (
            resolve_scope(context, views, namespace.expect_current).id if namespace.expect_current else None
        )
        _check_expectations(target, read_selection(context, views), expected_current, namespace.expect_backend)
        metadata = (target.path / ".meta.json").read_bytes()
        slug = json.loads(metadata)["slug"]
        branch = namespace.branch or f"{target.id}-{slug}"
        if not branch.isascii():
            raise StartPrecondition("INVALID_BRANCH", "branch name must be ASCII")
        checked_branch = run_git(context.root, "check-ref-format", "--branch", branch, timeout=namespace.timeout)
        if checked_branch != (branch + "\n").encode("ascii"):
            raise StartPrecondition("INVALID_BRANCH", "branch must name a literal branch, not checkout shorthand")
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
            tip = parse_commit_oid(existing)
        else:
            if not namespace.base:
                raise ValueError("a new branch requires --base")
            tip = parse_commit_oid(
                run_git(
                    context.root,
                    "rev-parse",
                    "--verify",
                    "--end-of-options",
                    f"{namespace.base}^{{commit}}",
                    timeout=namespace.timeout,
                )
            )
        if context.head is not None and len(tip) != len(context.head):
            raise ValueError("resolved commit OID differs from the repository object format")
        candidate = read_candidate(
            context, tip, target, views, timeout=namespace.timeout, proposed_token=proposed_token
        )
        readiness = observe_readiness(
            context, candidate, target.id, timeout=namespace.timeout, offline=namespace.offline
        )
        if run_git(context.root, "status", "--porcelain", "-z", timeout=namespace.timeout):
            raise ValueError("worktree must be clean before Start")
        planned_selection, planned_inventory = _check_selection(context, views, target, timeout=namespace.timeout)
        request = StartRequest(
            target.id,
            namespace.branch,
            namespace.base,
            namespace.switch_active,
            expected_current,
            namespace.expect_backend,
        )
        snapshot = StartLocalSnapshot(target, local_inputs, planned_selection, planned_inventory)
        observed = StartLiveObservations(branch, tip, create_branch, readiness)
        plan = plan_start(request, context, snapshot, observed)
        branch, tip, create_branch = plan.branch, plan.resolved_tip, plan.create_branch
        selection_plan = plan.selection
        if selection_plan.action in ("replace_same_scope", "switch_scope"):
            assert planned_selection.record is not None
            old_scope_id = planned_selection.record.scope_id
        if namespace.dry_run:
            if selection_plan.action == "unchanged":
                verify_candidate(context, candidate)
            planned_effects = [
                Effect("git.branch.create", "planned", branch),
                Effect("git.checkout", "planned", branch),
            ]
            if selection_plan.action in ("replace_same_scope", "switch_scope"):
                assert planned_selection.record is not None
                planned_effects.append(Effect("selection.clear", "planned", planned_selection.record.scope_id))
            planned_effects.append(Effect("selection.publish", "planned", target.id))
            return OperationResult(
                "work start",
                "planned",
                StartData(scope_id, False, context.branch, branch, None),
                0,
                effects=tuple(planned_effects),
            )
        with (
            DirectoryIdentity(context.root) as root_handle,
            StartLock(context.common_dir, timeout=namespace.lock_timeout) as lock,
        ):
            root_handle.verify()
            lock.verify()
            if root_handle.identity != context.worktree_identity or lock.identity != context.clone_identity:
                raise ValueError("project physical identity changed")
            current = _resolve_bound_context(context, root_handle, lock, timeout=namespace.timeout)
            verify_local_inputs(current, local_inputs)
            if (
                current.head != context.head
                or current.branch != context.branch
                or (target.path / ".meta.json").read_bytes() != metadata
            ):
                raise ValueError("Start snapshot changed")
            if run_git(current.root, "status", "--porcelain", "-z", timeout=namespace.timeout):
                raise ValueError("worktree clean state changed before Start effects")
            selection, locked_inventory = _check_selection(current, views, target, timeout=namespace.timeout)
            _verify_inventory(current, planned_inventory, locked_inventory, refresh_other=True)
            _check_branch_occupancy(current, locked_inventory, branch)
            _check_expectations(target, selection, expected_current, namespace.expect_backend)
            if selection != planned_selection:
                raise ValueError("direct selection changed before Start effects")
            _check_private_state(current, namespace.timeout, proposed_token)
            fresh_plan = plan_start(
                request, current, replace(snapshot, selection=selection, inventory=locked_inventory), observed
            )
            if fresh_plan != plan:
                raise ValueError("Start plan changed before effects")
            current_tip = (
                run_git(
                    current.root,
                    "rev-parse",
                    "--verify",
                    "--quiet",
                    f"refs/heads/{branch}",
                    timeout=namespace.timeout,
                    missing_ok=True,
                )
                .decode()
                .removesuffix("\n")
            )
            if (create_branch and current_tip) or (not create_branch and current_tip != tip):
                raise StartPrecondition("BRANCH_CHANGED", "branch presence or tip changed before Start effects")
            if selection_plan.action == "unchanged":
                verify_candidate(current, candidate)
                assert selection.handle is not None
                return OperationResult(
                    "work start",
                    "unchanged",
                    StartData(scope_id, True, context.branch, branch, selection.handle.token),
                    0,
                )
            mutation_started = True
            if create_branch:
                _mutate_git(
                    current,
                    root_handle,
                    lock,
                    candidate,
                    local_inputs,
                    phase=phase,
                    branch=branch,
                    tip=tip,
                    timeout=namespace.timeout,
                    args=("branch", branch, tip),
                )
            effects.append(Effect(phase, "succeeded" if create_branch else "unchanged", branch))
            root_handle.verify()
            lock.verify()
            confirmed_tip = parse_commit_oid(
                run_git(
                    current.root, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}", timeout=namespace.timeout
                )
            )
            if confirmed_tip != tip:
                raise StartPrecondition("BRANCH_CHANGED", "created or reused branch differs from fixed commit")
            phase = "git.checkout"
            _mutate_git(
                current,
                root_handle,
                lock,
                candidate,
                local_inputs,
                phase=phase,
                branch=branch,
                tip=tip,
                timeout=namespace.timeout,
                args=("checkout", branch),
            )
            effects.append(Effect(phase, "succeeded", branch))
            after = _resolve_bound_context(context, root_handle, lock, timeout=namespace.timeout)
            branch_after = after.branch
            root_handle.verify()
            lock.verify()
            if after.branch != branch or after.head != tip:
                raise ValueError("checkout target snapshot changed")
            verify_candidate(after, candidate)
            _check_private_state(after, namespace.timeout, proposed_token)
            _, checkout_inventory = _check_selection(after, candidate.views, target, timeout=namespace.timeout)
            _verify_inventory(after, locked_inventory, checkout_inventory, checkout=True)
            record = WorkTarget(
                "specdock.work-target/v1",
                target.id,
                target.github_ref,
                branch,
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                context.clone_identity,
                context.worktree_identity,
            )
            with WorkTargetStore(context.root, root_handle=root_handle) as store:
                root_handle.verify()
                lock.verify()
                _, publish_inventory = _check_selection(after, candidate.views, target, timeout=namespace.timeout)
                _verify_inventory(after, checkout_inventory, publish_inventory)
                if selection.handle is not None and selection.record is not None:
                    phase = "selection.clear"
                    removed = store.remove_observed(selection.handle)
                    effects.append(
                        Effect(phase, "succeeded" if removed == "removed" else "failed", selection.record.scope_id)
                    )
                    if removed != "removed":
                        raise StartPrecondition(
                            "SELECTION_CHANGED", "captured direct target changed before replacement"
                        )
                    root_handle.verify()
                    lock.verify()
                    latest = _resolve_bound_context(context, root_handle, lock, timeout=namespace.timeout)
                    if latest.branch != branch or latest.head != tip:
                        raise StartPrecondition("BRANCH_CHANGED", "checkout changed before publication")
                    verify_candidate(latest, candidate)
                    _check_private_state(latest, namespace.timeout, proposed_token)
                    _, cleared_inventory = _check_selection(latest, candidate.views, target, timeout=namespace.timeout)
                    _verify_inventory(latest, publish_inventory, cleared_inventory, cleared=True)
                phase = "selection.publish"
                handle = store.publish(record, token=proposed_token)
                token = handle.token
                try:
                    root_handle.verify()
                    lock.verify()
                except (OSError, ValueError) as error:
                    raise SelectionPublicationUnknown(token, error) from error
                effects.append(Effect(phase, "succeeded", target.id))
        return OperationResult(
            "work start",
            "succeeded",
            StartData(scope_id, True, context.branch, branch_after, token),
            0,
            effects=tuple(effects),
        )
    except (ValueError, OSError, RuntimeError) as error:
        if isinstance(error, SelectionPublicationUnknown):
            code, details, exit_code = "SELECTION_PUBLICATION_UNKNOWN", {}, 6
            token = error.token
            effects.append(Effect("selection.publish", "unknown", scope_id))
        elif isinstance(error, SelectionRemovalUnknown):
            code, details, exit_code = "SELECTION_REMOVAL_UNKNOWN", {}, 6
            effects.append(Effect("selection.clear", "unknown", old_scope_id))
        elif isinstance(error, GitProcessError):
            code, details, exit_code = "GIT_FAILED", error.details(), 5
            if isinstance(error, StartGitFailure):
                branch_after = error.branch_after
                effects.append(Effect(phase, error.effect_status, branch))
        elif isinstance(error, RemoteIssueError):
            code, details, exit_code = error.code, {}, error.exit_code
        elif isinstance(error, StartLockBusy):
            code, details, exit_code = "START_LOCK_BUSY", {}, 3
        elif isinstance(error, (StartPrecondition, StartPlanError, StartSelectionError, StartSnapshotError)):
            code, details, exit_code = error.code, {}, 3
        else:
            code, details, exit_code = "PRECONDITION_FAILED", {}, 3 if isinstance(error, ValueError) else 5
        if mutation_started:
            if phase in ("selection.clear", "selection.publish") and not any(
                effect.kind == phase for effect in effects
            ):
                effects.append(Effect(phase, "failed", old_scope_id if phase == "selection.clear" else scope_id))
            attempted = {effect.kind for effect in effects}
            remaining_effects: tuple[str, ...] = ("git.branch.create", "git.checkout")
            if old_scope_id is not None:
                remaining_effects += ("selection.clear",)
            remaining_effects += ("selection.publish",)
            for remaining in remaining_effects:
                if remaining not in attempted:
                    effect_target = (
                        old_scope_id
                        if remaining == "selection.clear"
                        else scope_id
                        if remaining == "selection.publish"
                        else branch
                    )
                    effects.append(Effect(remaining, "not_attempted", effect_target))
        partial = any(effect.status in ("succeeded", "unknown") for effect in effects)
        return OperationResult(
            "work start",
            "partial" if partial else "failed",
            StartData(scope_id, False, context.branch, branch_after, token),
            6 if partial else exit_code,
            effects=tuple(effects),
            error=Diagnostic(code, str(error), details),
            recovery=RecoveryInstructions((
                "現在のbranch/HEAD、branch show、active showで現物を確認してください。",
                "原因を修正後、branchが存在すれば--branchを明示して新しいwork startを実行してください。--baseは付けません。",
                "選択がinvalid/unknownならworkspace doctorで確認してください。記録やGit効果は自動で巻き戻しません。",
            ))
            if partial
            else None,
        )
