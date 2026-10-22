"""Installation no longer projects skills to `.claude` and retires only known SpecDock copies there."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.integration.test_issue413_assets import uninitialized_worktree

ROOT = Path(__file__).resolve().parents[2]
PROVIDER = ROOT / "src/spec_dock/assets/install_root/.agents/skills"
SLOTS = ("spec-dock-grill-with-docs", "spec-dock")
SKILL_FILES = (
    "spec-dock-grill-with-docs/SKILL.md",
    "spec-dock-grill-with-docs/agents/openai.yaml",
    "spec-dock-grill-with-docs/scripts/finalize-artifact.py",
    "spec-dock/SKILL.md",
)
AGENTS_FILES = tuple(f".agents/skills/{name}" for name in SKILL_FILES)
CLAUDE_FILES = tuple(f".claude/skills/{name}" for name in SKILL_FILES)
DISTRIBUTED = {
    **{f".claude/skills/{name}": (PROVIDER / name).read_bytes() for name in SKILL_FILES[:3]},
    ".claude/skills/spec-dock/SKILL.md": (ROOT / "tests/fixtures/issue421/spec-dock-skill-4d25a8b4.txt").read_bytes(),
}
USER_FILES = {
    ".claude/settings.json": b'{"permissions": {"allow": ["Bash(make lint)"]}}\n',
    ".claude/settings.local.json": b'{"env": {"PRIVATE": "user-local"}}\n',
    ".claude/skills/other-skill/SKILL.md": b"---\nname: other-skill\ndescription: user-owned\n---\n",
    ".claude/skills/spec-dock/user-notes.md": b"private user notes inside the retired slot\n",
}


def _run(capsys: pytest.CaptureFixture[str], *arguments: str) -> tuple[int, dict[str, Any]]:
    code = main([*arguments, "--json"])
    output = capsys.readouterr()
    assert not output.err
    return code, json.loads(output.out)


def _write(target: Path, files: dict[str, bytes]) -> None:
    for relative, payload in files.items():
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)


def test_init_creates_nothing_under_claude(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    code, result = _run(capsys, "installation", "init", str(target), "--yes")
    assert code == 0 and result["status"] == "succeeded"
    assert not (target / ".claude").exists()
    assert not any(path.startswith(".claude") for path in result["data"]["result"]["created_paths"])
    for name in SKILL_FILES:
        assert (target / ".agents/skills" / name).read_bytes() == (PROVIDER / name).read_bytes()


def test_init_leaves_an_existing_claude_directory_and_stale_copies_untouched(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    _write(target, {**USER_FILES, **DISTRIBUTED})
    before = tree_digest(target / ".claude")
    code, result = _run(capsys, "installation", "init", str(target), "--yes")
    assert code == 0 and result["status"] == "succeeded"
    assert not any(path.startswith(".claude") for path in result["data"]["result"]["created_paths"])
    assert tree_digest(target / ".claude") == before


def test_update_retires_only_known_claude_copies_and_keeps_user_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert _run(capsys, "installation", "init", str(target), "--yes")[0] == 0
    _write(target, {**USER_FILES, **DISTRIBUTED})
    before = tree_digest(target)
    backup = tmp_path / "backup"
    arguments = ("installation", "update", "--target", str(target), "--backup-dir", str(backup))

    code, planned = _run(capsys, *arguments, "--dry-run")
    assert code == 0 and planned["status"] == "planned", planned["error"]
    assert planned["data"]["result"]["planned_retired_paths"] == list(CLAUDE_FILES)
    assert {(effect["kind"], effect["target"]) for effect in planned["effects"]} == {
        ("backup", str(backup)),
        *(("installation.retire", name) for name in CLAUDE_FILES),
    }
    assert tree_digest(target) == before and not backup.exists()

    code, applied = _run(capsys, *arguments, "--yes")
    data = applied["data"]["result"]
    assert code == 0 and applied["status"] == "succeeded", applied["error"]
    assert data["retired_paths"] == list(CLAUDE_FILES)
    assert data["changed_paths"] == [] and data["created_paths"] == []
    assert {path.relative_to(backup).as_posix() for path in backup.rglob("*") if path.is_file()} == {
        f"static/{name}" for name in CLAUDE_FILES
    }
    assert all((backup / "static" / name).read_bytes() == payload for name, payload in DISTRIBUTED.items())
    assert not any((target / name).exists() for name in CLAUDE_FILES)
    assert all((target / name).read_bytes() == payload for name, payload in USER_FILES.items())
    for directory in (
        ".claude/skills/spec-dock",
        *(f".claude/skills/{SLOTS[0]}/{part}" for part in ("agents", "scripts")),
    ):
        assert (target / directory).is_dir() and not (target / directory).is_symlink()
    for name in SKILL_FILES:
        assert (target / ".agents/skills" / name).read_bytes() == (PROVIDER / name).read_bytes()

    code, again = _run(capsys, "installation", "update", "--target", str(target))
    assert code == 0 and again["status"] == "unchanged" and again["effects"] == []


def test_update_accepts_the_earlier_distributed_spec_dock_skill(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert _run(capsys, "installation", "init", str(target), "--yes")[0] == 0
    earlier = target / ".claude/skills/spec-dock/SKILL.md"
    earlier.parent.mkdir(parents=True)
    earlier.write_bytes((ROOT / "tests/fixtures/issue421/spec-dock-skill-99f304c8.txt").read_bytes())
    backup = tmp_path / "backup"
    code, result = _run(capsys, "installation", "update", "--target", str(target), "--backup-dir", str(backup), "--yes")
    assert code == 0 and result["data"]["result"]["retired_paths"] == [".claude/skills/spec-dock/SKILL.md"]
    assert not earlier.exists() and earlier.parent.is_dir()


def _link_claude(target: Path, outside: Path, shape: str) -> tuple[str, ...]:
    """Create the Claude Code side links before installation and return the link paths."""
    if shape == "claude-root-to-outside":
        _write(outside, {name.removeprefix(".claude/"): payload for name, payload in DISTRIBUTED.items()})
        (target / ".claude").symlink_to(outside, target_is_directory=True)
        return (".claude",)
    if shape == "skills-root":
        (target / ".claude").mkdir()
        (target / ".claude/skills").symlink_to("../.agents/skills", target_is_directory=True)
        return (".claude/skills",)
    (target / ".claude/skills").mkdir(parents=True)
    prefix = "missing-" if shape == "dangling-slots" else ""
    for slot in SLOTS:
        (target / ".claude/skills" / slot).symlink_to(f"../../.agents/skills/{prefix}{slot}", target_is_directory=True)
    return tuple(f".claude/skills/{slot}" for slot in SLOTS)


@pytest.mark.skipif(os.name != "posix", reason="native POSIX symbolic-link fixtures")
@pytest.mark.parametrize("shape", ["slots", "dangling-slots", "skills-root", "claude-root-to-outside"])
def test_linked_claude_slots_are_left_to_the_host(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], shape: str
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    outside = tmp_path / "outside-claude"
    links = {name: (target / name).readlink() for name in _link_claude(target, outside, shape)}
    outside_before = tree_digest(outside) if outside.exists() else None

    def assert_links_and_agents_unchanged() -> None:
        assert {name: (target / name).readlink() for name in links} == links
        assert all((target / name).is_symlink() for name in links)
        assert (tree_digest(outside) if outside.exists() else None) == outside_before

    code, initialized = _run(capsys, "installation", "init", str(target), "--yes")
    assert code == 0 and initialized["status"] == "succeeded", initialized["error"]
    assert not any(path.startswith(".claude") for path in initialized["data"]["result"]["created_paths"])
    assert_links_and_agents_unchanged()
    agents = {name: (target / name).read_bytes() for name in AGENTS_FILES}
    assert agents == {f".agents/skills/{name}": (PROVIDER / name).read_bytes() for name in SKILL_FILES}

    code, shown = _run(capsys, "installation", "show", "--target", str(target))
    assert code == 0 and shown["status"] == "succeeded" and shown["effects"] == []
    classifications = {item["path"]: item["classification"] for item in shown["data"]["result"]["assets"]}
    assert not any(path.startswith(".claude") for path in classifications)
    assert {classifications[name] for name in AGENTS_FILES} == {"current"}

    code, updated = _run(
        capsys, "installation", "update", "--target", str(target), "--backup-dir", str(tmp_path / "b1"), "--yes"
    )
    assert code == 0 and updated["status"] == "unchanged" and updated["effects"] == [], updated["error"]
    assert {name: (target / name).read_bytes() for name in AGENTS_FILES} == agents
    assert_links_and_agents_unchanged()

    code, removed = _run(
        capsys, "installation", "uninstall", "--target", str(target), "--backup-dir", str(tmp_path / "b2"), "--yes"
    )
    retired = removed["data"]["result"]["retired_paths"]
    assert code == 0 and removed["status"] == "succeeded", removed["error"]
    assert set(AGENTS_FILES) <= set(retired) and not any(path.startswith(".claude") for path in retired)
    assert not any((target / name).exists() for name in AGENTS_FILES)
    assert_links_and_agents_unchanged()


@pytest.mark.skipif(os.name != "posix", reason="native POSIX symbolic-link fixtures")
@pytest.mark.parametrize("leaf", ["update", "uninstall"])
@pytest.mark.parametrize("shape", ["claude-regular-file", "file-symlink-in-real-slot"])
def test_other_redirected_claude_shapes_still_stop_before_any_effect(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], leaf: str, shape: str
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert _run(capsys, "installation", "init", str(target), "--yes")[0] == 0
    if shape == "claude-regular-file":
        (target / ".claude").write_bytes(b"not a directory\n")
    else:
        (target / ".claude/skills/spec-dock").mkdir(parents=True)
        (target / ".claude/skills/spec-dock/SKILL.md").symlink_to("../../../.agents/skills/spec-dock/SKILL.md")
    before = tree_digest(target)
    backup = tmp_path / "backup"
    code, result = _run(capsys, "installation", leaf, "--target", str(target), "--backup-dir", str(backup), "--yes")
    assert code == 3 and result["error"]["code"] == "PRECONDITION_FAILED" and result["effects"] == []
    assert tree_digest(target) == before and not backup.exists()
