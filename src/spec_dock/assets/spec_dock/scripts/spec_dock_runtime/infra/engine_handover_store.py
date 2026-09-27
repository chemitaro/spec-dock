"""Durable records for a fixed engine generation handover."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import TYPE_CHECKING
from uuid import uuid4

from spec_dock_runtime.infra.control_store import control_directory
from spec_dock_runtime.infra.json_store import atomic_write_json, read_guarded_json

if TYPE_CHECKING:
    from pathlib import Path

_ID = re.compile(r"[0-9a-f]{32}\Z")
_DIGEST = re.compile(r"[0-9a-f]{64}\Z")


@dataclass(frozen=True)
class EngineHandoverRecord:
    operation_id: str
    common_dir: str
    source_update_id: str
    control_epoch: int
    prior_executable: str
    prior_distribution_root: str
    prior_digest: str
    next_executable: str
    next_distribution_root: str
    next_digest: str
    targets: tuple[str, ...]
    phase: str


def new_engine_handover(
    common_dir: Path,
    *,
    source_update_id: str,
    control_epoch: int,
    prior_executable: str,
    prior_distribution_root: str,
    prior_digest: str,
    next_executable: str,
    next_distribution_root: str,
    next_digest: str,
    targets: tuple[str, ...],
) -> EngineHandoverRecord:
    return EngineHandoverRecord(
        uuid4().hex,
        str(common_dir),
        source_update_id,
        control_epoch,
        prior_executable,
        prior_distribution_root,
        prior_digest,
        next_executable,
        next_distribution_root,
        next_digest,
        targets,
        "prepared",
    )


def _path(common_dir: Path, operation_id: str) -> Path:
    if _ID.fullmatch(operation_id) is None:
        raise ValueError("engine handover operation ID is invalid")
    return control_directory(common_dir) / "engine-handovers" / f"{operation_id}.json"


def write_engine_handover(common_dir: Path, record: EngineHandoverRecord, *, create: bool = False) -> None:
    path = _path(common_dir, record.operation_id)
    previous = read_guarded_json(path)
    if create and previous is not None:
        raise ValueError("engine handover record already exists")
    atomic_write_json(path, asdict(record), expected_identity=previous[1] if previous is not None else None)


def read_engine_handover(common_dir: Path, operation_id: str) -> EngineHandoverRecord:
    loaded = read_guarded_json(_path(common_dir, operation_id))
    if loaded is None or not isinstance(loaded[0], dict):
        raise ValueError("engine handover record is missing")
    payload = loaded[0]
    if (
        payload.get("operation_id") != operation_id
        or payload.get("common_dir") != str(common_dir)
        or _ID.fullmatch(str(payload.get("source_update_id"))) is None
        or type(payload.get("control_epoch")) is not int
        or payload["control_epoch"] < 0
        or any(
            not isinstance(payload.get(key), str) or not payload[key].startswith("/")
            for key in (
                "prior_executable",
                "prior_distribution_root",
                "next_executable",
                "next_distribution_root",
            )
        )
        or any(_DIGEST.fullmatch(str(payload.get(key))) is None for key in ("prior_digest", "next_digest"))
        or not isinstance(payload.get("targets"), list)
        or not payload["targets"]
        or not all(isinstance(item, str) and item for item in payload["targets"])
        or payload.get("phase") not in {"prepared", "committed", "rolling-back", "rolled-back"}
    ):
        raise ValueError("engine handover record is invalid")
    return EngineHandoverRecord(
        operation_id,
        str(common_dir),
        payload["source_update_id"],
        payload["control_epoch"],
        payload["prior_executable"],
        payload["prior_distribution_root"],
        payload["prior_digest"],
        payload["next_executable"],
        payload["next_distribution_root"],
        payload["next_digest"],
        tuple(payload["targets"]),
        payload["phase"],
    )


def pending_engine_handovers(common_dir: Path) -> tuple[str, ...]:
    directory = control_directory(common_dir) / "engine-handovers"
    if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
        raise ValueError("engine handover record directory is unsafe")
    if not directory.exists():
        return ()
    pending: list[str] = []
    for path in sorted(directory.iterdir()):
        if path.name == ".specdock-json-transactions" and path.is_dir() and not path.is_symlink():
            continue
        if path.is_symlink() or not path.is_file() or path.suffix != ".json":
            raise ValueError("engine handover record entry is unsafe")
        record = read_engine_handover(common_dir, path.stem)
        if record.phase not in {"committed", "rolled-back"}:
            pending.append(record.operation_id)
    return tuple(pending)
