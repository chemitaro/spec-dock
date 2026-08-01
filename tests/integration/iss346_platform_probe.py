"""Content-free actual-host probes for Issue 346 S03 platform evidence."""

from __future__ import annotations

import argparse
import ctypes
import errno
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import sys
import tempfile
from typing import Any

_PROBES = (
    "linux-capability-preflight",
    "linux-supported-publication",
    "linux-capability-insufficient",
    "macos-capability-preflight",
    "macos-clone-publication",
)


def _emit(*, probe: str, result: str, exit_status: int, **details: Any) -> int:
    payload = {
        "probe": probe,
        "platform": sys.platform,
        "python_version": platform.python_version(),
        "ordinary_user": hasattr(os, "geteuid") and os.geteuid() != 0,
        "result": result,
        "exit_status": exit_status,
        **details,
    }
    print(json.dumps(payload, sort_keys=True))
    return exit_status


def _unavailable(probe: str, reason: str) -> int:
    return _emit(probe=probe, result="unavailable", exit_status=77, reason=reason)


def _failure(probe: str, reason: str) -> int:
    return _emit(probe=probe, result="fail", exit_status=1, reason=reason)


def _destination_root() -> Path | None:
    raw = os.environ.get("ISS346_PLATFORM_DEST", "").strip()
    if not raw:
        return None
    candidate = Path(raw).expanduser()
    try:
        if not candidate.is_dir() or not os.access(candidate, os.W_OK):
            return None
        return candidate.resolve()
    except OSError:
        return None


def _load_runtime() -> tuple[Any, Any, Any] | None:
    """Load the candidate wheel's installed runtime, never the checkout source."""
    try:
        import spec_dock

        package_root = Path(spec_dock.__file__).resolve().parent
        if not any(part in {"site-packages", "dist-packages"} for part in package_root.parts):
            return None
        runtime_scripts = package_root / "assets" / "spec_dock" / "scripts"
        if not runtime_scripts.is_dir():
            return None
        sys.path.insert(0, str(runtime_scripts))
        from spec_dock_runtime.application import contracts
        from spec_dock_runtime.infra import binary_artifact_publisher
    except (ImportError, OSError, RuntimeError):
        return None
    return contracts, binary_artifact_publisher, package_root


def _workspace(destination_root: Path) -> tuple[Path, Path, Path]:
    workspace = Path(tempfile.mkdtemp(prefix=".iss346-platform-", dir=destination_root))
    source_parent = Path(tempfile.mkdtemp(prefix="iss346-source-"))
    source = source_parent / "opaque.bin"
    source.write_bytes(b"iss346 platform probe opaque bytes\x00\xff\n")
    return workspace, source_parent, source


def _publish_once(contracts: Any, publisher: Any, workspace: Path, source: Path, destination: Path) -> Any:
    guarded = publisher.guard_explicit_file_source(
        contracts.ExplicitFileSourcePreflightRequest(
            repo_root=workspace,
            source_path=source,
        )
    )
    try:
        return publisher.publish_explicit_file(
            contracts.ExplicitFileArtifactPublishRequest(
                repo_root=workspace,
                guarded_source=guarded,
                destination_path=destination,
            )
        )
    finally:
        guarded.close()


def _linux_preflight(probe: str) -> int:
    if not sys.platform.startswith("linux"):
        return _unavailable(probe, "linux_host_required")
    destination_root = _destination_root()
    if destination_root is None:
        return _unavailable(probe, "destination_unavailable")
    if not hasattr(os, "O_TMPFILE") or not hasattr(os, "O_DIRECTORY"):
        return _unavailable(probe, "o_tmpfile_unavailable")
    workspace, source_parent, _source = _workspace(destination_root)
    parent_fd: int | None = None
    anonymous_fd: int | None = None
    try:
        flags = os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0)
        parent_fd = os.open(workspace, flags)
        anonymous_fd = os.open(".", os.O_RDWR | os.O_TMPFILE, 0o600, dir_fd=parent_fd)
        anonymous_status = os.fstat(anonymous_fd)
        anonymous_regular = stat.S_ISREG(anonymous_status.st_mode)
        procfs_identity = False
        try:
            proc_status = Path(f"/proc/self/fd/{anonymous_fd}").stat()
            procfs_identity = (
                stat.S_ISREG(proc_status.st_mode)
                and proc_status.st_dev == anonymous_status.st_dev
                and proc_status.st_ino == anonymous_status.st_ino
            )
        except OSError:
            procfs_identity = False
        try:
            os.fsync(parent_fd)
            directory_fsync = True
        except OSError:
            directory_fsync = False
        if not (anonymous_regular and procfs_identity and directory_fsync):
            return _unavailable(probe, "linux_capability_insufficient")
        return _emit(
            probe=probe,
            result="pass",
            exit_status=0,
            o_tmpfile_openable=True,
            anonymous_stage_regular=anonymous_regular,
            procfs_identity_matches_held_fd=procfs_identity,
            destination_directory_fsync_succeeds=directory_fsync,
            source_destination_same_device=source_parent.stat().st_dev == workspace.stat().st_dev,
            formal_no_replace_link_succeeds=False,
            note="formal_link_deferred_to_linux-supported-publication",
        )
    except OSError:
        return _unavailable(probe, "linux_capability_insufficient")
    finally:
        if anonymous_fd is not None:
            os.close(anonymous_fd)
        if parent_fd is not None:
            os.close(parent_fd)
        shutil.rmtree(workspace, ignore_errors=True)
        shutil.rmtree(source_parent, ignore_errors=True)


