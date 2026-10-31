"""Canonical-mode `work start` and `work finish` (iss-00432; Epic design ch. 3, 5 and 6).

Start follows the legacy flow (`work_start.start_work`) with canonical inputs: the Scope comes from the GitHub
structure checked at decision freshness, the base commit must not track `spec-dock/initiatives`, and readiness
is I-4's `evaluate_readiness`. After the selection is recorded and the Start lock released, the checkout's
catalog link and `spec-dock/active` links are aligned and the in-progress mark is added; none of those follow-ups
changes the result. The legacy module stays unchanged (AC-15); its private helpers are reused, not copied.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import os
import secrets
from typing import TYPE_CHECKING, Literal

from spec_dock.runtime.application.active_links import sync_selection_links
from spec_dock.runtime.application.canonical_branches import refuse_specs_at
from spec_dock.runtime.application.canonical_catalog import catalog_changes, require_linked
from spec_dock.runtime.application.canonical_errors import (
    CANONICAL_SAVE_HELD,
    CANONICAL_SAVE_UNCONFIRMED,
    SAVE_HELD_NEXT_STEPS,
    SAVE_UNCONFIRMED_NEXT_STEP,
    CanonicalCommandError,
)
from spec_dock.runtime.application.canonical_link import link_after_command
from spec_dock.runtime.application.canonical_schedule import request_sync_now
from spec_dock.runtime.application.canonical_scope_check import SCOPE_CHECK_FAILED
from spec_dock.runtime.application.canonical_scopes import build_canonical_scopes
from spec_dock.runtime.application.canonical_writes import (
    CATALOG_LOCK_TIMEOUT,
    WriteFailed,
    check_expectations as check_write_expectations,
    diagnostic_for,
    open_write_session,
)
from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.application.scope_check import check_scope_documents, scope_format
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
from spec_dock.runtime.domain.canonical_layout import CANONICAL_BRANCH, scope_relative
from spec_dock.runtime.domain.canonical_readiness import evaluate_readiness
from spec_dock.runtime.domain.canonical_structure import IN_PROGRESS_LABEL, UpsertIssue, parse_timestamp
from spec_dock.runtime.domain.canonical_sync_state import holds_under
from spec_dock.runtime.domain.dependency_vnext import ReadinessResult
from spec_dock.runtime.domain.git_ref import parse_commit_oid
from spec_dock.runtime.domain.work_target import WorkTarget
from spec_dock.runtime.infra.canonical_git import run_catalog_git
from spec_dock.runtime.infra.canonical_state import StateUnreadable, read_catalog_state
from spec_dock.runtime.infra.git_cli import worktree_list
from spec_dock.runtime.infra.git_process import GitProcessError, run_git
from spec_dock.runtime.infra.github_structure import SYSTEM_CLOCK, GithubStructureError
from spec_dock.runtime.infra.identity import DirectoryIdentity
from spec_dock.runtime.infra.json_store import require_directory_publication_support
from spec_dock.runtime.infra.start_lock import StartLock, StartLockBusy
from spec_dock.runtime.infra.state_root import resolve_state_root
from spec_dock.runtime.infra.work_target_store import (
    SelectionPublicationUnknown,
    SelectionRemovalUnknown,
    StoredSelection,
    WorkTargetStore,
)
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    import argparse
    from pathlib import Path

    from spec_dock.runtime.application.canonical_writes import WriteSession
    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.scope_query import ScopeView
    from spec_dock.runtime.domain.canonical_readiness import ScopeReadiness
    from spec_dock.runtime.domain.canonical_sync_state import CatalogSyncState
    from spec_dock.runtime.infra.github_structure import GithubClock
    from spec_dock.runtime.infra.identity import PhysicalIdentity
    from spec_dock.runtime.infra.work_target_store import SelectionHandle
    from spec_dock.runtime.presentation.envelope import EffectStatus, ResultStatus

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
        chain = session.scopes.lineage(target.id)
        session.require_kind_unchanged(*chain)
        expected_current = (
            session.resolve(namespace.expect_current, selection_now).id if namespace.expect_current else None
        )
        # The change check can miss a dependency added on GitHub: the chain's blocked-by lists are read again too.
        for member in session.scopes.lineage(target.id):
            session.reread_blockers(session.node(member).number)
        session.reread([session.node(target.id).number, *_external_blockers(session, target.id)])
        session.require_kind_unchanged(*chain)  # a kind change only the reread saw
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


# work finish waits for the periodic sync to save and push the Scope's catalog places (Epic design ch. 6).
SAVE_TIMEOUT = 180.0
SAVE_INTERVAL = 2.0
# Tests replace it to reach the timeout without waiting; the cycle's own timestamps stay real time.
SAVE_CLOCK: GithubClock = SYSTEM_CLOCK


@dataclass(frozen=True)
class FinishData:
    scope_id: str
    completed: bool
    branch_before: str | None
    branch_after: str | None
    selection_token: str | None
    kind: str = "work-finish"


class _SaveStopped(Exception):
    """The save could not be confirmed; `error` is what the result reports."""

    def __init__(self, error: CanonicalCommandError) -> None:
        super().__init__(error.message)
        self.error = error


def finish_work(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    """Confirm the Scope's catalog places reached GitHub's canonical, then close it and release the selection."""
    context.require_writer()
    if not namespace.yes and not namespace.dry_run:
        raise ValueError("work finish requires --yes")
    session = open_write_session(context, namespace, link=True)
    assert session.catalog is not None
    catalog = session.catalog.catalog
    captured = session.selection()
    if captured.status in ("invalid", "unavailable"):
        raise ValueError(f"direct selection is {captured.status}: {captured.reason or 'cannot be safely observed'}")
    target = session.resolve(namespace.target, captured)
    check_write_expectations(session, namespace, captured, target)
    observed_state, descendants = _finish_rules(session, target.id)
    check_warnings, refusal = _check_before_finish(context, session, target, observed_state, timeout=namespace.timeout)
    clear_handle = (
        captured.handle
        if captured.status == "selected"
        and captured.record is not None
        and captured.record.scope_id in {target.id, *descendants}
        else None
    )
    places = tuple(scope_relative(scope_id).as_posix() for scope_id in (target.id, *descendants))
    state_root = resolve_state_root()
    _require_saveable(_read_sync_state(state_root, catalog), places)
    reference = target.github_ref
    if namespace.dry_run:
        planned = [Effect("github.issue.close", "planned" if observed_state != "completed" else "unchanged", reference)]
        if clear_handle is not None:
            planned.append(Effect("selection.clear", "planned", clear_handle.token))
        return OperationResult(
            "work finish",
            "planned",
            FinishData(target.id, observed_state == "completed", context.branch, context.branch, None),
            0,
            effects=tuple(planned),
            warnings=(*session.warnings, *check_warnings),
        )
    effects: list[Effect] = []
    warnings: list[Diagnostic] = [*session.warnings, *check_warnings]
    wrote_changeset = False
    try:
        with catalog_changes(catalog, command="work finish", origin="finish", timeout=CATALOG_LOCK_TIMEOUT) as changes:
            for place in sorted(_unsaved_places(catalog, places, timeout=namespace.timeout)):
                if os.path.lexists(catalog / place):
                    changes.add(place)
                else:
                    changes.delete(place)
        if changes.written is not None:
            wrote_changeset = True
            effects.append(Effect("catalog.changeset", "succeeded", changes.written.name))
        _wait_saved(
            state_root,
            catalog,
            places,
            changes.written.name if changes.written is not None else None,
            timeout=namespace.timeout,
        )
        # Confirm again on what GitHub reports now: another PC may have closed it or reopened a child meanwhile.
        session = open_write_session(context, namespace, link=True)
        observed_state, descendants = _finish_rules(session, target.id)
        if refusal is not None and observed_state != "completed":
            raise refusal  # completed at the first read, reopened since: the check's errors stop it again
    except (
        _SaveStopped,
        CanonicalCommandError,
        GithubStructureError,
        ValueError,
        LookupError,
        OSError,
        RuntimeError,
    ) as error:
        stopped = error.error if isinstance(error, _SaveStopped) else error
        if not wrote_changeset:
            raise stopped from error
        effects.append(Effect("github.issue.close", "not_attempted", reference))
        if clear_handle is not None:
            effects.append(Effect("selection.clear", "not_attempted", clear_handle.token))
        diagnostic = diagnostic_for(stopped, "PRECONDITION_FAILED")
        code = diagnostic.code
        recovery = (
            getattr(stopped, "recovery", ())
            if isinstance(stopped, CanonicalCommandError) and code != "SCOPE_KIND_CHANGED"
            else ()
        ) or (f"Run spec-dock work finish {target.id} --yes again once the reason is fixed.",)
        return OperationResult(
            "work finish",
            "partial",
            FinishData(target.id, False, context.branch, context.branch, None),
            6,
            effects=tuple(effects),
            warnings=tuple(warnings),
            error=diagnostic,
            recovery=RecoveryInstructions(tuple(recovery)),
        )
    return _close_and_release(session, context, namespace, target.id, observed_state, clear_handle, effects, warnings)


def _check_before_finish(
    context: ProjectContext, session: WriteSession, target: ScopeView, observed_state: str, *, timeout: float
) -> tuple[tuple[Diagnostic, ...], CanonicalCommandError | None]:
    """The `scope check` of the Scope being closed, before anything is written (R-B7, iss-00473).

    Returns the warnings to show and the refusal that applies while the Scope is open. A Markdown Scope or one
    without a directory is not checked. Errors or an unusable `cue` stop an open Scope here; a Scope GitHub
    already completed only has its selection released, so they become warnings: a type change after closing
    must not keep the selection from being released. The caller applies the refusal again if a later read
    finds the Scope open (another PC reopened it while finish waited for the save).
    """
    directory = session.scopes.directory(target.id)
    if directory is None or scope_format(directory.path) == "markdown":
        return (), None
    completed = observed_state == "completed"
    shown = target.path.relative_to(context.root).as_posix()
    try:
        report = check_scope_documents(
            directory.path, kind=target.kind, shown=shown, repository_root=context.root, timeout=timeout
        )
    except CanonicalCommandError as error:
        if not completed:
            raise
        return (Diagnostic(error.code, error.message, {"scope_id": target.id, **error.details}),), error
    if not report.errors:
        return report.warnings, None
    errors = [{"code": item.code, "message": item.message, "details": dict(item.details)} for item in report.errors]
    first = report.errors[0]
    message = f"{target.id} has {len(report.errors)} spec check error(s); first: [{first.code}] {first.message}"
    refusal = CanonicalCommandError(
        SCOPE_CHECK_FAILED,
        message,
        recovery=(
            f"Fix the errors (each names its file and a hint), confirm with spec-dock scope check {target.id}, "
            f"then run spec-dock work finish {target.id} --yes again.",
        ),
        details={"scope_id": target.id, "errors": errors},
    )
    if not completed:
        raise refusal
    return (Diagnostic(SCOPE_CHECK_FAILED, message, {"scope_id": target.id, "errors": errors}), *report.warnings), (
        refusal
    )


def _finish_rules(session: WriteSession, scope_id: str) -> tuple[str, tuple[str, ...]]:
    """The legacy finish rules on GitHub's state after a reread; descendants come from the GitHub parents."""
    from spec_dock.runtime.application.canonical_scope_change import require_known_descendants

    scopes = session.scopes
    descendants = tuple(view.id for view in scopes.views if scope_id in scopes.lineage(view.id)[1:])
    session.require_kind_unchanged(scope_id, *descendants)
    session.reread([session.node(scope_id).number])
    session.require_kind_unchanged(scope_id, *descendants)  # a kind change only the reread saw
    require_known_descendants(session, scope_id)
    observed = session.scopes.view(scope_id).status.state
    if observed == "unknown":
        raise ValueError("SCOPE_STATUS_UNKNOWN")
    if observed == "not-planned":
        raise ValueError("TERMINAL_REASON_CONFLICT: reopen is required")
    for child in descendants:
        if session.scopes.view(child).status.state != "completed":
            raise ValueError("DESCENDANT_NOT_COMPLETED")
    return observed, descendants


