"""Read-only Scope list/show projections from one local observation pass."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import TYPE_CHECKING, cast

from spec_dock_runtime.domain.ids import parse_id
from spec_dock_runtime.domain.lifecycle import GithubBackend, LocalBackend, StatusObservation, decode_scope_metadata
from spec_dock_runtime.domain.selectors import (
    ActiveScopeSelector,
    GithubScopeSelector,
    ScopeIdSelector,
    parse_scope_selector,
)
from spec_dock_runtime.infra import fs_repo
from spec_dock_runtime.infra.json_store import read_guarded_json

if TYPE_CHECKING:
    from spec_dock_runtime.domain.lifecycle import ObservedState, ScopeBackend, SelectionState
    from spec_dock_runtime.domain.selectors import ScopeKind


@dataclass(frozen=True)
class ScopeView:
    id: str
    kind: ScopeKind
    title: str
    parent_id: str | None
    backend: ScopeBackend
    path: Path
    revision: int
    status: StatusObservation
    github_ref: str | None


@dataclass(frozen=True)
class ScopeListResult:
    items: tuple[ScopeView, ...]
    snapshot_id: str
    kind: ScopeKind | None
    parent_id: str | None
    state: ObservedState | None


def _cached_status(payload: object, scope_id: str, backend: GithubBackend) -> StatusObservation:
    unknown = StatusObservation("unknown", "github", "unknown", None, None, True)
    if payload is None:
        return unknown
    if (
        not isinstance(payload, dict)
        or payload.get("schema_version") != 1
        or not isinstance(payload.get("items"), dict)
    ):
        raise ValueError("GitHub status cache schema is invalid")
    item = payload["items"].get(scope_id)
    if item is None:
        return unknown
    expected_ref = f"gh:{backend.repo_owner.lower()}/{backend.repo_name.lower()}#{backend.issue_number}"
    if not isinstance(item, dict) or item.get("github_ref") != expected_ref:
        return unknown
    state = item.get("state")
    observed_at = item.get("observed_at")
    if state not in ("open", "completed", "not-planned", "unknown") or not isinstance(observed_at, str):
        return unknown
    return StatusObservation(cast("ObservedState", state), "github", "cache", observed_at, None, True)


def load_scope_views(specdock_dir: Path) -> tuple[ScopeView, ...]:
    """Read local metadata and saved status only; never contact GitHub or mutate files."""
    if specdock_dir.is_symlink() or not specdock_dir.is_dir():
        raise ValueError("SpecDock workspace root is missing or redirected")
    loaded_cache = read_guarded_json(specdock_dir / ".agent" / "github-status-cache.json")
    cache = loaded_cache[0] if loaded_cache is not None else None
    views: list[ScopeView] = []
    for record in fs_repo.load_node_records(specdock_dir):
        loaded = read_guarded_json(Path(record.meta_path))
        if loaded is None or not isinstance(loaded[0], dict):
            raise ValueError("Scope metadata is missing or invalid")
        metadata = decode_scope_metadata(loaded[0])
        if (
            metadata.raw.get("id") != record.id
            or metadata.raw.get("type") != record.kind
            or metadata.raw.get("title") != record.title
            or metadata.raw.get("parent_id") != record.parent_id
        ):
            raise ValueError("Scope metadata changed during query")
        path = Path(record.path).resolve(strict=True)
        if not path.is_relative_to(specdock_dir.resolve(strict=True)):
            raise ValueError("Scope path is outside this workspace")
        if isinstance(metadata.backend, LocalBackend):
            lifecycle = metadata.backend.lifecycle
            status = StatusObservation(lifecycle.state, "local", "local", lifecycle.updated_at, None, False)
            github_ref = None
        else:
            status = _cached_status(cache, record.id, metadata.backend)
            github_ref = (
                f"gh:{metadata.backend.repo_owner.lower()}/{metadata.backend.repo_name.lower()}"
                f"#{metadata.backend.issue_number}"
            )
        views.append(
            ScopeView(
                id=record.id,
                kind=cast("ScopeKind", record.kind),
                title=record.title,
                parent_id=record.parent_id,
                backend=metadata.backend,
                path=path,
                revision=metadata.revision,
                status=status,
                github_ref=github_ref,
            )
        )
    return tuple(sorted(views, key=_sort_key))


def _sort_key(item: ScopeView) -> tuple[int, int, int, str]:
    _prefix, local, number = parse_id(item.id)
    return ({"initiative": 0, "epic": 1, "issue": 2}[item.kind], number, int(local), item.id)


def list_scopes(
    views: tuple[ScopeView, ...],
    *,
    kind: ScopeKind | None = None,
    parent_id: str | None = None,
    state: ObservedState | None = None,
) -> ScopeListResult:
    items = tuple(
        view
        for view in views
        if (kind is None or view.kind == kind)
        and (parent_id is None or view.parent_id == parent_id)
        and (state is None or view.status.state == state)
    )
    fingerprint = hashlib.sha256(
        json.dumps(
            [
                (
                    view.id,
                    view.revision,
                    view.title,
                    view.parent_id,
                    view.status.state,
                    view.status.source,
                    view.status.observed_at,
                )
                for view in views
            ],
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    return ScopeListResult(items, f"sha256:{fingerprint}", kind, parent_id, state)


def show_scope(views: tuple[ScopeView, ...], target: str, *, selection: SelectionState | None = None) -> ScopeView:
    selector = parse_scope_selector(target)
    if isinstance(selector, ScopeIdSelector):
        matches = [item for item in views if item.id == selector.id and item.kind == selector.kind]
    elif isinstance(selector, GithubScopeSelector):
        expected = f"gh:{selector.owner}/{selector.repo}#{selector.issue_number}"
        matches = [item for item in views if item.github_ref == expected]
    elif isinstance(selector, ActiveScopeSelector):
        if selection is None:
            raise LookupError("active selection is unavailable")
        selected = selection.focus_id if selector.role == "current" else getattr(selection, f"{selector.role}_id")
        matches = [item for item in views if item.id == selected] if selected is not None else []
    else:
        raise TypeError("unsupported Scope selector")
    if not matches:
        raise LookupError("Scope was not found")
    if len(matches) != 1:
        raise ValueError("ambiguous Scope selector")
    return matches[0]
