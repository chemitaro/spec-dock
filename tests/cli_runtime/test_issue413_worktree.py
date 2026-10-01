"""Explicit native worktree operations do not use SpecDock registrations."""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from tests.cli_runtime.test_issue413_active import select_fixture
from tests.cli_runtime.test_issue413_contract import add_scope
from tests.cli_runtime.test_issue413_work_start import committed_workspace

if TYPE_CHECKING:
    from pathlib import Path


def test_list_uses_native_inventory_without_scope_metadata_or_control(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    head = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    other = tmp_path / "linked with space"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "-b", "parallel", str(other)], check=True, capture_output=True
    )
    (root / "spec-dock/initiatives/init-00001-fixture/.meta.json").write_bytes(b"invalid unrelated metadata")
    assert main(["--project", str(root), "worktree", "list", "--json"]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == "" and result["effects"] == []
    assert result["data"] == {
        "kind": "worktree-list",
        "result": {
            "items": [
                {"path": str(root), "branch": "main", "head": head, "bare": False, "locked": False, "prunable": False},
                {
                    "path": str(other),
                    "branch": "parallel",
                    "head": head,
                    "bare": False,
                    "locked": False,
                    "prunable": False,
                },
            ]
        },
    }
    assert not (root / ".git/spec-dock").exists()
    assert not (other / "spec-dock/.agent").exists()


@pytest.mark.parametrize("reference", ["planning", "wt:wt1", "relative/path"])
def test_show_rejects_retired_aliases_and_relative_paths_before_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], reference: str
) -> None:
    assert main(["--project", str(tmp_path / "missing"), "worktree", "show", reference, "--json"]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("leaf", ["create", "bootstrap"])
def test_worktree_rejects_retired_recovery_before_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], leaf: str
) -> None:
    options = (
        ["planning", "--base", "HEAD", "--root", str(tmp_path / "worktrees"), "--recover", "wt1"]
        if leaf == "create"
        else [str(tmp_path / "linked"), "--recover"]
    )
    assert main(["--project", str(tmp_path / "missing"), "worktree", leaf, *options, "--json"]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED" and result["effects"] == []
    assert list(tmp_path.iterdir()) == []


def test_show_resolves_an_explicit_native_path_without_reading_the_target_workspace(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    other = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "-b", "parallel", str(other)], check=True, capture_output=True
    )
    (other / "spec-dock/workspace.json").unlink()
    assert main(["--project", str(root), "worktree", "show", str(other), "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["kind"] == "worktree" and result["effects"] == []
    observed = result["data"]["result"]
    assert observed["path"] == str(other) and observed["branch"] == "parallel"
    assert (
        observed["head"]
        == subprocess.run(
            ["git", "-C", str(other), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
        ).stdout.strip()
    )
    assert observed["changed"] is False
    assert observed["observed"]["bare"] is False and observed["observed"]["locked"] is False
    assert not (root / ".git/spec-dock").exists()


def test_create_uses_the_explicit_name_and_fixed_base_without_registration_or_bootstrap(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    head = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    container = tmp_path / "worktrees"
    created = container / "planning"
    assert (
        main([
            "--project",
            str(root),
            "worktree",
            "create",
            "planning",
            "--base",
            "HEAD",
            "--root",
            str(container),
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "succeeded" and result["data"]["kind"] == "worktree"
    data = result["data"]["result"]
    assert data["path"] == str(created) and data["branch"] == "worktree/planning"
    assert data["head"] == head and data["changed"] is True
    assert (
        subprocess.run(
            ["git", "-C", str(created), "branch", "--show-current"], check=True, capture_output=True, text=True
        ).stdout.strip()
        == "worktree/planning"
    )
    assert (created / "spec-dock/workspace.json").read_bytes() == (root / "spec-dock/workspace.json").read_bytes()
    assert not (created / "spec-dock/.agent").exists() and not (root / ".git/spec-dock").exists()
    assert not (created / "bootstrap-ran").exists()
    assert (
        subprocess.run(
            ["git", "-C", str(root), "branch", "--show-current"], check=True, capture_output=True, text=True
        ).stdout.strip()
        == "main"
    )


def test_create_dry_run_plans_the_fixed_target_without_creating_a_directory_or_branch(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    container = tmp_path / "worktrees"
    assert (
        main([
            "--project",
            str(root),
            "worktree",
            "create",
            "planning",
            "--base",
            "HEAD",
            "--root",
            str(container),
            "--dry-run",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "planned" and result["data"]["result"]["changed"] is False
    assert result["data"]["result"]["can_apply"] is True and result["data"]["result"]["blockers"] == []
    assert result["data"]["result"]["path"] == str(container / "planning")
    assert not container.exists()
    assert (
        subprocess.run(
            ["git", "-C", str(root), "show-ref", "--verify", "--quiet", "refs/heads/worktree/planning"],
            capture_output=True,
        ).returncode
        == 1
    )
    assert all(effect["status"] == "planned" for effect in result["effects"])


@pytest.mark.parametrize("dry_run", [False, True])
def test_create_handles_explicit_nested_placement_and_dry_run_keeps_all_missing_directories_absent(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], dry_run: bool
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    parent = tmp_path / "new-parent"
    container = parent / "worktrees"
    options = ["--dry-run"] if dry_run else []
    assert (
        main([
            "--project",
            str(root),
            "worktree",
            "create",
            "planning",
            "--base",
            "HEAD",
            "--root",
            str(container),
            *options,
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["path"] == str(container / "planning")
    assert (container / "planning").exists() is not dry_run
    assert parent.exists() is not dry_run
    assert [effect["target"] for effect in result["effects"] if effect["kind"] == "worktree-directory"] == [
        str(parent),
        str(container),
    ]
    assert all(effect["status"] == ("planned" if dry_run else "succeeded") for effect in result["effects"])


def test_create_requires_an_explicit_name_before_reading_the_project(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert (
        main([
            "--project",
            str(tmp_path / "missing"),
            "worktree",
            "create",
            "--base",
            "HEAD",
            "--root",
            str(tmp_path / "worktrees"),
            "--json",
        ])
        == 2
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("override", [False, True])
def test_create_uses_configured_root_with_explicit_root_taking_precedence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], override: bool
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    configured = tmp_path / "configured-worktrees"
    explicit = tmp_path / "explicit-worktrees"
    monkeypatch.setenv("SPEC_DOCK_WORKTREE_ROOT", str(configured))
    options = ["--root", str(explicit)] if override else []
    assert main(["--project", str(root), "worktree", "create", "planning", "--base", "HEAD", *options, "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    container = explicit if override else configured
    assert result["data"]["result"]["path"] == str(container / "planning")
    assert (container / "planning").is_dir()
    assert not (configured if override else explicit).exists()


def test_create_refuses_dirty_source_without_stashing_or_creating_a_branch(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    note = root / "untracked.txt"
    note.write_bytes(b"must remain")
    container = tmp_path / "worktrees"
    assert (
        main([
            "--project",
            str(root),
            "worktree",
            "create",
            "planning",
            "--base",
            "HEAD",
            "--root",
            str(container),
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and not container.exists()
    assert note.read_bytes() == b"must remain"
    assert (
        subprocess.run(
            ["git", "-C", str(root), "show-ref", "--verify", "--quiet", "refs/heads/worktree/planning"],
            capture_output=True,
        ).returncode
        == 1
    )


@pytest.mark.skipif(os.name != "posix", reason="native reference-transaction hook")
def test_create_stops_after_a_branch_hook_changes_source_selection_and_preserves_the_git_effect(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    hook = root / ".git/hooks/reference-transaction"
    hook.write_text(f'#!/bin/sh\nif [ "$1" = committed ]; then rm -f {shlex.quote(str(record))}; fi\nexit 0\n')
    hook.chmod(0o700)
    container = tmp_path / "worktrees"
    assert (
        main([
            "--project",
            str(root),
            "worktree",
            "create",
            "planning",
            "--base",
            "HEAD",
            "--root",
            str(container),
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "partial" and result["data"]["result"]["changed"] is True
    assert "direct selection changed" in result["error"]["message"]
    assert any(
        effect["kind"] == "git.branch.create" and effect["status"] == "succeeded" for effect in result["effects"]
    )
    assert any(
        effect["kind"] == "git.worktree.add" and effect["status"] == "not_attempted" for effect in result["effects"]
    )
    assert not record.exists() and not (container / "planning").exists()
    assert (
        subprocess.run(
            ["git", "-C", str(root), "show-ref", "--verify", "--quiet", "refs/heads/worktree/planning"],
            capture_output=True,
        ).returncode
        == 0
    )


def test_create_refuses_a_missing_path_still_present_in_native_inventory_without_creating_a_ref(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    container = tmp_path / "worktrees"
    path = container / "planning"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "-b", "older", str(path)], check=True, capture_output=True
    )
    shutil.rmtree(path)
    assert (
        main([
            "--project",
            str(root),
            "worktree",
            "create",
            "planning",
            "--base",
            "HEAD",
            "--root",
            str(container),
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and not path.exists()
    assert (
        subprocess.run(
            ["git", "-C", str(root), "show-ref", "--verify", "--quiet", "refs/heads/worktree/planning"],
            capture_output=True,
        ).returncode
        == 1
    )


@pytest.mark.skipif(os.name != "posix", reason="native post-checkout hook")
def test_create_reports_a_confirmed_worktree_even_when_native_git_returns_a_hook_failure(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    hook = root / ".git/hooks/post-checkout"
    hook.write_text("#!/bin/sh\nprintf 'fixture worktree checkout hook failed\\nsecond hook line\\n' >&2\nexit 17\n")
    hook.chmod(0o700)
    container = tmp_path / "worktrees"
    container.mkdir()
    path = container / "planning"
    assert (
        main([
            "--project",
            str(root),
            "worktree",
            "create",
            "planning",
            "--base",
            "HEAD",
            "--root",
            str(container),
            "--json",
        ])
        == 6
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == "" and result["error"]["code"] == "GIT_FAILED"
    assert "fixture worktree checkout hook failed\nsecond hook line\n" in result["error"]["details"]["git"]["stderr"]
    assert result["error"]["details"]["git"]["returncode"] != 0
    assert result["effects"] == [
        {"kind": "git.branch.create", "status": "succeeded", "target": "worktree/planning"},
        {"kind": "git.worktree.add", "status": "succeeded", "target": str(path)},
    ]
    assert path.is_dir() and (path / "spec-dock/workspace.json").exists()
    assert result["data"]["result"]["observed"]["branch"] == "worktree/planning"
    assert result["data"]["result"]["changed"] is True
    assert result["recovery"]["can_rollback"] is False


def test_unknown_placement_directory_creation_is_partial_without_attempting_git_mutations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    container = tmp_path / "worktrees"
    real_mkdir = os.mkdir

    def mkdir(path, mode=0o777, *, dir_fd=None):
        real_mkdir(path, mode, dir_fd=dir_fd)
        if path == "worktrees" and dir_fd is not None:
            raise OSError("placement directory reply was lost")

    monkeypatch.setattr(os, "mkdir", mkdir)
    assert (
        main([
            "--project",
            str(root),
            "worktree",
            "create",
            "planning",
            "--base",
            "HEAD",
            "--root",
            str(container),
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [
        {"kind": "worktree-directory", "status": "unknown", "target": str(container)},
        {"kind": "git.branch.create", "status": "not_attempted", "target": "worktree/planning"},
        {"kind": "git.worktree.add", "status": "not_attempted", "target": str(container / "planning")},
    ]
    assert container.is_dir() and list(container.iterdir()) == []
    assert (
        subprocess.run(
            ["git", "-C", str(root), "show-ref", "--verify", "--quiet", "refs/heads/worktree/planning"],
            capture_output=True,
        ).returncode
        == 1
    )


def test_create_refuses_a_scope_backend_guard_without_a_scope_target_before_any_effect(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    container = tmp_path / "worktrees"
    assert (
        main([
            "--project",
            str(root),
            "worktree",
            "create",
            "planning",
            "--base",
            "HEAD",
            "--root",
            str(container),
            "--expect-backend",
            "github",
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert "one existing Scope target" in result["error"]["message"]
    assert result["effects"] == [] and not container.exists()
    assert (
        subprocess.run(
            ["git", "-C", str(root), "show-ref", "--verify", "--quiet", "refs/heads/worktree/planning"],
            capture_output=True,
        ).returncode
        == 1
    )


def test_create_checks_the_captured_direct_scope_for_expect_current_without_changing_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    add_scope(root, "epic-00002", "epic", "init-00001", root / "spec-dock/initiatives/init-00001-fixture")
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
            "second scope fixture",
        ],
        check=True,
        capture_output=True,
    )
    record = select_fixture(root)
    before = record.read_bytes()
    container = tmp_path / "worktrees"
    assert (
        main([
            "--project",
            str(root),
            "worktree",
            "create",
            "planning",
            "--base",
            "HEAD",
            "--root",
            str(container),
            "--expect-current",
            "epic-00002",
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert "direct target does not match" in result["error"]["message"]
    assert result["effects"] == [] and not container.exists() and record.read_bytes() == before


@pytest.mark.parametrize("leaf", ["list", "show"])
def test_native_queries_do_not_silently_ignore_an_inapplicable_backend_guard(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], leaf: str
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    target = [str(root)] if leaf == "show" else []
    assert main(["--project", str(root), "worktree", leaf, *target, "--expect-backend", "github", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert "one existing Scope target" in result["error"]["message"] and result["effects"] == []


@pytest.mark.parametrize("leaf", ["list", "show"])
def test_native_queries_compare_expect_current_with_the_own_worktree_selection(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], leaf: str
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    target = [str(root)] if leaf == "show" else []
    assert main(["--project", str(root), "worktree", leaf, *target, "--expect-current", "init-00001", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert "direct target does not match" in result["error"]["message"] and result["effects"] == []
    record = select_fixture(root)
    before = record.read_bytes()
    assert (
        main(["--project", str(root), "worktree", leaf, *target, "--expect-current", "gh:example/repo#1", "--json"])
        == 0
    )
    assert json.loads(capsys.readouterr().out)["effects"] == [] and record.read_bytes() == before


def test_create_does_not_replace_an_explicit_empty_root_with_an_environment_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    configured = tmp_path / "configured-worktrees"
    monkeypatch.setenv("SPEC_DOCK_WORKTREE_ROOT", str(configured))
    assert (
        main(["--project", str(root), "worktree", "create", "planning", "--base", "HEAD", "--root", "", "--json"]) == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and not configured.exists()


@pytest.mark.skipif(os.name != "posix", reason="native reference-transaction hook")
def test_create_rechecks_the_new_branch_tip_before_attaching_a_worktree(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    previous = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
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
            "--allow-empty",
            "-qm",
            "second commit",
        ],
        check=True,
        capture_output=True,
    )
    marker = root / ".git/fixture-hook-ran"
    hook = root / ".git/hooks/reference-transaction"
    hook.write_text(
        f'#!/bin/sh\nif [ "$1" = committed ] && [ ! -e {shlex.quote(str(marker))} ]; then\n'
        f"touch {shlex.quote(str(marker))}\n"
        f"git -C {shlex.quote(str(root))} update-ref refs/heads/worktree/planning {previous}\nfi\nexit 0\n"
    )
    hook.chmod(0o700)
    container = tmp_path / "worktrees"
    assert (
        main([
            "--project",
            str(root),
            "worktree",
            "create",
            "planning",
            "--base",
            "HEAD",
            "--root",
            str(container),
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "partial"
    assert "branch no longer matches" in result["error"]["message"]
    assert any(
        effect["kind"] == "git.branch.create" and effect["status"] == "succeeded" for effect in result["effects"]
    )
    assert any(
        effect["kind"] == "git.worktree.add" and effect["status"] == "not_attempted" for effect in result["effects"]
    )
    assert not (container / "planning").exists()
    assert (
        subprocess.run(
            ["git", "-C", str(root), "rev-parse", "refs/heads/worktree/planning"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        == previous
    )


@pytest.mark.skipif(os.name != "posix", reason="native post-checkout hook")
def test_create_preserves_a_hook_modified_worktree_and_reports_partial_instead_of_success(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    hook = root / ".git/hooks/post-checkout"
    hook.write_text('#!/bin/sh\nprintf "hook output must remain\\n" > hook-note.txt\nexit 0\n')
    hook.chmod(0o700)
    container = tmp_path / "worktrees"
    assert (
        main([
            "--project",
            str(root),
            "worktree",
            "create",
            "planning",
            "--base",
            "HEAD",
            "--root",
            str(container),
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert "created worktree is not clean" in result["error"]["message"]
    assert result["data"]["result"]["changed"] is True
    assert any(effect["kind"] == "git.worktree.add" and effect["status"] == "succeeded" for effect in result["effects"])
    assert (container / "planning/hook-note.txt").read_text() == "hook output must remain\n"
    assert result["recovery"]["can_rollback"] is False


@pytest.mark.skipif(os.name != "posix", reason="native reference-transaction hook")
def test_create_does_not_adopt_a_target_directory_created_by_an_actor_after_branch_creation(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    container = tmp_path / "worktrees"
    container.mkdir()
    target = container / "planning"
    hook = root / ".git/hooks/reference-transaction"
    hook.write_text(
        f'#!/bin/sh\nif [ "$1" = committed ] && [ ! -e {shlex.quote(str(target))} ]; then '
        f"mkdir {shlex.quote(str(target))}; fi\nexit 0\n"
    )
    hook.chmod(0o700)
    assert (
        main([
            "--project",
            str(root),
            "worktree",
            "create",
            "planning",
            "--base",
            "HEAD",
            "--root",
            str(container),
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [
        {"kind": "git.branch.create", "status": "succeeded", "target": "worktree/planning"},
        {"kind": "git.worktree.add", "status": "not_attempted", "target": str(target)},
    ]
    assert target.is_dir() and list(target.iterdir()) == []
    inventory = subprocess.run(
        ["git", "-C", str(root), "worktree", "list", "--porcelain"], check=True, capture_output=True, text=True
    ).stdout
    assert str(target) not in inventory


def test_native_worktree_help_describes_name_path_and_git_inventory_without_retired_control(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["help", "worktree", "create"]) == 0
    create = capsys.readouterr().out
    assert "worktree/NAME" in create and "SPEC_DOCK_WORKTREE_ROOT" in create
    assert "--recover" not in create and "operation record" not in create
    assert main(["help", "worktree", "list"]) == 0
    listed = capsys.readouterr().out
    assert "native Git" in listed and "installation control" not in listed
    assert "Worktree ID" not in listed and "control state" not in listed
    assert main(["help", "worktree", "show"]) == 0
    shown = capsys.readouterr().out
    assert "/absolute/worktree" in shown and "installation control" not in shown
    assert "worktree ID" not in shown and "Worktree ID" not in shown


def test_create_refuses_a_direct_record_copied_from_another_physical_clone_without_effects(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    foreign = committed_workspace(tmp_path / "other-clone")
    record = select_fixture(root)
    record.write_bytes(select_fixture(foreign).read_bytes())
    before = record.read_bytes()
    container = tmp_path / "worktrees"
    assert (
        main([
            "--project",
            str(root),
            "worktree",
            "create",
            "planning",
            "--base",
            "HEAD",
            "--root",
            str(container),
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert "physical identity" in result["error"]["message"]
    assert result["effects"] == [] and not container.exists() and record.read_bytes() == before


@pytest.mark.skipif(os.name != "posix", reason="native directory replacement during fsync")
def test_create_stops_if_a_new_placement_parent_is_replaced_before_the_next_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    parent = tmp_path / "new-parent"
    container = parent / "worktrees"
    retained = tmp_path / "retained-parent"
    native_fsync = os.fsync
    boundary_identity = tmp_path.stat().st_ino

    def fsync(descriptor: int) -> None:
        if os.fstat(descriptor).st_ino == boundary_identity and parent.is_dir() and not retained.exists():
            parent.rename(retained)
            parent.mkdir()
        native_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", fsync)
    assert (
        main([
            "--project",
            str(root),
            "worktree",
            "create",
            "planning",
            "--base",
            "HEAD",
            "--root",
            str(container),
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [
        {"kind": "worktree-directory", "status": "succeeded", "target": str(parent)},
        {"kind": "worktree-directory", "status": "not_attempted", "target": str(container)},
        {"kind": "git.branch.create", "status": "not_attempted", "target": "worktree/planning"},
        {"kind": "git.worktree.add", "status": "not_attempted", "target": str(container / "planning")},
    ]
    assert parent.is_dir() and list(parent.iterdir()) == []
    assert retained.is_dir() and list(retained.iterdir()) == []


@pytest.mark.parametrize("from_linked", [False, True])
def test_list_reports_native_locked_detached_and_missing_worktrees_from_either_root(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], from_linked: bool
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    locked, detached, missing = (tmp_path / name for name in ("locked", "detached", "missing"))
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "-b", "parallel", str(locked)], check=True, capture_output=True
    )
    subprocess.run(["git", "-C", str(root), "worktree", "lock", str(locked)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(detached), "HEAD"], check=True, capture_output=True
    )
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "-b", "old", str(missing)], check=True, capture_output=True
    )
    shutil.rmtree(missing)
    assert main(["--project", str(locked if from_linked else root), "worktree", "list", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    rows = {item["path"]: item for item in result["data"]["result"]["items"]}
    assert rows[str(locked)]["locked"] is True and rows[str(locked)]["branch"] == "parallel"
    assert rows[str(detached)]["branch"] is None and rows[str(detached)]["bare"] is False
    assert rows[str(missing)]["prunable"] is True and rows[str(missing)]["branch"] == "old"
    assert result["effects"] == [] and not (root / ".git/spec-dock").exists()
    assert not missing.exists()


@pytest.mark.parametrize("mode", ["other-clone", "subdirectory", "symlink"])
def test_show_refuses_paths_that_are_not_an_exact_native_worktree_of_this_clone(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], mode: str
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    if mode == "other-clone":
        target = committed_workspace(tmp_path / "other-clone")
    elif mode == "subdirectory":
        target = root / "spec-dock"
    else:
        target = tmp_path / "alias"
        target.symlink_to(root, target_is_directory=True)
    assert main(["--project", str(root), "worktree", "show", str(target), "--json"]) == (5 if mode == "symlink" else 4)
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "failed" and result["effects"] == []
    assert (root / "spec-dock/workspace.json").is_file() and not (root / ".git/spec-dock").exists()


def test_known_directory_collision_preserves_the_actor_path_without_claiming_an_uncertain_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    container = tmp_path / "worktrees"
    native_mkdir = os.mkdir

    def mkdir(path, mode=0o777, *, dir_fd=None):
        native_mkdir(path, mode, dir_fd=dir_fd)
        if path == "worktrees" and dir_fd is not None:
            raise FileExistsError("another actor created the placement")

    monkeypatch.setattr(os, "mkdir", mkdir)
    assert (
        main([
            "--project",
            str(root),
            "worktree",
            "create",
            "planning",
            "--base",
            "HEAD",
            "--root",
            str(container),
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert all(effect["status"] == "not_attempted" for effect in result["effects"])
    assert container.is_dir() and list(container.iterdir()) == []
    assert (
        subprocess.run(
            ["git", "-C", str(root), "show-ref", "--verify", "--quiet", "refs/heads/worktree/planning"],
            capture_output=True,
        ).returncode
        == 1
    )
