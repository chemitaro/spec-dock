"""The command lines' drawing as pure computation (iss-00646 T-01, iss-00657 T-01), run in node like the other graph checks.

`views/graph/command_motion.js` draws each command line in SVGs of its own bounding box: a flowing line's dots are pairs
24px apart (a large head and, 6px behind it, a small tail) in twelve still pictures, each shifted 2px along the line and
shown for 0.1s in turn by an opacity animation, and a ripple is an HTML ring. Every value is synthetic: no real path,
address or session id.
"""

from __future__ import annotations

import json
import re
import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from tests.unit.presentation.test_dashboard_graph_js import ASSETS, ROOT, _node

if TYPE_CHECKING:
    from pathlib import Path

CHECK = ROOT / "tests" / "js" / "dashboard_graph_command_motion.mjs"
CURVE = "M 10 20 C 10 80 200 40 200 120"
STUB = "M 200 120 L 200 134"
ARROW = "M 196.5 128 L 200 134 L 203.5 128 Z"  # iss-00648 D-04: the arrowhead at `to` (200, 134)
MARK = {"x": 182, "y": 140, "w": 36, "h": 16, "band": False}  # a box's mark below the edge
SLOT = {"x": 174, "y": 134, "w": 52, "h": 28, "band": True}  # a band slot
IN_MARK = '<rect class="cl-in" x="180" y="138" width="40" height="20" rx="4"/>'
IN_SLOT = '<rect class="cl-in" x="172" y="132" width="56" height="32" rx="4"/>'
SVG = re.compile(r"<svg ([^>]*)>(.*?)</svg>", re.S)


