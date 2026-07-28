from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from spec_dock_runtime.application.authoring_pack.github_sync_preflight import (
    GitHubSyncPreflightRequest,
    run_github_sync_preflight,
)
from spec_dock_runtime.application.issue_planning_prompt import synthesize_issue_planning_prompt
from spec_dock_runtime.domain.ids import normalize_id_input
from spec_dock_runtime.domain.issue_planning_contracts import (
    PlanningContext,
    PlanningInvocationResult,
    PlanningSourceEvidence,
)

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
    return actual_hashes == expected_hashes
