"""canonical worktree, workbench and installation expectations (iss-00431)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.canonical_repo import git
from tests.support.canonical_scopes import CanonicalWorld

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "Plan")
    world.scope("initiative", 2, "Other")
    return world


def test_worktree_list_and_show_mark_the_catalog(world: CanonicalWorld) -> None:
    code, payload = world.run("worktree", "list")
    assert code == 0, payload
    rows = {item["path"]: item["catalog"] for item in payload["data"]["result"]["items"]}
    assert rows == {str(world.main): False, str(world.catalog.resolve()): True}
    code, payload = world.run("worktree", "show", str(world.catalog))
    assert code == 0 and payload["data"]["result"]["catalog"] is True


@pytest.mark.parametrize("leaf", [["worktree", "remove"], ["worktree", "bootstrap"]])
def test_the_catalog_is_protected_from_remove_and_bootstrap(world: CanonicalWorld, leaf: list[str]) -> None:
    before = tree_digest(world.catalog.resolve())
    code, payload = world.run(*leaf, str(world.catalog), "--yes")
    assert (code, payload["error"]["code"]) == (3, "CANONICAL_CATALOG_PROTECTED")
    assert payload["recovery"]["instructions"] == ["To detach this clone's catalog, run spec-dock canonical remove."]
    assert tree_digest(world.catalog.resolve()) == before
    assert str(world.catalog.resolve()) in git(world.main, "worktree", "list")


def test_worktree_remove_of_an_ordinary_worktree_still_works(world: CanonicalWorld) -> None:
    linked = world.worktree("feature")
    code, payload = world.run("worktree", "remove", str(linked), "--discard-ignored", "--yes")
    assert code == 0, payload
    assert not linked.exists()


def test_workbench_copy_is_refused_as_shared(world: CanonicalWorld) -> None:
    linked = world.worktree("feature")
    code, payload = world.run("workbench", "copy", "--scope", "init-00001", "--to-worktree", str(linked), "--yes")
    assert (code, payload["error"]["code"]) == (3, "CANONICAL_WORKBENCH_SHARED")


def test_expect_current_is_checked_against_the_snapshot(world: CanonicalWorld) -> None:
    world.select("init-00001", 1)
    assert world.run("worktree", "list", "--expect-current", "init-00001")[0] == 0
    code, payload = world.run("worktree", "list", "--expect-current", "init-00002")
    assert (code, payload["error"]["code"]) == (3, "PRECONDITION_FAILED")


def test_worktree_create_with_expect_current(world: CanonicalWorld) -> None:
    world.select("init-00001", 1)
    trees = world.tmp_path / "trees"
    code, payload = world.run(
        "worktree", "create", "wrong", "--base", "HEAD", "--root", str(trees), "--expect-current", "init-00002", "--yes"
    )
    assert (code, payload["error"]["code"]) == (3, "PRECONDITION_FAILED")
    assert not trees.exists()
    code, payload = world.run(
        "worktree", "create", "right", "--base", "HEAD", "--root", str(trees), "--expect-current", "init-00001", "--yes"
    )
    assert code == 0, payload
    assert (trees / "right/spec-dock/initiatives").is_symlink()


@pytest.mark.parametrize(
    "leaf",
    [["installation", "show"], ["installation", "update", "--dry-run"], ["installation", "uninstall", "--dry-run"]],
)
def test_installation_with_expect_current(world: CanonicalWorld, leaf: list[str]) -> None:
    world.select("init-00001", 1)
    code, payload = world.run(*leaf, "--expect-current", "init-00001")
    assert (code, payload["error"]) == (0, None), payload
    assert payload["status"] in ("succeeded", "planned")
    code, payload = world.run(*leaf, "--expect-current", "init-00002")
    assert (code, payload["error"]["code"]) == (3, "PRECONDITION_FAILED")
    assert payload["error"]["message"] == "direct target does not match --expect-current"