def _run(tmp_path: Path, request: dict[str, Any]) -> dict[str, Any]:
    path = tmp_path / "request.json"
    path.write_text(json.dumps(request), encoding="utf-8")
    result = subprocess.run(
        [_node(), str(CHECK), str(ASSETS), str(path)], capture_output=True, text=True, timeout=600, check=False
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def link(state: str = "flow", stubs: tuple[str, ...] = (), **extra: Any) -> dict[str, Any]:
    out: dict[str, Any] = {
        "id": "p-a\nc-b",
        "parent": "p-a",
        "child": "c-b",
        "state": state,
        "kind": "curve",
        "d": CURVE,
        "len": 336,
        "stubs": list(stubs),
        "from": {"x": 10, "y": 20},
        "to": {"x": 200, "y": 134},
    }
    return out | extra


def attrs(tag: str) -> dict[str, str]:
    return dict(re.findall(r'([\w-]+)="([^"]*)"', tag))


def svgs(html: str) -> list[tuple[dict[str, str], str]]:
    found = [(attrs(a), inner) for a, inner in SVG.findall(html)]
    assert "".join(f"<svg {a}>{i}</svg>" for a, i in SVG.findall(html)) == html, "only SVGs, one after another"
    return found


def style(value: str) -> dict[str, str]:
    return dict(part.split(":", 1) for part in value.split(";") if part)


def box_of(a: dict[str, str]) -> tuple[float, float, float, float]:
    """The SVG's place and size, which must equal its viewBox."""
    s = style(a["style"])
    place = (
        float(s["left"].removesuffix("px")),
        float(s["top"].removesuffix("px")),
        float(a["width"]),
        float(a["height"]),
    )
    assert tuple(float(v) for v in a["viewBox"].split()) == place
    assert all(v == int(v) for v in place)
    return place


def points(ds: list[str]) -> list[tuple[float, float]]:
    nums = [float(v) for d in ds for v in re.findall(r"-?\d+(?:\.\d+)?", d)]
    return list(zip(nums[::2], nums[1::2], strict=True))


def inside(box: tuple[float, float, float, float], pts: list[tuple[float, float]], pad: float) -> bool:
    x, y, w, h = box
    return all(x + pad <= px <= x + w - pad and y + pad <= py <= y + h - pad for px, py in pts)


@pytest.fixture(scope="module")
def motion(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    return _run(
        tmp_path_factory.mktemp("motion"),
        {
            "boxOf": [
                [[CURVE], None, None],
                [[CURVE, "M 0.4 5.6 L -3.2 9.9"], 4, []],
                [[STUB], 4, [{"x": 200, "y": 134, "r": 2.5}]],
                [[], 4, [{"x": 50, "y": 60, "r": 2.5}]],
                [[], 4, []],
            ],
            "links": [
                link("flow"),
                link("flow", (STUB,)),
                link("wait", (STUB,)),
                link("done"),
                link("flow", id='p"<&>', parent='p"<&>', child="c'x"),
                link("flow", mark=MARK),  # 5: a box's mark, no stub
                link("wait", mark=SLOT),  # 6: a band slot
                link("done", mark=MARK),  # 7
            ],
            "arrow": [{"x": 200, "y": 134}, {"x": 12.5, "y": -16}],
            "markRect": [MARK, SLOT],
            "ripples": [{"agent": "p-a", "x": 12.5, "y": 30}, {"agent": 'a"<&', "x": 0, "y": -4}],
            "dots": [[CURVE, 0], [CURVE, -22], [CURVE, -6], ['M 0 0 L "<&> 1', -2]],
            "svgOpen": [
                [{"x": -3, "y": 4, "w": 20, "h": 10}, "cl-svg", ""],
                [{"x": 0, "y": 0, "w": 1, "h": 2}, "cl-svg cl-ph", ";animation-delay:-0.1s"],
            ],
        },
    )


def test_the_constants(motion: dict[str, Any]) -> None:
    assert motion["MOTION"] == {"phases": 12, "step": 2, "tick": 0.1, "gap": 24, "tail": 6, "pad": 4}
    m = motion["MOTION"]
    assert m["step"] / m["tick"] == pytest.approx(20)  # 20px/s on every line
    assert m["phases"] * m["step"] == m["gap"]  # one round moves the dots one pair on (24px)
    assert m["phases"] * m["tick"] == pytest.approx(1.2)  # one round of 1.2s


def test_the_delays_and_the_offsets(motion: dict[str, Any]) -> None:
    assert motion["delays"] == pytest.approx([0, *(-(12 - i) / 10 for i in range(1, 12))])
    assert motion["delays"][:3] == [0, -1.1, -1.0] and motion["delays"][-1] == -0.1  # rounded in ms, no float tail
    assert motion["offsets"] == [-2 * i for i in range(12)]
    assert motion["offsets"][-1] == -22


def test_one_phase_shows_at_every_time_and_the_dots_move_forward(motion: dict[str, Any]) -> None:
    timeline = motion["timeline"]
    assert len(timeline) == 241  # 0..2.4s by 0.01s: two rounds
    for at in timeline:
        assert len(at["shown"]) == 1, at
        assert at["shown"][0] == round(at["t"] * 1000) // 100 % 12, at
    shown = [at["offsets"][0] for at in timeline]
    assert shown[:121:10] == [*(-2 * i for i in range(12)), 0]  # −2 each 0.1s, back to 0 after a round of 1.2s
    assert shown[120:241:10] == [*(-2 * i for i in range(12)), 0]  # the second round the same


def test_the_box_holds_every_point_and_the_dots(motion: dict[str, Any]) -> None:
    curve, mixed, stub, dot, empty = motion["boxOf"]
    assert curve == {"x": 6, "y": 16, "w": 198, "h": 108}  # the default pad of 4, the control points inside
    assert mixed == {"x": -8, "y": 1, "w": 212, "h": 123}  # floored left/top, ceiled right/bottom
    assert stub == {"x": 193, "y": 116, "w": 14, "h": 25}  # the dot's radius beyond the pad (134 + 2.5 + 4 → 141)
    assert dot == {"x": 43, "y": 53, "w": 14, "h": 14}
    assert empty is None


def test_svg_open(motion: dict[str, Any]) -> None:
    assert motion["svgOpen"] == [
        '<svg class="cl-svg" style="left:-3px;top:4px" width="20" height="10" viewBox="-3 4 20 10" aria-hidden="true">',
        '<svg class="cl-svg cl-ph" style="left:0px;top:0px;animation-delay:-0.1s" width="1" height="2" viewBox="0 0 1 2" aria-hidden="true">',
    ]


def test_dots_html_is_a_head_and_a_tail_6px_behind(motion: dict[str, Any]) -> None:
    """iss-00657 R-01: the same path twice, the tail's offset 6 more (6px behind, on the parent's side); no −0."""
    assert motion["dots"][:3] == [
        f'<path class="cl-line cl-hd" d="{CURVE}" style="stroke-dashoffset:0px"/><path class="cl-line cl-tl" d="{CURVE}" style="stroke-dashoffset:6px"/>',
        f'<path class="cl-line cl-hd" d="{CURVE}" style="stroke-dashoffset:-22px"/><path class="cl-line cl-tl" d="{CURVE}" style="stroke-dashoffset:-16px"/>',
        f'<path class="cl-line cl-hd" d="{CURVE}" style="stroke-dashoffset:-6px"/><path class="cl-line cl-tl" d="{CURVE}" style="stroke-dashoffset:0px"/>',
    ]
    escaped = motion["dots"][3]
    assert 'd="M 0 0 L &quot;&lt;&amp;&gt; 1"' in escaped and "<&>" not in escaped
    assert "-0px" not in "".join(motion["dots"])


def test_a_flowing_line_is_its_glow_and_twelve_phases(motion: dict[str, Any]) -> None:
    body = svgs(motion["links"][0]["body"])
    assert len(body) == 13
    (first, inner), phases = body[0], body[1:]
    assert first["class"] == "cl-svg"
    assert re.fullmatch(
        r'<g class="cl" data-id="p-a\nc-b" data-parent="p-a" data-child="c-b" data-state="flow"><path class="cl-glow" d="[^"]+"/></g>',
        inner,
    )
    box = box_of(first)
    assert inside(box, points([CURVE]), 4)
    for i, (a, inner) in enumerate(phases):
        assert a["class"] == "cl-svg cl-ph"
        assert a["data-ph"] == str(i)
        assert box_of(a) == box
        assert float(style(a["style"])["animation-delay"].removesuffix("s")) == pytest.approx(motion["delays"][i])
        g = re.fullmatch(
            r'<g ([^>]*)><path class="cl-line cl-hd" d="([^"]+)" style="stroke-dashoffset:(-?\d+)px"/>'
            r'<path class="cl-line cl-tl" d="([^"]+)" style="stroke-dashoffset:(-?\d+)px"/></g>',
            inner,
        )
        assert g, inner
        assert attrs(g.group(1)) == {
            "class": "cl",
            "data-id": "p-a\nc-b",
            "data-parent": "p-a",
            "data-child": "c-b",
            "data-state": "flow",
        }
        assert g.group(2) == g.group(4) == CURVE
        assert int(g.group(3)) == motion["offsets"][i]
        assert int(g.group(5)) == motion["offsets"][i] + motion["MOTION"]["tail"]


def test_a_waiting_or_done_line_is_one_still_picture(motion: dict[str, Any]) -> None:
    for i, state in ((2, "wait"), (3, "done")):
        body = svgs(motion["links"][i]["body"])
        assert len(body) == 1
        a, inner = body[0]
        assert a["class"] == "cl-svg"
        assert "data-ph" not in a
        assert inside(box_of(a), points([CURVE]), 4)
        assert re.fullmatch(
            rf'<g class="cl" [^>]*data-state="{state}"><path class="cl-glow" d="{re.escape(CURVE)}"/><path class="cl-line" d="{re.escape(CURVE)}"/></g>',
            inner,
        )


def test_the_ends_of_a_flowing_line_with_stubs(motion: dict[str, Any]) -> None:
    ends = svgs(motion["links"][1]["ends"])
    assert len(ends) == 13  # the stubs keep one cl-stub a picture (iss-00657 D-01)
    (first, inner), phases = ends[0], ends[1:]
    assert re.fullmatch(
        rf'<g class="cl" data-id="p-a\nc-b" data-state="flow"><path class="cl-arrow" d="{re.escape(ARROW)}"/></g>',
        inner,
    )
    box = box_of(first)
    assert inside(box, points([STUB, ARROW]), 4)
    for i, (a, inner) in enumerate(phases):
        assert a["class"] == "cl-svg cl-ph"
        assert a["data-ph"] == str(i)
        assert box_of(a) == box
        assert (
            inner
            == f'<g class="cl" data-id="p-a\nc-b" data-state="flow"><path class="cl-stub" d="{STUB}" style="stroke-dashoffset:{-2 * i}px"/></g>'
        )


def test_the_ends_without_stubs_and_of_a_waiting_line(motion: dict[str, Any]) -> None:
    plain = svgs(motion["links"][0]["ends"])
    assert len(plain) == 1  # no phases without stubs
    assert plain[0][1] == f'<g class="cl" data-id="p-a\nc-b" data-state="flow"><path class="cl-arrow" d="{ARROW}"/></g>'
    waiting = svgs(motion["links"][2]["ends"])
    assert len(waiting) == 1
    assert (
        waiting[0][1]
        == f'<g class="cl" data-id="p-a\nc-b" data-state="wait"><path class="cl-stub" d="{STUB}"/><path class="cl-arrow" d="{ARROW}"/></g>'
    )


def test_the_constants_of_the_arrowhead(motion: dict[str, Any]) -> None:
    """iss-00648 T-02 / R-04: 6 long, 3.5 each side (7 wide)."""
    assert motion["ARROW"] == {"len": 6, "half": 3.5}


def test_the_arrowhead_points_down_at_to(motion: dict[str, Any]) -> None:
    """iss-00648 T-02 / R-04: the tip at `to`, the base 6 above it and 7 wide."""
    assert motion["arrow"] == [ARROW, "M 9 -22 L 12.5 -16 L 16 -22 Z"]
    for d, to in zip(motion["arrow"], ((200, 134), (12.5, -16)), strict=True):
        (lx, ly), tip, (rx, ry) = points([d.removesuffix(" Z")])
        assert tip == to and ly == ry == to[1] - 6 and rx - lx == 7
        assert (lx + rx) / 2 == pytest.approx(to[0])


def test_the_mark_rect_rings_the_mark_2px_out(motion: dict[str, Any]) -> None:
    """iss-00648 T-02 / R-04."""
    assert motion["markRect"] == [IN_MARK, IN_SLOT]


def test_the_ends_have_one_arrowhead_no_dot_and_ring_a_boxs_mark(motion: dict[str, Any]) -> None:
    """iss-00648 T-02 / R-04, R-05: every end has one arrowhead and no dot; a box's mark is ringed in the ends' SVG,
    which holds the arrowhead and the ring; a flowing line without stubs has one still picture of its ends."""
    for entry in motion["links"]:
        assert entry["ends"].count('class="cl-arrow"') == 1
        assert "cl-dot" not in entry["ends"] and "<circle" not in entry["ends"]
    for i, state in ((5, "flow"), (7, "done")):
        ends = svgs(motion["links"][i]["ends"])
        assert len(ends) == 1 and ends[0][0]["class"] == "cl-svg" and "data-ph" not in ends[0][0]
        assert (
            ends[0][1]
            == f'<g class="cl" data-id="p-a\nc-b" data-state="{state}">{IN_MARK}<path class="cl-arrow" d="{ARROW}"/></g>'
        )
        assert inside(box_of(ends[0][0]), [*points([ARROW]), (180, 138), (220, 158)], 4)
    # a band slot: the ring is not in the ends' layer
    slot = svgs(motion["links"][6]["ends"])
    assert len(slot) == 1 and "cl-in" not in slot[0][1]


def test_band_mark_html_rings_only_a_band_childs_slot(motion: dict[str, Any]) -> None:
    """iss-00648 T-02 / R-04: one SVG with the ring and the line's id and state for a band slot; nothing otherwise."""
    band = svgs(motion["links"][6]["band"])
    assert len(band) == 1
    a, inner = band[0]
    assert a["class"] == "cl-svg"
    assert inner == f'<g class="cl" data-id="p-a\nc-b" data-state="wait">{IN_SLOT}</g>'
    assert inside(box_of(a), [(172, 132), (228, 164)], 4)
    assert [motion["links"][i]["band"] for i in (0, 1, 2, 3, 5, 7)] == [""] * 6


def test_the_ripple_is_an_html_ring_pair_at_its_centre(motion: dict[str, Any]) -> None:
    assert motion["ripples"] == [
        '<span class="cr" data-agent="p-a" style="left:12.5px;top:30px"><i class="cr-a"></i><i class="cr-b"></i></span>',
        '<span class="cr" data-agent="a&quot;&lt;&amp;" style="left:0px;top:-4px"><i class="cr-a"></i><i class="cr-b"></i></span>',
    ]


def test_the_values_are_escaped_and_no_length_is_written(motion: dict[str, Any]) -> None:
    html = motion["links"][4]["body"] + motion["links"][4]["ends"]
    assert 'data-id="p&quot;&lt;&amp;&gt;"' in html
    assert 'data-child="c&#39;x"' in html
    assert "<&>" not in html
    every = "".join(v["body"] + v["ends"] + v["band"] for v in motion["links"])
    assert "--cl-len" not in every
    assert "<animate" not in every
