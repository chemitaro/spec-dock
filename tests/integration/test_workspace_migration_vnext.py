"""Read-only inventory is the first gate before mapping or changing old worktrees."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.infra.control_store import (  # noqa: E402
    ControlState,
    WorktreeRegistration,
    load_control,
    store_control,
)
from spec_dock_runtime.infra.git_cli import git_common_directory  # noqa: E402
from spec_dock_runtime.infra.migration_store import (  # noqa: E402
    MigrationMap,
    inspect_migration_inventory,
    read_migration_map,
)
from spec_dock_runtime.infra.registry_store import RegistryStore  # noqa: E402


def _legacy_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "remote", "add", "origin", "https://github.com/example/repo.git"],
        check=True,
        capture_output=True,
    )
    initiative = repo / "spec-dock/initiatives/init-local-00001-plan"
    initiative.mkdir(parents=True)
    metadata = {
        "schema_version": 1,
        "type": "initiative",
        "id": "init-local-00001",
        "title": "Plan",
        "slug": "plan",
        "parent_id": None,
        "github": {"issue_number": 1, "repo_owner": "example", "repo_name": "repo"},
        "unknown_field": {"keep": True},
    }
    (initiative / ".meta.json").write_text(json.dumps(metadata), encoding="utf-8")
    epic = initiative / "epics/epic-local-00001-work"
    epic.mkdir(parents=True)
    (epic / ".meta.json").write_text(
        json.dumps({
            "schema_version": 1,
            "type": "epic",
            "id": "epic-local-00001",
            "parent_id": "init-local-00001",
            "github": None,
        }),
        encoding="utf-8",
    )
    issue = epic / "issues/iss-local-00001-task"
    issue.mkdir(parents=True)
    (issue / ".meta.json").write_text(
        json.dumps({
            "schema_version": 1,
            "type": "issue",
            "id": "iss-local-00001",
            "parent_id": "epic-local-00001",
            "github": None,
        }),
        encoding="utf-8",
    )
    active = repo / "spec-dock/.agent/active.json"
    active.parent.mkdir(parents=True)
    active.write_text(
        json.dumps({
            "schema_version": 2,
            "initiative": {"id": "init-local-00001", "path": "spec-dock/initiatives/init-local-00001-plan"},
            "epic": None,
            "issue": None,
        }),
        encoding="utf-8",
    )
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
        check=True,
        capture_output=True,
    )
    return repo


def test_migration_inventory_reads_all_worktrees_and_stays_stable(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)
    second = tmp_path / "second"
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "-q", "-b", "second", str(second)], check=True)
    first = inspect_migration_inventory(repo)
    again = inspect_migration_inventory(repo)
    assert first == again
    assert len(first.worktrees) == 2
    assert first.digest.startswith("sha256:")
    assert first.repository_uid.startswith("sha256:")
    assert all(worktree.active_focus == "init-local-00001" for worktree in first.worktrees)
    assert all(any(scope.backend_candidate == "github" for scope in worktree.scopes) for worktree in first.worktrees)
    assert all(any(scope.backend_candidate == "local" for scope in worktree.scopes) for worktree in first.worktrees)
    assert first.blockers == ()
    assert (
        subprocess.run(["git", "-C", str(repo), "status", "--porcelain"], check=True, capture_output=True).stdout == b""
    )


def test_migration_inventory_marks_partial_link_and_broken_active(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)
    initiative = repo / "spec-dock/initiatives/init-local-00001-plan/.meta.json"
    payload = json.loads(initiative.read_text(encoding="utf-8"))
    payload["github"] = {"issue_number": 1}
    initiative.write_text(json.dumps(payload), encoding="utf-8")
    active = repo / "spec-dock/.agent/active.json"
    active.write_text(
        json.dumps({
            "schema_version": 2,
            "initiative": {"id": "init-local-99999", "path": "missing"},
            "epic": None,
            "issue": None,
        }),
        encoding="utf-8",
    )
    inventory = inspect_migration_inventory(repo)
    assert "BACKEND_MAPPING_REQUIRED" in inventory.blockers
    assert "ACTIVE_REPAIR_REQUIRED" in inventory.blockers


def test_migration_inventory_detects_duplicate_id_and_unknown_field_change(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)
    original = inspect_migration_inventory(repo)
    metadata_path = repo / "spec-dock/initiatives/init-local-00001-plan/.meta.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    payload["unknown_field"] = {"keep": False}
    metadata_path.write_text(json.dumps(payload), encoding="utf-8")
    changed = inspect_migration_inventory(repo)
    assert changed.digest != original.digest
    assert changed.blockers == ()
    duplicate = repo / "spec-dock/initiatives/init-local-00002-duplicate"
    duplicate.mkdir()
    (duplicate / ".meta.json").write_text(json.dumps(payload), encoding="utf-8")
    assert "DUPLICATE_SCOPE_ID" in inspect_migration_inventory(repo).blockers


def test_migration_inventory_detects_unregistered_git_worktree(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)
    second = tmp_path / "second"
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "-q", "-b", "second", str(second)], check=True)
    common = git_common_directory(repo)
    registration = WorktreeRegistration("main", str(repo), 3, "specdock.writer/v1", "engine-a", True)
    store_control(
        common,
        ControlState(3, "specdock.writer/v1", 1, "engine-a", "maintenance", (registration,)),
        expected_epoch=None,
    )
    inventory = inspect_migration_inventory(repo)
    assert "WORKTREE_UNREGISTERED" in inventory.blockers
    assert {worktree.registration_id for worktree in inventory.worktrees} == {"main", None}


def test_migration_inventory_digest_includes_workspace_and_control_bytes(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)
    workspace = repo / "spec-dock/workspace.json"
    workspace.write_text(json.dumps({"schema_version": 1, "unknown": "a"}), encoding="utf-8")
    first = inspect_migration_inventory(repo)
    workspace.write_text(json.dumps({"schema_version": 1, "unknown": "b"}), encoding="utf-8")
    second = inspect_migration_inventory(repo)
    assert first.worktrees[0].workspace_schema == second.worktrees[0].workspace_schema == 1
    assert first.digest != second.digest
    common = git_common_directory(repo)
    registration = WorktreeRegistration("main", str(repo), 3, "specdock.writer/v1", "engine-a", True)
    store_control(
        common,
        ControlState(3, "specdock.writer/v1", 1, "engine-a", "maintenance", (registration,)),
        expected_epoch=None,
    )
    third = inspect_migration_inventory(repo)
    assert third.control_digest is not None
    assert third.digest != second.digest


def test_migration_plan_preserves_unknown_fields_and_active_focus(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)
    inventory = inspect_migration_inventory(repo)
    mapping = MigrationMap(
        inventory.repository_uid, inventory.digest, (), (), (), ({"root": str(repo), "registration_id": "main"},)
    )
    import spec_dock_runtime.application.migrate_workspace_vnext as migration_module

    changes = migration_module.plan_migration_changes(inventory, mapping, updated_at="2026-01-01T00:00:00Z")
    by_path = {change.path: json.loads(change.after_bytes) for change in changes}
    initiative_path = str(repo / "spec-dock/initiatives/init-local-00001-plan/.meta.json")
    initiative = by_path[initiative_path]
    assert initiative["schema_version"] == 3
    assert initiative["backend"] == "github"
    assert initiative["unknown_field"] == {"keep": True}
    epic_path = str(repo / "spec-dock/initiatives/init-local-00001-plan/epics/epic-local-00001-work/.meta.json")
    assert by_path[epic_path]["lifecycle"]["state"] == "open"
    active = by_path[str(repo / "spec-dock/.agent/active.json")]
    assert active["schema_version"] == 3
    assert active["focus_id"] == "init-local-00001"
    assert active["worktree_id"] is not None
    assert json.loads((repo / "spec-dock/.agent/active.json").read_text())["schema_version"] == 2


def test_migration_plan_rejects_missing_registration_and_changed_metadata(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)
    inventory = inspect_migration_inventory(repo)
    import spec_dock_runtime.application.migrate_workspace_vnext as migration_module

    empty_mapping = MigrationMap(inventory.repository_uid, inventory.digest, (), (), (), ())
    with pytest.raises(ValueError, match="registration"):
        migration_module.plan_migration_changes(inventory, empty_mapping, updated_at="2026-01-01T00:00:00Z")
    mapping = MigrationMap(
        inventory.repository_uid, inventory.digest, (), (), (), ({"root": str(repo), "registration_id": "main"},)
    )
    meta_path = repo / "spec-dock/initiatives/init-local-00001-plan/.meta.json"
    payload = json.loads(meta_path.read_text(encoding="utf-8"))
    payload["title"] = "Changed"
    meta_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="changed"):
        migration_module.plan_migration_changes(inventory, mapping, updated_at="2026-01-01T00:00:00Z")


def test_migration_applies_registered_worktree_and_keeps_maintenance(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)
    common = git_common_directory(repo)
    engine = "e" * 64
    control = ControlState(
        3,
        "specdock.writer/v1",
        1,
        engine,
        "maintenance",
        (WorktreeRegistration("main", str(repo), 1, "specdock.writer/v0", engine, True),),
    )
    store_control(common, control, expected_epoch=None)
    inventory = inspect_migration_inventory(repo)
    mapping = MigrationMap(inventory.repository_uid, inventory.digest, (), (), (), ())
    import spec_dock_runtime.application.migrate_workspace_vnext as migration_module

    result = migration_module.apply_workspace_migration(
        repo_root=repo,
        common_dir=common,
        worktree_id="main",
        engine_digest=engine,
        expected_epoch=1,
        inventory=inventory,
        mapping=mapping,
        updated_at="2026-01-01T00:00:00Z",
    )
    assert result.phase == "committed"
    meta = repo / "spec-dock/initiatives/init-local-00001-plan/.meta.json"
    assert json.loads(meta.read_text(encoding="utf-8"))["schema_version"] == 3
    active = repo / "spec-dock/.agent/active.json"
    assert json.loads(active.read_text(encoding="utf-8"))["focus_id"] == "init-local-00001"
    workspace = repo / "spec-dock/workspace.json"
    assert json.loads(workspace.read_text(encoding="utf-8"))["schema_version"] == 3
    updated_control = load_control(common)
    assert updated_control is not None and updated_control.mode == "maintenance"
    assert updated_control.worktrees[0].schema_version == 3


def test_migration_resumes_after_one_file_was_published(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _legacy_repo(tmp_path)
    common = git_common_directory(repo)
    engine = "e" * 64
    store_control(
        common,
        ControlState(
            3,
            "specdock.writer/v1",
            1,
            engine,
            "maintenance",
            (WorktreeRegistration("main", str(repo), 1, "specdock.writer/v0", engine, True),),
        ),
        expected_epoch=None,
    )
    inventory = inspect_migration_inventory(repo)
    mapping = MigrationMap(inventory.repository_uid, inventory.digest, (), (), (), ())
    import spec_dock_runtime.application.migrate_workspace_vnext as migration_module
    import spec_dock_runtime.infra.migration_journal as journal

    real_apply = migration_module.apply_migration_file
    attempts = 0

    def stop_second(*args: object, **kwargs: object) -> None:
        nonlocal attempts
        attempts += 1
        if attempts == 2:
            raise RuntimeError("injected migration stop")
        real_apply(*args, **kwargs)

    monkeypatch.setattr(migration_module, "apply_migration_file", stop_second)
    with pytest.raises(RuntimeError, match="requires explicit recovery"):
        migration_module.apply_workspace_migration(
            repo_root=repo,
            common_dir=common,
            worktree_id="main",
            engine_digest=engine,
            expected_epoch=1,
            inventory=inventory,
            mapping=mapping,
            updated_at="2026-01-01T00:00:00Z",
        )
    (operation_id,) = journal.pending_migrations(common)
    monkeypatch.setattr(migration_module, "apply_migration_file", real_apply)
    resumed = migration_module.resume_workspace_migration(
        repo_root=repo,
        common_dir=common,
        worktree_id="main",
        engine_digest=engine,
        operation_id=operation_id,
    )
    assert resumed.phase == "committed"
    assert journal.pending_migrations(common) == ()
    assert all(json.loads(Path(item.path).read_text())["schema_version"] == 3 for item in resumed.files)


def test_committed_migration_rollback_restores_before_bytes_in_maintenance(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)
    common = git_common_directory(repo)
    engine = "e" * 64
    control = ControlState(
        3,
        "specdock.writer/v1",
        1,
        engine,
        "maintenance",
        (WorktreeRegistration("main", str(repo), 1, "specdock.writer/v0", engine, True),),
    )
    store_control(common, control, expected_epoch=None)
    inventory = inspect_migration_inventory(repo)
    mapping = MigrationMap(inventory.repository_uid, inventory.digest, (), (), (), ())
    import spec_dock_runtime.application.migrate_workspace_vnext as migration_module

    active = repo / "spec-dock/.agent/active.json"
    before = active.read_bytes()
    completed = migration_module.apply_workspace_migration(
        repo_root=repo,
        common_dir=common,
        worktree_id="main",
        engine_digest=engine,
        expected_epoch=1,
        inventory=inventory,
        mapping=mapping,
        updated_at="2026-01-01T00:00:00Z",
    )
    rolled_back = migration_module.rollback_workspace_migration(
        repo_root=repo,
        common_dir=common,
        worktree_id="main",
        engine_digest=engine,
        operation_id=completed.operation_id,
    )
    assert rolled_back.phase == "rolled-back"
    assert active.read_bytes() == before
    assert not (repo / "spec-dock/workspace.json").exists()
    restored_control = load_control(common)
    assert restored_control is not None and restored_control.mode == "maintenance"
    assert restored_control.worktrees[0].schema_version == 1


def test_migration_rollback_refuses_later_user_edit_without_partial_restore(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)
    common = git_common_directory(repo)
    engine = "e" * 64
    store_control(
        common,
        ControlState(
            3,
            "specdock.writer/v1",
            1,
            engine,
            "maintenance",
            (WorktreeRegistration("main", str(repo), 1, "specdock.writer/v0", engine, True),),
        ),
        expected_epoch=None,
    )
    inventory = inspect_migration_inventory(repo)
    mapping = MigrationMap(inventory.repository_uid, inventory.digest, (), (), (), ())
    import spec_dock_runtime.application.migrate_workspace_vnext as migration_module

    completed = migration_module.apply_workspace_migration(
        repo_root=repo,
        common_dir=common,
        worktree_id="main",
        engine_digest=engine,
        expected_epoch=1,
        inventory=inventory,
        mapping=mapping,
        updated_at="2026-01-01T00:00:00Z",
    )
    active = repo / "spec-dock/.agent/active.json"
    active.write_bytes(active.read_bytes() + b" ")
    first_meta = Path(completed.files[0].path)
    first_after = first_meta.read_bytes()
    with pytest.raises(ValueError, match="later changes"):
        migration_module.rollback_workspace_migration(
            repo_root=repo,
            common_dir=common,
            worktree_id="main",
            engine_digest=engine,
            operation_id=completed.operation_id,
        )
    assert first_meta.read_bytes() == first_after
    assert active.read_bytes().endswith(b" ")


def test_migration_rollback_resumes_after_interruption(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _legacy_repo(tmp_path)
    common = git_common_directory(repo)
    engine = "e" * 64
    store_control(
        common,
        ControlState(
            3,
            "specdock.writer/v1",
            1,
            engine,
            "maintenance",
            (WorktreeRegistration("main", str(repo), 1, "specdock.writer/v0", engine, True),),
        ),
        expected_epoch=None,
    )
    inventory = inspect_migration_inventory(repo)
    mapping = MigrationMap(inventory.repository_uid, inventory.digest, (), (), (), ())
    import spec_dock_runtime.application.migrate_workspace_vnext as migration_module
    import spec_dock_runtime.infra.migration_journal as journal

    completed = migration_module.apply_workspace_migration(
        repo_root=repo,
        common_dir=common,
        worktree_id="main",
        engine_digest=engine,
        expected_epoch=1,
        inventory=inventory,
        mapping=mapping,
        updated_at="2026-01-01T00:00:00Z",
    )
    real_rollback = migration_module.rollback_migration_file
    calls = 0

    def stop_second(*args: object, **kwargs: object) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("injected rollback stop")
        real_rollback(*args, **kwargs)

    monkeypatch.setattr(migration_module, "rollback_migration_file", stop_second)
    with pytest.raises(RuntimeError, match="requires explicit recovery"):
        migration_module.rollback_workspace_migration(
            repo_root=repo,
            common_dir=common,
            worktree_id="main",
            engine_digest=engine,
            operation_id=completed.operation_id,
        )
    assert journal.pending_migrations(common) == (completed.operation_id,)
    monkeypatch.setattr(migration_module, "rollback_migration_file", real_rollback)
    rolled_back = migration_module.rollback_workspace_migration(
        repo_root=repo,
        common_dir=common,
        worktree_id="main",
        engine_digest=engine,
        operation_id=completed.operation_id,
    )
    assert rolled_back.phase == "rolled-back"
    assert journal.pending_migrations(common) == ()


def test_migration_adopts_explicit_existing_branch_and_rolls_binding_back(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)
    subprocess.run(["git", "-C", str(repo), "branch", "iss-local-00001-task"], check=True)
    tip = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    common = git_common_directory(repo)
    engine = "e" * 64
    store_control(
        common,
        ControlState(
            3,
            "specdock.writer/v1",
            1,
            engine,
            "maintenance",
            (WorktreeRegistration("main", str(repo), 1, "specdock.writer/v0", engine, True),),
        ),
        expected_epoch=None,
    )
    inventory = inspect_migration_inventory(repo)
    mapping_path = tmp_path / "mapping.json"
    mapping_path.write_text(
        json.dumps({
            "schema_version": "specdock.migration-map/v1",
            "repository_uid": inventory.repository_uid,
            "source_inventory_digest": inventory.digest,
            "scope_backend_overrides": [],
            "branch_bindings": [
                {
                    "worktree_id": "main",
                    "scope_id": "iss-local-00001",
                    "branch": "iss-local-00001-task",
                    "tip_sha": tip,
                    "reason": "adopt the existing issue work branch",
                }
            ],
            "active_repairs": [],
            "worktrees": [],
        }),
        encoding="utf-8",
    )
    mapping = read_migration_map(mapping_path, inventory)
    import spec_dock_runtime.application.migrate_workspace_vnext as migration_module

    completed = migration_module.apply_workspace_migration(
        repo_root=repo,
        common_dir=common,
        worktree_id="main",
        engine_digest=engine,
        expected_epoch=1,
        inventory=inventory,
        mapping=mapping,
        updated_at="2026-01-01T00:00:00Z",
    )
    registry_path = RegistryStore(common).path
    registry, _identity = RegistryStore(common).load()
    assert [(item.scope_id, item.name, item.initial_sha) for item in registry.branches] == [
        ("iss-local-00001", "iss-local-00001-task", tip)
    ]
    migration_module.rollback_workspace_migration(
        repo_root=repo,
        common_dir=common,
        worktree_id="main",
        engine_digest=engine,
        operation_id=completed.operation_id,
    )
    assert not registry_path.exists()
    assert (
        subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "iss-local-00001-task"], check=True, capture_output=True, text=True
        ).stdout.strip()
        == tip
    )


def test_migration_applies_and_restores_all_registered_worktrees(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)
    second = tmp_path / "second"
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "-q", "-b", "second", str(second)], check=True)
    common = git_common_directory(repo)
    engine = "e" * 64
    store_control(
        common,
        ControlState(
            3,
            "specdock.writer/v1",
            1,
            engine,
            "maintenance",
            (
                WorktreeRegistration("main", str(repo), 1, "specdock.writer/v0", engine, True),
                WorktreeRegistration("second", str(second), 1, "specdock.writer/v0", engine, True),
            ),
        ),
        expected_epoch=None,
    )
    inventory = inspect_migration_inventory(repo)
    mapping = MigrationMap(inventory.repository_uid, inventory.digest, (), (), (), ())
    import spec_dock_runtime.application.migrate_workspace_vnext as migration_module

    completed = migration_module.apply_workspace_migration(
        repo_root=repo,
        common_dir=common,
        worktree_id="main",
        engine_digest=engine,
        expected_epoch=1,
        inventory=inventory,
        mapping=mapping,
        updated_at="2026-01-01T00:00:00Z",
    )
    assert completed.phase == "committed"
    assert len(completed.worktrees) == 2
    for root in (repo, second):
        assert json.loads((root / "spec-dock/workspace.json").read_text())["schema_version"] == 3
    assert all(item.schema_version == 3 for item in load_control(common).worktrees)
    migration_module.rollback_workspace_migration(
        repo_root=repo,
        common_dir=common,
        worktree_id="main",
        engine_digest=engine,
        operation_id=completed.operation_id,
    )
    for root in (repo, second):
        assert not (root / "spec-dock/workspace.json").exists()
        assert json.loads((root / "spec-dock/.agent/active.json").read_text())["schema_version"] == 2


def test_migration_registers_explicitly_mapped_worktree_and_rollback_removes_registration(tmp_path: Path) -> None:
    repo = _legacy_repo(tmp_path)
    second = tmp_path / "second"
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "-q", "-b", "second", str(second)], check=True)
    common = git_common_directory(repo)
    engine = "e" * 64
    store_control(
        common,
        ControlState(
            3,
            "specdock.writer/v1",
            1,
            engine,
            "maintenance",
            (WorktreeRegistration("main", str(repo), 1, "specdock.writer/v0", engine, True),),
        ),
        expected_epoch=None,
    )
    inventory = inspect_migration_inventory(repo)
    mapping_path = tmp_path / "mapping.json"
    mapping_path.write_text(
        json.dumps({
            "schema_version": "specdock.migration-map/v1",
            "repository_uid": inventory.repository_uid,
            "source_inventory_digest": inventory.digest,
            "scope_backend_overrides": [],
            "branch_bindings": [],
            "active_repairs": [],
            "worktrees": [{"root": str(second), "registration_id": "second"}],
        }),
        encoding="utf-8",
    )
    mapping = read_migration_map(mapping_path, inventory)
    import spec_dock_runtime.application.migrate_workspace_vnext as migration_module

    completed = migration_module.apply_workspace_migration(
        repo_root=repo,
        common_dir=common,
        worktree_id="main",
        engine_digest=engine,
        expected_epoch=1,
        inventory=inventory,
        mapping=mapping,
        updated_at="2026-01-01T00:00:00Z",
    )
    assert {(item.id, item.schema_version) for item in load_control(common).worktrees} == {("main", 3), ("second", 3)}
    migration_module.rollback_workspace_migration(
        repo_root=repo,
        common_dir=common,
        worktree_id="main",
        engine_digest=engine,
        operation_id=completed.operation_id,
    )
    assert [(item.id, item.schema_version) for item in load_control(common).worktrees] == [("main", 1)]
