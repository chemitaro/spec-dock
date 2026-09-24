"""Create registered operational worktrees from an explicit immutable base."""

from __future__ import annotations

from dataclasses import dataclass, replace
import os
from pathlib import Path
import stat
import subprocess
from typing import TYPE_CHECKING

from spec_dock_runtime.application.branch_vnext import _resolve_commit
from spec_dock_runtime.application.worktree import (
    _close_fd,
    _open_created_exclusive_worktree,
    _open_exclusive_existing_worktree,
    _open_source_directory_for_filesystem_probe,
    _require_same_filesystem,
    _validate_worktree_root,
    _verify_worktree_path_binding,
)
from spec_dock_runtime.cli.admission import admit_writer
from spec_dock_runtime.domain.selectors import (
    WorktreeAliasSelector,
    WorktreeIdSelector,
    WorktreePathSelector,
    parse_worktree_selector,
)
from spec_dock_runtime.infra import git_cli
from spec_dock_runtime.infra.control_store import (
    WORKSPACE_SCHEMA,
    WRITER_PROTOCOL,
    WorktreeRegistration,
    load_control,
    store_control,
)
from spec_dock_runtime.infra.writer_lock import WriterLock

if TYPE_CHECKING:
    from spec_dock_runtime.infra.control_store import ControlState


@dataclass(frozen=True)
class WorktreeCreated:
    id: str
    alias: str | None
    path: Path
    branch: str
    commit: str
    control_epoch: int


@dataclass(frozen=True)
class WorktreeView:
    id: str | None
    alias: str | None
    path: Path
    head: str | None
    branch: str | None
    registered: bool
    locked: bool
    bare: bool
    detached: bool


@dataclass(frozen=True)
class WorktreeRemoved:
    id: str
    path: Path
    branch_deleted: bool
    control_epoch: int


@dataclass(frozen=True)
class WorktreeCreatePreview:
    id: str
    alias: str | None
    path: str
    branch: str
    commit: str


@dataclass(frozen=True)
class WorktreeRemovePreview:
    id: str
    path: str
    branch: str
    locked: bool
    ignored_payload: bool


def list_worktrees(*, repo_root: Path, common_dir: Path) -> tuple[WorktreeView, ...]:
    """Join Git's worktree inventory to the stable control registrations."""
    control = load_control(common_dir)
    if control is None:
        raise ValueError("repository worktree control is unavailable")
    records = git_cli.worktree_list(repo_root)
    if not records or repo_root.resolve(strict=True) not in {record.path.resolve(strict=False) for record in records}:
        raise ValueError("current repository is absent from Git worktree inventory")
    registrations = {item.root: item for item in control.worktrees}
    matched: set[str] = set()
    result: list[WorktreeView] = []
    for record in records:
        registration = registrations.get(str(record.path))
        if registration is not None:
            matched.add(registration.root)
        result.append(
            WorktreeView(
                registration.id if registration is not None else None,
                registration.alias if registration is not None else None,
                record.path,
                record.head,
                record.branch,
                registration is not None and registration.active,
                record.locked,
                record.bare,
                record.detached,
            )
        )
    for registration in control.worktrees:
        if registration.root not in matched:
            result.append(
                WorktreeView(
                    registration.id,
                    registration.alias,
                    Path(registration.root),
                    None,
                    None,
                    False,
                    False,
                    False,
                    False,
                )
            )
    return tuple(sorted(result, key=lambda item: ((item.id or "~"), str(item.path))))


