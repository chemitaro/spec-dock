"""Repository-wide writer compatibility metadata in the Git common directory."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
from typing import Literal
import uuid

ControlMode = Literal["uninitialized", "maintenance", "ready", "recovery-required"]
WRITER_PROTOCOL = "specdock.writer/v1"
WORKSPACE_SCHEMA = 3


@dataclass(frozen=True)
class WorktreeRegistration:
    id: str
    root: str
    schema_version: int
    writer_protocol: str
    engine_digest: str
    active: bool


@dataclass(frozen=True)
class ControlState:
    schema_version: int
    writer_protocol: str
    epoch: int
    engine_digest: str
    mode: ControlMode
    worktrees: tuple[WorktreeRegistration, ...]


def control_directory(common_dir: Path) -> Path:
    if not common_dir.is_absolute():
        raise ValueError("Git common directory must be absolute")
    return common_dir / "spec-dock" / "control"


def decode_control(payload: object) -> ControlState:
    if not isinstance(payload, dict):
        raise ValueError("control must be a JSON object")
    schema = payload.get("schema_version")
    protocol = payload.get("writer_protocol")
    epoch = payload.get("epoch")
    digest = payload.get("engine_digest")
    mode = payload.get("mode")
    items = payload.get("worktrees")
    if not isinstance(schema, int) or isinstance(schema, bool):
        raise ValueError("invalid control schema_version")
    if not isinstance(protocol, str) or not protocol:
        raise ValueError("invalid control writer_protocol")
    if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 0:
        raise ValueError("invalid control epoch")
    if not isinstance(digest, str) or not digest:
        raise ValueError("invalid control engine_digest")
    if mode not in ("uninitialized", "maintenance", "ready", "recovery-required"):
        raise ValueError("invalid control mode")
    if not isinstance(items, list):
        raise ValueError("invalid control worktree inventory")
    worktrees: list[WorktreeRegistration] = []
    seen_ids: set[str] = set()
    seen_roots: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("invalid worktree registration")
        worktree_id = item.get("id")
        root = item.get("root")
        item_schema = item.get("schema_version")
        item_protocol = item.get("writer_protocol")
        item_digest = item.get("engine_digest")
        active = item.get("active")
        if (
            not isinstance(worktree_id, str)
            or not worktree_id
            or not isinstance(root, str)
            or not Path(root).is_absolute()
            or not isinstance(item_schema, int)
            or isinstance(item_schema, bool)
            or not isinstance(item_protocol, str)
            or not item_protocol
            or not isinstance(item_digest, str)
            or not item_digest
            or not isinstance(active, bool)
        ):
            raise ValueError("invalid worktree registration")
        if worktree_id in seen_ids or root in seen_roots:
            raise ValueError("duplicate worktree registration")
        seen_ids.add(worktree_id)
        seen_roots.add(root)
        worktrees.append(WorktreeRegistration(worktree_id, root, item_schema, item_protocol, item_digest, active))
    return ControlState(schema, protocol, epoch, digest, mode, tuple(worktrees))


def load_control(common_dir: Path) -> ControlState | None:
    path = control_directory(common_dir) / "control.json"
    if path.is_symlink():
        raise ValueError("control JSON must not be a symlink")
    try:
        data = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    try:
        return decode_control(json.loads(data))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("invalid control JSON") from exc


def store_control(common_dir: Path, state: ControlState, *, expected_epoch: int | None) -> None:
    """Publish control under the common writer lock after an epoch check."""
    directory = control_directory(common_dir)
    for item in (common_dir / "spec-dock", directory):
        item.mkdir(mode=0o700, exist_ok=True)
        if item.is_symlink():
            raise ValueError("control directory must not be a symlink")
    current = load_control(common_dir)
    if expected_epoch is None:
        if current is not None:
            raise ValueError("control epoch already exists")
    elif current is None or current.epoch != expected_epoch or state.epoch != expected_epoch + 1:
        raise ValueError("control epoch changed")
    path = directory / "control.json"
    staged = directory / f".control-{uuid.uuid4().hex}.tmp"
    payload = (json.dumps(asdict(state), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
    fd = os.open(staged, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        staged.replace(path)
        dir_fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        staged.unlink(missing_ok=True)
