"""Stable vNext CLI result envelope."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
import json
import re
from typing import Generic, Literal, TypeVar

ResultStatus = Literal["succeeded", "unchanged", "planned", "failed", "partial"]
EffectStatus = Literal["planned", "succeeded", "unchanged", "failed", "not_attempted", "unknown"]
T = TypeVar("T")


@dataclass(frozen=True)
class TargetRef:
    requested: str
    id: str
    kind: str
    backend: str
    snapshot_id: str


@dataclass(frozen=True)
class Diagnostic:
    code: str
    message: str
    details: dict[str, object]


@dataclass(frozen=True)
class Effect:
    kind: str
    status: EffectStatus
    target: str | None


@dataclass(frozen=True)
class Recovery:
    operation_id: str | None
    can_resume: bool
    can_rollback: bool
    commands: tuple[tuple[str, ...], ...]
    blocked_reason: str | None


@dataclass(frozen=True)
class OperationResult(Generic[T]):
    command: str
    status: ResultStatus
    data: T
    exit_code: int
    operation_id: str | None = None
    target: TargetRef | None = None
    effects: tuple[Effect, ...] = ()
    warnings: tuple[Diagnostic, ...] = ()
    error: Diagnostic | None = None
    recovery: Recovery | None = None

    def __post_init__(self) -> None:
        if self.status == "partial":
            if self.exit_code != 6 or self.error is None:
                raise ValueError("partial result requires exit 6 and error")
        elif self.status == "failed":
            if self.exit_code not in (1, 2, 3, 4, 5, 7) or self.error is None:
                raise ValueError("failed result requires a failure exit and error")
        elif self.status in ("succeeded", "unchanged", "planned"):
            if self.exit_code != 0 or self.error is not None:
                raise ValueError("successful result requires exit 0 and no error")
        else:
            raise ValueError("invalid operation status")


def render_json(result: OperationResult[object]) -> str:
    if not is_dataclass(result.data) or isinstance(result.data, type):
        raise TypeError("command data must be a typed dataclass")
    payload = {
        "schema_version": "specdock.cli/v1",
        "command": result.command,
        "status": result.status,
        "operation_id": result.operation_id,
        "target": asdict(result.target) if result.target is not None else None,
        "data": asdict(result.data),
        "effects": [asdict(effect) for effect in result.effects],
        "warnings": [asdict(warning) for warning in result.warnings],
        "error": asdict(result.error) if result.error is not None else None,
        "recovery": asdict(result.recovery) if result.recovery is not None else None,
    }
    return json.dumps(_redact(payload), ensure_ascii=False, separators=(",", ":")) + "\n"


def render_text(result: OperationResult[object]) -> tuple[str, str]:
    stdout_lines = [f"spec-dock: {result.status} ({result.command})"]
    for effect in result.effects:
        target = f" target={_text_escape(effect.target)}" if effect.target is not None else ""
        stdout_lines.append(f"effect {effect.kind} status={effect.status}{target}")
    stderr_lines = [f"warning [{item.code}] {_text_escape(item.message)}" for item in result.warnings]
    if result.error is not None:
        stderr_lines.append(f"error [{result.error.code}] {_text_escape(result.error.message)}")
    if result.recovery is not None and result.recovery.blocked_reason:
        stderr_lines.append(f"recovery: {_text_escape(result.recovery.blocked_reason)}")
    return "\n".join(stdout_lines) + "\n", "\n".join(stderr_lines) + ("\n" if stderr_lines else "")


def _text_escape(value: str) -> str:
    return json.dumps(_redact(value), ensure_ascii=False)[1:-1]


_SENSITIVE_KEYS = {"token", "access_token", "password", "secret", "authorization", "cookie", "api_key", "client_secret"}
_CREDENTIAL_PATTERN = re.compile(r"(?i)\bBearer\s+\S+|\b(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]+")


def _redact(value: object) -> object:
    if isinstance(value, dict):
        return {
            key: "[redacted]"
            if isinstance(key, str) and key.lower().replace("-", "_") in _SENSITIVE_KEYS
            else _redact(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_redact(item) for item in value]
    if isinstance(value, str):
        return _CREDENTIAL_PATTERN.sub("[redacted]", value)
    return value
