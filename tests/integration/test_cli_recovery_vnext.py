"""Retired recovery options stop at the public CLI before project admission."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize(
    "command",
    [
        ("scope", "create", "initiative", "--backend", "github", "--title", "Plan"),
        ("scope", "import", "github", "initiative", "gh:example/repo#21", "--title", "Plan"),
        ("scope", "close", "init-00001"),
        ("scope", "reopen", "init-00001"),
        ("scope", "delete", "init-00001"),
        ("work", "start", "init-00001"),
        ("work", "finish", "init-00001"),
        ("branch", "create", "init-00001"),
        ("workspace", "migrate", "--to-schema", "3", "--to-writer-protocol", "specdock.worktree-writer/v1"),
        ("installation", "init", "--root", "{root}"),
        ("installation", "update"),
        ("installation", "uninstall"),
    ],
)
@pytest.mark.parametrize("option", ["--resume", "--rollback"])
def test_retired_recovery_is_rejected_before_project_access_without_touching_old_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    command: tuple[str, ...],
    option: str,
) -> None:
    evidence = tmp_path / "legacy-evidence.json"
    evidence.write_bytes(b'{"phase":"unknown","private":"keep"}\n')
    before = tree_digest(tmp_path)
    project = tmp_path / "missing"
    monkeypatch.setenv("PATH", str(tmp_path / "no-tools"))
    argv = [str(tmp_path / "fresh") if token == "{root}" else token for token in command]

    assert main(["--project", str(project), *argv, option, "old-operation", "--json"]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["schema_version"] == "specdock.cli/v2"
    assert result["status"] == "failed" and result["effects"] == []
    assert result["error"]["code"] == "ARGUMENT_RETIRED"
    assert option in result["error"]["message"]
    assert "new explicit operation" in result["error"]["message"]
    assert "operation_id" not in result and result["recovery"] is None
    assert tree_digest(tmp_path) == before
    assert not project.exists()
