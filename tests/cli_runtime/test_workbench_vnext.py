"""Workbench copy resolves local Scope IDs on both worktrees and protects conflicts."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING, cast

import pytest

from spec_dock.runtime.application.contracts import WorkbenchCopyError
from spec_dock.runtime.application.create_local_scope import create_local_scope
from spec_dock.runtime.application.workbench_vnext import copy_workbench
from spec_dock.runtime.application.worktree_vnext import create_worktree
from spec_dock.runtime.cli.vnext_runtime import run_vnext
from tests.cli_runtime.test_worktree_create_vnext import _committed_repo

if TYPE_CHECKING:
    from pathlib import Path


def test_copy_local_scope_defaults_to_conflict_error_and_supports_explicit_overwrite(tmp_path: Path) -> None:
    common = _committed_repo(tmp_path)
    source = cast("Path", common["repo_root"])
    initiative = create_local_scope(
        kind="initiative",
        title="Plan",
        parent=None,
        ancestors=(),
        updated_at="2026-09-25T00:00:00Z",
        **common,
    )
    subprocess.run(["git", "add", "-A"], cwd=source, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "scope"],
        cwd=source,
        check=True,
        capture_output=True,
    )
    target = create_worktree(base="HEAD", name="planning", root=tmp_path / "worktrees", **common)
    source_workbench = initiative.path / ".workbench"
    source_workbench.mkdir(exist_ok=True)
    (source_workbench / "note.txt").write_bytes(b"source")
    arguments = {
        "repo_root": source,
        "common_dir": source / ".git",
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 2,
        "scope": initiative.id,
        "to_worktree": "planning",
    }
    first = copy_workbench(**arguments)
    target_workbench = target.path / initiative.path.relative_to(source) / ".workbench"
    assert first.scope_id == initiative.id and (target_workbench / "note.txt").read_bytes() == b"source"
    (source_workbench / "a-new.txt").write_bytes(b"new")
    (source_workbench / "note.txt").write_bytes(b"new source")
    with pytest.raises(WorkbenchCopyError) as error:
        copy_workbench(**arguments)
    assert error.value.mutation_started is False
    assert not (target_workbench / "a-new.txt").exists()
    assert (target_workbench / "note.txt").read_bytes() == b"source"
    copy_workbench(on_conflict="overwrite", **arguments)
    assert (target_workbench / "note.txt").read_bytes() == b"new source"
    assert (target_workbench / "a-new.txt").read_bytes() == b"new"


def test_workbench_copy_cli_preview_conflict_and_explicit_overwrite(tmp_path: Path) -> None:
    common = _committed_repo(tmp_path)
    source = cast("Path", common["repo_root"])
    initiative = create_local_scope(
        kind="initiative", title="Plan", parent=None, ancestors=(), updated_at="2026-09-25T00:00:00Z", **common
    )
    subprocess.run(["git", "add", "-A"], cwd=source, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "scope"],
        cwd=source,
        check=True,
        capture_output=True,
    )
    target = create_worktree(base="HEAD", name="planning", root=tmp_path / "worktrees", **common)
    source_workbench = initiative.path / ".workbench"
    source_workbench.mkdir(exist_ok=True)
    (source_workbench / "note.txt").write_text("source", encoding="utf-8")
    target_workbench = target.path / initiative.path.relative_to(source) / ".workbench"
    prefix = ["workbench", "copy", "--scope", initiative.id, "--to-worktree", str(target.path)]

    def run(*options: str):
        return run_vnext(
            [*prefix, *options, "--json"], invocation_cwd=source, engine_digest="engine-a", engine_version="0.2.4"
        )

    preview = run("--dry-run")
    assert preview.exit_code == 0
    assert json.loads(preview.stdout)["status"] == "planned"
    assert not (target_workbench / "note.txt").exists()
    copied = run()
    assert copied.exit_code == 0
    assert (target_workbench / "note.txt").read_text(encoding="utf-8") == "source"
    (source_workbench / "note.txt").write_text("changed", encoding="utf-8")
    conflict = run()
    assert conflict.exit_code == 3
    assert json.loads(conflict.stdout)["error"]["code"] == "copy_failed"
    assert run("--on-conflict", "overwrite").exit_code == 3
    assert run("--on-conflict", "overwrite", "--dry-run").exit_code == 0
    assert run("--on-conflict", "overwrite", "--yes").exit_code == 0
    assert (target_workbench / "note.txt").read_text(encoding="utf-8") == "changed"
