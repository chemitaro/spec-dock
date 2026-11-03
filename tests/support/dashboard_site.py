"""A temporary state root with registered repositories, snapshots and catalogs for server tests (iss-00529)."""

from __future__ import annotations

from dataclasses import replace
import json
from typing import TYPE_CHECKING

from spec_dock.runtime.domain.canonical_sync_state import RegistryEntry, SyncRegistry
from spec_dock.runtime.infra.canonical_registry import read_registry, write_registry_locked
from tests.support.dashboard import node, snapshot

if TYPE_CHECKING:
    from pathlib import Path

    from spec_dock.runtime.domain.canonical_structure import StructureSnapshot


def register(state_root: Path, repository: str | None, catalog: Path) -> None:
    """Add a registry row; `repository` is github.com/<owner>/<name> or None."""
    catalog.mkdir(parents=True, exist_ok=True)
    try:
        current = read_registry(state_root)
    except Exception:
        current = SyncRegistry(None, ())
    entry = RegistryEntry(str(catalog), str(catalog.parent), repository, str(catalog / ".git"), "2026-11-01T00:00:00Z")
    write_registry_locked(state_root, current.with_entry(entry))


def snapshot_file(state_root: Path, repository: str) -> Path:
    host, owner, name = repository.split("/")
    return state_root / "github" / host / owner / name / "snapshot.json"


def write_snapshot(state_root: Path, structure: StructureSnapshot, *, raw: bytes | None = None) -> Path:
    path = snapshot_file(state_root, structure.repository)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw if raw is not None else json.dumps(structure.to_json()).encode())
    return path


def sample(repository: str = "github.com/o/r", *, fetched_at: str = "2026-11-04T11:50:00Z") -> StructureSnapshot:
    structure = snapshot(
        node(1, "epic"),
        node(2, "issue", parent=1, in_progress=True, title="Doing"),
        node(3, "issue", parent=1, blocked_by=(2,)),
        fetched_at=fetched_at,
    )
    return replace(structure, repository=repository)


def scope_dir(catalog: Path, scope_id: str) -> Path:
    directory = catalog / "00000-00999" / scope_id
    directory.mkdir(parents=True, exist_ok=True)
    return directory
