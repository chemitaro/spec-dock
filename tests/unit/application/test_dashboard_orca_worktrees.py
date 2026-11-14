"""Recorded worktrees in dashboard JSON and revisions (iss-00591 T-04, T-05)."""

from __future__ import annotations

from dataclasses import replace
import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.application import dashboard_scope_details
from spec_dock.runtime.application.contracts import GitWorktreeRecord
from spec_dock.runtime.application.dashboard_site import DashboardSite
from tests.support.dashboard import NOW, node, snapshot
from tests.support.dashboard_site import register, snapshot_file, write_snapshot
from tests.unit.application.test_dashboard_orca_web import get, http_for

if TYPE_CHECKING:
    from pathlib import Path


def test_structure_and_scope_include_all_matching_worktrees_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    state, catalog = tmp_path / "state", tmp_path / "main" / "catalog"
    register(state, "github.com/o/r", catalog)
    write_snapshot(
        state, replace(snapshot(node(471, "epic"), node(591, "issue", parent=471)), repository="github.com/o/r")
    )
    paths = [tmp_path / name for name in ("main", "catalog", "first", "second", "detached")]
    records = [
        GitWorktreeRecord(path, "a", branch, detached=branch is None)
        for path, branch in zip(
            paths, ("main", "spec-dock/canonical", "topic/iss-00591", "iss-00591-2", None), strict=True
        )
    ]
    calls: list[Path] = []

    def lister(root: Path, *, timeout: float) -> list[GitWorktreeRecord]:
        calls.append(root)
        return records

    monkeypatch.setattr(dashboard_scope_details, "worktree_list", lister)
    http = http_for(DashboardSite(state, now=lambda: NOW, user_config=tmp_path / "config.json"))
    document = json.loads(get(http, "/api/v1/r/github.com/o/r/structure").body)
    assert calls == [catalog]
    assert document["worktrees"] == {"status": "ok", "paths": list(map(str, paths))}
    scopes = {item["id"]: item for item in document["scopes"]}
    expected = [{"path": str(paths[2]), "branch": "topic/iss-00591"}, {"path": str(paths[3]), "branch": "iss-00591-2"}]
    assert scopes["iss-00591"]["worktrees"] == expected
    assert scopes["iss-00591"]["branch"] == "topic/iss-00591"
    assert scopes["epic-00471"]["worktrees"] == []
    scope = json.loads(get(http, "/api/v1/r/github.com/o/r/scopes/iss-00591").body)
    assert scope["scope"]["worktrees"] == scope["details"]["worktrees"]["items"] == expected
    snapshot_file(state, "github.com/o/r").unlink()
    empty = json.loads(get(http, "/api/v1/r/github.com/o/r/structure").body)
    assert empty["worktrees"] == {"status": "unreadable", "paths": []}


@pytest.mark.parametrize("mode", ["failure", "timeout", "missing", "ambiguous"])
def test_unreadable_inventory_supplies_no_paths_or_scope_records(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    state, catalog = tmp_path / "state", tmp_path / "main" / "catalog"
    register(state, "github.com/o/r", catalog)
    write_snapshot(state, replace(snapshot(node(591, "issue")), repository="github.com/o/r"))
    if mode == "missing":
        catalog.rmdir()
    elif mode == "ambiguous":
        register(state, "github.com/o/r", tmp_path / "second" / "catalog")

    def lister(root: Path, *, timeout: float) -> list[GitWorktreeRecord]:
        if mode == "timeout":
            raise TimeoutError("git timed out")
        raise OSError("git failed")

    monkeypatch.setattr(dashboard_scope_details, "worktree_list", lister)
    http = http_for(DashboardSite(state, now=lambda: NOW, user_config=tmp_path / "config.json"))
    document = json.loads(get(http, "/api/v1/r/github.com/o/r/structure").body)
    assert document["schema"] == "specdock.dashboard/v1"
    assert document["worktrees"] == {"status": "unreadable", "paths": []}
    (scope,) = document["scopes"]
    assert scope["id"] == "iss-00591" and scope["number"] == 591
    assert scope["branch"] is None and scope["assurance"] is None and scope["worktrees"] == []


def test_worktree_signature_changes_for_git_inventory_and_branch_changes(tmp_path: Path) -> None:
    from spec_dock.runtime.infra.worktree_signature import worktree_signature
    from tests.support.canonical_repo import add_worktree, bare_remote, clone, git

    main = clone(bare_remote(tmp_path / "remote.git"), tmp_path / "main")
    before = worktree_signature(main)
    assert before is not None and worktree_signature(main) == before
    linked = add_worktree(main, tmp_path / "linked", "feature")
    added = worktree_signature(main)
    assert added != before and worktree_signature(main) == added
    git(linked, "switch", "-c", "second-feature")
    switched = worktree_signature(main)
    assert switched != added
    moved = tmp_path / "moved"
    git(main, "worktree", "move", str(linked), str(moved))
    relocated = worktree_signature(main)
    assert relocated != switched
    git(main, "worktree", "remove", str(moved))
    removed = worktree_signature(main)
    assert removed != relocated
    git(main, "switch", "-c", "second-main")
    assert worktree_signature(main) != removed
    assert worktree_signature(None) is None
    assert worktree_signature(tmp_path / "missing") is None
    plain = tmp_path / "plain"
    plain.mkdir()
    (plain / ".git").write_text("gitdir: elsewhere\n")
    assert worktree_signature(plain) is None


def test_revision_changes_when_a_linked_worktree_is_added(tmp_path: Path) -> None:
    from tests.support.canonical_repo import add_worktree, bare_remote, clone

    main = clone(bare_remote(tmp_path / "remote.git"), tmp_path / "main")
    state, catalog = tmp_path / "state", main / "catalog"
    register(state, "github.com/o/r", catalog)
    write_snapshot(state, replace(snapshot(node(591, "issue")), repository="github.com/o/r"))
    http = http_for(DashboardSite(state, now=lambda: NOW, user_config=tmp_path / "config.json"))
    route = "/api/v1/r/github.com/o/r/revision"
    before = json.loads(get(http, route).body)["revision"]
    assert json.loads(get(http, route).body)["revision"] == before
    add_worktree(main, tmp_path / "linked", "feature")
    assert json.loads(get(http, route).body)["revision"] != before