def _read_sync_state(state_root: Path, catalog: Path) -> CatalogSyncState | None:
    try:
        return read_catalog_state(state_root, str(catalog))
    except StateUnreadable as error:
        raise CanonicalCommandError(
            CANONICAL_SAVE_UNCONFIRMED,
            f"the sync state cannot be read: {error}",
            recovery=(SAVE_UNCONFIRMED_NEXT_STEP,),
        ) from error


def _require_saveable(state: CatalogSyncState | None, places: tuple[str, ...]) -> None:
    """Stop on a hold under the Scope (the sync will not save it) or a paused catalog (it saves nothing)."""
    if state is None:
        return  # no cycle has run yet; the wait decides
    holds = [hold for place in places for hold in holds_under(state, place)]
    if holds:
        steps = tuple(dict.fromkeys(SAVE_HELD_NEXT_STEPS.get(hold.kind, SAVE_UNCONFIRMED_NEXT_STEP) for hold in holds))
        raise CanonicalCommandError(
            CANONICAL_SAVE_HELD,
            "the sync holds changes under this Scope: " + ", ".join(f"{hold.path} ({hold.kind})" for hold in holds),
            recovery=steps,
            details={"holds": [hold.to_json() for hold in holds]},
        )
    if state.paused is not None:
        raise CanonicalCommandError(
            CANONICAL_SAVE_UNCONFIRMED,
            f"the catalog sync is paused ({state.paused}); nothing can be saved until it resumes",
            recovery=(SAVE_UNCONFIRMED_NEXT_STEP,),
            details={"paused": state.paused},
        )


