from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import tempfile
from types import MappingProxyType
from typing import TYPE_CHECKING, Literal

from spec_dock_runtime.domain.issue_planning_candidate import DOCUMENT_NAMES
from spec_dock_runtime.infra.issue_planning_candidate import OutputDirectoryGuard

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from spec_dock_runtime.domain.issue_planning_contracts import (
        IssueCandidateIdentity,
        ReviewedPlanningIdentity,
    )
PlanningApplyStatus = Literal[
    "ready",
    "blocked",
    "stale",
    "rejected",
    "rolled_back",
    "recovery_required",
    "publication_pending",
    "blocked_remote_diverged",
]

_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_OPERATION_SCHEMA = "spec-dock.issue-planning-apply-operation.v1"
_PROHIBITED_GIT_WORDS = {
    "--force",
    "--force-with-lease",
    "reset",
    "--amend",
    "rebase",
}
_MANAGED_SYNC_FILES = (
    "spec-dock/.agent/index-all.json",
    "spec-dock/.agent/index.json",
    "spec-dock/.agent/tree-all.json",
    "spec-dock/.agent/tree.json",
    "spec-dock/.agent/deps-issues.json",
    "spec-dock/tree-all.puml",
    "spec-dock/tree.puml",
    "spec-dock/deps-issues.puml",
    "spec-dock/deps-raw.puml",
    "spec-dock/dashboard.md",
    "spec-dock/.agent/deps.json",
    "spec-dock/.agent/deps.puml",
    "spec-dock/.agent/deps.todo.puml",
    "spec-dock/.work/state.json",
    "spec-dock/.work/index.json",
    "spec-dock/.work/tree.json",
)
_MANAGED_SYNC_TREE = "spec-dock/adrs"
_MAX_MANAGED_ENTRIES = 10_000
_MAX_MANAGED_BYTES = 32_000_000
_DURABLE_OPERATION_STATES = frozenset({
    "OPERATION_RECORDED",
    "BACKED_UP",
    "MUTATING",
    "VALIDATED",
    "SYNCED",
    "STAGED",
    "COMMITTED",
    "PUSHED",
    "REMOTE_PARITY",
    "ROLLED_BACK",
})
_TRANSACTION_RESTORE_STATES = frozenset({
    "MUTATING",
    "VALIDATED",
    "SYNCED",
    "STAGED",
})
_NO_TRANSACTION_START_STATES = frozenset({
    "OPERATION_RECORDED",
    "ROLLED_BACK",
})


class PlanningApplyOutputRejected(ValueError):
    pass


class PlanningApplyUnsafeGitCommand(ValueError):
    pass


class PlanningApplyRestoreMismatch(RuntimeError):
    pass


@dataclass
class _ApplyEvidenceHandle:
    output_fd: int
    operation_fd: int
    logical_operation_path: Path

    def close(self) -> None:
        os.close(self.operation_fd)
        os.close(self.output_fd)

    def __truediv__(self, name: str) -> Path:
        return self.logical_operation_path / name

    def stat(self) -> os.stat_result:
        return self.logical_operation_path.stat()

    def iterdir(self):
        return self.logical_operation_path.iterdir()


@dataclass(frozen=True)
class FileSnapshot:
    existed: bool
    data: bytes
    mode: int
    sha256: str


@dataclass(frozen=True)
class GitIndexSnapshot:
    path: Path
    data: bytes
    mode: int
    sha256: str


@dataclass(frozen=True)
class GitCommandResult:
    returncode: int
    stdout: bytes
    stderr: bytes


@dataclass(frozen=True)
class ManagedStateEntry:
    kind: Literal["file", "directory", "symlink"]
    mode: int
    data: bytes = field(default=b"", repr=False)
    target: str | None = None


@dataclass(frozen=True)
class DurableTransactionBackup:
    index: GitIndexSnapshot
    files: Mapping[str, FileSnapshot]
    decision: FileSnapshot
    managed: Mapping[str, ManagedStateEntry]


@dataclass(frozen=True)
class ExpectedPlanningTargets:
    documents: Mapping[str, bytes]
    blob_oids: Mapping[str, str]


@dataclass(frozen=True)
class PlanningApplyExecution:
    status: PlanningApplyStatus
    reason: str
    operation_id: str
    decision_artifact_path: str | None = None
    local_commit: str | None = None
    local_tree: str | None = None
    remote_commit: str | None = None
    details: tuple[str, ...] = ()

    @property
    def is_ready(self) -> bool:
        return self.status == "ready" and self.reason == "adoption_published"

    def to_output(self) -> dict[str, object]:
        return {
            "operation_id": self.operation_id,
            "decision_artifact_path": self.decision_artifact_path,
            "local_commit": self.local_commit,
            "local_tree": self.local_tree,
            "remote_commit": self.remote_commit,
        }


@dataclass(frozen=True)
class PlanningApplyOperation:
    operation_id: str
    operation_core_bytes: bytes = field(repr=False)
    issue_id: str
    mode: Literal["archive-candidate", "git-bound"]
    repository: str
    branch: str
    expected_head: str
    reviewed_identity: ReviewedPlanningIdentity
    reviewed_identity_sha256: str
    review_result_sha256: str
    human_decision_sha256: str
    decision: Literal["approved", "rejected"]
    canonical_target_paths: tuple[str, str, str]
    pre_apply_target_blob_oids: Mapping[str, str]
    candidate_identity: IssueCandidateIdentity | None
    git_bound_operation_binding_sha256: str | None
    companion_target_path: str
    companion_sha256: str
    decision_artifact_path: str
    human_decision_bytes: bytes = field(repr=False)
    replacement_documents: Mapping[str, bytes] = field(repr=False)
    replacement_companion: bytes | None = field(repr=False)
    pre_apply_document_bytes: Mapping[str, bytes] = field(repr=False)

    @classmethod
    def create(
        cls,
        *,
        issue_id: str,
        mode: Literal["archive-candidate", "git-bound"],
        repository: str,
        branch: str,
        expected_head: str,
        reviewed_identity: ReviewedPlanningIdentity,
        reviewed_identity_sha256: str,
        review_result_sha256: str,
        human_decision_sha256: str,
        decision: Literal["approved", "rejected"],
        canonical_target_paths: tuple[str, str, str],
        pre_apply_target_blob_oids: Mapping[str, str],
        candidate_identity: IssueCandidateIdentity | None,
        git_bound_operation_binding_sha256: str | None,
        companion_target_path: str | None,
        companion_sha256: str | None,
        decision_artifact_path: str,
        human_decision_bytes: bytes,
        replacement_documents: Mapping[str, bytes],
        replacement_companion: bytes | None,
        pre_apply_document_bytes: Mapping[str, bytes],
    ) -> PlanningApplyOperation:
        if mode not in ("archive-candidate", "git-bound"):
            raise ValueError("invalid planning apply mode")
        if decision not in ("approved", "rejected"):
            raise ValueError("invalid planning decision")
        if _SHA40.fullmatch(expected_head) is None:
            raise ValueError("expected_head must be lowercase SHA-1")
        for digest in (
            reviewed_identity_sha256,
            review_result_sha256,
            human_decision_sha256,
        ):
            if _SHA256.fullmatch(digest) is None:
                raise ValueError("planning apply digest must be lowercase SHA-256")
        if reviewed_identity.sha256 != reviewed_identity_sha256:
            raise ValueError("reviewed identity digest mismatch")
        if candidate_identity is None:
            raise ValueError("planning apply requires Candidate identity")
        if (
            reviewed_identity.mode != mode
            or reviewed_identity.issue_id != issue_id
            or reviewed_identity.repository != repository
            or reviewed_identity.branch != branch
            or reviewed_identity.source_head != expected_head
        ):
            raise ValueError("reviewed identity does not match apply target")
        if tuple(sorted(canonical_target_paths, key=lambda value: value.encode())) != tuple(canonical_target_paths):
            raise ValueError("canonical target paths must be byte-sorted")
        for path in canonical_target_paths:
            _safe_repo_relative(path)
        if companion_target_path is None or companion_sha256 is None:
            raise ValueError("planning apply requires companion evidence")
        companion_path = _safe_repo_relative(companion_target_path).as_posix()
        issue_dir = PurePosixPath(canonical_target_paths[0]).parent
        if (
            PurePosixPath(companion_path).parent != issue_dir / "artifacts"
            or PurePosixPath(companion_path).suffix != ".md"
        ):
            raise ValueError("companion target must be beneath the Issue artifacts directory")
        if _SHA256.fullmatch(companion_sha256) is None:
            raise ValueError("companion SHA must be lowercase SHA-256")
        if mode == "git-bound":
            binding = reviewed_identity.git_bound_operation_binding
            if (
                git_bound_operation_binding_sha256 is None
                or _SHA256.fullmatch(git_bound_operation_binding_sha256) is None
                or binding is None
                or binding.binding_sha256 != git_bound_operation_binding_sha256
                or binding.candidate_identity != candidate_identity
                or binding.onboarding_companion.path != PurePosixPath(companion_path).relative_to(issue_dir).as_posix()
                or binding.onboarding_companion.sha256 != companion_sha256
                or reviewed_identity.canonical_target_paths != canonical_target_paths
            ):
                raise ValueError("git-bound operation binding mismatch")
        elif (
            git_bound_operation_binding_sha256 is not None or reviewed_identity.candidate_identity != candidate_identity
        ):
            raise ValueError("archive apply Candidate identity mismatch")
        if (
            set(pre_apply_target_blob_oids) != set(canonical_target_paths)
            or set(pre_apply_document_bytes) != set(DOCUMENT_NAMES)
            or any(_SHA40.fullmatch(value) is None for value in pre_apply_target_blob_oids.values())
            or any(
                PurePosixPath(path).name not in pre_apply_document_bytes
                or _git_blob_oid(pre_apply_document_bytes[PurePosixPath(path).name]) != pre_apply_target_blob_oids[path]
                for path in canonical_target_paths
            )
            or hashlib.sha256(human_decision_bytes).hexdigest() != human_decision_sha256
        ):
            raise ValueError("planning apply preimage evidence mismatch")
        expected_documents = set(DOCUMENT_NAMES) if decision == "approved" and mode == "archive-candidate" else set()
        if set(replacement_documents) != expected_documents:
            raise ValueError("replacement document inventory does not match apply mode")
        if (replacement_companion is not None) != (decision == "approved"):
            raise ValueError("replacement companion does not match Human decision")
        if replacement_companion is not None and hashlib.sha256(replacement_companion).hexdigest() != companion_sha256:
            raise ValueError("replacement companion SHA mismatch")
        core: dict[str, object] = {
            "schema_version": _OPERATION_SCHEMA,
            "issue_id": issue_id,
            "mode": mode,
            "repository": repository,
            "branch": branch,
            "expected_head": expected_head,
            "reviewed_identity": reviewed_identity.to_dict(),
            "reviewed_identity_sha256": reviewed_identity_sha256,
            "review_result_sha256": review_result_sha256,
            "human_decision_sha256": human_decision_sha256,
            "decision": decision,
            "canonical_target_paths": list(canonical_target_paths),
            "pre_apply_target_blob_oids": dict(
                sorted(pre_apply_target_blob_oids.items(), key=lambda item: item[0].encode())
            ),
            "candidate_identity": (None if candidate_identity is None else candidate_identity.to_dict()),
            "git_bound_operation_binding_sha256": git_bound_operation_binding_sha256,
            "companion_target_path": companion_path,
            "companion_sha256": companion_sha256,
            "replacement_companion_present": replacement_companion is not None,
        }
        core_bytes = _canonical_json_bytes(core)
        operation_id = hashlib.sha256(core_bytes).hexdigest()
        artifact = PurePosixPath(decision_artifact_path)
        _safe_repo_relative(artifact.as_posix())
        timestamp = artifact.name[:16]
        if re.fullmatch(r"[0-9]{8}t[0-9]{6}z", timestamp) is None:
            raise ValueError("decision artifact requires a UTC timestamp prefix")
        artifact_name = f"{timestamp}-planning-human-decision-{operation_id[:16]}.json"
        deterministic_artifact = artifact.with_name(artifact_name).as_posix()
        return cls(
            operation_id=operation_id,
            operation_core_bytes=core_bytes,
            issue_id=issue_id,
            mode=mode,
            repository=repository,
            branch=branch,
            expected_head=expected_head,
            reviewed_identity=reviewed_identity,
            reviewed_identity_sha256=reviewed_identity_sha256,
            review_result_sha256=review_result_sha256,
            human_decision_sha256=human_decision_sha256,
            decision=decision,
            canonical_target_paths=canonical_target_paths,
            pre_apply_target_blob_oids=MappingProxyType(dict(pre_apply_target_blob_oids)),
            candidate_identity=candidate_identity,
            git_bound_operation_binding_sha256=git_bound_operation_binding_sha256,
            companion_target_path=companion_path,
            companion_sha256=companion_sha256,
            decision_artifact_path=deterministic_artifact,
            human_decision_bytes=bytes(human_decision_bytes),
            replacement_documents=MappingProxyType(dict(replacement_documents)),
            replacement_companion=(None if replacement_companion is None else bytes(replacement_companion)),
            pre_apply_document_bytes=MappingProxyType(dict(pre_apply_document_bytes)),
        )


