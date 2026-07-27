from dataclasses import FrozenInstanceError
import hashlib
import json
from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
)
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))

from spec_dock_runtime.domain.issue_planning_contracts import (  # noqa: E402
    IssueCandidateIdentity,
    PlanningCommandResult,
    PlanningContext,
    PlanningHumanDecisionV1,
    PlanningReviewFinding,
    PlanningReviewResult,
    PlanningRevisionRequestV1,
    ReviewedPlanningIdentity,
)

HEAD = "a" * 40
ZIP_SHA = "b" * 64
PATHS = (
    "spec-dock/initiatives/init-one/epics/epic-one/issues/iss-one/design.md",
    "spec-dock/initiatives/init-one/epics/epic-one/issues/iss-one/plan.md",
    "spec-dock/initiatives/init-one/epics/epic-one/issues/iss-one/requirement.md",
)


def _candidate(**overrides):
    values = {
        "issue_id": "iss-00003",
        "candidate_id": "candidate-1",
        "version": 1,
        "logical_filename": "candidate.zip",
        "observed_transport_filename": "candidate (1).zip",
        "internal_root": "candidate-root",
        "source_repository": "owner/repo",
        "source_branch": "feature/issue",
        "source_head": HEAD,
        "zip_sha256": ZIP_SHA,
    }
    values.update(overrides)
    return IssueCandidateIdentity(**values)


def _archive_identity(candidate=None):
    candidate = candidate or _candidate()
    return ReviewedPlanningIdentity(
        mode="archive-candidate",
        issue_id=candidate.issue_id,
        repository=candidate.source_repository,
        branch=candidate.source_branch,
        source_head=candidate.source_head,
        candidate_identity=candidate,
    )


def _git_identity():
    return ReviewedPlanningIdentity(
        mode="git-bound",
        issue_id="iss-00003",
        repository="owner/repo",
        branch="feature/issue",
        source_head=HEAD,
        canonical_target_paths=PATHS,
        expected_canonical_target_paths=PATHS,
    )


def _finding(finding_id: str, severity: str):
    return PlanningReviewFinding(
        id=finding_id,
        severity=severity,
        exact_location="design.md:1",
        violated_requirement_or_contradiction="REQ-001",
        concrete_impact="contract mismatch",
    )


def _review(identity=None, findings=()):
    identity = identity or _archive_identity()
    findings = tuple(findings)
    return PlanningReviewResult(
        reviewed_identity=identity,
        reviewed_identity_sha256=identity.sha256,
        verdict="fail" if any(item.severity in ("p0", "p1") for item in findings) else "pass",
        findings=findings,
    )


