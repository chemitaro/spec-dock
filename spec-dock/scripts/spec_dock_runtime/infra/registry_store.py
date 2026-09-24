"""Shared, durable local Scope ID reservations for all linked worktrees."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import re
import subprocess
from typing import TYPE_CHECKING

from spec_dock_runtime.domain.branch_binding import BranchBinding, bind_branch
from spec_dock_runtime.domain.registry import LocalIdRegistry, reserve_local_id
from spec_dock_runtime.domain.selectors import ScopeIdSelector, parse_scope_selector
from spec_dock_runtime.infra.control_store import control_directory, load_control
from spec_dock_runtime.infra.json_store import atomic_write_json, read_guarded_json
from spec_dock_runtime.infra.writer_lock import WriterLock

if TYPE_CHECKING:
    from spec_dock_runtime.domain.selectors import ScopeKind

_HISTORY_LOCAL_ID = re.compile(r"(?:^|/)(?P<id>(?:init|epic|iss)-local-[0-9]+)(?=-|/|$)")
_KIND_ORDER = ("initiative", "epic", "issue")


def _decode_registry(payload: object) -> LocalIdRegistry:
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("invalid registry schema")
    revision = payload.get("revision")
    high_water = payload.get("high_water")
    reserved_ids = payload.get("reserved_ids")
    branches = payload.get("branch_bindings", [])
    deleted_ids = payload.get("deleted_ids", [])
    if (
        type(revision) is not int
        or not isinstance(high_water, dict)
        or set(high_water) != set(_KIND_ORDER)
        or any(type(high_water[kind]) is not int for kind in _KIND_ORDER)
        or not isinstance(reserved_ids, list)
        or not all(isinstance(item, str) for item in reserved_ids)
        or reserved_ids != sorted(set(reserved_ids))
        or not isinstance(branches, list)
        or not isinstance(deleted_ids, list)
        or not all(isinstance(item, str) for item in deleted_ids)
        or deleted_ids != sorted(set(deleted_ids))
        or any(
            not isinstance(binding, dict)
            or set(binding) != {"scope_id", "name", "initial_sha"}
            or any(not isinstance(binding[key], str) for key in ("scope_id", "name", "initial_sha"))
            for binding in branches
        )
    ):
        raise ValueError("invalid registry state")
    return LocalIdRegistry(
        revision,
        tuple(high_water[kind] for kind in _KIND_ORDER),
        frozenset(reserved_ids),
        tuple(BranchBinding(item["scope_id"], item["name"], item["initial_sha"]) for item in branches),
        frozenset(deleted_ids),
    )


def _encode_registry(state: LocalIdRegistry) -> dict[str, object]:
    return {
        "schema_version": 1,
        "revision": state.revision,
        "high_water": dict(zip(_KIND_ORDER, state.high_water, strict=True)),
        "reserved_ids": sorted(state.reserved),
        "deleted_ids": sorted(state.deleted_ids),
        "branch_bindings": [
            {"scope_id": item.scope_id, "name": item.name, "initial_sha": item.initial_sha} for item in state.branches
        ],
    }


def _working_tree_ids(roots: tuple[Path, ...]) -> set[str]:
    observed: set[str] = set()
    for root in roots:
        if not root.is_absolute() or root.is_symlink():
            raise ValueError("registered worktree root is invalid")
        subtree = root / "spec-dock" / "initiatives"
        if not subtree.exists():
            continue
        if subtree.is_symlink():
            raise ValueError("Scope tree must not be a symlink")
        for meta_path in subtree.rglob(".meta.json"):
            loaded = read_guarded_json(meta_path)
            if loaded is None:
                raise ValueError("Scope metadata disappeared during registry scan")
            payload, _identity = loaded
            if not isinstance(payload, dict) or not isinstance(payload.get("id"), str):
                raise ValueError("Scope metadata has no ID")
            selector = parse_scope_selector(payload["id"])
            if not isinstance(selector, ScopeIdSelector) or selector.id != payload["id"]:
                raise ValueError("Scope metadata ID is not canonical")
            observed.add(selector.id)
    return observed


def _historical_local_ids(repo_root: Path) -> set[str]:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "log", "--all", "--name-only", "--format=", "--", "spec-dock/initiatives"],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if completed.returncode != 0:
        raise ValueError("Git history could not be scanned for local Scope IDs")
    result: set[str] = set()
    for path in completed.stdout.splitlines():
        for match in _HISTORY_LOCAL_ID.finditer(path):
            selector = parse_scope_selector(match.group("id"))
            if not isinstance(selector, ScopeIdSelector) or selector.id != match.group("id"):
                raise ValueError("historical local Scope ID is not canonical")
            result.add(selector.id)
    return result


@dataclass(frozen=True)
class RegistryStore:
    common_dir: Path

    @property
    def path(self) -> Path:
        return control_directory(self.common_dir) / "registry.json"

    def load(self) -> tuple[LocalIdRegistry, tuple[int, int] | None]:
        loaded = read_guarded_json(self.path)
        if loaded is None:
            return LocalIdRegistry.empty(), None
        payload, identity = loaded
        return _decode_registry(payload), identity

    def reserve(self, *, kind: ScopeKind, repo_root: Path, timeout: float = 0.0) -> str:
        """Scan all registered worktrees and burn an ID under the shared writer lock."""
        with WriterLock(self.common_dir, timeout=timeout):
            return self.reserve_locked(kind=kind, repo_root=repo_root)

    def reserve_locked(self, *, kind: ScopeKind, repo_root: Path) -> str:
        """Reserve while the caller holds the common writer lock through its operation."""
        control = load_control(self.common_dir)
        if control is None or control.mode != "ready":
            raise ValueError("local ID registry requires ready repository control")
        roots = tuple(Path(item.root) for item in control.worktrees if item.active)
        if repo_root.resolve(strict=True) not in (root.resolve(strict=True) for root in roots):
            raise ValueError("current worktree is not registered")
        state, identity = self.load()
        observed = _working_tree_ids(roots)
        if identity is None:
            observed.update(_historical_local_ids(repo_root))
        next_state, scope_id = reserve_local_id(state, kind=kind, observed_ids=observed)
        atomic_write_json(self.path, _encode_registry(next_state), expected_identity=identity)
        return scope_id

    def bind_locked(self, binding: BranchBinding) -> LocalIdRegistry:
        """Publish a new binding while the caller holds the common writer lock."""
        state, identity = self.load()
        next_state = bind_branch(state, binding)
        if next_state != state:
            atomic_write_json(self.path, _encode_registry(next_state), expected_identity=identity)
        return next_state

    def mark_deleted_locked(self, scope_ids: tuple[str, ...]) -> LocalIdRegistry:
        """Keep tombstones and existing branch bindings when a Scope tree is removed."""
        state, identity = self.load()
        requested = frozenset(scope_ids)
        if not requested:
            raise ValueError("deleted Scope IDs are required")
        for scope_id in requested:
            selector = parse_scope_selector(scope_id)
            if not isinstance(selector, ScopeIdSelector) or selector.id != scope_id:
                raise ValueError("deleted Scope ID is invalid")
        if requested.issubset(state.deleted_ids):
            return state
        next_state = replace(
            state, revision=state.revision + 1,
            deleted_ids=state.deleted_ids | requested,
        )
        atomic_write_json(self.path, _encode_registry(next_state), expected_identity=identity)
        return next_state
