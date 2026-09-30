"""Incomplete Git inventory rows remain visible and cannot authorize Start."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from tests.cli_runtime.test_issue413_active import select_fixture
from tests.cli_runtime.test_issue413_finish import github_fixture
from tests.cli_runtime.test_issue413_work_start import committed_workspace

if TYPE_CHECKING:
    from pathlib import Path


def inventory_fixture(root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: bytes) -> Path:
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"],
        check=True,
        capture_output=True,
    )
    real_git = shutil.which("git")
    assert real_git
    output = subprocess.check_output([real_git, "-C", str(root), "worktree", "list", "--porcelain", "-z"])
    marker = b"worktree " + os.fsencode(linked) + b"\0"
    assert output.count(marker) == 1
    output = output.replace(marker, marker + field + b"\0")
    binary = tmp_path / "bin"
    binary.mkdir()
    executable = binary / "git"
    executable.write_text(
        f"#!{sys.executable}\nimport os, sys\n"
        "if sys.argv[-4:] == ['worktree', 'list', '--porcelain', '-z']:\n"
        f" sys.stdout.buffer.write({output!r}); sys.exit(0)\n"
        f"os.execv({real_git!r}, [{real_git!r}, *sys.argv[1:]])\n"
    )
    executable.chmod(0o700)
    monkeypatch.setenv("PATH", str(binary) + os.pathsep + os.environ.get("PATH", ""))
    return linked


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable fixture")
def test_sync_retains_unknown_inventory_row_and_healthy_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "main")
    record = select_fixture(root)
    before = record.read_bytes()
    linked = inventory_fixture(root, tmp_path, monkeypatch, b"future-attribute enabled")
    assert main(["--project", str(root), "workspace", "sync", "--json"]) == 7
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "partial"
    assert result["effects"] == []
    data = result["data"]
    assert data["complete"] is False
    rows = {row["path"]: row for row in data["worktrees"]}
    assert rows[str(root)]["selection"]["status"] == "selected"
    assert rows[str(linked)]["selection"]["status"] == "unavailable"
    assert "future-attribute" in rows[str(linked)]["findings"][0]["message"]
    assert data["counts"] == [
        {"scope_id": "init-00001", "direct_selected_count": 1, "descendant_selected_count": 0, "complete": False}
    ]
    assert record.read_bytes() == before
    assert not (linked / "spec-dock/.agent").exists()


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable fixture")
def test_sync_retains_duplicate_inventory_attribute_as_one_unavailable_row(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "main")
    linked = inventory_fixture(root, tmp_path, monkeypatch, b"HEAD " + b"0" * 40)
    assert main(["--project", str(root), "workspace", "sync", "--json"]) == 7
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert result["data"]["complete"] is False
    rows = {row["path"]: row for row in result["data"]["worktrees"]}
    assert rows[str(root)]["selection"]["status"] == "empty"
    assert rows[str(linked)]["selection"]["status"] == "unavailable"
    assert "duplicate" in rows[str(linked)]["findings"][0]["message"]
    assert not (root / "spec-dock/.agent").exists()


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable fixture")
@pytest.mark.parametrize("field", [b"future-attribute enabled", b"HEAD " + b"0" * 40])
def test_start_stops_before_git_effects_for_an_incomplete_inventory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], field: bytes
) -> None:
    root = committed_workspace(tmp_path / "main")
    linked = inventory_fixture(root, tmp_path, monkeypatch, field)
    github_fixture(tmp_path, monkeypatch, {"1": "open"})
    before = subprocess.check_output(["git", "-C", str(root), "show-ref"])
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert result["data"]["started"] is False
    assert subprocess.check_output(["git", "-C", str(root), "show-ref"]) == before
    assert not (root / "spec-dock/.agent").exists()
    assert not (linked / "spec-dock/.agent").exists()


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable fixture")
def test_sync_rejects_an_inventory_flag_with_an_unexpected_value(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "main")
    linked = inventory_fixture(root, tmp_path, monkeypatch, b"bare false")
    assert main(["--project", str(root), "workspace", "sync", "--json"]) == 7
    result = json.loads(capsys.readouterr().out)
    row = next(row for row in result["data"]["worktrees"] if row["path"] == str(linked))
    assert row["selection"]["status"] == "unavailable"
    assert "bare" in row["findings"][0]["message"]
    assert "attribute" in row["findings"][0]["message"]


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable fixture")
def test_sync_keeps_a_known_path_when_its_branch_attribute_is_invalid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "main")
    linked = inventory_fixture(root, tmp_path, monkeypatch, b"branch refs/tags/v1")
    assert main(["--project", str(root), "workspace", "sync", "--json"]) == 7
    result = json.loads(capsys.readouterr().out)
    assert len(result["data"]["worktrees"]) == 2
    row = next(row for row in result["data"]["worktrees"] if row["path"] == str(linked))
    assert row["selection"]["status"] == "unavailable"
    assert "branch" in row["findings"][0]["message"]
