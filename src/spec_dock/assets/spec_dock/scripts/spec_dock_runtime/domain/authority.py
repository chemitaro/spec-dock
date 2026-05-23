from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

AUTHORITY_PROPOSED = "proposed"
AUTHORITY_APPROVED = "approved"

GRANT_REVIEW_INPUT = "review_input"
GRANT_PLANNING_INPUT = "planning_input"
GRANT_DESIGN_BASELINE = "design_baseline"
GRANT_IMPLEMENTATION_START = "implementation_start"
GRANT_ISSUE_READY = "issue_ready"
GRANT_ISSUE_FINISH = "issue_finish"
GRANT_PHASE_COMPLETION = "phase_completion"

VALID_AUTHORITIES: tuple[str, ...] = (AUTHORITY_PROPOSED, AUTHORITY_APPROVED)
VALID_GRANTS: tuple[str, ...] = (
    GRANT_REVIEW_INPUT,
    GRANT_PLANNING_INPUT,
    GRANT_DESIGN_BASELINE,
    GRANT_IMPLEMENTATION_START,
    GRANT_ISSUE_READY,
    GRANT_ISSUE_FINISH,
    GRANT_PHASE_COMPLETION,
)
INVALID_WILDCARD_GRANTS: tuple[str, ...] = ("*", "grants.*", "all", "admin", "owner")


@dataclass(frozen=True)
class AuthorityGateResult:
    ok: bool
    reason: str
    details: tuple[str, ...] = ()


def approved_runtime_promotion_record(*, node_id: str) -> dict[str, str]:
    revision = f"active:{node_id}"
    return {
        "status": AUTHORITY_APPROVED,
        "authority": AUTHORITY_APPROVED,
        "source_revision": revision,
        "approved_revision": revision,
        "approved_hash": revision,
        "reviewer_target_hash": revision,
        "promotion_decision": "runtime_active_selection",
    }


def approved_runtime_grants() -> tuple[str, ...]:
    return VALID_GRANTS


def _normalize_grants(raw_grants: object) -> tuple[str, ...] | None:
    if not isinstance(raw_grants, list | tuple):
        return None
    normalized: list[str] = []
    for grant in raw_grants:
        if not isinstance(grant, str):
            return None
        stripped = grant.strip()
        if not stripped:
            return None
        normalized.append(stripped)
    return tuple(normalized)


def _promotion_value(promotion_record: Mapping[str, object], key: str) -> str | None:
    value = promotion_record.get(key)
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def evaluate_authority_gate(
    *,
    authority: object,
    grants: object,
    promotion_record: object,
    required_grant: str,
    purpose: str,
    expected_revision: str | None = None,
) -> AuthorityGateResult:
    if required_grant not in VALID_GRANTS:
        return AuthorityGateResult(False, "invalid_required_grant", (f"required_grant={required_grant}",))

    if not isinstance(authority, str) or not authority.strip():
        return AuthorityGateResult(False, "missing_authority", (f"purpose={purpose}",))
    normalized_authority = authority.strip()
    if normalized_authority not in VALID_AUTHORITIES:
        return AuthorityGateResult(False, "invalid_authority", (f"authority={normalized_authority}",))
    if normalized_authority != AUTHORITY_APPROVED:
        return AuthorityGateResult(
            False,
            "authority_not_approved",
            (f"authority={normalized_authority}", f"required_grant={required_grant}", f"purpose={purpose}"),
        )

    normalized_grants = _normalize_grants(grants)
    if normalized_grants is None:
        return AuthorityGateResult(False, "missing_or_invalid_grants", (f"purpose={purpose}",))
    invalid = tuple(grant for grant in normalized_grants if grant in INVALID_WILDCARD_GRANTS or grant not in VALID_GRANTS)
    if invalid:
        return AuthorityGateResult(False, "invalid_grants", tuple(f"grant={grant}" for grant in invalid))
    if required_grant not in normalized_grants:
        return AuthorityGateResult(
            False,
            "missing_required_grant",
            (f"required_grant={required_grant}", f"purpose={purpose}"),
        )

    if not isinstance(promotion_record, Mapping):
        return AuthorityGateResult(False, "missing_promotion_record", (f"purpose={purpose}",))
    required_fields = (
        "status",
        "authority",
        "source_revision",
        "approved_revision",
        "approved_hash",
        "reviewer_target_hash",
        "promotion_decision",
    )
    missing = tuple(field for field in required_fields if _promotion_value(promotion_record, field) is None)
    if missing:
        return AuthorityGateResult(False, "incomplete_promotion_record", tuple(f"missing={field}" for field in missing))
    if _promotion_value(promotion_record, "status") != AUTHORITY_APPROVED:
        return AuthorityGateResult(False, "promotion_not_approved", (f"status={promotion_record.get('status')}",))
    if _promotion_value(promotion_record, "authority") != AUTHORITY_APPROVED:
        return AuthorityGateResult(False, "promotion_authority_not_approved", ())
    if _promotion_value(promotion_record, "approved_hash") != _promotion_value(promotion_record, "reviewer_target_hash"):
        return AuthorityGateResult(False, "stale_promotion_hash", ())
    if _promotion_value(promotion_record, "source_revision") != _promotion_value(promotion_record, "approved_revision"):
        return AuthorityGateResult(False, "stale_promotion_revision", ())
    if expected_revision is not None:
        normalized_expected = expected_revision.strip()
        if not normalized_expected:
            return AuthorityGateResult(False, "missing_expected_revision", ())
        if _promotion_value(promotion_record, "approved_revision") != normalized_expected:
            return AuthorityGateResult(
                False,
                "promotion_record_not_bound_to_active_entry",
                (f"expected_revision={normalized_expected}",),
            )
        if _promotion_value(promotion_record, "approved_hash") != normalized_expected:
            return AuthorityGateResult(
                False,
                "promotion_hash_not_bound_to_active_entry",
                (f"expected_revision={normalized_expected}",),
            )
    return AuthorityGateResult(True, "ok", (f"required_grant={required_grant}", f"purpose={purpose}"))
