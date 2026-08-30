from __future__ import annotations

from pathlib import Path

import pytest
from scripts.quality.full_regression_baseline import (
    BaselineContractError,
    CandidateObservation,
    RetirementEvidenceObservation,
    evaluate_baseline,
    failure_signature,
    normalize_failure_message,
    parse_baseline,
)

ACTIVE_NODE = "tests/example/test_example.py::test_active"
FIXED_NODE = "tests/example/test_example.py::test_fixed"
OLD_NODE = "tests/example/test_example.py::test_old"
SUCCESSOR_NODE = "tests/example/test_example.py::test_successor"
RETIRED_NODE = "tests/example/test_example.py::test_retired"
ACTIVE_SIGNATURE = "a" * 64


def _row(
    nodeid: str = ACTIVE_NODE,
    *,
    lifecycle: str | None = None,
    resolution_mode: str | None = None,
    successor_nodeid: str | None = None,
    retirement_evidence_id: str | None = None,
    retirement_authority: str | None = None,
) -> dict[str, object]:
    value: dict[str, object] = {
        "nodeid": nodeid,
        "fixed_point_signature_sha256": ACTIVE_SIGNATURE,
        "rationale": "historical fixed-point evidence",
        "lifecycle": "active" if lifecycle is None else lifecycle,
    }
    if resolution_mode is not None:
        value["resolution_mode"] = resolution_mode
    if successor_nodeid is not None:
        value["successor_nodeid"] = successor_nodeid
    if retirement_evidence_id is not None:
        value["retirement_evidence_id"] = retirement_evidence_id
    if retirement_authority is not None:
        value["retirement_authority"] = retirement_authority
    return value


def _baseline(*rows: dict[str, object], schema_version: int = 2):
    return parse_baseline({"schema_version": schema_version, "failure_paths": list(rows)})


def _observation(
    *,
    collected: tuple[str, ...],
    executed: tuple[str, ...],
    outcomes: dict[str, str],
    failure_signatures: dict[str, str] | None = None,
    retirement_evidence: dict[str, RetirementEvidenceObservation] | None = None,
) -> CandidateObservation:
    return CandidateObservation(
        collected=collected,
        executed=executed,
        outcomes=outcomes,
        failure_signatures=failure_signatures or {},
        retirement_evidence=retirement_evidence or {},
    )


def test_schema_one_is_active_and_preserves_historical_fields() -> None:
    baseline = _baseline(_row(), schema_version=1)

    row = baseline.rows[0]
    assert baseline.schema_version == 1
    assert row.lifecycle == "active"
    assert row.nodeid == ACTIVE_NODE
    assert row.fixed_point_signature_sha256 == ACTIVE_SIGNATURE
    assert row.rationale == "historical fixed-point evidence"


def test_active_failure_with_exact_signature_is_verified() -> None:
    baseline = _baseline(_row())
    observation = _observation(
        collected=(ACTIVE_NODE,),
        executed=(ACTIVE_NODE,),
        outcomes={ACTIVE_NODE: "failed"},
        failure_signatures={ACTIVE_NODE: ACTIVE_SIGNATURE},
    )

    result = evaluate_baseline(baseline, observation)

    assert result.verified
    assert result.active_verified == (ACTIVE_NODE,)
    assert result.violations == ()


@pytest.mark.parametrize("outcome", ["passed", "skipped", "xfailed", "xpassed", "error"])
def test_active_non_failure_outcomes_fail_closed(outcome: str) -> None:
    baseline = _baseline(_row())
    observation = _observation(
        collected=(ACTIVE_NODE,),
        executed=(ACTIVE_NODE,),
        outcomes={ACTIVE_NODE: outcome},
    )

    result = evaluate_baseline(baseline, observation)

    assert not result.verified
    assert result.active_verified == ()
    assert result.violations
    assert result.violations[0].code in {"coverage_mismatch", "unexpected_error"}


