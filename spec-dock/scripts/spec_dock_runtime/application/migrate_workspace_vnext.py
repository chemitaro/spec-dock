"""Build an immutable schema-three write set from a fixed legacy inventory."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import TYPE_CHECKING

from spec_dock_runtime.domain.lifecycle import decode_scope_metadata

if TYPE_CHECKING:
    from spec_dock_runtime.infra.migration_store import MigrationInventory, MigrationMap


@dataclass(frozen=True)
class MigrationChange:
    path: str
    before_digest: str | None
    after_bytes: bytes


def _encode(payload: dict[str, object]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _snapshot(path: Path, expected_digest: str | None) -> tuple[dict[str, object] | None, str | None]:
    if path.is_symlink():
        raise ValueError("migration input path is redirected")
    if not path.exists():
        if expected_digest is not None:
            raise ValueError("migration input disappeared after inventory")
        return None, None
    data = path.read_bytes()
    digest = "sha256:" + hashlib.sha256(data).hexdigest()
    if digest != expected_digest:
        raise ValueError("migration input changed after inventory")
    try:
        payload = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("migration input is invalid JSON") from error
    if not isinstance(payload, dict):
        raise ValueError("migration input must be a JSON object")
    return payload, digest


def plan_migration_changes(
    inventory: MigrationInventory, mapping: MigrationMap, *, updated_at: str
) -> tuple[MigrationChange, ...]:
    """Prepare new bytes without changing any consumer file or Git history."""
    if (
        mapping.repository_uid != inventory.repository_uid
        or mapping.source_inventory_digest != inventory.digest
        or not updated_at
    ):
        raise ValueError("migration plan source identity is invalid")
    allowed_blockers = {"BACKEND_MAPPING_REQUIRED", "ACTIVE_REPAIR_REQUIRED", "WORKTREE_UNREGISTERED"}
    if set(inventory.blockers) - allowed_blockers:
        raise ValueError("migration inventory contains unresolved blockers")
    registered = {row["root"]: row["registration_id"] for row in mapping.worktrees}
    backend_overrides = {(row["worktree_id"], row["scope_id"]): row for row in mapping.scope_backend_overrides}
    repairs = {row["worktree_id"] for row in mapping.active_repairs}
    changes: list[MigrationChange] = []
    for worktree in inventory.worktrees:
        worktree_id = worktree.registration_id or registered.get(worktree.root)
        if not isinstance(worktree_id, str) or not worktree_id:
            raise ValueError("migration worktree requires an explicit registration")
        root = Path(worktree.root)
        for scope in worktree.scopes:
            if scope.id is None or scope.kind is None or scope.schema_version not in (1, 3):
                raise ValueError("migration Scope identity or schema is invalid")
            if set(scope.blockers) - {"BACKEND_MAPPING_REQUIRED"}:
                raise ValueError("migration Scope has an unresolved blocker")
            path = root / scope.path / ".meta.json"
            payload, digest = _snapshot(path, scope.digest)
            assert payload is not None
            if scope.schema_version == 3:
                decode_scope_metadata(payload)
                continue
            override = backend_overrides.get((worktree_id, scope.id))
            backend = override["backend"] if override is not None else scope.backend_candidate
            if backend not in ("github", "local"):
                raise ValueError("migration Scope backend needs explicit mapping")
            converted = dict(payload)
            converted.update(schema_version=3, revision=0, backend=backend)
            if backend == "local":
                converted["github"] = None
                converted["lifecycle"] = {"state": "open", "revision": 0, "updated_at": updated_at}
            else:
                if override is not None:
                    converted["github"] = override["github"]
                converted["lifecycle"] = None
            decode_scope_metadata(converted)
            changes.append(MigrationChange(str(path), digest, _encode(converted)))
        active_path = root / "spec-dock/.agent/active.json"
        if worktree.active_digest is not None:
            active, active_digest = _snapshot(active_path, worktree.active_digest)
            assert active is not None
            if "ACTIVE_REPAIR_REQUIRED" in worktree.blockers:
                if worktree_id not in repairs:
                    raise ValueError("migration active repair requires explicit mapping")
                selected: dict[str, object] = dict.fromkeys(("initiative", "epic", "issue"))
                focus = None
            else:
                selected = {role: active.get(role) for role in ("initiative", "epic", "issue")}
                focus = worktree.active_focus
            if active.get("schema_version") != 3 or "ACTIVE_REPAIR_REQUIRED" in worktree.blockers:
                converted_active: dict[str, object] = {
                    "schema_version": 3,
                    "worktree_id": worktree_id,
                    "revision": 0,
                    "focus_id": focus,
                    **selected,
                }
                changes.append(MigrationChange(str(active_path), active_digest, _encode(converted_active)))
        workspace_path = root / "spec-dock/workspace.json"
        workspace, workspace_digest = _snapshot(workspace_path, worktree.workspace_digest)
        if workspace is None:
            workspace = {}
        if worktree.workspace_schema not in (None, 1, 3):
            raise ValueError("migration workspace schema is unsupported")
        converted_workspace = dict(workspace)
        converted_workspace.update(schema_version=3, writer_protocol="specdock.writer/v1")
        if converted_workspace != workspace:
            changes.append(MigrationChange(str(workspace_path), workspace_digest, _encode(converted_workspace)))
    return tuple(changes)
