from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from datetime import datetime
import hashlib
import json
import math
from pathlib import PurePosixPath
import re
from typing import TYPE_CHECKING, Any, Literal, cast

from spec_dock_runtime.domain.ids import normalize_id_input

if TYPE_CHECKING:
    from collections.abc import Mapping

PlanningMode = Literal["archive-candidate", "git-bound"]
PlanningStatus = Literal[
    "ok",
    "ready",
    "blocked",
    "stale",
    "rejected",
    "rolled_back",
    "recovery_required",
    "publication_pending",
    "blocked_remote_diverged",
]
ReviewSeverity = Literal["p0", "p1", "p2", "p3"]
ReviewVerdict = Literal["pass", "fail"]
RevisionLane = Literal["semantic", "mechanical"]

_SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_REASON_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
_REPOSITORY_RE = re.compile(r"^[^/\s]+/[^/\s]+$")
_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")
_CANONICAL_FILENAMES = ("design.md", "plan.md", "requirement.md")
_SUCCESS_PAIRS = {
    ("ok", "candidate_created"),
    ("ok", "candidate_revised"),
    ("ok", "review_completed"),
    ("ready", "adoption_published"),
}
_STATUSES = {
    "ok",
    "ready",
    "blocked",
    "stale",
    "rejected",
    "rolled_back",
    "recovery_required",
    "publication_pending",
    "blocked_remote_diverged",
}


def _strict_json_object(data: bytes) -> dict[str, Any]:
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise ValueError("JSON must be valid UTF-8") from error

    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def reject_constant(value: str) -> None:
        raise ValueError(f"non-standard JSON number: {value}")

    try:
        value = json.loads(
            text,
            object_pairs_hook=reject_duplicates,
            parse_constant=reject_constant,
        )
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError("invalid JSON") from error
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object")
    return cast("dict[str, Any]", value)


def _closed_object(
    value: Mapping[str, Any],
    *,
    required: set[str],
    optional: set[str] | None = None,
    contract: str,
) -> None:
    allowed = required | (optional or set())
    keys = set(value)
    missing = required - keys
    unknown = keys - allowed
    if missing:
        raise ValueError(f"{contract} missing keys: {', '.join(sorted(missing))}")
    if unknown:
        raise ValueError(f"{contract} unknown keys: {', '.join(sorted(unknown))}")


