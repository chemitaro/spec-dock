"""Journaled replacement of SpecDock tooling, with identity-checked recovery."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import os
from pathlib import Path
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
    for relative in _MANAGED:
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


def _asset_path(bundle: VerifiedBundle, relative: str) -> Path:
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
) -> InstallationRecord:
    """Stage and verify every replacement before publishing a recoverable journal."""
    if action not in ("init", "update", "uninstall") or (action == "uninstall") != (bundle is None):
        raise ValueError("installation action and bundle do not match")
    _guard_target(target)
    installed = (target / VERSION_FILE).exists()
    if action == "init" and installed:
        raise ValueError("SpecDock is already installed")
    if action == "init" and any((target / relative).exists() for relative in TOOL_DIRECTORIES):
        raise ValueError("installation init refuses existing tooling directories")
    if action == "update" and not installed:
        raise ValueError("SpecDock is not installed")
    if bundle is not None:
        assert_disjoint_source_target(bundle.root, target)
        verify_bundle_integrity(bundle)
    if not journal_root.is_absolute() or journal_root.is_relative_to(target / "spec-dock"):
        raise ValueError("journal must be outside replaced tooling")
    operation_id = uuid.uuid4().hex
    area = _operation_area(target, operation_id)
    area.mkdir(mode=0o700, parents=True, exist_ok=False)
    before: dict[str, str | None] = {}
    after: dict[str, str | None] = {}
    try:
        for relative in _MANAGED:
            destination = target / relative
            before[relative] = _digest_path(destination)
            staged = area / "stage" / relative
            if action == "uninstall":
                # Consumer-specific ignore rules remain owned by the consumer.
                after[relative] = before[relative] if relative == IGNORE_FILE else None
            elif relative == VERSION_FILE:
                assert bundle is not None
                staged.parent.mkdir(parents=True, exist_ok=True)
                staged.write_text(
                    (installed_version or bundle.source.version or bundle.source.commit) + "\n", encoding="utf-8"
                )
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
        record = InstallationRecord(
            operation_id,
            action,
            str(target),
            None if bundle is None else bundle.source.commit,
            None if bundle is None else bundle.digest,
            "staged",
            (),
            before,
            after,
        )
        write_record(journal_root, record, create=True)
        return record
    except BaseException:
        # No managed path was touched; a failed staging area can be inspected or removed explicitly.
        raise


def _verify_record_paths(record: InstallationRecord) -> None:
    if set(record.before_hashes) != set(_MANAGED) or set(record.after_hashes) != set(_MANAGED):
        raise ValueError("installation journal path inventory differs from this engine")
    if len(set(record.completed_roots)) != len(record.completed_roots) or any(
        root not in _MANAGED for root in record.completed_roots
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
    if record.phase in ("committed", "rolled-back"):
        raise ValueError("installation operation is already terminal")
    target = Path(record.target)
    _guard_target(target)
    area = _operation_area(target, operation_id)
    if not area.is_dir():
        raise ValueError("installation operation area is missing")
    enter_maintenance(record)
    try:
        record = replace(record, phase="replacing", error=None)
        write_record(journal_root, record)
        for relative in _MANAGED:
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
        for relative in _MANAGED:
            if _digest_path(target / relative) != record.after_hashes[relative]:
                raise ValueError(f"installed content verification failed: {relative}")
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
) -> InstallationRecord:
    """Restore only untouched after-state paths, retaining both backups and displaced bytes."""
    record = read_record(journal_root, operation_id)
    _verify_record_paths(record)
    if record.phase == "rolled-back":
        return record
    if record.phase == "committed":
        raise ValueError("committed installation requires a separate maintenance recovery plan")
    target = Path(record.target)
    _guard_target(target)
    enter_maintenance(record)
    area = _operation_area(target, operation_id)
    for relative in _MANAGED:
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
    for relative in reversed(_MANAGED):
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
    record = replace(record, phase="rolled-back", error=None)
    write_record(journal_root, record)
    return record
