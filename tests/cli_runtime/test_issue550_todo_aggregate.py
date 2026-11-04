"""Human tasks of every registered repository and the summary's counts (iss-00550, epic-00547 D-13〜D-15).

The world is the linked clone of iss-00549 (fake gh on PATH, HOME/XDG_* in the temporary directory). Other
repositories are plain catalog directories registered in the temporary state root, holding record files copied
from tasks the CLI wrote, so every record has the real v1 shape.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import shutil
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.cli import main
from spec_dock.runtime.application import todo_common
from spec_dock.runtime.domain.canonical_sync_state import RegistryEntry, SyncRegistry
from spec_dock.runtime.infra.canonical_registry import write_registry_locked
from tests.support.canonical_writes import WriteWorld
from tests.support.dashboard_site import sample, write_snapshot

if TYPE_CHECKING:
    from collections.abc import Iterator

START = datetime(2026, 11, 4, 1, 0, tzinfo=timezone.utc)
MAIN = "github.com/example/repo"
OTHER = "github.com/o/s"


class Clock:
    def __init__(self) -> None:
        self.now = START

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **delta: float) -> None:
        self.now += timedelta(**delta)


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> Clock:
    fixed = Clock()
    monkeypatch.setattr(todo_common, "utc_now", fixed)
    return fixed


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> WriteWorld:
    built = WriteWorld.create(tmp_path, monkeypatch, capsys)
    built.scope("issue", 531, "葉の作業")
    code, payload = built.run("scope", "list")
    assert code == 0, payload
    return built


@pytest.fixture
def outside(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    place = tmp_path / "elsewhere"
    place.mkdir()
    monkeypatch.chdir(place)
    yield place


def state_root(world: WriteWorld) -> Path:
    return world.state / "spec-dock"


def register(world: WriteWorld, rows: list[tuple[str | None, Path, Path]]) -> None:
    """Replace the registry with (repository, catalog, main checkout) rows."""
    entries = tuple(
        RegistryEntry(str(catalog), str(checkout), repository, str(checkout / ".git"), "2026-11-01T00:00:00Z")
        for repository, catalog, checkout in rows
    )
    write_registry_locked(state_root(world), SyncRegistry(None, entries))


def other_catalog(world: WriteWorld, name: str, records: list[Path]) -> Path:
    catalog = world.tmp_path / name / "spec-dock" / ".canonical"
    for record in records:
        target = catalog / record.relative_to(world.catalog)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(record, target)
    catalog.mkdir(parents=True, exist_ok=True)
    return catalog


def add(world: WriteWorld, *argv: str) -> dict[str, Any]:
    code, payload = world.run("todo", "add", *argv)
    assert code == 0, payload
    return payload["data"]["result"]


def outside_run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, dict[str, Any]]:
    code = main([*argv, "--json"])
    return code, json.loads(capsys.readouterr().out)


def codes(payload: dict[str, Any]) -> list[str]:
    return [item["code"] for item in payload["warnings"]]


def two_repositories(world: WriteWorld) -> tuple[dict[str, Any], dict[str, Any], Path]:
    """A task in this clone's catalog and another (moved out of it) in a second repository's catalog."""
    mine = add(world, "--title", "窓口に電話する", "--blocks", "iss-531")
    theirs = add(world, "--title", "別の箱", "--due", "30m")
    moved = world.catalog / theirs["path"]
    catalog = other_catalog(world, "s", [moved])
    moved.unlink()
    register(world, [(MAIN, world.catalog, world.main), (OTHER, catalog, catalog.parent.parent)])
    return mine, theirs, catalog


def test_every_registered_repository_is_listed_outside_a_checkout(
    world: WriteWorld, clock: Clock, outside: Path
) -> None:
    mine, theirs, _catalog = two_repositories(world)
    before = len(world.requests())
    code, payload = outside_run(world.capsys, "todo", "list", "--all-repositories")
    assert code == 0, payload
    document = payload["data"]["result"]
    assert document["schema"] == "specdock.todo-list/v1" and document["mode"] == "all_repositories"
    assert [row["repository"] for row in document["repositories"]] == [MAIN, OTHER]
    assert [row["status"] for row in document["repositories"]] == ["ok", "ok"]
    assert [row["counts"]["open"] for row in document["repositories"]] == [1, 1]
    # The second repository's task is due sooner, so it comes first (epic-00547 D-08).
    assert [(item["ref"], item["repository"]) for item in document["items"]] == [
        (f"o/s/{theirs['todo']['id']}", OTHER),
        (f"example/repo/{mine['todo']['id']}", MAIN),
    ]
    assert document["filters"]["repositories"] == []
    code, payload = outside_run(world.capsys, "todo", "list", "--repository", "o/s")
    assert code == 0, payload
    document = payload["data"]["result"]
    assert document["mode"] == "all_repositories" and document["filters"]["repositories"] == [OTHER]
    assert [row["repository"] for row in document["repositories"]] == [OTHER]
    assert [item["todo"]["id"] for item in document["items"]] == [theirs["todo"]["id"]]
    code, payload = outside_run(world.capsys, "todo", "list", "--repository", "o/missing", "--repository", "o/s")
    assert code == 0 and codes(payload) == ["TODO_REPOSITORY_UNKNOWN"]
    assert payload["warnings"][0]["details"]["repository"] == "github.com/o/missing"
    code, payload = outside_run(world.capsys, "todo", "list", "--repository", "not a repository")
    assert (code, payload["error"]["code"]) == (2, "TODO_REPOSITORY_INVALID")
    assert len(world.requests()) == before  # nothing reached GitHub


def test_the_checkout_list_keeps_its_mode_and_the_flags_read_the_registry_inside_it(
    world: WriteWorld, clock: Clock
) -> None:
    two_repositories(world)
    code, payload = world.run("todo", "list")
    assert code == 0 and payload["data"]["result"]["mode"] == "repository"
    assert payload["data"]["result"]["filters"]["repositories"] == []
    code, payload = world.run("todo", "list", "--all-repositories")
    assert code == 0 and len(payload["data"]["result"]["repositories"]) == 2


def test_hidden_unknown_and_second_clones(world: WriteWorld, clock: Clock, outside: Path) -> None:
    mine = add(world, "--title", "見る")
    copy = other_catalog(world, "copy", [world.catalog / mine["path"]])
    nameless = other_catalog(world, "nameless", [world.catalog / mine["path"]])
    register(
        world,
        [
            (MAIN, copy, world.tmp_path / "zz-second"),
            (None, nameless, world.tmp_path / "nameless"),
            (MAIN, world.catalog, world.main),
        ],
    )
    code, payload = outside_run(world.capsys, "dashboard", "hide", "example/repo")
    assert code == 0, payload
    code, payload = outside_run(world.capsys, "todo", "list", "--all-repositories")
    assert code == 0, payload
    rows = payload["data"]["result"]["repositories"]
    assert [(row["repository"], row["catalog"], row["status"], row["hidden"]) for row in rows] == [
        (MAIN, str(world.catalog), "ok", True),
        (MAIN, str(copy), "duplicate", True),
        (None, str(nameless), "ok", False),
    ]
    assert rows[1]["counts"] is None and rows[1]["problem"]["code"] == "TODO_REPOSITORY_DUPLICATE"
    assert "TODO_REPOSITORY_DUPLICATE" in codes(payload)
    items = payload["data"]["result"]["items"]
    assert sorted((item["ref"], item["repository"]) for item in items if item["repository"] is None) == [(None, None)]
    assert len(items) == 2


def test_an_unreadable_catalog_is_reported_and_the_others_are_returned(
    world: WriteWorld, clock: Clock, outside: Path
) -> None:
    mine = add(world, "--title", "読める")
    broken = world.tmp_path / "broken" / "catalog"
    (broken / "todos").parent.mkdir(parents=True)
    (broken / "todos").write_text("not a directory", encoding="utf-8")
    register(
        world,
        [
            (MAIN, world.catalog, world.main),
            ("github.com/o/gone", world.tmp_path / "gone" / "catalog", world.tmp_path / "gone"),
            ("github.com/o/file", broken, broken.parent),
        ],
    )
    code, payload = outside_run(world.capsys, "todo", "list", "--all-repositories")
    assert code == 0, payload
    rows = {row["repository"]: row for row in payload["data"]["result"]["repositories"]}
    for name, checkout in (("github.com/o/gone", world.tmp_path / "gone"), ("github.com/o/file", broken.parent)):
        assert rows[name]["status"] == "unreadable" and rows[name]["counts"] is None
        assert rows[name]["problem"]["code"] == "TODO_REPOSITORY_UNREADABLE"
        assert rows[name]["problem"]["next_step"] == f"spec-dock --project {checkout} canonical link"
    assert codes(payload).count("TODO_REPOSITORY_UNREADABLE") == 2
    assert [item["todo"]["id"] for item in payload["data"]["result"]["items"]] == [mine["todo"]["id"]]
    registry = state_root(world) / "canonical-registry.json"
    registry.write_text("{broken", encoding="utf-8")
    code, payload = outside_run(world.capsys, "todo", "list", "--all-repositories")
    assert (code, payload["error"]["code"]) == (3, "TODO_REGISTRY_UNREADABLE")
    registry.unlink()
    code, payload = outside_run(world.capsys, "todo", "list", "--all-repositories")
    assert code == 0 and payload["data"]["result"]["repositories"] == []


def test_broken_records_and_conflict_copies_stay_in_their_repository(
    world: WriteWorld, clock: Clock, outside: Path
) -> None:
    good = add(world, "--title", "残る")
    bad = add(world, "--title", "壊す")
    path = world.catalog / bad["path"]
    path.write_text("{not json", encoding="utf-8")
    copy = path.with_name(f"{good['todo']['id']}.conflict-pc-20261104.json")
    copy.write_text("{}", encoding="utf-8")
    register(world, [(MAIN, world.catalog, world.main)])
    code, payload = outside_run(world.capsys, "todo", "list", "--all-repositories")
    assert code == 0, payload
    (row,) = payload["data"]["result"]["repositories"]
    assert row["status"] == "ok" and row["invalid_files"] == [bad["path"]]
    assert row["conflict_copies"] == [copy.relative_to(world.catalog).as_posix()]
    assert [item["todo"]["id"] for item in payload["data"]["result"]["items"]] == [good["todo"]["id"]]
    found = {item["code"]: item["details"] for item in payload["warnings"]}
    assert found["TODO_RECORD_INVALID"]["repository"] == MAIN
    assert found["TODO_CONFLICT_COPY"]["repository"] == MAIN


def test_show_ref_reads_one_task_outside_a_checkout(world: WriteWorld, clock: Clock, outside: Path) -> None:
    result = add(world, "--title", "束", "--kind", "checklist", "--item", "一", "--item", "二")
    todo_id = result["todo"]["id"]
    register(world, [(MAIN, world.catalog, world.main)])
    before = len(world.requests())
    for ref in (f"example/repo/{todo_id}", f"github.com/example/repo/{todo_id.upper()}", f"example/repo/{todo_id}.2"):
        code, payload = outside_run(world.capsys, "todo", "show", ref)
        assert code == 0, (ref, payload)
        view = payload["data"]["result"]
        assert view["ref"] == f"example/repo/{todo_id}" and view["path"] == result["path"]
        assert [item["title"] for item in view["derived"]["open_subtasks"]] == ["一", "二"]
    for ref, exit_code, code_name in (
        ("o/missing/t-0000", 3, "TODO_REPOSITORY_UNKNOWN"),
        ("no-such-host.example/o/r/t-0000", 2, "TODO_REPOSITORY_INVALID"),
        ("example/repo/t-u000", 2, "TODO_INVALID"),
        ("example/repo/t-0000", 3, "TODO_NOT_FOUND"),
        (f"example/repo/{todo_id}.9", 3, "TODO_NOT_FOUND"),
    ):
        code, payload = outside_run(world.capsys, "todo", "show", ref)
        assert (code, payload["error"]["code"]) == (exit_code, code_name), ref
    register(world, [(MAIN, world.tmp_path / "gone", world.tmp_path)])
    code, payload = outside_run(world.capsys, "todo", "show", f"example/repo/{todo_id}")
    assert (code, payload["error"]["code"]) == (3, "TODO_REPOSITORY_UNREADABLE")
    assert len(world.requests()) == before


def summary_todos(payload: dict[str, Any]) -> dict[str, Any]:
    return payload["data"]["result"]["todos"]


def test_dashboard_summary_counts_parent_tasks(world: WriteWorld, clock: Clock) -> None:
    write_snapshot(state_root(world), sample(MAIN))
    add(world, "--title", "止める", "--blocks", "iss-531", "--due", "30m")
    add(world, "--title", "あとで", "--due", "2d")
    snoozed = add(world, "--title", "延期", "--due", "3d")
    code, payload = world.run("todo", "snooze", snoozed["todo"]["id"], "--until", "1d")
    assert code == 0, payload
    closed = add(world, "--title", "済み")
    code, payload = world.run("todo", "done", closed["todo"]["id"])
    assert code == 0, payload
    add(world, "--title", "束", "--kind", "checklist", "--item", "一", "--item", "二")
    clock.advance(hours=1)  # the first task is now overdue
    before = len(world.requests())
    code, payload = world.run("dashboard", "summary")
    assert code == 0, payload
    assert summary_todos(payload) == {"status": "ok", "open": 4, "blocking": 1, "overdue": 1, "problem": None}
    assert len(world.requests()) == before


def test_dashboard_summary_reads_the_linked_catalog_or_else_the_registry(
    world: WriteWorld, clock: Clock, outside: Path
) -> None:
    write_snapshot(state_root(world), sample(MAIN))
    add(world, "--title", "一つ")
    register(world, [])  # as after `canonical link --no-schedule`: the registry does not know this catalog
    code, payload = world.run("dashboard", "summary")
    assert code == 0 and summary_todos(payload)["open"] == 1
    code, payload = outside_run(world.capsys, "dashboard", "summary", "example/repo")
    assert code == 0, payload
    todos = summary_todos(payload)
    assert (todos["status"], todos["open"], todos["problem"]["code"]) == (
        "unavailable",
        None,
        "TODO_REPOSITORY_UNKNOWN",
    )
    register(world, [(MAIN, world.catalog, world.main)])
    code, payload = outside_run(world.capsys, "dashboard", "summary", "example/repo")
    assert code == 0 and summary_todos(payload)["open"] == 1
    register(world, [(MAIN, world.tmp_path / "gone", world.tmp_path)])
    code, payload = outside_run(world.capsys, "dashboard", "summary", "example/repo")
    assert code == 0 and summary_todos(payload)["problem"]["code"] == "TODO_REPOSITORY_UNREADABLE"
    (state_root(world) / "canonical-registry.json").write_text("{broken", encoding="utf-8")
    code, payload = outside_run(world.capsys, "dashboard", "summary", "example/repo")
    assert code == 0 and summary_todos(payload)["problem"]["code"] == "TODO_REGISTRY_UNREADABLE"
    assert main(["dashboard", "summary", "example/repo"]) == 0
    assert "todos unavailable [TODO_REGISTRY_UNREADABLE]" in world.capsys.readouterr().out


def test_the_server_summary_has_the_same_counts(world: WriteWorld, clock: Clock, outside: Path) -> None:
    from spec_dock.runtime.application.dashboard_http import DashboardHttp, Request
    from spec_dock.runtime.application.dashboard_site import DashboardSite

    write_snapshot(state_root(world), sample(MAIN))
    add(world, "--title", "止める", "--blocks", "iss-531")
    register(world, [(MAIN, world.catalog, world.main)])
    code, payload = outside_run(world.capsys, "dashboard", "summary", "example/repo")
    assert code == 0, payload
    http = DashboardHttp(
        DashboardSite(state_root(world), now=clock),
        hosts=("127.0.0.1",),
        port=47800,
        embed_hosts=("127.0.0.1",),
        local_url="http://127.0.0.1:47800/",
        version="0.0.0",
        started_at="2026-11-04T00:00:00Z",
        now=clock,
    )
    response = http.handle(Request("GET", "/api/v1/r/github.com/example/repo/summary", {}, {"host": "127.0.0.1:47800"}))
    assert response.status == 200, response.body
    served = json.loads(response.body)["todos"]
    assert served == summary_todos(payload) and served["blocking"] == 1


def test_the_text_output_names_each_repository_and_task(world: WriteWorld, clock: Clock, outside: Path) -> None:
    mine = add(world, "--title", "見る")
    copy = other_catalog(world, "copy", [world.catalog / mine["path"]])
    register(
        world,
        [
            (MAIN, world.catalog, world.main),
            (MAIN, copy, world.tmp_path / "zz-second"),
            ("github.com/o/gone", world.tmp_path / "gone", world.tmp_path),
        ],
    )
    assert main(["todo", "list", "--all-repositories"]) == 0
    out = world.capsys.readouterr().out
    assert f"{MAIN}: open=1 overdue=0 blocking=0 snoozed=0" in out
    assert f"{MAIN}: duplicate {copy} (" in out
    assert "github.com/o/gone: unreadable [TODO_REPOSITORY_UNREADABLE]" in out
    assert f"example/repo/{mine['todo']['id']}  " in out


def test_the_shipped_reference_and_the_help_name_the_new_contract() -> None:
    from spec_dock.runtime.cli.catalog import HELP_PRECONDITIONS

    root = Path(__file__).resolve().parents[2]
    shipped = (root / "src/spec_dock/assets/spec_dock/docs/reference_cli.md").read_text(encoding="utf-8")
    assert (root / "spec-dock/docs/reference_cli.md").read_text(encoding="utf-8") == shipped
    for text in (
        "--all-repositories",
        "--repository REPOSITORY",
        "`ID\\|REF`",
        "all_repositories",
        "duplicate",
        "| `todos` |",
        "TODO_REPOSITORY_INVALID",
        "TODO_REPOSITORY_UNKNOWN",
        "TODO_REPOSITORY_UNREADABLE",
        "TODO_REPOSITORY_DUPLICATE",
        "TODO_REGISTRY_UNREADABLE",
    ):
        assert text in shipped, text
    assert "without a checkout" in HELP_PRECONDITIONS["todo list"]
    assert "needs no checkout" in HELP_PRECONDITIONS["todo show"]
    assert "todos counts" in HELP_PRECONDITIONS["dashboard summary"]
