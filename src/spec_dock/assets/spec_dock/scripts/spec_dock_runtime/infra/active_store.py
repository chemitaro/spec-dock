from __future__ import annotations

from pathlib import Path
from typing import Any

from ..io_json import _load_json
from .contracts import ActiveManifest, ActiveManifestEntry, ActiveManifestLoadResult


def _normalize_entry(entry: Any) -> ActiveManifestEntry | None:
    if not isinstance(entry, dict):
        return None
    raw_id = entry.get("id")
    if not isinstance(raw_id, str) or not raw_id.strip():
        return None
    raw_path = entry.get("path")
    path_value = raw_path if isinstance(raw_path, str) and raw_path.strip() else None
    return ActiveManifestEntry(id=raw_id.strip(), path=path_value)


def _normalize_manifest(current: Any) -> ActiveManifest | None:
    if not isinstance(current, dict):
        return None
    # Treat explicit all-null payload as a valid cleared state.
    if all(
        key in current and current[key] is None
        for key in ("initiative", "epic", "issue")
    ):
        return ActiveManifest(initiative=None, epic=None, issue=None)
    initiative = _normalize_entry(current.get("initiative"))
    epic = _normalize_entry(current.get("epic"))
    issue = _normalize_entry(current.get("issue"))
    if initiative is None and epic is None and issue is None:
        return None
    return ActiveManifest(initiative=initiative, epic=epic, issue=issue)


def load_active_manifest(specdock_dir: Path) -> ActiveManifestLoadResult:
    candidates = (
        ("agent.active", specdock_dir / ".agent" / "active.json"),
        ("legacy.work.active", specdock_dir / ".work" / "active.json"),
        ("legacy.work.current", specdock_dir / ".work" / "current.json"),
    )
    warnings: list[str] = []

    for source, path in candidates:
        if not path.exists():
            continue
        try:
            loaded = _load_json(path)
        except RuntimeError:
            warnings.append(f"active_manifest_invalid_json:{source}")
            continue
        manifest = _normalize_manifest(loaded)
        if manifest is None:
            warnings.append(f"active_manifest_invalid_shape:{source}")
            continue
        return ActiveManifestLoadResult(
            manifest=manifest,
            source=source,  # type: ignore[arg-type]
            warnings=warnings,
        )

    return ActiveManifestLoadResult(
        manifest=None,
        source="none",
        warnings=warnings,
    )


def load_active_issue_id(specdock_dir: Path) -> str | None:
    result = load_active_manifest(specdock_dir)
    if result.manifest is None or result.manifest.issue is None:
        return None
    return result.manifest.issue.id
