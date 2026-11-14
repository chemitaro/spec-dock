"""Every Scope's assurance level and this PC's branch in the structure API (iss-00544 T-02〜T-05)."""

from __future__ import annotations

from dataclasses import replace
import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.runtime.application import dashboard_scope_details as details_module
from spec_dock.runtime.application.contracts import GitWorktreeRecord
from spec_dock.runtime.application.dashboard_http import DashboardHttp, Request
from spec_dock.runtime.application.dashboard_scope_details import StructureFactsCache, read_structure_facts
from spec_dock.runtime.application.dashboard_site import DashboardSite, SiteRepository
from spec_dock.runtime.application.scope_check import AssuranceReading
from spec_dock.runtime.infra.cue_tool import CueToolError
from spec_dock.runtime.infra.git_process import GitProcessError
from spec_dock.runtime.infra.github_structure import GithubRepository
from tests.support.dashboard import NOW, node, snapshot
from tests.support.dashboard_site import register, scope_dir, write_snapshot

if TYPE_CHECKING:
    from spec_dock.runtime.infra.cue_tool import CueTool

HOST = "127.0.0.1:47800"
REPO = GithubRepository("o", "r")
IDS = ("epic-00001", "iss-00002", "iss-00003", "iss-00004")


def _site(catalog: Path | None) -> SiteRepository:
    return SiteRepository(REPO, catalog, ())


def _catalog(tmp_path: Path) -> Path:
    """epic-00001 and iss-00002 are CUE Scopes, iss-00003 a Markdown Scope, iss-00004 has no directory."""
    catalog = tmp_path / "c"
    (scope_dir(catalog, "epic-00001") / "requirement.cue").write_text("strict")
    (scope_dir(catalog, "iss-00002") / "requirement.cue").write_text("light")
    (scope_dir(catalog, "iss-00003") / "requirement.md").write_text("# r")
    return catalog


class Reader:
    """Reads the level written as the file's text; counts the calls."""

    def __init__(self) -> None:
        self.calls: list[Path | None] = []

    def __call__(self, directory: Path | None, *, timeout: float, tool: CueTool | None = None) -> AssuranceReading:
        self.calls.append(directory)
        assert directory is not None and timeout <= 3.0
        text = (directory / "requirement.cue").read_text()
        if text == "broken":
            return AssuranceReading(None, None, "unreadable")
        return AssuranceReading(text, "because", "cue")


class Lister:
    def __init__(self, records: list[GitWorktreeRecord] | None = None, error: Exception | None = None) -> None:
        self.records = records or []
        self.error = error
        self.calls = 0

    def __call__(self, repo_root: Path, *, timeout: float) -> list[GitWorktreeRecord]:
        self.calls += 1
        assert timeout <= 3.0
        if self.error is not None:
            raise self.error
        return self.records


def _locate(*, timeout: float) -> Any:
    return object()


def _read(catalog: Path | None, cache: StructureFactsCache, **kwargs: Any) -> dict[str, dict[str, object]]:
    kwargs.setdefault("assurance_reader", Reader())
    kwargs.setdefault("worktree_lister", Lister())
    kwargs.setdefault("cue_locator", _locate)
    return read_structure_facts(_site(catalog), IDS, cache, **kwargs).readings


# --- T-02: values ------------------------------------------------------------------------------------------


def test_cue_scopes_get_their_level_and_worktrees_their_branch(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path)
    lister = Lister([
        GitWorktreeRecord(Path("/w/main"), "a", "main"),
        GitWorktreeRecord(Path("/w/a"), "b", "chemitaro/iss-00002"),
        GitWorktreeRecord(Path("/w/b"), "c", "iss-00002-second"),
        GitWorktreeRecord(Path("/w/c"), "d", "iss-00004-x"),
        GitWorktreeRecord(Path("/w/d"), "e", None, detached=True),
    ])
    facts = _read(catalog, StructureFactsCache(), worktree_lister=lister)
    assert facts == {
        "epic-00001": {"assurance": "strict", "branch": None, "worktrees": []},
        "iss-00002": {
            "assurance": "light",
            "branch": "chemitaro/iss-00002",
            "worktrees": [
                {"path": "/w/a", "branch": "chemitaro/iss-00002"},
                {"path": "/w/b", "branch": "iss-00002-second"},
            ],
        },  # the first in the listing's order
        "iss-00003": {"assurance": None, "branch": None, "worktrees": []},  # a Markdown Scope has no level
        "iss-00004": {
            "assurance": None,
            "branch": "iss-00004-x",
            "worktrees": [{"path": "/w/c", "branch": "iss-00004-x"}],
        },
    }


