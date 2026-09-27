"""Durable maintenance-to-ready records in one Git common directory."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import TYPE_CHECKING
from uuid import uuid4

from spec_dock_runtime.infra.control_store import control_directory
from spec_dock_runtime.infra.json_store import atomic_write_json, read_guarded_json

_ID = re.compile(r"[0-9a-f]{32}\Z")

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class FinalizationRecord:
    operation_id: str
    common_dir: str
    control_epoch: int
    engine_digest: str
    targets: tuple[str, ...]
    phase: str


def new_finalization(
    common_dir: Path, *, control_epoch: int, engine_digest: str, targets: tuple[str, ...]
) -> FinalizationRecord:
    return FinalizationRecord(uuid4().hex, str(common_dir), control_epoch, engine_digest, targets, "prepared")


def _path(common_dir: Path, operation_id: str) -> Path:
    if _ID.fullmatch(operation_id) is None:
        raise ValueError("finalization operation ID is invalid")
    return control_directory(common_dir) / "finalizations" / f"{operation_id}.json"


def write_finalization(common_dir: Path, record: FinalizationRecord, *, create: bool = False) -> None:
    path = _path(common_dir, record.operation_id)
    previous = read_guarded_json(path)
    if create and previous is not None:
        raise ValueError("finalization record already exists")
    atomic_write_json(path, asdict(record), expected_identity=previous[1] if previous is not None else None)


def read_finalization(common_dir: Path, operation_id: str) -> FinalizationRecord:
    loaded = read_guarded_json(_path(common_dir, operation_id))
    if loaded is None or not isinstance(loaded[0], dict):
        raise ValueError("finalization record is missing")
    payload = loaded[0]
    if (
        payload.get("operation_id") != operation_id
        or payload.get("common_dir") != str(common_dir)
        or not isinstance(payload.get("control_epoch"), int)
        or not isinstance(payload.get("engine_digest"), str)
        or not isinstance(payload.get("targets"), list)
        or not all(isinstance(item, str) for item in payload["targets"])
        or payload.get("phase") not in {"prepared", "committed"}
    ):
        raise ValueError("finalization record is invalid")
    return FinalizationRecord(
        operation_id,
        str(common_dir),
        payload["control_epoch"],
        payload["engine_digest"],
        tuple(payload["targets"]),
        payload["phase"],
    )


def pending_finalizations(common_dir: Path) -> tuple[str, ...]:
    directory = control_directory(common_dir) / "finalizations"
    if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
        raise ValueError("finalization record directory is unsafe")
    if not directory.exists():
        return ()
    pending: list[str] = []
    for path in sorted(directory.iterdir()):
        if path.name == ".specdock-json-transactions" and path.is_dir() and not path.is_symlink():
            continue
        if path.is_symlink() or not path.is_file() or path.suffix != ".json":
            raise ValueError("finalization record entry is unsafe")
        record = read_finalization(common_dir, path.stem)
        if record.phase != "committed":
            pending.append(record.operation_id)
    return tuple(pending)
