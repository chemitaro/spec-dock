"""Selection changes keep the human navigation links under spec-dock/active in step."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING, Any

from spec_dock.cli import main
from tests.cli_runtime.test_issue413_contract import add_scope, make_workspace
from tests.cli_runtime.test_issue413_finish import github_fixture

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

INITIATIVE = "initiatives/init-00001-fixture"
EPIC = f"{INITIATIVE}/epics/epic-00002-fixture"
ISSUE = f"{EPIC}/issues/iss-00003-fixture"


def navigable_workspace(root: Path) -> Path:
    make_workspace(root)
    initiative = root / "spec-dock" / INITIATIVE
    epic = add_scope(root, "epic-00002", "epic", "init-00001", initiative)
    add_scope(root, "iss-00003", "issue", "epic-00002", epic)
    (root / "spec-dock/.gitignore").write_text(".agent/\n.workbench/\nactive/\n", encoding="utf-8")
    for role in ("initiative", "epic", "issue"):
        fallback = root / "spec-dock/system/active-none" / role
        fallback.mkdir(parents=True)
        (fallback / "README.md").write_text(f"# no {role}\n", encoding="utf-8")
    git(root, "add", ".")
    git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture")
    return root


def git(root: Path, *arguments: str) -> bytes:
    return subprocess.run(["git", "-C", str(root), *arguments], check=True, capture_output=True).stdout


def links(root: Path) -> dict[str, str]:
    active = root / "spec-dock/active"
    return {
        role: str((active / role).readlink())
        for role in ("initiative", "epic", "issue")
        if (active / role).is_symlink()
    }


def link_effects(result: dict[str, Any]) -> list[tuple[str, str]]:
    return [(effect["target"], effect["status"]) for effect in result["effects"] if effect["kind"] == "active.link"]


def run(root: Path, capsys: pytest.CaptureFixture[str], *arguments: str) -> tuple[int, dict[str, Any]]:
    code = main(["--project", str(root), *arguments, "--json"])
    return code, json.loads(capsys.readouterr().out)


def test_work_start_links_every_role_to_the_selected_issue_chain(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = navigable_workspace(tmp_path / "consumer")
    github_fixture(tmp_path, monkeypatch, {"1": "open", "2": "open", "3": "open"})
    code, result = run(root, capsys, "work", "start", "iss-00003", "--base", "HEAD")
    assert code == 0 and result["status"] == "succeeded", result
    assert links(root) == {"initiative": f"../{INITIATIVE}", "epic": f"../{EPIC}", "issue": f"../{ISSUE}"}
    assert (root / "spec-dock/active/issue/requirement.md").read_text(encoding="utf-8") == "# Fixture\n"
    assert link_effects(result) == [("initiative", "succeeded"), ("epic", "succeeded"), ("issue", "succeeded")]
    assert git(root, "status", "--porcelain") == b""


def test_work_start_dry_run_plans_links_without_writing_them(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = navigable_workspace(tmp_path / "consumer")
    github_fixture(tmp_path, monkeypatch, {"1": "open", "2": "open", "3": "open"})
    code, result = run(root, capsys, "work", "start", "epic-00002", "--base", "HEAD", "--dry-run")
    assert code == 0 and result["status"] == "planned", result
    assert link_effects(result) == [("initiative", "planned"), ("epic", "planned"), ("issue", "planned")]
    assert not (root / "spec-dock/active").exists()


FALLBACK = {role: f"../system/active-none/{role}" for role in ("initiative", "epic", "issue")}


def started(root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> str:
    github_fixture(tmp_path, monkeypatch, {"1": "open", "2": "open", "3": "open"})
    code, result = run(root, capsys, "work", "start", "iss-00003", "--base", "HEAD")
    assert code == 0, result
    return str(result["data"]["branch_after"])


def test_active_clear_points_every_role_back_to_the_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = navigable_workspace(tmp_path / "consumer")
    started(root, tmp_path, monkeypatch, capsys)
    code, preview = run(root, capsys, "active", "clear", "--all", "--dry-run")
    assert code == 0 and link_effects(preview) == [("initiative", "planned"), ("epic", "planned"), ("issue", "planned")]
    assert links(root)["issue"] == f"../{ISSUE}"
    code, result = run(root, capsys, "active", "clear", "--all")
    assert code == 0 and result["status"] == "succeeded", result
    assert links(root) == FALLBACK
    assert link_effects(result) == [("initiative", "succeeded"), ("epic", "succeeded"), ("issue", "succeeded")]


def test_clear_keeps_links_while_a_selection_remains_and_repairs_them_once_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = navigable_workspace(tmp_path / "consumer")
    add_scope(root, "epic-00004", "epic", "init-00001", root / "spec-dock" / INITIATIVE)
    git(root, "add", ".")
    git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "sibling")
    started(root, tmp_path, monkeypatch, capsys)
    before = links(root)
    code, result = run(root, capsys, "active", "clear", "--from", "epic-00004")
    assert code == 0 and result["status"] == "unchanged" and links(root) == before, result
    assert run(root, capsys, "active", "clear", "--all")[0] == 0
    (root / "spec-dock/active/issue").unlink()
    (root / "spec-dock/active/issue").symlink_to(f"../{ISSUE}")
    code, result = run(root, capsys, "active", "clear", "--all")
    assert code == 0 and result["status"] == "succeeded", result
    assert link_effects(result) == [("initiative", "unchanged"), ("epic", "unchanged"), ("issue", "succeeded")]
    assert links(root) == FALLBACK
    code, result = run(root, capsys, "active", "clear", "--all")
    assert (
        code == 0
        and result["status"] == "unchanged"
        and result["effects"]
        == [{"kind": "active.link", "status": "unchanged", "target": role} for role in ("initiative", "epic", "issue")]
    )


def test_work_finish_that_clears_the_selection_restores_the_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = navigable_workspace(tmp_path / "consumer")
    started(root, tmp_path, monkeypatch, capsys)
    code, preview = run(root, capsys, "work", "finish", "iss-00003", "--dry-run")
    assert code == 0 and preview["status"] == "planned", preview
    assert link_effects(preview) == [("initiative", "planned"), ("epic", "planned"), ("issue", "planned")]
    assert links(root)["issue"] == f"../{ISSUE}"
    code, result = run(root, capsys, "work", "finish", "iss-00003", "--yes")
    assert code == 0 and result["status"] == "succeeded", result
    assert links(root) == FALLBACK
    assert link_effects(result) == [("initiative", "succeeded"), ("epic", "succeeded"), ("issue", "succeeded")]
    assert git(root, "status", "--porcelain") == b""


def test_active_set_current_repairs_links_only_when_they_drifted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = navigable_workspace(tmp_path / "consumer")
    started(root, tmp_path, monkeypatch, capsys)
    code, result = run(root, capsys, "active", "set", "@current")
    assert code == 0 and result["status"] == "unchanged", result
    (root / "spec-dock/active/epic").unlink()
    (root / "spec-dock/active/context-pack.md").write_bytes(b"stale")
    code, preview = run(root, capsys, "active", "set", "@current", "--dry-run")
    assert code == 0 and preview["status"] == "planned", preview
    assert preview["effects"] == [
        {"kind": "active.link", "status": "planned", "target": "epic"},
        {"kind": "active.legacy.remove", "status": "planned", "target": "context-pack.md"},
    ]
    assert "epic" not in links(root)
    code, result = run(root, capsys, "active", "set", "@current")
    assert code == 0 and result["status"] == "succeeded", result
    assert result["data"]["selection"]["scope_id"] == "iss-00003"
    assert links(root) == {"initiative": f"../{INITIATIVE}", "epic": f"../{EPIC}", "issue": f"../{ISSUE}"}
    assert not (root / "spec-dock/active/context-pack.md").exists()


def warning_reasons(result: dict[str, Any]) -> list[tuple[str, object]]:
    return [(item["code"], item["details"].get("reason")) for item in result["warnings"]]


def test_occupied_role_is_a_warning_and_the_selection_still_succeeds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = navigable_workspace(tmp_path / "consumer")
    kept = root / "spec-dock/active/issue"
    kept.mkdir(parents=True)
    (kept / "mine.md").write_bytes(b"mine")
    github_fixture(tmp_path, monkeypatch, {"1": "open", "2": "open", "3": "open"})
    code, result = run(root, capsys, "work", "start", "iss-00003", "--base", "HEAD")
    assert code == 0 and result["status"] == "succeeded", result
    assert warning_reasons(result) == [("ACTIVE_LINK_NOT_UPDATED", "occupied")]
    assert link_effects(result) == [("initiative", "succeeded"), ("epic", "succeeded")]
    assert (kept / "mine.md").read_bytes() == b"mine"


def test_unignored_active_directory_is_never_written(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = navigable_workspace(tmp_path / "consumer")
    (root / "spec-dock/.gitignore").write_text(".agent/\n.workbench/\n", encoding="utf-8")
    git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qam", "unignore")
    github_fixture(tmp_path, monkeypatch, {"1": "open", "2": "open", "3": "open"})
    code, result = run(root, capsys, "work", "start", "iss-00003", "--base", "HEAD")
    assert code == 0 and result["status"] == "succeeded", result
    assert {reason for _, reason in warning_reasons(result)} == {"not_ignored"}
    assert link_effects(result) == [] and not (root / "spec-dock/active").exists()
    assert git(root, "status", "--porcelain") == b""


def test_read_commands_neither_write_nor_depend_on_links(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = navigable_workspace(tmp_path / "consumer")
    started(root, tmp_path, monkeypatch, capsys)
    code, with_links = run(root, capsys, "active", "show")
    for role in ("initiative", "epic", "issue"):
        (root / "spec-dock/active" / role).unlink()
    (root / "spec-dock/active/issue").symlink_to("../system/active-none/issue")
    code_without, without_links = run(root, capsys, "active", "show")
    assert code == code_without == 0 and with_links == without_links
    assert links(root) == {"issue": "../system/active-none/issue"}


def test_clear_removes_only_known_legacy_files_and_preserves_other_old_state(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root = navigable_workspace(tmp_path / "consumer")
    active = root / "spec-dock/active"
    active.mkdir()
    for name in ("context-pack.md", "issue.path"):
        (active / name).write_bytes(b"old generated\r\n")
    (active / "current-runbook.json").mkdir()
    (active / "current-runbook.json/preserve.bin").write_bytes(b"\x00private\xff")
    (active / "notes.md").write_bytes(b"user notes")
    for role in ("initiative", "epic", "issue"):
        (active / role).symlink_to(f"../system/active-none/{role}")
    work = root / "spec-dock/.work"
    work.mkdir()
    (work / "active.json").write_bytes(b'{"schema_version":2}\r\n')
    before = tree_digest(work)
    code, result = run(root, capsys, "active", "clear", "--all")
    assert code == 0 and result["status"] == "succeeded", result
    assert [effect for effect in result["effects"] if effect["kind"] == "active.legacy.remove"] == [
        {"kind": "active.legacy.remove", "status": "succeeded", "target": name}
        for name in ("context-pack.md", "issue.path")
    ]
    assert warning_reasons(result) == [("ACTIVE_LEGACY_NOT_REMOVED", "not_a_file")]
    assert sorted(path.name for path in active.iterdir()) == [
        "current-runbook.json",
        "epic",
        "initiative",
        "issue",
        "notes.md",
    ]
    assert (active / "current-runbook.json/preserve.bin").read_bytes() == b"\x00private\xff"
    assert (active / "notes.md").read_bytes() == b"user notes"
    assert tree_digest(work) == before
    assert "private" not in json.dumps(result)
