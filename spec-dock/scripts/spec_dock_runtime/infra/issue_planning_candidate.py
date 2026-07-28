from __future__ import annotations

from contextlib import suppress
import ctypes
from dataclasses import dataclass
import errno
import hashlib
import io
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import stat
import tempfile
from types import MappingProxyType
from typing import TYPE_CHECKING
import zipfile

from spec_dock_runtime.domain.authoring_pack.zip_contract import (
    PackReviewResult,
    issue_candidate_v1_profile,
    review_pack_input,
)
from spec_dock_runtime.domain.issue_planning_candidate import (
    CANDIDATE_PATHS,
    CandidateMaterial,
    derive_candidate_identity,
    parse_canonical_control_json,
    verify_issue_candidate_files,
)
from spec_dock_runtime.domain.issue_planning_contracts import IssueCandidateIdentity

if TYPE_CHECKING:
    from collections.abc import Mapping
    from datetime import datetime


class CandidateOutputRejected(ValueError):
    pass


class CandidateCollision(FileExistsError):
    pass


class CandidateArchiveRejected(ValueError):
    def __init__(self, findings: tuple[str, ...]) -> None:
        super().__init__("Issue Candidate archive validation failed")
        self.findings = findings


class CandidateBuildFailed(OSError):
    pass


class CandidatePublicationFailed(OSError):
    pass


MAX_CANDIDATE_ARCHIVE_BYTES = 16_000_000


@dataclass(frozen=True)
class OutputDirectoryGuard:
    path: Path
    device: int
    inode: int


@dataclass(frozen=True)
class PublishedCandidate:
    identity: IssueCandidateIdentity
    zip_byte_count: int


@dataclass(frozen=True)
class VerifiedIssueCandidate:
    identity: IssueCandidateIdentity
    files: Mapping[str, bytes]
    source_baseline: Mapping[str, object]
    zip_bytes: bytes


