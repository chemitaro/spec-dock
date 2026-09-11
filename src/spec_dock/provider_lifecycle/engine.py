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
import errno
import hashlib
import os
from pathlib import Path
import secrets
import shlex
import stat
from typing import TYPE_CHECKING, Literal, TypeVar, cast

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
    SEED_PATHS,
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
    SeedAdmissionState,
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
    project_domain_tree,
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
    resolve_private_namespace_at,
    tuple_key_for,
    validate_private_namespace_at,
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
    def __init__(
        self,
        point: str,
        *,
        cause: BaseException | None = None,
        bootstrap_rolled_back: bool = False,
        bootstrap_cleanup_failed: bool = False,
    ) -> None:
        super().__init__(point)
        self.point = point
        self.phase = point
        self.cause = cause
        self.bootstrap_rolled_back = bootstrap_rolled_back
        self.bootstrap_cleanup_failed = bootstrap_cleanup_failed


_PhaseResult = TypeVar("_PhaseResult")


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


def _cleanup_request_matches(
    request: LifecycleRequest,
    *,
    force: bool | None,
    token: str,
    expected: Mapping[str, str],
) -> bool:
    """Require the caller's hidden cleanup form to be the derived exact form."""

    desired = _desired_invocation(request, force=force)
    if desired["invocation_id"] != expected.get("invocation_id"):
        return False
    operation = _operation_from_request(request)
    seed_policy = _seed_from_request(request, operation)
    actual = _cleanup_invocation(request, operation, seed_policy, token)
    return actual == dict(expected)


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


def _target_components(path: str) -> tuple[str, ...]:
    parts = tuple(part for part in Path(path).parts if part not in {"", "/"})
    if any(part in {".", ".."} for part in parts):
        raise FilesystemSafetyError("target path contains dot components")
    return parts


def _safe_component(name: str) -> None:
    if not name or name in {".", ".."} or "/" in name or "\x00" in name:
        raise FilesystemSafetyError(f"unsafe relative component: {name!r}")


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
    if create:
        return _open_path_bound(root_fd, components, create=True)[0]
    current = os.dup(root_fd)
    try:
        for component in components:
            _safe_component(component)
            next_fd = _open_existing_child(current, component)
            if next_fd is None:
                raise FileNotFoundError(component)
            os.close(current)
            current = next_fd
        return current
    except BaseException:
        os.close(current)
        raise


def _directory_witness(fd: int) -> InodeWitness:
    value = os.fstat(fd)
    if not stat.S_ISDIR(value.st_mode):
        raise FilesystemSafetyError("path component is not a directory")
    return NativeAtomicFilesystem._witness(value, "directory", None)


def _directory_witness_or_close(fd: int) -> InodeWitness:
    try:
        return _directory_witness(fd)
    except BaseException:
        with contextlib.suppress(OSError):
            os.close(fd)
        raise


def _same_directory_binding(left: InodeWitness, right: InodeWitness) -> bool:
    return (
        left.kind == right.kind == "directory"
        and left.device == right.device
        and left.inode == right.inode
        and left.mode == right.mode
    )


def _rollback_created_path_components(created: list[tuple[int, str, InodeWitness]]) -> None:
    failure: BaseException | None = None
    for parent_fd, name, expected in reversed(created):
        try:
            try:
                value = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                continue
            current = NativeAtomicFilesystem._witness(value, "directory", None)
            if not _same_directory_binding(current, expected):
                raise FilesystemSafetyError(f"created path component {name!r} changed during rollback")
            os.rmdir(name, dir_fd=parent_fd)
            os.fsync(parent_fd)
        except (FilesystemSafetyError, OSError) as error:
            failure = failure or error
        finally:
            os.close(parent_fd)
    if failure is not None:
        raise FilesystemSafetyError("created path component cleanup failed") from failure


def _open_path_visible(root_fd: int, components: Sequence[str]) -> tuple[int, tuple[InodeWitness, ...]]:
    current = os.dup(root_fd)
    witnesses: list[InodeWitness] = []
    try:
        for component in components:
            _safe_component(component)
            next_fd = _open_existing_child(current, component)
            if next_fd is None:
                raise FileNotFoundError(component)
            witnesses.append(_directory_witness_or_close(next_fd))
            os.close(current)
            current = next_fd
        return current, tuple(witnesses)
    except BaseException:
        os.close(current)
        raise


def _open_path_bound(
    root_fd: int,
    components: Sequence[str],
    *,
    create: bool = False,
) -> tuple[int, tuple[InodeWitness, ...]]:
    """Open a root-relative directory chain and retain its transient witnesses."""

    current = os.dup(root_fd)
    witnesses: list[InodeWitness] = []
    created: list[tuple[int, str, InodeWitness]] = []
    try:
        for index, component in enumerate(components):
            _safe_component(component)
            next_fd = _open_existing_child(current, component)
            if next_fd is None:
                if not create:
                    raise FileNotFoundError(component)
                cleanup_parent_fd = os.dup(current)
                try:
                    os.mkdir(component, 0o755, dir_fd=current)
                except FileExistsError as failure:
                    os.close(cleanup_parent_fd)
                    raise FilesystemSafetyError(
                        f"path component {component!r} appeared during exclusive creation"
                    ) from failure
                next_fd = -1
                try:
                    next_fd = os.open(
                        component,
                        os.O_RDONLY
                        | getattr(os, "O_DIRECTORY", 0)
                        | getattr(os, "O_NOFOLLOW", 0)
                        | getattr(os, "O_CLOEXEC", 0),
                        dir_fd=current,
                    )
                    created_witness = _directory_witness(next_fd)
                except BaseException:
                    if next_fd >= 0:
                        os.close(next_fd)
                    with contextlib.suppress(OSError):
                        os.rmdir(component, dir_fd=current)
                    os.close(cleanup_parent_fd)
                    raise
                created.append((cleanup_parent_fd, component, created_witness))
                try:
                    os.fsync(current)
                    if index >= 0:
                        visible_fd, visible = _open_path_visible(root_fd, tuple(components[: index + 1]))
                        try:
                            if (
                                len(visible) != index + 1
                                or any(
                                    not _same_directory_binding(left, right)
                                    for left, right in zip(witnesses, visible[:-1], strict=True)
                                )
                                or not _same_directory_binding(created_witness, visible[-1])
                            ):
                                raise FilesystemSafetyError("created path component is no longer root-visible")
                        finally:
                            os.close(visible_fd)
                except BaseException:
                    os.close(next_fd)
                    raise
            witnesses.append(_directory_witness_or_close(next_fd))
            os.close(current)
            current = next_fd
        for parent_fd, _name, _expected in created:
            os.close(parent_fd)
        return current, tuple(witnesses)
    except BaseException as failure:
        try:
            _rollback_created_path_components(created)
        except FilesystemSafetyError as cleanup_failure:
            os.close(current)
            raise cleanup_failure from failure
        os.close(current)
        raise


def _require_path_binding(
    root_fd: int,
    components: Sequence[str],
    expected: Sequence[InodeWitness],
    bound_fd: int,
) -> None:
    """Reject a parent descriptor that no longer names the visible root-relative chain."""

    bound = _directory_witness(bound_fd)
    visible_fd, visible = _open_path_bound(root_fd, components)
    try:
        if (
            len(expected) != len(visible)
            or not _same_directory_binding(bound, expected[-1])
            or any(not _same_directory_binding(left, right) for left, right in zip(expected, visible, strict=True))
        ):
            raise FilesystemSafetyError("parent path binding changed before mutation")
    finally:
        os.close(visible_fd)


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


