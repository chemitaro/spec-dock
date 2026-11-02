"""A CLI-created canonical Scope Artifact and the shipped Grill finalizer (iss-00440).

Replaces tests/integration/test_issue413_artifact_skill.py, which ran on the retired schema-3 dependency workspace,
for what works today. The finalizer opens every directory component without following links, so it refuses a
canonical Artifact path through the `spec-dock/initiatives` link (a known gap kept out of this PR); here it
finalizes the CLI-generated scaffold in a real-directory copy of the same layout.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import TYPE_CHECKING

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.legacy_contracts_g3 import make_world

if TYPE_CHECKING:
    import pytest

ROOT = Path(__file__).resolve().parents[2]
HELPER = (
    ROOT / "src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py"
)


def _helper(*argv: str, cwd: Path, body: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [sys.executable, str(HELPER), *argv], cwd=cwd, input=body, capture_output=True, check=False, timeout=10
    )


def test_cli_research_artifact_can_be_finalized_without_recreating_its_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = make_world(tmp_path, monkeypatch, capsys, write=True)
    world.scope("epic", 2, "Fixture", parent=1)
    world.scope("issue", 3, "Fixture", parent=2)
    root = world.main
    catalog = world.catalog.resolve()
    for name in ("requirement.md", "design.md", "plan.md", "report.md"):
        for scope_id in ("init-00001", "epic-00002", "iss-00003"):
            (world.find(scope_id) / name).write_bytes(f"protected canonical {name}\n".encode())
    protected = {path: path.read_bytes() for path in catalog.rglob("*.md") if ".runtime" not in path.parts}
    assert len(protected) >= 12  # the three Scopes' documents plus the catalog's own files
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
    assert relative.startswith("spec-dock/initiatives/00000-00999/iss-00003/artifacts/")
    artifact = root / relative
    assert artifact.parent.resolve() == world.find("iss-00003") / "artifacts"
    original = artifact.read_bytes()
    assert {path: path.read_bytes() for path in protected} == protected
    assert tree_digest(root / ".git") == git_before
    assert not (root / "spec-dock/.agent").exists()

    # the same repository-relative layout with real directories, holding the CLI-generated scaffold
    mirror = tmp_path / "mirror"
    copied = mirror / relative
    copied.parent.mkdir(parents=True)
    copied.write_bytes(original)
    identity_result = _helper("identity", "--repo-root", str(mirror), "--artifact", relative, cwd=mirror)
    assert identity_result.returncode == 0, identity_result.stderr
    identity = json.loads(identity_result.stdout)
    body = "## Question\n\n- 現在の方式を確認する。\n\n## Source\n\n- 現行CLIの実JSON。\n".encode()
    finalized = _helper(
        "finalize",
        "--repo-root",
        str(mirror),
        "--artifact",
        relative,
        "--expected-device",
        str(identity["device"]),
        "--expected-inode",
        str(identity["inode"]),
        "--expected-ctime-ns",
        str(identity["ctime_ns"]),
        cwd=mirror,
        body=body,
    )
    assert finalized.returncode == 0, finalized.stderr
    prefix = original[: original.index(b"\n## ") + 1]
    assert copied.read_bytes() == prefix + body
    assert tuple(copied.parent.iterdir()) == (copied,)
