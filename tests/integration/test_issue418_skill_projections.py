"""Installation keeps the Codex and Claude Code skill projections inside their fixed slots."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
from typing import Any

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.integration.test_issue413_assets import uninitialized_worktree

ROOT = Path(__file__).resolve().parents[2]
PROVIDER = ROOT / "src/spec_dock/assets/install_root/.agents/skills"
FIXTURES = ROOT / "tests/fixtures/issue418"
SKILL_FILES = (
    "spec-dock-grill-with-docs/SKILL.md",
    "spec-dock-grill-with-docs/agents/openai.yaml",
    "spec-dock-grill-with-docs/scripts/finalize-artifact.py",
    "spec-dock/SKILL.md",
)
CLAUDE_FILES = tuple(f".claude/skills/{name}" for name in SKILL_FILES)
USER_FILES = {
    ".claude/settings.json": b'{"permissions": {"allow": ["Bash(make lint)"]}}\n',
    ".claude/settings.local.json": b'{"env": {"PRIVATE": "user-local"}}\n',
    ".claude/skills/other-skill/SKILL.md": b"---\nname: other-skill\ndescription: user-owned\n---\n",
    ".claude/skills/spec-dock/user-notes.md": b"private user notes inside the managed slot\n",
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


def _legacy_consumer(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> Path:
    """A 0.2.4 layout: old `.agents` skill bytes and no SpecDock `.claude` projection."""
    target = uninitialized_worktree(tmp_path / "consumer")
    assert _run(capsys, "installation", "init", str(target), "--yes")[0] == 0
    shutil.rmtree(target / ".claude")
    (target / ".agents/skills/spec-dock/SKILL.md").write_bytes((FIXTURES / "spec-dock-skill-v0.2.4.txt").read_bytes())
    (target / ".agents/skills/spec-dock-grill-with-docs/SKILL.md").write_bytes(
        (FIXTURES / "grill-with-docs-skill-v0.2.4.txt").read_bytes()
    )
    return target


def test_update_projects_skills_for_claude_code_into_an_existing_user_claude_directory(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = _legacy_consumer(tmp_path, capsys)
    user_files = {name: payload for name, payload in USER_FILES.items() if "/spec-dock/" not in name}
    _write(target, user_files)
    before = tree_digest(target)
    backup = tmp_path / "backup"
    arguments = ("installation", "update", "--target", str(target), "--backup-dir", str(backup))

    code, planned = _run(capsys, *arguments, "--dry-run")
    assert code == 0 and planned["status"] == "planned", planned["error"]
    assert {(effect["kind"], effect["target"]) for effect in planned["effects"]} == {
        ("backup", str(backup)),
        ("installation.change", ".agents/skills/spec-dock-grill-with-docs/SKILL.md"),
        ("installation.change", ".agents/skills/spec-dock/SKILL.md"),
        *(("installation.create", name) for name in CLAUDE_FILES),
    }
    assert tree_digest(target) == before and not backup.exists()

    code, applied = _run(capsys, *arguments, "--yes")
    data = applied["data"]["result"]
    assert code == 0 and applied["status"] == "succeeded"
    assert data["changed_paths"] == [
        ".agents/skills/spec-dock-grill-with-docs/SKILL.md",
        ".agents/skills/spec-dock/SKILL.md",
    ]
    assert data["created_paths"] == [
        ".claude/skills/spec-dock-grill-with-docs",
        CLAUDE_FILES[0],
        ".claude/skills/spec-dock-grill-with-docs/agents",
        CLAUDE_FILES[1],
        ".claude/skills/spec-dock-grill-with-docs/scripts",
        CLAUDE_FILES[2],
        ".claude/skills/spec-dock",
        CLAUDE_FILES[3],
    ]
    assert {path.relative_to(backup).as_posix() for path in backup.rglob("*") if path.is_file()} == {
        "static/.agents/skills/spec-dock-grill-with-docs/SKILL.md",
        "static/.agents/skills/spec-dock/SKILL.md",
    }
    assert (backup / "static/.agents/skills/spec-dock/SKILL.md").read_bytes() == (
        FIXTURES / "spec-dock-skill-v0.2.4.txt"
    ).read_bytes()
    for name in SKILL_FILES:
        payload = (PROVIDER / name).read_bytes()
        assert (target / ".agents/skills" / name).read_bytes() == payload
        assert (target / ".claude/skills" / name).read_bytes() == payload
    assert all((target / name).read_bytes() == payload for name, payload in user_files.items())

    code, again = _run(capsys, "installation", "update", "--target", str(target))
    assert code == 0 and again["status"] == "unchanged" and again["effects"] == []


@pytest.mark.parametrize("shape", ["symlink-to-installed-files", "symlink-to-empty-directory", "regular-file"])
def test_show_classifies_projection_files_under_an_unsafe_parent_as_unsafe(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], shape: str
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert _run(capsys, "installation", "init", str(target), "--yes")[0] == 0
    outside = tmp_path / "outside-claude"
    if shape == "symlink-to-installed-files":
        shutil.move(target / ".claude", outside)
    else:
        shutil.rmtree(target / ".claude")
        outside.mkdir()
    if shape == "regular-file":
        (target / ".claude").write_bytes(b"not a directory\n")
    else:
        (target / ".claude").symlink_to(outside, target_is_directory=True)
    before, outside_before = tree_digest(target), tree_digest(outside)
    code, result = _run(capsys, "installation", "show", "--target", str(target))
    assert code == 0 and result["status"] == "succeeded" and result["effects"] == []
    classifications = {item["path"]: item["classification"] for item in result["data"]["result"]["assets"]}
    assert {name: classifications[name] for name in CLAUDE_FILES} == dict.fromkeys(CLAUDE_FILES, "unsafe")
    assert {classifications[f".agents/skills/{name}"] for name in SKILL_FILES} == {"current"}
    assert tree_digest(target) == before and tree_digest(outside) == outside_before


def test_init_shares_an_existing_claude_directory_without_touching_user_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    _write(target, USER_FILES)
    code, result = _run(capsys, "installation", "init", str(target), "--yes")
    assert code == 0 and result["status"] == "succeeded"
    created = result["data"]["result"]["created_paths"]
    assert ".claude" not in created and ".claude/skills" not in created and ".claude/skills/spec-dock" not in created
    assert set(CLAUDE_FILES) <= set(created)
    assert all((target / name).read_bytes() == payload for name, payload in USER_FILES.items())
    for name in SKILL_FILES:
        assert (target / ".claude/skills" / name).read_bytes() == (PROVIDER / name).read_bytes()


@pytest.mark.parametrize("leaf", ["update", "uninstall"])
def test_static_changes_refuse_a_redirected_claude_directory_before_any_effect(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], leaf: str
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert _run(capsys, "installation", "init", str(target), "--yes")[0] == 0
    outside = tmp_path / "outside-claude"
    shutil.move(target / ".claude", outside)
    (target / ".claude").symlink_to(outside, target_is_directory=True)
    before, outside_before = tree_digest(target), tree_digest(outside)
    backup = tmp_path / "backup"
    code, result = _run(capsys, "installation", leaf, "--target", str(target), "--backup-dir", str(backup), "--yes")
    assert code == 3 and result["error"]["code"] == "PRECONDITION_FAILED" and result["effects"] == []
    assert tree_digest(target) == before and tree_digest(outside) == outside_before and not backup.exists()


@pytest.mark.skipif(os.name != "posix", reason="native POSIX directory-descriptor publication fixture")
def test_update_reports_a_partial_projection_and_converges_with_a_new_explicit_update(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    target = _legacy_consumer(tmp_path, capsys)
    slot = target / ".claude/skills/spec-dock-grill-with-docs"
    original = os.link
    attempts: list[str] = []

    def fail_first_projection_link(
        source: str,
        destination: str,
        *,
        src_dir_fd: int | None = None,
        dst_dir_fd: int | None = None,
        follow_symlinks: bool = True,
    ) -> None:
        if destination == "SKILL.md" and dst_dir_fd is not None and slot.is_dir() and not attempts:
            held, current = os.fstat(dst_dir_fd), slot.stat()
            if (held.st_dev, held.st_ino) == (current.st_dev, current.st_ino):
                attempts.append(destination)
                raise OSError("injected projection publication failure")
        original(source, destination, src_dir_fd=src_dir_fd, dst_dir_fd=dst_dir_fd, follow_symlinks=follow_symlinks)

    monkeypatch.setattr(os, "link", fail_first_projection_link)
    first = tmp_path / "first-backup"
    code, partial = _run(capsys, "installation", "update", "--target", str(target), "--backup-dir", str(first), "--yes")
    monkeypatch.setattr(os, "link", original)
    assert code == 6 and partial["status"] == "partial" and attempts == ["SKILL.md"]
    statuses = {(effect["kind"], effect["target"]): effect["status"] for effect in partial["effects"]}
    assert statuses["installation.change", ".agents/skills/spec-dock/SKILL.md"] == "succeeded"
    assert statuses["installation.create", CLAUDE_FILES[0]] == "unknown"
    assert {statuses["installation.create", name] for name in CLAUDE_FILES[1:]} == {"not_attempted"}
    assert {status for (kind, _), status in statuses.items() if kind == "installation.stage"} == {"unknown"}
    assert not (target / CLAUDE_FILES[0]).exists()
    assert (first / "static/.agents/skills/spec-dock/SKILL.md").read_bytes() == (
        FIXTURES / "spec-dock-skill-v0.2.4.txt"
    ).read_bytes()

    second = tmp_path / "second-backup"
    code, converged = _run(
        capsys, "installation", "update", "--target", str(target), "--backup-dir", str(second), "--yes"
    )
    assert code == 0 and converged["status"] == "succeeded"
    assert converged["data"]["result"]["changed_paths"] == []
    assert set(CLAUDE_FILES) <= set(converged["data"]["result"]["created_paths"])
    for name in SKILL_FILES:
        assert (target / ".claude/skills" / name).read_bytes() == (PROVIDER / name).read_bytes()
    assert _run(capsys, "installation", "update", "--target", str(target))[1]["status"] == "unchanged"
