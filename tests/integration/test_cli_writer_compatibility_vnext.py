"""Writer admission is worktree-local; only Start has shared exclusion."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.git_cli import git_common_directory
from spec_dock.runtime.infra.start_lock import StartLock
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.cli_runtime.test_issue413_work_start import committed_workspace

if TYPE_CHECKING:
    from pathlib import Path


def _retired_state(root: Path) -> Path:
    """Inert old files are fixture data, never a control-store API call."""
    control = root / ".git/spec-dock/control"
    control.mkdir(parents=True)
    (control / "control.json").write_text(
        json.dumps({
            "schema_version": 3,
            "writer_protocol": "specdock.writer/v1",
            "epoch": 12,
            "engine_digest": "old-engine",
            "mode": "maintenance",
            "worktrees": [],
        })
    )
    (control / "engine.json").write_bytes(b"opaque retired locator")
    for directory, filename in (
        ("operations", "journal.json"),
        ("migrations", "record.json"),
        ("installations", "group.json"),
    ):
        record = control / directory / ("a" * 32) / filename
        record.parent.mkdir(parents=True)
        record.write_text(json.dumps({"operation_id": "a" * 32, "terminal_status": "pending", "phase": "preparing"}))
    return control


@pytest.mark.parametrize(
    "protocol,expected",
    [
        ("specdock.worktree-writer/v1", 0),
        ("specdock.writer/v1", 3),
    ],
    ids=["current-own-workspace", "requires-own-migration"],
)
def test_writer_uses_own_declaration_without_registration_epoch_or_pending_recovery(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], protocol: str, expected: int
) -> None:
    root = committed_workspace((tmp_path / "consumer").resolve())
    declaration = root / "spec-dock/workspace.json"
    declaration.write_text(json.dumps({"schema_version": 3, "writer_protocol": protocol}))
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    before = metadata.read_bytes()
    declaration_before = declaration.read_bytes()
    control = _retired_state(root)
    legacy_before = tree_digest(control)
    assert (
        main(["--project", str(root), "scope", "edit", "init-00001", "--title", "Current writer", "--json"]) == expected
    )
    output = capsys.readouterr()
    payload = json.loads(output.out)
    assert payload["schema_version"] == "specdock.cli/v2" and not output.err
    if expected == 0:
        assert payload["data"]["result"]["changed"] is True
        assert json.loads(metadata.read_bytes())["title"] == "Current writer"
        assert payload["effects"] == [{"kind": "metadata", "status": "succeeded", "target": "init-00001"}]
    else:
        assert payload["error"]["code"] == "PRECONDITION_FAILED" and payload["effects"] == []
        assert metadata.read_bytes() == before
    assert tree_digest(control) == legacy_before and declaration.read_bytes() == declaration_before
    assert not (root / "spec-dock/.agent/work-target").exists()


def test_linked_worktrees_share_git_identity_without_requiring_matching_writer_declarations(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace((tmp_path / "main").resolve())
    linked = (tmp_path / "linked").resolve()
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"],
        check=True,
        capture_output=True,
    )
    assert git_common_directory(root) == git_common_directory(linked)
    declaration = linked / "spec-dock/workspace.json"
    declaration.write_text('{"schema_version":3,"writer_protocol":"specdock.writer/v1"}\n')
    other_before = tree_digest(linked / "spec-dock")
    control = _retired_state(root)
    legacy_before = tree_digest(control)
    assert main(["--project", str(root), "scope", "edit", "init-00001", "--title", "Current worktree", "--json"]) == 0
    output = capsys.readouterr()
    payload = json.loads(output.out)
    assert not output.err and payload["data"]["result"]["scope"]["title"] == "Current worktree"
    assert tree_digest(linked / "spec-dock") == other_before and tree_digest(control) == legacy_before
    assert not (linked / "spec-dock/.agent").exists()


@pytest.mark.skipif(os.name != "posix", reason="native POSIX directory Start lock across worktrees")
def test_start_exclusion_allows_a_public_scope_edit_in_a_different_worktree(tmp_path: Path) -> None:
    root = committed_workspace((tmp_path / "main").resolve())
    linked = (tmp_path / "linked").resolve()
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"],
        check=True,
        capture_output=True,
    )
    control = _retired_state(root)
    before = tree_digest(root / "spec-dock")
    legacy_before = tree_digest(control)
    with StartLock(git_common_directory(root), timeout=0):
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; from spec_dock.cli import main; sys.exit(main(sys.argv[1:]))",
                "--project",
                str(linked),
                "scope",
                "edit",
                "init-00001",
                "--title",
                "Parallel writer",
                "--json",
            ],
            cwd=linked,
            capture_output=True,
            text=True,
            timeout=15,
        )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "specdock.cli/v2" and not result.stderr
    assert payload["effects"] == [{"kind": "metadata", "status": "succeeded", "target": "init-00001"}]
    assert (
        json.loads((linked / "spec-dock/initiatives/init-00001-fixture/.meta.json").read_bytes())["title"]
        == "Parallel writer"
    )
    assert tree_digest(root / "spec-dock") == before and tree_digest(control) == legacy_before
    assert not (root / "spec-dock/.agent").exists() and not (linked / "spec-dock/.agent/work-target").exists()
