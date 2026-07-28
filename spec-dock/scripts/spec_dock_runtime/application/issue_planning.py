from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePath
import re
from typing import TYPE_CHECKING, Any, Literal, cast

from spec_dock_runtime.application.authoring_pack.github_sync_preflight import (
    GitHubSyncPreflightRequest,
    run_github_sync_preflight,
)
from spec_dock_runtime.application.issue_planning_prompt import (
    PlanningPromptAttachment,
    synthesize_issue_planning_prompt,
    synthesize_planning_evidence_prompt,
)
from spec_dock_runtime.domain.authoring_pack.authority_boundary import (
    private_absolute_path_finding,
    scan_constraint_sensitive_payload,
)
from spec_dock_runtime.domain.ids import normalize_id_input
from spec_dock_runtime.domain.issue_planning_candidate import (
    DOCUMENT_NAMES,
    apply_mechanical_revision,
    build_candidate_material,
    parse_current_front_matter_baseline,
    parse_planner_payload,
    render_planner_payload,
)
from spec_dock_runtime.domain.issue_planning_contracts import (
    PlanningCommandResult,
    PlanningContext,
    PlanningHumanDecisionV1,
    PlanningInvocationResult,
    PlanningReviewResult,
    PlanningRevisionRequestV1,
    PlanningSourceEvidence,
    ReviewedPlanningIdentity,
    raw_bytes_sha256,
)
from spec_dock_runtime.infra.clock import now_iso
from spec_dock_runtime.infra.issue_planning_apply import (
    ExpectedPlanningTargets,
    PlanningApplyExecution,
    PlanningApplyOperation,
    PlanningApplyOutputRejected,
    load_expected_planning_targets,
    planning_apply_resume_available,
)
from spec_dock_runtime.infra.issue_planning_candidate import (
    CandidateArchiveRejected,
    CandidateBuildFailed,
    CandidateCollision,
    CandidateOutputRejected,
    CandidatePublicationFailed,
    PublishedCandidate,
    VerifiedIssueCandidate,
    build_and_publish_candidate,
    load_verified_issue_candidate,
    open_safe_directory_descriptor,
    read_bounded_regular_file,
    read_bounded_regular_file_at,
    validate_candidate_output_directory,
)
from spec_dock_runtime.infra.issue_planning_review import (
    PublishedPlanningReview,
    publish_planning_review_evidence,
    read_external_review_result,
)
from spec_dock_runtime.presentation.issue_planning import render_planning_review_summary

MAX_REVIEW_SOURCE_FILE_BYTES = 2_000_000
MAX_REVIEW_SOURCE_TOTAL_BYTES = 10_000_000

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from spec_dock_runtime.domain.authoring_pack.preflight_contract import PreflightResult
    from spec_dock_runtime.infra.contracts import DirectDependencyResolution, StoredMetaRecord


@dataclass(frozen=True)
class PlanningCreateRequest:
    issue_id: str
    output_dir: Path


@dataclass(frozen=True)
class PlanningReviseRequest:
    candidate_path: Path
    request_path: Path
    output_dir: Path


@dataclass(frozen=True)
class PlanningRevisionEvidenceInput:
    review_result_path: Path
    review_result_sha256: str

    def __post_init__(self) -> None:
        if re.fullmatch(r"[0-9a-f]{64}", self.review_result_sha256) is None:
            raise ValueError("review_result_sha256 must be lowercase SHA-256")


@dataclass(frozen=True)
class PlanningReviewRequest:
    issue_id: str
    mode: Literal["archive-candidate", "git-bound"]
    output_dir: Path
    candidate_path: Path | None = None
    reviewed_head: str | None = None


@dataclass(frozen=True)
class PlanningApplyRequest:
    issue_id: str
    mode: Literal["archive-candidate", "git-bound"]
    review_result_path: Path
    human_decision_path: Path
    expected_head: str
    output_dir: Path
    candidate_path: Path | None = None
    logical_filename: str | None = None
    zip_sha256: str | None = None
    reviewed_head: str | None = None


@dataclass(frozen=True)
class ExistingIssueTarget:
    issue_id: str
    parent_epic_id: str
    parent_initiative_id: str
    canonical_issue_paths: tuple[str, str, str]


def resolve_existing_issue_target(
    issue: str,
    records: Sequence[StoredMetaRecord],
    repo_root: Path,
) -> ExistingIssueTarget:
    try:
        issue_id = normalize_id_input(issue, prefix="iss", field="issue")
    except RuntimeError as error:
        raise ValueError("an existing Issue ID is required") from error

    matches = [record for record in records if record.id == issue_id]
    if len(matches) != 1:
        raise ValueError(f"existing Issue not found: {issue_id}")
    record = matches[0]
    if record.kind != "issue":
        raise ValueError(f"existing Issue required: {issue_id}")
    if record.epic_id is None or record.initiative_id is None:
        raise ValueError(f"existing Issue parent identity is incomplete: {issue_id}")
    try:
        parent_epic_id = normalize_id_input(record.epic_id, prefix="epic", field="epic_id")
        parent_initiative_id = normalize_id_input(
            record.initiative_id,
            prefix="init",
            field="initiative_id",
        )
    except RuntimeError as error:
        raise ValueError(f"existing Issue parent identity is invalid: {issue_id}") from error

    root = repo_root.resolve(strict=True)
    raw_path = Path(record.path)
    if ".." in raw_path.parts:
        raise ValueError(f"canonical Issue path must be a safe path without '..': {issue_id}")
    issue_dir = raw_path if raw_path.is_absolute() else root / raw_path
    lexical_issue_dir = issue_dir.absolute()
    if _contains_symlink(root, lexical_issue_dir):
        raise ValueError(f"canonical Issue path must not contain symlinks: {issue_id}")
    try:
        resolved_issue_dir = issue_dir.resolve(strict=True)
    except OSError as error:
        raise ValueError(f"canonical Issue path does not exist: {issue_id}") from error
    initiatives_root = (root / "spec-dock" / "initiatives").resolve(strict=False)
    if not resolved_issue_dir.is_relative_to(initiatives_root):
        raise ValueError(f"canonical Issue path escapes spec-dock/initiatives: {issue_id}")

    paths: list[str] = []
    for filename in ("design.md", "plan.md", "requirement.md"):
        target = resolved_issue_dir / filename
        if target.is_symlink() or not target.is_file():
            raise ValueError(f"canonical Issue target is incomplete: {filename}")
        try:
            relative = target.relative_to(root).as_posix()
        except ValueError as error:
            raise ValueError("canonical Issue target escapes repository") from error
        paths.append(relative)
    ordered = tuple(sorted(paths, key=lambda path: path.encode("utf-8")))
    return ExistingIssueTarget(
        issue_id=issue_id,
        parent_epic_id=parent_epic_id,
        parent_initiative_id=parent_initiative_id,
        canonical_issue_paths=(ordered[0], ordered[1], ordered[2]),
    )


