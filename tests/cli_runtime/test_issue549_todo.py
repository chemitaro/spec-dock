"""`spec-dock todo` in a checkout (iss-00549): records in the catalog's todos/, never GitHub.

The world is a linked canonical clone with the fake gh on PATH; HOME, XDG_CONFIG_HOME and XDG_STATE_HOME point
into the temporary directory, so the user's settings file is never read or written.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.runtime.application import todo_common
from tests.support.canonical_writes import WriteWorld

if TYPE_CHECKING:
    from collections.abc import Callable

START = datetime(2026, 11, 4, 1, 0, tzinfo=timezone.utc)
AGENT = (
    "--by",
    "agent",
    "--role",
    "iss-00549 の担当",
    "--body",
    "背景と問い",
    "--reply-to",
    "Orca の担当",
    "--effort",
    "10m",
)


class Clock:
    def __init__(self) -> None:
        self.now = START

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **delta: float) -> None:
        self.now += timedelta(**delta)


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> WriteWorld:
    built = WriteWorld.create(tmp_path, monkeypatch, capsys)
    built.scope("initiative", 1, "plan")
    built.scope("epic", 2, "core", parent=1)
    built.scope("issue", 531, "葉の作業", parent=2)
    code, payload = built.run("scope", "list")  # saves the structure snapshot
    assert code == 0, payload
    return built


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> Clock:
    fixed = Clock()
    monkeypatch.setattr(todo_common, "utc_now", fixed)
    return fixed


def todo(world: WriteWorld, *argv: str, checkout: Path | None = None) -> tuple[int, dict[str, Any]]:
    return world.run("todo", *argv, checkout=checkout)


def added(world: WriteWorld, *argv: str) -> dict[str, Any]:
    code, payload = todo(world, "add", *argv)
    assert code == 0, payload
    return payload["data"]["result"]


def text(world: WriteWorld, *argv: str) -> str:
    from spec_dock.cli import main

    world.capsys.readouterr()
    main(["--project", str(world.main), "todo", *argv])
    return world.capsys.readouterr().out


def codes(payload: dict[str, Any]) -> list[str]:
    return [item["code"] for item in payload["warnings"]]


def test_a_task_lives_in_the_catalog_and_is_seen_from_another_worktree(world: WriteWorld, clock: Clock) -> None:
    before = len(world.requests())
    result = added(world, "--title", "窓口に電話する")
    todo_id = result["todo"]["id"]
    assert result["path"] == f"todos/2026-11/{todo_id}.json"
    assert result["todo"]["kind"] == "todo" and result["todo"]["due"] == "2026-11-04T05:00:00Z"
    assert result["ref"] == f"example/repo/{todo_id}" and result["repository"] == "github.com/example/repo"
    record_path = world.catalog / result["path"]
    assert json.loads(record_path.read_text(encoding="utf-8"))["id"] == todo_id
    worktree = world.worktree("wt")
    code, listed = todo(world, "list", checkout=worktree)
    assert code == 0, listed
    document = listed["data"]["result"]
    assert document["schema"] == "specdock.todo-list/v1" and document["mode"] == "repository"
    assert [item["todo"]["id"] for item in document["items"]] == [todo_id]
    (row,) = document["repositories"]
    assert row["status"] == "ok" and row["counts"]["open"] == 1 and row["hidden"] is False
    code, done = todo(world, "done", todo_id, "--note", "済んだ", "--record", "log.md")
    assert code == 0, done
    assert record_path.is_file() and json.loads(record_path.read_text(encoding="utf-8"))["status"] == "done"
    assert [changeset["paths"] for changeset in world.changesets()] == [[result["path"]], [result["path"]]]
    for argv in (
        ("show", todo_id),
        ("check",),
        ("settings",),
        ("list", "--status", "all"),
        ("reopen", todo_id),
        ("update", todo_id, "--title", "窓口に電話する（再）"),
        ("snooze", todo_id, "--until", "1d"),
        ("cancel", todo_id, "--reason", "不要になった"),
    ):
        code, payload = todo(world, *argv)
        assert code == 0, (argv, payload)
    assert len(world.requests()) == before  # nothing reached GitHub


def test_an_agent_must_give_its_fields_and_nothing_is_written(world: WriteWorld, clock: Clock) -> None:
    code, payload = todo(world, "add", "--title", "選ぶ", "--by", "agent", "--kind", "decide")
    assert (code, payload["error"]["code"]) == (2, "TODO_INVALID")
    assert set(payload["error"]["details"]["missing"]) == {
        "role",
        "body",
        "reply_to",
        "effort",
        "options",
        "recommendation",
    }
    assert not (world.catalog / "todos").exists() and world.changesets() == []
    result = added(
        world,
        "--title",
        "選ぶ",
        "--kind",
        "decide",
        *AGENT,
        "--option",
        "a=A にする",
        "--option",
        "b=B にする",
        "--recommend",
        "a",
        "--reason",
        "速い",
        "--due",
        "2d",
    )
    assert result["todo"]["options"] == [{"key": "a", "text": "A にする"}, {"key": "b", "text": "B にする"}]
    assert result["todo"]["due"] == "2026-11-06T01:00:00Z"
    code, payload = todo(world, "done", result["todo"]["id"], "--choice", "z")
    assert (code, payload["error"]["code"]) == (2, "TODO_INVALID")
    code, payload = todo(world, "done", result["todo"]["id"], "--choice", "a", "--by", "human")
    assert code == 0 and payload["data"]["result"]["todo"]["resolution"]["choice"] == "a"
    code, payload = todo(world, "done", result["todo"]["id"])
    assert (code, payload["error"]["code"]) == (3, "TODO_STATE_INVALID")
    code, payload = todo(world, "reopen", result["todo"]["id"])
    assert code == 0 and payload["data"]["result"]["todo"]["resolution"] is None


def test_subtasks_and_a_checklist(world: WriteWorld, clock: Clock) -> None:
    parent = added(world, "--title", "親")["todo"]["id"]
    for title in ("一", "二"):
        result = added(world, "--parent", parent, "--title", title)
    assert [item["id"] for item in result["todo"]["subtasks"]] == [f"{parent}.1", f"{parent}.2"]
    code, payload = todo(world, "add", "--parent", f"{parent}.1", "--title", "孫")
    assert (code, payload["error"]["code"]) == (2, "TODO_NESTING_TOO_DEEP")
    code, payload = todo(world, "done", parent)
    assert (code, payload["error"]["code"]) == (3, "TODO_SUBTASKS_OPEN")
    code, payload = todo(world, "done", f"{parent}.1")
    assert code == 0 and payload["data"]["result"]["derived"]["parent_closable"] is False
    code, payload = todo(world, "done", f"{parent}.2")
    assert code == 0 and payload["data"]["result"]["derived"]["parent_closable"] is True
    code, payload = todo(world, "show", parent)
    assert payload["data"]["result"]["derived"]["parent_closable"] is True
    assert payload["data"]["result"]["next_step"] == f"spec-dock todo done {parent}"
    code, payload = todo(world, "show", f"{parent}.9")
    assert (code, payload["error"]["code"]) == (3, "TODO_NOT_FOUND")
    bundle = added(world, "--title", "まとめて", "--kind", "checklist", *AGENT, "--item", "A", "--item", "B")
    assert [item["title"] for item in bundle["todo"]["subtasks"]] == ["A", "B"]
    assert bundle["todo"]["due"] == "2026-11-04T05:00:00Z"
    bundle_id = bundle["todo"]["id"]
    todo(world, "done", f"{bundle_id}.1")
    code, payload = todo(world, "show", bundle_id)
    assert payload["data"]["result"]["derived"]["open_subtasks"] == [{"id": f"{bundle_id}.2", "title": "B"}]
    assert "残り 1 件" in text(world, "show", bundle_id)
    code, payload = todo(world, "cancel", bundle_id, "--reason", "不要", "--include-subtasks")
    assert code == 0 and payload["data"]["result"]["todo"]["status"] == "cancelled"
    code, payload = todo(world, "add", "--parent", bundle_id, "--title", "X")
    assert (code, payload["error"]["code"]) == (3, "TODO_PARENT_CLOSED")


def test_due_overdue_snooze_and_order(world: WriteWorld, clock: Clock) -> None:
    late = added(world, "--title", "遅れ", "--due", "1h")["todo"]["id"]
    later = added(world, "--title", "あとで", "--due", "3d")["todo"]["id"]
    sleepy = added(world, "--title", "寝かせる", "--due", "5d")["todo"]["id"]
    code, payload = todo(world, "add", "--title", "過去", "--due", "2026-11-01")
    assert (code, payload["error"]["code"]) == (2, "TODO_INVALID")
    code, payload = todo(world, "snooze", sleepy, "--until", "1d")
    assert code == 0 and payload["data"]["result"]["todo"]["status"] == "snoozed"
    clock.advance(hours=2)
    code, payload = todo(world, "list")
    items = payload["data"]["result"]["items"]
    assert [item["todo"]["id"] for item in items] == [late, later]
    assert items[0]["derived"]["overdue"] is True
    assert payload["data"]["result"]["repositories"][0]["counts"]["overdue"] == 1
    code, payload = todo(world, "list", "--overdue")
    assert [item["todo"]["id"] for item in payload["data"]["result"]["items"]] == [late]
    clock.advance(days=1)
    code, payload = todo(world, "list")
    ids = [item["todo"]["id"] for item in payload["data"]["result"]["items"]]
    assert sleepy in ids


def test_limits_warn_and_settings_layers(world: WriteWorld, clock: Clock, tmp_path: Path) -> None:
    config = tmp_path / "home/.config/spec-dock/config.json"
    config.parent.mkdir(parents=True)
    config.write_text(json.dumps({"schema": "specdock.config/v1", "todo": {"parent_limit": 1, "subtask_limit": 1}}))
    added(world, "--title", "人のもの")  # a person's task is not counted
    first = added(world, "--title", "一", "--kind", "check", *AGENT)
    code, payload = todo(world, "add", "--title", "二", "--kind", "check", *AGENT)
    assert code == 0 and "TODO_LIMIT_EXCEEDED" in codes(payload)
    warning = next(item for item in payload["warnings"] if item["code"] == "TODO_LIMIT_EXCEEDED")
    assert warning["details"]["kind"] == "repository" and warning["details"]["source"] == "user"
    assert (warning["details"]["count"], warning["details"]["limit"]) == (2, 1)
    parent = first["todo"]["id"]
    added(world, "--parent", parent, "--title", "s1")
    code, payload = todo(world, "add", "--parent", parent, "--title", "s2")
    assert code == 0 and any(
        item["details"].get("kind") == "subtasks"
        for item in payload["warnings"]
        if item["code"] == "TODO_LIMIT_EXCEEDED"
    )
    (world.catalog / "todos/settings.json").write_text(
        json.dumps({"schema": "specdock.todo-settings/v1", "parent_limit": 50})
    )
    code, payload = todo(world, "settings")
    values = payload["data"]["result"]["values"]
    assert values["parent_limit"] == {"value": 50, "source": "repository"}
    assert values["subtask_limit"] == {"value": 1, "source": "user"}
    assert values["default_due"] == {"value": "4h", "source": "default"}
    config.write_text("{")
    code, payload = todo(world, "list")
    assert code == 0 and "TODO_SETTINGS_INVALID" in codes(payload)
    code, payload = todo(world, "settings")
    layers = {layer["layer"]: layer["state"] for layer in payload["data"]["result"]["layers"]}
    assert layers == {"user": "invalid", "repository": "ok"}


def test_settings_outside_a_checkout(world: WriteWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    from spec_dock.cli import main

    outside = tmp_path / "nowhere"
    outside.mkdir()
    capsys.readouterr()
    assert main(["--project", str(outside), "todo", "settings", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)["data"]["result"]
    layers = {layer["layer"]: layer["state"] for layer in result["layers"]}
    assert layers == {"user": "missing", "repository": "not_applicable"}


def test_scopes_are_marks_only(world: WriteWorld, clock: Clock) -> None:
    code, before = world.run("dependency", "check", "iss-531")
    result = added(world, "--title", "止める", "--blocks", "iss-531", "--scope", "epic-2")
    assert result["todo"]["scopes"] == {"related": ["epic-00002"], "blocks": ["iss-00531"]}
    code, payload = todo(world, "add", "--title", "知らない", "--scope", "iss-999")
    assert code == 0 and "TODO_SCOPE_UNKNOWN" in codes(payload)
    code, payload = todo(world, "add", "--title", "形が違う", "--scope", "issue-1")
    assert (code, payload["error"]["code"]) == (2, "TODO_INVALID")
    added(world, "--title", "関係なし")
    code, payload = todo(world, "list", "--scope", "iss-00531")
    assert [item["todo"]["id"] for item in payload["data"]["result"]["items"]] == [result["todo"]["id"]]
    code, payload = todo(world, "list", "--blocking")
    assert [item["todo"]["id"] for item in payload["data"]["result"]["items"]] == [result["todo"]["id"]]
    code, payload = todo(world, "update", result["todo"]["id"], "--remove-blocks", "iss-531", "--add-scope", "iss-531")
    assert code == 0 and payload["data"]["result"]["todo"]["scopes"]["blocks"] == []
    assert payload["data"]["result"]["todo"]["history"][-1]["fields"] == ["scopes"]
    code, after = world.run("dependency", "check", "iss-531")
    assert after["data"] == before["data"]


def test_readiness_code_never_reads_todos() -> None:
    root = Path(__file__).resolve().parents[2] / "src/spec_dock/runtime"
    for relative in (
        "domain/canonical_readiness.py",
        "application/canonical_scope_read.py",
        "application/work_start.py",
        "application/canonical_work.py",
    ):
        assert "todo" not in (root / relative).read_text(encoding="utf-8"), relative


def test_conflict_copies_duplicates_and_broken_records(world: WriteWorld, clock: Clock) -> None:
    result = added(world, "--title", "元")
    todo_id = result["todo"]["id"]
    path = world.catalog / result["path"]
    copy = path.with_name(f"{todo_id}.conflict-pc-20261104t010000z.json")
    copy.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    for argv in (("list",), ("show", todo_id), ("check",)):
        code, payload = todo(world, *argv)
        assert code == 0 and "TODO_CONFLICT_COPY" in codes(payload), argv
    copy.unlink()
    other = world.catalog / "todos/2026-10" / path.name
    other.parent.mkdir()
    other.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    code, payload = todo(world, "check")
    assert code == 7 and "TODO_ID_DUPLICATE" in [item["code"] for item in payload["data"]["result"]["errors"]]
    code, payload = todo(world, "done", todo_id)
    assert (code, payload["error"]["code"]) == (3, "TODO_ID_AMBIGUOUS")
    other.unlink()
    record = json.loads(path.read_text(encoding="utf-8"))
    record["status"] = "nope"
    path.write_text(json.dumps(record), encoding="utf-8")
    code, payload = todo(world, "check")
    errors = payload["data"]["result"]["errors"]
    assert code == 7 and {item["source"] for item in errors} == {"python", "cue"}
    assert all(item["file"] == result["path"] for item in errors)
    changesets = len(world.changesets())
    code, payload = todo(world, "done", todo_id)
    assert (code, payload["error"]["code"]) == (3, "TODO_RECORD_INVALID")
    record["schema"] = "specdock.todo/v9"
    path.write_text(json.dumps(record), encoding="utf-8")
    code, payload = todo(world, "update", todo_id, "--title", "x")
    assert (code, payload["error"]["code"]) == (3, "TODO_SCHEMA_UNSUPPORTED")
    code, payload = todo(world, "list")
    assert code == 0 and "TODO_RECORD_INVALID" in codes(payload)
    assert payload["data"]["result"]["repositories"][0]["invalid_files"] == [result["path"]]
    assert len(world.changesets()) == changesets


def test_check_without_cue_uses_python_only(world: WriteWorld, clock: Clock, monkeypatch: pytest.MonkeyPatch) -> None:
    added(world, "--title", "ふつう")
    import shutil

    real_which: Callable[..., Any] = shutil.which
    monkeypatch.setattr(shutil, "which", lambda name, *a, **k: None if name == "cue" else real_which(name, *a, **k))
    code, payload = todo(world, "check")
    assert code == 0 and "TODO_CUE_SKIPPED" in codes(payload)
    assert payload["data"]["result"]["cue"]["status"] == "skipped"


def test_an_unlinked_checkout_stops_before_writing(world: WriteWorld, clock: Clock) -> None:
    (world.main / "spec-dock/initiatives").unlink()
    for argv in (("add", "--title", "x"), ("list",), ("check",), ("settings",)):
        code, payload = todo(world, *argv)
        assert (code, payload["error"]["code"]) == (3, "CANONICAL_NOT_LINKED"), argv
        assert payload["error"]["details"]["next_step"] == "spec-dock canonical link"
    assert world.changesets() == []


def test_dry_run_plans_without_writing(world: WriteWorld, clock: Clock) -> None:
    code, payload = todo(world, "add", "--title", "試し", "--dry-run")
    assert code == 0 and payload["status"] == "planned"
    assert payload["data"]["result"]["todo"]["title"] == "試し"
    assert not (world.catalog / "todos").exists() and world.changesets() == []


def test_todos_do_not_disturb_the_scope_checks(world: WriteWorld, clock: Clock) -> None:
    code, scopes_before = world.run("scope", "list")
    code, validate_before = world.run("workspace", "validate")
    code, check_before = world.run("scope", "check", "iss-531")
    added(world, "--title", "置く")
    (world.catalog / "todos/settings.json").write_text(json.dumps({"schema": "specdock.todo-settings/v1"}))
    code, scopes_after = world.run("scope", "list")
    assert len(scopes_after["data"]["result"]["items"]) == len(scopes_before["data"]["result"]["items"])
    code, validate_after = world.run("workspace", "validate")
    assert (code, validate_after["data"]) == (validate_before["exit_code"], validate_before["data"])
    assert not any("MISPLACED" in json.dumps(item) for item in validate_after["warnings"])
    code, check_after = world.run("scope", "check", "iss-531")
    assert (check_after["exit_code"], check_after["data"]["result"]["errors"]) == (
        check_before["exit_code"],
        check_before["data"]["result"]["errors"],
    )


def test_a_busy_catalog_lock_stops_before_writing(
    world: WriteWorld, clock: Clock, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.application import todo_commands
    from spec_dock.runtime.infra.catalog_lock import CatalogLock

    monkeypatch.setattr(todo_commands, "CATALOG_LOCK_TIMEOUT", 0.2)
    with CatalogLock(world.catalog.resolve(), timeout=1):
        code, payload = todo(world, "add", "--title", "待つ")
    assert (code, payload["error"]["code"]) == (3, "CANONICAL_LOCK_BUSY")
    assert not (world.catalog / "todos").exists() and world.changesets() == []


def test_a_checkout_without_origin_still_works_with_a_null_ref(world: WriteWorld, clock: Clock) -> None:
    from tests.support.canonical_repo import git

    git(world.main, "remote", "rename", "origin", "upstream")
    result = added(world, "--title", "どこでも")
    assert result["ref"] is None and result["repository"] is None
    code, payload = todo(world, "list")
    assert code == 0 and payload["data"]["result"]["repositories"][0]["repository"] is None
