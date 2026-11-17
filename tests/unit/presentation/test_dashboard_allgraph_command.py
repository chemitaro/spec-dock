"""The cross-repository command lines' pure computation (iss-00617 T-01, T-03), run in node.

`views/allgraph/command.js` maps each worktree of orca-web's summary to a shown repository (a listed path first, then
the project of such a worktree), places each end in that repository's layout or band, or in the band "ほかの場所"
above every frame, decides the frames kept for their band alone, and moves the layouts into the world for
`graph/command.js`'s commandModel. `tests/js/dashboard_allgraph_command.mjs` runs the page's pipeline without a DOM.
Every value is synthetic: no real path, address, session id or name of the user's environment.
"""

from __future__ import annotations

import copy
import json
import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from tests.support.dashboard import closed, node, snapshot
from tests.support.dashboard_graph import document
from tests.unit.presentation.test_dashboard_graph_js import ASSETS, ROOT, _node

if TYPE_CHECKING:
    from pathlib import Path

HARNESS = ROOT / "tests" / "js" / "dashboard_allgraph_command.mjs"
SCHEMA = "orca-web.worktree-summary/v1"
W = 36  # a mark's width
GAP = 2
BAND = {"top": -16, "h": 28, "left": 8, "border": 1, "pad": 6, "gap": 10, "labelGap": 6, "slot": 52}
REPO_BAND = 48
REPO_BAND_TOP = 16
REPO_OTHER = 56
REPO_OTHER_TOP = 16
PAD = 16
OTHER = "ほかの場所"