def _canonical_json_bytes(value: Mapping[str, object]) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        + b"\n"
    )


def _safe_repo_relative(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in ("", ".", "..") for part in path.parts):
        raise ValueError("unsafe repository-relative path")
    return path


def validate_planning_git_argv(argv: tuple[str, ...]) -> None:
    if not argv or argv[0] != "git":
        raise PlanningApplyUnsafeGitCommand("planning Git argv must start with git")
    if any(word in _PROHIBITED_GIT_WORDS or word.startswith("--force-with-lease") for word in argv[1:]):
        raise PlanningApplyUnsafeGitCommand("prohibited planning Git operation")
    if argv[1:2] == ("update-ref",):
        raise PlanningApplyUnsafeGitCommand("custom Git refs are prohibited")
    if argv[1:2] == ("push",) and any(word.startswith("+") or word.startswith(":") for word in argv[2:]):
        raise PlanningApplyUnsafeGitCommand("non-fast-forward Git push is prohibited")


def snapshot_regular_file(path: Path) -> FileSnapshot:
    try:
        opened = path.stat(follow_symlinks=False)
    except FileNotFoundError:
        return FileSnapshot(existed=False, data=b"", mode=0, sha256=hashlib.sha256(b"").hexdigest())
    if not stat.S_ISREG(opened.st_mode):
        raise ValueError("transaction target must be a regular non-symlink file")
    data = path.read_bytes()
    return FileSnapshot(
        existed=True,
        data=data,
        mode=stat.S_IMODE(opened.st_mode),
        sha256=hashlib.sha256(data).hexdigest(),
    )


def restore_regular_file(path: Path, snapshot: FileSnapshot) -> None:
    if snapshot.existed:
        _atomic_write_exact(path, snapshot.data, mode=snapshot.mode)
        restored = snapshot_regular_file(path)
        if restored != snapshot:
            raise PlanningApplyRestoreMismatch("file restore mismatch")
    else:
        if path.exists() or path.is_symlink():
            path.unlink()
        if path.exists() or path.is_symlink():
            raise PlanningApplyRestoreMismatch("file absence restore mismatch")


def _atomic_write_exact(path: Path, data: bytes, *, mode: int) -> None:
    parent = path.parent
    if parent.is_symlink() or not parent.is_dir():
        raise ValueError("transaction parent must be an existing safe directory")
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=parent)
    temp_path = Path(temporary)
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        temp_path.replace(path)
        directory_descriptor = os.open(parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _git_index_path(repo_root: Path) -> Path:
    result = _run_git(repo_root, ("rev-parse", "--git-path", "index"))
    if result.returncode != 0:
        raise ValueError("Git index cannot be resolved")
    value = result.stdout.decode("utf-8", errors="strict").strip()
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def snapshot_git_index(repo_root: Path) -> GitIndexSnapshot:
    path = _git_index_path(repo_root)
    snapshot = snapshot_regular_file(path)
    if not snapshot.existed:
        raise ValueError("Git index must exist before planning apply")
    return GitIndexSnapshot(
        path=path,
        data=snapshot.data,
        mode=snapshot.mode,
        sha256=snapshot.sha256,
    )


def restore_git_index(repo_root: Path, snapshot: GitIndexSnapshot) -> None:
    if _git_index_path(repo_root).resolve() != snapshot.path.resolve():
        raise PlanningApplyRestoreMismatch("Git index path changed")
    _atomic_write_exact(snapshot.path, snapshot.data, mode=snapshot.mode)
    if snapshot_git_index(repo_root) != snapshot:
        raise PlanningApplyRestoreMismatch("Git index restore mismatch")


def record_planning_apply_operation(
    operation: PlanningApplyOperation,
    *,
    output_guard: OutputDirectoryGuard | None = None,
    output_dir: Path | None = None,
    capture_hook: Callable[[str], None] | None = None,
) -> _ApplyEvidenceHandle:
    output_guard = output_guard or _guard_from_current_output(output_dir)
    output_fd = _open_guarded_output(output_guard)
    operation_name = f"planning-apply-{operation.operation_id}"
    try:
        if capture_hook is not None:
            capture_hook("after_output_capture")
        try:
            os.mkdir(operation_name, mode=0o700, dir_fd=output_fd)
            created = True
        except FileExistsError:
            created = False
        operation_fd = _open_directory_at(output_fd, operation_name)
        handle = _ApplyEvidenceHandle(
            output_fd=output_fd,
            operation_fd=operation_fd,
            logical_operation_path=output_guard.path / operation_name,
        )
        try:
            if not _owned_private_directory_at(output_fd, operation_name):
                raise PlanningApplyOutputRejected("operation identity collision")
            if created:
                _write_private_no_replace_at(handle, "operation.json", operation.operation_core_bytes)
                _mkdir_private_at(handle, "attempts")
                _set_operation_state(handle, operation, "OPERATION_RECORDED")
                return handle
            _validate_existing_operation_evidence(handle)
            if _read_private_file_at(handle, "operation.json") != operation.operation_core_bytes:
                raise PlanningApplyOutputRejected("operation identity collision")
            state_bytes = _read_private_file_at(handle, "state.json")
            try:
                state = json.loads(state_bytes)
            except (ValueError, json.JSONDecodeError):
                raise PlanningApplyOutputRejected("operation evidence is incomplete") from None
            if (
                not isinstance(state, dict)
                or set(state) != {"operation_id", "state"}
                or state.get("operation_id") != operation.operation_id
                or _canonical_json_bytes(state) != state_bytes
            ):
                raise PlanningApplyOutputRejected("operation evidence is incomplete")
            return handle
        except BaseException:
            handle.close()
            output_fd = -1
            raise
    except BaseException:
        if output_fd >= 0:
            with suppress(OSError):
                os.close(output_fd)
        raise


def _open_guarded_output(guard: OutputDirectoryGuard) -> int:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(guard.path, flags)
    opened = os.fstat(descriptor)
    if not stat.S_ISDIR(opened.st_mode) or (opened.st_dev, opened.st_ino) != (guard.device, guard.inode):
        os.close(descriptor)
        raise PlanningApplyOutputRejected("apply output identity changed")
    return descriptor


def _guard_from_current_output(output_dir: Path | None) -> OutputDirectoryGuard:
    if output_dir is None:
        raise PlanningApplyOutputRejected("apply output guard is required")
    path = output_dir.resolve(strict=True)
    opened = path.stat(follow_symlinks=False)
    if not stat.S_ISDIR(opened.st_mode) or path.is_symlink():
        raise PlanningApplyOutputRejected("apply output is unsafe")
    return OutputDirectoryGuard(path=path, device=opened.st_dev, inode=opened.st_ino)


def _open_directory_at(parent_fd: int, name: str) -> int:
    descriptor = os.open(
        name,
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
        dir_fd=parent_fd,
    )
    opened = os.fstat(descriptor)
    if not stat.S_ISDIR(opened.st_mode) or opened.st_uid != os.geteuid() or stat.S_IMODE(opened.st_mode) != 0o700:
        os.close(descriptor)
        raise PlanningApplyOutputRejected("operation evidence is not private")
    return descriptor


def _parent_fd(handle: _ApplyEvidenceHandle, relative: str) -> tuple[int, str, list[int]]:
    parts = PurePosixPath(relative).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise PlanningApplyOutputRejected("operation evidence path is invalid")
    parent = handle.operation_fd
    opened: list[int] = []
    for part in parts[:-1]:
        parent = _open_directory_at(parent, part)
        opened.append(parent)
    return parent, parts[-1], opened


def _close_opened(opened: list[int]) -> None:
    for descriptor in reversed(opened):
        os.close(descriptor)


def _entry_stat_at(handle: _ApplyEvidenceHandle, relative: str) -> os.stat_result | None:
    parent, name, opened = _parent_fd(handle, relative)
    try:
        try:
            return os.stat(name, dir_fd=parent, follow_symlinks=False)
        except FileNotFoundError:
            return None
    finally:
        _close_opened(opened)


def _entry_exists_at(handle: _ApplyEvidenceHandle, relative: str) -> bool:
    return _entry_stat_at(handle, relative) is not None


def _read_private_file_at(handle: _ApplyEvidenceHandle, relative: str) -> bytes:
    parent, name, opened = _parent_fd(handle, relative)
    descriptor = -1
    try:
        descriptor = os.open(name, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=parent)
        metadata = os.fstat(descriptor)
        if (
            not stat.S_ISREG(metadata.st_mode)
            or metadata.st_uid != os.geteuid()
            or stat.S_IMODE(metadata.st_mode) != 0o600
        ):
            raise PlanningApplyOutputRejected("operation evidence is not private")
        chunks: list[bytes] = []
        while chunk := os.read(descriptor, 1024 * 1024):
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        _close_opened(opened)


def _write_all(descriptor: int, data: bytes) -> None:
    offset = 0
    while offset < len(data):
        offset += os.write(descriptor, data[offset:])
    os.fsync(descriptor)


def _write_private_no_replace_at(
    handle: _ApplyEvidenceHandle,
    relative: str,
    data: bytes,
) -> None:
    parent, name, opened = _parent_fd(handle, relative)
    descriptor = -1
    try:
        descriptor = os.open(
            name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=parent,
        )
        os.fchmod(descriptor, 0o600)
        _write_all(descriptor, data)
        os.fsync(parent)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        _close_opened(opened)


def _write_private_atomic_at(
    handle: _ApplyEvidenceHandle,
    relative: str,
    data: bytes,
) -> None:
    parent, name, opened = _parent_fd(handle, relative)
    temporary = f".{name}.{os.getpid()}.{os.urandom(8).hex()}"
    descriptor = -1
    try:
        descriptor = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=parent,
        )
        os.fchmod(descriptor, 0o600)
        _write_all(descriptor, data)
        os.close(descriptor)
        descriptor = -1
        os.replace(temporary, name, src_dir_fd=parent, dst_dir_fd=parent)
        os.fsync(parent)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        with suppress(FileNotFoundError):
            os.unlink(temporary, dir_fd=parent)
        _close_opened(opened)