def validate_candidate_output_directory(output_dir: Path, repo_root: Path) -> OutputDirectoryGuard:
    lexical = output_dir.absolute()
    if not lexical.exists() or not lexical.is_dir():
        raise CandidateOutputRejected("candidate output must be an existing directory")
    if _has_symlink_component(lexical):
        raise CandidateOutputRejected("candidate output path must not contain symlinks")
    try:
        output = lexical.resolve(strict=True)
        repository = repo_root.resolve(strict=True)
    except OSError as error:
        raise CandidateOutputRejected("candidate output or repository cannot be resolved") from error
    if output == repository or output.is_relative_to(repository) or repository.is_relative_to(output):
        raise CandidateOutputRejected("candidate output must be external to the repository")
    flags = os.O_RDONLY
    flags |= getattr(os, "O_DIRECTORY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(output, flags)
    except OSError as error:
        raise CandidateOutputRejected("candidate output cannot be safely opened") from error
    try:
        opened = os.fstat(descriptor)
        current = output.stat(follow_symlinks=False)
        if (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino):
            raise CandidateOutputRejected("candidate output identity changed")
    finally:
        os.close(descriptor)
    return OutputDirectoryGuard(path=output, device=current.st_dev, inode=current.st_ino)


def load_verified_issue_candidate(candidate_path: Path, repo_root: Path) -> VerifiedIssueCandidate:
    lexical = candidate_path.absolute()
    if (
        not lexical.exists()
        or not lexical.is_file()
        or _has_symlink_component(lexical)
        or lexical.suffix != ".zip"
    ):
        raise CandidateArchiveRejected(("unsafe_candidate_path",))
    try:
        candidate = lexical.resolve(strict=True)
        repository = repo_root.resolve(strict=True)
    except OSError as error:
        raise CandidateArchiveRejected(("unsafe_candidate_path",)) from error
    if candidate == repository or candidate.is_relative_to(repository):
        raise CandidateArchiveRejected(("unsafe_candidate_path",))
    try:
        zip_bytes = _read_candidate_snapshot(candidate)
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
            names = tuple(info.filename for info in archive.infolist())
    except (OSError, zipfile.BadZipFile) as error:
        raise CandidateArchiveRejected(("archive_unreadable",)) from error
    roots = {
        name.partition("/")[0]
        for name in names
        if "/" in name and name.partition("/")[0]
    }
    if len(roots) != 1:
        raise CandidateArchiveRejected(("root_mismatch",))
    internal_root = next(iter(roots))
    review = _review_candidate_snapshot(
        zip_bytes,
        repo_root=repository,
        internal_root=internal_root,
    )
    if review.status != "pass":
        raise CandidateArchiveRejected(review.findings)
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
            files = {
                relative: archive.read(f"{internal_root}/{relative}")
                for relative in CANDIDATE_PATHS
            }
        manifest = parse_canonical_control_json(files["MANIFEST.json"])
        source = parse_canonical_control_json(files["SOURCE-BASELINE.json"])
        candidate_control = manifest["candidate"]
        if not isinstance(candidate_control, dict):
            raise ValueError("Candidate manifest identity is invalid")
        identity = IssueCandidateIdentity(
            issue_id=candidate_control["issue_id"],
            candidate_id=candidate_control["candidate_id"],
            version=candidate_control["version"],
            logical_filename=candidate_control["logical_filename"],
            observed_transport_filename=candidate.name,
            internal_root=candidate_control["internal_root"],
            source_repository=source["source_repository"],
            source_branch=source["source_branch"],
            source_head=source["source_head"],
            zip_sha256=hashlib.sha256(zip_bytes).hexdigest(),
        )
    except (KeyError, OSError, TypeError, ValueError, zipfile.BadZipFile) as error:
        raise CandidateArchiveRejected(("candidate_identity_mismatch",)) from error
    return VerifiedIssueCandidate(
        identity=identity,
        files=MappingProxyType(files),
        source_baseline=MappingProxyType(source),
        zip_bytes=zip_bytes,
    )


def _read_candidate_snapshot(candidate: Path) -> bytes:
    try:
        return read_bounded_regular_file(candidate, max_bytes=MAX_CANDIDATE_ARCHIVE_BYTES)
    except (OSError, ValueError) as error:
        raise CandidateArchiveRejected(("archive_unreadable",)) from error


def open_safe_directory_descriptor(path: Path) -> int:
    absolute = path.absolute()
    if not absolute.is_absolute() or any(part in ("", ".", "..") for part in absolute.parts[1:]):
        raise ValueError("directory traversal rejected")
    flags = os.O_RDONLY
    flags |= getattr(os, "O_DIRECTORY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = -1
    try:
        descriptor = os.open(absolute.anchor, flags)
        for part in absolute.parts[1:]:
            next_descriptor = os.open(part, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        return descriptor
    except OSError:
        if descriptor >= 0:
            with suppress(OSError):
                os.close(descriptor)
        raise ValueError("directory traversal rejected") from None


def read_bounded_regular_file(path: Path, *, max_bytes: int) -> bytes:
    parent_descriptor = open_safe_directory_descriptor(path.parent)
    try:
        return read_bounded_regular_file_at(
            parent_descriptor,
            path.name,
            max_bytes=max_bytes,
        )
    finally:
        os.close(parent_descriptor)


def read_bounded_regular_file_at(
    root_descriptor: int,
    relative_path: str,
    *,
    max_bytes: int,
) -> bytes:
    relative = PurePosixPath(relative_path)
    if relative.is_absolute() or any(part in ("", ".", "..") for part in relative.parts):
        raise ValueError("file traversal rejected")
    directory_descriptor = os.dup(root_descriptor)
    directory_flags = os.O_RDONLY
    directory_flags |= getattr(os, "O_DIRECTORY", 0)
    directory_flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        for part in relative.parts[:-1]:
            next_descriptor = os.open(
                part,
                directory_flags,
                dir_fd=directory_descriptor,
            )
            os.close(directory_descriptor)
            directory_descriptor = next_descriptor
        file_flags = os.O_RDONLY
        file_flags |= getattr(os, "O_NOFOLLOW", 0)
        file_flags |= getattr(os, "O_NONBLOCK", 0)
        descriptor = os.open(
            relative.parts[-1],
            file_flags,
            dir_fd=directory_descriptor,
        )
    except OSError:
        raise ValueError("file traversal rejected") from None
    finally:
        os.close(directory_descriptor)
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise ValueError("file traversal rejected")
        if opened.st_size > max_bytes:
            raise ValueError("file exceeds bounded size")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(1024 * 1024, max_bytes + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > max_bytes:
                raise ValueError("file exceeds bounded size")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def _review_candidate_snapshot(
    zip_bytes: bytes,
    *,
    repo_root: Path,
    internal_root: str,
) -> PackReviewResult:
    temporary_root = Path(tempfile.gettempdir()).resolve(strict=True)
    if temporary_root == repo_root or temporary_root.is_relative_to(repo_root):
        raise CandidateArchiveRejected(("unsafe_candidate_path",))
    with tempfile.TemporaryDirectory(prefix="specdock-candidate-snapshot-", dir=temporary_root) as raw:
        snapshot = Path(raw) / "candidate.zip"
        with snapshot.open("xb") as stream:
            stream.write(zip_bytes)
            stream.flush()
            os.fsync(stream.fileno())
        return review_pack_input(
            snapshot,
            profile=issue_candidate_v1_profile(
                expected_root=internal_root,
                cross_file_validator=verify_issue_candidate_files,
            ),
        )


def build_deterministic_zip(
    destination: Path,
    internal_root: str,
    files: Mapping[str, bytes],
    operation_time: datetime,
) -> None:
    date_time = (
        operation_time.year,
        operation_time.month,
        operation_time.day,
        operation_time.hour,
        operation_time.minute,
        operation_time.second,
    )
    with zipfile.ZipFile(
        destination,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as archive:
        archive.comment = b""
        for relative_path in sorted(files, key=lambda value: value.encode("utf-8")):
            info = zipfile.ZipInfo(f"{internal_root}/{relative_path}", date_time=date_time)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.extra = b""
            info.comment = b""
            archive.writestr(info, files[relative_path], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def atomic_publish_no_replace(source: Path, destination: Path) -> None:
    if platform.system() == "Darwin":
        _rename_exclusive_darwin(source, destination)
        return
    if platform.system() == "Linux":
        _rename_exclusive_linux(source, destination)
        return
    raise NotImplementedError("atomic no-replace publication is unsupported")


def build_and_publish_candidate(
    *,
    output_guard: OutputDirectoryGuard,
    repo_root: Path,
    material: CandidateMaterial,
) -> PublishedCandidate:
    final_path = output_guard.path / material.logical_filename
    if final_path.exists():
        raise CandidateCollision(material.logical_filename)
    temporary_dir: Path | None = None
    published = False
    try:
        temporary_dir = Path(
            tempfile.mkdtemp(
                prefix=".spec-dock-issue-candidate-",
                dir=output_guard.path,
            )
        )
        Path(temporary_dir).chmod(0o700)
        staged = temporary_dir / material.logical_filename
        try:
            build_deterministic_zip(
                staged,
                material.internal_root,
                material.files,
                material.operation_time,
            )
            with staged.open("rb") as stream:
                os.fsync(stream.fileno())
        except OSError as error:
            raise CandidateBuildFailed("Candidate ZIP construction failed") from error
        profile = issue_candidate_v1_profile(
            expected_root=material.internal_root,
            cross_file_validator=verify_issue_candidate_files,
        )
        review = review_pack_input(staged, profile=profile)
        if review.status != "pass":
            raise CandidateArchiveRejected(review.findings)
        try:
            zip_bytes = staged.read_bytes()
        except OSError as error:
            raise CandidateBuildFailed("Candidate ZIP digest read failed") from error
        identity = derive_candidate_identity(
            material,
            zip_bytes,
            observed_transport_filename=material.logical_filename,
        )
        _revalidate_output_guard(output_guard, repo_root)
        if final_path.exists():
            raise CandidateCollision(material.logical_filename)
        try:
            atomic_publish_no_replace(staged, final_path)
        except FileExistsError as error:
            raise CandidateCollision(material.logical_filename) from error
        except (NotImplementedError, OSError) as error:
            raise CandidatePublicationFailed("Candidate publication failed") from error
        published = True
        return PublishedCandidate(identity=identity, zip_byte_count=len(zip_bytes))
    finally:
        if temporary_dir is not None:
            if published:
                with suppress(OSError):
                    temporary_dir.rmdir()
            else:
                shutil.rmtree(temporary_dir, ignore_errors=True)


def _revalidate_output_guard(guard: OutputDirectoryGuard, repo_root: Path) -> None:
    current = validate_candidate_output_directory(guard.path, repo_root)
    if (current.device, current.inode) != (guard.device, guard.inode):
        raise CandidateOutputRejected("candidate output identity changed")


def _has_symlink_component(path: Path) -> bool:
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.is_symlink():
            return True
    return False


def _rename_exclusive_darwin(source: Path, destination: Path) -> None:
    library = ctypes.CDLL(None, use_errno=True)
    rename = getattr(library, "renamex_np", None)
    if rename is None:
        raise NotImplementedError("renamex_np is unavailable")
    rename.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint)
    rename.restype = ctypes.c_int
    result = rename(os.fsencode(source), os.fsencode(destination), 0x00000004)
    if result == 0:
        return
    error_number = ctypes.get_errno()
    if error_number == errno.EEXIST:
        raise FileExistsError(error_number, os.strerror(error_number), destination)
    raise OSError(error_number, os.strerror(error_number), destination)


def _rename_exclusive_linux(source: Path, destination: Path) -> None:
    library = ctypes.CDLL(None, use_errno=True)
    rename = getattr(library, "renameat2", None)
    if rename is None:
        raise NotImplementedError("renameat2 is unavailable")
    rename.argtypes = (
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    )
    rename.restype = ctypes.c_int
    result = rename(-100, os.fsencode(source), -100, os.fsencode(destination), 0x00000001)
    if result == 0:
        return
    error_number = ctypes.get_errno()
    if error_number == errno.EEXIST:
        raise FileExistsError(error_number, os.strerror(error_number), destination)
    raise OSError(error_number, os.strerror(error_number), destination)
