"""The cross-repository structure screen, `views/allgraph.js`, in node with a stand-in DOM (iss-00614 T-05 to T-07).

`tests/js/dashboard_allgraph_screen.mjs` renders the screen with stub API answers (synthetic structures of nine
repositories in the shape this PC has), presses its buttons and boxes, runs its 5-second refresh, and returns what
each repository frame drew, what the panel shows, what was fetched and what the browser storage holds.
"""

from __future__ import annotations

from dataclasses import replace
import json
import re
import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from tests.support.dashboard import closed, node, snapshot
from tests.support.dashboard_graph import document, scope_of
from tests.unit.presentation.test_dashboard_graph_js import ASSETS, ROOT, _node

if TYPE_CHECKING:
    from pathlib import Path

HARNESS = ROOT / "tests" / "js" / "dashboard_allgraph_screen.mjs"
CSS = ASSETS / "views" / "allgraph.css"
KEY = "specdock.allgraph.v1"
V3 = "specdock.graph.v3"
NONE = "これから進める Scope は、どのリポジトリにもありません。全体で、終わったものを見られます。"
EMPTY = "表示しているリポジトリがありません。`spec-dock dashboard list` で確かめてください。"
# The second item is a 0.9.5 server's `tier`: the screen must not draw it (iss-00635 F-01).
SHAPE = {
    "company-os": (None, []),
    "housing-lifecycle": ("company-os", ["事業"]),
    "taikyohiyou_project": ("housing-lifecycle", ["プロダクト"]),
    "input-devices": ("company-os", ["事業"]),
    "generic-mona": ("input-devices", ["プロダクト"]),
    "tenting-cradle": ("input-devices", ["プロダクト"]),
    "yubisaki": ("input-devices", ["プロダクト", "groups"]),
    "spec-dock": (None, []),
    "orca-web": (None, []),
}


def key(name: str) -> str:
    return f"github.com/o/{name}"


def repos() -> list[dict[str, Any]]:
    out = []
    for name, (parent, tier) in sorted(SHAPE.items(), key=lambda kv: key(kv[0])):
        out.append({
            "repository": key(name),
            "host": "github.com",
            "owner": "o",
            "name": name,
            "path": f"/r/{key(name)}/",
            "api": f"/api/v1/r/{key(name)}",
            "problem": None,
            "parent": key(parent) if parent else None,
            "tier": tier,
        })
    return out


def doc_of(name: str, *nodes: Any, revision: str = "r1") -> dict[str, Any]:
    structure = replace(snapshot(*nodes), repository=key(name))
    return document(structure) | {"revision": revision}


def _open() -> tuple[Any, ...]:
    return (
        node(1, "epic"),
        node(2, "issue", parent=1),
        node(3, "issue", parent=1, blocked_by=(2,)),
        closed(4, "issue", parent=1),
        node(5, "issue", in_progress=True),
    )


DONE = (closed(1, "epic"), closed(2, "issue", parent=1), closed(3, "issue"))


def docs() -> dict[str, Any]:
    unreadable = doc_of("yubisaki", *DONE)
    unreadable["snapshot"] = {**unreadable["snapshot"], "status": "unreadable"}
    return {
        key("company-os"): doc_of("company-os", *DONE),
        key("housing-lifecycle"): doc_of("housing-lifecycle", *DONE),
        key("taikyohiyou_project"): doc_of("taikyohiyou_project", *_open()),
        key("input-devices"): doc_of("input-devices"),
        key("generic-mona"): doc_of("generic-mona", *DONE),
        key("tenting-cradle"): {"status": 500, "message": "boom"},
        key("yubisaki"): unreadable,
        key("spec-dock"): doc_of("spec-dock", *_open(), node(6, "issue", blocked_by=(5,))),
        key("orca-web"): doc_of("orca-web", *DONE),
    }


def scope_docs() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for name, nodes in (("spec-dock", (*_open(), node(6, "issue", blocked_by=(5,)))), ("taikyohiyou_project", _open())):
        structure = replace(snapshot(*nodes), repository=key(name))
        out[key(name)] = {s.id: scope_of(structure, s.id) for s in structure.issues.values() if s.id}
    return out


def _run(tmp_path: Path, runs: list[dict[str, Any]]) -> dict[str, Any]:
    path = tmp_path / "request.json"
    path.write_text(json.dumps({"runs": runs}), encoding="utf-8")
    result = subprocess.run(
        [_node(), str(HARNESS), str(ASSETS), str(path)], capture_output=True, text=True, timeout=600, check=False
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)["runs"]


def base(name: str, **extra: Any) -> dict[str, Any]:
    return {"name": name, "repos": repos(), "docs": docs(), "scopes": scope_docs(), "saved": None, **extra}


