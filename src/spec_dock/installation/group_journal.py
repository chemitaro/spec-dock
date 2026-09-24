"""Shared installation transaction record for a fixed Git worktree group."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import uuid

_ID = re.compile(r"[0-9a-f]{32}\Z")
_SHA = re.compile(r"[0-9a-f]{40}\Z")
_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_PHASES = {"preparing", "staged", "applying", "recovery-required", "committed", "rolled-back"}


@dataclass(frozen=True)
class InstallationTarget:
    worktree_id: str
    root: str
    child_operation_id: str | None
    completed: bool


@dataclass(frozen=True)
class InstallationGroupRecord:
    operation_id: str
    action: str
    common_dir: str
    control_epoch: int
    engine_digest: str
    source_commit: str | None
    source_digest: str | None
    keep_maintenance: bool
    targets: tuple[InstallationTarget, ...]
    phase: str
    error: str | None = None
    bootstrap: bool = False


def child_operation_id(group_id: str, worktree_id: str) -> str:
    """Derive a stable child ID so recovery can locate a stage after a crash."""
    if (
        not isinstance(group_id, str)
        or _ID.fullmatch(group_id) is None
        or not isinstance(worktree_id, str)
        or re.fullmatch(r"[a-z0-9][a-z0-9._-]*", worktree_id) is None
    ):
        raise ValueError("invalid installation child identity")
    return hashlib.sha256(f"{group_id}:{worktree_id}".encode()).hexdigest()[:32]


def _directory(common_dir: Path, operation_id: str) -> Path:
    if not common_dir.is_absolute() or _ID.fullmatch(operation_id) is None:
        raise ValueError("invalid installation group location")
    directory = common_dir / "spec-dock" / "control" / "installations" / operation_id
    if any(path.is_symlink() for path in (directory, *directory.parents)):
        raise ValueError("installation group location is redirected")
    return directory


def _validate(record: InstallationGroupRecord) -> None:
    if (
        not isinstance(record.operation_id, str)
        or _ID.fullmatch(record.operation_id) is None
        or record.action not in {"init", "update", "uninstall"}
        or record.phase not in _PHASES
        or not isinstance(record.common_dir, str)
        or not Path(record.common_dir).is_absolute()
        or type(record.control_epoch) is not int
        or record.control_epoch < 0
        or not isinstance(record.engine_digest, str)
        or _DIGEST.fullmatch(record.engine_digest) is None
        or (
            record.source_commit is not None
            and (not isinstance(record.source_commit, str) or _SHA.fullmatch(record.source_commit) is None)
        )
        or (
            record.source_digest is not None
            and (not isinstance(record.source_digest, str) or _DIGEST.fullmatch(record.source_digest) is None)
        )
        or (record.action == "uninstall" and (record.source_commit is not None or record.source_digest is not None))
        or (record.action == "update" and (record.source_commit is None or record.source_digest is None))
        or (record.action == "init" and record.source_digest is None)
        or type(record.keep_maintenance) is not bool
        or not isinstance(record.targets, tuple)
        or not record.targets
        or (record.error is not None and not isinstance(record.error, str))
        or type(record.bootstrap) is not bool
    ):
        raise ValueError("invalid installation group record")
    identifiers: set[str] = set()
    roots: set[str] = set()
    child_ids: set[str] = set()
    for target in record.targets:
        if (
            not isinstance(target.worktree_id, str)
            or re.fullmatch(r"[a-z0-9][a-z0-9._-]*", target.worktree_id) is None
            or not isinstance(target.root, str)
            or not Path(target.root).is_absolute()
            or (
                target.child_operation_id is not None
                and (not isinstance(target.child_operation_id, str) or _ID.fullmatch(target.child_operation_id) is None)
            )
            or type(target.completed) is not bool
            or (target.completed and target.child_operation_id is None)
            or target.worktree_id in identifiers
            or target.root in roots
            or (target.child_operation_id is not None and target.child_operation_id in child_ids)
        ):
            raise ValueError("invalid installation group target")
        identifiers.add(target.worktree_id)
        roots.add(target.root)
        if target.child_operation_id is not None:
            child_ids.add(target.child_operation_id)
    if tuple(sorted(identifiers)) != tuple(target.worktree_id for target in record.targets):
        raise ValueError("installation group targets must be sorted")
    if record.phase == "committed" and any(not target.completed for target in record.targets):
        raise ValueError("committed installation group has incomplete targets")
    if record.phase in {"staged", "applying", "committed"} and any(
        target.child_operation_id is None for target in record.targets
    ):
        raise ValueError("installation group has unstaged targets")


def read_group_record(common_dir: Path, operation_id: str) -> InstallationGroupRecord:
    path = _directory(common_dir, operation_id) / "group.json"
    if path.is_symlink():
        raise ValueError("installation group journal is redirected")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("installation group journal is missing or invalid") from error
    if not isinstance(payload, dict) or not isinstance(payload.get("targets"), list):
        raise ValueError("installation group journal shape is invalid")
    try:
        targets = tuple(InstallationTarget(**item) for item in payload.pop("targets"))
        record = InstallationGroupRecord(targets=targets, **payload)
    except (TypeError, AttributeError) as error:
        raise ValueError("installation group journal shape is invalid") from error
    _validate(record)
    if record.operation_id != operation_id or record.common_dir != str(common_dir):
        raise ValueError("installation group journal identity differs")
    return record


def write_group_record(common_dir: Path, record: InstallationGroupRecord, *, create: bool = False) -> None:
    _validate(record)
    if record.common_dir != str(common_dir):
        raise ValueError("installation group common directory differs")
    directory = _directory(common_dir, record.operation_id)
    if create:
        directory.mkdir(mode=0o700, parents=True, exist_ok=False)
    elif not directory.is_dir():
        raise ValueError("installation group journal directory is missing")
    path = directory / "group.json"
    if path.is_symlink():
        raise ValueError("installation group journal is redirected")
    staged = directory / f".group-{uuid.uuid4().hex}.tmp"
    payload = (json.dumps(asdict(record), sort_keys=True, separators=(",", ":")) + "\n").encode()
    descriptor = os.open(staged, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        staged.replace(path)
        directory_fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        staged.unlink(missing_ok=True)
