from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Literal
import hashlib
import json

from spec_dock_runtime.domain.authoring_pack.authority_boundary import scan_authoring_payload, scan_sensitive_payload
from spec_dock_runtime.domain.authoring_pack.prompt_pack_contract import (
    ADOPTION_STATUS,
    AUTHORITY,
    BUNDLE_GENERATION_NOT_PROMOTION,
    EXPECTED_OUTPUT_ROOT,
)
from spec_dock_runtime.domain.authoring_pack.zip_contract import MAX_ENTRY_BYTES


CandidateKind = Literal["initiative-epic", "epic-issue"]
CandidateStatus = Literal["pass", "fail", "blocked", "stale", "rejected"]

ALLOWED_PROFILES = {"lite", "standard", "strict", "critical"}


@dataclass(frozen=True)
class CandidateValidationResult:
    status: CandidateStatus
    input_path: str
    candidate_kind: CandidateKind
    authority: str = AUTHORITY
    adoption_status: str = ADOPTION_STATUS
    bundle_generation_not_promotion: bool = BUNDLE_GENERATION_NOT_PROMOTION
    evidence_mode: str = "github-synced"
    review_status: str | None = None
    review_gate_passed: bool = False
    fallback: bool = False
    parent_scope: str | None = None
    expected_source_manifest_hash: str | None = None
    observed_source_manifest_hash: str | None = None
    candidate_count: int = 0
    valid_candidate_count: int = 0
    approval_required: bool = True
    node_creation_performed: bool = False
    canonical_written: bool = False
    assurance_mutated: bool = False
    reviewer_pass_claimed: bool = False
    execution_ready: bool = False
    pr_ready: bool = False
    findings: tuple[str, ...] = ()
    comparison: tuple[str, ...] = ()
    candidates: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "input_path": self.input_path,
            "candidate_kind": self.candidate_kind,
            "authority": self.authority,
            "adoption_status": self.adoption_status,
            "bundle_generation_not_promotion": self.bundle_generation_not_promotion,
            "evidence_mode": self.evidence_mode,
            "review_status": self.review_status,
            "review_gate_passed": self.review_gate_passed,
            "fallback": self.fallback,
            "parent_scope": self.parent_scope,
            "expected_source_manifest_hash": self.expected_source_manifest_hash,
            "observed_source_manifest_hash": self.observed_source_manifest_hash,
            "candidate_count": self.candidate_count,
            "valid_candidate_count": self.valid_candidate_count,
            "approval_required": self.approval_required,
            "node_creation_performed": self.node_creation_performed,
            "canonical_written": self.canonical_written,
            "assurance_mutated": self.assurance_mutated,
            "reviewer_pass_claimed": self.reviewer_pass_claimed,
            "execution_ready": self.execution_ready,
            "pr_ready": self.pr_ready,
            "findings": list(self.findings),
            "comparison": list(self.comparison),
            "candidates": list(self.candidates),
        }


