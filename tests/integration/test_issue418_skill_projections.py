"""A 0.2.4 consumer receives the current host-neutral skills in the `.agents` slots only."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.integration.test_issue413_assets import uninitialized_worktree

if TYPE_CHECKING:
    import pytest

ROOT = Path(__file__).resolve().parents[2]
PROVIDER = ROOT / "src/spec_dock/assets/install_root/.agents/skills"
FIXTURES = ROOT / "tests/fixtures/issue418"
SKILL_FILES = (
    "spec-dock-grill-with-docs/SKILL.md",
    "spec-dock-grill-with-docs/agents/openai.yaml",
    "spec-dock-grill-with-docs/scripts/finalize-artifact.py",
    "spec-dock/SKILL.md",
)


def _run(capsys: pytest.CaptureFixture[str], *arguments: str) -> tuple[int, dict[str, Any]]:
    code = main([*arguments, "--json"])
    output = capsys.readouterr()
    assert not output.err
    return code, json.loads(output.out)


def _legacy_consumer(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> Path:
    """A 0.2.4 layout: old `.agents` skill bytes and no `.claude` directory."""
    target = uninitialized_worktree(tmp_path / "consumer")
    assert _run(capsys, "installation", "init", str(target), "--yes")[0] == 0
    (target / ".agents/skills/spec-dock/SKILL.md").write_bytes((FIXTURES / "spec-dock-skill-v0.2.4.txt").read_bytes())
    (target / ".agents/skills/spec-dock-grill-with-docs/SKILL.md").write_bytes(
        (FIXTURES / "grill-with-docs-skill-v0.2.4.txt").read_bytes()
    )
    return target


def test_update_refreshes_legacy_agents_skills_without_creating_claude(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = _legacy_consumer(tmp_path, capsys)
    before = tree_digest(target)
    backup = tmp_path / "backup"
    arguments = ("installation", "update", "--target", str(target), "--backup-dir", str(backup))

    code, planned = _run(capsys, *arguments, "--dry-run")
    assert code == 0 and planned["status"] == "planned", planned["error"]
    assert {(effect["kind"], effect["target"]) for effect in planned["effects"]} == {
        ("backup", str(backup)),
        ("installation.change", ".agents/skills/spec-dock-grill-with-docs/SKILL.md"),
        ("installation.change", ".agents/skills/spec-dock/SKILL.md"),
    }
    assert tree_digest(target) == before and not backup.exists()

    code, applied = _run(capsys, *arguments, "--yes")
    data = applied["data"]["result"]
    assert code == 0 and applied["status"] == "succeeded"
    assert data["changed_paths"] == [
        ".agents/skills/spec-dock-grill-with-docs/SKILL.md",
        ".agents/skills/spec-dock/SKILL.md",
    ]
    assert data["created_paths"] == [] and data["retired_paths"] == []
    assert (backup / "static/.agents/skills/spec-dock/SKILL.md").read_bytes() == (
        FIXTURES / "spec-dock-skill-v0.2.4.txt"
    ).read_bytes()
    for name in SKILL_FILES:
        assert (target / ".agents/skills" / name).read_bytes() == (PROVIDER / name).read_bytes()
    assert not (target / ".claude").exists()

    code, again = _run(capsys, "installation", "update", "--target", str(target))
    assert code == 0 and again["status"] == "unchanged" and again["effects"] == []
