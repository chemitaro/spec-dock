"""Journaled replacement of SpecDock tooling, with identity-checked recovery."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
from typing import TYPE_CHECKING
import uuid

from spec_dock.asset_layout import IGNORE_FILE, LEGACY_WORKBENCH_IGNORE, TOOL_DIRECTORIES, VERSION_FILE
from spec_dock.installation.journal import InstallationRecord, read_record, write_record
from spec_dock.installation.source import VerifiedBundle, assert_disjoint_source_target, verify_bundle_integrity

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

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


def _path_identity(path: Path) -> str | None:
    try:
        path.lstat()
    except FileNotFoundError:
        return None
    digest = hashlib.sha256()
    entries = (path, *sorted(path.rglob("*"))) if path.is_dir() and not path.is_symlink() else (path,)
    for entry in entries:
        observed = entry.lstat()
        kind = "directory" if stat.S_ISDIR(observed.st_mode) else "file"
        if not (stat.S_ISDIR(observed.st_mode) or stat.S_ISREG(observed.st_mode)):
            raise ValueError(f"installation path has an unsupported entry: {entry}")
        if kind == "file" and observed.st_nlink != 1:
            raise ValueError(f"installation path has an unowned hardlink: {entry}")
        identity = (
            entry.relative_to(path).as_posix(),
            kind,
            stat.S_IMODE(observed.st_mode),
            observed.st_dev,
            observed.st_ino,
            observed.st_nlink,
            observed.st_size,
        )
        digest.update(json.dumps(identity, separators=(",", ":")).encode() + b"\n")
    return digest.hexdigest()


def _observed_path_state(path: Path) -> tuple[str | None, str | None]:
    """Read content only while the entry graph remains the same."""
    identity = _path_identity(path)
    content = _digest_path(path)
    if _path_identity(path) != identity or (identity is None) != (content is None):
        raise ValueError(f"installation path changed during observation: {path}")
    return identity, content


def _planned_snapshot(target: Path, action: str) -> tuple[dict[str, str | None], dict[str, str | None]]:
    hashes: dict[str, str | None] = {}
    identities: dict[str, str | None] = {}
    for relative in _record_paths(action):
        path = target / relative
        identity = _path_identity(path)
        digest = _digest_path(path)
        if _path_identity(path) != identity or (identity is None) != (digest is None):
            raise ValueError(f"installation target changed during planning: {relative}")
        hashes[relative] = digest
        identities[relative] = identity
    for relative in hashes:
        path = target / relative
        if _path_identity(path) != identities[relative] or _digest_path(path) != hashes[relative]:
            raise ValueError(f"installation target changed during planning: {relative}")
    return hashes, identities


def _verify_planned_before(record: InstallationRecord) -> None:
    paths = _record_paths(record.action)
    if (
        record.identity_schema != 2
        or record.before_identities is None
        or set(record.before_hashes) != set(paths)
        or set(record.before_identities) != set(paths)
    ):
        raise ValueError("planned installation lacks a fixed target snapshot; forward resume is unsafe")
    target = Path(record.target)
    for relative in paths:
        path = target / relative
        if (
            _path_identity(path) != record.before_identities[relative]
            or _digest_path(path) != record.before_hashes[relative]
        ):
            raise ValueError(f"installation target changed after planning: {relative}")


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


@contextmanager
def _operation_entry(area: Path, relative: str, *, create_parents: bool = False) -> Iterator[tuple[int, str]]:
    """Bind an operation entry to a no-follow parent directory descriptor."""
    nofollow = getattr(os, "O_NOFOLLOW", None)
    directory = getattr(os, "O_DIRECTORY", None)
    if nofollow is None or directory is None or not area.is_absolute():
        raise ValueError("this platform cannot safely access installation operation paths")
    parts = Path(relative).parts
    if not parts or Path(relative).is_absolute() or any(part in ("", ".", "..") for part in parts):
        raise ValueError("installation operation path is invalid")
    descriptor = os.open("/", os.O_RDONLY | directory)
    try:
        area_parts = area.parts[1:]
        for index, part in enumerate((*area_parts, *parts[:-1])):
            if index >= len(area_parts) and create_parents:
                try:
                    os.mkdir(part, mode=0o700, dir_fd=descriptor)
                    os.fsync(descriptor)
                except FileExistsError:
                    pass
            try:
                child = os.open(part, os.O_RDONLY | directory | nofollow, dir_fd=descriptor)
            except OSError as error:
                try:
                    observed = os.stat(part, dir_fd=descriptor, follow_symlinks=False)
                except FileNotFoundError:
                    raise error from None
                if stat.S_ISLNK(observed.st_mode):
                    raise ValueError(f"installation operation path is a symlink: {area / relative}") from error
                raise
            os.close(descriptor)
            descriptor = child
        yield descriptor, parts[-1]
    finally:
        os.close(descriptor)


def _entry_snapshot(parent: int, name: str) -> tuple[str, str] | None:
    """Compute the journal's identity and content hashes without resolving path ancestors."""
    entries: list[tuple[str, os.stat_result, bytes | None]] = []

    def visit(directory: int, child_name: str, relative: str) -> None:
        before = os.stat(child_name, dir_fd=directory, follow_symlinks=False)
        if stat.S_ISDIR(before.st_mode):
            kind = "directory"
            flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        elif stat.S_ISREG(before.st_mode):
            kind = "file"
            flags = os.O_RDONLY | os.O_NOFOLLOW
        else:
            raise ValueError(f"installation operation path has an unsupported entry: {relative}")
        descriptor = os.open(child_name, flags, dir_fd=directory)
        try:
            observed = os.fstat(descriptor)
            if (before.st_dev, before.st_ino, before.st_mode) != (
                observed.st_dev,
                observed.st_ino,
                observed.st_mode,
            ):
                raise ValueError(f"installation operation path changed identity: {relative}")
            if kind == "file" and observed.st_nlink != 1:
                raise ValueError(f"installation operation path has an unowned hardlink: {relative}")
            content: bytes | None = None
            if kind == "file":
                chunks = []
                while chunk := os.read(descriptor, 1024 * 1024):
                    chunks.append(chunk)
                content = b"".join(chunks)
            entries.append((relative, observed, content))
            if kind == "directory":
                for child in sorted(item.name for item in os.scandir(descriptor)):
                    visit(descriptor, child, child if relative == "." else f"{relative}/{child}")
            after = os.stat(child_name, dir_fd=directory, follow_symlinks=False)
            current = os.fstat(descriptor)
            if (
                before.st_dev,
                before.st_ino,
                before.st_mode,
                before.st_size,
            ) != (
                after.st_dev,
                after.st_ino,
                after.st_mode,
                after.st_size,
            ) or (
                observed.st_dev,
                observed.st_ino,
                observed.st_mode,
                observed.st_size,
            ) != (
                current.st_dev,
                current.st_ino,
                current.st_mode,
                current.st_size,
            ):
                raise ValueError(f"installation operation path changed during observation: {relative}")
        finally:
            os.close(descriptor)

    try:
        visit(parent, name, ".")
    except FileNotFoundError as error:
        if not entries:
            return None
        raise ValueError(f"installation operation path changed during observation: {name}") from error
    entries.sort(key=lambda entry: entry[0])
    identity = hashlib.sha256()
    content = hashlib.sha256()
    root_mode = stat.S_IMODE(entries[0][1].st_mode).to_bytes(2, "big")
    if entries[0][2] is None:
        content.update(b"directory\0" + root_mode)
    else:
        content.update(b"file\0" + root_mode + entries[0][2])
    for relative, observed, data in entries:
        kind = "directory" if data is None else "file"
        mode = stat.S_IMODE(observed.st_mode)
        identity.update(
            json.dumps(
                (relative, kind, mode, observed.st_dev, observed.st_ino, observed.st_nlink, observed.st_size),
                separators=(",", ":"),
            ).encode()
            + b"\n"
        )
        if relative == ".":
            continue
        relative_bytes = relative.encode()
        mode_bytes = mode.to_bytes(2, "big")
        if data is None:
            content.update(b"directory\0" + relative_bytes + b"\0" + mode_bytes + b"\0")
        else:
            content.update(b"file\0" + relative_bytes + b"\0" + mode_bytes + data + b"\0")
    return identity.hexdigest(), content.hexdigest()


