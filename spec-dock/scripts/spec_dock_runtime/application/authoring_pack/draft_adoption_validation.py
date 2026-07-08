from __future__ import annotations

from dataclasses import dataclass
import json
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from pathlib import Path

from spec_dock_runtime.application.authoring_pack.pack_review import _unsafe_report_path
from spec_dock_runtime.domain.authoring_pack.draft_adoption_contract import (
    DraftAdoptionResult,
    blocked_result,
    failed_result,
    file_sha256,
    read_json_payload,
    validate_issue_draft_adoption_payload,
    validate_selected_skeleton_payload,
)


@dataclass(frozen=True)
class IssueDraftAdoptionValidationRequest:
    input_path: Path
    issue_dir: Path
    output_format: Literal["text", "json"] = "text"
    evidence_mode: Literal["github-synced", "local-context"] = "github-synced"
    review_report: Path | None = None
    expected_review_digest: str | None = None
    expected_draft_pack_digest: str | None = None
    expected_source_hash: str | None = None
    report_path: Path | None = None


@dataclass(frozen=True)
class SelectedSkeletonFillValidationRequest:
    input_path: Path
    issue_dir: Path
    assurance: Path
    selected_skeleton: Path
    output_format: Literal["text", "json"] = "text"
    evidence_mode: Literal["github-synced", "local-context"] = "github-synced"
    expected_profile: str | None = None
    expected_source_hash: str | None = None
    report_path: Path | None = None


def validate_issue_draft_adoption(request: IssueDraftAdoptionValidationRequest) -> DraftAdoptionResult:
    payload, findings = read_json_payload(request.input_path, "issue-draft-adoption")
    if payload is None:
        result_factory = blocked_result if _missing_or_unreadable_json(findings) else failed_result
        return _write_report_if_requested(
            result_factory(
                input_path=request.input_path,
                validation_kind="issue-draft-adoption",
                evidence_mode=request.evidence_mode,
                findings=findings,
            ),
            request.report_path,
        )
    issue_gate = _issue_node_gate(request.input_path, request.issue_dir, "issue-draft-adoption", request.evidence_mode)
    if issue_gate is not None:
        return _write_report_if_requested(issue_gate, request.report_path)
    if request.review_report is None:
        return _write_report_if_requested(
            blocked_result(
                input_path=request.input_path,
                validation_kind="issue-draft-adoption",
                evidence_mode=request.evidence_mode,
                findings=("missing_review_report",),
            ),
            request.report_path,
        )
    review_report_path = request.review_report
    review_gate = _review_gate(request.input_path, review_report_path, "issue-draft-adoption", request.evidence_mode)
    if review_gate.status != "pass":
        return _write_report_if_requested(review_gate, request.report_path)
    result = validate_issue_draft_adoption_payload(
        payload,
        input_path=request.input_path,
        issue_dir=request.issue_dir,
        review_status="pass",
        review_digest=file_sha256(review_report_path),
        expected_review_digest=request.expected_review_digest,
        expected_draft_pack_digest=request.expected_draft_pack_digest,
        expected_source_hash=request.expected_source_hash,
        evidence_mode=request.evidence_mode,
    )
    return _write_report_if_requested(result, request.report_path)


def validate_selected_skeleton_fill(request: SelectedSkeletonFillValidationRequest) -> DraftAdoptionResult:
    payload, findings = read_json_payload(request.input_path, "selected-skeleton-fill")
    if payload is None:
        result_factory = blocked_result if _missing_or_unreadable_json(findings) else failed_result
        return _write_report_if_requested(
            result_factory(
                input_path=request.input_path,
                validation_kind="selected-skeleton-fill",
                evidence_mode=request.evidence_mode,
                findings=findings,
            ),
            request.report_path,
        )
    issue_gate = _issue_node_gate(
        request.input_path, request.issue_dir, "selected-skeleton-fill", request.evidence_mode
    )
    if issue_gate is not None:
        return _write_report_if_requested(issue_gate, request.report_path)
    assurance, assurance_findings = read_json_payload(request.assurance, "assurance")
    if assurance is None:
        result_factory = blocked_result if _missing_or_unreadable_json(assurance_findings) else failed_result
        return _write_report_if_requested(
            result_factory(
                input_path=request.input_path,
                validation_kind="selected-skeleton-fill",
                evidence_mode=request.evidence_mode,
                findings=assurance_findings,
            ),
            request.report_path,
        )
    selected_skeleton, skeleton_findings = read_json_payload(request.selected_skeleton, "selected-skeleton")
    if selected_skeleton is None:
        result_factory = blocked_result if _missing_or_unreadable_json(skeleton_findings) else failed_result
        return _write_report_if_requested(
            result_factory(
                input_path=request.input_path,
                validation_kind="selected-skeleton-fill",
                evidence_mode=request.evidence_mode,
                findings=skeleton_findings,
            ),
            request.report_path,
        )
    result = validate_selected_skeleton_payload(
        payload,
        input_path=request.input_path,
        issue_dir=request.issue_dir,
        assurance=assurance,
        selected_skeleton=selected_skeleton,
        expected_profile=request.expected_profile,
        expected_source_hash=request.expected_source_hash,
        evidence_mode=request.evidence_mode,
    )
    return _write_report_if_requested(result, request.report_path)


