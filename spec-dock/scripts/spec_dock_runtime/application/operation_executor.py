"""Prepare and advance D-16 journals without re-resolving dynamic selectors."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Literal
import uuid

from spec_dock_runtime.domain.operation import OperationEffect, OperationRecord

if TYPE_CHECKING:
    from collections.abc import Mapping


def prepare_operation(
    *,
    command: str,
    fixed_targets: Mapping[str, str],
    request_fingerprint: str,
    before_revisions: Mapping[str, int],
    engine_digest: str,
    writer_epoch: int,
) -> OperationRecord:
    return OperationRecord(
        operation_id=uuid.uuid4().hex,
        command=command,
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
    if record.before_revisions != tuple(sorted(current_revisions.items())):
        raise ValueError("resume before revision differs from the original operation")
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
    if any(effect.id == effect_id for effect in record.effects):
        raise ValueError("effect intent already exists")
    effect = OperationEffect(effect_id, kind, target, "intent")
    return replace(record, phase="effect-intent", effects=(*record.effects, effect), sequence=record.sequence + 1)


def record_effect_result(
    record: OperationRecord,
    *,
    effect_id: str,
    status: Literal["succeeded", "failed", "unknown"],
) -> OperationRecord:
    if status not in ("succeeded", "failed", "unknown"):
        raise ValueError("invalid effect result")
    if not any(effect.id == effect_id and effect.status == "intent" for effect in record.effects):
        raise ValueError("effect result requires a recorded intent")
    effects = tuple(replace(effect, status=status) if effect.id == effect_id else effect for effect in record.effects)
    return replace(record, phase="effect-result", effects=effects, sequence=record.sequence + 1)


def can_send_effect(record: OperationRecord, effect_id: str) -> bool:
    """Never issue the same external request twice without operation-specific observation."""
    return record.terminal_status == "pending" and all(effect.id != effect_id for effect in record.effects)
