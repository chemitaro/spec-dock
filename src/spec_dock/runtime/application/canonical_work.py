"""Canonical-mode `work start` and `work finish` (iss-00432; Epic design ch. 3, 5 and 6).

Start follows the legacy flow (`work_start.start_work`) with canonical inputs: the Scope comes from the GitHub
structure checked at decision freshness, the base commit must not track `spec-dock/initiatives`, and readiness
is I-4's `evaluate_readiness`. After the selection is recorded and the Start lock released, the checkout's
catalog link and `spec-dock/active` links are aligned and the in-progress mark is added; none of those follow-ups
changes the result. The legacy module stays unchanged (AC-15); its private helpers are reused, not copied.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import secrets
from typing import TYPE_CHECKING, Literal

from spec_dock.runtime.application.active_links import sync_selection_links
from spec_dock.runtime.application.canonical_branches import refuse_specs_at
from spec_dock.runtime.application.canonical_catalog import require_linked
from spec_dock.runtime.application.canonical_errors import CanonicalCommandError
from spec_dock.runtime.application.canonical_link import link_after_command
from spec_dock.runtime.application.canonical_scopes import build_canonical_scopes
from spec_dock.runtime.application.canonical_writes import WriteFailed, open_write_session
from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.application.start_plan import (
    StartLiveObservations,
    StartLocalSnapshot,
    StartPlanError,
    StartRequest,
    check_branch_occupancy,
    check_expectations,
    check_inventory,
    plan_start,
)
from spec_dock.runtime.application.start_selection import StartSelectionError
from spec_dock.runtime.application.start_snapshot import StartSnapshotError
from spec_dock.runtime.application.work_start import (
    StartData,
    StartGitFailure,
    StartPrecondition,
    _check_private_state,
    _resolve_bound_context,
    _verify_inventory,
)
from spec_dock.runtime.application.worktree_observation import (
    SelectionObservation,
    WorktreeSelection,
    read_selection,
)
from spec_dock.runtime.domain.canonical_content import FORMAT_FILE
from spec_dock.runtime.domain.canonical_layout import CANONICAL_BRANCH
from spec_dock.runtime.domain.canonical_readiness import evaluate_readiness
from spec_dock.runtime.domain.canonical_structure import IN_PROGRESS_LABEL, UpsertIssue
from spec_dock.runtime.domain.dependency_vnext import ReadinessResult
from spec_dock.runtime.domain.git_ref import parse_commit_oid
from spec_dock.runtime.domain.work_target import WorkTarget
from spec_dock.runtime.infra.git_cli import worktree_list
from spec_dock.runtime.infra.git_process import GitProcessError, run_git
from spec_dock.runtime.infra.github_structure import GithubStructureError
from spec_dock.runtime.infra.identity import DirectoryIdentity
from spec_dock.runtime.infra.json_store import require_directory_publication_support
from spec_dock.runtime.infra.start_lock import StartLock, StartLockBusy
from spec_dock.runtime.infra.work_target_store import (
    SelectionPublicationUnknown,
    SelectionRemovalUnknown,
    StoredSelection,
    WorkTargetStore,
)
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.canonical_writes import WriteSession
    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.scope_query import ScopeView
    from spec_dock.runtime.domain.canonical_readiness import ScopeReadiness
    from spec_dock.runtime.infra.identity import PhysicalIdentity
    from spec_dock.runtime.presentation.envelope import ResultStatus

SCOPE_IN_PROGRESS = "SCOPE_IN_PROGRESS"
CANONICAL_PROGRESS_MARK_FAILED = "CANONICAL_PROGRESS_MARK_FAILED"
READINESS_NOT_SATISFIED = "READINESS_NOT_SATISFIED"
IN_PROGRESS_NEXT_STEP = (
    "Ask the user whether this Scope is being worked on from another PC; if the mark is stale, run "
    "spec-dock work finish there or remove the spec-dock:in-progress label on GitHub."
)
MARK_START_NEXT_STEP = (
    "Add the spec-dock:in-progress label and yourself as assignee on the GitHub Issue; work can go on without them."
)


class ReadinessRefused(StartPrecondition):
    """The Scope is not ready; the details carry the state, the blockers and the unknown reasons."""

    def __init__(self, readiness: ScopeReadiness) -> None:
        blocked = ", ".join(item.scope_id or f"#{item.number}" for item in readiness.blockers)
        unknown = ", ".join(item.code for item in readiness.unknown)
        super().__init__(
            READINESS_NOT_SATISFIED,
            f"{readiness.scope_id} is {readiness.state}; blockers: {blocked or 'none'}; unknown: {unknown or 'none'}",
        )
        self.details: dict[str, object] = {
            "state": readiness.state,
            "blockers": [
                {
                    "number": item.number,
                    "scope_id": item.scope_id,
                    "role": item.role,
                    "required_state": item.required_state,
                    "observed_state": item.observed_state,
                }
                for item in readiness.blockers
            ],
            "unknown": [
                {"number": item.number, "scope_id": item.scope_id, "code": item.code, "message": item.message}
                for item in readiness.unknown
            ],
        }


def canonical_worktree_rows(
    context: ProjectContext, views: tuple[ScopeView, ...], *, timeout: float
) -> tuple[WorktreeSelection, ...]:
    """The legacy `observe_worktrees` rows, with every selection read against the canonical Scope views."""
    seen: set[object] = set()
    rows: list[WorktreeSelection] = []
    for entry in worktree_list(context.root, timeout=timeout):
        direct: StoredSelection | None = None
        identity: PhysicalIdentity | None = None
        try:
            if entry.inventory_error is not None:
                raise ValueError(entry.inventory_error)
            if entry.bare:
                raise ValueError("bare repository is not a working tree")
            if entry.branch == CANONICAL_BRANCH and (entry.path / FORMAT_FILE).is_file():
                continue  # the clone's catalog worktree selects nothing
            other = resolve_context(str(entry.path), context.root, timeout=timeout)
            identity = other.worktree_identity
            if other.clone_identity != context.clone_identity:
                raise ValueError("worktree common directory identity mismatch")
            if other.worktree_identity in seen:
                continue
            seen.add(other.worktree_identity)
            with WorkTargetStore(other.root) as store:
                direct = store.read()
            rows.append(
                WorktreeSelection(str(entry.path), read_selection(other, views, stored=direct), views, identity, entry)
            )
        except (OSError, ValueError, RuntimeError) as error:
            rows.append(
                WorktreeSelection(
                    str(entry.path),
                    SelectionObservation(
                        "unavailable",
                        direct.record if direct else None,
                        direct.handle if direct else None,
                        entry.branch,
                        reason=str(error),
                    ),
                    (),
                    identity,
                    entry,
                    error,
                )
            )
    return tuple(rows)


def _check_selection(
    context: ProjectContext, views: tuple[ScopeView, ...], target: ScopeView, *, timeout: float
) -> tuple[SelectionObservation, tuple[WorktreeSelection, ...]]:
    rows = canonical_worktree_rows(context, views, timeout=timeout)
    check_inventory(context, rows, target)
    return read_selection(context, views), rows


def _mutate_git(
    context: ProjectContext,
    root_handle: DirectoryIdentity,
    lock: StartLock,
    *,
    phase: str,
    branch: str,
    tip: str,
    timeout: float,
    args: tuple[str, ...],
) -> None:
    """The legacy `_mutate_git` observation after a Git failure, with the canonical base check."""
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
                observed_tip = _branch_tip(context, branch, timeout=timeout)
                if observed_tip == tip:
                    effect_status = "succeeded"
                elif not observed_tip and not error.uncertain:
                    effect_status = "failed"
            elif after.branch == branch and after.head == tip:
                if not run_git(after.root, "status", "--porcelain", "-z", timeout=timeout):
                    effect_status = "succeeded"
            elif after.branch == context.branch and after.head == context.head and not error.uncertain:
                if not run_git(after.root, "status", "--porcelain", "-z", timeout=timeout):
                    effect_status = "failed"
        except (OSError, ValueError, RuntimeError):
            pass
        raise StartGitFailure(error, observed_branch, effect_status) from error


def _branch_tip(context: ProjectContext, branch: str, *, timeout: float) -> str:
    return (
        run_git(
            context.root, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}", timeout=timeout, missing_ok=True
        )
        .decode()
        .removesuffix("\n")
    )


def start_work(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[StartData]:
    effects: list[Effect] = []
    warnings: list[Diagnostic] = []
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
        session = open_write_session(context, namespace, link=False)
        selection_now = session.selection()
        target = session.resolve(namespace.target, selection_now)
        scope_id = target.id
        session.require_kind_unchanged(*session.scopes.lineage(target.id))
        expected_current = (
            session.resolve(namespace.expect_current, selection_now).id if namespace.expect_current else None
        )
        # The change check can miss a dependency added on GitHub: the chain's blocked-by lists are read again too.
        for member in session.scopes.lineage(target.id):
            session.reread_blockers(session.node(member).number)
        session.reread([session.node(target.id).number, *_external_blockers(session, target.id)])
        target = session.scopes.view(target.id)
        readiness = evaluate_readiness(session.scopes.snapshot, target.id)
        if not readiness.ready:
            raise ReadinessRefused(readiness)
        if readiness.in_progress:
            node = session.node(target.id)
            warnings.append(
                Diagnostic(
                    SCOPE_IN_PROGRESS,
                    f"{target.id} already carries {IN_PROGRESS_LABEL}; another PC may be working on it",
                    {
                        "scope_id": target.id,
                        "number": node.number,
                        "assignees": list(node.assignees),
                        "labeled_at": None,
                        "next_step": IN_PROGRESS_NEXT_STEP,
                    },
                )
            )
        views = session.scopes.views
        check_expectations(target, read_selection(context, views), expected_current, namespace.expect_backend)
        branch = namespace.branch or target.id
        if not branch.isascii():
            raise StartPrecondition("INVALID_BRANCH", "branch name must be ASCII")
        checked_branch = run_git(context.root, "check-ref-format", "--branch", branch, timeout=namespace.timeout)
        if checked_branch != (branch + "\n").encode("ascii"):
            raise StartPrecondition("INVALID_BRANCH", "branch must name a literal branch, not checkout shorthand")
        existing = _branch_tip(context, branch, timeout=namespace.timeout)
        create_branch = not existing
        if not create_branch:
            if not namespace.branch:
                raise ValueError(f"existing branch requires explicit --branch {branch}")
            if namespace.base:
                raise ValueError("existing branch reuse does not accept --base")
            tip = parse_commit_oid(existing.encode("ascii"))
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
        refuse_specs_at(context, tip, timeout=namespace.timeout)
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
        snapshot = StartLocalSnapshot(target, (), planned_selection, planned_inventory)
        observed = StartLiveObservations(branch, tip, create_branch, ReadinessResult(target.id, True, (), False))
        plan = plan_start(request, context, snapshot, observed)
        branch, tip, create_branch = plan.branch, plan.resolved_tip, plan.create_branch
        selection_plan = plan.selection
        if selection_plan.action != "unchanged":
            require_directory_publication_support()
        if selection_plan.action in ("replace_same_scope", "switch_scope"):
            assert planned_selection.record is not None
            old_scope_id = planned_selection.record.scope_id
        if namespace.dry_run:
            planned_effects = [
                Effect("git.branch.create", "planned", branch),
                Effect("git.checkout", "planned", branch),
            ]
            if old_scope_id is not None:
                planned_effects.append(Effect("selection.clear", "planned", old_scope_id))
            planned_effects.append(Effect("selection.publish", "planned", target.id))
            return OperationResult(
                "work start",
                "planned",
                StartData(scope_id, False, context.branch, branch, None),
                0,
                effects=tuple(planned_effects),
                warnings=(*session.warnings, *warnings),
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
            if current.head != context.head or current.branch != context.branch:
                raise ValueError("Start snapshot changed")
            if run_git(current.root, "status", "--porcelain", "-z", timeout=namespace.timeout):
                raise ValueError("worktree clean state changed before Start effects")
            selection, locked_inventory = _check_selection(current, views, target, timeout=namespace.timeout)
            _verify_inventory(current, planned_inventory, locked_inventory, refresh_other=True)
            check_branch_occupancy(current, locked_inventory, branch)
            check_expectations(target, selection, expected_current, namespace.expect_backend)
            if selection != planned_selection:
                raise ValueError("direct selection changed before Start effects")
            _check_private_state(current, namespace.timeout, proposed_token)
            fresh_plan = plan_start(
                request, current, replace(snapshot, selection=selection, inventory=locked_inventory), observed
            )
            if fresh_plan != plan:
                raise ValueError("Start plan changed before effects")
            current_tip = _branch_tip(current, branch, timeout=namespace.timeout)
            if (create_branch and current_tip) or (not create_branch and current_tip != tip):
                raise StartPrecondition("BRANCH_CHANGED", "branch presence or tip changed before Start effects")
            if selection_plan.action == "unchanged":
                assert selection.handle is not None
                token = selection.handle.token
            else:
                mutation_started = True
                if create_branch:
                    _mutate_git(
                        current,
                        root_handle,
                        lock,
                        phase=phase,
                        branch=branch,
                        tip=tip,
                        timeout=namespace.timeout,
                        args=("branch", branch, tip),
                    )
                effects.append(Effect(phase, "succeeded" if create_branch else "unchanged", branch))
                root_handle.verify()
                lock.verify()
                if _branch_tip(current, branch, timeout=namespace.timeout) != tip:
                    raise StartPrecondition("BRANCH_CHANGED", "created or reused branch differs from fixed commit")
                phase = "git.checkout"
                if current.branch == branch and current.head == tip:
                    effects.append(Effect(phase, "unchanged", branch))
                else:
                    _mutate_git(
                        current,
                        root_handle,
                        lock,
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
                if run_git(after.root, "status", "--porcelain", "-z", timeout=namespace.timeout):
                    raise StartPrecondition("WORKTREE_CHANGED", "worktree is no longer clean after checkout")
                _check_private_state(after, namespace.timeout, proposed_token)
                _, checkout_inventory = _check_selection(after, views, target, timeout=namespace.timeout)
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
                    _, publish_inventory = _check_selection(after, views, target, timeout=namespace.timeout)
                    _verify_inventory(after, checkout_inventory, publish_inventory)
                    if run_git(after.root, "status", "--porcelain", "-z", timeout=namespace.timeout):
                        raise StartPrecondition(
                            "WORKTREE_CHANGED", "worktree is no longer clean before selection change"
                        )
                    if selection.handle is not None and selection.record is not None:
                        phase = "selection.clear"
                        removed = store.remove_observed(selection.handle)
                        effects.append(
                            Effect(
                                phase,
                                "succeeded"
                                if removed == "removed"
                                else "unchanged"
                                if removed == "already_absent"
                                else "failed",
                                selection.record.scope_id,
                            )
                        )
                        if removed == "conflict":
                            raise StartPrecondition(
                                "SELECTION_CHANGED", "captured direct target changed before replacement"
                            )
                        root_handle.verify()
                        lock.verify()
                        latest = _resolve_bound_context(context, root_handle, lock, timeout=namespace.timeout)
                        if latest.branch != branch or latest.head != tip:
                            raise StartPrecondition("BRANCH_CHANGED", "checkout changed before publication")
                        if run_git(latest.root, "status", "--porcelain", "-z", timeout=namespace.timeout):
                            raise StartPrecondition(
                                "WORKTREE_CHANGED", "worktree is no longer clean before publication"
                            )
                        _check_private_state(latest, namespace.timeout, proposed_token)
                        _, cleared_inventory = _check_selection(latest, views, target, timeout=namespace.timeout)
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
        # Outside the Start lock: the follow-ups never change the selection result (Epic design ch. 3).
        _follow_up_links(session, context, target.id, effects, warnings, timeout=namespace.timeout)
        _mark_in_progress(session, target.id, effects, warnings)
        status: ResultStatus = "succeeded" if any(effect.status == "succeeded" for effect in effects) else "unchanged"
        return OperationResult(
            "work start",
            status,
            StartData(scope_id, True, context.branch, branch_after, token),
            0,
            effects=tuple(effects),
            warnings=(*session.warnings, *warnings),
        )
    except (ValueError, OSError, RuntimeError, LookupError, GithubStructureError) as error:
        if isinstance(error, (CanonicalCommandError, GithubStructureError, LookupError)) and not mutation_started:
            raise  # dispatch renders a canonical stop or a GitHub failure before any write
        if isinstance(error, SelectionPublicationUnknown):
            code, details, exit_code = "SELECTION_PUBLICATION_UNKNOWN", {}, 6
            token = None
            effects.append(Effect("selection.publish", "unknown", scope_id))
        elif isinstance(error, SelectionRemovalUnknown):
            code, details, exit_code = "SELECTION_REMOVAL_UNKNOWN", {}, 6
            effects.append(Effect("selection.clear", "unknown", old_scope_id))
        elif isinstance(error, GitProcessError):
            code, details, exit_code = "GIT_FAILED", error.details(), 5
            if isinstance(error, StartGitFailure):
                branch_after = error.branch_after
                effects.append(Effect(phase, error.effect_status, branch))
        elif isinstance(error, StartLockBusy):
            code, details, exit_code = "START_LOCK_BUSY", {}, 3
        elif isinstance(error, ReadinessRefused):
            code, details, exit_code = error.code, error.details, 3
        elif isinstance(error, (StartPrecondition, StartPlanError, StartSelectionError, StartSnapshotError)):
            code, details, exit_code = error.code, {}, 3
        elif isinstance(error, LookupError):
            code, details, exit_code = "SCOPE_NOT_FOUND", {}, 4
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
            warnings=tuple(warnings),
            error=Diagnostic(code, str(error), details),
            recovery=RecoveryInstructions((
                "現在のbranch/HEAD、branch show、active showで現物を確認してください。",
                "原因を修正後、branchが存在すれば--branchを明示して新しいwork startを実行してください。--baseは付けません。",
                "選択がinvalid/unknownならworkspace doctorで確認してください。記録やGit効果は自動で巻き戻しません。",
            ))
            if partial
            else None,
        )


def _external_blockers(session: WriteSession, scope_id: str) -> tuple[int, ...]:
    """Non-Scope Issues the target and its ancestors are blocked by; readiness reads them again (Epic ch. 2)."""
    snapshot = session.scopes.snapshot
    numbers: list[int] = []
    for current in session.scopes.lineage(scope_id):
        for blocker in session.node(current).blocked_by:
            if blocker not in snapshot.issues:
                numbers.append(blocker)
    return tuple(dict.fromkeys(numbers))


def _follow_up_links(
    session: WriteSession,
    context: ProjectContext,
    scope_id: str,
    effects: list[Effect],
    warnings: list[Diagnostic],
    *,
    timeout: float,
) -> None:
    """The checkout's catalog link (R-B4), then spec-dock/active when that link is correct."""
    follow = link_after_command(context.root, timeout=timeout)
    effects.extend(follow.effects)
    warnings.extend(follow.warnings)
    try:
        linked = require_linked(context, timeout=timeout)
    except (CanonicalCommandError, GitProcessError, OSError) as error:
        step = "Run spec-dock canonical link, then spec-dock active set " + scope_id + "."
        warnings.append(
            Diagnostic(
                "ACTIVE_LINK_NOT_UPDATED",
                f"spec-dock/active was not aligned because the catalog link is not correct: {error}",
                {"scope_id": scope_id, "next_step": step},
            )
        )
        return
    scopes = build_canonical_scopes(context, session.repository, session.scopes.fresh, linked)
    link_effects, link_warnings = sync_selection_links(context, scopes.views, scope_id, dry_run=False, timeout=timeout)
    effects.extend(link_effects)
    warnings.extend(link_warnings)


