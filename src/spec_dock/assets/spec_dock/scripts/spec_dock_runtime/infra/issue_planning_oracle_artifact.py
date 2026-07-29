"""Versioned, private Oracle 0.16.1 session artifact reader."""

from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Any
import zipfile

from spec_dock_runtime.domain.issue_planning_contracts import (
    OracleAuthoringZipSnapshot,
    OracleReviewJsonPayload,
)

SUPPORTED_ORACLE_VERSION = "0.16.1"
MAX_METADATA_BYTES = 1024 * 1024
MAX_ARTIFACTS = 32
MAX_ARTIFACT_BYTES = 64 * 1024 * 1024
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_TRANSPORT_ZIP_RE = re.compile(r"^(?P<stem>.+?)(?: \([1-9][0-9]*\))?\.zip$")
_ANSWER_MARKER = b"\n## Answer\n"


class OracleArtifactError(RuntimeError):
    """Content-free error for the direct Oracle adapter."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def read_session_status(
    session_root: Path,
    *,
    session_id: str,
    oracle_version: str,
) -> str:
    metadata = _read_metadata(session_root, session_id=session_id, oracle_version=oracle_version)
    status_value = metadata.get("status")
    if not isinstance(status_value, str) or not status_value:
        raise OracleArtifactError("oracle_artifact_rejected")
    return status_value


def snapshot_authoring_zip(
    session_root: Path,
    *,
    session_id: str,
    oracle_version: str,
    staging_dir: Path,
) -> OracleAuthoringZipSnapshot:
    metadata = _read_metadata(session_root, session_id=session_id, oracle_version=oracle_version)
    artifacts = _artifact_inventory(metadata)
    matches = [
        artifact
        for artifact in artifacts
        if artifact.get("kind") == "file"
        and isinstance(artifact.get("path"), str)
        and _TRANSPORT_ZIP_RE.fullmatch(Path(artifact["path"]).name)
    ]
    if not matches:
        raise OracleArtifactError("oracle_artifact_missing")
    if len(matches) != 1:
        raise OracleArtifactError("oracle_artifact_ambiguous")
    artifact = matches[0]
    payload = _snapshot_artifact(
        session_root,
        artifact=artifact,
        staging_dir=staging_dir,
    )
    observed = Path(str(artifact["path"])).name
    match = _TRANSPORT_ZIP_RE.fullmatch(observed)
    if match is None:
        raise OracleArtifactError("oracle_artifact_rejected")
    expected = f"{match.group('stem')}.zip"
    internal_root = _zip_internal_root(payload)
    return OracleAuthoringZipSnapshot(
        expected_logical_filename=expected,
        observed_transport_filename=observed,
        internal_root=internal_root,
        size_bytes=len(payload),
        sha256=hashlib.sha256(payload).hexdigest(),
        zip_bytes=payload,
    )


def snapshot_review_json(
    session_root: Path,
    *,
    session_id: str,
    oracle_version: str,
    staging_dir: Path,
) -> OracleReviewJsonPayload:
    metadata = _read_metadata(session_root, session_id=session_id, oracle_version=oracle_version)
    artifacts = _artifact_inventory(metadata)
    matches = [artifact for artifact in artifacts if artifact.get("kind") == "transcript"]
    if not matches:
        raise OracleArtifactError("oracle_artifact_missing")
    if len(matches) != 1:
        raise OracleArtifactError("oracle_artifact_ambiguous")
    transcript = _snapshot_artifact(
        session_root,
        artifact=matches[0],
        staging_dir=staging_dir,
    )
    marker_index = transcript.find(_ANSWER_MARKER)
    if marker_index < 0 or transcript.find(_ANSWER_MARKER, marker_index + 1) >= 0:
        raise OracleArtifactError("oracle_artifact_rejected")
    payload = transcript[marker_index + len(_ANSWER_MARKER) :].strip()
    if not payload:
        raise OracleArtifactError("oracle_artifact_rejected")
    try:
        parsed = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OracleArtifactError("oracle_artifact_rejected") from error
    if not isinstance(parsed, dict):
        raise OracleArtifactError("oracle_artifact_rejected")
    return OracleReviewJsonPayload(
        size_bytes=len(payload),
        sha256=hashlib.sha256(payload).hexdigest(),
        json_bytes=payload,
    )


def _read_metadata(
    session_root: Path,
    *,
    session_id: str,
    oracle_version: str,
) -> dict[str, Any]:
    if oracle_version != SUPPORTED_ORACLE_VERSION:
        raise OracleArtifactError("oracle_artifact_rejected")
    if session_root.name != session_id:
        raise OracleArtifactError("oracle_artifact_rejected")
    raw = _read_bounded_regular_file(session_root / "meta.json", MAX_METADATA_BYTES)
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OracleArtifactError("oracle_artifact_rejected") from error
    if not isinstance(value, dict) or value.get("id") != session_id:
        raise OracleArtifactError("oracle_artifact_rejected")
    if value.get("mode") != "browser":
        raise OracleArtifactError("oracle_artifact_rejected")
    return value


def _artifact_inventory(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    value = metadata.get("artifacts")
    if not isinstance(value, list) or len(value) > MAX_ARTIFACTS:
        raise OracleArtifactError("oracle_artifact_rejected")
    if not all(isinstance(item, dict) for item in value):
        raise OracleArtifactError("oracle_artifact_rejected")
    return value


def _snapshot_artifact(
    session_root: Path,
    *,
    artifact: dict[str, Any],
    staging_dir: Path,
) -> bytes:
    raw_path = artifact.get("path")
    size_bytes = artifact.get("sizeBytes")
    expected_sha = artifact.get("sha256")
    validation = artifact.get("validation")
    if (
        not isinstance(raw_path, str)
        or not isinstance(size_bytes, int)
        or isinstance(size_bytes, bool)
        or size_bytes <= 0
        or size_bytes > MAX_ARTIFACT_BYTES
        or not isinstance(expected_sha, str)
        or not _SHA256_RE.fullmatch(expected_sha)
        or not isinstance(validation, dict)
        or validation.get("ok") is not True
    ):
        raise OracleArtifactError("oracle_artifact_rejected")
    source = _contained_regular_path(session_root, raw_path)
    staging_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    staged = staging_dir / "oracle-artifact.snapshot"
    if staged.exists() or staged.is_symlink():
        raise OracleArtifactError("oracle_artifact_rejected")
    source_fd = _open_regular_nofollow(source)
    try:
        before = os.fstat(source_fd)
        if before.st_size != size_bytes:
            raise OracleArtifactError("oracle_artifact_rejected")
        payload = _read_fd_bounded(source_fd, MAX_ARTIFACT_BYTES)
        after = os.fstat(source_fd)
        if (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
        ) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        ):
            raise OracleArtifactError("oracle_artifact_rejected")
    finally:
        os.close(source_fd)
    if len(payload) != size_bytes or hashlib.sha256(payload).hexdigest() != expected_sha:
        raise OracleArtifactError("oracle_artifact_rejected")
    staging_fd = os.open(staged, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        view = memoryview(payload)
        while view:
            written = os.write(staging_fd, view)
            if written <= 0:
                raise OracleArtifactError("oracle_artifact_rejected")
            view = view[written:]
        os.fsync(staging_fd)
    finally:
        os.close(staging_fd)
    copied = _read_bounded_regular_file(staged, MAX_ARTIFACT_BYTES)
    if len(copied) != size_bytes or hashlib.sha256(copied).hexdigest() != expected_sha:
        raise OracleArtifactError("oracle_artifact_rejected")
    return copied


def _contained_regular_path(session_root: Path, raw_path: str) -> Path:
    root = session_root.absolute()
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.absolute()
    try:
        relative = candidate.relative_to(root)
    except ValueError as error:
        raise OracleArtifactError("oracle_artifact_rejected") from error
    relative_parts = PurePosixPath(relative.as_posix()).parts
    if not relative_parts or any(part in ("", ".", "..") for part in relative_parts):
        raise OracleArtifactError("oracle_artifact_rejected")
    current = root
    try:
        root_stat = current.lstat()
        if stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode):
            raise OracleArtifactError("oracle_artifact_rejected")
        for part in relative.parts:
            current = current / part
            mode = current.lstat().st_mode
            if stat.S_ISLNK(mode):
                raise OracleArtifactError("oracle_artifact_rejected")
        if not stat.S_ISREG(mode):
            raise OracleArtifactError("oracle_artifact_rejected")
    except OSError as error:
        raise OracleArtifactError("oracle_artifact_rejected") from error
    return candidate


def _open_regular_nofollow(path: Path) -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            os.close(descriptor)
            raise OracleArtifactError("oracle_artifact_rejected")
        return descriptor
    except OSError as error:
        raise OracleArtifactError("oracle_artifact_rejected") from error


def _read_bounded_regular_file(path: Path, limit: int) -> bytes:
    descriptor = _open_regular_nofollow(path)
    try:
        return _read_fd_bounded(descriptor, limit)
    finally:
        os.close(descriptor)


def _read_fd_bounded(descriptor: int, limit: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = os.read(descriptor, min(1024 * 1024, limit + 1 - total))
        if not chunk:
            break
        chunks.append(chunk)
        total += len(chunk)
        if total > limit:
            raise OracleArtifactError("oracle_artifact_rejected")
    return b"".join(chunks)


def _zip_internal_root(payload: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            infos = archive.infolist()
            if not infos or archive.testzip() is not None:
                raise OracleArtifactError("oracle_artifact_rejected")
            roots: set[str] = set()
            for info in infos:
                path = PurePosixPath(info.filename)
                if path.is_absolute() or "\\" in info.filename or any(part in ("", ".", "..") for part in path.parts):
                    raise OracleArtifactError("oracle_artifact_rejected")
                roots.add(path.parts[0])
    except (OSError, zipfile.BadZipFile) as error:
        raise OracleArtifactError("oracle_artifact_rejected") from error
    if len(roots) != 1:
        raise OracleArtifactError("oracle_artifact_rejected")
    return next(iter(roots))
