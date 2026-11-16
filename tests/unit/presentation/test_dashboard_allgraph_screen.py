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
    "yubisaki",
    "spec-dock",
]


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


def test_the_frames_are_flat_in_the_world_nested_by_depth_with_names_and_tiers(out: dict[str, Any]) -> None:
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
    assert "事業" in f[key("housing-lifecycle")]["head"]
    assert "o/company-os" in f[key("company-os")]["head"] and "sd-badge" not in f[key("company-os")]["headHtml"]
    tiers = re.findall(r'<span class="sd-badge"[^>]*>([^<]*)</span>', f[key("yubisaki")]["headHtml"])
    assert tiers == ["プロダクト", "groups"]
    assert " › " in f[key("yubisaki")]["head"]
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


def test_a_failed_or_unread_repository_says_why_and_the_info_warning_shows_too(out: dict[str, Any]) -> None:
    f = frames(out["plain"]["shots"][0])
    failed = f[key("tenting-cradle")]
    assert failed["warn"][0]["level"] == "error"
    assert "このリポジトリを読めませんでした（boom）。" in failed["warn"][0]["text"]
    assert "spec-dock dashboard list" in failed["warn"][0]["text"]
    assert "spec-dock dashboard list" in failed["warn"][0]["title"]
    unread = f[key("yubisaki")]
    assert [w["level"] for w in unread["warn"]][:1] == ["error"]
    assert "構造のスナップショットが読めません" in unread["warn"][0]["text"]
    # the info warning (no pull request state) is listed in a shown frame
    assert "PR の状態が分かりません。" in [w["text"] for w in f[key("spec-dock")]["warn"]]


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
    for selector in (".ax-repo", ".ax-head", ".ax-warn", ".ax-body", ".ax-line"):
        assert selector in body, selector


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
