"""The dashboard's human-task API, marks and revision (iss-00554 T-03〜T-08, T-12)."""

from __future__ import annotations

from dataclasses import replace
import json
import time
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.runtime.application import dashboard_todos
from spec_dock.runtime.application.dashboard_http import DashboardHttp, Request
from spec_dock.runtime.application.dashboard_site import DashboardSite
from spec_dock.runtime.application.dashboard_summary import summarize
from spec_dock.runtime.domain.todo_record import new_record, transition
from spec_dock.runtime.infra.dashboard_store import hide_repository
from spec_dock.runtime.infra.github_structure import GithubRepository
from spec_dock.runtime.infra.todo_store import TodoStore, encode
from tests.support.dashboard import NOW, node, snapshot
from tests.support.dashboard_site import register, sample, write_snapshot

if TYPE_CHECKING:
    from pathlib import Path

HOST = "127.0.0.1:47800"
CREATED = "2026-11-01T00:00:00Z"
PAST = "2026-11-04T09:00:00Z"  # 3 hours before NOW
SOON = "2026-11-04T18:00:00Z"
LATER = "2026-11-20T00:00:00Z"


def put(catalog: Path, todo_id: str, *, due: str = LATER, action: str | None = None, **changes: Any) -> Path:
    record = new_record(todo_id, title=f"task {todo_id}", by="human", role=None, kind=None, now=CREATED, due=due)
    record.update(changes)
    if action is not None:
        record = transition(record, action, now="2026-11-02T00:00:00Z", by="human", role=None)
    store = TodoStore(catalog)
    path = store.record_path(todo_id, CREATED)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encode(record))
    return path