def _contains_symlink(root: Path, target: Path) -> bool:
    try:
        relative = target.relative_to(root)
    except ValueError:
        return False
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def run_issue_planning_apply(
    *,
    request: PlanningApplyRequest,
    records: Sequence[StoredMetaRecord],
    repo_root: Path,
    repo_slug_resolver: Callable[[Path], str | None],
    validation_runner: Callable[[], object],
    sync_runner: Callable[[], object],
    preflight_runner: Callable[
        [GitHubSyncPreflightRequest], PreflightResult
    ] = run_github_sync_preflight,
    candidate_loader: Callable[
        [Path, Path], VerifiedIssueCandidate
    ] = load_verified_issue_candidate,
    expected_target_loader: Callable[
        [Path, str, tuple[str, str, str]], ExpectedPlanningTargets
    ] = load_expected_planning_targets,
    resume_probe: Callable[..., bool] = planning_apply_resume_available,
    transaction_runner: Callable[..., PlanningApplyExecution],
) -> PlanningCommandResult:
    issue_id = request.issue_id
    try:
        target = resolve_existing_issue_target(request.issue_id, records, repo_root)
    except ValueError:
        return PlanningCommandResult(
            status="rejected",
            reason="apply_request_rejected",
            issue_id=issue_id,
        )
    issue_id = target.issue_id
    if not _apply_mode_options_are_closed(request):
        return PlanningCommandResult(
            status="rejected",
            reason="apply_request_rejected",
            issue_id=issue_id,
        )
    try:
        validate_candidate_output_directory(request.output_dir, repo_root)
    except (CandidateOutputRejected, OSError, ValueError):
        return PlanningCommandResult(
            status="rejected",
            reason="apply_output_rejected",
            issue_id=issue_id,
        )
    if not request.review_result_path.exists():
        return PlanningCommandResult(
            status="blocked",
            reason="review_result_unavailable",
            issue_id=issue_id,
        )
    if not request.human_decision_path.exists():
        return PlanningCommandResult(
            status="blocked",
            reason="human_decision_unavailable",
            issue_id=issue_id,
        )
    try:
        review_bytes = _read_external_bounded_file(
            request.review_result_path,
            repo_root=repo_root,
        )
    except OSError:
        return PlanningCommandResult(
            status="blocked",
            reason="review_result_unavailable",
            issue_id=issue_id,
        )
    except (UnicodeDecodeError, ValueError):
        return PlanningCommandResult(
            status="rejected",
            reason="review_result_rejected",
            issue_id=issue_id,
        )
    try:
        human_bytes = _read_external_bounded_file(
            request.human_decision_path,
            repo_root=repo_root,
        )
    except OSError:
        return PlanningCommandResult(
            status="blocked",
            reason="human_decision_unavailable",
            issue_id=issue_id,
        )
    except (UnicodeDecodeError, ValueError):
        return PlanningCommandResult(
            status="rejected",
            reason="human_decision_rejected",
            issue_id=issue_id,
        )
    expected_paths = _review_expected_paths_for_parse(review_bytes, request.mode)
    try:
        review = PlanningReviewResult.from_json_bytes(
            review_bytes,
            expected_canonical_target_paths=expected_paths,
        )
    except ValueError:
        return PlanningCommandResult(
            status="rejected",
            reason="review_result_rejected",
            issue_id=issue_id,
        )
    if _review_result_has_sensitive_content(review):
        return PlanningCommandResult(
            status="rejected",
            reason="review_result_rejected",
            issue_id=issue_id,
        )
    try:
        human = PlanningHumanDecisionV1.from_json_bytes(
            human_bytes,
            review_result_bytes=review_bytes,
            expected_canonical_target_paths=(
                review.reviewed_identity.canonical_target_paths
                if request.mode == "git-bound"
                else None
            ),
        )
    except ValueError:
        return PlanningCommandResult(
            status="rejected",
            reason="human_decision_rejected",
            issue_id=issue_id,
        )
    identity = review.reviewed_identity
    if (
        review.reviewed_identity != human.reviewed_identity
        or identity.issue_id != issue_id
        or human.issue_id != issue_id
        or identity.mode != request.mode
        or request.expected_head != identity.source_head
    ):
        return PlanningCommandResult(
            status="rejected",
            reason="review_identity_rejected",
            issue_id=issue_id,
        )
    if human.decision == "approved" and review.verdict != "pass":
        return PlanningCommandResult(
            status="blocked",
            reason="review_not_passed",
            issue_id=issue_id,
        )

    verified_candidate: VerifiedIssueCandidate | None = None
    if request.mode == "archive-candidate":
        candidate_identity = identity.candidate_identity
        if (
            candidate_identity is None
            or request.logical_filename != candidate_identity.logical_filename
            or request.zip_sha256 != candidate_identity.zip_sha256
        ):
            return PlanningCommandResult(
                status="rejected",
                reason="candidate_identity_rejected",
                issue_id=issue_id,
            )
        assert request.candidate_path is not None
        try:
            verified_candidate = candidate_loader(request.candidate_path, repo_root)
        except CandidateArchiveRejected as error:
            return PlanningCommandResult(
                status="rejected",
                reason="archive_rejected",
                issue_id=issue_id,
                details=tuple(str(item) for item in error.args[0])
                if error.args and isinstance(error.args[0], tuple)
                else (),
            )
        if verified_candidate.identity != candidate_identity:
            return PlanningCommandResult(
                status="stale",
                reason="apply_target_changed",
                issue_id=issue_id,
            )
    else:
        if (
            request.reviewed_head != identity.source_head
            or identity.canonical_target_paths != target.canonical_issue_paths
        ):
            return PlanningCommandResult(
                status="rejected",
                reason="review_identity_rejected",
                issue_id=issue_id,
            )

    repository = repo_slug_resolver(repo_root)
    if repository is None or repository != identity.repository:
        return PlanningCommandResult(
            status="stale",
            reason="apply_target_changed",
            issue_id=issue_id,
        )
    source_paths: tuple[str, ...] = target.canonical_issue_paths
    expected_source_hash: str | None = None
    if verified_candidate is not None:
        baseline = verified_candidate.source_baseline
        canonical = baseline.get("canonical_issue_paths", ())
        relevant = baseline.get("relevant_paths", ())
        if isinstance(canonical, list) and isinstance(relevant, list):
            source_paths = tuple(
                sorted(
                    {
                        *(str(item) for item in canonical),
                        *(str(item) for item in relevant),
                    },
                    key=lambda value: value.encode("utf-8"),
                )
            )
        value = baseline.get("source_manifest_hash")
        expected_source_hash = value if isinstance(value, str) else None
    try:
        expected_targets = expected_target_loader(
            repo_root,
            request.expected_head,
            target.canonical_issue_paths,
        )
    except (OSError, ValueError):
        return PlanningCommandResult(
            status="stale",
            reason="apply_target_changed",
            issue_id=issue_id,
        )
    decided_at = datetime.fromisoformat(human.decided_at.replace("Z", "+00:00"))
    timestamp = decided_at.astimezone(timezone.utc).strftime("%Y%m%dt%H%M%Sz")
    issue_dir = PurePath(target.canonical_issue_paths[0]).parent
    decision_path = (
        issue_dir
        / "artifacts"
        / f"{timestamp}-planning-human-decision-placeholder.json"
    ).as_posix()
    replacements: dict[str, bytes] = {}
    if (
        request.mode == "archive-candidate"
        and human.decision == "approved"
        and verified_candidate is not None
    ):
        replacements = {
            name: verified_candidate.files[name]
            for name in DOCUMENT_NAMES
        }
    try:
        operation = PlanningApplyOperation.create(
            issue_id=issue_id,
            mode=request.mode,
            repository=identity.repository,
            branch=identity.branch,
            expected_head=request.expected_head,
            reviewed_identity=identity,
            reviewed_identity_sha256=review.reviewed_identity_sha256,
            review_result_sha256=raw_bytes_sha256(review_bytes),
            human_decision_sha256=raw_bytes_sha256(human_bytes),
            decision=human.decision,
            canonical_target_paths=target.canonical_issue_paths,
            pre_apply_target_blob_oids=expected_targets.blob_oids,
            candidate_identity=(
                None if verified_candidate is None else verified_candidate.identity
            ),
            decision_artifact_path=decision_path,
            human_decision_bytes=human_bytes,
            replacement_documents=replacements,
            pre_apply_document_bytes=expected_targets.documents,
        )
    except ValueError:
        return PlanningCommandResult(
            status="rejected",
            reason="apply_request_rejected",
            issue_id=issue_id,
        )
    try:
        resume_available = resume_probe(
            operation,
            output_dir=request.output_dir,
        )
    except (OSError, PlanningApplyOutputRejected, ValueError):
        return PlanningCommandResult(
            status="rejected",
            reason="apply_output_rejected",
            issue_id=issue_id,
        )
    if resume_available:
        execution = transaction_runner(
            operation,
            repo_root=repo_root,
            output_dir=request.output_dir,
            validation_runner=validation_runner,
            sync_runner=sync_runner,
        )
        return _planning_result_from_execution(issue_id, execution)

    preflight = preflight_runner(
        GitHubSyncPreflightRequest(
            repo_root=repo_root,
            ref=identity.branch,
            source_paths=source_paths,
            expected_source_hash=expected_source_hash,
        )
    )
    if (
        preflight.status != "pass"
        or preflight.local_head != request.expected_head
        or preflight.remote_head != request.expected_head
    ):
        if request.mode == "archive-candidate" and any(
            blocker in {
                "source_hash_mismatch",
                "dirty_tracked",
                "dirty_untracked",
                "dirty_index",
            }
            for blocker in preflight.blockers
        ):
            return PlanningCommandResult(
                status="stale",
                reason="fresh_review_required",
                issue_id=issue_id,
            )
        if preflight.status == "blocked":
            return PlanningCommandResult(
                status="blocked",
                reason="git_preflight_blocked",
                issue_id=issue_id,
            )
        return PlanningCommandResult(
            status="stale",
            reason="apply_target_changed",
            issue_id=issue_id,
        )
    observed_source_hash = getattr(preflight.source_manifest, "source_manifest_hash", None)
    if expected_source_hash is not None and observed_source_hash != expected_source_hash:
        return PlanningCommandResult(
            status="stale",
            reason="apply_target_changed",
            issue_id=issue_id,
        )
    execution = transaction_runner(
        operation,
        repo_root=repo_root,
        output_dir=request.output_dir,
        validation_runner=validation_runner,
        sync_runner=sync_runner,
    )
    return _planning_result_from_execution(issue_id, execution)


