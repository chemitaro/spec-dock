"""Rebuild derived workspace state without selecting or changing a Scope."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import json
from typing import TYPE_CHECKING, Literal

from spec_dock_runtime.application.scope_query import ScopeView, list_scopes, load_scope_views
from spec_dock_runtime.cli.admission import admit_writer
from spec_dock_runtime.domain.lifecycle import GithubBackend, StatusObservation
from spec_dock_runtime.infra.active_store import load_selection_v3
from spec_dock_runtime.infra.control_store import load_control
from spec_dock_runtime.infra.generation_store import Generation, publish_generation
from spec_dock_runtime.infra.github_lifecycle import GithubIssueGateway, RemoteIssueError
from spec_dock_runtime.infra.json_store import atomic_write_json, read_guarded_json
from spec_dock_runtime.infra.writer_lock import WriterLock

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path


@dataclass(frozen=True)
class WorkspaceSyncResult:
    generation: Generation
    node_count: int
    complete: bool
    projection_stale: bool
    findings: tuple[str, ...]


@dataclass(frozen=True)
class WorkspaceSyncPreview:
    node_count: int
    source: Literal["cache", "github"]
    valid: bool
    remote_count: int
    findings: tuple[str, ...]


def preview_sync_workspace(
    *, repo_root: Path, source: Literal["cache", "github"] = "cache", allow_invalid: bool = False, offline: bool = False
) -> WorkspaceSyncPreview:
    """Inspect planned inputs without publishing or contacting GitHub."""
    if source not in ("cache", "github"):
        raise ValueError("workspace sync source must be cache or github")
    views = load_scope_views(repo_root / "spec-dock")
    findings = _structural_findings(views)
    if findings and not allow_invalid:
        raise ValueError("workspace structure is invalid")
    remote_count = sum(isinstance(item.backend, GithubBackend) for item in views)
    if source == "github" and offline and remote_count:
        raise ValueError("offline mode cannot refresh GitHub-backed Scopes")
    return WorkspaceSyncPreview(len(views), source, not findings, remote_count, findings)


def _structural_findings(views: Sequence[ScopeView]) -> tuple[str, ...]:
    by_id = {item.id: item for item in views}
    findings: list[str] = []
    for item in views:
        expected_parent_kind = {"initiative": None, "epic": "initiative", "issue": "epic"}[item.kind]
        if expected_parent_kind is None:
            if item.parent_id is not None:
                findings.append(f"invalid_parent:{item.id}")
            continue
        parent = by_id.get(item.parent_id or "")
        if parent is None or parent.kind != expected_parent_kind:
            findings.append(f"invalid_parent:{item.id}")
    return tuple(findings)


def _json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _refresh_github(
    views: tuple[ScopeView, ...],
    *,
    repo_root: Path,
    gateway: GithubIssueGateway,
) -> tuple[tuple[ScopeView, ...], tuple[str, ...]]:
    refreshed: list[ScopeView] = []
    warnings: list[str] = []
    observed_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for item in views:
        if not isinstance(item.backend, GithubBackend):
            refreshed.append(item)
            continue
        repository = f"{item.backend.repo_owner}/{item.backend.repo_name}"
        try:
            record = gateway.get(repo_root, repository, item.backend.issue_number)
        except RemoteIssueError:
            warnings.append(f"github_unavailable:{item.id}")
            refreshed.append(item)
            continue
        refreshed.append(
            replace(
                item,
                status=StatusObservation(record.state, "github", "github", observed_at, record.updated_at, False),
            )
        )
    return tuple(refreshed), tuple(warnings)


def _node_payload(item: ScopeView, *, repo_root: Path) -> dict[str, object]:
    return {
        "id": item.id,
        "kind": item.kind,
        "title": item.title,
        "parent_id": item.parent_id,
        "path": item.path.relative_to(repo_root).as_posix(),
        "revision": item.revision,
        "backend": item.backend.kind,
        "github_ref": item.github_ref,
        "status": {
            "state": item.status.state,
            "authority": item.status.authority,
            "source": item.status.source,
            "observed_at": item.status.observed_at,
            "remote_updated_at": item.status.remote_updated_at,
            "stale": item.status.stale,
        },
    }


def _publish_projection(specdock_dir: Path, *, index: dict[str, object], tree: dict[str, object]) -> bool:
    stale = False
    for name, payload in (("index-all.json", index), ("tree-all.json", tree)):
        path = specdock_dir / ".agent" / name
        try:
            current = read_guarded_json(path)
            atomic_write_json(path, payload, expected_identity=current[1] if current is not None else None)
        except (OSError, RuntimeError, ValueError):
            stale = True
    return stale


def _publish_github_cache(specdock_dir: Path, views: Sequence[ScopeView]) -> bool:
    items = {
        item.id: {
            "github_ref": item.github_ref,
            "state": item.status.state,
            "observed_at": item.status.observed_at,
        }
        for item in views
        if isinstance(item.backend, GithubBackend)
        and item.status.state != "unknown"
        and item.status.observed_at is not None
    }
    path = specdock_dir / ".agent" / "github-status-cache.json"
    try:
        current = read_guarded_json(path)
        atomic_write_json(
            path, {"schema_version": 1, "items": items}, expected_identity=current[1] if current else None
        )
    except (OSError, RuntimeError, ValueError):
        return True
    return False


def sync_workspace(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    source: Literal["cache", "github"] = "cache",
    allow_invalid: bool = False,
    offline: bool = False,
    gateway: GithubIssueGateway | None = None,
    lock_timeout: float = 0.0,
) -> WorkspaceSyncResult:
    """Stage one complete derived snapshot, then atomically expose its pointer."""
    if source not in ("cache", "github"):
        raise ValueError("workspace sync source must be cache or github")
    with WriterLock(common_dir, timeout=lock_timeout):
        admit_writer(
            load_control(common_dir),
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
        )
        specdock_dir = repo_root / "spec-dock"
        views = load_scope_views(specdock_dir)
        initial_snapshot_id = list_scopes(views).snapshot_id
        selection, _identity = load_selection_v3(specdock_dir, worktree_id=worktree_id)
        findings = _structural_findings(views)
        if findings and not allow_invalid:
            raise ValueError("workspace structure is invalid")
        has_remote = any(isinstance(item.backend, GithubBackend) for item in views)
        if source == "github" and offline and has_remote:
            raise ValueError("offline mode cannot refresh GitHub-backed Scopes")
        warnings: tuple[str, ...] = ()
        if source == "github" and has_remote:
            views, warnings = _refresh_github(
                views, repo_root=repo_root, gateway=gateway if gateway is not None else GithubIssueGateway()
            )
        complete = not warnings
        nodes = {item.id: _node_payload(item, repo_root=repo_root) for item in views}
        snapshot_id = list_scopes(views).snapshot_id
        index: dict[str, object] = {
            "schema_version": 1,
            "snapshot_id": snapshot_id,
            "source": source,
            "valid": not findings,
            "complete": complete,
            "active": {"focus_id": selection.focus_id, "revision": selection.revision},
            "nodes": nodes,
            "findings": [*findings, *warnings],
        }
        tree: dict[str, object] = {
            "schema_version": 1,
            "snapshot_id": snapshot_id,
            "nodes": [{"id": item.id, "parent_id": item.parent_id, "kind": item.kind} for item in views],
        }
        if list_scopes(load_scope_views(specdock_dir)).snapshot_id != initial_snapshot_id:
            raise ValueError("Scope metadata changed during sync")
        current_selection, _ = load_selection_v3(specdock_dir, worktree_id=worktree_id)
        if current_selection != selection:
            raise ValueError("active selection changed during sync")
        generation = publish_generation(
            specdock_dir,
            files={"index.json": _json_bytes(index), "tree.json": _json_bytes(tree)},
            source=source,
            valid=not findings,
            selection_revision=selection.revision,
            warnings=(*findings, *warnings),
        )
        projection_stale = _publish_projection(specdock_dir, index=index, tree=tree)
        if source == "github" and has_remote:
            projection_stale = _publish_github_cache(specdock_dir, views) or projection_stale
        return WorkspaceSyncResult(generation, len(views), complete, projection_stale, (*findings, *warnings))
