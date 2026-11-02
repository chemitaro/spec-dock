"""`migration_backup.create_verified_backup` on a whole checkout tree, without `workspace migrate` (iss-00440, G4).

The fail-closed checks that tests/integration/test_issue413_migration.py exercised through the removed
`workspace migrate` leaf (symlinks kept as links under another umask, copy and restore failures, an existing or
redirected destination, a backup or source changed after verification). `installation update` keeps using this
module with a captured tree of regular files.
"""

from __future__ import annotations

import os
from pathlib import Path
import stat

import pytest

from spec_dock.runtime.infra import migration_backup
from spec_dock.runtime.infra.migration_backup import BackupTree, MigrationBackupIncomplete, create_verified_backup
from spec_dock.runtime.infra.tree_backup import tree_digest

pytestmark = pytest.mark.skipif(os.name != "posix", reason="POSIX directory descriptors and symlink modes")


def checkout(tmp_path: Path) -> Path:
    root = tmp_path / "consumer"
    (root / "spec-dock").mkdir(parents=True)
    (root / "spec-dock/workspace.json").write_bytes(b'{"schema_version":4}\n')
    (root / "untracked-user-work.md").write_bytes(b"before backup\n")
    return root.resolve()


def sources(root: Path) -> tuple[BackupTree, ...]:
    return (BackupTree(root, Path("checkout"), tree_digest(root)),)


def unchanged() -> None:
    return None


def test_backup_preserves_a_symlink_itself_without_copying_its_target(tmp_path: Path) -> None:
    root = checkout(tmp_path)
    external = tmp_path / "outside"
    external.mkdir()
    (external / "private.txt").write_bytes(b"arbitrary external data must not be traversed")
    link = root / "untracked-link"
    link.symlink_to(external, target_is_directory=True)
    backup = tmp_path / "backup"
    verified = create_verified_backup(backup, sources(root), verify=unchanged)
    copied = backup / "checkout/untracked-link"
    assert copied.is_symlink() and copied.readlink() == link.readlink()
    assert not any(path.name == "private.txt" for path in backup.rglob("*"))
    assert (external / "private.txt").read_bytes() == b"arbitrary external data must not be traversed"
    assert tree_digest(backup / "checkout") == tree_digest(root)
    verified.verify()


def test_backup_preserves_symlink_permissions_under_a_different_creation_umask_without_touching_target(
    tmp_path: Path,
) -> None:
    root = checkout(tmp_path)
    external = tmp_path / "external.bin"
    external.write_bytes(b"outside target must stay untouched")
    external.chmod(0o640)
    link = root / "external-link"
    previous = os.umask(0)
    try:
        link.symlink_to("../external.bin")
    finally:
        os.umask(previous)
    assert stat.S_IMODE(link.lstat().st_mode) == 0o777
    backup = tmp_path / "backup"
    previous = os.umask(0o022)
    try:
        create_verified_backup(backup, sources(root), verify=unchanged)
    finally:
        os.umask(previous)
    preserved = backup / "checkout/external-link"
    assert preserved.is_symlink() and str(preserved.readlink()) == "../external.bin"
    assert stat.S_IMODE(preserved.lstat().st_mode) == 0o777
    assert stat.S_IMODE(link.lstat().st_mode) == 0o777
    assert external.read_bytes() == b"outside target must stay untouched"
    assert stat.S_IMODE(external.stat().st_mode) == 0o640


@pytest.mark.parametrize("failure", ["copy", "restore"])
def test_backup_or_restore_failure_is_incomplete_and_keeps_the_source_and_the_partial_backup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    root = checkout(tmp_path)
    before = tree_digest(root)
    backup = tmp_path / "backup"
    original = migration_backup.copy_tree_at
    copied: list[Path] = []

    def damage(descriptor: int, relative: Path, source: Path) -> None:
        copied.append(source)
        if failure == "copy":
            raise OSError("copy failed")
        original(descriptor, relative, source)
        if source == backup / "checkout":
            target = os.open(str(relative / "spec-dock/workspace.json"), os.O_WRONLY | os.O_TRUNC, dir_fd=descriptor)
            try:
                os.write(target, b"restore differs\n")
            finally:
                os.close(target)

    monkeypatch.setattr(migration_backup, "copy_tree_at", damage)
    with pytest.raises(MigrationBackupIncomplete) as raised:
        create_verified_backup(backup, sources(root), verify=unchanged)
    assert (raised.value.backup_verified, raised.value.restore_verified) == (False, False)
    assert tree_digest(root) == before
    assert backup.is_dir()  # retained for inspection, never removed or restored into the source
    if failure == "restore":
        assert backup / "checkout" in copied
        assert (backup / "checkout/spec-dock/workspace.json").read_bytes() == b'{"schema_version":4}\n'


@pytest.mark.parametrize("location", ["existing", "relative", "redirected-parent"])
def test_backup_refuses_an_unsafe_or_existing_destination_without_overwriting_it(tmp_path: Path, location: str) -> None:
    root = checkout(tmp_path)
    before = tree_digest(root)
    backup = tmp_path / "backup"
    if location == "existing":
        backup.mkdir()
        (backup / "user-owned.md").write_bytes(b"never overwrite\n")
    elif location == "relative":
        backup = Path("relative-backup")
    else:
        redirected = tmp_path / "redirect"
        redirected.symlink_to(tmp_path, target_is_directory=True)
        backup = redirected / "backup"
    verified: list[str] = []
    with pytest.raises((OSError, ValueError)) as raised:
        create_verified_backup(backup, sources(root), verify=lambda: verified.append("checked"))
    assert not isinstance(raised.value, MigrationBackupIncomplete)  # nothing was claimed
    assert tree_digest(root) == before
    if location == "existing":
        assert (backup / "user-owned.md").read_bytes() == b"never overwrite\n"
        assert sorted(path.name for path in backup.iterdir()) == ["user-owned.md"]
    else:
        assert not (tmp_path / "backup").exists() and not Path("relative-backup").exists()


def test_a_backup_changed_after_verification_is_detected_before_publication(tmp_path: Path) -> None:
    root = checkout(tmp_path)
    backup = tmp_path / "backup"
    verified = create_verified_backup(backup, sources(root), verify=unchanged)
    verified.verify()
    (backup / "checkout/spec-dock/workspace.json").write_bytes(b"backup replaced after verification\n")
    with pytest.raises(ValueError, match="verified backup content changed"):
        verified.verify()


def test_a_source_edit_during_backup_stops_it_and_leaves_the_edit_intact(tmp_path: Path) -> None:
    root = checkout(tmp_path)
    body = root / "untracked-user-work.md"
    backup = tmp_path / "backup"
    captured = sources(root)
    checks: list[str] = []

    def concurrent_edit() -> None:
        checks.append("checked")
        if len(checks) == 2:  # the re-check after the backup and its restore were verified
            body.write_bytes(b"concurrent user edit\n")
            if tree_digest(root) != captured[0].digest:
                raise ValueError("source changed during backup")

    with pytest.raises(MigrationBackupIncomplete) as raised:
        create_verified_backup(backup, captured, verify=concurrent_edit)
    assert (raised.value.backup_verified, raised.value.restore_verified) == (True, True)
    assert checks == ["checked", "checked"]
    assert body.read_bytes() == b"concurrent user edit\n"
    assert (backup / "checkout/untracked-user-work.md").read_bytes() == b"before backup\n"