def frames(shot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {r["key"]: r for r in shot["repos"]}


def pressed_range(shot: dict[str, Any]) -> str:
    found = re.findall(r'data-act="range" data-range="(\w+)" aria-pressed="true"', shot["tools"])
    assert len(found) == 1, shot["tools"]
    return found[0]


def chip(shot: dict[str, Any], hl: str) -> int:
    m = re.search(rf'data-hl="{hl}"[^>]*>.*?<b>(\d+)</b>', shot["next"])
    assert m, hl
    return int(m.group(1))


SHOWN_NEXT = [
    "company-os",
    "housing-lifecycle",
    "taikyohiyou_project",
    "input-devices",
    "tenting-cradle",
    "spec-dock",
]  # yubisaki's unreadable snapshot is in the page's summary (iss-00632 R-02): nothing keeps its frame in next


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    box = '[data-repo="{}"] .ax-body .gx-box[data-id="{}"]'
    head = '[data-repo="{}"] .ax-body .gx-fh[data-id="{}"]'
    sd, tk = key("spec-dock"), key("taikyohiyou_project")
    return _run(
        tmp_path_factory.mktemp("allgraph"),
        [
            base(
                "plain",
                saved={V3: json.dumps({"mode": "tree", "range": "all"})},
                steps=[
                    {"act": "range", "range": "all"},
                    {"act": "range", "range": "now"},
                    {"remount": True},
                    {"act": "range", "range": "next"},
                ],
            ),
            base("saved-all", saved={KEY: json.dumps({"range": "all"})}),
            base("broken", saved={KEY: "{not json"}),
            base("outside", saved={KEY: json.dumps({"range": "everything"})}),
            {"name": "none", "repos": repos(), "docs": {key(n): doc_of(n, *DONE) for n in SHAPE}, "saved": None},
            {"name": "nothing", "repos": [], "docs": {}, "saved": None},
            base(
                "select",
                orca={sd: {"iss-00002": [60]}, tk: {}},
                steps=[
                    {"tap": box.format(sd, "iss-00002")},
                    {"news": True},
                    {"tap": head.format(sd, "epic-00001")},
                    {"click": '.panel [data-act="focus"]'},
                    {"dbl": box.format(tk, "iss-00003")},
                    {"key": "Escape"},
                    {"hl": "ready"},
                ],
            ),
            base("embed", embed=True, steps=[{"tap": box.format(sd, "iss-00002")}]),
            base(
                "refresh",
                steps=[
                    {"tick": 3},
                    {"set": {"revisions": {sd: "r2"}, "docs": {sd: doc_of("spec-dock", *_open(), revision="r2")}}},
                    {"tick": 1},
                    {"tick": 2},
                ],
            ),
            base(
                "rows",
                orca={sd: {}},
                steps=[
                    {"orca": {sd: {"iss-00002": [80, 80, 80]}}},
                    {"news": True},
                    {"orca": {sd: {"iss-00002": [80, 80, 80], "iss-00003": [70, 70]}}},
                ],
            ),
        ],
    )


# --- T-05 ---------------------------------------------------------------------------------------------------------


def test_next_is_the_default_and_the_range_is_kept_in_its_own_key(out: dict[str, Any]) -> None:
    plain = out["plain"]["shots"]
    assert pressed_range(plain[0]) == "next"
    assert plain[0]["screen"] == "allgraph"
    assert plain[0]["saved"] == {V3: json.dumps({"mode": "tree", "range": "all"})}
    assert pressed_range(plain[1]) == "all"
    assert json.loads(plain[1]["saved"][KEY]) == {"range": "all"}
    assert pressed_range(plain[2]) == "now" and json.loads(plain[2]["saved"][KEY]) == {"range": "now"}
    assert pressed_range(plain[3]) == "now"  # drawn again from the kept choice
    for shot in plain:
        assert shot["saved"][V3] == json.dumps({"mode": "tree", "range": "all"})  # the graph's key is untouched
    assert pressed_range(out["saved-all"]["shots"][0]) == "all"
    assert pressed_range(out["broken"]["shots"][0]) == "next"
    assert pressed_range(out["outside"]["shots"][0]) == "next"


def test_the_frames_are_flat_in_the_world_nested_by_depth_with_names_only(out: dict[str, Any]) -> None:
    shot = out["plain"]["shots"][1]  # all
    assert [r["key"] for r in shot["repos"]] == [
        key(n)
        for n in (
            "company-os",
            "housing-lifecycle",
            "taikyohiyou_project",
            "input-devices",
            "generic-mona",
            "tenting-cradle",
            "yubisaki",
            "orca-web",
            "spec-dock",
        )
    ]
    f = frames(shot)
    assert f[key("company-os")]["depth"] == "0" and f[key("input-devices")]["depth"] == "1"
    assert f[key("yubisaki")]["depth"] == "2"
    assert "o/housing-lifecycle" in f[key("housing-lifecycle")]["head"]
    assert "o/company-os" in f[key("company-os")]["head"]
    # The heading is the name and the link only, though the list still carries a tier (iss-00635 R-02, F-01).
    for name in SHAPE:
        frame = f[key(name)]
        assert "sd-badge" not in frame["headHtml"] and "ax-tier" not in frame["headHtml"], name
        for word in ("事業", "プロダクト", "groups", " › "):
            assert word not in frame["head"], (name, word)
        assert f"o/{name}" in frame["head"], name
        assert f'href="/r/github.com/o/{name}/"' in frame["headHtml"], name
    assert 'href="/r/github.com/o/yubisaki/"' in f[key("yubisaki")]["headHtml"]
    # every frame is placed by its own style
    assert all(re.fullmatch(r"left:\d+px;top:\d+px;width:\d+px;height:\d+px", r["style"]) for r in shot["repos"])


def test_next_shows_only_what_has_something_and_the_containers(out: dict[str, Any]) -> None:
    shot = out["plain"]["shots"][0]
    assert [r["key"] for r in shot["repos"]] == [key(n) for n in SHOWN_NEXT]
    f = frames(shot)
    for n in ("company-os", "housing-lifecycle", "input-devices"):
        assert f[key(n)]["ids"] == [], n  # containers: no graph
        assert f[key(n)]["body"] is None or f[key(n)]["body"]["text"] is None, n
    assert f[key("spec-dock")]["ids"]
    # all and now show every frame; no Scope and nothing shown say so on one line
    for i in (1, 2):
        g = frames(out["plain"]["shots"][i])
        assert set(g) == {key(n) for n in SHAPE}
        assert g[key("input-devices")]["body"]["text"] == "Scope はまだありません"
    assert frames(out["plain"]["shots"][2])[key("company-os")]["body"]["text"] == "この範囲で見せる Scope はありません"


def test_a_frame_holds_what_its_graph_would_show_in_the_same_range(out: dict[str, Any]) -> None:
    run = out["plain"]
    for shot, range_ in ((run["shots"][0], "next"), (run["shots"][1], "all"), (run["shots"][2], "now")):
        for r in shot["repos"]:
            if r["key"] in run["alone"] and r["ids"]:
                assert sorted(r["ids"]) == run["alone"][r["key"]][range_], (r["key"], range_)
    assert run["alone"][key("spec-dock")]["next"]


def test_a_failed_repository_says_why_in_its_frame_and_the_shared_kinds_go_to_the_summary(out: dict[str, Any]) -> None:
    shot = out["plain"]["shots"][0]
    f = frames(shot)
    failed = f[key("tenting-cradle")]
    assert [w["level"] for w in failed["warn"]] == ["error"]
    assert "このリポジトリを読めませんでした（boom）。" in failed["warn"][0]["text"]
    assert "spec-dock dashboard list" in failed["warn"][0]["text"]
    assert "spec-dock dashboard list" in failed["warn"][0]["title"]
    # the unreadable snapshot (a readable repository with Scopes) and the unknown pull requests are summarised once
    rows = shot["sum"]["rows"]
    assert not shot["sum"]["hidden"] and shot["sum"]["inLeft"]
    assert [(r["kind"], r["level"]) for r in rows] == [("snapshot-unreadable", "error"), ("pr-unknown", "info")]
    assert rows[0]["text"].startswith("構造のスナップショットが読めません：yubisaki")
    assert "spec-dock canonical status" in rows[0]["text"]
    assert rows[1]["text"].startswith("PR の状態が分かりません：company-os、generic-mona、housing-lifecycle")
    assert "tenting-cradle" not in rows[1]["text"]
    for r in shot["repos"]:
        assert all("PR の状態" not in w["text"] and "スナップショット" not in w["text"] for w in r["warn"]), r["key"]


def test_the_two_notices(out: dict[str, Any]) -> None:
    none = out["none"]["shots"][0]
    assert none["repos"] == [] and not none["none"]["hidden"] and none["none"]["text"] == NONE
    assert none["bar"] and none["view"]
    nothing = out["nothing"]["shots"][0]
    assert not nothing["empty"]["hidden"] and nothing["empty"]["text"] == EMPTY
    assert not nothing["bar"] and not nothing["view"]


def test_the_css_adds_no_colour_and_places_the_parts_inside_a_frame() -> None:
    css = CSS.read_text(encoding="utf-8")
    body = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", body)
    assert "rgb(" not in body and "hsl(" not in body and "rgba(" not in body
    assert not re.search(r"(^|[;{\s])--[a-zA-Z0-9-]+\s*:", body)  # no custom property of its own
    assert re.search(r"\.ax-body > \.gx-box[^{]*\{[^}]*position: absolute", body)
    assert ".ax-body > .gx-clean" in body and ".ax-body > .gx-frame" in body
    assert '.main[data-view="allgraph"]' in body
    panel = (ASSETS / "views" / "_shared" / "panel.css").read_text(encoding="utf-8")
    assert re.search(r'\[data-view="allgraph"\][^{]*\{[^}]*--pn-w', body + panel)
    for selector in (".ax-repo", ".ax-head", ".ax-warn", ".ax-body", ".ax-line", ".ax-sum"):
        assert selector in body, selector
    # iss-00632 R-03: only the summary's rows take the pointer; the rest of the bar's column lets it through to the graph
    assert re.search(r'\.gx\[data-screen="allgraph"\] \.gx-left \{[^}]*pointer-events: none', body)
    assert re.search(r'\.gx\[data-screen="allgraph"\] \.gx-next \{[^}]*pointer-events: auto', body)
    assert re.search(r"\.gx \.ax-sum \{[^}]*pointer-events: none", body)
    assert re.search(r"\.gx \.ax-sum li \{[^}]*pointer-events: auto", body)
    assert re.search(r"\.gx \.ax-sum li \{[^}]*width: fit-content", body)
    assert re.search(r"\.gx \.ax-sum li \{[^}]*max-width: 100%", body)


def test_the_screen_module_and_its_styles() -> None:
    source = (ASSETS / "views" / "allgraph.js").read_text(encoding="utf-8")
    for css in ("parts.css", "scope_tabs.css", "panel.css", "graph.css", "allgraph.css"):
        assert css in source, css
    assert "markSeen" not in source and "/seen" not in source
    assert 'from "./allgraph/compose.js"' in source and 'from "./graph/draw.js"' in source


# --- T-06 ---------------------------------------------------------------------------------------------------------


def test_a_box_selects_in_its_own_repository_and_the_panel_keeps_that_context(out: dict[str, Any]) -> None:
    shots = out["select"]["shots"]
    sd, tk = key("spec-dock"), key("taikyohiyou_project")
    tapped = shots[1]
    assert f"GET /api/v1/r/{sd}/scopes/iss-00002" in tapped["calls"]
    assert not any(c.startswith(f"GET /api/v1/r/{tk}/scopes") for c in tapped["calls"])
    f = frames(tapped)
    assert "is-sel" in f[sd]["classes"].get("iss-00002", "")
    assert "is-sel" not in f[tk]["classes"].get("iss-00002", "")
    assert all("is-poff" in c for c in f[tk]["classes"].values()) and f[tk]["classes"]  # the other frames fade
    assert "has-path" in tapped["worldClass"]
    assert tapped["panel"]["open"]
    detail = next(a for a in tapped["panel"]["foot"] if a["label"] == "詳しい画面")
    assert detail["href"].startswith(f"/r/{sd}/scopes/iss-00002")
    assert tapped["panel"]["marks"] == 1  # the panel's heading reads that repository's structure
    # orca-web's news redraws the panel from current(): still the same repository and structure
    again = shots[2]
    assert again["panel"]["marks"] == 1
    assert next(a for a in again["panel"]["foot"] if a["label"] == "詳しい画面")["href"].startswith(
        f"/r/{sd}/scopes/iss-00002"
    )
    # a frame's heading, and its "focus" goes to that repository's graph
    frame = shots[3]
    assert "is-sel" in frames(frame)[sd]["classes"].get("epic-00001", "")
    assert any(a["act"] == "focus" and a["focus"] == "epic-00001" for a in frame["panel"]["foot"])
    assert shots[4]["navigated"] == [f"/r/{sd}/?focus=epic-00001"]
    assert shots[5]["navigated"] == [f"/r/{tk}/scopes/iss-00003"]  # a double click opens the detail screen
    # the lines: only the selected repository's lines take the path's classes
    assert any("is-p1" in c or "is-off" in c for c in frames(tapped)[sd]["edgeClasses"])
    assert not any("is-p1" in c or "is-p2" in c or "is-off" in c for c in frames(tapped)[tk]["edgeClasses"])
    # Escape lets go
    assert not shots[6]["panel"]["open"] and "has-path" not in shots[6]["worldClass"]


def test_the_embedded_panel_keeps_embed(out: dict[str, Any]) -> None:
    tapped = out["embed"]["shots"][1]
    detail = next(a for a in tapped["panel"]["foot"] if a["label"] == "詳しい画面")
    assert detail["href"].startswith(f"/r/{key('spec-dock')}/scopes/iss-00002") and "embed=1" in detail["href"]


def test_the_state_chips_count_every_shown_frame_and_highlight_in_all(out: dict[str, Any]) -> None:
    shot = out["select"]["shots"][0]
    all_docs = docs()
    shown = [r["key"] for r in shot["repos"]]
    expect: dict[str, int] = {"ready": 0, "blocked": 0, "doing": 0}
    for k in shown:
        for s in all_docs[k].get("scopes", []):
            open_issue = s["kind"] == "issue" and s["state"] != "done"
            if open_issue and s.get("merge") not in ("mergeable", "needs_fix") and s.get("lane") in expect:
                expect[s["lane"]] += 1
    assert expect["ready"] >= 2
    for lane, n in expect.items():
        assert chip(shot, lane) == n, lane
    lit = out["select"]["shots"][7]
    hl = {k: [i for i, c in r["classes"].items() if "is-hl" in c] for k, r in frames(lit).items()}
    assert hl[key("spec-dock")] and hl[key("taikyohiyou_project")]


def test_the_agents_marks_only_in_the_repository_with_the_worktree(out: dict[str, Any]) -> None:
    f = frames(out["select"]["shots"][0])
    assert f[key("spec-dock")]["marks"] == 1
    assert f[key("taikyohiyou_project")]["marks"] == 0


# --- T-07 ---------------------------------------------------------------------------------------------------------


def test_refreshing_reads_the_revisions_and_lays_out_only_what_changed(out: dict[str, Any]) -> None:
    shots = out["refresh"]["shots"]
    first = shots[0]["stats"]
    loaded = [c for c in shots[0]["calls"] if "/structure" in c]
    assert len(loaded) == 9 and first["loads"] == 9
    ticked = shots[1]
    assert ticked["stats"]["layouts"] == first["layouts"]
    assert not [c for c in ticked["calls"] if "/structure" in c]
    assert len([c for c in ticked["calls"] if c.endswith("/revision")]) >= 3 * 8
    changed = shots[3]
    assert [c for c in changed["calls"] if "/structure" in c] == [f"GET /api/v1/r/{key('spec-dock')}/structure"]
    assert changed["stats"]["layouts"] == first["layouts"] + 1
    assert changed["stats"]["repos"][key("spec-dock")]["layouts"] == first["repos"][key("spec-dock")]["layouts"] + 1
    assert shots[4]["stats"]["layouts"] == changed["stats"]["layouts"]
    for run in out.values():
        for shot in run["shots"]:
            assert not [c for c in shot["calls"] if c.startswith("POST") or "/seen" in c]
    assert out["refresh"]["intervals"] == 0 and out["refresh"]["audit"] == "gone"  # dispose stops and forgets


def test_the_rows_of_agents_lay_out_only_their_repository_again(out: dict[str, Any]) -> None:
    shots = out["rows"]["shots"]
    sd = key("spec-dock")
    per = [s["stats"]["repos"] for s in shots]
    others = [k for k in per[0] if k != sd]
    # three marks of 80px are two rows of agents in a 152px box: spec-dock alone is laid out again, once
    assert per[1][sd]["layouts"] == per[0][sd]["layouts"] + 1
    assert all(per[1][k]["layouts"] == per[0][k]["layouts"] for k in others)
    # the same marks again: the rows agree, nothing is laid out
    assert per[2][sd]["layouts"] == per[1][sd]["layouts"]
    # more marks on another box: at most twice per news
    assert per[1][sd]["layouts"] < per[3][sd]["layouts"] <= per[1][sd]["layouts"] + 2
    assert frames(shots[3])[sd]["marks"] == 5


def test_the_line_check_reports_every_repository(out: dict[str, Any]) -> None:
    audit = out["plain"]["shots"][1]["audit"]
    assert audit is not None
    assert key("spec-dock") in audit["repos"] and key("taikyohiyou_project") in audit["repos"]
    for name in ("boxHits", "ownHits", "overlaps", "diagonal", "portShare", "failed", "missing", "markOverflow"):
        assert name in audit["total"], name


def test_fit_holds_a_world_that_needs_less_than_the_graphs_least_zoom(tmp_path: Path) -> None:
    """R-07: 'fit' shows every frame even when that takes a zoom below the structure graph's 0.02 (iss-00614)."""
    view = {"width": 300, "height": 120, "bar": 50}
    run = base("tiny", view=view, saved={KEY: json.dumps({"range": "all"})}, steps=[{"act": "fit"}])
    shot = _run(tmp_path, [run])["tiny"]["shots"][1]
    width, height = (float(v.removesuffix("px")) for v in shot["size"])
    top = view["bar"] + 8
    fit = min(1, (view["width"] - 16) / width, (view["height"] - top - 16) / height)
    assert fit < 0.02, (width, height)
    m = re.fullmatch(r"translate\(([-\d.e]+)px, ([-\d.e]+)px\) scale\(([-\d.e]+)\)", shot["transform"])
    assert m, shot["transform"]
    tx, ty, s = (float(x) for x in m.groups())
    assert s == pytest.approx(fit)
    assert tx >= 0 and tx + width * s <= view["width"] + 1e-6
    assert ty >= top and ty + height * s <= view["height"] + 1e-6


def test_the_screen_has_no_tier() -> None:
    """iss-00635 R-02: no tier badge in the screen's style or code (the list API's parent alone nests the frames)."""
    assert "ax-tier" not in CSS.read_text(encoding="utf-8")
    js = (ASSETS / "views" / "allgraph.js").read_text(encoding="utf-8")
    assert "ax-tier" not in js
    assert re.search(r"\btier\b", js) is None


# --- iss-00629 T-03: the first view fits the width and follows the world until the reader moves it ----------------

PC_VIEW = {"width": 1440, "height": 900, "bar": 50}


def _chain(n: int) -> tuple[Any, ...]:
    """An Initiative of n issues blocked one after another: a graph wider than the graph area."""
    return (
        node(1, "epic"),
        *(node(i, "issue", parent=1, blocked_by=(i - 1,) if i > 2 else ()) for i in range(2, n + 2)),
    )


def _done_chain(n: int) -> tuple[Any, ...]:
    return (
        closed(1, "epic"),
        *(closed(i, "issue", parent=1, blocked_by=(i - 1,) if i > 2 else ()) for i in range(2, n + 2)),
    )


def _wide_docs() -> dict[str, Any]:
    # spec-dock is wider than the area in every range; orca-web's finished chain widens all further
    return docs() | {
        key("spec-dock"): doc_of("spec-dock", *_chain(10)),
        key("orca-web"): doc_of("orca-web", *_done_chain(20)),
    }


def _t(shot: dict[str, Any]) -> tuple[float, float, float]:
    m = re.fullmatch(r"translate\(([-\d.e]+)px, ([-\d.e]+)px\) scale\(([-\d.e]+)\)", shot["transform"])
    assert m, shot["transform"]
    tx, ty, s = (float(x) for x in m.groups())
    return tx, ty, s


def _world(shot: dict[str, Any]) -> float:
    return float(shot["size"][0].removesuffix("px"))


@pytest.fixture(scope="module")
def first(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    phone = {"width": 390, "height": 800, "bar": 50}
    styled = {"styled": True, "hold": True, "view": PC_VIEW, "width": 1440}
    return _run(
        tmp_path_factory.mktemp("first"),
        [
            base("wide", docs=_wide_docs(), steps=[{"release": True}], **styled),
            base("narrow", steps=[{"release": True}], **styled),
            base("phone", docs=_wide_docs(), steps=[{"release": True}], **(styled | {"view": phone, "width": 390})),
            base(
                "range",
                docs=_wide_docs(),
                saved={KEY: json.dumps({"range": "now"})},
                steps=[{"release": True}, {"act": "range", "range": "all"}],
                **styled,
            ),
            base(
                "moved",
                docs=_wide_docs(),
                saved={KEY: json.dumps({"range": "now"})},
                steps=[{"release": True}, {"act": "zin"}, {"act": "range", "range": "all"}, {"tick": 1}],
                **styled,
            ),
        ],
    )


def _fits(shot: dict[str, Any]) -> None:
    tx, ty, s = _t(shot)
    width = _world(shot)
    assert s == pytest.approx(min(1, (PC_VIEW["width"] - 16) / width)), (width, s)
    assert tx == 8 and ty == PC_VIEW["bar"] + 8
    assert tx + width * s <= PC_VIEW["width"] - 8 + 1e-6


def test_the_first_view_on_a_pc_fits_a_wide_world_to_the_width(first: dict[str, Any]) -> None:
    loading, arrived = first["wide"]["shots"]
    _fits(loading)
    # the structures arrive after the first draw: the scale follows the wider world (not the loading world's 1)
    assert _world(arrived) > PC_VIEW["width"], arrived["size"]
    _fits(arrived)
    assert _t(arrived)[2] < 1


def test_the_first_view_of_a_narrow_world_is_at_100_percent_from_the_left(first: dict[str, Any]) -> None:
    shot = first["narrow"]["shots"][-1]
    assert _world(shot) <= PC_VIEW["width"] - 16, shot["size"]
    assert _t(shot) == (8, PC_VIEW["bar"] + 8, 1)


def test_the_first_view_on_a_phone_stays_as_the_structure_graphs(first: dict[str, Any]) -> None:
    for shot in first["phone"]["shots"]:
        tx, ty, s = _t(shot)
        assert (tx, s) == (4, 0.74) and ty == 50 + 8


def test_a_new_range_fits_again_until_the_reader_moves_and_then_keeps_the_view(first: dict[str, Any]) -> None:
    now, all_ = first["range"]["shots"][1:]
    assert _world(now) != _world(all_)
    _fits(now)
    _fits(all_)
    arrived, zoomed, ranged, ticked = first["moved"]["shots"][1:]
    _fits(arrived)
    assert _t(zoomed)[2] == pytest.approx(_t(arrived)[2] * 1.25)
    assert _world(ranged) != _world(zoomed)
    assert _t(ranged) == _t(zoomed) == _t(ticked)


# --- iss-00632 T-03, T-04: the notices' summary ------------------------------------------------------------------

STALE = {"status": "ok", "fetched_at": "2026-11-04T11:50:00Z", "age_seconds": 3 * 3600, "stale": True, "detail": None}
PR_OK = {"status": "ok", "fetched_at": "2026-11-04T11:50:00Z", "error": None}


def _quiet(doc: dict[str, Any]) -> dict[str, Any]:
    return doc | {"notices": [], "pull_requests": PR_OK}


def _notice_docs() -> dict[str, Any]:
    out = {k: (_quiet(d) if "scopes" in d else d) for k, d in docs().items()}
    out[key("yubisaki")] = _quiet(doc_of("yubisaki", *DONE))
    for name in ("company-os", "housing-lifecycle", "orca-web"):
        out[key(name)] = out[key(name)] | {"snapshot": STALE}
    out[key("spec-dock")] = out[key("spec-dock")] | {
        "pull_requests": {"status": "unknown", "fetched_at": None, "error": None}
    }
    # no Scope and an unreadable snapshot: the screen cannot draw it (failed), its frame tells why
    empty = _quiet(doc_of("generic-mona"))
    out[key("generic-mona")] = empty | {"snapshot": {**empty["snapshot"], "status": "unreadable", "age_seconds": 7200}}
    return out


@pytest.fixture(scope="module")
def notices(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    quiet = {k: _quiet(doc_of(n, *DONE)) for n in SHAPE for k in [key(n)]}
    styled = {"styled": True, "hold": True, "width": 1440}
    return _run(
        tmp_path_factory.mktemp("notices"),
        [
            base("notices", docs=_notice_docs()),
            base("quiet", docs=quiet),
            base("summed", steps=[{"release": True}], view=PC_VIEW | {"sum": 90}, **styled),
            base(
                "summed-phone",
                steps=[{"release": True}],
                view={"width": 390, "height": 800, "bar": 50, "sum": 90},
                **(styled | {"width": 390}),
            ),
        ],
    )


def test_one_row_per_kind_names_the_repositories_and_no_frame_repeats_it(notices: dict[str, Any]) -> None:
    shot = notices["notices"]["shots"][0]  # next
    rows = shot["sum"]["rows"]
    assert [(r["kind"], r["level"]) for r in rows] == [("stale", "warning"), ("pr-unknown", "info")]
    stale, pr = rows
    assert stale["text"].startswith(
        "構造が更新されていません：company-os（3時間）、housing-lifecycle（3時間）、orca-web（3時間）"
    )
    assert stale["text"].count("spec-dock canonical status") == 1
    assert stale["title"].startswith("構造が更新されていません：company-os（3時間）") and "次の1手" in stale["title"]
    assert pr["text"] == "PR の状態が分かりません：spec-dock"
    f = frames(shot)
    # orca-web has nothing in next and no warning of its own: no frame, its name is in the summary (R-01, R-02)
    assert key("orca-web") not in f
    for r in shot["repos"]:
        assert all(
            w["text"].startswith("このリポジトリを読めませんでした") or "読めません" in w["text"] for w in r["warn"]
        ), r["key"]
    assert [w["text"] for w in f[key("company-os")]["warn"]] == []
    # every range lists the same rows
    for later in notices["notices"]["shots"][1:]:
        assert later["sum"]["rows"] == rows


def test_a_repository_the_screen_cannot_draw_keeps_its_reasons_in_its_frame(notices: dict[str, Any]) -> None:
    f = frames(notices["notices"]["shots"][0])
    mona = f[key("generic-mona")]
    assert [w["level"] for w in mona["warn"]] == ["error"]
    assert "構造のスナップショットが読めません（最後に読めたのは2時間前の取得）。" in mona["warn"][0]["text"]
    assert re.search(r"height:80px$", mona["style"])  # the heading 40, one warning 24, the padding 16
    cradle = f[key("tenting-cradle")]
    assert [w["level"] for w in cradle["warn"]] == ["error"] and re.search(r"height:80px$", cradle["style"])
    rows = notices["notices"]["shots"][0]["sum"]["rows"]
    assert all("generic-mona" not in r["text"] and "tenting-cradle" not in r["text"] for r in rows)


def test_no_notice_hides_the_summary(notices: dict[str, Any]) -> None:
    shot = notices["quiet"]["shots"][0]
    assert shot["sum"]["hidden"] and shot["sum"]["rows"] == []
    assert all(r["warn"] == [] for r in shot["repos"])


def test_the_first_view_starts_below_the_summary(notices: dict[str, Any]) -> None:
    pc = notices["summed"]["shots"][-1]
    assert not pc["sum"]["hidden"]
    tx, ty, _ = _t(pc)
    assert (tx, ty) == (8, 90 + 8)
    phone = notices["summed-phone"]["shots"][-1]
    tx, ty, s = _t(phone)
    assert (tx, s) == (4, 0.74) and ty == 90 + 8


# --- iss-00640 T-01, T-02: the bar's rows on a PC and the view under them ------------------------------------------


def test_the_pc_bar_puts_the_tools_after_the_chips_and_the_summary_last() -> None:
    """R-01, R-04: on a PC the chips' column gives its parts to the bar (the tools follow the chips, the summary takes its
    own row below); the condition is the exact complement of the phone's rule, whose rules stay as they are."""
    body = re.sub(r"/\*.*?\*/", "", CSS.read_text(encoding="utf-8"), flags=re.S)
    m = re.search(r"@container app not \(max-width: (\d+)px\) \{(.*?)\n\}", body, flags=re.S)
    assert m, "the PC block"
    phone = int(m.group(1))
    block = m.group(2)
    assert re.search(r'\.gx\[data-screen="allgraph"\] \.gx-left \{[^}]*display: contents', block)
    assert re.search(r'\.gx\[data-screen="allgraph"\] \.ax-sum \{[^}]*order: 1;[^}]*flex-basis: 100%', block)
    js = (ASSETS / "views" / "allgraph.js").read_text(encoding="utf-8")
    assert re.search(rf"const PHONE = {phone};", js)
    graph = re.sub(r"/\*.*?\*/", "", (ASSETS / "views" / "graph.css").read_text(encoding="utf-8"), flags=re.S)
    assert f"@container app (max-width: {phone}px)" in graph
    # the structure graph's bar is unchanged (R-02): tools pushed right, wrapping to the next row
    assert re.search(r"\.gx \.gx-bar \{[^}]*flex-wrap: wrap;[^}]*justify-content: space-between", graph)
    assert re.search(r"\.gx \.gx-tools \{[^}]*margin-left: auto", graph)


BAR_ROWS = {
    # one row: chips and tools side by side, the summary under them (1280, 1440)
    "one-row": {"next": 44, "tools": 44, "sum": 96},
    # the fixed form: chips, tools right-aligned on the next row, the summary under them (1000)
    "two-rows": {"next": 44, "tools": 84, "sum": 136},
    # no summary: the tools' row is the bar's bottom
    "no-summary": {"next": 44, "tools": 84, "sum": 0},
    # the tools lower than the summary (the bar before iss-00640): the lowest still counts
    "tools-last": {"next": 44, "tools": 176, "sum": 136},
}


@pytest.fixture(scope="module")
def rows(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    styled = {"styled": True, "hold": True, "width": 1440}
    runs = []
    for name, bottoms in BAR_ROWS.items():
        view = PC_VIEW | {"bar": 44, **bottoms}
        runs.append(base(name, steps=[{"release": True}], view=view, **styled))
        runs.append(base(f"{name}-fit", steps=[{"release": True}, {"act": "fit"}], view=view, **styled))
    return _run(tmp_path_factory.mktemp("rows"), runs)


@pytest.mark.parametrize("name", BAR_ROWS)
def test_the_first_view_and_fit_start_under_the_lowest_part_of_the_bar(rows: dict[str, Any], name: str) -> None:
    """R-03, F-01: the first view and 'fit' start 8 px under the lowest of the chips, the tools and the summary."""
    top = max(BAR_ROWS[name].values()) + 8
    first = rows[name]["shots"][-1]
    tx, ty, _ = _t(first)
    assert (tx, ty) == (8, top)
    shot = rows[f"{name}-fit"]["shots"][-1]
    width, height = (float(v.removesuffix("px")) for v in shot["size"])
    tx, ty, s = _t(shot)
    fit = min(1, (PC_VIEW["width"] - 16) / width, (PC_VIEW["height"] - top - 16) / height)
    assert s == pytest.approx(max(min(0.12, fit), fit))
    assert ty == pytest.approx(top + max(0, (PC_VIEW["height"] - top - 8 - height * s) / 2))
