"""Reject malformed committed Scope positions before native Git mutation."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from tests.cli_runtime.test_issue413_contract import add_scope
from tests.cli_runtime.test_issue413_work_start import committed_workspace, open_issue

if TYPE_CHECKING:
    from pathlib import Path


def commit(root: Path) -> None:
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
            "structure",
        ],
        check=True,
        capture_output=True,
    )


@pytest.mark.parametrize("mode", ["blob", "symlink", "gitlink"])
@pytest.mark.parametrize(
    "location",
    [
        "spec-dock/initiatives/init-00099-other",
        "spec-dock/initiatives/init-00001-fixture/epics",
        "spec-dock/initiatives/init-00001-fixture/epics/epic-00099-other",
        "spec-dock/initiatives/init-00001-fixture/epics/epic-00002-fixture/issues",
        "spec-dock/initiatives/init-00001-fixture/epics/epic-00002-fixture/issues/iss-00099-other",
    ],
)
def test_candidate_non_directory_scope_positions_stop_before_git_effects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], mode: str, location: str
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    if "epic-00002-fixture" in location:
        add_scope(root, "epic-00002", "epic", "init-00001", root / "spec-dock/initiatives/init-00001-fixture")
        subprocess.run(["git", "-C", str(root), "add", "spec-dock"], check=True, capture_output=True)
        commit(root)
    subprocess.run(["git", "-C", str(root), "checkout", "-qb", "candidate"], check=True, capture_output=True)
    path = root / location
    path.parent.mkdir(parents=True, exist_ok=True)
    if mode == "blob":
        path.write_text("not a Scope directory\n")
    elif mode == "symlink":
        path.symlink_to("outside")
    else:
        oid = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"]).decode().strip()
        subprocess.run(
            ["git", "-C", str(root), "update-index", "--add", "--cacheinfo", f"160000,{oid},{location}"],
            check=True,
            capture_output=True,
        )
    if mode != "gitlink":
        subprocess.run(["git", "-C", str(root), "add", "--", location], check=True, capture_output=True)
    commit(root)
    subprocess.run(["git", "-C", str(root), "checkout", "-q", "main"], check=True, capture_output=True)
    assert not subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"])
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    assert (
        main([
            "--project",
            str(root),
            "work",
            "start",
            "init-00001",
            "--base",
            "candidate",
            "--branch",
            "attempted",
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"main\n"
    assert (
        subprocess.run(
            ["git", "-C", str(root), "show-ref", "--verify", "--quiet", "refs/heads/attempted"], capture_output=True
        ).returncode
        == 1
    )
    assert not (root / "spec-dock/.agent/work-target").exists()
