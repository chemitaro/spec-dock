from __future__ import annotations

from pathlib import Path
from typing import Any

from ..io_json import _load_json, _now_iso, _try_make_readonly, _warn, _write_json
from .contracts import StoredMetaRecord

_INITIATIVES_DIRNAME = "initiatives"
_META_FILENAME = ".meta.json"
_LEGACY_META_FILENAME = "meta.json"


def _initiatives_root(specdock_dir: Path) -> Path:
    return specdock_dir / _INITIATIVES_DIRNAME


def _iter_node_meta_paths(initiatives_root: Path) -> list[Path]:
    return sorted(initiatives_root.rglob(_META_FILENAME), key=lambda p: p.as_posix())


def _find_legacy_meta_paths(initiatives_root: Path) -> list[Path]:
    return sorted(initiatives_root.rglob(_LEGACY_META_FILENAME), key=lambda p: p.as_posix())


def ensure_no_legacy_meta_json(specdock_dir: Path) -> None:
    initiatives_root = _initiatives_root(specdock_dir)
    if not initiatives_root.exists():
        return
    legacy_paths = _find_legacy_meta_paths(initiatives_root)
    if not legacy_paths:
        return
    listed = "\n".join(f"- {p}" for p in legacy_paths)
    raise RuntimeError(
        "Unsupported legacy meta.json detected. Rename legacy files to '.meta.json' and retry:\n"
        f"{listed}"
    )


def load_node_records(specdock_dir: Path) -> list[StoredMetaRecord]:
    ensure_no_legacy_meta_json(specdock_dir)
    initiatives_root = _initiatives_root(specdock_dir)
    if not initiatives_root.exists():
        return []

    records: list[StoredMetaRecord] = []
    seen_ids: set[str] = set()
    for meta_path in _iter_node_meta_paths(initiatives_root):
        meta = _load_json(meta_path)
        if not isinstance(meta, dict):
            raise RuntimeError(f"Invalid .meta.json (expected object): {meta_path}")

        node_type = str(meta.get("type", "")).strip()
        node_id = str(meta.get("id", "")).strip()
        title = str(meta.get("title", "")).strip()
        slug = str(meta.get("slug", "")).strip()
        if not node_type or not node_id:
            continue
        if node_id in seen_ids:
            raise RuntimeError(f"Duplicate id detected: {node_id} ({meta_path})")
        seen_ids.add(node_id)

        github_issue_number: int | None = None
        github = meta.get("github")
        if isinstance(github, dict) and github.get("issue_number") is not None:
            try:
                github_issue_number = int(github.get("issue_number"))
            except (TypeError, ValueError) as exc:
                raise RuntimeError(
                    f"Invalid github.issue_number in {meta_path}: {github.get('issue_number')}"
                ) from exc

        records.append(
            StoredMetaRecord(
                kind=node_type,
                id=node_id,
                title=title,
                slug=slug,
                path=meta_path.parent.as_posix(),
                parent_id=meta.get("parent_id") or None,
                initiative_id=meta.get("initiative_id") or None,
                epic_id=meta.get("epic_id") or None,
                github_issue_number=github_issue_number,
                meta_path=meta_path.as_posix(),
            )
        )
    return records


def _build_meta_payload(record: StoredMetaRecord) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": 1,
        "type": record.kind,
        "id": record.id,
        "title": record.title,
        "slug": record.slug,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "parent_id": record.parent_id,
        "initiative_id": record.initiative_id,
        "epic_id": record.epic_id,
        "_spec_dock": {
            "managed": True,
            "do_not_edit": True,
            "edit_via": "spec-dock",
        },
    }
    if record.github_issue_number is not None:
        payload["github"] = {"issue_number": int(record.github_issue_number)}
    return payload


def write_meta(dest_dir: Path, record: StoredMetaRecord) -> None:
    meta_path = dest_dir / _META_FILENAME
    _write_json(meta_path, _build_meta_payload(record))
    readonly_ok, readonly_err = _try_make_readonly(meta_path)
    if not readonly_ok:
        reason = readonly_err or "unknown error"
        _warn(f"readonly_lock_failed: {meta_path} ({reason})")
