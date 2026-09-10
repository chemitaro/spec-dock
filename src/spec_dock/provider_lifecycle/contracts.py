"""Immutable contracts used by the provider lifecycle foundation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

Operation = Literal["install", "update", "uninstall"]
SeedPolicy = Literal["create-if-absent", "preserve-only"]
SeedAdmissionState = Literal["absent", "present"]
LifecycleMode = Literal["dry-run", "apply"]
RecordState = Literal["incomplete", "ready", "tooling-absent-preserved-data"]
ActiveLifecycleState = Literal["prepared", "running", "ready", "terminal-cleanup"]
SEED_PATHS = ("spec-dock/.gitignore", ".github/workflows/ci.yml")


@dataclass(frozen=True, slots=True)
class LifecycleRequest:
    """Parser-normalized request echo used by the closed result surface."""

    target: str
    mode: LifecycleMode
    apply: bool
    specs_mode: str | None = None
    operation: Operation | None = None
    candidate_digest: str | None = None
    seed_policy: SeedPolicy | None = None


@dataclass(frozen=True, slots=True)
class LifecycleAction:
    path: str
    category: str
    status: str
    reason: str


@dataclass(frozen=True, slots=True)
class LifecycleResult:
    schema_version: int
    target: str
    mode: LifecycleMode
    apply: bool
    specs_mode: str | None
    status: str
    code: str
    operation: Operation | None
    candidate_digest: str | None
    seed_policy: SeedPolicy | None
    mutation_started: bool
    bootstrap_rolled_back: bool
    phase: str
    last_completed_phase: str
    retry_command: str | None
    continuation: Mapping[str, object]
    failed_paths: Sequence[str]
    pending_paths: Sequence[str]
    summary: Mapping[str, int]
    actions: Sequence[LifecycleAction]
    guidance: Sequence[str]
    warnings: Sequence[str]
    errors: Sequence[str]


@dataclass(frozen=True, slots=True)
class InstallationRecord:
    schema_version: int
    state: RecordState
    operation: Operation | None
    version: str
    candidate_digest: str
    seed_policy: SeedPolicy
    skill_slots: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class SkillSlotMarker:
    schema_version: int
    slot: str
    version: str
    candidate_digest: str


@dataclass(frozen=True, slots=True)
class CandidateDomain:
    kind: str
    path: str
    tree_digest: str
    entry_count: int


@dataclass(frozen=True, slots=True)
class CandidateIdentity:
    schema_version: int
    version: str
    aggregate_digest: str
    domains: Sequence[CandidateDomain]


@dataclass(frozen=True, slots=True)
class RepositoryBinding:
    device: int
    inode: int
    euid: int


@dataclass(frozen=True, slots=True)
class InodeWitness:
    kind: Literal["regular", "directory"]
    device: int
    inode: int
    ctime_ns: int
    mode: int
    link_count: int
    size: int | None
    sha256: str | None


@dataclass(frozen=True, slots=True)
class ActiveState:
    schema_version: int
    state: ActiveLifecycleState
    repository_key: str
    repository_identity: Mapping[str, int]
    tuple_key: str
    operation_generation: str
    operation: Operation
    candidate_digest: str
    seed_policy: SeedPolicy
    seed_admission: Mapping[str, SeedAdmissionState]
    result_family: Literal["install", "legacy-migration", "update", "uninstall"]
    original_record: Mapping[str, object]
    expected_incomplete_record: Mapping[str, str]
    bootstrap_container: Mapping[str, object]
    owned_target_witnesses: Sequence[Mapping[str, object]]
    registered_stage_entries: Sequence[Mapping[str, object]]
    record_temp_witness: InodeWitness | None
    terminal_record_digest: str
    cleanup_token: str
    cleanup_retry_invocation: Mapping[str, str]
    deferred_invocation: Mapping[str, str] | None


@dataclass(frozen=True, slots=True)
class CompletionReceipt:
    schema_version: int
    repository_key: str
    tuple_key: str
    operation_generation: str
    operation: Operation
    candidate_digest: str
    seed_policy: SeedPolicy
    result_family: Literal["install", "legacy-migration", "update", "uninstall"]
    terminal_record_digest: str
    cleanup_token: str
    cleanup_retry_invocation: Mapping[str, str]
    deferred_invocation: Mapping[str, str] | None


@dataclass(frozen=True, slots=True)
class StageOwner:
    schema_version: int
    repository_key: str
    tuple_key: str
    operation_generation: str
    operation: Operation
    candidate_digest: str
    seed_policy: SeedPolicy
    result_family: Literal["install", "legacy-migration", "update", "uninstall"]
    entry_names: Sequence[str]
    candidate_domain_digests: Sequence[str | None]
    original_domain_digests: Sequence[str | None]


__all__ = [
    "SEED_PATHS",
    "ActiveState",
    "CandidateIdentity",
    "CompletionReceipt",
    "InodeWitness",
    "InstallationRecord",
    "LifecycleAction",
    "LifecycleRequest",
    "LifecycleResult",
    "RepositoryBinding",
    "SeedAdmissionState",
    "SkillSlotMarker",
    "StageOwner",
]
