from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path


DEFAULT_SOURCE_PATHS: tuple[str, ...] = (
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack",
    "spec-dock/scripts/spec_dock_runtime/commands/authoring.py",
    "spec-dock/scripts/spec_dock_runtime/application/authoring_pack",
    "spec-dock/scripts/spec_dock_runtime/domain/authoring_pack",
    "spec-dock/scripts/spec_dock_runtime/presentation/authoring_pack",
)


@dataclass(frozen=True)
class SourceManifest:
    source_paths: tuple[str, ...]
    source_hashes: dict[str, str]
    source_manifest_hash: str

    def to_dict(self) -> dict[str, object]:
        return {
            "source_paths": list(self.source_paths),
            "source_hashes": dict(self.source_hashes),
            "source_manifest_hash": self.source_manifest_hash,
        }


def build_source_manifest(repo_root: Path, source_paths: tuple[str, ...]) -> SourceManifest:
    paths = source_paths or DEFAULT_SOURCE_PATHS
    source_hashes: dict[str, str] = {}
    selected_paths: list[str] = []
    for source_path in paths:
        path = (repo_root / source_path).resolve() if not Path(source_path).is_absolute() else Path(source_path)
        if not path.exists():
            continue
        selected_paths.append(_repo_relative(repo_root, path))
        if path.is_file():
            rel_path = _repo_relative(repo_root, path)
            source_hashes[rel_path] = _hash_file(path)
            continue
        for child in sorted(item for item in path.rglob("*") if item.is_file() and not _is_ignored_manifest_path(item)):
            rel_path = _repo_relative(repo_root, child)
            source_hashes[rel_path] = _hash_file(child)
    manifest_payload = json.dumps(source_hashes, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return SourceManifest(
        source_paths=tuple(selected_paths),
        source_hashes=source_hashes,
        source_manifest_hash=hashlib.sha256(manifest_payload).hexdigest(),
    )


def expected_hash_from_manifest(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    value = payload.get("source_manifest_hash")
    if not isinstance(value, str) or not value:
        raise ValueError("expected source manifest must contain source_manifest_hash")
    return value


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_ignored_manifest_path(path: Path) -> bool:
    return "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()
