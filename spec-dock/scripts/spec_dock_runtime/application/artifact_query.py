"""Read stored Artifact identities without opening bodies or inferring authority."""

from __future__ import annotations

from dataclasses import dataclass
import os
import stat
from typing import TYPE_CHECKING

from spec_dock_runtime.application.scope_query import load_scope_views, show_scope
from spec_dock_runtime.domain.artifacts import (
    ArtifactFilename,
    GenericImportedArtifactFilename,
    SequentialArtifactFilename,
    can_create_artifact_type,
    parse_existing_artifact_filename,
    scan_artifact_slot_ledger,
)
from spec_dock_runtime.domain.selectors import ArtifactRootSelector, parse_artifact_selector

if TYPE_CHECKING:
    from pathlib import Path

    from spec_dock_runtime.domain.lifecycle import SelectionState


@dataclass(frozen=True)
class ArtifactCatalogEntry:
    artifact_id: str
    scope_id: str
    relative_path: str
    creation_type: str | None
    observed_type: str
    observed_authority: str


@dataclass(frozen=True)
class ArtifactCatalog:
    scope_id: str
    items: tuple[ArtifactCatalogEntry, ...]


def list_artifacts(*, repo_root: Path, scope: str, selection: SelectionState | None = None) -> ArtifactCatalog:
    """Return identifiers only; source paths, contents, hashes, and sizes stay private."""
    specdock_dir = repo_root / "spec-dock"
    if specdock_dir.is_symlink() or not specdock_dir.is_dir():
        raise ValueError("SpecDock workspace root is missing or redirected")
    selector = parse_artifact_selector(scope)
    if isinstance(selector, ArtifactRootSelector):
        scope_id = "root"
        owner = specdock_dir
    else:
        target = show_scope(load_scope_views(specdock_dir), scope, selection=selection)
        scope_id = target.id
        owner = target.path
    artifacts_dir = owner / "artifacts"
    if not os.path.lexists(artifacts_dir):
        return ArtifactCatalog(scope_id, ())
    if artifacts_dir.is_symlink() or not artifacts_dir.is_dir():
        raise ValueError("ARTIFACT_CATALOG_INVALID")
    problem, _ledger = scan_artifact_slot_ledger(artifacts_dir)
    if problem is not None:
        raise ValueError("ARTIFACT_CATALOG_INVALID")
    entries: list[ArtifactCatalogEntry] = []
    with os.scandir(artifacts_dir) as directory:
        for entry in directory:
            if entry.name == "rules.md":
                continue
            parsed = parse_existing_artifact_filename(entry.name)
            if parsed is None:
                continue
            info = entry.stat(follow_symlinks=False)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise ValueError("ARTIFACT_CATALOG_INVALID")
            creation_type: str | None = None
            if isinstance(parsed, GenericImportedArtifactFilename):
                observed_type = "generic-file"
            elif isinstance(parsed, SequentialArtifactFilename):
                observed_type = f"historical-{parsed.artifact_type}"
            else:
                assert isinstance(parsed, ArtifactFilename)
                if parsed.artifact_type != "blank" and can_create_artifact_type(parsed.artifact_type):
                    creation_type = parsed.artifact_type
                    observed_type = "current-typed"
                elif parsed.artifact_type == "blank":
                    observed_type = "untyped-markdown"
                else:
                    observed_type = f"historical-{parsed.artifact_type}"
            path = artifacts_dir / entry.name
            entries.append(
                ArtifactCatalogEntry(
                    parsed.artifact_id,
                    scope_id,
                    path.relative_to(repo_root).as_posix(),
                    creation_type,
                    observed_type,
                    "unverified",
                )
            )
    entries.sort(key=lambda item: item.artifact_id)
    return ArtifactCatalog(scope_id, tuple(entries))


def show_artifact(
    *, repo_root: Path, scope: str, artifact_id: str, selection: SelectionState | None = None
) -> ArtifactCatalogEntry:
    matches = [
        item
        for item in list_artifacts(repo_root=repo_root, scope=scope, selection=selection).items
        if item.artifact_id == artifact_id
    ]
    if not matches:
        raise LookupError("Artifact was not found")
    if len(matches) != 1:
        raise ValueError("ARTIFACT_CATALOG_INVALID")
    return matches[0]
