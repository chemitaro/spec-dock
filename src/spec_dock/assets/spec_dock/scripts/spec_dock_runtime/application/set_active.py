from __future__ import annotations

from pathlib import Path

from ..infra.contracts import ActiveManifestEntry
from .contracts import ActiveViewEntry, ActiveViewResult, ShowActiveRequest
from .ports import Ports


def _resolve_specdock_dir(ports: Ports) -> Path:
    if ports.specdock_dir is not None:
        return ports.specdock_dir
    if ports.repo_root is not None:
        return ports.repo_root / "spec-dock"
    raise RuntimeError("specdock_dir is required")


def _to_view_entry(entry: ActiveManifestEntry | None) -> ActiveViewEntry:
    if entry is None:
        return ActiveViewEntry(id=None, path=None)
    return ActiveViewEntry(id=entry.id, path=entry.path)


def show_active(req: ShowActiveRequest, ports: Ports) -> ActiveViewResult:
    del req
    if ports.active_state_store is None:
        raise RuntimeError("active_state_store is required")

    specdock_dir = _resolve_specdock_dir(ports)
    load_result = ports.active_state_store.load_active_manifest(specdock_dir)
    manifest = load_result.manifest
    return ActiveViewResult(
        initiative=_to_view_entry(manifest.initiative if manifest is not None else None),
        epic=_to_view_entry(manifest.epic if manifest is not None else None),
        issue=_to_view_entry(manifest.issue if manifest is not None else None),
        source=load_result.source,
        warnings=list(load_result.warnings),
    )