def _mkdir_private_at(handle: _ApplyEvidenceHandle, relative: str) -> None:
    parent, name, opened = _parent_fd(handle, relative)
    try:
        os.mkdir(name, mode=0o700, dir_fd=parent)
        if not _owned_private_directory_at(parent, name):
            raise PlanningApplyOutputRejected("operation evidence is not private")
        os.fsync(parent)
    finally:
        _close_opened(opened)


def _owned_private_directory_at(parent_fd: int, name: str) -> bool:
    try:
        opened = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except OSError:
        return False
    return stat.S_ISDIR(opened.st_mode) and opened.st_uid == os.geteuid() and stat.S_IMODE(opened.st_mode) == 0o700


def _owned_private_subdirectory_at(handle: _ApplyEvidenceHandle, relative: str) -> bool:
    parent, name, opened = _parent_fd(handle, relative)
    try:
        return _owned_private_directory_at(parent, name)
    finally:
        _close_opened(opened)


def _owned_private_file_at(handle: _ApplyEvidenceHandle, relative: str) -> bool:
    opened = _entry_stat_at(handle, relative)
    if opened is None:
        return False
    return stat.S_ISREG(opened.st_mode) and opened.st_uid == os.geteuid() and stat.S_IMODE(opened.st_mode) == 0o600


def _owned_private_file(path: Path) -> bool:
    try:
        opened = path.stat(follow_symlinks=False)
    except OSError:
        return False
    return (
        stat.S_ISREG(opened.st_mode)
        and not path.is_symlink()
        and opened.st_uid == os.geteuid()
        and stat.S_IMODE(opened.st_mode) == 0o600
    )


def _list_directory_at(handle: _ApplyEvidenceHandle, relative: str = "") -> set[str]:
    if relative:
        parent, name, opened = _parent_fd(handle, relative)
        descriptor = _open_directory_at(parent, name)
    else:
        opened = []
        descriptor = os.dup(handle.operation_fd)
    try:
        return set(os.listdir(descriptor))  # noqa: PTH208 - descriptor-relative authority
    finally:
        os.close(descriptor)
        _close_opened(opened)


def _validate_existing_operation_evidence(handle: _ApplyEvidenceHandle) -> None:
    allowed = {
        "operation.json",
        "state.json",
        "attempts",
        "transaction",
        "commit.json",
        "publication.json",
    }
    if not _list_directory_at(handle) <= allowed:
        raise PlanningApplyOutputRejected("operation evidence contains unexpected entries")
    for required in ("operation.json", "state.json"):
        if not _owned_private_file_at(handle, required):
            raise PlanningApplyOutputRejected("operation evidence is not private")
    if not _owned_private_directory_at(handle.operation_fd, "attempts"):
        raise PlanningApplyOutputRejected("operation attempts are not private")
    for attempt in _list_directory_at(handle, "attempts"):
        if not _owned_private_file_at(handle, f"attempts/{attempt}"):
            raise PlanningApplyOutputRejected("operation attempt is not private")
    for optional in ("commit.json", "publication.json"):
        if _entry_exists_at(handle, optional) and not _owned_private_file_at(handle, optional):
            raise PlanningApplyOutputRejected("operation evidence is not private")
    if _entry_exists_at(handle, "transaction"):
        if not _owned_private_directory_at(handle.operation_fd, "transaction"):
            raise PlanningApplyOutputRejected("transaction evidence is not private")
        allowed_transaction = {"files", "managed-state", "git-index.bin", "backup-manifest.json"}
        if not _list_directory_at(handle, "transaction") <= allowed_transaction:
            raise PlanningApplyOutputRejected("transaction evidence contains unexpected entries")
        transaction_fd = _open_directory_at(handle.operation_fd, "transaction")
        try:
            for directory in ("files", "managed-state"):
                if not _owned_private_directory_at(transaction_fd, directory):
                    raise PlanningApplyOutputRejected("transaction directory is not private")
                for name in _list_directory_at(handle, f"transaction/{directory}"):
                    if not _owned_private_file_at(handle, f"transaction/{directory}/{name}"):
                        raise PlanningApplyOutputRejected("transaction evidence is not private")
        finally:
            os.close(transaction_fd)
        for filename in ("git-index.bin", "backup-manifest.json"):
            if not _owned_private_file_at(handle, f"transaction/{filename}"):
                raise PlanningApplyOutputRejected("transaction evidence is not private")


def _set_operation_state(
    handle: _ApplyEvidenceHandle,
    operation: PlanningApplyOperation,
    state: str,
) -> None:
    _write_private_atomic_at(
        handle,
        "state.json",
        _canonical_json_bytes({
            "operation_id": operation.operation_id,
            "state": state,
        }),
    )


def _load_operation_state(
    handle: _ApplyEvidenceHandle,
    operation: PlanningApplyOperation,
) -> str:
    try:
        state_bytes = _read_private_file_at(handle, "state.json")
        state = json.loads(state_bytes)
    except (OSError, ValueError, json.JSONDecodeError):
        raise PlanningApplyRestoreMismatch("operation state is unreadable") from None
    if (
        not isinstance(state, dict)
        or set(state) != {"operation_id", "state"}
        or state.get("operation_id") != operation.operation_id
        or not isinstance(state.get("state"), str)
        or state.get("state") not in _DURABLE_OPERATION_STATES
        or _canonical_json_bytes(state) != state_bytes
    ):
        raise PlanningApplyRestoreMismatch("operation state is invalid")
    return state["state"]


def _record_operation_attempt(
    handle: _ApplyEvidenceHandle,
    operation: PlanningApplyOperation,
) -> None:
    if not _owned_private_directory_at(handle.operation_fd, "attempts"):
        raise PlanningApplyOutputRejected("operation attempt evidence is unsafe")
    for number in range(1, 10_001):
        relative = f"attempts/{number:06d}.json"
        if _entry_exists_at(handle, relative):
            continue
        _write_private_no_replace_at(
            handle,
            relative,
            _canonical_json_bytes({
                "attempt": number,
                "operation_id": operation.operation_id,
            }),
        )
        return
    raise PlanningApplyOutputRejected("operation attempt bound exceeded")


