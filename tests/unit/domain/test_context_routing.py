from __future__ import annotations

import json
from pathlib import Path
import sys


def _context_routing_module():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.domain import context_routing
    finally:
        sys.path.pop(0)
    return context_routing


def _continuation_facts(context_routing, **overrides):
    values = {
        "previous_source_binding_hash": "binding-a",
        "current_source_binding_hash": "binding-a",
        "previous_source_revision": "rev-a",
        "current_source_revision": "rev-a",
        "previous_goal_hash": "goal-a",
        "current_goal_hash": "goal-a",
        "previous_scope_hash": "scope-a",
        "current_scope_hash": "scope-a",
        "previous_allowed_paths_hash": "paths-a",
        "current_allowed_paths_hash": "paths-a",
        "previous_risk_fingerprint": "risk-a",
        "current_risk_fingerprint": "risk-a",
        "current_head_revalidated": True,
        "worktree_clean": True,
        "files_revalidated": True,
    }
    values.update(overrides)
    return context_routing.ContinuationFacts(**values)


def test_policy_json_matches_domain_routing_matrix_for_step_kinds() -> None:
    context_routing = _context_routing_module()
    policy_path = (
        Path(__file__).resolve().parents[3]
        / "src"
        / "spec_dock"
        / "assets"
        / "spec_dock"
        / "system"
        / "assurance"
        / "context-routing-policy.json"
    )
    policy = context_routing.context_routing_policy_from_dict(json.loads(policy_path.read_text()))
    authority = context_routing.AssuranceAuthority(authorized_profile="standard")

    cases = {
        context_routing.TaskKind.DOCS_ONLY: (
            context_routing.AgentRole.DOC_WRITER,
            context_routing.ReasoningEffort.LOW,
            context_routing.ContextMode.MINIMAL_PACKET,
            ("docs_inspection",),
            (context_routing.AgentRole.SPEC_REVIEWER,),
        ),
        context_routing.TaskKind.RUNTIME: (
            context_routing.AgentRole.DEV_CODER,
            context_routing.ReasoningEffort.MEDIUM,
            context_routing.ContextMode.RECENT_FORK,
            ("unit_tests",),
            (context_routing.AgentRole.CODE_REVIEWER,),
        ),
        context_routing.TaskKind.MIGRATION: (
            context_routing.AgentRole.DEV_CODER,
            context_routing.ReasoningEffort.HIGH,
            context_routing.ContextMode.BOUNDED_PACKET,
            ("unit_tests", "integration_tests", "rollback_plan"),
            (context_routing.AgentRole.CODE_REVIEWER, context_routing.AgentRole.QA_REVIEWER),
        ),
        context_routing.TaskKind.SECURITY_SENSITIVE: (
            context_routing.AgentRole.DEV_CODER,
            context_routing.ReasoningEffort.MAX,
            context_routing.ContextMode.BOUNDED_PACKET,
            ("unit_tests", "security_review", "privacy_review"),
            (
                context_routing.AgentRole.CODE_REVIEWER,
                context_routing.AgentRole.QA_REVIEWER,
                context_routing.AgentRole.SPEC_REVIEWER,
            ),
        ),
    }

    for task_kind, expected in cases.items():
        decision = context_routing.decide_step_assurance(
            context_routing.StepFacts(
                step_id=f"S-{task_kind.value}",
                title=task_kind.value,
                task_kind=task_kind,
                source_binding_hash="binding-a",
                scope_hash="scope-a",
            ),
            authority,
            policy=policy,
        )
        assert (
            decision.worker,
            decision.reasoning_effort,
            decision.context_mode,
            decision.verification,
            decision.reviewers,
        ) == expected
        assert decision.return_contract.allowed_fields == (
            "summary",
            "changed_files",
            "verification_result",
            "evidence_refs",
            "unresolved_risks",
            "ledger_note",
        )
        assert "raw_shell_transcript" in decision.return_contract.forbidden_fields


def test_worker_continuation_requires_same_context_and_bounded_revalidation() -> None:
    context_routing = _context_routing_module()

    allowed = context_routing.decide_worker_continuation(_continuation_facts(context_routing))
    assert allowed.eligible
    assert allowed.context_mode == context_routing.ContextMode.RECENT_FORK
    assert allowed.reason_codes == ("continuation_revalidated",)

    changed = context_routing.decide_worker_continuation(
        _continuation_facts(
            context_routing,
            current_source_binding_hash="binding-b",
            current_source_revision="rev-b",
            current_goal_hash="goal-b",
            current_scope_hash="scope-b",
            current_allowed_paths_hash="paths-b",
            current_risk_fingerprint="risk-b",
            current_head_revalidated=False,
            worktree_clean=False,
            files_revalidated=False,
        )
    )
    assert not changed.eligible
    assert changed.context_mode == context_routing.ContextMode.BOUNDED_PACKET
    assert changed.reason_codes == (
        "source_binding_changed",
        "source_revision_changed",
        "goal_changed",
        "scope_changed",
        "allowed_paths_changed",
        "risk_changed",
        "current_head_revalidation_failed",
        "worktree_not_clean",
        "file_revalidation_failed",
    )

    decision = context_routing.decide_step_assurance(
        context_routing.StepFacts(step_id="S01", title="runtime", task_kind="runtime"),
        context_routing.AssuranceAuthority(authorized_profile="standard"),
        continuation_facts=_continuation_facts(context_routing, files_revalidated=False),
    )
    assert decision.context_mode == context_routing.ContextMode.BOUNDED_PACKET
    assert decision.continuation is not None
    assert not decision.continuation.eligible


