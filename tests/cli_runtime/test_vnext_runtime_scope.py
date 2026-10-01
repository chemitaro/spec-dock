"""Public Scope projections and title edits preserve the selected document."""

from __future__ import annotations

import json
import os
import sys
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.cli_runtime.test_issue413_active import select_fixture
from tests.cli_runtime.test_issue413_work_start import committed_workspace
from tests.cli_runtime.test_work_commands_vnext import three_kind_workspace

if TYPE_CHECKING:
    from pathlib import Path


def test_scope_list_show_and_edit_target_the_same_scope(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = three_kind_workspace(tmp_path / "consumer")
    issue = root / "spec-dock/initiatives/init-00001-fixture/epics/epic-00002-fixture/issues/iss-00003-fixture"
    document = issue / "requirement.md"
    document.write_text("# Existing specification\nKeep this body.\n")
    before = document.read_bytes()
    record = select_fixture(root, scope_id="iss-00003", number=3)
    selected = record.read_bytes()
    prefix = ["--project", str(root), "scope"]
    assert main([*prefix, "list", "--kind", "issue", "--parent", "epic-00002", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    items = payload["data"]["result"]["items"]
    assert [item["id"] for item in items] == ["iss-00003"]
    assert items[0]["backend"] == "github" and items[0]["path"] == issue.relative_to(root).as_posix()
    assert items[0]["status"]["state"] == "unknown"
    assert main([*prefix, "show", "@current", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["data"]["result"]["scope"]["id"] == "iss-00003"
    assert (
        main([
            *prefix,
            "edit",
            "@current",
            "--title",
            "Renamed",
            "--expect-current",
            "iss-00003",
            "--dry-run",
            "--json",
        ])
        == 0
    )
    assert json.loads(capsys.readouterr().out)["status"] == "planned"
    assert json.loads((issue / ".meta.json").read_bytes())["title"] == "Fixture"
    assert main([*prefix, "edit", "@current", "--title", "Renamed", "--expect-current", "iss-00003", "--json"]) == 0
    edited = json.loads(capsys.readouterr().out)
    assert edited["data"]["result"]["changed"] is True
    assert edited["data"]["result"]["scope"]["revision"] == 1
    assert main([*prefix, "show", "iss-00003", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["data"]["result"]["scope"]["title"] == "Renamed"
    assert document.read_bytes() == before and record.read_bytes() == selected
    assert not (root / ".git/spec-dock").exists()


@pytest.mark.parametrize("command", [["scope", "list"], ["scope", "edit", "init-00001", "--title", "New"]])
def test_native_context_failure_keeps_git_diagnostic_and_no_effects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], command: list[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    before = tree_digest(root)
    bin_dir = tmp_path / "blocked-git"
    bin_dir.mkdir()
    original = "fatal: fixture Git context refused\nsecond original line\n"
    executable = bin_dir / "git"
    executable.write_text(f"#!{sys.executable}\nimport sys\nsys.stderr.write({original!r})\nsys.exit(73)\n")
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])
    assert main(["--project", str(root), *command, "--json"]) == 5
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert not output.err and result["error"]["code"] == "GIT_FAILED" and result["effects"] == []
    assert result["error"]["details"]["git"]["stderr"] == original
    assert result["error"]["details"]["git"]["returncode"] == 73
    assert tree_digest(root) == before


def test_runtime_rejects_a_nonroot_project_before_scope_edit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    before = tree_digest(root)
    assert (
        main(["--project", str(root / "spec-dock"), "scope", "edit", "init-00001", "--title", "Wrong root", "--json"])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "PRECONDITION_FAILED" and result["effects"] == []
    assert tree_digest(root) == before