def _planning_result_from_execution(
    issue_id: str,
    execution: PlanningApplyExecution,
) -> PlanningCommandResult:
    return PlanningCommandResult(
        status=execution.status,
        reason=execution.reason,
        issue_id=issue_id,
        output={
            key: value
            for key, value in execution.to_output().items()
            if value is not None
        },
        details=execution.details,
    )


def _apply_mode_options_are_closed(request: PlanningApplyRequest) -> bool:
    if re.fullmatch(r"[0-9a-f]{40}", request.expected_head) is None:
        return False
    if request.mode == "archive-candidate":
        return (
            request.candidate_path is not None
            and request.logical_filename is not None
            and request.zip_sha256 is not None
            and re.fullmatch(r"[0-9a-f]{64}", request.zip_sha256) is not None
            and request.reviewed_head is None
        )
    if request.mode == "git-bound":
        return (
            request.candidate_path is None
            and request.logical_filename is None
            and request.zip_sha256 is None
            and request.reviewed_head is not None
            and re.fullmatch(r"[0-9a-f]{40}", request.reviewed_head) is not None
        )
    return False


def _review_expected_paths_for_parse(
    review_bytes: bytes,
    mode: object,
) -> tuple[str, str, str] | None:
    if mode != "git-bound":
        return None
    try:
        value = json.loads(review_bytes)
        identity = value["reviewed_identity"]
        paths = identity["canonical_target_paths"]
        if (
            isinstance(paths, list)
            and len(paths) == 3
            and all(isinstance(item, str) for item in paths)
        ):
            return (paths[0], paths[1], paths[2])
    except (KeyError, TypeError, json.JSONDecodeError):
        pass
    return None


