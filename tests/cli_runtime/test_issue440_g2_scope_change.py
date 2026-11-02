"""Canonical `scope edit`, `scope close`, `scope reopen` and Scope read contracts kept from legacy tests (iss-00440).

Replaces the common-contract tests of tests/cli_runtime/test_issue413_scope_edit.py,
tests/cli_runtime/test_issue413_scope_lifecycle.py, tests/cli_runtime/test_scope_lifecycle_commands_vnext.py and
tests/cli_runtime/test_vnext_runtime_scope.py, which used a schema-3 `.meta.json` fixture.
"""

from __future__ import annotations

import io
import os
import sys
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.canonical_scopes import CanonicalWorld
from tests.support.canonical_writes import WriteWorld

if TYPE_CHECKING:
    from pathlib import Path

    from tests.support.fake_github import FakeGithub


class TerminalAnswer(io.StringIO):
    def isatty(self) -> bool:
        return True


def _world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> WriteWorld:
    world = WriteWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "plan")
    world.scope("epic", 2, "core", parent=1)
    world.scope("issue", 3, "leaf", parent=2)
    return world


def _selected(world: WriteWorld, scope_id: str = "iss-00003", number: int = 3) -> Path:
    world.select(scope_id, number)
    return next((world.main / "spec-dock/.agent/work-target").iterdir())


def _documents(world: WriteWorld) -> dict[str, bytes]:
    return {
        path.relative_to(world.catalog).as_posix(): path.read_bytes()
        for path in world.catalog.rglob("*")
        if path.is_file()
    }


def _git_state(world: WriteWorld) -> tuple[str, str]:
    from tests.support.canonical_repo import git

    return git(world.main, "rev-parse", "HEAD"), git(world.main, "branch", "--show-current")


# scope edit


def test_scope_edit_dry_run_returns_a_valid_title_plan_without_writing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = _documents(world)
    code, payload = world.run("scope", "edit", "epic-00002", "--title", "変更予定", "--dry-run")
    assert (code, payload["status"]) == (0, "planned"), payload
    data = payload["data"]["result"]
    assert data["can_apply"] is True and data["blockers"] == [] and data["changed"] is False
    assert payload["effects"] == [{"kind": "github.issue.title", "status": "planned", "target": "epic-00002"}]
    # The same title under --dry-run plans nothing.
    code, payload = world.run("scope", "edit", "epic-00002", "--title", "core", "--dry-run")
    assert (code, payload["status"], payload["effects"]) == (0, "planned", [])
    assert world.writes() == [] and world.changesets() == [] and _documents(world) == before
    assert world.fake().issue(2).title == "core"