def show_worktree(*, repo_root: Path, common_dir: Path, reference: str) -> WorktreeView:
    """Resolve a stable ID, unique alias, or exact bound path without guessing."""
    selector = parse_worktree_selector(reference)
    inventory = list_worktrees(repo_root=repo_root, common_dir=common_dir)
    if isinstance(selector, WorktreeIdSelector):
        matches = [item for item in inventory if item.id == selector.id]
    elif isinstance(selector, WorktreeAliasSelector):
        matches = [item for item in inventory if item.alias == selector.name]
    else:
        assert isinstance(selector, WorktreePathSelector)
        requested = Path(selector.path)
        if requested.is_symlink() or not requested.is_dir():
            raise LookupError("worktree path is not a registered real directory")
        observed = requested.lstat()
        if not stat.S_ISDIR(observed.st_mode):
            raise LookupError("worktree path is not a registered real directory")
        matches = []
        for item in inventory:
            if item.id is None or item.path.is_symlink() or not item.path.is_dir():
                continue
            bound = item.path.lstat()
            if (bound.st_dev, bound.st_ino) == (observed.st_dev, observed.st_ino):
                matches.append(item)
    if len(matches) != 1 or matches[0].id is None:
        raise LookupError("registered worktree selector is missing or ambiguous")
    return matches[0]


def _validated_name(name: str | None) -> str | None:
    if name is None:
        return None
    if not name or any(char not in "abcdefghijklmnopqrstuvwxyz0123456789-" for char in name):
        raise ValueError("worktree name must use lowercase letters, digits, and hyphens")
    return name


def _worktree_root(root: Path | None) -> Path:
    if root is None:
        configured = os.environ.get("SPEC_DOCK_WORKTREE_ROOT")
        if not configured:
            raise ValueError("worktree root requires --root or SPEC_DOCK_WORKTREE_ROOT")
        root = Path(configured)
    if not root.is_absolute():
        raise ValueError("worktree root must be absolute")
    return _validate_worktree_root(str(root))


def _branch_exists(repo_root: Path, branch: str) -> bool:
    observed = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
        cwd=repo_root,
        capture_output=True,
        check=False,
        timeout=30,
    )
    if observed.returncode not in (0, 1):
        raise RuntimeError("worktree branch inventory could not be read")
    return observed.returncode == 0


def _next_id(repo_root: Path, container: Path, control: ControlState) -> str:
    reserved = {item.id for item in control.worktrees} | {
        item.alias for item in control.worktrees if item.alias is not None
    }
    for number in range(1, 10001):
        stable_id = f"wt{number}"
        branch = f"worktree/{stable_id}"
        path = container / f"{container.name}-{stable_id}"
        if stable_id not in reserved and not os.path.lexists(path) and not _branch_exists(repo_root, branch):
            return stable_id
    raise RuntimeError("worktree stable ID capacity is exhausted")


def _materialize(repo_root: Path, path: Path, commit: str, target_fd: int) -> None:
    witnesses = git_cli.materialize_worktree(repo_root, path=path, target_commit=commit, target_fd=target_fd)
    if git_cli.current_head_or_none(path) != commit:
        raise RuntimeError("created worktree HEAD does not match the fixed base")
    git_cli.require_clean_working_tree(path, allowed_missing_paths=("spec-dock/scripts/spec-dock",))
    git_cli.publish_worktree_entrypoint(
        repo_root, target_fd=target_fd, target_commit=commit, directory_witnesses=witnesses
    )
    if git_cli.current_head_or_none(path) != commit:
        raise RuntimeError("created worktree HEAD changed after entrypoint publication")
    git_cli.require_clean_working_tree(path)


def preview_create_worktree(
    *, repo_root: Path, common_dir: Path, base: str, name: str | None = None, root: Path | None = None
) -> WorktreeCreatePreview:
    alias = _validated_name(name)
    central_root = _worktree_root(root)
    control = load_control(common_dir)
    if control is None or control.mode != "ready":
        raise ValueError("repository worktree control is not ready")
    git_cli.require_clean_working_tree(repo_root)
    commit = _resolve_commit(repo_root, base)
    git_records = git_cli.worktree_list(repo_root)
    if not git_records or repo_root.resolve(strict=True) not in {
        item.path.resolve(strict=True) for item in git_records
    }:
        raise ValueError("source worktree is not registered by Git")
    names = {item.id for item in control.worktrees} | {
        item.alias for item in control.worktrees if item.alias is not None
    }
    if alias is not None and alias in names:
        raise ValueError("worktree name is already registered")
    container = central_root / git_records[0].path.name
    stable_id = _next_id(repo_root, container, control)
    if alias == stable_id:
        raise ValueError("worktree name conflicts with its stable ID")
    return WorktreeCreatePreview(
        stable_id, alias, str(container / f"{container.name}-{stable_id}"), f"worktree/{stable_id}", commit
    )


