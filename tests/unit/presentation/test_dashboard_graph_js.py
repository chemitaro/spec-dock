"""The structure graph's placement, routing and line check, and the time axis' series, run in node (iss-00532 D-07).

The page's pure modules (`views/graph/layout.js`, `views/graph/router.js`, `views/timeline/series.js`) are loaded by
`tests/js/dashboard_graph_check.mjs` without a DOM. The line check is the adopted prototype's `edgeAudit`: lines
hitting other boxes or their own box, lanes closer than 8px, diagonal segments and ports closer than a lane, plus
runs along the tree's parent lines. On CI node must exist; elsewhere a missing node skips with the reason.
"""

from __future__ import annotations

from itertools import pairwise
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any

import pytest

from tests.support.dashboard import closed, node, snapshot
from tests.support.dashboard_graph import document, document_of, generated, many_lines as generated_many_lines

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
        # iss-00578: many lines from one Issue and into one, across the stage columns
        "many-lines": document(generated_many_lines()),
    }
    return _run(tmp_path_factory.mktemp("graph"), {"documents": documents, "checks": ["audit"]})


def test_every_way_of_showing_the_representative_structures_draws_clean_lines(representative: dict[str, Any]) -> None:
    runs = representative["audit"]
    assert {run["name"] for run in runs} == {"spec-dock", "generated", "generated-15", "generated-18", "many-lines"}
    assert len(runs) >= 5 * 16  # 16 combinations each, and every open Epic or Initiative as the focus
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
    assert len(runs) == 16 + 2 * 8  # and the nested ones at a PC's and a phone's width (iss-00560)
    assert max(run["ms"] for run in runs) < 1000


# --- iss-00578: the passages between columns and rows fit the lines that pass --------------------------------------

# A lane is 8px and each side keeps 10px, so n runs need 8n + 12; a column passage is 44 at least (the column gap), a row
# band 12 (the row gap). 24 more (3 lanes) is the allowance.
_BASE = {"x": 44, "y": 12}
_ALLOWANCE = 24


@pytest.fixture(scope="module")
def many_lines(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    return _run(
        tmp_path_factory.mktemp("many-lines"),
        {"documents": {"many-lines": document(generated_many_lines())}, "checks": ["passages"]},
    )


def _too_wide(runs: list[dict[str, Any]], axis: str) -> list[dict[str, Any]]:
    return [
        {"opts": run["opts"], **p, "bound": max(_BASE[axis], 8 * p["runs"] + 12) + _ALLOWANCE}
        for run in runs
        for p in run["passages"]
        if p["axis"] == axis and p["gap"] > max(_BASE[axis], 8 * p["runs"] + 12) + _ALLOWANCE
    ]


def test_the_passage_between_stage_columns_fits_the_lines_that_pass(many_lines: dict[str, Any]) -> None:
    """Before iss-00578 one passage of this structure was 954px wide for 9 vertical runs."""
    runs = many_lines["passages"]
    assert len(runs) >= 16 + 2 * 8
    assert max(p["runs"] for run in runs for p in run["passages"] if p["axis"] == "x") >= 8  # many lines pass
    assert _too_wide(runs, "x") == []


def test_the_band_between_rows_fits_the_lines_that_pass(many_lines: dict[str, Any]) -> None:
    """Under a box of a row that a tall box makes tall, the band holds the lines into the tall one: a crowded entry side
    takes a port every lane, not every two (iss-00578). Before, one band was 283px for 15 horizontal runs."""
    runs = many_lines["passages"]
    assert max(p["runs"] for run in runs for p in run["passages"] if p["axis"] == "y") >= 8  # many lines pass
    assert _too_wide(runs, "y") == []


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


def _reading(nodes: dict[str, dict[str, Any]], ids: tuple[str, ...]) -> list[str]:
    """The reading order: shelves from the top, left to right on a shelf."""
    return sorted(ids, key=lambda i: (nodes[i]["y1"], nodes[i]["x1"]))


def test_prerequisites_sit_left_and_what_follows_keeps_the_row(small: dict[str, Any]) -> None:
    nodes = _nodes(small, "home")
    assert nodes["iss-00002"]["x2"] < nodes["iss-00003"]["x1"]
    assert nodes["iss-00002"]["y1"] == nodes["iss-00003"]["y1"]
    # iss-00560: 22 and the two waiting for it are one group; one of them keeps 22's row, the other goes below
    assert nodes["iss-00024"]["x1"] == nodes["iss-00025"]["x1"] == nodes["iss-00022"]["x2"] + 44
    assert nodes["iss-00024"]["y1"] == nodes["iss-00022"]["y1"] < nodes["iss-00025"]["y1"]
    # 21 and 23 wait for nothing: groups of their own, after the group of 22 (the recommended order), left to right
    assert _reading(nodes, ("iss-00022", "iss-00021", "iss-00023")) == ["iss-00022", "iss-00021", "iss-00023"]
    assert nodes["iss-00021"]["y1"] == nodes["iss-00023"]["y1"] == nodes["iss-00022"]["y1"]


def test_seven_stages_stay_on_one_row(small: dict[str, Any]) -> None:
    """iss-00556 R-07: the stages no longer wrap after six; they go on to the right."""
    nodes = _nodes(small, "home")
    chain = [nodes[f"iss-{n:05d}"] for n in range(11, 18)]
    assert len({box["y1"] for box in chain}) == 1
    assert all(a["x2"] < b["x1"] for a, b in pairwise(chain))


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
            closed(90, "epic"),  # closed with open children (Epic R-12): its stages count the open ones only
            closed(91, "issue", parent=90),
            node(92, "issue", parent=90, blocked_by=(91,)),
            node(95, "issue", parent=90),
            node(96, "issue", parent=90, blocked_by=(95,)),
        )
    )


