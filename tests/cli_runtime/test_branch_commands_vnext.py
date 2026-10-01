"""Public branch leaves observe refs and preserve dry-run boundaries."""

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


def test_branch_adapter_create_show_switch_and_dry_run(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = committed_workspace(tmp_path / "consumer")
    arguments = ["--project", str(root), "branch"]
    before = tree_digest(root)
    tip = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    assert main([*arguments, "create", "init-00001", "--base", "HEAD", "--dry-run", "--json"]) == 0
    planned = json.loads(capsys.readouterr().out)
    assert planned["status"] == "planned" and tree_digest(root) == before
    assert planned["data"]["result"]["name"] == "init-00001-fixture"
    assert (
        subprocess.run(
            ["git", "-C", str(root), "show-ref", "--verify", "--quiet", "refs/heads/init-00001-fixture"],
            capture_output=True,
        ).returncode
        == 1
    )
    assert main([*arguments, "create", "init-00001", "--base", "HEAD", "--json"]) == 0
    created = json.loads(capsys.readouterr().out)
    assert created["data"]["result"] == {
        "scope_id": "init-00001",
        "name": "init-00001-fixture",
        "tip": tip,
        "created": True,
        "switched": False,
        "binding_persisted": False,
    }
    assert created["effects"] == [{"kind": "git.branch.create", "status": "succeeded", "target": "init-00001-fixture"}]
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"main\n"
    assert main([*arguments, "show", "init-00001", "--json"]) == 0
    shown = json.loads(capsys.readouterr().out)
    assert shown["data"]["result"]["tip"] == tip and shown["effects"] == []
    before = tree_digest(root)
    assert main([*arguments, "switch", "init-00001", "--dry-run", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "planned" and tree_digest(root) == before
    assert main([*arguments, "switch", "init-00001", "--json"]) == 0
    switched = json.loads(capsys.readouterr().out)
    assert switched["data"]["result"]["switched"] is True
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"init-00001-fixture\n"
    refs_before = subprocess.check_output(["git", "-C", str(root), "show-ref"])
    assert main([*arguments, "create", "init-00001", "--base", "HEAD", "--json"]) == 3
    rejected = json.loads(capsys.readouterr().out)
    assert rejected["effects"] == [] and "already exists" in rejected["error"]["message"]
    assert subprocess.check_output(["git", "-C", str(root), "show-ref"]) == refs_before
    assert not (root / "spec-dock/.agent").exists() and not (root / ".git/spec-dock").exists()
