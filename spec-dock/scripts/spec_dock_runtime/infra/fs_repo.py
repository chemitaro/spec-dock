from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any

from .clock import now_iso
from .contracts import StoredMetaRecord
from .json_store import load_json, write_json

_INITIATIVES_DIRNAME = "initiatives"
_META_FILENAME = ".meta.json"
_LEGACY_META_FILENAME = "meta.json"
_NODE_DIRNAME_PATTERNS: dict[str, re.Pattern[str]] = {
    "initiative": re.compile(r"^(?P<id>init(?:-local)?-[0-9]+)-[a-z0-9]+(?:-[a-z0-9]+)*$"),
    "epic": re.compile(r"^(?P<id>epic(?:-local)?-[0-9]+)-[a-z0-9]+(?:-[a-z0-9]+)*$"),
    "issue": re.compile(r"^(?P<id>iss(?:-local)?-[0-9]+)-[a-z0-9]+(?:-[a-z0-9]+)*$"),
}


def _try_make_readonly(path: Path) -> tuple[bool, str | None]:
    try:
        mode = path.stat().st_mode
        path.chmod(mode & ~0o222)
    except OSError as e:
        return False, str(e)

    if os.name == "posix":
        try:
            if path.stat().st_mode & 0o222:
                return False, "write bit still set after chmod"
        except OSError as e:
            return False, str(e)

    return True, None


def _warn(message: str) -> None:
    print(f"spec-dock: (warn) {message}", file=sys.stderr)


def _initiatives_root(specdock_dir: Path) -> Path:
    return specdock_dir / _INITIATIVES_DIRNAME


def _iter_node_meta_paths(initiatives_root: Path) -> list[Path]:
    return sorted(initiatives_root.rglob(_META_FILENAME), key=lambda p: p.as_posix())


def _find_legacy_meta_paths(initiatives_root: Path) -> list[Path]:
    return sorted(initiatives_root.rglob(_LEGACY_META_FILENAME), key=lambda p: p.as_posix())


def _sorted_child_dirs(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return sorted((p for p in path.iterdir() if p.is_dir()), key=lambda p: p.as_posix())


def _parse_node_id_from_dirname(kind: str, dirname: str) -> str | None:
    pattern = _NODE_DIRNAME_PATTERNS[kind]
    matched = pattern.fullmatch(dirname)
    if matched is None:
        return None
    return str(matched.group("id"))


def _iter_expected_node_dirs(initiatives_root: Path) -> list[tuple[str, str, Path]]:
    rows: list[tuple[str, str, Path]] = []
    for initiative_dir in _sorted_child_dirs(initiatives_root):
        initiative_id = _parse_node_id_from_dirname("initiative", initiative_dir.name)
        if initiative_id is None:
            continue
        rows.append(("initiative", initiative_id, initiative_dir))

        epics_root = initiative_dir / "epics"
        for epic_dir in _sorted_child_dirs(epics_root):
            epic_id = _parse_node_id_from_dirname("epic", epic_dir.name)
            if epic_id is None:
                continue
            rows.append(("epic", epic_id, epic_dir))

            issues_root = epic_dir / "issues"
            for issue_dir in _sorted_child_dirs(issues_root):
                issue_id = _parse_node_id_from_dirname("issue", issue_dir.name)
                if issue_id is None:
                    continue
                rows.append(("issue", issue_id, issue_dir))
    return rows


def _meta_path_for_output(meta_path: Path, *, repo_root: Path) -> str:
    try:
        return meta_path.relative_to(repo_root).as_posix()
    except ValueError:
        return meta_path.as_posix()


def _ensure_expected_node_meta_present(*, specdock_dir: Path, initiatives_root: Path) -> None:
    repo_root = specdock_dir.parent
    for kind, node_id, node_dir in _iter_expected_node_dirs(initiatives_root):
        meta_path = node_dir / _META_FILENAME
        if meta_path.is_file():
            continue
        raise RuntimeError(
            "Missing required artifact: "
            f"kind={kind} id={node_id} "
            f"artifact={_meta_path_for_output(meta_path, repo_root=repo_root)} "
            "(restore .meta.json for this node directory)"
        )


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
    _ensure_expected_node_meta_present(specdock_dir=specdock_dir, initiatives_root=initiatives_root)

    records: list[StoredMetaRecord] = []
    seen_ids: set[str] = set()
    for meta_path in _iter_node_meta_paths(initiatives_root):
        meta = load_json(meta_path)
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
        github_repo_owner: str | None = None
        github_repo_name: str | None = None
        github = meta.get("github")
        if isinstance(github, dict):
            if github.get("issue_number") is not None:
                try:
                    github_issue_number = int(github.get("issue_number"))
                except (TypeError, ValueError) as exc:
                    raise RuntimeError(
                        f"Invalid github.issue_number in {meta_path}: {github.get('issue_number')}"
                    ) from exc

            owner_raw = github.get("repo_owner")
            name_raw = github.get("repo_name")
            if owner_raw is not None or name_raw is not None:
                if owner_raw is None or name_raw is None:
                    raise RuntimeError(
                        f"Invalid github.repo_owner/repo_name in {meta_path}: both fields are required"
                    )
                if not isinstance(owner_raw, str) or not isinstance(name_raw, str):
                    raise RuntimeError(
                        f"Invalid github.repo_owner/repo_name in {meta_path}: both fields must be strings"
                    )
                owner = owner_raw.strip().lower()
                name = name_raw.strip().lower()
                if not owner or not name:
                    raise RuntimeError(
                        f"Invalid github.repo_owner/repo_name in {meta_path}: empty value is not allowed"
                    )
                if github_issue_number is None:
                    raise RuntimeError(
                        f"Invalid github.repo_owner/repo_name in {meta_path}: github.issue_number is required"
                    )
                github_repo_owner = owner
                github_repo_name = name

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
                github_repo_owner=github_repo_owner,
                github_repo_name=github_repo_name,
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
        "created_at": now_iso(),
        "updated_at": now_iso(),
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
        github_payload: dict[str, Any] = {"issue_number": int(record.github_issue_number)}
        owner = (record.github_repo_owner or "").strip().lower()
        name = (record.github_repo_name or "").strip().lower()
        if owner or name:
            if not owner or not name:
                raise RuntimeError("github_repo_owner and github_repo_name must be provided together")
            github_payload["repo_owner"] = owner
            github_payload["repo_name"] = name
        payload["github"] = github_payload
    return payload


def write_meta(dest_dir: Path, record: StoredMetaRecord) -> None:
    meta_path = dest_dir / _META_FILENAME
    write_json(meta_path, _build_meta_payload(record))
    readonly_ok, readonly_err = _try_make_readonly(meta_path)
    if not readonly_ok:
        reason = readonly_err or "unknown error"
        _warn(f"readonly_lock_failed: {meta_path} ({reason})")