def _wide() -> dict[str, Any]:
    """An Epic of twelve Issues without dependencies, and twelve top-level Issues: wider than 1240px each in a row."""
    return document(
        snapshot(
            node(200, "epic"),
            *(node(n, "issue", parent=200) for n in range(201, 213)),
            *(node(n, "issue") for n in range(220, 232)),
        )
    )


def _missing_times() -> dict[str, Any]:
    """Scopes without `active_at` (and a done one without `closed_at`): the oldest in the activity order (F-01)."""
    doc = document(
        snapshot(
            node(100, "initiative"),
            node(101, "epic", parent=100),
            node(102, "issue", parent=101),
            node(103, "epic", parent=100),
            node(104, "issue", parent=103),
            closed(105, "issue", parent=103),
            closed(106, "issue", parent=103, closed_at=_at("10-20")),
        )
    )
    for item in doc["scopes"]:
        if item["id"] in {"epic-00101", "iss-00102", "iss-00105"}:
            item.pop("active_at")
        if item["id"] == "iss-00105":
            item["closed_at"] = None
    return doc


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
            "documents": {"context": _context(), "missing": _missing_times(), "wide": _wide()},
            "layouts": {
                "context": layouts,
                "missing": {"home": {}},
                "wide": {"home": {}, "w1240": {"width": 1240}, "w1400": {"width": 1400}, "w374": {"width": 374}},
            },
            "checks": ["layout", "audit"],
            "prefs": [
                {"current": None, "legacy": None},
                {
                    "current": None,
                    "legacy": {"mode": "tree", "showDone": True, "deps": "wait", "fold": False, "legend": True},
                },
                {
                    "current": {"mode": "nest", "showDone": True, "deps": "wait", "fold": True, "legend": False},
                    "legacy": {"mode": "tree"},
                },
                {
                    "current": {"mode": "box", "showDone": "yes", "deps": "some", "fold": 1, "legend": None},
                    "legacy": None,
                },
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

    assert pairs("home")["iss-00003", "iss-00005"] is True
    assert ("iss-00003", "iss-00005") not in pairs("wait")
    dirty = [run for run in context["audit"] if any(run[key] for key in AUDIT_KEYS)]
    assert dirty == []


def test_frames_follow_activity_and_boxes_put_done_below(context: dict[str, Any]) -> None:
    home = _ids(context, "home")
    roots = ("init-00001", "epic-00020", "epic-00030", "init-00060")
    # iss-00560: the top level is shelves of groups too, read from the top and left to right
    assert _reading(home, roots) == ["init-00001", "epic-00020", "epic-00030", "init-00060"]
    inside = ("epic-00002", "epic-00008", "epic-00012", "epic-00014")
    assert _reading(home, inside) == ["epic-00002", "epic-00014", "epic-00012", "epic-00008"]
    # the finished prerequisite 3 sits left of 5, which waits for it, on its row (stages counting the done ones)
    assert home["iss-00003"]["x2"] < home["iss-00005"]["x1"]
    assert home["iss-00003"]["y1"] == home["iss-00005"]["y1"]
    # the groups in the activity order: open boxes by the recommended order, then the done ones, most recent first
    assert _reading(home, ("iss-00007", "iss-00006", "iss-00004")) == ["iss-00007", "iss-00006", "iss-00004"]
    tree = _ids(context, "tree")
    assert _top_down(tree, roots) == ["init-00001", "epic-00020", "epic-00030", "init-00060"]  # the tree: unchanged
    # a closed parent with open children shows no done child: its dependencies are the open ones, so 92 (waiting
    # only for the done 91) is a group of its own beside the group 95 -> 96 (its open children are cleanup
    # candidates: unfolded)
    unfolded = _ids(context, "unfolded")
    assert "iss-00091" not in unfolded
    assert unfolded["iss-00096"]["x1"] == unfolded["iss-00095"]["x2"] + 44
    assert unfolded["iss-00092"]["x1"] == unfolded["iss-00096"]["x2"] + 14
    assert unfolded["iss-00092"]["y1"] == unfolded["iss-00095"]["y1"] == unfolded["iss-00096"]["y1"]


def test_scopes_without_times_are_the_oldest(context: dict[str, Any]) -> None:
    nodes = {item["id"]: item for item in context["layout"]["missing"]["home"]["nodes"]}
    # epic 101 and its Issue have no time: after epic 103 of the same tier, against the order of the numbers
    reading = sorted(("epic-00101", "epic-00103"), key=lambda i: (nodes[i]["y1"], nodes[i]["x1"]))
    assert reading == ["epic-00103", "epic-00101"]
    # done 105 has neither completion nor activity time: after 106
    done = sorted(("iss-00105", "iss-00106"), key=lambda i: (nodes[i]["y1"], nodes[i]["x1"]))
    assert done == ["iss-00106", "iss-00105"]


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


def test_groups_without_dependencies_wrap_at_the_width_seen(context: dict[str, Any]) -> None:
    """iss-00560 R-02: twelve Issues without dependencies wrap inside their Epic at the width it may use; without a
    width the layout takes 1240px (F-01)."""
    for key, width in (("home", 1240), ("w1240", 1240), ("w1400", 1400), ("w374", 374)):
        nodes = {item["id"]: item for item in context["layout"]["wide"][key]["nodes"]}
        for ids, room in (
            ([f"iss-{n:05d}" for n in range(201, 213)], width - 48 - 24),  # inside an Epic: its 12px sides too
            ([f"iss-{n:05d}" for n in range(220, 232)], width - 48),  # the top level
        ):
            boxes = [nodes[i] for i in ids]
            shelves: dict[float, list[dict[str, Any]]] = {}
            for box in boxes:
                shelves.setdefault(box["y1"], []).append(box)
            assert len(shelves) > 1, key
            for shelf in shelves.values():
                assert max(b["x2"] for b in shelf) - min(b["x1"] for b in shelf) <= room, key
                assert len(shelf) == max(1, (room + 14) // (178 + 14)) or shelf is list(shelves.values())[-1], key
    assert context["layout"]["wide"]["home"]["nodes"] == context["layout"]["wide"]["w1240"]["nodes"]
    assert not [run for run in context["audit"] if run["name"] == "wide" and any(run[key] for key in AUDIT_KEYS)]


# --- iss-00560: what dependencies connect, on one row from left to right ----------------------------------------


def _chains() -> dict[str, Any]:
    """An Initiative like spec-dock's init-00423: 401 -> 402 -> 403 -> 404 (Epics), and beside them 405, also after
    402, more active and wide; 406 and 402 wait for each other through done Issues (a cycle)."""
    return document(
        snapshot(
            node(400, "initiative"),
            closed(401, "epic", parent=400, closed_at=_at("10-20")),
            closed(410, "issue", parent=401, closed_at=_at("10-20")),
            node(402, "epic", parent=400, blocked_by=(401,)),
            node(411, "issue", parent=402),
            closed(414, "issue", parent=402, closed_at=_at("10-25")),
            node(415, "issue", parent=402, blocked_by=(427,)),
            node(403, "epic", parent=400, blocked_by=(402,)),
            node(412, "issue", parent=403),
            node(404, "epic", parent=400, blocked_by=(403,)),
            node(413, "issue", parent=404),
            node(405, "epic", parent=400, blocked_by=(402,)),
            *(node(n, "issue", parent=405, in_progress=n == 420, updated_at=_at("11-03")) for n in range(420, 426)),
            node(406, "epic", parent=400),
            closed(427, "issue", parent=406, closed_at=_at("10-26")),
            node(428, "issue", parent=406, blocked_by=(414,)),
        )
    )


def _crossing() -> dict[str, Any]:
    """One group whose first stage in the activity order (501 first) crosses: 501 -> 503, 501 -> 504, 503 -> 505,
    502 -> 505."""
    return document(
        snapshot(
            node(500, "epic"),
            node(501, "issue", parent=500, in_progress=True, updated_at=_at("11-03")),
            node(502, "issue", parent=500),
            node(503, "issue", parent=500, blocked_by=(501,)),
            node(504, "issue", parent=500, blocked_by=(501,)),
            node(505, "issue", parent=500, blocked_by=(503, 502)),
        )
    )


@pytest.fixture(scope="module")
def rows(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    return _run(
        tmp_path_factory.mktemp("rows"),
        {
            "documents": {"chains": _chains(), "crossing": _crossing()},
            "layouts": {
                "chains": {"home": {}, "w374": {"width": 374}, "done": {"showDone": True}},
                "crossing": {"home": {}},
            },
            "checks": ["layout", "audit", "order"],
        },
    )


def _at_key(result: dict[str, Any], name: str, key: str) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in result["layout"][name][key]["nodes"]}


def test_a_chain_of_epics_stays_on_one_row(rows: dict[str, Any]) -> None:
    for key in ("home", "w374", "done"):
        nodes = _at_key(rows, "chains", key)
        chain = [nodes[f"epic-{n:05d}"] for n in (401, 402, 403, 404)]
        assert len({box["y1"] for box in chain}) == 1, key
        assert all(a["x2"] < b["x1"] for a, b in pairwise(chain)), key
        # what follows 402 and goes on (403) keeps its row; 405, more active but with nothing after it, goes below
        assert nodes["epic-00405"]["y1"] > nodes["epic-00403"]["y2"], key
        # packed: 404 sits one column gap right of 403, not right of the wide 405 on the row below
        assert nodes["epic-00404"]["x1"] == nodes["epic-00403"]["x2"] + 44, key
    home = _at_key(rows, "chains", "home")
    assert home["epic-00405"]["x2"] > home["epic-00404"]["x1"]  # at a PC's width 405 is wider than 403


def test_a_cycle_through_done_issues_keeps_the_chain(rows: dict[str, Any]) -> None:
    """F-02: 402 and 406 wait for each other through done Issues; the one from the older sibling (402 -> 406) stays."""
    nodes = _at_key(rows, "chains", "home")
    assert {f"epic-{n:05d}" for n in range(401, 407)} <= nodes.keys()
    assert nodes["epic-00402"]["x2"] < nodes["epic-00406"]["x1"]
    assert nodes["epic-00406"]["x1"] == nodes["epic-00403"]["x1"]
    pairs = {(p[0], p[1]) for e in rows["layout"]["chains"]["home"]["edges"] for p in e["pairs"]}
    assert {("iss-00427", "iss-00415"), ("iss-00414", "iss-00428")} <= pairs  # both lines are still drawn
    assert not [run for run in rows["audit"] if any(run[key] for key in AUDIT_KEYS)]


def test_reordering_the_first_stage_removes_the_crossing(rows: dict[str, Any]) -> None:
    assert rows["order"]["crossing"]["epic-00500"][:2] == ["iss-00501", "iss-00502"]  # 501 first in the activity order
    nodes = _at_key(rows, "crossing", "home")
    assert nodes["iss-00502"]["y1"] < nodes["iss-00501"]["y1"]
    assert nodes["iss-00505"]["y1"] == nodes["iss-00502"]["y1"]
    row = {i: nodes[i]["y1"] for i in nodes}
    lines = [(p[0], p[1]) for e in rows["layout"]["crossing"]["home"]["edges"] for p in e["pairs"]]
    crossing = [
        (a, b)
        for i, a in enumerate(lines)
        for b in lines[i + 1 :]
        if a[0] != b[0] and a[1] != b[1] and (row[a[0]] - row[b[0]]) * (row[a[1]] - row[b[1]]) < 0
    ]
    assert crossing == []


def test_the_graph_lays_out_again_only_when_the_width_changes() -> None:
    source = (ASSETS / "views" / "graph.js").read_text(encoding="utf-8")
    assert "width: V.width" in source and "seenWidth()" in source
    assert "|${seenWidth()}`" in source  # the width is part of what tells a new layout
    assert "seenWidth() === V.width" in source  # a resize of the height or a zoom keeps the layout
