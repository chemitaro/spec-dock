from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

WorkflowStateKind = Literal["no-active", "requirement-capture", "classification-required", "ready", "blocked"]
WorkflowArtifactReadiness = Literal["missing", "scaffold", "substantive"]
WorkflowProfile = Literal["lite", "standard", "strict", "critical", "unavailable"]
WorkflowObligationSource = Literal["authorized_profile", "unavailable"]


@dataclass(frozen=True)
class RunbookAuthority:
    authorized_profile: WorkflowProfile
    lite_candidate: bool
    obligation_source: WorkflowObligationSource


@dataclass(frozen=True)
class WorkflowState:
    kind: WorkflowStateKind
    active_issue_id: str | None
    reason_code: str
    artifact_readiness: WorkflowArtifactReadiness
    authority: RunbookAuthority
    details: tuple[str, ...] = ()


STRICT_LEGACY_AUTHORITY = RunbookAuthority(
    authorized_profile="strict",
    lite_candidate=False,
    obligation_source="authorized_profile",
)

UNAVAILABLE_AUTHORITY = RunbookAuthority(
    authorized_profile="unavailable",
    lite_candidate=False,
    obligation_source="unavailable",
)


def classify_requirement_text(text: str) -> WorkflowArtifactReadiness:
    stripped = text.strip()
    if not stripped:
        return "missing"
    placeholder_markers = (
        "<ISS_ID>",
        "<ISS_TITLE>",
        "<GITHUB_ISSUE_NUMBER_OR_URL>",
        "<YOUR_NAME>",
        "YYYY-MM-DD",
        "（1〜3行）...",
        "  - ...",
        "- ...",
        "1. ...",
        "2. ...",
        "draft | approved",
    )
    if any(marker in stripped for marker in placeholder_markers):
        return "scaffold"
    return "substantive"