def _operation_observed_state(area: Path, relative: str) -> tuple[str | None, str | None]:
    try:
        with _operation_entry(area, relative) as (parent, name):
            first = _entry_snapshot(parent, name)
            second = _entry_snapshot(parent, name)
            if first != second:
                raise ValueError(f"installation operation path changed during observation: {relative}")
            return first if first is not None else (None, None)
    except FileNotFoundError:
        return None, None


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


def _copy_entry(source: Path, parent: int, name: str) -> None:
    """Copy one verified source entry beneath an already bound stage directory."""
    observed = source.lstat()
    mode = stat.S_IMODE(observed.st_mode)
    if stat.S_ISDIR(observed.st_mode):
        os.mkdir(name, mode=0o700, dir_fd=parent)
        directory = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
        try:
            for child in sorted(source.iterdir()):
                _copy_entry(child, directory, child.name)
            os.fchmod(directory, mode)
            os.fsync(directory)
        finally:
            os.close(directory)
    elif stat.S_ISREG(observed.st_mode):
        descriptor = os.open(name, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600, dir_fd=parent)
        with os.fdopen(descriptor, "wb") as destination, source.open("rb") as origin:
            shutil.copyfileobj(origin, destination)
            destination.flush()
            os.fchmod(destination.fileno(), mode)
            os.fsync(destination.fileno())
    else:
        raise ValueError(f"distribution entry is not a regular file or directory: {source}")
    os.fsync(parent)


