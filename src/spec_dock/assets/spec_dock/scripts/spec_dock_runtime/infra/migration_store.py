"""Read-only legacy workspace inventory for an explicit schema-three migration."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path

from spec_dock_runtime.domain.lifecycle import decode_scope_metadata
from spec_dock_runtime.domain.selectors import ScopeIdSelector, parse_scope_selector
from spec_dock_runtime.infra.control_store import control_directory, load_control
from spec_dock_runtime.infra.git_cli import git_common_directory, origin_github_repo_slug, worktree_list


@dataclass(frozen=True)
class MigrationScope:
    path: str
    digest: str
    id: str | None
    kind: str | None
    schema_version: int | None
    backend_candidate: str | None
    parent_id: str | None
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class MigrationWorktree:
    root: str
    registration_id: str | None
    branch: str | None
    head: str | None
    workspace_schema: int | None
    workspace_digest: str | None
    active_digest: str | None
    active_focus: str | None
    scopes: tuple[MigrationScope, ...]
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class MigrationInventory:
    common_dir: str
    repository_uid: str
    control_digest: str | None
    digest: str
    worktrees: tuple[MigrationWorktree, ...]
    blockers: tuple[str, ...]


def _digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _read_json(path: Path) -> tuple[object, str]:
    if path.is_symlink():
        raise ValueError(f"migration input is a symlink: {path}")
    data = path.read_bytes()
    try:
        return json.loads(data.decode("utf-8")), _digest(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"migration input is not valid UTF-8 JSON: {path}") from error


def _metadata_paths(root: Path) -> tuple[Path, ...]:
    tree = root / "spec-dock" / "initiatives"
    if not tree.exists():
        return ()
    if tree.is_symlink() or not tree.is_dir():
        raise ValueError("migration Scope tree is not a real directory")
    paths: list[Path] = []
    for current, directories, files in os.walk(tree, followlinks=False):
        current_path = Path(current)
        if any((current_path / name).is_symlink() for name in (*directories, *files)):
            raise ValueError("migration Scope tree contains a symlink")
        if ".meta.json" in files:
            paths.append(current_path / ".meta.json")
    return tuple(sorted(paths))


def _classify_scope(path: Path, root: Path, repository: str | None) -> MigrationScope:
    relative = path.parent.relative_to(root).as_posix()
    try:
        payload, digest = _read_json(path)
    except (OSError, ValueError):
        return MigrationScope(relative, "unreadable", None, None, None, None, None, ("METADATA_UNREADABLE",))
    if not isinstance(payload, dict):
        return MigrationScope(relative, digest, None, None, None, None, None, ("METADATA_SHAPE_UNKNOWN",))
    scope_id = payload.get("id")
    kind = payload.get("type")
    schema = payload.get("schema_version")
    parent_id = payload.get("parent_id")
    blockers: list[str] = []
    if not isinstance(scope_id, str) or not isinstance(kind, str):
        blockers.append("METADATA_ID_INVALID")
    else:
        try:
            selector = parse_scope_selector(scope_id)
        except ValueError:
            selector = None
        if not isinstance(selector, ScopeIdSelector) or selector.id != scope_id or selector.kind != kind:
            blockers.append("METADATA_ID_INVALID")
    if parent_id is not None and not isinstance(parent_id, str):
        blockers.append("METADATA_PARENT_INVALID")
    candidate: str | None = None
    if schema == 3:
        try:
            candidate = decode_scope_metadata(payload).backend.kind
        except ValueError:
            blockers.append("METADATA_SHAPE_UNKNOWN")
    elif schema == 1:
        github = payload.get("github")
        if github is None and isinstance(scope_id, str) and "-local-" in scope_id:
            candidate = "local"
        elif isinstance(github, dict):
            number = github.get("issue_number")
            owner = github.get("repo_owner")
            repo_name = github.get("repo_name")
            if (
                type(number) is int
                and number > 0
                and isinstance(owner, str)
                and isinstance(repo_name, str)
                and repository == f"{owner.lower()}/{repo_name.lower()}"
            ):
                candidate = "github"
            else:
                blockers.append("BACKEND_MAPPING_REQUIRED")
        else:
            blockers.append("BACKEND_MAPPING_REQUIRED")
    else:
        blockers.append("METADATA_SHAPE_UNKNOWN")
    return MigrationScope(
        relative,
        digest,
        scope_id if isinstance(scope_id, str) else None,
        kind if isinstance(kind, str) else None,
        schema if type(schema) is int else None,
        candidate,
        parent_id if isinstance(parent_id, str) else None,
        tuple(sorted(set(blockers))),
    )


def _active_focus(root: Path, scopes: tuple[MigrationScope, ...]) -> tuple[str | None, str | None, tuple[str, ...]]:
    path = root / "spec-dock/.agent/active.json"
    if not path.exists() and not path.is_symlink():
        return None, None, ()
    try:
        payload, digest = _read_json(path)
    except (OSError, ValueError):
        return None, "unreadable", ("ACTIVE_REPAIR_REQUIRED",)
    if not isinstance(payload, dict) or payload.get("schema_version") not in (2, 3):
        return None, digest, ("ACTIVE_REPAIR_REQUIRED",)
    by_id = {scope.id: scope for scope in scopes if scope.id is not None}
    selected: list[str] = []
    for role in ("initiative", "epic", "issue"):
        entry = payload.get(role)
        if entry is None:
            continue
        if (
            not isinstance(entry, dict)
            or not isinstance(entry.get("id"), str)
            or not isinstance(entry.get("path"), str)
        ):
            return None, digest, ("ACTIVE_REPAIR_REQUIRED",)
        scope = by_id.get(entry["id"])
        if scope is None or scope.id is None or scope.kind != role or scope.path != entry["path"]:
            return None, digest, ("ACTIVE_REPAIR_REQUIRED",)
        if role == "epic" and (not selected or scope.parent_id != selected[-1]):
            return None, digest, ("ACTIVE_REPAIR_REQUIRED",)
        if role == "issue" and (len(selected) != 2 or scope.parent_id != selected[-1]):
            return None, digest, ("ACTIVE_REPAIR_REQUIRED",)
        selected.append(scope.id)
    focus = selected[-1] if selected else None
    if payload.get("schema_version") == 3 and payload.get("focus_id") != focus:
        return None, digest, ("ACTIVE_REPAIR_REQUIRED",)
    return focus, digest, ()


def _inspect_worktree(
    root: Path, registration_id: str | None, branch: str | None, head: str | None, repository: str | None
) -> MigrationWorktree:
    specdock_dir = root / "spec-dock"
    workspace = specdock_dir / "workspace.json"
    workspace_schema: int | None = None
    workspace_digest: str | None = None
    blockers: list[str] = []
    if workspace.exists() or workspace.is_symlink():
        try:
            payload, workspace_digest = _read_json(workspace)
            schema = payload.get("schema_version") if isinstance(payload, dict) else None
            if type(schema) is int:
                workspace_schema = schema
            else:
                blockers.append("WORKSPACE_SHAPE_UNKNOWN")
        except (OSError, ValueError):
            blockers.append("WORKSPACE_SHAPE_UNKNOWN")
    try:
        scopes = tuple(_classify_scope(path, root, repository) for path in _metadata_paths(root))
    except (OSError, ValueError):
        scopes = ()
        blockers.append("SCOPE_TREE_UNREADABLE")
    by_id = {scope.id: scope for scope in scopes if scope.id is not None}
    if len(by_id) != len([scope for scope in scopes if scope.id is not None]):
        blockers.append("DUPLICATE_SCOPE_ID")
    for scope in scopes:
        blockers.extend(scope.blockers)
        if scope.parent_id is not None and scope.parent_id not in by_id:
            blockers.append("SCOPE_PARENT_MISSING")
    focus, active_digest, active_blockers = _active_focus(root, scopes)
    blockers.extend(active_blockers)
    return MigrationWorktree(
        str(root),
        registration_id,
        branch,
        head,
        workspace_schema,
        workspace_digest,
        active_digest,
        focus,
        scopes,
        tuple(sorted(set(blockers))),
    )


def inspect_migration_inventory(repo_root: Path) -> MigrationInventory:
    """Inventory every Git worktree without converting or writing any consumer bytes."""
    root = repo_root.resolve(strict=True)
    common_dir = git_common_directory(root)
    try:
        repository = origin_github_repo_slug(root)
    except RuntimeError:
        repository = None
    records = worktree_list(root)
    if not records:
        raise ValueError("Git worktree inventory is empty")
    blockers: list[str] = []
    worktrees: list[MigrationWorktree] = []
    control_path = control_directory(common_dir) / "control.json"
    control_digest: str | None = None
    if control_path.exists() or control_path.is_symlink():
        if control_path.is_symlink() or control_path.parent.is_symlink():
            blockers.append("CONTROL_UNREADABLE")
        else:
            try:
                control_digest = _digest(control_path.read_bytes())
            except OSError:
                blockers.append("CONTROL_UNREADABLE")
    try:
        control = load_control(common_dir)
    except ValueError:
        control = None
        blockers.append("CONTROL_UNREADABLE")
    registrations = (
        {str(Path(item.root).resolve(strict=False)): item.id for item in control.worktrees if item.active}
        if control is not None
        else {}
    )
    observed_roots: set[str] = set()
    for record in sorted(records, key=lambda item: str(item.path)):
        candidate = record.path
        if record.bare or not candidate.is_dir() or candidate.is_symlink():
            blockers.append("WORKTREE_UNAVAILABLE")
            continue
        canonical = candidate.resolve(strict=True)
        observed_roots.add(str(canonical))
        registration_id = registrations.get(str(canonical))
        if control is not None and registration_id is None:
            blockers.append("WORKTREE_UNREGISTERED")
        worktree = _inspect_worktree(canonical, registration_id, record.branch, record.head, repository)
        worktrees.append(worktree)
        blockers.extend(worktree.blockers)
    if control is not None and set(registrations) - observed_roots:
        blockers.append("CONTROL_WORKTREE_MISSING")
    uid = _digest(str(common_dir).encode())
    encoded = json.dumps(
        {
            "repository_uid": uid,
            "control_digest": control_digest,
            "worktrees": [asdict(worktree) for worktree in worktrees],
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return MigrationInventory(
        str(common_dir), uid, control_digest, _digest(encoded), tuple(worktrees), tuple(sorted(set(blockers)))
    )