def _issue_node_gate(
    input_path: Path, issue_dir: Path, validation_kind: str, evidence_mode: str
) -> DraftAdoptionResult | None:
    if not issue_dir.is_dir() or issue_dir.is_symlink():
        return blocked_result(
            input_path=input_path,
            validation_kind=validation_kind,
            evidence_mode=evidence_mode,
            findings=("missing_issue_node",),
        )
    meta = issue_dir / ".meta.json"
    if not meta.is_file() or meta.is_symlink():
        return blocked_result(
            input_path=input_path,
            validation_kind=validation_kind,
            evidence_mode=evidence_mode,
            findings=("missing_issue_node",),
        )
    return None


def _review_gate(
    input_path: Path, review_report: Path, validation_kind: str, evidence_mode: str
) -> DraftAdoptionResult:
    if not review_report.is_file():
        return blocked_result(
            input_path=input_path,
            validation_kind=validation_kind,
            evidence_mode=evidence_mode,
            findings=("missing_review_report",),
        )
    try:
        payload = json.loads(review_report.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        return failed_result(
            input_path=input_path,
            validation_kind=validation_kind,
            evidence_mode=evidence_mode,
            findings=("malformed_review_report",),
        )
    except OSError:
        return blocked_result(
            input_path=input_path,
            validation_kind=validation_kind,
            evidence_mode=evidence_mode,
            findings=("unreadable_review_report",),
        )
    except json.JSONDecodeError:
        return failed_result(
            input_path=input_path,
            validation_kind=validation_kind,
            evidence_mode=evidence_mode,
            findings=("malformed_review_report",),
        )
    if not isinstance(payload, dict):
        return failed_result(
            input_path=input_path,
            validation_kind=validation_kind,
            evidence_mode=evidence_mode,
            findings=("malformed_review_report",),
        )
    status = payload.get("status")
    if status == "pass":
        return DraftAdoptionResult(
            status="pass",
            input_path=str(input_path),
            validation_kind=validation_kind,
            evidence_mode=evidence_mode,
            review_status="pass",
            review_gate_passed=True,
        )
    if status in {"stale", "rejected", "fail", "blocked"}:
        return DraftAdoptionResult(
            status=status,  # type: ignore[arg-type]
            input_path=str(input_path),
            validation_kind=validation_kind,
            evidence_mode=evidence_mode,
            review_status=str(status),
            review_gate_passed=False,
            findings=(f"review_not_pass:{status}",),
        )
    return blocked_result(
        input_path=input_path,
        validation_kind=validation_kind,
        evidence_mode=evidence_mode,
        review_status=str(status),
        findings=(f"unsupported_review_status:{status}",),
    )


def _write_report_if_requested(result: DraftAdoptionResult, report_path: Path | None) -> DraftAdoptionResult:
    if report_path is None:
        return result
    unsafe = _unsafe_report_path(report_path)
    if unsafe:
        return DraftAdoptionResult(
            status="rejected",
            input_path=result.input_path,
            validation_kind=result.validation_kind,
            evidence_mode=result.evidence_mode,
            findings=(unsafe,),
        )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result.to_dict(), sort_keys=True) + "\n", encoding="utf-8")
    return result


def _missing_or_unreadable_json(findings: tuple[str, ...]) -> bool:
    return any(finding.startswith(("missing_json:", "unreadable_payload:")) for finding in findings)
