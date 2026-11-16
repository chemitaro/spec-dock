"""The cross-repository structure's frames, computed by `views/allgraph/compose.js` in node (iss-00614 T-01, T-02).

`tests/js/dashboard_allgraph_compose.mjs` loads the pure module without a DOM and returns its frames. The inputs are
synthetic: the nine registrations of the shape this PC has (company-os holding two businesses and their products,
spec-dock and orca-web outside), with keys only and no paths.
"""

from __future__ import annotations

from itertools import combinations, pairwise
import json
import subprocess
from typing import TYPE_CHECKING, Any

from tests.unit.presentation.test_dashboard_graph_js import ASSETS, ROOT, _node

if TYPE_CHECKING:
    from pathlib import Path

HARNESS = ROOT / "tests" / "js" / "dashboard_allgraph_compose.mjs"
REPO = {"head": 40, "warn": 24, "line": 28, "pad": 16, "gap": 16, "minW": 360, "headW": 280, "margin": 8}

BUSINESS = ["事業"]
PRODUCT = ["プロダクト"]
SHAPE = {
    "company-os": (None, []),
    "housing-lifecycle": ("company-os", BUSINESS),
    "taikyohiyou_project": ("housing-lifecycle", PRODUCT),
    "input-devices": ("company-os", BUSINESS),
    "generic-mona": ("input-devices", PRODUCT),
    "tenting-cradle": ("input-devices", PRODUCT),
    "yubisaki": ("input-devices", PRODUCT),
    "spec-dock": (None, []),
    "orca-web": (None, []),
}


def key(name: str) -> str:
    return f"github.com/o/{name}"


def repos(shape: dict[str, tuple[str | None, list[str]]] = SHAPE) -> list[dict[str, Any]]:
    """The list API's order: the keys sorted."""
    return [
        {"repository": key(n), "parent": key(p) if p else None, "tier": t, "owner": "o", "name": n}
        for n, (p, t) in sorted(shape.items(), key=lambda kv: key(kv[0]))
    ]


def ok(w: int = 600, h: int = 300, shown: int = 5, scopes: int | None = None, warns: int = 0, alerts: int = 0) -> dict:
    return {
        "status": "ok",
        "w": w,
        "h": h,
        "shown": shown,
        "scopes": shown if scopes is None else scopes,
        "warns": warns,
        "alerts": alerts,
    }


def quiet(scopes: int = 4, warns: int = 0, alerts: int = 0) -> dict:
    return ok(0, 0, 0, scopes, warns, alerts) | {"w": 500, "h": 200}


def empty() -> dict:
    return ok(0, 0, 0, 0)


def all_ok() -> dict[str, dict]:
    return {key(n): ok(500 + 40 * i, 200 + 30 * i) for i, n in enumerate(SHAPE)}


