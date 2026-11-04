"""The structure graph's placement, routing and line check, and the time axis' series, run in node (iss-00532 D-07).

The page's pure modules (`views/graph/layout.js`, `views/graph/router.js`, `views/timeline/series.js`) are loaded by
`tests/js/dashboard_graph_check.mjs` without a DOM. The line check is the adopted prototype's `edgeAudit`: lines
hitting other boxes or their own box, lanes closer than 8px, diagonal segments and ports closer than a lane, plus
runs along the tree's parent lines. On CI node must exist; elsewhere a missing node skips with the reason.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any

import pytest

from tests.support.dashboard import closed, node, snapshot
from tests.support.dashboard_graph import document, document_of, generated

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "src" / "spec_dock" / "assets" / "dashboard"
CHECK = ROOT / "tests" / "js" / "dashboard_graph_check.mjs"
SNAPSHOT = ROOT / "tests" / "fixtures" / "issue532" / "spec-dock-snapshot.json"
AUDIT_KEYS = ("boxHits", "ownHits", "overlaps", "diagonal", "portShare", "trunkOverlaps", "failed")


def _node() -> str:
    found = shutil.which("node")
    if found is None:
        if os.environ.get("CI"):
            pytest.fail("node is required on CI for the structure graph check (iss-00532)")
        pytest.skip("node is not installed: the structure graph check runs the page's JavaScript in node")
    return found


def _run(tmp_path: Path, request: dict[str, Any]) -> dict[str, Any]:
    path = tmp_path / "request.json"
    path.write_text(json.dumps(request), encoding="utf-8")
    result = subprocess.run(
        [_node(), str(CHECK), str(ASSETS), str(path)], capture_output=True, text=True, timeout=300, check=False
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def _small() -> dict[str, Any]:
    return document(
        snapshot(
            node(1, "epic"),
            node(2, "issue", parent=1),
            node(3, "issue", parent=1, blocked_by=(2,)),
            closed(5, "issue", parent=1),
            closed(6, "epic"),  # closed with an open child: stays, the child is a cleanup candidate
            node(7, "issue", parent=6),
            node(8, "epic"),  # open with every child closed: a cleanup candidate
            closed(9, "issue", parent=8),
            node(10, "epic"),  # seven stages in a row
            *(node(n, "issue", parent=10, blocked_by=((n - 1,) if n > 11 else ())) for n in range(11, 18)),
            node(20, "epic"),
            node(21, "issue", parent=20),
            node(22, "issue", parent=20),
            node(23, "issue", parent=20),
            node(24, "issue", parent=20, blocked_by=(22,)),
            node(25, "issue", parent=20, blocked_by=(22,)),
            node(30, "epic"),
            closed(31, "issue", parent=30),
            node(32, "issue", parent=30, blocked_by=(31,)),
            node(33, "issue", parent=30),
            node(34, "issue", parent=30, blocked_by=(33,)),
        )
    )


@pytest.fixture(scope="module")
def representative(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    documents = {
        "spec-dock": document_of(json.loads(SNAPSHOT.read_text(encoding="utf-8"))),
        "generated": document(generated()),
        # With 8 rounds that return the last round, both keep lanes too close in some ways of showing (iss-00544).
        "generated-15": document(generated(seed=15)),
        "generated-18": document(generated(seed=18)),
    }
    return _run(tmp_path_factory.mktemp("graph"), {"documents": documents, "checks": ["audit"]})


def test_every_way_of_showing_the_representative_structures_draws_clean_lines(representative: dict[str, Any]) -> None:
    runs = representative["audit"]
    assert {run["name"] for run in runs} == {"spec-dock", "generated", "generated-15", "generated-18"}
    assert len(runs) >= 4 * 16  # 16 combinations each, and every open Epic or Initiative as the focus
    assert sum(run["edges"] for run in runs if run["name"] == "spec-dock" and run["opts"]["deps"] == "all") > 100
    dirty = [
        {
            "name": run["name"],
            "opts": run["opts"],
            **{key: run[key] for key in AUDIT_KEYS if run[key]},
            "list": run["list"],
        }
        for run in runs
        if any(run[key] for key in AUDIT_KEYS)
    ]
    assert dirty == []


def test_the_250_scope_structure_routes_within_a_second(representative: dict[str, Any]) -> None:
    runs = [run for run in representative["audit"] if run["name"] == "generated" and not run["opts"].get("focus")]
    assert len(runs) == 16
    assert max(run["ms"] for run in runs) < 1000


@pytest.fixture(scope="module")
def small(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    layouts = {
        "home": {},
        "unfolded": {"fold": False},
        "done": {"showDone": True},
        "tree": {"mode": "tree"},
        "focus": {"focus": "epic-00001"},
        "wait": {"showDone": True, "deps": "wait"},
        "all": {"showDone": True, "deps": "all"},
        "none": {"showDone": True, "deps": "none"},
    }
    doc = _small()
    return {
        "doc": doc,
        **_run(
            tmp_path_factory.mktemp("small"),
            {
                "documents": {"small": doc},
                "layouts": {"small": layouts},
                "checks": ["layout", "series"],
            },
        ),
    }


def _nodes(result: dict[str, Any], key: str) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in result["layout"]["small"][key]["nodes"]}


def test_prerequisites_sit_left_and_a_stage_keeps_the_recommended_order(small: dict[str, Any]) -> None:
    nodes = _nodes(small, "home")
    assert nodes["iss-00002"]["x2"] < nodes["iss-00003"]["x1"]
    # 22 has two waiting Scopes: first in the first stage of epic 20, then 21 and 23 by number
    first = sorted((nodes[i] for i in ("iss-00021", "iss-00022", "iss-00023")), key=lambda item: item["y1"])
    assert [item["id"] for item in first] == ["iss-00022", "iss-00021", "iss-00023"]
    assert nodes["iss-00024"]["x1"] == nodes["iss-00025"]["x1"] > nodes["iss-00022"]["x2"]


def test_seven_stages_wrap_onto_a_second_row(small: dict[str, Any]) -> None:
    nodes = _nodes(small, "home")
    assert nodes["iss-00011"]["x1"] < nodes["iss-00016"]["x1"]  # six columns in the first row
    assert nodes["iss-00017"]["x1"] == nodes["iss-00011"]["x1"]
    assert nodes["iss-00017"]["y1"] > nodes["iss-00011"]["y2"]


def test_home_hides_done_keeps_closed_parents_and_folds_cleanup(small: dict[str, Any]) -> None:
    home = small["layout"]["small"]["home"]
    nodes = _nodes(small, "home")
    # iss-00556: a done Issue under an open Epic stays (5); one under an Epic folded as a cleanup candidate (9)
    # belongs to the folded group's Epic and is not drawn on its own
    assert "iss-00005" in nodes and "iss-00009" not in nodes
    assert nodes["epic-00006"]["type"] == "frame"  # closed, but its open child keeps it
    folded = {item_id for group in home["groups"] for item_id in group["ids"]}
    assert folded == {"iss-00007", "epic-00008"}
    assert "epic-00008" not in nodes
    unfolded = _nodes(small, "unfolded")
    assert {"iss-00007", "epic-00008"} <= unfolded.keys()
    assert small["layout"]["small"]["unfolded"]["groups"] == []
    assert "iss-00005" in _nodes(small, "done")


def test_the_tree_shows_every_scope_as_a_box_with_parent_lines(small: dict[str, Any]) -> None:
    tree = small["layout"]["small"]["tree"]
    nodes = _nodes(small, "tree")
    assert tree["groups"] == [] and tree["trunks"] > 0
    assert {"epic-00008", "iss-00007"} <= nodes.keys()
    assert {item["type"] for item in nodes.values()} == {"box", "tframe"}
    assert nodes["iss-00002"]["x1"] > nodes["epic-00001"]["x1"]  # indented under its parent
    assert nodes["iss-00002"]["y1"] > nodes["epic-00001"]["y2"]


def test_focus_shows_only_the_scope_and_its_descendants(small: dict[str, Any]) -> None:
    focus = small["layout"]["small"]["focus"]
    assert focus["focus"] == "epic-00001"
    assert set(_nodes(small, "focus")) == {"epic-00001", "iss-00002", "iss-00003", "iss-00005"}


def test_the_three_dependency_line_choices(small: dict[str, Any]) -> None:
    def pairs(key: str) -> dict[tuple[str, str], bool]:
        return {(p[0], p[1]): e["done"] for e in small["layout"]["small"][key]["edges"] for p in e["pairs"]}

    wait, every, none = pairs("wait"), pairs("all"), pairs("none")
    assert ("iss-00031", "iss-00032") not in wait
    assert every["iss-00031", "iss-00032"] is True  # a finished dependency: drawn dashed
    assert every["iss-00033", "iss-00034"] is False
    assert set(wait) < set(every)
    assert none == {}


def test_weeks_of_the_chosen_kinds_add_up(small: dict[str, Any]) -> None:
    series = small["series"]["small"]
    weeks = small["doc"]["timeline"]["weeks_by_kind"]
    assert series["none"] == []
    assert series["issue"] == weeks["issue"]
    last = series["all"][-1]
    assert last["created"] == sum(week[-1]["created"] for week in weeks.values() if week)
    assert last["closed"] == sum(week[-1]["closed"] for week in weeks.values() if week)
    assert [week["week_start"] for week in series["all"]] == sorted({
        w["week_start"] for k in weeks.values() for w in k
    })


def test_recent_events_are_grouped_by_day_newest_first(small: dict[str, Any]) -> None:
    groups = small["series"]["small"]["groups"]
    events = [item for group in groups for item in group["items"]]
    assert [item["at"] for item in events] == sorted((item["at"] for item in events), reverse=True)
    assert len({group["day"] for group in groups}) == len(groups)
    assert all(item["scope"]["id"] == item["scope_id"] for item in events)


# --- iss-00556: the plan's context in the default view, the activity order, the saved choices --------------------


def _at(day: str) -> str:
    return f"2026-{day}T00:00:00Z"


def _context() -> dict[str, Any]:
    return document(
        snapshot(
            node(1, "initiative", updated_at=_at("10-26")),
            node(2, "epic", parent=1),  # doing inside: first among the Initiative's frames
            closed(3, "issue", parent=2, closed_at=_at("10-28"), updated_at=_at("10-28")),
            closed(4, "issue", parent=2, closed_at=_at("10-31"), updated_at=_at("10-31")),
            node(5, "issue", parent=2, blocked_by=(3,)),  # waits for a finished Issue: a done line
            node(6, "issue", parent=2),
            node(7, "issue", parent=2, in_progress=True, updated_at=_at("11-03")),
            closed(8, "epic", parent=1, closed_at=_at("10-29"), updated_at=_at("10-29")),  # a folded frame
            closed(9, "issue", parent=8, closed_at=_at("10-27")),  # its parent is done: hidden
            closed(10, "epic", closed_at=_at("11-02")),  # no parent: hidden
            closed(11, "issue", parent=10, closed_at=_at("11-01")),
            node(12, "epic", parent=1),
            node(13, "issue", parent=12, updated_at=_at("10-27")),
            node(14, "epic", parent=1),  # ready inside, moved later than 12: above 12
            node(15, "issue", parent=14, updated_at=_at("11-01")),
            node(20, "epic"),
            node(21, "issue", parent=20, in_progress=True, updated_at=_at("10-30")),
            node(30, "epic"),
            node(31, "issue", parent=30),
            node(60, "initiative"),  # only a blocked Epic inside
            node(61, "epic", parent=60, blocked_by=(30,)),
            node(80, "epic"),  # open with every child closed: a cleanup candidate, not the context of its children
            closed(81, "issue", parent=80, closed_at=_at("10-20")),
            closed(82, "issue", parent=80, closed_at=_at("10-21")),
        )
    )


@pytest.fixture(scope="module")
def context(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    layouts = {
        "home": {},
        "tree": {"mode": "tree"},
        "wait": {"deps": "wait"},
        "done": {"showDone": True},
        "focus8": {"focus": "epic-00008"},
        "unfolded": {"fold": False},
        "focus80": {"focus": "epic-00080"},
    }
    return _run(
        tmp_path_factory.mktemp("context"),
        {
            "documents": {"context": _context()},
            "layouts": {"context": layouts},
            "checks": ["layout", "audit"],
            "prefs": [
                {"current": None, "legacy": None},
                {"current": None, "legacy": {"mode": "tree", "showDone": True, "deps": "wait", "fold": False, "legend": True}},
                {"current": {"mode": "nest", "showDone": True, "deps": "wait", "fold": True, "legend": False}, "legacy": {"mode": "tree"}},
                {"current": {"mode": "box", "showDone": "yes", "deps": "some", "fold": 1, "legend": None}, "legacy": None},
                {"current": [1, 2], "legacy": "x"},
            ],
        },
    )


def _ids(result: dict[str, Any], key: str) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in result["layout"]["context"][key]["nodes"]}


def _top_down(nodes: dict[str, dict[str, Any]], ids: tuple[str, ...]) -> list[str]:
    return [item["id"] for item in sorted((nodes[i] for i in ids), key=lambda item: item["y1"])]


def test_the_default_view_keeps_done_scopes_under_open_parents(context: dict[str, Any]) -> None:
    for key in ("home", "tree"):
        nodes = _ids(context, key)
        assert {"iss-00003", "iss-00004", "epic-00008"} <= nodes.keys(), key
        assert not {"iss-00009", "epic-00010", "iss-00011"} & nodes.keys(), key
    home = _ids(context, "home")
    assert home["epic-00008"]["type"] == "frame"
    folded = context["layout"]["context"]["home"]
    assert folded["nodes"] and all(item["id"] != "iss-00009" for item in folded["nodes"])
    assert {"iss-00009", "epic-00010", "iss-00011"} <= _ids(context, "done").keys()
    assert "iss-00009" in _ids(context, "focus8")  # narrowed to a done Epic: its children show
    # the done children of an open Epic whose every child is done (a cleanup candidate) are not shown, folded or not
    for key in ("tree", "unfolded"):
        nodes = _ids(context, key)
        assert "epic-00080" in nodes and not {"iss-00081", "iss-00082"} & nodes.keys(), key
    assert {"iss-00081", "iss-00082"} <= _ids(context, "focus80").keys()


def test_the_default_view_draws_finished_dependencies_between_shown_boxes(context: dict[str, Any]) -> None:
    def pairs(key: str) -> dict[tuple[str, str], bool]:
        return {(p[0], p[1]): e["done"] for e in context["layout"]["context"][key]["edges"] for p in e["pairs"]}

    assert pairs("home")[("iss-00003", "iss-00005")] is True
    assert ("iss-00003", "iss-00005") not in pairs("wait")
    dirty = [run for run in context["audit"] if any(run[key] for key in AUDIT_KEYS)]
    assert dirty == []


def test_frames_follow_activity_and_boxes_put_done_below(context: dict[str, Any]) -> None:
    home = _ids(context, "home")
    roots = ("init-00001", "epic-00020", "epic-00030", "init-00060")
    assert _top_down(home, roots) == ["init-00001", "epic-00020", "epic-00030", "init-00060"]
    inside = ("epic-00002", "epic-00008", "epic-00012", "epic-00014")
    order = sorted(inside, key=lambda i: (home[i]["y1"], home[i]["x1"]))
    assert order == ["epic-00002", "epic-00014", "epic-00012", "epic-00008"]
    # the finished prerequisite 3 sits in the stage left of 5, which waits for it (stages counting the done ones)
    assert home["iss-00003"]["x2"] < home["iss-00005"]["x1"]
    first = ("iss-00003", "iss-00004", "iss-00006", "iss-00007")
    assert len({home[i]["x1"] for i in first}) == 1
    assert _top_down(home, first) == ["iss-00007", "iss-00006", "iss-00004", "iss-00003"]
    tree = _ids(context, "tree")
    assert _top_down(tree, roots) == ["init-00001", "epic-00020", "epic-00030", "init-00060"]


def test_saved_choices_of_the_old_version_do_not_override_the_new_defaults(context: dict[str, Any]) -> None:
    empty, legacy, current, broken, junk = context["prefs"]
    defaults = {"mode": "nest", "showDone": False, "deps": "all", "fold": True}
    assert empty == {"opts": defaults, "legend": False}
    assert legacy == {"opts": {**defaults, "mode": "tree", "fold": False}, "legend": True}
    assert current == {"opts": {**defaults, "showDone": True, "deps": "wait"}, "legend": False}
    assert broken == {"opts": defaults, "legend": False}
    assert junk == {"opts": defaults, "legend": False}


def test_the_graph_saves_its_choices_under_the_new_key() -> None:
    source = (ASSETS / "views" / "graph.js").read_text(encoding="utf-8")
    assert '"specdock.graph.v1"' not in source
    assert "restorePrefs" in source and "PREFS_KEY" in source and "LEGACY_KEY" in source
