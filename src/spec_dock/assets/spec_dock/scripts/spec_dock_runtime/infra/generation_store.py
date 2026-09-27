"""Immutable derived generations with one atomic current-generation pointer."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import TYPE_CHECKING, Literal
from uuid import uuid4

from spec_dock_runtime.infra.json_store import atomic_write_json, read_guarded_json

if TYPE_CHECKING:
    from collections.abc import Mapping

_GENERATION_ID = re.compile(r"[0-9a-f]{32}\Z")


@dataclass(frozen=True)
class Generation:
    id: str
    path: Path
    source: Literal["cache", "github"]
    valid: bool
    selection_revision: int
    warnings: tuple[str, ...]
    files: dict[str, bytes]


def _guard_directory(path: Path) -> None:
    if path.is_symlink() or (path.exists() and not path.is_dir()):
        raise ValueError("generation directory is redirected or invalid")


def _write_exclusive(path: Path, data: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(os.dup(fd), "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        os.close(fd)


def _sync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _paths(specdock_dir: Path) -> tuple[Path, Path]:
    _guard_directory(specdock_dir)
    agent = specdock_dir / ".agent"
    generations = agent / "generations"
    _guard_directory(agent)
    _guard_directory(generations)
    return agent, generations


def load_generation(specdock_dir: Path) -> Generation | None:
    """Read the published generation; an unpointed stage is never current."""
    agent, generations = _paths(specdock_dir)
    pointer = read_guarded_json(agent / "generation.json")
    if pointer is None:
        return None
    payload = pointer[0]
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("generation pointer schema is invalid")
    generation_id = payload.get("generation_id")
    if not isinstance(generation_id, str) or _GENERATION_ID.fullmatch(generation_id) is None:
        raise ValueError("generation pointer ID is invalid")
    directory = generations / generation_id
    _guard_directory(directory)
    if not directory.is_dir():
        raise ValueError("published generation directory is missing")
    loaded = read_guarded_json(directory / "manifest.json")
    if loaded is None or not isinstance(loaded[0], dict):
        raise ValueError("published generation manifest is missing")
    manifest = loaded[0]
    source = manifest.get("source")
    valid = manifest.get("valid")
    revision = manifest.get("selection_revision")
    warnings = manifest.get("warnings")
    file_hashes = manifest.get("files")
    if (
        manifest.get("schema_version") != 1
        or manifest.get("generation_id") != generation_id
        or source not in ("cache", "github")
        or type(valid) is not bool
        or type(revision) is not int
        or revision < 0
        or not isinstance(warnings, list)
        or any(not isinstance(item, str) for item in warnings)
        or not isinstance(file_hashes, dict)
    ):
        raise ValueError("published generation manifest is invalid")
    files: dict[str, bytes] = {}
    for name, digest in file_hashes.items():
        if (
            not isinstance(name, str)
            or Path(name).name != name
            or name in ("", ".", "..", "manifest.json")
            or not isinstance(digest, str)
            or re.fullmatch(r"[0-9a-f]{64}", digest) is None
        ):
            raise ValueError("published generation file record is invalid")
        fd = os.open(directory / name, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            metadata = os.fstat(fd)
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
                raise ValueError("published generation file is not a single-link regular file")
            with os.fdopen(os.dup(fd), "rb") as stream:
                content = stream.read()
        finally:
            os.close(fd)
        if hashlib.sha256(content).hexdigest() != digest:
            raise ValueError("published generation file digest differs")
        files[name] = content
    return Generation(generation_id, directory, source, valid, revision, tuple(warnings), files)


def publish_generation(
    specdock_dir: Path,
    *,
    files: Mapping[str, bytes],
    source: Literal["cache", "github"],
    valid: bool,
    selection_revision: int,
    warnings: tuple[str, ...] = (),
) -> Generation:
    """Publish only after every file and the manifest are durable."""
    if (
        source not in ("cache", "github")
        or type(valid) is not bool
        or type(selection_revision) is not int
        or selection_revision < 0
        or any(not isinstance(item, str) for item in warnings)
    ):
        raise ValueError("generation metadata is invalid")
    if not files:
        raise ValueError("generation requires at least one derived file")
    for name, content in files.items():
        if (
            not isinstance(name, str)
            or Path(name).name != name
            or name in ("", ".", "..", "manifest.json")
            or not isinstance(content, bytes)
        ):
            raise ValueError("generation file name or content is invalid")
    agent, generations = _paths(specdock_dir)
    agent.mkdir(mode=0o700, exist_ok=True)
    generations.mkdir(mode=0o700, exist_ok=True)
    _guard_directory(agent)
    _guard_directory(generations)
    generation_id = uuid4().hex
    directory = generations / generation_id
    directory.mkdir(mode=0o700)
    manifest = {
        "schema_version": 1,
        "generation_id": generation_id,
        "source": source,
        "valid": valid,
        "selection_revision": selection_revision,
        "warnings": list(warnings),
        "files": {name: hashlib.sha256(content).hexdigest() for name, content in sorted(files.items())},
    }
    for name, content in sorted(files.items()):
        _write_exclusive(directory / name, content)
    _write_exclusive(
        directory / "manifest.json",
        (json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode(),
    )
    _sync_directory(directory)
    _sync_directory(generations)
    current_pointer = read_guarded_json(agent / "generation.json")
    atomic_write_json(
        agent / "generation.json",
        {"schema_version": 1, "generation_id": generation_id},
        expected_identity=current_pointer[1] if current_pointer is not None else None,
    )
    return Generation(generation_id, directory, source, valid, selection_revision, warnings, dict(files))