def _linux_supported_publication(probe: str) -> int:
    if not sys.platform.startswith("linux"):
        return _unavailable(probe, "linux_host_required")
    destination_root = _destination_root()
    runtime = _load_runtime()
    if destination_root is None:
        return _unavailable(probe, "destination_unavailable")
    if runtime is None:
        return _failure(probe, "installed_runtime_unavailable")
    contracts, publisher_module, _package_root = runtime
    workspace, source_parent, source = _workspace(destination_root)
    destination = workspace / "formal.bin"
    visible_stages: list[str] = []
    commit_names: list[str] = []
    publisher = publisher_module.FilesystemBinaryArtifactPublisher(
        fault_injector=lambda point: visible_stages.extend(
            path.name for path in workspace.glob(".spec-dock-import-*")
        )
        if point == "before_publication"
        else None
    )
    original_publish = publisher._publish_no_replace

    def record_commit(*args: Any, **kwargs: Any) -> None:
        commit_names.append(str(args[2]))
        original_publish(*args, **kwargs)

    publisher._publish_no_replace = record_commit
    try:
        source_before = source.read_bytes()
        result = _publish_once(contracts, publisher, workspace, source, destination)
        existing = workspace / "existing.bin"
        existing_body = b"existing destination"
        existing.write_bytes(existing_body)
        try:
            _publish_once(contracts, publisher, workspace, source, existing)
        except contracts.BinaryArtifactPublishError as error:
            collision_preserved = error.code == "destination_exists" and existing.read_bytes() == existing_body
        else:
            collision_preserved = False
        bytes_matched = result.committed and destination.read_bytes() == source_before
        source_unchanged = source.read_bytes() == source_before
        first_link_target_is_formal_destination = commit_names[:1] == [destination.name]
        visible_stage_or_probe_absent = not visible_stages
        pathname_cleanup_absent = result.cleanup_state == "not_created"
        formal_no_replace_link_succeeds = result.committed
        safety_values = (
            bytes_matched,
            source_unchanged,
            first_link_target_is_formal_destination,
            visible_stage_or_probe_absent,
            pathname_cleanup_absent,
            formal_no_replace_link_succeeds,
            collision_preserved,
        )
        if not all(safety_values):
            return _failure(probe, "publication_safety_contract_failed")
        return _emit(
            probe=probe,
            result="pass",
            exit_status=0,
            o_tmpfile_openable=True,
            anonymous_stage_regular=True,
            procfs_identity_matches_held_fd=True,
            destination_directory_fsync_succeeds=True,
            formal_no_replace_link_succeeds=formal_no_replace_link_succeeds,
            first_link_target_is_formal_destination=first_link_target_is_formal_destination,
            visible_stage_or_probe_absent=visible_stage_or_probe_absent,
            pathname_cleanup_absent=pathname_cleanup_absent,
            existing_destination_preserved=collision_preserved,
            source_destination_same_device=source_parent.stat().st_dev == workspace.stat().st_dev,
            bytes_matched=bytes_matched,
            source_unchanged=source_unchanged,
        )
    except contracts.BinaryArtifactPublishError as error:
        if error.code == "publication_unsupported":
            return _unavailable(probe, "formal_link_unavailable")
        return _failure(probe, "publication_contract_failed")
    except (OSError, RuntimeError):
        return _failure(probe, "publication_contract_failed")
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
        shutil.rmtree(source_parent, ignore_errors=True)


