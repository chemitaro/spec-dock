from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

POLICY_VERSION = "context-routing-policy-v1"


class AgentRole(str, Enum):
    DEV_CODER = "dev-coder"
    DOC_WRITER = "doc-writer"
    CODE_REVIEWER = "code-reviewer"
    QA_REVIEWER = "qa-reviewer"
    SPEC_REVIEWER = "spec-reviewer"
    CONSULTANT = "consultant"


class ContextMode(str, Enum):
    RECENT_FORK = "recent_fork"
    BOUNDED_PACKET = "bounded_packet"
    CLEAN_ROOM = "clean_room"
    MINIMAL_PACKET = "minimal_packet"


class ReasoningEffort(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAX = "max"


class TaskKind(str, Enum):
    DOCS_ONLY = "docs-only"
    RUNTIME = "runtime"
    MIGRATION = "migration"
    SECURITY_SENSITIVE = "security-sensitive"


REVIEWER_ROLES = frozenset({
    AgentRole.CODE_REVIEWER,
    AgentRole.QA_REVIEWER,
    AgentRole.SPEC_REVIEWER,
})
CONSULTANT_ROLES = frozenset({AgentRole.CONSULTANT})
CLEAN_ROOM_ROLES = REVIEWER_ROLES | CONSULTANT_ROLES

AUTHOR_CONTAMINATION_SOURCES = (
    "author_self_assessment",
    "implementation_transcript",
    "previous_reviewer_verdict",
    "private_reasoning",
    "raw_full_logs",
)
CONSULTANT_FIRST_PASS_EXCLUSIONS = (
    "main_recommendation",
    "architect_recommendation",
)
BOUNDED_RETURN_FIELDS = (
    "summary",
    "changed_files",
    "verification_result",
    "evidence_refs",
    "unresolved_risks",
    "ledger_note",
)


@dataclass(frozen=True)
class AssuranceAuthority:
    authorized_profile: str
    lite_candidate: bool = False


@dataclass(frozen=True)
class StepFacts:
    step_id: str
    title: str
    task_kind: TaskKind | str
    risk_tags: tuple[str, ...] = ()
    source_binding_hash: str = ""
    scope_hash: str = ""

    @property
    def normalized_task_kind(self) -> TaskKind:
        if isinstance(self.task_kind, TaskKind):
            return self.task_kind
        return TaskKind(self.task_kind)


@dataclass(frozen=True)
class ContinuationFacts:
    previous_source_binding_hash: str
    current_source_binding_hash: str
    previous_source_revision: str
    current_source_revision: str
    previous_goal_hash: str
    current_goal_hash: str
    previous_scope_hash: str
    current_scope_hash: str
    previous_allowed_paths_hash: str
    current_allowed_paths_hash: str
    previous_risk_fingerprint: str
    current_risk_fingerprint: str
    current_head_revalidated: bool
    worktree_clean: bool
    files_revalidated: bool


@dataclass(frozen=True)
class ContinuationDecision:
    eligible: bool
    context_mode: ContextMode
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class RoleContextContract:
    role: AgentRole
    context_mode: ContextMode
    include_categories: tuple[str, ...]
    exclude_categories: tuple[str, ...]
    fail_closed_if_unavailable: bool


@dataclass(frozen=True)
class BoundedReturnContract:
    allowed_fields: tuple[str, ...] = BOUNDED_RETURN_FIELDS
    forbidden_fields: tuple[str, ...] = (
        "raw_shell_transcript",
        "private_reasoning",
        "full_test_log",
        "implementation_transcript",
    )


@dataclass(frozen=True)
class StepAssuranceDecision:
    step_id: str
    worker: AgentRole
    reasoning_effort: ReasoningEffort
    context_mode: ContextMode
    verification: tuple[str, ...]
    reviewers: tuple[AgentRole, ...]
    policy_version: str
    return_contract: BoundedReturnContract
    continuation: ContinuationDecision | None = None


@dataclass(frozen=True)
class ContextRoutingPolicy:
    version: str
    routing_matrix: dict[TaskKind, dict[str, Any]]
    reviewer_exclusions: tuple[str, ...]
    consultant_first_pass_exclusions: tuple[str, ...]
    bounded_return_fields: tuple[str, ...]


def default_context_routing_policy() -> ContextRoutingPolicy:
    return ContextRoutingPolicy(
        version=POLICY_VERSION,
        routing_matrix={
            TaskKind.DOCS_ONLY: {
                "worker": AgentRole.DOC_WRITER,
                "reasoning_effort": ReasoningEffort.LOW,
                "context_mode": ContextMode.MINIMAL_PACKET,
                "verification": ("docs_inspection",),
                "reviewers": (AgentRole.SPEC_REVIEWER,),
            },
            TaskKind.RUNTIME: {
                "worker": AgentRole.DEV_CODER,
                "reasoning_effort": ReasoningEffort.MEDIUM,
                "context_mode": ContextMode.RECENT_FORK,
                "verification": ("unit_tests",),
                "reviewers": (AgentRole.CODE_REVIEWER,),
            },
            TaskKind.MIGRATION: {
                "worker": AgentRole.DEV_CODER,
                "reasoning_effort": ReasoningEffort.HIGH,
                "context_mode": ContextMode.BOUNDED_PACKET,
                "verification": ("unit_tests", "integration_tests", "rollback_plan"),
                "reviewers": (AgentRole.CODE_REVIEWER, AgentRole.QA_REVIEWER),
            },
            TaskKind.SECURITY_SENSITIVE: {
                "worker": AgentRole.DEV_CODER,
                "reasoning_effort": ReasoningEffort.MAX,
                "context_mode": ContextMode.BOUNDED_PACKET,
                "verification": ("unit_tests", "security_review", "privacy_review"),
                "reviewers": (AgentRole.CODE_REVIEWER, AgentRole.QA_REVIEWER, AgentRole.SPEC_REVIEWER),
            },
        },
        reviewer_exclusions=AUTHOR_CONTAMINATION_SOURCES,
        consultant_first_pass_exclusions=AUTHOR_CONTAMINATION_SOURCES + CONSULTANT_FIRST_PASS_EXCLUSIONS,
        bounded_return_fields=BOUNDED_RETURN_FIELDS,
    )


def context_routing_policy_from_dict(payload: dict[str, Any]) -> ContextRoutingPolicy:
    version = _require_str(payload, "version")
    if version != POLICY_VERSION:
        raise ValueError(f"unsupported context routing policy version: {version}")
    matrix_payload = payload.get("routing_matrix")
    if not isinstance(matrix_payload, dict):
        raise ValueError("context routing policy requires routing_matrix")

    routing_matrix: dict[TaskKind, dict[str, Any]] = {}
    for task_kind in TaskKind:
        raw_rule = matrix_payload.get(task_kind.value)
        if not isinstance(raw_rule, dict):
            raise ValueError(f"context routing policy missing rule for {task_kind.value}")
        reviewers = tuple(AgentRole(value) for value in _require_str_tuple(raw_rule, "reviewers"))
        non_reviewer_roles = tuple(role.value for role in reviewers if role not in REVIEWER_ROLES)
        if non_reviewer_roles:
            joined_roles = ", ".join(non_reviewer_roles)
            raise ValueError(f"context routing policy has non-reviewer roles in reviewers: {joined_roles}")
        routing_matrix[task_kind] = {
            "worker": AgentRole(_require_str(raw_rule, "worker")),
            "reasoning_effort": ReasoningEffort(_require_str(raw_rule, "reasoning_effort")),
            "context_mode": ContextMode(_require_str(raw_rule, "context_mode")),
            "verification": _require_str_tuple(raw_rule, "verification"),
            "reviewers": reviewers,
        }

    reviewer_exclusions = _require_str_tuple(payload, "reviewer_exclusions")
    for forbidden_source in AUTHOR_CONTAMINATION_SOURCES:
        if forbidden_source not in reviewer_exclusions:
            raise ValueError(f"context routing policy missing reviewer exclusion: {forbidden_source}")

    consultant_first_pass_exclusions = _require_str_tuple(payload, "consultant_first_pass_exclusions")
    for forbidden_source in AUTHOR_CONTAMINATION_SOURCES + CONSULTANT_FIRST_PASS_EXCLUSIONS:
        if forbidden_source not in consultant_first_pass_exclusions:
            raise ValueError(f"context routing policy missing consultant exclusion: {forbidden_source}")

    bounded_return_fields = _require_str_tuple(payload, "bounded_return_fields")
    for field in BOUNDED_RETURN_FIELDS:
        if field not in bounded_return_fields:
            raise ValueError(f"context routing policy missing bounded return field: {field}")
    extra_bounded_return_fields = tuple(sorted(set(bounded_return_fields) - set(BOUNDED_RETURN_FIELDS)))
    if extra_bounded_return_fields:
        extras = ", ".join(extra_bounded_return_fields)
        raise ValueError(f"context routing policy has unsupported bounded return fields: {extras}")

    return ContextRoutingPolicy(
        version=version,
        routing_matrix=routing_matrix,
        reviewer_exclusions=reviewer_exclusions,
        consultant_first_pass_exclusions=consultant_first_pass_exclusions,
        bounded_return_fields=bounded_return_fields,
    )


def decide_step_assurance(
    step_facts: StepFacts,
    assurance_authority: AssuranceAuthority,
    *,
    policy: ContextRoutingPolicy | None = None,
    continuation_facts: ContinuationFacts | None = None,
) -> StepAssuranceDecision:
    effective_policy = policy or default_context_routing_policy()
    rule = effective_policy.routing_matrix[step_facts.normalized_task_kind]
    reasoning_effort = _profile_adjusted_effort(
        rule["reasoning_effort"],
        assurance_authority.authorized_profile,
    )
    context_mode = rule["context_mode"]
    continuation = None
    if continuation_facts is not None:
        continuation = decide_worker_continuation(continuation_facts, base_context_mode=context_mode)
        context_mode = continuation.context_mode

    return StepAssuranceDecision(
        step_id=step_facts.step_id,
        worker=rule["worker"],
        reasoning_effort=reasoning_effort,
        context_mode=context_mode,
        verification=rule["verification"],
        reviewers=rule["reviewers"],
        policy_version=effective_policy.version,
        return_contract=BoundedReturnContract(allowed_fields=effective_policy.bounded_return_fields),
        continuation=continuation,
    )


def decide_worker_continuation(
    facts: ContinuationFacts,
    *,
    base_context_mode: ContextMode = ContextMode.RECENT_FORK,
) -> ContinuationDecision:
    reason_codes: list[str] = []
    if facts.previous_source_binding_hash != facts.current_source_binding_hash:
        reason_codes.append("source_binding_changed")
    if facts.previous_source_revision != facts.current_source_revision:
        reason_codes.append("source_revision_changed")
    if facts.previous_goal_hash != facts.current_goal_hash:
        reason_codes.append("goal_changed")
    if facts.previous_scope_hash != facts.current_scope_hash:
        reason_codes.append("scope_changed")
    if facts.previous_allowed_paths_hash != facts.current_allowed_paths_hash:
        reason_codes.append("allowed_paths_changed")
    if facts.previous_risk_fingerprint != facts.current_risk_fingerprint:
        reason_codes.append("risk_changed")
    if not facts.current_head_revalidated:
        reason_codes.append("current_head_revalidation_failed")
    if not facts.worktree_clean:
        reason_codes.append("worktree_not_clean")
    if not facts.files_revalidated:
        reason_codes.append("file_revalidation_failed")

    if reason_codes:
        return ContinuationDecision(
            eligible=False,
            context_mode=ContextMode.BOUNDED_PACKET,
            reason_codes=tuple(reason_codes),
        )
    return ContinuationDecision(
        eligible=True,
        context_mode=base_context_mode,
        reason_codes=("continuation_revalidated",),
    )


def role_context_contract(
    role: AgentRole | str,
    *,
    policy: ContextRoutingPolicy | None = None,
    consultant_first_pass: bool = False,
) -> RoleContextContract:
    effective_role = AgentRole(role)
    effective_policy = policy or default_context_routing_policy()
    if effective_role in REVIEWER_ROLES:
        return RoleContextContract(
            role=effective_role,
            context_mode=ContextMode.CLEAN_ROOM,
            include_categories=("requirements", "design", "plan", "diff_summary", "evidence_refs"),
            exclude_categories=effective_policy.reviewer_exclusions,
            fail_closed_if_unavailable=True,
        )
    if effective_role == AgentRole.CONSULTANT:
        exclusions = (
            effective_policy.consultant_first_pass_exclusions
            if consultant_first_pass
            else effective_policy.reviewer_exclusions
        )
        return RoleContextContract(
            role=effective_role,
            context_mode=ContextMode.CLEAN_ROOM,
            include_categories=("requirements", "design", "plan", "problem_facts"),
            exclude_categories=exclusions,
            fail_closed_if_unavailable=True,
        )
    return RoleContextContract(
        role=effective_role,
        context_mode=ContextMode.BOUNDED_PACKET,
        include_categories=("requirements", "design", "plan", "allowed_paths", "evidence_refs"),
        exclude_categories=("private_reasoning", "raw_full_logs"),
        fail_closed_if_unavailable=False,
    )


def _profile_adjusted_effort(effort: ReasoningEffort, authorized_profile: str) -> ReasoningEffort:
    if authorized_profile == "critical":
        return ReasoningEffort.MAX
    if authorized_profile == "strict" and effort in {ReasoningEffort.LOW, ReasoningEffort.MEDIUM}:
        return ReasoningEffort.HIGH
    return effort


def _require_str(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"context routing policy requires string field: {key}")
    return value


def _require_str_tuple(payload: dict[str, Any], key: str) -> tuple[str, ...]:
    value = payload.get(key)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"context routing policy requires string list field: {key}")
    return tuple(value)