def _unsaved_places(catalog: Path, places: tuple[str, ...], *, timeout: float) -> set[str]:
    """The places with uncommitted catalog changes (deletions included), read without writing .git."""
    output = run_catalog_git(
        catalog,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
        "--",
        *(f":(literal){place}" for place in places),  # status has no --pathspec-from-file
        read_only=True,
        timeout=timeout,
    ).stdout
    entries = output.split(b"\0")
    dirty: set[str] = set()
    index = 0
    while index < len(entries):
        entry = entries[index].decode("utf-8", "surrogateescape")
        index += 1
        if len(entry) < 4:
            continue
        if entry[0] in "RC":
            index += 1  # the rename source follows
        path = entry[3:]
        dirty.update(place for place in places if path == place or path.startswith(place + "/"))
    return dirty


def _wait_saved(
    state_root: Path, catalog: Path, places: tuple[str, ...], changeset: str | None, *, timeout: float
) -> None:
    """Ask for a cycle now, then wait until it saved and pushed every place (or stop without closing)."""
    started = datetime.now(timezone.utc).replace(microsecond=0)
    request_sync_now(state_root)
    deadline = SAVE_CLOCK.monotonic() + SAVE_TIMEOUT
    while True:
        try:
            state = _read_sync_state(state_root, catalog)
            _require_saveable(state, places)
        except CanonicalCommandError as error:
            raise _SaveStopped(error) from error
        if state is not None and _saved(state, catalog, places, changeset, started, timeout=timeout):
            return
        if SAVE_CLOCK.monotonic() >= deadline:
            raise _SaveStopped(
                CanonicalCommandError(
                    CANONICAL_SAVE_UNCONFIRMED,
                    f"the save of {', '.join(places)} was not confirmed within {int(SAVE_TIMEOUT)} seconds",
                    recovery=(SAVE_UNCONFIRMED_NEXT_STEP,),
                    details={"places": list(places), "changeset": changeset},
                )
            )
        SAVE_CLOCK.sleep(SAVE_INTERVAL)


