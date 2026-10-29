"""Reading commands write only the structure snapshot; only Issue 432's writing commands stay unimplemented."""

from __future__ import annotations

from typing import TYPE_CHECKING

from spec_dock.runtime.cli.catalog import LEAF_PATHS
from spec_dock.runtime.commands.canonical_dispatch import CANONICAL_HANDLERS, REPOSITORY_INDEPENDENT_HANDLERS
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.canonical_repo import git
from tests.support.canonical_scopes import CanonicalWorld

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

READING = [
    ["scope", "show", "iss-00003"],
    ["scope", "list"],
    ["dependency", "list", "iss-00003"],
    ["dependency", "check", "iss-00003"],
    ["dependency", "check", "iss-00003", "--source", "github"],
    ["active", "show"],
    ["artifact", "list", "--scope", "iss-00003"],
    ["artifact", "show", "<artifact>", "--scope", "iss-00003"],
    ["branch", "show", "iss-00003"],
    ["worktree", "list"],
    ["worktree", "show", "<main>"],
    ["workspace", "sync"],
    ["workspace", "sync", "--source", "github"],
    ["workspace", "validate"],
    ["workspace", "doctor"],
    ["canonical", "status", "--structure"],
]


def test_reading_commands_change_no_catalog_git_checkout_or_github(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "Plan")
    world.scope("epic", 2, "Core", parent=1)
    world.scope("issue", 3, "Leaf", parent=2)
    artifacts = world.catalog / "iss-00003/artifacts"
    artifacts.mkdir()
    (artifacts / "20261026t000000z-note.md").write_text("# note\n", encoding="utf-8")
    world.select("iss-00003", 3)
    artifact = world.run("artifact", "list", "--scope", "iss-00003")[1]["data"]["result"]["items"][0]["id"]
    catalog, dot_git = world.catalog.resolve(), world.main / ".git"
    before = (tree_digest(catalog), tree_digest(dot_git), git(world.main, "status", "--porcelain", "--ignored"))
    for argv in READING:
        world.age_probe()
        values = {"<artifact>": artifact, "<main>": str(world.main)}
        code, payload = world.run(*(values.get(item, item) for item in argv))
        assert code == 0, (argv, payload)
        after = (tree_digest(catalog), tree_digest(dot_git), git(world.main, "status", "--porcelain", "--ignored"))
        assert after == before, argv
    assert world.fake().writes() == []


def test_only_the_writing_commands_of_issue_432_lack_a_canonical_handler() -> None:
    unhandled = {
        leaf
        for leaf in LEAF_PATHS
        if leaf not in CANONICAL_HANDLERS
        and leaf not in REPOSITORY_INDEPENDENT_HANDLERS
        and not leaf.startswith("installation ")
        and leaf not in ("help", "completion")
    }
    assert unhandled == {
        "scope create initiative",
        "scope create epic",
        "scope create issue",
        "scope import github initiative",
        "scope import github epic",
        "scope import github issue",
        "scope edit",
        "scope close",
        "scope reopen",
        "scope delete",
        "dependency add",
        "dependency remove",
        "artifact create",
        "artifact import file",
        "work start",
        "work finish",
    }
