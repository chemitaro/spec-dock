"""Skills are projected only to `.agents/skills`; the earlier `.claude` copies are retired inventory."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from spec_dock.asset_layout import SKILL_ROOTS
from spec_dock.runtime.infra.static_assets import package_retired_assets, package_static_assets

ROOT = Path(__file__).resolve().parents[3]
SKILLS = ROOT / "src/spec_dock/assets/install_root/.agents/skills"
SKILL_FILES = (
    "spec-dock-grill-with-docs/SKILL.md",
    "spec-dock-grill-with-docs/agents/openai.yaml",
    "spec-dock-grill-with-docs/scripts/finalize-artifact.py",
    "spec-dock/SKILL.md",
)
DISTRIBUTED_CLAUDE_HASHES = {
    ".claude/skills/spec-dock-grill-with-docs/SKILL.md": {
        "acb7e66a3e6d956918043875d5a87c5c6a3f0a804fe651b2d68a1f839c34b6d9"
    },
    ".claude/skills/spec-dock-grill-with-docs/agents/openai.yaml": {
        "a1499d95abd8447558c535fe5554adcc3c9b988a0a39264a6283d430effe1e94"
    },
    ".claude/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py": {
        "105f1da76838aeb6d059628495c120b49ab603e8373863e4998ba064c0b2d0dc"
    },
    ".claude/skills/spec-dock/SKILL.md": {
        "4d8befe341350c0f8e7b6055f1086cfd8bfbaf6ea2ef4bf46db6d7aa1a71c500",
        "f8086263d985edec295fe9757b7ef7beb83993b03be2cfa87e5a8813bc9235da",
    },
}


def test_current_inventory_projects_skills_only_to_agents() -> None:
    assets = {asset.path: asset for asset in package_static_assets()}
    assert {path for path in assets if path.startswith((".agents/", ".claude/"))} == {
        f".agents/skills/{name}" for name in SKILL_FILES
    }
    for name in SKILL_FILES:
        assert assets[f".agents/skills/{name}"].payload == (SKILLS / name).read_bytes()
    assert SKILL_ROOTS == (".agents/skills",)
    assert not (ROOT / "src/spec_dock/assets/install_root/.claude").exists()


def test_retired_inventory_holds_every_distributed_claude_copy_hash() -> None:
    retired = {asset.path: set(asset.known_old_sha256) for asset in package_retired_assets()}
    assert {path: hashes for path, hashes in retired.items() if path.startswith(".claude/")} == (
        DISTRIBUTED_CLAUDE_HASHES
    )


def _retired_inventory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, target: str) -> None:
    resources = tmp_path / "assets"
    resources.mkdir()
    (resources / "static-inventory.json").write_text(
        json.dumps({
            "schema_version": "specdock.static-inventory/v1",
            "files": [],
            "retired": [{"path": target, "known_old_sha256": ["0" * 64]}],
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr("spec_dock.runtime.infra.static_assets.files", lambda _package: tmp_path)


@pytest.mark.parametrize(
    "target",
    [
        ".claude/settings.json",
        ".claude/skills/other-skill/SKILL.md",
        ".claude/skills/spec-dock-extra/SKILL.md",
        ".claude/skills/spec-dock",
        ".agents/skills/spec-dock/SKILL.md",
    ],
)
def test_retired_inventory_refuses_paths_outside_the_two_fixed_claude_slots(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, target: str
) -> None:
    _retired_inventory(tmp_path, monkeypatch, target)
    with pytest.raises(ValueError, match="unsafe target"):
        package_retired_assets()


@pytest.mark.parametrize(
    "target", [".claude/skills/spec-dock/SKILL.md", ".claude/skills/spec-dock-grill-with-docs/scripts/helper.py"]
)
def test_retired_inventory_accepts_files_inside_the_two_fixed_claude_slots(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, target: str
) -> None:
    _retired_inventory(tmp_path, monkeypatch, target)
    assert [asset.path for asset in package_retired_assets()] == [target]


def test_spec_dock_skill_describes_the_agents_projection_and_host_links() -> None:
    skill = (SKILLS / "spec-dock/SKILL.md").read_text(encoding="utf-8")
    assert "`.claude/skills` skill projections" not in skill
    assert "the root `.agents/skills` skill projection" in skill
    assert "`.claude/skills/<name>` -> `../../.agents/skills/<name>`" in skill
    assert "running agent processes" in skill
    assert "never manages other skills" in skill