@pytest.mark.parametrize("guard", [("--expect-current", "init-00001"), ("--expect-backend", "local")])
def test_scope_edit_guard_mismatch_preserves_title_documents_and_direct_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], guard: tuple[str, str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    record = _selected(world)
    selected, before = record.read_bytes(), _documents(world)
    code, payload = world.run("scope", "edit", "@epic", "--title", "拒否する変更", *guard)
    assert (code, payload["error"]["code"], payload["effects"]) == (3, "PRECONDITION_FAILED", []), payload
    assert world.writes() == [] and _documents(world) == before and record.read_bytes() == selected
    assert world.fake().issue(2).title == "core"


def test_scope_mutation_checks_expected_current_and_backend_before_edit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    record = _selected(world)
    selected = record.read_bytes()
    for guard in (("--expect-current", "init-00001"), ("--expect-backend", "local")):
        code, payload = world.run("scope", "edit", "@current", "--title", "New", *guard)
        assert (code, payload["error"]["code"], payload["effects"]) == (3, "PRECONDITION_FAILED", []), payload
        assert world.writes() == [] and record.read_bytes() == selected
    code, payload = world.run(
        "scope", "edit", "@current", "--title", "New", "--expect-current", "iss-00003", "--expect-backend", "github"
    )
    assert code == 0, payload
    assert payload["data"]["result"]["scope"]["id"] == "iss-00003"
    assert world.writes() == [("PATCH", "repos/example/repo/issues/3", {"title": "New"})]
    assert record.read_bytes() == selected


def test_scope_edit_proceeds_while_start_exclusion_is_held(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.runtime.infra.start_lock import StartLock

    world = _world(tmp_path, monkeypatch, capsys)
    with StartLock(world.main / ".git", timeout=0):
        code, payload = world.run("scope", "edit", "epic-00002", "--title", "ロック外の編集")
    assert code == 0, payload
    assert payload["data"]["result"]["changed"] is True
    assert world.fake().issue(2).title == "ロック外の編集"


def test_scope_list_show_and_edit_target_the_same_scope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    record = _selected(world)
    selected, before = record.read_bytes(), _documents(world)
    code, payload = world.run("scope", "list", "--kind", "issue", "--parent", "epic-00002")
    assert code == 0 and [item["id"] for item in payload["data"]["result"]["items"]] == ["iss-00003"]
    code, payload = world.run("scope", "show", "@current")
    assert code == 0 and payload["data"]["result"]["scope"]["id"] == "iss-00003"
    edit = ("scope", "edit", "@current", "--title", "Renamed", "--expect-current", "iss-00003")
    code, payload = world.run(*edit, "--dry-run")
    assert (code, payload["status"]) == (0, "planned") and world.writes() == []
    code, payload = world.run(*edit)
    assert code == 0 and payload["data"]["result"]["changed"] is True, payload
    assert world.writes() == [("PATCH", "repos/example/repo/issues/3", {"title": "Renamed"})]
    code, payload = world.run("scope", "show", "iss-00003")
    assert code == 0 and payload["data"]["result"]["scope"]["title"] == "Renamed"
    assert _documents(world) == before and record.read_bytes() == selected


# scope close / reopen


@pytest.mark.parametrize("action,state", [("close", "open"), ("reopen", "completed")])
def test_lifecycle_dry_run_exposes_a_valid_plan_without_mutating_authority_or_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], action: str, state: str
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    if state == "completed":

        def close(fake: FakeGithub) -> None:
            fake.issue(3).state, fake.issue(3).state_reason = "closed", "completed"

        world.edit(close)
    record = _selected(world)
    selected, before = record.read_bytes(), _documents(world)
    code, payload = world.run("scope", action, "@current", "--dry-run")
    assert (code, payload["status"]) == (0, "planned"), payload
    result = payload["data"]["result"]
    assert result["can_apply"] is True and result["blockers"] == [] and result["changed"] is False
    assert result["scope"]["status"]["state"] == state
    assert payload["effects"] == [
        {"kind": f"github.issue.{action}", "status": "planned", "target": "gh:example/repo#3"}
    ]
    assert world.writes() == [] and world.changesets() == []
    assert record.read_bytes() == selected and _documents(world) == before


def test_scope_close_confirms_completed_without_releasing_the_direct_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    record = _selected(world)
    selected, git_state = record.read_bytes(), _git_state(world)
    code, payload = world.run("scope", "close", "@current", "--expect-current", "iss-00003", "--yes")
    assert code == 0, payload
    scope = payload["data"]["result"]["scope"]
    assert scope["id"] == "iss-00003" and scope["status"]["state"] == "completed"
    assert payload["data"]["result"]["changed"] is True
    assert payload["effects"] == [{"kind": "github.issue.close", "status": "succeeded", "target": "gh:example/repo#3"}]
    assert world.writes() == [
        ("PATCH", "repos/example/repo/issues/3", {"state": "closed", "state_reason": "completed"})
    ]
    assert record.read_bytes() == selected and _git_state(world) == git_state


@pytest.mark.parametrize("answer", ["yes\n", "no\n"])
def test_scope_close_accepts_a_terminal_confirmation_after_planning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], answer: str
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    record = _selected(world)
    selected = record.read_bytes()
    monkeypatch.setattr(sys, "stdin", TerminalAnswer(answer))
    code = main(["--project", str(world.main), "scope", "close", "@current"])
    output = capsys.readouterr()
    assert "Target: iss-00003" in output.err and "Confirm [yes/no]" in output.err
    if answer == "yes\n":
        assert code == 0, output
        assert world.writes() == [
            ("PATCH", "repos/example/repo/issues/3", {"state": "closed", "state_reason": "completed"})
        ]
    else:
        assert code == 3, output
        assert "CONFIRMATION_DECLINED" in output.err and world.writes() == []
    assert record.read_bytes() == selected


