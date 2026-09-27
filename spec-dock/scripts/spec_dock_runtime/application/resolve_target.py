"""Resolve command targets against one loaded Scope and selection snapshot."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING

from spec_dock_runtime.domain.selectors import (
    ActiveScopeSelector,
    ScopeIdSelector,
    ScopeSelector,
    WorktreeAliasSelector,
    WorktreeIdSelector,
    WorktreePathSelector,
    WorktreeSelector,
    parse_scope_selector,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from spec_dock_runtime.domain.lifecycle import SelectionState
    from spec_dock_runtime.domain.models import SpecNode, SpecNodeKind


@dataclass(frozen=True)
class ScopeSnapshot:
    nodes: Mapping[str, SpecNode]
    selection: SelectionState
    repository: tuple[str, str] | None

    def __post_init__(self) -> None:
        for node_id, node in self.nodes.items():
            try:
                selector = parse_scope_selector(node_id)
            except ValueError as exc:
                raise ValueError("snapshot contains an invalid Scope ID") from exc
            if not isinstance(selector, ScopeIdSelector) or selector.id != node_id or node.id != node_id:
                raise ValueError("snapshot contains a noncanonical Scope ID")
            if selector.kind != node.kind:
                raise ValueError("snapshot Scope ID kind disagrees with node kind")
        object.__setattr__(self, "nodes", MappingProxyType(dict(self.nodes)))
        if self.repository is not None:
            object.__setattr__(self, "repository", tuple(part.lower() for part in self.repository))


@dataclass(frozen=True)
class WorktreeRecord:
    id: str
    path: Path
    alias: str | None


def resolve_worktree_target(records: tuple[WorktreeRecord, ...], selector: WorktreeSelector) -> WorktreeRecord:
    """Match an explicit selector to one registry entry, never an arbitrary directory."""
    if isinstance(selector, WorktreeIdSelector):
        matches = [record for record in records if record.id == selector.id]
    elif isinstance(selector, WorktreeAliasSelector):
        matches = [record for record in records if record.alias == selector.name]
    elif isinstance(selector, WorktreePathSelector):
        target_path = Path(selector.path).resolve(strict=True)
        matches = [record for record in records if record.path.resolve(strict=True) == target_path]
    else:
        raise TypeError("unsupported worktree selector")
    if not matches:
        raise LookupError("worktree is not registered")
    if len(matches) != 1:
        raise ValueError("ambiguous worktree selector")
    return matches[0]


def _selected_id(selection: SelectionState, role: str) -> str | None:
    if role == "current":
        return selection.focus_id
    if role == "initiative":
        return selection.initiative_id
    if role == "epic":
        return selection.epic_id
    return selection.issue_id


def _assert_selection_integrity(snapshot: ScopeSnapshot) -> None:
    selection = snapshot.selection
    for role in ("initiative", "epic", "issue"):
        scope_id = _selected_id(selection, role)
        if scope_id is None:
            continue
        node = snapshot.nodes.get(scope_id)
        if node is None or node.kind != role:
            raise ValueError("selection references a missing or wrong-kind Scope")
        expected_parent = {"initiative": None, "epic": selection.initiative_id, "issue": selection.epic_id}[role]
        if node.parent_id != expected_parent:
            raise ValueError("selection chain has an invalid parent")


def _resolve_one(snapshot: ScopeSnapshot, selector: ScopeSelector) -> SpecNode:
    if isinstance(selector, ActiveScopeSelector):
        scope_id = _selected_id(snapshot.selection, selector.role)
        if scope_id is None:
            raise LookupError(f"no selected {selector.role} Scope")
        node = snapshot.nodes.get(scope_id)
        if node is None:
            raise ValueError("selection references a missing Scope")
        return node
    if isinstance(selector, ScopeIdSelector):
        node = snapshot.nodes.get(selector.id)
        if node is None:
            raise LookupError(f"Scope {selector.id} was not found")
        if node.kind != selector.kind:
            raise ValueError("Scope ID kind disagrees with stored kind")
        return node
    if snapshot.repository is None:
        raise ValueError("GitHub Scope selector requires a known project repository")
    if (selector.owner, selector.repo) != snapshot.repository:
        raise ValueError("foreign GitHub repository is not a Scope selector for this project")
    matches = [
        node
        for node in snapshot.nodes.values()
        if node.github_issue_number == selector.issue_number
        and (str(node.github_repo_owner).lower(), str(node.github_repo_name).lower()) == snapshot.repository
    ]
    if not matches:
        raise LookupError("GitHub Issue has not been imported as a Scope")
    if len(matches) != 1:
        raise ValueError("ambiguous GitHub Issue link; multiple Scopes match")
    return matches[0]


def resolve_scope_targets(
    snapshot: ScopeSnapshot,
    selectors: Mapping[str, ScopeSelector],
    *,
    expected_kinds: Mapping[str, SpecNodeKind] | None = None,
    expected_parents: Mapping[str, str | None] | None = None,
    expected_current: str | None = None,
    require_current_guard: bool = False,
) -> Mapping[str, SpecNode]:
    """Fix every role from one snapshot before a command performs effects."""
    uses_selection = any(isinstance(selector, ActiveScopeSelector) for selector in selectors.values())
    if uses_selection:
        _assert_selection_integrity(snapshot)
        if require_current_guard and expected_current is None:
            raise ValueError("--expect-current is required for a non-interactive active selector mutation")
        if expected_current is not None:
            parsed_expected = parse_scope_selector(expected_current)
            if not isinstance(parsed_expected, ScopeIdSelector):
                raise ValueError("--expect-current requires a complete Scope ID")
            if parsed_expected.id != snapshot.selection.focus_id:
                raise ValueError("current Scope changed since the expected selection")
    resolved: dict[str, SpecNode] = {}
    for role, selector in selectors.items():
        node = _resolve_one(snapshot, selector)
        if expected_kinds is not None and role in expected_kinds and node.kind != expected_kinds[role]:
            raise ValueError(f"{role} kind must be {expected_kinds[role]}")
        if expected_parents is not None and role in expected_parents and node.parent_id != expected_parents[role]:
            raise ValueError(f"{role} parent does not match the required Scope")
        resolved[role] = node
    return MappingProxyType(resolved)


def resolve_project_root(
    cwd: Path,
    *,
    git_root: Callable[[Path], Path | None],
    explicit_project: Path | None = None,
    shim_root: Path | None = None,
) -> Path:
    """Resolve a Scope command's local project without guessing another checkout."""
    actual_cwd = cwd.resolve(strict=True)
    selected = explicit_project.resolve(strict=True) if explicit_project is not None else actual_cwd
    if not selected.is_dir():
        raise ValueError("project path must be a directory")
    if shim_root is not None and explicit_project is not None and selected != shim_root.resolve(strict=True):
        raise ValueError("--project conflicts with the repository-local shim")
    root = git_root(selected)
    if root is None:
        raise ValueError("Scope operations require a Git worktree")
    canonical_root = root.resolve(strict=True)
    if explicit_project is not None and selected != canonical_root:
        raise ValueError("--project must name the Git worktree root")
    if explicit_project is None and not actual_cwd.is_relative_to(canonical_root):
        raise ValueError("Git root does not contain the current directory")
    if shim_root is not None and canonical_root != shim_root.resolve(strict=True):
        raise ValueError("resolved Git root conflicts with the repository-local shim")
    return canonical_root