def run(tmp_path: Path, cases: dict[str, Any], body_width: list[list[int]] | None = None) -> dict[str, Any]:
    path = tmp_path / "request.json"
    path.write_text(json.dumps({"cases": cases, "bodyWidth": body_width or []}), encoding="utf-8")
    result = subprocess.run(
        [_node(), str(HARNESS), str(ASSETS), str(path)], capture_output=True, text=True, timeout=120, check=False
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def one(tmp_path: Path, case: dict[str, Any]) -> dict[str, Any]:
    return run(tmp_path, {"c": case})["cases"]["c"]


def inside(outer: dict, inner: dict) -> bool:
    return (
        outer["x1"] <= inner["x1"]
        and inner["x2"] <= outer["x2"]
        and outer["y1"] <= inner["y1"]
        and inner["y2"] <= outer["y2"]
    )


def apart(a: dict, b: dict) -> bool:
    return a["x2"] <= b["x1"] or b["x2"] <= a["x1"] or a["y2"] <= b["y1"] or b["y2"] <= a["y1"]


def body_rect(f: dict) -> dict:
    b = f["body"]
    return {"x1": b["x"], "y1": b["y"], "x2": b["x"] + b["w"], "y2": b["y"] + b["h"]}


def check_no_overlap(out: dict, shape: dict[str, tuple[str | None, list[str]]] = SHAPE) -> None:
    """R-03's second criterion: a child is inside its parent, below the parent's body, apart from its siblings."""
    frames = out["frames"]
    kids: dict[str | None, list[str]] = {}
    for n, (p, _) in shape.items():
        if key(n) in frames:
            kids.setdefault(key(p) if p and key(p) in frames else None, []).append(key(n))
    for parent, children in kids.items():
        for c in children:
            if parent:
                assert inside(frames[parent], frames[c]), (parent, c)
                assert apart(body_rect(frames[parent]), frames[c]), (parent, c)
                assert frames[c]["y1"] >= frames[parent]["body"]["y"] + frames[parent]["body"]["h"], (parent, c)
        for a, b in combinations(children, 2):
            assert apart(frames[a], frames[b]), (a, b)


# --- T-01: the nesting ------------------------------------------------------------------------------------------


def test_the_nine_registrations_nest_as_the_company_does(tmp_path: Path) -> None:
    out = run(tmp_path, {"pc": {"repos": repos(), "sizes": all_ok(), "options": {"range": "all", "width": 1400}}})
    assert out["REPO"] == REPO
    got = out["cases"]["pc"]
    f = got["frames"]
    assert set(f) == {key(n) for n in SHAPE}
    co = f[key("company-os")]
    for n in (
        "housing-lifecycle",
        "input-devices",
        "taikyohiyou_project",
        "generic-mona",
        "tenting-cradle",
        "yubisaki",
    ):
        assert inside(co, f[key(n)]), n
    assert inside(f[key("housing-lifecycle")], f[key("taikyohiyou_project")])
    for n in ("generic-mona", "tenting-cradle", "yubisaki"):
        assert inside(f[key("input-devices")], f[key(n)]), n
    for n in ("spec-dock", "orca-web"):
        assert apart(co, f[key(n)]), n
    check_no_overlap(got)
    depth = {k: v["depth"] for k, v in f.items()}
    assert depth[key("company-os")] == 0 and depth[key("input-devices")] == 1 and depth[key("yubisaki")] == 2
    # depth first, a parent before its children, siblings in the list's order
    assert got["order"] == [
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
    # every frame is inside the world's margin
    for v in f.values():
        assert v["x1"] >= REPO["margin"] and v["y1"] >= REPO["margin"]
        assert v["x2"] <= got["width"] - REPO["margin"] and v["y2"] <= got["height"] - REPO["margin"]


def test_a_frame_stacks_its_heading_warnings_band_body_and_shelf(tmp_path: Path) -> None:
    sizes = all_ok()
    sizes[key("input-devices")] = ok(700, 260, warns=2, alerts=1)
    got = one(tmp_path, {"repos": repos(), "sizes": sizes, "options": {"range": "all", "width": 1400}})
    f = got["frames"][key("input-devices")]
    assert f["head"] == {"x1": f["x1"], "y1": f["y1"], "x2": f["x2"], "y2": f["y1"] + REPO["head"]}
    assert f["warn"] == {"x1": f["x1"], "y1": f["y1"] + 40, "x2": f["x2"], "y2": f["y1"] + 40 + 48}
    assert f["band"] == {"x1": f["x1"], "y1": f["y1"] + 88, "x2": f["x2"], "y2": f["y1"] + 88}
    assert f["body"] == {"kind": "graph", "x": f["x1"] + REPO["pad"], "y": f["y1"] + 88, "w": 700, "h": 260}
    kids = [got["frames"][key(n)] for n in ("generic-mona", "tenting-cradle", "yubisaki")]
    assert min(k["y1"] for k in kids) == f["y1"] + 88 + 260 + REPO["pad"]
    assert min(k["x1"] for k in kids) == f["x1"] + REPO["pad"]
    assert f["y2"] == max(k["y2"] for k in kids) + REPO["pad"]
    # a frame without children: the body and the bottom padding
    leaf = got["frames"][key("spec-dock")]
    assert leaf["y2"] == leaf["body"]["y"] + leaf["body"]["h"] + REPO["pad"]
    assert leaf["x2"] - leaf["x1"] == max(REPO["headW"], leaf["body"]["w"]) + 2 * REPO["pad"]


def test_the_top_level_and_the_shelves_wrap_at_their_widths(tmp_path: Path) -> None:
    width = 1400
    got = one(tmp_path, {"repos": repos(), "sizes": all_ok(), "options": {"range": "all", "width": width}})
    f = got["frames"]
    tops = [f[key(n)] for n in ("company-os", "orca-web", "spec-dock")]
    # the top level wraps at the width less the margins: no frame past it unless alone on its row
    rows: dict[float, list[dict]] = {}
    for t in tops:
        rows.setdefault(t["y1"], []).append(t)
    for row in rows.values():
        if len(row) > 1:
            assert max(t["x2"] for t in row) <= width - REPO["margin"]
    assert len(rows) >= 2
    # a shelf wraps at its parent's usable body width (bodyWidth of the parent's depth), not at the body's width
    parent = f[key("input-devices")]
    limit = max(REPO["minW"], width - 2 * REPO["margin"] - 2 * REPO["pad"] * 2)
    kids = sorted((f[key(n)] for n in ("generic-mona", "tenting-cradle", "yubisaki")), key=lambda k: (k["y1"], k["x1"]))
    for k in kids:
        assert k["x2"] - (parent["x1"] + REPO["pad"]) <= limit or k["x1"] == parent["x1"] + REPO["pad"]
    assert len({k["y1"] for k in kids}) >= 2  # 692 + 732 + 772 and the gaps are wider than the limit 1320
    first_row = [k for k in kids if k["y1"] == kids[0]["y1"]]
    for a, b in pairwise(first_row):
        assert b["x1"] == a["x2"] + REPO["gap"]
    check_no_overlap(got)


def test_body_width_is_the_width_less_the_margins_and_paddings_with_a_floor(tmp_path: Path) -> None:
    out = run(tmp_path, {}, [[1400, 0], [1400, 1], [1400, 2], [450, 2], [300, 0], [600, 2]])
    assert out["bodyWidth"] == [1400 - 16 - 32, 1400 - 16 - 64, 1400 - 16 - 96, 360, 360, 600 - 16 - 96]


def test_a_parent_not_in_the_list_or_a_cycle_puts_the_repository_at_the_top_once(tmp_path: Path) -> None:
    shape = {"a": ("missing", []), "b": ("c", []), "c": ("b", []), "d": ("b", PRODUCT), "e": (None, [])}
    rs = repos(shape)
    for r in rs:
        if r["name"] == "a":
            r["parent"] = "github.com/o/not-listed"
    sizes = {key(n): ok(400, 200) for n in shape}
    got = one(tmp_path, {"repos": rs, "sizes": sizes, "options": {"range": "all", "width": 1400}})
    assert got["order"] == [key("a"), key("b"), key("d"), key("c"), key("e")]
    assert len(got["order"]) == len(set(got["order"]))
    f = got["frames"]
    assert f[key("a")]["depth"] == 0 and f[key("b")]["depth"] == 0 and f[key("c")]["depth"] == 0
    assert f[key("d")]["depth"] == 1 and inside(f[key("b")], f[key("d")])


def test_only_the_keys_and_the_parents_are_needed(tmp_path: Path) -> None:
    rs = [{"repository": r["repository"], "parent": r["parent"]} for r in repos()]
    got = one(tmp_path, {"repos": rs, "sizes": all_ok(), "options": {"range": "all", "width": 1400}})
    assert len(got["order"]) == 9
    check_no_overlap(got)


# --- T-02: what next shows, and the band ------------------------------------------------------------------------


def _next_sizes() -> dict[str, dict]:
    sizes = {key(n): quiet() for n in SHAPE}
    sizes[key("company-os")] = empty()  # no Scope: an empty container
    sizes[key("housing-lifecycle")] = quiet()  # Scopes, none shown: a quiet container of a visible grandchild
    sizes[key("taikyohiyou_project")] = ok(500, 220)
    sizes[key("input-devices")] = quiet(warns=1)  # an info warning only: not shown without a visible child
    sizes[key("generic-mona")] = quiet(warns=1)  # info only, no child: hidden
    sizes[key("tenting-cradle")] = quiet(warns=1, alerts=1)  # a warning that is not info: shown
    sizes[key("spec-dock")] = {"status": "loading"}
    del sizes[key("orca-web")]  # no size yet: loading
    sizes[key("yubisaki")] = {"status": "failed", "warns": 1, "alerts": 1}
    return sizes


def test_next_hides_what_has_nothing_to_show_and_keeps_the_containers(tmp_path: Path) -> None:
    got = one(tmp_path, {"repos": repos(), "sizes": _next_sizes(), "options": {"range": "next", "width": 1400}})
    f = got["frames"]
    assert key("generic-mona") not in f
    assert set(f) == {key(n) for n in SHAPE} - {key("generic-mona")}
    assert f[key("company-os")]["body"] == {
        "kind": "empty",
        "x": f[key("company-os")]["x1"] + 16,
        "y": f[key("company-os")]["y1"] + 40,
        "w": 0,
        "h": 0,
    }
    assert f[key("housing-lifecycle")]["body"]["kind"] == "quiet" and f[key("housing-lifecycle")]["body"]["h"] == 0
    assert f[key("input-devices")]["body"]["kind"] == "quiet" and f[key("input-devices")]["body"]["h"] == 0
    assert f[key("tenting-cradle")]["body"]["kind"] == "quiet" and f[key("tenting-cradle")]["body"]["h"] == 0
    assert f[key("taikyohiyou_project")]["body"]["kind"] == "graph"
    assert f[key("spec-dock")]["body"]["kind"] == "loading" and f[key("spec-dock")]["body"]["h"] == REPO["line"]
    assert f[key("orca-web")]["body"]["kind"] == "loading"
    assert f[key("yubisaki")]["body"]["kind"] == "failed" and f[key("yubisaki")]["body"]["h"] == 0
    # a container's shelf starts right below its heading (no padding after a body of height 0), children side by side
    co = f[key("company-os")]
    hl, ind = f[key("housing-lifecycle")], f[key("input-devices")]
    assert hl["y1"] == co["y1"] + REPO["head"] == ind["y1"]
    assert hl["x2"] + REPO["gap"] == ind["x1"]
    kids = [f[key(n)] for n in ("tenting-cradle", "yubisaki")]
    assert kids[0]["y1"] == kids[1]["y1"] == ind["y1"] + REPO["head"] + REPO["warn"]
    # a frame with no body and no child: heading, warnings and the bottom padding
    yb = f[key("yubisaki")]
    assert yb["y2"] - yb["y1"] == REPO["head"] + REPO["warn"] + REPO["pad"]
    check_no_overlap(got)


def test_next_with_nothing_anywhere_shows_no_frame(tmp_path: Path) -> None:
    sizes = {key(n): quiet() for n in SHAPE}
    got = one(tmp_path, {"repos": repos(), "sizes": sizes, "options": {"range": "next", "width": 1400}})
    assert got["order"] == [] and got["frames"] == {}


def test_all_and_now_show_every_frame_with_a_line_for_no_scope_and_nothing_shown(tmp_path: Path) -> None:
    sizes = _next_sizes()
    cases = {r: {"repos": repos(), "sizes": sizes, "options": {"range": r, "width": 1400}} for r in ("all", "now")}
    out = run(tmp_path, cases)["cases"]
    for r in ("all", "now"):
        f = out[r]["frames"]
        assert set(f) == {key(n) for n in SHAPE}, r
        assert f[key("company-os")]["body"]["kind"] == "empty" and f[key("company-os")]["body"]["h"] == REPO["line"]
        assert f[key("generic-mona")]["body"]["kind"] == "quiet" and f[key("generic-mona")]["body"]["h"] == REPO["line"]
        assert f[key("generic-mona")]["body"]["w"] == 0
        co = f[key("company-os")]
        # with a body of one line, the shelf is the padding below it
        assert min(f[key(n)]["y1"] for n in ("housing-lifecycle", "input-devices")) == co["y1"] + 40 + 28 + 16
        check_no_overlap(out[r])


def test_a_band_moves_the_body_and_the_shelf_down_and_no_band_is_zero(tmp_path: Path) -> None:
    plain: dict[str, Any] = {"range": "all", "width": 1400}
    base: dict[str, Any] = {"repos": repos(), "sizes": all_ok(), "options": plain}
    zeros = {key(n): 0 for n in SHAPE}
    cases = {
        "none": {"repos": base["repos"], "sizes": base["sizes"]},
        "plain": base,
        "empty": {**base, "options": {**plain, "bands": {}}},
        "zeros": {**base, "options": {**plain, "bands": zeros}},
        "band": {**base, "options": {**plain, "bands": {key("input-devices"): 30}}},
        "next_none": {**base, "options": {"range": "next", "width": 1400}},
        "next_zeros": {**base, "options": {"range": "next", "width": 1400, "bands": zeros}},
    }
    out = run(tmp_path, cases)["cases"]
    assert out["plain"] == out["empty"] == out["zeros"]
    assert out["next_none"] == out["next_zeros"]
    # without options: all and no wrap width given still composes (the defaults)
    assert len(out["none"]["order"]) == 9
    a = out["plain"]["frames"][key("input-devices")]
    b = out["band"]["frames"][key("input-devices")]
    assert b["band"] == {"x1": b["x1"], "y1": b["y1"] + REPO["head"], "x2": b["x2"], "y2": b["y1"] + REPO["head"] + 30}
    assert b["body"]["y"] - b["y1"] == a["body"]["y"] - a["y1"] + 30
    assert (b["y2"] - b["y1"]) == (a["y2"] - a["y1"]) + 30
    for n in ("generic-mona", "tenting-cradle", "yubisaki"):
        assert out["band"]["frames"][key(n)]["y1"] - b["y1"] == out["plain"]["frames"][key(n)]["y1"] - a["y1"] + 30
    check_no_overlap(out["band"])
