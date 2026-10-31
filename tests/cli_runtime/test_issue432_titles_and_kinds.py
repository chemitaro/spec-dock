"""AC-432-18 and AC-432-19 on the remaining commands: title rule, kind change and old IDs stop before writing."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.support.canonical_writes import WriteWorld

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> WriteWorld:
    world = WriteWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "plan")
    world.scope("epic", 2, "core", parent=1)
    world.scope("issue", 3, "leaf", parent=2)
    world.scope("issue", 4, "closed leaf", parent=2, state="closed", state_reason="completed")
    return world


@pytest.mark.parametrize("title", ["   ", "two\nlines", "x" * 257])
def test_edit_refuses_a_title_outside_the_rule(world: WriteWorld, title: str) -> None:
    code, payload = world.run("scope", "edit", "iss-00003", "--title", title)
    assert (code, payload["error"]["code"]) == (3, "PRECONDITION_FAILED")
    assert world.writes() == []


def test_edit_accepts_256_characters_in_any_language(world: WriteWorld) -> None:
    title = "題" * 256
    code, payload = world.run("scope", "edit", "iss-00003", "--title", title)
    assert code == 0, payload
    assert world.fake().issue(3).title == title


def test_an_import_of_an_issue_whose_github_title_breaks_the_rule_writes_nothing(world: WriteWorld) -> None:
    world.edit(lambda fake: fake.add_issue(9, title="line\nbreak"))
    code, payload = world.run(
        "scope",
        "import",
        "github",
        "issue",
        "9",
        "--parent",
        "epic-00002",
        "--title",
        "anything",
        "--assurance",
        "standard",
        "--assurance-reason",
        "既定の理由",
    )
    assert (code, payload["error"]["code"]) == (3, "PRECONDITION_FAILED")
    assert "fix the title on GitHub" in payload["error"]["message"] and world.writes() == []


@pytest.mark.parametrize(
    "argv",
    [
        ("scope", "edit", "iss-00003", "--title", "New"),
        ("scope", "close", "iss-00003", "--yes"),
        ("scope", "reopen", "iss-00004", "--yes"),
        (
            "scope",
            "create",
            "issue",
            "--backend",
            "github",
            "--parent",
            "epic-00002",
            "--title",
            "X",
            "--yes",
            "--assurance",
            "standard",
            "--assurance-reason",
            "既定の理由",
        ),
        ("dependency", "add", "--from", "iss-00004", "--to", "iss-00003"),
    ],
)
def test_a_kind_change_stops_each_writing_command_before_any_write(world: WriteWorld, argv: tuple[str, ...]) -> None:
    world.edit(lambda fake: setattr(fake.issue(3), "labels", ["spec-dock:epic"]))
    world.edit(lambda fake: setattr(fake.issue(4), "labels", ["spec-dock:epic"]) if "reopen" in argv else None)
    if "create" in argv:
        world.edit(lambda fake: setattr(fake.issue(2), "labels", ["spec-dock:initiative"]))
        world.directory("epic", 2)
    code, payload = world.run(*argv)
    assert (code, payload["error"]["code"]) == (3, "SCOPE_KIND_CHANGED"), payload
    assert payload["recovery"]["instructions"]
    assert world.writes() == [] and world.changesets() == []


def test_the_current_id_of_a_kind_changed_scope_also_stops(world: WriteWorld) -> None:
    world.edit(lambda fake: setattr(fake.issue(3), "labels", ["spec-dock:epic"]))
    code, payload = world.run("scope", "close", "epic-3", "--yes")
    assert (code, payload["error"]["code"]) == (3, "SCOPE_KIND_CHANGED")
    assert payload["error"]["details"]["current_id"] == "epic-00003"
    assert world.writes() == []


def test_a_japanese_only_title_shows_in_scope_show_and_workspace_sync(world: WriteWorld) -> None:
    code, payload = world.write(
        "scope",
        "create",
        "issue",
        "--backend",
        "github",
        "--parent",
        "epic-00002",
        "--title",
        "日本語だけの題名",
        "--assurance",
        "standard",
        "--assurance-reason",
        "既定の理由",
    )
    assert code == 0, payload
    assert world.run("scope", "show", "iss-00005")[1]["data"]["result"]["scope"]["title"] == "日本語だけの題名"
    code, synced = world.run("workspace", "sync")
    assert code == 0, synced
    titles = {item["scope_id"]: item["title"] for item in synced["data"]["scopes"]}
    assert titles["iss-00005"] == "日本語だけの題名" and titles["epic-00002"] == "core"
    from spec_dock.cli import main

    assert main(["--project", str(world.main), "workspace", "sync"]) == 0
    assert 'scope_id=iss-00005 title="日本語だけの題名"' in world.capsys.readouterr().out