def test_unconfirmed_close_reports_unknown_and_never_repeats_a_patch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    record = _selected(world)
    selected = record.read_bytes()
    world.edit(lambda fake: fake.inject(status=503, body={"message": "x"}, method="PATCH", endpoint="issues/3"))
    code, payload = world.run("scope", "close", "@current", "--yes")
    assert (code, payload["status"], payload["error"]["code"]) == (6, "partial", "GITHUB_EFFECT_UNKNOWN"), payload
    assert payload["effects"] == [{"kind": "github.issue.close", "status": "unknown", "target": "gh:example/repo#3"}]
    assert payload["recovery"]["can_resume"] is False and payload["recovery"]["can_rollback"] is False
    assert [item.method for item in world.fake().requests if item.method == "PATCH"] == ["PATCH"]
    assert record.read_bytes() == selected


def test_completed_close_requires_reopen_after_not_planned_and_preserves_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)

    def not_planned(fake: FakeGithub) -> None:
        fake.issue(3).state, fake.issue(3).state_reason = "closed", "not_planned"

    world.edit(not_planned)
    record = _selected(world)
    selected, before = record.read_bytes(), _documents(world)
    code, payload = world.run("scope", "close", "@current", "--yes")
    assert (code, payload["effects"]) == (3, []), payload
    assert "TERMINAL_REASON_CONFLICT" in payload["error"]["message"]
    assert world.writes() == [] and record.read_bytes() == selected and _documents(world) == before
    assert world.fake().issue(3).state_reason == "not_planned"


# Project context and selectors (mode-independent; formerly on a schema-3 fixture)


@pytest.mark.parametrize("command", [["scope", "list"], ["scope", "edit", "init-00001", "--title", "New"]])
def test_native_context_failure_keeps_git_diagnostic_and_no_effects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], command: list[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = tree_digest(world.main)
    bin_dir = tmp_path / "blocked-git"
    bin_dir.mkdir()
    original = "fatal: fixture Git context refused\nsecond original line\n"
    executable = bin_dir / "git"
    executable.write_text(f"#!{sys.executable}\nimport sys\nsys.stderr.write({original!r})\nsys.exit(73)\n")
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])
    assert main(["--project", str(world.main), *command, "--json"]) == 5
    output = capsys.readouterr()
    result = _json(output.out)
    assert not output.err and result["error"]["code"] == "GIT_FAILED" and result["effects"] == []
    assert result["error"]["details"]["git"]["stderr"] == original
    assert result["error"]["details"]["git"]["returncode"] == 73
    assert tree_digest(world.main) == before and world.writes() == []


def _json(text: str) -> dict[str, Any]:
    import json

    return json.loads(text)


def test_runtime_rejects_a_nonroot_project_before_scope_edit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = tree_digest(world.main)
    code, payload = world.run("scope", "edit", "init-00001", "--title", "Wrong root", checkout=world.main / "spec-dock")
    assert (code, payload["error"]["code"], payload["effects"]) == (3, "PRECONDITION_FAILED", []), payload
    assert tree_digest(world.main) == before and world.writes() == []


