from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import hashlib
from pathlib import Path, PurePath
import re
from typing import TYPE_CHECKING, Any, Literal, cast

from spec_dock_runtime.application.authoring_pack.github_sync_preflight import (
    GitHubSyncPreflightRequest,
    run_github_sync_preflight,
)
from spec_dock_runtime.application.issue_planning_prompt import (
    authoring_output_expectation,
    synthesize_issue_planning_prompt,
    synthesize_planning_evidence_prompt,
)
from spec_dock_runtime.application.ports import (
    BlueBindingResolution,
    BlueThreadBinding,
    ChatGptThreadPort,
    ExpectedPlanningTargetsView,
    IssuePlanningApplyOutputRejected,
    IssuePlanningCandidateArchiveRejected,
    IssuePlanningCandidateBuildFailed,
    IssuePlanningCandidateCollision,
    IssuePlanningCandidateOutputRejected,
    IssuePlanningCandidatePublicationFailed,
    IssuePlanningDependencies,
    IssuePlanningGateway,
    PlanningApplyExecutionView,
    PublishedCandidateView,
    PublishedPlanningReviewView,
    ThreadInvocationMode,
    ThreadInvocationReceipt,
    VerifiedIssueCandidateView,
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
)
from spec_dock_runtime.domain.issue_planning_contracts import (
    GitBoundOperationBindingV1,
    PlanningCommandResult,
    PlanningContext,
    PlanningHumanDecisionV1,
    PlanningInvocationResult,
    PlanningPublicationSourceStale,
    PlanningReviewResult,
    PlanningRevisionRequestV1,
    PlanningSourceEvidence,
    ReviewedPlanningIdentity,
    raw_bytes_sha256,
)
from spec_dock_runtime.presentation.issue_planning import render_planning_review_summary

_INVALID_ISSUE_ID = "iss-00000"

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from spec_dock_runtime.domain.authoring_pack.preflight_contract import PreflightResult
    from spec_dock_runtime.infra.contracts import DirectDependencyResolution, StoredMetaRecord


@dataclass(frozen=True)
class PlanningCreateRequest:
    issue_id: str
    output_dir: Path
    provided_context_paths: tuple[Path, ...] = ()


@dataclass(frozen=True)
class PlanningReviseRequest:
    candidate_path: Path
    request_path: Path
    output_dir: Path
    provided_context_paths: tuple[Path, ...] = ()


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
    provided_context_paths: tuple[Path, ...] = ()


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


def _result_issue_id(value: str) -> str:
    try:
        return normalize_id_input(value, prefix="iss", field="issue")
    except (AttributeError, RuntimeError, ValueError):
        return _INVALID_ISSUE_ID