def _run_git(
    repo_root: Path,
    argv: tuple[str, ...],
    *,
    check: bool = False,
) -> GitCommandResult:
    full_argv = ("git", "-C", repo_root.as_posix(), *argv)
    validate_planning_git_argv(("git", *argv))
    completed = subprocess.run(
        full_argv,
        check=False,
        capture_output=True,
    )
    result = GitCommandResult(
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
    if check and result.returncode != 0:
        raise RuntimeError("planning Git command failed")
    return result


def _git_text(repo_root: Path, *argv: str) -> str | None:
    result = _run_git(repo_root, tuple(argv))
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8", errors="strict").strip()


def _git_blob_oid(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def load_expected_planning_targets(
    repo_root: Path,
    expected_head: str,
    canonical_target_paths: tuple[str, str, str],
) -> ExpectedPlanningTargets:
    if _SHA40.fullmatch(expected_head) is None:
        raise ValueError("expected planning HEAD is invalid")
    documents: dict[str, bytes] = {}
    blob_oids: dict[str, str] = {}
    for relative in canonical_target_paths:
        _safe_repo_relative(relative)
        blob_oid = _git_text(repo_root, "rev-parse", f"{expected_head}:{relative}")
        content = _run_git(repo_root, ("show", f"{expected_head}:{relative}"))
        if (
            blob_oid is None
            or _SHA40.fullmatch(blob_oid) is None
            or content.returncode != 0
            or _git_blob_oid(content.stdout) != blob_oid
        ):
            raise ValueError("expected planning target cannot be proven")
        documents[PurePosixPath(relative).name] = content.stdout
        blob_oids[relative] = blob_oid
    if set(documents) != {"design.md", "plan.md", "requirement.md"}:
        raise ValueError("expected planning target set is incomplete")
    return ExpectedPlanningTargets(
        documents=MappingProxyType(documents),
        blob_oids=MappingProxyType(blob_oids),
    )


def _load_expected_companion_preimage(
    operation: PlanningApplyOperation,
    repo_root: Path,
) -> tuple[bool, bytes, str | None]:
    relative = operation.companion_target_path
    listing = _run_git(
        repo_root,
        ("ls-tree", "-z", operation.expected_head, "--", relative),
    )
    if listing.returncode != 0:
        raise ValueError("expected companion preimage cannot be proven")
    if listing.stdout == b"":
        return False, b"", None
    try:
        metadata, observed_path = listing.stdout.removesuffix(b"\0").split(b"\t", 1)
        mode, object_type, oid_bytes = metadata.split(b" ")
        oid = oid_bytes.decode("ascii")
    except (UnicodeDecodeError, ValueError) as error:
        raise ValueError("expected companion preimage cannot be proven") from error
    if (
        mode not in (b"100644", b"100755")
        or object_type != b"blob"
        or observed_path != relative.encode("utf-8")
        or _SHA40.fullmatch(oid) is None
    ):
        raise ValueError("expected companion preimage cannot be proven")
    content = _run_git(repo_root, ("cat-file", "blob", oid))
    if content.returncode != 0 or _git_blob_oid(content.stdout) != oid:
        raise ValueError("expected companion preimage cannot be proven")
    return True, content.stdout, oid


def planning_apply_resume_available(
    operation: PlanningApplyOperation,
    *,
    output_guard: OutputDirectoryGuard | None = None,
    output_dir: Path | None = None,
) -> bool:
    output_guard = output_guard or _guard_from_current_output(output_dir)
    output_fd = _open_guarded_output(output_guard)
    try:
        try:
            existing = os.stat(
                f"planning-apply-{operation.operation_id}",
                dir_fd=output_fd,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            return False
        if not stat.S_ISDIR(existing.st_mode):
            raise PlanningApplyOutputRejected("operation identity collision")
    finally:
        os.close(output_fd)
    handle = record_planning_apply_operation(operation, output_guard=output_guard)
    try:
        return _entry_exists_at(handle, "commit.json") or _entry_exists_at(handle, "transaction")
    finally:
        handle.close()


def _remote_head_observation(
    repo_root: Path,
    branch: str,
) -> tuple[Literal["present", "absent", "unavailable"], str | None]:
    result = _run_git(repo_root, ("ls-remote", "--heads", "origin", f"refs/heads/{branch}"))
    if result.returncode != 0:
        return "unavailable", None
    text = result.stdout.decode("ascii", errors="strict").strip()
    if not text:
        return "absent", None
    value = text.split()[0]
    if _SHA40.fullmatch(value) is None:
        return "unavailable", None
    return "present", value


def _remote_head(repo_root: Path, branch: str) -> str | None:
    disposition, value = _remote_head_observation(repo_root, branch)
    return value if disposition == "present" else None


def _push_operation_commit_cas(
    *,
    repo_root: Path,
    branch: str,
    expected_remote_head: str,
    local_commit: str,
    local_tree: str,
) -> GitCommandResult:
    if (
        _SHA40.fullmatch(expected_remote_head) is None
        or _SHA40.fullmatch(local_commit) is None
        or _SHA40.fullmatch(local_tree) is None
        or not branch
        or branch.startswith("-")
        or any(character.isspace() for character in branch)
        or _git_text(repo_root, "check-ref-format", "--branch", branch) != branch
        or _git_text(repo_root, "rev-parse", "HEAD") != local_commit
        or _git_text(repo_root, "rev-parse", f"{local_commit}^") != expected_remote_head
        or _git_text(repo_root, "rev-parse", f"{local_commit}^{{tree}}") != local_tree
    ):
        raise PlanningApplyUnsafeGitCommand("planning publication CAS proof failed")
    destination = f"refs/heads/{branch}"
    lease = f"--force-with-lease={destination}:{expected_remote_head}"
    refspec = f"{local_commit}:{destination}"
    completed = subprocess.run(
        ("git", "-C", repo_root.as_posix(), "push", lease, "origin", refspec),
        check=False,
        capture_output=True,
    )
    return GitCommandResult(
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def _cas_failure_result(
    operation: PlanningApplyOperation,
    *,
    repo_root: Path,
    local_commit: str,
    local_tree: str,
) -> PlanningApplyExecution | None:
    disposition, remote = _remote_head_observation(repo_root, operation.branch)
    if disposition == "present" and remote == local_commit:
        remote_tree = _git_text(repo_root, "rev-parse", f"{remote}^{{tree}}")
        if remote_tree == local_tree:
            return None
    if disposition == "present" and remote == operation.expected_head:
        return _operation_result(
            operation,
            status="publication_pending",
            reason="push_failed",
            local_commit=local_commit,
            local_tree=local_tree,
            remote_commit=remote,
        )
    if disposition in {"absent", "present"}:
        return _operation_result(
            operation,
            status="blocked_remote_diverged",
            reason="remote_diverged",
            local_commit=local_commit,
            local_tree=local_tree,
            remote_commit=remote,
        )
    return _operation_result(
        operation,
        status="publication_pending",
        reason="push_failed",
        local_commit=local_commit,
        local_tree=local_tree,
    )


def _changed_paths(repo_root: Path, *, cached: bool = False) -> set[str] | None:
    argv = ["diff"]
    if cached:
        argv.append("--cached")
    argv.extend(["--name-only", "-z", "--no-renames"])
    result = _run_git(repo_root, tuple(argv))
    if result.returncode != 0:
        return None
    return {item.decode("utf-8") for item in result.stdout.split(b"\0") if item}


def _operation_result(
    operation: PlanningApplyOperation,
    *,
    status: PlanningApplyStatus,
    reason: str,
    local_commit: str | None = None,
    local_tree: str | None = None,
    remote_commit: str | None = None,
) -> PlanningApplyExecution:
    return PlanningApplyExecution(
        status=status,
        reason=reason,
        operation_id=operation.operation_id,
        decision_artifact_path=operation.decision_artifact_path,
        local_commit=local_commit,
        local_tree=local_tree,
        remote_commit=remote_commit,
    )


def _apply_targets_match_snapshots(
    operation: PlanningApplyOperation,
    repo_root: Path,
    file_snapshots: Mapping[str, FileSnapshot],
) -> bool:
    if (
        _git_text(repo_root, "branch", "--show-current") != operation.branch
        or _git_text(repo_root, "rev-parse", "HEAD") != operation.expected_head
    ):
        return False
    for relative in (*operation.canonical_target_paths, operation.companion_target_path):
        expected = file_snapshots.get(relative)
        if expected is None:
            return False
        try:
            if snapshot_regular_file(repo_root / relative) != expected:
                return False
        except (OSError, ValueError):
            return False
    return True


def _finalize_transaction_cleanup(
    handle: _ApplyEvidenceHandle,
    operation: PlanningApplyOperation,
    *,
    final_state: str,
) -> None:
    _remove_transaction_backup(handle)
    if _entry_exists_at(handle, "transaction"):
        raise ValueError("pre-mutation transaction backup was not removed")
    os.fsync(handle.operation_fd)
    _set_operation_state(handle, operation, final_state)


def _discard_pre_mutation_backup(
    handle: _ApplyEvidenceHandle,
    operation: PlanningApplyOperation,
    *,
    final_state: str,
) -> None:
    _finalize_transaction_cleanup(
        handle,
        operation,
        final_state=final_state,
    )


def _validate_no_transaction_state(
    handle: _ApplyEvidenceHandle,
    operation: PlanningApplyOperation,
) -> None:
    state = _load_operation_state(handle, operation)
    if state not in _NO_TRANSACTION_START_STATES or _entry_exists_at(handle, "publication.json"):
        raise PlanningApplyRestoreMismatch("operation state cannot start a transaction")


def execute_planning_apply_transaction(
    operation: PlanningApplyOperation,
    *,
    repo_root: Path,
    output_guard: OutputDirectoryGuard | None = None,
    output_dir: Path | None = None,
    validation_runner: Callable[[], object],
    sync_runner: Callable[[], object],
    fault_hook: Callable[[str], None] | None = None,
) -> PlanningApplyExecution:
    output_guard = output_guard or _guard_from_current_output(output_dir)
    try:
        handle = record_planning_apply_operation(
            operation,
            output_guard=output_guard,
            capture_hook=fault_hook,
        )
    except (OSError, PlanningApplyOutputRejected, ValueError):
        return _operation_result(
            operation,
            status="rejected",
            reason="apply_output_rejected",
        )
    try:
        return _execute_planning_apply_transaction(
            operation,
            repo_root=repo_root,
            handle=handle,
            validation_runner=validation_runner,
            sync_runner=sync_runner,
            fault_hook=fault_hook,
        )
    finally:
        handle.close()


def _execute_planning_apply_transaction(
    operation: PlanningApplyOperation,
    *,
    repo_root: Path,
    handle: _ApplyEvidenceHandle,
    validation_runner: Callable[[], object],
    sync_runner: Callable[[], object],
    fault_hook: Callable[[str], None] | None,
) -> PlanningApplyExecution:
    has_commit = _entry_exists_at(handle, "commit.json")
    has_transaction = _entry_exists_at(handle, "transaction")
    if not has_commit and not has_transaction:
        try:
            _validate_no_transaction_state(handle, operation)
        except PlanningApplyRestoreMismatch:
            return _operation_result(
                operation,
                status="recovery_required",
                reason="restore_mismatch",
            )
    try:
        _record_operation_attempt(handle, operation)
    except (OSError, PlanningApplyOutputRejected):
        return _operation_result(
            operation,
            status="rejected",
            reason="apply_output_rejected",
        )
    if has_commit:
        return _resume_publication(operation, repo_root=repo_root, handle=handle, fault_hook=fault_hook)
    if has_transaction:
        return _recover_interrupted_transaction(
            operation,
            repo_root=repo_root,
            handle=handle,
        )
    if _git_text(repo_root, "rev-parse", "HEAD") != operation.expected_head:
        return _operation_result(operation, status="stale", reason="apply_target_changed")
    if _git_text(repo_root, "branch", "--show-current") != operation.branch:
        return _operation_result(operation, status="stale", reason="apply_target_changed")
    if _git_bound_targets_are_stale(operation, repo_root):
        return _operation_result(operation, status="stale", reason="apply_target_changed")
    try:
        expected_companion = _load_expected_companion_preimage(operation, repo_root)
    except (OSError, ValueError):
        return _operation_result(
            operation,
            status="blocked",
            reason="git_preflight_blocked",
        )
    companion_path = repo_root / operation.companion_target_path
    decision_parent = (repo_root / operation.decision_artifact_path).parent
    if not decision_parent.is_dir() or decision_parent.is_symlink():
        return _operation_result(
            operation,
            status="rejected",
            reason="apply_output_rejected",
        )

    try:
        index_snapshot = snapshot_git_index(repo_root)
    except (OSError, ValueError):
        return _operation_result(operation, status="blocked", reason="git_preflight_blocked")
    try:
        managed_snapshot = snapshot_managed_sync_state(repo_root)
    except ValueError:
        return _operation_result(
            operation,
            status="blocked",
            reason="managed_state_snapshot_rejected",
        )
    except OSError:
        return _operation_result(operation, status="blocked", reason="git_preflight_blocked")
    try:
        file_snapshots = {path: snapshot_regular_file(repo_root / path) for path in operation.canonical_target_paths}
        companion_snapshot = snapshot_regular_file(companion_path)
        file_snapshots[operation.companion_target_path] = companion_snapshot
    except (OSError, ValueError):
        return _operation_result(
            operation,
            status="rejected",
            reason="apply_output_rejected",
        )
    canonical_preimages_match = all(
        snapshot.existed
        and snapshot.data == operation.pre_apply_document_bytes[PurePosixPath(path).name]
        and _git_blob_oid(snapshot.data) == operation.pre_apply_target_blob_oids[path]
        for path, snapshot in ((path, file_snapshots[path]) for path in operation.canonical_target_paths)
    )
    expected_companion_existed, expected_companion_bytes, expected_companion_oid = expected_companion
    companion_preimage_matches = (
        companion_snapshot.existed == expected_companion_existed
        and companion_snapshot.data == expected_companion_bytes
        and (
            (not companion_snapshot.existed and expected_companion_oid is None)
            or (companion_snapshot.existed and _git_blob_oid(companion_snapshot.data) == expected_companion_oid)
        )
    )
    if (
        not canonical_preimages_match
        or not companion_preimage_matches
        or (
            operation.replacement_companion is not None
            and companion_snapshot.existed
            and companion_snapshot.data != operation.replacement_companion
        )
    ):
        return _operation_result(
            operation,
            status="stale",
            reason="apply_target_changed",
        )
    try:
        decision_path = repo_root / operation.decision_artifact_path
        decision_snapshot = snapshot_regular_file(decision_path)
        if decision_snapshot.existed:
            return _operation_result(
                operation,
                status="rejected",
                reason="operation_identity_collision",
            )
        _persist_transaction_backup(
            handle,
            operation,
            index_snapshot=index_snapshot,
            file_snapshots=file_snapshots,
            decision_snapshot=decision_snapshot,
            managed_snapshot=managed_snapshot,
        )
        _set_operation_state(handle, operation, "BACKED_UP")
    except (OSError, ValueError):
        return _operation_result(operation, status="blocked", reason="git_preflight_blocked")

    mutation_started = False
    failure_reason = "planning_commit_failed"
    committed = False
    local_commit: str | None = None
    local_tree: str | None = None
    try:
        if fault_hook is not None:
            fault_hook("after_operation_recorded")
        if not _apply_targets_match_snapshots(operation, repo_root, file_snapshots):
            try:
                _discard_pre_mutation_backup(
                    handle,
                    operation,
                    final_state="OPERATION_RECORDED",
                )
            except (OSError, ValueError):
                return _operation_result(
                    operation,
                    status="recovery_required",
                    reason="restore_mismatch",
                )
            return _operation_result(
                operation,
                status="stale",
                reason="apply_target_changed",
            )
        try:
            _set_operation_state(handle, operation, "MUTATING")
        except (OSError, ValueError):
            return _operation_result(
                operation,
                status="recovery_required",
                reason="restore_mismatch",
            )
        mutation_started = True
        _atomic_write_exact(decision_path, operation.human_decision_bytes, mode=0o600)
        if fault_hook is not None:
            fault_hook("after_decision_write")
        if operation.decision == "approved" and operation.mode == "archive-candidate":
            for filename, checkpoint in (
                ("requirement.md", "after_requirement_replace"),
                ("design.md", "after_design_replace"),
                ("plan.md", "after_plan_replace"),
            ):
                replacement = operation.replacement_documents.get(filename)
                if replacement is None:
                    raise _ApplyFailure("adoption_semantic_mutation")
                relative = _path_for_filename(operation.canonical_target_paths, filename)
                mode = file_snapshots[relative].mode
                _atomic_write_exact(repo_root / relative, replacement, mode=mode)
                if fault_hook is not None:
                    fault_hook(checkpoint)
            for relative in operation.canonical_target_paths:
                filename = PurePosixPath(relative).name
                if (repo_root / relative).read_bytes() != operation.replacement_documents[filename]:
                    raise _ApplyFailure("candidate_parity_failed")
        if operation.replacement_companion is not None:
            if not companion_snapshot.existed:
                _atomic_write_exact(
                    companion_path,
                    operation.replacement_companion,
                    mode=0o644,
                )
            if fault_hook is not None:
                fault_hook("after_companion_write")
            if companion_path.read_bytes() != operation.replacement_companion:
                raise _ApplyFailure("candidate_parity_failed")
            if fault_hook is not None:
                fault_hook("after_companion_parity")
        if _git_bound_targets_are_stale(operation, repo_root):
            raise _ApplyFailure("apply_target_changed")
        if fault_hook is not None:
            fault_hook("after_canonical_proof")

        validation = validation_runner()
        errors = getattr(getattr(validation, "report", None), "errors", None)
        if errors is None or errors:
            raise _ApplyFailure("specdock_validation_failed")
        if fault_hook is not None:
            fault_hook("after_validation")
        _set_operation_state(handle, operation, "VALIDATED")

        sync = sync_runner()
        if (
            getattr(sync, "artifact_failure", None) is not None
            or getattr(getattr(sync, "state", None), "deps_preflight_error", None) is not None
        ):
            raise _ApplyFailure("specdock_sync_failed")
        if not _sync_write_result_is_scoped(sync, repo_root):
            raise _ApplyFailure("specdock_sync_failed")
        if fault_hook is not None:
            fault_hook("after_sync")
        _set_operation_state(handle, operation, "SYNCED")

        expected_paths = {operation.decision_artifact_path}
        if operation.decision == "approved" and operation.mode == "archive-candidate":
            expected_paths.update(
                relative
                for relative in operation.canonical_target_paths
                if (repo_root / relative).read_bytes() != file_snapshots[relative].data
            )
        if operation.replacement_companion is not None and not companion_snapshot.existed:
            expected_paths.add(operation.companion_target_path)
        changed = _changed_paths(repo_root)
        untracked = _git_text(
            repo_root,
            "ls-files",
            "--others",
            "--exclude-standard",
            "-z",
        )
        if changed is None:
            raise _ApplyFailure("apply_diff_out_of_scope")
        actual = set(changed)
        if untracked:
            actual.update(item for item in untracked.split("\0") if item)
        if actual != expected_paths:
            raise _ApplyFailure("apply_diff_out_of_scope")
        if fault_hook is not None:
            fault_hook("after_diff_proof")

        add_result = _run_git(repo_root, ("add", "--", *sorted(expected_paths)))
        if add_result.returncode != 0 or _changed_paths(repo_root, cached=True) != expected_paths:
            raise _ApplyFailure("planning_commit_failed")
        local_tree = _git_text(repo_root, "write-tree")
        if local_tree is None:
            raise _ApplyFailure("planning_commit_failed")
        if fault_hook is not None:
            fault_hook("after_index_stage")
            fault_hook("before_commit")
        _set_operation_state(handle, operation, "STAGED")

        subject = (
            f"docs({operation.issue_id}): adopt reviewed planning"
            if operation.decision == "approved"
            else f"docs({operation.issue_id}): record rejected planning decision"
        )
        _run_git(
            repo_root,
            (
                "commit",
                "-m",
                subject,
                "-m",
                f"SpecDock-Planning-Operation: {operation.operation_id}",
            ),
        )
        current_head = _git_text(repo_root, "rev-parse", "HEAD")
        if current_head == operation.expected_head:
            raise _ApplyFailure("planning_commit_failed")
        if current_head is None:
            raise PlanningApplyRestoreMismatch("unexpected local HEAD")
        local_commit = current_head
        parent = _git_text(repo_root, "rev-parse", f"{local_commit}^")
        commit_tree = _git_text(repo_root, "rev-parse", f"{local_commit}^{{tree}}")
        commit_paths = _git_text(
            repo_root,
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            local_commit,
        )
        trailer = _git_text(repo_root, "show", "-s", "--format=%B", local_commit)
        if (
            parent != operation.expected_head
            or commit_tree != local_tree
            or set(commit_paths.splitlines() if commit_paths else ()) != expected_paths
            or trailer is None
            or f"SpecDock-Planning-Operation: {operation.operation_id}" not in trailer
        ):
            raise PlanningApplyRestoreMismatch("operation commit proof failed")
        committed = True
        _write_private_no_replace_at(
            handle,
            "commit.json",
            _canonical_json_bytes({
                "operation_id": operation.operation_id,
                "local_commit": local_commit,
                "local_tree": local_tree,
                "decision": operation.decision,
            }),
        )
        _set_operation_state(handle, operation, "COMMITTED")
        if fault_hook is not None:
            fault_hook("after_commit")
        post_commit_status = _git_text(repo_root, "status", "--porcelain=v2", "-z")
        if post_commit_status != "":
            return _operation_result(
                operation,
                status="recovery_required",
                reason="post_commit_workspace_changed",
                local_commit=local_commit,
                local_tree=local_tree,
            )
        _remove_transaction_backup(handle)
        if fault_hook is not None:
            fault_hook("before_push")
        push = _push_operation_commit_cas(
            repo_root=repo_root,
            branch=operation.branch,
            expected_remote_head=operation.expected_head,
            local_commit=local_commit,
            local_tree=local_tree,
        )
        if push.returncode != 0:
            failure = _cas_failure_result(
                operation,
                repo_root=repo_root,
                local_commit=local_commit,
                local_tree=local_tree,
            )
            if failure is not None:
                return failure
        if fault_hook is not None:
            fault_hook("after_push")
        _set_operation_state(handle, operation, "PUSHED")
        remote = _remote_head(repo_root, operation.branch)
        if fault_hook is not None:
            fault_hook("after_fetch")
        if remote != local_commit:
            return _operation_result(
                operation,
                status="publication_pending",
                reason="remote_parity_unconfirmed",
                local_commit=local_commit,
                local_tree=local_tree,
                remote_commit=remote,
            )
        remote_tree = _git_text(repo_root, "rev-parse", f"{remote}^{{tree}}")
        if remote_tree != local_tree:
            return _operation_result(
                operation,
                status="publication_pending",
                reason="remote_parity_unconfirmed",
                local_commit=local_commit,
                local_tree=local_tree,
                remote_commit=remote,
            )
        _record_publication(handle, operation, local_commit, local_tree)
        _set_operation_state(handle, operation, "REMOTE_PARITY")
        if operation.decision == "approved":
            return _operation_result(
                operation,
                status="ready",
                reason="adoption_published",
                local_commit=local_commit,
                local_tree=local_tree,
                remote_commit=remote,
            )
        return _operation_result(
            operation,
            status="rejected",
            reason="plan_rejected",
            local_commit=local_commit,
            local_tree=local_tree,
            remote_commit=remote,
        )
    except _ApplyFailure as error:
        failure_reason = error.reason
    except PlanningApplyRestoreMismatch:
        return _operation_result(
            operation,
            status="recovery_required",
            reason="restore_mismatch",
            local_commit=local_commit,
            local_tree=local_tree,
        )
    except Exception:
        if committed:
            return _operation_result(
                operation,
                status="publication_pending",
                reason="remote_parity_unconfirmed",
                local_commit=local_commit,
                local_tree=local_tree,
            )
        failure_reason = "planning_commit_failed"

    if not mutation_started:
        return _operation_result(operation, status="blocked", reason="git_preflight_blocked")
    try:
        _restore_transaction(
            operation,
            repo_root=repo_root,
            index_snapshot=index_snapshot,
            file_snapshots=file_snapshots,
            decision_snapshot=decision_snapshot,
            managed_snapshot=managed_snapshot,
            fault_hook=fault_hook,
        )
    except (OSError, PlanningApplyRestoreMismatch, ValueError):
        return _operation_result(
            operation,
            status="recovery_required",
            reason="restore_mismatch",
        )
    try:
        _finalize_transaction_cleanup(
            handle,
            operation,
            final_state="ROLLED_BACK",
        )
    except (OSError, ValueError):
        return _operation_result(
            operation,
            status="recovery_required",
            reason="restore_mismatch",
        )
    return _operation_result(operation, status="rolled_back", reason=failure_reason)


def _recover_interrupted_transaction(
    operation: PlanningApplyOperation,
    *,
    repo_root: Path,
    handle: _ApplyEvidenceHandle,
) -> PlanningApplyExecution:
    try:
        state = _load_operation_state(handle, operation)
    except PlanningApplyRestoreMismatch:
        return _operation_result(
            operation,
            status="recovery_required",
            reason="restore_mismatch",
        )
    if (
        state not in {"BACKED_UP", *_TRANSACTION_RESTORE_STATES}
        or _entry_exists_at(handle, "commit.json")
        or _entry_exists_at(handle, "publication.json")
    ):
        return _operation_result(
            operation,
            status="recovery_required",
            reason="restore_mismatch",
        )
    if state == "BACKED_UP":
        try:
            backup = _load_transaction_backup(
                handle,
                operation,
                repo_root=repo_root,
            )
        except (OSError, ValueError, PlanningApplyRestoreMismatch):
            return _operation_result(
                operation,
                status="recovery_required",
                reason="restore_mismatch",
            )
        if not _apply_targets_match_snapshots(operation, repo_root, backup.files):
            try:
                _discard_pre_mutation_backup(
                    handle,
                    operation,
                    final_state="OPERATION_RECORDED",
                )
            except (OSError, ValueError):
                return _operation_result(
                    operation,
                    status="recovery_required",
                    reason="restore_mismatch",
                )
            return _operation_result(
                operation,
                status="stale",
                reason="apply_target_changed",
            )
        if _remote_head(repo_root, operation.branch) != operation.expected_head:
            return _operation_result(
                operation,
                status="recovery_required",
                reason="restore_mismatch",
            )
        try:
            _discard_pre_mutation_backup(
                handle,
                operation,
                final_state="ROLLED_BACK",
            )
        except (OSError, ValueError):
            return _operation_result(
                operation,
                status="recovery_required",
                reason="restore_mismatch",
            )
        return _operation_result(
            operation,
            status="rolled_back",
            reason="planning_commit_failed",
        )
    if (
        _git_text(repo_root, "branch", "--show-current") != operation.branch
        or _git_text(repo_root, "rev-parse", "HEAD") != operation.expected_head
    ):
        return _operation_result(
            operation,
            status="recovery_required",
            reason="restore_mismatch",
        )
    try:
        backup = _load_transaction_backup(
            handle,
            operation,
            repo_root=repo_root,
        )
        _restore_transaction(
            operation,
            repo_root=repo_root,
            index_snapshot=backup.index,
            file_snapshots=backup.files,
            decision_snapshot=backup.decision,
            managed_snapshot=backup.managed,
            fault_hook=None,
        )
        if _remote_head(repo_root, operation.branch) != operation.expected_head:
            raise PlanningApplyRestoreMismatch("remote changed during recovery")
    except (OSError, ValueError, PlanningApplyRestoreMismatch):
        return _operation_result(
            operation,
            status="recovery_required",
            reason="restore_mismatch",
        )
    try:
        _finalize_transaction_cleanup(
            handle,
            operation,
            final_state="ROLLED_BACK",
        )
    except (OSError, ValueError):
        return _operation_result(
            operation,
            status="recovery_required",
            reason="restore_mismatch",
        )
    return _operation_result(
        operation,
        status="rolled_back",
        reason="planning_commit_failed",
    )


class _ApplyFailure(RuntimeError):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def _path_for_filename(paths: tuple[str, str, str], filename: str) -> str:
    matches = [path for path in paths if PurePosixPath(path).name == filename]
    if len(matches) != 1:
        raise _ApplyFailure("adoption_semantic_mutation")
    return matches[0]


def _git_bound_targets_are_stale(
    operation: PlanningApplyOperation,
    repo_root: Path,
) -> bool:
    if operation.mode != "git-bound":
        return False
    for relative in operation.canonical_target_paths:
        expected = operation.pre_apply_target_blob_oids.get(relative)
        actual = _git_text(
            repo_root,
            "hash-object",
            "--",
            relative,
        )
        reviewed = _git_text(
            repo_root,
            "rev-parse",
            f"{operation.expected_head}:{relative}",
        )
        if expected is None or actual != expected or reviewed != expected:
            return True
    return False


def _restore_transaction(
    operation: PlanningApplyOperation,
    *,
    repo_root: Path,
    index_snapshot: GitIndexSnapshot,
    file_snapshots: Mapping[str, FileSnapshot],
    decision_snapshot: FileSnapshot,
    managed_snapshot: Mapping[str, ManagedStateEntry],
    fault_hook: Callable[[str], None] | None,
) -> None:
    if fault_hook is not None:
        fault_hook("during_restore")
    restore_managed_sync_state(repo_root, managed_snapshot)
    restore_regular_file(
        repo_root / operation.companion_target_path,
        file_snapshots[operation.companion_target_path],
    )
    for relative in reversed(operation.canonical_target_paths):
        restore_regular_file(repo_root / relative, file_snapshots[relative])
    restore_regular_file(repo_root / operation.decision_artifact_path, decision_snapshot)
    restore_git_index(repo_root, index_snapshot)
    if fault_hook is not None:
        fault_hook("after_restore")
    if _git_text(repo_root, "rev-parse", "HEAD") != operation.expected_head:
        raise PlanningApplyRestoreMismatch("HEAD changed during rollback")
    status = _git_text(repo_root, "status", "--porcelain=v2", "-z")
    if status != "":
        raise PlanningApplyRestoreMismatch("worktree changed during rollback")
    # Some Git builds refresh index stat data during a read-only status. Restore
    # the captured bytes once more so the transaction postcondition is byte-exact.
    restore_git_index(repo_root, index_snapshot)
    if snapshot_managed_sync_state(repo_root) != managed_snapshot:
        raise PlanningApplyRestoreMismatch("managed sync state restore mismatch")


def _resume_publication(
    operation: PlanningApplyOperation,
    *,
    repo_root: Path,
    handle: _ApplyEvidenceHandle,
    fault_hook: Callable[[str], None] | None,
) -> PlanningApplyExecution:
    try:
        commit_bytes = _read_private_file_at(handle, "commit.json")
        commit = json.loads(commit_bytes)
        if (
            not isinstance(commit, dict)
            or set(commit) != {"operation_id", "local_commit", "local_tree", "decision"}
            or commit.get("operation_id") != operation.operation_id
            or not isinstance(commit.get("local_commit"), str)
            or not isinstance(commit.get("local_tree"), str)
            or commit.get("decision") != operation.decision
            or _canonical_json_bytes(commit) != commit_bytes
        ):
            raise ValueError
        local_commit = commit["local_commit"]
        local_tree = commit["local_tree"]
    except (OSError, ValueError, json.JSONDecodeError):
        return _operation_result(
            operation,
            status="rejected",
            reason="operation_identity_collision",
        )
    commit_paths = _git_text(
        repo_root,
        "diff-tree",
        "--no-commit-id",
        "--name-only",
        "-r",
        local_commit,
    )
    trailer = _git_text(repo_root, "show", "-s", "--format=%B", local_commit)
    expected_paths = _expected_operation_commit_paths(operation, repo_root)
    decision_path = repo_root / operation.decision_artifact_path
    if (
        _SHA40.fullmatch(local_commit) is None
        or _SHA40.fullmatch(local_tree) is None
        or _git_text(repo_root, "rev-parse", "HEAD") != local_commit
        or _git_text(repo_root, "rev-parse", f"{local_commit}^") != operation.expected_head
        or _git_text(repo_root, "rev-parse", f"{local_commit}^{{tree}}") != local_tree
        or set(commit_paths.splitlines() if commit_paths else ()) != expected_paths
        or trailer is None
        or f"SpecDock-Planning-Operation: {operation.operation_id}" not in trailer
        or not _owned_private_file(decision_path)
        or decision_path.read_bytes() != operation.human_decision_bytes
        or _git_text(repo_root, "status", "--porcelain=v2", "-z") != ""
        or not _operation_documents_match_committed_state(operation, repo_root)
    ):
        return _operation_result(
            operation,
            status="recovery_required",
            reason="restore_mismatch",
        )
    remote_disposition, remote = _remote_head_observation(repo_root, operation.branch)
    if remote_disposition == "absent":
        return _operation_result(
            operation,
            status="blocked_remote_diverged",
            reason="remote_diverged",
            local_commit=local_commit,
            local_tree=local_tree,
        )
    if remote_disposition == "unavailable" or remote is None:
        return _operation_result(
            operation,
            status="publication_pending",
            reason="remote_parity_unconfirmed",
            local_commit=local_commit,
            local_tree=local_tree,
        )
    if remote == operation.expected_head:
        if fault_hook is not None:
            fault_hook("before_push")
        push = _push_operation_commit_cas(
            repo_root=repo_root,
            branch=operation.branch,
            expected_remote_head=operation.expected_head,
            local_commit=local_commit,
            local_tree=local_tree,
        )
        if push.returncode != 0:
            failure = _cas_failure_result(
                operation,
                repo_root=repo_root,
                local_commit=local_commit,
                local_tree=local_tree,
            )
            if failure is not None:
                return failure
        remote = _remote_head(repo_root, operation.branch)
    elif remote != local_commit:
        return _operation_result(
            operation,
            status="blocked_remote_diverged",
            reason="remote_diverged",
            local_commit=local_commit,
            local_tree=local_tree,
            remote_commit=remote,
        )
    if remote != local_commit or _git_text(repo_root, "rev-parse", f"{remote}^{{tree}}") != local_tree:
        return _operation_result(
            operation,
            status="publication_pending",
            reason="remote_parity_unconfirmed",
            local_commit=local_commit,
            local_tree=local_tree,
            remote_commit=remote,
        )
    _record_publication(handle, operation, local_commit, local_tree)
    _set_operation_state(handle, operation, "REMOTE_PARITY")
    _remove_transaction_backup(handle)
    return _operation_result(
        operation,
        status="ready" if operation.decision == "approved" else "rejected",
        reason="adoption_published" if operation.decision == "approved" else "plan_rejected",
        local_commit=local_commit,
        local_tree=local_tree,
        remote_commit=remote,
    )


def _expected_operation_commit_paths(
    operation: PlanningApplyOperation,
    repo_root: Path,
) -> set[str]:
    paths = {operation.decision_artifact_path}
    if operation.mode == "archive-candidate" and operation.decision == "approved":
        for relative in operation.canonical_target_paths:
            filename = PurePosixPath(relative).name
            if operation.replacement_documents.get(filename) != operation.pre_apply_document_bytes.get(filename):
                paths.add(relative)
    if operation.decision == "approved":
        reviewed_companion = _git_text(
            repo_root,
            "rev-parse",
            f"{operation.expected_head}:{operation.companion_target_path}",
        )
        if reviewed_companion is None:
            paths.add(operation.companion_target_path)
    return paths


def _operation_documents_match_committed_state(
    operation: PlanningApplyOperation,
    repo_root: Path,
) -> bool:
    for relative in operation.canonical_target_paths:
        filename = PurePosixPath(relative).name
        expected = operation.pre_apply_document_bytes.get(filename)
        if operation.mode == "archive-candidate" and operation.decision == "approved":
            expected = operation.replacement_documents.get(filename)
        if expected is None:
            return False
        try:
            if (repo_root / relative).read_bytes() != expected:
                return False
        except OSError:
            return False
    if operation.decision == "approved":
        try:
            companion = (repo_root / operation.companion_target_path).read_bytes()
        except OSError:
            return False
        if hashlib.sha256(companion).hexdigest() != operation.companion_sha256:
            return False
    return True


def _record_publication(
    handle: _ApplyEvidenceHandle,
    operation: PlanningApplyOperation,
    local_commit: str,
    local_tree: str,
) -> None:
    data = _canonical_json_bytes({
        "operation_id": operation.operation_id,
        "local_commit": local_commit,
        "local_tree": local_tree,
        "remote_commit": local_commit,
    })
    if _entry_exists_at(handle, "publication.json"):
        if _read_private_file_at(handle, "publication.json") != data:
            raise PlanningApplyOutputRejected("publication evidence collision")
        return
    _write_private_no_replace_at(handle, "publication.json", data)


def _persist_transaction_backup(
    handle: _ApplyEvidenceHandle,
    operation: PlanningApplyOperation,
    *,
    index_snapshot: GitIndexSnapshot,
    file_snapshots: Mapping[str, FileSnapshot],
    decision_snapshot: FileSnapshot,
    managed_snapshot: Mapping[str, ManagedStateEntry],
) -> None:
    _mkdir_private_at(handle, "transaction")
    _mkdir_private_at(handle, "transaction/files")
    _mkdir_private_at(handle, "transaction/managed-state")
    _write_private_no_replace_at(handle, "transaction/git-index.bin", index_snapshot.data)
    entries: list[dict[str, object]] = []
    for relative, snapshot in sorted(
        file_snapshots.items(),
        key=lambda item: item[0].encode("utf-8"),
    ):
        backup_name = f"{hashlib.sha256(relative.encode()).hexdigest()}.bin"
        _write_private_no_replace_at(handle, f"transaction/files/{backup_name}", snapshot.data)
        entries.append({
            "path": relative,
            "backup": backup_name,
            "existed": snapshot.existed,
            "mode": snapshot.mode,
            "sha256": snapshot.sha256,
        })
    manifest = {
        "operation_id": operation.operation_id,
        "index": {
            "mode": index_snapshot.mode,
            "sha256": index_snapshot.sha256,
        },
        "files": entries,
        "decision_artifact": {
            "path": operation.decision_artifact_path,
            "existed": decision_snapshot.existed,
        },
        "managed_state": [],
    }
    managed_entries = manifest["managed_state"]
    assert isinstance(managed_entries, list)
    for relative, managed_entry in sorted(
        managed_snapshot.items(),
        key=lambda item: item[0].encode("utf-8"),
    ):
        backup_name = f"{hashlib.sha256(relative.encode()).hexdigest()}.bin"
        backup_data = (
            managed_entry.data if managed_entry.kind == "file" else (managed_entry.target or "").encode("utf-8")
        )
        _write_private_no_replace_at(handle, f"transaction/managed-state/{backup_name}", backup_data)
        managed_entries.append({
            "path": relative,
            "backup": backup_name,
            "kind": managed_entry.kind,
            "mode": managed_entry.mode,
            "sha256": hashlib.sha256(backup_data).hexdigest(),
        })
    _write_private_no_replace_at(
        handle,
        "transaction/backup-manifest.json",
        _canonical_json_bytes(manifest),
    )


def _load_transaction_backup(
    handle: _ApplyEvidenceHandle,
    operation: PlanningApplyOperation,
    *,
    repo_root: Path,
) -> DurableTransactionBackup:
    if not _owned_private_directory_at(handle.operation_fd, "transaction") or not _owned_private_file_at(
        handle, "transaction/backup-manifest.json"
    ):
        raise ValueError("transaction backup is unsafe")
    manifest_bytes = _read_private_file_at(handle, "transaction/backup-manifest.json")
    manifest = json.loads(manifest_bytes)
    if (
        not isinstance(manifest, dict)
        or set(manifest)
        != {
            "operation_id",
            "index",
            "files",
            "decision_artifact",
            "managed_state",
        }
        or manifest.get("operation_id") != operation.operation_id
        or _canonical_json_bytes(manifest) != manifest_bytes
    ):
        raise ValueError("transaction backup manifest mismatch")

    index_value = manifest["index"]
    if (
        not isinstance(index_value, dict)
        or set(index_value) != {"mode", "sha256"}
        or isinstance(index_value.get("mode"), bool)
        or not isinstance(index_value.get("mode"), int)
        or not isinstance(index_value.get("sha256"), str)
        or _SHA256.fullmatch(index_value["sha256"]) is None
        or not _owned_private_file_at(handle, "transaction/git-index.bin")
    ):
        raise ValueError("transaction index backup mismatch")
    index_bytes = _read_private_file_at(handle, "transaction/git-index.bin")
    if hashlib.sha256(index_bytes).hexdigest() != index_value["sha256"]:
        raise ValueError("transaction index backup mismatch")
    index_snapshot = GitIndexSnapshot(
        path=_git_index_path(repo_root),
        data=index_bytes,
        mode=index_value["mode"],
        sha256=index_value["sha256"],
    )

    file_values = manifest["files"]
    if not isinstance(file_values, list):
        raise ValueError("transaction file backup mismatch")
    file_snapshots: dict[str, FileSnapshot] = {}
    expected_file_backups: set[str] = set()
    allowed_file_paths = {
        *operation.canonical_target_paths,
        operation.companion_target_path,
    }
    for value in file_values:
        if (
            not isinstance(value, dict)
            or set(value) != {"path", "backup", "existed", "mode", "sha256"}
            or not isinstance(value.get("path"), str)
            or value["path"] not in allowed_file_paths
            or value["path"] in file_snapshots
            or not isinstance(value.get("existed"), bool)
            or (value["path"] in operation.canonical_target_paths and value["existed"] is not True)
            or isinstance(value.get("mode"), bool)
            or not isinstance(value.get("mode"), int)
            or not isinstance(value.get("sha256"), str)
            or _SHA256.fullmatch(value["sha256"]) is None
        ):
            raise ValueError("transaction file backup mismatch")
        expected_backup = f"{hashlib.sha256(value['path'].encode()).hexdigest()}.bin"
        if value.get("backup") != expected_backup:
            raise ValueError("transaction file backup mismatch")
        backup_relative = f"transaction/files/{expected_backup}"
        if not _owned_private_file_at(handle, backup_relative):
            raise ValueError("transaction file backup mismatch")
        data = _read_private_file_at(handle, backup_relative)
        if hashlib.sha256(data).hexdigest() != value["sha256"]:
            raise ValueError("transaction file backup mismatch")
        expected_file_backups.add(expected_backup)
        file_snapshots[value["path"]] = FileSnapshot(
            existed=value["existed"],
            data=data,
            mode=value["mode"],
            sha256=value["sha256"],
        )
    if (
        set(file_snapshots) != allowed_file_paths
        or not _owned_private_subdirectory_at(handle, "transaction/files")
        or _list_directory_at(handle, "transaction/files") != expected_file_backups
    ):
        raise ValueError("transaction file backup inventory mismatch")

    decision_value = manifest["decision_artifact"]
    if (
        not isinstance(decision_value, dict)
        or set(decision_value) != {"path", "existed"}
        or decision_value.get("path") != operation.decision_artifact_path
        or decision_value.get("existed") is not False
    ):
        raise ValueError("transaction decision backup mismatch")
    decision_snapshot = FileSnapshot(
        existed=False,
        data=b"",
        mode=0,
        sha256=hashlib.sha256(b"").hexdigest(),
    )

    managed_values = manifest["managed_state"]
    if not isinstance(managed_values, list):
        raise ValueError("transaction managed backup mismatch")
    managed_snapshots: dict[str, ManagedStateEntry] = {}
    expected_managed_backups: set[str] = set()
    for value in managed_values:
        if (
            not isinstance(value, dict)
            or set(value) != {"path", "backup", "kind", "mode", "sha256"}
            or not isinstance(value.get("path"), str)
            or not _managed_path_is_allowed(value["path"])
            or value["path"] in managed_snapshots
            or value.get("kind") not in {"file", "directory", "symlink"}
            or isinstance(value.get("mode"), bool)
            or not isinstance(value.get("mode"), int)
            or not isinstance(value.get("sha256"), str)
            or _SHA256.fullmatch(value["sha256"]) is None
        ):
            raise ValueError("transaction managed backup mismatch")
        expected_backup = f"{hashlib.sha256(value['path'].encode()).hexdigest()}.bin"
        if value.get("backup") != expected_backup:
            raise ValueError("transaction managed backup mismatch")
        backup_relative = f"transaction/managed-state/{expected_backup}"
        if not _owned_private_file_at(handle, backup_relative):
            raise ValueError("transaction managed backup mismatch")
        data = _read_private_file_at(handle, backup_relative)
        if hashlib.sha256(data).hexdigest() != value["sha256"]:
            raise ValueError("transaction managed backup mismatch")
        kind = value["kind"]
        target = data.decode("utf-8", errors="strict") if kind == "symlink" else None
        managed_snapshots[value["path"]] = ManagedStateEntry(
            kind=kind,
            mode=value["mode"],
            data=data if kind == "file" else b"",
            target=target,
        )
        expected_managed_backups.add(expected_backup)
    if (
        not _owned_private_subdirectory_at(handle, "transaction/managed-state")
        or _list_directory_at(handle, "transaction/managed-state") != expected_managed_backups
    ):
        raise ValueError("transaction managed backup inventory mismatch")
    return DurableTransactionBackup(
        index=index_snapshot,
        files=MappingProxyType(file_snapshots),
        decision=decision_snapshot,
        managed=MappingProxyType(managed_snapshots),
    )


def _managed_path_is_allowed(value: str) -> bool:
    return value in _MANAGED_SYNC_FILES or value == _MANAGED_SYNC_TREE or value.startswith(f"{_MANAGED_SYNC_TREE}/")


def _unlink_at(handle: _ApplyEvidenceHandle, relative: str) -> None:
    parent, name, opened = _parent_fd(handle, relative)
    try:
        os.unlink(name, dir_fd=parent)
        os.fsync(parent)
    finally:
        _close_opened(opened)


def _rmdir_at(handle: _ApplyEvidenceHandle, relative: str) -> None:
    parent, name, opened = _parent_fd(handle, relative)
    try:
        os.rmdir(name, dir_fd=parent)
        os.fsync(parent)
    finally:
        _close_opened(opened)


def _remove_transaction_backup(handle: _ApplyEvidenceHandle) -> None:
    if not _entry_exists_at(handle, "transaction"):
        return
    if not _owned_private_subdirectory_at(handle, "transaction"):
        raise PlanningApplyOutputRejected("transaction evidence is unsafe")
    root_entries = _list_directory_at(handle, "transaction")
    allowed_root = {"files", "managed-state", "git-index.bin", "backup-manifest.json"}
    if not root_entries <= allowed_root:
        raise PlanningApplyOutputRejected("transaction evidence contains unexpected entries")
    for directory in ("files", "managed-state"):
        relative = f"transaction/{directory}"
        if relative.split("/")[-1] in root_entries:
            if not _owned_private_subdirectory_at(handle, relative):
                raise PlanningApplyOutputRejected("transaction evidence is unsafe")
            for name in _list_directory_at(handle, relative):
                child = f"{relative}/{name}"
                if not _owned_private_file_at(handle, child):
                    raise PlanningApplyOutputRejected("transaction evidence is unsafe")
                _unlink_at(handle, child)
            _rmdir_at(handle, relative)
    for filename in ("git-index.bin", "backup-manifest.json"):
        relative = f"transaction/{filename}"
        if _entry_exists_at(handle, relative):
            if not _owned_private_file_at(handle, relative):
                raise PlanningApplyOutputRejected("transaction evidence is unsafe")
            _unlink_at(handle, relative)
    _rmdir_at(handle, "transaction")


def snapshot_managed_sync_state(
    repo_root: Path,
) -> Mapping[str, ManagedStateEntry]:
    entries: dict[str, ManagedStateEntry] = {}
    total_bytes = 0

    def capture(path: Path) -> None:
        nonlocal total_bytes
        relative = path.relative_to(repo_root).as_posix()
        opened = path.lstat()
        mode = stat.S_IMODE(opened.st_mode)
        if stat.S_ISLNK(opened.st_mode):
            target = path.readlink().as_posix()
            total_bytes += len(target.encode("utf-8"))
            entries[relative] = ManagedStateEntry(
                kind="symlink",
                mode=mode,
                target=target,
            )
        elif stat.S_ISDIR(opened.st_mode):
            entries[relative] = ManagedStateEntry(kind="directory", mode=mode)
        elif stat.S_ISREG(opened.st_mode):
            data = path.read_bytes()
            total_bytes += len(data)
            entries[relative] = ManagedStateEntry(kind="file", mode=mode, data=data)
        else:
            raise ValueError("managed state contains an unsupported entry")
        if len(entries) > _MAX_MANAGED_ENTRIES or total_bytes > _MAX_MANAGED_BYTES:
            raise ValueError("managed state exceeds transaction bounds")

    for relative in _MANAGED_SYNC_FILES:
        path = repo_root / relative
        if path.exists() or path.is_symlink():
            capture(path)
    tree = repo_root / _MANAGED_SYNC_TREE
    if tree.exists() or tree.is_symlink():
        capture(tree)
        if tree.is_dir() and not tree.is_symlink():
            for path in sorted(tree.rglob("*"), key=lambda item: item.as_posix().encode()):
                capture(path)
    return MappingProxyType(entries)


def restore_managed_sync_state(
    repo_root: Path,
    snapshot: Mapping[str, ManagedStateEntry],
) -> None:
    for relative in _MANAGED_SYNC_FILES:
        _remove_any(repo_root / relative)
    _remove_any(repo_root / _MANAGED_SYNC_TREE)
    directories = [(relative, entry) for relative, entry in snapshot.items() if entry.kind == "directory"]
    for relative, entry in sorted(
        directories,
        key=lambda item: (len(PurePosixPath(item[0]).parts), item[0].encode()),
    ):
        path = repo_root / relative
        path.mkdir(parents=True, exist_ok=True)
        path.chmod(entry.mode)
    for relative, entry in sorted(
        snapshot.items(),
        key=lambda item: item[0].encode("utf-8"),
    ):
        if entry.kind == "directory":
            continue
        path = repo_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if entry.kind == "file":
            _atomic_write_exact(path, entry.data, mode=entry.mode)
        else:
            assert entry.target is not None
            path.symlink_to(entry.target)
    if snapshot_managed_sync_state(repo_root) != snapshot:
        raise PlanningApplyRestoreMismatch("managed sync state restore mismatch")


def _remove_any(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _sync_write_result_is_scoped(sync: object, repo_root: Path) -> bool:
    active_update = getattr(sync, "active_update", None)
    if active_update is not None and getattr(active_update, "applied", False):
        return False
    write_result = getattr(sync, "write_result", None)
    if write_result is None:
        return True
    allowed = set(_MANAGED_SYNC_FILES)
    for value in vars(write_result).values():
        if not isinstance(value, str):
            return False
        path = Path(value)
        if path.is_absolute():
            try:
                relative = path.relative_to(repo_root).as_posix()
            except ValueError:
                return False
        else:
            relative = path.as_posix()
        if relative not in allowed:
            return False
    return True
