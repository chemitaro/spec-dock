"""Journaled replacement of SpecDock tooling, with identity-checked recovery."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import os
from pathlib import Path
import re
import shutil
import stat
from typing import TYPE_CHECKING
import uuid

from spec_dock.installation.journal import InstallationRecord, read_record, write_record
from spec_dock.installation.source import VerifiedBundle, assert_disjoint_source_target, verify_bundle_integrity
from spec_dock.installer import IGNORE_FILE, LEGACY_WORKBENCH_IGNORE, TOOL_DIRECTORIES, VERSION_FILE

if TYPE_CHECKING:
    from collections.abc import Callable

_MANAGED = (*TOOL_DIRECTORIES, VERSION_FILE, IGNORE_FILE)
_INIT_SCAFFOLD = ("spec-dock/workspace.json", "spec-dock/.workbench/README.md")
_OPERATION_ID = re.compile(r"[0-9a-f]{32}\Z")


def _record_paths(action: str) -> tuple[str, ...]:
    return (*_MANAGED, *_INIT_SCAFFOLD) if action == "init" else _MANAGED


def _digest_path(path: Path) -> str | None:
    if path.is_symlink():
        raise ValueError(f"installation path is a symlink: {path}")
    if not path.exists():
        return None
    digest = hashlib.sha256()
    if path.is_file():
        digest.update(b"file\0" + stat.S_IMODE(path.stat().st_mode).to_bytes(2, "big") + path.read_bytes())
        return digest.hexdigest()
    if not path.is_dir():
        raise ValueError(f"installation path is not a regular file or directory: {path}")
    digest.update(b"directory\0" + stat.S_IMODE(path.stat().st_mode).to_bytes(2, "big"))
    for child in sorted(path.rglob("*")):
        if child.is_symlink():
            raise ValueError(f"installation tree has a symlink: {child}")
        relative = child.relative_to(path).as_posix().encode()
        mode = stat.S_IMODE(child.stat().st_mode).to_bytes(2, "big")
        if child.is_file():
            digest.update(b"file\0" + relative + b"\0" + mode + child.read_bytes() + b"\0")
        elif child.is_dir():
            digest.update(b"directory\0" + relative + b"\0" + mode + b"\0")
        else:
            raise ValueError(f"installation tree has an unsupported entry: {child}")
    return digest.hexdigest()


def _guard_target(target: Path) -> None:
    if not target.is_absolute() or not target.is_dir() or any(path.is_symlink() for path in (target, *target.parents)):
        raise ValueError("installation target must be an existing absolute directory")
    for relative in (*_MANAGED, *_INIT_SCAFFOLD):
        candidate = target
        for part in Path(relative).parts:
            candidate = candidate / part
            if candidate.is_symlink():
                raise ValueError(f"installation target contains a symlink: {candidate}")


def _operation_area(target: Path, operation_id: str) -> Path:
    area = target / ".spec-dock-installations" / operation_id
    if area.is_symlink() or area.parent.is_symlink():
        raise ValueError("installation operation area is a symlink")
    return area


def _marker_identity(path: Path, *, temporary: Path | None = None) -> dict[str, int] | None:
    if path.parent.is_symlink():
        raise ValueError("installation recovery directory is a symlink")
    try:
        before = path.lstat()
    except FileNotFoundError:
        return None
    linked = temporary is not None and temporary.exists()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != (2 if linked else 1):
        raise ValueError("installation recovery ignore marker is not a regular single-link file")
    if (
        linked
        and temporary is not None
        and (
            temporary.is_symlink()
            or (temporary.stat().st_dev, temporary.stat().st_ino) != (before.st_dev, before.st_ino)
        )
    ):
        raise ValueError("installation recovery ignore marker has an unowned hardlink")
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise ValueError("this platform cannot safely inspect the installation recovery marker")
    descriptor = os.open(path, os.O_RDONLY | nofollow)
    try:
        current = os.fstat(descriptor)
        if (before.st_dev, before.st_ino) != (current.st_dev, current.st_ino) or current.st_nlink != before.st_nlink:
            raise ValueError("installation recovery ignore marker changed identity")
        if os.read(descriptor, 3) != b"*\n":
            raise ValueError("installation recovery ignore marker has unexpected content")
        after = path.lstat()
        if (after.st_dev, after.st_ino, after.st_nlink) != (current.st_dev, current.st_ino, current.st_nlink):
            raise ValueError("installation recovery ignore marker changed identity")
        return {"device": current.st_dev, "inode": current.st_ino}
    finally:
        os.close(descriptor)


def validate_recovery_marker(target: Path) -> None:
    """Reject unsafe shared recovery state even when this child was never prepared."""
    recovery = target / ".spec-dock-installations"
    identity = _marker_identity(recovery / ".gitignore")
    if identity is None and recovery.is_dir() and any(recovery.iterdir()):
        raise ValueError("unjournaled installation recovery bytes lack an ignore marker")


def verify_installation_marker(journal_root: Path, operation_id: str) -> None:
    record = read_record(journal_root, operation_id)
    _verify_marker(record, _operation_area(Path(record.target), operation_id))


def _verify_marker(record: InstallationRecord, area: Path, *, finish_link: bool = False) -> bool:
    if not record.marker_tracked:
        raise ValueError("installation recovery marker is not tracked by this journal")
    marker = area.parent / ".gitignore"
    temporary = area / "ignore-marker.tmp"
    identity = _marker_identity(marker, temporary=temporary if record.marker_publish is not None else None)
    expected = record.marker_before or record.marker_publish
    if identity is None:
        if record.marker_before is not None:
            raise ValueError("installation recovery ignore marker disappeared")
        return False
    if expected is None or identity != expected:
        raise ValueError("installation recovery ignore marker changed identity")
    if finish_link and temporary.exists():
        temporary.unlink()
        _sync_directory(area)
        if _marker_identity(marker) != expected:
            raise ValueError("installation recovery ignore marker changed identity")
    if finish_link:
        _sync_directory(area.parent)
    return True


def _publish_marker(journal_root: Path, record: InstallationRecord, area: Path) -> InstallationRecord:
    if _verify_marker(record, area, finish_link=True):
        return record
    temporary = area / "ignore-marker.tmp"
    descriptor = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(b"*\n")
            stream.flush()
            os.fsync(stream.fileno())
        _sync_directory(area)
        identity = {"device": temporary.stat().st_dev, "inode": temporary.stat().st_ino}
        record = replace(record, marker_publish=identity)
        write_record(journal_root, record)
        os.link(temporary, area.parent / ".gitignore", follow_symlinks=False)
        _sync_directory(area.parent)
        if not _verify_marker(record, area, finish_link=True):
            raise ValueError("installation recovery ignore marker publication failed")
        return record
    except BaseException:
        # The planned journal owns the temporary and a possibly published marker.
        raise


def _asset_path(bundle: VerifiedBundle, relative: str) -> Path:
    if relative == "spec-dock/.workbench/README.md":
        return bundle.root / "src/spec_dock/assets/spec_dock/templates/root/.workbench/README.md"
    if relative.startswith("spec-dock/"):
        return bundle.root / "src/spec_dock/assets/spec_dock" / relative.removeprefix("spec-dock/")
    return bundle.root / "src/spec_dock/assets/install_root" / relative


def _copy_entry(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination, symlinks=True)
    elif source.is_file():
        shutil.copy2(source, destination)
    else:
        raise ValueError(f"distribution entry missing: {source}")


def _sync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _fsync_stage(area: Path) -> None:
    stage = area / "stage"
    for path in sorted(stage.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        if path.is_file():
            with path.open("rb") as stream:
                os.fsync(stream.fileno())
        elif path.is_dir():
            _sync_directory(path)
    for directory in (stage, area, area.parent):
        if directory.is_dir():
            _sync_directory(directory)


def prepare_installation(
    target: Path,
    journal_root: Path,
    *,
    action: str,
    bundle: VerifiedBundle | None,
    installed_version: str | None = None,
    operation_id: str | None = None,
) -> InstallationRecord:
    """Stage and verify every replacement before publishing a recoverable journal."""
    if action not in ("init", "update", "uninstall") or (action == "uninstall") != (bundle is None):
        raise ValueError("installation action and bundle do not match")
    _guard_target(target)
    installed = (target / VERSION_FILE).exists()
    if action == "init" and installed:
        raise ValueError("SpecDock is already installed")
    if action == "init" and any((target / relative).exists() for relative in (*TOOL_DIRECTORIES, *_INIT_SCAFFOLD)):
        raise ValueError("installation init refuses existing tooling directories")
    if action == "update" and not installed:
        raise ValueError("SpecDock is not installed")
    if bundle is not None:
        assert_disjoint_source_target(bundle.root, target)
        verify_bundle_integrity(bundle)
    if not journal_root.is_absolute() or any(
        journal_root.resolve(strict=False).is_relative_to((target / relative).resolve(strict=False))
        for relative in TOOL_DIRECTORIES
    ):
        raise ValueError("journal must be outside replaced tooling")
    operation_id = uuid.uuid4().hex if operation_id is None else operation_id
    if not isinstance(operation_id, str) or _OPERATION_ID.fullmatch(operation_id) is None:
        raise ValueError("installation operation ID is invalid")
    area = _operation_area(target, operation_id)
    marker_before = _marker_identity(area.parent / ".gitignore")
    record = InstallationRecord(
        operation_id,
        action,
        str(target),
        None if bundle is None else bundle.source.commit,
        None if bundle is None else bundle.digest,
        "planned",
        (),
        {},
        {},
        marker_tracked=True,
        marker_before=marker_before,
    )
    write_record(journal_root, record, create=True)
    return _stage_preparation(journal_root, record, bundle, installed_version=installed_version)


def resume_preparation(journal_root: Path, operation_id: str, *, bundle: VerifiedBundle | None) -> InstallationRecord:
    """Complete a planned child without changing its fixed target or source."""
    record = read_record(journal_root, operation_id)
    if record.phase != "planned" or not record.marker_tracked:
        raise ValueError("installation child is not a recoverable planned preparation")
    if (record.action == "uninstall") != (bundle is None) or (
        bundle is not None and (record.source_commit != bundle.source.commit or record.source_digest != bundle.digest)
    ):
        raise ValueError("installation recovery bundle differs from planned source")
    target = Path(record.target)
    _guard_target(target)
    if bundle is not None:
        assert_disjoint_source_target(bundle.root, target)
        verify_bundle_integrity(bundle)
    return _stage_preparation(journal_root, record, bundle, recover=True)


def _stage_preparation(
    journal_root: Path,
    record: InstallationRecord,
    bundle: VerifiedBundle | None,
    *,
    installed_version: str | None = None,
    recover: bool = False,
) -> InstallationRecord:
    target = Path(record.target)
    action = record.action
    area = _operation_area(target, record.operation_id)
    if recover and area.exists():
        if not area.is_dir() or any(os.path.lexists(area / name) for name in ("backup", "displaced")):
            raise ValueError("planned installation area contains replacement evidence")
        _verify_marker(record, area, finish_link=True)
        area.rename(area.parent / f"{record.operation_id}.abandoned-{uuid.uuid4().hex}")
        _sync_directory(area.parent)
    area.mkdir(mode=0o700, parents=True, exist_ok=False)
    _sync_directory(area.parent)
    record = _publish_marker(journal_root, record, area)
    before: dict[str, str | None] = {}
    after: dict[str, str | None] = {}
    try:
        for relative in _record_paths(action):
            destination = target / relative
            before[relative] = _digest_path(destination)
            staged = area / "stage" / relative
            if action == "uninstall":
                # Consumer-specific ignore rules remain owned by the consumer.
                after[relative] = before[relative] if relative == IGNORE_FILE else None
            elif relative == VERSION_FILE:
                assert bundle is not None
                version = installed_version or bundle.source.version or bundle.source.commit
                if version is None:
                    raise ValueError("installation source has no version identity")
                staged.parent.mkdir(parents=True, exist_ok=True)
                staged.write_text(version + "\n", encoding="utf-8")
                after[relative] = _digest_path(staged)
            elif relative == IGNORE_FILE:
                if before[relative] is not None and destination.read_bytes() != LEGACY_WORKBENCH_IGNORE:
                    after[relative] = before[relative]
                else:
                    assert bundle is not None
                    _copy_entry(_asset_path(bundle, relative), staged)
                    after[relative] = _digest_path(staged)
            else:
                assert bundle is not None
                _copy_entry(_asset_path(bundle, relative), staged)
                after[relative] = _digest_path(staged)
        _fsync_stage(area)
        _verify_marker(record, area)
        record = replace(record, phase="staged", before_hashes=before, after_hashes=after)
        write_record(journal_root, record)
        return record
    except BaseException:
        # No managed path was touched; a failed staging area can be inspected or removed explicitly.
        raise


def _verify_record_paths(record: InstallationRecord) -> None:
    if record.phase == "planned":
        if (
            record.marker_tracked
            and not record.before_hashes
            and not record.after_hashes
            and not record.completed_roots
        ):
            return
        raise ValueError("installation planned journal has unexpected path state")
    paths = _record_paths(record.action)
    if set(record.before_hashes) != set(paths) or set(record.after_hashes) != set(paths):
        raise ValueError("installation journal path inventory differs from this engine")
    if len(set(record.completed_roots)) != len(record.completed_roots) or any(
        root not in paths for root in record.completed_roots
    ):
        raise ValueError("installation journal completed-root inventory is invalid")


def _replace_root(target: Path, area: Path, relative: str, before: str | None, after: str | None) -> None:
    destination = target / relative
    backup = area / "backup" / relative
    staged = area / "stage" / relative
    current = _digest_path(destination)
    if current == after and (after is not None or before is None):
        if before is not None and before != after and _digest_path(backup) != before:
            raise ValueError(f"installation backup does not match before state: {relative}")
        return
    if current == before and before is not None:
        backup.parent.mkdir(parents=True, exist_ok=True)
        if backup.exists() or backup.is_symlink():
            raise ValueError(f"unexpected preexisting installation backup: {relative}")
        destination.replace(backup)
        _sync_directory(destination.parent)
        _sync_directory(backup.parent)
    elif current is None and before is not None:
        if _digest_path(backup) != before:
            raise ValueError(f"installation backup does not match before state: {relative}")
    elif current is not None:
        raise ValueError(f"installation target changed after preparation: {relative}")
    if after is not None:
        if _digest_path(staged) != after:
            raise ValueError(f"installation stage does not match planned content: {relative}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        staged.replace(destination)
        _sync_directory(destination.parent)
        _sync_directory(staged.parent)
    if _digest_path(destination) != after:
        raise ValueError(f"installation replacement did not reach planned state: {relative}")


def apply_installation(
    journal_root: Path,
    operation_id: str,
    *,
    enter_maintenance: Callable[[InstallationRecord], None],
    after_root: Callable[[str], None] | None = None,
) -> InstallationRecord:
    """Apply or resume a pinned operation; caller owns writer locking and maintenance."""
    record = read_record(journal_root, operation_id)
    _verify_record_paths(record)
    if record.phase == "planned":
        raise ValueError("installation preparation must resume before apply")
    if record.phase in ("committed", "rolled-back"):
        raise ValueError("installation operation is already terminal")
    target = Path(record.target)
    _guard_target(target)
    area = _operation_area(target, operation_id)
    if not area.is_dir():
        raise ValueError("installation operation area is missing")
    _verify_marker(record, area)
    enter_maintenance(record)
    try:
        record = replace(record, phase="replacing", error=None)
        write_record(journal_root, record)
        for relative in _record_paths(record.action):
            if relative in record.completed_roots:
                if _digest_path(target / relative) != record.after_hashes[relative]:
                    raise ValueError(f"completed installation path changed: {relative}")
                continue
            _guard_target(target)
            _replace_root(target, area, relative, record.before_hashes[relative], record.after_hashes[relative])
            record = replace(record, completed_roots=(*record.completed_roots, relative))
            write_record(journal_root, record)
            if after_root is not None:
                after_root(relative)
        for relative in _record_paths(record.action):
            if _digest_path(target / relative) != record.after_hashes[relative]:
                raise ValueError(f"installed content verification failed: {relative}")
        _verify_marker(record, area)
        record = replace(record, phase="committed")
        write_record(journal_root, record)
        return record
    except Exception as error:
        record = replace(record, phase="recovery-required", error=str(error))
        write_record(journal_root, record)
        raise


def rollback_installation(
    journal_root: Path,
    operation_id: str,
    *,
    enter_maintenance: Callable[[InstallationRecord], None],
    allow_committed: bool = False,
) -> InstallationRecord:
    """Restore only untouched after-state paths, retaining both backups and displaced bytes."""
    record = preflight_rollback_installation(journal_root, operation_id, allow_committed=allow_committed)
    if record.phase == "rolled-back":
        return record
    target = Path(record.target)
    enter_maintenance(record)
    area = _operation_area(target, operation_id)
    if record.phase == "planned":
        if area.exists():
            if not area.is_dir() or any(os.path.lexists(area / name) for name in ("backup", "displaced")):
                raise ValueError("planned installation area contains replacement evidence")
            _verify_marker(record, area, finish_link=True)
            if _marker_identity(area.parent / ".gitignore") is None:
                area.rename(area.parent / f"{operation_id}.abandoned-{uuid.uuid4().hex}")
                _sync_directory(area.parent)
        if not area.exists():
            area.mkdir(mode=0o700, parents=True, exist_ok=False)
            _sync_directory(area.parent)
        record = _publish_marker(journal_root, record, area)
        record = replace(record, phase="rolled-back", error=None)
        write_record(journal_root, record)
        return record
    _verify_marker(record, area)
    for relative in reversed(_record_paths(record.action)):
        destination = target / relative
        backup = area / "backup" / relative
        current = _digest_path(destination)
        previous = record.before_hashes[relative]
        if current == previous:
            continue
        if current is not None:
            displaced = area / "displaced" / relative
            displaced.parent.mkdir(parents=True, exist_ok=True)
            if displaced.exists() or displaced.is_symlink():
                raise ValueError(f"installation rollback displaced path exists: {relative}")
            destination.replace(displaced)
            _sync_directory(destination.parent)
            _sync_directory(displaced.parent)
        if previous is not None:
            destination.parent.mkdir(parents=True, exist_ok=True)
            backup.replace(destination)
            _sync_directory(destination.parent)
            _sync_directory(backup.parent)
    _verify_marker(record, area)
    record = replace(record, phase="rolled-back", error=None)
    write_record(journal_root, record)
    return record


def preflight_rollback_installation(
    journal_root: Path, operation_id: str, *, allow_committed: bool = False
) -> InstallationRecord:
    """Check a child restore without changing the target; group rollback checks every child first."""
    record = read_record(journal_root, operation_id)
    _verify_record_paths(record)
    if record.phase == "rolled-back":
        return record
    if record.phase == "committed" and not allow_committed:
        raise ValueError("committed installation requires a separate maintenance recovery plan")
    target = Path(record.target)
    _guard_target(target)
    area = _operation_area(target, operation_id)
    if record.phase == "planned":
        if area.exists() and (
            not area.is_dir() or any(os.path.lexists(area / name) for name in ("backup", "displaced"))
        ):
            raise ValueError("planned installation area contains replacement evidence")
        _verify_marker(record, area)
        return record
    _verify_marker(record, area)
    for relative in _record_paths(record.action):
        current = _digest_path(target / relative)
        expected = record.after_hashes[relative]
        previous = record.before_hashes[relative]
        backup = area / "backup" / relative
        if current not in (expected, previous, None):
            raise ValueError(f"installation rollback refuses later changes: {relative}")
        if relative in record.completed_roots and expected is not None and current is None:
            raise ValueError(f"installation rollback refuses later deletion: {relative}")
        if current is None and previous is not None and _digest_path(backup) != previous:
            raise ValueError(f"installation rollback lacks before state: {relative}")
        if current == expected and previous != expected and previous is not None and _digest_path(backup) != previous:
            raise ValueError(f"installation rollback backup changed: {relative}")
    return record
