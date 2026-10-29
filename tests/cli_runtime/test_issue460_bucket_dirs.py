"""Scope directories under their number's thousand bucket, and unpadded ID input (iss-00460).

`#1454` lives in `01000-01999/iss-01454/`, the others in `00000-00999/`. Commands show and open
`spec-dock/initiatives/<bucket>/<ID>`, checks report anything outside its bucket as misplaced, and every canonical
ID input accepts `iss-454` for `iss-00454` while every output stays padded.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest

from spec_dock.runtime.domain.canonical_layout import SCOPE_TO_SPEC_DOCK, scope_relative
from tests.support.canonical_repo import git
from tests.support.canonical_scopes import CanonicalWorld

LOW = "00000-00999"


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "Plan")
    world.scope("epic", 2, "Core", parent=1)
    world.scope("issue", 454, "Leaf", parent=2)
    world.scope("issue", 1454, "Far", parent=2)
    return world


def _codes(items: list[dict[str, Any]], code: str) -> list[dict[str, Any]]:
    return [item for item in items if item["code"] == code]


def test_scope_paths_name_the_bucket(world: CanonicalWorld) -> None:
    assert (world.catalog / LOW / "iss-00454").is_dir() and (world.catalog / "01000-01999/iss-01454").is_dir()
    code, payload = world.run("scope", "show", "iss-01454")
    assert code == 0, payload
    assert payload["data"]["result"]["scope"]["path"] == "spec-dock/initiatives/01000-01999/iss-01454"
    code, payload = world.run("scope", "list")
    assert code == 0, payload
    paths = {item["id"]: item["path"] for item in payload["data"]["result"]["items"]}
    assert paths == {
        "init-00001": f"spec-dock/initiatives/{LOW}/init-00001",
        "epic-00002": f"spec-dock/initiatives/{LOW}/epic-00002",
        "iss-00454": f"spec-dock/initiatives/{LOW}/iss-00454",
        "iss-01454": "spec-dock/initiatives/01000-01999/iss-01454",
    }


def test_active_links_and_artifacts_go_through_the_bucket(world: CanonicalWorld) -> None:
    artifacts = world.catalog / "01000-01999/iss-01454/artifacts"
    artifacts.mkdir()
    (artifacts / "20261029t000000z-note.md").write_text("# note\n", encoding="utf-8")
    linked = world.worktree("feature")
    world.select("iss-01454", 1454, checkout=linked)
    code, payload = world.run("active", "set", "iss-01454", "--yes", checkout=linked)
    assert code == 0, payload
    issue = linked / "spec-dock/active/issue"
    assert str(issue.readlink()) == "../initiatives/01000-01999/iss-01454"
    assert (issue / "requirement.md").is_file()
    assert str((linked / "spec-dock/active/epic").readlink()) == f"../initiatives/{LOW}/epic-00002"
    code, payload = world.run("artifact", "list", "--scope", "iss-01454", checkout=linked)
    assert code == 0, payload
    [item] = payload["data"]["result"]["items"]
    assert item["path"] == "spec-dock/initiatives/01000-01999/iss-01454/artifacts/20261029t000000z-note.md"


def test_a_flat_leftover_is_never_the_scopes_place(world: CanonicalWorld) -> None:
    world.scope("issue", 5, "Flat", parent=2, directory=False)
    (world.catalog / "iss-00005").mkdir()
    (world.catalog / "iss-00005/requirement.md").write_text("# r\n", encoding="utf-8")
    code, payload = world.run("scope", "show", "iss-00005")
    assert code == 0, payload
    scope = payload["data"]["result"]["scope"]
    assert (scope["path"], scope["directory_found"]) == (None, False)
    code, payload = world.run("workspace", "validate")
    assert code == 7
    [missing] = _codes(payload["data"]["result"]["findings"], "SCOPE_DIRECTORY_MISSING")
    assert missing["details"]["path"] == f"{LOW}/iss-00005"
    assert f"spec-dock/initiatives/{LOW}/iss-00005/" in missing["details"]["next_step"]
    [misplaced] = _codes(payload["warnings"], "SCOPE_DIRECTORY_MISPLACED")
    assert (misplaced["details"]["path"], misplaced["details"]["reason"], misplaced["details"]["expected"]) == (
        "iss-00005",
        "root",
        f"{LOW}/iss-00005",
    )


def test_checks_report_everything_outside_its_bucket(world: CanonicalWorld) -> None:
    for relative in ("0-999", f"{LOW}/iss-02454", f"{LOW}/iss-00454-old", f"{LOW}/epic-00002/issues"):
        (world.catalog / relative).mkdir(parents=True)
    code, payload = world.run("workspace", "validate")
    assert code == 0, payload
    found = {
        item["details"]["path"]: (item["details"]["reason"], item["details"]["expected"])
        for item in _codes(payload["warnings"], "SCOPE_DIRECTORY_MISPLACED")
    }
    assert found == {
        "0-999": ("bucket", None),
        f"{LOW}/iss-02454": ("bucket", "02000-02999/iss-02454"),
        f"{LOW}/iss-00454-old": ("name", None),
        f"{LOW}/epic-00002/issues": ("nested", None),
    }
    code, payload = world.run("canonical", "status", "--structure")
    assert code == 0, payload
    item = payload["data"]["structure"]
    assert item["status"] == "problem"
    assert {entry["details"]["path"] for entry in item["anomalies"]} == set(found)
    assert item["next_step"].startswith("Move the Scope contents it holds into spec-dock/initiatives/<bucket>/<ID>/")


def test_a_kind_change_is_found_in_the_same_bucket(world: CanonicalWorld) -> None:
    assert world.run("scope", "list")[0] == 0

    def relabel(fake: Any) -> None:
        issue = fake.issue(454)
        issue.labels = sorted({*issue.labels} - {"spec-dock:issue"} | {"spec-dock:epic"})
        fake.set_parent(454, 1)
        fake.touch(454)

    world.edit(relabel)
    world.age_probe()
    code, payload = world.run("workspace", "validate")
    assert code == 7
    findings = payload["data"]["result"]["findings"]
    [change] = _codes(findings, "SCOPE_KIND_CHANGED")
    assert (change["details"]["current_id"], change["details"]["directories"]) == ("epic-00454", ["iss-00454"])
    assert _codes(findings, "SCOPE_DIRECTORY_MISSING") == _codes(findings, "SCOPE_ISSUE_MISSING") == []
    assert _codes(payload["warnings"], "SCOPE_DIRECTORY_MISPLACED") == []


EXPECTING = [
    ["scope", "show", "iss-01454"],
    ["scope", "list"],
    ["dependency", "list", "iss-01454"],
    ["dependency", "check", "iss-01454"],
    ["active", "show"],
    ["artifact", "list", "--scope", "iss-01454"],
    ["branch", "show", "iss-01454"],
    ["workspace", "validate"],
    ["workspace", "sync"],
    ["workspace", "doctor"],
    ["worktree", "list"],
    ["worktree", "show", "<main>"],
    ["installation", "show"],
]
UNPADDED = [
    ["scope", "show", "iss-454"],
    ["scope", "show", "iss-000454"],
    ["scope", "show", " ISS-454 "],
    ["scope", "list", "--parent", "epic-2"],
    ["dependency", "list", "iss-454"],
    ["dependency", "check", "iss-454"],
    ["artifact", "list", "--scope", "iss-454"],
    ["artifact", "show", "<artifact>", "--scope", "iss-454"],
    ["branch", "show", "iss-454"],
    *([*argv, "--expect-current", "iss-454"] for argv in EXPECTING),
    ["scope", "list", "--expect-current", "iss-0454"],
]


@pytest.mark.parametrize("argv", UNPADDED, ids=lambda argv: " ".join(argv).strip())
def test_unpadded_ids_are_accepted_and_every_output_is_padded(world: CanonicalWorld, argv: list[str]) -> None:
    artifacts = world.catalog / LOW / "iss-00454/artifacts"
    artifacts.mkdir()
    (artifacts / "20261029t000000z-note.md").write_text("# note\n", encoding="utf-8")
    world.select("iss-00454", 454)
    [artifact] = world.run("artifact", "list", "--scope", "iss-00454")[1]["data"]["result"]["items"]
    named = {"<main>": str(world.main), "<artifact>": artifact["id"]}
    code, payload = world.run(*(named.get(item, item) for item in argv))
    assert code == 0, payload
    text = json.dumps(payload)
    assert "iss-454" not in text and "iss-0454" not in text and "iss-000454" not in text
    if argv[:2] == ["scope", "show"] and argv[2] != "iss-01454":
        scope = payload["data"]["result"]["scope"]
        assert (scope["id"], scope["path"]) == ("iss-00454", f"spec-dock/initiatives/{LOW}/iss-00454")


def test_writing_entries_accept_unpadded_ids(world: CanonicalWorld) -> None:
    world.select("iss-00454", 454)
    code, payload = world.run("active", "set", "iss-454", "--yes")
    assert code == 0, payload
    assert str((world.main / "spec-dock/active/issue").readlink()) == f"../initiatives/{LOW}/iss-00454"
    for role in ("initiative", "epic", "issue"):
        (world.main / "spec-dock/system/active-none" / role).mkdir(parents=True, exist_ok=True)
    code, payload = world.run("active", "clear", "--from", "iss-454", "--yes")
    assert code == 0, payload
    assert str((world.main / "spec-dock/active/issue").readlink()) == "../system/active-none/issue"
    code, payload = world.run("branch", "create", "iss-454", "--base", "HEAD", "--yes")
    assert code == 0, payload
    assert "iss-00454" in git(world.main, "for-each-ref", "--format=%(refname:short)", "refs/heads").split()
    code, payload = world.run("branch", "switch", "iss-454", "--yes")
    assert code == 0, payload
    assert git(world.main, "branch", "--show-current").strip() == "iss-00454"
    world.select("iss-00454", 454)
    trees = world.tmp_path / "trees"
    code, payload = world.run(
        "worktree", "create", "next", "--base", "HEAD", "--root", str(trees), "--expect-current", "iss-454", "--yes"
    )
    assert code == 0, payload


def test_unpadded_directory_names_are_not_scope_directories(world: CanonicalWorld) -> None:
    world.scope("issue", 7, "Short", parent=2, directory=False)
    (world.catalog / LOW / "iss-7").mkdir()
    code, payload = world.run("scope", "show", "iss-7")
    assert code == 0, payload
    assert payload["data"]["result"]["scope"]["id"] == "iss-00007"
    assert payload["data"]["result"]["scope"]["path"] is None


def test_links_three_levels_up_open_spec_dock_docs_from_main_and_linked_worktrees(world: CanonicalWorld) -> None:
    """A Markdown link resolves by text in each checkout; a symlink resolves through the catalog's real place."""
    linked = world.worktree("feature")
    for checkout in (world.main, linked):
        docs = checkout / "spec-dock/docs/authoring"
        docs.mkdir(parents=True, exist_ok=True)
        (docs / "requirement.md").write_text("# guide\n", encoding="utf-8")
    rules = world.main / "spec-dock/docs/rules/issue"
    rules.mkdir(parents=True, exist_ok=True)
    (rules / "artifacts.md").write_text("# rules\n", encoding="utf-8")
    scope = world.catalog / scope_relative("iss-01454")
    detail = (SCOPE_TO_SPEC_DOCK / "docs/authoring/requirement.md").as_posix()
    assert detail == "../../../docs/authoring/requirement.md"
    (scope / "artifacts").mkdir(exist_ok=True)
    (scope / "artifacts/rules.md").symlink_to(Path("..") / SCOPE_TO_SPEC_DOCK / "docs/rules/issue/artifacts.md")
    for checkout in (world.main, linked):
        directory = checkout / "spec-dock/initiatives" / scope_relative("iss-01454")
        assert Path(os.path.normpath(directory / detail)).read_text(encoding="utf-8") == "# guide\n"
        assert (directory / "artifacts/rules.md").read_text(encoding="utf-8") == "# rules\n"