def test_active_signature_drift_is_typed() -> None:
    baseline = _baseline(_row())
    observation = _observation(
        collected=(ACTIVE_NODE,),
        executed=(ACTIVE_NODE,),
        outcomes={ACTIVE_NODE: "failed"},
        failure_signatures={ACTIVE_NODE: "b" * 64},
    )

    result = evaluate_baseline(baseline, observation)

    assert not result.verified
    assert {violation.code for violation in result.violations} == {"signature_mismatch"}


def test_resolved_fixed_in_place_requires_normal_pass() -> None:
    baseline = _baseline(_row(FIXED_NODE, lifecycle="resolved", resolution_mode="fixed-in-place"))
    observation = _observation(
        collected=(FIXED_NODE,),
        executed=(FIXED_NODE,),
        outcomes={FIXED_NODE: "passed"},
    )

    result = evaluate_baseline(baseline, observation)

    assert result.verified
    assert result.resolved_verified == (FIXED_NODE,)


@pytest.mark.parametrize("outcome", ["skipped", "xfailed", "xpassed", "failed", "error"])
def test_resolved_fixed_in_place_rejects_non_normal_pass(outcome: str) -> None:
    baseline = _baseline(_row(FIXED_NODE, lifecycle="resolved", resolution_mode="fixed-in-place"))
    observation = _observation(
        collected=(FIXED_NODE,),
        executed=(FIXED_NODE,),
        outcomes={FIXED_NODE: outcome},
        failure_signatures={FIXED_NODE: ACTIVE_SIGNATURE} if outcome == "failed" else {},
    )

    result = evaluate_baseline(baseline, observation)

    assert not result.verified
    assert result.resolved_verified == ()


def test_resolved_superseded_requires_byte_exact_successor_node() -> None:
    baseline = _baseline(_row(OLD_NODE, lifecycle="resolved", resolution_mode="superseded", successor_nodeid=SUCCESSOR_NODE))
    observation = _observation(
        collected=(SUCCESSOR_NODE,),
        executed=(SUCCESSOR_NODE,),
        outcomes={SUCCESSOR_NODE: "passed"},
    )

    result = evaluate_baseline(baseline, observation)

    assert result.verified
    assert result.resolved_verified == (OLD_NODE,)


@pytest.mark.parametrize(
    ("collected", "executed", "outcome"),
    [
        (("tests/example/test_example.py::test_successor_extra",), ("tests/example/test_example.py::test_successor_extra",), "passed"),
        ((), (), "passed"),
        ((SUCCESSOR_NODE,), (), "passed"),
        ((SUCCESSOR_NODE,), (SUCCESSOR_NODE,), "skipped"),
        ((SUCCESSOR_NODE,), (SUCCESSOR_NODE,), "xfailed"),
        ((SUCCESSOR_NODE,), (SUCCESSOR_NODE,), "xpassed"),
        ((SUCCESSOR_NODE,), (SUCCESSOR_NODE,), "failed"),
        ((SUCCESSOR_NODE,), (SUCCESSOR_NODE,), "error"),
    ],
)
def test_resolved_superseded_negative_cases_are_not_passed(
    collected: tuple[str, ...],
    executed: tuple[str, ...],
    outcome: str,
) -> None:
    baseline = _baseline(_row(OLD_NODE, lifecycle="resolved", resolution_mode="superseded", successor_nodeid=SUCCESSOR_NODE))
    outcomes = {executed[0]: outcome} if executed else {}
    observation = _observation(collected=collected, executed=executed, outcomes=outcomes)

    result = evaluate_baseline(baseline, observation)

    assert not result.verified
    assert result.resolved_verified == ()


def test_resolved_superseded_rejects_old_failure_recurrence() -> None:
    baseline = _baseline(_row(OLD_NODE, lifecycle="resolved", resolution_mode="superseded", successor_nodeid=SUCCESSOR_NODE))
    observation = _observation(
        collected=(SUCCESSOR_NODE, OLD_NODE),
        executed=(SUCCESSOR_NODE, OLD_NODE),
        outcomes={SUCCESSOR_NODE: "passed", OLD_NODE: "failed"},
        failure_signatures={OLD_NODE: ACTIVE_SIGNATURE},
    )

    result = evaluate_baseline(baseline, observation)

    assert not result.verified
    assert any(violation.code == "unexpected_failure" and violation.nodeid == OLD_NODE for violation in result.violations)


