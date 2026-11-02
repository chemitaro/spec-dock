"""Retiring an earlier `.claude/skills` copy without a Claude Code link warns and shows how to place it."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.cli import main
from tests.integration.test_issue413_assets import uninitialized_worktree
from tests.integration.test_issue421_claude_skill_retirement import DISTRIBUTED, SLOTS

if TYPE_CHECKING:
    from pathlib import Path

CODE = "CLAUDE_SKILL_LINK_MISSING"


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


def _installed_with_copies(tmp_path: Path, capsys: pytest.CaptureFixture[str], copies: dict[str, bytes]) -> Path:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert _run(capsys, "installation", "init", str(target), "--yes")[0] == 0
    _write(target, copies)
    return target


def _expected(target: Path, slot: str) -> dict[str, Any]:
    name = slot.removeprefix(".claude/skills/")
    root = shlex.quote(str(target))
    return {
        "code": CODE,
        "details": {
            "slot": slot,
            "link_target": f"../../.agents/skills/{name}",
            "command": (
                f"cd {root} && find {slot} -mindepth 1 -depth -type d -empty -delete"
                f" && rmdir {slot} && ln -s ../../.agents/skills/{name} {slot}"
            ),
        },
    }


def _warnings(result: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"code": item["code"], "details": item["details"]} for item in result["warnings"] if item["code"] == CODE]


def test_dry_run_warns_per_slot_whose_copies_are_retired_without_a_link(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = _installed_with_copies(tmp_path, capsys, DISTRIBUTED)
    code, planned = _run(
        capsys, "installation", "update", "--target", str(target), "--backup-dir", str(tmp_path / "b"), "--dry-run"
    )
    assert code == 0 and planned["status"] == "planned", planned["error"]
    assert _warnings(planned) == [_expected(target, f".claude/skills/{slot}") for slot in ("spec-dock", SLOTS[0])]
    for item in planned["warnings"]:
        assert "sync-project-skills" in item["message"] and item["details"]["command"] in item["message"]


@pytest.mark.skipif(os.name != "posix", reason="native POSIX symbolic-link commands")
def test_applied_update_warns_in_json_and_text_and_the_command_places_the_link(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    target = _installed_with_copies(tmp_path, capsys, DISTRIBUTED)
    code, applied = _run(
        capsys, "installation", "update", "--target", str(target), "--backup-dir", str(tmp_path / "b1"), "--yes"
    )
    assert code == 0 and applied["status"] == "succeeded", applied["error"]
    expected = [_expected(target, f".claude/skills/{slot}") for slot in ("spec-dock", SLOTS[0])]
    assert _warnings(applied) == expected

    outside = tmp_path / "elsewhere"
    outside.mkdir()
    for item in expected:
        subprocess.run(item["details"]["command"], shell=True, check=True, cwd=outside)
    for slot in ("spec-dock", SLOTS[0]):
        link = target / ".claude/skills" / slot
        assert link.is_symlink() and str(link.readlink()) == f"../../.agents/skills/{slot}"
        assert (link / "SKILL.md").read_bytes() == (target / ".agents/skills" / slot / "SKILL.md").read_bytes()

    (tmp_path / "text").mkdir()
    text_target = _installed_with_copies(tmp_path / "text", capsys, DISTRIBUTED)
    monkeypatch.chdir(text_target)
    code = main(["installation", "update", "--backup-dir", str(tmp_path / "b2"), "--yes"])
    stderr = capsys.readouterr().err.splitlines()
    assert code == 0
    assert [line.split("]")[0] for line in stderr if CODE in line] == [f"warning [{CODE}"] * 2
    assert all("sync-project-skills" in line and "ln -s ../../.agents/skills/" in line for line in stderr)


@pytest.mark.skipif(os.name != "posix", reason="native POSIX symbolic-link fixtures")
@pytest.mark.parametrize("shape", ["slot-links", "dangling-slot-links", "no-copies"])
def test_no_warning_when_nothing_is_retired_from_a_real_slot(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], shape: str
) -> None:
    target = _installed_with_copies(tmp_path, capsys, {})
    if shape != "no-copies":
        (target / ".claude/skills").mkdir(parents=True)
        prefix = "missing-" if shape == "dangling-slot-links" else ""
        for slot in SLOTS:
            (target / ".claude/skills" / slot).symlink_to(f"../../.agents/skills/{prefix}{slot}")
    for flag in ("--dry-run", "--yes"):
        code, result = _run(
            capsys, "installation", "update", "--target", str(target), "--backup-dir", str(tmp_path / "b"), flag
        )
        assert code == 0 and result["status"] in ("planned", "unchanged"), result["error"]
        assert result["warnings"] == []


def test_no_warning_on_a_second_update_or_on_uninstall(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = _installed_with_copies(tmp_path, capsys, DISTRIBUTED)
    arguments = ("installation", "update", "--target", str(target))
    assert _warnings(_run(capsys, *arguments, "--backup-dir", str(tmp_path / "b1"), "--yes")[1])
    code, again = _run(capsys, *arguments, "--dry-run")
    assert code == 0 and again["status"] == "planned" and again["warnings"] == []

    _write(target, DISTRIBUTED)
    code, removed = _run(
        capsys, "installation", "uninstall", "--target", str(target), "--backup-dir", str(tmp_path / "b2"), "--yes"
    )
    assert code == 0 and removed["status"] == "succeeded", removed["error"]
    assert set(DISTRIBUTED) <= set(removed["data"]["result"]["retired_paths"])
    assert removed["warnings"] == []


def test_only_the_slot_with_retired_copies_warns(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    copies = {name: payload for name, payload in DISTRIBUTED.items() if name.startswith(".claude/skills/spec-dock/")}
    target = _installed_with_copies(tmp_path, capsys, copies)
    code, applied = _run(
        capsys, "installation", "update", "--target", str(target), "--backup-dir", str(tmp_path / "b"), "--yes"
    )
    assert code == 0 and applied["status"] == "succeeded", applied["error"]
    assert _warnings(applied) == [_expected(target, ".claude/skills/spec-dock")]


def test_partial_update_warns_only_for_slots_whose_copies_were_removed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.application import direct_static_update
    from spec_dock.runtime.infra.file_publication import FileRetirementIncomplete

    target = _installed_with_copies(tmp_path, capsys, DISTRIBUTED)
    retire = direct_static_update.retire_file

    def stop_at_spec_dock(path: Path, **kwargs: Any) -> None:
        if path == target / ".claude/skills/spec-dock/SKILL.md":
            raise FileRetirementIncomplete("injected stop", confirmed=False)
        retire(path, **kwargs)

    monkeypatch.setattr(direct_static_update, "retire_file", stop_at_spec_dock)
    code, result = _run(
        capsys, "installation", "update", "--target", str(target), "--backup-dir", str(tmp_path / "b"), "--yes"
    )
    assert code == 6 and result["status"] == "partial"
    assert ".claude/skills/spec-dock/SKILL.md" not in result["data"]["result"]["retired_paths"]
    assert _warnings(result) == [_expected(target, f".claude/skills/{SLOTS[0]}")]
