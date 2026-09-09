"""Provider-owned installer lifecycle engine.

The engine is the only lifecycle mutation owner used by the public installer.
It deliberately keeps the public surface closed by constructing every result
through :mod:`provider_lifecycle.wire` and by using the CP1 descriptor/native
filesystem primitives for durable boundaries.
"""

from __future__ import annotations

import base64
import contextlib
from dataclasses import dataclass, replace
import hashlib
import os
from pathlib import Path
import secrets
import shlex
import stat
from typing import TYPE_CHECKING, Literal, cast

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

from spec_dock.provider_lifecycle.candidate import (
    CANDIDATE_VERSION,
    FIXED_DOMAINS,
    SLOT_MARKER_NAME,
    CandidateError,
    _is_generated_python_cache,
    capture_packaged_candidate,
    marker_bytes,
)
from spec_dock.provider_lifecycle.contracts import (
    ActiveState,
    CandidateIdentity,
    CompletionReceipt,
    InodeWitness,
    InstallationRecord,
    LifecycleAction,
    LifecycleRequest,
    LifecycleResult,
    Operation,
    RecordState,
    RepositoryBinding,
    SeedPolicy,
    StageOwner,
)
from spec_dock.provider_lifecycle.coordination import (
    RepositoryBusy,
    RepositoryCoordinationError,
    RepositoryCoordinationUnavailable,
    RepositoryLease,
    acquire_exclusive_repository_lease,
)
from spec_dock.provider_lifecycle.filesystem import (
    AtomicRenameUnavailable,
    DomainTreeIdentity,
    FilesystemSafetyError,
    NativeAtomicFilesystem,
    TreeEntry,
)
from spec_dock.provider_lifecycle.legacy_fixture import (
    classify_exact_legacy_workspace,
    load_legacy_fixture,
)
from spec_dock.provider_lifecycle.private_state import (
    ACTIVE_NAME,
    RECORD_TEMP_NAME,
    STAGE_ENTRY_NAMES,
    STAGE_NAME,
    STAGE_OWNER_NAME,
    STAGE_TARGET_PATHS,
    ActiveStateStore,
    CompletionReceiptStore,
    PrivateStateError,
    PrivateStateForeignError,
    StageStore,
    cleanup_token_for,
    repository_key_for,
    resolve_private_namespace,
    tuple_key_for,
)
from spec_dock.provider_lifecycle.wire import (
    WireValidationError,
    build_public_result,
    parse_installation_record,
    parse_slot_marker,
    serialize_installation_record,
)

TARGET_PATHS = (
    "spec-dock/docs",
    "spec-dock/templates",
    "spec-dock/system",
    "spec-dock/scripts",
    ".agents/skills/spec-dock",
    ".agents/skills/spec-dock-grill-with-docs",
)
SEED_PATHS = ("spec-dock/.gitignore", ".github/workflows/ci.yml")
LIFECYCLE_GUIDANCE = (
    "Run continuation.next_command to resume the exact lifecycle operation.",
    "Do not switch operation, candidate package, or seed policy.",
)
CLEANUP_FAILED_GUIDANCE = (
    "Run continuation.next_command to retry owned stage cleanup.",
    "No lifecycle request is pending after cleanup.",
    "The requested terminal tooling state is already durable.",
)
CLEANUP_FAILED_DEFERRED_GUIDANCE = (
    "Run continuation.next_command to retry owned stage cleanup.",
    "After cleanup succeeds, run continuation.after_cleanup_command.",
    "The requested terminal tooling state is already durable.",
)
CLEANUP_COMPLETED_GUIDANCE = (
    "Owned provider stage cleanup completed; no lifecycle operation was executed.",
    "No lifecycle operation is pending.",
)
CLEANUP_COMPLETED_DEFERRED_GUIDANCE = (
    "Owned provider stage cleanup completed; no lifecycle operation was executed.",
    "Run continuation.next_command to execute the preserved requested operation.",
)
PHASES = (
    "request-validation",
    "preflight",
    "candidate-staging",
    "bootstrap-container",
    "publish-incomplete-record",
    "publish-docs",
    "publish-templates",
    "publish-system",
    "publish-scripts",
    "publish-slot-spec-dock",
    "publish-slot-spec-dock-grill-with-docs",
    "create-seed-spec-dock-gitignore",
    "create-seed-consumer-ci",
    "detach-docs",
    "detach-templates",
    "detach-system",
    "detach-scripts",
    "detach-slot-spec-dock",
    "detach-slot-spec-dock-grill-with-docs",
    "verify-target",
    "publish-terminal-record",
    "cleanup-stage",
    "complete",
)
FAULT_POINTS = frozenset(
    {
        "private-top-mkdir",
        "private-top-fsync",
        "private-repo-mkdir",
        "private-repo-fsync",
        "active-temp-open",
        "active-temp-write",
        "active-temp-fsync",
        "active-temp-rename",
        "active-parent-fsync",
        "stage-mkdir",
        "stage-owner-write",
        "stage-owner-fsync",
        "stage-parent-fsync",
        "bootstrap-container-mkdir",
        "bootstrap-container-fsync",
        "record-temp-open",
        "record-temp-write",
        "record-temp-fsync",
        "record-publish-no-replace",
        "record-publish-exchange",
        "record-parent-fsync",
        "record-exchange-residue-unlink",
        "record-temp-parent-fsync",
        "source-parent-fsync",
        "target-parent-fsync",
        "target-verify",
        "stage-remove",
        "receipt-temp-open",
        "receipt-temp-write",
        "receipt-temp-fsync",
        "receipt-temp-rename",
        "receipt-parent-fsync",
        "active-expected-unlink",
        "active-expected-parent-fsync",
        "response-loss",
    }
    | {
        f"stage-entry-{name}-{operation}"
        for name in STAGE_ENTRY_NAMES
        for operation in ("create", "write", "fsync", "remove")
    }
    | {
        f"{kind}-{name}-{operation}"
        for kind in ("root", "slot")
        for name in ("docs", "templates", "system", "scripts", "spec-dock", "spec-dock-grill-with-docs")
        for operation in ("publish-or-detach",)
    }
    | {
        f"seed-{name}-{operation}"
        for name in ("spec-dock-gitignore", "consumer-ci")
        for operation in ("no-replace-create", "parent-fsync")
    }
)


class LifecycleEngineError(RuntimeError):
    """Base class for engine failures that are safe to expose as Wire rows."""


class _InjectedFailure(OSError):
    def __init__(self, point: str) -> None:
        super().__init__(f"fault injected at {point}")
        self.point = point


class _AdmissionFailure(LifecycleEngineError):
    def __init__(
        self,
        code: str,
        *,
        phase: str = "preflight",
        last_completed_phase: str = "request-validation",
        operation: str | None = None,
        candidate_digest: str | None = None,
        seed_policy: str | None = None,
    ) -> None:
        super().__init__(code)
        self.code = code
        self.phase = phase
        self.last_completed_phase = last_completed_phase
        self.operation = operation
        self.candidate_digest = candidate_digest
        self.seed_policy = seed_policy


class _LifecycleFailure(LifecycleEngineError):
    def __init__(self, point: str, *, cause: BaseException | None = None) -> None:
        super().__init__(point)
        self.point = point
        self.cause = cause


@dataclass(frozen=True, slots=True)
class FaultInjector:
    """Small fixed-ID fault seam used by the CP2 campaign tests."""

    points: frozenset[str] = frozenset()

    def __init__(self, points: Sequence[str] | str = ()) -> None:
        values = (points,) if isinstance(points, str) else tuple(points)
        unknown = set(values) - FAULT_POINTS
        if unknown:
            raise ValueError(f"unknown provider lifecycle fault point: {sorted(unknown)}")
        object.__setattr__(self, "points", frozenset(values))

    def check(self, point: str) -> None:
        if point in self.points:
            raise _InjectedFailure(point)


@dataclass(frozen=True, slots=True)
class _ObservedTarget:
    path: str
    kind: str
    witness: InodeWitness | None
    tree: DomainTreeIdentity | None
    owned: bool = False
    current: bool = False


@dataclass(frozen=True, slots=True)
class _LifecycleContext:
    request: LifecycleRequest
    operation: str
    candidate: CandidateIdentity | None
    candidate_digest: str
    seed_policy: str
    result_family: str
    active: ActiveState
    original_record: Mapping[str, object]
    originals: tuple[_ObservedTarget, ...]
    desired_invocation: Mapping[str, str]
    cleanup_invocation: Mapping[str, str]
    terminal_payload: bytes
    owner: StageOwner
    stage_reused: bool = False


def _operation_from_request(request: LifecycleRequest) -> str:
    if request.operation in {"install", "update", "uninstall"}:
        return cast("str", request.operation)
    if request.specs_mode in {"keep", "remove"}:
        return "uninstall"
    return "install"


def _seed_from_request(request: LifecycleRequest, operation: str) -> str:
    if request.seed_policy in {"create-if-absent", "preserve-only"}:
        return cast("str", request.seed_policy)
    return "preserve-only" if operation != "install" else "create-if-absent"


def _quoted_target(target: str) -> str:
    return shlex.join([target])


def _desired_invocation(request: LifecycleRequest, *, force: bool | None = None) -> dict[str, str]:
    operation = _operation_from_request(request)
    if operation == "install":
        invocation_id = "init-force" if force else "init"
        command = f"spec-dock {'init --force' if force else 'init'} -- {_quoted_target(request.target)}"
    elif operation == "update":
        invocation_id = "update"
        command = f"spec-dock update -- {_quoted_target(request.target)}"
    elif request.mode == "dry-run":
        invocation_id = "uninstall-dry-run-keep" if request.specs_mode == "keep" else "uninstall-dry-run"
        flag = " --keep-specs" if request.specs_mode == "keep" else ""
        command = f"spec-dock uninstall{flag} -- {_quoted_target(request.target)}"
    else:
        invocation_id = "uninstall-apply-keep" if request.specs_mode == "keep" else "uninstall-apply"
        flag = " --keep-specs" if request.specs_mode == "keep" else ""
        command = f"spec-dock uninstall --apply{flag} -- {_quoted_target(request.target)}"
    return {"invocation_id": invocation_id, "rendered_command": command}


def _cleanup_invocation(request: LifecycleRequest, operation: str, seed_policy: str, token: str) -> dict[str, str]:
    if operation == "uninstall":
        invocation_id = "uninstall-apply-keep"
        command = (
            f"spec-dock uninstall --apply --keep-specs --provider-cleanup-token {token} -- "
            f"{_quoted_target(request.target)}"
        )
    elif operation == "install" and seed_policy == "create-if-absent":
        invocation_id = "init-force"
        command = f"spec-dock init --force --provider-cleanup-token {token} -- {_quoted_target(request.target)}"
    else:
        invocation_id = "update"
        command = f"spec-dock update --provider-cleanup-token {token} -- {_quoted_target(request.target)}"
    return {
        "role": "cleanup-retry",
        "invocation_id": invocation_id,
        "cleanup_token": token,
        "rendered_command": command,
    }


def _record_mapping(record: InstallationRecord) -> dict[str, object]:
    return {
        "schema_version": record.schema_version,
        "state": record.state,
        "operation": record.operation,
        "version": record.version,
        "candidate_digest": record.candidate_digest,
        "seed_policy": record.seed_policy,
        "skill_slots": dict(record.skill_slots),
    }