def _saved(
    state: CatalogSyncState,
    catalog: Path,
    places: tuple[str, ...],
    changeset: str | None,
    started: datetime,
    *,
    timeout: float,
) -> bool:
    if changeset is not None and changeset not in state.consumed_changesets:
        return False
    if state.last_cycle is None or parse_timestamp(state.last_cycle.started_at) < started:
        return False
    if state.remote_contains_head is not True or state.head is None:
        return False
    head = run_catalog_git(catalog, "rev-parse", "HEAD", read_only=True, timeout=timeout).stdout.decode().strip()
    return head == state.head and not _unsaved_places(catalog, places, timeout=timeout)


def _close_and_release(
    session: WriteSession,
    context: ProjectContext,
    namespace: argparse.Namespace,
    scope_id: str,
    observed_state: str,
    clear_handle: SelectionHandle | None,
    effects: list[Effect],
    warnings: list[Diagnostic],
) -> OperationResult[object]:
    node = session.node(scope_id)
    reference = session.scopes.view(scope_id).github_ref
    completed = observed_state == "completed"
    try:
        if completed:
            effects.append(Effect("github.issue.close", "unchanged", reference))
        else:
            closed = session.write(
                "github.issue.close",
                reference,
                lambda: session.client.update_issue(node.number, state="closed", state_reason="completed"),
                lambda facts: [UpsertIssue(facts)],
            )
            session.facts[node.number] = closed  # later reflections (the label removal) build on the closed Issue
            effects.append(session.effects[-1])
            completed = True
    except WriteFailed as error:
        effects.append(session.effects[-1])
        if clear_handle is not None:
            effects.append(Effect("selection.clear", "not_attempted", clear_handle.token))
        diagnostic = Diagnostic(error.cause.code, error.cause.message, {})
        applied = any(effect.status in ("succeeded", "unknown") for effect in effects)
        return OperationResult(
            "work finish",
            "partial" if applied else "failed",
            FinishData(scope_id, False, context.branch, context.branch, None),
            6 if applied else 5,
            effects=tuple(effects),
            warnings=tuple(warnings),
            error=diagnostic,
            recovery=RecoveryInstructions((
                f"Inspect {reference} on GitHub, then run spec-dock work finish {scope_id} --yes again.",
            )),
        )
    _unmark_in_progress(session, scope_id, effects, warnings)
    token: str | None = None
    if clear_handle is not None:
        try:
            with WorkTargetStore(context.root) as store:
                outcome = store.remove_observed(clear_handle)
        except (SelectionRemovalUnknown, OSError, ValueError, RuntimeError) as error:
            # The Issue is already closed: report it with the selection effect, as the legacy finish does.
            status: EffectStatus = "unknown" if isinstance(error, SelectionRemovalUnknown) else "failed"
            effects.append(Effect("selection.clear", status, clear_handle.token))
            return OperationResult(
                "work finish",
                "partial",
                FinishData(scope_id, True, context.branch, context.branch, None),
                6,
                effects=tuple(effects),
                warnings=tuple(warnings),
                error=Diagnostic("WORK_FINISH_INCOMPLETE", str(error), {}),
                recovery=RecoveryInstructions((
                    "The Scope is completed; check spec-dock active show and clear the selection with "
                    "spec-dock active clear if it remains.",
                )),
            )
        if outcome == "conflict":
            effects.append(Effect("selection.clear", "failed", clear_handle.token))
            return OperationResult(
                "work finish",
                "partial",
                FinishData(scope_id, True, context.branch, context.branch, clear_handle.token),
                6,
                effects=tuple(effects),
                warnings=tuple(warnings),
                error=Diagnostic("WORK_FINISH_INCOMPLETE", "captured selection changed", {}),
            )
        effects.append(
            Effect("selection.clear", "succeeded" if outcome == "removed" else "unchanged", clear_handle.token)
        )
        if outcome == "removed":
            link_effects, link_warnings = sync_selection_links(
                context, (), None, dry_run=False, timeout=namespace.timeout
            )
            effects.extend(link_effects)
            warnings.extend(link_warnings)
    else:
        after = session.selection()
        token = after.handle.token if after.status == "selected" and after.handle else None
    return OperationResult(
        "work finish",
        "succeeded" if any(effect.status == "succeeded" for effect in effects) else "unchanged",
        FinishData(scope_id, completed, context.branch, context.branch, token),
        0,
        effects=tuple(effects),
        warnings=tuple(warnings),
    )


def _unmark_in_progress(
    session: WriteSession, scope_id: str, effects: list[Effect], warnings: list[Diagnostic]
) -> None:
    node = session.node(scope_id)
    if IN_PROGRESS_LABEL not in node.labels:
        return
    facts = session.known_facts(node.number)
    try:
        session.write(
            "github.issue.label",
            scope_id,
            lambda: session.client.remove_label(node.number, IN_PROGRESS_LABEL),
            lambda _: [
                UpsertIssue(replace(facts, labels=tuple(label for label in facts.labels if label != IN_PROGRESS_LABEL)))
            ],
        )
        effects.append(session.effects[-1])
    except WriteFailed as error:
        warnings.append(
            Diagnostic(
                CANONICAL_PROGRESS_MARK_FAILED,
                f"the in-progress label of {scope_id} was not removed: {error}",
                {
                    "scope_id": scope_id,
                    "writes": [{"kind": "github.issue.label", "status": session.effects[-1].status}],
                    "next_step": "Remove the spec-dock:in-progress label on GitHub; the Scope is already completed.",
                },
            )
        )
