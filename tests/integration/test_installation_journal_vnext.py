"""Crash-safe record semantics for the external installer."""

from __future__ import annotations

from dataclasses import replace
import json
import os
import shutil
import subprocess
from typing import TYPE_CHECKING

import pytest

from spec_dock.installation.executor import (
    apply_installation,
    prepare_installation,
    resume_preparation,
    rollback_installation,
)
from spec_dock.installation.journal import InstallationRecord, read_record, write_record
from spec_dock.installation.source import PinnedSource, VerifiedBundle, _digest_paths, _tooling_inventory
from spec_dock.installer import TOOL_DIRECTORIES

if TYPE_CHECKING:
    from pathlib import Path


def _record(target: Path) -> InstallationRecord:
    return InstallationRecord(
        "a" * 32,
        "update",
        str(target),
        "b" * 40,
        "c" * 64,
        "planned",
        (),
        {"spec-dock/docs": "d" * 64},
        {"spec-dock/docs": "e" * 64},
    )


def test_installation_record_survives_phase_updates(tmp_path: Path) -> None:
    root = tmp_path / "common"
    original = _record(tmp_path / "target")
    write_record(root, original, create=True)
    assert read_record(root, original.operation_id) == original
    updated = replace(original, phase="replacing", completed_roots=("spec-dock/docs",))
    write_record(root, updated)
    assert read_record(root, updated.operation_id) == updated


def test_installation_record_rejects_symlink_and_corruption(tmp_path: Path) -> None:
    root = tmp_path / "common"
    original = _record(tmp_path / "target")
    write_record(root, original, create=True)
    path = root / "installations" / original.operation_id / "record.json"
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="shape"):
        read_record(root, original.operation_id)
    path.unlink()
    path.symlink_to(tmp_path / "elsewhere")
    with pytest.raises(ValueError, match="symlink"):
        read_record(root, original.operation_id)


def test_installation_record_rejects_invalid_digest_and_symlinked_directory(tmp_path: Path) -> None:
    root = tmp_path / "common"
    original = _record(tmp_path / "target")
    write_record(root, original, create=True)
    record_file = root / "installations" / original.operation_id / "record.json"
    payload = json.loads(record_file.read_text(encoding="utf-8"))
    payload["before_hashes"]["spec-dock/docs"] = "bad"
    record_file.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="hash"):
        read_record(root, original.operation_id)
    operation_dir = record_file.parent
    operation_dir.rename(root / "real-operation")
    operation_dir.symlink_to(root / "real-operation")
    with pytest.raises(ValueError, match="symlink"):
        read_record(root, original.operation_id)


def _bundle(tmp_path: Path) -> VerifiedBundle:
    root = tmp_path / "bundle"
    assets = root / "src/spec_dock/assets"
    for relative in TOOL_DIRECTORIES:
        source = (
            assets / "spec_dock" / relative.removeprefix("spec-dock/")
            if relative.startswith("spec-dock/")
            else assets / "install_root" / relative
        )
        source.mkdir(parents=True)
        (source / "source.txt").write_text(relative, encoding="utf-8")
    ignore = assets / "spec_dock/.gitignore"
    ignore.write_text(".agent/\n", encoding="utf-8")
    (assets / "spec_dock/workspace.json").write_text("{}\n", encoding="utf-8")
    readme = assets / "spec_dock/templates/root/.workbench/README.md"
    readme.parent.mkdir(parents=True)
    readme.write_text("workbench\n", encoding="utf-8")
    (root / "pyproject.toml").write_text('[project]\nname = "spec-dock"\nversion = "0.2.4"\n', encoding="utf-8")
    paths = sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file())
    return VerifiedBundle(
        PinnedSource("chemitaro/spec-dock", "a" * 40, "0.2.4"),
        root,
        _digest_paths(root, paths),
        _tooling_inventory(root),
    )