class Env:
    def __init__(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        self.clock = [NOW]
        self.state = tmp_path / "state"
        self.r = tmp_path / "r" / "spec-dock" / ".canonical"
        self.s = tmp_path / "s" / "spec-dock" / ".canonical"
        register(self.state, "github.com/o/r", self.r)
        register(self.state, "github.com/o/s", self.s)
        write_snapshot(self.state, sample("github.com/o/r"))
        write_snapshot(self.state, sample("github.com/o/s"))
        self.site = DashboardSite(self.state, now=lambda: self.clock[0])
        self.http = DashboardHttp(
            self.site,
            hosts=("127.0.0.1",),
            port=47800,
            embed_hosts=("127.0.0.1",),
            local_url=None,
            version="0.5.1",
            started_at="2026-11-04T11:00:00Z",
            now=lambda: self.clock[0],
        )

    def get(self, path: str) -> Any:
        target, _, query = path.partition("?")
        params: dict[str, list[str]] = {}
        for pair in filter(None, query.split("&")):
            key, _, value = pair.partition("=")
            params.setdefault(key, []).append(value)
        return self.http.handle(Request("GET", target, params, {"host": HOST}))

    def json(self, path: str) -> tuple[int, Any]:
        response = self.get(path)
        assert response.header("content-type").startswith("application/json"), path
        return response.status, json.loads(response.body)


@pytest.fixture
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Env:
    return Env(tmp_path, monkeypatch)


def ids(document: dict[str, Any]) -> list[str]:
    return [item["todo"]["id"] for item in document["items"]]


# --- T-03: every visible repository ----------------------------------------------------------------------------


def test_all_repositories_in_the_d08_order_without_hidden_ones(env: Env) -> None:
    put(env.r, "t-0001", due=LATER)
    put(env.r, "t-0002", due=PAST)
    put(env.s, "t-0003", due=SOON)
    put(env.s, "t-0004", scopes={"related": [], "blocks": ["iss-00003"]})
    put(env.s, "t-0005", action="done")
    status, body = env.json("/api/v1/todos")
    assert status == 200 and body["schema"] == "specdock.todo-list/v1" and body["mode"] == "all_repositories"
    assert ids(body) == ["t-0002", "t-0003", "t-0004", "t-0001"]  # overdue, soon, blocking, later
    assert [item["repository"] for item in body["items"]] == [
        "github.com/o/r",
        "github.com/o/s",
        "github.com/o/s",
        "github.com/o/r",
    ]
    assert body["items"][0]["ref"] == "o/r/t-0002" and body["items"][0]["derived"]["overdue"] is True
    assert [row["repository"] for row in body["repositories"]] == ["github.com/o/r", "github.com/o/s"]
    assert all(row["status"] == "ok" and row["hidden"] is False for row in body["repositories"])
    assert ids(env.json("/api/v1/todos?status=all")[1])[-1] == "t-0005"
    assert ids(env.json("/api/v1/todos?status=done")[1]) == ["t-0005"]
    status, error = env.json("/api/v1/todos?status=nope")
    assert status == 400 and error["error"]["code"] == "DASHBOARD_TODO_FILTER_INVALID"
    hide_repository(env.state, GithubRepository("o", "s"), now=NOW)
    status, body = env.json("/api/v1/todos")
    assert ids(body) == ["t-0002", "t-0001"] and [row["repository"] for row in body["repositories"]] == [
        "github.com/o/r"
    ]


# --- T-04: one repository and one task -------------------------------------------------------------------------


def test_one_repository_list_and_one_task(env: Env) -> None:
    put(env.r, "t-0001", body="**x**", subtasks=[])
    put(env.s, "t-0002")
    status, body = env.json("/api/v1/r/github.com/o/r/todos")
    assert status == 200 and body["mode"] == "repository" and ids(body) == ["t-0001"]
    assert [row["repository"] for row in body["repositories"]] == ["github.com/o/r"]
    status, one = env.json("/api/v1/r/github.com/o/r/todos/t-0001")
    assert status == 200 and one["todo"]["id"] == "t-0001" and one["ref"] == "o/r/t-0001"
    assert set(one) >= {"todo", "derived", "ref", "repository", "path", "warnings_detail"}
    assert one["path"] == "todos/2026-11/t-0001.json"
    for missing in ("t-zzzz", "nonsense", "t-0002"):
        status, error = env.json(f"/api/v1/r/github.com/o/r/todos/{missing}")
        assert status == 404, missing
        assert error["error"]["code"] in ("TODO_NOT_FOUND", "TODO_INVALID")
    put(env.r, "t-0009").write_text("{ broken")
    status, error = env.json("/api/v1/r/github.com/o/r/todos/t-0009")
    assert status == 409 and error["error"]["code"] == "TODO_RECORD_INVALID"
    assert env.json("/api/v1/r/github.com/o/x/todos")[0] == 404
    hide_repository(env.state, GithubRepository("o", "s"), now=NOW)
    assert env.json("/api/v1/r/github.com/o/s/todos")[0] == 404


def test_one_task_of_an_unreadable_catalog_is_503(env: Env) -> None:
    (env.r / "todos").write_text("not a directory")
    status, error = env.json("/api/v1/r/github.com/o/r/todos/t-0001")
    assert status == 503 and error["error"]["code"] == "TODO_REPOSITORY_UNREADABLE"
    assert error["error"]["next_steps"]
    status, body = env.json("/api/v1/r/github.com/o/r/todos")
    assert status == 200 and body["repositories"][0]["status"] == "unreadable"


# --- T-05: one repository's failure ----------------------------------------------------------------------------


def test_one_unreadable_repository_and_broken_files_stay_in_their_rows(env: Env) -> None:
    (env.r / "todos").write_text("not a directory")
    put(env.s, "t-0001")
    put(env.s, "t-0002").write_text("[]")
    copy = env.s / "todos" / "2026-11" / "t-0001.conflict-pc-20261104.json"
    copy.write_text("{}")
    status, body = env.json("/api/v1/todos")
    assert status == 200
    rows = {row["repository"]: row for row in body["repositories"]}
    assert (
        rows["github.com/o/r"]["status"] == "unreadable"
        and rows["github.com/o/r"]["problem"]["code"] == "TODO_REPOSITORY_UNREADABLE"
    )
    assert rows["github.com/o/s"]["status"] == "ok"
    assert rows["github.com/o/s"]["invalid_files"] == ["todos/2026-11/t-0002.json"]
    assert rows["github.com/o/s"]["conflict_copies"] == ["todos/2026-11/t-0001.conflict-pc-20261104.json"]
    assert ids(body) == ["t-0001"]


# --- T-06: revision and the remembered readings ----------------------------------------------------------------


def test_revision_follows_the_tasks_and_the_clock(env: Env, monkeypatch: pytest.MonkeyPatch) -> None:
    def revisions() -> tuple[str, str]:
        return (
            env.json("/api/v1/r/github.com/o/r/revision")[1]["revision"],
            env.json("/api/v1/todos/revision")[1]["revision"],
        )

    first = revisions()
    assert revisions() == first
    put(env.r, "t-0001", due=SOON)
    second = revisions()
    assert second[0] != first[0] and second[1] != first[1]
    calls: list[object] = []
    real = dashboard_todos.read_catalog

    def counted(*args: Any, **kwargs: Any) -> Any:
        calls.append(args)
        return real(*args, **kwargs)

    monkeypatch.setattr(dashboard_todos, "read_catalog", counted)
    assert revisions() == second
    env.json("/api/v1/todos")
    env.json("/api/v1/r/github.com/o/r/structure")
    assert calls == []  # nothing changed, nothing re-read
    env.clock[0] = NOW.replace(hour=19)  # the task's due passes without any write
    third = revisions()
    assert third[0] != second[0] and third[1] != second[1]
    assert calls == []
    _status, body = env.json("/api/v1/todos")
    assert body["items"][0]["derived"]["overdue"] is True


def test_a_catalog_without_todos_that_breaks_or_heals_is_noticed(env: Env) -> None:
    def summary() -> dict[str, Any]:
        return env.json("/api/v1/r/github.com/o/r/structure")[1]["todos"]

    assert summary()["status"] == "ok"  # no todos/ yet: zero tasks
    moved = env.r.with_name("moved")
    env.r.rename(moved)
    assert summary()["status"] == "unavailable"
    moved.rename(env.r)
    assert summary()["status"] == "ok"


# --- T-07: marks, lists and the summary on structure and scope -------------------------------------------------


def test_structure_and_scope_carry_marks_lists_and_the_summary(env: Env) -> None:
    put(env.r, "t-0001", due=PAST, scopes={"related": [], "blocks": ["iss-00003"]})
    put(env.r, "t-0002", scopes={"related": ["iss-00003"], "blocks": ["epic-00001"]})
    put(env.r, "t-0003", scopes={"related": [], "blocks": []})
    status, body = env.json("/api/v1/r/github.com/o/r/structure")
    assert status == 200
    marks = {scope["id"]: scope["todos"] for scope in body["scopes"]}
    assert marks["iss-00003"] == {"blocking": 1, "blocking_with_descendants": 1, "related": 1}
    assert marks["epic-00001"] == {"blocking": 1, "blocking_with_descendants": 2, "related": 0}
    assert marks["iss-00002"] == {"blocking": 0, "blocking_with_descendants": 0, "related": 0}
    cli = summarize(
        "dashboard summary", GithubRepository("o", "r"), state_root=env.state, now=lambda: NOW, todo_now=lambda: NOW
    )
    expected = cli.data.result["todos"]  # type: ignore[attr-defined]
    assert body["todos"] == expected and body["todos"]["open"] == 3 and body["todos"]["overdue"] == 1
    status, scope = env.json("/api/v1/r/github.com/o/r/scopes/iss-00003")
    lists = scope["todos"]
    assert lists["status"] == "ok"
    assert [item["id"] for item in lists["blocking"]] == ["t-0001"] and lists["blocking"][0]["overdue"] is True
    assert set(lists["blocking"][0]) >= {
        "ref",
        "repository",
        "id",
        "title",
        "kind",
        "due",
        "overdue",
        "due_soon",
        "effective_status",
        "blocks",
        "related",
    }
    assert [item["id"] for item in lists["related"]] == ["t-0002"]
    assert lists["descendants"] == []
    epic = env.json("/api/v1/r/github.com/o/r/scopes/epic-00001")[1]["todos"]
    assert [item["id"] for item in epic["blocking"]] == ["t-0002"]
    assert [item["id"] for item in epic["descendants"]] == ["t-0001"]


def test_structure_survives_unreadable_or_failing_tasks(env: Env, monkeypatch: pytest.MonkeyPatch) -> None:
    (env.r / "todos").write_text("not a directory")
    status, body = env.json("/api/v1/r/github.com/o/r/structure")
    assert status == 200 and body["todos"]["status"] == "unavailable" and body["todos"]["problem"]["code"]
    assert all(scope["todos"]["blocking"] == 0 for scope in body["scopes"])
    status, scope = env.json("/api/v1/r/github.com/o/r/scopes/iss-00003")
    assert status == 200 and scope["todos"]["status"] == "unavailable" and scope["todos"]["blocking"] == []

    def boom(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr(dashboard_todos, "read_catalog", boom)
    put(env.s, "t-0001")
    status, body = env.json("/api/v1/r/github.com/o/s/structure")
    assert status == 200 and body["todos"]["status"] == "unavailable"
    assert env.json("/api/v1/r/github.com/o/s/revision")[0] == 200


# --- T-08: screen paths and read only --------------------------------------------------------------------------


@pytest.mark.parametrize("path", ["/todos", "/r/github.com/o/r/todos", "/r/github.com/o/r/todos/t-0001"])
def test_task_screen_paths_return_the_shell(env: Env, path: str) -> None:
    response = env.get(path)
    assert response.status == 200 and response.header("content-type").startswith("text/html")
    assert b'id="view"' in response.body


def test_reading_every_task_route_writes_nothing(env: Env) -> None:
    put(env.r, "t-0001", scopes={"related": [], "blocks": ["iss-00003"]})

    def tree() -> dict[str, bytes]:
        return {
            str(path): path.read_bytes()
            for root in (env.r, env.s, env.state)
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }

    before = tree()
    for path in (
        "/todos",
        "/r/github.com/o/r/todos",
        "/r/github.com/o/r/todos/t-0001",
        "/api/v1/todos",
        "/api/v1/todos?status=all",
        "/api/v1/todos/revision",
        "/api/v1/r/github.com/o/r/todos",
        "/api/v1/r/github.com/o/r/todos/t-0001",
        "/api/v1/r/github.com/o/r/structure",
        "/api/v1/r/github.com/o/r/scopes/iss-00003",
        "/api/v1/r/github.com/o/r/revision",
    ):
        assert env.get(path).status == 200, path
    assert tree() == before


# --- T-12: speed ------------------------------------------------------------------------------------------------


def test_250_scopes_and_100_tasks_stay_quick(env: Env) -> None:
    nodes = [node(1, "initiative")]
    nodes += [node(number, "epic", parent=1) for number in range(2, 22)]
    nodes += [node(number, "issue", parent=2 + (number % 20)) for number in range(22, 251)]
    structure = replace(snapshot(*nodes, fetched_at="2026-11-04T11:50:00Z"), repository="github.com/o/r")
    write_snapshot(env.state, structure)
    for index in range(100):
        put(env.r, f"t-{index:04d}", scopes={"related": [], "blocks": [f"iss-{22 + index * 2:05d}"]})
    env.json("/api/v1/r/github.com/o/r/structure")  # warm the caches
    started = time.perf_counter()
    status, body = env.json("/api/v1/r/github.com/o/r/structure")
    elapsed = time.perf_counter() - started
    assert status == 200 and body["todos"]["blocking"] == 100
    initiative = next(scope for scope in body["scopes"] if scope["id"] == "init-00001")
    assert initiative["todos"]["blocking_with_descendants"] == 100
    assert elapsed < 1.0, elapsed
