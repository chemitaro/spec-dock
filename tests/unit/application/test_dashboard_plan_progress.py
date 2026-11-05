"""The plan progress of the Issues in progress (iss-00574 T-01, T-02)."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from spec_dock.runtime.application.dashboard_progress import PlanProgressCache, read_plan_progress
from spec_dock.runtime.application.dashboard_site import SiteRepository
from spec_dock.runtime.infra.cue_tool import CueToolError
from spec_dock.runtime.infra.github_structure import GithubRepository
from tests.support.dashboard_site import scope_dir

if TYPE_CHECKING:
    from spec_dock.runtime.infra.cue_tool import CueTool

REPO = GithubRepository("o", "r")
IDS = ("iss-00002", "iss-00003", "iss-00004")
MTIME = datetime(2026, 11, 5, 10, 0, 7, tzinfo=timezone.utc).timestamp()


def _plan(catalog: Path, scope_id: str, steps: dict[str, str] | str) -> Path:
    """The plan file's text is the JSON of `{step: status}` (read by the fake reader), or a marker word."""
    path = scope_dir(catalog, scope_id) / "plan.cue"
    path.write_text(steps if isinstance(steps, str) else json.dumps(steps))
    os.utime(path, (MTIME, MTIME))
    return path


def _catalog(tmp_path: Path) -> Path:
    """iss-00002 has 5 steps (one dropped), iss-00003 a plan with no steps, iss-00004 no plan."""
    catalog = tmp_path / "c"
    _plan(catalog, "iss-00002", {"S-01": "done", "S-02": "done", "S-03": "doing", "S-04": "todo", "S-05": "dropped"})
    _plan(catalog, "iss-00003", {})
    scope_dir(catalog, "iss-00004")
    return catalog


