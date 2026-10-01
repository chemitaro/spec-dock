"""Public Scope deletion requires approval and a verified external backup."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.cli_runtime.test_issue413_finish import github_fixture
from tests.cli_runtime.test_issue413_work_start import committed_workspace

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_scope_delete_cli_requires_confirmation_and_previews_without_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    scope = root / "spec-dock/initiatives/init-00001-fixture"
    document = scope / "requirement.md"
    document.write_bytes(b"Preserve the exact specification.\n")
    before = {path.relative_to(root): path.read_bytes() for path in scope.rglob("*") if path.is_file()}
    backup = (tmp_path / "backup").resolve()
    log = github_fixture(tmp_path, monkeypatch, {})
    command = ["--project", str(root), "scope", "delete", "init-00001", "--backup-dir", str(backup), "--json"]
    snapshot = tree_digest(root)
    assert main(command) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == [] and tree_digest(root) == snapshot
    assert main([*command, "--dry-run"]) == 0
    preview = json.loads(capsys.readouterr().out)
    assert preview["status"] == "planned" and preview["data"]["result"]["can_apply"] is True
    assert preview["data"]["result"]["removed_ids"] == []
    assert preview["data"]["result"]["remaining_paths"] == [scope.relative_to(root).as_posix()]
    assert tree_digest(root) == snapshot and not backup.exists()
    assert main([*command, "--yes"]) == 0
    deleted = json.loads(capsys.readouterr().out)
    assert deleted["status"] == "succeeded" and deleted["data"]["result"]["removed_ids"] == ["init-00001"]
    assert deleted["data"]["result"]["remaining_paths"] == [] and not scope.exists()
    assert all((backup / relative).read_bytes() == exact for relative, exact in before.items())
    assert main([*command, "--yes"]) == 3
    rejected = json.loads(capsys.readouterr().out)
    assert rejected["effects"] == [] and "backup destination already exists" in rejected["error"]["message"]
    assert all((backup / relative).read_bytes() == exact for relative, exact in before.items())
    assert not log.exists() and not (root / ".git/spec-dock").exists()
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"main\n"