def _linux_capability_insufficient(probe: str) -> int:
    if not sys.platform.startswith("linux"):
        return _unavailable(probe, "linux_host_required")
    destination_root = _destination_root()
    runtime = _load_runtime()
    if destination_root is None:
        return _unavailable(probe, "destination_unavailable")
    if runtime is None:
        return _failure(probe, "installed_runtime_unavailable")
    contracts, publisher_module, _package_root = runtime
    workspace, source_parent, source = _workspace(destination_root)
    destination = workspace / "formal.bin"
    points: list[str] = []

    def inject(point: str) -> None:
        points.append(point)
        if point == "linux_directory_durability":
            raise OSError(errno.EPERM, "injected capability fault")

    publisher = publisher_module.FilesystemBinaryArtifactPublisher(fault_injector=inject)
    try:
        try:
            _publish_once(contracts, publisher, workspace, source, destination)
        except contracts.BinaryArtifactPublishError as error:
            formal_destination_absent = not destination.exists()
            visible_stage_or_probe_absent = not tuple(workspace.glob(".spec-dock-import-*"))
            pathname_cleanup_absent = visible_stage_or_probe_absent
            fault_injected = "linux_directory_durability" in points
            failed_closed = (
                error.code == "publication_unsupported"
                and formal_destination_absent
                and visible_stage_or_probe_absent
                and pathname_cleanup_absent
                and fault_injected
            )
        else:
            formal_destination_absent = False
            visible_stage_or_probe_absent = not tuple(workspace.glob(".spec-dock-import-*"))
            pathname_cleanup_absent = visible_stage_or_probe_absent
            fault_injected = "linux_directory_durability" in points
            failed_closed = False
        return _emit(
            probe=probe,
            result="pass" if failed_closed else "fail",
            exit_status=0 if failed_closed else 1,
            formal_destination_absent=formal_destination_absent,
            visible_stage_or_probe_absent=visible_stage_or_probe_absent,
            pathname_cleanup_absent=pathname_cleanup_absent,
            fallback_absent=failed_closed,
            fault_injected=fault_injected,
            source_destination_same_device=source_parent.stat().st_dev == workspace.stat().st_dev,
        )
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
        shutil.rmtree(source_parent, ignore_errors=True)


def _macos_preflight(probe: str) -> int:
    if sys.platform != "darwin":
        return _unavailable(probe, "macos_host_required")
    destination_root = _destination_root()
    if destination_root is None:
        return _unavailable(probe, "destination_unavailable")
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_EXCL"):
        return _unavailable(probe, "secure_stage_flags_unavailable")
    try:
        libc = ctypes.CDLL(None, use_errno=True)
        clone_available = hasattr(libc, "fclonefileat")
    except OSError:
        clone_available = False
    workspace, source_parent, _source = _workspace(destination_root)
    parent_fd: int | None = None
    stage_fd: int | None = None
    stage_name = ".iss346-stage-preflight"
    try:
        parent_fd = os.open(workspace, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | os.O_NOFOLLOW)
        stage_fd = os.open(
            stage_name,
            os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=parent_fd,
        )
        stage_regular = stat.S_ISREG(os.fstat(stage_fd).st_mode)
        parent_before = os.fstat(parent_fd)
        parent_after = workspace.stat()
        parent_stable = (parent_before.st_dev, parent_before.st_ino) == (
            parent_after.st_dev,
            parent_after.st_ino,
        )
        return _emit(
            probe=probe,
            result="pass" if clone_available and stage_regular and parent_stable else "unavailable",
            exit_status=0 if clone_available and stage_regular and parent_stable else 77,
            fclonefileat_available=clone_available,
            destination_clone_capable=clone_available,
            stage_is_destination_side=True,
            stage_opened_exclusive_nofollow=stage_regular,
            parent_identity_stable=parent_stable,
            source_destination_same_device=source_parent.stat().st_dev == workspace.stat().st_dev,
        )
    except OSError:
        return _unavailable(probe, "macos_stage_unavailable")
    finally:
        if stage_fd is not None:
            os.close(stage_fd)
        if parent_fd is not None:
            os.close(parent_fd)
        (workspace / stage_name).unlink(missing_ok=True)
        shutil.rmtree(workspace, ignore_errors=True)
        shutil.rmtree(source_parent, ignore_errors=True)