def validate_candidate_pack(
    pack_root: Path,
    *,
    input_path: Path,
    candidate_kind: CandidateKind,
    review_status: str,
    expected_parent_initiative: str | None = None,
    expected_parent_epic: str | None = None,
    expected_source_hash: str | None = None,
    expected_review_digest: str | None = None,
    evidence_mode: str = "github-synced",
) -> CandidateValidationResult:
    parent_scope = expected_parent_initiative if candidate_kind == "initiative-epic" else expected_parent_epic
    findings: list[str] = []
    comparison: list[str] = []
    candidates: list[str] = []

    observed_source_hash = _source_manifest_hash(pack_root, findings)
    if expected_source_hash and observed_source_hash != expected_source_hash:
        comparison.append("source_manifest_hash_mismatch")
    observed_review_digest = tree_digest(pack_root)
    if expected_review_digest and observed_review_digest != expected_review_digest:
        comparison.append("review_digest_mismatch")

    index_rel = "candidates/epics/index.json" if candidate_kind == "initiative-epic" else "candidates/issues/index.json"
    index_payload = _read_json(pack_root / index_rel, index_rel, findings)
    candidate_items: list[object] = []
    if isinstance(index_payload, dict):
        _validate_common_authority(index_payload, index_rel, findings, require_claims=False)
        raw_candidates = index_payload.get("candidates")
        if isinstance(raw_candidates, list):
            candidate_items = raw_candidates
            if not candidate_items:
                findings.append("empty_candidates")
        else:
            findings.append("missing_or_invalid_field:candidates")
    elif index_payload is not None:
        findings.append(f"non_object_json:{index_rel}")

    seen_ids: dict[str, int] = {}
    seen_titles: dict[str, int] = {}
    seen_slugs: dict[str, int] = {}
    scope_signatures: dict[str, int] = {}
    indexed_candidate_ids = {
        item.get("candidate_id")
        for item in candidate_items
        if isinstance(item, dict) and isinstance(item.get("candidate_id"), str)
    }

    valid_count = 0
    for item in candidate_items:
        if not isinstance(item, dict):
            findings.append("invalid_candidate_index_item")
            continue
        candidate_id = _string_field(item, "candidate_id", "index", findings)
        title = _string_field(item, "title", candidate_id or "index", findings)
        slug = _string_field(item, "slug", candidate_id or "index", findings)
        candidate_path = _string_field(item, "path", candidate_id or "index", findings)
        if candidate_id:
            candidates.append(candidate_id)
            _record_duplicate(seen_ids, candidate_id, "duplicate_candidate_id", findings)
        if title:
            _record_duplicate(seen_titles, title.lower(), "duplicate_title", findings)
        if slug:
            _record_duplicate(seen_slugs, slug, "duplicate_slug", findings)
        if not candidate_path:
            continue
        rel_path = _safe_rel(candidate_path, findings)
        if rel_path is None:
            continue
        payload = _read_json(pack_root / rel_path, rel_path, findings)
        if not isinstance(payload, dict):
            if payload is not None:
                findings.append(f"non_object_json:{rel_path}")
            continue
        _validate_common_authority(payload, rel_path, findings, require_claims=True)
        if payload.get("candidate_kind") != ("epic" if candidate_kind == "initiative-epic" else "issue"):
            findings.append(f"invalid_candidate_kind:{candidate_id or rel_path}")
        _validate_parent_trace(
            payload,
            candidate_kind=candidate_kind,
            candidate_id=candidate_id or rel_path,
            expected_parent_initiative=expected_parent_initiative,
            expected_parent_epic=expected_parent_epic,
            comparison=comparison,
            findings=findings,
        )
        _validate_boundary(payload, candidate_id or rel_path, scope_signatures, findings)
        if candidate_kind == "initiative-epic":
            _validate_epic_candidate(payload, candidate_id or rel_path, indexed_candidate_ids, findings)
        else:
            _validate_issue_candidate(payload, candidate_id or rel_path, findings)
        _validate_drafts(pack_root, payload, candidate_path=rel_path, candidate_id=candidate_id or rel_path, findings=findings)
        valid_count += 1

    status = _status_from_findings(findings, comparison)
    return CandidateValidationResult(
        status=status,
        input_path=str(input_path),
        candidate_kind=candidate_kind,
        evidence_mode=evidence_mode,
        review_status=review_status,
        review_gate_passed=review_status == "pass",
        parent_scope=parent_scope,
        expected_source_manifest_hash=expected_source_hash,
        observed_source_manifest_hash=observed_source_hash,
        candidate_count=len(candidate_items),
        valid_candidate_count=valid_count if status == "pass" else 0,
        findings=tuple(dict.fromkeys(findings)),
        comparison=tuple(dict.fromkeys(comparison)),
        candidates=tuple(sorted(candidates)),
    )


def tree_digest(pack_root: Path) -> str | None:
    if not pack_root.is_dir() or pack_root.is_symlink():
        return None
    digest = hashlib.sha256()
    for path in sorted(item for item in pack_root.rglob("*") if item.is_file() and not item.is_symlink()):
        rel_path = path.relative_to(pack_root).as_posix()
        digest.update(rel_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).hexdigest().encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def _source_manifest_hash(pack_root: Path, findings: list[str]) -> str | None:
    payload = _read_json(pack_root / "source-manifest.json", "source-manifest.json", findings)
    if isinstance(payload, dict):
        value = payload.get("source_manifest_hash")
        if isinstance(value, str):
            return value
        findings.append("missing_or_invalid_field:source_manifest_hash")
    return None


def _read_json(path: Path, label: str, findings: list[str]) -> object | None:
    if path.is_symlink():
        findings.append(f"symlink_entry:{label}")
        return None
    if not path.is_file():
        findings.append(f"missing_json:{label}")
        return None
    try:
        size = path.stat().st_size
    except OSError:
        findings.append(f"unreadable_payload:{label}")
        return None
    if size > MAX_ENTRY_BYTES:
        findings.append(f"oversized_entry:{label}")
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        findings.append(f"unreadable_payload:{label}")
        return None
    except UnicodeDecodeError:
        findings.append(f"binary_payload:{label}")
        return None
    findings.extend(scan_sensitive_payload(text))
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        findings.append(f"invalid_json:{label}")
        return None