def _git_blob_oid(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def run_issue_planning_transport(
    *,
    issue: str,
    records: Sequence[StoredMetaRecord],
    repo_root: Path,
    role: Literal["planner", "reviewer"],
    repo_slug_resolver: Callable[[Path], str | None],
    backend_invoker: Callable[..., PlanningInvocationResult],
    dependency_loader: Callable[[str], Sequence[DirectDependencyResolution]] | None = None,
    relevant_source_paths: Sequence[str] = (),
    operator_context: Sequence[str] = (),
    timeout_seconds: float | None = None,
    preflight_runner: Callable[[GitHubSyncPreflightRequest], PreflightResult] = run_github_sync_preflight,
    prompt_synthesizer: Callable[..., Any] = synthesize_issue_planning_prompt,
) -> PlanningInvocationResult:
    target = resolve_existing_issue_target(issue, records, repo_root)
    relevant = tuple(sorted(set(relevant_source_paths), key=lambda value: value.encode("utf-8")))
    source_paths = tuple(
        sorted(
            {*target.canonical_issue_paths, *relevant},
            key=lambda value: value.encode("utf-8"),
        )
    )
    preflight = preflight_runner(
        GitHubSyncPreflightRequest(
            repo_root=repo_root,
            ref=None,
            allow_default_branch_fallback=False,
            source_paths=source_paths,
        )
    )
    if preflight.status != "pass" or preflight.repository is None:
        return PlanningInvocationResult(
            status="blocked",
            reason="git_preflight_blocked",
            details=_content_free_preflight_categories(preflight.blockers),
        )
    repository = preflight.repository
    if (
        repository.branch is None
        or repository.upstream != f"origin/{repository.branch}"
        or repository.effective_ref != repository.branch
    ):
        return PlanningInvocationResult(status="blocked", reason="upstream_branch_mismatch")
    if (
        repository.local_head is None
        or repository.remote_head is None
        or repository.local_head != repository.remote_head
        or repository.remote_head_disposition != "fetched_remote_tracking_ref"
    ):
        return PlanningInvocationResult(
            status="blocked",
            reason="git_preflight_blocked",
            details=("head_or_remote_evidence_mismatch",),
        )
    try:
        repository_slug = repo_slug_resolver(repo_root)
    except RuntimeError:
        repository_slug = None
    if repository_slug is None:
        return PlanningInvocationResult(status="blocked", reason="github_upstream_required")

    source_evidence = PlanningSourceEvidence(
        repository=repository_slug,
        branch=repository.branch,
        upstream=repository.upstream,
        local_head=repository.local_head,
        remote_head=repository.remote_head,
        source_manifest_hash=repository.source_manifest.source_manifest_hash,
        snapshot_id=repository.snapshot_id,
        remote_head_disposition="fetched_remote_tracking_ref",
    )
    dependency_resolutions = dependency_loader(target.issue_id) if dependency_loader else ()
    context = PlanningContext(
        issue_id=target.issue_id,
        repository=repository_slug,
        branch=repository.branch,
        source_head=repository.local_head,
        parent_epic_id=target.parent_epic_id,
        parent_initiative_id=target.parent_initiative_id,
        dependency_summary=tuple(
            sorted(
                {resolution.resolved_node_id for resolution in dependency_resolutions},
                key=lambda value: value.encode("utf-8"),
            )
        ),
        canonical_issue_paths=target.canonical_issue_paths,
        relevant_source_paths=relevant,
        operator_context=tuple(
            sorted(set(operator_context), key=lambda value: value.encode("utf-8"))
        ),
    )
    try:
        synthesized = prompt_synthesizer(
            role=role,
            context=context,
            repo_root=repo_root,
            upstream=repository.upstream,
            remote_head=repository.remote_head,
        )
    except (OSError, UnicodeError, ValueError) as error:
        reason = (
            "sensitive_input_rejected"
            if "sensitive" in str(error).lower() or "private" in str(error).lower()
            else "planning_context_rejected"
        )
        return PlanningInvocationResult(
            status="rejected",
            reason=reason,
            source_evidence=None if reason == "sensitive_input_rejected" else source_evidence,
        )
    if _exact_attachments_have_sensitive_content(synthesized):
        return PlanningInvocationResult(
            status="rejected",
            reason="sensitive_input_rejected",
        )
    if not _attachments_match_source_manifest(
        synthesized,
        repository.source_manifest.source_hashes,
    ):
        return PlanningInvocationResult(
            status="blocked",
            reason="git_preflight_blocked",
            source_evidence=source_evidence,
            details=("source_snapshot_mismatch",),
        )
    return backend_invoker(
        repo_root=repo_root,
        role=role,
        source_evidence=source_evidence,
        synthesized=synthesized,
        timeout_seconds=timeout_seconds,
    )


def run_issue_planning_create(
    *,
    request: PlanningCreateRequest,
    records: Sequence[StoredMetaRecord],
    repo_root: Path,
    repo_slug_resolver: Callable[[Path], str | None],
    backend_invoker: Callable[..., PlanningInvocationResult],
    dependency_loader: Callable[[str], Sequence[DirectDependencyResolution]] | None = None,
    relevant_source_paths: Sequence[str] = (),
    operator_context: Sequence[str] = (),
    timeout_seconds: float | None = None,
    preflight_runner: Callable[[GitHubSyncPreflightRequest], PreflightResult] = run_github_sync_preflight,
    prompt_synthesizer: Callable[..., Any] = synthesize_issue_planning_prompt,
    transport_runner: Callable[..., PlanningInvocationResult] = run_issue_planning_transport,
    publisher: Callable[..., PublishedCandidate] = build_and_publish_candidate,
    clock: Callable[[], str] = now_iso,
) -> PlanningCommandResult:
    try:
        target = resolve_existing_issue_target(request.issue_id, records, repo_root)
        current_documents = {
            name: (repo_root / next(
                path for path in target.canonical_issue_paths if Path(path).name == name
            )).read_bytes()
            for name in DOCUMENT_NAMES
        }
        baseline = parse_current_front_matter_baseline(current_documents)
        if (
            baseline.issue_id != target.issue_id
            or baseline.parents != (target.parent_epic_id, target.parent_initiative_id)
        ):
            raise ValueError("current front matter does not match the existing Issue target")
    except (OSError, UnicodeError, ValueError):
        return PlanningCommandResult(
            status="rejected",
            reason="planning_context_rejected",
            issue_id=request.issue_id,
        )
    try:
        output_guard = validate_candidate_output_directory(request.output_dir, repo_root)
    except CandidateOutputRejected:
        return PlanningCommandResult(
            status="rejected",
            reason="candidate_output_rejected",
            issue_id=target.issue_id,
        )

    dependency_snapshot: tuple[DirectDependencyResolution, ...] | None = None

    def load_dependency_snapshot(issue_id: str) -> tuple[DirectDependencyResolution, ...]:
        nonlocal dependency_snapshot
        if issue_id != target.issue_id:
            raise ValueError("dependency snapshot requested for a different Issue")
        if dependency_snapshot is None:
            dependency_snapshot = tuple(dependency_loader(issue_id)) if dependency_loader else ()
        return dependency_snapshot

    transport = transport_runner(
        issue=target.issue_id,
        records=records,
        repo_root=repo_root,
        role="planner",
        repo_slug_resolver=repo_slug_resolver,
        backend_invoker=backend_invoker,
        dependency_loader=load_dependency_snapshot,
        relevant_source_paths=relevant_source_paths,
        operator_context=operator_context,
        timeout_seconds=timeout_seconds,
        preflight_runner=preflight_runner,
        prompt_synthesizer=prompt_synthesizer,
    )
    if transport.status != "pass":
        return PlanningCommandResult(
            status=cast("Literal['blocked', 'rejected']", transport.status),
            reason=transport.reason,
            issue_id=target.issue_id,
            details=transport.details,
        )
    payload = transport.transient_payload
    if (
        transport.reason != "transport_received"
        or transport.source_evidence is None
        or payload is None
        or transport.response_sha256 is None
        or hashlib.sha256(payload).hexdigest() != transport.response_sha256
    ):
        return PlanningCommandResult(
            status="rejected",
            reason="planner_response_rejected",
            issue_id=target.issue_id,
        )
    try:
        planner_documents = parse_planner_payload(payload)
    except (UnicodeError, ValueError):
        return PlanningCommandResult(
            status="rejected",
            reason="planner_response_rejected",
            issue_id=target.issue_id,
        )
    operation_time = datetime.fromisoformat(clock().replace("Z", "+00:00"))
    try:
        dependencies = load_dependency_snapshot(target.issue_id)
        context = PlanningContext(
            issue_id=target.issue_id,
            repository=transport.source_evidence.repository,
            branch=transport.source_evidence.branch,
            source_head=transport.source_evidence.local_head,
            parent_epic_id=target.parent_epic_id,
            parent_initiative_id=target.parent_initiative_id,
            dependency_summary=tuple(
                sorted(
                    {resolution.resolved_node_id for resolution in dependencies},
                    key=lambda value: value.encode("utf-8"),
                )
            ),
            canonical_issue_paths=target.canonical_issue_paths,
            relevant_source_paths=tuple(
                sorted(set(relevant_source_paths), key=lambda value: value.encode("utf-8"))
            ),
            operator_context=tuple(
                sorted(set(operator_context), key=lambda value: value.encode("utf-8"))
            ),
        )
        material = build_candidate_material(
            planner_documents=planner_documents,
            baseline=baseline,
            context=context,
            source_evidence=transport.source_evidence,
            planner_payload=payload,
            operation_time=operation_time,
        )
    except (UnicodeError, ValueError):
        return PlanningCommandResult(
            status="rejected",
            reason="planner_response_rejected",
            issue_id=target.issue_id,
        )
    try:
        published = publisher(
            output_guard=output_guard,
            repo_root=repo_root,
            material=material,
        )
    except CandidateCollision:
        return PlanningCommandResult(
            status="rejected",
            reason="output_collision",
            issue_id=target.issue_id,
        )
    except CandidateArchiveRejected as error:
        return PlanningCommandResult(
            status="rejected",
            reason="archive_rejected",
            issue_id=target.issue_id,
            details=error.findings,
        )
    except CandidateBuildFailed:
        return PlanningCommandResult(
            status="blocked",
            reason="candidate_build_failed",
            issue_id=target.issue_id,
        )
    except CandidatePublicationFailed:
        return PlanningCommandResult(
            status="blocked",
            reason="candidate_publication_failed",
            issue_id=target.issue_id,
        )
    except CandidateOutputRejected:
        return PlanningCommandResult(
            status="rejected",
            reason="candidate_output_rejected",
            issue_id=target.issue_id,
        )
    return PlanningCommandResult(
        status="ok",
        reason="candidate_created",
        issue_id=target.issue_id,
        output={
            "candidate_identity": published.identity.to_dict(),
            "zip_byte_count": published.zip_byte_count,
        },
    )


def run_issue_planning_review(
    *,
    request: PlanningReviewRequest,
    records: Sequence[StoredMetaRecord],
    repo_root: Path,
    repo_slug_resolver: Callable[[Path], str | None],
    backend_invoker: Callable[..., PlanningInvocationResult],
    relevant_source_paths: Sequence[str] = (),
    operator_context: Sequence[str] = (),
    timeout_seconds: float | None = None,
    preflight_runner: Callable[[GitHubSyncPreflightRequest], PreflightResult] = run_github_sync_preflight,
    transport_runner: Callable[..., PlanningInvocationResult] = run_issue_planning_transport,
    candidate_loader: Callable[[Path, Path], VerifiedIssueCandidate] = load_verified_issue_candidate,
    publisher: Callable[..., PublishedPlanningReview] = publish_planning_review_evidence,
    clock: Callable[[], str] = now_iso,
) -> PlanningCommandResult:
    repository_descriptor: int | None = None
    try:
        target = resolve_existing_issue_target(request.issue_id, records, repo_root)
        validate_candidate_output_directory(request.output_dir, repo_root)
        if request.mode == "archive-candidate":
            if request.candidate_path is None or request.reviewed_head is not None:
                raise ValueError("archive Review requires only a Candidate")
            candidate = candidate_loader(request.candidate_path, repo_root)
            if candidate.identity.issue_id != target.issue_id:
                raise ValueError("Candidate Issue does not match Review target")
        elif request.mode == "git-bound":
            if request.candidate_path is not None or request.reviewed_head is None:
                raise ValueError("git-bound Review requires only reviewed_head")
            if re.fullmatch(r"[0-9a-f]{40}", request.reviewed_head) is None:
                raise ValueError("reviewed_head is invalid")
            candidate = None
        else:
            raise ValueError("Review mode is invalid")
        repository_descriptor = open_safe_directory_descriptor(repo_root.resolve(strict=True))
    except CandidateArchiveRejected as error:
        return PlanningCommandResult(
            status="rejected",
            reason="archive_rejected",
            issue_id=request.issue_id,
            details=error.findings,
        )
    except (OSError, UnicodeError, ValueError):
        return PlanningCommandResult(
            status="rejected",
            reason="review_request_rejected",
            issue_id=request.issue_id,
        )

    captured_identity: list[ReviewedPlanningIdentity] = []

    def review_prompt_synthesizer(**kwargs: Any) -> Any:
        context = cast("PlanningContext", kwargs["context"])
        if request.mode == "archive-candidate":
            assert candidate is not None
            identity = ReviewedPlanningIdentity(
                mode="archive-candidate",
                issue_id=target.issue_id,
                repository=context.repository,
                branch=context.branch,
                source_head=context.source_head,
                candidate_identity=candidate.identity,
            )
            targets = (
                PlanningPromptAttachment(
                    name="target-candidate.zip",
                    classification="review-target",
                    source_label=candidate.identity.logical_filename,
                    content=candidate.zip_bytes,
                ),
            )
        else:
            assert request.reviewed_head is not None
            assert repository_descriptor is not None
            if context.source_head != request.reviewed_head:
                raise ValueError("reviewed HEAD does not match synchronized source")
            identity = ReviewedPlanningIdentity(
                mode="git-bound",
                issue_id=target.issue_id,
                repository=context.repository,
                branch=context.branch,
                source_head=context.source_head,
                canonical_target_paths=target.canonical_issue_paths,
                expected_canonical_target_paths=target.canonical_issue_paths,
            )
            targets = tuple(
                PlanningPromptAttachment(
                    name=f"target-{Path(path).name}",
                    classification="review-target",
                    source_label=path,
                    content=read_bounded_regular_file_at(
                        repository_descriptor,
                        path,
                        max_bytes=MAX_REVIEW_SOURCE_FILE_BYTES,
                    ),
                )
                for path in target.canonical_issue_paths
            )
        identity_bytes = _canonical_json_bytes(identity.to_dict())
        assert repository_descriptor is not None
        supplemental = _read_review_supplemental_attachments(
            context,
            repository_descriptor=repository_descriptor,
        )
        captured_identity[:] = [identity]
        return synthesize_planning_evidence_prompt(
            role="reviewer",
            source_head=context.source_head,
            repository=context.repository,
            branch=context.branch,
            exact_attachments=(
                *targets,
                PlanningPromptAttachment(
                    name="reviewed-identity.json",
                    classification="formal-evidence",
                    source_label="reviewed-identity.json",
                    content=identity_bytes,
                ),
                PlanningPromptAttachment(
                    name="reviewed-identity-sha256.txt",
                    classification="formal-evidence",
                    source_label="reviewed-identity-sha256.txt",
                    content=f"{identity.sha256}\n".encode("ascii"),
                ),
            ),
            supplemental_attachments=supplemental,
        )

    try:
        transport = transport_runner(
            issue=target.issue_id,
            records=records,
            repo_root=repo_root,
            role="reviewer",
            repo_slug_resolver=repo_slug_resolver,
            backend_invoker=backend_invoker,
            relevant_source_paths=relevant_source_paths,
            operator_context=operator_context,
            timeout_seconds=timeout_seconds,
            preflight_runner=preflight_runner,
            prompt_synthesizer=review_prompt_synthesizer,
        )
    finally:
        assert repository_descriptor is not None
        os.close(repository_descriptor)
    if transport.status != "pass":
        if (
            request.mode == "git-bound"
            and transport.reason == "git_preflight_blocked"
            and "source_snapshot_mismatch" in transport.details
        ):
            return PlanningCommandResult(
                status="stale",
                reason="review_target_changed",
                issue_id=target.issue_id,
            )
        return PlanningCommandResult(
            status=cast("Literal['blocked', 'rejected']", transport.status),
            reason=transport.reason,
            issue_id=target.issue_id,
            details=transport.details,
        )
    payload = transport.transient_payload
    if (
        transport.reason != "transport_received"
        or transport.source_evidence is None
        or payload is None
        or transport.response_sha256 != hashlib.sha256(payload).hexdigest()
        or len(captured_identity) != 1
    ):
        return PlanningCommandResult(
            status="rejected",
            reason="review_result_rejected",
            issue_id=target.issue_id,
        )
    identity = captured_identity[0]
    try:
        parsed = PlanningReviewResult.from_json_bytes(
            payload,
            expected_canonical_target_paths=(
                target.canonical_issue_paths if request.mode == "git-bound" else None
            ),
        )
        if parsed.reviewed_identity != identity or parsed.reviewed_identity_sha256 != identity.sha256:
            raise ValueError("Review result identity mismatch")
        if _review_result_has_sensitive_content(parsed):
            raise ValueError("Review result contains unsafe dynamic content")
    except (UnicodeError, ValueError):
        return PlanningCommandResult(
            status="rejected",
            reason="review_result_rejected",
            issue_id=target.issue_id,
        )
    if candidate is not None:
        try:
            current = candidate_loader(cast("Path", request.candidate_path), repo_root)
        except CandidateArchiveRejected:
            return PlanningCommandResult(
                status="stale",
                reason="review_target_changed",
                issue_id=target.issue_id,
            )
        if current.identity != candidate.identity or current.zip_bytes != candidate.zip_bytes:
            return PlanningCommandResult(
                status="stale",
                reason="review_target_changed",
                issue_id=target.issue_id,
            )
    source_paths = tuple(
        sorted(
            {*target.canonical_issue_paths, *relevant_source_paths},
            key=lambda value: value.encode("utf-8"),
        )
    )
    post = preflight_runner(
        GitHubSyncPreflightRequest(
            repo_root=repo_root,
            ref=None,
            allow_default_branch_fallback=False,
            source_paths=source_paths,
            expected_source_hash=transport.source_evidence.source_manifest_hash,
        )
    )
    repository = post.repository
    evidence = transport.source_evidence
    if (
        post.status != "pass"
        or repository is None
        or repository.branch != evidence.branch
        or repository.local_head != evidence.local_head
        or repository.remote_head != evidence.remote_head
        or repository.source_manifest.source_manifest_hash != evidence.source_manifest_hash
    ):
        return PlanningCommandResult(
            status="stale",
            reason="review_target_changed",
            issue_id=target.issue_id,
        )
    try:
        published = publisher(
            output_dir=request.output_dir,
            repo_root=repo_root,
            reviewed_identity_sha256=identity.sha256,
            review_result_bytes=payload,
            summary_bytes=render_planning_review_summary(parsed).encode("utf-8"),
            operation_time=datetime.fromisoformat(clock().replace("Z", "+00:00")),
        )
    except FileExistsError:
        return PlanningCommandResult(
            status="rejected",
            reason="output_collision",
            issue_id=target.issue_id,
        )
    except (OSError, UnicodeError, ValueError):
        return PlanningCommandResult(
            status="blocked",
            reason="review_publication_failed",
            issue_id=target.issue_id,
        )
    return PlanningCommandResult(
        status="ok",
        reason="review_completed",
        issue_id=target.issue_id,
        output={
            "review_result_file": published.review_result_file,
            "review_summary_file": published.review_summary_file,
            "review_result_sha256": published.review_result_sha256,
            "reviewed_identity_sha256": identity.sha256,
            "verdict": parsed.verdict,
        },
    )


def run_issue_planning_revise(
    *,
    request: PlanningReviseRequest,
    review_evidence: PlanningRevisionEvidenceInput | None = None,
    records: Sequence[StoredMetaRecord],
    repo_root: Path,
    repo_slug_resolver: Callable[[Path], str | None],
    backend_invoker: Callable[..., PlanningInvocationResult],
    timeout_seconds: float | None = None,
    preflight_runner: Callable[[GitHubSyncPreflightRequest], PreflightResult] = run_github_sync_preflight,
    transport_runner: Callable[..., PlanningInvocationResult] = run_issue_planning_transport,
    candidate_loader: Callable[[Path, Path], VerifiedIssueCandidate] = load_verified_issue_candidate,
    publisher: Callable[..., PublishedCandidate] = build_and_publish_candidate,
    clock: Callable[[], str] = now_iso,
) -> PlanningCommandResult:
    issue_id = "iss-00000"
    try:
        candidate = candidate_loader(request.candidate_path, repo_root)
        issue_id = candidate.identity.issue_id
        target = resolve_existing_issue_target(issue_id, records, repo_root)
        output_guard = validate_candidate_output_directory(request.output_dir, repo_root)
        request_bytes = _read_external_bounded_file(request.request_path, repo_root=repo_root)
        revision = PlanningRevisionRequestV1.from_json_bytes(request_bytes)
        if revision.candidate_identity != candidate.identity:
            raise ValueError("revision Candidate identity mismatch")
    except CandidateArchiveRejected as error:
        return PlanningCommandResult(
            status="rejected",
            reason="archive_rejected",
            issue_id=issue_id,
            details=error.findings,
        )
    except (OSError, UnicodeError, ValueError):
        return PlanningCommandResult(
            status="rejected",
            reason="revision_request_rejected",
            issue_id=issue_id,
        )
    try:
        if review_evidence is None:
            review_result_path = request.request_path.parent / "planning-review-result.json"
            if not review_result_path.exists():
                return PlanningCommandResult(
                    status="blocked",
                    reason="revision_review_unavailable",
                    issue_id=issue_id,
                )
            review_bytes = _read_external_bounded_file(
                review_result_path,
                repo_root=repo_root,
            )
            review_evidence = PlanningRevisionEvidenceInput(
                review_result_path=review_result_path,
                review_result_sha256=hashlib.sha256(review_bytes).hexdigest(),
            )
        else:
            review_bytes = read_external_review_result(
                review_evidence.review_result_path,
                repo_root=repo_root,
                expected_sha256=review_evidence.review_result_sha256,
            )
    except FileNotFoundError:
        return PlanningCommandResult(
            status="blocked",
            reason="revision_review_unavailable",
            issue_id=issue_id,
        )
    except (OSError, UnicodeError, ValueError):
        return PlanningCommandResult(
            status="rejected",
            reason="revision_evidence_mismatch",
            issue_id=issue_id,
        )
    try:
        review = PlanningReviewResult.from_json_bytes(review_bytes)
        reviewed = review.reviewed_identity
        if (
            reviewed.mode != "archive-candidate"
            or reviewed.candidate_identity != candidate.identity
        ):
            raise ValueError("revision Review Candidate identity mismatch")
        if _review_result_has_sensitive_content(review):
            raise ValueError("revision Review contains unsafe dynamic content")
        blocking = tuple(
            finding for finding in review.findings if finding.severity in ("p0", "p1")
        )
        if not blocking:
            return PlanningCommandResult(
                status="blocked",
                reason="revision_not_required",
                issue_id=issue_id,
            )
        if revision.lane == "semantic":
            if revision.review_result_sha256 != review_evidence.review_result_sha256:
                raise ValueError("semantic Review digest mismatch")
            revision.validate_against(review, review_bytes)
    except (UnicodeError, ValueError):
        return PlanningCommandResult(
            status="rejected",
            reason="revision_evidence_mismatch",
            issue_id=issue_id,
        )
    source = _revision_source_state(
        candidate=candidate,
        target=target,
        repo_root=repo_root,
        preflight_runner=preflight_runner,
    )
    if isinstance(source, PlanningCommandResult):
        return source
    context, source_evidence = source
    operation_time = datetime.fromisoformat(clock().replace("Z", "+00:00"))
    try:
        baseline = parse_current_front_matter_baseline(
            {name: candidate.files[name] for name in DOCUMENT_NAMES}
        )
    except ValueError:
        return PlanningCommandResult(
            status="rejected",
            reason="archive_rejected",
            issue_id=issue_id,
        )
    if revision.lane == "mechanical":
        try:
            revised_documents = apply_mechanical_revision(
                {name: candidate.files[name] for name in DOCUMENT_NAMES},
                target_file=cast("str", revision.target_file),
                old_text=cast("str", revision.old_text),
                new_text=cast("str", revision.new_text),
                diff_budget=cast("int", revision.diff_budget),
            )
            payload = render_planner_payload(revised_documents)
            planner_documents = parse_planner_payload(payload)
        except (UnicodeError, ValueError):
            return PlanningCommandResult(
                status="rejected",
                reason="mechanical_revision_rejected",
                issue_id=issue_id,
            )
    else:
        selected = {
            finding.id: finding
            for finding in review.findings
            if finding.id in revision.finding_ids
        }

        def revision_prompt_synthesizer(**kwargs: Any) -> Any:
            runtime_context = cast("PlanningContext", kwargs["context"])
            if (
                runtime_context.repository != candidate.identity.source_repository
                or runtime_context.branch != candidate.identity.source_branch
                or runtime_context.source_head != candidate.identity.source_head
            ):
                raise ValueError("semantic revision source changed")
            base = synthesize_issue_planning_prompt(**kwargs)
            attachments = [
                PlanningPromptAttachment(
                    name="prior-candidate.zip",
                    classification="review-target",
                    source_label=candidate.identity.logical_filename,
                    content=candidate.zip_bytes,
                ),
                PlanningPromptAttachment(
                    name="planning-review-result.json",
                    classification="formal-evidence",
                    source_label="planning-review-result.json",
                    content=review_bytes,
                ),
            ]
            attachments.extend(
                PlanningPromptAttachment(
                    name=f"prior-{name}",
                    classification="supplemental-context",
                    source_label=f"candidate/{name}",
                    content=candidate.files[name],
                )
                for name in DOCUMENT_NAMES
            )
            instructions = (
                *(
                    f"selected finding {finding.id}: {finding.severity}"
                    for finding in selected.values()
                ),
                *(f"preserve assumption: {item}" for item in revision.preserve_assumptions),
            )
            return synthesize_planning_evidence_prompt(
                role="planner",
                source_head=runtime_context.source_head,
                repository=runtime_context.repository,
                branch=runtime_context.branch,
                exact_attachments=tuple(attachments),
                instructions=instructions,
                supplemental_attachments=base.attachments,
            )

        transport = transport_runner(
            issue=issue_id,
            records=records,
            repo_root=repo_root,
            role="planner",
            repo_slug_resolver=repo_slug_resolver,
            backend_invoker=backend_invoker,
            relevant_source_paths=tuple(
                cast("list[str]", candidate.source_baseline["relevant_paths"])
            ),
            operator_context=(),
            timeout_seconds=timeout_seconds,
            preflight_runner=preflight_runner,
            prompt_synthesizer=revision_prompt_synthesizer,
        )
        if transport.status != "pass":
            return PlanningCommandResult(
                status=cast("Literal['blocked', 'rejected']", transport.status),
                reason=transport.reason,
                issue_id=issue_id,
                details=transport.details,
            )
        payload = transport.transient_payload
        if (
            payload is None
            or transport.response_sha256 != hashlib.sha256(payload).hexdigest()
            or transport.source_evidence is None
        ):
            return PlanningCommandResult(
                status="rejected",
                reason="planner_response_rejected",
                issue_id=issue_id,
            )
        source_evidence = transport.source_evidence
        try:
            planner_documents = parse_planner_payload(payload)
        except (UnicodeError, ValueError):
            return PlanningCommandResult(
                status="rejected",
                reason="planner_response_rejected",
                issue_id=issue_id,
            )
    try:
        material = build_candidate_material(
            planner_documents=planner_documents,
            baseline=baseline,
            context=context,
            source_evidence=source_evidence,
            planner_payload=payload,
            operation_time=operation_time,
            version=candidate.identity.version + 1,
        )
    except (UnicodeError, ValueError):
        return PlanningCommandResult(
            status="rejected",
            reason="planner_response_rejected",
            issue_id=issue_id,
        )
    current_source = _revision_source_state(
        candidate=candidate,
        target=target,
        repo_root=repo_root,
        preflight_runner=preflight_runner,
    )
    try:
        current_candidate = candidate_loader(request.candidate_path, repo_root)
    except CandidateArchiveRejected:
        current_candidate = None
    if (
        isinstance(current_source, PlanningCommandResult)
        or current_candidate is None
        or current_candidate.identity != candidate.identity
        or current_candidate.zip_bytes != candidate.zip_bytes
    ):
        return PlanningCommandResult(
            status="stale",
            reason="revision_source_stale",
            issue_id=issue_id,
        )
    try:
        published = publisher(
            output_guard=output_guard,
            repo_root=repo_root,
            material=material,
        )
    except CandidateCollision:
        return PlanningCommandResult(
            status="rejected",
            reason="output_collision",
            issue_id=issue_id,
        )
    except CandidateArchiveRejected as error:
        return PlanningCommandResult(
            status="rejected",
            reason="archive_rejected",
            issue_id=issue_id,
            details=error.findings,
        )
    except CandidateBuildFailed:
        return PlanningCommandResult(
            status="blocked",
            reason="candidate_build_failed",
            issue_id=issue_id,
        )
    except CandidatePublicationFailed:
        return PlanningCommandResult(
            status="blocked",
            reason="candidate_publication_failed",
            issue_id=issue_id,
        )
    return PlanningCommandResult(
        status="ok",
        reason="candidate_revised",
        issue_id=issue_id,
        output={
            "candidate_identity": published.identity.to_dict(),
            "zip_byte_count": published.zip_byte_count,
        },
    )


def _content_free_preflight_categories(blockers: Sequence[str]) -> tuple[str, ...]:
    if not blockers:
        return ("repository_snapshot_missing",)
    categories: list[str] = []
    safe_prefixed = {
        "missing_source_path",
        "unsafe_source_path",
    }
    safe_exact = {
        "ahead_of_remote",
        "behind_remote",
        "concurrent_repo_change",
        "default_branch_unknown",
        "detached_head",
        "dirty_tracked",
        "diverged_from_remote",
        "git_status_unavailable",
        "head_mismatch",
        "origin_fetch_failed",
        "origin_mismatch",
        "origin_missing",
        "remote_branch_missing",
        "source_hash_mismatch",
        "staged_changes",
        "untracked_files",
    }
    for blocker in blockers:
        prefix = blocker.partition(":")[0]
        if prefix in safe_prefixed:
            categories.append(prefix)
        elif blocker in safe_exact:
            categories.append(blocker)
        else:
            categories.append("preflight_blocked")
    return tuple(dict.fromkeys(categories))


def _revision_source_state(
    *,
    candidate: VerifiedIssueCandidate,
    target: ExistingIssueTarget,
    repo_root: Path,
    preflight_runner: Callable[[GitHubSyncPreflightRequest], PreflightResult],
) -> tuple[PlanningContext, PlanningSourceEvidence] | PlanningCommandResult:
    baseline = candidate.source_baseline
    try:
        source_paths = tuple(
            sorted(
                {
                    *cast("list[str]", baseline["canonical_issue_paths"]),
                    *cast("list[str]", baseline["relevant_paths"]),
                },
                key=lambda value: value.encode("utf-8"),
            )
        )
        preflight = preflight_runner(
            GitHubSyncPreflightRequest(
                repo_root=repo_root,
                ref=None,
                allow_default_branch_fallback=False,
                source_paths=source_paths,
                expected_source_hash=cast("str", baseline["source_manifest_hash"]),
            )
        )
    except (KeyError, TypeError, ValueError):
        return PlanningCommandResult(
            status="rejected",
            reason="archive_rejected",
            issue_id=candidate.identity.issue_id,
        )
    if preflight.status != "pass" or preflight.repository is None:
        return PlanningCommandResult(
            status="blocked",
            reason="git_preflight_blocked",
            issue_id=candidate.identity.issue_id,
            details=_content_free_preflight_categories(preflight.blockers),
        )
    repository = preflight.repository
    if (
        repository.branch != candidate.identity.source_branch
        or repository.local_head != candidate.identity.source_head
        or repository.remote_head != candidate.identity.source_head
        or repository.source_manifest.source_manifest_hash
        != baseline["source_manifest_hash"]
    ):
        return PlanningCommandResult(
            status="stale",
            reason="revision_source_stale",
            issue_id=candidate.identity.issue_id,
        )
    try:
        context = PlanningContext(
            issue_id=candidate.identity.issue_id,
            repository=candidate.identity.source_repository,
            branch=candidate.identity.source_branch,
            source_head=candidate.identity.source_head,
            parent_epic_id=target.parent_epic_id,
            parent_initiative_id=target.parent_initiative_id,
            dependency_summary=tuple(cast("list[str]", baseline["dependency_ids"])),
            canonical_issue_paths=target.canonical_issue_paths,
            relevant_source_paths=tuple(cast("list[str]", baseline["relevant_paths"])),
            operator_context=(),
        )
        evidence = PlanningSourceEvidence(
            repository=candidate.identity.source_repository,
            branch=candidate.identity.source_branch,
            upstream=f"origin/{candidate.identity.source_branch}",
            local_head=candidate.identity.source_head,
            remote_head=candidate.identity.source_head,
            source_manifest_hash=cast("str", baseline["source_manifest_hash"]),
            snapshot_id=repository.snapshot_id,
            remote_head_disposition="fetched_remote_tracking_ref",
        )
    except (KeyError, TypeError, ValueError):
        return PlanningCommandResult(
            status="rejected",
            reason="archive_rejected",
            issue_id=candidate.identity.issue_id,
        )
    return context, evidence


def _read_external_bounded_file(path: Path, *, repo_root: Path) -> bytes:
    lexical = path.absolute()
    if not lexical.exists() or not lexical.is_file() or _contains_symlink(Path(lexical.anchor), lexical):
        raise ValueError("external input path is unsafe")
    resolved = lexical.resolve(strict=True)
    repository = repo_root.resolve(strict=True)
    if resolved == repository or resolved.is_relative_to(repository):
        raise ValueError("external input must be outside repository")
    try:
        data = read_bounded_regular_file(resolved, max_bytes=1024 * 1024)
    except ValueError as error:
        if "bounded" in str(error):
            raise ValueError("external input exceeds bounded size") from None
        raise ValueError("external input path is unsafe") from None
    data.decode("utf-8", errors="strict")
    return data


def _attachments_match_source_manifest(
    synthesized: object,
    expected_hashes: dict[str, str],
) -> bool:
    attachments = getattr(synthesized, "attachments", None)
    if not isinstance(attachments, tuple):
        return False
    actual_hashes: dict[str, str] = {}
    for attachment in attachments:
        if (
            not isinstance(attachment, tuple)
            or len(attachment) != 2
            or not isinstance(attachment[0], str)
            or not isinstance(attachment[1], str)
            or attachment[0] in actual_hashes
        ):
            return False
        actual_hashes[attachment[0]] = hashlib.sha256(attachment[1].encode("utf-8")).hexdigest()
    if actual_hashes != expected_hashes:
        return False
    exact_attachments = getattr(synthesized, "exact_attachments", None)
    if not isinstance(exact_attachments, tuple):
        return False
    for attachment in exact_attachments:
        source_label = getattr(attachment, "source_label", None)
        classification = getattr(attachment, "classification", None)
        content = getattr(attachment, "content", None)
        if (
            classification == "review-target"
            and isinstance(source_label, str)
            and source_label in expected_hashes
            and (
                not isinstance(content, bytes)
                or hashlib.sha256(content).hexdigest() != expected_hashes[source_label]
            )
        ):
            return False
    return True


def _read_review_supplemental_attachments(
    context: PlanningContext,
    *,
    repository_descriptor: int,
) -> tuple[tuple[str, str], ...]:
    for value in context.operator_context:
        if scan_constraint_sensitive_payload(value) or private_absolute_path_finding(value):
            raise ValueError("sensitive Review context rejected")
    attachments: list[tuple[str, str]] = []
    total = 0
    paths = tuple(
        sorted(
            {*context.canonical_issue_paths, *context.relevant_source_paths},
            key=lambda value: value.encode("utf-8"),
        )
    )
    for path in paths:
        content = read_bounded_regular_file_at(
            repository_descriptor,
            path,
            max_bytes=MAX_REVIEW_SOURCE_FILE_BYTES,
        )
        total += len(content)
        if total > MAX_REVIEW_SOURCE_TOTAL_BYTES:
            raise ValueError("Review context exceeds bounded size")
        text = content.decode("utf-8", errors="strict")
        if scan_constraint_sensitive_payload(text) or private_absolute_path_finding(text):
            raise ValueError("sensitive Review context rejected")
        attachments.append((path, text))
    return tuple(attachments)


def _exact_attachments_have_sensitive_content(synthesized: object) -> bool:
    exact_attachments = getattr(synthesized, "exact_attachments", None)
    if not isinstance(exact_attachments, tuple):
        return True
    for attachment in exact_attachments:
        content = getattr(attachment, "content", None)
        if not isinstance(content, bytes):
            return True
        text = content.decode("utf-8", errors="ignore")
        if scan_constraint_sensitive_payload(text) or private_absolute_path_finding(text):
            return True
    return False


def _canonical_json_bytes(value: dict[str, Any]) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        + b"\n"
    )


def _review_result_has_sensitive_content(result: PlanningReviewResult) -> bool:
    for finding in result.findings:
        for value in (
            finding.id,
            finding.exact_location,
            finding.violated_requirement_or_contradiction,
            finding.concrete_impact,
        ):
            if scan_constraint_sensitive_payload(value) or private_absolute_path_finding(value):
                return True
    return False
