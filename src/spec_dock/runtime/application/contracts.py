from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from spec_dock.runtime.domain.artifacts import (
    CURRENT_CREATABLE_ARTIFACT_TYPES,  # noqa: F401 - runtime re-export for CLI contracts.
)

if TYPE_CHECKING:
    from pathlib import Path


POST_MUTATION_FATAL_WARNING_CODES: tuple[str, ...] = ("gh_fetch_failed",)
BootstrapStatus = Literal["skipped", "succeeded", "failed", "detection_failed"]
WorktreeClassificationReason = Literal[
    "root_valid",
    "root_missing",
    "root_blank",
    "root_invalid",
    "namespace_symlink",
]
WorktreeOrigin = Literal["spec_dock_managed", "external", "classification_unavailable"]
WORKTREE_CLASSIFICATION_REASONS: tuple[WorktreeClassificationReason, ...] = (
    "root_valid",
    "root_missing",
    "root_blank",
    "root_invalid",
    "namespace_symlink",
)
WORKTREE_ORIGINS: tuple[WorktreeOrigin, ...] = (
    "spec_dock_managed",
    "external",
    "classification_unavailable",
)


GitHubCapability = Literal[
    "repo_metadata_read",
    "pull_request_read",
    "check_runs_read",
    "commit_statuses_read",
    "status_check_rollup_read",
    "actions_read",
    "issue_comments_read",
    "pull_reviews_read",
    "pull_review_comments_read",
    "pull_review_threads_read",
    "trigger_comment_write",
]
GitHubCapabilityStatus = Literal[
    "ok",
    "permission_denied",
    "auth_missing",
    "rate_limited",
    "target_unavailable",
    "transient_unknown",
    "schema_unavailable",
    "skipped",
]
GitHubCapabilityTokenSource = Literal["GH_TOKEN", "GITHUB_TOKEN", "gh_saved_auth", "unknown"]
GitHubCapabilitySeverity = Literal["info", "warning", "blocking"]
GitHubCapabilityGroup = Literal["core", "extended"]
GitHubCapabilityDiagnosticCode = Literal[
    "github_capability_ok",
    "github_token_permission_denied",
    "github_auth_missing",
    "github_rate_limited",
    "github_target_unavailable",
    "github_transient_unknown",
    "github_schema_unavailable",
    "github_capability_skipped",
    "github_probe_target_mismatch",
]


@dataclass(frozen=True)
class GitHubCapabilityProbeRequest:
    github_repo: str
    github_pr: int
    github_head_sha: str
    include_extended: bool = False


@dataclass(frozen=True)
class GitHubCapabilityDiagnostic:
    code: GitHubCapabilityDiagnosticCode
    capability: GitHubCapability
    status: GitHubCapabilityStatus
    token_source: GitHubCapabilityTokenSource
    api: str
    severity: GitHubCapabilitySeverity
    message: str
    recommended_next_action: str
    secret_redacted: bool
    stderr_sha256: str | None
    group: GitHubCapabilityGroup


@dataclass(frozen=True)
class GitWorktreeRecord:
    path: Path
    head: str | None
    branch: str | None
    detached: bool = False
    bare: bool = False
    locked: bool = False
    prunable: bool = False
    locked_reason: str | None = None
    prunable_reason: str | None = None
    inventory_error: str | None = None


BinaryArtifactCleanupState = Literal["not_created", "removed", "retained"]
BinaryArtifactPublishWarning = Literal[
    "directory_fsync_failed",
    "temp_cleanup_retained",
]


FileArtifactTargetKind = Literal["root", "initiative", "epic", "issue"]
FileArtifactSourceVisibility = Literal["repo_relative", "basename_only"]
FileArtifactPublicationState = Literal["not_committed", "committed", "committed_with_warning"]
FileArtifactRetryDisposition = Literal["safe_after_remediation", "not_needed"]
FileArtifactStorageIdentity = Literal["generic"]
FileArtifactImportWarning = Literal[
    "create_lock_release_failed",
    "directory_fsync_failed",
    "temp_cleanup_retained",
]


MutateDepsAction = Literal["add", "remove"]
MutateDepsResultKind = Literal["updated", "unchanged"]


DeleteTerminalStatus = Literal[
    "ok",
    "invalid_selector_combination",
    "invalid_selector_syntax",
    "target_not_found",
    "ambiguous_target",
    "active_conflict",
    "dependency_conflict",
    "recursive_required",
    "confirmation_required",
    "metadata_validation_failed",
    "remote_close_failed",
    "local_delete_partial_failure",
]
