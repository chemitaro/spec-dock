from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any

CONTEXT_PACKET_INDEX_PATH = "spec-dock/.agent/context-packets/current-context-packets.json"
CONTEXT_PACKET_DIR = "spec-dock/.agent/context-packets"


@dataclass(frozen=True)
class ContextPacketWriteResult:
    written: bool
    refs: tuple[dict[str, str | None], ...]
    errors: tuple[str, ...] = ()


class ContextPacketStore:
    def __init__(self, repo_root: Path) -> None:
        self._repo_root = Path(repo_root).resolve()

    def write_current(self, payload: dict[str, Any]) -> ContextPacketWriteResult:
        writes = _packet_writes(payload)
        staged: list[tuple[Path, Path]] = []
        backups: list[tuple[Path | None, Path]] = []
        stale_paths: list[Path] = []
        refs: list[dict[str, str | None]] = []
        try:
            write_rel_paths = {rel_path for rel_path, _payload in writes}
            for rel_path, packet_payload in writes:
                path = self._safe_projection_path(rel_path)
                text = json.dumps(packet_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
                staged.append((_stage_text(path, text), path))
                refs.append(
                    {
                        "path": rel_path,
                        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                        "missing_reason": None,
                    }
                )
            for _tmp_path, path in staged:
                backups.append((_backup_existing_path(path), path))
            stale_paths = self._stale_role_packet_paths(write_rel_paths)
            for path in stale_paths:
                backups.append((_backup_existing_path(path), path))
            for tmp_path, path in staged:
                _replace_path(tmp_path, path)
            for path in stale_paths:
                path.unlink(missing_ok=True)
        except OSError as exc:
            _restore_backups(backups)
            for tmp_path, _path in staged:
                tmp_path.unlink(missing_ok=True)
            for backup_path, _path in backups:
                if backup_path is not None:
                    backup_path.unlink(missing_ok=True)
            return ContextPacketWriteResult(written=False, refs=(), errors=(str(exc),))
        for backup_path, _path in backups:
            if backup_path is not None:
                backup_path.unlink(missing_ok=True)
        return ContextPacketWriteResult(written=True, refs=tuple(refs))

    def _safe_projection_path(self, rel_path: str) -> Path:
        path = self._repo_root / rel_path
        resolved_parent = path.parent.resolve()
        if not _is_relative_to(resolved_parent, self._repo_root / CONTEXT_PACKET_DIR):
            raise OSError(f"refusing to write context packet outside ignored state: {rel_path}")
        if path.is_symlink():
            raise OSError(f"refusing to replace symlinked context packet: {rel_path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def _stale_role_packet_paths(self, write_rel_paths: set[str]) -> list[Path]:
        packet_dir = self._repo_root / CONTEXT_PACKET_DIR
        if not packet_dir.exists() or not packet_dir.is_dir():
            return []
        stale = []
        for path in packet_dir.glob("*-packet.json"):
            rel_path = _repo_relative(self._repo_root, path)
            if rel_path not in write_rel_paths:
                stale.append(path)
        return stale


def _packet_writes(payload: dict[str, Any]) -> tuple[tuple[str, dict[str, Any]], ...]:
    packets = payload.get("packets")
    role_writes: list[tuple[str, dict[str, Any]]] = []
    if isinstance(packets, list):
        for packet in packets:
            if not isinstance(packet, dict):
                continue
            role = packet.get("role")
            if not isinstance(role, str) or not role:
                continue
            role_writes.append((f"{CONTEXT_PACKET_DIR}/{role}-packet.json", packet))
    return ((CONTEXT_PACKET_INDEX_PATH, payload), *tuple(role_writes))


def _stage_text(path: Path, text: str) -> Path:
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(text)
            tmp.flush()
            os.fsync(tmp.fileno())
        return tmp_path
    except OSError:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)
        raise


def _backup_existing_path(path: Path) -> Path | None:
    if not path.exists():
        return None
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.backup-",
        suffix=".tmp",
        dir=path.parent,
    )
    os.close(fd)
    backup_path = Path(tmp_name)
    shutil.copy2(path, backup_path)
    return backup_path


def _replace_path(src: Path, dst: Path) -> None:
    src.replace(dst)


def _restore_backups(backups: list[tuple[Path | None, Path]]) -> None:
    for backup_path, path in backups:
        if backup_path is None:
            path.unlink(missing_ok=True)
        elif backup_path.exists():
            backup_path.replace(path)


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()