def test_retired_requires_checked_absence_evidence() -> None:
    baseline = _baseline(
        _row(
            RETIRED_NODE,
            lifecycle="retired",
            retirement_evidence_id="retire-001",
            retirement_authority="accepted ADR 20260830t085007z",
        )
    )
    observation = _observation(
        collected=(),
        executed=(),
        outcomes={},
        retirement_evidence={
            "retire-001": RetirementEvidenceObservation(checked=True, outcome="absent"),
        },
    )

    result = evaluate_baseline(baseline, observation)

    assert result.verified
    assert result.retired_verified == (RETIRED_NODE,)


@pytest.mark.parametrize(
    "evidence",
    [
        None,
        RetirementEvidenceObservation(checked=False, outcome="absent"),
        RetirementEvidenceObservation(checked=True, outcome="unknown"),
        RetirementEvidenceObservation(checked=True, outcome="present"),
    ],
)
def test_retired_missing_or_unproven_evidence_fails_closed(
    evidence: RetirementEvidenceObservation | None,
) -> None:
    baseline = _baseline(
        _row(
            RETIRED_NODE,
            lifecycle="retired",
            retirement_evidence_id="retire-001",
            retirement_authority="accepted ADR 20260830t085007z",
        )
    )
    retirement_evidence = {} if evidence is None else {"retire-001": evidence}
    observation = _observation(
        collected=(),
        executed=(),
        outcomes={},
        retirement_evidence=retirement_evidence,
    )

    result = evaluate_baseline(baseline, observation)

    assert not result.verified
    assert result.retired_verified == ()
    assert result.violations[0].code in {"retirement_evidence_missing", "retirement_evidence_invalid"}


@pytest.mark.parametrize(
    "payload",
    [
        {"schema_version": 3, "failure_paths": [_row()]},
        {"schema_version": 2, "failure_paths": [_row(lifecycle="unknown")]},
        {"schema_version": 2, "failure_paths": [_row(OLD_NODE, lifecycle="resolved")]},
        {
            "schema_version": 2,
            "failure_paths": [
                _row(RETIRED_NODE, lifecycle="retired", retirement_authority="accepted ADR"),
            ],
        },
        {"schema_version": 2, "failure_paths": [_row(), _row()]},
    ],
)
def test_invalid_baseline_contract_is_rejected(payload: dict[str, object]) -> None:
    with pytest.raises(BaselineContractError):
        parse_baseline(payload)


def test_unexpected_failure_and_error_are_machine_readable() -> None:
    baseline = _baseline(_row())
    unexpected_failure = "tests/example/test_example.py::test_new_failure"
    unexpected_error = "tests/example/test_example.py::test_new_error"
    observation = _observation(
        collected=(ACTIVE_NODE, unexpected_failure, unexpected_error),
        executed=(ACTIVE_NODE, unexpected_failure, unexpected_error),
        outcomes={
            ACTIVE_NODE: "failed",
            unexpected_failure: "failed",
            unexpected_error: "error",
        },
        failure_signatures={ACTIVE_NODE: ACTIVE_SIGNATURE, unexpected_failure: "c" * 64},
    )

    result = evaluate_baseline(baseline, observation)

    assert not result.verified
    assert {(item.code, item.nodeid) for item in result.violations} >= {
        ("unexpected_failure", unexpected_failure),
        ("unexpected_error", unexpected_error),
    }
    rendered = result.to_dict()
    assert rendered["verified"] is False
    assert rendered["violations"][0]["code"]


def test_failure_signature_matches_existing_normalization() -> None:
    repository = Path("/repo")
    message = "assert 1 == 2 +  where /repo/.venv/bin/python3"

    assert normalize_failure_message(message, repository) == "assert 1 == 2"
    assert failure_signature(message, repository) == failure_signature("assert 1 == 2", repository)