def run(tmp_path: Path, request: dict[str, Any]) -> dict[str, Any]:
    path = tmp_path / "request.json"
    path.write_text(json.dumps(request), encoding="utf-8")
    result = subprocess.run(
        [_node(), str(HARNESS), str(ASSETS), str(path)], capture_output=True, text=True, timeout=600, check=False
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def key(name: str) -> str:
    return f"github.com/o/{name}"


def ag(agent_id: str, mark: str = "working", parent: str | None = None) -> dict[str, Any]:
    out: dict[str, Any] = {
        "id": agent_id,
        "mark": mark,
        "workingMode": "monitoring" if mark == "working" else None,
        "agentType": "claude",
        "detail": f"/embed/agent?id={agent_id}",
    }
    if parent:
        out["parent"] = {"id": parent, "worktreeId": None}
    return out


def wt(
    worktree_id: str,
    path: str,
    branch: str | None,
    agents: list[dict[str, Any]],
    project: tuple[str, str | None] | None,
    *,
    main: bool = False,
) -> dict[str, Any]:
    return {
        "id": worktree_id,
        "path": path,
        "branch": branch,
        "project": None if project is None else {"id": project[0], "name": project[1]},
        "main": main,
        "agents": agents,
        "counts": {},
    }


def summary(*worktrees: dict[str, Any]) -> dict[str, Any]:
    return {"schema": SCHEMA, "connection": {"state": "connected"}, "worktrees": list(worktrees)}


def _scopes(done: bool = False) -> dict[str, Any]:
    if done:
        return document(snapshot(closed(1, "epic"), closed(2, "issue", parent=1), closed(3, "issue", parent=1)))
    return document(
        snapshot(
            node(1, "epic"),
            node(2, "issue", parent=1),
            node(3, "issue", parent=1, blocked_by=(2,)),
            closed(5, "issue", parent=1),
        )
    )


def structure(
    main: str, records: dict[str, str] | None = None, *, status: str = "ok", done: bool = False
) -> dict[str, Any]:
    """A repository of Epic 1 with Issues 2, 3 (open) and 5 (closed), its main checkout at `main`."""
    doc = copy.deepcopy(_scopes(done))
    records = records or {}
    doc["worktrees"] = {"status": status, "paths": [main, *records.values()]}
    for scope in doc["scopes"]:
        if scope["id"] in records:
            scope["worktrees"] = [{"path": records[scope["id"]], "branch": scope["id"]}]
    return doc


def tall(main: str, last: int, worktree: str) -> dict[str, Any]:
    """A repository of Epic 1 with Issues 2..last (open, no dependency), the last one's worktree at `worktree`."""
    doc = copy.deepcopy(document(snapshot(node(1, "epic"), *(node(n, "issue", parent=1) for n in range(2, last + 1)))))
    doc["worktrees"] = {"status": "ok", "paths": [main, worktree]}
    for scope in doc["scopes"]:
        if scope["id"] == f"iss-{last:05d}":
            scope["worktrees"] = [{"path": worktree, "branch": scope["id"]}]
    return doc


def mark(*ids: str) -> dict[str, Any]:
    return {"items": [W] * len(ids), "gap": GAP, "ids": list(ids)}


PROJ_P = ("p-p", "repo-p")
PROJ_C = ("p-c", "repo-c")
PROJ_X = ("p-x", "repo-x")
REPO_P = {"key": key("p"), "parent": None, "structure": structure("/w/p")}
REPO_C = {
    "key": key("c"),
    "parent": None,
    "structure": structure("/w/c", {"iss-00002": "/w/c-2", "iss-00005": "/w/c-5"}),
}

# a coordinator in p's main checkout directs two agents in c's Issue 2 worktree, which direct each other (one arc)
CROSS = summary(
    wt("wt-p", "/w/p", "main", [ag("a-coord")], PROJ_P, main=True),
    wt("wt-c2", "/w/c-2", "iss-00002", [ag("a-own", parent="a-coord"), ag("a-impl", "waiting", "a-own")], PROJ_C),
)
CROSS_MARKS = {key("c"): {"iss-00002": mark("a-own", "a-impl")}}


def _sc(**kw: Any) -> dict[str, Any]:
    base: dict[str, Any] = {"repos": [REPO_C, REPO_P], "range": "all", "width": 1400}
    return base | kw


SCENARIOS: dict[str, dict[str, Any]] = {
    "cross": _sc(summary=CROSS, marks=CROSS_MARKS),
    # F-03: the marks of c are not measured
    "unmeasured": _sc(summary=CROSS),
    # a worktree in no repository: "ほかの場所"; one without a project; two ends both there; two ends in one band
    "other": _sc(
        summary=summary(
            wt("wt-x", "/x/one", "topic-x", [ag("x-coord")], PROJ_X, main=True),
            wt("wt-n", "/n/one", "topic-n", [ag("n-a", parent="x-coord")], None),
            wt("wt-p", "/w/p", "main", [ag("p-a", parent="x-coord"), ag("p-b", parent="p-a")], PROJ_P, main=True),
        ),
    ),
    # F-02: c is still loading, so the worktree in no repository may be c's: its pairs are not made
    "unknownLoading": _sc(
        repos=[{**REPO_C, "structure": None}, REPO_P],
        summary=summary(
            wt("wt-x", "/x/one", "topic-x", [ag("x-coord")], PROJ_X, main=True),
            wt("wt-p", "/w/p", "main", [ag("p-a", parent="x-coord"), ag("p-b", parent="p-a")], PROJ_P, main=True),
        ),
    ),
    # F-02: c's list of worktrees could not be read
    "unknownStatus": _sc(
        repos=[{**REPO_C, "structure": structure("/w/c", status="unreadable")}, REPO_P],
        summary=summary(
            wt("wt-x", "/x/one", "topic-x", [ag("x-coord")], PROJ_X, main=True),
            wt("wt-p", "/w/p", "main", [ag("p-a", parent="x-coord")], PROJ_P, main=True),
        ),
    ),
    # R-03: e has nothing to show in "next"; its main checkout's coordinator keeps its frame for the band
    "keep": _sc(
        range="next",
        repos=[REPO_C, {"key": key("e"), "parent": None, "structure": structure("/w/e", done=True)}],
        summary=summary(
            wt("wt-e", "/w/e", "main", [ag("e-coord")], ("p-e", "repo-e"), main=True),
            wt("wt-c2", "/w/c-2", "iss-00002", [ag("c-own", parent="e-coord")], PROJ_C),
        ),
        marks={key("c"): {"iss-00002": mark("c-own")}},
    ),
    # R-03: only a child in e: no frame for e, the child in "ほかの場所"
    "childOnly": _sc(
        range="next",
        repos=[REPO_C, {"key": key("e"), "parent": None, "structure": structure("/w/e", done=True)}],
        summary=summary(
            wt("wt-e", "/w/e", "main", [ag("e-child", parent="c-own")], ("p-e", "repo-e"), main=True),
            wt("wt-c2", "/w/c-2", "iss-00002", [ag("c-own")], PROJ_C),
        ),
        marks={key("c"): {"iss-00002": mark("c-own")}},
    ),
    # R-03: e is kept for its coordinator; m (e's parent repository, nothing to show) appears around it, and m's child
    # end stays in m's band
    "keepParent": _sc(
        range="next",
        repos=[
            REPO_C,
            {"key": key("e"), "parent": key("m"), "structure": structure("/w/m/e", done=True)},
            {"key": key("m"), "parent": None, "structure": structure("/w/m", done=True)},
        ],
        summary=summary(
            wt("wt-e", "/w/m/e", "main", [ag("e-coord")], ("p-e", "repo-e"), main=True),
            wt("wt-m", "/w/m", "main", [ag("m-child", parent="e-coord")], ("p-m", "repo-m"), main=True),
        ),
    ),
    # two repositories with the same ids: their frames' ends on one edge are not spread as one edge's
    "sameIds": _sc(
        range="next",
        repos=[
            REPO_C,
            {"key": key("d"), "parent": None, "structure": structure("/w/d", {"iss-00005": "/w/d-5"})},
            REPO_P,
        ],
        summary=summary(
            wt("wt-p", "/w/p", "main", [ag("a-coord")], PROJ_P, main=True),
            wt("wt-c5", "/w/c-5", "iss-00005", [ag("c-five", parent="a-coord")], PROJ_C),
            wt("wt-d5", "/w/d-5", "iss-00005", [ag("d-five", parent="a-coord")], ("p-d", "repo-d")),
        ),
    ),
    # iss-00648 F-02: "ほかの場所" at the world's top directs an agent in a box far below (and one beside the band)
    "deep": _sc(
        repos=[{"key": key("t"), "parent": None, "structure": tall("/w/t", 60, "/w/t-60")}],
        summary=summary(
            wt("wt-x", "/x/one", "topic-x", [ag("x-coord"), ag("x-help", parent="x-coord")], PROJ_X, main=True),
            wt("wt-t60", "/w/t-60", "iss-00060", [ag("t-own", parent="x-coord")], ("p-t", "repo-t")),
        ),
        marks={key("t"): {"iss-00060": mark("t-own")}},
    ),
}


@pytest.fixture(scope="module")
def got(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    return run(tmp_path_factory.mktemp("allcmd"), {"scenarios": SCENARIOS, "key": True})


def _sc_of(got: dict[str, Any], name: str) -> dict[str, Any]:
    return got["scenarios"][name]


def _link(entry: dict[str, Any], link_id: str) -> dict[str, Any]:
    found = [link for link in entry["model"]["links"] if link["id"] == link_id]
    assert len(found) == 1, (link_id, [link["id"] for link in entry["model"]["links"]])
    return found[0]


# --- T-01: the repository of each worktree ------------------------------------------------------------------------


def test_a_listed_path_comes_before_the_project_and_the_first_repository_wins(tmp_path: Path) -> None:
    a = {"key": "a", "structure": {"worktrees": {"status": "ok", "paths": ["/w/a", "/w/both"]}}}
    b = {"key": "b", "structure": {"worktrees": {"status": "ok", "paths": ["/w/b", "/w/b-x", "/w/both/"]}}}
    s = summary(
        wt("wt-a", "/w/a", "main", [], ("p-x", "x"), main=True),
        wt("wt-bx", "/w/b-x", "topic", [], ("p-x", "x")),  # p-x is a's project too: the path wins
        wt("wt-y", "/w/y", "topic", [], ("p-x", "x")),  # no path: the first repository with the project
        wt("wt-both", "/w/both", "topic", [], ("p-z", "z")),  # both list it: the first in the list's order
        wt("wt-none", "/w/none", "topic", [], ("p-q", "q")),
    )
    out = run(tmp_path, {"repoOf": [{"repos": [a, b], "summary": s}, {"repos": [b, a], "summary": s}]})["repoOf"]
    assert out[0] == {"of": {"wt-a": "a", "wt-bx": "b", "wt-y": "a", "wt-both": "a"}, "unknown": False}
    assert out[1] == {"of": {"wt-a": "a", "wt-bx": "b", "wt-y": "b", "wt-both": "b"}, "unknown": False}


def test_a_repository_not_read_or_without_its_worktrees_is_unknown(tmp_path: Path) -> None:
    ok = {"key": "a", "structure": {"worktrees": {"status": "ok", "paths": ["/w/a"]}}}
    s = summary(wt("wt-a", "/w/a", "main", [], ("p-a", "a"), main=True))
    cases = [
        {"repos": [ok], "summary": s},
        {"repos": [ok, {"key": "b", "structure": None}], "summary": s},
        {"repos": [ok, {"key": "b", "structure": {"worktrees": {"status": "unreadable", "paths": []}}}], "summary": s},
        {"repos": [ok], "summary": {"schema": "other", "worktrees": s["worktrees"]}},
    ]
    out = run(tmp_path, {"repoOf": cases})["repoOf"]
    assert [o["unknown"] for o in out] == [False, True, True, False]
    assert out[1]["of"] == {"wt-a": "a"} and out[2]["of"] == {"wt-a": "a"}
    assert out[3]["of"] == {}


# --- T-01: the places, the rows and the frames kept -----------------------------------------------------------------


def test_a_line_across_two_repositories(got: dict[str, Any]) -> None:
    sc = _sc_of(got, "cross")
    assert sc["of"] == {"wt-p": key("p"), "wt-c2": key("c")}
    assert sc["pairs"] == sc["allPairs"] == [["a-own", "a-impl"], ["a-coord", "a-own"]]
    assert sc["places"]["a-coord"] == {"kind": "band", "repo": key("p"), "row": key("p"), "key": "wt-p"}
    assert sc["places"]["a-own"] == {
        "kind": "mark",
        "repo": key("c"),
        "row": None,
        "id": "iss-00002",
        "scope": "iss-00002",
    }
    assert sc["rows"] == {
        key("p"): [{"key": "wt-p", "label": "main のチェックアウト", "own": True, "main": True, "agents": ["a-coord"]}]
    }
    assert sc["keep"] == []
    assert [link["kind"] for link in sc["model"]["links"]] == ["arc", "curve"]


def test_the_ends_of_a_line_across_repositories_are_their_bodies_origins_plus_the_layout(got: dict[str, Any]) -> None:
    sc = _sc_of(got, "cross")
    fc = sc["comp"]["frames"][key("c")]
    fp = sc["comp"]["frames"][key("p")]
    spot = next(s for s in sc["spots"][key("c")]["iss-00002"] if s["id"] == "a-own")
    box = sc["nodes"][key("c")]["iss-00002"]
    link = _link(sc, "a-coord>a-own")
    # the child's end: right above its mark on the top of its box, moved by c's body origin (iss-00648 D-01)
    assert link["to"] == {"x": fc["body"]["x"] + spot["x"] + spot["w"] / 2, "y": fc["body"]["y"] + box["y1"]}
    # the parent's end: the top of its slot's item in p's band row, below p's heading
    row = sc["model"]["band"]["rows"][0]
    assert row["key"] == key("p")
    assert row["left"] == fp["x1"] + PAD and row["top"] == fp["band"]["y1"] + REPO_BAND_TOP
    slot = row["items"][0]["agents"][0]
    assert link["from"] == {"x": slot["x"] + slot["w"] / 2, "y": row["top"]}
    assert row["items"][0]["y"] == row["top"]
    # the hop of one box: both marks moved by the same origin, on the box's top, no stub
    arc = _link(sc, "a-own>a-impl")
    assert arc["kind"] == "arc"
    assert arc["from"]["y"] == arc["to"]["y"] == fc["body"]["y"] + box["y1"]
    mids = [fc["body"]["x"] + s["x"] + s["w"] / 2 for s in sc["spots"][key("c")]["iss-00002"]]
    assert [arc["from"]["x"], arc["to"]["x"]] == mids
    assert arc["stubs"] == [] and link["stubs"] == []


def test_the_band_moves_the_body_down_and_widens_nothing_narrow(got: dict[str, Any]) -> None:
    sc = _sc_of(got, "cross")
    a = sc["plain"]["frames"][key("p")]
    b = sc["comp"]["frames"][key("p")]
    assert b["band"]["y2"] - b["band"]["y1"] == REPO_BAND
    assert b["body"]["y"] - b["y1"] == a["body"]["y"] - a["y1"] + REPO_BAND
    assert sc["shape"]["bands"] == {key("p"): {"h": REPO_BAND, "w": sc["shape"]["bands"][key("p")]["w"]}}
    item = sc["model"]["band"]["rows"][0]["items"][0]
    assert sc["shape"]["bands"][key("p")]["w"] == item["w"] + 2 * PAD
    assert sc["shape"]["other"] is None and sc["comp"]["other"] is None
    assert sc["shapeAgain"] is True
    # c has no band: its frame is the same size
    pc, cc = sc["plain"]["frames"][key("c")], sc["comp"]["frames"][key("c")]
    assert (pc["y2"] - pc["y1"], pc["x2"] - pc["x1"]) == (cc["y2"] - cc["y1"], cc["x2"] - cc["x1"])


def test_a_worktree_in_no_repository_goes_to_the_other_places_band(got: dict[str, Any]) -> None:
    sc = _sc_of(got, "other")
    assert sc["of"] == {"wt-p": key("p")}
    assert sorted(sc["pairs"]) == sorted(sc["allPairs"])
    assert sc["places"]["x-coord"] == {"kind": "band", "repo": None, "row": "", "key": "wt-x"}
    assert sc["places"]["n-a"]["row"] == ""
    assert sc["places"]["p-a"]["row"] == sc["places"]["p-b"]["row"] == key("p")
    labels = {it["key"]: it["label"] for it in sc["rows"][""]}
    assert labels == {"wt-x": "repo-x · topic-x", "wt-n": "ほかのリポジトリ · topic-n"}
    assert all(not it["own"] for it in sc["rows"][""])
    # both ends in "ほかの場所", both ends in p's band: arcs or curves, all drawn
    assert {link["id"] for link in sc["model"]["links"]} == {"x-coord>n-a", "x-coord>p-a", "p-a>p-b"}
    assert _link(sc, "p-a>p-b")["kind"] == "arc"


def test_the_other_places_band_sits_above_every_frame_with_its_lead(got: dict[str, Any]) -> None:
    sc = _sc_of(got, "other")
    other = sc["comp"]["other"]
    assert other["y1"] == 8 and other["y2"] - other["y1"] == REPO_OTHER
    for k in (key("p"), key("c")):
        assert sc["comp"]["frames"][k]["y1"] == sc["plain"]["frames"][k]["y1"] + REPO_OTHER
    assert sc["comp"]["height"] == sc["plain"]["height"] + REPO_OTHER + REPO_BAND
    row = next(r for r in sc["model"]["band"]["rows"] if r["key"] == "")
    assert row["lead"] == OTHER and row["top"] == other["y1"] + REPO_OTHER_TOP and row["left"] == other["x1"] + PAD
    assert row["items"][0]["x"] == row["left"] + row["leadWidth"] + BAND["labelGap"]
    assert sc["shape"]["other"]["h"] == REPO_OTHER
    lead = row["leadWidth"] + BAND["labelGap"]
    items = sum(it["w"] for it in row["items"]) + BAND["gap"] * (len(row["items"]) - 1)
    assert sc["shape"]["other"]["w"] == lead + items + 2 * PAD


@pytest.mark.parametrize("name", ["unknownLoading", "unknownStatus"])
def test_while_a_repository_is_unknown_no_end_goes_to_the_other_places(got: dict[str, Any], name: str) -> None:
    sc = _sc_of(got, name)
    assert sc["unknown"] is True
    assert all(p[0] != "x-coord" for p in sc["pairs"])
    assert "" not in sc["rows"] and sc["comp"]["other"] is None
    if name == "unknownLoading":
        assert sc["pairs"] == [["p-a", "p-b"]]  # the pair of known ends stays


def test_a_repository_with_nothing_shown_is_kept_for_its_coordinator(got: dict[str, Any]) -> None:
    sc = _sc_of(got, "keep")
    assert key("e") not in sc["visible"]
    assert sc["keep"] == [key("e")] and sc["shape"]["keep"] == [key("e")]
    f = sc["comp"]["frames"][key("e")]
    assert f["body"]["kind"] in {"quiet", "empty"} and f["body"]["h"] == 0
    assert f["band"]["y2"] - f["band"]["y1"] == REPO_BAND
    assert sc["places"]["e-coord"]["row"] == key("e")
    assert [link["id"] for link in sc["model"]["links"]] == ["e-coord>c-own"]


def test_a_repository_with_nothing_shown_and_only_a_child_is_not_kept(got: dict[str, Any]) -> None:
    sc = _sc_of(got, "childOnly")
    assert sc["keep"] == [] and key("e") not in sc["comp"]["frames"]
    assert sc["places"]["e-child"] == {"kind": "band", "repo": key("e"), "row": "", "key": "wt-e"}
    assert [it["label"] for it in sc["rows"][""]] == ["repo-e · main"]
    assert sc["comp"]["other"] is not None


def test_the_parent_repository_of_a_kept_frame_keeps_its_childs_end(got: dict[str, Any]) -> None:
    sc = _sc_of(got, "keepParent")
    assert sc["keep"] == [key("e")]
    assert set(sc["comp"]["order"]) >= {key("m"), key("e")}
    assert sc["places"]["m-child"]["row"] == key("m")
    assert sc["comp"]["other"] is None
    assert {r["key"] for r in sc["model"]["band"]["rows"]} == {key("e"), key("m")}


def test_frames_of_the_same_id_in_two_repositories_are_not_one_edge(got: dict[str, Any]) -> None:
    sc = _sc_of(got, "sameIds")
    assert sc["places"]["c-five"]["kind"] == sc["places"]["d-five"]["kind"] == "frame"
    # the world's copies of the two frames epic-00001 have keys of their own repository
    assert sorted(sc["frameKeys"]["epic-00001"]) == sorted([
        f"{key('c')}\nepic-00001",
        f"{key('d')}\nepic-00001",
        f"{key('p')}\nepic-00001",
    ])
    for agent, repo in (("c-five", key("c")), ("d-five", key("d"))):
        link = _link(sc, f"a-coord>{agent}")
        f = sc["comp"]["frames"][repo]["body"]
        n = sc["nodes"][repo]["epic-00001"]
        x1, y1, x2, y2 = f["x"] + n["x1"], f["y"] + n["y1"], f["x"] + n["x2"], f["y"] + n["y2"]
        # the middle of the upper edge: not moved along it by a spread with the other repository's frame
        assert link["to"] == {"x": (x1 + x2) / 2, "y": y1}, (agent, link["to"], (x1, y1, x2, y2))


def test_hops_from_the_other_places_band_stay_below_the_ceiling(got: dict[str, Any]) -> None:
    """iss-00648 T-01 / F-02: crossModel passes ceiling 4: the hop to a box 500px or more below peaks at 4 - 0.5 or
    lower, and the band item's own hop as well."""
    sc = _sc_of(got, "deep")
    link = _link(sc, "x-coord>t-own")
    assert link["kind"] == "curve"
    assert link["to"]["y"] - link["from"]["y"] >= 500
    assert link["from"]["y"] - 56 < 4  # without the ceiling it would rise above the world
    assert link["peak"] >= 4 - 0.5 and link["peak"] == pytest.approx(4, abs=0.5)
    own = _link(sc, "x-coord>x-help")
    assert own["kind"] == "arc" and own["peak"] >= 4 - 0.5
    assert all(link["peak"] >= 4 - 0.5 for link in sc["model"]["links"])


# --- T-03: the world's model ------------------------------------------------------------------------------------------


def test_the_synthetic_inputs_have_no_overlap(got: dict[str, Any]) -> None:
    for name, sc in got["scenarios"].items():
        assert sc["model"]["audit"]["boxOverlaps"] == 0, name
        assert sc["model"]["audit"]["edgeOverlaps"] == 0, name


def test_unmeasured_marks_end_on_the_edge_and_make_no_arc(got: dict[str, Any]) -> None:
    sc = _sc_of(got, "unmeasured")
    assert [link["id"] for link in sc["model"]["links"]] == ["a-coord>a-own"]
    fc = sc["comp"]["frames"][key("c")]["body"]
    box = sc["nodes"][key("c")]["iss-00002"]
    assert _link(sc, "a-coord>a-own")["to"] == {"x": fc["x"] + (box["x1"] + box["x2"]) / 2, "y": fc["y"] + box["y1"]}


def test_without_a_band_row_in_the_frames_the_band_ends_are_not_drawn(got: dict[str, Any]) -> None:
    # F-05's limit: the frames composed without the band have no row for p's coordinator
    sc = _sc_of(got, "cross")
    assert sc["flat"] == {"links": 0, "band": False}


def test_band_row_width(tmp_path: Path) -> None:
    out = run(
        tmp_path,
        {
            "rowWidth": [
                [[{"label": "main", "agents": 1}], None],
                [[{"label": "main", "agents": 1}, {"label": "ab", "agents": 2}], None],
                [[{"label": "main", "agents": 1}], OTHER],
            ]
        },
    )["rowWidth"]
    # border 2, padding 12, labelWidth("main") = ceil(4 * 6.6) = 27, labelGap 6, one slot 52
    assert out[0] == 2 + 12 + 27 + 6 + 52
    assert out[1] == out[0] + BAND["gap"] + (2 + 12 + 24 + 6 + 104)  # labelWidth("ab") is at least 24
    assert out[2] == out[0] + 58 + BAND["labelGap"]  # labelWidth("ほかの場所") = ceil(5 * 11.5) = 58


def test_command_model_rows_place_the_items_after_the_lead_and_end_at_the_rows_bottom(tmp_path: Path) -> None:
    layout = {
        "nodes": [{"type": "box", "id": "b1", "x1": 100, "y1": 300, "x2": 278, "y2": 388, "rows": 2}],
        "width": 2000,
        "height": 2000,
    }
    rc = {
        "layout": layout,
        "pairs": [
            ["o1", "o2", {"o1": {"band": "k-o"}, "o2": {"band": "k-o"}}],
            ["o1", "c1", {"o1": {"band": "k-o"}, "c1": {"band": "k-r"}}],
        ],
        "rows": [
            {
                "key": "",
                "left": 24,
                "top": 24,
                "lead": OTHER,
                "items": [{"key": "k-o", "label": "x · y", "agents": ["o1", "o2"]}],
            },
            {
                "key": "r",
                "left": 40,
                "top": 140,
                "lead": None,
                "items": [{"key": "k-r", "label": "main", "agents": ["c1"]}],
            },
        ],
    }
    out = run(tmp_path, {"rows": [rc]})["rows"][0]
    band = out["band"]
    assert band["top"] == 24 and out["top"] == min(0, *(link["peak"] - 6 for link in out["links"]))
    first, second = band["rows"]
    assert (
        first["leadWidth"] == 58
        and first["items"][0]["x"] == 24 + 58 + BAND["labelGap"]
        and first["items"][0]["y"] == 24
    )
    assert second["items"][0]["x"] == 40 and second["items"][0]["y"] == 140
    arc = next(link for link in out["links"] if link["id"] == "o1>o2")
    assert arc["kind"] == "arc" and arc["from"]["y"] == 24 and arc["to"]["y"] == 24
    curve = next(link for link in out["links"] if link["id"] == "o1>c1")
    assert curve["from"]["y"] == 24 and curve["to"]["y"] == 140  # iss-00648 D-01: the items' upper edges
    assert band["right"] == max(it["x"] + it["w"] for r in band["rows"] for it in r["items"])


def test_bounds_of_limit_a_hops_height_above_a_box(tmp_path: Path) -> None:
    node_ = {"type": "box", "id": "b1", "x1": 100, "y1": 300, "x2": 278, "y2": 388, "rows": 2}
    base = {
        "layout": {"nodes": [node_], "width": 2000, "height": 2000},
        "pairs": [["m1", "m2", {"m1": {"mark": "b1"}, "m2": {"mark": "b1"}}]],
        "rows": [],
        "marks": {"b1": mark("m1", "m2")},
    }
    out = run(tmp_path, {"rows": [base, base | {"bounds": {"x1": 0, "y1": 300 - 13, "x2": 2000, "y2": 2000}}]})["rows"]
    free, bounded = out[0]["links"][0], out[1]["links"][0]
    assert free["bulge"] == 18 and bounded["bulge"] == 10  # 13px of room: 13 - 3


def test_placer_gives_place_agents_places(tmp_path: Path) -> None:
    s = structure("/w/c", {"iss-00002": "/w/c-2", "iss-00005": "/w/c-5"})
    sm = summary(
        wt("wt-c", "/w/c", "main", [ag("a-coord")], PROJ_C, main=True),
        wt("wt-c2", "/w/c-2", "iss-00002", [ag("a-own", parent="a-coord")], PROJ_C),
        wt("wt-c5", "/w/c-5", "iss-00005", [ag("a-five", parent="a-coord")], PROJ_C),
    )
    out = run(tmp_path, {"placer": [{"structure": s, "summary": sm, "layout": {"mode": "nest", "range": "next"}}]})[
        "placer"
    ][0]
    assert out["same"] is True and out["count"] == 3
    assert {p["kind"] for p in out["places"].values()} == {"band", "mark", "frame"}


def test_the_key_is_the_same_for_the_same_inputs(got: dict[str, Any]) -> None:
    k = got["key"]
    assert k["same"] and k["copied"] and k["withoutCompSame"]
    for name in (
        "otherSummary",
        "otherEg",
        "otherStructure",
        "otherMarks",
        "otherIds",
        "otherComp",
        "otherVisible",
        "withoutComp",
    ):
        assert k[name] is False, name
