from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from typing import Any

from spec_dock_runtime.domain.context_routing import (
    AgentRole,
    AssuranceAuthority,
    ContextMode,
    ContextRoutingPolicy,
    ContinuationFacts,
    ReasoningEffort,
    StepAssuranceDecision,
    StepFacts,
    TaskKind,
    decide_step_assurance,
    default_context_routing_policy,
    role_context_contract,
)

_STEP_HEADING_RE = re.compile(r"^#{2,3}\s+実装ステップ\s+(S\d+)\s+[—-]\s+(.+)$", re.MULTILINE)
_ANY_HEADING_RE = re.compile(r"^#{2,3}\s+", re.MULTILINE)


@dataclass(frozen=True)
class SourceRef:
    path: str
    sha256: str | None
    missing_reason: str | None = None

    def to_payload(self) -> dict[str, str | None]:
        return {"path": self.path, "sha256": self.sha256, "missing_reason": self.missing_reason}


@dataclass(frozen=True)
class StepAssuranceProjection:
    selected_step: dict[str, Any]
    decision: StepAssuranceDecision | None
    policy: ContextRoutingPolicy | None
    policy_status: str
    policy_reason: str
    source_refs: tuple[SourceRef, ...]
    continuation_state: dict[str, str]

    def to_payload(self) -> dict[str, Any]:
        return {
            "selected_step": self.selected_step,
            "policy": {
                "status": self.policy_status,
                "reason": self.policy_reason,
                "version": self.decision.policy_version if self.decision is not None else None,
            },
            "worker": self.decision.worker.value if self.decision is not None else None,
            "reasoning_effort": _reasoning_effort_wire_value(self.decision.reasoning_effort)
            if self.decision is not None
            else None,
            "context_mode": self.decision.context_mode.value
            if self.decision is not None
            else ContextMode.MINIMAL_PACKET.value,
            "verification": list(self.decision.verification) if self.decision is not None else [],
            "reviewers": [role.value for role in self.decision.reviewers] if self.decision is not None else [],
            "return_contract": {
                "allowed_fields": list(self.decision.return_contract.allowed_fields)
                if self.decision is not None
                else [],
                "forbidden_fields": list(self.decision.return_contract.forbidden_fields)
                if self.decision is not None
                else [],
            },
            "continuation": None
            if self.decision is None or self.decision.continuation is None
            else {
                "eligible": self.decision.continuation.eligible,
                "context_mode": self.decision.continuation.context_mode.value,
                "reason_codes": list(self.decision.continuation.reason_codes),
            },
            "continuation_state": self.continuation_state,
            "source_refs": [ref.to_payload() for ref in self.source_refs],
        }


@dataclass(frozen=True)
class ContextPacketProjection:
    written: bool
    refs: tuple[SourceRef, ...]
    invocation_events: tuple[dict[str, Any], ...]
    errors: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, Any]:
        return {
            "written": self.written,
            "refs": [ref.to_payload() for ref in self.refs],
            "invocation_events": list(self.invocation_events),
            "errors": list(self.errors),
        }


def compile_step_assurance_projection(
    *,
    issue_id: str,
    authorized_profile: str,
    lite_candidate: bool,
    plan_text: str | None,
    report_text: str | None,
    source_refs: tuple[SourceRef, ...],
    policy_result: Any,
    continuation_facts: ContinuationFacts | None = None,
    continuation_state: dict[str, str] | None = None,
) -> StepAssuranceProjection:
    selected_step = _select_step(plan_text or "", report_text or "")
    if selected_step["selection_method"] == "issue_wide_default":
        return StepAssuranceProjection(
            selected_step=selected_step,
            decision=None,
            policy=None,
            policy_status=str(getattr(policy_result, "status", "missing")),
            policy_reason=str(getattr(policy_result, "reason", "context_policy_missing")),
            source_refs=source_refs,
            continuation_state=continuation_state or {},
        )
    policy = getattr(policy_result, "policy", None)
    policy_status = str(getattr(policy_result, "status", "missing"))
    policy_reason = str(getattr(policy_result, "reason", "context_policy_missing"))
    if policy is None:
        policy = default_context_routing_policy()
    facts = StepFacts(
        step_id=selected_step["id"],
        title=selected_step["title"],
        task_kind=selected_step["task_kind"],
        risk_tags=tuple(selected_step["risk_tags"]),
        source_binding_hash=_combined_hash(source_refs),
        scope_hash=hashlib.sha256(issue_id.encode("utf-8")).hexdigest(),
    )
    decision = decide_step_assurance(
        facts,
        AssuranceAuthority(authorized_profile=authorized_profile, lite_candidate=lite_candidate),
        policy=policy,
        continuation_facts=continuation_facts,
    )
    if policy_status != "valid":
        decision = StepAssuranceDecision(
            step_id=decision.step_id,
            worker=decision.worker,
            reasoning_effort=decision.reasoning_effort,
            context_mode=ContextMode.BOUNDED_PACKET,
            verification=decision.verification,
            reviewers=decision.reviewers,
            policy_version=decision.policy_version,
            return_contract=decision.return_contract,
            continuation=decision.continuation,
        )
    return StepAssuranceProjection(
        selected_step=selected_step,
        decision=decision,
        policy=policy,
        policy_status=policy_status,
        policy_reason=policy_reason,
        source_refs=source_refs,
        continuation_state=continuation_state or {},
    )


