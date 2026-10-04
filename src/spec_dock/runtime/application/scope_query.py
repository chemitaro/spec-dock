"""Read-only Scope list/show projections from one local observation pass."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import TYPE_CHECKING, cast

from spec_dock.runtime.domain.ids import parse_id
from spec_dock.runtime.domain.lifecycle import LocalBackend, StatusObservation
from spec_dock.runtime.domain.selectors import (
    ActiveScopeSelector,
    GithubScopeSelector,
    ScopeIdSelector,
    parse_scope_selector,
)
from spec_dock.runtime.infra.scope_tree import load_scope_tree

if TYPE_CHECKING:
    from pathlib import Path

    from spec_dock.runtime.domain.lifecycle import ObservedState, ScopeBackend, SelectionState
    from spec_dock.runtime.domain.selectors import ScopeKind


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


def load_scope_views(specdock_dir: Path, *, target_id: str | None = None, timeout: float = 30) -> tuple[ScopeView, ...]:
    """Read current metadata; GitHub lifecycle is unknown until a live observation."""
    if specdock_dir.is_symlink() or not specdock_dir.is_dir():
        raise ValueError("SpecDock workspace root is missing or redirected")
    views: list[ScopeView] = []
    for record in load_scope_tree(specdock_dir, target_id=target_id, timeout=timeout):
        metadata = record.metadata
        raw = metadata.raw
        scope_id, kind, title, parent = raw["id"], raw["type"], raw["title"], raw["parent_id"]
        assert isinstance(scope_id, str) and isinstance(kind, str) and isinstance(title, str)
        assert parent is None or isinstance(parent, str)
        path = record.path.resolve(strict=True)
        if not path.is_relative_to(specdock_dir.resolve(strict=True)):
            raise ValueError("Scope path is outside this workspace")
        if isinstance(metadata.backend, LocalBackend):
            lifecycle = metadata.backend.lifecycle
            status = StatusObservation(lifecycle.state, "local", "local", lifecycle.updated_at, None, False)
            github_ref = None
        else:
            status = StatusObservation("unknown", "github", "unknown", None, None, False)
            github_ref = (
                f"gh:{metadata.backend.repo_owner.lower()}/{metadata.backend.repo_name.lower()}"
                f"#{metadata.backend.issue_number}"
            )
        views.append(
            ScopeView(
                id=scope_id,
                kind=cast("ScopeKind", kind),
                title=title,
                parent_id=parent,
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