def _mark_in_progress(session: WriteSession, scope_id: str, effects: list[Effect], warnings: list[Diagnostic]) -> None:
    """Label and assignee; a failure is a warning only, and only confirmed writes become effects."""
    node = session.node(scope_id)
    before = len(session.effects)
    try:
        session.ensure_labels([IN_PROGRESS_LABEL])
        if IN_PROGRESS_LABEL not in node.labels:
            facts = session.known_facts(node.number)
            labels = session.write(
                "github.issue.label",
                scope_id,
                lambda: session.client.add_labels(node.number, [IN_PROGRESS_LABEL]),
            )
            session.reflect([UpsertIssue(replace(facts, labels=tuple(labels)))])
        login = session.client.current_login()
        if login not in node.assignees:
            session.write(
                "github.issue.assignee",
                scope_id,
                lambda: session.client.add_assignees(node.number, [login]),
            )
    except (WriteFailed, GithubStructureError) as error:
        written = session.effects[before:]
        effects.extend(effect for effect in written if effect.status == "succeeded")
        warnings.append(
            Diagnostic(
                CANONICAL_PROGRESS_MARK_FAILED,
                f"the in-progress mark of {scope_id} was not completed: {error}",
                {
                    "scope_id": scope_id,
                    "writes": [
                        {"kind": effect.kind, "status": effect.status}
                        for effect in written
                        if effect.status != "succeeded"
                    ],
                    "next_step": MARK_START_NEXT_STEP,
                },
            )
        )
        return
    effects.extend(session.effects[before:])