def _json_bytes(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()


def test_planning_context_is_immutable_and_has_exact_path_order() -> None:
    context = PlanningContext(
        issue_id="iss-00003",
        repository="owner/repo",
        branch="feature/issue",
        source_head=HEAD,
        parent_epic_id="epic-00002",
        parent_initiative_id="init-00001",
        dependency_summary=("iss-00001:done",),
        canonical_issue_paths=PATHS,
        relevant_source_paths=("src/example.py",),
        operator_context=("preserve scope",),
    )
    assert tuple(context.to_dict()) == (
        "issue_id",
        "repository",
        "branch",
        "source_head",
        "parent_epic_id",
        "parent_initiative_id",
        "dependency_summary",
        "canonical_issue_paths",
        "relevant_source_paths",
        "operator_context",
    )
    with pytest.raises(FrozenInstanceError):
        context.issue_id = "iss-00004"


@pytest.mark.parametrize(
    "overrides",
    [
        {"source_head": "A" * 40},
        {"canonical_issue_paths": tuple(reversed(PATHS))},
        {"canonical_issue_paths": (PATHS[0], PATHS[1], PATHS[1])},
        {"issue_id": "epic-00003"},
    ],
)
def test_planning_context_rejects_malformed_identity(overrides) -> None:
    values = {
        "issue_id": "iss-00003",
        "repository": "owner/repo",
        "branch": "feature/issue",
        "source_head": HEAD,
        "parent_epic_id": "epic-00002",
        "parent_initiative_id": "init-00001",
        "dependency_summary": (),
        "canonical_issue_paths": PATHS,
        "relevant_source_paths": (),
        "operator_context": (),
    }
    values.update(overrides)
    with pytest.raises(ValueError):
        PlanningContext(**values)


def test_candidate_identity_accepts_closed_transport_alias_and_round_trips() -> None:
    candidate = _candidate()
    assert IssueCandidateIdentity.from_json_bytes(_json_bytes(candidate.to_dict())) == candidate


@pytest.mark.parametrize(
    "overrides",
    [
        {"observed_transport_filename": "renamed.zip"},
        {"internal_root": "../candidate"},
        {"source_head": "A" * 40},
        {"zip_sha256": "x" * 64},
        {"version": 0},
        {"version": False},
    ],
)
def test_candidate_identity_rejects_unsafe_or_ambiguous_values(overrides) -> None:
    with pytest.raises(ValueError):
        _candidate(**overrides)


def test_reviewed_identity_closes_archive_and_git_bound_modes() -> None:
    archive = _archive_identity()
    git_bound = _git_identity()
    assert ReviewedPlanningIdentity.from_dict(archive.to_dict()).sha256 == archive.sha256
    assert ReviewedPlanningIdentity.from_dict(
        git_bound.to_dict(),
        expected_canonical_target_paths=PATHS,
    ).sha256 == git_bound.sha256
    assert archive.sha256 == ReviewedPlanningIdentity.from_dict(
        dict(reversed(list(archive.to_dict().items())))
    ).sha256


def test_reviewed_identity_rejects_mode_mismatch() -> None:
    with pytest.raises(ValueError, match="requires only"):
        ReviewedPlanningIdentity(
            mode="archive-candidate",
            issue_id="iss-00003",
            repository="owner/repo",
            branch="feature/issue",
            source_head=HEAD,
            candidate_identity=_candidate(),
            canonical_target_paths=PATHS,
        )
    with pytest.raises(ValueError, match="does not match"):
        ReviewedPlanningIdentity(
            mode="archive-candidate",
            issue_id="iss-00004",
            repository="owner/repo",
            branch="feature/issue",
            source_head=HEAD,
            candidate_identity=_candidate(),
        )


def test_git_bound_identity_rejects_cross_issue_canonical_tuple() -> None:
    other_issue_paths = tuple(path.replace("iss-one", "iss-other") for path in PATHS)
    with pytest.raises(ValueError, match="canonical target"):
        ReviewedPlanningIdentity(
            mode="git-bound",
            issue_id="iss-00003",
            repository="owner/repo",
            branch="feature/issue",
            source_head=HEAD,
            canonical_target_paths=other_issue_paths,
            expected_canonical_target_paths=PATHS,
        )


@pytest.mark.parametrize(
    "payload",
    [
        b'{"issue_id":"iss-00003","issue_id":"iss-00004"}',
        b'{"value":NaN}',
        b'[]',
    ],
)
def test_strict_json_rejects_duplicates_nonstandard_numbers_and_non_object_roots(payload) -> None:
    with pytest.raises(ValueError):
        IssueCandidateIdentity.from_json_bytes(payload)


def test_strict_json_rejects_unknown_top_level_and_nested_keys() -> None:
    candidate = _candidate().to_dict()
    candidate["unknown"] = True
    with pytest.raises(ValueError, match="unknown keys"):
        IssueCandidateIdentity.from_json_bytes(_json_bytes(candidate))

    identity = _archive_identity().to_dict()
    identity["candidate_identity"]["unknown"] = True
    with pytest.raises(ValueError, match="unknown keys"):
        ReviewedPlanningIdentity.from_json_bytes(_json_bytes(identity))


@pytest.mark.parametrize(
    ("severities", "verdict"),
    [
        ((), "pass"),
        (("p2", "p3"), "pass"),
        (("p0",), "fail"),
        (("p1", "p2"), "fail"),
    ],
)
def test_review_verdict_is_derived_from_p0_p1_only(severities, verdict) -> None:
    identity = _archive_identity()
    findings = tuple(_finding(f"F-{index}", severity) for index, severity in enumerate(severities))
    result = PlanningReviewResult(
        reviewed_identity=identity,
        reviewed_identity_sha256=identity.sha256,
        verdict=verdict,
        findings=findings,
    )
    assert result.verdict == verdict


def test_review_rejects_duplicate_findings_and_verdict_contradiction() -> None:
    identity = _archive_identity()
    finding = _finding("F-1", "p1")
    with pytest.raises(ValueError, match="unique"):
        PlanningReviewResult(identity, identity.sha256, "fail", (finding, finding))
    with pytest.raises(ValueError, match="contradicts"):
        PlanningReviewResult(identity, identity.sha256, "pass", (finding,))


def test_review_json_rejects_wrong_identity_digest() -> None:
    payload = _review().to_dict()
    payload["reviewed_identity_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="digest mismatch"):
        PlanningReviewResult.from_json_bytes(_json_bytes(payload))


def test_semantic_revision_accepts_only_bound_p0_p1_findings() -> None:
    review = _review(findings=(_finding("P1-1", "p1"),))
    review_bytes = _json_bytes(review.to_dict())
    request = PlanningRevisionRequestV1(
        schema_version=1,
        lane="semantic",
        candidate_identity=_candidate(),
        preserve_assumptions=("keep command family",),
        finding_ids=("P1-1",),
        review_result_sha256=hashlib.sha256(review_bytes).hexdigest(),
    )
    request.validate_against(review, review_bytes)


@pytest.mark.parametrize(
    "selected",
    [
        ("P2-1",),
        ("P1-1", "P2-1"),
        ("UNKNOWN",),
    ],
)
def test_semantic_revision_rejects_nonblocking_mixed_and_unknown_findings(selected) -> None:
    review = _review(findings=(_finding("P1-1", "p1"), _finding("P2-1", "p2")))
    review_bytes = _json_bytes(review.to_dict())
    request = PlanningRevisionRequestV1(
        schema_version=1,
        lane="semantic",
        candidate_identity=_candidate(),
        preserve_assumptions=(),
        finding_ids=selected,
        review_result_sha256=hashlib.sha256(review_bytes).hexdigest(),
    )
    with pytest.raises(ValueError):
        request.validate_against(review, review_bytes)


def test_semantic_revision_rejects_raw_bytes_candidate_and_mode_mismatch() -> None:
    review = _review(findings=(_finding("P1-1", "p1"),))
    review_bytes = _json_bytes(review.to_dict())
    request = PlanningRevisionRequestV1(
        schema_version=1,
        lane="semantic",
        candidate_identity=_candidate(),
        preserve_assumptions=(),
        finding_ids=("P1-1",),
        review_result_sha256=hashlib.sha256(review_bytes).hexdigest(),
    )
    with pytest.raises(ValueError, match="raw bytes"):
        request.validate_against(review, review_bytes + b"\n")

    wrong_candidate_request = PlanningRevisionRequestV1(
        schema_version=1,
        lane="semantic",
        candidate_identity=_candidate(candidate_id="candidate-2"),
        preserve_assumptions=(),
        finding_ids=("P1-1",),
        review_result_sha256=hashlib.sha256(review_bytes).hexdigest(),
    )
    with pytest.raises(ValueError, match="archive Candidate"):
        wrong_candidate_request.validate_against(review, review_bytes)

    git_review = _review(identity=_git_identity(), findings=(_finding("P1-1", "p1"),))
    git_bytes = _json_bytes(git_review.to_dict())
    wrong_mode_request = PlanningRevisionRequestV1(
        schema_version=1,
        lane="semantic",
        candidate_identity=_candidate(),
        preserve_assumptions=(),
        finding_ids=("P1-1",),
        review_result_sha256=hashlib.sha256(git_bytes).hexdigest(),
    )
    with pytest.raises(ValueError, match="archive"):
        wrong_mode_request.validate_against(git_review, git_bytes)


def test_semantic_revision_rejects_object_not_parsed_from_exact_review_bytes() -> None:
    review_object = _review(findings=(_finding("P1-OBJECT", "p1"),))
    review_from_bytes = _review(findings=())
    review_bytes = _json_bytes(review_from_bytes.to_dict())
    request = PlanningRevisionRequestV1(
        schema_version=1,
        lane="semantic",
        candidate_identity=_candidate(),
        preserve_assumptions=(),
        finding_ids=("P1-OBJECT",),
        review_result_sha256=hashlib.sha256(review_bytes).hexdigest(),
    )
    with pytest.raises(ValueError, match="exact Review result bytes"):
        request.validate_against(review_object, review_bytes)


def test_revision_json_rejects_duplicate_unknown_and_cross_lane_fields() -> None:
    candidate_json = json.dumps(_candidate().to_dict(), separators=(",", ":"))
    duplicate = (
        '{"schema_version":1,"lane":"semantic","lane":"mechanical",'
        f'"candidate_identity":{candidate_json},"preserve_assumptions":[],'
        f'"finding_ids":["P1-1"],"review_result_sha256":"{"c" * 64}"'
        "}"
    ).encode()
    with pytest.raises(ValueError, match="duplicate"):
        PlanningRevisionRequestV1.from_json_bytes(duplicate)

    semantic = {
        "schema_version": 1,
        "lane": "semantic",
        "candidate_identity": _candidate().to_dict(),
        "preserve_assumptions": [],
        "finding_ids": ["P1-1"],
        "review_result_sha256": "c" * 64,
        "target_file": "design.md",
    }
    with pytest.raises(ValueError, match="unknown keys"):
        PlanningRevisionRequestV1.from_json_bytes(_json_bytes(semantic))


def test_mechanical_revision_closes_structure_without_mutation() -> None:
    request = PlanningRevisionRequestV1(
        schema_version=1,
        lane="mechanical",
        candidate_identity=_candidate(),
        preserve_assumptions=(),
        target_file="design.md",
        old_text="old",
        new_text="new",
        meaning_invariant="meaning unchanged",
        diff_budget=1,
    )
    assert request.target_file == "design.md"


@pytest.mark.parametrize(
    "overrides",
    [
        {"target_file": "notes.md"},
        {"old_text": ""},
        {"new_text": "old"},
        {"meaning_invariant": ""},
        {"diff_budget": 0},
        {"diff_budget": False},
    ],
)
def test_mechanical_revision_rejects_open_or_unbounded_fields(overrides) -> None:
    values = {
        "schema_version": 1,
        "lane": "mechanical",
        "candidate_identity": _candidate(),
        "preserve_assumptions": (),
        "target_file": "design.md",
        "old_text": "old",
        "new_text": "new",
        "meaning_invariant": "meaning unchanged",
        "diff_budget": 1,
    }
    values.update(overrides)
    with pytest.raises(ValueError):
        PlanningRevisionRequestV1(**values)


@pytest.mark.parametrize("decision", ["approved", "rejected"])
@pytest.mark.parametrize("plan_adoption", [False, True])
@pytest.mark.parametrize("implementation_start", [False, True])
def test_human_decision_truth_table(decision, plan_adoption, implementation_start) -> None:
    identity = _archive_identity()
    expected_valid = (decision, plan_adoption, implementation_start) in {
        ("approved", True, True),
        ("rejected", False, False),
    }
    kwargs = {
        "schema_version": 1,
        "issue_id": identity.issue_id,
        "reviewed_identity": identity,
        "reviewed_identity_sha256": identity.sha256,
        "review_result_sha256": "c" * 64,
        "decision": decision,
        "plan_adoption": plan_adoption,
        "implementation_start": implementation_start,
        "decided_at": "2026-07-28T12:00:00+09:00",
    }
    if expected_valid:
        assert PlanningHumanDecisionV1(**kwargs).decision == decision
    else:
        with pytest.raises(ValueError, match="truth table"):
            PlanningHumanDecisionV1(**kwargs)


def test_human_decision_binds_identity_and_exact_review_bytes() -> None:
    identity = _archive_identity()
    review = _review(identity=identity)
    review_bytes = _json_bytes(review.to_dict())
    payload = {
        "schema_version": 1,
        "issue_id": identity.issue_id,
        "reviewed_identity": identity.to_dict(),
        "reviewed_identity_sha256": identity.sha256,
        "review_result_sha256": hashlib.sha256(review_bytes).hexdigest(),
        "decision": "approved",
        "plan_adoption": True,
        "implementation_start": True,
        "decided_at": "2026-07-28T12:00:00Z",
    }
    assert PlanningHumanDecisionV1.from_json_bytes(
        _json_bytes(payload),
        review_result_bytes=review_bytes,
    ).decision == "approved"
    with pytest.raises(ValueError, match="raw bytes"):
        PlanningHumanDecisionV1.from_json_bytes(
            _json_bytes(payload),
            review_result_bytes=json.dumps(review.to_dict(), indent=2).encode(),
        )
    payload["reviewed_identity_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="identity digest"):
        PlanningHumanDecisionV1.from_json_bytes(
            _json_bytes(payload),
            review_result_bytes=review_bytes,
        )


def test_human_decision_rejects_cross_candidate_review_bytes() -> None:
    decision_identity = _archive_identity()
    other_identity = _archive_identity(_candidate(candidate_id="candidate-2"))
    other_review_bytes = _json_bytes(_review(identity=other_identity).to_dict())
    payload = {
        "schema_version": 1,
        "issue_id": decision_identity.issue_id,
        "reviewed_identity": decision_identity.to_dict(),
        "reviewed_identity_sha256": decision_identity.sha256,
        "review_result_sha256": hashlib.sha256(other_review_bytes).hexdigest(),
        "decision": "approved",
        "plan_adoption": True,
        "implementation_start": True,
        "decided_at": "2026-07-28T12:00:00Z",
    }
    with pytest.raises(ValueError, match="Review identity"):
        PlanningHumanDecisionV1.from_json_bytes(
            _json_bytes(payload),
            review_result_bytes=other_review_bytes,
        )


def test_human_decision_rejects_cross_issue_review_bytes() -> None:
    decision_identity = _archive_identity()
    other_identity = _archive_identity(_candidate(issue_id="iss-00004"))
    other_review_bytes = _json_bytes(_review(identity=other_identity).to_dict())
    payload = {
        "schema_version": 1,
        "issue_id": decision_identity.issue_id,
        "reviewed_identity": decision_identity.to_dict(),
        "reviewed_identity_sha256": decision_identity.sha256,
        "review_result_sha256": hashlib.sha256(other_review_bytes).hexdigest(),
        "decision": "approved",
        "plan_adoption": True,
        "implementation_start": True,
        "decided_at": "2026-07-28T12:00:00Z",
    }
    with pytest.raises(ValueError, match="Review identity"):
        PlanningHumanDecisionV1.from_json_bytes(
            _json_bytes(payload),
            review_result_bytes=other_review_bytes,
        )


def test_git_bound_human_decision_requires_exact_resolved_target_tuple() -> None:
    identity = _git_identity()
    review_bytes = _json_bytes(_review(identity=identity).to_dict())
    payload = {
        "schema_version": 1,
        "issue_id": identity.issue_id,
        "reviewed_identity": identity.to_dict(),
        "reviewed_identity_sha256": identity.sha256,
        "review_result_sha256": hashlib.sha256(review_bytes).hexdigest(),
        "decision": "approved",
        "plan_adoption": True,
        "implementation_start": True,
        "decided_at": "2026-07-28T12:00:00Z",
    }
    decision = PlanningHumanDecisionV1.from_json_bytes(
        _json_bytes(payload),
        review_result_bytes=review_bytes,
        expected_canonical_target_paths=PATHS,
    )
    assert decision.reviewed_identity == identity
    with pytest.raises(ValueError, match="expected canonical target"):
        PlanningHumanDecisionV1.from_json_bytes(
            _json_bytes(payload),
            review_result_bytes=review_bytes,
        )


def test_human_decision_rejects_non_review_bytes_even_when_sha_matches() -> None:
    identity = _archive_identity()
    arbitrary_bytes = b'{"not":"a review result"}'
    payload = {
        "schema_version": 1,
        "issue_id": identity.issue_id,
        "reviewed_identity": identity.to_dict(),
        "reviewed_identity_sha256": identity.sha256,
        "review_result_sha256": hashlib.sha256(arbitrary_bytes).hexdigest(),
        "decision": "approved",
        "plan_adoption": True,
        "implementation_start": True,
        "decided_at": "2026-07-28T12:00:00Z",
    }
    with pytest.raises(ValueError):
        PlanningHumanDecisionV1.from_json_bytes(
            _json_bytes(payload),
            review_result_bytes=arbitrary_bytes,
        )


def test_human_decision_strict_json_rejects_duplicate_and_unknown_metadata() -> None:
    identity = _archive_identity()
    identity_json = json.dumps(identity.to_dict(), separators=(",", ":"))
    payload = (
        '{"schema_version":1,"issue_id":"iss-00003",'
        f'"reviewed_identity":{identity_json},'
        f'"reviewed_identity_sha256":"{identity.sha256}",'
        f'"review_result_sha256":"{"c" * 64}",'
        '"decision":"approved","decision":"rejected",'
        '"plan_adoption":true,"implementation_start":true,'
        '"decided_at":"2026-07-28T12:00:00Z"}'
    ).encode()
    with pytest.raises(ValueError, match="duplicate"):
        PlanningHumanDecisionV1.from_json_bytes(payload, review_result_bytes=b"x")

    valid = json.loads(payload.decode().replace(',"decision":"rejected"', ""))
    valid["approved_by"] = "Human"
    with pytest.raises(ValueError, match="unknown keys"):
        PlanningHumanDecisionV1.from_json_bytes(_json_bytes(valid), review_result_bytes=b"x")


@pytest.mark.parametrize(
    ("status", "reason", "ready"),
    [
        ("ok", "candidate_created", False),
        ("ok", "candidate_revised", False),
        ("ok", "review_completed", False),
        ("ready", "adoption_published", True),
    ],
)
def test_result_accepts_exact_success_pairs(status, reason, ready) -> None:
    result = PlanningCommandResult(status=status, reason=reason, issue_id="iss-00003")
    assert result.is_ready is ready
    assert result.exit_code == 0


@pytest.mark.parametrize(
    ("status", "reason"),
    [
        ("ready", "candidate_created"),
        ("ready", "review_completed"),
        ("ok", "adoption_published"),
    ],
)
def test_result_rejects_invalid_success_pair(status, reason) -> None:
    with pytest.raises(ValueError, match="status/reason"):
        PlanningCommandResult(status=status, reason=reason, issue_id="iss-00003")


@pytest.mark.parametrize("value", [Path("candidate.zip"), b"bytes", {"set"}, {1: "value"}, float("nan")])
def test_result_rejects_non_json_output_values(value) -> None:
    with pytest.raises(ValueError, match=r"JSON|non-string|finite"):
        PlanningCommandResult(
            status="blocked",
            reason="missing_evidence",
            issue_id="iss-00003",
            output={"value": value} if not isinstance(value, dict) else value,
        )


def test_non_success_result_maps_to_exit_one() -> None:
    result = PlanningCommandResult(
        status="blocked",
        reason="missing_evidence",
        issue_id="iss-00003",
    )
    assert result.exit_code == 1
    assert result.is_ready is False
