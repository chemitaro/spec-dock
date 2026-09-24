"""Prepare and advance D-16 journals without re-resolving dynamic selectors."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Literal
import uuid

from spec_dock_runtime.domain.operation import OperationEffect, OperationRecord

if TYPE_CHECKING:
    from collections.abc import Mapping


def _logical_id(effect: OperationEffect) -> str:
    return effect.retry_of or effect.id


def prepare_operation(
    *,
    command: str,
    effect_plan: tuple[str, ...],
    fixed_targets: Mapping[str, str],
    request_fingerprint: str,
    before_revisions: Mapping[str, int],
    engine_digest: str,
    writer_epoch: int,
) -> OperationRecord:
    return OperationRecord(
        operation_id=uuid.uuid4().hex,
        command=command,
        effect_plan=effect_plan,
        fixed_targets=tuple(sorted(fixed_targets.items())),
        request_fingerprint=request_fingerprint,
        before_revisions=tuple(sorted(before_revisions.items())),
        phase="prepared",
        effects=(),
        backup_refs=(),
        engine_digest=engine_digest,
        writer_epoch=writer_epoch,
        terminal_status="pending",
        sequence=0,
    )


def assert_resume_request(
    record: OperationRecord,
    *,
    command: str,
    fixed_targets: Mapping[str, str],
    request_fingerprint: str,
    current_revisions: Mapping[str, int],
    engine_digest: str,
    writer_epoch: int,
) -> None:
    if record.command != command:
        raise ValueError("resume command differs from the original operation")
    if record.fixed_targets != tuple(sorted(fixed_targets.items())):
        raise ValueError("resume fixed target differs from the original operation")
    if record.request_fingerprint != request_fingerprint:
        raise ValueError("resume request fingerprint differs from the original operation")
    expected_revisions = dict(record.before_revisions)
    for effect in record.effects:
        if effect.status == "succeeded":
            expected_revisions.update(effect.after_revisions)
    if tuple(sorted(expected_revisions.items())) != tuple(sorted(current_revisions.items())):
        raise ValueError("resume revision differs from the recorded effects")
    if record.engine_digest != engine_digest or record.writer_epoch != writer_epoch:
        raise ValueError("resume engine or writer epoch differs from the original operation")


def record_effect_intent(
    record: OperationRecord,
    *,
    effect_id: str,
    kind: Literal["local", "git", "remote"],
    target: str,
) -> OperationRecord:
    if record.terminal_status != "pending":
        raise ValueError("operation is already terminal")
    if not effect_id or "#" in effect_id:
        raise ValueError("invalid effect ID")
    prior = [effect for effect in record.effects if _logical_id(effect) == effect_id]
    if (
        record.effects
        and record.effects[-1].status != "succeeded"
        and (not prior or record.effects[-1] != prior[-1] or prior[-1].status != "not-applied")
    ):
        raise ValueError("unresolved effect prevents the next intent")
    if prior:
        last = prior[-1]
        if last.status != "not-applied" or (last.kind, last.target) != (kind, target):
            raise ValueError("effect intent already exists or retry target changed")
        effect = OperationEffect(f"{effect_id}#{len(prior) + 1}", kind, target, "intent", retry_of=effect_id)
    else:
        effect = OperationEffect(effect_id, kind, target, "intent")
    return replace(record, phase="effect-intent", effects=(*record.effects, effect), sequence=record.sequence + 1)


def record_effect_result(
    record: OperationRecord,
    *,
    effect_id: str,
    status: Literal["succeeded", "failed", "unknown"],
    after_revisions: Mapping[str, int] | None = None,
) -> OperationRecord:
    if status not in ("succeeded", "failed", "unknown"):
        raise ValueError("invalid effect result")
    if (
        record.terminal_status != "pending"
        or not record.effects
        or _logical_id(record.effects[-1]) != effect_id
        or record.effects[-1].status != "intent"
    ):
        raise ValueError("effect result requires a recorded intent")
    if status != "succeeded" and after_revisions:
        raise ValueError("only succeeded effects may record after revisions")
    updated = replace(record.effects[-1], status=status, after_revisions=tuple(sorted((after_revisions or {}).items())))
    effects = (*record.effects[:-1], updated)
    return replace(record, phase="effect-result", effects=effects, sequence=record.sequence + 1)


def record_effect_observation(
    record: OperationRecord,
    *,
    effect_id: str,
    outcome: Literal["observed_applied", "observed_not_applied", "still_unknown"],
    after_revisions: Mapping[str, int] | None = None,
) -> OperationRecord:
    if record.terminal_status != "pending" or not record.effects:
        raise ValueError("observation requires a pending operation")
    effect = record.effects[-1]
    if _logical_id(effect) != effect_id or effect.kind != "remote" or effect.status != "unknown":
        raise ValueError("observation requires the last unknown remote effect")
    if outcome == "observed_applied":
        updated = replace(effect, status="succeeded", after_revisions=tuple(sorted((after_revisions or {}).items())))
    elif outcome == "observed_not_applied":
        if after_revisions:
            raise ValueError("not-applied observation cannot advance revisions")
        updated = replace(effect, status="not-applied")
    elif outcome == "still_unknown":
        if after_revisions:
            raise ValueError("unknown observation cannot advance revisions")
        updated = effect
    else:
        raise ValueError("invalid observation result")
    return replace(
        record, phase="effect-observed", effects=(*record.effects[:-1], updated), sequence=record.sequence + 1
    )


def can_send_effect(record: OperationRecord, effect_id: str) -> bool:
    """Never issue the same external request twice without operation-specific observation."""
    if record.terminal_status != "pending":
        return False
    prior = [effect for effect in record.effects if _logical_id(effect) == effect_id]
    if prior:
        return prior[-1].status == "not-applied" and record.effects[-1] == prior[-1]
    return not record.effects or record.effects[-1].status == "succeeded"
