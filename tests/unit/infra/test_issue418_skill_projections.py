"""One provider skill source is projected to the Codex and Claude Code project discovery roots."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from spec_dock.runtime.infra.static_assets import package_static_assets

ROOT = Path(__file__).resolve().parents[3]
SKILLS = ROOT / "src/spec_dock/assets/install_root/.agents/skills"
SKILL_FILES = (
    "spec-dock-grill-with-docs/SKILL.md",
    "spec-dock-grill-with-docs/agents/openai.yaml",
    "spec-dock-grill-with-docs/scripts/finalize-artifact.py",
    "spec-dock/SKILL.md",
)


def test_each_claude_projection_entry_mirrors_its_agents_entry() -> None:
    assets = {asset.path: asset for asset in package_static_assets()}
    for root in (".agents/skills", ".claude/skills"):
        assert {path for path in assets if path.startswith(f"{root}/")} == {f"{root}/{name}" for name in SKILL_FILES}
    for name in SKILL_FILES:
        agents, claude = assets[f".agents/skills/{name}"], assets[f".claude/skills/{name}"]
        assert claude.payload == agents.payload == (SKILLS / name).read_bytes()
        assert (claude.sha256, claude.mode, claude.init_only) == (agents.sha256, agents.mode, agents.init_only)
    inventory = json.loads((ROOT / "src/spec_dock/assets/static-inventory.json").read_bytes())
    sources = {entry["path"]: entry["source"] for entry in inventory["files"]}
    for name in SKILL_FILES:
        expected = f"install_root/.agents/skills/{name}"
        assert sources[f".claude/skills/{name}"] == sources[f".agents/skills/{name}"] == expected
    assert not (ROOT / "src/spec_dock/assets/install_root/.claude").exists()


def _section(content: str, heading: str) -> str:
    start = content.index(heading)
    end = content.find("\n## ", start + len(heading))
    return content[start : end if end >= 0 else None]


def test_grill_skill_resolves_its_helper_from_the_loaded_skill_directory() -> None:
    grill = (SKILLS / "spec-dock-grill-with-docs/SKILL.md").read_text(encoding="utf-8")
    preflight = _section(grill, "## Read-only bootstrap preflight")
    protocol = _section(grill, "## One-write protocol")
    assert ".agents/skills/spec-dock-grill-with-docs/scripts" not in grill
    assert "${CLAUDE_SKILL_DIR}" not in grill
    assert "`<skill-dir>/scripts/finalize-artifact.py`" in preflight
    assert "`agents/openai.yaml` and `scripts/finalize-artifact.py`" not in grill
    assert "`agents/openai.yaml` is Codex invocation metadata, not a prerequisite" in preflight
    for command in ("identity", "finalize"):
        assert f"python3 <skill-dir>/scripts/finalize-artifact.py {command} \\" in protocol
    assert "agent host configuration (for example `.codex/config.toml` and `.claude/settings.json`)" in grill
    assert grill.startswith("---\nname: spec-dock-grill-with-docs\n")
    assert "\ndisable-model-invocation: true\n---\n" in grill
    assert (SKILLS / "spec-dock-grill-with-docs/agents/openai.yaml").read_text(encoding="utf-8") == (
        "policy:\n  allow_implicit_invocation: false\n"
    )


def test_spec_dock_skill_describes_both_project_projections_without_host_specific_processes() -> None:
    skill = (SKILLS / "spec-dock/SKILL.md").read_text(encoding="utf-8")
    assert "the root `.agents/skills` and `.claude/skills` skill projections" in skill
    assert "Codex discovers `.agents/skills` and Claude Code discovers `.claude/skills`" in skill
    assert "running Codex processes" not in skill and "running agent processes" in skill
    assert "never manages other skills or host configuration" in skill


@pytest.mark.parametrize(
    "target",
    [
        ".claude/settings.json",
        ".claude/settings.local.json",
        ".claude/skills/other-skill/SKILL.md",
        ".claude/skills/spec-dock-extra/SKILL.md",
        ".claude/agents/spec-dock.md",
    ],
)
def test_inventory_refuses_claude_targets_outside_the_two_fixed_skill_slots(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, target: str
) -> None:
    resources = tmp_path / "assets"
    resources.mkdir()
    payload = b"inert fixture\n"
    (resources / "payload.md").write_bytes(payload)
    (resources / "static-inventory.json").write_text(
        json.dumps({
            "schema_version": "specdock.static-inventory/v1",
            "files": [
                {
                    "path": target,
                    "source": "payload.md",
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "mode": 0o644,
                    "init_only": False,
                    "known_old_sha256": [],
                }
            ],
            "retired": [],
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr("spec_dock.runtime.infra.static_assets.files", lambda _package: tmp_path)
    with pytest.raises(ValueError, match="unsafe target"):
        package_static_assets()
