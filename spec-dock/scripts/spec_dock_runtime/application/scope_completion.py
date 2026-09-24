"""Pure completion decisions over an explicitly observed Scope snapshot."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
from typing import TYPE_CHECKING, Literal, cast

from spec_dock_runtime.application.operation_executor import (
    prepare_operation,
    record_effect_intent,
    record_effect_observation,
    record_effect_result,
)
from spec_dock_runtime.application.scope_query import load_scope_views, show_scope
from spec_dock_runtime.cli.admission import admit_writer
from spec_dock_runtime.domain.lifecycle import (
    GithubBackend,
    LocalBackend,
    LocalLifecycle,
    decode_scope_metadata,
    encode_scope_metadata,
)
from spec_dock_runtime.infra.control_store import load_control
from spec_dock_runtime.infra.github_lifecycle import GithubIssueGateway, RemoteIssueError
from spec_dock_runtime.infra.json_store import atomic_write_json, read_guarded_json
from spec_dock_runtime.infra.operation_journal import JournalStore
from spec_dock_runtime.infra.writer_lock import WriterLock

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from spec_dock_runtime.application.scope_query import ScopeView
    from spec_dock_runtime.domain.lifecycle import ObservedState
    from spec_dock_runtime.domain.operation import OperationRecord

CompletionReason = Literal["completed", "not-planned"]


@dataclass(frozen=True)
class CompletionDecision:
    target_id: str
    before: ObservedState
    after: Literal["open", "completed", "not-planned"]
    changed: bool
    descendants: tuple[str, ...]


@dataclass(frozen=True)
class CompletionResult:
    decision: CompletionDecision
    changed: bool
    operation_id: str | None


def _completion_fingerprint(fixed: dict[str, str]) -> str:
    payload = json.dumps(fixed, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()


def _state(statuses: Mapping[str, ObservedState], scope_id: str) -> ObservedState:
    try:
        return statuses[scope_id]
    except KeyError as error:
        raise ValueError("SCOPE_STATUS_UNOBSERVED") from error


def _ancestors(views: tuple[ScopeView, ...], target: ScopeView) -> tuple[ScopeView, ...]:
    by_id = {view.id: view for view in views}
    ancestors: list[ScopeView] = []
    seen = {target.id}
    parent_id = target.parent_id
    while parent_id is not None:
        if parent_id in seen or parent_id not in by_id:
            raise ValueError("SCOPE_ANCESTRY_INVALID")
        seen.add(parent_id)
        parent = by_id[parent_id]
        ancestors.append(parent)
        parent_id = parent.parent_id
    return tuple(ancestors)


def _descendants(views: tuple[ScopeView, ...], target: ScopeView) -> tuple[ScopeView, ...]:
    by_id = {view.id: view for view in views}
    children: list[ScopeView] = []
    for view in views:
        if view.id == target.id:
            continue
        seen = {view.id}
        parent_id = view.parent_id
        while parent_id is not None:
            if parent_id in seen or parent_id not in by_id:
                raise ValueError("SCOPE_ANCESTRY_INVALID")
            if parent_id == target.id:
                children.append(view)
                break
            seen.add(parent_id)
            parent_id = by_id[parent_id].parent_id
    return tuple(children)


def plan_close(
    views: tuple[ScopeView, ...],
    target_id: str,
    statuses: Mapping[str, ObservedState],
    *,
    reason: CompletionReason = "completed",
) -> CompletionDecision:
    if reason not in ("completed", "not-planned"):
        raise ValueError("INVALID_COMPLETION_REASON")
    target = show_scope(views, target_id)
    before = _state(statuses, target.id)
    descendants = _descendants(views, target)
    if reason == "completed" and any(_state(statuses, child.id) != "completed" for child in descendants):
        raise ValueError("DESCENDANT_NOT_COMPLETED")
    if before == "unknown":
        raise ValueError("SCOPE_STATUS_UNKNOWN")
    if before != "open" and before != reason:
        raise ValueError("TERMINAL_REASON_CONFLICT")
    return CompletionDecision(target.id, before, reason, before != reason, tuple(child.id for child in descendants))


def plan_reopen(
    views: tuple[ScopeView, ...], target_id: str, statuses: Mapping[str, ObservedState]
) -> CompletionDecision:
    target = show_scope(views, target_id)
    before = _state(statuses, target.id)
    if any(_state(statuses, ancestor.id) != "open" for ancestor in _ancestors(views, target)):
        raise ValueError("ANCESTOR_TERMINAL")
    if before == "unknown":
        raise ValueError("SCOPE_STATUS_UNKNOWN")
    return CompletionDecision(target.id, before, "open", before != "open", ())


def change_scope_lifecycle(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    target_id: str,
    action: Literal["close", "reopen"],
    updated_at: str,
    reason: CompletionReason = "completed",
    gateway: GithubIssueGateway | None = None,
    lock_timeout: float = 0.0,
) -> CompletionResult:
    """Apply one lifecycle change; selection and Git checkout are outside this use case."""
    if not updated_at:
        raise ValueError("lifecycle update timestamp is required")
    if action not in ("close", "reopen") or (action == "reopen" and reason != "completed"):
        raise ValueError("invalid lifecycle action or reason")
    with WriterLock(common_dir, timeout=lock_timeout):
        control = load_control(common_dir)
        admit_writer(
            control,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
        )
        views = load_scope_views(repo_root / "spec-dock")
        target = show_scope(views, target_id)
        relevant = (target, *_descendants(views, target)) if action == "close" else (target, *_ancestors(views, target))
        statuses: dict[str, ObservedState] = {}
        for view in relevant:
            if isinstance(view.backend, LocalBackend):
                statuses[view.id] = view.status.state
            else:
                if gateway is None:
                    raise ValueError("GitHub lifecycle requires a live gateway")
                remote = gateway.get(
                    repo_root,
                    f"{view.backend.repo_owner}/{view.backend.repo_name}",
                    view.backend.issue_number,
                )
                statuses[view.id] = remote.state
        decision = (
            plan_close(views, target.id, statuses, reason=reason)
            if action == "close"
            else plan_reopen(views, target.id, statuses)
        )
        if not decision.changed:
            return CompletionResult(decision, False, None)
        loaded = read_guarded_json(target.path / ".meta.json")
        if loaded is None or not isinstance(loaded[0], dict):
            raise ValueError("Scope metadata is missing")
        metadata = decode_scope_metadata(loaded[0])
        if metadata.raw.get("id") != target.id or metadata.revision != target.revision:
            raise ValueError("Scope metadata changed before lifecycle update")
        assert control is not None
        fixed = {
            "scope": target.id,
            "action": action,
            "reason": reason if action == "close" else "open",
            "updated_at": updated_at,
            "before_state": decision.before,
        }
        if target.github_ref is not None:
            fixed["github_ref"] = target.github_ref
        fingerprint = _completion_fingerprint(fixed)
        journal = JournalStore(common_dir)
        operation = prepare_operation(
            command=f"scope.{action}",
            effect_plan=("lifecycle-update",),
            fixed_targets=fixed,
            request_fingerprint=fingerprint,
            before_revisions={"metadata": metadata.revision},
            engine_digest=engine_digest,
            writer_epoch=control.epoch,
        )
        journal.create(operation)
        intent = record_effect_intent(
            operation,
            effect_id="lifecycle-update",
            kind="local" if isinstance(metadata.backend, LocalBackend) else "remote",
            target=target.id,
        )
        journal.update(intent, expected_sequence=operation.sequence)
        if isinstance(metadata.backend, LocalBackend):
            prior = metadata.backend.lifecycle
            next_metadata = replace(
                metadata,
                backend=LocalBackend(LocalLifecycle(decision.after, prior.revision + 1, updated_at)),
                revision=metadata.revision + 1,
            )
            atomic_write_json(
                target.path / ".meta.json", encode_scope_metadata(next_metadata), expected_identity=loaded[1]
            )
            after_revisions = {"metadata": next_metadata.revision}
            remote_ref = None
        else:
            if gateway is None:
                raise AssertionError("live gateway was checked before the operation")
            backend = metadata.backend
            assert isinstance(backend, GithubBackend)
            repository = f"{backend.repo_owner}/{backend.repo_name}"
            try:
                gateway.set_state(
                    repo_root,
                    repository,
                    backend.issue_number,
                    state="open" if action == "reopen" else "closed",
                    reason=None if action == "reopen" else "completed" if reason == "completed" else "not_planned",
                )
            except RemoteIssueError as error:
                observed = record_effect_result(
                    intent, effect_id="lifecycle-update", status="unknown" if error.uncertain else "failed"
                )
                journal.update(observed, expected_sequence=intent.sequence)
                if not error.uncertain:
                    terminal = replace(
                        observed, phase="complete", terminal_status="failed", sequence=observed.sequence + 1
                    )
                    journal.update(terminal, expected_sequence=observed.sequence)
                raise
            after_revisions = {}
            remote_ref = target.github_ref
        succeeded = record_effect_result(
            intent,
            effect_id="lifecycle-update",
            status="succeeded",
            after_revisions=after_revisions,
            remote_ref=remote_ref,
        )
        journal.update(succeeded, expected_sequence=intent.sequence)
        terminal = replace(succeeded, phase="complete", terminal_status="succeeded", sequence=succeeded.sequence + 1)
        journal.update(terminal, expected_sequence=succeeded.sequence)
        return CompletionResult(decision, True, operation.operation_id)


def resume_scope_lifecycle(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    operation_id: str,
    gateway: GithubIssueGateway | None = None,
    lock_timeout: float = 0.0,
) -> CompletionResult:
    """Reconcile a fixed local lifecycle effect before applying anything else."""
    with WriterLock(common_dir, timeout=lock_timeout):
        journal = JournalStore(common_dir)
        operation = journal.load(operation_id)
        fixed = dict(operation.fixed_targets)
        if (
            not {"scope", "action", "reason", "updated_at", "before_state"}.issubset(fixed)
            or set(fixed) - {"scope", "action", "reason", "updated_at", "before_state", "github_ref"}
            or fixed["action"] not in ("close", "reopen")
            or fixed["reason"] not in ("open", "completed", "not-planned")
            or fixed["before_state"] not in ("open", "completed", "not-planned")
            or operation.command != f"scope.{fixed['action']}"
            or operation.effect_plan != ("lifecycle-update",)
            or operation.request_fingerprint != _completion_fingerprint(fixed)
            or operation.engine_digest != engine_digest
            or operation.writer_epoch != expected_epoch
        ):
            raise ValueError("lifecycle recovery operation differs from fixed request")
        action = fixed["action"]
        desired = fixed["reason"]
        before_state = cast("ObservedState", fixed["before_state"])
        decision = CompletionDecision(
            fixed["scope"], before_state, cast("Literal['open', 'completed', 'not-planned']", desired), True, ()
        )
        if operation.terminal_status == "succeeded":
            return CompletionResult(decision, True, operation.operation_id)
        admit_writer(
            load_control(common_dir),
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
            recovery_operation_id=operation_id,
        )
        views = load_scope_views(repo_root / "spec-dock")
        target = show_scope(views, fixed["scope"])
        if not isinstance(target.backend, LocalBackend):
            if fixed.get("github_ref") != target.github_ref:
                raise ValueError("GitHub identity differs from fixed lifecycle request")
            return _resume_github_lifecycle(
                repo_root=repo_root,
                journal=journal,
                operation=operation,
                fixed=fixed,
                views=views,
                target=target,
                before_state=before_state,
                decision=decision,
                gateway=gateway,
            )
        if "github_ref" in fixed:
            raise ValueError("local lifecycle recovery has unexpected GitHub identity")
        path = target.path / ".meta.json"
        loaded = read_guarded_json(path)
        if loaded is None or not isinstance(loaded[0], dict):
            raise ValueError("Scope metadata is missing")
        metadata = decode_scope_metadata(loaded[0])
        if not isinstance(metadata.backend, LocalBackend) or metadata.raw.get("id") != target.id:
            raise ValueError("Scope backend changed during lifecycle recovery")
        before_revision = dict(operation.before_revisions).get("metadata")
        if before_revision is None:
            raise ValueError("recorded metadata revision is missing")
        lifecycle = metadata.backend.lifecycle
        applied = (
            metadata.revision == before_revision + 1
            and lifecycle.state == desired
            and lifecycle.updated_at == fixed["updated_at"]
        )
        unapplied = metadata.revision == before_revision and lifecycle.state == before_state
        if not applied and not unapplied:
            raise ValueError("lifecycle metadata differs from recorded before/after state")
        if operation.effects:
            effect = operation.effects[0]
            if len(operation.effects) != 1 or effect.id != "lifecycle-update" or effect.target != target.id:
                raise ValueError("recorded lifecycle effect is invalid")
        else:
            if applied:
                raise ValueError("lifecycle changed without a recorded effect intent")
            next_record = record_effect_intent(operation, effect_id="lifecycle-update", kind="local", target=target.id)
            journal.update(next_record, expected_sequence=operation.sequence)
            operation = next_record
        if unapplied:
            if operation.effects[0].status != "intent":
                raise ValueError("recorded lifecycle effect result conflicts with metadata")
            relevant = (
                (target, *_descendants(views, target)) if action == "close" else (target, *_ancestors(views, target))
            )
            statuses: dict[str, ObservedState] = {}
            for view in relevant:
                if isinstance(view.backend, LocalBackend):
                    statuses[view.id] = view.status.state
                else:
                    if gateway is None:
                        raise ValueError("GitHub descendant requires live observation for lifecycle recovery")
                    remote = gateway.get(
                        repo_root,
                        f"{view.backend.repo_owner}/{view.backend.repo_name}",
                        view.backend.issue_number,
                    )
                    statuses[view.id] = remote.state
            renewed = (
                plan_close(views, target.id, statuses, reason=cast("CompletionReason", desired))
                if action == "close"
                else plan_reopen(views, target.id, statuses)
            )
            if not renewed.changed or renewed.before != before_state:
                raise ValueError("lifecycle precondition changed during recovery")
            next_metadata = replace(
                metadata,
                backend=LocalBackend(LocalLifecycle(renewed.after, lifecycle.revision + 1, fixed["updated_at"])),
                revision=metadata.revision + 1,
            )
            atomic_write_json(path, encode_scope_metadata(next_metadata), expected_identity=loaded[1])
        if operation.effects[0].status == "intent":
            next_record = record_effect_result(
                operation,
                effect_id="lifecycle-update",
                status="succeeded",
                after_revisions={"metadata": before_revision + 1},
            )
            journal.update(next_record, expected_sequence=operation.sequence)
            operation = next_record
        elif operation.effects[0].status != "succeeded":
            raise ValueError("recorded lifecycle effect cannot be resumed")
        terminal = replace(operation, phase="complete", terminal_status="succeeded", sequence=operation.sequence + 1)
        journal.update(terminal, expected_sequence=operation.sequence)
        return CompletionResult(decision, True, operation.operation_id)


def _resume_github_lifecycle(
    *,
    repo_root: Path,
    journal: JournalStore,
    operation: OperationRecord,
    fixed: dict[str, str],
    views: tuple[ScopeView, ...],
    target: ScopeView,
    before_state: ObservedState,
    decision: CompletionDecision,
    gateway: GithubIssueGateway | None,
) -> CompletionResult:
    if gateway is None or not isinstance(target.backend, GithubBackend):
        raise ValueError("GitHub lifecycle recovery requires a live gateway")
    metadata = read_guarded_json(target.path / ".meta.json")
    if metadata is None or not isinstance(metadata[0], dict):
        raise ValueError("Scope metadata is missing")
    decoded = decode_scope_metadata(metadata[0])
    before_revision = dict(operation.before_revisions).get("metadata")
    if (
        before_revision is None
        or decoded.revision != before_revision
        or not isinstance(decoded.backend, GithubBackend)
        or decoded.raw.get("id") != target.id
    ):
        raise ValueError("GitHub Scope metadata changed during recovery")
    backend = target.backend
    repository = f"{backend.repo_owner}/{backend.repo_name}"
    observed = gateway.get(repo_root, repository, backend.issue_number)
    if operation.effects:
        effect = operation.effects[0]
        if (
            len(operation.effects) != 1
            or effect.id != "lifecycle-update"
            or effect.target != target.id
            or effect.kind != "remote"
        ):
            raise ValueError("recorded GitHub lifecycle effect is invalid")
    else:
        if observed.state != before_state:
            raise ValueError("GitHub state changed before recorded effect intent")
        relevant = (
            (target, *_descendants(views, target))
            if fixed["action"] == "close"
            else (target, *_ancestors(views, target))
        )
        statuses: dict[str, ObservedState] = {target.id: observed.state}
        for view in relevant[1:]:
            if isinstance(view.backend, LocalBackend):
                statuses[view.id] = view.status.state
            else:
                state = gateway.get(
                    repo_root, f"{view.backend.repo_owner}/{view.backend.repo_name}", view.backend.issue_number
                )
                statuses[view.id] = state.state
        renewed = (
            plan_close(views, target.id, statuses, reason=cast("CompletionReason", fixed["reason"]))
            if fixed["action"] == "close"
            else plan_reopen(views, target.id, statuses)
        )
        if not renewed.changed or renewed.before != before_state:
            raise ValueError("GitHub lifecycle precondition changed before recovery")
        next_record = record_effect_intent(operation, effect_id="lifecycle-update", kind="remote", target=target.id)
        journal.update(next_record, expected_sequence=operation.sequence)
        operation = next_record
        try:
            gateway.set_state(
                repo_root,
                repository,
                backend.issue_number,
                state="open" if fixed["action"] == "reopen" else "closed",
                reason=None
                if fixed["action"] == "reopen"
                else "completed"
                if fixed["reason"] == "completed"
                else "not_planned",
            )
        except RemoteIssueError as error:
            result = record_effect_result(
                operation, effect_id="lifecycle-update", status="unknown" if error.uncertain else "failed"
            )
            journal.update(result, expected_sequence=operation.sequence)
            if not error.uncertain:
                terminal = replace(result, phase="complete", terminal_status="failed", sequence=result.sequence + 1)
                journal.update(terminal, expected_sequence=result.sequence)
            raise
        observed = gateway.get(repo_root, repository, backend.issue_number)
    if observed.state != decision.after:
        if operation.effects[0].status == "intent":
            uncertain = record_effect_result(operation, effect_id="lifecycle-update", status="unknown")
            journal.update(uncertain, expected_sequence=operation.sequence)
        raise ValueError("GitHub lifecycle effect is unconfirmed; no blind resend")
    if operation.effects[0].status == "intent":
        next_record = record_effect_result(
            operation, effect_id="lifecycle-update", status="succeeded", remote_ref=target.github_ref
        )
        journal.update(next_record, expected_sequence=operation.sequence)
        operation = next_record
    elif operation.effects[0].status == "unknown":
        next_record = record_effect_observation(
            operation, effect_id="lifecycle-update", outcome="observed_applied", remote_ref=target.github_ref
        )
        journal.update(next_record, expected_sequence=operation.sequence)
        operation = next_record
    elif operation.effects[0].status != "succeeded":
        raise ValueError("recorded GitHub effect cannot be resumed")
    terminal = replace(operation, phase="complete", terminal_status="succeeded", sequence=operation.sequence + 1)
    journal.update(terminal, expected_sequence=operation.sequence)
    return CompletionResult(decision, True, operation.operation_id)
