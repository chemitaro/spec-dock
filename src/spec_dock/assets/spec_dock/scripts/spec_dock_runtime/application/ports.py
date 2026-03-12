from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from typing import Any
from typing import Protocol

from .contracts import ArtifactWriteResult, SyncCommandResult, SyncRequest
from ..domain.models import IssueSnapshot, SpecGraph
from ..infra.contracts import ActiveManifest
from ..infra.contracts import ActiveManifestLoadResult
from ..infra.contracts import ActiveStateSnapshot
from ..infra.contracts import DepsTopologyLoadResult
from ..infra.contracts import StoredMetaRecord
from ..presentation.contracts import ArtifactBundle


class ValidateNodeReader(Protocol):
    def load_node_records(self) -> list[StoredMetaRecord]:
        ...


class DerivedStateReader(Protocol):
    def load_cached_issue_status_by_id(self, specdock_dir: Path) -> dict[str, str]:
        ...


class IssueGateway(Protocol):
    def issue_index(self, repo_root: Path, *, limit: int) -> list[IssueSnapshot]:
        ...


class ActiveStateStore(Protocol):
    def load_active_manifest(self, specdock_dir: Path) -> ActiveManifestLoadResult:
        ...

    def load_active_manifest_no_migrate(self, specdock_dir: Path) -> ActiveManifestLoadResult:
        ...

    def load_active_issue_id(self, specdock_dir: Path) -> str | None:
        ...

    def write_active_manifest(self, specdock_dir: Path, manifest: ActiveManifest) -> ActiveManifest:
        ...

    def apply_active_pointers(self, specdock_dir: Path, manifest: ActiveManifest | None, rendered_context_pack: str) -> None:
        ...

    def patch_agent_state_active_fields(self, specdock_dir: Path, manifest: ActiveManifest | None) -> None:
        ...

    def snapshot_current_state(self, specdock_dir: Path) -> ActiveStateSnapshot:
        ...

    def restore_previous_state(self, specdock_dir: Path, snapshot: ActiveStateSnapshot) -> None:
        ...


class DepsTopologyReader(Protocol):
    def load_issue_depends_on_map(self, specdock_dir: Path, graph: SpecGraph) -> DepsTopologyLoadResult:
        ...


class GitGateway(Protocol):
    def require_clean_working_tree(self, repo_root: Path) -> None:
        ...

    def current_branch_or_none(self, repo_root: Path) -> str | None:
        ...

    def local_branch_exists(self, repo_root: Path, branch: str) -> bool:
        ...

    def checkout_branch(self, repo_root: Path, branch: str) -> None:
        ...

    def create_and_checkout_branch(self, repo_root: Path, branch: str) -> None:
        ...

    def check_ref_format_branch(self, repo_root: Path, branch: str) -> bool:
        ...


class ArtifactWriter(Protocol):
    def write(self, specdock_dir: Path, bundle: ArtifactBundle) -> ArtifactWriteResult:
        ...


class SyncLegacyRunner(Protocol):
    def run_sync(
        self,
        req: SyncRequest,
        *,
        active_manifest_mode: Literal["migrate", "no_migrate"] = "migrate",
    ) -> SyncCommandResult:
        ...


@dataclass(frozen=True)
class Ports:
    node_reader: ValidateNodeReader
    repo_root: Path | None
    specdock_dir: Path | None = None
    derived_state_reader: DerivedStateReader | None = None
    issue_gateway: IssueGateway | None = None
    active_state_store: ActiveStateStore | None = None
    deps_topology_reader: DepsTopologyReader | None = None
    git_gateway: GitGateway | None = None
    json_store: Any | None = None
    clock: Any | None = None
    artifact_writer: ArtifactWriter | None = None
    sync_legacy_runner: SyncLegacyRunner | None = None
