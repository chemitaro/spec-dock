"""Canonical `scope close`, `scope reopen` and `scope create` reread what the confirmation saw (iss-00506).

Restores the legacy guards whose tests were removed with legacy mode (iss-00440 follow-ups 1-3):
`test_issue413_scope_lifecycle.py::test_scope_lifecycle_refuses_a_changed_direct_selection_after_terminal_confirmation`,
`test_scope_create_commands_vnext.py::test_github_create_confirmation_rejects_native_origin_change_before_post` and
`test_issue413_scope_publish.py::test_repository_change_during_create_keeps_the_confirmed_old_ref_without_local_publication`.
"""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.github_structure import GithubStructureClient
from tests.support.canonical_repo import git
from tests.support.canonical_writes import WriteWorld

if TYPE_CHECKING:
    from pathlib import Path

    from tests.support.fake_github import FakeGithub

ASSURANCE = ("--assurance", "standard", "--assurance-reason", "fixture reason")
OTHER_ORIGIN = "https://github.com/example/other.git"


class AnswerAfter:
    """A terminal that runs `change` while the user types the answer, then answers `answer`."""

    def __init__(self, change: Any, answer: str = "yes\n") -> None:
        self.change = change
        self.answer = answer

    def isatty(self) -> bool:
        return True

    def readline(self) -> str:
        self.change()
        return self.answer


def _world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> WriteWorld:
    world = WriteWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "plan")
    world.scope("epic", 2, "core", parent=1)
    world.scope("issue", 3, "leaf", parent=2)
    return world


def _records(world: WriteWorld) -> dict[str, bytes]:
    directory = world.main / "spec-dock/.agent/work-target"
    return {path.name: path.read_bytes() for path in sorted(directory.iterdir())}


def _catalog(world: WriteWorld) -> dict[str, bytes]:
    return {
        path.relative_to(world.catalog).as_posix(): path.read_bytes()
        for path in sorted(world.catalog.rglob("*"))
        if path.is_file()
    }


# scope close / reopen


@pytest.mark.parametrize("action,state", [("close", "open"), ("reopen", "completed")])
@pytest.mark.parametrize("guard", [(), ("--expect-current", "iss-00003")])
def test_lifecycle_refuses_a_selection_changed_during_terminal_confirmation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    action: str,
    state: str,
    guard: tuple[str, ...],
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    if state == "completed":

        def close(fake: FakeGithub) -> None:
            fake.issue(3).state, fake.issue(3).state_reason = "closed", "completed"

        world.edit(close)
    world.select("iss-00003", 3)
    directory = world.main / "spec-dock/.agent/work-target"
    after: dict[str, bytes] = {}

    def switch_selection() -> None:  # another `work start` replaces the direct record
        for path in directory.iterdir():
            path.unlink()
        world.select("epic-00002", 2)
        after.update(_records(world))

    before = _catalog(world)
    monkeypatch.setattr(sys, "stdin", AnswerAfter(switch_selection))
    code = main(["--project", str(world.main), "scope", action, "@current", *guard])
    output = capsys.readouterr()
    assert "Confirm [yes/no]" in output.err and "iss-00003" in output.err, output
    assert code == 3, output
    assert "PRECONDITION_FAILED" in output.err and "selection changed" in output.err, output
    assert world.writes() == [] and world.changesets() == []
    assert after and _records(world) == after
    assert _catalog(world) == before
    assert world.fake().issue(3).state == ("open" if state == "open" else "closed")


def test_lifecycle_with_yes_keeps_closing_the_resolved_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.select("iss-00003", 3)
    code, payload = world.write("scope", "close", "@current")
    assert code == 0, payload
    assert world.writes() == [
        ("PATCH", "repos/example/repo/issues/3", {"state": "closed", "state_reason": "completed"})
    ]


# scope create


def _create(world: WriteWorld, *extra: str) -> int:
    return main([
        "--project",
        str(world.main),
        "scope",
        "create",
        "initiative",
        "--backend",
        "github",
        "--title",
        "New Work",
        *ASSURANCE,
        *extra,
    ])


def test_create_refuses_an_origin_changed_during_terminal_confirmation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = _catalog(world)
    monkeypatch.setattr(sys, "stdin", AnswerAfter(lambda: git(world.main, "remote", "set-url", "origin", OTHER_ORIGIN)))
    code = _create(world)
    output = capsys.readouterr()
    assert "Confirm [yes/no]" in output.err and "example/repo" in output.err, output
    assert code == 3, output
    assert "PRECONDITION_FAILED" in output.err and "GitHub repository changed" in output.err, output
    assert world.writes() == [] and world.changesets() == []
    assert _catalog(world) == before


