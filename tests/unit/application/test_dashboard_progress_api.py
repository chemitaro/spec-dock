"""The plan progress through the HTTP API and the revision (iss-00574 T-03)."""

from __future__ import annotations

from dataclasses import replace
import json
import os
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.runtime.application import (
    dashboard_progress as progress_module,
    dashboard_scope_details as details_module,
)
from spec_dock.runtime.application.dashboard_http import DashboardHttp, Request
from spec_dock.runtime.application.dashboard_site import DashboardSite
from spec_dock.runtime.application.scope_check import AssuranceReading
from tests.support.dashboard import NOW, node, snapshot
from tests.support.dashboard_site import register, scope_dir, write_snapshot

if TYPE_CHECKING:
    from pathlib import Path

    from spec_dock.runtime.infra.cue_tool import CueTool

HOST = "127.0.0.1:47800"
BASE = "/api/v1/r/github.com/o/r/"


class Reader:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def __call__(self, directory: Path, *, timeout: float, tool: CueTool | None = None) -> dict[str, object] | None:
        self.calls.append(directory.name)
        steps = json.loads((directory / "plan.cue").read_text())
        return {key: {"title": key, "status": value} for key, value in steps.items()}


class Env:
    """epic-00001 (in progress through its child) holds iss-00002 (in progress) and iss-00003 (ready)."""

    def __init__(self, tmp_path: Path, reader: Reader) -> None:
        self.reader = reader
        self.state = tmp_path / "state"
        self.catalog = tmp_path / "c"
        for scope_id in ("epic-00001", "iss-00002", "iss-00003"):
            (scope_dir(self.catalog, scope_id) / "plan.cue").write_text(json.dumps({"S-01": "done", "S-02": "todo"}))
        register(self.state, "github.com/o/r", self.catalog)
        structure = snapshot(
            node(1, "epic"),
            node(2, "issue", parent=1, in_progress=True),
            node(3, "issue", parent=1),
        )
        write_snapshot(self.state, replace(structure, repository="github.com/o/r"))
        self.http = DashboardHttp(
            DashboardSite(self.state, now=lambda: NOW),
            hosts=("127.0.0.1",),
            port=47800,
            embed_hosts=("127.0.0.1",),
            local_url="http://127.0.0.1:47800/",
            version="0.5.1",
            started_at="2026-11-04T11:00:00Z",
            now=lambda: NOW,
        )

    def json(self, path: str) -> Any:
        response = self.http.handle(Request("GET", BASE + path, {}, {"host": HOST}))
        assert response.status == 200, response.body
        return json.loads(response.body)


@pytest.fixture
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Env:
    reader = Reader()

    def read(directory: Path, *, timeout: float, tool: CueTool | None = None) -> dict[str, object] | None:
        return reader(directory, timeout=timeout, tool=tool)

    def no_level(directory: Path | None, *, timeout: float, tool: CueTool | None = None) -> AssuranceReading:
        return AssuranceReading(None, None, "unset")

    monkeypatch.setattr(progress_module, "read_plan_steps", read)
    monkeypatch.setattr(progress_module, "locate_cue", lambda *, timeout: object())
    monkeypatch.setattr(details_module, "read_assurance", no_level)
    monkeypatch.setattr(details_module, "worktree_list", lambda root, *, timeout: [])
    monkeypatch.setattr(details_module, "locate_cue", lambda *, timeout: object())
    return Env(tmp_path, reader)


def _progress(body: dict[str, Any]) -> dict[str, Any]:
    return {item["id"]: item["progress"] for item in body["scopes"]}


def test_only_the_issue_in_progress_carries_its_plan_counts(env: Env) -> None:
    got = _progress(env.json("structure"))
    assert got["epic-00001"] is None and got["iss-00003"] is None
    assert {k: got["iss-00002"][k] for k in ("total", "done", "doing", "todo", "dropped")} == {
        "total": 2,
        "done": 1,
        "doing": 0,
        "todo": 1,
        "dropped": 0,
    }
    assert got["iss-00002"]["modified_at"].endswith("Z")
    assert env.reader.calls == ["iss-00002"]


def test_the_scope_api_matches_and_keeps_the_remembered_counts(env: Env) -> None:
    structure = _progress(env.json("structure"))
    one = env.json("scopes/iss-00002")
    assert one["scope"]["progress"] == structure["iss-00002"]
    assert env.json("scopes/iss-00003")["scope"]["progress"] is None
    env.json("structure")
    assert env.reader.calls == ["iss-00002"]  # neither the detail nor the next list ran cue again


def test_rewriting_the_plan_of_an_issue_in_progress_changes_the_revision(env: Env) -> None:
    first = env.json("revision")["revision"]
    assert env.json("revision")["revision"] == first
    plan = env.catalog / "00000-00999" / "iss-00003" / "plan.cue"
    os.utime(plan, (1_800_000_000, 1_800_000_000))  # not in progress: no change
    assert env.json("revision")["revision"] == first
    plan = env.catalog / "00000-00999" / "iss-00002" / "plan.cue"
    plan.write_text(json.dumps({"S-01": "done", "S-02": "done"}))
    os.utime(plan, (1_800_000_000, 1_800_000_000))
    second = env.json("revision")["revision"]
    assert second != first
    assert _progress(env.json("structure"))["iss-00002"]["done"] == 2
