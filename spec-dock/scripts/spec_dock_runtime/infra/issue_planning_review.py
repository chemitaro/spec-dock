from __future__ import annotations

import ctypes
from dataclasses import dataclass
from datetime import datetime, timezone
import errno
import hashlib
import os
from pathlib import Path
import platform
import secrets

from spec_dock_runtime.infra.issue_planning_candidate import (
    OutputDirectoryGuard,
    read_bounded_regular_file,
    validate_candidate_output_directory,
)

MAX_REVIEW_RESULT_BYTES = 1024 * 1024


@dataclass(frozen=True)
class PublishedPlanningReview:
    review_result_file: str
    review_summary_file: str
    review_result_sha256: str


def read_external_review_result(
    path: Path,
    *,
    repo_root: Path,
    expected_sha256: str,
) -> bytes:
    if len(expected_sha256) != 64 or any(character not in "0123456789abcdef" for character in expected_sha256):
        raise ValueError("Review result SHA-256 is invalid")
    lexical = path.absolute()
    if not lexical.exists() or not lexical.is_file() or _has_symlink_component(lexical):
        raise FileNotFoundError("Review result is unavailable")
    resolved = lexical.resolve(strict=True)
    repository = repo_root.resolve(strict=True)
    if resolved == repository or resolved.is_relative_to(repository):
        raise ValueError("Review result must be outside the repository")
    try:
        data = read_bounded_regular_file(resolved, max_bytes=MAX_REVIEW_RESULT_BYTES)
    except ValueError as error:
        reason = "bounded size" if "bounded" in str(error) else "unavailable"
        if reason == "bounded size":
            raise ValueError("Review result exceeds the bounded size") from None
        raise FileNotFoundError("Review result is unavailable") from None
    data.decode("utf-8", errors="strict")
    if hashlib.sha256(data).hexdigest() != expected_sha256:
        raise ValueError("Review result SHA-256 mismatch")
    return data


def publish_planning_review_evidence(
    *,
    output_dir: Path,
    repo_root: Path,
    reviewed_identity_sha256: str,
    review_result_bytes: bytes,
    summary_bytes: bytes,
    operation_time: datetime,
) -> PublishedPlanningReview:
    guard = validate_candidate_output_directory(output_dir, repo_root)
    if (
        len(reviewed_identity_sha256) != 64
        or any(character not in "0123456789abcdef" for character in reviewed_identity_sha256)
    ):
        raise ValueError("reviewed identity SHA-256 is invalid")
    if len(review_result_bytes) > MAX_REVIEW_RESULT_BYTES:
        raise ValueError("Review result exceeds the bounded size")
    review_result_bytes.decode("utf-8", errors="strict")
    summary_bytes.decode("utf-8", errors="strict")
    instant = operation_time.astimezone(timezone.utc).replace(microsecond=0)
    token = instant.strftime("%Y%m%dt%H%M%Sz")
    directory_name = f"review-{token}-{reviewed_identity_sha256}"
    output_descriptor = _open_guarded_output_directory(guard)
    temporary_name: str | None = None
    cleanup_name: str | None = None
    published = False
    try:
        _ensure_relative_name_absent(output_descriptor, directory_name)
        _revalidate_output_guard(guard, repo_root)
        temporary_name = _create_temporary_directory_at(output_descriptor)
        cleanup_name = temporary_name
        temporary_descriptor = _open_directory_at(output_descriptor, temporary_name)
        try:
            _write_exact_at(
                temporary_descriptor,
                "planning-review-result.json",
                review_result_bytes,
            )
            _write_exact_at(
                temporary_descriptor,
                "planning-review-summary.md",
                summary_bytes,
            )
            os.fsync(temporary_descriptor)
        finally:
            os.close(temporary_descriptor)
        _revalidate_output_guard(guard, repo_root)
        _atomic_publish_no_replace_at(
            output_descriptor,
            temporary_name,
            directory_name,
        )
        cleanup_name = directory_name
        os.fsync(output_descriptor)
        _revalidate_output_guard(guard, repo_root)
        published = True
    finally:
        if not published and cleanup_name is not None:
            _remove_evidence_directory_at(output_descriptor, cleanup_name)
        os.close(output_descriptor)
    return PublishedPlanningReview(
        review_result_file=f"{directory_name}/planning-review-result.json",
        review_summary_file=f"{directory_name}/planning-review-summary.md",
        review_result_sha256=hashlib.sha256(review_result_bytes).hexdigest(),
    )


