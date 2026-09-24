"""Crash-safe record semantics for the external installer."""

from __future__ import annotations

from dataclasses import replace
import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.installation.executor import apply_installation, prepare_installation, rollback_installation
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