def test_reviewer_and_consultant_clean_room_exclusions_are_fail_closed() -> None:
    context_routing = _context_routing_module()
    forbidden_sources = {
        "author_self_assessment",
        "implementation_transcript",
        "previous_reviewer_verdict",
        "private_reasoning",
        "raw_full_logs",
    }

    for role in (
        context_routing.AgentRole.CODE_REVIEWER,
        context_routing.AgentRole.QA_REVIEWER,
        context_routing.AgentRole.SPEC_REVIEWER,
    ):
        contract = context_routing.role_context_contract(role)
        assert contract.context_mode == context_routing.ContextMode.CLEAN_ROOM
        assert contract.fail_closed_if_unavailable
        assert forbidden_sources.issubset(contract.exclude_categories)

    consultant = context_routing.role_context_contract(
        context_routing.AgentRole.CONSULTANT,
        consultant_first_pass=True,
    )
    assert consultant.context_mode == context_routing.ContextMode.CLEAN_ROOM
    assert consultant.fail_closed_if_unavailable
    assert forbidden_sources.issubset(consultant.exclude_categories)
    assert "main_recommendation" in consultant.exclude_categories
    assert "architect_recommendation" in consultant.exclude_categories

    worker = context_routing.role_context_contract(context_routing.AgentRole.DEV_CODER)
    assert worker.context_mode == context_routing.ContextMode.BOUNDED_PACKET
    assert not worker.fail_closed_if_unavailable


def test_policy_parser_rejects_unsupported_policy_versions() -> None:
    context_routing = _context_routing_module()
    policy_path = (
        Path(__file__).resolve().parents[3]
        / "src"
        / "spec_dock"
        / "assets"
        / "spec_dock"
        / "system"
        / "assurance"
        / "context-routing-policy.json"
    )
    payload = json.loads(policy_path.read_text())
    payload["version"] = "context-routing-policy-v999"

    try:
        context_routing.context_routing_policy_from_dict(payload)
    except ValueError as exc:
        assert str(exc) == "unsupported context routing policy version: context-routing-policy-v999"
    else:
        raise AssertionError("unsupported policy version was accepted")


def test_policy_parser_rejects_bounded_return_supersets() -> None:
    context_routing = _context_routing_module()
    policy_path = (
        Path(__file__).resolve().parents[3]
        / "src"
        / "spec_dock"
        / "assets"
        / "spec_dock"
        / "system"
        / "assurance"
        / "context-routing-policy.json"
    )
    payload = json.loads(policy_path.read_text())
    payload["bounded_return_fields"] = [*payload["bounded_return_fields"], "raw_shell_transcript"]

    try:
        context_routing.context_routing_policy_from_dict(payload)
    except ValueError as exc:
        assert str(exc) == "context routing policy has unsupported bounded return fields: raw_shell_transcript"
    else:
        raise AssertionError("bounded return policy superset was accepted")


def test_policy_parser_rejects_non_reviewer_roles_in_reviewers() -> None:
    context_routing = _context_routing_module()
    policy_path = (
        Path(__file__).resolve().parents[3]
        / "src"
        / "spec_dock"
        / "assets"
        / "spec_dock"
        / "system"
        / "assurance"
        / "context-routing-policy.json"
    )
    payload = json.loads(policy_path.read_text())
    payload["routing_matrix"]["runtime"]["reviewers"] = ["dev-coder"]

    try:
        context_routing.context_routing_policy_from_dict(payload)
    except ValueError as exc:
        assert str(exc) == "context routing policy has non-reviewer roles in reviewers: dev-coder"
    else:
        raise AssertionError("non-reviewer role was accepted in reviewers")


def test_policy_parser_rejects_reviewer_roles_in_worker() -> None:
    context_routing = _context_routing_module()
    policy_path = (
        Path(__file__).resolve().parents[3]
        / "src"
        / "spec_dock"
        / "assets"
        / "spec_dock"
        / "system"
        / "assurance"
        / "context-routing-policy.json"
    )
    payload = json.loads(policy_path.read_text())
    payload["routing_matrix"]["runtime"]["worker"] = "code-reviewer"

    try:
        context_routing.context_routing_policy_from_dict(payload)
    except ValueError as exc:
        assert str(exc) == "context routing policy has non-worker role in worker: code-reviewer"
    else:
        raise AssertionError("reviewer role was accepted as worker")
