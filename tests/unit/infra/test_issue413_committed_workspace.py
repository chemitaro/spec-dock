"""Committed planning paths cannot escape the temporary reader on any OS."""

from pathlib import Path
import subprocess

import pytest

from spec_dock.runtime.infra.committed_workspace import committed_workspace


def test_committed_reader_rejects_windows_separator_in_git_tree(tmp_path: Path) -> None:
    if (tmp_path / "..\\escape").name != "..\\escape":
        pytest.skip("fixture requires a filesystem where backslash is a literal filename character")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    directory = tmp_path / "spec-dock/initiatives/..\\escape"
    directory.mkdir(parents=True)
    (directory / ".meta.json").write_text("{}")
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "unsafe path",
        ],
        check=True,
    )
    oid = subprocess.check_output(["git", "-C", str(tmp_path), "rev-parse", "HEAD"]).decode().rstrip("\n")
    with pytest.raises(ValueError, match="unsafe"), committed_workspace(tmp_path, oid, timeout=30):
        pytest.fail("unsafe committed path was accepted")