def _context_source_operands(_repo_root: Path, context: PlanningContext) -> tuple[Path, ...]:
    seen: set[str] = set()
    operands: list[Path] = []
    for relative in (*context.canonical_issue_paths, *context.relevant_source_paths):
        if relative not in seen:
            seen.add(relative)
            # Oracle executes with cwd=repo_root; preserve the repository-
            # relative lexical operand instead of leaking a host absolute path.
            operands.append(Path(relative))
    return tuple(operands)


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
    dependencies: IssuePlanningDependencies,
    repo_slug_resolver: Callable[[Path], str | None],
    validation_runner: Callable[[], object],
    sync_runner: Callable[[], object],
    preflight_runner: Callable[[GitHubSyncPreflightRequest], PreflightResult] = run_github_sync_preflight,
    candidate_loader: Callable[[Path, Path], VerifiedIssueCandidateView] | None = None,
    expected_target_loader: Callable[[Path, str, tuple[str, str, str]], ExpectedPlanningTargetsView] | None = None,
    resume_probe: Callable[..., bool] | None = None,
    transaction_runner: Callable[..., PlanningApplyExecutionView],
) -> PlanningCommandResult:
    gateway = dependencies.gateway
    candidate_loader = candidate_loader or gateway.load_verified_issue_candidate
    expected_target_loader = expected_target_loader or gateway.load_expected_planning_targets
    resume_probe = resume_probe or gateway.planning_apply_resume_available
    issue_id = _result_issue_id(request.issue_id)
    try:
        target = resolve_existing_issue_target(request.issue_id, records, repo_root)
    except ValueError:
        return PlanningCommandResult(
            status="rejected",
            reason="apply_request_rejected",
            issue_id=issue_id,
        )
    issue_id = target.issue_id
    if request.mode == "git-bound" and request.candidate_path is None:
        return PlanningCommandResult(
            status="rejected",
            reason="operation_candidate_required",
            issue_id=issue_id,
        )
    if not _apply_mode_options_are_closed(request):
        return PlanningCommandResult(
            status="rejected",
            reason="apply_request_rejected",
            issue_id=issue_id,
        )
    try:
        output_guard = gateway.validate_candidate_output_directory(request.output_dir, repo_root)
    except (IssuePlanningCandidateOutputRejected, OSError, ValueError):
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
            gateway=gateway,
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
            gateway=gateway,
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
    try:
        review = PlanningReviewResult.from_json_bytes(
            review_bytes,
            expected_canonical_target_paths=(target.canonical_issue_paths if request.mode == "git-bound" else None),
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
                review.reviewed_identity.canonical_target_paths if request.mode == "git-bound" else None
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

    verified_candidate: VerifiedIssueCandidateView | None = None
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
        except IssuePlanningCandidateArchiveRejected as error:
            return PlanningCommandResult(
                status="rejected",
                reason="archive_rejected",
                issue_id=issue_id,
                details=tuple(str(item) for item in error.findings),
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
        assert request.candidate_path is not None
        try:
            verified_candidate = candidate_loader(request.candidate_path, repo_root)
        except IssuePlanningCandidateArchiveRejected as error:
            return PlanningCommandResult(
                status="rejected",
                reason="operation_binding_rejected",
                issue_id=issue_id,
                details=error.findings,
            )
        try:
            binding = GitBoundOperationBindingV1.create(
                issue_id=issue_id,
                repository=identity.repository,
                branch=identity.branch,
                source_head=identity.source_head,
                candidate_identity=verified_candidate.identity,
                onboarding_companion=verified_candidate.onboarding_companion,
            )
        except ValueError:
            return PlanningCommandResult(
                status="rejected",
                reason="operation_binding_mismatch",
                issue_id=issue_id,
            )
        if identity.git_bound_operation_binding != binding:
            return PlanningCommandResult(
                status="rejected",
                reason="operation_binding_mismatch",
                issue_id=issue_id,
            )

    try:
        repository = repo_slug_resolver(repo_root)
    except RuntimeError:
        return PlanningCommandResult(
            status="blocked",
            reason="github_upstream_required",
            issue_id=issue_id,
        )
    if repository is None:
        return PlanningCommandResult(
            status="blocked",
            reason="github_upstream_required",
            issue_id=issue_id,
        )
    if repository != identity.repository:
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
    decision_path = (issue_dir / "artifacts" / f"{timestamp}-planning-human-decision-placeholder.json").as_posix()
    replacements: dict[str, bytes] = {}
    if request.mode == "archive-candidate" and human.decision == "approved" and verified_candidate is not None:
        replacements = {name: verified_candidate.files[name] for name in DOCUMENT_NAMES}
    companion_target_path: str | None = None
    companion_bytes: bytes | None = None
    if verified_candidate is not None:
        companion_target_path = (issue_dir / verified_candidate.onboarding_companion.path).as_posix()
        if human.decision == "approved":
            companion_bytes = verified_candidate.files[verified_candidate.onboarding_companion.path]
    try:
        operation = gateway.create_planning_apply_operation(
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
            candidate_identity=(None if verified_candidate is None else verified_candidate.identity),
            git_bound_operation_binding_sha256=(
                identity.git_bound_operation_binding.binding_sha256
                if identity.git_bound_operation_binding is not None
                else None
            ),
            companion_target_path=companion_target_path,
            companion_sha256=(
                verified_candidate.onboarding_companion.sha256 if verified_candidate is not None else None
            ),
            decision_artifact_path=decision_path,
            human_decision_bytes=human_bytes,
            replacement_documents=replacements,
            replacement_companion=companion_bytes,
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
            output_guard=output_guard,
        )
    except (OSError, IssuePlanningApplyOutputRejected, ValueError):
        return PlanningCommandResult(
            status="rejected",
            reason="apply_output_rejected",
            issue_id=issue_id,
        )
    if resume_available:
        execution = transaction_runner(
            operation,
            repo_root=repo_root,
            output_guard=output_guard,
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
            blocker
            in {
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
    assert request.candidate_path is not None
    try:
        current_candidate = candidate_loader(request.candidate_path, repo_root)
    except IssuePlanningCandidateArchiveRejected:
        return PlanningCommandResult(
            status="stale" if request.mode == "archive-candidate" else "rejected",
            reason=("apply_target_changed" if request.mode == "archive-candidate" else "operation_binding_mismatch"),
            issue_id=issue_id,
        )
    if (
        verified_candidate is None
        or current_candidate.identity != verified_candidate.identity
        or current_candidate.zip_bytes != verified_candidate.zip_bytes
        or current_candidate.files != verified_candidate.files
        or current_candidate.source_baseline != verified_candidate.source_baseline
        or current_candidate.onboarding_companion != verified_candidate.onboarding_companion
    ):
        return PlanningCommandResult(
            status="stale" if request.mode == "archive-candidate" else "rejected",
            reason=("apply_target_changed" if request.mode == "archive-candidate" else "operation_binding_mismatch"),
            issue_id=issue_id,
        )
    if request.mode == "git-bound":
        try:
            current_binding = GitBoundOperationBindingV1.create(
                issue_id=issue_id,
                repository=identity.repository,
                branch=identity.branch,
                source_head=identity.source_head,
                candidate_identity=current_candidate.identity,
                onboarding_companion=current_candidate.onboarding_companion,
            )
        except ValueError:
            return PlanningCommandResult(
                status="rejected",
                reason="operation_binding_mismatch",
                issue_id=issue_id,
            )
        if identity.git_bound_operation_binding != current_binding:
            return PlanningCommandResult(
                status="rejected",
                reason="operation_binding_mismatch",
                issue_id=issue_id,
            )
    execution = transaction_runner(
        operation,
        repo_root=repo_root,
        output_guard=output_guard,
        validation_runner=validation_runner,
        sync_runner=sync_runner,
    )
    return _planning_result_from_execution(issue_id, execution)


def _planning_result_from_execution(
    issue_id: str,
    execution: PlanningApplyExecutionView,
) -> PlanningCommandResult:
    return PlanningCommandResult(
        status=cast("Any", execution.status),
        reason=execution.reason,
        issue_id=issue_id,
        output={key: value for key, value in execution.to_output().items() if value is not None},
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
            request.candidate_path is not None
            and request.logical_filename is None
            and request.zip_sha256 is None
            and request.reviewed_head is not None
            and re.fullmatch(r"[0-9a-f]{40}", request.reviewed_head) is not None
        )
    return False


def _git_blob_oid(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def _thread_contract_failure() -> PlanningInvocationResult:
    return PlanningInvocationResult(
        status="blocked",
        reason="planning_context_rejected",
        details=("thread_receipt_invalid",),
    )


def _thread_command_contract_failure(issue_id: str) -> PlanningCommandResult:
    return PlanningCommandResult(
        status="blocked",
        reason="planning_context_rejected",
        issue_id=issue_id,
        details=("thread_receipt_invalid",),
    )


def _validate_blue_resolution(
    resolution: BlueBindingResolution,
    prior_lineage: GitBoundOperationBindingV1,
) -> str:
    """Validate a resolved Blue binding against the requested Candidate lineage."""

    if not isinstance(resolution, BlueBindingResolution):
        raise ValueError("Blue binding resolution type is invalid")
    resolution.__post_init__()
    if resolution.status == "exact":
        binding = resolution.binding
        if not isinstance(binding, BlueThreadBinding):
            raise ValueError("exact Blue binding is invalid")
        binding.__post_init__()
        if binding.lineage_sha256 != prior_lineage.binding_sha256:
            raise ValueError("Blue binding lineage mismatch")
    elif resolution.binding is not None:
        raise ValueError("non-exact Blue binding must not carry a binding")
    return resolution.status


def _validate_thread_receipt(
    receipt: ThreadInvocationReceipt,
    *,
    mode: ThreadInvocationMode,
    required_binding: BlueThreadBinding | None = None,
    required_lineage_sha256: str | None = None,
) -> None:
    """Re-check private receipt invariants at the application boundary."""

    if not isinstance(receipt, ThreadInvocationReceipt):
        raise ValueError("thread invocation receipt type is invalid")
    # A port/test double may have bypassed dataclass construction or mutated an
    # otherwise frozen instance. Re-run the closed contract before consuming it.
    receipt.__post_init__()
    if receipt.blue_binding is not None:
        receipt.blue_binding.__post_init__()
    if receipt.mode != mode:
        raise ValueError("thread invocation mode mismatch")
    result_status = getattr(receipt.result, "status", None)
    if result_status not in ("pass", "blocked", "rejected"):
        raise ValueError("thread invocation result status is invalid")
    if mode == "continuation" and receipt.submission_state == "successful":
        if required_binding is None or receipt.blue_binding is not required_binding:
            raise ValueError("continuation Blue binding mismatch")
        if receipt.blue_binding.provider_handle is not required_binding.provider_handle:
            raise ValueError("continuation provider handle mismatch")
        expected_lineage = required_lineage_sha256 or required_binding.lineage_sha256
        if receipt.blue_binding.lineage_sha256 != expected_lineage:
            raise ValueError("continuation lineage mismatch")


def _thread_backend_invoker(
    *,
    backend_invoker: Callable[..., PlanningInvocationResult],
    thread_port: ChatGptThreadPort | None,
    mode: Literal["new_blue", "continuation", "fresh_red"],
    capture: Callable[[ThreadInvocationReceipt], None],
    binding: BlueThreadBinding | None = None,
    reviewed_identity: ReviewedPlanningIdentity | None = None,
) -> Callable[..., PlanningInvocationResult]:
    """Select the private thread policy while preserving the transport contract."""

    def invoke(**kwargs: Any) -> PlanningInvocationResult:
        if thread_port is None:
            # Preserve the legacy one-shot path without manufacturing a
            # private S06 receipt when the optional capability is absent.
            return backend_invoker(**kwargs)
        try:
            if mode == "new_blue":
                receipt = thread_port.invoke_new_blue(backend_invoker, **kwargs)
            elif mode == "continuation":
                if binding is None:
                    raise ValueError("continuation requires an exact Blue binding")
                receipt = thread_port.invoke_continuation(binding, backend_invoker, **kwargs)
            else:
                if reviewed_identity is None:
                    raise ValueError("fresh Red requires a reviewed identity")
                receipt = thread_port.invoke_fresh_red(reviewed_identity, backend_invoker, **kwargs)
            _validate_thread_receipt(
                receipt,
                mode=mode,
                required_binding=binding,
                required_lineage_sha256=(binding.lineage_sha256 if binding is not None else None),
            )
        except (AttributeError, TypeError, ValueError):
            return _thread_contract_failure()
        capture(receipt)
        return receipt.result

    return invoke


def _commit_published_blue(
    *,
    thread_port: ChatGptThreadPort | None,
    receipt: ThreadInvocationReceipt | None,
    lineage: GitBoundOperationBindingV1,
) -> PlanningCommandResult | None:
    if thread_port is None or receipt is None:
        return None
    thread_port.commit_blue(receipt, lineage)
    return None


def _require_publishable_thread_receipt(
    *,
    thread_port: ChatGptThreadPort | None,
    receipts: Sequence[ThreadInvocationReceipt],
    issue_id: str,
    mode: ThreadInvocationMode,
    required_binding: BlueThreadBinding | None = None,
    required_lineage_sha256: str | None = None,
) -> PlanningCommandResult | None:
    """Gate all thread-backed publication on one valid submitted receipt."""

    if thread_port is None:
        return None
    if len(receipts) != 1:
        return _thread_command_contract_failure(issue_id)
    try:
        receipt = receipts[0]
        _validate_thread_receipt(
            receipt,
            mode=mode,
            required_binding=required_binding,
            required_lineage_sha256=required_lineage_sha256,
        )
        if receipt.submission_state != "successful" or getattr(receipt.result, "status", None) != "pass":
            raise ValueError("thread receipt is not publishable")
        if mode in ("new_blue", "continuation") and receipt.blue_binding is None:
            raise ValueError("publishable Blue receipt requires binding")
        if mode == "fresh_red" and receipt.red_binding is None:
            raise ValueError("publishable Red receipt requires binding")
    except (AttributeError, TypeError, ValueError):
        return _thread_command_contract_failure(issue_id)
    return None


def run_issue_planning_transport(
    *,
    issue: str,
    records: Sequence[StoredMetaRecord],
    repo_root: Path,
    role: Literal["planner", "semantic_revision", "reviewer"],
    repo_slug_resolver: Callable[[Path], str | None],
    backend_invoker: Callable[..., PlanningInvocationResult],
    dependency_loader: Callable[[str], Sequence[DirectDependencyResolution]] | None = None,
    relevant_source_paths: Sequence[str] = (),
    operator_context: Sequence[str] = (),
    timeout_seconds: float | None = None,
    preflight_runner: Callable[[GitHubSyncPreflightRequest], PreflightResult] = run_github_sync_preflight,
    prompt_synthesizer: Callable[..., Any] = synthesize_issue_planning_prompt,
    onboarding_companion_path: str | None = None,
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
        operator_context=tuple(sorted(set(operator_context), key=lambda value: value.encode("utf-8"))),
        onboarding_companion_path=onboarding_companion_path,
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
    dependencies: IssuePlanningDependencies,
    repo_slug_resolver: Callable[[Path], str | None],
    backend_invoker: Callable[..., PlanningInvocationResult],
    dependency_loader: Callable[[str], Sequence[DirectDependencyResolution]] | None = None,
    relevant_source_paths: Sequence[str] = (),
    operator_context: Sequence[str] = (),
    timeout_seconds: float | None = None,
    preflight_runner: Callable[[GitHubSyncPreflightRequest], PreflightResult] = run_github_sync_preflight,
    prompt_synthesizer: Callable[..., Any] = synthesize_issue_planning_prompt,
    transport_runner: Callable[..., PlanningInvocationResult] = run_issue_planning_transport,
    authoring_loader: Callable[..., Any] | None = None,
    publisher: Callable[..., PublishedCandidateView] | None = None,
    clock: Callable[[], str] | None = None,
) -> PlanningCommandResult:
    gateway = dependencies.gateway
    authoring_loader = authoring_loader or gateway.load_validated_issue_authoring_payload
    publisher = publisher or gateway.build_and_publish_candidate
    clock = clock or dependencies.clock.now_iso
    try:
        target = resolve_existing_issue_target(request.issue_id, records, repo_root)
        current_documents = {
            name: (
                repo_root / next(path for path in target.canonical_issue_paths if Path(path).name == name)
            ).read_bytes()
            for name in DOCUMENT_NAMES
        }
        baseline = parse_current_front_matter_baseline(current_documents)
        if baseline.issue_id != target.issue_id or baseline.parents != (
            target.parent_epic_id,
            target.parent_initiative_id,
        ):
            raise ValueError("current front matter does not match the existing Issue target")
    except (OSError, UnicodeError, ValueError):
        return PlanningCommandResult(
            status="rejected",
            reason="planning_context_rejected",
            issue_id=_result_issue_id(request.issue_id),
        )
    try:
        output_guard = gateway.validate_candidate_output_directory(request.output_dir, repo_root)
    except IssuePlanningCandidateOutputRejected:
        return PlanningCommandResult(
            status="rejected",
            reason="candidate_output_rejected",
            issue_id=target.issue_id,
        )

    try:
        operation_time = datetime.fromisoformat(clock().replace("Z", "+00:00"))
        onboarding_companion_path = _resolve_onboarding_companion_path(operation_time)
    except (TypeError, ValueError):
        return PlanningCommandResult(
            status="rejected",
            reason="planning_context_rejected",
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

    def create_prompt_synthesizer(**kwargs: Any) -> Any:
        return prompt_synthesizer(
            **kwargs,
            provided_context_paths=request.provided_context_paths,
        )

    thread_receipts: list[ThreadInvocationReceipt] = []

    def capture_thread_receipt(receipt: ThreadInvocationReceipt) -> None:
        thread_receipts[:] = [receipt]

    transport = transport_runner(
        issue=target.issue_id,
        records=records,
        repo_root=repo_root,
        role="planner",
        repo_slug_resolver=repo_slug_resolver,
        backend_invoker=_thread_backend_invoker(
            backend_invoker=backend_invoker,
            thread_port=dependencies.thread_port,
            mode="new_blue",
            capture=capture_thread_receipt,
        ),
        dependency_loader=load_dependency_snapshot,
        relevant_source_paths=relevant_source_paths,
        operator_context=operator_context,
        timeout_seconds=timeout_seconds,
        preflight_runner=preflight_runner,
        prompt_synthesizer=create_prompt_synthesizer,
        onboarding_companion_path=onboarding_companion_path,
    )
    if transport.status != "pass":
        return PlanningCommandResult(
            status=cast("Literal['blocked', 'rejected']", transport.status),
            reason=transport.reason,
            issue_id=target.issue_id,
            details=transport.details,
        )
    receipt_gate = _require_publishable_thread_receipt(
        thread_port=dependencies.thread_port,
        receipts=thread_receipts,
        issue_id=target.issue_id,
        mode="new_blue",
    )
    if receipt_gate is not None:
        return receipt_gate
    authoring_zip = transport.authoring_zip
    if (
        transport.reason != "transport_received"
        or transport.source_evidence is None
        or authoring_zip is None
        or transport.review_json is not None
        or transport.response_sha256 is None
        or authoring_zip.sha256 != transport.response_sha256
    ):
        return PlanningCommandResult(
            status="rejected",
            reason="planner_response_rejected",
            issue_id=target.issue_id,
        )
    if not _source_evidence_is_current(
        target=target,
        relevant_source_paths=relevant_source_paths,
        repo_root=repo_root,
        evidence=transport.source_evidence,
        preflight_runner=preflight_runner,
    ):
        return PlanningCommandResult(
            status="stale",
            reason="planning_source_stale",
            issue_id=target.issue_id,
        )
    try:
        authoring = authoring_loader(
            authoring_zip,
            expected_companion_path=onboarding_companion_path,
            repo_root=repo_root,
        )
    except (IssuePlanningCandidateArchiveRejected, UnicodeError, ValueError) as error:
        return PlanningCommandResult(
            status="rejected",
            reason="archive_rejected",
            issue_id=target.issue_id,
            details=error.findings if isinstance(error, IssuePlanningCandidateArchiveRejected) else (),
        )
    try:
        dependency_resolutions = load_dependency_snapshot(target.issue_id)
        context = PlanningContext(
            issue_id=target.issue_id,
            repository=transport.source_evidence.repository,
            branch=transport.source_evidence.branch,
            source_head=transport.source_evidence.local_head,
            parent_epic_id=target.parent_epic_id,
            parent_initiative_id=target.parent_initiative_id,
            dependency_summary=tuple(
                sorted(
                    {resolution.resolved_node_id for resolution in dependency_resolutions},
                    key=lambda value: value.encode("utf-8"),
                )
            ),
            canonical_issue_paths=target.canonical_issue_paths,
            relevant_source_paths=tuple(sorted(set(relevant_source_paths), key=lambda value: value.encode("utf-8"))),
            operator_context=tuple(sorted(set(operator_context), key=lambda value: value.encode("utf-8"))),
            onboarding_companion_path=onboarding_companion_path,
        )
        material = build_candidate_material(
            planner_documents=authoring.documents,
            onboarding_companion_path=authoring.onboarding_companion_path,
            onboarding_companion_bytes=authoring.onboarding_companion_bytes,
            baseline=baseline,
            context=context,
            source_evidence=transport.source_evidence,
            source_payload_sha256=authoring.zip_sha256,
            source_payload_size=authoring.zip_size_bytes,
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
            publication_guard=lambda: _source_evidence_is_current(
                target=target,
                relevant_source_paths=relevant_source_paths,
                repo_root=repo_root,
                evidence=transport.source_evidence,
                preflight_runner=preflight_runner,
            ),
        )
    except PlanningPublicationSourceStale:
        return PlanningCommandResult(
            status="stale",
            reason="planning_source_stale",
            issue_id=target.issue_id,
        )
    except IssuePlanningCandidateCollision:
        return PlanningCommandResult(
            status="rejected",
            reason="output_collision",
            issue_id=target.issue_id,
        )
    except IssuePlanningCandidateArchiveRejected as error:
        return PlanningCommandResult(
            status="rejected",
            reason="archive_rejected",
            issue_id=target.issue_id,
            details=error.findings,
        )
    except IssuePlanningCandidateBuildFailed:
        return PlanningCommandResult(
            status="blocked",
            reason="candidate_build_failed",
            issue_id=target.issue_id,
        )
    except IssuePlanningCandidatePublicationFailed:
        return PlanningCommandResult(
            status="blocked",
            reason="candidate_publication_failed",
            issue_id=target.issue_id,
        )
    except IssuePlanningCandidateOutputRejected:
        return PlanningCommandResult(
            status="rejected",
            reason="candidate_output_rejected",
            issue_id=target.issue_id,
        )
    binding = GitBoundOperationBindingV1.create(
        issue_id=target.issue_id,
        repository=published.identity.source_repository,
        branch=published.identity.source_branch,
        source_head=published.identity.source_head,
        candidate_identity=published.identity,
        onboarding_companion=published.onboarding_companion,
    )
    commit_result = _commit_published_blue(
        thread_port=dependencies.thread_port,
        receipt=thread_receipts[0] if thread_receipts else None,
        lineage=binding,
    )
    if commit_result is not None:
        return replace(commit_result, issue_id=target.issue_id)
    return PlanningCommandResult(
        status="ok",
        reason="candidate_created",
        issue_id=target.issue_id,
        output={
            "candidate_path": str(published.candidate_path),
            "candidate_identity": published.identity.to_dict(),
            "git_bound_operation_binding_sha256": binding.binding_sha256,
            "zip_byte_count": published.zip_byte_count,
        },
    )


def run_issue_planning_review(
    *,
    request: PlanningReviewRequest,
    records: Sequence[StoredMetaRecord],
    repo_root: Path,
    dependencies: IssuePlanningDependencies,
    repo_slug_resolver: Callable[[Path], str | None],
    backend_invoker: Callable[..., PlanningInvocationResult],
    relevant_source_paths: Sequence[str] = (),
    operator_context: Sequence[str] = (),
    timeout_seconds: float | None = None,
    preflight_runner: Callable[[GitHubSyncPreflightRequest], PreflightResult] = run_github_sync_preflight,
    transport_runner: Callable[..., PlanningInvocationResult] = run_issue_planning_transport,
    candidate_loader: Callable[[Path, Path], VerifiedIssueCandidateView] | None = None,
    publisher: Callable[..., PublishedPlanningReviewView] | None = None,
    clock: Callable[[], str] | None = None,
) -> PlanningCommandResult:
    gateway = dependencies.gateway
    candidate_loader = candidate_loader or gateway.load_verified_issue_candidate
    publisher = publisher or gateway.publish_planning_review_evidence
    clock = clock or dependencies.clock.now_iso
    result_issue_id = _result_issue_id(request.issue_id)
    if request.mode == "git-bound" and request.candidate_path is None:
        return PlanningCommandResult(
            status="rejected",
            reason="operation_candidate_required",
            issue_id=result_issue_id,
        )
    try:
        target = resolve_existing_issue_target(request.issue_id, records, repo_root)
        gateway.validate_candidate_output_directory(request.output_dir, repo_root)
        if request.mode == "archive-candidate":
            if request.candidate_path is None or request.reviewed_head is not None:
                raise ValueError("archive Review requires only a Candidate")
            candidate = candidate_loader(request.candidate_path, repo_root)
            if candidate.identity.issue_id != target.issue_id:
                raise ValueError("Candidate Issue does not match Review target")
        elif request.mode == "git-bound":
            if request.candidate_path is None or request.reviewed_head is None:
                raise ValueError("git-bound Review requires Candidate and reviewed_head")
            if re.fullmatch(r"[0-9a-f]{40}", request.reviewed_head) is None:
                raise ValueError("reviewed_head is invalid")
            candidate = candidate_loader(request.candidate_path, repo_root)
            if candidate.identity.issue_id != target.issue_id:
                raise ValueError("Candidate Issue does not match Review target")
        else:
            raise ValueError("Review mode is invalid")
    except IssuePlanningCandidateArchiveRejected as error:
        return PlanningCommandResult(
            status="rejected",
            reason=("operation_binding_rejected" if request.mode == "git-bound" else "archive_rejected"),
            issue_id=result_issue_id,
            details=error.findings,
        )
    except (OSError, UnicodeError, ValueError):
        return PlanningCommandResult(
            status="rejected",
            reason="review_request_rejected",
            issue_id=result_issue_id,
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
            targets = (request.candidate_path,)
        else:
            assert request.reviewed_head is not None
            assert candidate is not None
            if context.source_head != request.reviewed_head:
                raise ValueError("reviewed HEAD does not match synchronized source")
            binding = GitBoundOperationBindingV1.create(
                issue_id=target.issue_id,
                repository=context.repository,
                branch=context.branch,
                source_head=context.source_head,
                candidate_identity=candidate.identity,
                onboarding_companion=candidate.onboarding_companion,
            )
            identity = ReviewedPlanningIdentity(
                mode="git-bound",
                issue_id=target.issue_id,
                repository=context.repository,
                branch=context.branch,
                source_head=context.source_head,
                canonical_target_paths=target.canonical_issue_paths,
                git_bound_operation_binding=binding,
                expected_canonical_target_paths=target.canonical_issue_paths,
            )
            targets = (request.candidate_path,)
        source_paths = _context_source_operands(repo_root, context)
        if request.mode == "git-bound":
            dynamic_paths = (
                *targets,
                *(Path(path) for path in context.canonical_issue_paths),
                *(Path(path) for path in context.relevant_source_paths if path not in context.canonical_issue_paths),
            )
        else:
            dynamic_paths = (*targets, *source_paths)
        captured_identity[:] = [identity]
        return synthesize_planning_evidence_prompt(
            role="reviewer",
            source_head=context.source_head,
            repository=context.repository,
            branch=context.branch,
            context=context,
            remote_head=kwargs["remote_head"],
            upstream=kwargs["upstream"],
            attachment_paths=dynamic_paths,
            provided_context_paths=request.provided_context_paths,
            reviewed_identity=identity.to_dict(),
            reviewed_identity_sha256=identity.sha256,
        )

    thread_receipts: list[ThreadInvocationReceipt] = []

    def capture_thread_receipt(receipt: ThreadInvocationReceipt) -> None:
        thread_receipts[:] = [receipt]

    def review_backend_invoker(**kwargs: Any) -> PlanningInvocationResult:
        if len(captured_identity) != 1:
            return PlanningInvocationResult(
                status="blocked",
                reason="planning_context_rejected",
                details=("review_identity_unavailable",),
            )
        return _thread_backend_invoker(
            backend_invoker=backend_invoker,
            thread_port=dependencies.thread_port,
            mode="fresh_red",
            capture=capture_thread_receipt,
            reviewed_identity=captured_identity[0],
        )(**kwargs)

    transport = transport_runner(
        issue=target.issue_id,
        records=records,
        repo_root=repo_root,
        role="reviewer",
        repo_slug_resolver=repo_slug_resolver,
        backend_invoker=review_backend_invoker,
        relevant_source_paths=relevant_source_paths,
        operator_context=operator_context,
        timeout_seconds=timeout_seconds,
        preflight_runner=preflight_runner,
        prompt_synthesizer=review_prompt_synthesizer,
    )
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
    receipt_gate = _require_publishable_thread_receipt(
        thread_port=dependencies.thread_port,
        receipts=thread_receipts,
        issue_id=target.issue_id,
        mode="fresh_red",
    )
    if receipt_gate is not None:
        return receipt_gate
    review_json = transport.review_json
    payload = None if review_json is None else review_json.json_bytes
    if (
        transport.reason != "transport_received"
        or transport.source_evidence is None
        or payload is None
        or transport.authoring_zip is not None
        or transport.response_sha256 != review_json.sha256
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
            expected_canonical_target_paths=(target.canonical_issue_paths if request.mode == "git-bound" else None),
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
        except IssuePlanningCandidateArchiveRejected:
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
            publication_guard=lambda: _review_publication_is_current(
                target=target,
                relevant_source_paths=relevant_source_paths,
                repo_root=repo_root,
                evidence=evidence,
                preflight_runner=preflight_runner,
                candidate_path=request.candidate_path,
                candidate=candidate,
                candidate_loader=candidate_loader,
            ),
        )
    except PlanningPublicationSourceStale:
        return PlanningCommandResult(
            status="stale",
            reason="review_target_changed",
            issue_id=target.issue_id,
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
            **(
                {"git_bound_operation_binding_sha256": (identity.git_bound_operation_binding.binding_sha256)}
                if identity.git_bound_operation_binding is not None
                else {}
            ),
            "verdict": parsed.verdict,
        },
    )


def run_issue_planning_revise(
    *,
    request: PlanningReviseRequest,
    review_evidence: PlanningRevisionEvidenceInput | None = None,
    records: Sequence[StoredMetaRecord],
    repo_root: Path,
    dependencies: IssuePlanningDependencies,
    repo_slug_resolver: Callable[[Path], str | None],
    backend_invoker: Callable[..., PlanningInvocationResult],
    timeout_seconds: float | None = None,
    preflight_runner: Callable[[GitHubSyncPreflightRequest], PreflightResult] = run_github_sync_preflight,
    transport_runner: Callable[..., PlanningInvocationResult] = run_issue_planning_transport,
    candidate_loader: Callable[[Path, Path], VerifiedIssueCandidateView] | None = None,
    authoring_loader: Callable[..., Any] | None = None,
    publisher: Callable[..., PublishedCandidateView] | None = None,
    clock: Callable[[], str] | None = None,
) -> PlanningCommandResult:
    gateway = dependencies.gateway
    candidate_loader = candidate_loader or gateway.load_verified_issue_candidate
    authoring_loader = authoring_loader or gateway.load_validated_issue_authoring_payload
    publisher = publisher or gateway.build_and_publish_candidate
    clock = clock or dependencies.clock.now_iso
    issue_id = _INVALID_ISSUE_ID
    try:
        candidate = candidate_loader(request.candidate_path, repo_root)
        issue_id = candidate.identity.issue_id
        target = resolve_existing_issue_target(issue_id, records, repo_root)
        output_guard = gateway.validate_candidate_output_directory(request.output_dir, repo_root)
        request_bytes = _read_external_bounded_file(
            request.request_path,
            repo_root=repo_root,
            gateway=gateway,
        )
        revision = PlanningRevisionRequestV1.from_json_bytes(
            request_bytes,
            expected_companion_path=candidate.onboarding_companion.path,
        )
        if revision.candidate_identity != candidate.identity:
            raise ValueError("revision Candidate identity mismatch")
    except IssuePlanningCandidateArchiveRejected as error:
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
                gateway=gateway,
            )
            review_evidence = PlanningRevisionEvidenceInput(
                review_result_path=review_result_path,
                review_result_sha256=hashlib.sha256(review_bytes).hexdigest(),
            )
        else:
            review_bytes = gateway.read_external_review_result(
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
        if reviewed.mode != "archive-candidate" or reviewed.candidate_identity != candidate.identity:
            raise ValueError("revision Review Candidate identity mismatch")
        if _review_result_has_sensitive_content(review):
            raise ValueError("revision Review contains unsafe dynamic content")
        blocking = tuple(finding for finding in review.findings if finding.severity in ("p0", "p1"))
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
    onboarding_companion_path = (
        candidate.onboarding_companion.path
        if revision.lane == "mechanical"
        else _resolve_onboarding_companion_path(operation_time)
    )
    context = replace(
        context,
        onboarding_companion_path=onboarding_companion_path,
    )
    try:
        baseline = parse_current_front_matter_baseline({name: candidate.files[name] for name in DOCUMENT_NAMES})
    except ValueError:
        return PlanningCommandResult(
            status="rejected",
            reason="archive_rejected",
            issue_id=issue_id,
        )
    if revision.lane == "mechanical":
        try:
            revised_payloads = apply_mechanical_revision(
                {
                    **{name: candidate.files[name] for name in DOCUMENT_NAMES},
                    candidate.onboarding_companion.path: candidate.files[candidate.onboarding_companion.path],
                },
                target_file=cast("str", revision.target_file),
                onboarding_companion_path=candidate.onboarding_companion.path,
                old_text=cast("str", revision.old_text),
                new_text=cast("str", revision.new_text),
                diff_budget=cast("int", revision.diff_budget),
            )
            planner_documents = {name: revised_payloads[name] for name in DOCUMENT_NAMES}
            onboarding_companion_bytes = revised_payloads[candidate.onboarding_companion.path]
            source_payload_sha256 = cast(
                "str",
                candidate.source_baseline["planner_payload_sha256"],
            )
            source_payload_size = cast(
                "int",
                candidate.source_baseline["planner_payload_size"],
            )
        except (UnicodeError, ValueError):
            return PlanningCommandResult(
                status="rejected",
                reason="mechanical_revision_rejected",
                issue_id=issue_id,
            )
    else:
        selected = {finding.id: finding for finding in review.findings if finding.id in revision.finding_ids}

        thread_receipts: list[ThreadInvocationReceipt] = []
        continuation_binding: BlueThreadBinding | None = None
        continuation_lineage_sha256: str | None = None
        use_continuation = False
        if dependencies.thread_port is not None:
            try:
                prior_lineage = GitBoundOperationBindingV1.create(
                    issue_id=issue_id,
                    repository=candidate.identity.source_repository,
                    branch=candidate.identity.source_branch,
                    source_head=candidate.identity.source_head,
                    candidate_identity=candidate.identity,
                    onboarding_companion=candidate.onboarding_companion,
                )
                resolution = dependencies.thread_port.resolve_blue(prior_lineage)
                resolution_status = _validate_blue_resolution(resolution, prior_lineage)
            except (AttributeError, OSError, TypeError, UnicodeError, ValueError):
                return PlanningCommandResult(
                    status="blocked",
                    reason="planning_context_rejected",
                    issue_id=issue_id,
                    details=("blue_lineage_ambiguous",),
                )
            if resolution_status == "ambiguous":
                return PlanningCommandResult(
                    status="blocked",
                    reason="planning_context_rejected",
                    issue_id=issue_id,
                    details=("blue_lineage_ambiguous",),
                )
            continuation_binding = resolution.binding
            use_continuation = resolution_status == "exact"
            if continuation_binding is not None:
                continuation_lineage_sha256 = continuation_binding.lineage_sha256

        def capture_thread_receipt(receipt: ThreadInvocationReceipt) -> None:
            thread_receipts[:] = [receipt]

        def revision_prompt_synthesizer(**kwargs: Any) -> Any:
            runtime_context = cast("PlanningContext", kwargs["context"])
            if (
                runtime_context.repository != candidate.identity.source_repository
                or runtime_context.branch != candidate.identity.source_branch
                or runtime_context.source_head != candidate.identity.source_head
            ):
                raise ValueError("semantic revision source changed")
            expectation = authoring_output_expectation(
                issue_id,
                onboarding_companion_path,
            )
            instructions = (
                *(f"selected finding {finding.id}: {finding.severity}" for finding in selected.values()),
                *(f"preserve assumption: {item}" for item in revision.preserve_assumptions),
            )
            attachment_paths = (
                request.candidate_path,
                review_evidence.review_result_path,
                request.request_path,
                *_context_source_operands(repo_root, runtime_context),
            )
            return synthesize_planning_evidence_prompt(
                role="semantic_revision",
                source_head=runtime_context.source_head,
                repository=runtime_context.repository,
                branch=runtime_context.branch,
                context=runtime_context,
                remote_head=kwargs["remote_head"],
                upstream=kwargs["upstream"],
                attachment_paths=attachment_paths,
                provided_context_paths=request.provided_context_paths,
                instructions=instructions,
                output_expectation=expectation,
            )

        def revision_backend_invoker(**kwargs: Any) -> PlanningInvocationResult:
            if dependencies.thread_port is None:
                return backend_invoker(**kwargs)
            try:
                if use_continuation:
                    assert continuation_binding is not None
                    receipt = dependencies.thread_port.invoke_continuation(
                        continuation_binding,
                        backend_invoker,
                        **kwargs,
                    )
                    _validate_thread_receipt(
                        receipt,
                        mode="continuation",
                        required_binding=continuation_binding,
                        required_lineage_sha256=continuation_lineage_sha256,
                    )
                    if (
                        receipt.submission_state == "not_submitted"
                        and receipt.continuation_unavailable_before_submission
                    ):
                        receipt = dependencies.thread_port.invoke_new_blue(backend_invoker, **kwargs)
                        _validate_thread_receipt(receipt, mode="new_blue")
                else:
                    receipt = dependencies.thread_port.invoke_new_blue(backend_invoker, **kwargs)
                    _validate_thread_receipt(receipt, mode="new_blue")
            except (AttributeError, TypeError, ValueError):
                return _thread_contract_failure()
            capture_thread_receipt(receipt)
            return receipt.result

        transport = transport_runner(
            issue=issue_id,
            records=records,
            repo_root=repo_root,
            role="semantic_revision",
            repo_slug_resolver=repo_slug_resolver,
            backend_invoker=revision_backend_invoker,
            relevant_source_paths=tuple(cast("list[str]", candidate.source_baseline["relevant_paths"])),
            operator_context=(),
            timeout_seconds=timeout_seconds,
            preflight_runner=preflight_runner,
            prompt_synthesizer=revision_prompt_synthesizer,
            onboarding_companion_path=onboarding_companion_path,
        )
        if transport.status != "pass":
            return PlanningCommandResult(
                status=cast("Literal['blocked', 'rejected']", transport.status),
                reason=transport.reason,
                issue_id=issue_id,
                details=transport.details,
            )
        receipt_mode: ThreadInvocationMode = "continuation" if use_continuation else "new_blue"
        if thread_receipts and thread_receipts[0].mode == "new_blue":
            receipt_mode = "new_blue"
        receipt_gate = _require_publishable_thread_receipt(
            thread_port=dependencies.thread_port,
            receipts=thread_receipts,
            issue_id=issue_id,
            mode=receipt_mode,
            required_binding=(continuation_binding if receipt_mode == "continuation" else None),
            required_lineage_sha256=(continuation_lineage_sha256 if receipt_mode == "continuation" else None),
        )
        if receipt_gate is not None:
            return receipt_gate
        authoring_zip = transport.authoring_zip
        if (
            authoring_zip is None
            or transport.review_json is not None
            or transport.response_sha256 != authoring_zip.sha256
            or transport.source_evidence is None
        ):
            return PlanningCommandResult(
                status="rejected",
                reason="planner_response_rejected",
                issue_id=issue_id,
            )
        source_evidence = transport.source_evidence
        try:
            authoring = authoring_loader(
                authoring_zip,
                expected_companion_path=onboarding_companion_path,
                repo_root=repo_root,
            )
            planner_documents = authoring.documents
            onboarding_companion_bytes = authoring.onboarding_companion_bytes
            source_payload_sha256 = authoring.zip_sha256
            source_payload_size = authoring.zip_size_bytes
        except (IssuePlanningCandidateArchiveRejected, UnicodeError, ValueError):
            return PlanningCommandResult(
                status="rejected",
                reason="planner_response_rejected",
                issue_id=issue_id,
            )
    try:
        material = build_candidate_material(
            planner_documents=planner_documents,
            onboarding_companion_path=onboarding_companion_path,
            onboarding_companion_bytes=onboarding_companion_bytes,
            baseline=baseline,
            context=context,
            source_evidence=source_evidence,
            source_payload_sha256=source_payload_sha256,
            source_payload_size=source_payload_size,
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
    except IssuePlanningCandidateArchiveRejected:
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
            publication_guard=lambda: _revision_publication_is_current(
                candidate=candidate,
                current_candidate_loader=candidate_loader,
                candidate_path=request.candidate_path,
                target=target,
                repo_root=repo_root,
                source_evidence=source_evidence,
                preflight_runner=preflight_runner,
            ),
        )
    except PlanningPublicationSourceStale:
        return PlanningCommandResult(
            status="stale",
            reason="revision_source_stale",
            issue_id=issue_id,
        )
    except IssuePlanningCandidateCollision:
        return PlanningCommandResult(
            status="rejected",
            reason="output_collision",
            issue_id=issue_id,
        )
    except IssuePlanningCandidateArchiveRejected as error:
        return PlanningCommandResult(
            status="rejected",
            reason="archive_rejected",
            issue_id=issue_id,
            details=error.findings,
        )
    except IssuePlanningCandidateBuildFailed:
        return PlanningCommandResult(
            status="blocked",
            reason="candidate_build_failed",
            issue_id=issue_id,
        )
    except IssuePlanningCandidatePublicationFailed:
        return PlanningCommandResult(
            status="blocked",
            reason="candidate_publication_failed",
            issue_id=issue_id,
        )
    binding = GitBoundOperationBindingV1.create(
        issue_id=issue_id,
        repository=published.identity.source_repository,
        branch=published.identity.source_branch,
        source_head=published.identity.source_head,
        candidate_identity=published.identity,
        onboarding_companion=published.onboarding_companion,
    )
    commit_result = _commit_published_blue(
        thread_port=dependencies.thread_port,
        receipt=thread_receipts[0] if revision.lane == "semantic" and thread_receipts else None,
        lineage=binding,
    )
    if commit_result is not None:
        return replace(commit_result, issue_id=issue_id)
    return PlanningCommandResult(
        status="ok",
        reason="candidate_revised",
        issue_id=issue_id,
        output={
            "candidate_path": str(published.candidate_path),
            "candidate_identity": published.identity.to_dict(),
            "git_bound_operation_binding_sha256": binding.binding_sha256,
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
    candidate: VerifiedIssueCandidateView,
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
        or repository.source_manifest.source_manifest_hash != baseline["source_manifest_hash"]
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


def _resolve_onboarding_companion_path(operation_time: datetime) -> str:
    if operation_time.tzinfo is None:
        raise ValueError("operation time must be timezone-aware")
    timestamp = operation_time.astimezone(timezone.utc).strftime("%Y%m%dt%H%M%Sz")
    return f"artifacts/{timestamp}-guide-new-member-chatgpt-first-issue-planning.md"


def _source_evidence_is_current(
    *,
    target: ExistingIssueTarget,
    relevant_source_paths: Sequence[str],
    repo_root: Path,
    evidence: PlanningSourceEvidence,
    preflight_runner: Callable[[GitHubSyncPreflightRequest], PreflightResult],
) -> bool:
    source_paths = tuple(
        sorted(
            {*target.canonical_issue_paths, *relevant_source_paths},
            key=lambda value: value.encode("utf-8"),
        )
    )
    try:
        preflight = preflight_runner(
            GitHubSyncPreflightRequest(
                repo_root=repo_root,
                ref=None,
                allow_default_branch_fallback=False,
                source_paths=source_paths,
                expected_source_hash=evidence.source_manifest_hash,
            )
        )
    except Exception:
        return False
    if preflight.status != "pass" or preflight.repository is None:
        return False
    repository = preflight.repository
    return (
        repository.branch == evidence.branch
        and repository.upstream == evidence.upstream
        and repository.local_head == evidence.local_head
        and repository.remote_head == evidence.remote_head
        and repository.remote_head_disposition == evidence.remote_head_disposition
        and repository.source_manifest.source_manifest_hash == evidence.source_manifest_hash
    )


def _review_publication_is_current(
    *,
    target: ExistingIssueTarget,
    relevant_source_paths: Sequence[str],
    repo_root: Path,
    evidence: PlanningSourceEvidence,
    preflight_runner: Callable[[GitHubSyncPreflightRequest], PreflightResult],
    candidate_path: Path | None,
    candidate: VerifiedIssueCandidateView | None,
    candidate_loader: Callable[[Path, Path], VerifiedIssueCandidateView],
) -> bool:
    if candidate is None or candidate_path is None:
        return _source_evidence_is_current(
            target=target,
            relevant_source_paths=relevant_source_paths,
            repo_root=repo_root,
            evidence=evidence,
            preflight_runner=preflight_runner,
        )
    if not _candidate_view_is_current(
        candidate=candidate,
        candidate_path=candidate_path,
        repo_root=repo_root,
        candidate_loader=candidate_loader,
    ):
        return False
    if not _source_evidence_is_current(
        target=target,
        relevant_source_paths=relevant_source_paths,
        repo_root=repo_root,
        evidence=evidence,
        preflight_runner=preflight_runner,
    ):
        return False
    return _candidate_view_is_current(
        candidate=candidate,
        candidate_path=candidate_path,
        repo_root=repo_root,
        candidate_loader=candidate_loader,
    )


def _revision_publication_is_current(
    *,
    candidate: VerifiedIssueCandidateView,
    current_candidate_loader: Callable[[Path, Path], VerifiedIssueCandidateView],
    candidate_path: Path,
    target: ExistingIssueTarget,
    repo_root: Path,
    source_evidence: PlanningSourceEvidence,
    preflight_runner: Callable[[GitHubSyncPreflightRequest], PreflightResult],
) -> bool:
    if not _candidate_view_is_current(
        candidate=candidate,
        candidate_path=candidate_path,
        repo_root=repo_root,
        candidate_loader=current_candidate_loader,
    ):
        return False
    if not _source_evidence_is_current(
        target=target,
        relevant_source_paths=tuple(cast("Sequence[str]", candidate.source_baseline.get("relevant_paths", ()))),
        repo_root=repo_root,
        evidence=source_evidence,
        preflight_runner=preflight_runner,
    ):
        return False
    return _candidate_view_is_current(
        candidate=candidate,
        candidate_path=candidate_path,
        repo_root=repo_root,
        candidate_loader=current_candidate_loader,
    )


def _candidate_view_is_current(
    *,
    candidate: VerifiedIssueCandidateView,
    candidate_path: Path,
    repo_root: Path,
    candidate_loader: Callable[[Path, Path], VerifiedIssueCandidateView],
) -> bool:
    try:
        current = candidate_loader(candidate_path, repo_root)
    except Exception:
        return False
    return current.identity == candidate.identity and current.zip_bytes == candidate.zip_bytes


def _read_external_bounded_file(
    path: Path,
    *,
    repo_root: Path,
    gateway: IssuePlanningGateway,
) -> bytes:
    lexical = path.absolute()
    if not lexical.exists() or not lexical.is_file() or _contains_symlink(Path(lexical.anchor), lexical):
        raise ValueError("external input path is unsafe")
    resolved = lexical.resolve(strict=True)
    repository = repo_root.resolve(strict=True)
    if resolved == repository or resolved.is_relative_to(repository):
        raise ValueError("external input must be outside repository")
    try:
        data = gateway.read_bounded_regular_file(resolved, max_bytes=1024 * 1024)
    except ValueError as error:
        if "bounded" in str(error):
            raise ValueError("external input exceeds bounded size") from None
        raise ValueError("external input path is unsafe") from None
    data.decode("utf-8", errors="strict")
    return data


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