def test_fresh_init_journals_scaffold_and_restores_absence(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    bundle = _bundle(tmp_path)
    journal_root = tmp_path / "common"
    record = prepare_installation(target, journal_root, action="init", bundle=bundle)
    assert "spec-dock/workspace.json" in record.after_hashes
    assert "spec-dock/.workbench/README.md" in record.after_hashes
    completed = apply_installation(journal_root, record.operation_id, enter_maintenance=lambda _: None)
    assert completed.phase == "committed"
    assert (target / "spec-dock/workspace.json").read_text(encoding="utf-8") == "{}\n"
    assert (target / "spec-dock/.workbench/README.md").read_text(encoding="utf-8") == "workbench\n"
    restored = rollback_installation(
        journal_root, record.operation_id, enter_maintenance=lambda _: None, allow_committed=True
    )
    assert restored.phase == "rolled-back"
    assert not (target / "spec-dock/workspace.json").exists()
    assert not (target / "spec-dock/.workbench/README.md").exists()


def test_staged_hardlink_is_rejected_before_replacement(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    journal = tmp_path / "common"
    record = prepare_installation(target, journal, action="init", bundle=_bundle(tmp_path))
    stage = target / ".spec-dock-installations" / record.operation_id / "stage/spec-dock/spec-dock.version"
    os.link(stage, tmp_path / "foreign-link")
    with pytest.raises(ValueError, match=r"hardlink|identity"):
        apply_installation(journal, record.operation_id, enter_maintenance=lambda _: None)
    assert not (target / "spec-dock/spec-dock.version").exists()


def test_completed_same_content_inode_swap_blocks_rollback(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    journal = tmp_path / "common"
    record = prepare_installation(target, journal, action="init", bundle=_bundle(tmp_path))
    apply_installation(journal, record.operation_id, enter_maintenance=lambda _: None)
    installed = target / "spec-dock/spec-dock.version"
    replacement = installed.with_name("same-content")
    replacement.write_bytes(installed.read_bytes())
    replacement.chmod(installed.stat().st_mode)
    replacement.replace(installed)
    with pytest.raises(ValueError, match=r"identity|later changes"):
        rollback_installation(journal, record.operation_id, enter_maintenance=lambda _: None, allow_committed=True)
    assert installed.read_text(encoding="utf-8") == "0.2.4\n"


def test_backup_same_content_inode_swap_blocks_rollback(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    version = target / "spec-dock/spec-dock.version"
    version.parent.mkdir(parents=True)
    version.write_text("old\n", encoding="utf-8")
    journal = tmp_path / "common"
    record = prepare_installation(target, journal, action="update", bundle=_bundle(tmp_path))

    def interrupt(relative: str) -> None:
        if relative == "spec-dock/spec-dock.version":
            raise RuntimeError("stop after version")

    with pytest.raises(RuntimeError, match="stop after version"):
        apply_installation(journal, record.operation_id, enter_maintenance=lambda _: None, after_root=interrupt)
    backup = target / ".spec-dock-installations" / record.operation_id / "backup/spec-dock/spec-dock.version"
    replacement = backup.with_name("foreign-backup")
    shutil.copy2(backup, replacement)
    replacement.replace(backup)
    with pytest.raises(ValueError, match="backup changed identity"):
        rollback_installation(journal, record.operation_id, enter_maintenance=lambda _: None)
    assert version.read_text(encoding="utf-8") == "0.2.4\n"


def test_rollback_rechecks_same_inode_content_after_preflight(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    version = target / "spec-dock/spec-dock.version"
    version.parent.mkdir(parents=True)
    version.write_text("old\n", encoding="utf-8")
    journal = tmp_path / "common"
    record = prepare_installation(target, journal, action="update", bundle=_bundle(tmp_path))
    original_inode = version.stat().st_ino

    def change_after_preflight(_record: InstallationRecord) -> None:
        version.write_text("bad\n", encoding="utf-8")
        assert version.stat().st_ino == original_inode

    with pytest.raises(ValueError, match="later changes"):
        rollback_installation(journal, record.operation_id, enter_maintenance=change_after_preflight)
    assert version.read_text(encoding="utf-8") == "bad\n"
    assert read_record(journal, record.operation_id).phase != "rolled-back"


def test_rollback_preserves_changed_after_state_before_displacement(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    version = target / "spec-dock/spec-dock.version"
    version.parent.mkdir(parents=True)
    version.write_text("old\n", encoding="utf-8")
    journal = tmp_path / "common"
    record = prepare_installation(target, journal, action="update", bundle=_bundle(tmp_path))
    apply_installation(journal, record.operation_id, enter_maintenance=lambda _: None)
    original_inode = version.stat().st_ino

    def change_after_preflight(_record: InstallationRecord) -> None:
        version.write_text("9.2.4\n", encoding="utf-8")
        assert version.stat().st_ino == original_inode

    with pytest.raises(ValueError, match="later changes"):
        rollback_installation(
            journal, record.operation_id, enter_maintenance=change_after_preflight, allow_committed=True
        )
    assert version.read_text(encoding="utf-8") == "9.2.4\n"
    assert not (
        target / ".spec-dock-installations" / record.operation_id / "displaced/spec-dock/spec-dock.version"
    ).exists()
    assert read_record(journal, record.operation_id).phase == "committed"


def test_rollback_rechecks_backup_content_before_restore(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    version = target / "spec-dock/spec-dock.version"
    version.parent.mkdir(parents=True)
    version.write_text("old\n", encoding="utf-8")
    journal = tmp_path / "common"
    record = prepare_installation(target, journal, action="update", bundle=_bundle(tmp_path))
    apply_installation(journal, record.operation_id, enter_maintenance=lambda _: None)
    backup = target / ".spec-dock-installations" / record.operation_id / "backup/spec-dock/spec-dock.version"
    original_inode = backup.stat().st_ino

    def change_after_preflight(_record: InstallationRecord) -> None:
        backup.write_text("bad\n", encoding="utf-8")
        assert backup.stat().st_ino == original_inode

    with pytest.raises(ValueError, match="backup or target changed"):
        rollback_installation(
            journal, record.operation_id, enter_maintenance=change_after_preflight, allow_committed=True
        )
    assert backup.read_text(encoding="utf-8") == "bad\n"
    assert version.read_text(encoding="utf-8") == "0.2.4\n"
    assert read_record(journal, record.operation_id).phase != "rolled-back"


def test_stage_identity_survives_rename_before_completion_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    journal = tmp_path / "common"
    record = prepare_installation(target, journal, action="init", bundle=_bundle(tmp_path))
    original = type(target).replace
    stopped = False

    def interrupt(path: Path, destination: Path) -> Path:
        nonlocal stopped
        result = original(path, destination)
        if not stopped and "/stage/" in str(path):
            stopped = True
            raise RuntimeError("rename completed before journal")
        return result

    with monkeypatch.context() as patch:
        patch.setattr(type(target), "replace", interrupt)
        with pytest.raises(RuntimeError, match="rename completed before journal"):
            apply_installation(journal, record.operation_id, enter_maintenance=lambda _: None)
    completed = apply_installation(journal, record.operation_id, enter_maintenance=lambda _: None)
    assert completed.phase == "committed"


def test_installation_recovery_area_does_not_dirty_git_worktree(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=target, check=True)
    record = prepare_installation(target, tmp_path / "common", action="init", bundle=_bundle(tmp_path))
    assert (target / ".spec-dock-installations" / record.operation_id / "stage").is_dir()
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=target,
        check=True,
        capture_output=True,
        text=True,
    )
    assert status.stdout == ""


def test_installation_has_durable_planned_record_before_worktree_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    journal_root = tmp_path / "common"
    operation_id = "f" * 32
    original_mkdir = type(target).mkdir

    def interrupted_mkdir(path: Path, mode: int = 0o777, parents: bool = False, exist_ok: bool = False) -> None:
        if path.name == operation_id and path.parent.name == ".spec-dock-installations":
            assert read_record(journal_root, operation_id).phase == "planned"
            raise OSError("preparation interrupted")
        original_mkdir(path, mode=mode, parents=parents, exist_ok=exist_ok)

    monkeypatch.setattr(type(target), "mkdir", interrupted_mkdir)
    with pytest.raises(OSError, match="preparation interrupted"):
        prepare_installation(target, journal_root, action="init", bundle=_bundle(tmp_path), operation_id=operation_id)
    assert read_record(journal_root, operation_id).phase == "planned"


@pytest.mark.parametrize("action", ["init", "update", "uninstall"])
def test_planned_resume_rejects_managed_target_changed_after_interruption(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, action: str
) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    version = target / "spec-dock/spec-dock.version"
    if action != "init":
        version.parent.mkdir()
        version.write_text("old\n", encoding="utf-8")
    bundle = None if action == "uninstall" else _bundle(tmp_path)
    journal_root = tmp_path / "common"
    operation_id = "7" * 32
    original_mkdir = type(target).mkdir

    def interrupted_mkdir(path: Path, mode: int = 0o777, parents: bool = False, exist_ok: bool = False) -> None:
        if path.name == operation_id and path.parent.name == ".spec-dock-installations":
            raise OSError("preparation interrupted")
        original_mkdir(path, mode=mode, parents=parents, exist_ok=exist_ok)

    with monkeypatch.context() as patch:
        patch.setattr(type(target), "mkdir", interrupted_mkdir)
        with pytest.raises(OSError, match="preparation interrupted"):
            prepare_installation(target, journal_root, action=action, bundle=bundle, operation_id=operation_id)
    assert read_record(journal_root, operation_id).phase == "planned"
    version.parent.mkdir(parents=True, exist_ok=True)
    version.write_text("changed after interruption\n", encoding="utf-8")
    with pytest.raises(ValueError, match="changed after planning"):
        resume_preparation(journal_root, operation_id, bundle=bundle)
    assert version.read_text(encoding="utf-8") == "changed after interruption\n"
    assert not (target / ".spec-dock-installations" / operation_id).exists()


def test_planned_resume_rejects_new_scaffold_without_moving_it(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    journal_root = tmp_path / "common"
    operation_id = "6" * 32
    bundle = _bundle(tmp_path)
    original_mkdir = type(target).mkdir

    def interrupted_mkdir(path: Path, mode: int = 0o777, parents: bool = False, exist_ok: bool = False) -> None:
        if path.name == operation_id and path.parent.name == ".spec-dock-installations":
            raise OSError("preparation interrupted")
        original_mkdir(path, mode=mode, parents=parents, exist_ok=exist_ok)

    with monkeypatch.context() as patch:
        patch.setattr(type(target), "mkdir", interrupted_mkdir)
        with pytest.raises(OSError, match="preparation interrupted"):
            prepare_installation(target, journal_root, action="init", bundle=bundle, operation_id=operation_id)
    scaffold = target / "spec-dock/workspace.json"
    scaffold.parent.mkdir()
    scaffold.write_text('{"owner":"consumer"}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="changed after planning"):
        resume_preparation(journal_root, operation_id, bundle=bundle)
    assert scaffold.read_text(encoding="utf-8") == '{"owner":"consumer"}\n'
    assert not (target / ".spec-dock-installations" / operation_id).exists()
    rolled_back = rollback_installation(journal_root, operation_id, enter_maintenance=lambda _record: None)
    assert rolled_back.phase == "rolled-back"
    assert scaffold.read_text(encoding="utf-8") == '{"owner":"consumer"}\n'


def test_planned_resume_rejects_same_content_inode_replacement(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = tmp_path / "consumer"
    version = target / "spec-dock/spec-dock.version"
    version.parent.mkdir(parents=True)
    version.write_text("old\n", encoding="utf-8")
    journal_root = tmp_path / "common"
    operation_id = "5" * 32
    bundle = _bundle(tmp_path)
    original_mkdir = type(target).mkdir

    def interrupted_mkdir(path: Path, mode: int = 0o777, parents: bool = False, exist_ok: bool = False) -> None:
        if path.name == operation_id and path.parent.name == ".spec-dock-installations":
            raise OSError("preparation interrupted")
        original_mkdir(path, mode=mode, parents=parents, exist_ok=exist_ok)

    with monkeypatch.context() as patch:
        patch.setattr(type(target), "mkdir", interrupted_mkdir)
        with pytest.raises(OSError, match="preparation interrupted"):
            prepare_installation(target, journal_root, action="update", bundle=bundle, operation_id=operation_id)
    replacement = version.parent / "replacement"
    replacement.write_text("old\n", encoding="utf-8")
    replacement.replace(version)
    with pytest.raises(ValueError, match="changed after planning"):
        resume_preparation(journal_root, operation_id, bundle=bundle)
    assert version.read_text(encoding="utf-8") == "old\n"


def test_planned_resume_rejects_nested_same_content_inode_replacement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "consumer"
    version = target / "spec-dock/spec-dock.version"
    version.parent.mkdir(parents=True)
    version.write_text("old\n", encoding="utf-8")
    nested = target / "spec-dock/docs/guide.md"
    nested.parent.mkdir()
    nested.write_text("original\n", encoding="utf-8")
    journal_root = tmp_path / "common"
    operation_id = "3" * 32
    bundle = _bundle(tmp_path)
    original_mkdir = type(target).mkdir

    def interrupted_mkdir(path: Path, mode: int = 0o777, parents: bool = False, exist_ok: bool = False) -> None:
        if path.name == operation_id and path.parent.name == ".spec-dock-installations":
            raise OSError("preparation interrupted")
        original_mkdir(path, mode=mode, parents=parents, exist_ok=exist_ok)

    with monkeypatch.context() as patch:
        patch.setattr(type(target), "mkdir", interrupted_mkdir)
        with pytest.raises(OSError, match="preparation interrupted"):
            prepare_installation(target, journal_root, action="update", bundle=bundle, operation_id=operation_id)
    replacement = nested.parent / "replacement"
    replacement.write_text("original\n", encoding="utf-8")
    replacement.replace(nested)
    with pytest.raises(ValueError, match="changed after planning"):
        resume_preparation(journal_root, operation_id, bundle=bundle)
    assert nested.read_text(encoding="utf-8") == "original\n"


def test_planned_resume_keeps_requested_version(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    journal_root = tmp_path / "common"
    operation_id = "4" * 32
    bundle = _bundle(tmp_path)
    original_mkdir = type(target).mkdir

    def interrupted_mkdir(path: Path, mode: int = 0o777, parents: bool = False, exist_ok: bool = False) -> None:
        if path.name == operation_id and path.parent.name == ".spec-dock-installations":
            raise OSError("preparation interrupted")
        original_mkdir(path, mode=mode, parents=parents, exist_ok=exist_ok)

    with monkeypatch.context() as patch:
        patch.setattr(type(target), "mkdir", interrupted_mkdir)
        with pytest.raises(OSError, match="preparation interrupted"):
            prepare_installation(
                target,
                journal_root,
                action="init",
                bundle=bundle,
                operation_id=operation_id,
                installed_version="requested-version",
            )
    planned = read_record(journal_root, operation_id)
    assert planned.requested_version == "requested-version"
    staged = resume_preparation(journal_root, operation_id, bundle=bundle)
    assert staged.phase == "staged"
    apply_installation(journal_root, operation_id, enter_maintenance=lambda _record: None)
    assert (target / "spec-dock/spec-dock.version").read_text(encoding="utf-8") == "requested-version\n"


def test_legacy_planned_record_cannot_replan_but_can_roll_back(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    bundle = _bundle(tmp_path)
    journal_root = tmp_path / "common"
    legacy = InstallationRecord(
        "2" * 32,
        "init",
        str(target),
        bundle.source.commit,
        bundle.digest,
        "planned",
        (),
        {},
        {},
        marker_tracked=True,
    )
    write_record(journal_root, legacy, create=True)
    with pytest.raises(ValueError, match="fixed target snapshot"):
        resume_preparation(journal_root, legacy.operation_id, bundle=bundle)
    rolled_back = rollback_installation(journal_root, legacy.operation_id, enter_maintenance=lambda _record: None)
    assert rolled_back.phase == "rolled-back"
    assert not (target / "spec-dock").exists()


def test_staged_apply_rejects_same_content_target_replacement(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    version = target / "spec-dock/spec-dock.version"
    version.parent.mkdir(parents=True)
    version.write_text("old\n", encoding="utf-8")
    journal_root = tmp_path / "common"
    record = prepare_installation(target, journal_root, action="update", bundle=_bundle(tmp_path))
    replacement = version.parent / "replacement"
    replacement.write_text("old\n", encoding="utf-8")
    replacement.replace(version)
    with pytest.raises(ValueError, match="changed after planning"):
        apply_installation(journal_root, record.operation_id, enter_maintenance=lambda _record: None)
    assert version.read_text(encoding="utf-8") == "old\n"
    assert not (target / ".spec-dock-installations" / record.operation_id / "backup").exists()


@pytest.mark.parametrize("marker_kind", ["empty", "symlink", "hardlink"])
def test_installation_rejects_untrusted_existing_recovery_marker_before_mutation(
    tmp_path: Path, marker_kind: str
) -> None:
    target = tmp_path / "consumer"
    recovery = target / ".spec-dock-installations"
    recovery.mkdir(parents=True)
    marker = recovery / ".gitignore"
    if marker_kind == "empty":
        marker.write_bytes(b"")
    elif marker_kind == "symlink":
        marker.symlink_to(tmp_path / "external")
    else:
        external = tmp_path / "external"
        external.write_bytes(b"*\n")
        marker.hardlink_to(external)
    with pytest.raises(ValueError, match="ignore marker"):
        prepare_installation(target, tmp_path / "common", action="init", bundle=_bundle(tmp_path))
    assert sorted(recovery.iterdir()) == [marker]


def test_interrupted_marker_publication_resumes_same_child_and_restores_clean_git(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=target, check=True)
    journal_root = tmp_path / "common"
    operation_id = "e" * 32
    bundle = _bundle(tmp_path)
    import spec_dock.installation.executor as executor

    with monkeypatch.context() as patch:
        patch.setattr(executor.os, "link", lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("interrupted")))
        with pytest.raises(OSError, match="interrupted"):
            prepare_installation(target, journal_root, action="init", bundle=bundle, operation_id=operation_id)
    assert read_record(journal_root, operation_id).phase == "planned"
    assert not (target / ".spec-dock-installations/.gitignore").exists()
    completed = resume_preparation(journal_root, operation_id, bundle=bundle)
    assert completed.phase == "staged" and completed.operation_id == operation_id
    apply_installation(journal_root, operation_id, enter_maintenance=lambda _record: None)
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=target,
        check=True,
        capture_output=True,
        text=True,
    )
    assert (target / ".spec-dock-installations/.gitignore").read_bytes() == b"*\n"
    assert ".spec-dock-installations" not in status.stdout


def test_interrupted_marker_publication_rolls_back_same_child_without_git_dirt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=target, check=True)
    journal_root = tmp_path / "common"
    operation_id = "d" * 32
    import spec_dock.installation.executor as executor

    with monkeypatch.context() as patch:
        patch.setattr(executor.os, "link", lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("interrupted")))
        with pytest.raises(OSError, match="interrupted"):
            prepare_installation(
                target, journal_root, action="init", bundle=_bundle(tmp_path), operation_id=operation_id
            )
    restored = rollback_installation(journal_root, operation_id, enter_maintenance=lambda _record: None)
    assert restored.phase == "rolled-back"
    assert not (target / "spec-dock").exists()
    assert (target / ".spec-dock-installations/.gitignore").read_bytes() == b"*\n"
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=target,
        check=True,
        capture_output=True,
        text=True,
    )
    assert status.stdout == ""


def test_published_marker_recovers_after_parent_directory_sync_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    journal_root = tmp_path / "common"
    operation_id = "c" * 32
    bundle = _bundle(tmp_path)
    import spec_dock.installation.executor as executor

    original_sync = executor._sync_directory
    stopped = False

    def interrupted_sync(path: Path) -> None:
        nonlocal stopped
        if path == target / ".spec-dock-installations" and (path / ".gitignore").exists() and not stopped:
            stopped = True
            raise OSError("sync interrupted")
        original_sync(path)

    with monkeypatch.context() as patch:
        patch.setattr(executor, "_sync_directory", interrupted_sync)
        with pytest.raises(OSError, match="sync interrupted"):
            prepare_installation(target, journal_root, action="init", bundle=bundle, operation_id=operation_id)
    assert read_record(journal_root, operation_id).phase == "planned"
    staged = resume_preparation(journal_root, operation_id, bundle=bundle)
    assert staged.phase == "staged"
    assert (target / ".spec-dock-installations/.gitignore").stat().st_nlink == 1


def test_temporary_marker_sync_failure_rolls_back_without_partial_visible_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=target, check=True)
    journal_root = tmp_path / "common"
    operation_id = "b" * 32
    import spec_dock.installation.executor as executor

    original_sync = executor._sync_directory

    def interrupted_sync(path: Path) -> None:
        if path.name == operation_id and (path / "ignore-marker.tmp").exists():
            raise OSError("temporary sync interrupted")
        original_sync(path)

    with monkeypatch.context() as patch:
        patch.setattr(executor, "_sync_directory", interrupted_sync)
        with pytest.raises(OSError, match="temporary sync interrupted"):
            prepare_installation(
                target, journal_root, action="init", bundle=_bundle(tmp_path), operation_id=operation_id
            )
    assert read_record(journal_root, operation_id).phase == "planned"
    assert not (target / ".spec-dock-installations/.gitignore").exists()
    restored = rollback_installation(journal_root, operation_id, enter_maintenance=lambda _record: None)
    assert restored.phase == "rolled-back"
    assert (target / ".spec-dock-installations/.gitignore").read_bytes() == b"*\n"
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=target,
        check=True,
        capture_output=True,
        text=True,
    )
    assert status.stdout == ""


def test_planned_recovery_refuses_unowned_marker_without_replacing_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    journal_root = tmp_path / "common"
    operation_id = "9" * 32
    bundle = _bundle(tmp_path)
    import spec_dock.installation.executor as executor

    with monkeypatch.context() as patch:
        patch.setattr(executor.os, "link", lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("interrupted")))
        with pytest.raises(OSError, match="interrupted"):
            prepare_installation(target, journal_root, action="init", bundle=bundle, operation_id=operation_id)
    marker = target / ".spec-dock-installations/.gitignore"
    marker.write_bytes(b"unexpected\n")
    with pytest.raises(ValueError, match="ignore marker"):
        resume_preparation(journal_root, operation_id, bundle=bundle)
    with pytest.raises(ValueError, match="ignore marker"):
        rollback_installation(journal_root, operation_id, enter_maintenance=lambda _record: None)
    assert marker.read_bytes() == b"unexpected\n"


@pytest.mark.parametrize("action", ["update", "uninstall"])
def test_planned_update_and_uninstall_roll_back_after_marker_publication_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, action: str
) -> None:
    target = tmp_path / "consumer"
    version = target / "spec-dock/spec-dock.version"
    version.parent.mkdir(parents=True)
    version.write_text("old\n", encoding="utf-8")
    journal_root = tmp_path / "common"
    operation_id = "8" * 32
    bundle = _bundle(tmp_path) if action == "update" else None
    import spec_dock.installation.executor as executor

    with monkeypatch.context() as patch:
        patch.setattr(executor.os, "link", lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("interrupted")))
        with pytest.raises(OSError, match="interrupted"):
            prepare_installation(target, journal_root, action=action, bundle=bundle, operation_id=operation_id)
    restored = rollback_installation(journal_root, operation_id, enter_maintenance=lambda _record: None)
    assert restored.phase == "rolled-back"
    assert version.read_text(encoding="utf-8") == "old\n"
    assert (target / ".spec-dock-installations/.gitignore").read_bytes() == b"*\n"


def test_marker_same_content_replacement_blocks_apply_and_rollback(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    journal_root = tmp_path / "common"
    record = prepare_installation(target, journal_root, action="init", bundle=_bundle(tmp_path))
    marker = target / ".spec-dock-installations/.gitignore"
    replacement = marker.parent / "replacement"
    replacement.write_bytes(b"*\n")
    replacement.replace(marker)
    with pytest.raises(ValueError, match="changed identity"):
        apply_installation(journal_root, record.operation_id, enter_maintenance=lambda _record: None)
    with pytest.raises(ValueError, match="changed identity"):
        rollback_installation(journal_root, record.operation_id, enter_maintenance=lambda _record: None)
    assert marker.read_bytes() == b"*\n"


def test_installation_resumes_after_first_root_and_preserves_custom_ignore(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    old = target / TOOL_DIRECTORIES[0]
    old.mkdir(parents=True)
    (old / "old.txt").write_text("old", encoding="utf-8")
    (target / "spec-dock/spec-dock.version").write_text("old\n", encoding="utf-8")
    ignore = target / "spec-dock/.gitignore"
    ignore.write_text("my custom ignore\n", encoding="utf-8")
    journal_root = tmp_path / "common"
    record = prepare_installation(target, journal_root, action="update", bundle=_bundle(tmp_path))
    maintenance_calls: list[str] = []

    def after_first(_root: str) -> None:
        raise RuntimeError("process stopped")

    with pytest.raises(RuntimeError, match="process stopped"):
        apply_installation(
            journal_root,
            record.operation_id,
            enter_maintenance=lambda current: maintenance_calls.append(current.operation_id),
            after_root=after_first,
        )
    pending = read_record(journal_root, record.operation_id)
    assert pending.phase == "recovery-required"
    assert pending.completed_roots == (TOOL_DIRECTORIES[0],)
    complete = apply_installation(
        journal_root,
        record.operation_id,
        enter_maintenance=lambda current: maintenance_calls.append(current.operation_id),
    )
    assert complete.phase == "committed"
    assert len(complete.completed_roots) == len(TOOL_DIRECTORIES) + 2
    assert (old / "source.txt").read_text(encoding="utf-8") == TOOL_DIRECTORIES[0]
    assert ignore.read_text(encoding="utf-8") == "my custom ignore\n"
    assert len(maintenance_calls) == 2


def test_installation_rollback_refuses_later_changes(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    original = target / TOOL_DIRECTORIES[0]
    original.mkdir(parents=True)
    (original / "old.txt").write_text("old", encoding="utf-8")
    (target / "spec-dock/spec-dock.version").write_text("old\n", encoding="utf-8")
    journal_root = tmp_path / "common"
    record = prepare_installation(target, journal_root, action="update", bundle=_bundle(tmp_path))

    with pytest.raises(RuntimeError, match="stopped"):
        apply_installation(
            journal_root,
            record.operation_id,
            enter_maintenance=lambda _current: None,
            after_root=lambda _root: (_ for _ in ()).throw(RuntimeError("stopped")),
        )
    (original / "later.txt").write_text("user edit", encoding="utf-8")
    with pytest.raises(ValueError, match="later changes"):
        rollback_installation(journal_root, record.operation_id, enter_maintenance=lambda _current: None)
    (original / "later.txt").unlink()
    result = rollback_installation(journal_root, record.operation_id, enter_maintenance=lambda _current: None)
    assert result.phase == "rolled-back"
    assert (original / "old.txt").read_text(encoding="utf-8") == "old"


def test_installation_refuses_modified_verified_bundle_before_staging(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    bundle = _bundle(tmp_path)
    source = bundle.root / "src/spec_dock/assets/spec_dock/docs/source.txt"
    source.write_text("modified", encoding="utf-8")
    with pytest.raises(ValueError, match="content changed"):
        prepare_installation(target, tmp_path / "common", action="init", bundle=bundle)
    assert not (target / ".spec-dock-installations").exists()


def test_init_refuses_existing_unversioned_tooling(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    (target / TOOL_DIRECTORIES[0]).mkdir(parents=True)
    with pytest.raises(ValueError, match="existing tooling"):
        prepare_installation(target, tmp_path / "common", action="init", bundle=_bundle(tmp_path))


def test_installation_refuses_journal_inside_replaced_skill(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    journal_root = target / ".agents/skills/spec-dock/control"
    with pytest.raises(ValueError, match="outside replaced tooling"):
        prepare_installation(target, journal_root, action="init", bundle=_bundle(tmp_path))
    assert not (target / ".spec-dock-installations").exists()
    assert not journal_root.exists()


def test_installation_can_fix_child_operation_id_before_staging(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    journal_root = tmp_path / "common"
    child_id = "f" * 32
    bundle = _bundle(tmp_path)
    record = prepare_installation(target, journal_root, action="init", bundle=bundle, operation_id=child_id)
    assert record.operation_id == child_id
    assert read_record(journal_root, child_id) == record
    with pytest.raises(ValueError, match="operation ID"):
        prepare_installation(target, journal_root, action="init", bundle=bundle, operation_id="bad")


def test_uninstall_retains_consumer_data_and_ignore_file(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    bundle = _bundle(tmp_path)
    journal_root = tmp_path / "common"
    setup = prepare_installation(target, journal_root, action="init", bundle=bundle)
    apply_installation(journal_root, setup.operation_id, enter_maintenance=lambda _current: None)
    consumer_data = target / "spec-dock/initiatives/local-1/requirement.md"
    consumer_data.parent.mkdir(parents=True)
    consumer_data.write_text("user data", encoding="utf-8")
    cleanup = prepare_installation(target, journal_root, action="uninstall", bundle=None)
    complete = apply_installation(journal_root, cleanup.operation_id, enter_maintenance=lambda _current: None)
    assert complete.phase == "committed"
    assert consumer_data.read_text(encoding="utf-8") == "user data"
    assert (target / "spec-dock/.gitignore").is_file()
    assert not (target / TOOL_DIRECTORIES[0]).exists()