def _copy_tree(
    source: Path,
    destination_fd: int,
    *,
    slot: str | None,
    candidate: CandidateIdentity,
    fault: Callable[[str], None] | None = None,
    fault_prefix: str | None = None,
) -> None:
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
        if fault is not None and fault_prefix is not None:
            fault(f"{fault_prefix}-fsync")
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

    def _execute_phase(self, phase: str, callback: Callable[[], _PhaseResult]) -> _PhaseResult:
        try:
            return callback()
        except (
            _InjectedFailure,
            _AdmissionFailure,
            PrivateStateForeignError,
            _LifecycleFailure,
            AtomicRenameUnavailable,
        ):
            raise
        except (FilesystemSafetyError, PrivateStateError, OSError) as failure:
            raise _LifecycleFailure(phase, cause=failure) from failure

    def _filesystem(self) -> NativeAtomicFilesystem:
        if self.filesystem is None:
            self.filesystem = NativeAtomicFilesystem()
        return self.filesystem

    def _capture_engine_domain(
        self,
        parent_fd: int,
        name: str,
        *,
        exclude_marker: bool = False,
    ) -> tuple[InodeWitness, DomainTreeIdentity]:
        witness, tree = self._filesystem().capture_bound_domain_tree(parent_fd, name)
        for entry in tree.entries:
            if entry.kind == "regular" and entry.mode not in {0o644, 0o755}:
                raise FilesystemSafetyError(f"unsupported regular mode at {entry.path}")
            if entry.kind == "symlink" and (
                entry.target is None or entry.target.startswith("/") or "\\" in entry.target or "\x00" in entry.target
            ):
                raise FilesystemSafetyError(f"unsafe symlink at {entry.path}")
        if exclude_marker:
            tree = project_domain_tree(tree, exclude_root_names={SLOT_MARKER_NAME})
        return witness, tree

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
        try:
            filesystem = self._filesystem()
        except AtomicRenameUnavailable:
            return self._blocked(
                request,
                "atomic-rename-unavailable",
                operation=operation,
                candidate_digest=None,
                seed_policy=seed_policy,
            )
        try:
            bound = filesystem.open_directory_chain_no_follow(request.target)
        except OSError:
            return self._blocked(request, "unsafe-repository-binding")
        with bound:
            try:
                lease.revalidate()
                bound_stat = os.fstat(bound.fd)
            except (RepositoryCoordinationError, OSError):
                return self._blocked(request, "unsafe-repository-binding")
            if (
                not stat.S_ISDIR(bound_stat.st_mode)
                or bound_stat.st_dev != lease.binding.device
                or bound_stat.st_ino != lease.binding.inode
            ):
                return self._blocked(request, "unsafe-repository-binding")
            try:
                filesystem.probe_native_capability(bound.fd)
            except AtomicRenameUnavailable:
                return self._blocked(
                    request,
                    "atomic-rename-unavailable",
                    operation=operation,
                    candidate_digest=None,
                    seed_policy=seed_policy,
                )
            except (FilesystemSafetyError, OSError):
                return self._blocked(request, "unsafe-repository-binding")
            try:
                namespace = self._namespace_for(request.target, lease)
                active_store, receipt_store, stage_store = self._stores(
                    namespace,
                    request.apply,
                    repository_root_fd=bound.fd,
                    repository_binding=lease.binding,
                )
            except AtomicRenameUnavailable:
                return self._blocked(
                    request,
                    "atomic-rename-unavailable",
                    operation=operation,
                    candidate_digest=None,
                    seed_policy=seed_policy,
                )
            except PrivateStateForeignError:
                return self._blocked(request, "stage-owner-mismatch")
            except (PrivateStateError, OSError, _InjectedFailure):
                return self._blocked(request, "lifecycle-preparation-failed")
            try:
                active, active_witness = active_store.load_with_witness() if active_store is not None else (None, None)
                receipt, receipt_witness = (
                    receipt_store.load_with_witness() if receipt_store is not None else (None, None)
                )
                if active is not None and active_store is not None:
                    if active_witness is None:
                        return self._blocked(request, "lifecycle-preparation-failed")
                    active_witness = active_store.ensure_durable(expected=active_witness)
                    if active_witness is None:
                        return self._blocked(request, "lifecycle-preparation-failed")
                if receipt is not None and receipt_store is not None:
                    if receipt_witness is None:
                        return self._blocked(request, "lifecycle-preparation-failed")
                    receipt_witness = receipt_store.ensure_durable(expected=receipt_witness)
            except AtomicRenameUnavailable:
                return self._blocked(
                    request,
                    "atomic-rename-unavailable",
                    operation=operation,
                    candidate_digest=None,
                    seed_policy=seed_policy,
                )
            except PrivateStateForeignError:
                return self._blocked(request, "stage-owner-mismatch")
            except (PrivateStateError, OSError):
                return self._blocked(request, "lifecycle-preparation-failed")

            if active is not None:
                assert active_store is not None
                try:
                    active_valid = self._validate_active_authority(
                        active,
                        bound.fd,
                        request.target,
                        active_store=active_store,
                    )
                except _AdmissionFailure as failure:
                    return self._admission_result(request, failure)
                except PrivateStateForeignError:
                    return self._blocked(
                        request,
                        "stage-owner-mismatch",
                        operation=active.operation,
                        candidate_digest=active.candidate_digest,
                        seed_policy=active.seed_policy,
                        phase="candidate-staging",
                        last_completed_phase="preflight",
                    )
                except (FilesystemSafetyError, PrivateStateError, OSError, ValueError, WireValidationError):
                    return self._blocked(
                        request,
                        "lifecycle-preparation-failed",
                        operation=active.operation,
                        candidate_digest=active.candidate_digest,
                        seed_policy=active.seed_policy,
                        phase="candidate-staging",
                        last_completed_phase="preflight",
                    )
                if not active_valid:
                    return self._blocked(
                        request,
                        "stage-owner-mismatch",
                        operation=active.operation,
                        candidate_digest=active.candidate_digest,
                        seed_policy=active.seed_policy,
                        phase="candidate-staging",
                        last_completed_phase="preflight",
                    )

            if cleanup_token is not None:
                if active is not None and active.state not in {"ready", "terminal-cleanup"}:
                    return self.invalid_request(request)
                return self._cleanup_retry_or_replay(
                    request,
                    cleanup_token,
                    active,
                    receipt,
                    active_store,
                    receipt_store,
                    stage_store,
                    bound.fd,
                    active_witness=active_witness,
                    receipt_witness=receipt_witness,
                    force=force,
                )
            if active is not None:
                if active_witness is None:
                    return self._blocked(request, "lifecycle-preparation-failed")
                if active.state in {"ready", "terminal-cleanup"}:
                    return self._complete_pending_cleanup(
                        request,
                        active,
                        active_store,
                        receipt_store,
                        stage_store,
                        bound.fd,
                        active_witness=active_witness,
                        receipt_witness=receipt_witness,
                        force=force,
                        receipt=receipt,
                    )
                if receipt is not None and not self._receipt_matches_active(receipt, active):
                    return self.invalid_request(request)
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
                try:
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
                        active_witness=active_witness,
                    )
                except _AdmissionFailure as failure:
                    return self._admission_result(request, failure)

            if receipt is not None and not self._receipt_matches_repository(receipt, lease):
                return self.invalid_request(request)
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
                    receipt_witness=receipt_witness,
                )
            except _AdmissionFailure as failure:
                return self._admission_result(request, failure)
            except AtomicRenameUnavailable:
                return self._blocked(
                    request,
                    "atomic-rename-unavailable",
                    operation=operation,
                    candidate_digest=None,
                    seed_policy=seed_policy,
                )
            except (FilesystemSafetyError, PrivateStateError, OSError) as failure:
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
        *,
        repository_root_fd: int,
        repository_binding: RepositoryBinding,
    ) -> tuple[ActiveStateStore | None, CompletionReceiptStore | None, StageStore | None]:
        root_binding = (repository_binding.device, repository_binding.inode)
        if apply:
            for point in ("private-top-mkdir", "private-top-fsync", "private-repo-mkdir", "private-repo-fsync"):
                self._check_fault(point)
            namespace = resolve_private_namespace_at(
                repository_root_fd,
                namespace,
                effective_euid=repository_binding.euid,
                expected_binding=root_binding,
            )
            active = ActiveStateStore(
                namespace,
                repository_root_fd=repository_root_fd,
                repository_root_binding=root_binding,
            )
            receipt = CompletionReceiptStore(
                namespace,
                repository_root_fd=repository_root_fd,
                repository_root_binding=root_binding,
            )
            return (
                active,
                receipt,
                StageStore(
                    namespace,
                    active,
                    repository_root_fd=repository_root_fd,
                    repository_root_binding=root_binding,
                ),
            )
        if not validate_private_namespace_at(
            repository_root_fd,
            namespace,
            effective_euid=repository_binding.euid,
            expected_binding=root_binding,
        ):
            return None, None, None
        active = ActiveStateStore(
            namespace,
            repository_root_fd=repository_root_fd,
            repository_root_binding=root_binding,
        )
        receipt = CompletionReceiptStore(
            namespace,
            repository_root_fd=repository_root_fd,
            repository_root_binding=root_binding,
        )
        return (
            active,
            receipt,
            StageStore(
                namespace,
                active,
                repository_root_fd=repository_root_fd,
                repository_root_binding=root_binding,
            ),
        )

    def _receipt_matches_repository(self, receipt: CompletionReceipt, lease: RepositoryLease) -> bool:
        binding = lease.binding
        return receipt.repository_key == repository_key_for(binding.device, binding.inode, binding.euid)

    def _validate_active_authority(
        self,
        active: ActiveState,
        root_fd: int,
        target: str,
        *,
        active_store: ActiveStateStore,
    ) -> bool:
        device, inode, euid = self._repository_identity(root_fd)
        expected_identity = {"device": device, "inode": inode, "euid": euid}
        if active.repository_key != repository_key_for(device, inode, euid):
            return False
        if dict(active.repository_identity) != expected_identity:
            return False
        if active.state in {"ready", "terminal-cleanup"}:
            if active.state == "ready":
                raw, witness, record, record_kind = self._observe_record(target, root_fd)
                return (
                    self._terminal_record_matches(
                        root_fd,
                        operation=active.operation,
                        candidate_digest=active.candidate_digest,
                        seed_policy=active.seed_policy,
                        terminal_record_digest=active.terminal_record_digest,
                        expected_witness=active.public_record_witness,
                    )
                    or self._record_matches_expected(active, raw, witness, record, record_kind)
                    or self._post_exchange_terminal_record_matches(active, root_fd, active_store)
                )
            return self._terminal_record_matches(
                root_fd,
                operation=active.operation,
                candidate_digest=active.candidate_digest,
                seed_policy=active.seed_policy,
                terminal_record_digest=active.terminal_record_digest,
                expected_witness=active.public_record_witness,
            )

        raw, witness, record, record_kind = self._observe_record(target, root_fd)
        expected_record = self._record_matches_expected(active, raw, witness, record, record_kind)
        original_record = self._record_matches_original(active, raw, witness, record_kind)
        if active.state == "prepared":
            if not (expected_record or original_record):
                return False
            if not self._bootstrap_matches(active, root_fd):
                return False
            targets = self._observe_domains_for_admission(
                root_fd,
                operation=active.operation,
                seed_policy=active.seed_policy,
            )
            return all(
                self._target_matches_active_original(root_fd, active, index, target)
                for index, target in enumerate(targets)
            )

        if active.state != "running" or not expected_record or not self._bootstrap_matches(active, root_fd):
            return False
        targets = self._observe_domains_for_admission(
            root_fd,
            operation=active.operation,
            seed_policy=active.seed_policy,
        )
        return all(
            self._target_matches_active_original(root_fd, active, index, target)
            or self._target_matches_terminal(
                root_fd,
                target,
                active.owned_target_witnesses[index],
                active.candidate_digest,
            )
            for index, target in enumerate(targets)
        )

    def _bootstrap_matches(self, active: ActiveState, root_fd: int) -> bool:
        container = self._observe_container(root_fd)
        disposition = active.bootstrap_container["disposition"]
        if disposition == "planned-create":
            return container.kind == "absent"
        if disposition in {"existing", "created"}:
            return container.kind == "directory" and self._directory_binding_matches(
                active.bootstrap_container["witness"], container.witness
            )
        return False

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
        actions: Sequence[LifecycleAction] = (),
    ) -> LifecycleResult:
        """Map an I/O admission failure to the one closed preparation row."""

        retry = ProviderLifecycleEngine._retry_for(request, operation, seed_policy)
        failed_paths, pending_paths = _action_path_sets(actions)
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
            failed_paths=failed_paths,
            pending_paths=pending_paths,
            actions=actions,
        )

    def _preparation_partial_actions(
        self,
        active: ActiveState,
        root_fd: int,
    ) -> tuple[LifecycleAction, ...]:
        """Describe the bounded Consumer state left by an initial-record failure."""

        disposition = active.bootstrap_container.get("disposition")
        container_action = (
            _make_action("spec-dock", "container", "completed", "fresh-container-create")
            if disposition == "created"
            else _make_action("spec-dock", "container", "preserved", "shared-container-preserve")
        )
        actions: list[LifecycleAction] = [
            container_action,
            _make_action("spec-dock/spec-dock.version", "record", "failed", "incomplete-record-publish"),
        ]
        for index, (category, path, _source) in enumerate(FIXED_DOMAINS):
            original = active.owned_target_witnesses[index]
            if active.operation == "uninstall":
                if original.get("original_kind") == "directory":
                    actions.append(_make_action(path, category, "pending", f"owned-{category}-remove"))
                else:
                    actions.append(_make_action(path, category, "preserved", f"owned-{category}-absent"))
                continue
            suffix = "replace" if original.get("original_kind") == "directory" else "create"
            actions.append(_make_action(path, category, "pending", f"candidate-{category}-{suffix}"))

        if active.seed_policy == "preserve-only":
            actions.extend(_make_action(path, "seed", "preserved", "preserve-only-seed") for path in SEED_PATHS)
        else:
            first_seed = active.seed_admission["spec-dock/.gitignore"]
            actions.append(
                _make_action(
                    "spec-dock/.gitignore",
                    "seed",
                    "pending" if first_seed == "absent" else "preserved",
                    "fresh-seed-create" if first_seed == "absent" else "consumer-seed-present",
                )
            )
            for parent in (".github", ".github/workflows"):
                if self._observe_target(root_fd, parent, expect_tree=False).kind == "absent":
                    actions.append(_make_action(parent, "container", "pending", "fresh-container-create"))
            second_seed = active.seed_admission[".github/workflows/ci.yml"]
            actions.append(
                _make_action(
                    ".github/workflows/ci.yml",
                    "seed",
                    "pending" if second_seed == "absent" else "preserved",
                    "fresh-seed-create" if second_seed == "absent" else "consumer-seed-present",
                )
            )
        actions.append(_make_action("@provider-stage", "stage", "pending", "candidate-stage-cleanup"))
        return tuple(actions)

    def _bootstrap_cleanup_actions(self, active: ActiveState, root_fd: int) -> tuple[LifecycleAction, ...]:
        """Describe the install work that remains after bootstrap cleanup failed."""

        actions = list(self._preparation_partial_actions(active, root_fd))
        actions[0] = _make_action("spec-dock", "container", "failed", "fresh-container-create")
        actions[1] = _make_action("spec-dock/spec-dock.version", "record", "pending", "incomplete-record-publish")
        return tuple(actions)

    def _preparation_mutation_started(self, active: ActiveState, root_fd: int) -> bool | None:
        if active.bootstrap_container.get("disposition") == "created":
            return True
        try:
            raw, _witness, record, record_kind = self._observe_record("", root_fd)
        except (FilesystemSafetyError, OSError, ValueError, WireValidationError):
            return None
        expected = base64.b64decode(active.expected_incomplete_record["bytes_base64"])
        return (
            raw == expected
            and record_kind == "final"
            and record is not None
            and record.state == "incomplete"
            and record.operation == active.operation
            and record.candidate_digest == active.candidate_digest
            and record.seed_policy == active.seed_policy
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
        receipt_witness: InodeWitness | None,
    ) -> LifecycleResult:
        if operation == "uninstall":
            return self._dispatch_uninstall(
                request,
                seed_policy,
                active_store,
                receipt_store,
                stage_store,
                root_fd,
                receipt=receipt,
                receipt_witness=receipt_witness,
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
        requested_force = force is True
        durable_operation = operation
        if record_kind == "legacy-0.2.3":
            if operation == "install" and not requested_force:
                fixture_digest = cast("str", load_legacy_fixture()["aggregate_digest"])
                raise _AdmissionFailure(
                    "already-initialized",
                    operation="install",
                    candidate_digest=fixture_digest,
                    seed_policy="preserve-only",
                )
            durable_operation = "install"
            seed_policy = "preserve-only"
            result_family = "legacy-migration"
        elif record is None:
            durable_operation = "install"
            seed_policy = "create-if-absent" if operation == "install" else "preserve-only"
            result_family = "install"
        elif record.state == "incomplete":
            raise _AdmissionFailure(
                "installation-record-state-inconsistent",
                candidate_digest=record.candidate_digest,
                seed_policy=record.seed_policy,
            )
        elif record.state == "tooling-absent-preserved-data":
            durable_operation = "install"
            seed_policy = "preserve-only"
            result_family = "install"
        elif operation == "install" and not requested_force:
            raise _AdmissionFailure(
                "already-initialized",
                operation="install",
                candidate_digest=record.candidate_digest,
                seed_policy=record.seed_policy,
            )
        else:
            durable_operation = "update"
            seed_policy = "preserve-only"
            result_family = "update"
        seed_admission = self._admit_existing_seeds(
            root_fd,
            operation=durable_operation,
            seed_policy=seed_policy,
        )
        targets = self._observe_domains_for_admission(
            root_fd,
            operation=durable_operation,
            seed_policy=seed_policy,
        )
        if any(item.kind not in {"absent", "directory"} for item in targets):
            raise _AdmissionFailure(
                "unsafe-target-type",
                operation=durable_operation,
                candidate_digest=None,
                seed_policy=seed_policy,
            )
        if (
            record is not None
            and record.state == "tooling-absent-preserved-data"
            and any(item.kind == "directory" for item in targets)
        ):
            raise _AdmissionFailure(
                "installation-record-state-inconsistent",
                candidate_digest=record.candidate_digest,
                seed_policy=record.seed_policy,
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
            durable_operation,
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
            receipt_witness=receipt_witness,
            seed_admission=seed_admission,
            target_observations=targets,
            legacy=record_kind == "legacy-0.2.3",
        )

    def _admit_existing_seeds(
        self,
        root_fd: int,
        *,
        operation: str,
        seed_policy: str,
    ) -> dict[str, SeedAdmissionState]:
        """Reject fixed seed collisions before any lifecycle state is mutated."""

        admission: dict[str, SeedAdmissionState] = {}
        for path in SEED_PATHS:
            try:
                item = self._observe_target(root_fd, path, expect_tree=False)
            except OSError as failure:
                if failure.errno not in {errno.ELOOP, errno.ENOTDIR}:
                    raise
                raise _AdmissionFailure(
                    "unsafe-parent-binding",
                    operation=operation,
                    candidate_digest=None,
                    seed_policy=seed_policy,
                ) from failure
            if item.kind not in {"absent", "regular"}:
                raise _AdmissionFailure(
                    "unsafe-target-type",
                    operation=operation,
                    candidate_digest=None,
                    seed_policy=seed_policy,
                )
            admission[path] = "absent" if item.kind == "absent" else "present"
        return admission

    def _dispatch_uninstall(
        self,
        request: LifecycleRequest,
        seed_policy: str,
        active_store: ActiveStateStore | None,
        receipt_store: CompletionReceiptStore | None,
        stage_store: StageStore | None,
        root_fd: int,
        *,
        receipt: CompletionReceipt | None,
        receipt_witness: InodeWitness | None,
    ) -> LifecycleResult:
        raw_record, record_witness, record, record_kind = self._observe_record(request.target, root_fd)
        targets = self._observe_domains_for_admission(
            root_fd,
            operation="uninstall",
            seed_policy=seed_policy,
        )
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
            return self._uninstall_not_installed_result(request)
        if record_kind == "legacy-0.2.3":
            fixture = load_legacy_fixture()
            candidate_digest = cast("str", fixture["aggregate_digest"])
        else:
            assert record is not None
            if record.state == "tooling-absent-preserved-data":
                if container.kind != "directory" or any(item.kind == "directory" for item in targets):
                    raise _AdmissionFailure(
                        "installation-record-state-inconsistent",
                        operation="uninstall",
                        candidate_digest=record.candidate_digest,
                        seed_policy=record.seed_policy,
                    )
                self._admit_existing_seeds(
                    root_fd,
                    operation="uninstall",
                    seed_policy="preserve-only",
                )
                return self._uninstall_already_absent_result(request, record)
            if record.state == "incomplete" and record.operation != "uninstall":
                raise _AdmissionFailure(
                    "resume-operation-mismatch",
                    operation=record.operation,
                    candidate_digest=record.candidate_digest,
                    seed_policy=record.seed_policy,
                )
            if record.state == "incomplete" and (active_store is None or active_store.load() is None):
                raise _AdmissionFailure(
                    "installation-record-state-inconsistent",
                    candidate_digest=record.candidate_digest,
                    seed_policy=record.seed_policy,
                )
            candidate_digest = record.candidate_digest
            seed_policy = record.seed_policy
            self._admit_existing_slots(root_fd, targets, candidate_digest)
        seed_admission = self._admit_existing_seeds(
            root_fd,
            operation="uninstall",
            seed_policy="preserve-only",
        )
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
            receipt=receipt,
            receipt_witness=receipt_witness,
            seed_admission=seed_admission,
            target_observations=targets,
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
        seed_admission: Mapping[str, SeedAdmissionState],
        target_observations: Sequence[_ObservedTarget],
        receipt: CompletionReceipt | None = None,
        receipt_witness: InodeWitness | None = None,
        legacy: bool = False,
    ) -> LifecycleResult:
        if request.mode == "dry-run":
            assert candidate is not None
            return self._install_plan_result(
                request,
                operation,
                seed_policy,
                candidate,
                root_fd,
                target_observations,
                record,
            )
        assert active_store is not None and receipt_store is not None and stage_store is not None
        if candidate is None and operation != "uninstall":
            raise _AdmissionFailure("candidate-invalid", operation=operation, seed_policy=seed_policy)
        try:
            if receipt is not None:
                if receipt_witness is None:
                    raise PrivateStateForeignError("completion receipt witness is missing")
                self._invalidate_receipt(receipt_store, receipt, receipt_witness)
            active, active_witness = self._prepare_active(
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
                seed_admission=seed_admission,
                target_observations=target_observations,
            )
            return self._run_active(
                request,
                active,
                candidate,
                active_store,
                receipt_store,
                stage_store,
                root_fd,
                active_witness=active_witness,
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
        except PrivateStateForeignError:
            foreign_digest = (
                candidate.aggregate_digest
                if candidate is not None
                else record.candidate_digest
                if record is not None
                else None
            )
            return self._blocked(
                request,
                "stage-owner-mismatch",
                operation=operation,
                candidate_digest=foreign_digest,
                seed_policy=seed_policy,
                phase="candidate-staging",
                last_completed_phase="preflight",
            )
        except (_LifecycleFailure, FilesystemSafetyError, PrivateStateError, OSError) as failure:
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

    def _invalidate_receipt(
        self,
        store: CompletionReceiptStore,
        receipt: CompletionReceipt,
        expected_witness: InodeWitness,
    ) -> None:
        current, witness = store.load_with_witness()
        if current is None or witness is None or current != receipt or witness != expected_witness:
            raise PrivateStateForeignError("completion receipt changed before invalidation")
        namespace_fd = store._open_namespace()
        try:
            self._filesystem().unlink_bound(namespace_fd, store.filename, expected_witness)
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
        seed_admission: Mapping[str, SeedAdmissionState],
        target_observations: Sequence[_ObservedTarget],
    ) -> tuple[ActiveState, InodeWitness]:
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
        original_digests = tuple(
            item.tree.tree_digest if item.tree is not None else None for item in target_observations
        )
        candidate_digests = tuple(
            domain.tree_digest if candidate is not None else None for domain in (candidate.domains if candidate else ())
        )
        if candidate is None:
            candidate_digests = (None,) * 6
        owned_targets: list[dict[str, object]] = []
        for index, item in enumerate(target_observations):
            if item.kind not in {"absent", "directory"}:
                raise FilesystemSafetyError(f"unsafe fixed target type at {item.path}")
            owned_targets.append({
                "path": item.path,
                "original_kind": item.kind,
                "original_tree_digest": item.tree.tree_digest if item.tree is not None else None,
                "original_inode": _witness_mapping(item.witness) if item.witness is not None else None,
                "terminal_kind": "absent" if operation == "uninstall" else "directory",
                "terminal_tree_digest": (None if operation == "uninstall" else candidate_digests[index]),
            })
        owned = tuple(owned_targets)
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
            3,
            "prepared",
            binding_key,
            {"device": binding.device, "inode": binding.inode, "euid": binding.euid},
            tuple_key,
            generation,
            cast("Operation", operation),
            candidate_digest,
            cast("SeedPolicy", seed_policy),
            seed_admission,
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
            record_witness,
            hashlib.sha256(terminal_bytes).hexdigest(),
            token,
            _cleanup_invocation(request, operation, seed_policy, token),
            None,
        )
        active_witness = self._execute_phase(
            "candidate-staging", lambda: self._save_active(active_store, active, expected_absent=True)
        )
        self._execute_phase("candidate-staging", lambda: self._prepare_stage(stage_store, active, candidate, root_fd))
        return active, active_witness

    @staticmethod
    def _repository_identity(root_fd: int) -> tuple[int, int, int]:
        value = os.fstat(root_fd)
        if not stat.S_ISDIR(value.st_mode):
            raise FilesystemSafetyError("repository root descriptor is not a directory")
        return value.st_dev, value.st_ino, os.geteuid() if hasattr(os, "geteuid") else os.getuid()

    def _save_active(
        self,
        store: ActiveStateStore,
        active: ActiveState,
        *,
        expected: InodeWitness | None = None,
        expected_absent: bool = False,
    ) -> InodeWitness:
        return store.save(
            active,
            expected=expected,
            expected_absent=expected_absent,
            fault=self._check_fault,
        )

    def _prepare_stage(
        self,
        stage_store: StageStore,
        active: ActiveState,
        candidate: CandidateIdentity | None,
        root_fd: int,
    ) -> None:
        if active.state != "prepared":
            return
        owner = self._stage_owner(active)
        stage_state, _entries = stage_store.inspect(owner)
        if stage_state == "complete" and self._stage_payload_valid(stage_store, candidate, root_fd):
            stage_store.ensure_durable(owner)
            return
        stage_store.ensure_registered_entries(fault=self._check_fault)
        stage_store.save_owner(owner, fault=self._check_fault)
        stage_fd = stage_store._stage_fd()
        try:
            if candidate is None:
                return
            assets = self._assets()
            for index, ((_, _, source_suffix), stage_name) in enumerate(
                zip(FIXED_DOMAINS, STAGE_ENTRY_NAMES, strict=True)
            ):
                self._check_fault(f"stage-entry-{stage_name}-remove")
                self._remove_stage_entry(stage_fd, stage_name)
                self._check_fault(f"stage-entry-{stage_name}-create")
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
                    self._check_fault(f"stage-entry-{stage_name}-write")
                    _copy_tree(
                        assets / source_suffix,
                        entry_fd,
                        slot=slot,
                        candidate=candidate,
                        fault=self._check_fault,
                        fault_prefix=f"stage-entry-{stage_name}",
                    )
                finally:
                    os.close(entry_fd)
            self._check_fault("stage-parent-fsync")
            os.fsync(stage_fd)
        finally:
            os.close(stage_fd)
        if candidate is not None and not self._stage_payload_valid(stage_store, candidate, root_fd):
            raise FilesystemSafetyError("staged candidate does not match frozen candidate")

    @staticmethod
    def _stage_owner(active: ActiveState) -> StageOwner:
        return StageOwner(
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

    def _stage_payload_valid(
        self,
        stage_store: StageStore,
        candidate: CandidateIdentity | None,
        _root_fd: int,
    ) -> bool:
        stage_fd = stage_store._stage_fd()
        try:
            for index, stage_name in enumerate(STAGE_ENTRY_NAMES):
                _witness, current = self._capture_engine_domain(
                    stage_fd,
                    stage_name,
                    exclude_marker=index >= 4,
                )
                if candidate is None:
                    if current.entry_count != 0:
                        return False
                    if index >= 4 and not self._stage_slot_marker_absent(stage_fd, stage_name):
                        return False
                    continue
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

    @staticmethod
    def _stage_slot_marker_absent(stage_fd: int, stage_name: str) -> bool:
        entry_fd = os.open(
            stage_name,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
            dir_fd=stage_fd,
        )
        try:
            try:
                os.stat(SLOT_MARKER_NAME, dir_fd=entry_fd, follow_symlinks=False)
            except FileNotFoundError:
                return True
            return False
        finally:
            os.close(entry_fd)

    @staticmethod
    def _witness_matches(stored: object, current: InodeWitness | None) -> bool:
        return current is not None and stored == _witness_mapping(current)

    @staticmethod
    def _directory_binding_matches(stored: object, current: InodeWitness | None) -> bool:
        return (
            current is not None
            and isinstance(stored, dict)
            and stored.get("kind") == "directory"
            and stored.get("device") == current.device
            and stored.get("inode") == current.inode
            and stored.get("mode") == current.mode
        )

    def _require_bootstrap_binding(self, active: ActiveState, root_fd: int) -> None:
        container = self._observe_container(root_fd)
        if (
            active.bootstrap_container.get("disposition") not in {"existing", "created"}
            or container.kind != "directory"
            or not self._directory_binding_matches(active.bootstrap_container.get("witness"), container.witness)
        ):
            raise PrivateStateForeignError("bootstrap container binding changed before consumer mutation")

    def _target_matches_original(self, item: _ObservedTarget, stored: Mapping[str, object]) -> bool:
        original_kind = stored["original_kind"]
        if original_kind == "absent":
            return item.kind == "absent"
        if original_kind != "directory":
            return False
        return (
            item.kind == "directory"
            and item.tree is not None
            and item.tree.tree_digest == stored["original_tree_digest"]
            and self._witness_matches(stored["original_inode"], item.witness)
        )

    def _target_matches_active_original(
        self,
        root_fd: int,
        active: ActiveState,
        index: int,
        item: _ObservedTarget,
    ) -> bool:
        stored = active.owned_target_witnesses[index]
        if not self._target_matches_original(item, stored):
            return False
        if (
            stored["original_kind"] != "directory"
            or index < 4
            or active.original_record["kind"] == "legacy-0.2.3"
            or active.result_family == "legacy-migration"
        ):
            return True
        return self._slot_marker_matches(
            root_fd,
            item,
            None,
            expected_digest=self._original_slot_marker_digest(active),
        )

    @staticmethod
    def _original_slot_marker_digest(active: ActiveState) -> str:
        original_kind = active.original_record["kind"]
        if original_kind == "absent":
            return active.candidate_digest
        if original_kind == "legacy-0.2.3":
            return cast("str", load_legacy_fixture()["aggregate_digest"])
        if original_kind != "final":
            raise ValueError("ACTIVE original record kind cannot determine slot marker authority")
        encoded = active.original_record["bytes_base64"]
        if not isinstance(encoded, str):
            raise ValueError("ACTIVE original record bytes are missing")
        return parse_installation_record(base64.b64decode(encoded)).candidate_digest

    def _require_active_target_bindings(
        self,
        root_fd: int,
        active: ActiveState,
        targets: Sequence[_ObservedTarget],
    ) -> None:
        if len(targets) != len(active.owned_target_witnesses):
            raise FilesystemSafetyError("ACTIVE target binding count changed")
        for index, item in enumerate(targets):
            stored = active.owned_target_witnesses[index]
            if not (
                self._target_matches_active_original(root_fd, active, index, item)
                or self._target_matches_terminal(root_fd, item, stored, active.candidate_digest)
            ):
                raise FilesystemSafetyError(f"fixed target binding changed before publication at {item.path}")

    def _target_matches_terminal(
        self,
        root_fd: int,
        item: _ObservedTarget,
        stored: Mapping[str, object],
        candidate_digest: str,
    ) -> bool:
        terminal_kind = stored["terminal_kind"]
        if terminal_kind == "absent":
            return item.kind == "absent"
        if terminal_kind != "directory":
            return False
        if item.kind != "directory" or item.tree is None:
            return False
        if item.tree.tree_digest != stored["terminal_tree_digest"]:
            return False
        if item.path in {FIXED_DOMAINS[4][1], FIXED_DOMAINS[5][1]}:
            return self._slot_marker_matches(root_fd, item, None, expected_digest=candidate_digest)
        return True

    def _record_matches_original(
        self,
        active: ActiveState,
        raw: bytes | None,
        witness: InodeWitness | None,
        record_kind: str,
    ) -> bool:
        original = active.original_record
        kind = original["kind"]
        if kind == "absent":
            return raw is None and witness is None and record_kind == "absent"
        if raw is None or witness is None or record_kind != kind:
            return False
        encoded = original["bytes_base64"]
        digest = original["sha256"]
        if not isinstance(encoded, str) or not isinstance(digest, str):
            return False
        return (
            raw == base64.b64decode(encoded)
            and hashlib.sha256(raw).hexdigest() == digest
            and self._witness_matches(original["witness"], witness)
        )

    @staticmethod
    def _record_matches_expected(
        active: ActiveState,
        raw: bytes | None,
        witness: InodeWitness | None,
        record: InstallationRecord | None,
        record_kind: str,
    ) -> bool:
        expected = base64.b64decode(active.expected_incomplete_record["bytes_base64"])
        if (
            raw != expected
            or record is None
            or record_kind != "final"
            or record.state != "incomplete"
            or record.operation != active.operation
            or record.candidate_digest != active.candidate_digest
            or record.seed_policy != active.seed_policy
        ):
            return False
        if (
            witness is not None
            and active.public_record_witness is not None
            and NativeAtomicFilesystem._same_content_identity(witness, active.public_record_witness)
        ):
            return True
        return (
            witness is not None
            and active.record_temp_witness is not None
            and NativeAtomicFilesystem._same_content_identity(witness, active.record_temp_witness)
        )

    def _expected_incomplete_record_predecessor(
        self,
        active: ActiveState,
        root_fd: int,
    ) -> tuple[bytes, InodeWitness]:
        raw, witness, record, record_kind = self._observe_record("", root_fd)
        if not self._record_matches_expected(active, raw, witness, record, record_kind):
            raise PrivateStateForeignError("expected incomplete record changed before terminal publication")
        if raw is None or witness is None:
            raise PrivateStateForeignError("expected incomplete record is absent before terminal publication")
        return raw, witness

    def _recover_public_record_state(
        self,
        active: ActiveState,
        current_witness: InodeWitness | None,
        active_store: ActiveStateStore,
        active_witness: InodeWitness,
        *,
        root_fd: int,
        residue_kind: Literal["original", "incomplete"] = "original",
    ) -> tuple[ActiveState, InodeWitness]:
        if current_witness is None:
            raise PrivateStateForeignError("expected public record witness is missing")
        public_witness_matches = (
            active.public_record_witness is not None
            and NativeAtomicFilesystem._same_content_identity(current_witness, active.public_record_witness)
        )

        namespace_fd = active_store._open_namespace()
        try:
            try:
                residue_raw, residue_witness = _read_regular(namespace_fd, RECORD_TEMP_NAME)
            except FileNotFoundError:
                if public_witness_matches:
                    return active, active_witness
                residue_raw, residue_witness = None, None
            if not public_witness_matches and (
                active.record_temp_witness is None
                or not NativeAtomicFilesystem._same_content_identity(current_witness, active.record_temp_witness)
            ):
                raise PrivateStateForeignError("public record publication source is foreign")
            if residue_witness is not None:
                if residue_kind == "original":
                    original_payload = active.original_record.get("bytes_base64")
                    original_witness = active.original_record.get("witness")
                    residue_matches = (
                        isinstance(original_payload, str)
                        and residue_raw == base64.b64decode(original_payload)
                        and self._content_identity_matches_mapping(original_witness, residue_witness)
                    )
                else:
                    expected_payload = base64.b64decode(active.expected_incomplete_record["bytes_base64"])
                    residue_matches = (
                        residue_raw == expected_payload
                        and active.public_record_witness is not None
                        and NativeAtomicFilesystem._same_content_identity(residue_witness, active.public_record_witness)
                    )
                if not residue_matches:
                    raise PrivateStateForeignError("public record exchange residue is foreign during recovery")
                recovered = replace(
                    active,
                    record_temp_witness=residue_witness,
                    public_record_witness=current_witness,
                )
                active_witness = self._save_active(active_store, recovered, expected=active_witness)
                self._check_fault("record-exchange-residue-unlink")
                if residue_kind == "incomplete":
                    public_matches = self._terminal_record_matches(
                        root_fd,
                        operation=recovered.operation,
                        candidate_digest=recovered.candidate_digest,
                        seed_policy=recovered.seed_policy,
                        terminal_record_digest=recovered.terminal_record_digest,
                        expected_witness=recovered.public_record_witness,
                    )
                else:
                    public_raw, public_witness, public_record, public_kind = self._observe_record("", root_fd)
                    expected_payload = base64.b64decode(recovered.expected_incomplete_record["bytes_base64"])
                    public_matches = (
                        public_raw == expected_payload
                        and public_witness is not None
                        and recovered.public_record_witness is not None
                        and NativeAtomicFilesystem._same_content_identity(
                            public_witness, recovered.public_record_witness
                        )
                        and public_record is not None
                        and public_kind == "final"
                        and public_record.state == "incomplete"
                        and public_record.operation == recovered.operation
                        and public_record.candidate_digest == recovered.candidate_digest
                        and public_record.seed_policy == recovered.seed_policy
                    )
                if not public_matches:
                    raise PrivateStateForeignError("public record changed before exchange residue cleanup")
                self._filesystem().unlink_bound(namespace_fd, RECORD_TEMP_NAME, residue_witness)
                self._filesystem().fsync_directory(namespace_fd)
            elif residue_kind == "incomplete":
                raise PrivateStateForeignError("expected incomplete record residue is missing during recovery")
        finally:
            os.close(namespace_fd)
        recovered = replace(active, record_temp_witness=None, public_record_witness=current_witness)
        active_witness = self._save_active(active_store, recovered, expected=active_witness)
        return recovered, active_witness

    def _post_exchange_terminal_record_matches(
        self,
        active: ActiveState,
        root_fd: int,
        active_store: ActiveStateStore,
    ) -> bool:
        if active.record_temp_witness is None or active.public_record_witness is None:
            return False
        try:
            specdock_fd = _open_path(root_fd, ("spec-dock",))
            try:
                self._filesystem().fsync_directory(specdock_fd)
            finally:
                os.close(specdock_fd)
            raw, witness, record, record_kind = self._observe_record("", root_fd)
        except (FilesystemSafetyError, OSError, ValueError, WireValidationError):
            return False
        expected_state = "tooling-absent-preserved-data" if active.operation == "uninstall" else "ready"
        if (
            raw is None
            or witness is None
            or record is None
            or record_kind != "final"
            or not NativeAtomicFilesystem._same_content_identity(witness, active.record_temp_witness)
            or record.state != expected_state
            or record.operation is not None
            or record.candidate_digest != active.candidate_digest
            or record.seed_policy != active.seed_policy
            or hashlib.sha256(raw).hexdigest() != active.terminal_record_digest
        ):
            return False
        try:
            namespace_fd = active_store._open_namespace()
            try:
                residue_raw, residue_witness = _read_regular(namespace_fd, RECORD_TEMP_NAME)
            finally:
                os.close(namespace_fd)
        except (FilesystemSafetyError, PrivateStateError, OSError, ValueError):
            return False
        expected = base64.b64decode(active.expected_incomplete_record["bytes_base64"])
        return residue_raw == expected and NativeAtomicFilesystem._same_content_identity(
            residue_witness, active.public_record_witness
        )

    @staticmethod
    def _content_identity_matches_mapping(stored: object, current: InodeWitness) -> bool:
        return (
            isinstance(stored, dict)
            and stored.get("kind") == current.kind
            and stored.get("device") == current.device
            and stored.get("inode") == current.inode
            and stored.get("mode") == current.mode
            and stored.get("link_count") == current.link_count
            and stored.get("size") == current.size
            and stored.get("sha256") == current.sha256
        )

    def _cleanup_record_exchange_residue(
        self,
        active: ActiveState,
        active_store: ActiveStateStore,
        active_witness: InodeWitness,
        *,
        root_fd: int,
    ) -> tuple[ActiveState, InodeWitness]:
        expected_residue = active.record_temp_witness
        if expected_residue is None:
            return active, active_witness

        namespace_fd = active_store._open_namespace()
        try:
            try:
                residue_raw, residue_witness = _read_regular(namespace_fd, RECORD_TEMP_NAME)
            except FileNotFoundError:
                residue_raw, residue_witness = None, None
            if residue_witness is not None:
                expected_payload = base64.b64decode(active.expected_incomplete_record["bytes_base64"])
                if (
                    not NativeAtomicFilesystem._same_content_identity(residue_witness, expected_residue)
                    or residue_raw != expected_payload
                ):
                    raise PrivateStateForeignError("public record exchange residue is foreign during cleanup")
                self._check_fault("record-exchange-residue-unlink")
                if not self._terminal_record_matches(
                    root_fd,
                    operation=active.operation,
                    candidate_digest=active.candidate_digest,
                    seed_policy=active.seed_policy,
                    terminal_record_digest=active.terminal_record_digest,
                    expected_witness=active.public_record_witness,
                ):
                    raise PrivateStateForeignError("public record changed before exchange residue cleanup")
                self._filesystem().unlink_bound(namespace_fd, RECORD_TEMP_NAME, residue_witness)
                self._filesystem().fsync_directory(namespace_fd)
        finally:
            os.close(namespace_fd)

        cleaned = replace(active, record_temp_witness=None)
        active_witness = self._save_active(active_store, cleaned, expected=active_witness)
        return cleaned, active_witness

    def _validate_running_stage(
        self,
        stage_store: StageStore,
        active: ActiveState,
        candidate: CandidateIdentity | None,
        root_fd: int,
    ) -> bool:
        owner = self._stage_owner(active)
        status, present = stage_store.inspect(owner)
        if status == "complete":
            stage_store.ensure_durable(owner)
        if status == "absent" or stage_store.load_owner() is None:
            return False
        targets = self._observe_domains_for_admission(
            root_fd,
            operation=active.operation,
            seed_policy=active.seed_policy,
        )
        stage_fd = stage_store._stage_fd()
        present_names = set(present)
        try:
            for index, stage_name in enumerate(STAGE_ENTRY_NAMES):
                stored = active.owned_target_witnesses[index]
                target = targets[index]
                is_original = self._target_matches_active_original(root_fd, active, index, target)
                is_terminal = self._target_matches_terminal(root_fd, target, stored, active.candidate_digest)
                expected_digest: str | None = None
                expected_empty = False
                expected_absent = False
                expected_candidate = False
                if active.operation == "uninstall":
                    if is_original:
                        expected_empty = True
                    elif is_terminal and stored["original_kind"] == "directory":
                        expected_digest = cast("str", stored["original_tree_digest"])
                    elif is_terminal and stored["original_kind"] == "absent":
                        expected_empty = True
                    else:
                        return False
                elif is_original:
                    if candidate is None:
                        return False
                    expected = candidate.domains[index]
                    expected_digest = expected.tree_digest
                    expected_candidate = True
                elif is_terminal and stored["original_kind"] == "directory":
                    expected_digest = cast("str", stored["original_tree_digest"])
                elif is_terminal and stored["original_kind"] == "absent":
                    expected_absent = True
                else:
                    return False

                if expected_absent:
                    if stage_name in present_names:
                        return False
                    continue
                if stage_name not in present_names:
                    return False
                _witness, current = self._capture_engine_domain(
                    stage_fd,
                    stage_name,
                    exclude_marker=index >= 4,
                )
                if expected_empty:
                    if current.entry_count != 0:
                        return False
                    if index >= 4 and not self._stage_slot_marker_absent(stage_fd, stage_name):
                        return False
                    continue
                if expected_digest is None or current.tree_digest != expected_digest:
                    return False
                if expected_candidate and index >= 4:
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
                    if marker.slot != FIXED_DOMAINS[index][1] or marker.candidate_digest != active.candidate_digest:
                        return False
            return True
        except (CandidateError, FilesystemSafetyError, OSError, ValueError, WireValidationError):
            return False
        finally:
            os.close(stage_fd)

    def _remove_stage_entry(self, stage_fd: int, name: str) -> None:
        _safe_component(name)
        try:
            _witness, current = self._capture_engine_domain(stage_fd, name)
        except FileNotFoundError:
            return
        self._filesystem().remove_tree_bound(stage_fd, name, current)

    def _observe_container(self, root_fd: int) -> _ObservedTarget:
        return self._observe_target(root_fd, "spec-dock", expect_tree=False)

    def _observe_domains(self, root_fd: int) -> tuple[_ObservedTarget, ...]:
        return tuple(self._observe_target(root_fd, path, expect_tree=True) for _, path, _ in FIXED_DOMAINS)

    def _observe_domains_for_admission(
        self,
        root_fd: int,
        *,
        operation: str,
        seed_policy: str,
    ) -> tuple[_ObservedTarget, ...]:
        try:
            return self._observe_domains(root_fd)
        except OSError as failure:
            if failure.errno not in {errno.ELOOP, errno.ENOTDIR}:
                raise
            raise _AdmissionFailure(
                "unsafe-parent-binding",
                operation=operation,
                candidate_digest=None,
                seed_policy=seed_policy,
            ) from failure

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
            if expect_tree:
                witness, tree = self._capture_engine_domain(
                    parent_fd,
                    name,
                    exclude_marker=path in {FIXED_DOMAINS[4][1], FIXED_DOMAINS[5][1]},
                )
            else:
                container_witness = self._filesystem().capture_inode(parent_fd, name, "directory")
                if container_witness is None:
                    raise FilesystemSafetyError(f"{name!r} disappeared while reading")
                witness = container_witness
                tree = None
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
                    item,
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
                item,
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
        item: _ObservedTarget,
        candidate: CandidateIdentity | None,
        *,
        expected_digest: str,
    ) -> bool:
        if item.kind != "directory" or item.witness is None:
            return False
        path = item.path
        components = _target_components(path)
        slot_fd: int | None = None
        parent_fd: int | None = None
        try:
            slot_fd = _open_path(root_fd, components)
            opened = NativeAtomicFilesystem._witness(os.fstat(slot_fd), "directory", None)
            if not NativeAtomicFilesystem._same_content_identity(opened, item.witness):
                return False
            parent_fd = _open_path(root_fd, components[:-1])
            visible = os.stat(components[-1], dir_fd=parent_fd, follow_symlinks=False)
            visible_witness = NativeAtomicFilesystem._witness(visible, "directory", None)
            if not NativeAtomicFilesystem._same_content_identity(visible_witness, item.witness):
                return False
        except (FileNotFoundError, OSError, FilesystemSafetyError):
            return False
        assert slot_fd is not None and parent_fd is not None
        try:
            try:
                raw, _witness = _read_regular(slot_fd, SLOT_MARKER_NAME, maximum=2048)
                marker = parse_slot_marker(raw)
            except (FileNotFoundError, FilesystemSafetyError, CandidateError, ValueError, WireValidationError):
                return False
            after = NativeAtomicFilesystem._witness(os.fstat(slot_fd), "directory", None)
            if not NativeAtomicFilesystem._same_content_identity(after, item.witness):
                return False
            visible = os.stat(components[-1], dir_fd=parent_fd, follow_symlinks=False)
            visible_witness = NativeAtomicFilesystem._witness(visible, "directory", None)
            if not NativeAtomicFilesystem._same_content_identity(visible_witness, item.witness):
                return False
            return (
                marker.slot == path
                and marker.version == (candidate.version if candidate is not None else CANDIDATE_VERSION)
                and marker.candidate_digest == expected_digest
            )
        finally:
            if slot_fd is not None:
                os.close(slot_fd)
            if parent_fd is not None:
                os.close(parent_fd)

    def _install_plan_result(
        self,
        request: LifecycleRequest,
        operation: str,
        seed_policy: str,
        candidate: CandidateIdentity,
        root_fd: int,
        targets: Sequence[_ObservedTarget],
        _record: InstallationRecord | None,
    ) -> LifecycleResult:
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
        incomplete_uninstall = record is not None and record.state == "incomplete" and record.operation == "uninstall"
        code = (
            "uninstall-planned"
            if incomplete_uninstall or any(item.kind == "directory" for item in targets)
            else "uninstall-already-absent"
        )
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

    def _uninstall_not_installed_result(self, request: LifecycleRequest) -> LifecycleResult:
        return build_public_result(
            request,
            status="blocked",
            code="tooling-not-installed",
            operation="uninstall",
            candidate_digest=None,
            seed_policy="preserve-only",
            phase="preflight",
            last_completed_phase="request-validation",
        )

    def _uninstall_already_absent_result(
        self,
        request: LifecycleRequest,
        record: InstallationRecord,
    ) -> LifecycleResult:
        actions = (
            _make_action("spec-dock", "container", "preserved", "shared-container-preserve"),
            _make_action("spec-dock/spec-dock.version", "record", "preserved", "terminal-record-current"),
            _make_action("spec-dock/.gitignore", "seed", "preserved", "preserve-only-seed"),
            _make_action(".github/workflows/ci.yml", "seed", "preserved", "preserve-only-seed"),
        )
        return build_public_result(
            request,
            status="completed" if request.mode == "apply" else "planned",
            code="uninstall-already-absent",
            operation="uninstall",
            candidate_digest=record.candidate_digest,
            seed_policy="preserve-only",
            phase="complete",
            last_completed_phase="preflight",
            actions=actions,
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
        partial_phase: str | None = None,
        original_targets: Sequence[Mapping[str, object]] | None = None,
        failure_point: str | None = None,
        seed_admission: Mapping[str, SeedAdmissionState] | None = None,
    ) -> tuple[LifecycleAction, ...]:
        container = self._observe_container(root_fd)
        result: list[LifecycleAction] = []
        container_status = "preserved" if container.kind == "directory" else "planned" if planned else "completed"
        container_reason = "shared-container-preserve" if container.kind == "directory" else "fresh-container-create"
        result.append(_make_action("spec-dock", "container", container_status, container_reason))
        if planned:
            record_status = "planned"
            record_reason = "terminal-record-publish"
        elif partial_phase == "publish-terminal-record":
            record_status = "failed"
            record_reason = "terminal-record-publish"
        elif partial_phase is not None:
            record_status = "completed"
            record_reason = "incomplete-record-publish"
        else:
            record_status = "completed"
            record_reason = "terminal-record-publish"
        result.append(_make_action("spec-dock/spec-dock.version", "record", record_status, record_reason))
        for index, item in enumerate(targets):
            kind, path, _ = FIXED_DOMAINS[index]
            current = self._target_matches_candidate(root_fd, item, index, candidate)
            category = kind
            original_kind = item.kind
            original_current = False
            if original_targets is not None:
                with contextlib.suppress(IndexError, KeyError):
                    original = original_targets[index]
                    original_kind = cast("str", original["original_kind"])
                    original_current = (
                        current
                        and original_kind == "directory"
                        and original.get("original_tree_digest") == candidate.domains[index].tree_digest
                    )
            preserved_current = current and original_current
            reason = (
                f"candidate-{category}-current"
                if preserved_current
                else f"candidate-{category}-{'create' if original_kind == 'absent' else 'replace'}"
            )
            if planned:
                status = "preserved" if current else "planned"
            elif partial_index is None:
                status = "preserved" if preserved_current else "completed"
            elif partial_phase == "verify-target":
                status = "preserved" if preserved_current else "completed" if current else "failed"
            elif preserved_current:
                status = "preserved"
            elif index < partial_index:
                status = "completed"
            elif index == partial_index:
                status = "failed"
            else:
                status = "pending"
            result.append(_make_action(path, category, status, reason))
        for seed_index, (path, _seed_name) in enumerate((
            ("spec-dock/.gitignore", "spec-dock-gitignore"),
            (".github/workflows/ci.yml", "consumer-ci"),
        )):
            seed_phase = "create-seed-spec-dock-gitignore" if seed_index == 0 else "create-seed-consumer-ci"
            existing = self._observe_target(root_fd, path, expect_tree=False)
            admission_state = (
                seed_admission[path]
                if seed_admission is not None
                else "absent"
                if existing.kind == "absent"
                else "present"
            )
            failed_seed = (
                seed_policy == "create-if-absent"
                and partial_phase in {"create-seed-spec-dock-gitignore", "create-seed-consumer-ci"}
                and seed_phase == partial_phase
            )
            if failed_seed:
                reason = "fresh-seed-create"
            elif admission_state == "present":
                reason = (
                    "consumer-seed-present"
                    if operation == "install" and seed_policy == "create-if-absent"
                    else "preserve-only-seed"
                )
            else:
                reason = "fresh-seed-create" if seed_policy == "create-if-absent" else "preserve-only-seed"
            if reason != "fresh-seed-create":
                status = "preserved"
            elif planned:
                status = "planned"
            elif partial_phase is None:
                status = "completed"
            elif failed_seed:
                status = "failed"
            else:
                partial_rank = PHASES.index(partial_phase) if partial_phase in PHASES else len(PHASES)
                seed_rank = PHASES.index(seed_phase)
                status = "pending" if partial_rank < seed_rank else "completed"
            result.append(_make_action(path, "seed", status, reason))
        if include_stage:
            stage_status = "pending" if partial_phase is not None or failure_point is not None else "completed"
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
        partial_phase: str | None = None,
        original_targets: Sequence[Mapping[str, object]] | None = None,
        initial_absent_paths: frozenset[str] | None = None,
    ) -> tuple[LifecycleAction, ...]:
        result = [_make_action("spec-dock", "container", "preserved", "shared-container-preserve")]
        if planned:
            record_status = "planned"
            record_reason = "terminal-record-publish"
        elif partial_phase == "publish-terminal-record":
            record_status = "failed"
            record_reason = "terminal-record-publish"
        elif partial_phase is not None:
            record_status = "completed"
            record_reason = "incomplete-record-publish"
        else:
            record_status = "completed"
            record_reason = "terminal-record-publish"
        result.append(_make_action("spec-dock/spec-dock.version", "record", record_status, record_reason))
        initially_absent = initial_absent_paths or frozenset()
        for index, item in enumerate(targets):
            category, path, _ = FIXED_DOMAINS[index]
            original_kind = item.kind
            if original_targets is not None:
                with contextlib.suppress(IndexError, KeyError):
                    original_kind = cast("str", original_targets[index]["original_kind"])
            originally_present = original_kind == "directory"
            was_absent_at_start = path in initially_absent
            reason = (
                f"owned-{category}-remove"
                if originally_present and not was_absent_at_start
                else f"owned-{category}-absent"
            )
            if planned:
                status = "planned" if originally_present else "preserved"
            elif partial_phase == "verify-target":
                if item.kind != "absent":
                    status = "failed"
                else:
                    status = "preserved" if was_absent_at_start or not originally_present else "completed"
            elif was_absent_at_start:
                status = "preserved"
            elif partial_index is None:
                status = "completed" if originally_present else "preserved"
            elif not originally_present:
                status = "preserved"
            elif index < partial_index:
                status = "completed"
            elif index == partial_index:
                status = "failed"
            else:
                status = "pending"
            result.append(_make_action(path, category, status, reason))
        for path in ("spec-dock/.gitignore", ".github/workflows/ci.yml"):
            result.append(_make_action(path, "seed", "preserved", "preserve-only-seed"))
        if include_stage:
            result.append(
                _make_action(
                    "@provider-stage",
                    "stage",
                    "pending" if partial_phase is not None else "completed",
                    "candidate-stage-cleanup",
                )
            )
        return tuple(result)

    @staticmethod
    def _cleanup_completed_result(request: LifecycleRequest, active: ActiveState) -> LifecycleResult:
        return build_public_result(
            request,
            status="completed",
            code="terminal-cleanup-completed",
            operation=active.operation,
            candidate_digest=active.candidate_digest,
            seed_policy=active.seed_policy,
            mutation_started=True,
            phase="complete",
            last_completed_phase="cleanup-stage",
            continuation=_completed_cleanup_continuation(active.deferred_invocation),
            actions=(LifecycleAction("@provider-stage", "stage", "completed", "candidate-stage-cleanup"),),
            guidance=(
                CLEANUP_COMPLETED_DEFERRED_GUIDANCE
                if active.deferred_invocation is not None
                else CLEANUP_COMPLETED_GUIDANCE
            ),
        )

    def _run_active(
        self,
        request: LifecycleRequest,
        active: ActiveState,
        candidate: CandidateIdentity | None,
        active_store: ActiveStateStore,
        receipt_store: CompletionReceiptStore,
        stage_store: StageStore,
        root_fd: int,
        *,
        active_witness: InodeWitness,
    ) -> LifecycleResult:
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
            return self._complete_pending_cleanup(
                request,
                active,
                active_store,
                receipt_store,
                stage_store,
                root_fd,
                active_witness=active_witness,
            )
        initial_absent_paths: frozenset[str] | None = None
        try:
            if active.operation == "uninstall":
                initial_absent_paths = frozenset(
                    item.path
                    for item in self._observe_domains_for_admission(
                        root_fd,
                        operation=active.operation,
                        seed_policy=active.seed_policy,
                    )
                    if item.kind == "absent"
                )
                return self._run_uninstall_active(
                    request,
                    active,
                    active_store,
                    receipt_store,
                    stage_store,
                    root_fd,
                    active_witness=active_witness,
                    initial_absent_paths=initial_absent_paths,
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
                active_witness=active_witness,
            )
        except _InjectedFailure as failure:
            current = active_store.load() or active
            return self._partial_failure_result(
                request, current, failure, root_fd, initial_absent_paths=initial_absent_paths
            )
        except (
            _LifecycleFailure,
            AtomicRenameUnavailable,
            FilesystemSafetyError,
            PrivateStateError,
            OSError,
        ) as failure:
            current = active_store.load() or active
            return self._partial_failure_result(
                request, current, failure, root_fd, initial_absent_paths=initial_absent_paths
            )

    def _run_install_active(
        self,
        request: LifecycleRequest,
        active: ActiveState,
        candidate: CandidateIdentity,
        active_store: ActiveStateStore,
        receipt_store: CompletionReceiptStore,
        stage_store: StageStore,
        root_fd: int,
        *,
        active_witness: InodeWitness,
    ) -> LifecycleResult:
        active, active_witness = self._execute_phase(
            "bootstrap-container",
            lambda: self._ensure_bootstrap(request, active, active_store, root_fd, active_witness),
        )
        raw_record, record_witness, record, record_kind = self._execute_phase(
            "publish-incomplete-record",
            lambda: self._observe_record(request.target, root_fd),
        )
        if not self._record_matches_expected(active, raw_record, record_witness, record, record_kind):
            expected_incomplete = base64.b64decode(active.expected_incomplete_record["bytes_base64"])
            active, active_witness = self._execute_phase(
                "publish-incomplete-record",
                lambda: self._write_public_record(
                    request,
                    active,
                    expected_incomplete,
                    active_store,
                    root_fd,
                    expected_active_witness=active_witness,
                    expected_predecessor=(raw_record, record_witness),
                    predecessor_kind="original",
                ),
            )
        else:
            active, active_witness = self._recover_public_record_state(
                active,
                record_witness,
                active_store,
                active_witness,
                root_fd=root_fd,
            )
        if active.state == "prepared":
            self._execute_phase(
                "publish-incomplete-record", lambda: self._ensure_expected_record_durable(active, root_fd)
            )
        if active.state == "prepared":
            active = replace(active, state="running")
            active_witness = self._execute_phase(
                "publish-incomplete-record",
                lambda: self._save_active(active_store, active, expected=active_witness),
            )
        targets = self._execute_phase("verify-target", lambda: self._observe_domains(root_fd))
        self._execute_phase(
            "verify-target",
            lambda: self._require_active_target_bindings(root_fd, active, targets),
        )
        for index, item in enumerate(targets):
            phase = f"publish-{STAGE_ENTRY_NAMES[index]}"

            def publish_domain(index: int = index, item: _ObservedTarget = item) -> None:
                if self._target_matches_candidate(root_fd, item, index, candidate):
                    self._ensure_domain_durable(root_fd, stage_store, item.path, index=index, candidate=candidate)
                    return
                self._publish_domain(request, active, stage_store, index, candidate, root_fd, detach=False)

            self._execute_phase(phase, publish_domain)
        self._execute_phase(
            "create-seed-spec-dock-gitignore",
            lambda: self._publish_seed(
                request, active, root_fd, "spec-dock/.gitignore", "spec-dock-gitignore", "spec_dock/.gitignore"
            ),
        )
        self._execute_phase(
            "create-seed-consumer-ci",
            lambda: self._publish_seed(
                request,
                active,
                root_fd,
                ".github/workflows/ci.yml",
                "consumer-ci",
                "install_root/.github/workflows/ci.yml",
            ),
        )

        def verify_targets() -> None:
            self._check_fault("target-verify")
            current = self._observe_domains(root_fd)
            if not all(
                self._target_matches_candidate(root_fd, item, index, candidate) for index, item in enumerate(current)
            ):
                raise FilesystemSafetyError("published candidate does not verify")

        self._execute_phase("verify-target", verify_targets)
        active = replace(active, state="ready")
        active_witness = self._execute_phase(
            "publish-terminal-record",
            lambda: self._save_active(active_store, active, expected=active_witness),
        )
        terminal = self._terminal_record_bytes(active)
        terminal_predecessor = self._execute_phase(
            "publish-terminal-record",
            lambda: self._expected_incomplete_record_predecessor(active, root_fd),
        )
        active, active_witness = self._execute_phase(
            "publish-terminal-record",
            lambda: self._write_public_record(
                request,
                active,
                terminal,
                active_store,
                root_fd,
                expected_active_witness=active_witness,
                expected_predecessor=terminal_predecessor,
                predecessor_kind="incomplete",
            ),
        )
        active = replace(active, state="terminal-cleanup")
        active_witness = self._execute_phase(
            "cleanup-stage",
            lambda: self._save_active(active_store, active, expected=active_witness),
        )
        return self._finish_cleanup(
            request,
            active,
            active_store,
            receipt_store,
            stage_store,
            root_fd,
            active_witness=active_witness,
        )

    def _run_uninstall_active(
        self,
        request: LifecycleRequest,
        active: ActiveState,
        active_store: ActiveStateStore,
        receipt_store: CompletionReceiptStore,
        stage_store: StageStore,
        root_fd: int,
        *,
        active_witness: InodeWitness,
        initial_absent_paths: frozenset[str],
    ) -> LifecycleResult:
        container = self._execute_phase("bootstrap-container", lambda: self._observe_container(root_fd))
        if container.kind != "directory":
            raise _LifecycleFailure(
                "bootstrap-container",
                cause=FilesystemSafetyError("tooling container disappeared during uninstall"),
            )
        raw_record, record_witness, record, record_kind = self._execute_phase(
            "publish-incomplete-record",
            lambda: self._observe_record(request.target, root_fd),
        )
        if not self._record_matches_expected(active, raw_record, record_witness, record, record_kind):
            expected_incomplete = base64.b64decode(active.expected_incomplete_record["bytes_base64"])
            active, active_witness = self._execute_phase(
                "publish-incomplete-record",
                lambda: self._write_public_record(
                    request,
                    active,
                    expected_incomplete,
                    active_store,
                    root_fd,
                    expected_active_witness=active_witness,
                    expected_predecessor=(raw_record, record_witness),
                    predecessor_kind="original",
                ),
            )
        else:
            active, active_witness = self._recover_public_record_state(
                active,
                record_witness,
                active_store,
                active_witness,
                root_fd=root_fd,
            )
        if active.state == "prepared":
            self._execute_phase(
                "publish-incomplete-record", lambda: self._ensure_expected_record_durable(active, root_fd)
            )
        if active.state == "prepared":
            active = replace(active, state="running")
            active_witness = self._execute_phase(
                "publish-incomplete-record",
                lambda: self._save_active(active_store, active, expected=active_witness),
            )
        for index, (_kind, _path, _source) in enumerate(FIXED_DOMAINS):
            phase = f"detach-{STAGE_ENTRY_NAMES[index]}"

            def observe_target(index: int = index) -> _ObservedTarget:
                item = self._observe_domains(root_fd)[index]
                if item.kind not in {"absent", "directory"}:
                    raise FilesystemSafetyError(f"unsupported fixed target type at {item.path}")
                stored = active.owned_target_witnesses[index]
                if not (
                    self._target_matches_active_original(root_fd, active, index, item)
                    or self._target_matches_terminal(root_fd, item, stored, active.candidate_digest)
                ):
                    raise FilesystemSafetyError(f"fixed target binding changed before detach at {item.path}")
                return item

            item = self._execute_phase("verify-target", observe_target)
            if item.kind == "directory":

                def detach_domain(index: int = index) -> None:
                    self._publish_domain(request, active, stage_store, index, None, root_fd, detach=True)

                self._execute_phase(
                    phase,
                    detach_domain,
                )

        def verify_targets() -> None:
            self._check_fault("target-verify")
            if any(item.kind != "absent" for item in self._observe_domains(root_fd)):
                raise FilesystemSafetyError("tooling target remained after uninstall")

        self._execute_phase("verify-target", verify_targets)
        active = replace(active, state="ready")
        active_witness = self._execute_phase(
            "publish-terminal-record",
            lambda: self._save_active(active_store, active, expected=active_witness),
        )
        terminal = self._terminal_record_bytes(active)
        terminal_predecessor = self._execute_phase(
            "publish-terminal-record",
            lambda: self._expected_incomplete_record_predecessor(active, root_fd),
        )
        active, active_witness = self._execute_phase(
            "publish-terminal-record",
            lambda: self._write_public_record(
                request,
                active,
                terminal,
                active_store,
                root_fd,
                expected_active_witness=active_witness,
                expected_predecessor=terminal_predecessor,
                predecessor_kind="incomplete",
            ),
        )
        active = replace(active, state="terminal-cleanup")
        active_witness = self._execute_phase(
            "cleanup-stage",
            lambda: self._save_active(active_store, active, expected=active_witness),
        )
        return self._finish_cleanup(
            request,
            active,
            active_store,
            receipt_store,
            stage_store,
            root_fd,
            active_witness=active_witness,
            initial_absent_paths=initial_absent_paths,
        )

    def _ensure_bootstrap(
        self,
        _request: LifecycleRequest,
        active: ActiveState,
        active_store: ActiveStateStore,
        root_fd: int,
        active_witness: InodeWitness,
    ) -> tuple[ActiveState, InodeWitness]:
        container = self._observe_container(root_fd)
        disposition = active.bootstrap_container.get("disposition")
        bootstrap_matches = (
            disposition == "planned-create"
            and active.bootstrap_container.get("witness") is None
            and container.kind == "absent"
        ) or (
            disposition in {"existing", "created"}
            and container.kind == "directory"
            and self._directory_binding_matches(active.bootstrap_container.get("witness"), container.witness)
        )
        if not bootstrap_matches:
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
            try:
                os.mkdir("spec-dock", 0o755, dir_fd=root_fd)
            except FileExistsError as failure:
                raise _AdmissionFailure(
                    "bootstrap-container-conflict",
                    phase="bootstrap-container",
                    last_completed_phase="candidate-staging",
                    operation=active.operation,
                    candidate_digest=active.candidate_digest,
                    seed_policy=active.seed_policy,
                ) from failure
            container_fd = os.open(
                "spec-dock",
                os.O_RDONLY
                | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_CLOEXEC", 0),
                dir_fd=root_fd,
            )
            witness: InodeWitness | None = None
            try:
                witness = self._filesystem().capture_inode(root_fd, "spec-dock", "directory")
                if witness is None:
                    raise FilesystemSafetyError("bootstrap container disappeared")
                self._check_fault("bootstrap-container-fsync")
                self._filesystem().fsync_directory(root_fd)
                witness = self._filesystem().capture_inode(root_fd, "spec-dock", "directory")
            except (AtomicRenameUnavailable, FilesystemSafetyError, PrivateStateError, OSError) as failure:
                raise self._bootstrap_rollback_failure(root_fd, witness, failure) from failure
            finally:
                os.close(container_fd)
            if witness is None:
                raise FilesystemSafetyError("bootstrap container disappeared")
            active = replace(
                active, bootstrap_container={"disposition": "created", "witness": _witness_mapping(witness)}
            )
            try:
                active_witness = self._save_active(active_store, active, expected=active_witness)
            except (AtomicRenameUnavailable, FilesystemSafetyError, PrivateStateError, OSError) as failure:
                raise self._bootstrap_rollback_failure(
                    root_fd,
                    witness,
                    failure,
                    active_store=active_store,
                    original_active=replace(
                        active, bootstrap_container={"disposition": "planned-create", "witness": None}
                    ),
                    created_active=active,
                ) from failure
        return active, active_witness

    def _bootstrap_rollback_failure(
        self,
        root_fd: int,
        expected: InodeWitness | None,
        failure: BaseException,
        *,
        active_store: ActiveStateStore | None = None,
        original_active: ActiveState | None = None,
        created_active: ActiveState | None = None,
    ) -> _LifecycleFailure:
        if active_store is not None and original_active is not None and created_active is not None:
            try:
                self._restore_bootstrap_active(active_store, original_active, created_active, original_active)
            except (AtomicRenameUnavailable, FilesystemSafetyError, PrivateStateError, OSError) as restore_failure:
                try:
                    self._restore_bootstrap_active(active_store, original_active, created_active, created_active)
                except (AtomicRenameUnavailable, FilesystemSafetyError, PrivateStateError, OSError) as keep_failure:
                    return _LifecycleFailure(
                        "bootstrap-container",
                        cause=keep_failure,
                        bootstrap_cleanup_failed=True,
                    )
                return _LifecycleFailure(
                    "bootstrap-container",
                    cause=restore_failure,
                    bootstrap_cleanup_failed=True,
                )
        try:
            current = self._filesystem().capture_inode(root_fd, "spec-dock", "directory")
            if current is not None:
                if expected is None or not NativeAtomicFilesystem._same_content_identity(current, expected):
                    raise FilesystemSafetyError("bootstrap container identity changed during rollback")
                tree = self._filesystem().capture_domain_tree(root_fd, "spec-dock")
                if tree.entry_count != 0:
                    raise FilesystemSafetyError("bootstrap container is no longer empty during rollback")
                self._filesystem().remove_tree_bound(root_fd, "spec-dock", tree)
            self._filesystem().fsync_directory(root_fd)
        except (AtomicRenameUnavailable, FilesystemSafetyError, PrivateStateError, OSError) as cleanup_failure:
            if active_store is not None and original_active is not None and created_active is not None:
                try:
                    current = self._filesystem().capture_inode(root_fd, "spec-dock", "directory")
                    if current is not None:
                        if expected is None or not NativeAtomicFilesystem._same_content_identity(current, expected):
                            raise FilesystemSafetyError("bootstrap container identity changed during recovery")
                        self._restore_bootstrap_active(active_store, original_active, created_active, created_active)
                except (AtomicRenameUnavailable, FilesystemSafetyError, PrivateStateError, OSError):
                    pass
            return _LifecycleFailure(
                "bootstrap-container",
                cause=cleanup_failure,
                bootstrap_cleanup_failed=True,
            )
        return _LifecycleFailure("bootstrap-container", cause=failure, bootstrap_rolled_back=True)

    @staticmethod
    def _restore_bootstrap_active(
        active_store: ActiveStateStore,
        original_active: ActiveState,
        created_active: ActiveState,
        desired: ActiveState,
    ) -> None:
        current, current_witness = active_store.load_with_witness()
        if current is None or current_witness is None or current.state != "prepared":
            raise PrivateStateForeignError("ACTIVE changed during bootstrap rollback")
        if (
            current.repository_key,
            current.tuple_key,
            current.operation_generation,
            current.operation,
            current.candidate_digest,
            current.seed_policy,
            current.result_family,
        ) != (
            original_active.repository_key,
            original_active.tuple_key,
            original_active.operation_generation,
            original_active.operation,
            original_active.candidate_digest,
            original_active.seed_policy,
            original_active.result_family,
        ):
            raise PrivateStateForeignError("ACTIVE changed during bootstrap rollback")
        if current.bootstrap_container not in (original_active.bootstrap_container, created_active.bootstrap_container):
            raise PrivateStateForeignError("ACTIVE changed during bootstrap rollback")
        published = active_store.save(desired, expected=current_witness)
        active_store.ensure_durable(expected=published)

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

    def _require_public_record_predecessor(
        self,
        active: ActiveState,
        raw: bytes | None,
        witness: InodeWitness | None,
        *,
        predecessor_kind: Literal["original", "incomplete"],
    ) -> None:
        if active.public_record_witness is None:
            if witness is not None:
                raise PrivateStateForeignError("public record predecessor witness changed")
        elif witness is None or not NativeAtomicFilesystem._same_content_identity(
            witness, active.public_record_witness
        ):
            raise PrivateStateForeignError("public record predecessor witness changed")
        if predecessor_kind == "original":
            original_payload = active.original_record.get("bytes_base64")
            matches = (
                raw is None
                if active.original_record.get("kind") == "absent"
                else isinstance(original_payload, str) and raw == base64.b64decode(original_payload)
            )
        else:
            expected = base64.b64decode(active.expected_incomplete_record["bytes_base64"])
            matches = raw == expected
        if not matches:
            raise PrivateStateForeignError("public record predecessor bytes changed")
        if predecessor_kind == "original" and raw is not None:
            if witness is None or not self._witness_matches(active.original_record.get("witness"), witness):
                raise PrivateStateForeignError("original public record predecessor is foreign")
        elif predecessor_kind == "incomplete" and witness is None:
            raise PrivateStateForeignError("incomplete public record predecessor is absent")

    def _write_public_record(
        self,
        _request: LifecycleRequest,
        active: ActiveState,
        payload: bytes,
        active_store: ActiveStateStore,
        root_fd: int,
        *,
        expected_active_witness: InodeWitness,
        expected_predecessor: tuple[bytes | None, InodeWitness | None],
        predecessor_kind: Literal["original", "incomplete"],
    ) -> tuple[ActiveState, InodeWitness]:
        predecessor_raw, predecessor_witness = expected_predecessor
        self._require_public_record_predecessor(
            active,
            predecessor_raw,
            predecessor_witness,
            predecessor_kind=predecessor_kind,
        )
        witness = active_store.write_record_temp(payload, fault=self._check_fault)
        try:
            active_witness = self._save_active(
                active_store,
                replace(active, record_temp_witness=witness),
                expected=expected_active_witness,
            )
        except (AtomicRenameUnavailable, FilesystemSafetyError, PrivateStateError, OSError) as failure:
            namespace_fd = active_store._open_namespace()
            try:
                current = self._filesystem().capture_inode(namespace_fd, RECORD_TEMP_NAME, "regular")
                if current is None or not NativeAtomicFilesystem._same_content_identity(current, witness):
                    raise PrivateStateForeignError("RECORD-TEMP changed before witness rollback")
                self._filesystem().unlink_bound(namespace_fd, RECORD_TEMP_NAME, witness)
                self._filesystem().fsync_directory(namespace_fd)
            except (AtomicRenameUnavailable, FilesystemSafetyError, PrivateStateError, OSError) as cleanup_failure:
                raise PrivateStateError(
                    "RECORD-TEMP cleanup failed after ACTIVE publication error"
                ) from cleanup_failure
            finally:
                os.close(namespace_fd)
            raise failure
        namespace_fd = active_store._open_namespace()
        specdock_components = ("spec-dock",)
        specdock_fd = -1
        filesystem = self._filesystem()
        exchanged = False
        try:
            self._require_bootstrap_binding(active, root_fd)
            specdock_fd, specdock_binding = _open_path_bound(root_fd, specdock_components)
            self._require_bootstrap_binding(active, root_fd)
            if not specdock_binding or not self._directory_binding_matches(
                active.bootstrap_container.get("witness"), specdock_binding[-1]
            ):
                raise PrivateStateForeignError("bootstrap container binding changed before record publication")
            _require_path_binding(root_fd, specdock_components, specdock_binding, specdock_fd)
            try:
                old_raw, old_witness = _read_regular(specdock_fd, "spec-dock.version")
            except FileNotFoundError:
                old_raw, old_witness = None, None
            if old_raw != predecessor_raw or old_witness != predecessor_witness:
                raise PrivateStateForeignError("public record predecessor changed before publication")
            if old_witness is None:
                self._check_fault("record-publish-no-replace")
                self._rename_no_replace_bound(
                    filesystem,
                    root_fd,
                    specdock_components,
                    specdock_binding,
                    specdock_fd,
                    namespace_fd,
                    RECORD_TEMP_NAME,
                    specdock_fd,
                    "spec-dock.version",
                    expected_source=witness,
                )
            else:
                assert predecessor_witness is not None
                self._check_fault("record-publish-exchange")
                self._exchange_bound(
                    filesystem,
                    root_fd,
                    specdock_components,
                    specdock_binding,
                    specdock_fd,
                    namespace_fd,
                    RECORD_TEMP_NAME,
                    specdock_fd,
                    "spec-dock.version",
                    expected_source=witness,
                    expected_destination=predecessor_witness,
                )
                _, residue_witness = _read_regular(namespace_fd, RECORD_TEMP_NAME)
                if not NativeAtomicFilesystem._same_content_identity(residue_witness, predecessor_witness):
                    raise PrivateStateForeignError("public record exchange residue is foreign")
                public_raw, public_witness = _read_regular(specdock_fd, "spec-dock.version")
                if (
                    public_raw != payload
                    or public_witness.mode != 0o644
                    or not NativeAtomicFilesystem._same_content_identity(public_witness, witness)
                ):
                    raise FilesystemSafetyError("public record exchange source is foreign")
                self._check_fault("record-parent-fsync")
                filesystem.fsync_directory(specdock_fd)
                current_raw, current_witness = _read_regular(specdock_fd, "spec-dock.version")
                if (
                    current_raw != payload
                    or current_witness.mode != 0o644
                    or not NativeAtomicFilesystem._same_content_identity(current_witness, witness)
                ):
                    raise FilesystemSafetyError("public record changed before ACTIVE publication")
                active = replace(
                    active,
                    record_temp_witness=residue_witness,
                    public_record_witness=current_witness,
                )
                active_witness = self._save_active(active_store, active, expected=active_witness)
                self._check_fault("record-exchange-residue-unlink")
                current_raw, current_witness = _read_regular(specdock_fd, "spec-dock.version")
                if (
                    current_raw != payload
                    or current_witness.mode != 0o644
                    or not NativeAtomicFilesystem._same_content_identity(current_witness, witness)
                ):
                    raise FilesystemSafetyError("public record changed before exchange residue cleanup")
                filesystem.unlink_bound(namespace_fd, RECORD_TEMP_NAME, residue_witness)
                filesystem.fsync_directory(namespace_fd)
                exchanged = True
            if not exchanged:
                self._check_fault("record-parent-fsync")
                filesystem.fsync_directory(specdock_fd)
                current_raw, current_witness = _read_regular(specdock_fd, "spec-dock.version")
                if (
                    current_raw != payload
                    or current_witness.mode != 0o644
                    or not NativeAtomicFilesystem._same_content_identity(current_witness, witness)
                ):
                    raise FilesystemSafetyError("public record postcondition failed")
        finally:
            if specdock_fd >= 0:
                os.close(specdock_fd)
            os.close(namespace_fd)
        final_active = replace(active, record_temp_witness=None, public_record_witness=current_witness)
        final_witness = self._save_active(active_store, final_active, expected=active_witness)
        return final_active, final_witness

    def _ensure_expected_record_durable(self, active: ActiveState, root_fd: int) -> None:
        expected = base64.b64decode(active.expected_incomplete_record["bytes_base64"])
        specdock_fd = _open_path(root_fd, ("spec-dock",))
        try:
            self._check_fault("record-parent-fsync")
            self._filesystem().fsync_directory(specdock_fd)
            current, witness = _read_regular(specdock_fd, "spec-dock.version")
        finally:
            os.close(specdock_fd)
        if current != expected:
            raise PrivateStateForeignError("expected incomplete record changed before re-entry")
        if active.public_record_witness is not None and NativeAtomicFilesystem._same_content_identity(
            witness, active.public_record_witness
        ):
            return
        if active.record_temp_witness is None or not NativeAtomicFilesystem._same_content_identity(
            witness, active.record_temp_witness
        ):
            raise PrivateStateForeignError("expected incomplete record changed before re-entry")

    def _target_matches_candidate(
        self,
        root_fd: int,
        item: _ObservedTarget,
        index: int,
        candidate: CandidateIdentity,
    ) -> bool:
        if item.kind != "directory" or item.tree is None:
            return False
        expected = candidate.domains[index]
        if item.tree.tree_digest != expected.tree_digest or item.tree.entry_count != expected.entry_count:
            return False
        if index < 4:
            return True
        return self._slot_marker_matches(
            root_fd,
            item,
            candidate,
            expected_digest=candidate.aggregate_digest,
        )

    @staticmethod
    def _rollback_no_replace(
        filesystem: NativeAtomicFilesystem,
        source_parent_fd: int,
        source_name: str,
        destination_parent_fd: int,
        destination_name: str,
        expected_source: InodeWitness,
    ) -> None:
        source = filesystem.capture_inode(source_parent_fd, source_name, expected_source.kind)
        destination = filesystem.capture_inode(destination_parent_fd, destination_name, expected_source.kind)
        if source is not None:
            if destination is None or not NativeAtomicFilesystem._same_content_identity(destination, expected_source):
                return
            raise FilesystemSafetyError("native no-replace rollback found duplicate source identity")
        if destination is None or not NativeAtomicFilesystem._same_content_identity(destination, expected_source):
            raise FilesystemSafetyError("native no-replace rollback cannot identify moved source")
        filesystem.rename_no_replace(
            destination_parent_fd,
            destination_name,
            source_parent_fd,
            source_name,
            expected_source=expected_source,
        )
        filesystem.fsync_directory(destination_parent_fd)
        filesystem.fsync_directory(source_parent_fd)

    def _rename_no_replace_bound(
        self,
        filesystem: NativeAtomicFilesystem,
        root_fd: int,
        destination_components: Sequence[str],
        expected_binding: Sequence[InodeWitness],
        bound_parent_fd: int,
        source_parent_fd: int,
        source_name: str,
        destination_parent_fd: int,
        destination_name: str,
        expected_source: InodeWitness,
    ) -> None:
        _require_path_binding(root_fd, destination_components, expected_binding, bound_parent_fd)
        try:
            filesystem.rename_no_replace(
                source_parent_fd,
                source_name,
                destination_parent_fd,
                destination_name,
                expected_source=expected_source,
            )
            _require_path_binding(root_fd, destination_components, expected_binding, bound_parent_fd)
        except (AtomicRenameUnavailable, FilesystemSafetyError, OSError) as failure:
            try:
                self._rollback_no_replace(
                    filesystem,
                    source_parent_fd,
                    source_name,
                    destination_parent_fd,
                    destination_name,
                    expected_source,
                )
            except (AtomicRenameUnavailable, FilesystemSafetyError, OSError) as cleanup_failure:
                raise FilesystemSafetyError("native no-replace rollback failed") from cleanup_failure
            raise failure

    @staticmethod
    def _rollback_exchange(
        filesystem: NativeAtomicFilesystem,
        source_parent_fd: int,
        source_name: str,
        destination_parent_fd: int,
        destination_name: str,
        expected_source: InodeWitness,
        expected_destination: InodeWitness,
    ) -> None:
        source = filesystem.capture_inode(source_parent_fd, source_name, expected_destination.kind)
        destination = filesystem.capture_inode(destination_parent_fd, destination_name, expected_source.kind)
        if source is not None and destination is not None:
            if NativeAtomicFilesystem._same_content_identity(
                source, expected_source
            ) and NativeAtomicFilesystem._same_content_identity(destination, expected_destination):
                return
            if NativeAtomicFilesystem._same_content_identity(
                source, expected_destination
            ) and NativeAtomicFilesystem._same_content_identity(destination, expected_source):
                filesystem.exchange(
                    source_parent_fd,
                    source_name,
                    destination_parent_fd,
                    destination_name,
                    expected_source=expected_destination,
                    expected_destination=expected_source,
                )
                filesystem.fsync_directory(source_parent_fd)
                filesystem.fsync_directory(destination_parent_fd)
                return
        raise FilesystemSafetyError("native exchange rollback cannot identify swapped identities")

    def _exchange_bound(
        self,
        filesystem: NativeAtomicFilesystem,
        root_fd: int,
        destination_components: Sequence[str],
        expected_binding: Sequence[InodeWitness],
        bound_parent_fd: int,
        source_parent_fd: int,
        source_name: str,
        destination_parent_fd: int,
        destination_name: str,
        expected_source: InodeWitness,
        expected_destination: InodeWitness,
    ) -> None:
        _require_path_binding(root_fd, destination_components, expected_binding, bound_parent_fd)
        try:
            filesystem.exchange(
                source_parent_fd,
                source_name,
                destination_parent_fd,
                destination_name,
                expected_source=expected_source,
                expected_destination=expected_destination,
            )
            _require_path_binding(root_fd, destination_components, expected_binding, bound_parent_fd)
        except (AtomicRenameUnavailable, FilesystemSafetyError, OSError) as failure:
            try:
                self._rollback_exchange(
                    filesystem,
                    source_parent_fd,
                    source_name,
                    destination_parent_fd,
                    destination_name,
                    expected_source,
                    expected_destination,
                )
            except (AtomicRenameUnavailable, FilesystemSafetyError, OSError) as cleanup_failure:
                raise FilesystemSafetyError("native exchange rollback failed") from cleanup_failure
            raise failure

    def _publish_domain(
        self,
        _request: LifecycleRequest,
        active: ActiveState,
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
                self._ensure_domain_durable(root_fd, stage_store, path, expected_absent=True)
                return
        destination_components = components[:-1]
        destination_parent, destination_binding = _open_path_bound(root_fd, destination_components, create=not detach)
        stage_fd = stage_store._stage_fd()
        filesystem = self._filesystem()
        try:
            target = self._observe_target(root_fd, path, expect_tree=True)
            stored = active.owned_target_witnesses[index]
            if not (
                self._target_matches_active_original(root_fd, active, index, target)
                or self._target_matches_terminal(root_fd, target, stored, active.candidate_digest)
            ):
                raise FilesystemSafetyError(f"fixed target binding changed during publication at {path}")
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
                self._rename_no_replace_bound(
                    filesystem,
                    root_fd,
                    destination_components,
                    destination_binding,
                    destination_parent,
                    destination_parent,
                    components[-1],
                    stage_fd,
                    name,
                    expected_source=target.witness,
                )
            else:
                if candidate is None:
                    raise CandidateError("candidate is required for publication")
                if self._target_matches_candidate(root_fd, target, index, candidate):
                    self._ensure_domain_durable(root_fd, stage_store, path, index=index, candidate=candidate)
                    return
                if target.kind == "absent":
                    source_witness = filesystem.capture_inode(stage_fd, name, "directory")
                    if source_witness is None:
                        raise FilesystemSafetyError(f"missing stage source witness at {name}")
                    self._rename_no_replace_bound(
                        filesystem,
                        root_fd,
                        destination_components,
                        destination_binding,
                        destination_parent,
                        stage_fd,
                        name,
                        destination_parent,
                        components[-1],
                        expected_source=source_witness,
                    )
                elif target.kind == "directory":
                    if target.witness is None:
                        raise FilesystemSafetyError(f"missing fixed target witness at {path}")
                    source_witness = filesystem.capture_inode(stage_fd, name, "directory")
                    if source_witness is None:
                        raise FilesystemSafetyError(f"missing stage source witness at {name}")
                    self._exchange_bound(
                        filesystem,
                        root_fd,
                        destination_components,
                        destination_binding,
                        destination_parent,
                        stage_fd,
                        name,
                        destination_parent,
                        components[-1],
                        expected_source=source_witness,
                        expected_destination=target.witness,
                    )
                else:
                    raise FilesystemSafetyError(f"unsafe fixed target type at {path}")
            self._check_fault("source-parent-fsync")
            filesystem.fsync_directory(stage_fd)
            self._check_fault("target-parent-fsync")
            filesystem.fsync_directory(destination_parent)
        finally:
            os.close(stage_fd)
            os.close(destination_parent)

    def _ensure_domain_durable(
        self,
        root_fd: int,
        stage_store: StageStore,
        path: str,
        *,
        index: int | None = None,
        candidate: CandidateIdentity | None = None,
        expected_absent: bool = False,
    ) -> None:
        """Re-fsync both sides of a visible domain transition before reuse."""

        components = _target_components(path)
        destination_parent = _open_path(root_fd, components[:-1])
        stage_fd = stage_store._stage_fd()
        try:
            self._filesystem().fsync_directory(stage_fd)
            self._filesystem().fsync_directory(destination_parent)
        finally:
            os.close(stage_fd)
            os.close(destination_parent)
        current = self._observe_target(root_fd, path, expect_tree=True)
        if expected_absent:
            if current.kind != "absent":
                raise FilesystemSafetyError(f"domain {path} changed during durability repair")
            return
        if candidate is None or index is None or not self._target_matches_candidate(root_fd, current, index, candidate):
            raise FilesystemSafetyError(f"domain {path} changed during durability repair")

    def _publish_seed(
        self,
        _request: LifecycleRequest,
        active: ActiveState,
        root_fd: int,
        public_path: str,
        seed_name: str,
        source_suffix: str,
    ) -> None:
        admission_state = active.seed_admission[public_path]
        item = self._observe_target(root_fd, public_path, expect_tree=False)
        if item.kind == "symlink" or item.kind == "other" or item.kind == "directory":
            raise FilesystemSafetyError(f"unsafe seed type at {public_path}")
        if item.kind == "regular":
            self._ensure_seed_durable(root_fd, public_path)
            return
        if admission_state == "present" or active.seed_policy != "create-if-absent":
            return
        if item.kind != "absent":
            return
        self._check_fault(f"seed-{seed_name}-no-replace-create")
        components = _target_components(public_path)
        parent_components = components[:-1]
        parent_fd, parent_binding = _open_path_bound(root_fd, parent_components, create=True)
        destination_fd = -1
        created_witness: InodeWitness | None = None
        filesystem = self._filesystem()
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
                _require_path_binding(root_fd, parent_components, parent_binding, parent_fd)
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
                created_witness = filesystem.capture_inode(parent_fd, components[-1], "regular")
                if created_witness is None:
                    raise FilesystemSafetyError(f"seed {public_path} disappeared after publication")
                _require_path_binding(root_fd, parent_components, parent_binding, parent_fd)
            except FileExistsError:
                # The no-replace operation lost a race.  Reclassify the visible
                # entry; never replace a consumer seed.
                pass
            self._check_fault(f"seed-{seed_name}-parent-fsync")
            filesystem.fsync_directory(parent_fd)
            _require_path_binding(root_fd, parent_components, parent_binding, parent_fd)
            current = self._observe_target(root_fd, public_path, expect_tree=False)
            if current.kind not in {"regular"}:
                raise FilesystemSafetyError(f"seed {public_path} changed after publication")
        except (AtomicRenameUnavailable, FilesystemSafetyError, OSError) as failure:
            if created_witness is not None:
                try:
                    created_current = filesystem.capture_inode(parent_fd, components[-1], "regular")
                    if created_current is not None and NativeAtomicFilesystem._same_content_identity(
                        created_current, created_witness
                    ):
                        filesystem.unlink_bound(parent_fd, components[-1], created_witness)
                        filesystem.fsync_directory(parent_fd)
                    elif created_current is not None:
                        raise FilesystemSafetyError(f"seed {public_path} changed during rollback")
                except (AtomicRenameUnavailable, FilesystemSafetyError, OSError) as cleanup_failure:
                    raise FilesystemSafetyError(f"seed {public_path} rollback failed") from cleanup_failure
            raise failure
        finally:
            if destination_fd >= 0:
                os.close(destination_fd)
            os.close(source_fd)
            os.close(parent_fd)

    def _ensure_seed_durable(self, root_fd: int, public_path: str) -> None:
        components = _target_components(public_path)
        parent_fd = _open_path(root_fd, components[:-1])
        try:
            self._filesystem().fsync_directory(parent_fd)
        finally:
            os.close(parent_fd)
        if self._observe_target(root_fd, public_path, expect_tree=False).kind != "regular":
            raise FilesystemSafetyError(f"seed {public_path} changed during durability repair")

    def _finish_cleanup(
        self,
        request: LifecycleRequest,
        active: ActiveState,
        active_store: ActiveStateStore,
        receipt_store: CompletionReceiptStore,
        stage_store: StageStore,
        root_fd: int,
        *,
        active_witness: InodeWitness,
        receipt: CompletionReceipt | None = None,
        receipt_witness: InodeWitness | None = None,
        cleanup_only: bool = False,
        initial_absent_paths: frozenset[str] | None = None,
    ) -> LifecycleResult:
        try:
            self._cleanup_stage(stage_store, active)
            self._check_fault("stage-parent-fsync")
            stored_active, stored_witness = active_store.load_with_witness()
            if stored_active != active or stored_witness != active_witness:
                raise PrivateStateForeignError("ACTIVE changed before receipt publication")
            if stored_witness is None:
                raise PrivateStateForeignError("ACTIVE witness is missing before receipt publication")
            if active.public_record_witness is None or not self._terminal_record_matches(
                root_fd,
                operation=active.operation,
                candidate_digest=active.candidate_digest,
                seed_policy=active.seed_policy,
                terminal_record_digest=active.terminal_record_digest,
                expected_witness=active.public_record_witness,
            ):
                raise PrivateStateForeignError("public record changed before receipt publication")
            if receipt is None:
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
                receipt_witness = receipt_store.save(receipt, expected_absent=True, fault=self._check_fault)
            self._check_fault("active-expected-unlink")
            stored_active, stored_witness = active_store.load_with_witness()
            if stored_active != active or stored_witness != active_witness:
                raise PrivateStateForeignError("ACTIVE changed before expected unlink")
            if stored_witness is None:
                raise PrivateStateForeignError("ACTIVE witness is missing before expected unlink")
            namespace_fd = active_store._open_namespace()
            try:
                if receipt_witness is None:
                    raise PrivateStateForeignError("completion receipt witness is missing before expected unlink")
                stored_receipt, stored_receipt_witness = receipt_store.load_with_witness()
                if stored_receipt != receipt or stored_receipt_witness != receipt_witness:
                    raise PrivateStateForeignError("completion receipt changed before expected unlink")
                if stored_active.public_record_witness is None or not self._terminal_record_matches(
                    root_fd,
                    operation=stored_active.operation,
                    candidate_digest=stored_active.candidate_digest,
                    seed_policy=stored_active.seed_policy,
                    terminal_record_digest=stored_active.terminal_record_digest,
                    expected_witness=stored_active.public_record_witness,
                ):
                    raise PrivateStateForeignError("public record changed before expected unlink")
                self._filesystem().unlink_bound(namespace_fd, ACTIVE_NAME, stored_witness)
                self._check_fault("active-expected-parent-fsync")
                self._filesystem().fsync_directory(namespace_fd)
            finally:
                os.close(namespace_fd)
        except (
            _LifecycleFailure,
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
            return (
                self._cleanup_completed_result(request, active)
                if cleanup_only
                else self._completed_result(request, active, root_fd, initial_absent_paths=initial_absent_paths)
            )
        return (
            self._cleanup_completed_result(request, active)
            if cleanup_only
            else self._completed_result(request, active, root_fd, initial_absent_paths=initial_absent_paths)
        )

    def _cleanup_stage(self, stage_store: StageStore, active: ActiveState) -> None:
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
            names = tuple(sorted(os.listdir(stage_fd), key=lambda name: os.fsencode(name)))  # noqa: PTH208
            allowed = {STAGE_OWNER_NAME, *STAGE_ENTRY_NAMES}
            if any(name not in allowed for name in names):
                raise PrivateStateForeignError("STAGE contains an unknown entry")
            expected_owner = self._stage_owner(active)
            owner_witness = None
            current_owner = stage_store.load_owner()
            if current_owner is None:
                if names:
                    raise PrivateStateForeignError("STAGE-OWNER.json is missing")
            else:
                if current_owner != expected_owner:
                    raise PrivateStateForeignError("STAGE-OWNER.json belongs to another operation")
                owner_witness = self._filesystem().capture_inode(stage_fd, STAGE_OWNER_NAME, "regular")
                if owner_witness is None:
                    raise PrivateStateForeignError("STAGE-OWNER.json disappeared during cleanup")
            registered = {str(item["name"]): item for item in active.registered_stage_entries}
            staged_trees: dict[str, DomainTreeIdentity] = {}
            for index, name in enumerate(STAGE_ENTRY_NAMES):
                try:
                    value = os.stat(name, dir_fd=stage_fd, follow_symlinks=False)
                except FileNotFoundError:
                    continue
                if not stat.S_ISDIR(value.st_mode):
                    raise PrivateStateForeignError(f"stage entry {name} is unsafe")
                _witness, tree = self._capture_engine_domain(stage_fd, name)
                validation_tree = (
                    project_domain_tree(tree, exclude_root_names={SLOT_MARKER_NAME}) if index >= 4 else tree
                )
                stored = active.owned_target_witnesses[index]
                registered_entry = registered.get(name)
                if (
                    registered_entry is None
                    or registered_entry["original_tree_digest"] != stored["original_tree_digest"]
                ):
                    raise PrivateStateForeignError(f"stage entry {name} is not registered by ACTIVE")
                original_kind = stored["original_kind"]
                if original_kind == "directory":
                    expected_digest = registered_entry["original_tree_digest"]
                    if validation_tree.tree_digest != expected_digest:
                        raise PrivateStateForeignError(f"stage entry {name} has foreign payload")
                elif active.operation == "uninstall":
                    if validation_tree.entry_count != 0 or (
                        index >= 4 and not self._stage_slot_marker_absent(stage_fd, name)
                    ):
                        raise PrivateStateForeignError(f"stage entry {name} has foreign payload")
                else:
                    raise PrivateStateForeignError(f"unexpected stage entry {name} remains after publication")
                staged_trees[name] = tree

            for name in STAGE_ENTRY_NAMES:
                staged_tree = staged_trees.get(name)
                if staged_tree is None:
                    continue
                self._check_fault(f"stage-entry-{name}-remove")
                self._filesystem().remove_tree_bound(stage_fd, name, staged_tree)
            if owner_witness is not None:
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

    def _completed_result(
        self,
        request: LifecycleRequest,
        active: ActiveState,
        root_fd: int,
        *,
        initial_absent_paths: frozenset[str] | None = None,
    ) -> LifecycleResult:
        if active.operation == "uninstall":
            targets = self._observe_domains(root_fd)
            actions = self._uninstall_actions(
                targets,
                self._observe_container(root_fd),
                None,
                planned=False,
                include_stage=True,
                original_targets=active.owned_target_witnesses,
                initial_absent_paths=initial_absent_paths,
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
                original_targets=active.owned_target_witnesses,
                seed_admission=active.seed_admission,
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
        *,
        initial_absent_paths: frozenset[str] | None = None,
    ) -> LifecycleResult:
        if active.state in {"ready", "terminal-cleanup"}:
            return self._terminal_cleanup_failure(request, active, failure)
        point = getattr(failure, "point", "")
        phase = self._phase_for_fault(point, active.operation)
        if active.state == "prepared" and phase == "cleanup-stage" and point.startswith("active-"):
            phase = "publish-incomplete-record"
        if phase == "bootstrap-container":
            if getattr(failure, "bootstrap_rolled_back", False):
                return self._blocked(
                    request,
                    "bootstrap-container-conflict",
                    operation=active.operation,
                    candidate_digest=active.candidate_digest,
                    seed_policy=active.seed_policy,
                    phase="bootstrap-container",
                    last_completed_phase="candidate-staging",
                    bootstrap_rolled_back=True,
                )
            if getattr(failure, "bootstrap_cleanup_failed", False):
                retry = self._retry_for(request, active.operation, active.seed_policy)
                bootstrap_actions = self._bootstrap_cleanup_actions(active, root_fd)
                failed_paths, pending_paths = _action_path_sets(bootstrap_actions)
                return build_public_result(
                    request,
                    status="partial_failure",
                    code="bootstrap-cleanup-failed",
                    operation=active.operation,
                    candidate_digest=active.candidate_digest,
                    seed_policy=active.seed_policy,
                    mutation_started=True,
                    phase="bootstrap-container",
                    last_completed_phase="candidate-staging",
                    retry_command=retry,
                    continuation=_lifecycle_continuation(retry) if retry is not None else _empty_continuation(),
                    failed_paths=failed_paths,
                    pending_paths=pending_paths,
                    actions=bootstrap_actions,
                )
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
            mutation_started = phase == "publish-incomplete-record" and self._preparation_mutation_started(
                active, root_fd
            )
            if mutation_started is None:
                return self._blocked(
                    request,
                    "stage-owner-mismatch",
                    operation=active.operation,
                    candidate_digest=active.candidate_digest,
                    seed_policy=active.seed_policy,
                    phase="candidate-staging",
                    last_completed_phase="preflight",
                )
            return self._preparation_failure(
                request,
                active.operation,
                active.candidate_digest,
                active.seed_policy,
                failure,
                phase=phase,
                last_completed_phase=(
                    "preflight"
                    if phase == "candidate-staging"
                    else "candidate-staging"
                    if active.original_record.get("kind") == "final"
                    else "bootstrap-container"
                ),
                mutation_started=mutation_started,
                actions=self._preparation_partial_actions(active, root_fd) if mutation_started else (),
            )
        if phase == "preflight":
            return self._blocked(request, "lifecycle-preparation-failed")
        retry = self._retry_for(request, active.operation, active.seed_policy)
        if retry is None:
            retry = active.cleanup_retry_invocation["rendered_command"]
        index = self._partial_index_for_phase(phase)
        if active.operation == "uninstall":
            actions = list(
                self._uninstall_actions(
                    self._observe_domains(root_fd),
                    self._observe_container(root_fd),
                    None,
                    planned=False,
                    include_stage=True,
                    partial_index=index,
                    partial_phase=phase,
                    original_targets=active.owned_target_witnesses,
                    initial_absent_paths=initial_absent_paths,
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
                    partial_phase=phase,
                    original_targets=active.owned_target_witnesses,
                    include_stage=True,
                    failure_point=point,
                    seed_admission=active.seed_admission,
                )
            )
            code = "install-partial-failure" if active.operation == "install" else "update-partial-failure"
        if actions and actions[-1].path == "@provider-stage":
            actions[-1] = LifecycleAction("@provider-stage", "stage", "pending", "candidate-stage-cleanup")
        last_completed = self._last_completed_phase(phase, active.operation, active.seed_policy)
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
    def _last_completed_phase(phase: str, operation: str, seed_policy: str) -> str:
        order: tuple[str, ...]
        if operation == "uninstall":
            order = (
                "request-validation",
                "preflight",
                "candidate-staging",
                "bootstrap-container",
                "publish-incomplete-record",
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
        else:
            order = (
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
                "verify-target",
                "publish-terminal-record",
                "cleanup-stage",
                "complete",
            )
            if operation == "install" and seed_policy == "create-if-absent":
                order = (
                    *order[:11],
                    "create-seed-spec-dock-gitignore",
                    "create-seed-consumer-ci",
                    *order[11:],
                )
        try:
            index = order.index(phase)
        except ValueError:
            return "request-validation"
        return "request-validation" if index == 0 else order[index - 1]

    @staticmethod
    def _partial_index_for_phase(phase: str) -> int | None:
        target_indices = {
            "publish-docs": 0,
            "publish-templates": 1,
            "publish-system": 2,
            "publish-scripts": 3,
            "publish-slot-spec-dock": 4,
            "publish-slot-spec-dock-grill-with-docs": 5,
            "detach-docs": 0,
            "detach-templates": 1,
            "detach-system": 2,
            "detach-scripts": 3,
            "detach-slot-spec-dock": 4,
            "detach-slot-spec-dock-grill-with-docs": 5,
            "create-seed-spec-dock-gitignore": 6,
            "create-seed-consumer-ci": 7,
            "verify-target": 6,
            "publish-terminal-record": 7,
        }
        return target_indices.get(phase)

    @staticmethod
    def _phase_for_fault(point: str, operation: str) -> str:
        if point in PHASES:
            return point
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
        *,
        active_witness: InodeWitness | None,
        receipt_witness: InodeWitness | None,
        force: bool | None,
    ) -> LifecycleResult:
        if active is not None:
            if active.state not in {"ready", "terminal-cleanup"}:
                return self.invalid_request(request)
            if active.cleanup_token != token or not _cleanup_request_matches(
                request,
                force=force,
                token=token,
                expected=active.cleanup_retry_invocation,
            ):
                return self.invalid_request(request)
            if active_store is None or receipt_store is None or stage_store is None:
                return self._blocked(request, "lifecycle-preparation-failed")
            if active_witness is None:
                return self._blocked(request, "lifecycle-preparation-failed")
            return self._complete_pending_cleanup(
                request,
                active,
                active_store,
                receipt_store,
                stage_store,
                root_fd,
                active_witness=active_witness,
                receipt_witness=receipt_witness,
                force=force,
                receipt=receipt,
                capture_desired=False,
            )
        if receipt is not None and receipt.cleanup_token == token:
            if not _cleanup_request_matches(
                request,
                force=force,
                token=token,
                expected=receipt.cleanup_retry_invocation,
            ) or not self._terminal_record_matches(
                root_fd,
                operation=receipt.operation,
                candidate_digest=receipt.candidate_digest,
                seed_policy=receipt.seed_policy,
                terminal_record_digest=receipt.terminal_record_digest,
            ):
                return self.invalid_request(request)
            return build_public_result(
                request,
                status="completed",
                code="terminal-cleanup-completed",
                operation=receipt.operation,
                candidate_digest=receipt.candidate_digest,
                seed_policy=receipt.seed_policy,
                phase="complete",
                last_completed_phase="cleanup-stage",
                continuation=_completed_cleanup_continuation(receipt.deferred_invocation),
                actions=(),
                guidance=(
                    CLEANUP_COMPLETED_DEFERRED_GUIDANCE
                    if receipt.deferred_invocation is not None
                    else CLEANUP_COMPLETED_GUIDANCE
                ),
            )
        return self.invalid_request(request)

    def _terminal_record_matches(
        self,
        root_fd: int,
        *,
        operation: str,
        candidate_digest: str,
        seed_policy: str,
        terminal_record_digest: str,
        expected_witness: InodeWitness | None = None,
    ) -> bool:
        try:
            specdock_fd = _open_path(root_fd, ("spec-dock",))
            try:
                self._filesystem().fsync_directory(specdock_fd)
            finally:
                os.close(specdock_fd)
            raw, witness, record, record_kind = self._observe_record("", root_fd)
        except (FilesystemSafetyError, OSError, ValueError, WireValidationError):
            return False
        if raw is None or record is None or record_kind != "final":
            return False
        if expected_witness is not None and (
            witness is None or not NativeAtomicFilesystem._same_content_identity(witness, expected_witness)
        ):
            return False
        expected_state = "tooling-absent-preserved-data" if operation == "uninstall" else "ready"
        return (
            record.state == expected_state
            and record.operation is None
            and record.candidate_digest == candidate_digest
            and record.seed_policy == seed_policy
            and hashlib.sha256(raw).hexdigest() == terminal_record_digest
        )

    def _complete_pending_cleanup(
        self,
        request: LifecycleRequest,
        active: ActiveState,
        active_store: ActiveStateStore | None,
        receipt_store: CompletionReceiptStore | None,
        stage_store: StageStore | None,
        root_fd: int,
        *,
        active_witness: InodeWitness,
        receipt_witness: InodeWitness | None = None,
        force: bool | None = None,
        receipt: CompletionReceipt | None = None,
        capture_desired: bool = True,
    ) -> LifecycleResult:
        if active_store is None or receipt_store is None or stage_store is None:
            return self._blocked(request, "lifecycle-preparation-failed")
        if receipt is not None and receipt_witness is None:
            return self._blocked(request, "lifecycle-preparation-failed")
        if receipt is not None and not self._receipt_matches_active(receipt, active):
            return self.invalid_request(request)
        if receipt is not None:
            if active.deferred_invocation is not None and active.deferred_invocation != receipt.deferred_invocation:
                return self.invalid_request(request)
            if active.deferred_invocation is None and receipt.deferred_invocation is None and capture_desired:
                receipt = replace(receipt, deferred_invocation=_desired_invocation(request, force=force))
                try:
                    receipt_witness = receipt_store.save(
                        receipt,
                        expected=receipt_witness,
                        fault=self._check_fault,
                    )
                except (
                    AtomicRenameUnavailable,
                    FilesystemSafetyError,
                    PrivateStateError,
                    OSError,
                    _InjectedFailure,
                ) as failure:
                    try:
                        durable_receipt, durable_witness = receipt_store.load_with_witness()
                    except (PrivateStateError, OSError):
                        durable_receipt, durable_witness = None, None
                    if durable_receipt is not None and durable_witness is not None and durable_receipt == receipt:
                        receipt = durable_receipt
                        receipt_witness = durable_witness
                        active = replace(active, deferred_invocation=durable_receipt.deferred_invocation)
                    return self._terminal_cleanup_failure(request, active, failure)
            if active.deferred_invocation != receipt.deferred_invocation:
                active = replace(active, deferred_invocation=receipt.deferred_invocation)
                try:
                    active_witness = self._save_active(active_store, active, expected=active_witness)
                except (
                    AtomicRenameUnavailable,
                    FilesystemSafetyError,
                    PrivateStateError,
                    OSError,
                    _InjectedFailure,
                ) as failure:
                    return self._terminal_cleanup_failure(request, active, failure)
        try:
            if not self._terminal_record_matches(
                root_fd,
                operation=active.operation,
                candidate_digest=active.candidate_digest,
                seed_policy=active.seed_policy,
                terminal_record_digest=active.terminal_record_digest,
                expected_witness=active.public_record_witness,
            ):
                raw, witness, record, record_kind = self._observe_record(request.target, root_fd)
                if self._record_matches_expected(active, raw, witness, record, record_kind):
                    if raw is None or witness is None:
                        return self._blocked(request, "installation-record-state-inconsistent")
                    active, active_witness = self._write_public_record(
                        request,
                        active,
                        self._terminal_record_bytes(active),
                        active_store,
                        root_fd,
                        expected_active_witness=active_witness,
                        expected_predecessor=(raw, witness),
                        predecessor_kind="incomplete",
                    )
                elif self._post_exchange_terminal_record_matches(active, root_fd, active_store):
                    if witness is None:
                        return self._blocked(request, "installation-record-state-inconsistent")
                    active, active_witness = self._recover_public_record_state(
                        active,
                        witness,
                        active_store,
                        active_witness,
                        root_fd=root_fd,
                        residue_kind="incomplete",
                    )
                else:
                    return self._blocked(request, "installation-record-state-inconsistent")
                if not self._terminal_record_matches(
                    root_fd,
                    operation=active.operation,
                    candidate_digest=active.candidate_digest,
                    seed_policy=active.seed_policy,
                    terminal_record_digest=active.terminal_record_digest,
                    expected_witness=active.public_record_witness,
                ):
                    return self._blocked(request, "installation-record-state-inconsistent")
            active, active_witness = self._cleanup_record_exchange_residue(
                active,
                active_store,
                active_witness,
                root_fd=root_fd,
            )
            if receipt is not None and not self._terminal_record_matches(
                root_fd,
                operation=receipt.operation,
                candidate_digest=receipt.candidate_digest,
                seed_policy=receipt.seed_policy,
                terminal_record_digest=receipt.terminal_record_digest,
            ):
                return self.invalid_request(request)
            if receipt is None and capture_desired and active.deferred_invocation is None:
                active = replace(active, deferred_invocation=_desired_invocation(request, force=force))
                active_witness = self._save_active(active_store, active, expected=active_witness)
            if active.state == "ready":
                active = replace(active, state="terminal-cleanup")
                active_witness = self._save_active(active_store, active, expected=active_witness)
        except (
            AtomicRenameUnavailable,
            FilesystemSafetyError,
            PrivateStateError,
            OSError,
            _InjectedFailure,
        ) as failure:
            return self._terminal_cleanup_failure(request, active, failure)
        return self._finish_cleanup(
            request,
            active,
            active_store,
            receipt_store,
            stage_store,
            root_fd,
            active_witness=active_witness,
            receipt=receipt,
            receipt_witness=receipt_witness,
            cleanup_only=True,
        )

    @staticmethod
    def _receipt_matches_active(receipt: CompletionReceipt, active: ActiveState) -> bool:
        return (
            receipt.repository_key == active.repository_key
            and receipt.tuple_key == active.tuple_key
            and receipt.operation_generation == active.operation_generation
            and receipt.operation == active.operation
            and receipt.candidate_digest == active.candidate_digest
            and receipt.seed_policy == active.seed_policy
            and receipt.result_family == active.result_family
            and receipt.terminal_record_digest == active.terminal_record_digest
            and receipt.cleanup_token == active.cleanup_token
        )

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
        active_witness: InodeWitness | None = None,
        force: bool | None = None,
    ) -> LifecycleResult:
        if not self._request_admits_active(operation, seed_policy, active, force=force):
            code = (
                "resume-seed-policy-mismatch"
                if active.operation == operation == "install"
                else "resume-operation-mismatch"
            )
            return self._blocked(
                request,
                code,
                operation=active.operation,
                candidate_digest=active.candidate_digest,
                seed_policy=active.seed_policy,
            )
        if request.mode == "dry-run":
            if active.operation != "uninstall":
                return self._blocked(
                    request,
                    "resume-operation-mismatch",
                    operation=active.operation,
                    candidate_digest=active.candidate_digest,
                    seed_policy=active.seed_policy,
                )
            if stage_store is None:
                return self._blocked(request, "lifecycle-preparation-failed")
            try:
                stage_state, _stage_entries = stage_store.inspect(self._stage_owner(active))
                if stage_state == "complete" and not self._stage_payload_valid(stage_store, None, root_fd):
                    raise PrivateStateForeignError("prepared uninstall stage payload is unsafe")
            except PrivateStateForeignError:
                return self._blocked(
                    request,
                    "stage-owner-mismatch",
                    operation=active.operation,
                    candidate_digest=active.candidate_digest,
                    seed_policy=active.seed_policy,
                    phase="candidate-staging",
                    last_completed_phase="preflight",
                )
            except (PrivateStateError, OSError):
                return self._blocked(
                    request,
                    "lifecycle-preparation-failed",
                    operation=active.operation,
                    candidate_digest=active.candidate_digest,
                    seed_policy=active.seed_policy,
                    phase="candidate-staging",
                    last_completed_phase="preflight",
                )
            try:
                self._admit_existing_seeds(
                    root_fd,
                    operation=active.operation,
                    seed_policy=active.seed_policy,
                )
            except _AdmissionFailure as failure:
                return self._admission_result(request, failure)
            targets = self._observe_domains_for_admission(
                root_fd,
                operation=active.operation,
                seed_policy=active.seed_policy,
            )
            container = self._observe_container(root_fd)
            raw_record, record_witness, record, record_kind = self._observe_record(request.target, root_fd)
            expected = base64.b64decode(active.expected_incomplete_record["bytes_base64"])
            expected_record = (
                raw_record == expected
                and record is not None
                and record_kind == "final"
                and record.state == "incomplete"
                and record.operation == "uninstall"
                and record.candidate_digest == active.candidate_digest
                and record.seed_policy == "preserve-only"
            )
            original_record = self._record_matches_original(active, raw_record, record_witness, record_kind)
            if raw_record is not None and not (expected_record or original_record):
                return self._blocked(
                    request,
                    "installation-record-state-inconsistent",
                    operation=active.operation,
                    candidate_digest=active.candidate_digest,
                    seed_policy=active.seed_policy,
                )
            return self._uninstall_plan_result(request, active.candidate_digest, targets, container, record)
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
        if active_store is None or receipt_store is None or stage_store is None:
            return self._blocked(request, "lifecycle-preparation-failed")
        if active.operation != "uninstall" or request.mode != "dry-run":
            try:
                self._admit_existing_seeds(
                    root_fd,
                    operation=active.operation,
                    seed_policy=active.seed_policy,
                )
            except _AdmissionFailure as failure:
                return self._admission_result(request, failure)
        initial_absent_paths: frozenset[str] | None = None
        try:
            if active.operation == "uninstall":
                initial_absent_paths = frozenset(
                    item.path
                    for item in self._observe_domains_for_admission(
                        root_fd,
                        operation=active.operation,
                        seed_policy=active.seed_policy,
                    )
                    if item.kind == "absent"
                )
            if active.state == "prepared":
                self._execute_phase(
                    "candidate-staging",
                    lambda: self._prepare_stage(stage_store, active, candidate, root_fd),
                )
            elif not self._execute_phase(
                "candidate-staging",
                lambda: self._validate_running_stage(stage_store, active, candidate, root_fd),
            ):
                return self._blocked(
                    request,
                    "stage-owner-mismatch",
                    operation=active.operation,
                    candidate_digest=active.candidate_digest,
                    seed_policy=active.seed_policy,
                    phase="candidate-staging",
                    last_completed_phase="preflight",
                )
        except PrivateStateForeignError:
            return self._blocked(
                request,
                "stage-owner-mismatch",
                operation=active.operation,
                candidate_digest=active.candidate_digest,
                seed_policy=active.seed_policy,
                phase="candidate-staging",
                last_completed_phase="preflight",
            )
        except (
            AtomicRenameUnavailable,
            FilesystemSafetyError,
            PrivateStateError,
            OSError,
            _InjectedFailure,
        ) as failure:
            return self._partial_failure_result(
                request, active, failure, root_fd, initial_absent_paths=initial_absent_paths
            )
        if active_witness is None:
            return self._blocked(request, "lifecycle-preparation-failed")
        return self._run_active(
            request,
            active,
            candidate,
            active_store,
            receipt_store,
            stage_store,
            root_fd,
            active_witness=active_witness,
        )

    @staticmethod
    def _request_admits_active(
        operation: str,
        seed_policy: str,
        active: ActiveState,
        *,
        force: bool | None,
    ) -> bool:
        """Classify a retry against the durable operation tuple, not raw flags alone."""

        if active.operation == operation:
            return seed_policy == active.seed_policy
        if (
            active.result_family == "install"
            and active.operation == "install"
            and active.seed_policy == "preserve-only"
        ):
            return operation == "update" and seed_policy == "preserve-only"
        if active.result_family == "legacy-migration" and active.operation == "install":
            return (operation == "update" and seed_policy == "preserve-only") or (
                operation == "install" and seed_policy == "create-if-absent" and force is True
            )
        if active.result_family == "update" and active.operation == "update":
            return (operation == "update" and seed_policy == "preserve-only") or (
                operation == "install" and seed_policy == "create-if-absent" and force is True
            )
        return False
