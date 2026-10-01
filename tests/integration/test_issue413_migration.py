"""Local declaration cutover preserves actual data without replaying old control."""

from __future__ import annotations

import json
import os
import select
import stat
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from tests.cli_runtime.test_issue413_work_start import committed_workspace

if TYPE_CHECKING:
    from pathlib import Path


TARGET = ["--to-schema", "3", "--to-writer-protocol", "specdock.worktree-writer/v1"]


def legacy_workspace(root: Path) -> Path:
    committed_workspace(root)
    (root / "spec-dock/workspace.json").write_text(
        json.dumps({
            "schema_version": 3,
            "writer_protocol": "specdock.writer/v1",
            "control_epoch": 7,
            "required_features": [],
            "future_optional": {"private": "preserve-without-echo", "values": [1, False, None]},
        })
        + "\n",
        encoding="utf-8",
    )
    return root


def test_migration_preview_without_control_writes_no_backup_stage_or_git_state(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root = legacy_workspace(tmp_path / "consumer")
    before = tree_digest(root)

    def no_lock(*_args: object, **_kwargs: object) -> object:
        pytest.fail("migration must not acquire the Start exclusion")

    monkeypatch.setattr("spec_dock.runtime.infra.start_lock.StartLock.__enter__", no_lock)
    assert main(["--project", str(root), "workspace", "migrate", *TARGET, "--dry-run", "--json"]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["status"] == "planned" and result["data"]["kind"] == "migration"
    assert result["data"]["result"]["changed_paths"] == []
    assert result["data"]["result"]["before_protocol"] == "specdock.writer/v1"
    assert result["data"]["result"]["can_apply"] is True
    assert all(effect["status"] == "planned" for effect in result["effects"])
    assert "preserve-without-echo" not in output.out + output.err
    assert tree_digest(root) == before
    assert list(tmp_path.iterdir()) == [root]
    assert not (root / "spec-dock/.agent").exists()


@pytest.mark.parametrize(
    "changed",
    [
        {"schema_version": 2},
        {"schema_version": 99},
        {"schema_version": True},
        {"schema_version": 3.0},
        {"writer_protocol": "future.writer/v2"},
        {"required_features": ["future-state"]},
    ],
)
def test_migration_refuses_unknown_declarations_without_creating_a_backup(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], changed: dict[str, object]
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root = legacy_workspace(tmp_path / "consumer")
    workspace = root / "spec-dock/workspace.json"
    workspace.write_text(json.dumps({**json.loads(workspace.read_bytes()), **changed}), encoding="utf-8")
    before = tree_digest(root)
    backup = tmp_path / "backup"
    assert (
        main([
            "--project",
            str(root),
            "workspace",
            "migrate",
            *TARGET,
            "--backup-dir",
            str(backup),
            "--confirm-old-writers-stopped",
            "--yes",
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and tree_digest(root) == before
    assert not backup.exists()


def test_migration_rechecks_verified_backup_before_publication(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.application import direct_migration

    root = legacy_workspace(tmp_path / "consumer")
    before = (root / "spec-dock/workspace.json").read_bytes()
    backup = tmp_path / "backup"
    original = direct_migration.create_verified_backup

    def replace_backup(*args: object, **kwargs: object) -> object:
        result = original(*args, **kwargs)
        (backup / "checkout/spec-dock/workspace.json").write_bytes(b"backup replaced after verification\n")
        return result

    monkeypatch.setattr(direct_migration, "create_verified_backup", replace_backup)
    assert (
        main([
            "--project",
            str(root),
            "workspace",
            "migrate",
            *TARGET,
            "--backup-dir",
            str(backup),
            "--confirm-old-writers-stopped",
            "--yes",
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "partial"
    assert (
        next(effect for effect in result["effects"] if effect["kind"] == "workspace.migrate")["status"]
        == "not_attempted"
    )
    assert (root / "spec-dock/workspace.json").read_bytes() == before


def test_migration_after_publication_interruption_reports_uncertainty_and_fresh_retry_uses_actual_protocol(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root = legacy_workspace(tmp_path / "consumer")
    backup = tmp_path / "backup"
    original = os.replace

    def replace_then_fail(source: str, target: str, **kwargs: object) -> None:
        original(source, target, **kwargs)
        if target == "workspace.json":
            raise OSError("interrupted after atomic publication")

    with monkeypatch.context() as patched:
        patched.setattr(os, "replace", replace_then_fail)
        assert (
            main([
                "--project",
                str(root),
                "workspace",
                "migrate",
                *TARGET,
                "--backup-dir",
                str(backup),
                "--confirm-old-writers-stopped",
                "--yes",
                "--json",
            ])
            == 6
        )
    result = json.loads(capsys.readouterr().out)
    assert next(effect for effect in result["effects"] if effect["kind"] == "workspace.migrate")["status"] == "unknown"
    assert result["data"]["result"]["after_protocol"] == "specdock.worktree-writer/v1"
    assert main(["--project", str(root), "workspace", "migrate", *TARGET, "--json"]) == 0
    retry = json.loads(capsys.readouterr().out)
    assert retry["status"] == "unchanged" and retry["effects"] == []
    assert not (root / ".git/spec-dock").exists()


@pytest.mark.parametrize("failure", ["copy", "restore"])
def test_migration_preserves_the_old_declaration_if_real_backup_or_restoration_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    from spec_dock.runtime.infra import migration_backup

    root = legacy_workspace(tmp_path / "consumer")
    before = (root / "spec-dock/workspace.json").read_bytes()
    backup = tmp_path / "backup"
    original = migration_backup.copy_tree_at
    copied: list[str] = []

    def damage(descriptor: int, relative: Path, source: Path) -> None:
        copied.append(str(source))
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
    assert (
        main([
            "--project",
            str(root),
            "workspace",
            "migrate",
            *TARGET,
            "--backup-dir",
            str(backup),
            "--confirm-old-writers-stopped",
            "--yes",
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["restore_verified"] is False
    assert result["effects"][0]["status"] == "unknown"
    assert (root / "spec-dock/workspace.json").read_bytes() == before
    assert backup.is_dir()
    if failure == "restore":
        assert str(backup / "checkout") in copied


def test_migration_in_linked_worktree_preserves_common_git_and_the_other_workspace(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root = legacy_workspace(tmp_path / "main")
    subprocess.run(["git", "-C", str(root), "add", "."], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "old declaration",
        ],
        check=True,
        capture_output=True,
    )
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "-b", "linked", str(linked)], check=True, capture_output=True
    )
    main_before = tree_digest(root)
    linked_before = tree_digest(linked)
    common_before = tree_digest(root / ".git")
    backup = tmp_path / "backup"
    assert (
        main([
            "--project",
            str(linked),
            "workspace",
            "migrate",
            *TARGET,
            "--backup-dir",
            str(backup),
            "--confirm-old-writers-stopped",
            "--yes",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["changed_paths"] == ["spec-dock/workspace.json"]
    assert tree_digest(root) == main_before and tree_digest(root / ".git") == common_before
    assert tree_digest(backup / "checkout") == linked_before
    assert tree_digest(backup / "common-git") == common_before


def test_migration_backs_up_and_restores_real_work_before_changing_only_its_declaration(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root = legacy_workspace(tmp_path / "consumer")
    workspace = root / "spec-dock/workspace.json"
    workspace.chmod(0o640)
    metadata = next((root / "spec-dock/initiatives").rglob(".meta.json"))
    metadata_before = metadata.read_bytes()
    notes = root / "spec-dock/.workbench/private-notes.md"
    notes.parent.mkdir()
    notes.write_bytes(b"uncommitted ignored work\n")
    notes.chmod(0o600)
    document = root / "untracked-draft.md"
    document.write_bytes(b"user-owned untracked body\n")
    active = root / "spec-dock/.agent/active.json"
    active.parent.mkdir()
    active.write_text(
        json.dumps({
            "schema_version": 3,
            "worktree_id": "old-worktree",
            "revision": 1,
            "focus": "initiative",
            "initiative": {"id": "init-00001", "path": "initiatives/init-00001-fixture"},
            "epic": None,
            "issue": None,
        }),
        encoding="utf-8",
    )
    old_active = active.read_bytes()
    before = tree_digest(root)
    git_before = tree_digest(root / ".git")
    original = json.loads(workspace.read_bytes())
    backup = tmp_path / "backup"

    assert (
        main([
            "--project",
            str(root),
            "workspace",
            "migrate",
            *TARGET,
            "--backup-dir",
            str(backup),
            "--confirm-old-writers-stopped",
            "--yes",
            "--json",
        ])
        == 0
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["status"] == "succeeded" and result["data"]["kind"] == "migration"
    data = result["data"]["result"]
    assert data["changed_paths"] == ["spec-dock/workspace.json"]
    assert data["backup_path"] == str(backup) and data["backup_verified"] is True
    assert data["restore_verified"] is True
    assert tree_digest(backup / "checkout") == before
    assert tree_digest(root / ".git") == git_before
    assert (backup / "checkout/spec-dock/.workbench/private-notes.md").read_bytes() == notes.read_bytes()
    assert (backup / "checkout/untracked-draft.md").read_bytes() == document.read_bytes()
    assert stat.S_IMODE(notes.stat().st_mode) == 0o600
    assert metadata.read_bytes() == metadata_before and active.read_bytes() == old_active
    assert data["legacy_active"]["policy"] == "preserved-not-imported"
    assert not (root / "spec-dock/.agent/work-target").exists()
    expected = {**original, "writer_protocol": "specdock.worktree-writer/v1"}
    del expected["control_epoch"]
    assert json.loads(workspace.read_bytes()) == expected
    assert "title" not in expected and "project_linkage" not in expected
    assert stat.S_IMODE(workspace.stat().st_mode) == 0o640
    assert "preserve-without-echo" not in output.out + output.err


@pytest.mark.parametrize("omitted", ["backup", "stop", "yes"])
def test_migration_requires_every_apply_confirmation_before_any_write(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], omitted: str
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root = legacy_workspace(tmp_path / "consumer")
    backup = tmp_path / "backup"
    before = tree_digest(root)
    arguments = [] if omitted == "backup" else ["--backup-dir", str(backup)]
    arguments += [] if omitted == "stop" else ["--confirm-old-writers-stopped"]
    arguments += [] if omitted == "yes" else ["--yes"]
    assert main(["--project", str(root), "workspace", "migrate", *TARGET, *arguments, "--json"]) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == []
    assert tree_digest(root) == before and not backup.exists()


@pytest.mark.parametrize("retired", ["--mapping-file", "--maintenance", "--resume", "--rollback"])
def test_migration_rejects_retired_global_or_recovery_arguments_before_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], retired: str
) -> None:
    assert (
        main(["--project", str(tmp_path / "missing"), "workspace", "migrate", *TARGET, retired, "old-record", "--json"])
        == 2
    )
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED" and result["effects"] == []
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("location", ["current", "git", "relative", "existing", "redirected-parent"])
def test_migration_refuses_an_unsafe_or_existing_backup_without_overwriting_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], location: str
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root = legacy_workspace(tmp_path / "consumer")
    backup = tmp_path / "backup"
    if location == "current":
        backup = root / "backup"
    elif location == "git":
        backup = root / ".git/backup"
    elif location == "relative":
        backup = type(backup)("relative-backup")
    elif location == "existing":
        backup.mkdir()
        (backup / "user-owned.md").write_bytes(b"never overwrite\n")
    elif location == "redirected-parent":
        redirected = tmp_path / "redirect"
        redirected.symlink_to(tmp_path, target_is_directory=True)
        backup = redirected / "backup"
    before = tree_digest(root)
    assert (
        main([
            "--project",
            str(root),
            "workspace",
            "migrate",
            *TARGET,
            "--backup-dir",
            str(backup),
            "--confirm-old-writers-stopped",
            "--yes",
            "--json",
        ])
        == 3
    )
    assert json.loads(capsys.readouterr().out)["effects"] == []
    assert tree_digest(root) == before
    if location == "existing":
        assert (backup / "user-owned.md").read_bytes() == b"never overwrite\n"
    else:
        assert not backup.exists()


def test_migration_refuses_unresolved_remote_journal_without_replay_or_mutating_legacy_data(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root = legacy_workspace(tmp_path / "consumer")
    journal = root / ".git/spec-dock/control/operations" / ("a" * 32) / "journal.json"
    journal.parent.mkdir(parents=True)
    journal.write_text(
        json.dumps({
            "operation_id": "a" * 32,
            "command": "scope close",
            "effect_plan": ["remote"],
            "request_fingerprint": "old",
            "phase": "remote-intent",
            "engine_digest": "old",
            "writer_epoch": 1,
            "sequence": 0,
            "terminal_status": "pending",
            "backup_refs": [],
            "fixed_targets": [],
            "before_revisions": [],
            "effects": [{"id": "remote", "kind": "remote", "target": "private-target", "status": "unknown"}],
        }),
        encoding="utf-8",
    )
    before = tree_digest(root)
    backup = tmp_path / "backup"

    def no_github(*_args: object, **_kwargs: object) -> object:
        pytest.fail("migration cannot reconcile or replay a historical remote request")

    monkeypatch.setattr("spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", no_github)
    assert (
        main([
            "--project",
            str(root),
            "workspace",
            "migrate",
            *TARGET,
            "--backup-dir",
            str(backup),
            "--confirm-old-writers-stopped",
            "--yes",
            "--json",
        ])
        == 3
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["error"]["code"] == "LEGACY_IMPACT_UNVERIFIED" and result["effects"] == []
    assert "private-target" not in output.out + output.err
    assert tree_digest(root) == before and not backup.exists()


def test_migration_preserves_symlink_itself_without_copying_arbitrary_targets(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = legacy_workspace(tmp_path / "consumer")
    external = tmp_path / "outside"
    external.mkdir()
    (external / "private.txt").write_bytes(b"arbitrary external data must not be traversed")
    link = root / "untracked-link"
    link.symlink_to(external, target_is_directory=True)
    backup = tmp_path / "backup"
    assert (
        main([
            "--project",
            str(root),
            "workspace",
            "migrate",
            *TARGET,
            "--backup-dir",
            str(backup),
            "--confirm-old-writers-stopped",
            "--yes",
            "--json",
        ])
        == 0
    )
    assert json.loads(capsys.readouterr().out)["data"]["result"]["restore_verified"] is True
    copied = backup / "checkout/untracked-link"
    assert copied.is_symlink() and copied.readlink() == link.readlink()
    assert (external / "private.txt").read_bytes() == b"arbitrary external data must not be traversed"


def test_migration_preserves_240_scope_metadata_bytes_including_two_legacy_spelled_github_ids(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.application.workspace_structure import inspect_structure
    from spec_dock.runtime.infra import scope_tree

    root = legacy_workspace(tmp_path / "consumer")
    workspace = root / "spec-dock"
    existing = next((workspace / "initiatives").iterdir())
    template = json.loads((existing / ".meta.json").read_bytes())
    renamed = existing.with_name("init-local-00001-fixture")
    existing.rename(renamed)
    first = {**template, "id": "init-local-00001", "future_optional": {"retain": True}}
    (renamed / ".meta.json").write_text(json.dumps(first), encoding="utf-8")
    second = workspace / "initiatives/init-local-00002-fixture"
    second.mkdir()
    (second / ".meta.json").write_text(
        json.dumps({
            **first,
            "id": "init-local-00002",
            "github": {"issue_number": 2, "repo_owner": "example", "repo_name": "repo"},
        }),
        encoding="utf-8",
    )
    epics = []
    for number in range(3, 7):
        initiative = renamed if number % 2 else second
        initiative_id = "init-local-00001" if number % 2 else "init-local-00002"
        epic_id = f"epic-{number:05}"
        epic = initiative / "epics" / f"{epic_id}-fixture"
        epic.mkdir(parents=True)
        (epic / ".meta.json").write_text(
            json.dumps({
                **first,
                "id": epic_id,
                "type": "epic",
                "parent_id": initiative_id,
                "initiative_id": initiative_id,
                "github": {"issue_number": number, "repo_owner": "example", "repo_name": "repo"},
            }),
            encoding="utf-8",
        )
        epics.append((epic, epic_id, initiative_id))
    for number in range(7, 241):
        epic, epic_id, initiative_id = epics[number % 4]
        issue_id = f"iss-{number:05}"
        issue = epic / "issues" / f"{issue_id}-fixture"
        issue.mkdir(parents=True)
        (issue / ".meta.json").write_text(
            json.dumps({
                **first,
                "id": issue_id,
                "type": "issue",
                "parent_id": epic_id,
                "initiative_id": initiative_id,
                "epic_id": epic_id,
                "github": {"issue_number": number, "repo_owner": "example", "repo_name": "repo"},
            }),
            encoding="utf-8",
        )
        (issue / "requirement.md").write_bytes(b"user-authored requirement; preserve exactly\n")
    metadata = {path.relative_to(root): path.read_bytes() for path in workspace.rglob(".meta.json")}
    assert len(metadata) == 240
    metadata_reads: list[Path] = []
    original = scope_tree.read_guarded_json

    def observed_read(path: Path) -> object:
        metadata_reads.append(path)
        return original(path)

    with monkeypatch.context() as patched:
        patched.setattr(scope_tree, "read_guarded_json", observed_read)
        views, findings = inspect_structure(root)
    assert len(views) == 240 and findings == ()
    assert len(metadata_reads) <= 2 * len(metadata), "Artifact validation must reuse one structural observation"
    backup = tmp_path / "backup"
    assert (
        main([
            "--project",
            str(root),
            "workspace",
            "migrate",
            *TARGET,
            "--backup-dir",
            str(backup),
            "--confirm-old-writers-stopped",
            "--yes",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["scope_count"] == 240
    assert result["data"]["result"]["changed_paths"] == ["spec-dock/workspace.json"]
    assert {path.relative_to(root): path.read_bytes() for path in workspace.rglob(".meta.json")} == metadata
    assert {
        (path.relative_to(backup / "checkout")): path.read_bytes()
        for path in (backup / "checkout/spec-dock").rglob(".meta.json")
    } == metadata


@pytest.mark.skipif(os.name != "posix", reason="native SIGKILL at an atomic-publication boundary")
@pytest.mark.parametrize("boundary", ["before", "after"])
def test_migration_fresh_process_does_not_resume_a_process_killed_at_publication(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], boundary: str
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root = legacy_workspace(tmp_path / "consumer")
    workspace = root / "spec-dock/workspace.json"
    original_bytes = workspace.read_bytes()
    git_before = tree_digest(root / ".git")
    backup = tmp_path / "backup"
    child_code = """
import os, signal, sys
from spec_dock.cli import main
from spec_dock.runtime.application import direct_migration
original = direct_migration.replace_existing_json
boundary = sys.argv[1]
def hold():
    os.write(1, b'READY\\n')
    signal.pause()
def replace(*args, **kwargs):
    if boundary == 'before':
        verify = kwargs['before_replace']
        def before():
            verify()
            hold()
        kwargs['before_replace'] = before
    result = original(*args, **kwargs)
    if boundary == 'after':
        hold()
    return result
direct_migration.replace_existing_json = replace
sys.exit(main(sys.argv[2:]))
"""
    process = subprocess.Popen(
        [
            sys.executable,
            "-c",
            child_code,
            boundary,
            "--project",
            str(root),
            "workspace",
            "migrate",
            *TARGET,
            "--backup-dir",
            str(backup),
            "--confirm-old-writers-stopped",
            "--yes",
            "--json",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        assert process.stdout is not None
        ready, _, _ = select.select([process.stdout], [], [], 15)
        assert ready and process.stdout.readline() == b"READY\n", "child must reach the fixed publication boundary"
    finally:
        process.kill()
        stdout, stderr = process.communicate(timeout=10)
    assert process.returncode == -9 and not stdout and not stderr
    protocol = json.loads(workspace.read_bytes())["writer_protocol"]
    assert protocol == ("specdock.writer/v1" if boundary == "before" else "specdock.worktree-writer/v1")
    assert (backup / "checkout/spec-dock/workspace.json").read_bytes() == original_bytes
    assert tree_digest(root / ".git") == git_before
    assert (
        main([
            "--project",
            str(root),
            "workspace",
            "migrate",
            *TARGET,
            *(["--dry-run"] if boundary == "before" else []),
            "--json",
        ])
        == 0
    )
    fresh = json.loads(capsys.readouterr().out)
    assert fresh["status"] == ("planned" if boundary == "before" else "unchanged")
    assert not (root / "spec-dock/.agent/work-target").exists()
    assert not (root / ".git/spec-dock").exists()


def test_migration_detects_an_unrelated_user_edit_after_backup_and_leaves_it_intact(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.application import direct_migration

    root = legacy_workspace(tmp_path / "consumer")
    workspace_before = (root / "spec-dock/workspace.json").read_bytes()
    body = root / "untracked-user-work.md"
    body.write_bytes(b"before backup\n")
    backup = tmp_path / "backup"
    original = direct_migration.create_verified_backup

    def concurrent_edit(*args: object, **kwargs: object) -> object:
        verified = original(*args, **kwargs)
        body.write_bytes(b"concurrent user edit\n")
        return verified

    monkeypatch.setattr(direct_migration, "create_verified_backup", concurrent_edit)
    assert (
        main([
            "--project",
            str(root),
            "workspace",
            "migrate",
            *TARGET,
            "--backup-dir",
            str(backup),
            "--confirm-old-writers-stopped",
            "--yes",
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"][-1]["status"] == "not_attempted"
    assert body.read_bytes() == b"concurrent user edit\n"
    assert (backup / "checkout/untracked-user-work.md").read_bytes() == b"before backup\n"
    assert (root / "spec-dock/workspace.json").read_bytes() == workspace_before


@pytest.mark.parametrize("phase", ["backup", "before-publication", "after-publication"])
def test_migration_retains_native_git_errors_after_a_confirmed_backup_or_publication(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, phase: str
) -> None:
    from spec_dock.runtime.application import direct_migration
    from spec_dock.runtime.infra.git_process import GitProcessError

    root = legacy_workspace(tmp_path / "consumer")
    backup = tmp_path / "backup"
    original_context = direct_migration.resolve_context
    original_backup = direct_migration.create_verified_backup
    backup_returned = False

    def backup_and_mark(*args: object, **kwargs: object) -> object:
        nonlocal backup_returned
        verified = original_backup(*args, **kwargs)
        backup_returned = True
        return verified

    def context_or_error(*args: object, **kwargs: object) -> object:
        published = (
            json.loads((root / "spec-dock/workspace.json").read_bytes())["writer_protocol"]
            == "specdock.worktree-writer/v1"
        )
        fail = (
            (phase == "backup" and backup.exists())
            or (phase == "before-publication" and backup_returned)
            or (phase == "after-publication" and published)
        )
        if fail:
            raise GitProcessError(
                ("git", "-C", str(root), "worktree", "list"),
                b"fatal: native inventory failed\nsecond native line\n",
                128,
                stdout=b"native stdout\n",
            )
        return original_context(*args, **kwargs)

    monkeypatch.setattr(direct_migration, "create_verified_backup", backup_and_mark)
    monkeypatch.setattr(direct_migration, "resolve_context", context_or_error)
    assert (
        main([
            "--project",
            str(root),
            "workspace",
            "migrate",
            *TARGET,
            "--backup-dir",
            str(backup),
            "--confirm-old-writers-stopped",
            "--yes",
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "GIT_FAILED"
    details = result["error"]["details"]["git"]
    assert details["returncode"] == 128 and details["stdout"] == "native stdout\n"
    assert details["stderr"] == "fatal: native inventory failed\nsecond native line\n"
    assert result["effects"][-1]["status"] == ("succeeded" if phase == "after-publication" else "not_attempted")