def _non_empty(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip() or _CONTROL_RE.search(value):
        raise ValueError(f"{field_name} must be a non-empty string without control characters")
    return value.strip()


def _issue_id(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("issue_id must be a string")
    try:
        normalized = normalize_id_input(value, prefix="iss", field="issue_id")
    except RuntimeError as error:
        raise ValueError(str(error)) from error
    if value.strip().lower() != normalized:
        raise ValueError(f"issue_id must be canonical: {normalized}")
    return normalized


def _node_id(value: Any, *, prefix: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    try:
        normalized = normalize_id_input(value, prefix=prefix, field=field_name)
    except RuntimeError as error:
        raise ValueError(str(error)) from error
    if value.strip().lower() != normalized:
        raise ValueError(f"{field_name} must be canonical: {normalized}")
    return normalized


def _repository(value: Any, *, field_name: str) -> str:
    text = _non_empty(value, field_name=field_name)
    if not _REPOSITORY_RE.fullmatch(text):
        raise ValueError(f"{field_name} must be owner/name")
    if text != text.lower():
        raise ValueError(f"{field_name} must be normalized lowercase owner/name")
    return text


def _sha(value: Any, *, length: int, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a lowercase hexadecimal string")
    pattern = _SHA40_RE if length == 40 else _SHA256_RE
    if not pattern.fullmatch(value):
        raise ValueError(f"{field_name} must be a lowercase {length}-hex digest")
    return value


def _safe_relative_path(value: Any, *, field_name: str) -> str:
    text = _non_empty(value, field_name=field_name)
    if "\\" in text:
        raise ValueError(f"{field_name} must use POSIX separators")
    path = PurePosixPath(text)
    if (
        path.is_absolute()
        or text in (".", "..")
        or text != path.as_posix()
        or any(part in ("", ".", "..") for part in path.parts)
    ):
        raise ValueError(f"{field_name} must be a safe repository-relative POSIX path")
    return text


def _string_tuple(value: Any, *, field_name: str, allow_empty: bool = True) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{field_name} must be an array")
    items = tuple(_non_empty(item, field_name=field_name) for item in value)
    if not allow_empty and not items:
        raise ValueError(f"{field_name} must not be empty")
    if len(set(items)) != len(items):
        raise ValueError(f"{field_name} must not contain duplicates")
    return items


def _canonical_paths(value: Any) -> tuple[str, str, str]:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError("canonical paths must contain exactly three paths")
    paths = tuple(_safe_relative_path(item, field_name="canonical path") for item in value)
    parents = {PurePosixPath(path).parent for path in paths}
    if len(parents) != 1:
        raise ValueError("canonical paths must share one Issue directory")
    if tuple(PurePosixPath(path).name for path in paths) != _CANONICAL_FILENAMES:
        raise ValueError("canonical paths must be design.md, plan.md, requirement.md")
    expected = tuple(sorted(paths, key=lambda path: path.encode("utf-8")))
    if paths != expected:
        raise ValueError("canonical paths must be in UTF-8 byte order")
    return cast("tuple[str, str, str]", paths)


def _canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _canonical_digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def raw_bytes_sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _validate_json_value(value: Any, *, field_name: str) -> None:
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        if math.isfinite(value):
            return
        raise ValueError(f"{field_name} contains a non-finite number")
    if isinstance(value, list):
        for item in value:
            _validate_json_value(item, field_name=field_name)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{field_name} contains a non-string key")
            _validate_json_value(item, field_name=field_name)
        return
    raise ValueError(f"{field_name} contains a non-JSON value: {type(value).__name__}")


@dataclass(frozen=True)
class PlanningContext:
    issue_id: str
    repository: str
    branch: str
    source_head: str
    parent_epic_id: str
    parent_initiative_id: str
    dependency_summary: tuple[str, ...]
    canonical_issue_paths: tuple[str, str, str]
    relevant_source_paths: tuple[str, ...]
    operator_context: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "issue_id", _issue_id(self.issue_id))
        object.__setattr__(self, "repository", _repository(self.repository, field_name="repository"))
        object.__setattr__(self, "branch", _non_empty(self.branch, field_name="branch"))
        object.__setattr__(self, "source_head", _sha(self.source_head, length=40, field_name="source_head"))
        object.__setattr__(
            self,
            "parent_epic_id",
            _node_id(self.parent_epic_id, prefix="epic", field_name="parent_epic_id"),
        )
        object.__setattr__(
            self,
            "parent_initiative_id",
            _node_id(self.parent_initiative_id, prefix="init", field_name="parent_initiative_id"),
        )
        object.__setattr__(
            self,
            "dependency_summary",
            _string_tuple(self.dependency_summary, field_name="dependency_summary"),
        )
        object.__setattr__(self, "canonical_issue_paths", _canonical_paths(self.canonical_issue_paths))
        relevant = tuple(
            _safe_relative_path(path, field_name="relevant_source_paths") for path in self.relevant_source_paths
        )
        if len(set(relevant)) != len(relevant):
            raise ValueError("relevant_source_paths must not contain duplicates")
        object.__setattr__(self, "relevant_source_paths", relevant)
        object.__setattr__(
            self,
            "operator_context",
            _string_tuple(self.operator_context, field_name="operator_context"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "issue_id": self.issue_id,
            "repository": self.repository,
            "branch": self.branch,
            "source_head": self.source_head,
            "parent_epic_id": self.parent_epic_id,
            "parent_initiative_id": self.parent_initiative_id,
            "dependency_summary": list(self.dependency_summary),
            "canonical_issue_paths": list(self.canonical_issue_paths),
            "relevant_source_paths": list(self.relevant_source_paths),
            "operator_context": list(self.operator_context),
        }


@dataclass(frozen=True)
class IssueCandidateIdentity:
    issue_id: str
    candidate_id: str
    version: int
    logical_filename: str
    observed_transport_filename: str
    internal_root: str
    source_repository: str
    source_branch: str
    source_head: str
    zip_sha256: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "issue_id", _issue_id(self.issue_id))
        object.__setattr__(self, "candidate_id", _non_empty(self.candidate_id, field_name="candidate_id"))
        if isinstance(self.version, bool) or not isinstance(self.version, int) or self.version < 1:
            raise ValueError("version must be a positive integer")
        logical = _zip_basename(self.logical_filename, field_name="logical_filename")
        observed = _zip_basename(
            self.observed_transport_filename,
            field_name="observed_transport_filename",
        )
        logical_path = PurePosixPath(logical)
        alias_pattern = re.compile(
            rf"^{re.escape(logical_path.stem)} \([1-9][0-9]*\){re.escape(logical_path.suffix)}$"
        )
        if observed != logical and not alias_pattern.fullmatch(observed):
            raise ValueError("observed_transport_filename is not a closed transport alias")
        object.__setattr__(self, "logical_filename", logical)
        object.__setattr__(self, "observed_transport_filename", observed)
        object.__setattr__(
            self,
            "internal_root",
            _safe_relative_path(self.internal_root, field_name="internal_root"),
        )
        object.__setattr__(
            self,
            "source_repository",
            _repository(self.source_repository, field_name="source_repository"),
        )
        object.__setattr__(
            self,
            "source_branch",
            _non_empty(self.source_branch, field_name="source_branch"),
        )
        object.__setattr__(
            self,
            "source_head",
            _sha(self.source_head, length=40, field_name="source_head"),
        )
        object.__setattr__(
            self,
            "zip_sha256",
            _sha(self.zip_sha256, length=64, field_name="zip_sha256"),
        )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> IssueCandidateIdentity:
        required = {
            "issue_id",
            "candidate_id",
            "version",
            "logical_filename",
            "observed_transport_filename",
            "internal_root",
            "source_repository",
            "source_branch",
            "source_head",
            "zip_sha256",
        }
        _closed_object(value, required=required, contract="IssueCandidateIdentity")
        return cls(**{key: value[key] for key in required})

    @classmethod
    def from_json_bytes(cls, data: bytes) -> IssueCandidateIdentity:
        return cls.from_dict(_strict_json_object(data))

    def to_dict(self) -> dict[str, Any]:
        return {
            "issue_id": self.issue_id,
            "candidate_id": self.candidate_id,
            "version": self.version,
            "logical_filename": self.logical_filename,
            "observed_transport_filename": self.observed_transport_filename,
            "internal_root": self.internal_root,
            "source_repository": self.source_repository,
            "source_branch": self.source_branch,
            "source_head": self.source_head,
            "zip_sha256": self.zip_sha256,
        }


def _zip_basename(value: Any, *, field_name: str) -> str:
    text = _non_empty(value, field_name=field_name)
    path = PurePosixPath(text)
    if text != path.name or path.suffix != ".zip":
        raise ValueError(f"{field_name} must be a basename-only .zip filename")
    return text


@dataclass(frozen=True)
class ReviewedPlanningIdentity:
    mode: PlanningMode
    issue_id: str
    repository: str
    branch: str
    source_head: str
    candidate_identity: IssueCandidateIdentity | None = None
    canonical_target_paths: tuple[str, str, str] | None = None
    expected_canonical_target_paths: InitVar[tuple[str, str, str] | None] = None

    def __post_init__(
        self,
        expected_canonical_target_paths: tuple[str, str, str] | None,
    ) -> None:
        if self.mode not in ("archive-candidate", "git-bound"):
            raise ValueError("mode must be archive-candidate or git-bound")
        object.__setattr__(self, "issue_id", _issue_id(self.issue_id))
        object.__setattr__(self, "repository", _repository(self.repository, field_name="repository"))
        object.__setattr__(self, "branch", _non_empty(self.branch, field_name="branch"))
        object.__setattr__(self, "source_head", _sha(self.source_head, length=40, field_name="source_head"))
        if self.mode == "archive-candidate":
            if self.candidate_identity is None or self.canonical_target_paths is not None:
                raise ValueError("archive-candidate identity requires only candidate_identity")
            candidate = self.candidate_identity
            if (
                candidate.issue_id != self.issue_id
                or candidate.source_repository != self.repository
                or candidate.source_branch != self.branch
                or candidate.source_head != self.source_head
            ):
                raise ValueError("archive candidate identity does not match reviewed identity")
        else:
            if self.candidate_identity is not None or self.canonical_target_paths is None:
                raise ValueError("git-bound identity requires only canonical_target_paths")
            object.__setattr__(
                self,
                "canonical_target_paths",
                _canonical_paths(self.canonical_target_paths),
            )
            if expected_canonical_target_paths is None:
                raise ValueError("git-bound identity requires expected canonical target paths")
            self.validate_canonical_target_paths(expected_canonical_target_paths)

    @classmethod
    def from_dict(
        cls,
        value: Mapping[str, Any],
        *,
        expected_canonical_target_paths: tuple[str, str, str] | None = None,
    ) -> ReviewedPlanningIdentity:
        common = {"mode", "issue_id", "repository", "branch", "source_head"}
        mode = value.get("mode")
        if mode == "archive-candidate":
            _closed_object(
                value,
                required=common | {"candidate_identity"},
                contract="ReviewedPlanningIdentity",
            )
            candidate_raw = value["candidate_identity"]
            if not isinstance(candidate_raw, dict):
                raise ValueError("candidate_identity must be an object")
            return cls(
                mode="archive-candidate",
                issue_id=value["issue_id"],
                repository=value["repository"],
                branch=value["branch"],
                source_head=value["source_head"],
                candidate_identity=IssueCandidateIdentity.from_dict(candidate_raw),
            )
        if mode == "git-bound":
            _closed_object(
                value,
                required=common | {"canonical_target_paths"},
                contract="ReviewedPlanningIdentity",
            )
            identity = cls(
                mode="git-bound",
                issue_id=value["issue_id"],
                repository=value["repository"],
                branch=value["branch"],
                source_head=value["source_head"],
                canonical_target_paths=_canonical_paths(value["canonical_target_paths"]),
                expected_canonical_target_paths=expected_canonical_target_paths,
            )
            return identity
        raise ValueError("mode must be archive-candidate or git-bound")

    @classmethod
    def from_json_bytes(
        cls,
        data: bytes,
        *,
        expected_canonical_target_paths: tuple[str, str, str] | None = None,
    ) -> ReviewedPlanningIdentity:
        return cls.from_dict(
            _strict_json_object(data),
            expected_canonical_target_paths=expected_canonical_target_paths,
        )

    def to_dict(self) -> dict[str, Any]:
        base: dict[str, Any] = {
            "mode": self.mode,
            "issue_id": self.issue_id,
            "repository": self.repository,
            "branch": self.branch,
            "source_head": self.source_head,
        }
        if self.mode == "archive-candidate":
            assert self.candidate_identity is not None
            base["candidate_identity"] = self.candidate_identity.to_dict()
        else:
            assert self.canonical_target_paths is not None
            base["canonical_target_paths"] = list(self.canonical_target_paths)
        return base

    @property
    def sha256(self) -> str:
        return _canonical_digest(self.to_dict())

    def validate_canonical_target_paths(
        self,
        expected_paths: tuple[str, str, str],
    ) -> None:
        if self.mode != "git-bound" or self.canonical_target_paths is None:
            raise ValueError("canonical target path binding is only valid for git-bound identity")
        expected = _canonical_paths(expected_paths)
        if self.canonical_target_paths != expected:
            raise ValueError("canonical target paths do not match the resolved Issue target")


@dataclass(frozen=True)
class PlanningReviewFinding:
    id: str
    severity: ReviewSeverity
    exact_location: str
    violated_requirement_or_contradiction: str
    concrete_impact: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", _non_empty(self.id, field_name="finding id"))
        if self.severity not in ("p0", "p1", "p2", "p3"):
            raise ValueError("severity must be p0, p1, p2, or p3")
        for field_name in (
            "exact_location",
            "violated_requirement_or_contradiction",
            "concrete_impact",
        ):
            object.__setattr__(
                self,
                field_name,
                _non_empty(getattr(self, field_name), field_name=field_name),
            )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> PlanningReviewFinding:
        required = {
            "id",
            "severity",
            "exact_location",
            "violated_requirement_or_contradiction",
            "concrete_impact",
        }
        _closed_object(value, required=required, contract="PlanningReviewFinding")
        return cls(**{key: value[key] for key in required})

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "severity": self.severity,
            "exact_location": self.exact_location,
            "violated_requirement_or_contradiction": self.violated_requirement_or_contradiction,
            "concrete_impact": self.concrete_impact,
        }


@dataclass(frozen=True)
class PlanningReviewResult:
    reviewed_identity: ReviewedPlanningIdentity
    reviewed_identity_sha256: str
    verdict: ReviewVerdict
    findings: tuple[PlanningReviewFinding, ...]

    def __post_init__(self) -> None:
        digest = _sha(
            self.reviewed_identity_sha256,
            length=64,
            field_name="reviewed_identity_sha256",
        )
        if digest != self.reviewed_identity.sha256:
            raise ValueError("reviewed identity digest mismatch")
        if self.verdict not in ("pass", "fail"):
            raise ValueError("verdict must be pass or fail")
        ids = tuple(finding.id for finding in self.findings)
        if len(set(ids)) != len(ids):
            raise ValueError("finding IDs must be unique")
        expected = "fail" if any(finding.severity in ("p0", "p1") for finding in self.findings) else "pass"
        if self.verdict != expected:
            raise ValueError("verdict contradicts P0/P1 blocking findings")

    @classmethod
    def from_dict(
        cls,
        value: Mapping[str, Any],
        *,
        expected_canonical_target_paths: tuple[str, str, str] | None = None,
    ) -> PlanningReviewResult:
        required = {"reviewed_identity", "reviewed_identity_sha256", "verdict", "findings"}
        _closed_object(value, required=required, contract="PlanningReviewResult")
        identity_raw = value["reviewed_identity"]
        findings_raw = value["findings"]
        if not isinstance(identity_raw, dict):
            raise ValueError("reviewed_identity must be an object")
        if not isinstance(findings_raw, list):
            raise ValueError("findings must be an array")
        findings: list[PlanningReviewFinding] = []
        for item in findings_raw:
            if not isinstance(item, dict):
                raise ValueError("each finding must be an object")
            findings.append(PlanningReviewFinding.from_dict(item))
        return cls(
            reviewed_identity=ReviewedPlanningIdentity.from_dict(
                identity_raw,
                expected_canonical_target_paths=expected_canonical_target_paths,
            ),
            reviewed_identity_sha256=value["reviewed_identity_sha256"],
            verdict=value["verdict"],
            findings=tuple(findings),
        )

    @classmethod
    def from_json_bytes(
        cls,
        data: bytes,
        *,
        expected_canonical_target_paths: tuple[str, str, str] | None = None,
    ) -> PlanningReviewResult:
        return cls.from_dict(
            _strict_json_object(data),
            expected_canonical_target_paths=expected_canonical_target_paths,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "reviewed_identity": self.reviewed_identity.to_dict(),
            "reviewed_identity_sha256": self.reviewed_identity_sha256,
            "verdict": self.verdict,
            "findings": [finding.to_dict() for finding in self.findings],
        }


@dataclass(frozen=True)
class PlanningRevisionRequestV1:
    schema_version: int
    lane: RevisionLane
    candidate_identity: IssueCandidateIdentity
    preserve_assumptions: tuple[str, ...]
    finding_ids: tuple[str, ...] = ()
    review_result_sha256: str | None = None
    target_file: str | None = None
    old_text: str | None = None
    new_text: str | None = None
    meaning_invariant: str | None = None
    diff_budget: int | None = None

    def __post_init__(self) -> None:
        if isinstance(self.schema_version, bool) or self.schema_version != 1:
            raise ValueError("schema_version must be integer 1")
        if self.lane not in ("semantic", "mechanical"):
            raise ValueError("lane must be semantic or mechanical")
        object.__setattr__(
            self,
            "preserve_assumptions",
            _string_tuple(self.preserve_assumptions, field_name="preserve_assumptions"),
        )
        if self.lane == "semantic":
            object.__setattr__(
                self,
                "finding_ids",
                _string_tuple(self.finding_ids, field_name="finding_ids", allow_empty=False),
            )
            if self.review_result_sha256 is None:
                raise ValueError("semantic revision requires review_result_sha256")
            object.__setattr__(
                self,
                "review_result_sha256",
                _sha(self.review_result_sha256, length=64, field_name="review_result_sha256"),
            )
            if any(
                value is not None
                for value in (
                    self.target_file,
                    self.old_text,
                    self.new_text,
                    self.meaning_invariant,
                    self.diff_budget,
                )
            ):
                raise ValueError("semantic revision contains mechanical fields")
        else:
            if self.finding_ids or self.review_result_sha256 is not None:
                raise ValueError("mechanical revision contains semantic fields")
            if self.target_file not in ("requirement.md", "design.md", "plan.md"):
                raise ValueError("mechanical target_file is not allowed")
            old_text = _non_empty(self.old_text, field_name="old_text")
            new_text = _non_empty(self.new_text, field_name="new_text")
            if old_text == new_text:
                raise ValueError("old_text and new_text must differ")
            object.__setattr__(self, "old_text", old_text)
            object.__setattr__(self, "new_text", new_text)
            object.__setattr__(
                self,
                "meaning_invariant",
                _non_empty(self.meaning_invariant, field_name="meaning_invariant"),
            )
            if isinstance(self.diff_budget, bool) or not isinstance(self.diff_budget, int) or self.diff_budget < 1:
                raise ValueError("diff_budget must be a positive integer")

    @classmethod
    def from_json_bytes(cls, data: bytes) -> PlanningRevisionRequestV1:
        value = _strict_json_object(data)
        lane = value.get("lane")
        common = {"schema_version", "lane", "candidate_identity", "preserve_assumptions"}
        if lane == "semantic":
            required = common | {"finding_ids", "review_result_sha256"}
        elif lane == "mechanical":
            required = common | {"target_file", "old_text", "new_text", "meaning_invariant", "diff_budget"}
        else:
            raise ValueError("lane must be semantic or mechanical")
        _closed_object(value, required=required, contract="PlanningRevisionRequestV1")
        candidate_raw = value["candidate_identity"]
        if not isinstance(candidate_raw, dict):
            raise ValueError("candidate_identity must be an object")
        kwargs = {key: value[key] for key in required if key not in common}
        return cls(
            schema_version=value["schema_version"],
            lane=lane,
            candidate_identity=IssueCandidateIdentity.from_dict(candidate_raw),
            preserve_assumptions=_string_tuple(value["preserve_assumptions"], field_name="preserve_assumptions"),
            **kwargs,
        )

    def validate_against(self, review_result: PlanningReviewResult, review_result_bytes: bytes) -> None:
        if self.lane != "semantic":
            raise ValueError("only semantic revisions bind to a Review result")
        if self.review_result_sha256 != raw_bytes_sha256(review_result_bytes):
            raise ValueError("Review result raw bytes digest mismatch")
        if review_result.reviewed_identity.mode != "archive-candidate":
            raise ValueError("semantic revision must match an archive Candidate Review")
        parsed_review_result = PlanningReviewResult.from_json_bytes(review_result_bytes)
        if parsed_review_result != review_result:
            raise ValueError("Review result object does not match exact Review result bytes")
        identity = review_result.reviewed_identity
        if identity.mode != "archive-candidate" or identity.candidate_identity != self.candidate_identity:
            raise ValueError("semantic revision must match an archive Candidate Review")
        findings = {finding.id: finding for finding in review_result.findings}
        selected: list[PlanningReviewFinding] = []
        for finding_id in self.finding_ids:
            finding = findings.get(finding_id)
            if finding is None:
                raise ValueError(f"unknown Review finding ID: {finding_id}")
            selected.append(finding)
        if any(finding.severity not in ("p0", "p1") for finding in selected):
            raise ValueError("semantic revision may select only P0/P1 findings")

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema_version": self.schema_version,
            "lane": self.lane,
            "candidate_identity": self.candidate_identity.to_dict(),
            "preserve_assumptions": list(self.preserve_assumptions),
        }
        if self.lane == "semantic":
            payload["finding_ids"] = list(self.finding_ids)
            payload["review_result_sha256"] = self.review_result_sha256
        else:
            payload.update(
                {
                    "target_file": self.target_file,
                    "old_text": self.old_text,
                    "new_text": self.new_text,
                    "meaning_invariant": self.meaning_invariant,
                    "diff_budget": self.diff_budget,
                }
            )
        return payload


@dataclass(frozen=True)
class PlanningHumanDecisionV1:
    schema_version: int
    issue_id: str
    reviewed_identity: ReviewedPlanningIdentity
    reviewed_identity_sha256: str
    review_result_sha256: str
    decision: Literal["approved", "rejected"]
    plan_adoption: bool
    implementation_start: bool
    decided_at: str

    def __post_init__(self) -> None:
        if isinstance(self.schema_version, bool) or self.schema_version != 1:
            raise ValueError("schema_version must be integer 1")
        object.__setattr__(self, "issue_id", _issue_id(self.issue_id))
        if self.issue_id != self.reviewed_identity.issue_id:
            raise ValueError("Human decision issue does not match reviewed identity")
        digest = _sha(
            self.reviewed_identity_sha256,
            length=64,
            field_name="reviewed_identity_sha256",
        )
        if digest != self.reviewed_identity.sha256:
            raise ValueError("reviewed identity digest mismatch")
        object.__setattr__(
            self,
            "review_result_sha256",
            _sha(self.review_result_sha256, length=64, field_name="review_result_sha256"),
        )
        if not isinstance(self.plan_adoption, bool) or not isinstance(self.implementation_start, bool):
            raise ValueError("Human decision flags must be booleans")
        valid = (
            self.decision == "approved"
            and self.plan_adoption
            and self.implementation_start
        ) or (
            self.decision == "rejected"
            and not self.plan_adoption
            and not self.implementation_start
        )
        if not valid:
            raise ValueError("Human decision truth table violation")
        decided_at = _non_empty(self.decided_at, field_name="decided_at")
        try:
            parsed = datetime.fromisoformat(decided_at.replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError("decided_at must be ISO-8601") from error
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("decided_at must include a timezone")

    @classmethod
    def from_json_bytes(
        cls,
        data: bytes,
        *,
        review_result_bytes: bytes,
        expected_canonical_target_paths: tuple[str, str, str] | None = None,
    ) -> PlanningHumanDecisionV1:
        value = _strict_json_object(data)
        required = {
            "schema_version",
            "issue_id",
            "reviewed_identity",
            "reviewed_identity_sha256",
            "review_result_sha256",
            "decision",
            "plan_adoption",
            "implementation_start",
            "decided_at",
        }
        _closed_object(value, required=required, contract="PlanningHumanDecisionV1")
        identity_raw = value["reviewed_identity"]
        if not isinstance(identity_raw, dict):
            raise ValueError("reviewed_identity must be an object")
        decision = cls(
            schema_version=value["schema_version"],
            issue_id=value["issue_id"],
            reviewed_identity=ReviewedPlanningIdentity.from_dict(
                identity_raw,
                expected_canonical_target_paths=expected_canonical_target_paths,
            ),
            reviewed_identity_sha256=value["reviewed_identity_sha256"],
            review_result_sha256=value["review_result_sha256"],
            decision=value["decision"],
            plan_adoption=value["plan_adoption"],
            implementation_start=value["implementation_start"],
            decided_at=value["decided_at"],
        )
        if decision.review_result_sha256 != raw_bytes_sha256(review_result_bytes):
            raise ValueError("Review result raw bytes digest mismatch")
        review_result = PlanningReviewResult.from_json_bytes(
            review_result_bytes,
            expected_canonical_target_paths=expected_canonical_target_paths,
        )
        if (
            review_result.reviewed_identity != decision.reviewed_identity
            or review_result.reviewed_identity_sha256 != decision.reviewed_identity_sha256
        ):
            raise ValueError("Review identity does not match Human decision identity")
        return decision

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "issue_id": self.issue_id,
            "reviewed_identity": self.reviewed_identity.to_dict(),
            "reviewed_identity_sha256": self.reviewed_identity_sha256,
            "review_result_sha256": self.review_result_sha256,
            "decision": self.decision,
            "plan_adoption": self.plan_adoption,
            "implementation_start": self.implementation_start,
            "decided_at": self.decided_at,
        }


@dataclass(frozen=True)
class PlanningCommandResult:
    status: PlanningStatus
    reason: str
    issue_id: str
    output: dict[str, Any] = field(default_factory=dict)
    details: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.status not in _STATUSES:
            raise ValueError("invalid planning result status")
        reason = _non_empty(self.reason, field_name="reason")
        if not _REASON_RE.fullmatch(reason):
            raise ValueError("reason must be lower snake_case")
        pair = (self.status, reason)
        if (
            self.status in ("ok", "ready")
            or reason in {item[1] for item in _SUCCESS_PAIRS}
        ) and pair not in _SUCCESS_PAIRS:
            raise ValueError("invalid status/reason success pair")
        object.__setattr__(self, "issue_id", _issue_id(self.issue_id))
        if not isinstance(self.output, dict):
            raise ValueError("output must be a JSON object")
        _validate_json_value(self.output, field_name="output")
        object.__setattr__(self, "output", dict(self.output))
        object.__setattr__(self, "details", _string_tuple(self.details, field_name="details"))

    @property
    def is_ready(self) -> bool:
        return self.status == "ready"

    @property
    def exit_code(self) -> int:
        return 0 if self.status in ("ok", "ready") else 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "reason": self.reason,
            "issue_id": self.issue_id,
            "output": dict(self.output),
            "details": list(self.details),
        }