def _sync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _fsync_stage(area: Path) -> None:
    def sync_tree(directory: int) -> None:
        for child in os.scandir(directory):
            observed = os.stat(child.name, dir_fd=directory, follow_symlinks=False)
            if stat.S_ISDIR(observed.st_mode):
                descriptor = os.open(child.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
                try:
                    sync_tree(descriptor)
                finally:
                    os.close(descriptor)
            elif stat.S_ISREG(observed.st_mode):
                descriptor = os.open(child.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
                try:
                    os.fsync(descriptor)
                finally:
                    os.close(descriptor)
            else:
                raise ValueError(f"installation stage contains an unsupported entry: {child.name}")
        os.fsync(directory)

    with _operation_entry(area, "stage") as (area_descriptor, stage_name):
        try:
            stage_descriptor = os.open(stage_name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=area_descriptor)
        except FileNotFoundError:
            pass
        else:
            try:
                sync_tree(stage_descriptor)
            finally:
                os.close(stage_descriptor)
        os.fsync(area_descriptor)
    _sync_directory(area.parent)


def prepare_installation(
    target: Path,
    journal_root: Path,
    *,
    action: str,
    bundle: VerifiedBundle | None,
    installed_version: str | None = None,
    operation_id: str | None = None,
    version_tracked: bool = False,
) -> InstallationRecord:
    """Stage and verify every replacement before publishing a recoverable journal."""
    if action not in ("init", "update", "uninstall") or (action == "uninstall") != (bundle is None):
        raise ValueError("installation action and bundle do not match")
    if version_tracked and action != "update":
        raise ValueError("only installation update tracks the source version")
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
    before_hashes, before_identities = _planned_snapshot(target, action)
    record = InstallationRecord(
        operation_id,
        action,
        str(target),
        None if bundle is None else bundle.source.commit,
        None if bundle is None else bundle.digest,
        "planned",
        (),
        before_hashes,
        {},
        marker_tracked=True,
        marker_before=marker_before,
        before_identities=before_identities,
        requested_version=installed_version,
        identity_schema=2,
        version_tracked=version_tracked,
    )
    write_record(journal_root, record, create=True)
    return _stage_preparation(journal_root, record, bundle)


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
    _verify_planned_before(record)
    return _stage_preparation(journal_root, record, bundle, recover=True)


def _stage_preparation(
    journal_root: Path,
    record: InstallationRecord,
    bundle: VerifiedBundle | None,
    *,
    recover: bool = False,
) -> InstallationRecord:
    target = Path(record.target)
    action = record.action
    area = _operation_area(target, record.operation_id)
    _verify_planned_before(record)
    if recover and area.exists():
        if not area.is_dir() or any(os.path.lexists(area / name) for name in ("backup", "displaced")):
            raise ValueError("planned installation area contains replacement evidence")
        _verify_marker(record, area, finish_link=True)
        area.rename(area.parent / f"{record.operation_id}.abandoned-{uuid.uuid4().hex}")
        _sync_directory(area.parent)
    area.mkdir(mode=0o700, parents=True, exist_ok=False)
    _sync_directory(area.parent)
    record = _publish_marker(journal_root, record, area)
    before = record.before_hashes
    assert record.before_identities is not None
    after: dict[str, str | None] = {}
    after_identities: dict[str, str | None] = {}
    try:
        for relative in _record_paths(action):
            destination = target / relative
            if action == "uninstall":
                # Consumer-specific ignore rules remain owned by the consumer.
                after[relative] = before[relative] if relative == IGNORE_FILE else None
            elif relative == VERSION_FILE:
                assert bundle is not None
                version = (
                    (record.requested_version if record.requested_version is not None else record.source_commit)
                    if record.version_tracked
                    else (record.requested_version or bundle.source.version or bundle.source.commit)
                )
                if version is None:
                    raise ValueError("installation source has no version identity")
                with _operation_entry(area, f"stage/{relative}", create_parents=True) as (
                    stage_parent,
                    stage_name,
                ):
                    descriptor = os.open(
                        stage_name,
                        os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW,
                        0o644,
                        dir_fd=stage_parent,
                    )
                    with os.fdopen(descriptor, "wb") as stream:
                        stream.write((version + "\n").encode())
                        stream.flush()
                        os.fsync(stream.fileno())
                    os.fsync(stage_parent)
                    staged = _entry_snapshot(stage_parent, stage_name)
                    assert staged is not None
                    after[relative] = staged[1]
            elif relative == IGNORE_FILE:
                if before[relative] is not None and destination.read_bytes() != LEGACY_WORKBENCH_IGNORE:
                    after[relative] = before[relative]
                else:
                    assert bundle is not None
                    with _operation_entry(area, f"stage/{relative}", create_parents=True) as (
                        stage_parent,
                        stage_name,
                    ):
                        _copy_entry(_asset_path(bundle, relative), stage_parent, stage_name)
                        staged = _entry_snapshot(stage_parent, stage_name)
                        assert staged is not None
                        after[relative] = staged[1]
            else:
                assert bundle is not None
                with _operation_entry(area, f"stage/{relative}", create_parents=True) as (
                    stage_parent,
                    stage_name,
                ):
                    _copy_entry(_asset_path(bundle, relative), stage_parent, stage_name)
                    staged = _entry_snapshot(stage_parent, stage_name)
                    assert staged is not None
                    after[relative] = staged[1]
        _fsync_stage(area)
        for relative in _record_paths(action):
            staged_identity, staged_content = _operation_observed_state(area, f"stage/{relative}")
            after_identities[relative] = (
                staged_identity
                if staged_identity is not None
                else record.before_identities[relative]
                if after[relative] is not None
                else None
            )
            if staged_identity is not None and staged_content != after[relative]:
                raise ValueError(f"installation stage changed during preparation: {relative}")
        _verify_marker(record, area)
        _verify_planned_before(record)
        record = replace(
            record, phase="staged", before_hashes=before, after_hashes=after, after_identities=after_identities
        )
        write_record(journal_root, record)
        return record
    except BaseException:
        # No managed path was touched; a failed staging area can be inspected or removed explicitly.
        raise


def _verify_record_paths(record: InstallationRecord) -> None:
    if record.phase == "planned":
        if (
            record.marker_tracked
            and not record.after_hashes
            and not record.completed_roots
            and (
                (not record.before_hashes and record.before_identities is None)
                or (
                    record.before_identities is not None
                    and set(record.before_hashes) == set(_record_paths(record.action))
                    and set(record.before_identities) == set(_record_paths(record.action))
                )
            )
        ):
            return
        raise ValueError("installation planned journal has unexpected path state")
    paths = _record_paths(record.action)
    if set(record.before_hashes) != set(paths) or set(record.after_hashes) != set(paths):
        raise ValueError("installation journal path inventory differs from this engine")
    if (
        record.identity_schema != 2
        or record.before_identities is None
        or record.after_identities is None
        or set(record.before_identities) != set(paths)
        or set(record.after_identities) != set(paths)
        or any((record.before_hashes[key] is None) != (record.before_identities[key] is None) for key in paths)
        or any((record.after_hashes[key] is None) != (record.after_identities[key] is None) for key in paths)
    ):
        raise ValueError("installation journal lacks fixed ownership evidence")
    if len(set(record.completed_roots)) != len(record.completed_roots) or any(
        root not in paths for root in record.completed_roots
    ):
        raise ValueError("installation journal completed-root inventory is invalid")


def _replace_root(
    target: Path,
    area: Path,
    relative: str,
    before: str | None,
    after: str | None,
    before_identity: str | None,
    after_identity: str | None,
) -> None:
    destination = target / relative
    current_identity = _path_identity(destination)
    current = _digest_path(destination)
    backup_identity, backup_content = _operation_observed_state(area, f"backup/{relative}")
    if backup_identity is not None and (backup_identity != before_identity or backup_content != before):
        raise ValueError(f"installation backup changed identity: {relative}")
    if before is None and backup_identity is not None:
        raise ValueError(f"unexpected installation backup: {relative}")
    if (
        current_identity == after_identity
        and current == after
        and (before_identity == after_identity or before is None or backup_identity == before_identity)
    ):
        return
    if after is not None and _operation_observed_state(area, f"stage/{relative}") != (
        after_identity,
        after,
    ):
        raise ValueError(f"installation stage changed identity: {relative}")
    if current_identity == before_identity and current == before and before is not None:
        with _operation_entry(area, f"backup/{relative}", create_parents=True) as (
            backup_parent,
            backup_name,
        ):
            if backup_identity is not None or _entry_snapshot(backup_parent, backup_name) is not None:
                raise ValueError(f"unexpected preexisting installation backup: {relative}")
            os.replace(destination, backup_name, dst_dir_fd=backup_parent)
            _sync_directory(destination.parent)
            os.fsync(backup_parent)
            if _entry_snapshot(backup_parent, backup_name) != (before_identity, before):
                raise ValueError(f"installation backup changed identity: {relative}")
    elif current_identity is None and before is not None:
        if backup_identity != before_identity:
            raise ValueError(f"installation backup does not match before state: {relative}")
    elif current_identity is not None:
        raise ValueError(f"installation target changed after preparation: {relative}")
    if after is not None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with _operation_entry(area, f"stage/{relative}") as (stage_parent, stage_name):
            if _entry_snapshot(stage_parent, stage_name) != (after_identity, after):
                raise ValueError(f"installation stage changed identity: {relative}")
            os.replace(stage_name, destination, src_dir_fd=stage_parent)
            _sync_directory(destination.parent)
            os.fsync(stage_parent)
    if _path_identity(destination) != after_identity or _digest_path(destination) != after:
        raise ValueError(f"installation replacement did not reach planned state: {relative}")


def _verify_published(record: InstallationRecord) -> None:
    _verify_record_paths(record)
    assert record.after_identities is not None
    for relative in _record_paths(record.action):
        path = Path(record.target) / relative
        if (
            _path_identity(path) != record.after_identities[relative]
            or _digest_path(path) != record.after_hashes[relative]
        ):
            raise ValueError(f"completed installation path changed identity: {relative}")


def verify_installation_after(journal_root: Path, operation_id: str) -> None:
    """Verify the committed child owns every published path, including nested entries."""
    record = read_record(journal_root, operation_id)
    if record.phase != "committed":
        raise ValueError("installation child is not committed")
    _guard_target(Path(record.target))
    _verify_marker(record, _operation_area(Path(record.target), operation_id))
    _verify_published(record)


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
    if record.phase == "staged":
        _verify_planned_before(record)
    assert record.before_identities is not None
    assert record.after_identities is not None
    for relative in record.completed_roots:
        assert record.after_identities is not None
        if (
            _path_identity(target / relative) != record.after_identities[relative]
            or _digest_path(target / relative) != record.after_hashes[relative]
        ):
            raise ValueError(f"completed installation path changed identity: {relative}")
    enter_maintenance(record)
    try:
        record = replace(record, phase="replacing", error=None)
        write_record(journal_root, record)
        for relative in _record_paths(record.action):
            if relative in record.completed_roots:
                continue
            _guard_target(target)
            _replace_root(
                target,
                area,
                relative,
                record.before_hashes[relative],
                record.after_hashes[relative],
                record.before_identities[relative] if record.before_identities is not None else None,
                record.after_identities[relative] if record.after_identities is not None else None,
            )
            record = replace(record, completed_roots=(*record.completed_roots, relative))
            write_record(journal_root, record)
            if after_root is not None:
                after_root(relative)
        _verify_published(record)
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
        assert record.before_identities is not None
        assert record.after_identities is not None
        previous = record.before_identities[relative]
        current = _observed_path_state(destination)
        before = (previous, record.before_hashes[relative])
        after = (record.after_identities[relative], record.after_hashes[relative])
        displaced_state = _operation_observed_state(area, f"displaced/{relative}")
        if displaced_state not in ((None, None), after):
            raise ValueError(f"installation rollback displaced path changed: {relative}")
        if current == before:
            continue
        if current not in (after, (None, None)):
            raise ValueError(f"installation rollback refuses later changes: {relative}")
        if previous is not None and _operation_observed_state(area, f"backup/{relative}") != before:
            raise ValueError(f"installation rollback backup or target changed: {relative}")
        if current[0] is not None:
            with _operation_entry(area, f"displaced/{relative}", create_parents=True) as (
                displaced_parent,
                displaced_name,
            ):
                if displaced_state != (None, None) or _entry_snapshot(displaced_parent, displaced_name) is not None:
                    raise ValueError(f"installation rollback displaced path exists: {relative}")
                if _observed_path_state(destination) != after:
                    raise ValueError(f"installation rollback refuses later changes: {relative}")
                os.replace(destination, displaced_name, dst_dir_fd=displaced_parent)
                _sync_directory(destination.parent)
                os.fsync(displaced_parent)
                if _entry_snapshot(displaced_parent, displaced_name) != after:
                    raise ValueError(f"installation rollback displaced path changed: {relative}")
        elif relative in record.completed_roots and after[0] is not None and displaced_state != after:
            raise ValueError(f"installation rollback refuses later deletion: {relative}")
        if previous is not None:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with _operation_entry(area, f"backup/{relative}") as (backup_parent, backup_name):
                if _entry_snapshot(backup_parent, backup_name) != before or _observed_path_state(destination) != (
                    None,
                    None,
                ):
                    raise ValueError(f"installation rollback backup or target changed: {relative}")
                os.replace(backup_name, destination, src_dir_fd=backup_parent)
                _sync_directory(destination.parent)
                os.fsync(backup_parent)
            if _observed_path_state(destination) != before:
                raise ValueError(f"installation rollback did not restore before identity: {relative}")
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
    if record.identity_schema != 2 and record.phase != "planned":
        raise ValueError("installation rollback lacks fixed ownership evidence")
    if record.phase != "planned":
        assert record.before_identities is not None
        assert record.after_identities is not None
    assert record.before_identities is not None
    assert record.after_identities is not None
    for relative in _record_paths(record.action):
        current_identity, current = _observed_path_state(target / relative)
        expected_identity = record.after_identities[relative]
        previous_identity = record.before_identities[relative]
        expected = record.after_hashes[relative]
        previous = record.before_hashes[relative]
        backup_identity, backup_content = _operation_observed_state(area, f"backup/{relative}")
        displaced_identity, displaced_content = _operation_observed_state(area, f"displaced/{relative}")
        if displaced_identity is not None and (
            displaced_identity != expected_identity or displaced_content != expected
        ):
            raise ValueError(f"installation rollback displaced path changed: {relative}")
        if backup_identity is not None and (backup_identity != previous_identity or backup_content != previous):
            raise ValueError(f"installation rollback backup changed identity: {relative}")
        if previous_identity is None and backup_identity is not None:
            raise ValueError(f"installation rollback has unexpected backup: {relative}")
        if current_identity == previous_identity and current == previous:
            continue
        if displaced_identity is not None and current_identity is not None:
            raise ValueError(f"installation rollback displaced path conflicts with target: {relative}")
        if current_identity not in (expected_identity, None) or (
            current_identity == expected_identity and current != expected
        ):
            raise ValueError(f"installation rollback refuses later changes: {relative}")
        if (
            relative in record.completed_roots
            and expected_identity is not None
            and current_identity is None
            and displaced_identity is None
        ):
            raise ValueError(f"installation rollback refuses later deletion: {relative}")
        if current_identity is None and previous_identity is not None and backup_identity != previous_identity:
            raise ValueError(f"installation rollback lacks before state: {relative}")
        if (
            current_identity == expected_identity
            and previous_identity != expected_identity
            and previous_identity is not None
            and backup_identity != previous_identity
        ):
            raise ValueError(f"installation rollback backup changed: {relative}")
    return record
