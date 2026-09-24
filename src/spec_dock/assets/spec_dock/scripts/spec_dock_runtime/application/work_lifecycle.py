"""Compose work transitions from fixed Scope and selection snapshots."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
from typing import TYPE_CHECKING

from spec_dock_runtime.application.active_selection import clear_selection
from spec_dock_runtime.application.operation_executor import (
    prepare_operation,
    record_effect_intent,
    record_effect_result,
)
from spec_dock_runtime.application.scope_completion import _descendants, plan_close
from spec_dock_runtime.application.scope_query import load_scope_views, show_scope
from spec_dock_runtime.cli.admission import admit_writer
from spec_dock_runtime.domain.lifecycle import (
    LocalBackend,
    LocalLifecycle,
    SelectionState,
    decode_scope_metadata,
    encode_scope_metadata,
)
from spec_dock_runtime.infra.active_store import load_selection_v3, save_selection_v3
from spec_dock_runtime.infra.control_store import load_control
from spec_dock_runtime.infra.json_store import atomic_write_json, read_guarded_json
from spec_dock_runtime.infra.operation_journal import JournalStore
from spec_dock_runtime.infra.writer_lock import WriterLock

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from spec_dock_runtime.application.scope_completion import CompletionDecision
    from spec_dock_runtime.application.scope_query import ScopeView
    from spec_dock_runtime.domain.lifecycle import ObservedState


@dataclass(frozen=True)
class WorkFinishPlan:
    target_id: str
    completion: CompletionDecision
    selection_after: SelectionState


@dataclass(frozen=True)
class WorkFinishResult:
    target_id: str
    completion_changed: bool
    selection_changed: bool
    operation_id: str | None


def plan_finish_work(
    views: tuple[ScopeView, ...],
    *,
    target: str,
    statuses: Mapping[str, ObservedState],
    selection: SelectionState,
) -> WorkFinishPlan:
    """Fix the requested Scope before any lifecycle or active mutation occurs."""
    scope = show_scope(views, target, selection=selection)
    completion = plan_close(views, scope.id, statuses)
    selection_after = clear_selection(views, current=selection, from_target=scope.id)
    return WorkFinishPlan(scope.id, completion, selection_after)


def _fingerprint(fixed: dict[str, str]) -> str:
    encoded = json.dumps(fixed, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _metadata_digest(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _selection_chain(selection: SelectionState) -> str:
    return json.dumps(
        [selection.initiative_id, selection.epic_id, selection.issue_id, selection.focus_id], separators=(",", ":")
    )


def finish_work(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    target: str,
    updated_at: str,
    lock_timeout: float = 0.0,
) -> WorkFinishResult:
    """Record local completion and selection clearing as separate resumable effects."""
    if not updated_at:
        raise ValueError("work finish timestamp is required")
    specdock_dir = repo_root / "spec-dock"
    with WriterLock(common_dir, timeout=lock_timeout):
        control = load_control(common_dir)
        admit_writer(
            control,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
        )
        views = load_scope_views(specdock_dir)
        selection, selection_identity = load_selection_v3(specdock_dir, worktree_id=worktree_id)
        scope = show_scope(views, target, selection=selection)
        if not isinstance(scope.backend, LocalBackend):
            raise ValueError("GitHub-backed work finish requires a live effect adapter")
        descendants = _descendants(views, scope)
        if any(not isinstance(view.backend, LocalBackend) for view in descendants):
            raise ValueError("GitHub descendants require live observation before work finish")
        statuses = {view.id: view.status.state for view in (scope, *descendants)}
        plan = plan_finish_work(views, target=scope.id, statuses=statuses, selection=selection)
        selection_changed = plan.selection_after != selection
        if not plan.completion.changed and not selection_changed:
            return WorkFinishResult(scope.id, False, False, None)
        loaded = read_guarded_json(scope.path / ".meta.json")
        if loaded is None or not isinstance(loaded[0], dict):
            raise ValueError("Scope metadata is missing")
        metadata = decode_scope_metadata(loaded[0])
        if not isinstance(metadata.backend, LocalBackend) or metadata.revision != scope.revision:
            raise ValueError("Scope metadata changed before work finish")
        next_metadata_payload = loaded[0]
        after_revision = metadata.revision
        if plan.completion.changed:
            lifecycle = metadata.backend.lifecycle
            next_metadata = replace(
                metadata,
                backend=LocalBackend(LocalLifecycle("completed", lifecycle.revision + 1, updated_at)),
                revision=metadata.revision + 1,
            )
            next_metadata_payload = encode_scope_metadata(next_metadata)
            after_revision = next_metadata.revision
        assert control is not None
        fixed = {
            "scope": scope.id,
            "worktree": worktree_id,
            "updated_at": updated_at,
            "before_state": plan.completion.before,
            "metadata_before_digest": _metadata_digest(loaded[0]),
            "metadata_after_digest": _metadata_digest(next_metadata_payload),
            "selection_before": _selection_chain(selection),
            "selection_after": _selection_chain(plan.selection_after),
            "lifecycle_changed": str(plan.completion.changed).lower(),
        }
        journal = JournalStore(common_dir)
        operation = prepare_operation(
            command="work.finish",
            fixed_targets=fixed,
            effect_plan=("lifecycle-update", "selection-clear"),
            request_fingerprint=_fingerprint(fixed),
            before_revisions={"metadata": metadata.revision, "selection": selection.revision},
            engine_digest=engine_digest,
            writer_epoch=control.epoch,
        )
        journal.create(operation)
        lifecycle_intent = record_effect_intent(operation, effect_id="lifecycle-update", kind="local", target=scope.id)
        journal.update(lifecycle_intent, expected_sequence=operation.sequence)
        if plan.completion.changed:
            atomic_write_json(scope.path / ".meta.json", next_metadata_payload, expected_identity=loaded[1])
        lifecycle_done = record_effect_result(
            lifecycle_intent,
            effect_id="lifecycle-update",
            status="succeeded",
            after_revisions={"metadata": after_revision},
        )
        journal.update(lifecycle_done, expected_sequence=lifecycle_intent.sequence)
        selection_intent = record_effect_intent(
            lifecycle_done, effect_id="selection-clear", kind="local", target=worktree_id
        )
        journal.update(selection_intent, expected_sequence=lifecycle_done.sequence)
        if selection_changed:
            save_selection_v3(specdock_dir, plan.selection_after, views=views, expected_identity=selection_identity)
        selection_done = record_effect_result(
            selection_intent,
            effect_id="selection-clear",
            status="succeeded",
            after_revisions={"selection": plan.selection_after.revision},
        )
        journal.update(selection_done, expected_sequence=selection_intent.sequence)
        terminal = replace(
            selection_done, phase="complete", terminal_status="succeeded", sequence=selection_done.sequence + 1
        )
        journal.update(terminal, expected_sequence=selection_done.sequence)
        return WorkFinishResult(scope.id, plan.completion.changed, selection_changed, operation.operation_id)


def _decode_selection_chain(raw: str, *, worktree_id: str, revision: int) -> SelectionState:
    try:
        fields = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError("recorded work finish selection is invalid") from error
    if (
        not isinstance(fields, list)
        or len(fields) != 4
        or any(item is not None and not isinstance(item, str) for item in fields)
    ):
        raise ValueError("recorded work finish selection is invalid")
    return SelectionState(worktree_id, revision, *fields)


def resume_finish_work(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    operation_id: str,
    lock_timeout: float = 0.0,
) -> WorkFinishResult:
    """Reconcile one local finish from its recorded target and before/after states."""
    specdock_dir = repo_root / "spec-dock"
    with WriterLock(common_dir, timeout=lock_timeout):
        journal = JournalStore(common_dir)
        operation = journal.load(operation_id)
        fixed = dict(operation.fixed_targets)
        revisions = dict(operation.before_revisions)
        if (
            operation.command != "work.finish"
            or operation.effect_plan != ("lifecycle-update", "selection-clear")
            or set(fixed)
            != {
                "scope",
                "worktree",
                "updated_at",
                "before_state",
                "metadata_before_digest",
                "metadata_after_digest",
                "selection_before",
                "selection_after",
                "lifecycle_changed",
            }
            or fixed["worktree"] != worktree_id
            or fixed["before_state"] not in ("open", "completed")
            or fixed["lifecycle_changed"] not in ("true", "false")
            or set(revisions) != {"metadata", "selection"}
            or operation.request_fingerprint != _fingerprint(fixed)
            or operation.engine_digest != engine_digest
            or operation.writer_epoch != expected_epoch
        ):
            raise ValueError("work finish recovery differs from the recorded request")
        before_selection = _decode_selection_chain(
            fixed["selection_before"], worktree_id=worktree_id, revision=revisions["selection"]
        )
        after_selection = _decode_selection_chain(
            fixed["selection_after"],
            worktree_id=worktree_id,
            revision=revisions["selection"] + (fixed["selection_before"] != fixed["selection_after"]),
        )
        lifecycle_changed = fixed["lifecycle_changed"] == "true"
        selection_changed = after_selection != before_selection
        if lifecycle_changed != (fixed["before_state"] == "open"):
            raise ValueError("recorded work finish lifecycle transition is invalid")
        if operation.terminal_status == "succeeded":
            return WorkFinishResult(fixed["scope"], lifecycle_changed, selection_changed, operation_id)
        if operation.terminal_status != "pending":
            raise ValueError("work finish recovery requires a pending operation")
        admit_writer(
            load_control(common_dir),
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
            recovery_operation_id=operation_id,
        )
        views = load_scope_views(specdock_dir)
        scope = show_scope(views, fixed["scope"])
        if not isinstance(scope.backend, LocalBackend):
            raise ValueError("recorded work finish backend changed")
        descendants = _descendants(views, scope)
        if any(not isinstance(view.backend, LocalBackend) for view in descendants):
            raise ValueError("GitHub descendants require live observation before work finish recovery")
        statuses = {view.id: view.status.state for view in (scope, *descendants)}
        plan_close(views, scope.id, statuses)
        if clear_selection(views, current=before_selection, from_target=scope.id) != after_selection:
            raise ValueError("recorded work finish selection does not match the fixed Scope")
        metadata_path = scope.path / ".meta.json"
        loaded = read_guarded_json(metadata_path)
        if loaded is None or not isinstance(loaded[0], dict):
            raise ValueError("Scope metadata is missing during work finish recovery")
        metadata = decode_scope_metadata(loaded[0])
        if not isinstance(metadata.backend, LocalBackend) or metadata.raw.get("id") != scope.id:
            raise ValueError("recorded work finish Scope identity changed")
        expected_metadata_revision = revisions["metadata"] + lifecycle_changed
        lifecycle = metadata.backend.lifecycle
        applied = (
            lifecycle_changed
            and metadata.revision == expected_metadata_revision
            and lifecycle.state == "completed"
            and lifecycle.updated_at == fixed["updated_at"]
        )
        unapplied = metadata.revision == revisions["metadata"] and lifecycle.state == fixed["before_state"]
        if not applied and not unapplied:
            raise ValueError("work finish metadata differs from recorded before/after state")
        expected_digest = fixed["metadata_after_digest"] if applied else fixed["metadata_before_digest"]
        if _metadata_digest(loaded[0]) != expected_digest:
            raise ValueError("work finish metadata differs from recorded before/after content")
        if operation.effects:
            effect = operation.effects[0]
            if effect.id != "lifecycle-update" or effect.target != scope.id or effect.kind != "local":
                raise ValueError("recorded work finish lifecycle effect is invalid")
        else:
            if applied:
                raise ValueError("work finish lifecycle changed before effect intent")
            next_record = record_effect_intent(operation, effect_id="lifecycle-update", kind="local", target=scope.id)
            journal.update(next_record, expected_sequence=operation.sequence)
            operation = next_record
        if operation.effects[0].status == "intent":
            if unapplied and lifecycle_changed:
                if statuses[scope.id] != "open":
                    raise ValueError("work finish lifecycle precondition changed during recovery")
                next_metadata = replace(
                    metadata,
                    backend=LocalBackend(LocalLifecycle("completed", lifecycle.revision + 1, fixed["updated_at"])),
                    revision=metadata.revision + 1,
                )
                atomic_write_json(metadata_path, encode_scope_metadata(next_metadata), expected_identity=loaded[1])
            succeeded = record_effect_result(
                operation,
                effect_id="lifecycle-update",
                status="succeeded",
                after_revisions={"metadata": expected_metadata_revision},
            )
            journal.update(succeeded, expected_sequence=operation.sequence)
            operation = succeeded
        elif operation.effects[0].status != "succeeded" or (lifecycle_changed and not applied):
            raise ValueError("recorded work finish lifecycle effect cannot be reconciled")
        selection, selection_identity = load_selection_v3(specdock_dir, worktree_id=worktree_id)
        if selection not in (before_selection, after_selection):
            raise ValueError("active selection differs from recorded work finish before/after state")
        if len(operation.effects) == 1:
            if selection_changed and selection == after_selection:
                raise ValueError("work finish selection changed before effect intent")
            next_record = record_effect_intent(operation, effect_id="selection-clear", kind="local", target=worktree_id)
            journal.update(next_record, expected_sequence=operation.sequence)
            operation = next_record
        if len(operation.effects) != 2 or operation.effects[1].id != "selection-clear":
            raise ValueError("recorded work finish selection effect is invalid")
        if operation.effects[1].status == "intent":
            if selection_changed and selection == before_selection:
                save_selection_v3(specdock_dir, after_selection, views=views, expected_identity=selection_identity)
            succeeded = record_effect_result(
                operation,
                effect_id="selection-clear",
                status="succeeded",
                after_revisions={"selection": after_selection.revision},
            )
            journal.update(succeeded, expected_sequence=operation.sequence)
            operation = succeeded
        elif operation.effects[1].status != "succeeded" or selection != after_selection:
            raise ValueError("recorded work finish selection effect cannot be reconciled")
        terminal = replace(operation, phase="complete", terminal_status="succeeded", sequence=operation.sequence + 1)
        journal.update(terminal, expected_sequence=operation.sequence)
        return WorkFinishResult(scope.id, lifecycle_changed, selection_changed, operation_id)