def compile_context_packet_projection(
    *,
    step_projection: StepAssuranceProjection,
    packet_store: Any,
) -> ContextPacketProjection:
    payload = _packet_payload(step_projection)
    write_result = packet_store.write_current(payload)
    refs = tuple(
        SourceRef(path=str(ref["path"]), sha256=_as_optional_str(ref.get("sha256"))) for ref in write_result.refs
    )
    if not write_result.written:
        refs = (
            SourceRef(
                path="spec-dock/.agent/context-packets/current-context-packets.json",
                sha256=None,
                missing_reason="write_failed",
            ),
        )
    return ContextPacketProjection(
        written=write_result.written,
        refs=refs,
        invocation_events=tuple(payload["invocation_events"]),
        errors=tuple(write_result.errors),
    )


def _packet_payload(step_projection: StepAssuranceProjection) -> dict[str, Any]:
    step_payload = step_projection.to_payload()
    decision = step_projection.decision
    if decision is None:
        return {
            "schema_version": "context-packet-projection-v1",
            "step_assurance": step_payload,
            "continuation_state": step_projection.continuation_state,
            "packets": [],
            "invocation_events": [],
        }
    roles = (decision.worker, *decision.reviewers)
    packets: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    for role in roles:
        contract = role_context_contract(role, policy=step_projection.policy)
        missing_reason = None
        context_mode = contract.context_mode
        if step_projection.policy_status != "valid" and contract.fail_closed_if_unavailable:
            missing_reason = step_projection.policy_reason
        elif role == decision.worker:
            context_mode = decision.context_mode
        event = _invocation_event(
            role=role,
            reasoning_effort=_reasoning_effort_wire_value(decision.reasoning_effort),
            context_mode=context_mode.value,
            step_projection=step_projection,
            policy_version=decision.policy_version,
            include_categories=contract.include_categories,
            exclude_categories=contract.exclude_categories,
            missing_reason=missing_reason,
        )
        events.append(event)
        if missing_reason is None:
            packets.append({
                "role": role.value,
                "step_assurance": step_payload,
                "context_mode": context_mode.value,
                "include_categories": list(contract.include_categories),
                "exclude_categories": list(contract.exclude_categories),
                "returned_evidence_refs": event["returned_evidence_refs"],
            })
    return {
        "schema_version": "context-packet-projection-v1",
        "step_assurance": step_payload,
        "continuation_state": step_projection.continuation_state,
        "packets": packets,
        "invocation_events": events,
    }


def _invocation_event(
    *,
    role: AgentRole,
    reasoning_effort: str,
    context_mode: str,
    step_projection: StepAssuranceProjection,
    policy_version: str,
    include_categories: tuple[str, ...],
    exclude_categories: tuple[str, ...],
    missing_reason: str | None,
) -> dict[str, Any]:
    packet_hash = None
    if missing_reason is None:
        packet_hash = hashlib.sha256(
            "|".join((
                role.value,
                reasoning_effort,
                context_mode,
                policy_version,
                _combined_hash(step_projection.source_refs),
            )).encode("utf-8")
        ).hexdigest()
    return {
        "role": role.value,
        "reasoning_effort": reasoning_effort,
        "context_mode": context_mode,
        "policy_version": policy_version,
        "packet_hash": packet_hash,
        "source_hashes": [ref.to_payload() for ref in step_projection.source_refs],
        "fork_turn_count": 0,
        "include_categories": list(include_categories),
        "exclude_categories": list(exclude_categories),
        "returned_evidence_refs": [ref.to_payload() for ref in step_projection.source_refs],
        "missing_reason": missing_reason,
    }


def _reasoning_effort_wire_value(reasoning_effort: ReasoningEffort) -> str:
    if reasoning_effort == ReasoningEffort.MAX:
        return "xhigh"
    return reasoning_effort.value


