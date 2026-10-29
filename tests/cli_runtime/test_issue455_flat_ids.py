"""Flat `<catalog>/<bucket>/<ID>/` directories and GitHub kind-label changes in canonical mode (iss-00455, iss-00460).

GitHub moves #454 from `spec-dock:issue` to `spec-dock:epic`, so its ID becomes `epic-00454` while the catalog
keeps `iss-00454/`. SpecDock renames nothing: checks report SCOPE_KIND_CHANGED once, reading commands warn,
branch and selection writes stop with exit 3, and the old ID names the current one instead of SCOPE_NOT_FOUND.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.canonical_repo import git
from tests.support.canonical_scopes import CanonicalWorld

if TYPE_CHECKING:
    from pathlib import Path

RECOVERY = (
    "Restore the GitHub kind label. If the new kind is intended, create the Scope again with that kind "
    "(spec-dock scope create), move the old directory's contents into the new <ID>/, then run "
    "spec-dock scope delete <current ID>."
)


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "Plan")
    world.scope("epic", 2, "Core", parent=1)
    world.scope("issue", 3, "Leaf", parent=2)
    world.scope("issue", 454, "Moving", parent=2)
    assert world.run("scope", "list")[0] == 0  # the snapshot first knows #454 as iss-00454

    def relabel(fake: Any) -> None:
        issue = fake.issue(454)
        issue.labels = sorted({*issue.labels} - {"spec-dock:issue"} | {"spec-dock:epic"})
        fake.set_parent(454, 1)
        fake.touch(454)

    world.edit(relabel)
    world.age_probe()
    return world


def _kind_changed(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in payload["warnings"] if item["code"] == "SCOPE_KIND_CHANGED"]


def test_validate_reports_one_kind_change_and_no_missing_pair(world: CanonicalWorld) -> None:
    code, payload = world.run("workspace", "validate")
    assert (code, payload["error"]["code"]) == (7, "WORKSPACE_VALIDATION_FAILED")
    findings = payload["data"]["result"]["findings"]
    about_454 = [item for item in findings if item["details"].get("number") == 454 or "00454" in item["message"]]
    assert [item["code"] for item in about_454] == ["SCOPE_KIND_CHANGED"]
    details = about_454[0]["details"]
    assert (details["current_id"], details["scope_id"], details["directories"]) == (
        "epic-00454",
        "epic-00454",
        ["iss-00454"],
    )
    assert details["next_step"] == RECOVERY
    assert not {"SCOPE_DIRECTORY_SLUG_MISMATCH", "SCOPE_DIRECTORY_DUPLICATE"} & {item["code"] for item in findings}
    assert _kind_changed(payload) == []  # a finding here, not also a warning


def test_both_old_and_new_directories_still_give_one_kind_change(world: CanonicalWorld) -> None:
    (world.catalog / "00000-00999/epic-00454").mkdir()
    (world.catalog / "00000-00999/init-00454").mkdir()
    code, payload = world.run("workspace", "validate")
    assert code == 7
    findings = [item for item in payload["data"]["result"]["findings"] if item["code"] == "SCOPE_KIND_CHANGED"]
    assert [item["details"]["directories"] for item in findings] == [["init-00454", "iss-00454"]]
    assert "SCOPE_ISSUE_MISSING" not in {item["code"] for item in payload["data"]["result"]["findings"]}


def test_an_undecided_kind_with_a_directory_is_only_its_label_anomaly(world: CanonicalWorld) -> None:
    def two_kinds(fake: Any) -> None:
        issue = fake.issue(3)
        issue.labels = sorted({*issue.labels, "spec-dock:epic"})
        fake.touch(3)

    world.edit(two_kinds)
    code, payload = world.run("workspace", "validate")
    assert code == 7
    about_3 = {
        item["code"]
        for item in payload["data"]["result"]["findings"]
        if "00003" in item["message"] or item["details"].get("number") == 3
    }
    assert "KIND_LABEL_MULTIPLE" in about_3
    assert not {"SCOPE_ISSUE_MISSING", "SCOPE_KIND_CHANGED"} & about_3


@pytest.mark.parametrize("old", ["iss-00454", "ISS-00454", "iss-454"])
def test_an_old_id_names_the_current_one_instead_of_not_found(world: CanonicalWorld, old: str) -> None:
    code, payload = world.run("scope", "show", old)
    assert (code, payload["error"]["code"]) == (3, "SCOPE_KIND_CHANGED")
    assert payload["error"]["details"]["current_id"] == "epic-00454"
    assert payload["error"]["details"]["requested"] == "iss-00454"
    assert payload["recovery"]["instructions"] == [RECOVERY]


def test_an_old_id_in_expect_current_is_also_a_kind_change(world: CanonicalWorld) -> None:
    code, payload = world.run("scope", "show", "iss-00003", "--expect-current", "iss-00454")
    assert (code, payload["error"]["code"]) == (3, "SCOPE_KIND_CHANGED")


def test_without_the_catalog_an_old_id_is_still_decided_by_the_snapshot(world: CanonicalWorld) -> None:
    (world.main / "spec-dock/initiatives").unlink()
    code, payload = world.run("branch", "show", "iss-00454")
    assert (code, payload["error"]["code"]) == (3, "SCOPE_KIND_CHANGED")
    assert payload["error"]["details"]["directories"] == []
    assert world.run("branch", "show", "epic-00454")[0] == 0  # no catalog: the new ID cannot be checked


READING = [
    ["scope", "show", "iss-00003"],
    ["scope", "show", "epic-00454"],
    ["scope", "list"],
    ["dependency", "list", "iss-00003"],
    ["dependency", "check", "iss-00003"],
    ["artifact", "list", "--scope", "iss-00003"],
    ["active", "show"],
    ["branch", "show", "epic-00454"],
    ["worktree", "list"],
    ["worktree", "show", "<main>"],
    ["worktree", "list", "--expect-current", "iss-00003"],
    ["workspace", "sync"],
]


@pytest.mark.parametrize("argv", READING, ids=lambda argv: " ".join(argv))
def test_reading_commands_warn_and_succeed(world: CanonicalWorld, argv: list[str]) -> None:
    world.select("iss-00003", 3)
    code, payload = world.run(*(str(world.main) if item == "<main>" else item for item in argv))
    assert code == 0, payload
    [warning] = _kind_changed(payload)
    assert (warning["details"]["current_id"], warning["details"]["directories"]) == ("epic-00454", ["iss-00454"])


def test_the_current_id_shows_without_a_directory(world: CanonicalWorld) -> None:
    code, payload = world.run("scope", "show", "epic-00454")
    assert code == 0, payload
    scope = payload["data"]["result"]["scope"]
    assert (scope["id"], scope["parent_id"], scope["path"], scope["directory_found"]) == (
        "epic-00454",
        "init-00001",
        None,
        False,
    )


@pytest.mark.parametrize("dry_run", [False, True])
@pytest.mark.parametrize("target", ["epic-00454", "iss-00454"])
def test_branch_create_and_switch_stop_before_any_git_write(world: CanonicalWorld, target: str, dry_run: bool) -> None:
    git(world.main, "branch", "epic-00454")
    before = git(world.main, "for-each-ref", "refs/heads"), git(world.main, "branch", "--show-current")
    extra = ["--dry-run"] if dry_run else []
    for argv in (["branch", "create", target, "--base", "HEAD"], ["branch", "switch", target]):
        code, payload = world.run(*argv, *extra, "--yes")
        assert (code, payload["error"]["code"]) == (3, "SCOPE_KIND_CHANGED"), argv
        assert payload["error"]["details"]["current_id"] == "epic-00454"
        assert payload["effects"] == []
    assert (git(world.main, "for-each-ref", "refs/heads"), git(world.main, "branch", "--show-current")) == before


def test_active_set_stops_for_a_re_kinded_target(world: CanonicalWorld) -> None:
    (world.catalog / "00000-00999/epic-00454").mkdir()
    world.select("epic-00454", 454)
    code, payload = world.run("active", "set", "epic-00454", "--yes")
    assert (code, payload["error"]["code"]) == (3, "SCOPE_KIND_CHANGED")
    assert not (world.main / "spec-dock/active/epic").is_symlink()


def test_active_set_stops_when_an_ancestor_changed_kind(world: CanonicalWorld) -> None:
    def relabel_parent(fake: Any) -> None:
        epic = fake.issue(2)
        epic.labels = sorted({*epic.labels} - {"spec-dock:epic"} | {"spec-dock:initiative"})
        fake.set_parent(2, None)
        fake.touch(2)

    world.edit(relabel_parent)
    world.age_probe()
    world.select("iss-00003", 3)
    code, payload = world.run("active", "set", "iss-00003", "--yes")
    assert (code, payload["error"]["code"]) == (3, "SCOPE_KIND_CHANGED")


def test_worktree_create_with_expect_current_stops(world: CanonicalWorld) -> None:
    (world.catalog / "00000-00999/epic-00454").mkdir()
    world.select("epic-00454", 454)
    trees = world.tmp_path / "trees"
    catalog = tree_digest(world.catalog.resolve())
    code, payload = world.run(
        "worktree", "create", "next", "--base", "HEAD", "--root", str(trees), "--expect-current", "epic-00454", "--yes"
    )
    assert (code, payload["error"]["code"]) == (3, "SCOPE_KIND_CHANGED")
    assert not trees.exists() and tree_digest(world.catalog.resolve()) == catalog


def test_status_structure_shows_the_kind_change_as_its_first_anomaly(world: CanonicalWorld) -> None:
    code, payload = world.run("canonical", "status", "--structure")
    assert code == 0, payload
    item = payload["data"]["structure"]
    assert [entry["code"] for entry in item["anomalies"]] == ["SCOPE_KIND_CHANGED"]
    assert item["next_step"] == RECOVERY


@pytest.mark.parametrize("leaf", [["workspace", "validate"], ["workspace", "doctor"]])
def test_an_old_id_in_expect_current_of_a_check_is_a_kind_change(world: CanonicalWorld, leaf: list[str]) -> None:
    """The structure findings must not hide the old ID behind PRECONDITION_FAILED."""
    code, payload = world.run(*leaf, "--expect-current", "iss-00454")
    assert (code, payload["error"]["code"]) == (3, "SCOPE_KIND_CHANGED")
    assert payload["error"]["details"]["current_id"] == "epic-00454"


def test_an_unreadable_scope_directory_keeps_the_structure_item_unavailable(world: CanonicalWorld) -> None:
    import os

    locked = world.catalog / "00000-00999/iss-00003"
    locked.chmod(0)
    try:
        if os.access(locked, os.X_OK):
            pytest.skip("this user can read a mode-000 directory")
        code, payload = world.run("canonical", "status", "--structure")
    finally:
        locked.chmod(0o755)
    assert code == 0, payload
    item = payload["data"]["structure"]
    assert (item["status"], item["code"]) == ("unavailable", "LOCAL_IO_FAILED")
    assert payload["data"]["catalog"]["status"]  # the other items are still reported


def test_the_reading_side_public_shapes_used_by_later_issues(world: CanonicalWorld) -> None:
    """The interface I-5, I-11 and I-15 call directly (iss-00455 design, 責務・Interface)."""
    from spec_dock.runtime.application import canonical_errors, canonical_scopes, canonical_workspace
    from spec_dock.runtime.application.canonical_errors import CanonicalCommandError
    from spec_dock.runtime.application.project_context import resolve_context

    context = resolve_context(str(world.main), world.main)
    scopes = canonical_scopes.load_canonical_scopes(context, timeout=30, link=True)
    rebuilt = canonical_scopes.build_canonical_scopes(context, scopes.repository, scopes.fresh, scopes.catalog)
    assert (rebuilt.views, rebuilt.directories, rebuilt.kind_changes) == (
        scopes.views,
        scopes.directories,
        scopes.kind_changes,
    )
    assert set(scopes.kind_changes) == {454}
    assert scopes.lineage("iss-00003") == ("iss-00003", "epic-00002", "init-00001")
    assert scopes.lineage("epic-00454") == ("epic-00454", "init-00001")
    assert scopes.lineage("iss-00454") == ()
    scopes.require_kind_unchanged("iss-00003", "epic-00002")
    expected = {
        "scope_id": "epic-00454",
        "number": 454,
        "current_id": "epic-00454",
        "directories": ["iss-00454"],
        "next_step": canonical_errors.SCOPE_KIND_CHANGED_RECOVERY,
    }
    with pytest.raises(CanonicalCommandError) as stopped:
        scopes.require_kind_unchanged("iss-00003", "epic-00454")
    assert (stopped.value.code, stopped.value.exit_code, stopped.value.details) == ("SCOPE_KIND_CHANGED", 3, expected)
    assert stopped.value.recovery == (canonical_errors.SCOPE_KIND_CHANGED_RECOVERY,)
    [warning] = scopes.kind_change_warnings()
    assert (warning.code, warning.details) == ("SCOPE_KIND_CHANGED", expected)
    assert scopes.warnings() == (*scopes.snapshot_warnings(), warning)
    error = canonical_scopes.kind_change_error(scopes.kind_changes[454], requested="iss-00454")
    assert error.details == {**expected, "requested": "iss-00454"}
    for spelling in ("iss-00454", "iss-454"):
        with pytest.raises(CanonicalCommandError) as old:
            canonical_scopes.resolve_canonical_scope(context, scopes, spelling)
        assert old.value.details == {**expected, "requested": "iss-00454"}
    canonical_scopes.refuse_old_ids(scopes, None, "@current", "gh:example/repo#454", "epic-00454", "not an id")
    assert canonical_scopes.resolve_canonical_scope(context, scopes, "epic-00454").id == "epic-00454"
    with pytest.raises(CanonicalCommandError):
        canonical_scopes.check_canonical_scope_expectations(
            context, scopes, None, target=None, expected_current="iss-00454", expected_backend=None
        )
    report = canonical_workspace.directory_anomalies(scopes)
    assert isinstance(report, canonical_workspace.DirectoryReport)
    assert [item.code for item in report.errors] == ["SCOPE_KIND_CHANGED"] and report.warnings == ()