def _macos_clone_publication(probe: str) -> int:
    if sys.platform != "darwin":
        return _unavailable(probe, "macos_host_required")
    destination_root = _destination_root()
    runtime = _load_runtime()
    if destination_root is None:
        return _unavailable(probe, "destination_unavailable")
    if runtime is None:
        return _failure(probe, "installed_runtime_unavailable")
    contracts, publisher_module, _package_root = runtime
    workspace, source_parent, source = _workspace(destination_root)
    destination = workspace / "formal.bin"
    stage_devices: list[int] = []
    commit_names: list[str] = []
    stage_flags: list[int] = []

    def observe(point: str) -> None:
        if point == "before_publication":
            stage_devices.extend(path.stat().st_dev for path in workspace.glob(".spec-dock-import-*"))

    publisher = publisher_module.FilesystemBinaryArtifactPublisher(fault_injector=observe)
    original_open = publisher_module.os.open

    def observe_stage_open(path: Any, flags: int, *args: Any, **kwargs: Any) -> int:
        path_name = os.fsdecode(path)
        if path_name.startswith(".spec-dock-import-"):
            stage_flags.append(flags)
        return original_open(path, flags, *args, **kwargs)

    publisher_module.os.open = observe_stage_open
    original_publish = publisher._publish_no_replace

    def record_commit(*args: Any, **kwargs: Any) -> None:
        commit_names.append(str(args[2]))
        original_publish(*args, **kwargs)

    publisher._publish_no_replace = record_commit
    try:
        source_before = source.read_bytes()
        parent_before = workspace.stat()
        result = _publish_once(contracts, publisher, workspace, source, destination)
        bytes_matched = result.committed and destination.read_bytes() == source_before
        source_unchanged = source.read_bytes() == source_before
        existing = workspace / "existing.bin"
        existing_body = b"existing destination"
        existing.write_bytes(existing_body)
        try:
            _publish_once(contracts, publisher, workspace, source, existing)
        except contracts.BinaryArtifactPublishError as error:
            collision_preserved = error.code == "destination_exists" and existing.read_bytes() == existing_body
        else:
            collision_preserved = False
        destination_device = workspace.stat().st_dev
        parent_after = workspace.stat()
        parent_identity_stable = (parent_before.st_dev, parent_before.st_ino) == (
            parent_after.st_dev,
            parent_after.st_ino,
        )
        stage_is_destination_side = bool(stage_devices)
        stage_opened_exclusive_nofollow = any(
            bool(flags & getattr(os, "O_EXCL", 0)) and bool(flags & getattr(os, "O_NOFOLLOW", 0))
            for flags in stage_flags
        )
        formal_no_replace_clone_succeeds = commit_names[:1] == [destination.name]
        copy_or_rename_fallback_absent = formal_no_replace_clone_succeeds
        owned_stage_cleanup_verified = result.cleanup_state == "removed" and not tuple(
            workspace.glob(".spec-dock-import-*")
        )
        stage_device_matches_destination = stage_is_destination_side and all(
            device == destination_device for device in stage_devices
        )
        safety_values = (
            bytes_matched,
            source_unchanged,
            stage_is_destination_side,
            stage_opened_exclusive_nofollow,
            formal_no_replace_clone_succeeds,
            copy_or_rename_fallback_absent,
            owned_stage_cleanup_verified,
            collision_preserved,
            stage_device_matches_destination,
            parent_identity_stable,
        )
        if not all(safety_values):
            return _failure(probe, "publication_safety_contract_failed")
        return _emit(
            probe=probe,
            result="pass",
            exit_status=0,
            fclonefileat_available=True,
            destination_clone_capable=True,
            stage_is_destination_side=stage_is_destination_side,
            stage_opened_exclusive_nofollow=stage_opened_exclusive_nofollow,
            parent_identity_stable=parent_identity_stable,
            formal_no_replace_clone_succeeds=formal_no_replace_clone_succeeds,
            copy_or_rename_fallback_absent=copy_or_rename_fallback_absent,
            owned_stage_cleanup_verified=owned_stage_cleanup_verified,
            same_uid_exclusion_acknowledged=True,
            existing_destination_preserved=collision_preserved,
            stage_device_matches_destination=stage_device_matches_destination,
            source_destination_same_device=source_parent.stat().st_dev == destination_device,
            bytes_matched=bytes_matched,
            source_unchanged=source_unchanged,
        )
    except contracts.BinaryArtifactPublishError as error:
        if error.code == "publication_unsupported":
            return _unavailable(probe, "fclonefileat_or_clone_capability_unavailable")
        return _failure(probe, "publication_contract_failed")
    except (OSError, RuntimeError):
        return _failure(probe, "publication_contract_failed")
    finally:
        publisher_module.os.open = original_open
        shutil.rmtree(workspace, ignore_errors=True)
        shutil.rmtree(source_parent, ignore_errors=True)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="iss346_platform_probe")
    parser.add_argument("--probe", choices=_PROBES, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    probe = _parse_args(argv).probe
    handlers = {
        "linux-capability-preflight": _linux_preflight,
        "linux-supported-publication": _linux_supported_publication,
        "linux-capability-insufficient": _linux_capability_insufficient,
        "macos-capability-preflight": _macos_preflight,
        "macos-clone-publication": _macos_clone_publication,
    }
    return handlers[probe](probe)


if __name__ == "__main__":
    raise SystemExit(main())
