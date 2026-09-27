"""Registered worktree removal protects current, dirty, and ignored payloads."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
from typing import cast

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.worktree_vnext import create_worktree, remove_worktree  # noqa: E402
from spec_dock_runtime.infra.control_store import load_control  # noqa: E402
from tests.cli_runtime.test_worktree_create_vnext import _committed_repo  # noqa: E402


def _created(tmp_path: Path):
    common = _committed_repo(tmp_path)
    source = cast("Path", common["repo_root"])
    result = create_worktree(base="HEAD", name="planning", root=tmp_path / "worktrees", **common)
    return common, source, result


def test_remove_keeps_branch_and_retires_registration(tmp_path: Path) -> None:
    _common, source, created = _created(tmp_path)
    result = remove_worktree(
        repo_root=source,
        common_dir=source / ".git",
        worktree_id="main",
        engine_digest="engine-a",
        expected_epoch=2,
        reference=f"wt:{created.id}",
    )
    assert result.id == created.id and result.branch_deleted is False
    assert not created.path.exists()
    assert (
        subprocess.run(
            ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{created.branch}"],
            cwd=source,
            capture_output=True,
        ).returncode
        == 0
    )
    control = load_control(source / ".git")
    assert control is not None and not next(item for item in control.worktrees if item.id == created.id).active


def test_remove_rejects_untracked_even_with_discard_ignored(tmp_path: Path) -> None:
    _common, source, created = _created(tmp_path)
    (created.path / "untracked.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(ValueError, match="untracked"):
        remove_worktree(
            repo_root=source,
            common_dir=source / ".git",
            worktree_id="main",
            engine_digest="engine-a",
            expected_epoch=2,
            reference="planning",
            discard_ignored=True,
        )
    assert (created.path / "untracked.txt").read_text(encoding="utf-8") == "keep"


def test_remove_rejects_current_and_ignored_without_explicit_flag(tmp_path: Path) -> None:
    _common, source, created = _created(tmp_path)
    with pytest.raises(ValueError, match="current"):
        remove_worktree(
            repo_root=source,
            common_dir=source / ".git",
            worktree_id="main",
            engine_digest="engine-a",
            expected_epoch=2,
            reference="wt:main",
        )
    exclude = source / ".git" / "info" / "exclude"
    exclude.write_text(exclude.read_text(encoding="utf-8") + "\nsecret.bin\n", encoding="utf-8")
    (created.path / "secret.bin").write_bytes(b"keep private")
    with pytest.raises(ValueError, match="ignored"):
        remove_worktree(
            repo_root=source,
            common_dir=source / ".git",
            worktree_id="main",
            engine_digest="engine-a",
            expected_epoch=2,
            reference="planning",
        )
    assert (created.path / "secret.bin").read_bytes() == b"keep private"


def test_remove_discards_only_explicitly_allowed_ignored_payload(tmp_path: Path) -> None:
    _common, source, created = _created(tmp_path)
    exclude = source / ".git" / "info" / "exclude"
    exclude.write_text(exclude.read_text(encoding="utf-8") + "\nsecret.bin\n", encoding="utf-8")
    (created.path / "secret.bin").write_bytes(b"private")
    result = remove_worktree(
        repo_root=source,
        common_dir=source / ".git",
        worktree_id="main",
        engine_digest="engine-a",
        expected_epoch=2,
        reference="planning",
        discard_ignored=True,
    )
    assert result.id == created.id and not created.path.exists()


def test_locked_worktree_requires_explicit_unlock(tmp_path: Path) -> None:
    _common, source, created = _created(tmp_path)
    subprocess.run(["git", "worktree", "lock", str(created.path)], cwd=source, check=True, capture_output=True)
    arguments = {
        "repo_root": source,
        "common_dir": source / ".git",
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 2,
        "reference": "planning",
    }
    with pytest.raises(ValueError, match="unlock"):
        remove_worktree(**arguments)
    assert created.path.exists()
    removed = remove_worktree(unlock=True, **arguments)
    assert removed.id == created.id and not created.path.exists()