def create_worktree(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    base: str,
    name: str | None = None,
    root: Path | None = None,
    lock_timeout: float = 0.0,
) -> WorktreeCreated:
    """Create an independent worktree; bootstrap is a separate explicit command."""
    alias = _validated_name(name)
    central_root = _worktree_root(root)
    with WriterLock(common_dir, timeout=lock_timeout):
        control = load_control(common_dir)
        admit_writer(
            control,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
        )
        assert control is not None
        git_cli.require_clean_working_tree(repo_root)
        commit = _resolve_commit(repo_root, base)
        git_records = git_cli.worktree_list(repo_root)
        if not git_records or repo_root.resolve(strict=True) not in {
            item.path.resolve(strict=True) for item in git_records
        }:
            raise ValueError("source worktree is not registered by Git")
        existing_names = {item.id for item in control.worktrees} | {
            item.alias for item in control.worktrees if item.alias is not None
        }
        if alias is not None and alias in existing_names:
            raise ValueError("worktree name is already registered")
        main_root = git_records[0].path
        container = central_root / main_root.name
        stable_id = _next_id(repo_root, container, control)
        if alias == stable_id:
            raise ValueError("worktree name conflicts with its stable ID")
        branch = f"worktree/{stable_id}"
        path = container / f"{container.name}-{stable_id}"
        if (
            subprocess.run(
                ["git", "check-ref-format", "--branch", branch], cwd=repo_root, capture_output=True, check=False
            ).returncode
            != 0
        ):
            raise ValueError("generated worktree branch is invalid")
        container.mkdir(parents=True, exist_ok=True)
        phase = "target-reservation"
        target_fd: int | None = None
        try:
            target_fd = _open_created_exclusive_worktree(path, allow_symlink_at=central_root)
            source_fd = _open_source_directory_for_filesystem_probe(repo_root)
            try:
                _require_same_filesystem(source_fd, target_fd)
            finally:
                _close_fd(source_fd)
            _verify_worktree_path_binding(path, target_fd)
            phase = "git-worktree-add"
            git_cli.add_worktree_at_commit(
                repo_root, path=path, branch=branch, target_commit=commit, target_fd=target_fd
            )
            phase = "materialization"
            _materialize(repo_root, path, commit, target_fd)
            phase = "registration"
            registration = WorktreeRegistration(
                stable_id, str(path), WORKSPACE_SCHEMA, WRITER_PROTOCOL, engine_digest, True, alias
            )
            next_control = replace(control, epoch=control.epoch + 1, worktrees=(*control.worktrees, registration))
            store_control(common_dir, next_control, expected_epoch=control.epoch)
            return WorktreeCreated(stable_id, alias, path, branch, commit, next_control.epoch)
        except Exception as error:
            raise RuntimeError(
                f"worktree create stopped at {phase}; inspect Git worktree, branch, and path before retrying"
            ) from error
        finally:
            _close_fd(target_fd)


def _target_payload_state(path: Path) -> tuple[bool, bool, bool]:
    """Classify tracked changes, untracked entries, and ignored payload separately."""
    observed = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--ignored=matching", "--untracked-files=all"],
        cwd=path,
        capture_output=True,
        check=False,
        timeout=30,
    )
    if observed.returncode != 0:
        raise RuntimeError("target worktree payload could not be classified")
    tracked = False
    untracked = False
    ignored = False
    for item in observed.stdout.split(b"\0"):
        if not item:
            continue
        if len(item) < 4 or item[2:3] != b" ":
            raise RuntimeError("target worktree status is malformed")
        if item[:2] == b"!!":
            ignored = True
        elif item[:2] == b"??":
            untracked = True
        else:
            tracked = True
    return tracked, untracked, ignored


def _discard_ignored_payload(path: Path) -> None:
    cleaned = subprocess.run(["git", "clean", "-fdX", "--"], cwd=path, capture_output=True, check=False, timeout=60)
    if cleaned.returncode != 0:
        raise RuntimeError("ignored payload cleanup failed; inspect the target before retrying")


