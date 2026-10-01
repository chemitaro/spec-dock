"""Native worktree CLI uses explicit paths and retains branches after removal."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.cli_runtime.test_issue413_work_start import committed_workspace

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_worktree_list_and_show_use_native_identity_without_scope_or_control_read(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    (root / "spec-dock/initiatives/init-00001-fixture/.meta.json").write_bytes(b"unreadable unrelated metadata")
    before = tree_digest(root)
    prefix = ["--project", str(root), "worktree"]
    assert main([*prefix, "list", "--json"]) == 0
    listed = json.loads(capsys.readouterr().out)
    items = listed["data"]["result"]["items"]
    assert len(items) == 1 and items[0]["path"] == str(root) and items[0]["branch"] == "main"
    assert listed["effects"] == []
    assert main([*prefix, "show", str(root), "--json"]) == 0
    shown = json.loads(capsys.readouterr().out)
    assert shown["data"]["result"]["path"] == str(root)
    assert shown["data"]["result"]["head"] == items[0]["head"] and shown["data"]["result"]["branch"] == "main"
    assert shown["effects"] == [] and tree_digest(root) == before
    assert not (root / ".git/spec-dock").exists() and not (root / "spec-dock/.agent").exists()


def test_worktree_create_and_remove_preview_without_writes_and_retain_the_branch(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    container = tmp_path / "worktrees"
    target = container / "planning"
    command = [
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
    ]
    before = tree_digest(root)
    assert main([*command, "--dry-run"]) == 0
    preview = json.loads(capsys.readouterr().out)
    assert preview["status"] == "planned" and preview["data"]["result"]["path"] == str(target)
    assert preview["data"]["result"]["changed"] is False and preview["data"]["result"]["can_apply"] is True
    assert not container.exists() and tree_digest(root) == before
    assert main(command) == 0
    created = json.loads(capsys.readouterr().out)
    assert (
        created["data"]["result"]["path"] == str(target) and created["data"]["result"]["branch"] == "worktree/planning"
    )
    assert target.is_dir() and created["data"]["result"]["changed"] is True
    branch_tip = subprocess.check_output(["git", "-C", str(root), "rev-parse", "refs/heads/worktree/planning"])
    remove = ["--project", str(root), "worktree", "remove", str(target), "--json"]
    current = tree_digest(root)
    target_before = tree_digest(target)
    assert main(remove) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == []
    assert tree_digest(root) == current and tree_digest(target) == target_before
    assert main([*remove, "--dry-run"]) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["status"] == "planned" and plan["data"]["result"]["can_apply"] is True
    assert tree_digest(root) == current and tree_digest(target) == target_before
    assert main([*remove, "--yes"]) == 0
    removed = json.loads(capsys.readouterr().out)
    assert removed["data"]["result"]["path"] == str(target) and removed["data"]["result"]["changed"] is True
    assert not target.exists()
    assert subprocess.check_output(["git", "-C", str(root), "rev-parse", "refs/heads/worktree/planning"]) == branch_tip
    assert not (root / ".git/spec-dock").exists()


def test_worktree_bootstrap_is_explicit_and_preview_or_offline_never_runs_make(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    target = tmp_path / "trees/planning"
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
            str(target.parent),
            "--json",
        ])
        == 0
    )
    capsys.readouterr()
    (target / "Makefile").write_text("init:\n\t@printf 'one run\\n' >> bootstrap-ran\n", encoding="utf-8")
    command = ["--project", str(root), "worktree", "bootstrap", str(target), "--json"]
    before = tree_digest(root)
    target_before = tree_digest(target)
    assert main([*command, "--dry-run"]) == 0
    preview = json.loads(capsys.readouterr().out)
    assert preview["status"] == "planned" and preview["data"]["result"]["can_apply"] is True
    assert main([*command, "--offline", "--yes"]) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == []
    assert tree_digest(root) == before and tree_digest(target) == target_before
    assert not (target / "bootstrap-ran").exists()
    assert main([*command, "--yes"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["observed"]["started"] is True
    assert result["data"]["result"]["observed"]["returncode"] == 0
    assert (target / "bootstrap-ran").read_bytes() == b"one run\n" and not (root / "bootstrap-ran").exists()
    assert not (root / ".git/spec-dock").exists() and not (target / "spec-dock/.agent").exists()