def _witness_mapping(witness: InodeWitness | None) -> dict[str, object] | None:
    if witness is None:
        return None
    return {
        "kind": witness.kind,
        "device": witness.device,
        "inode": witness.inode,
        "ctime_ns": witness.ctime_ns,
        "mode": witness.mode,
        "link_count": witness.link_count,
        "size": witness.size,
        "sha256": witness.sha256,
    }


def _record_ref(raw: bytes | None, kind: str, witness: InodeWitness | None) -> dict[str, object]:
    if raw is None:
        return {"kind": "absent", "bytes_base64": None, "sha256": None, "witness": None}
    return {
        "kind": kind,
        "bytes_base64": base64.b64encode(raw).decode("ascii"),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "witness": _witness_mapping(witness),
    }


def _domain_digest(entries: Sequence[TreeEntry]) -> str:
    stream = bytearray()
    for entry in entries:
        path = entry.path.encode("utf-8")
        if entry.kind == "directory":
            stream.extend(b"D\0" + path + b"\0")
        elif entry.kind == "regular":
            assert entry.mode is not None and entry.sha256 is not None
            stream.extend(b"F\0" + path + b"\0" + f"{entry.mode:04o}".encode() + b"\0" + entry.sha256.encode() + b"\0")
        elif entry.kind == "symlink":
            assert entry.target is not None
            stream.extend(b"L\0" + path + b"\0" + entry.target.encode("utf-8") + b"\0")
        else:
            raise FilesystemSafetyError("unsupported domain entry")
    return hashlib.sha256(bytes(stream)).hexdigest()


