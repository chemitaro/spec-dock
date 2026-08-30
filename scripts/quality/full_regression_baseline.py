"""Pure parser and evaluator for the Full Regression baseline contract.

The module deliberately has no repository, test-runner, or process boundary.
Adapters collect an observation and pass it here; this module owns the policy
that determines whether the observation proves the baseline contract.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import re
from typing import TYPE_CHECKING, Literal, cast

if TYPE_CHECKING:
    from pathlib import Path


Lifecycle = Literal["active", "resolved", "retired"]
ResolutionMode = Literal["fixed-in-place", "superseded"]
Outcome = Literal["passed", "failed", "skipped", "xfailed", "xpassed", "error"]
RetirementOutcome = Literal["absent", "present", "unknown"]
ViolationCode = Literal[
    "coverage_mismatch",
    "unexpected_failure",
    "unexpected_error",
    "signature_mismatch",
    "retirement_evidence_missing",
    "retirement_evidence_invalid",
]

_OUTCOMES = frozenset({"passed", "failed", "skipped", "xfailed", "xpassed", "error"})
_RETIREMENT_OUTCOMES = frozenset({"absent", "present", "unknown"})


class BaselineContractError(ValueError):
    """Raised when a baseline payload cannot be safely interpreted."""


@dataclass(frozen=True)
class BaselineRow:
    """One historical failure path and its current lifecycle disposition."""

    nodeid: str
    fixed_point_signature_sha256: str
    rationale: str
    lifecycle: Lifecycle = "active"
    resolution_mode: ResolutionMode | None = None
    successor_nodeid: str | None = None
    retirement_evidence_id: str | None = None
    retirement_authority: str | None = None


@dataclass(frozen=True)
class FullRegressionBaseline:
    """Validated baseline payload consumed by :func:`evaluate_baseline`."""

    schema_version: int
    rows: tuple[BaselineRow, ...]


@dataclass(frozen=True)
class RetirementEvidenceObservation:
    """Observation supplied by an adapter for one retired baseline row."""

    checked: bool
    outcome: RetirementOutcome


@dataclass(frozen=True)
class CandidateObservation:
    """Runner output required by the pure baseline evaluator."""

    collected: tuple[str, ...]
    executed: tuple[str, ...]
    outcomes: Mapping[str, Outcome]
    failure_signatures: Mapping[str, str]
    retirement_evidence: Mapping[str, RetirementEvidenceObservation]


@dataclass(frozen=True)
class BaselineViolation:
    """Machine-readable fail-closed reason for a candidate observation."""

    code: ViolationCode
    nodeid: str | None
    detail: str

    def to_dict(self) -> dict[str, str | None]:
        return {"code": self.code, "nodeid": self.nodeid, "detail": self.detail}


@dataclass(frozen=True)
class BaselineEvaluation:
    """Typed result shared by standalone and pytest adapters."""

    verified: bool
    active_verified: tuple[str, ...]
    resolved_verified: tuple[str, ...]
    retired_verified: tuple[str, ...]
    violations: tuple[BaselineViolation, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "verified": self.verified,
            "active_verified": list(self.active_verified),
            "resolved_verified": list(self.resolved_verified),
            "retired_verified": list(self.retired_verified),
            "violations": [violation.to_dict() for violation in self.violations],
        }


def _mapping(value: object, context: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise BaselineContractError(f"{context} must be an object")
    return cast("Mapping[str, object]", value)


def _non_empty_string(value: object, context: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise BaselineContractError(f"{context} must be a non-empty string")
    return value


def _nodeid(value: object, context: str) -> str:
    nodeid = _non_empty_string(value, context)
    if "::" not in nodeid or nodeid.startswith("::") or nodeid.endswith("::"):
        raise BaselineContractError(f"{context} must be a full pytest node ID")
    return nodeid


def _optional_string(value: object, context: str) -> str | None:
    if value is None:
        return None
    return _non_empty_string(value, context)


def _parse_row(raw_value: object, schema_version: int, index: int) -> BaselineRow:
    row = _mapping(raw_value, f"failure_paths[{index}]")
    nodeid = _nodeid(row.get("nodeid"), f"failure_paths[{index}].nodeid")
    signature = _non_empty_string(
        row.get("fixed_point_signature_sha256"),
        f"failure_paths[{index}].fixed_point_signature_sha256",
    )
    rationale_value = row.get("rationale", "")
    if not isinstance(rationale_value, str):
        raise BaselineContractError(f"failure_paths[{index}].rationale must be a string")

    if schema_version == 1:
        return BaselineRow(
            nodeid=nodeid,
            fixed_point_signature_sha256=signature,
            rationale=rationale_value,
        )

    lifecycle_value = row.get("lifecycle")
    if lifecycle_value not in {"active", "resolved", "retired"}:
        raise BaselineContractError(f"failure_paths[{index}].lifecycle is unsupported")
    lifecycle = cast("Lifecycle", lifecycle_value)
    mode_value = row.get("resolution_mode")
    successor_value = row.get("successor_nodeid")
    mode: ResolutionMode | None = None
    successor: str | None = None
    if mode_value is not None:
        if mode_value not in {"fixed-in-place", "superseded"}:
            raise BaselineContractError(f"failure_paths[{index}].resolution mode is unsupported")
        mode = cast("ResolutionMode", mode_value)
    if successor_value is not None:
        successor = _nodeid(successor_value, f"failure_paths[{index}].successor_nodeid")

    evidence_id = _optional_string(
        row.get("retirement_evidence_id"),
        f"failure_paths[{index}].retirement_evidence_id",
    )
    authority = _optional_string(
        row.get("retirement_authority"),
        f"failure_paths[{index}].retirement_authority",
    )

    if lifecycle == "active":
        if mode is not None or successor is not None or evidence_id is not None or authority is not None:
            raise BaselineContractError("active row cannot carry resolution or retirement metadata")
    elif lifecycle == "resolved":
        if mode is None:
            raise BaselineContractError("resolved row requires a resolution mode")
        if mode == "fixed-in-place" and successor is not None:
            raise BaselineContractError("fixed-in-place row cannot carry a successor node ID")
        if mode == "superseded" and successor is None:
            raise BaselineContractError("superseded row requires a successor node ID")
        if evidence_id is not None or authority is not None:
            raise BaselineContractError("resolved row cannot carry retirement metadata")
    else:
        if mode is not None or successor is not None:
            raise BaselineContractError("retired row cannot carry resolution metadata")
        if evidence_id is None or authority is None:
            raise BaselineContractError("retired row requires evidence ID and accepted authority")

    return BaselineRow(
        nodeid=nodeid,
        fixed_point_signature_sha256=signature,
        rationale=rationale_value,
        lifecycle=lifecycle,
        resolution_mode=mode,
        successor_nodeid=successor,
        retirement_evidence_id=evidence_id,
        retirement_authority=authority,
    )


def parse_baseline(payload: Mapping[str, object]) -> FullRegressionBaseline:
    """Parse schema 1/2 baseline data and reject ambiguous contracts."""

    root = _mapping(payload, "baseline")
    schema_value = root.get("schema_version")
    if isinstance(schema_value, bool) or schema_value not in {1, 2}:
        raise BaselineContractError("baseline schema_version must be 1 or 2")
    schema_version = cast("int", schema_value)
    raw_rows = root.get("failure_paths")
    if not isinstance(raw_rows, Sequence) or isinstance(raw_rows, (str, bytes, bytearray)):
        raise BaselineContractError("baseline failure_paths must be an array")
    rows = tuple(_parse_row(value, schema_version, index) for index, value in enumerate(raw_rows))

    nodeids = [row.nodeid for row in rows]
    if len(nodeids) != len(set(nodeids)):
        raise BaselineContractError("baseline contains duplicate current node IDs")
    successors = [row.successor_nodeid for row in rows if row.successor_nodeid is not None]
    if len(successors) != len(set(successors)):
        raise BaselineContractError("baseline contains duplicate successor node IDs")
    if set(successors) & set(nodeids):
        raise BaselineContractError("baseline successor node ID crosses a current row")
    evidence_ids = [row.retirement_evidence_id for row in rows if row.retirement_evidence_id is not None]
    if len(evidence_ids) != len(set(evidence_ids)):
        raise BaselineContractError("baseline contains duplicate retirement evidence IDs")
    return FullRegressionBaseline(schema_version=schema_version, rows=rows)


def normalize_failure_message(message: str, repository: Path) -> str:
    """Normalize known environment-specific pytest failure text."""

    message = message.split(" +  where ", 1)[0]
    message = message.replace(str(repository), "<repo>")
    message = re.sub(r"/tmp/tmp[^/`'\"\\ ]*", "<tmp>", message)
    message = re.sub(
        r"/(?:private/)?var/folders/[^/]+/[^/]+/T/tmp[^/`'\"\\ ]*",
        "<tmp>",
        message,
    )
    message = re.sub(r"/(?:private/)?var/folders/[^'\" ,]+", "<tmp-runtime-path>", message)
    message = re.sub(
        r"(\n\s*Right contains one more item:[^\n]*)\n(?:\s*\n)?\s*Full diff:.*\Z",
        r"\1\n  Use -v to get more diff",
        message,
        flags=re.DOTALL,
    )
    message = message.replace("<repo>/.venv/bin/python3", "<python>")
    message = message.replace("<repo>/.venv/bin/python", "<python>")
    return " ".join(message.split())


def failure_signature(message: str, repository: Path) -> str:
    """Return the stable SHA-256 signature of normalized failure text."""

    return hashlib.sha256(normalize_failure_message(message, repository).encode("utf-8")).hexdigest()


def _validated_nodeids(value: object, field: str) -> tuple[str, ...]:
    if not isinstance(value, tuple) or any(not isinstance(nodeid, str) or not nodeid for nodeid in value):
        raise BaselineContractError(f"observation.{field} must be a tuple of non-empty node IDs")
    return cast("tuple[str, ...]", value)


def _validated_outcomes(value: object) -> Mapping[str, Outcome]:
    if not isinstance(value, Mapping):
        raise BaselineContractError("observation.outcomes must be a mapping")
    for nodeid, outcome in value.items():
        if not isinstance(nodeid, str) or not nodeid:
            raise BaselineContractError("observation.outcomes contains an invalid node ID")
        if not isinstance(outcome, str) or outcome not in _OUTCOMES:
            raise BaselineContractError(f"observation has an unknown outcome for {nodeid!r}")
    return cast("Mapping[str, Outcome]", value)


def _validated_signatures(value: object) -> Mapping[str, str]:
    if not isinstance(value, Mapping):
        raise BaselineContractError("observation.failure_signatures must be a mapping")
    for nodeid, signature in value.items():
        if not isinstance(nodeid, str) or not nodeid or not isinstance(signature, str) or not signature:
            raise BaselineContractError("observation has an invalid failure signature")
    return cast("Mapping[str, str]", value)


def _validated_evidence(value: object) -> Mapping[str, RetirementEvidenceObservation]:
    if not isinstance(value, Mapping):
        raise BaselineContractError("observation.retirement_evidence must be a mapping")
    for evidence_id, evidence in value.items():
        if not isinstance(evidence_id, str) or not evidence_id:
            raise BaselineContractError("retirement evidence has an invalid ID")
        if not isinstance(evidence, RetirementEvidenceObservation):
            raise BaselineContractError(f"retirement evidence {evidence_id!r} is not typed evidence")
        if not isinstance(evidence.checked, bool) or evidence.outcome not in _RETIREMENT_OUTCOMES:
            raise BaselineContractError(f"retirement evidence {evidence_id!r} is invalid")
    return cast("Mapping[str, RetirementEvidenceObservation]", value)


def evaluate_baseline(
    baseline: FullRegressionBaseline,
    observation: CandidateObservation,
) -> BaselineEvaluation:
    """Evaluate a candidate observation using one fail-closed policy."""

    violations: list[BaselineViolation] = []
    violation_keys: set[tuple[str, str | None, str]] = set()

    def add_violation(code: str, nodeid: str | None, detail: str) -> None:
        key = (code, nodeid, detail)
        if key not in violation_keys:
            violation_keys.add(key)
            violations.append(
                BaselineViolation(
                    code=cast("ViolationCode", code),
                    nodeid=nodeid,
                    detail=detail,
                )
            )

    if not isinstance(baseline, FullRegressionBaseline):
        raise BaselineContractError("baseline must be a parsed FullRegressionBaseline")
    if not isinstance(observation, CandidateObservation):
        raise BaselineContractError("observation must be a CandidateObservation")
    if not isinstance(baseline.rows, tuple) or any(not isinstance(row, BaselineRow) for row in baseline.rows):
        raise BaselineContractError("baseline rows must be parsed BaselineRow values")

    collected = _validated_nodeids(observation.collected, "collected")
    executed = _validated_nodeids(observation.executed, "executed")
    outcomes = _validated_outcomes(observation.outcomes)
    signatures = _validated_signatures(observation.failure_signatures)
    evidence = _validated_evidence(observation.retirement_evidence)

    for field, values in (("collected", collected), ("executed", executed)):
        seen: set[str] = set()
        for nodeid in values:
            if nodeid in seen:
                add_violation("coverage_mismatch", nodeid, f"observation.{field} contains a duplicate node ID")
            seen.add(nodeid)
    collected_set = set(collected)
    executed_set = set(executed)
    for nodeid in sorted(executed_set - collected_set):
        add_violation("coverage_mismatch", nodeid, "executed node was not collected")
    for nodeid in sorted(set(outcomes) - executed_set):
        add_violation("coverage_mismatch", nodeid, "outcome exists for a node that did not execute")
    for nodeid in sorted(executed_set - set(outcomes)):
        add_violation("coverage_mismatch", nodeid, "executed node has no outcome")
    for nodeid in sorted(set(signatures) - set(outcomes)):
        add_violation("coverage_mismatch", nodeid, "failure signature exists without an outcome")
    for nodeid, outcome in outcomes.items():
        if outcome != "failed" and nodeid in signatures:
            add_violation("coverage_mismatch", nodeid, "non-failed outcome has a failure signature")

    active_verified: list[str] = []
    resolved_verified: list[str] = []
    retired_verified: list[str] = []
    handled_failure_nodes: set[str] = set()

    def exactly_once(nodeid: str, values: tuple[str, ...], field: str) -> bool:
        count = values.count(nodeid)
        if count != 1:
            add_violation(
                "coverage_mismatch",
                nodeid,
                f"{field} must contain the exact node ID exactly once (observed {count})",
            )
            return False
        return True

    for row in baseline.rows:
        if row.lifecycle == "active":
            handled_failure_nodes.add(row.nodeid)
            if not exactly_once(row.nodeid, collected, "collected") or not exactly_once(row.nodeid, executed, "executed"):
                continue
            active_outcome = outcomes.get(row.nodeid)
            if active_outcome == "failed":
                observed_signature = signatures.get(row.nodeid)
                if observed_signature != row.fixed_point_signature_sha256:
                    add_violation(
                        "signature_mismatch",
                        row.nodeid,
                        "active failure signature does not match the fixed-point signature",
                    )
                else:
                    active_verified.append(row.nodeid)
            elif active_outcome == "error":
                add_violation("unexpected_error", row.nodeid, "active baseline node errored")
            else:
                add_violation("coverage_mismatch", row.nodeid, "active baseline node did not fail normally")
        elif row.lifecycle == "resolved" and row.resolution_mode == "fixed-in-place":
            handled_failure_nodes.add(row.nodeid)
            if not exactly_once(row.nodeid, collected, "collected") or not exactly_once(row.nodeid, executed, "executed"):
                continue
            row_outcome = outcomes.get(row.nodeid)
            if row_outcome == "passed":
                resolved_verified.append(row.nodeid)
            elif row_outcome == "error":
                add_violation("unexpected_error", row.nodeid, "fixed-in-place baseline node errored")
            elif row_outcome == "failed":
                add_violation("unexpected_failure", row.nodeid, "fixed-in-place baseline node failed again")
            else:
                add_violation("coverage_mismatch", row.nodeid, "fixed-in-place node did not pass normally")
        elif row.lifecycle == "resolved" and row.resolution_mode == "superseded":
            assert row.successor_nodeid is not None
            handled_failure_nodes.update({row.nodeid, row.successor_nodeid})
            successor = row.successor_nodeid
            if exactly_once(successor, collected, "collected") and exactly_once(successor, executed, "executed"):
                successor_outcome = outcomes.get(successor)
                if successor_outcome == "passed":
                    resolved_verified.append(row.nodeid)
                elif successor_outcome == "error":
                    add_violation("unexpected_error", successor, "successor node errored")
                elif successor_outcome == "failed":
                    add_violation("unexpected_failure", successor, "successor node failed")
                else:
                    add_violation("coverage_mismatch", successor, "successor node did not pass normally")
            old_outcome = outcomes.get(row.nodeid)
            if old_outcome == "failed":
                add_violation("unexpected_failure", row.nodeid, "superseded historical node failed again")
            elif old_outcome == "error":
                add_violation("unexpected_error", row.nodeid, "superseded historical node errored")
        elif row.lifecycle == "retired":
            evidence_id = row.retirement_evidence_id
            assert evidence_id is not None
            observed_evidence = evidence.get(evidence_id)
            if observed_evidence is None:
                add_violation("retirement_evidence_missing", row.nodeid, f"retirement evidence {evidence_id!r} was not supplied")
            elif observed_evidence.checked is True and observed_evidence.outcome == "absent":
                retired_verified.append(row.nodeid)
            else:
                add_violation(
                    "retirement_evidence_invalid",
                    row.nodeid,
                    f"retirement evidence {evidence_id!r} must be checked with outcome absent",
                )

    for nodeid, outcome in outcomes.items():
        if nodeid in handled_failure_nodes:
            continue
        if outcome == "failed":
            add_violation("unexpected_failure", nodeid, "failure is not covered by an active baseline row")
        elif outcome == "error":
            add_violation("unexpected_error", nodeid, "error is not covered by a baseline row")

    return BaselineEvaluation(
        verified=not violations,
        active_verified=tuple(active_verified),
        resolved_verified=tuple(resolved_verified),
        retired_verified=tuple(retired_verified),
        violations=tuple(violations),
    )


__all__ = [
    "BaselineContractError",
    "BaselineEvaluation",
    "BaselineRow",
    "BaselineViolation",
    "CandidateObservation",
    "FullRegressionBaseline",
    "RetirementEvidenceObservation",
    "evaluate_baseline",
    "failure_signature",
    "normalize_failure_message",
    "parse_baseline",
]