@pytest.mark.parametrize("mode", ["implicit-child", "explicit-child", "non-git"])
def test_scope_read_resolves_native_project_context_without_changing_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "plan")
    child = world.main / "nested/child"
    child.mkdir(parents=True)
    outside = tmp_path / "non-git"
    outside.mkdir()
    before, outside_before = tree_digest(world.main), tree_digest(outside)
    monkeypatch.chdir(outside if mode == "non-git" else child)
    project = ["--project", str(child)] if mode == "explicit-child" else []
    expected = {"implicit-child": 0, "explicit-child": 3, "non-git": 5}[mode]
    assert main([*project, "scope", "show", "init-00001", "--json"]) == expected
    result = _json(capsys.readouterr().out)
    assert result["effects"] == []
    if mode == "implicit-child":
        assert result["data"]["result"]["scope"]["id"] == "init-00001"
    else:
        assert result["error"]["code"] == ("GIT_FAILED" if mode == "non-git" else "PRECONDITION_FAILED")
        if mode == "non-git":
            assert "not a git repository" in result["error"]["details"]["git"]["stderr"]
    assert tree_digest(world.main) == before and tree_digest(outside) == outside_before


@pytest.mark.parametrize(
    "target,code,scope_id",
    [
        ("gh:EXAMPLE/REPO#1", 0, "init-00001"),
        ("gh:other/repo#1", 4, None),
        ("gh:example/repo#99", 4, None),
        ("iss-99999", 4, None),
    ],
)
def test_scope_query_uses_only_exact_imported_github_linkage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    target: str,
    code: int,
    scope_id: str | None,
) -> None:
    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "plan")
    world.edit(lambda fake: fake.add_issue(99, title="Plain"))
    before = tree_digest(world.main)
    result_code, payload = world.run("scope", "show", target)
    assert (result_code, payload["effects"]) == (code, []), payload
    if scope_id is not None:
        assert payload["data"]["result"]["scope"]["id"] == scope_id
    else:
        assert payload["error"]["code"] == "SCOPE_NOT_FOUND"
    assert tree_digest(world.main) == before
    assert [item for item in world.fake().requests if item.method != "GET" and item.endpoint != "graphql"] == []


# Parts of legacy lifecycle tests that the iss-00432 counterparts did not assert


def _set_state(world: WriteWorld, number: int, state: str, reason: str | None) -> None:
    def change(fake: FakeGithub) -> None:
        fake.issue(number).state, fake.issue(number).state_reason = state, reason

    world.edit(change)


@pytest.mark.parametrize("child", [("open", None), ("closed", "not_planned")])
@pytest.mark.parametrize("parent_completed", [False, True])
def test_completed_parent_close_still_checks_unfinished_descendants(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    child: tuple[str, str | None],
    parent_completed: bool,
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    _set_state(world, 3, *child)
    if parent_completed:
        _set_state(world, 2, "closed", "completed")
    code, payload = world.write("scope", "close", "epic-00002")
    assert (code, payload["error"]["message"], payload["effects"]) == (3, "DESCENDANT_NOT_COMPLETED", []), payload
    assert world.writes() == []


@pytest.mark.parametrize("ancestor", [("completed", 2), ("not_planned", 2), ("not_planned", 1)])
def test_reopen_even_an_open_child_requires_open_ancestors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], ancestor: tuple[str, int]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    reason, number = ancestor
    _set_state(world, number, "closed", reason)
    for target in ("iss-00003", "epic-00002") if number == 1 else ("iss-00003",):
        code, payload = world.write("scope", "reopen", target)
        assert (code, payload["error"]["message"], payload["effects"]) == (3, "ANCESTOR_TERMINAL", []), payload
    assert world.writes() == []


def test_not_planned_close_lists_children_and_never_closes_them(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    code, payload = world.write("scope", "close", "epic-00002", "--reason", "not-planned")
    assert code == 0, payload
    assert payload["data"]["result"]["descendants"] == ["iss-00003"]
    assert world.writes() == [
        ("PATCH", "repos/example/repo/issues/2", {"state": "closed", "state_reason": "not_planned"})
    ]
    assert world.fake().issue(3).state == "open"