# --- T-03: one listing per request, levels remembered by time and size ---------------------------------------


def test_a_second_request_reuses_the_levels_and_lists_worktrees_again(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path)
    cache = StructureFactsCache()
    reader, lister = Reader(), Lister()
    first = _read(catalog, cache, assurance_reader=reader, worktree_lister=lister)
    assert len(reader.calls) == 2 and lister.calls == 1
    second = _read(catalog, cache, assurance_reader=reader, worktree_lister=lister)
    assert second == first and len(reader.calls) == 2 and lister.calls == 2


def test_a_changed_requirement_is_read_again_alone(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path)
    cache = StructureFactsCache()
    reader = Reader()
    _read(catalog, cache, assurance_reader=reader)
    path = catalog / "00000-00999" / "iss-00002" / "requirement.cue"
    path.write_text("critical")
    os.utime(path, ns=(path.stat().st_atime_ns, path.stat().st_mtime_ns + 1_000_000))
    facts = _read(catalog, cache, assurance_reader=reader)
    assert facts["iss-00002"]["assurance"] == "critical"
    assert reader.calls[2:] == [catalog / "00000-00999" / "iss-00002"]


def test_scopes_not_asked_for_are_forgotten(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path)
    cache = StructureFactsCache()
    reader = Reader()
    _read(catalog, cache, assurance_reader=reader)
    read_structure_facts(
        _site(catalog), ("iss-00002",), cache, assurance_reader=reader, worktree_lister=Lister(), cue_locator=_locate
    )
    assert set(cache.catalogs[str(catalog)]) == {"iss-00002"}


def test_an_unreadable_requirement_is_remembered_until_it_changes(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path)
    (catalog / "00000-00999" / "iss-00002" / "requirement.cue").write_text("broken")
    cache = StructureFactsCache()
    reader = Reader()
    assert _read(catalog, cache, assurance_reader=reader)["iss-00002"]["assurance"] is None
    _read(catalog, cache, assurance_reader=reader)
    assert len(reader.calls) == 2  # read once each: epic-00001 and the broken iss-00002


# --- T-04: failures stay in their field ----------------------------------------------------------------------


def test_failures_leave_only_their_field_empty(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path)

    def raising(directory: Path | None, *, timeout: float, tool: CueTool | None = None) -> AssuranceReading:
        if directory is not None and directory.name == "iss-00002":
            raise OSError("boom")
        return AssuranceReading("standard", "r", "cue")

    failing = Lister(error=GitProcessError(("git",), b"fatal", 128))
    facts = _read(catalog, StructureFactsCache(), assurance_reader=raising, worktree_lister=failing)
    assert facts["epic-00001"] == {"assurance": "standard", "branch": None, "worktrees": []}
    assert facts["iss-00002"] == {"assurance": None, "branch": None, "worktrees": []}


def test_missing_cue_leaves_levels_empty_and_unremembered(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path)
    cache = StructureFactsCache()
    reader = Reader()

    def missing(*, timeout: float) -> Any:
        raise CueToolError("CUE_NOT_FOUND", "cue is not on PATH", exit_code=3, next_step="install cue")

    facts = _read(catalog, cache, assurance_reader=reader, cue_locator=missing)
    assert all(item["assurance"] is None for item in facts.values()) and reader.calls == []
    assert _read(catalog, cache, assurance_reader=reader)["epic-00001"]["assurance"] == "strict"


@pytest.mark.parametrize("catalog_state", ["ambiguous", "missing"])
def test_no_catalog_means_every_field_is_empty(tmp_path: Path, catalog_state: str) -> None:
    catalog = None if catalog_state == "ambiguous" else tmp_path / "nowhere"
    lister = Lister([GitWorktreeRecord(Path("/w/a"), "b", "iss-00002")])
    facts = _read(catalog, StructureFactsCache(), worktree_lister=lister)
    assert all(item == {"assurance": None, "branch": None, "worktrees": []} for item in facts.values())


# --- T-05: the time limit -------------------------------------------------------------------------------------


class Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def test_scopes_past_the_limit_are_empty_and_read_on_the_next_request(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path)
    cache = StructureFactsCache()
    clock = Clock()

    class SlowReader(Reader):
        def __call__(self, directory: Path | None, *, timeout: float, tool: CueTool | None = None) -> AssuranceReading:
            reading = super().__call__(directory, timeout=timeout, tool=tool)
            clock.now += 5.0  # the first read uses up the whole limit
            return reading

    reader = SlowReader()
    facts = _read(catalog, cache, assurance_reader=reader, clock=clock)
    assert facts["epic-00001"]["assurance"] == "strict" and facts["iss-00002"]["assurance"] is None
    assert set(cache.catalogs[str(catalog)]) == {"epic-00001"}
    facts = _read(catalog, cache, assurance_reader=reader, clock=clock)
    assert facts["iss-00002"]["assurance"] == "light"
    assert [path.name for path in reader.calls if path is not None] == ["epic-00001", "iss-00002"]


def test_a_read_that_runs_past_the_limit_unreadable_is_not_remembered(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path)
    cache = StructureFactsCache()
    clock = Clock()

    def timing_out(directory: Path | None, *, timeout: float, tool: CueTool | None = None) -> AssuranceReading:
        clock.now += timeout  # cue stopped by its time limit
        return AssuranceReading(None, None, "unreadable")

    facts = _read(catalog, cache, assurance_reader=timing_out, clock=clock)
    assert facts["epic-00001"]["assurance"] is None and cache.catalogs[str(catalog)] == {}


# --- Through the HTTP API (T-02, T-04) -----------------------------------------------------------------------


class Env:
    def __init__(self, tmp_path: Path) -> None:
        self.state = tmp_path / "state"
        self.catalog = _catalog(tmp_path)
        register(self.state, "github.com/o/r", self.catalog)
        structure = snapshot(
            node(1, "epic"),
            node(2, "issue", parent=1, in_progress=True),
            node(3, "issue", parent=1),
            node(4, "issue", parent=1),
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

    def json(self, path: str) -> tuple[int, Any]:
        response = self.http.handle(Request("GET", path, {}, {"host": HOST}))
        return response.status, json.loads(response.body)


@pytest.fixture
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Env:
    reader = Reader()

    def read(directory: Path | None, *, timeout: float, tool: CueTool | None = None) -> AssuranceReading:
        return reader(directory, timeout=timeout, tool=tool)

    lister = Lister([GitWorktreeRecord(Path("/w/a"), "b", "u/iss-00002")])
    monkeypatch.setattr(details_module, "read_assurance", read)
    monkeypatch.setattr(details_module, "worktree_list", lister)
    monkeypatch.setattr(details_module, "locate_cue", _locate)
    return Env(tmp_path)


def test_the_structure_api_carries_the_levels_and_branches(env: Env) -> None:
    status, body = env.json("/api/v1/r/github.com/o/r/structure")
    assert status == 200
    got = {item["id"]: (item["assurance"], item["branch"]) for item in body["scopes"]}
    assert got == {
        "epic-00001": ("strict", None),
        "iss-00002": ("light", "u/iss-00002"),
        "iss-00003": (None, None),
        "iss-00004": (None, None),
    }


def test_the_scope_api_matches_its_details(env: Env) -> None:
    status, body = env.json("/api/v1/r/github.com/o/r/scopes/iss-00002")
    assert status == 200
    assert body["scope"]["assurance"] == body["details"]["assurance"]["level"] == "light"
    assert body["scope"]["branch"] == body["details"]["worktrees"]["items"][0]["branch"] == "u/iss-00002"
    status, body = env.json("/api/v1/r/github.com/o/r/scopes/iss-00003")
    assert (body["scope"]["assurance"], body["scope"]["branch"]) == (None, None)


def test_the_structure_api_answers_when_every_reader_fails(env: Env, monkeypatch: pytest.MonkeyPatch) -> None:
    def broken(*args: object, **kwargs: object) -> Any:
        raise RuntimeError("boom")

    monkeypatch.setattr(details_module, "read_assurance", broken)
    monkeypatch.setattr(details_module, "worktree_list", broken)
    status, body = env.json("/api/v1/r/github.com/o/r/structure")
    assert status == 200
    assert all(item["assurance"] is None and item["branch"] is None for item in body["scopes"])
