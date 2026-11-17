"""The command lines' drawing as pure computation (iss-00646 T-01), run in node like the other graph checks.

`views/graph/command_motion.js` draws each command line in SVGs of its own bounding box: a flowing line's dots are four
still pictures, each shifted 2px along the line and shown for 0.05s in turn by an opacity animation, and a ripple is an
HTML ring. Every value is synthetic: no real path, address or session id.
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
            ],
            "ripples": [{"agent": "p-a", "x": 12.5, "y": 30}, {"agent": 'a"<&', "x": 0, "y": -4}],
            "svgOpen": [
                [{"x": -3, "y": 4, "w": 20, "h": 10}, "cl-svg", ""],
                [{"x": 0, "y": 0, "w": 1, "h": 2}, "cl-svg cl-ph", ";animation-delay:-0.1s"],
            ],
        },
    )


def test_the_constants(motion: dict[str, Any]) -> None:
    assert motion["MOTION"] == {"phases": 4, "step": 2, "tick": 0.05, "pad": 4}
    m = motion["MOTION"]
    assert m["step"] / m["tick"] == pytest.approx(40)  # 40px/s on every line
    assert m["phases"] * m["step"] == 8  # one round of the dots' period of 8px


def test_the_delays_and_the_offsets(motion: dict[str, Any]) -> None:
    assert motion["delays"] == pytest.approx([0, -0.15, -0.1, -0.05])
    assert motion["offsets"] == [0, -2, -4, -6]


def test_one_phase_shows_at_every_time_and_the_dots_move_forward(motion: dict[str, Any]) -> None:
    timeline = motion["timeline"]
    assert len(timeline) == 41
    for at in timeline:
        assert len(at["shown"]) == 1, at
        assert at["shown"][0] == round(at["t"] * 1000) // 50 % 4, at
    shown = [at["offsets"][0] for at in timeline]
    assert shown[:21:5] == [0, -2, -4, -6, 0]  # −2 each 0.05s, back to 0 after a round (one period of 8px)


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


def test_a_flowing_line_is_its_glow_and_four_phases(motion: dict[str, Any]) -> None:
    body = svgs(motion["links"][0]["body"])
    assert len(body) == 5
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
            r'<g ([^>]*)><path class="cl-line" d="([^"]+)" style="stroke-dashoffset:(-?\d+)px"/></g>', inner
        )
        assert g, inner
        assert attrs(g.group(1)) == {
            "class": "cl",
            "data-id": "p-a\nc-b",
            "data-parent": "p-a",
            "data-child": "c-b",
            "data-state": "flow",
        }
        assert g.group(2) == CURVE
        assert int(g.group(3)) == motion["offsets"][i]


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
    assert len(ends) == 5
    (first, inner), phases = ends[0], ends[1:]
    assert re.fullmatch(
        r'<g class="cl" data-id="p-a\nc-b" data-state="flow"><circle class="cl-dot" cx="200" cy="134" r="2.5"/></g>',
        inner,
    )
    box = box_of(first)
    assert inside(box, [*points([STUB]), (200, 136.5), (200, 131.5)], 4)
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
    assert (
        plain[0][1]
        == '<g class="cl" data-id="p-a\nc-b" data-state="flow"><circle class="cl-dot" cx="200" cy="134" r="2.5"/></g>'
    )
    waiting = svgs(motion["links"][2]["ends"])
    assert len(waiting) == 1
    assert (
        waiting[0][1]
        == f'<g class="cl" data-id="p-a\nc-b" data-state="wait"><path class="cl-stub" d="{STUB}"/><circle class="cl-dot" cx="200" cy="134" r="2.5"/></g>'
    )


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
    every = "".join(v["body"] + v["ends"] for v in motion["links"])
    assert "--cl-len" not in every
    assert "<animate" not in every