def _write_exact_at(directory_descriptor: int, name: str, data: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(name, flags, 0o600, dir_fd=directory_descriptor)
    try:
        view = memoryview(data)
        while view:
            written = os.write(descriptor, view)
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _has_symlink_component(path: Path) -> bool:
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.is_symlink():
            return True
    return False


def _revalidate_output_guard(guard: OutputDirectoryGuard, repo_root: Path) -> None:
    current = validate_candidate_output_directory(guard.path, repo_root)
    if (current.device, current.inode) != (guard.device, guard.inode):
        raise ValueError("review output directory identity changed")


def _open_guarded_output_directory(guard: OutputDirectoryGuard) -> int:
    flags = os.O_RDONLY
    flags |= getattr(os, "O_DIRECTORY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(guard.path, flags)
    except OSError:
        raise ValueError("review output directory cannot be safely opened") from None
    opened = os.fstat(descriptor)
    if (opened.st_dev, opened.st_ino) == (guard.device, guard.inode):
        return descriptor
    os.close(descriptor)
    raise ValueError("review output directory identity changed")


def _open_directory_at(parent_descriptor: int, name: str) -> int:
    flags = os.O_RDONLY
    flags |= getattr(os, "O_DIRECTORY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    return os.open(name, flags, dir_fd=parent_descriptor)


def _ensure_relative_name_absent(directory_descriptor: int, name: str) -> None:
    try:
        os.stat(name, dir_fd=directory_descriptor, follow_symlinks=False)
    except FileNotFoundError:
        return
    raise FileExistsError(name)


def _create_temporary_directory_at(directory_descriptor: int) -> str:
    for _ in range(100):
        name = f".spec-dock-planning-review-{secrets.token_hex(16)}"
        try:
            os.mkdir(name, mode=0o700, dir_fd=directory_descriptor)
        except FileExistsError:
            continue
        return name
    raise FileExistsError("review staging directory collision")


def _atomic_publish_no_replace_at(
    directory_descriptor: int,
    source_name: str,
    destination_name: str,
) -> None:
    if platform.system() == "Darwin":
        library = ctypes.CDLL(None, use_errno=True)
        rename = getattr(library, "renameatx_np", None)
        if rename is None:
            raise NotImplementedError("renameatx_np is unavailable")
    elif platform.system() == "Linux":
        library = ctypes.CDLL(None, use_errno=True)
        rename = getattr(library, "renameat2", None)
        if rename is None:
            raise NotImplementedError("renameat2 is unavailable")
    else:
        raise NotImplementedError("atomic no-replace publication is unsupported")
    rename.argtypes = (
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    )
    rename.restype = ctypes.c_int
    result = rename(
        directory_descriptor,
        os.fsencode(source_name),
        directory_descriptor,
        os.fsencode(destination_name),
        0x00000004 if platform.system() == "Darwin" else 0x00000001,
    )
    if result == 0:
        return
    error_number = ctypes.get_errno()
    if error_number == errno.EEXIST:
        raise FileExistsError(error_number, os.strerror(error_number), destination_name)
    raise OSError(error_number, os.strerror(error_number), destination_name)


def _remove_evidence_directory_at(directory_descriptor: int, name: str) -> None:
    try:
        evidence_descriptor = _open_directory_at(directory_descriptor, name)
    except FileNotFoundError:
        return
    try:
        for child in os.listdir(evidence_descriptor):  # noqa: PTH208 - directory fd is the guard
            os.unlink(child, dir_fd=evidence_descriptor)
    finally:
        os.close(evidence_descriptor)
    try:
        os.rmdir(name, dir_fd=directory_descriptor)
        os.fsync(directory_descriptor)
    except OSError:
        raise ValueError("review output directory cleanup failed") from None