def _validate_common_authority(
    payload: dict[str, object], label: str, findings: list[str], *, require_claims: bool
) -> None:
    if payload.get("schema_version") != 1:
        findings.append(f"invalid_schema_version:{label}")
    expected = {
        "authority": AUTHORITY,
        "adoption_status": ADOPTION_STATUS,
        "bundle_generation_not_promotion": BUNDLE_GENERATION_NOT_PROMOTION,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            findings.append(f"invalid_{key}:{label}")
    claims = payload.get("authority_claims")
    if not require_claims and claims is None:
        return
    if not isinstance(claims, dict):
        findings.append(f"missing_or_invalid_field:{label}:authority_claims")
        return
    for key in (
        "node_creation_performed",
        "canonical_written",
        "assurance_mutated",
        "reviewer_pass_claimed",
        "execution_ready",
        "pr_ready",
    ):
        if claims.get(key) is not False:
            findings.append(f"forbidden_authority_claim:{key}")


def _string_field(payload: dict[str, object], key: str, label: str, findings: list[str]) -> str | None:
    value = payload.get(key)
    if isinstance(value, str) and value:
        return value
    findings.append(f"missing_or_invalid_field:{label}:{key}")
    return None


def _record_duplicate(seen: dict[str, int], value: str, finding: str, findings: list[str]) -> None:
    seen[value] = seen.get(value, 0) + 1
    if seen[value] == 2:
        findings.append(f"{finding}:{value}")


def _safe_rel(value: str, findings: list[str]) -> str | None:
    rel = PurePosixPath(value)
    if rel.is_absolute() or any(part == ".." for part in rel.parts):
        findings.append(f"path_traversal:{value}")
        return None
    if any(part.startswith(".") for part in rel.parts):
        findings.append(f"hidden_path:{value}")
        return None
    parts = tuple(part.lower() for part in rel.parts)
    if parts and parts[0] in {"users", "home", "volumes", "private"}:
        findings.append(f"host_local_path:{value}")
        return None
    if any(part in {".oracle", ".ssh"} for part in parts):
        findings.append(f"host_local_path:{value}")
        return None
    if any(
        part in {"secret", "secrets", "token", "tokens", "credential", "credentials", "password", "passwords"}
        or "api-key" in part
        or "api_key" in part
        for part in parts
    ):
        findings.append(f"secret_path:{value}")
        return None
    if rel.suffix.lower() != ".json":
        findings.append(f"unsupported_suffix:{value}")
        return None
    return rel.as_posix()


def _validate_parent_trace(
    payload: dict[str, object],
    *,
    candidate_kind: CandidateKind,
    candidate_id: str,
    expected_parent_initiative: str | None,
    expected_parent_epic: str | None,
    comparison: list[str],
    findings: list[str],
) -> None:
    trace = payload.get("parent_trace")
    if not isinstance(trace, dict):
        findings.append(f"missing_or_invalid_field:{candidate_id}:parent_trace")
        return
    if candidate_kind == "initiative-epic" and expected_parent_initiative:
        if trace.get("initiative_id") != expected_parent_initiative:
            comparison.append(f"parent_initiative_mismatch:{candidate_id}")
    if candidate_kind == "epic-issue" and expected_parent_epic:
        if trace.get("epic_id") != expected_parent_epic:
            comparison.append(f"parent_epic_mismatch:{candidate_id}")


def _validate_boundary(
    payload: dict[str, object], candidate_id: str, scope_signatures: dict[str, int], findings: list[str]
) -> None:
    boundary = payload.get("boundary")
    if not isinstance(boundary, dict):
        findings.append(f"missing_or_invalid_field:{candidate_id}:boundary")
        return
    scope = _string_list(boundary.get("scope"))
    non_scope = _string_list(boundary.get("non_scope"))
    if not scope:
        findings.append(f"missing_or_invalid_field:{candidate_id}:boundary.scope")
    if not non_scope:
        findings.append(f"missing_or_invalid_field:{candidate_id}:boundary.non_scope")
    overlap = sorted(set(scope).intersection(non_scope))
    if overlap:
        findings.append(f"overlapping_boundary:{candidate_id}")
    signature = "\0".join(sorted(scope))
    if signature:
        _record_duplicate(scope_signatures, signature, "duplicate_scope_signature", findings)


def _validate_epic_candidate(
    payload: dict[str, object], candidate_id: str, candidate_ids: set[str], findings: list[str]
) -> None:
    if payload.get("approval_gate") != "human_approval_before_epic_node_creation":
        findings.append(f"invalid_approval_gate:{candidate_id}")
    epic_boundary = payload.get("epic_boundary")
    if not isinstance(epic_boundary, dict):
        findings.append(f"missing_or_invalid_field:{candidate_id}:epic_boundary")
        return
    dependencies = epic_boundary.get("depends_on_epic_candidates")
    if dependencies is None:
        return
    if not isinstance(dependencies, list) or not all(isinstance(item, str) for item in dependencies):
        findings.append(f"missing_or_invalid_field:{candidate_id}:epic_boundary.depends_on_epic_candidates")
        return
    for dependency in dependencies:
        if dependency not in candidate_ids:
            findings.append(f"unknown_epic_candidate_dependency:{candidate_id}:{dependency}")


def _validate_issue_candidate(payload: dict[str, object], candidate_id: str, findings: list[str]) -> None:
    grade = payload.get("grade_recommendation")
    if isinstance(grade, dict):
        grade_value = grade.get("grade")
        if grade_value is not None and grade_value not in ALLOWED_PROFILES:
            findings.append(f"unsupported_grade:{candidate_id}")
        if grade.get("advisory_only") is not True:
            findings.append(f"non_advisory_grade_recommendation:{candidate_id}")
    profile = payload.get("profile_recommendation")
    if isinstance(profile, dict):
        profile_value = profile.get("profile")
        if profile_value is not None and profile_value not in ALLOWED_PROFILES:
            findings.append(f"unsupported_profile:{candidate_id}")
        if profile.get("authorized_profile") is not None:
            findings.append(f"forbidden_authority_claim:authorized_profile:{candidate_id}")
        if profile.get("advisory_only") is not True or profile.get("ignored_for_authority") is not True:
            findings.append(f"non_advisory_profile_recommendation:{candidate_id}")


def _validate_drafts(
    pack_root: Path, payload: dict[str, object], *, candidate_path: str, candidate_id: str, findings: list[str]
) -> None:
    draft_files = payload.get("draft_files")
    if not isinstance(draft_files, dict):
        findings.append(f"missing_or_invalid_field:{candidate_id}:draft_files")
        return
    candidate_dir = PurePosixPath(candidate_path).parent
    for key in ("requirement", "design", "plan"):
        value = draft_files.get(key)
        if not isinstance(value, str) or not value:
            findings.append(f"missing_or_invalid_field:{candidate_id}:draft_files.{key}")
            continue
        rel = PurePosixPath(value)
        if rel.is_absolute() or any(part == ".." for part in rel.parts):
            findings.append(f"path_traversal:{candidate_id}:{key}")
            continue
        if any(part.startswith(".") for part in rel.parts):
            findings.append(f"hidden_path:{candidate_id}:{key}")
            continue
        lower_parts = tuple(part.lower() for part in rel.parts)
        if any(
            part in {"secret", "secrets", "token", "tokens", "credential", "credentials", "password", "passwords"}
            or "api-key" in part
            or "api_key" in part
            or "token" in part
            or "secret" in part
            or "credential" in part
            for part in lower_parts
        ):
            findings.append(f"secret_path:{candidate_id}:{key}")
            continue
        if rel.suffix.lower() != ".md":
            findings.append(f"unsupported_suffix:{candidate_id}:{key}")
            continue
        target = pack_root / candidate_dir / rel
        if target.is_symlink():
            findings.append(f"symlink_entry:{candidate_id}:{key}")
            continue
        if not target.is_file():
            findings.append(f"missing_draft:{candidate_id}:{key}")
            continue
        stat_result = target.stat()
        if stat_result.st_mode & 0o111:
            findings.append(f"executable_entry:{candidate_id}:{key}")
        if stat_result.st_size > MAX_ENTRY_BYTES:
            findings.append(f"oversized_entry:{candidate_id}:{key}")
            continue
        try:
            text = target.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(f"binary_payload:{candidate_id}:{key}")
            continue
        findings.extend(scan_authoring_payload(text))


def _string_list(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, str) and item)


def _status_from_findings(findings: list[str], comparison: list[str]) -> CandidateStatus:
    if any(_is_rejected(finding) for finding in findings):
        return "rejected"
    if comparison:
        return "stale"
    if findings:
        return "fail"
    return "pass"


def _is_rejected(finding: str) -> bool:
    prefixes = (
        "path_traversal:",
        "host_local_path:",
        "secret_path:",
        "hidden_path:",
        "unsupported_suffix:",
        "symlink_entry:",
        "executable_entry:",
        "oversized_entry:",
        "binary_payload:",
        "secret_like_payload:",
        "raw_transcript:",
        "forbidden_authority_claim:",
        "non_advisory_",
        "secret_path:",
    )
    return finding.startswith(prefixes)
