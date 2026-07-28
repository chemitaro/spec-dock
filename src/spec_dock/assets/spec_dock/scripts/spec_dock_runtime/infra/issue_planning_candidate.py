from __future__ import annotations

from contextlib import suppress
import ctypes
from dataclasses import dataclass
import errno
import os
from pathlib import Path
import platform
import shutil
import stat
import tempfile
from typing import TYPE_CHECKING
import zipfile

from spec_dock_runtime.domain.authoring_pack.zip_contract import (
    issue_candidate_v1_profile,
    review_pack_input,
)
from spec_dock_runtime.domain.issue_planning_candidate import (
    CandidateMaterial,
    derive_candidate_identity,
    verify_issue_candidate_files,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from datetime import datetime

    from spec_dock_runtime.domain.issue_planning_contracts import IssueCandidateIdentity


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


@dataclass(frozen=True)
class OutputDirectoryGuard:
    path: Path
    device: int
    inode: int


@dataclass(frozen=True)
class PublishedCandidate:
    identity: IssueCandidateIdentity
    zip_byte_count: int


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