def _select_step(plan_text: str, report_text: str) -> dict[str, Any]:
    matches = list(_STEP_HEADING_RE.finditer(plan_text))
    completed_ids = _completed_step_ids(report_text)
    all_heading_starts = [heading.start() for heading in _ANY_HEADING_RE.finditer(plan_text)]
    for match in matches:
        step_id = match.group(1)
        if step_id in {"S90", "S99"} or step_id in completed_ids:
            continue
        block_end = next((start for start in all_heading_starts if start > match.start()), len(plan_text))
        block = plan_text[match.start() : block_end]
        task_kind, risk_tags = _classify_task_kind(block)
        return {
            "id": step_id,
            "title": match.group(2).strip(),
            "task_kind": task_kind.value,
            "risk_tags": list(risk_tags),
            "selection_method": "plan_first_uncompleted_heading",
        }
    return {
        "id": "issue-wide",
        "title": "Issue-wide default",
        "task_kind": TaskKind.RUNTIME.value,
        "risk_tags": [],
        "selection_method": "issue_wide_default",
    }


def _completed_step_ids(report_text: str) -> set[str]:
    completed_ids: set[str] = set()
    session_matches = list(re.finditer(r"^###\s+セッションログ（[^\n]*$", report_text, re.MULTILINE))
    heading_starts = [heading.start() for heading in re.finditer(r"^###\s+", report_text, re.MULTILINE)]
    for match in session_matches:
        block_end = next((start for start in heading_starts if start > match.start()), len(report_text))
        block = report_text[match.start() : block_end]
        for step_id in _session_step_ids(match.group(0), block):
            if _block_has_completed_step_row(block, step_id):
                completed_ids.add(step_id)
        completed_ids.update(_completed_step_rows(block))
    return completed_ids


def _session_step_ids(heading: str, block: str) -> set[str]:
    step_ids = set(re.findall(r"\bS\d+\b", heading))
    target_match = re.search(r"^####\s+対象\s*$", block, re.MULTILINE)
    if target_match is None:
        return step_ids
    next_section = re.search(r"^####\s+", block[target_match.end() :], re.MULTILINE)
    target_end = target_match.end() + next_section.start() if next_section is not None else len(block)
    step_ids.update(re.findall(r"\bS\d+\b", block[target_match.end() : target_end]))
    return step_ids


def _completed_step_rows(block: str) -> set[str]:
    completed_ids: set[str] = set()
    completed_values = {"pass", "passed", "committed", "approved-no-op"}
    incomplete_values = {"fail", "failed", "blocked"}
    in_completion_section = False
    for line in block.splitlines():
        stripped = line.strip()
        lowered = stripped.lower()
        if lowered.startswith("####"):
            in_completion_section = _is_completion_section(stripped, lowered)
            continue
        if not in_completion_section or not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip().lower() for cell in stripped.strip("|").split("|")]
        if not cells or not re.fullmatch(r"s\d+", cells[0]):
            continue
        if any(cell in incomplete_values for cell in cells):
            continue
        if any(cell in completed_values for cell in cells):
            completed_ids.add(cells[0].upper())
    return completed_ids


def _is_completion_section(stripped: str, lowered: str) -> bool:
    return (
        "ステップ契約の完了証跡" in stripped
        or "step contract closure" in lowered
        or "ステップ commit" in lowered
        or "step commit gate" in lowered
    )


def _block_has_completed_step_row(block: str, step_id: str) -> bool:
    completed_values = {"pass", "passed", "committed", "approved-no-op"}
    incomplete_values = {"fail", "failed", "blocked"}
    normalized_step_id = step_id.lower()
    in_completion_section = False
    for line in block.splitlines():
        stripped = line.strip()
        lowered = stripped.lower()
        if lowered.startswith("####"):
            in_completion_section = _is_completion_section(stripped, lowered)
            continue
        if not in_completion_section:
            continue
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip().lower() for cell in stripped.strip("|").split("|")]
        if not cells or cells[0] != normalized_step_id:
            continue
        if any(cell in incomplete_values for cell in cells):
            return False
        if any(cell in completed_values for cell in cells):
            return True
    return False


def _classify_task_kind(text: str) -> tuple[TaskKind, tuple[str, ...]]:
    lowered = text.lower()
    if "security" in lowered or "privacy" in lowered:
        return TaskKind.SECURITY_SENSITIVE, ("security",)
    if "migration" in lowered or "rollback" in lowered:
        return TaskKind.MIGRATION, ("migration",)
    if "docs-only" in lowered or "docs impact" in lowered or "doc-writer" in lowered:
        return TaskKind.DOCS_ONLY, ("docs",)
    return TaskKind.RUNTIME, ("runtime",)


def _combined_hash(refs: tuple[SourceRef, ...]) -> str:
    material = "|".join(f"{ref.path}:{ref.sha256 or ref.missing_reason or ''}" for ref in refs)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _as_optional_str(value: object) -> str | None:
    if isinstance(value, str):
        return value
    return None