class Reader:
    """Reads the steps written as the file's JSON; "broken" is a plan cue cannot evaluate. Counts the calls."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def __call__(self, directory: Path, *, timeout: float, tool: CueTool | None = None) -> dict[str, object] | None:
        self.calls.append(directory.name)
        assert timeout <= 3.0
        text = (directory / "plan.cue").read_text()
        if text == "broken":
            return None
        return {key: {"title": key, "status": value} for key, value in json.loads(text).items()}


class Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def _locate(*, timeout: float) -> Any:
    return object()


def _read(catalog: Path | None, cache: PlanProgressCache, ids: tuple[str, ...] = IDS, **kwargs: Any) -> dict[str, Any]:
    kwargs.setdefault("steps_reader", Reader())
    kwargs.setdefault("cue_locator", _locate)
    return read_plan_progress(SiteRepository(REPO, catalog, ()), ids, cache, **kwargs)


# --- T-01 ------------------------------------------------------------------------------------------------------


def test_an_issue_in_progress_gets_its_step_counts_and_the_plan_time(tmp_path: Path) -> None:
    progress = _read(_catalog(tmp_path), PlanProgressCache())
    assert progress == {
        "iss-00002": {
            "total": 4,
            "done": 2,
            "doing": 1,
            "todo": 1,
            "dropped": 1,
            "modified_at": "2026-11-05T10:00:07Z",
        },
        "iss-00003": None,  # no steps
        "iss-00004": None,  # no plan.cue
    }


def test_a_second_request_reuses_the_counts_and_a_changed_plan_is_read_again(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path)
    cache = PlanProgressCache()
    reader = Reader()
    _read(catalog, cache, steps_reader=reader)
    assert reader.calls == ["iss-00002", "iss-00003"]
    _read(catalog, cache, steps_reader=reader)
    assert reader.calls == ["iss-00002", "iss-00003"]  # nothing changed: no cue
    _plan(catalog, "iss-00003", {"S-01": "done"})
    os.utime(catalog / "00000-00999" / "iss-00003" / "plan.cue", (MTIME + 60, MTIME + 60))
    progress = _read(catalog, cache, steps_reader=reader)
    assert reader.calls == ["iss-00002", "iss-00003", "iss-00003"]
    assert progress["iss-00003"]["done"] == progress["iss-00003"]["total"] == 1


def test_a_request_without_pruning_keeps_the_other_counts(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path)
    cache = PlanProgressCache()
    reader = Reader()
    _read(catalog, cache, steps_reader=reader)
    _read(catalog, cache, ("iss-00003",), steps_reader=reader, prune=False)  # the detail screen
    _read(catalog, cache, steps_reader=reader)
    assert reader.calls == ["iss-00002", "iss-00003"]
    _read(catalog, cache, ("iss-00003",), steps_reader=reader)  # pruning: the others are dropped
    _read(catalog, cache, steps_reader=reader)
    assert reader.calls == ["iss-00002", "iss-00003", "iss-00002"]


# --- T-02 ------------------------------------------------------------------------------------------------------


def test_an_unreadable_plan_is_none_and_remembered(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path)
    _plan(catalog, "iss-00002", "broken")
    cache = PlanProgressCache()
    reader = Reader()
    assert _read(catalog, cache, steps_reader=reader)["iss-00002"] is None
    _read(catalog, cache, steps_reader=reader)
    assert reader.calls.count("iss-00002") == 1


def test_no_cue_and_an_exception_are_none_and_not_remembered(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path)
    cache = PlanProgressCache()

    def no_cue(*, timeout: float) -> Any:
        raise CueToolError("CUE_NOT_FOUND", "no cue", exit_code=3, next_step="install cue")

    assert all(value is None for value in _read(catalog, cache, cue_locator=no_cue).values())

    def broken(directory: Path, *, timeout: float, tool: CueTool | None = None) -> dict[str, object] | None:
        raise RuntimeError("boom")

    assert all(value is None for value in _read(catalog, cache, steps_reader=broken).values())
    assert _read(catalog, cache)["iss-00002"]["total"] == 4


def test_plans_past_the_limit_are_none_and_read_on_the_next_request(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path)
    cache = PlanProgressCache()
    clock = Clock()

    class Slow(Reader):
        def __call__(self, directory: Path, *, timeout: float, tool: CueTool | None = None) -> dict[str, object] | None:
            found = super().__call__(directory, timeout=timeout, tool=tool)
            clock.now += 5.0
            return found

    reader = Slow()
    progress = _read(catalog, cache, steps_reader=reader, clock=clock)
    assert progress["iss-00002"]["total"] == 4 and reader.calls == ["iss-00002"]
    _read(catalog, cache, steps_reader=reader, clock=clock)
    assert reader.calls == ["iss-00002", "iss-00003"]


def test_a_read_that_runs_past_the_limit_unreadable_is_not_remembered(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path)
    cache = PlanProgressCache()
    clock = Clock()

    def timing_out(directory: Path, *, timeout: float, tool: CueTool | None = None) -> dict[str, object] | None:
        clock.now += timeout
        return None

    assert _read(catalog, cache, steps_reader=timing_out, clock=clock)["iss-00002"] is None
    assert cache.catalogs[str(catalog)] == {}


def test_no_catalog_means_none_for_every_issue(tmp_path: Path) -> None:
    for catalog in (None, tmp_path / "nowhere"):
        assert _read(catalog, PlanProgressCache()) == dict.fromkeys(IDS)


# --- The real cue ----------------------------------------------------------------------------------------------


def test_the_real_cue_reads_the_steps_of_a_plan_alone(tmp_path: Path) -> None:
    from spec_dock.runtime.application.dashboard_progress import read_plan_steps
    from tests.support.cue import cue_executable

    cue_executable()
    directory = scope_dir(tmp_path / "c", "iss-00002")
    (directory / "plan.cue").write_text(
        'package spec\n\nsteps: {\n\t"S-01": {title: "a", realizes: ["R-01"], status: "done"}\n'
        '\t"S-02": {title: "b", realizes: ["R-01"]}\n}\n'
    )
    progress = _read(tmp_path / "c", PlanProgressCache(), ("iss-00002",), steps_reader=read_plan_steps, cue_locator=None)
    assert progress["iss-00002"] is not None
    assert {k: progress["iss-00002"][k] for k in ("total", "done", "todo")} == {"total": 2, "done": 1, "todo": 1}
    (directory / "plan.cue").write_text("package spec\n\nsteps: {\n")  # a syntax error
    assert read_plan_steps(directory, timeout=3.0) is None
