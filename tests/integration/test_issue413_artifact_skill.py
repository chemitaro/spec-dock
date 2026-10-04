"""The documented JSON Artifact path works with the shipped Grill finalizer."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import TYPE_CHECKING

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.cli_runtime.test_issue413_artifact import artifact_workspace

if TYPE_CHECKING:
    import pytest

ROOT = Path(__file__).resolve().parents[2]
HELPER = (
    ROOT / "src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py"
)


def test_cli_research_artifact_can_be_finalized_without_recreating_its_identity(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, owner = artifact_workspace(tmp_path)
    for metadata_path in (root / "spec-dock/initiatives").rglob(".meta.json"):
        for name in ("requirement.md", "design.md", "plan.md", "report.md"):
            (metadata_path.parent / name).write_bytes(f"protected canonical {name}\n".encode())
    protected = {path: path.read_bytes() for path in (root / "spec-dock/initiatives").rglob("*.md")}
    assert len(protected) == 16
    metadata = {path: path.read_bytes() for path in (root / "spec-dock/initiatives").rglob(".meta.json")}
    git_before = tree_digest(root / ".git")
    assert (
        main([
            "--project",
            str(root),
            "artifact",
            "create",
            "--scope",
            "iss-00003",
            "--type",
            "research",
            "--title",
            "技術方式の確認",
            "--slug",
            "architecture-review",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["schema_version"] == "specdock.cli/v2" and result["status"] == "succeeded"
    assert result["data"]["kind"] == "artifact"
    relative = result["data"]["result"]["artifact"]["path"]
    artifact = root / relative
    assert artifact.parent == owner / "artifacts"
    original = artifact.read_bytes()
    identity_result = subprocess.run(
        [sys.executable, str(HELPER), "identity", "--repo-root", str(root), "--artifact", relative],
        cwd=root,
        capture_output=True,
        check=False,
        timeout=10,
    )
    assert identity_result.returncode == 0, identity_result.stderr
    identity = json.loads(identity_result.stdout)
    body = "## Question\n\n- 現在の方式を確認する。\n\n## Source\n\n- 現行CLIの実JSON。\n".encode()
    finalized = subprocess.run(
        [
            sys.executable,
            str(HELPER),
            "finalize",
            "--repo-root",
            str(root),
            "--artifact",
            relative,
            "--expected-device",
            str(identity["device"]),
            "--expected-inode",
            str(identity["inode"]),
            "--expected-ctime-ns",
            str(identity["ctime_ns"]),
        ],
        cwd=root,
        input=body,
        capture_output=True,
        check=False,
        timeout=10,
    )
    assert finalized.returncode == 0, finalized.stderr
    prefix = original[: original.index(b"\n## ") + 1]
    assert artifact.read_bytes() == prefix + body
    assert tuple(artifact.parent.iterdir()) == (artifact,)
    assert {path: path.read_bytes() for path in protected} == protected
    assert {path: path.read_bytes() for path in metadata} == metadata
    assert tree_digest(root / ".git") == git_before
    assert not (root / "spec-dock/.agent").exists()
