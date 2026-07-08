from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from spec_dock_runtime.domain.authoring_pack.source_manifest import SourceManifest

PreflightStatus = Literal["pass", "blocked", "stale"]
EvidenceMode = Literal["github-synced", "local-context"]
SyncState = Literal["synced", "blocked", "stale", "local_context"]
GitHubSync = Literal["verified", "not_verified", "failed"]


@dataclass(frozen=True)
class PreflightResult:
    status: PreflightStatus
    evidence_mode: EvidenceMode
    sync_state: SyncState
    github_sync: GitHubSync
    requested_ref: str | None
    effective_ref: str | None
    local_head: str | None
    remote_head: str | None
    source_manifest: SourceManifest
    source_hash_mismatch_checked: bool
    blockers: tuple[str, ...] = ()
    remediation: tuple[str, ...] = ()
    expected_source_hash: str | None = None
    current_source_hash: str | None = None
    provided_context_paths: tuple[str, ...] = ()
    diff_summary: str | None = None
    unsynced_reason: str | None = None
    authority: str = "evidence_only"
    adoption_requires: str = "explicit_eal_disposition"
    bundle_generation_not_promotion: bool = True

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "status": self.status,
            "evidence_mode": self.evidence_mode,
            "sync_state": self.sync_state,
            "authority": self.authority,
            "requested_ref": self.requested_ref,
            "effective_ref": self.effective_ref,
            "local_head": self.local_head,
            "remote_head": self.remote_head,
            "source_hash_mismatch_checked": self.source_hash_mismatch_checked,
            "github_sync": self.github_sync,
            "provided_context_paths": list(self.provided_context_paths),
            "diff_summary": self.diff_summary,
            "unsynced_reason": self.unsynced_reason,
            "blockers": list(self.blockers),
            "remediation": list(self.remediation),
            "adoption_requires": self.adoption_requires,
            "bundle_generation_not_promotion": self.bundle_generation_not_promotion,
            "expected_source_hash": self.expected_source_hash,
            "current_source_hash": self.current_source_hash,
        }
        payload.update(self.source_manifest.to_dict())
        return payload


@dataclass(frozen=True)
class GitVisibleRef:
    state: Literal[
        "resolved",
        "branch_missing",
        "connector_unavailable",
        "default_branch_unknown",
        "origin_mismatch",
    ]
    requested_ref: str | None
    effective_ref: str | None
    remote_head: str | None
    blockers: tuple[str, ...] = field(default_factory=tuple)
    remediation: tuple[str, ...] = field(default_factory=tuple)
