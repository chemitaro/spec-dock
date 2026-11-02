"""Selection changes keep the navigation links under spec-dock/active in step, in canonical mode.

Replaces tests/cli_runtime/test_issue416_active_links.py (iss-00440); the two finish cases are in
test_issue440_g1_work_finish.py, which has the save-wait fixture. Canonical links point through the catalog link
(`../initiatives/<bucket>/<ID>`); the fallback is the checkout's spec-dock/system/active-none/<role>.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.runtime.infra.start_lock import StartLock
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.canonical_repo import git
from tests.support.legacy_contracts_g1 import chain_world, commit

if TYPE_CHECKING:
    from pathlib import Path

    from tests.support.canonical_writes import WriteWorld

ROLES = ("initiative", "epic", "issue")
CHAIN = {
    "initiative": "../initiatives/00000-00999/init-00001",
    "epic": "../initiatives/00000-00999/epic-00002",
    "issue": "../initiatives/00000-00999/iss-00003",
}
FALLBACK = {role: f"../system/active-none/{role}" for role in ROLES}


def with_fallback(world: WriteWorld) -> WriteWorld:
    for role in ROLES:
        fallback = world.main / "spec-dock/system/active-none" / role
        fallback.mkdir(parents=True)
        (fallback / "README.md").write_text(f"# no {role}\n", encoding="utf-8")
    commit(world.main, "fallback", "spec-dock/system")
    return world


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> WriteWorld:
    return with_fallback(chain_world(tmp_path, monkeypatch, capsys, write=True))  # type: ignore[arg-type]


def links(root: Path) -> dict[str, str]:
    active = root / "spec-dock/active"
    return {role: str((active / role).readlink()) for role in ROLES if (active / role).is_symlink()}


def link_effects(result: dict[str, Any]) -> list[tuple[str, str]]:
    return [(effect["target"], effect["status"]) for effect in result["effects"] if effect["kind"] == "active.link"]


def warning_reasons(result: dict[str, Any]) -> list[tuple[str, object]]:
    return [(item["code"], item["details"].get("reason")) for item in result["warnings"]]


def link_warning_reasons(result: dict[str, Any]) -> set[object]:
    return {reason for code, reason in warning_reasons(result) if code == "ACTIVE_LINK_NOT_UPDATED"}


def started(world: WriteWorld) -> str:
    code, result = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 0, result
    return str(result["data"]["branch_after"])


def test_work_start_dry_run_plans_links_without_writing_them(world: WriteWorld) -> None:
    code, result = world.run("work", "start", "epic-00002", "--base", "HEAD", "--dry-run")
    assert code == 0 and result["status"] == "planned", result
    # Canonical start plans only its Git and selection effects; the links follow after a real start.
    assert link_effects(result) == []
    assert not (world.main / "spec-dock/active").exists()


def test_active_clear_points_every_role_back_to_the_fallback(world: WriteWorld) -> None:
    started(world)
    code, preview = world.run("active", "clear", "--all", "--dry-run")
    assert code == 0 and link_effects(preview) == [(role, "planned") for role in ROLES], preview
    assert links(world.main)["issue"] == CHAIN["issue"]
    code, result = world.run("active", "clear", "--all")
    assert code == 0 and result["status"] == "succeeded", result
    assert links(world.main) == FALLBACK
    assert link_effects(result) == [(role, "succeeded") for role in ROLES]


def test_clear_keeps_links_while_a_selection_remains_and_repairs_them_once_empty(world: WriteWorld) -> None:
    world.scope("epic", 4, "sibling", parent=1)
    started(world)
    before = links(world.main)
    code, result = world.run("active", "clear", "--from", "epic-00004")
    assert code == 0 and result["status"] == "unchanged" and links(world.main) == before, result
    assert world.run("active", "clear", "--all")[0] == 0
    (world.main / "spec-dock/active/issue").unlink()
    (world.main / "spec-dock/active/issue").symlink_to(CHAIN["issue"])
    code, result = world.run("active", "clear", "--all")
    assert code == 0 and result["status"] == "succeeded", result
    assert link_effects(result) == [("initiative", "unchanged"), ("epic", "unchanged"), ("issue", "succeeded")]
    assert links(world.main) == FALLBACK
    code, result = world.run("active", "clear", "--all")
    assert code == 0 and result["status"] == "unchanged", result
    assert result["effects"] == [{"kind": "active.link", "status": "unchanged", "target": role} for role in ROLES]


def test_active_set_current_repairs_links_only_when_they_drifted(world: WriteWorld) -> None:
    started(world)
    code, result = world.run("active", "set", "@current")
    assert code == 0 and result["status"] == "unchanged", result
    (world.main / "spec-dock/active/epic").unlink()
    (world.main / "spec-dock/active/context-pack.md").write_bytes(b"stale")
    code, preview = world.run("active", "set", "@current", "--dry-run")
    assert code == 0 and preview["status"] == "planned", preview
    assert [effect for effect in preview["effects"] if effect["status"] != "unchanged"] == [
        {"kind": "active.link", "status": "planned", "target": "epic"}
    ]
    assert "epic" not in links(world.main)
    code, result = world.run("active", "set", "@current")
    assert code == 0 and result["status"] == "succeeded", result
    assert result["data"]["selection"]["scope_id"] == "iss-00003"
    assert links(world.main) == CHAIN
    assert (world.main / "spec-dock/active/context-pack.md").read_bytes() == b"stale"


def test_occupied_role_is_a_warning_and_the_selection_still_succeeds(world: WriteWorld) -> None:
    kept = world.main / "spec-dock/active/issue"
    kept.mkdir(parents=True)
    (kept / "mine.md").write_bytes(b"mine")
    code, result = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 0 and result["status"] == "succeeded", result
    assert [item for item in warning_reasons(result) if item[0] == "ACTIVE_LINK_NOT_UPDATED"] == [
        ("ACTIVE_LINK_NOT_UPDATED", "occupied")
    ]
    assert link_effects(result) == [("initiative", "succeeded"), ("epic", "succeeded")]
    assert (kept / "mine.md").read_bytes() == b"mine"


def test_unignored_active_directory_is_never_written(world: WriteWorld) -> None:
    ignore = world.main / "spec-dock/.gitignore"
    ignore.write_text(ignore.read_text(encoding="utf-8").replace("\nactive/\n", "\n"), encoding="utf-8")
    commit(world.main, "unignore", "spec-dock/.gitignore")
    code, result = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 0 and result["status"] == "succeeded", result
    assert link_warning_reasons(result) == {"not_ignored"}
    assert link_effects(result) == [] and not (world.main / "spec-dock/active").exists()
    assert git(world.main, "status", "--porcelain") == ""


def test_read_commands_neither_write_nor_depend_on_links(world: WriteWorld) -> None:
    started(world)
    code, with_links = world.run("active", "show")
    for role in ROLES:
        (world.main / "spec-dock/active" / role).unlink()
    (world.main / "spec-dock/active/issue").symlink_to("../system/active-none/issue")
    code_without, without_links = world.run("active", "show")
    assert code == code_without == 0
    assert with_links["data"] == without_links["data"] and without_links["effects"] == []
    assert links(world.main) == {"issue": "../system/active-none/issue"}


def test_link_sync_preserves_every_old_writer_file_and_other_old_state(world: WriteWorld) -> None:
    from tests.support.legacy_contracts_g1 import select_record

    select_record(world, "iss-00003", 3)
    active = world.main / "spec-dock/active"
    active.mkdir()
    for name in ("context-pack.md", "current-runbook.md", "initiative.path", "epic.path", "issue.path"):
        (active / name).write_bytes(b"old generated\r\n")
    (active / "current-runbook.json").mkdir()
    (active / "current-runbook.json/preserve.bin").write_bytes(b"\x00private\xff")
    (active / "notes.md").write_bytes(b"user notes")
    for role in ROLES:
        (active / role).symlink_to(CHAIN["initiative"])
    old = {path.name: path.read_bytes() for path in active.iterdir() if path.is_file() and not path.is_symlink()}
    work = world.main / "spec-dock/.work"
    work.mkdir()
    (work / "active.json").write_bytes(b'{"schema_version":2}\r\n')
    before = tree_digest(work)
    code, result = world.run("active", "clear", "--all")
    assert code == 0 and result["status"] == "succeeded", result
    assert link_effects(result) == [(role, "succeeded") for role in ROLES]
    assert [effect["kind"] for effect in result["effects"]] == [
        "selection.clear",
        "active.link",
        "active.link",
        "active.link",
    ]
    assert result["warnings"] == []
    assert links(world.main) == FALLBACK
    assert {name: (active / name).read_bytes() for name in old} == old
    assert (active / "current-runbook.json/preserve.bin").read_bytes() == b"\x00private\xff"
    assert tree_digest(work) == before
    assert "private" not in json.dumps(result)


def test_tracked_files_under_active_are_never_changed_even_when_ignore_rules_match(world: WriteWorld) -> None:
    tracked = world.main / "spec-dock/active/context-pack.md"
    tracked.parent.mkdir()
    tracked.write_bytes(b"tracked by accident\n")
    commit(world.main, "tracked", "spec-dock/active/context-pack.md")
    code, result = world.run("work", "start", "iss-00003", "--base", "HEAD")
    assert code == 0 and result["status"] == "succeeded", result
    assert link_warning_reasons(result) == {"tracked"}
    assert link_effects(result) == [] and links(world.main) == {}
    assert tracked.read_bytes() == b"tracked by accident\n"
    assert git(world.main, "status", "--porcelain") == ""


def test_clear_from_with_an_empty_selection_also_repairs_the_fallback(world: WriteWorld) -> None:
    started(world)
    assert world.run("active", "clear", "--all")[0] == 0
    (world.main / "spec-dock/active/epic").unlink()
    (world.main / "spec-dock/active/epic").symlink_to(CHAIN["epic"])
    code, result = world.run("active", "clear", "--from", "epic-00002")
    assert code == 0 and result["status"] == "succeeded", result
    assert link_effects(result) == [("initiative", "unchanged"), ("epic", "succeeded"), ("issue", "unchanged")]
    assert links(world.main) == FALLBACK


def test_link_sync_never_waits_for_or_races_a_running_start(world: WriteWorld) -> None:
    started(world)
    before = links(world.main)
    with StartLock(world.main / ".git", timeout=0):
        code, result = world.run("active", "clear", "--all")
    assert code == 0 and result["status"] == "succeeded", result
    assert result["data"]["selection"]["status"] == "empty"
    assert link_warning_reasons(result) == {"start_in_progress"}
    assert link_effects(result) == [] and links(world.main) == before


def test_link_sync_does_not_write_while_branch_switch_holds_the_start_lock(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.application import canonical_branches

    started(world)
    git(world.main, "branch", "candidate")
    (world.main / "spec-dock/active/epic").unlink()
    before = links(world.main)
    during: list[tuple[int, dict[str, Any]]] = []
    real_run_git = canonical_branches.run_git

    def checkout_with_concurrent_repair(repo: Path, *arguments: str, **options: Any) -> bytes:
        if arguments[:1] == ("checkout",):
            during.append(world.run("active", "set", "@current"))
        return real_run_git(repo, *arguments, **options)

    monkeypatch.setattr(canonical_branches, "run_git", checkout_with_concurrent_repair)
    code, result = world.run("branch", "switch", "iss-00003", "--name", "candidate", "--yes")
    assert code == 0 and result["status"] == "succeeded", result
    [(repair_code, repair)] = during
    assert repair_code == 0 and repair["status"] == "unchanged", repair
    assert link_warning_reasons(repair) == {"start_in_progress"}
    assert links(world.main) == before
    monkeypatch.setattr(canonical_branches, "run_git", real_run_git)
    code, repaired = world.run("active", "set", "@current")
    assert code == 0 and repaired["status"] == "succeeded", repaired
    assert links(world.main)["epic"] == CHAIN["epic"]
