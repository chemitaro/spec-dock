from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ..domain.models import IssueSnapshot, SpecGraph
from ..infra.contracts import ActiveManifestLoadResult
from ..infra.contracts import DepsTopologyLoadResult
from ..infra.contracts import StoredMetaRecord


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

    def load_active_issue_id(self, specdock_dir: Path) -> str | None:
        ...


class DepsTopologyReader(Protocol):
    def load_issue_depends_on_map(self, specdock_dir: Path, graph: SpecGraph) -> DepsTopologyLoadResult:
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
