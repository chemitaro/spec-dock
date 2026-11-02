"""Read-only `workspace sync` over the direct selections of a canonical clone's worktrees (iss-00440, G4).

Replaces the mode-independent tests of tests/integration/test_issue413_sync.py and
tests/cli_runtime/test_workspace_sync_vnext.py, which ran on per-worktree `.meta.json` trees (schema 3). Canonical
sync reads the Scopes and their lifecycle from the GitHub structure snapshot (`--source github` refetches it), so
the legacy `source=local`, per-Issue GET and `.meta.json` assertions are gone; the selection-record contracts stay.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.canonical_repo import git
from tests.support.canonical_scopes import CanonicalWorld

if TYPE_CHECKING:
    from pathlib import Path

    from tests.support.fake_github import FakeGithub


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "Plan")
    world.scope("epic", 2, "Core", parent=1)
    world.scope("issue", 3, "Leaf", parent=2)
    return world


def record_of(checkout: Path) -> Path:
    (record,) = (checkout / "spec-dock/.agent/work-target").glob("target-*.json")
    return record


def counts_of(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["scope_id"]: row for row in data["counts"]}


def untouched(root: Path) -> tuple[str, str]:
    return tree_digest(root), git(root, "status", "--porcelain", "--ignored")


def complete_issue_3(fake: FakeGithub) -> None:
    issue = fake.issue(3)
    issue.state, issue.state_reason = "closed", "completed"


def detach_and_complete_issue_3(fake: FakeGithub) -> None:
    """The selected Issue 3 loses its parent (so its selection is stale) and is completed on GitHub."""
    fake.set_parent(3, None)
    complete_issue_3(fake)


@pytest.mark.parametrize("preview", [False, True])
@pytest.mark.parametrize(
    "pointer",
    [
        b"opaque old generation, never read or repaired",
        b'{"schema_version":1,"generation_id":"' + b"f" * 32 + b'"}',
        b'{"generation_id":"../x"}',
    ],
)
def test_sync_preserves_direct_selection_and_opaque_old_projection(
    world: CanonicalWorld, preview: bool, pointer: bytes
) -> None:
    # Also replaces test_issue413_sync::test_sync_ignores_and_preserves_retired_generations_and_current_pointer.
    world.select("iss-00003", 3)
    record = record_of(world.main)
    agent = world.main / "spec-dock/.agent"
    (agent / "generation.json").write_bytes(pointer)
    previous = agent / "generations" / ("f" * 32)
    previous.mkdir(parents=True)
    (previous / "manifest.json").write_text('{"source":"github","valid":false}')
    (previous / "index.json").write_text('{"private-body":"must not be displayed","state":"completed"}')
    before = untouched(world.main)
    code, result = world.run("workspace", "sync", *(["--dry-run"] if preview else []))
    assert code == 0, result
    data = result["data"]
    assert result["status"] == ("planned" if preview else "succeeded") and result["effects"] == []
    assert data["source"] == "snapshot" and data["complete"] is True
    assert {row["scope_id"]: row["lifecycle"] for row in data["scopes"]} == {
        "init-00001": "open",
        "epic-00002": "open",
        "iss-00003": "open",
    }
    assert counts_of(data)["iss-00003"] == {
        "scope_id": "iss-00003",
        "direct_selected_count": 1,
        "descendant_selected_count": 0,
        "complete": True,
    }
    (row,) = data["worktrees"]
    assert row["selection"]["scope_id"] == "iss-00003" and row["process_state"] == "not_observed"
    assert "private-body" not in json.dumps(result)
    assert untouched(world.main) == before
    assert set(record.parent.iterdir()) == {record} and not (world.main / ".git/spec-dock").exists()
    assert world.fake().writes() == []


def test_sync_offline_mode_refuses_requested_github_observation_before_a_get(world: CanonicalWorld) -> None:
    code, payload = world.run("workspace", "sync")  # the saved structure snapshot that offline mode reads
    assert code == 0, payload
    requests = len(world.fake().requests)
    code, result = world.run("workspace", "sync", "--source", "github", "--offline")
    assert (code, result["error"]["code"]) == (3, "PRECONDITION_FAILED")
    assert result["effects"] == []
    assert len(world.fake().requests) == requests
    assert not (world.main / "spec-dock/.agent").exists()
    code, result = world.run("workspace", "sync", "--offline")
    assert code == 0, result
    assert result["data"]["complete"] is True
    assert len(world.fake().requests) == requests


def test_sync_text_displays_each_worktree_lifecycle_and_selection_counts(world: CanonicalWorld) -> None:
    world.edit(complete_issue_3)
    world.select("iss-00003", 3)
    assert main(["--project", str(world.main), "workspace", "sync", "--source", "github"]) == 0
    output = world.capsys.readouterr()
    assert output.err == ""
    assert "source=github complete=true" in output.out
    assert str(world.main) in output.out
    assert "selection=selected scope_id=iss-00003 lifecycle=completed" in output.out
    assert "process_state=not_observed" in output.out
    # The canonical Scope line also names the GitHub title and carries its counts on the same line.
    assert (
        'scope_id=iss-00003 title="Leaf" github_ref=gh:example/repo#3 lifecycle=completed '
        "direct_selected_count=1 descendant_selected_count=0 complete=true"
    ) in output.out


def test_existing_duplicate_selections_are_displayed_without_automatic_clear(world: CanonicalWorld) -> None:
    linked = world.worktree("linked")
    world.select("iss-00003", 3)
    world.select("iss-00003", 3, checkout=linked)
    records = [record_of(world.main), record_of(linked)]
    before = {record: record.read_bytes() for record in records}
    code, result = world.run("workspace", "sync")
    assert code == 7
    assert result["status"] == "partial" and result["effects"] == []
    data = result["data"]
    assert data["complete"] is False
    assert counts_of(data)["iss-00003"] == {
        "scope_id": "iss-00003",
        "direct_selected_count": 2,
        "descendant_selected_count": 0,
        "complete": False,
    }
    assert len(data["worktrees"]) == 2
    assert all(row["selection"]["status"] == "selected" for row in data["worktrees"])
    assert any(item["code"] == "SELECTION_DUPLICATE" for item in data["findings"])
    assert all(path.read_bytes() == value for path, value in before.items())


def test_stale_duplicate_selections_keep_both_state_and_duplicate_findings(world: CanonicalWorld) -> None:
    linked = world.worktree("linked")
    world.select("iss-00003", 3)
    world.select("iss-00003", 3, checkout=linked)
    records = [record_of(world.main), record_of(linked)]
    before = {record: record.read_bytes() for record in records}
    # The legacy trigger deleted the Scope directory; here the GitHub structure no longer gives Issue 3 a parent.
    world.edit(detach_and_complete_issue_3)
    code, result = world.run("workspace", "sync", "--source", "github")
    assert code == 7
    assert result["status"] == "partial" and result["effects"] == []
    data = result["data"]
    assert data["complete"] is False
    assert counts_of(data)["iss-00003"] == {
        "scope_id": "iss-00003",
        "direct_selected_count": 2,
        "descendant_selected_count": 0,
        "complete": False,
    }
    assert len(data["worktrees"]) == 2
    assert all(row["selection"]["status"] == "stale" for row in data["worktrees"])
    codes = [item["code"] for item in data["findings"]]
    assert codes.count("WORKTREE_SELECTION_STALE") == 2
    assert codes.count("SELECTION_DUPLICATE") == 1
    assert all(path.read_bytes() == value for path, value in before.items())
    assert not (world.main / ".git/spec-dock").exists()


def test_unavailable_duplicate_keeps_its_decoded_record_and_both_findings(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.application import canonical_workspace

    linked = world.worktree("linked")
    world.select("iss-00003", 3)
    world.select("iss-00003", 3, checkout=linked)
    records = [record_of(world.main), record_of(linked)]
    before = {record: record.read_bytes() for record in records}
    original = canonical_workspace.read_selection

    # No canonical input makes a decoded record unreadable afterwards (the legacy trigger was a broken .meta.json
    # in that worktree), so the observation of the linked worktree fails after its record was read.
    def unreadable_after_the_record(context: Any, views: Any, **kwargs: Any) -> Any:
        if context.root == linked:
            raise OSError("fixture: the linked worktree cannot be observed")
        return original(context, views, **kwargs)

    monkeypatch.setattr(canonical_workspace, "read_selection", unreadable_after_the_record)
    code, result = world.run("workspace", "sync")
    assert code == 7
    assert result["status"] == "partial" and result["effects"] == []
    data = result["data"]
    assert data["complete"] is False
    assert counts_of(data)["iss-00003"] == {
        "scope_id": "iss-00003",
        "direct_selected_count": 2,
        "descendant_selected_count": 0,
        "complete": False,
    }
    rows = {row["path"]: row for row in data["worktrees"]}
    assert rows[str(world.main)]["selection"]["status"] == "selected"
    assert rows[str(linked)]["selection"]["status"] == "unavailable"
    assert rows[str(linked)]["selection"]["scope_id"] == "iss-00003"
    assert {item["code"] for item in rows[str(linked)]["findings"]} == {
        "WORKTREE_SELECTION_UNAVAILABLE",
        "SELECTION_DUPLICATE",
    }
    assert all(path.read_bytes() == value for path, value in before.items())
    assert not (world.main / ".git/spec-dock").exists()


def test_unreadable_worktree_record_keeps_known_counts_incomplete_and_preserves_bytes(world: CanonicalWorld) -> None:
    linked = world.worktree("linked")
    world.select("iss-00003", 3)
    world.select("iss-00003", 3, checkout=linked)
    record, broken = record_of(world.main), record_of(linked)
    broken.write_bytes(b"not valid JSON")
    before = {record: record.read_bytes(), broken: broken.read_bytes()}
    code, result = world.run("workspace", "sync")
    assert code == 7
    assert result["status"] == "partial" and result["effects"] == []
    data = result["data"]
    assert data["complete"] is False
    assert counts_of(data)["iss-00003"] == {
        "scope_id": "iss-00003",
        "direct_selected_count": 1,
        "descendant_selected_count": 0,
        "complete": False,
    }
    rows = {row["path"]: row for row in data["worktrees"]}
    assert rows[str(world.main)]["selection"]["status"] == "selected"
    assert rows[str(linked)]["selection"]["status"] == "invalid"
    assert rows[str(linked)]["findings"]
    assert any(item["details"].get("path") == str(linked) for item in data["findings"])
    assert all(path.read_bytes() == value for path, value in before.items())
    assert not (world.main / ".git/spec-dock").exists()
    assert set(record.parent.iterdir()) == {record}


def test_stale_selection_keeps_its_known_scope_and_direct_count_without_metadata(world: CanonicalWorld) -> None:
    # The `--source local` case was removed with that source in 0.5.0; the GitHub structure is the only source.
    linked = world.worktree("linked")
    world.select("iss-00003", 3, checkout=linked)
    record = record_of(linked)
    before = record.read_bytes()
    world.edit(detach_and_complete_issue_3)
    graphql = len(world.fake().graphql_requests())
    code, result = world.run("workspace", "sync", "--source", "github")
    assert code == 7
    assert result["effects"] == []
    data = result["data"]
    assert data["complete"] is False
    assert {row["scope_id"]: row["lifecycle"] for row in data["scopes"]}["iss-00003"] == "completed"
    assert counts_of(data)["iss-00003"] == {
        "scope_id": "iss-00003",
        "direct_selected_count": 1,
        "descendant_selected_count": 0,
        "complete": False,
    }
    row = next(row for row in data["worktrees"] if row["path"] == str(linked))
    assert row["selection"]["status"] == "stale"
    assert row["selection"]["scope_id"] == "iss-00003"
    assert row["lifecycle"] == "completed"
    assert record.read_bytes() == before
    assert len(world.fake().graphql_requests()) > graphql and world.fake().writes() == []


def test_multiple_worktrees_share_parent_counts_and_live_refs_once_with_schema_valid_output(
    world: CanonicalWorld,
) -> None:
    world.scope("issue", 4, "Second", parent=2)
    world.scope("issue", 6, "Third", parent=2)
    world.edit(complete_issue_3)
    world.select("epic-00002", 2)
    for number in (3, 4):
        world.select(f"iss-{number:05d}", number, checkout=world.worktree(f"linked-{number}"))
    records = [record_of(world.main), record_of(world.tmp_path / "linked-3"), record_of(world.tmp_path / "linked-4")]
    before = {record: record.read_bytes() for record in records}
    code, result = world.run("workspace", "sync", "--source", "github")
    assert code == 0, result
    data = result["data"]
    assert len(data["worktrees"]) == 3
    assert all(row["process_state"] == "not_observed" for row in data["worktrees"])
    counts = counts_of(data)
    assert counts["epic-00002"] == {
        "scope_id": "epic-00002",
        "direct_selected_count": 1,
        "descendant_selected_count": 2,
        "complete": True,
    }
    assert counts["init-00001"]["descendant_selected_count"] == 3
    assert counts["iss-00003"]["direct_selected_count"] == 1
    assert counts["iss-00006"]["direct_selected_count"] == 0
    states = {row["scope_id"]: row["lifecycle"] for row in data["scopes"]}
    assert states["iss-00003"] == "completed" and states["iss-00006"] == "open"
    # Each Scope is listed once; the legacy per-Issue GETs and the iss-00413 cli-schema.json (source local|github,
    # no title or snapshot) do not describe the canonical output, which reads the structure in one refetch.
    assert sorted(states) == ["epic-00002", "init-00001", "iss-00003", "iss-00004", "iss-00006"]
    assert world.fake().writes() == []
    assert all(path.read_bytes() == value for path, value in before.items())


def test_sync_preserves_native_git_error_when_one_worktree_cannot_be_read(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    world.select("iss-00003", 3)
    linked = world.worktree("linked")
    real_git = shutil.which("git")
    assert real_git is not None
    bin_dir = world.tmp_path / "git-bin"
    bin_dir.mkdir()
    executable = bin_dir / "git"
    original_error = "fatal: fixture read refused\nsecond original line\n"
    executable.write_text(
        f"#!{sys.executable}\nimport os,sys\n"
        f"if sys.argv[1:4]==['-C',{str(linked)!r},'rev-parse']:\n"
        f" sys.stderr.write({original_error!r}); sys.exit(73)\n"
        f"os.execv({real_git!r},['git',*sys.argv[1:]])\n"
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])

    assert main(["--project", str(world.main), "workspace", "sync", "--json"]) == 7
    output = world.capsys.readouterr()
    assert output.err == ""
    result = json.loads(output.out)
    assert result["status"] == "partial" and result["effects"] == []
    # Canonical sync keeps the native Git details in the failing row's finding; the envelope error
    # (SYNC_INCOMPLETE) carries none, where the legacy sync put them in error.details.git.
    rows = {row["path"]: row for row in result["data"]["worktrees"]}
    (finding,) = rows[str(linked)]["findings"]
    assert finding["code"] == "WORKTREE_SELECTION_UNAVAILABLE"
    assert finding["details"]["git"]["stderr"] == original_error
    assert finding["details"]["git"]["returncode"] == 73
    assert main(["--project", str(world.main), "workspace", "sync"]) == 7
    assert "fatal: fixture read refused" in world.capsys.readouterr().out


@pytest.mark.parametrize("source", [["--source", "cache"], ["--source=cache"]])
def test_sync_rejects_retired_cache_source_before_resolving_the_project(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], source: list[str]
) -> None:
    assert main(["--project", str(tmp_path / "missing"), "workspace", "sync", *source, "--json"]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED"
    assert "github" in result["error"]["message"]
    assert result["effects"] == []
    assert list(tmp_path.iterdir()) == []


def test_sync_help_describes_readonly_observations_without_generations(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["help", "workspace", "sync"]) == 0
    text = capsys.readouterr().out
    assert "github" in text
    assert "worktrees" in text and "scopes" in text and "counts" in text
    assert "complete" in text and "not_observed" in text
    assert "specdock.cli/v2" in text
    assert "generation" not in text.lower()
    assert "None; this command only reads" in text
