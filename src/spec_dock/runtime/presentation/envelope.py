"""Stable vNext CLI result envelope."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
import json
import re
from typing import Generic, Literal, TypeVar, cast

from spec_dock.runtime.presentation.command_data import FamilyData, SyncData

ResultStatus = Literal["succeeded", "unchanged", "planned", "failed", "partial"]
EffectStatus = Literal["planned", "succeeded", "unchanged", "failed", "not_attempted", "unknown"]
T = TypeVar("T", covariant=True)


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
class RecoveryInstructions:
    instructions: tuple[str, ...]
    can_resume: Literal[False] = False
    can_rollback: Literal[False] = False


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
    recovery: Recovery | RecoveryInstructions | None = None

    def __post_init__(self) -> None:
        if self.status == "partial":
            if self.exit_code not in (6, 7) or self.error is None:
                raise ValueError("partial result requires exit 6 or diagnostic exit 7 and error")
        elif self.status == "failed":
            if self.exit_code not in (1, 2, 3, 4, 5, 7) or self.error is None:
                raise ValueError("failed result requires a failure exit and error")
        elif self.status in ("succeeded", "unchanged", "planned"):
            if self.exit_code != 0 or self.error is not None:
                raise ValueError("successful result requires exit 0 and no error")
        else:
            raise ValueError("invalid operation status")
        effect_states = {effect.status for effect in self.effects}
        if self.status == "succeeded" and not effect_states <= {"succeeded", "unchanged"}:
            raise ValueError("succeeded result cannot contain incomplete effects")
        if self.status == "unchanged" and not effect_states <= {"unchanged"}:
            raise ValueError("unchanged result cannot contain mutation effects")
        if self.status == "planned" and not effect_states <= {"planned"}:
            raise ValueError("planned result cannot contain executed effects")
        if self.status == "failed" and effect_states & {"succeeded", "unknown"}:
            raise ValueError("failed result cannot hide applied or unknown effects")
        if (
            self.status == "partial"
            and self.exit_code == 6
            and not ("unknown" in effect_states or "succeeded" in effect_states)
        ):
            raise ValueError("partial result requires an applied or unknown effect")


def render_utility_json(command: str, text: str, *, version: str | None = None) -> str:
    """Render a context-free utility with the public v2 contract."""
    return (
        json.dumps(
            {
                "schema_version": "specdock.cli/v2",
                "command": command,
                "status": "succeeded",
                "exit_code": 0,
                "data": {"kind": "utility", "text": text, "version": version},
                "effects": [],
                "warnings": [],
                "error": None,
                "recovery": None,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        + "\n"
    )


def render_diagnostic_json(command: str, code: str, message: str, *, exit_code: int) -> str:
    """Render a front-door failure before any business effects."""
    return (
        json.dumps(
            _redact({
                "schema_version": "specdock.cli/v2",
                "command": command,
                "status": "failed",
                "exit_code": exit_code,
                "data": {"kind": "diagnostic", "findings": [], "unverified": []},
                "effects": [],
                "warnings": [],
                "error": {"code": code, "message": message, "details": {}},
                "recovery": None,
            }),
            ensure_ascii=False,
            separators=(",", ":"),
        )
        + "\n"
    )


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


def render_json_v2(result: OperationResult[object]) -> str:
    """Public stateless envelope; legacy operation IDs are never exposed."""
    if not is_dataclass(result.data) or isinstance(result.data, type):
        raise TypeError("command data must be a typed dataclass")
    payload = {
        "schema_version": "specdock.cli/v2",
        "command": result.command,
        "status": result.status,
        "exit_code": result.exit_code,
        "data": asdict(result.data),
        "effects": [asdict(effect) for effect in result.effects],
        "warnings": [asdict(item) for item in result.warnings],
        "error": asdict(result.error) if result.error else None,
        "recovery": asdict(result.recovery) if isinstance(result.recovery, RecoveryInstructions) else None,
    }
    return json.dumps(_redact(payload), ensure_ascii=False, separators=(",", ":")) + "\n"


def render_text(
    result: OperationResult[object], *, native_git: bool = False, dependency_view: str | None = None
) -> tuple[str, str]:
    stdout_lines = [f"spec-dock: {result.status} ({result.command})"]
    if isinstance(result.data, SyncData):
        stdout_lines.extend(_sync_text(result.data))
    elif result.command == "dependency list" and isinstance(result.data, FamilyData):
        stdout_lines.append(f"scope_id={_field_text(result.data.result['scope_id'])}")
        for view in (dependency_view,) if dependency_view is not None else ("declared", "effective"):
            stdout_lines.append(f"{view}={json.dumps(_redact(result.data.result[view]), ensure_ascii=False)}")
    elif result.command == "dependency check" and isinstance(result.data, FamilyData):
        stdout_lines.append(
            f"scope_id={_field_text(result.data.result['scope_id'])} ready={str(result.data.result['ready']).lower()}"
        )
        for blocker in cast("tuple[Diagnostic, ...]", result.data.result["blockers"]):
            stdout_lines.append(f"blocker [{blocker.code}] {_text_escape(blocker.message)}")
    for effect in result.effects:
        target = f" target={_text_escape(effect.target)}" if effect.target is not None else ""
        stdout_lines.append(f"effect {effect.kind} status={effect.status}{target}")
    stderr_lines = [f"warning [{item.code}] {_text_escape(item.message)}" for item in result.warnings]
    native_stderr = ""
    if result.error is not None:
        git_details = result.error.details.get("git")
        if native_git and isinstance(git_details, dict) and isinstance(git_details.get("stderr"), str):
            stderr_lines.append(f"error [{result.error.code}]")
            native_stderr = str(_redact(git_details["stderr"]))
        else:
            stderr_lines.append(f"error [{result.error.code}] {_text_escape(result.error.message)}")
    if isinstance(result.recovery, RecoveryInstructions):
        stderr_lines.extend(f"recovery: {_text_escape(item)}" for item in result.recovery.instructions)
    elif result.recovery is not None and result.recovery.blocked_reason:
        stderr_lines.append(f"recovery: {_text_escape(result.recovery.blocked_reason)}")
    return "\n".join(stdout_lines) + "\n", "\n".join(stderr_lines) + ("\n" if stderr_lines else "") + native_stderr


def _sync_text(data: SyncData) -> list[str]:
    lines = [f"observed_at={data.observed_at} source={data.source} complete={str(data.complete).lower()}"]
    for row in data.worktrees:
        selected = cast("dict[str, object]", row["selection"])
        lines.append(f'worktree path="{_text_escape(str(row["path"]))}"')
        lines.append(
            f"  selection={selected['status']} scope_id={_field_text(selected['scope_id'])} "
            f"lifecycle={row['lifecycle']} current_branch={_field_text(selected['current_branch'])} "
            f"selected_branch={_field_text(selected['selected_branch'])} "
            f"branch_changed={str(selected['branch_changed']).lower()} process_state={row['process_state']}"
        )
    counts = {str(row["scope_id"]): row for row in data.counts}
    for scope in data.scopes:
        count = counts[str(scope["scope_id"])]
        lines.append(
            f"scope_id={scope['scope_id']} github_ref={_field_text(scope['github_ref'])} lifecycle={scope['lifecycle']} "
            f"direct_selected_count={count['direct_selected_count']} "
            f"descendant_selected_count={count['descendant_selected_count']} complete={str(count['complete']).lower()}"
        )
    lines.extend(
        f"finding [{finding.code}] {_text_escape(finding.message)} "
        f"details={json.dumps(_redact(finding.details), ensure_ascii=False)}"
        for finding in data.findings
    )
    return lines


def _field_text(value: object) -> str:
    return "null" if value is None else _text_escape(str(value))


def _text_escape(value: str) -> str:
    return json.dumps(_redact(value), ensure_ascii=False)[1:-1]


_SENSITIVE_KEYS = {"token", "access_token", "password", "secret", "authorization", "cookie", "api_key", "client_secret"}
_CREDENTIAL_PATTERN = re.compile(r"(?i)\bBearer\s+\S+|\b(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]+")
_USERINFO_PATTERN = re.compile(r"(?i)(\b[a-z][a-z0-9+.-]*://)[^\s/?#\"'<>]*@")


def redact_text(value: str) -> str:
    """Keep normal wording and URL host/path while removing credential portions."""
    return _CREDENTIAL_PATTERN.sub("[redacted]", _USERINFO_PATTERN.sub(r"\1[redacted]@", value))


def _redact(value: object) -> object:
    if isinstance(value, dict):
        rendered = {
            key: "[redacted]"
            if isinstance(key, str) and key.lower().replace("-", "_") in _SENSITIVE_KEYS
            else _redact(item)
            for key, item in value.items()
        }
        if all(key in value for key in ("code", "message", "details")):
            details = rendered.get("details")
            reasons = _redaction_reasons((value["message"], value["details"]))
            if isinstance(details, dict) and reasons:
                details.update(redacted=True, redaction_reasons=sorted(reasons))
        if all(key in value for key in ("argv", "stderr", "redacted")):
            reasons = _redaction_reasons((value["argv"], value["stderr"], value.get("stdout")))
            if reasons:
                rendered.update(redacted=True, redaction_reasons=sorted(reasons))
        return rendered
    if isinstance(value, (list, tuple)):
        return [_redact(item) for item in value]
    if isinstance(value, str):
        return redact_text(value)
    return value


def _redaction_reasons(value: object) -> set[str]:
    if isinstance(value, str):
        return ({"credential"} if _CREDENTIAL_PATTERN.search(value) else set()) | (
            {"url-userinfo"} if _USERINFO_PATTERN.search(value) else set()
        )
    if isinstance(value, (list, tuple)):
        return set().union(*(_redaction_reasons(item) for item in value))
    if isinstance(value, dict):
        reasons = set().union(*(_redaction_reasons(item) for item in value.values()))
        if any(isinstance(key, str) and key.lower().replace("-", "_") in _SENSITIVE_KEYS for key in value):
            reasons.add("sensitive-field")
        return reasons
    return set()