def _read_regular(parent_fd: int, name: str, maximum: int = 4096) -> tuple[bytes, InodeWitness]:
    value = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    if not stat.S_ISREG(value.st_mode) or value.st_nlink != 1 or stat.S_IMODE(value.st_mode) != 0o644:
        raise FilesystemSafetyError(f"{name!r} is not an owned regular record")
    fd = os.open(name, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0), dir_fd=parent_fd)
    try:
        opened = os.fstat(fd)
        if not NativeAtomicFilesystem._same_inode(value, opened):
            raise FilesystemSafetyError(f"{name!r} changed while opening")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(fd, min(1024 * 1024, maximum + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > maximum:
                raise FilesystemSafetyError(f"{name!r} is oversized")
        after = os.fstat(fd)
        if not NativeAtomicFilesystem._same_inode(opened, after):
            raise FilesystemSafetyError(f"{name!r} changed while reading")
        raw = b"".join(chunks)
        return raw, NativeAtomicFilesystem._witness(after, "regular", hashlib.sha256(raw).hexdigest())
    finally:
        os.close(fd)


def _open_child(parent_fd: int, components: Sequence[str], *, create: bool = False) -> int:
    current = os.dup(parent_fd)
    try:
        for component in components:
            if component in {"", ".", ".."} or "/" in component or "\x00" in component:
                raise FilesystemSafetyError("unsafe relative component")
            try:
                next_fd = os.open(
                    component,
                    os.O_RDONLY
                    | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_NOFOLLOW", 0)
                    | getattr(os, "O_CLOEXEC", 0),
                    dir_fd=current,
                )
            except FileNotFoundError:
                if not create:
                    raise
                os.mkdir(component, 0o755, dir_fd=current)
                next_fd = os.open(
                    component,
                    os.O_RDONLY
                    | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_NOFOLLOW", 0)
                    | getattr(os, "O_CLOEXEC", 0),
                    dir_fd=current,
                )
                os.fsync(current)
            os.close(current)
            current = next_fd
        return current
    except BaseException:
        os.close(current)
        raise


def _capture_entries(parent_fd: int, name: str, *, exclude_marker: bool = False) -> tuple[TreeEntry, ...]:
    root_fd = os.open(
        name,
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
        dir_fd=parent_fd,
    )
    entries: list[TreeEntry] = []

    def visit(directory_fd: int, prefix: str) -> None:
        names = sorted(os.listdir(directory_fd), key=os.fsencode)
        for child in names:
            if exclude_marker and not prefix and child == SLOT_MARKER_NAME:
                continue
            relative = f"{prefix}/{child}" if prefix else child
            value = os.stat(child, dir_fd=directory_fd, follow_symlinks=False)
            if stat.S_ISDIR(value.st_mode):
                entries.append(TreeEntry("directory", relative))
                child_fd = os.open(
                    child,
                    os.O_RDONLY
                    | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_NOFOLLOW", 0)
                    | getattr(os, "O_CLOEXEC", 0),
                    dir_fd=directory_fd,
                )
                try:
                    visit(child_fd, relative)
                finally:
                    os.close(child_fd)
            elif stat.S_ISREG(value.st_mode):
                if stat.S_IMODE(value.st_mode) not in {0o644, 0o755}:
                    raise FilesystemSafetyError(f"unsupported regular mode at {relative}")
                fd = os.open(
                    child, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0), dir_fd=directory_fd
                )
                try:
                    content = NativeAtomicFilesystem._sha256_fd(fd)
                finally:
                    os.close(fd)
                entries.append(TreeEntry("regular", relative, stat.S_IMODE(value.st_mode), content))
            elif stat.S_ISLNK(value.st_mode):
                target = os.readlink(child, dir_fd=directory_fd)
                if target.startswith("/") or "\\" in target or "\x00" in target:
                    raise FilesystemSafetyError(f"unsafe symlink at {relative}")
                entries.append(TreeEntry("symlink", relative, target=target))
            else:
                raise FilesystemSafetyError(f"unsupported entry at {relative}")

    try:
        visit(root_fd, "")
    finally:
        os.close(root_fd)
    return tuple(sorted(entries, key=lambda entry: entry.path.encode("utf-8")))


def _capture_domain(parent_fd: int, name: str, *, exclude_marker: bool = False) -> DomainTreeIdentity:
    entries = _capture_entries(parent_fd, name, exclude_marker=exclude_marker)
    return DomainTreeIdentity(_domain_digest(entries), len(entries), entries)


def _target_components(path: str) -> tuple[str, ...]:
    parts = tuple(part for part in Path(path).parts if part not in {"", "/"})
    if any(part in {".", ".."} for part in parts):
        raise FilesystemSafetyError("target path contains dot components")
    return parts


def _safe_component(name: str) -> None:
    if not name or name in {".", ".."} or "/" in name or "\x00" in name:
        raise FilesystemSafetyError(f"unsafe relative component: {name!r}")


def _mkdir_child(parent_fd: int, name: str, mode: int = 0o755) -> int:
    """Create/open a directory below an already-bound descriptor."""

    _safe_component(name)
    with contextlib.suppress(FileExistsError):
        os.mkdir(name, mode, dir_fd=parent_fd)
    fd = os.open(
        name,
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
        dir_fd=parent_fd,
    )
    value = os.fstat(fd)
    if not stat.S_ISDIR(value.st_mode):
        os.close(fd)
        raise FilesystemSafetyError(f"{name!r} is not a directory")
    return fd


def _open_existing_child(parent_fd: int, name: str) -> int | None:
    _safe_component(name)
    try:
        return os.open(
            name,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
            dir_fd=parent_fd,
        )
    except FileNotFoundError:
        return None


def _open_path(root_fd: int, components: Sequence[str], *, create: bool = False) -> int:
    current = os.dup(root_fd)
    try:
        for component in components:
            _safe_component(component)
            next_fd = _mkdir_child(current, component) if create else _open_existing_child(current, component)
            if next_fd is None:
                raise FileNotFoundError(component)
            os.close(current)
            current = next_fd
        return current
    except BaseException:
        os.close(current)
        raise


def _source_directory(path: Path) -> int:
    """Open a packaged source directory without following its final component."""

    if not path.is_absolute():
        path = path.absolute()
    fd = os.open(
        path,
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
    )
    value = os.fstat(fd)
    if not stat.S_ISDIR(value.st_mode):
        os.close(fd)
        raise CandidateError(f"packaged domain is not a directory: {path}")
    return fd


def _copy_source_entry(source_fd: int, name: str, destination_fd: int) -> None:
    _safe_component(name)
    value = os.stat(name, dir_fd=source_fd, follow_symlinks=False)
    if stat.S_ISDIR(value.st_mode):
        os.mkdir(name, 0o700, dir_fd=destination_fd)
        child_source = os.open(
            name,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
            dir_fd=source_fd,
        )
        child_destination = os.open(
            name,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
            dir_fd=destination_fd,
        )
        try:
            with os.scandir(child_source) as children:
                child_names = sorted(
                    (child.name for child in children if not _is_generated_python_cache(child.name)),
                    key=os.fsencode,
                )
            for child in child_names:
                _copy_source_entry(child_source, child, child_destination)
        finally:
            os.close(child_source)
            os.close(child_destination)
        return
    if stat.S_ISREG(value.st_mode):
        mode = stat.S_IMODE(value.st_mode)
        if mode not in {0o644, 0o755} or value.st_nlink != 1:
            raise CandidateError(f"packaged regular file is unsafe: {name}")
        source_object = os.open(
            name,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
            dir_fd=source_fd,
        )
        destination_object = os.open(
            name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
            mode,
            dir_fd=destination_fd,
        )
        try:
            source_stat = os.fstat(source_object)
            if not NativeAtomicFilesystem._same_inode(value, source_stat):
                raise CandidateError(f"packaged file changed while opening: {name}")
            while True:
                chunk = os.read(source_object, 1024 * 1024)
                if not chunk:
                    break
                cursor = 0
                while cursor < len(chunk):
                    cursor += os.write(destination_object, chunk[cursor:])
            os.fchmod(destination_object, mode)
            os.fsync(destination_object)
            if not NativeAtomicFilesystem._same_inode(source_stat, os.fstat(source_object)):
                raise CandidateError(f"packaged file changed while reading: {name}")
        finally:
            os.close(source_object)
            os.close(destination_object)
        return
    if stat.S_ISLNK(value.st_mode):
        target = os.readlink(name, dir_fd=source_fd)
        if target.startswith("/") or "\\" in target or "\x00" in target:
            raise CandidateError(f"packaged symlink target is unsafe: {name}")
        os.symlink(target, name, dir_fd=destination_fd)
        return
    raise CandidateError(f"packaged domain contains unsupported entry: {name}")


def _copy_tree(source: Path, destination_fd: int, *, slot: str | None, candidate: CandidateIdentity) -> None:
    """Copy one trusted packaged domain into an already-owned empty stage entry."""

    source_fd = _source_directory(source)
    try:
        with os.scandir(source_fd) as children:
            child_names = sorted(
                (child.name for child in children if not _is_generated_python_cache(child.name)),
                key=os.fsencode,
            )
        for child in child_names:
            _copy_source_entry(source_fd, child, destination_fd)
        if slot is not None:
            marker_fd = os.open(
                SLOT_MARKER_NAME,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
                0o644,
                dir_fd=destination_fd,
            )
            try:
                payload = marker_bytes(candidate, slot)
                cursor = 0
                while cursor < len(payload):
                    cursor += os.write(marker_fd, payload[cursor:])
                os.fchmod(marker_fd, 0o644)
                os.fsync(marker_fd)
            finally:
                os.close(marker_fd)
        os.fsync(destination_fd)
    finally:
        os.close(source_fd)


def _make_action(path: str, category: str, status: str, reason: str) -> LifecycleAction:
    return LifecycleAction(path, category, status, reason)


def _empty_continuation() -> dict[str, str | None]:
    return {
        "next_action": "none",
        "next_command": None,
        "after_cleanup_action": "none",
        "after_cleanup_command": None,
    }


def _lifecycle_continuation(command: str) -> dict[str, str | None]:
    return {
        "next_action": "run-request",
        "next_command": command,
        "after_cleanup_action": "none",
        "after_cleanup_command": None,
    }


def _cleanup_continuation(
    command: str,
    deferred: Mapping[str, str] | None,
) -> dict[str, str | None]:
    return {
        "next_action": "retry-cleanup",
        "next_command": command,
        "after_cleanup_action": "run-request" if deferred is not None else "none",
        "after_cleanup_command": None if deferred is None else deferred["rendered_command"],
    }


def _completed_cleanup_continuation(deferred: Mapping[str, str] | None) -> dict[str, str | None]:
    return {
        "next_action": "run-request" if deferred is not None else "none",
        "next_command": None if deferred is None else deferred["rendered_command"],
        "after_cleanup_action": "none",
        "after_cleanup_command": None,
    }


def _action_path_sets(actions: Sequence[LifecycleAction]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return (
        tuple(action.path for action in actions if action.status == "failed"),
        tuple(action.path for action in actions if action.status == "pending"),
    )


class ProviderLifecycleEngine:
    """Execute install, update, migration, uninstall, and cleanup replay."""

    def __init__(
        self,
        assets_root: str | os.PathLike[str] | None = None,
        *,
        filesystem: NativeAtomicFilesystem | None = None,
        fault_injector: FaultInjector | Callable[[str], None] | Sequence[str] | str | None = None,
    ) -> None:
        self.assets_root = None if assets_root is None else Path(assets_root)
        self.filesystem = filesystem
        if fault_injector is None:
            self.fault_injector: FaultInjector | Callable[[str], None] = FaultInjector()
        elif isinstance(fault_injector, FaultInjector) or callable(fault_injector):
            self.fault_injector = fault_injector
        else:
            self.fault_injector = FaultInjector(fault_injector)

    def _check_fault(self, point: str) -> None:
        injector = self.fault_injector
        if isinstance(injector, FaultInjector):
            injector.check(point)
        else:
            injector(point)

    def _filesystem(self) -> NativeAtomicFilesystem:
        if self.filesystem is None:
            self.filesystem = NativeAtomicFilesystem()
        return self.filesystem

    def _assets(self) -> Path:
        value = Path(__file__).parent.parent / "assets" if self.assets_root is None else self.assets_root
        if (value / "spec_dock").is_dir() and (value / "install_root").is_dir():
            return value
        if (value / "assets" / "spec_dock").is_dir() and (value / "assets" / "install_root").is_dir():
            return value / "assets"
        raise CandidateError("source root does not contain packaged provider assets")

    def _candidate(self) -> CandidateIdentity:
        return capture_packaged_candidate(self._assets())

    @staticmethod
    def invalid_request(request: LifecycleRequest, *, code: str = "invalid-request") -> LifecycleResult:
        guidance = (
            [
                "Use tooling-only uninstall without --remove-specs.",
                "Spec history and Workbench data remain consumer-owned.",
            ]
            if code == "spec-history-purge-removed"
            else []
        )
        return build_public_result(
            request,
            status="error",
            code=code,
            operation=None,
            candidate_digest=None,
            seed_policy=None,
            phase="request-validation",
            last_completed_phase="not-started",
            guidance=guidance,
        )

    def execute(
        self,
        request: LifecycleRequest,
        *,
        force: bool | None = None,
        cleanup_token: str | None = None,
    ) -> LifecycleResult:
        """Run one normalized request while preserving the closed Wire surface."""

        if not isinstance(request, LifecycleRequest):
            raise TypeError("request must be LifecycleRequest")
        operation = _operation_from_request(request)
        seed_policy = _seed_from_request(request, operation)
        if request.mode not in {"dry-run", "apply"} or request.apply != (request.mode == "apply"):
            return self.invalid_request(request)
        if request.specs_mode == "remove":
            return self.invalid_request(request, code="spec-history-purge-removed")
        if not Path(request.target).is_absolute() or "\x00" in request.target:
            return self.invalid_request(request)
        if operation == "uninstall" and request.mode == "dry-run" and request.apply:
            return self.invalid_request(request)
        if operation != "uninstall" and request.specs_mode is not None:
            return self.invalid_request(request)

        try:
            lease = acquire_exclusive_repository_lease(request.target)
        except RepositoryBusy:
            return self._blocked(request, "repository-operation-busy")
        except RepositoryCoordinationUnavailable:
            return self._blocked(request, "repository-coordination-unavailable")
        except RepositoryCoordinationError:
            return self._blocked(request, "unsafe-repository-binding")

        try:
            return self._execute_bound(
                request, operation, seed_policy, force=force, cleanup_token=cleanup_token, lease=lease
            )
        finally:
            lease.close()

    def _blocked(
        self,
        request: LifecycleRequest,
        code: str,
        *,
        operation: str | None = None,
        candidate_digest: str | None = None,
        seed_policy: str | None = None,
        phase: str = "preflight",
        last_completed_phase: str = "request-validation",
        bootstrap_rolled_back: bool = False,
    ) -> LifecycleResult:
        return build_public_result(
            request,
            status="blocked",
            code=code,
            operation=operation,
            candidate_digest=candidate_digest,
            seed_policy=seed_policy,
            mutation_started=False,
            bootstrap_rolled_back=bootstrap_rolled_back,
            phase=phase,
            last_completed_phase=last_completed_phase,
        )

    def _execute_bound(
        self,
        request: LifecycleRequest,
        operation: str,
        seed_policy: str,
        *,
        force: bool | None,
        cleanup_token: str | None,
        lease: RepositoryLease,
    ) -> LifecycleResult:
        filesystem = self._filesystem()
        try:
            bound = filesystem.open_directory_chain_no_follow(request.target)
        except OSError:
            return self._blocked(request, "unsafe-repository-binding")
        with bound:
            try:
                candidate = None if operation == "uninstall" else self._candidate()
            except (CandidateError, OSError, ValueError):
                return self._blocked(
                    request,
                    "candidate-invalid",
                    operation=operation,
                    candidate_digest=None,
                    seed_policy=seed_policy,
                    phase="candidate-staging",
                )
            candidate_digest = candidate.aggregate_digest if candidate is not None else None
            try:
                namespace = self._namespace_for(request.target, lease)
                active_store, receipt_store, stage_store = self._stores(namespace, request.apply, request.target)
            except (PrivateStateError, PrivateStateForeignError, OSError, _InjectedFailure):
                return self._blocked(request, "lifecycle-preparation-failed")
            try:
                active = active_store.load() if active_store is not None else None
                receipt = receipt_store.load() if receipt_store is not None else None
            except (PrivateStateError, PrivateStateForeignError, OSError):
                return self._blocked(request, "lifecycle-preparation-failed")

            if cleanup_token is not None:
                return self._cleanup_retry_or_replay(
                    request,
                    cleanup_token,
                    active,
                    receipt,
                    active_store,
                    receipt_store,
                    stage_store,
                    bound.fd,
                )
            if active is not None:
                if active.state in {"ready", "terminal-cleanup"}:
                    return self._complete_pending_cleanup(
                        request,
                        active,
                        active_store,
                        receipt_store,
                        stage_store,
                        bound.fd,
                    )
                return self._resume_or_block(
                    request,
                    operation,
                    seed_policy,
                    candidate,
                    active,
                    active_store,
                    receipt_store,
                    stage_store,
                    bound.fd,
                    force=force,
                )

            if receipt is not None and not self._receipt_matches_repository(receipt, lease):
                return self._blocked(request, "invalid-request")
            try:
                return self._dispatch_new(
                    request,
                    operation,
                    seed_policy,
                    candidate,
                    active_store,
                    receipt_store,
                    stage_store,
                    bound.fd,
                    force=force,
                    receipt=receipt,
                )
            except _AdmissionFailure as failure:
                return self._admission_result(request, failure)
            except (AtomicRenameUnavailable, FilesystemSafetyError, PrivateStateError, OSError) as failure:
                return self._preparation_failure(
                    request,
                    operation,
                    candidate_digest,
                    seed_policy,
                    failure,
                    phase="candidate-staging",
                    last_completed_phase="preflight",
                )

    def _namespace_for(self, target: str, lease: RepositoryLease) -> Path:
        binding = lease.binding
        key = repository_key_for(binding.device, binding.inode, binding.euid)
        return Path(target).parent / f".spec-dock-provider-lifecycle-v1-euid-{binding.euid}" / key

    def _stores(
        self,
        namespace: Path,
        apply: bool,
        target: str,
    ) -> tuple[ActiveStateStore | None, CompletionReceiptStore | None, StageStore | None]:
        if apply:
            for point in ("private-top-mkdir", "private-top-fsync", "private-repo-mkdir", "private-repo-fsync"):
                self._check_fault(point)
            namespace = resolve_private_namespace(target)
            active = ActiveStateStore(namespace)
            receipt = CompletionReceiptStore(namespace)
            return active, receipt, StageStore(namespace, active)
        try:
            value = os.lstat(namespace)
        except FileNotFoundError:
            return None, None, None
        if not stat.S_ISDIR(value.st_mode) or stat.S_ISLNK(value.st_mode):
            raise PrivateStateForeignError("private namespace is not a directory")
        active = ActiveStateStore(namespace)
        receipt = CompletionReceiptStore(namespace)
        return active, receipt, StageStore(namespace, active)

    def _receipt_matches_repository(self, receipt: CompletionReceipt, lease: RepositoryLease) -> bool:
        binding = lease.binding
        return receipt.repository_key == repository_key_for(binding.device, binding.inode, binding.euid)

    def _admission_result(
        self,
        request: LifecycleRequest,
        failure: _AdmissionFailure,
    ) -> LifecycleResult:
        operation = failure.operation
        return build_public_result(
            request,
            status="blocked",
            code=failure.code,
            operation=operation,
            candidate_digest=failure.candidate_digest,
            seed_policy=failure.seed_policy,
            phase=failure.phase,
            last_completed_phase=failure.last_completed_phase,
        )

    @staticmethod
    def _preparation_failure(
        request: LifecycleRequest,
        operation: str,
        candidate_digest: str | None,
        seed_policy: str,
        _failure: BaseException,
        *,
        phase: str = "candidate-staging",
        last_completed_phase: str = "preflight",
        mutation_started: bool = False,
    ) -> LifecycleResult:
        """Map an I/O admission failure to the one closed preparation row."""

        retry = ProviderLifecycleEngine._retry_for(request, operation, seed_policy)
        return build_public_result(
            request,
            status="partial_failure" if mutation_started else "blocked",
            code="lifecycle-preparation-failed",
            operation=operation,
            candidate_digest=candidate_digest,
            seed_policy=seed_policy,
            mutation_started=mutation_started,
            phase=phase,
            last_completed_phase=last_completed_phase,
            retry_command=retry,
            continuation=_lifecycle_continuation(retry) if retry is not None else _empty_continuation(),
        )

    @staticmethod
    def _retry_for(request: LifecycleRequest, operation: str | None, seed_policy: str | None) -> str | None:
        if operation is None:
            return None
        if operation == "uninstall":
            token = "uninstall retry"
        elif operation == "update":
            token = "update retry"
        elif seed_policy == "create-if-absent":
            token = "install/create-if-absent retry"
        else:
            token = "install/preserve-only retry"
        target = _quoted_target(request.target)
        if token == "uninstall retry":
            return f"spec-dock uninstall --apply --keep-specs -- {target}"
        if token == "update retry":
            return f"spec-dock update -- {target}"
        if token == "install/create-if-absent retry":
            return f"spec-dock init --force -- {target}"
        return f"spec-dock update -- {target}"

    # The methods below are intentionally kept in this module.  They form the
    # single mutation owner used by the public adapter; the runtime package and
    # the installer CLI do not interpret ACTIVE, STAGE, or public records.

    def _dispatch_new(
        self,
        request: LifecycleRequest,
        operation: str,
        seed_policy: str,
        candidate: CandidateIdentity | None,
        active_store: ActiveStateStore | None,
        receipt_store: CompletionReceiptStore | None,
        stage_store: StageStore | None,
        root_fd: int,
        *,
        force: bool | None,
        receipt: CompletionReceipt | None,
    ) -> LifecycleResult:
        if operation == "uninstall":
            return self._dispatch_uninstall(
                request,
                seed_policy,
                active_store,
                receipt_store,
                stage_store,
                root_fd,
            )
        assert candidate is not None
        raw_record, record_witness, record, record_kind = self._observe_record(request.target, root_fd)
        if record_kind == "invalid":
            raise _AdmissionFailure(
                "installation-record-invalid",
                operation=operation,
                candidate_digest=None,
                seed_policy=seed_policy,
            )
        if operation == "update" and record is None and record_kind != "legacy-0.2.3":
            raise _AdmissionFailure(
                "tooling-not-installed",
                operation=operation,
                candidate_digest=candidate.aggregate_digest,
                seed_policy=seed_policy,
            )
        if operation == "install" and record is not None and not force:
            seed_policy = record.seed_policy
            raise _AdmissionFailure(
                "already-initialized",
                operation=operation,
                candidate_digest=candidate.aggregate_digest,
                seed_policy=seed_policy,
            )
        result_family = "legacy-migration" if record_kind == "legacy-0.2.3" else operation
        if result_family == "legacy-migration":
            seed_policy = "preserve-only"
        targets = self._observe_domains(root_fd)
        if any(item.kind not in {"absent", "directory"} for item in targets):
            raise _AdmissionFailure(
                "unsafe-target-type",
                operation=operation,
                candidate_digest=None,
                seed_policy=seed_policy,
            )
        if result_family != "legacy-migration":
            self._admit_existing_targets(
                root_fd,
                targets,
                candidate,
                owner_digest=record.candidate_digest if record is not None else None,
            )
        return self._start_or_run(
            request,
            operation,
            seed_policy,
            result_family,
            candidate,
            raw_record,
            record_witness,
            record,
            active_store,
            receipt_store,
            stage_store,
            root_fd,
            receipt=receipt,
        )

    def _dispatch_uninstall(
        self,
        request: LifecycleRequest,
        seed_policy: str,
        active_store: ActiveStateStore | None,
        receipt_store: CompletionReceiptStore | None,
        stage_store: StageStore | None,
        root_fd: int,
    ) -> LifecycleResult:
        raw_record, record_witness, record, record_kind = self._observe_record(request.target, root_fd)
        targets = self._observe_domains(root_fd)
        container = self._observe_container(root_fd)
        if any(item.kind not in {"absent", "directory"} for item in targets) or container.kind not in {
            "absent",
            "directory",
        }:
            raise _AdmissionFailure("unsafe-target-type", operation="uninstall", seed_policy=seed_policy)
        if record_kind == "invalid":
            raise _AdmissionFailure("installation-record-invalid", operation="uninstall", seed_policy=seed_policy)
        if record is None and record_kind != "legacy-0.2.3":
            if any(item.kind == "directory" for item in targets):
                raise _AdmissionFailure("installation-record-invalid", operation="uninstall", seed_policy=seed_policy)
            digest = self._candidate().aggregate_digest
            return self._uninstall_absent_result(request, digest, targets, container, root_fd)
        if record_kind == "legacy-0.2.3":
            fixture = load_legacy_fixture()
            candidate_digest = cast("str", fixture["aggregate_digest"])
        else:
            assert record is not None
            candidate_digest = record.candidate_digest
            seed_policy = record.seed_policy
            self._admit_existing_slots(root_fd, targets, candidate_digest)
        if request.mode == "dry-run":
            return self._uninstall_plan_result(request, candidate_digest, targets, container, record)
        assert active_store is not None and receipt_store is not None and stage_store is not None
        return self._start_or_run(
            request,
            "uninstall",
            "preserve-only",
            "uninstall",
            None,
            raw_record,
            record_witness,
            record,
            active_store,
            receipt_store,
            stage_store,
            root_fd,
            receipt=receipt_store.load() if receipt_store is not None else None,
            legacy=record_kind == "legacy-0.2.3",
        )

    def _start_or_run(
        self,
        request: LifecycleRequest,
        operation: str,
        seed_policy: str,
        result_family: str,
        candidate: CandidateIdentity | None,
        raw_record: bytes | None,
        record_witness: InodeWitness | None,
        record: InstallationRecord | None,
        active_store: ActiveStateStore | None,
        receipt_store: CompletionReceiptStore | None,
        stage_store: StageStore | None,
        root_fd: int,
        *,
        receipt: CompletionReceipt | None = None,
        legacy: bool = False,
    ) -> LifecycleResult:
        if request.mode == "dry-run":
            assert candidate is not None
            return self._install_plan_result(request, operation, seed_policy, candidate, root_fd, record)
        assert active_store is not None and receipt_store is not None and stage_store is not None
        if candidate is None and operation != "uninstall":
            raise _AdmissionFailure("candidate-invalid", operation=operation, seed_policy=seed_policy)
        try:
            if receipt is not None:
                self._invalidate_receipt(receipt_store)
            active = self._prepare_active(
                request,
                operation,
                seed_policy,
                result_family,
                candidate,
                raw_record,
                record_witness,
                record,
                active_store,
                stage_store,
                root_fd,
                legacy=legacy,
            )
            return self._run_active(
                request,
                active,
                candidate,
                active_store,
                receipt_store,
                stage_store,
                root_fd,
            )
        except _AdmissionFailure:
            raise
        except _InjectedFailure as failure:
            current = active_store.load()
            if current is not None:
                return self._preparation_failure(
                    request,
                    current.operation,
                    current.candidate_digest,
                    current.seed_policy,
                    failure,
                    phase="candidate-staging",
                    last_completed_phase="preflight",
                )
            digest = (
                candidate.aggregate_digest
                if candidate is not None
                else record.candidate_digest
                if record is not None
                else None
            )
            return self._preparation_failure(request, operation, digest, seed_policy, failure)
        except (AtomicRenameUnavailable, FilesystemSafetyError, PrivateStateError, OSError) as failure:
            current = active_store.load()
            if current is None:
                digest = (
                    candidate.aggregate_digest
                    if candidate is not None
                    else record.candidate_digest
                    if record is not None
                    else None
                )
                return self._preparation_failure(request, operation, digest, seed_policy, failure)
            return self._partial_failure_result(request, current, failure, root_fd)

    def _invalidate_receipt(self, store: CompletionReceiptStore) -> None:
        witness = store._current_witness()
        if witness is None:
            return
        namespace_fd = store._open_namespace()
        try:
            self._filesystem().unlink_bound(namespace_fd, store.filename, witness)
            self._filesystem().fsync_directory(namespace_fd)
        finally:
            os.close(namespace_fd)

    def _prepare_active(
        self,
        request: LifecycleRequest,
        operation: str,
        seed_policy: str,
        result_family: str,
        candidate: CandidateIdentity | None,
        raw_record: bytes | None,
        record_witness: InodeWitness | None,
        record: InstallationRecord | None,
        active_store: ActiveStateStore,
        stage_store: StageStore,
        root_fd: int,
        *,
        legacy: bool,
    ) -> ActiveState:
        binding = RepositoryBinding(*self._repository_identity(root_fd))
        candidate_digest = (
            candidate.aggregate_digest
            if candidate is not None
            else (
                record.candidate_digest
                if record is not None
                else cast("str", load_legacy_fixture()["aggregate_digest"])
            )
        )
        tuple_key = tuple_key_for(operation, candidate_digest, seed_policy)
        generation = secrets.token_hex(16)
        expected_incomplete = InstallationRecord(
            1,
            "incomplete",
            cast("Operation", operation),
            CANDIDATE_VERSION,
            candidate_digest,
            cast("SeedPolicy", seed_policy),
            {"spec-dock": CANDIDATE_VERSION, "spec-dock-grill-with-docs": CANDIDATE_VERSION},
        )
        expected_incomplete_bytes = serialize_installation_record(expected_incomplete)
        terminal_state = "tooling-absent-preserved-data" if operation == "uninstall" else "ready"
        terminal_record = InstallationRecord(
            1,
            cast("RecordState", terminal_state),
            None,
            CANDIDATE_VERSION,
            candidate_digest,
            cast("SeedPolicy", seed_policy),
            {"spec-dock": CANDIDATE_VERSION, "spec-dock-grill-with-docs": CANDIDATE_VERSION},
        )
        terminal_bytes = serialize_installation_record(terminal_record)
        family = cast("Literal['install', 'legacy-migration', 'update', 'uninstall']", result_family)
        token = cleanup_token_for(
            binding_key := repository_key_for(binding.device, binding.inode, binding.euid),
            tuple_key,
            family,
            generation,
        )
        target_observations = self._observe_domains(root_fd)
        original_digests = tuple(
            item.tree.tree_digest if item.tree is not None else None for item in target_observations
        )
        candidate_digests = tuple(
            domain.tree_digest if candidate is not None else None for domain in (candidate.domains if candidate else ())
        )
        if candidate is None:
            candidate_digests = (None,) * 6
        owned = tuple(
            {
                "path": item.path,
                "original_kind": "directory" if item.kind == "directory" else None,
                "original_tree_digest": item.tree.tree_digest if item.tree is not None else None,
                "original_inode": _witness_mapping(item.witness) if item.witness is not None else None,
                "terminal_kind": None,
                "terminal_tree_digest": None,
            }
            for item in target_observations
        )
        registered = tuple(
            {
                "name": name,
                "target_path": path,
                "candidate_tree_digest": candidate_digests[index],
                "original_tree_digest": original_digests[index],
            }
            for index, (name, path) in enumerate(zip(STAGE_ENTRY_NAMES, STAGE_TARGET_PATHS, strict=True))
        )
        container = self._observe_container(root_fd)
        bootstrap = {
            "disposition": "existing" if container.witness is not None else "planned-create",
            "witness": _witness_mapping(container.witness),
        }
        active = ActiveState(
            1,
            "prepared",
            binding_key,
            {"device": binding.device, "inode": binding.inode, "euid": binding.euid},
            tuple_key,
            generation,
            cast("Operation", operation),
            candidate_digest,
            cast("SeedPolicy", seed_policy),
            family,
            _record_ref(
                raw_record,
                "legacy-0.2.3" if legacy else "final" if raw_record is not None else "absent",
                record_witness,
            ),
            {
                "bytes_base64": base64.b64encode(expected_incomplete_bytes).decode("ascii"),
                "sha256": hashlib.sha256(expected_incomplete_bytes).hexdigest(),
            },
            bootstrap,
            owned,
            registered,
            None,
            hashlib.sha256(terminal_bytes).hexdigest(),
            token,
            _cleanup_invocation(request, operation, seed_policy, token),
            None,
        )
        self._save_active(active_store, active)
        self._prepare_stage(stage_store, active, candidate)
        return active

    @staticmethod
    def _repository_identity(root_fd: int) -> tuple[int, int, int]:
        value = os.fstat(root_fd)
        if not stat.S_ISDIR(value.st_mode):
            raise FilesystemSafetyError("repository root descriptor is not a directory")
        return value.st_dev, value.st_ino, os.geteuid() if hasattr(os, "geteuid") else os.getuid()

    def _save_active(self, store: ActiveStateStore, active: ActiveState) -> None:
        for point in (
            "active-temp-open",
            "active-temp-write",
            "active-temp-fsync",
            "active-temp-rename",
            "active-parent-fsync",
        ):
            self._check_fault(point)
        store.save(active)

    def _prepare_stage(
        self,
        stage_store: StageStore,
        active: ActiveState,
        candidate: CandidateIdentity | None,
    ) -> None:
        owner = StageOwner(
            1,
            active.repository_key,
            active.tuple_key,
            active.operation_generation,
            active.operation,
            active.candidate_digest,
            active.seed_policy,
            active.result_family,
            STAGE_ENTRY_NAMES,
            tuple(cast("str | None", item["candidate_tree_digest"]) for item in active.registered_stage_entries),
            tuple(cast("str | None", item["original_tree_digest"]) for item in active.registered_stage_entries),
        )
        if stage_store.reuse_if_valid(owner) and self._stage_payload_valid(stage_store, candidate):
            return
        self._check_fault("stage-mkdir")
        stage_store.ensure_registered_entries()
        self._check_fault("stage-owner-write")
        stage_store.save_owner(owner)
        self._check_fault("stage-owner-fsync")
        stage_fd = stage_store._stage_fd()
        try:
            if candidate is None:
                return
            assets = self._assets()
            for index, ((_, _, source_suffix), stage_name) in enumerate(
                zip(FIXED_DOMAINS, STAGE_ENTRY_NAMES, strict=True)
            ):
                for operation in ("create", "write", "fsync"):
                    self._check_fault(f"stage-entry-{stage_name}-{operation}")
                self._remove_stage_entry(stage_fd, stage_name)
                os.mkdir(stage_name, 0o700, dir_fd=stage_fd)
                entry_fd = os.open(
                    stage_name,
                    os.O_RDONLY
                    | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_NOFOLLOW", 0)
                    | getattr(os, "O_CLOEXEC", 0),
                    dir_fd=stage_fd,
                )
                try:
                    slot = FIXED_DOMAINS[index][1] if index >= 4 else None
                    _copy_tree(assets / source_suffix, entry_fd, slot=slot, candidate=candidate)
                finally:
                    os.close(entry_fd)
            self._check_fault("stage-parent-fsync")
            os.fsync(stage_fd)
        finally:
            os.close(stage_fd)

    def _stage_payload_valid(self, stage_store: StageStore, candidate: CandidateIdentity | None) -> bool:
        if candidate is None:
            return True
        stage_fd = stage_store._stage_fd()
        try:
            for index, stage_name in enumerate(STAGE_ENTRY_NAMES):
                current = _capture_domain(stage_fd, stage_name, exclude_marker=index >= 4)
                expected = candidate.domains[index]
                if current.tree_digest != expected.tree_digest or current.entry_count != expected.entry_count:
                    return False
                if index >= 4:
                    entry_fd = os.open(
                        stage_name,
                        os.O_RDONLY
                        | getattr(os, "O_DIRECTORY", 0)
                        | getattr(os, "O_NOFOLLOW", 0)
                        | getattr(os, "O_CLOEXEC", 0),
                        dir_fd=stage_fd,
                    )
                    try:
                        marker_raw, _ = _read_regular(entry_fd, SLOT_MARKER_NAME)
                    finally:
                        os.close(entry_fd)
                    marker = parse_slot_marker(marker_raw)
                    if marker.slot != FIXED_DOMAINS[index][1] or marker.candidate_digest != candidate.aggregate_digest:
                        return False
            return True
        except (OSError, FilesystemSafetyError, CandidateError, ValueError):
            return False
        finally:
            os.close(stage_fd)

    def _remove_stage_entry(self, stage_fd: int, name: str) -> None:
        _safe_component(name)
        try:
            current = _capture_domain(stage_fd, name)
        except FileNotFoundError:
            return
        NativeAtomicFilesystem().remove_tree_bound(stage_fd, name, current)

    def _observe_container(self, root_fd: int) -> _ObservedTarget:
        return self._observe_target(root_fd, "spec-dock", expect_tree=False)

    def _observe_domains(self, root_fd: int) -> tuple[_ObservedTarget, ...]:
        return tuple(self._observe_target(root_fd, path, expect_tree=True) for _, path, _ in FIXED_DOMAINS)

    def _observe_target(self, root_fd: int, path: str, *, expect_tree: bool) -> _ObservedTarget:
        components = _target_components(path)
        parent_components, name = components[:-1], components[-1]
        try:
            parent_fd = _open_path(root_fd, parent_components)
        except FileNotFoundError:
            return _ObservedTarget(path, "absent", None, None)
        try:
            try:
                value = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                return _ObservedTarget(path, "absent", None, None)
            kind = (
                "directory"
                if stat.S_ISDIR(value.st_mode)
                else "symlink"
                if stat.S_ISLNK(value.st_mode)
                else "regular"
                if stat.S_ISREG(value.st_mode)
                else "other"
            )
            if kind != "directory":
                return _ObservedTarget(path, kind, None, None)
            witness = NativeAtomicFilesystem().capture_inode(parent_fd, name, "directory")
            tree = (
                _capture_domain(parent_fd, name, exclude_marker=path in {FIXED_DOMAINS[4][1], FIXED_DOMAINS[5][1]})
                if expect_tree
                else None
            )
            return _ObservedTarget(path, "directory", witness, tree)
        finally:
            os.close(parent_fd)

    def _observe_record(
        self,
        target: str,
        root_fd: int,
    ) -> tuple[bytes | None, InodeWitness | None, InstallationRecord | None, str]:
        specdock = self._observe_container(root_fd)
        if specdock.kind == "absent":
            return None, None, None, "absent"
        if specdock.kind != "directory":
            return None, None, None, "invalid"
        specdock_fd = _open_path(root_fd, ("spec-dock",))
        try:
            try:
                raw, witness = _read_regular(specdock_fd, "spec-dock.version")
            except FileNotFoundError:
                return None, None, None, "absent"
            except FilesystemSafetyError:
                return None, None, None, "invalid"
        finally:
            os.close(specdock_fd)
        if raw == b"0.2.3\n":
            classification = classify_exact_legacy_workspace(target)
            return raw, witness, None, "legacy-0.2.3" if classification == "legacy-0.2.3" else "invalid"
        try:
            return raw, witness, parse_installation_record(raw), "final"
        except (ValueError, WireValidationError):
            return raw, witness, None, "invalid"

    def _admit_existing_targets(
        self,
        root_fd: int,
        targets: Sequence[_ObservedTarget],
        candidate: CandidateIdentity,
        *,
        owner_digest: str | None,
    ) -> None:
        """Require ownership evidence before fresh fixed-target replacement."""

        for index, item in enumerate(targets):
            if item.kind != "directory":
                continue
            if index >= 4:
                if not self._slot_marker_matches(
                    root_fd,
                    item.path,
                    candidate,
                    expected_digest=owner_digest or candidate.aggregate_digest,
                ):
                    raise _AdmissionFailure(
                        "foreign-skill-slot",
                        operation="update" if owner_digest is not None else "install",
                        candidate_digest=None,
                        seed_policy="preserve-only" if owner_digest is not None else "create-if-absent",
                    )
                continue
            if owner_digest is not None:
                continue
            if (
                item.tree is None
                or item.tree.tree_digest != candidate.domains[index].tree_digest
                or item.tree.entry_count != candidate.domains[index].entry_count
            ):
                raise _AdmissionFailure(
                    "foreign-tooling-root",
                    operation="install",
                    candidate_digest=None,
                    seed_policy="create-if-absent",
                )

    def _admit_existing_slots(
        self,
        root_fd: int,
        targets: Sequence[_ObservedTarget],
        candidate_digest: str,
    ) -> None:
        for item in targets[4:]:
            if item.kind == "directory" and not self._slot_marker_matches(
                root_fd,
                item.path,
                None,
                expected_digest=candidate_digest,
            ):
                raise _AdmissionFailure(
                    "foreign-skill-slot",
                    operation="uninstall",
                    candidate_digest=None,
                    seed_policy="preserve-only",
                )

    def _slot_marker_matches(
        self,
        root_fd: int,
        path: str,
        candidate: CandidateIdentity | None,
        *,
        expected_digest: str,
    ) -> bool:
        components = _target_components(path)
        try:
            slot_fd = _open_path(root_fd, components)
        except (FileNotFoundError, OSError, FilesystemSafetyError):
            return False
        try:
            try:
                raw, _witness = _read_regular(slot_fd, SLOT_MARKER_NAME, maximum=2048)
                marker = parse_slot_marker(raw)
            except (FileNotFoundError, FilesystemSafetyError, CandidateError, ValueError, WireValidationError):
                return False
            return (
                marker.slot == path
                and marker.version == (candidate.version if candidate is not None else CANDIDATE_VERSION)
                and marker.candidate_digest == expected_digest
            )
        finally:
            os.close(slot_fd)

    def _install_plan_result(
        self,
        request: LifecycleRequest,
        operation: str,
        seed_policy: str,
        candidate: CandidateIdentity,
        root_fd: int,
        _record: InstallationRecord | None,
    ) -> LifecycleResult:
        targets = self._observe_domains(root_fd)
        actions = self._install_actions(operation, seed_policy, candidate, targets, root_fd, planned=True)
        return build_public_result(
            request,
            status="planned",
            code="install-planned" if operation == "install" else "update-planned",
            operation=operation,
            candidate_digest=candidate.aggregate_digest,
            seed_policy=seed_policy,
            phase="complete",
            last_completed_phase="preflight",
            actions=actions,
        )

    def _uninstall_plan_result(
        self,
        request: LifecycleRequest,
        candidate_digest: str,
        targets: Sequence[_ObservedTarget],
        container: _ObservedTarget,
        record: InstallationRecord | None,
    ) -> LifecycleResult:
        actions = self._uninstall_actions(targets, container, record, planned=True, include_stage=False)
        code = "uninstall-planned" if any(item.kind == "directory" for item in targets) else "uninstall-already-absent"
        return build_public_result(
            request,
            status="planned",
            code=code,
            operation="uninstall",
            candidate_digest=candidate_digest,
            seed_policy="preserve-only",
            phase="complete",
            last_completed_phase="preflight",
            actions=actions,
        )

    def _uninstall_absent_result(
        self,
        request: LifecycleRequest,
        candidate_digest: str,
        targets: Sequence[_ObservedTarget],
        container: _ObservedTarget,
        _root_fd: int,
    ) -> LifecycleResult:
        if request.mode == "dry-run":
            return self._uninstall_plan_result(request, candidate_digest, targets, container, None)
        return build_public_result(
            request,
            status="completed",
            code="uninstall-already-absent",
            operation="uninstall",
            candidate_digest=candidate_digest,
            seed_policy="preserve-only",
            phase="complete",
            last_completed_phase="preflight",
            actions=self._uninstall_actions(targets, container, None, planned=False, include_stage=False),
        )

    def _install_actions(
        self,
        operation: str,
        seed_policy: str,
        candidate: CandidateIdentity,
        targets: Sequence[_ObservedTarget],
        root_fd: int,
        *,
        planned: bool,
        partial_index: int | None = None,
        include_stage: bool = False,
        failure_point: str | None = None,
    ) -> tuple[LifecycleAction, ...]:
        container = self._observe_container(root_fd)
        result: list[LifecycleAction] = []
        container_status = "preserved" if container.kind == "directory" else "planned" if planned else "completed"
        container_reason = "shared-container-preserve" if container.kind == "directory" else "fresh-container-create"
        result.append(_make_action("spec-dock", "container", container_status, container_reason))
        record_status = "planned" if planned else "completed"
        result.append(_make_action("spec-dock/spec-dock.version", "record", record_status, "terminal-record-publish"))
        for index, item in enumerate(targets):
            kind, path, _ = FIXED_DOMAINS[index]
            current = False
            with contextlib.suppress(IndexError):
                current = item.tree is not None and item.tree.tree_digest == candidate.domains[index].tree_digest
            category = kind
            reason = (
                f"candidate-{category}-current"
                if current
                else f"candidate-{category}-{'create' if item.kind == 'absent' else 'replace'}"
            )
            status = "preserved" if current else "planned" if planned else "completed"
            if partial_index is not None and not current:
                if index < partial_index:
                    status = "completed"
                elif index == partial_index:
                    status = "failed"
                else:
                    status = "pending"
            result.append(_make_action(path, category, status, reason))
        for seed_index, (path, seed_name) in enumerate((
            ("spec-dock/.gitignore", "spec-dock-gitignore"),
            (".github/workflows/ci.yml", "consumer-ci"),
        )):
            existing = self._observe_target(root_fd, path, expect_tree=False)
            if existing.kind in {"directory", "other", "symlink", "regular"}:
                reason = (
                    "consumer-seed-present"
                    if operation == "install" and seed_policy == "create-if-absent"
                    else "preserve-only-seed"
                )
            else:
                reason = "fresh-seed-create" if seed_policy == "create-if-absent" else "preserve-only-seed"
            status = "preserved" if reason != "fresh-seed-create" else "planned" if planned else "completed"
            if (
                failure_point is not None
                and failure_point.startswith(f"seed-{seed_name}-")
                and reason == "fresh-seed-create"
            ):
                status = "failed"
            elif (
                failure_point is not None
                and failure_point.startswith("seed-")
                and seed_index == 1
                and reason == "fresh-seed-create"
            ):
                status = "pending"
            result.append(_make_action(path, "seed", status, reason))
        if include_stage:
            stage_status = "pending" if failure_point is not None else "completed"
            result.append(_make_action("@provider-stage", "stage", stage_status, "candidate-stage-cleanup"))
        return tuple(result)

    def _uninstall_actions(
        self,
        targets: Sequence[_ObservedTarget],
        _container: _ObservedTarget,
        _record: InstallationRecord | None,
        *,
        planned: bool,
        include_stage: bool,
        partial_index: int | None = None,
    ) -> tuple[LifecycleAction, ...]:
        result = [_make_action("spec-dock", "container", "preserved", "shared-container-preserve")]
        record_status = "planned" if planned else "completed"
        result.append(_make_action("spec-dock/spec-dock.version", "record", record_status, "terminal-record-publish"))
        for index, item in enumerate(targets):
            category, path, _ = FIXED_DOMAINS[index]
            reason = f"owned-{category}-remove" if item.kind == "directory" else f"owned-{category}-absent"
            status = (
                "planned"
                if planned and item.kind == "directory"
                else "preserved"
                if item.kind != "directory"
                else "completed"
            )
            if partial_index is not None and item.kind == "directory":
                if index < partial_index:
                    status = "completed"
                elif index == partial_index:
                    status = "failed"
                else:
                    status = "pending"
            result.append(_make_action(path, category, status, reason))
        for path in ("spec-dock/.gitignore", ".github/workflows/ci.yml"):
            result.append(_make_action(path, "seed", "preserved", "preserve-only-seed"))
        if include_stage:
            result.append(_make_action("@provider-stage", "stage", "completed", "candidate-stage-cleanup"))
        return tuple(result)

    def _run_active(
        self,
        request: LifecycleRequest,
        active: ActiveState,
        candidate: CandidateIdentity | None,
        active_store: ActiveStateStore,
        receipt_store: CompletionReceiptStore,
        stage_store: StageStore,
        root_fd: int,
    ) -> LifecycleResult:
        if active.operation != _operation_from_request(request):
            return self._blocked(
                request,
                "resume-operation-mismatch",
                operation=active.operation,
                candidate_digest=active.candidate_digest,
                seed_policy=active.seed_policy,
            )
        if candidate is not None and candidate.aggregate_digest != active.candidate_digest:
            return self._blocked(
                request,
                "resume-candidate-mismatch",
                operation=active.operation,
                candidate_digest=active.candidate_digest,
                seed_policy=active.seed_policy,
                phase="candidate-staging",
                last_completed_phase="preflight",
            )
        if active.state in {"ready", "terminal-cleanup"}:
            return self._complete_pending_cleanup(request, active, active_store, receipt_store, stage_store, root_fd)
        try:
            if active.operation == "uninstall":
                return self._run_uninstall_active(
                    request,
                    active,
                    active_store,
                    receipt_store,
                    stage_store,
                    root_fd,
                )
            assert candidate is not None
            return self._run_install_active(
                request,
                active,
                candidate,
                active_store,
                receipt_store,
                stage_store,
                root_fd,
            )
        except _InjectedFailure as failure:
            current = active_store.load() or active
            return self._partial_failure_result(request, current, failure, root_fd)
        except (AtomicRenameUnavailable, FilesystemSafetyError, PrivateStateError, OSError) as failure:
            current = active_store.load() or active
            return self._partial_failure_result(request, current, failure, root_fd)

    def _run_install_active(
        self,
        request: LifecycleRequest,
        active: ActiveState,
        candidate: CandidateIdentity,
        active_store: ActiveStateStore,
        receipt_store: CompletionReceiptStore,
        stage_store: StageStore,
        root_fd: int,
    ) -> LifecycleResult:
        active = self._ensure_bootstrap(request, active, active_store, root_fd)
        _raw_record, _record_witness, record, _record_kind = self._observe_record(request.target, root_fd)
        expected_incomplete = base64.b64decode(active.expected_incomplete_record["bytes_base64"])
        if not (
            record is not None
            and record.state == "incomplete"
            and record.operation == active.operation
            and record.candidate_digest == active.candidate_digest
            and record.seed_policy == active.seed_policy
        ):
            self._write_public_record(request, active, expected_incomplete, active_store, root_fd)
            active = active_store.load() or active
        if active.state == "prepared":
            active = replace(active, state="running")
            self._save_active(active_store, active)
        targets = self._observe_domains(root_fd)
        for index, item in enumerate(targets):
            if self._target_matches_candidate(root_fd, item.path, index, candidate):
                continue
            self._publish_domain(request, active, stage_store, index, candidate, root_fd, detach=False)
        self._publish_seed(
            request, active, root_fd, "spec-dock/.gitignore", "spec-dock-gitignore", "spec_dock/.gitignore"
        )
        self._publish_seed(
            request,
            active,
            root_fd,
            ".github/workflows/ci.yml",
            "consumer-ci",
            "install_root/.github/workflows/ci.yml",
        )
        self._check_fault("target-verify")
        if not all(
            self._target_matches_candidate(root_fd, path, index, candidate)
            for index, (_, path, _) in enumerate(FIXED_DOMAINS)
        ):
            raise FilesystemSafetyError("published candidate does not verify")
        active = replace(active, state="ready")
        self._save_active(active_store, active)
        terminal = self._terminal_record_bytes(active)
        self._write_public_record(request, active, terminal, active_store, root_fd)
        active = active_store.load() or active
        active = replace(active, state="terminal-cleanup")
        self._save_active(active_store, active)
        return self._finish_cleanup(request, active, active_store, receipt_store, stage_store, root_fd)

    def _run_uninstall_active(
        self,
        request: LifecycleRequest,
        active: ActiveState,
        active_store: ActiveStateStore,
        receipt_store: CompletionReceiptStore,
        stage_store: StageStore,
        root_fd: int,
    ) -> LifecycleResult:
        container = self._observe_container(root_fd)
        if container.kind != "directory":
            raise FilesystemSafetyError("tooling container disappeared during uninstall")
        expected_incomplete = base64.b64decode(active.expected_incomplete_record["bytes_base64"])
        _raw, _witness, record, _kind = self._observe_record(request.target, root_fd)
        if not (
            record is not None
            and record.state == "incomplete"
            and record.operation == "uninstall"
            and record.candidate_digest == active.candidate_digest
        ):
            self._write_public_record(request, active, expected_incomplete, active_store, root_fd)
            active = active_store.load() or active
        if active.state == "prepared":
            active = replace(active, state="running")
            self._save_active(active_store, active)
        for index, (_kind, _path, _source) in enumerate(FIXED_DOMAINS):
            item = self._observe_domains(root_fd)[index]
            if item.kind == "directory":
                self._publish_domain(request, active, stage_store, index, None, root_fd, detach=True)
        self._check_fault("target-verify")
        if any(item.kind == "directory" for item in self._observe_domains(root_fd)):
            raise FilesystemSafetyError("tooling target remained after uninstall")
        active = replace(active, state="ready")
        self._save_active(active_store, active)
        terminal = self._terminal_record_bytes(active)
        self._write_public_record(request, active, terminal, active_store, root_fd)
        active = active_store.load() or active
        active = replace(active, state="terminal-cleanup")
        self._save_active(active_store, active)
        return self._finish_cleanup(request, active, active_store, receipt_store, stage_store, root_fd)

    def _ensure_bootstrap(
        self,
        _request: LifecycleRequest,
        active: ActiveState,
        active_store: ActiveStateStore,
        root_fd: int,
    ) -> ActiveState:
        container = self._observe_container(root_fd)
        if container.kind == "other" or container.kind == "symlink":
            raise _AdmissionFailure(
                "bootstrap-container-conflict",
                phase="bootstrap-container",
                last_completed_phase="candidate-staging",
                operation=active.operation,
                candidate_digest=active.candidate_digest,
                seed_policy=active.seed_policy,
            )
        if container.kind == "absent":
            self._check_fault("bootstrap-container-mkdir")
            self._check_fault("bootstrap-container-fsync")
            container_fd = _mkdir_child(root_fd, "spec-dock")
            try:
                self._filesystem().fsync_directory(root_fd)
                witness = self._filesystem().capture_inode(root_fd, "spec-dock", "directory")
            finally:
                os.close(container_fd)
            if witness is None:
                raise FilesystemSafetyError("bootstrap container disappeared")
            active = replace(
                active, bootstrap_container={"disposition": "created", "witness": _witness_mapping(witness)}
            )
            self._save_active(active_store, active)
        return active

    def _terminal_record_bytes(self, active: ActiveState) -> bytes:
        state = "tooling-absent-preserved-data" if active.operation == "uninstall" else "ready"
        record = InstallationRecord(
            1,
            cast("RecordState", state),
            None,
            CANDIDATE_VERSION,
            active.candidate_digest,
            active.seed_policy,
            {"spec-dock": CANDIDATE_VERSION, "spec-dock-grill-with-docs": CANDIDATE_VERSION},
        )
        return serialize_installation_record(record)

    def _write_public_record(
        self,
        _request: LifecycleRequest,
        active: ActiveState,
        payload: bytes,
        active_store: ActiveStateStore,
        root_fd: int,
    ) -> None:
        for point in ("record-temp-open", "record-temp-write", "record-temp-fsync"):
            self._check_fault(point)
        witness = active_store.write_record_temp(payload)
        self._save_active(active_store, replace(active, record_temp_witness=witness))
        self._check_fault("record-temp-parent-fsync")
        namespace_fd = active_store._open_namespace()
        specdock_fd = _open_path(root_fd, ("spec-dock",), create=True)
        filesystem = self._filesystem()
        try:
            try:
                old_raw, old_witness = _read_regular(specdock_fd, "spec-dock.version")
            except FileNotFoundError:
                old_raw, old_witness = None, None
            if old_witness is None:
                self._check_fault("record-publish-no-replace")
                filesystem.rename_no_replace(
                    namespace_fd,
                    RECORD_TEMP_NAME,
                    specdock_fd,
                    "spec-dock.version",
                    expected_source=witness,
                )
            else:
                self._check_fault("record-publish-exchange")
                filesystem.exchange(
                    namespace_fd,
                    RECORD_TEMP_NAME,
                    specdock_fd,
                    "spec-dock.version",
                    expected_destination=old_witness,
                )
                residue_raw, residue_witness = _read_regular(namespace_fd, RECORD_TEMP_NAME)
                if not NativeAtomicFilesystem._same_content_identity(residue_witness, old_witness):
                    filesystem.exchange(namespace_fd, RECORD_TEMP_NAME, specdock_fd, "spec-dock.version")
                    raise PrivateStateForeignError("public record exchange residue is foreign")
                self._check_fault("record-exchange-residue-unlink")
                filesystem.unlink_bound(namespace_fd, RECORD_TEMP_NAME, residue_witness)
                del residue_raw
            self._check_fault("record-parent-fsync")
            filesystem.fsync_directory(specdock_fd)
            current_raw, current_witness = _read_regular(specdock_fd, "spec-dock.version")
            if current_raw != payload or current_witness.mode != 0o644:
                raise FilesystemSafetyError("public record postcondition failed")
            del old_raw
        finally:
            os.close(specdock_fd)
            os.close(namespace_fd)
        self._save_active(active_store, replace(active, record_temp_witness=None))

    def _target_matches_candidate(
        self,
        root_fd: int,
        path: str,
        index: int,
        candidate: CandidateIdentity,
    ) -> bool:
        item = self._observe_target(root_fd, path, expect_tree=True)
        if item.kind != "directory" or item.tree is None:
            return False
        expected = candidate.domains[index]
        if item.tree.tree_digest != expected.tree_digest or item.tree.entry_count != expected.entry_count:
            return False
        if index < 4:
            return True
        components = _target_components(path)
        parent_fd = _open_path(root_fd, components[:-1])
        try:
            try:
                target_fd = _open_path(root_fd, components)
            except FileNotFoundError:
                return False
            try:
                marker_raw, _marker_witness = _read_regular(target_fd, SLOT_MARKER_NAME)
            except (FileNotFoundError, FilesystemSafetyError):
                return False
            finally:
                os.close(target_fd)
            marker = parse_slot_marker(marker_raw)
            return (
                marker.slot == path
                and marker.version == CANDIDATE_VERSION
                and marker.candidate_digest == candidate.aggregate_digest
            )
        finally:
            os.close(parent_fd)

    def _publish_domain(
        self,
        _request: LifecycleRequest,
        _active: ActiveState,
        stage_store: StageStore,
        index: int,
        candidate: CandidateIdentity | None,
        root_fd: int,
        *,
        detach: bool,
    ) -> None:
        kind, path, _source = FIXED_DOMAINS[index]
        name = STAGE_ENTRY_NAMES[index]
        fault_name = path.rsplit("/", 1)[-1] if index < 4 else name.removeprefix("slot-")
        self._check_fault(f"{kind}-{fault_name}-publish-or-detach")
        components = _target_components(path)
        if detach:
            observed = self._observe_target(root_fd, path, expect_tree=True)
            if observed.kind != "directory":
                return
        destination_parent = _open_path(root_fd, components[:-1], create=not detach)
        stage_fd = stage_store._stage_fd()
        filesystem = self._filesystem()
        try:
            target = self._observe_target(root_fd, path, expect_tree=True)
            if detach:
                if target.kind != "directory":
                    return
                if target.witness is None:
                    raise FilesystemSafetyError(f"missing fixed target witness at {path}")
                try:
                    stage_tree = filesystem.capture_domain_tree(stage_fd, name)
                    filesystem.remove_tree_bound(stage_fd, name, stage_tree)
                except FileNotFoundError:
                    pass
                filesystem.rename_no_replace(
                    destination_parent,
                    components[-1],
                    stage_fd,
                    name,
                    expected_source=target.witness,
                )
            else:
                if candidate is None:
                    raise CandidateError("candidate is required for publication")
                if self._target_matches_candidate(root_fd, path, index, candidate):
                    return
                if target.kind == "absent":
                    filesystem.rename_no_replace(stage_fd, name, destination_parent, components[-1])
                elif target.kind == "directory":
                    old_tree = filesystem.capture_domain_tree(destination_parent, components[-1])
                    if target.witness is None:
                        raise FilesystemSafetyError(f"missing fixed target witness at {path}")
                    filesystem.exchange(
                        stage_fd,
                        name,
                        destination_parent,
                        components[-1],
                        expected_destination=target.witness,
                    )
                    residue = filesystem.capture_domain_tree(stage_fd, name)
                    filesystem.remove_tree_bound(stage_fd, name, residue if residue != old_tree else old_tree)
                else:
                    raise FilesystemSafetyError(f"unsafe fixed target type at {path}")
            self._check_fault("source-parent-fsync")
            filesystem.fsync_directory(stage_fd)
            self._check_fault("target-parent-fsync")
            filesystem.fsync_directory(destination_parent)
        finally:
            os.close(stage_fd)
            os.close(destination_parent)

    def _publish_seed(
        self,
        _request: LifecycleRequest,
        active: ActiveState,
        root_fd: int,
        public_path: str,
        seed_name: str,
        source_suffix: str,
    ) -> None:
        item = self._observe_target(root_fd, public_path, expect_tree=False)
        if item.kind == "symlink" or item.kind == "other" or item.kind == "directory":
            raise FilesystemSafetyError(f"unsafe seed type at {public_path}")
        if item.kind == "regular":
            return
        if item.kind == "absent" and active.seed_policy != "create-if-absent":
            return
        if item.kind != "absent":
            return
        self._check_fault(f"seed-{seed_name}-no-replace-create")
        components = _target_components(public_path)
        parent_fd = _open_path(root_fd, components[:-1], create=True)
        destination_fd = -1
        try:
            source = self._assets() / source_suffix
            source_fd = os.open(
                source,
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
            )
        except BaseException:
            os.close(parent_fd)
            raise
        try:
            try:
                destination_fd = os.open(
                    components[-1],
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
                    0o644,
                    dir_fd=parent_fd,
                )
                while True:
                    chunk = os.read(source_fd, 1024 * 1024)
                    if not chunk:
                        break
                    cursor = 0
                    while cursor < len(chunk):
                        cursor += os.write(destination_fd, chunk[cursor:])
                os.fchmod(destination_fd, 0o644)
                os.fsync(destination_fd)
            except FileExistsError:
                # The no-replace operation lost a race.  Reclassify the visible
                # entry; never replace a consumer seed.
                pass
            self._check_fault(f"seed-{seed_name}-parent-fsync")
            self._filesystem().fsync_directory(parent_fd)
        finally:
            if destination_fd >= 0:
                os.close(destination_fd)
            os.close(source_fd)
            os.close(parent_fd)

    def _finish_cleanup(
        self,
        request: LifecycleRequest,
        active: ActiveState,
        active_store: ActiveStateStore,
        receipt_store: CompletionReceiptStore,
        stage_store: StageStore,
        root_fd: int,
    ) -> LifecycleResult:
        try:
            self._cleanup_stage(stage_store)
            self._check_fault("stage-parent-fsync")
            receipt = CompletionReceipt(
                1,
                active.repository_key,
                active.tuple_key,
                active.operation_generation,
                active.operation,
                active.candidate_digest,
                active.seed_policy,
                active.result_family,
                active.terminal_record_digest,
                active.cleanup_token,
                active.cleanup_retry_invocation,
                active.deferred_invocation,
            )
            for point in (
                "receipt-temp-open",
                "receipt-temp-write",
                "receipt-temp-fsync",
                "receipt-temp-rename",
                "receipt-parent-fsync",
            ):
                self._check_fault(point)
            receipt_store.save(receipt)
            self._check_fault("active-expected-unlink")
            namespace_fd = active_store._open_namespace()
            try:
                witness = active_store._current_witness()
                if witness is not None:
                    self._filesystem().unlink_bound(namespace_fd, ACTIVE_NAME, witness)
                    self._check_fault("active-expected-parent-fsync")
                    self._filesystem().fsync_directory(namespace_fd)
            finally:
                os.close(namespace_fd)
        except (
            AtomicRenameUnavailable,
            FilesystemSafetyError,
            PrivateStateError,
            OSError,
            _InjectedFailure,
        ) as failure:
            return self._terminal_cleanup_failure(request, active, failure)
        try:
            self._check_fault("response-loss")
        except _InjectedFailure:
            # The durable terminal state is already complete.  The seam models
            # a lost response without manufacturing a second mutation attempt.
            return self._completed_result(request, active, root_fd)
        return self._completed_result(request, active, root_fd)

    def _cleanup_stage(self, stage_store: StageStore) -> None:
        try:
            stage_fd = stage_store._stage_fd()
        except PrivateStateError as exc:
            namespace_fd = stage_store._namespace_fd()
            try:
                try:
                    os.stat(STAGE_NAME, dir_fd=namespace_fd, follow_symlinks=False)
                except FileNotFoundError:
                    return
            finally:
                os.close(namespace_fd)
            raise exc
        try:
            for name in STAGE_ENTRY_NAMES:
                try:
                    tree = self._filesystem().capture_domain_tree(stage_fd, name)
                except FileNotFoundError:
                    continue
                self._check_fault(f"stage-entry-{name}-remove")
                self._filesystem().remove_tree_bound(stage_fd, name, tree)
            try:
                value = os.stat(STAGE_OWNER_NAME, dir_fd=stage_fd, follow_symlinks=False)
            except FileNotFoundError:
                value = None
            if value is not None:
                if not stat.S_ISREG(value.st_mode) or stat.S_IMODE(value.st_mode) != 0o600 or value.st_nlink != 1:
                    raise PrivateStateForeignError("STAGE-OWNER.json is unsafe")
                owner_witness = self._filesystem().capture_inode(stage_fd, STAGE_OWNER_NAME, "regular")
                if owner_witness is None:
                    raise PrivateStateForeignError("STAGE-OWNER.json disappeared during cleanup")
                self._filesystem().unlink_bound(stage_fd, STAGE_OWNER_NAME, owner_witness)
            os.fsync(stage_fd)
        finally:
            os.close(stage_fd)
        namespace_fd = stage_store._namespace_fd()
        try:
            self._check_fault("stage-remove")
            os.rmdir(STAGE_NAME, dir_fd=namespace_fd)
            self._filesystem().fsync_directory(namespace_fd)
        finally:
            os.close(namespace_fd)

    def _completed_result(self, request: LifecycleRequest, active: ActiveState, root_fd: int) -> LifecycleResult:
        if active.operation == "uninstall":
            targets = self._observe_domains(root_fd)
            actions = self._uninstall_actions(
                targets,
                self._observe_container(root_fd),
                None,
                planned=False,
                include_stage=True,
            )
            code = "uninstall-completed"
        else:
            candidate = self._candidate()
            targets = self._observe_domains(root_fd)
            actions = self._install_actions(
                active.operation,
                active.seed_policy,
                candidate,
                targets,
                root_fd,
                planned=False,
                include_stage=True,
            )
            code = f"{active.result_family}-completed"
        return build_public_result(
            request,
            status="completed",
            code=code,
            operation=active.operation,
            candidate_digest=active.candidate_digest,
            seed_policy=active.seed_policy,
            mutation_started=True,
            phase="complete",
            last_completed_phase="cleanup-stage",
            actions=actions,
        )

    def _terminal_cleanup_failure(
        self,
        request: LifecycleRequest,
        active: ActiveState,
        _failure: BaseException,
    ) -> LifecycleResult:
        retry = active.cleanup_retry_invocation["rendered_command"]
        actions = (LifecycleAction("@provider-stage", "stage", "failed", "candidate-stage-cleanup"),)
        failed_paths, pending_paths = _action_path_sets(actions)
        return build_public_result(
            request,
            status="partial_failure",
            code="terminal-cleanup-failed",
            operation=active.operation,
            candidate_digest=active.candidate_digest,
            seed_policy=active.seed_policy,
            mutation_started=True,
            phase="cleanup-stage",
            last_completed_phase="publish-terminal-record",
            retry_command=retry,
            continuation=_cleanup_continuation(retry, active.deferred_invocation),
            failed_paths=failed_paths,
            pending_paths=pending_paths,
            actions=actions,
            guidance=(
                CLEANUP_FAILED_DEFERRED_GUIDANCE if active.deferred_invocation is not None else CLEANUP_FAILED_GUIDANCE
            ),
        )

    def _partial_failure_result(
        self,
        request: LifecycleRequest,
        active: ActiveState,
        failure: BaseException,
        root_fd: int,
    ) -> LifecycleResult:
        if active.state in {"ready", "terminal-cleanup"}:
            return self._terminal_cleanup_failure(request, active, failure)
        point = getattr(failure, "point", "")
        phase = self._phase_for_fault(point, active.operation)
        if phase == "bootstrap-container":
            return self._preparation_failure(
                request,
                active.operation,
                active.candidate_digest,
                active.seed_policy,
                failure,
                phase="publish-incomplete-record",
                last_completed_phase="bootstrap-container",
            )
        if active.state == "prepared" and phase in {"candidate-staging", "publish-incomplete-record"}:
            return self._preparation_failure(
                request,
                active.operation,
                active.candidate_digest,
                active.seed_policy,
                failure,
                phase=phase,
                last_completed_phase="preflight" if phase == "candidate-staging" else "bootstrap-container",
                mutation_started=phase == "publish-incomplete-record" and not point.startswith("record-temp-"),
            )
        if phase == "preflight":
            return self._blocked(request, "lifecycle-preparation-failed")
        retry = self._retry_for(request, active.operation, active.seed_policy)
        if retry is None:
            retry = active.cleanup_retry_invocation["rendered_command"]
        index = self._fault_index(point)
        if active.operation == "uninstall":
            actions = list(
                self._uninstall_actions(
                    self._observe_domains(root_fd),
                    self._observe_container(root_fd),
                    None,
                    planned=False,
                    include_stage=True,
                    partial_index=index,
                )
            )
            code = "uninstall-partial-failure"
        else:
            candidate = self._candidate()
            actions = list(
                self._install_actions(
                    active.operation,
                    active.seed_policy,
                    candidate,
                    self._observe_domains(root_fd),
                    root_fd,
                    planned=False,
                    partial_index=index,
                    include_stage=True,
                    failure_point=point,
                )
            )
            code = "install-partial-failure" if active.operation == "install" else "update-partial-failure"
        if actions and actions[-1].path == "@provider-stage":
            actions[-1] = LifecycleAction("@provider-stage", "stage", "pending", "candidate-stage-cleanup")
        last_completed = self._last_completed_phase(phase, active.operation)
        failed_paths, pending_paths = _action_path_sets(actions)
        return build_public_result(
            request,
            status="partial_failure",
            code=code,
            operation=active.operation,
            candidate_digest=active.candidate_digest,
            seed_policy=active.seed_policy,
            mutation_started=True,
            phase=phase,
            last_completed_phase=last_completed,
            retry_command=retry,
            continuation=_lifecycle_continuation(retry),
            failed_paths=failed_paths,
            pending_paths=pending_paths,
            actions=actions,
            guidance=LIFECYCLE_GUIDANCE,
        )

    @staticmethod
    def _last_completed_phase(phase: str, operation: str) -> str:
        order = [value for value in PHASES if operation == "uninstall" or not value.startswith("detach-")]
        try:
            index = order.index(phase)
        except ValueError:
            return "request-validation"
        return "request-validation" if index == 0 else order[index - 1]

    @staticmethod
    def _fault_index(point: str) -> int | None:
        for index, name in enumerate(STAGE_ENTRY_NAMES):
            if name in point:
                return index
        names = ("docs", "templates", "system", "scripts", "spec-dock", "spec-dock-grill-with-docs")
        for index, name in enumerate(names):
            if name in point:
                return index
        if "verify" in point:
            return 6
        if "terminal-record" in point:
            return 7
        if "seed-spec-dock" in point:
            return 6
        if "seed-consumer" in point:
            return 7
        return None

    @staticmethod
    def _phase_for_fault(point: str, operation: str) -> str:
        if not point:
            return "publish-incomplete-record"
        if point.startswith("bootstrap"):
            return "bootstrap-container"
        if point.startswith("record-") or point.startswith("record_"):
            return "publish-incomplete-record"
        for _index, name in enumerate((
            "docs",
            "templates",
            "system",
            "scripts",
            "slot-spec-dock",
            "slot-spec-dock-grill-with-docs",
        )):
            if name in point:
                return ("detach-" if operation == "uninstall" else "publish-") + name
        if point.startswith("seed-spec-dock-gitignore"):
            return "create-seed-spec-dock-gitignore"
        if point.startswith("seed-consumer-ci"):
            return "create-seed-consumer-ci"
        if point.startswith("target-verify"):
            return "verify-target"
        if point in {"source-parent-fsync", "target-parent-fsync"}:
            return "detach-docs" if operation == "uninstall" else "publish-docs"
        if point.startswith("stage") or point.startswith("receipt") or point.startswith("active"):
            return "cleanup-stage"
        return "publish-incomplete-record"

    def _cleanup_retry_or_replay(
        self,
        request: LifecycleRequest,
        token: str,
        active: ActiveState | None,
        receipt: CompletionReceipt | None,
        active_store: ActiveStateStore | None,
        receipt_store: CompletionReceiptStore | None,
        stage_store: StageStore | None,
        root_fd: int,
    ) -> LifecycleResult:
        if active is not None and active.cleanup_token == token:
            if active_store is None or receipt_store is None or stage_store is None:
                return self._blocked(request, "lifecycle-preparation-failed")
            return self._finish_cleanup(request, active, active_store, receipt_store, stage_store, root_fd)
        if receipt is not None and receipt.cleanup_token == token:
            return build_public_result(
                request,
                status="completed",
                code="terminal-cleanup-completed",
                operation=receipt.operation,
                candidate_digest=receipt.candidate_digest,
                seed_policy=receipt.seed_policy,
                phase="complete",
                last_completed_phase="cleanup-stage",
                actions=(LifecycleAction("@provider-stage", "stage", "completed", "candidate-stage-cleanup"),),
                continuation=_completed_cleanup_continuation(receipt.deferred_invocation),
                guidance=(
                    CLEANUP_COMPLETED_DEFERRED_GUIDANCE
                    if receipt.deferred_invocation is not None
                    else CLEANUP_COMPLETED_GUIDANCE
                ),
            )
        return self._blocked(request, "lifecycle-preparation-failed")

    def _complete_pending_cleanup(
        self,
        request: LifecycleRequest,
        active: ActiveState,
        active_store: ActiveStateStore | None,
        receipt_store: CompletionReceiptStore | None,
        stage_store: StageStore | None,
        root_fd: int,
    ) -> LifecycleResult:
        if active_store is None or receipt_store is None or stage_store is None:
            return self._blocked(request, "lifecycle-preparation-failed")
        if active.state == "ready":
            active = replace(active, state="terminal-cleanup")
            try:
                self._save_active(active_store, active)
            except (
                AtomicRenameUnavailable,
                FilesystemSafetyError,
                PrivateStateError,
                OSError,
                _InjectedFailure,
            ) as failure:
                return self._terminal_cleanup_failure(request, active, failure)
        return self._finish_cleanup(request, active, active_store, receipt_store, stage_store, root_fd)

    def _resume_or_block(
        self,
        request: LifecycleRequest,
        operation: str,
        seed_policy: str,
        candidate: CandidateIdentity | None,
        active: ActiveState,
        active_store: ActiveStateStore | None,
        receipt_store: CompletionReceiptStore | None,
        stage_store: StageStore | None,
        root_fd: int,
        *,
        force: bool | None,
    ) -> LifecycleResult:
        del force
        if active.operation != operation:
            return self._blocked(
                request,
                "resume-operation-mismatch",
                operation=active.operation,
                candidate_digest=active.candidate_digest,
                seed_policy=active.seed_policy,
            )
        if candidate is not None and candidate.aggregate_digest != active.candidate_digest:
            return self._blocked(
                request,
                "resume-candidate-mismatch",
                operation=operation,
                candidate_digest=active.candidate_digest,
                seed_policy=active.seed_policy,
                phase="candidate-staging",
                last_completed_phase="preflight",
            )
        if seed_policy != active.seed_policy and operation != "uninstall":
            return self._blocked(
                request,
                "resume-seed-policy-mismatch",
                operation=operation,
                candidate_digest=active.candidate_digest,
                seed_policy=active.seed_policy,
            )
        if active_store is None or receipt_store is None or stage_store is None:
            return self._blocked(request, "lifecycle-preparation-failed")
        try:
            self._prepare_stage(stage_store, active, candidate)
        except (
            AtomicRenameUnavailable,
            FilesystemSafetyError,
            PrivateStateError,
            OSError,
            _InjectedFailure,
        ) as failure:
            return self._partial_failure_result(request, active, failure, root_fd)
        return self._run_active(request, active, candidate, active_store, receipt_store, stage_store, root_fd)