def preview_remove_worktree(
    *, repo_root: Path, common_dir: Path, reference: str, unlock: bool, discard_ignored: bool
) -> WorktreeRemovePreview:
    target = show_worktree(repo_root=repo_root, common_dir=common_dir, reference=reference)
    git_records = git_cli.worktree_list(repo_root)
    if not target.registered or target.id is None or target.head is None or target.branch is None:
        raise ValueError("target worktree has no active registration and Git record")
    if target.bare or target.detached:
        raise ValueError("bare or detached worktree cannot be removed")
    if target.path == git_records[0].path or target.path.resolve(strict=True) == repo_root.resolve(strict=True):
        raise ValueError("main or current worktree cannot be removed")
    if target.locked and not unlock:
        raise ValueError("locked worktree requires --unlock")
    tracked, untracked, ignored = _target_payload_state(target.path)
    if tracked or untracked:
        raise ValueError("worktree payload prevents removal")
    if ignored and not discard_ignored:
        raise ValueError("ignored worktree payload requires --discard-ignored")
    return WorktreeRemovePreview(target.id, str(target.path), target.branch, target.locked, ignored)


def remove_worktree(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    reference: str,
    unlock: bool = False,
    discard_ignored: bool = False,
    lock_timeout: float = 0.0,
) -> WorktreeRemoved:
    """Remove only a clean registered noncurrent worktree and retain its branch."""
    with WriterLock(common_dir, timeout=lock_timeout):
        control = load_control(common_dir)
        admit_writer(
            control,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
        )
        assert control is not None
        target = show_worktree(repo_root=repo_root, common_dir=common_dir, reference=reference)
        registration = next(item for item in control.worktrees if item.id == target.id)
        git_records = git_cli.worktree_list(repo_root)
        if not target.registered or not registration.active or target.head is None or target.branch is None:
            raise ValueError("target worktree has no active registration and Git record")
        if target.bare or target.detached:
            raise ValueError("bare or detached worktree cannot be removed")
        if target.path == git_records[0].path or target.path.resolve(strict=True) == repo_root.resolve(strict=True):
            raise ValueError("main or current worktree cannot be removed")
        if target.locked and not unlock:
            raise ValueError("locked worktree requires --unlock")
        path = target.path
        target_fd = _open_exclusive_existing_worktree(path)
        try:
            _verify_worktree_path_binding(path, target_fd)
            tracked, untracked, ignored = _target_payload_state(path)
            if tracked:
                raise ValueError("tracked worktree changes prevent removal")
            if untracked:
                raise ValueError("untracked worktree payload prevents removal")
            if ignored and not discard_ignored:
                raise ValueError("ignored worktree payload requires --discard-ignored")
            if target.locked:
                unlocked = subprocess.run(
                    ["git", "worktree", "unlock", str(path)],
                    cwd=repo_root,
                    capture_output=True,
                    check=False,
                    timeout=30,
                )
                if unlocked.returncode != 0:
                    raise RuntimeError("worktree unlock failed; inspect the target before retrying")
            if ignored:
                _discard_ignored_payload(path)
            if any(_target_payload_state(path)):
                raise ValueError("worktree payload changed before removal")
            _verify_worktree_path_binding(path, target_fd)
            git_cli.remove_worktree(repo_root, path=path, force=False, target_fd=target_fd)
            if os.path.lexists(path):
                raise RuntimeError("worktree path remains after Git removal; inspect before retrying")
            if not _branch_exists(repo_root, target.branch):
                raise RuntimeError("worktree branch disappeared unexpectedly")
            retired = replace(registration, active=False)
            next_control = replace(
                control,
                epoch=control.epoch + 1,
                worktrees=tuple(retired if item.id == registration.id else item for item in control.worktrees),
            )
            store_control(common_dir, next_control, expected_epoch=control.epoch)
            return WorktreeRemoved(registration.id, path, False, next_control.epoch)
        finally:
            _close_fd(target_fd)