def test_create_refuses_an_origin_changed_after_the_label_before_post(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = WriteWorld.create(tmp_path, monkeypatch, capsys)  # no Scope yet: the kind label does not exist
    assert world.fake().labels == {}
    before = _catalog(world)
    original = GithubStructureClient.create_label

    def create_label_then_move_origin(self: GithubStructureClient, *args: Any, **kwargs: Any) -> Any:
        value = original(self, *args, **kwargs)
        git(world.main, "remote", "set-url", "origin", OTHER_ORIGIN)
        return value

    monkeypatch.setattr(GithubStructureClient, "create_label", create_label_then_move_origin)
    code = _create(world, "--yes", "--json")
    payload = json.loads(capsys.readouterr().out)
    assert (code, payload["status"], payload["error"]["code"]) == (6, "partial", "CANONICAL_WRITE_INCOMPLETE")
    assert payload["effects"][0] == {
        "kind": "github.label.create",
        "status": "succeeded",
        "target": "spec-dock:initiative",
    }
    assert {item["kind"]: item["status"] for item in payload["effects"][1:]} == {
        "github-create": "not_attempted",
        "scaffold": "not_attempted",
    }
    assert [item for item in world.fake().writes() if item.endpoint.endswith("/issues")] == []
    assert _catalog(world) == before


@pytest.mark.parametrize("parent", [(), ("--parent", "init-00001")])
def test_repository_change_during_create_keeps_the_confirmed_ref_without_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], parent: tuple[str, ...]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = _catalog(world)
    original = GithubStructureClient.create_issue

    def create_then_move_origin(self: GithubStructureClient, *args: Any, **kwargs: Any) -> Any:
        value = original(self, *args, **kwargs)
        git(world.main, "remote", "set-url", "origin", OTHER_ORIGIN)
        return value

    monkeypatch.setattr(GithubStructureClient, "create_issue", create_then_move_origin)
    kind = "epic" if parent else "initiative"
    code = main([
        "--project",
        str(world.main),
        "scope",
        "create",
        kind,
        "--backend",
        "github",
        *parent,
        "--title",
        "New Work",
        *ASSURANCE,
        "--yes",
        "--json",
    ])
    payload = json.loads(capsys.readouterr().out)
    assert (code, payload["status"], payload["error"]["code"]) == (6, "partial", "SCOPE_PUBLICATION_INCOMPLETE"), (
        payload
    )
    number = max(number for _, number in world.fake().issues)
    assert payload["data"]["result"]["github_ref"] == f"gh:example/repo#{number}"
    effects = payload["effects"]
    assert effects[0] == {"kind": "github-create", "status": "succeeded", "target": "example/repo"}
    expected = {"scaffold": "not_attempted"}
    if parent:
        expected["github.sub-issue.add"] = "not_attempted"
    assert {item["kind"]: item["status"] for item in effects[1:]} == expected
    assert (
        "example/repo" in payload["recovery"]["instructions"][0] and "origin" in payload["recovery"]["instructions"][0]
    )
    assert [item.endpoint for item in world.fake().writes() if item.method == "POST"].count(
        "repos/example/repo/issues"
    ) == 1
    assert not any("sub_issues" in item.endpoint for item in world.fake().writes())
    assert world.changesets() == [] and _catalog(world) == before


def test_repository_change_while_adding_to_the_parent_stops_before_catalog_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = _catalog(world)
    original = GithubStructureClient.add_sub_issue

    def add_then_move_origin(self: GithubStructureClient, *args: Any, **kwargs: Any) -> Any:
        value = original(self, *args, **kwargs)
        git(world.main, "remote", "set-url", "origin", OTHER_ORIGIN)
        return value

    monkeypatch.setattr(GithubStructureClient, "add_sub_issue", add_then_move_origin)
    code = main([
        "--project",
        str(world.main),
        "scope",
        "create",
        "epic",
        "--backend",
        "github",
        "--parent",
        "init-00001",
        "--title",
        "New Work",
        *ASSURANCE,
        "--yes",
        "--json",
    ])
    payload = json.loads(capsys.readouterr().out)
    assert (code, payload["status"], payload["error"]["code"]) == (6, "partial", "SCOPE_PUBLICATION_INCOMPLETE"), (
        payload
    )
    assert {item["kind"]: item["status"] for item in payload["effects"]} == {
        "github-create": "succeeded",
        "github.sub-issue.add": "succeeded",
        "scaffold": "not_attempted",
    }
    assert world.changesets() == [] and _catalog(world) == before
