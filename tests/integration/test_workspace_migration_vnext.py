"""Read-only inventory is the first gate before mapping or changing old worktrees."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.infra.control_store import (  # noqa: E402
    ControlState,
    WorktreeRegistration,
    store_control,
)
from spec_dock_runtime.infra.git_cli import git_common_directory  # noqa: E402
from spec_dock_runtime.infra.migration_store import inspect_migration_inventory  # noqa: E402


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
