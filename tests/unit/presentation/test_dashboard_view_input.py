"""The graphs' wheel and key input as pure computation (iss-00655 T-01, T-02), run in node like the other graph checks.

`views/graph/view_input.js` tells a mouse wheel from a trackpad's wheel events (D-01), maps a wheel event to a zoom at
the cursor or a pan (D-02), maps a key to a pan, a zoom or a fit (D-03), and tells whether a keydown belongs to the
graph (D-03). The wheel values are synthetic, made from the browsers' rules (Firefox's lines, a wheel notch of
`wheelDelta` 120, a trackpad's pixels with `wheelDeltaY` = −3·deltaY), not measured on a machine.
"""

from __future__ import annotations

import json
import math
import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from tests.unit.presentation.test_dashboard_graph_js import ASSETS, ROOT, _node

if TYPE_CHECKING:
    from pathlib import Path

CHECK = ROOT / "tests" / "js" / "dashboard_view_input.mjs"


def _run(tmp_path: Path, request: dict[str, Any]) -> dict[str, Any]:
    path = tmp_path / "request.json"
    path.write_text(json.dumps(request), encoding="utf-8")
    result = subprocess.run(
        [_node(), str(CHECK), str(ASSETS), str(path)], capture_output=True, text=True, timeout=600, check=False
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def wheel(**values: Any) -> dict[str, Any]:
    """A wheel event's values; clientX/clientY are the cursor."""
    return {"clientX": 300, "clientY": 200} | values


# D-01's table: (scene, event, kind)
KINDS: list[tuple[str, dict[str, Any], str]] = [
    ("chrome windows wheel up", wheel(deltaMode=0, deltaY=-100, deltaX=0, wheelDeltaY=120), "wheel?"),
    ("chrome windows wheel down", wheel(deltaMode=0, deltaY=100, deltaX=0, wheelDeltaY=-120), "wheel?"),
    ("chrome macos wheel accelerated", wheel(deltaMode=0, deltaY=40, deltaX=0, wheelDeltaY=-240), "wheel?"),
    ("chrome macos wheel slow", wheel(deltaMode=0, deltaY=-4, deltaX=0, wheelDeltaY=120), "wheel?"),
    ("safari macos wheel", wheel(deltaMode=0, deltaY=4, deltaX=0, wheelDeltaY=-120), "wheel?"),
    ("firefox wheel one line", wheel(deltaMode=1, deltaY=1, deltaX=0), "wheel"),
    ("firefox wheel three lines", wheel(deltaMode=1, deltaY=-3, deltaX=0), "wheel"),
    ("firefox page", wheel(deltaMode=2, deltaY=1, deltaX=0), "wheel"),
    ("firefox tilt", wheel(deltaMode=1, deltaY=0, deltaX=3), "pan"),
    ("firefox tilt one", wheel(deltaMode=1, deltaY=0, deltaX=-1), "pan"),
    ("trackpad small", wheel(deltaMode=0, deltaY=2.5, deltaX=0, wheelDeltaY=-7.5), "pan"),
    ("trackpad up", wheel(deltaMode=0, deltaY=-7, deltaX=1, wheelDeltaY=21), "pan"),
    ("trackpad down", wheel(deltaMode=0, deltaY=12, deltaX=-3, wheelDeltaY=-36), "pan"),
    ("trackpad straight", wheel(deltaMode=0, deltaY=12, deltaX=0, wheelDeltaY=-36), "pan"),
    ("windows precision touchpad", wheel(deltaMode=0, deltaY=3.2, deltaX=0, wheelDeltaY=-9), "pan"),
    ("firefox trackpad no wheelDeltaY", wheel(deltaMode=0, deltaY=6, deltaX=0), "pan"),
    ("firefox trackpad wheelDeltaY not a notch", wheel(deltaMode=0, deltaY=6, deltaX=0, wheelDeltaY=-18), "pan"),
    ("wheelDeltaY zero", wheel(deltaMode=0, deltaY=6, deltaX=0, wheelDeltaY=0), "pan"),
    ("notch with deltaX", wheel(deltaMode=0, deltaY=40, deltaX=2, wheelDeltaY=-120), "pan"),
    ("pinch ctrl", wheel(deltaMode=0, deltaY=3, deltaX=0, ctrlKey=True), "pinch"),
    ("pinch meta", wheel(deltaMode=0, deltaY=-10, deltaX=0, metaKey=True), "pinch"),
    ("ctrl wheel windows", wheel(deltaMode=0, deltaY=100, deltaX=0, wheelDeltaY=-120, ctrlKey=True), "pinch"),
    ("shift chrome", wheel(deltaMode=0, deltaY=0, deltaX=100, wheelDeltaY=0, shiftKey=True), "hpan"),
    ("shift firefox", wheel(deltaMode=1, deltaY=3, deltaX=0, shiftKey=True), "hpan"),
    ("no values", wheel(deltaY=5, deltaX=1), "pan"),
    ("no values straight", wheel(deltaY=5), "pan"),
]


@pytest.fixture(scope="module")
def result(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    return _run(
        tmp_path_factory.mktemp("view-input"),
        {
            "kinds": [e for _, e, _ in KINDS],
            "actions": [[e, last, now, page] for _, e, last, now, page in ACTIONS],
            "keys": [e for _, e, _ in KEYS],
            "chains": [[[e, now] for e, now in chain] for chain in CHAINS.values()],
            "order": [
                wheel(deltaMode=0, deltaY=-100, deltaX=0, wheelDeltaY=120),
                wheel(deltaMode=1, deltaY=3, deltaX=0),
            ],
            "owns": list(OWNS),
        },
    )


def test_the_constants(result: dict[str, Any]) -> None:
    assert result["WHEEL"] == {"step": 1.15, "maxSteps": 2, "stick": 200}
    assert result["KEYS"] == {"pan": 80, "fast": 4, "zin": 1.25, "zout": 0.8}


def test_wheel_kind_follows_the_table(result: dict[str, Any]) -> None:
    got = dict(zip([s for s, _, _ in KINDS], result["kinds"], strict=True))
    assert got == {s: k for s, _, k in KINDS}


def test_delta_mode_is_read_before_wheel_delta_y(result: dict[str, Any]) -> None:
    notch, lines = result["order"]
    for reads in (notch["kind"], notch["action"]):
        assert "deltaMode" in reads
        assert "wheelDeltaY" in reads
        assert reads.index("deltaMode") < reads.index("wheelDeltaY")
    for reads in (lines["kind"], lines["action"]):
        assert "deltaMode" in reads  # a sure wheel: wheelDeltaY is not needed
        if "wheelDeltaY" in reads:
            assert reads.index("deltaMode") < reads.index("wheelDeltaY")


S = 1.15
PAN = {"kind": "pan", "at": 1000}
NOTCH_UP = wheel(deltaMode=0, deltaY=-100, deltaX=0, wheelDeltaY=120)

# (scene, event, last, now, page)
ACTIONS: list[tuple[str, dict[str, Any], Any, float, float]] = [
    ("notch up", NOTCH_UP, None, 1000, 1000),
    ("notch down", wheel(deltaMode=0, deltaY=100, deltaX=0, wheelDeltaY=-120), None, 1000, 1000),
    ("two notches", wheel(deltaMode=0, deltaY=-200, deltaX=0, wheelDeltaY=240), None, 1000, 1000),
    ("three notches", wheel(deltaMode=0, deltaY=-300, deltaX=0, wheelDeltaY=360), None, 1000, 1000),
    ("three notches down", wheel(deltaMode=0, deltaY=300, deltaX=0, wheelDeltaY=-360), None, 1000, 1000),
    ("firefox three lines", wheel(deltaMode=1, deltaY=3, deltaX=0), None, 1000, 1000),
    ("firefox one line up", wheel(deltaMode=1, deltaY=-1, deltaX=0), None, 1000, 1000),
    ("sure wheel zero", wheel(deltaMode=1, deltaY=0, deltaX=0), None, 1000, 1000),
    ("pinch", wheel(deltaMode=0, deltaY=3, deltaX=0, ctrlKey=True), None, 1000, 1000),
    ("pinch out", wheel(deltaMode=0, deltaY=-10, deltaX=0, metaKey=True), None, 1000, 1000),
    ("two fingers", wheel(deltaMode=0, deltaY=7, deltaX=3, wheelDeltaY=-21), None, 1000, 1000),
    ("shift chrome", wheel(deltaMode=0, deltaY=0, deltaX=100, shiftKey=True), None, 1000, 1000),
    ("shift deltaY", wheel(deltaMode=0, deltaY=-100, deltaX=0, shiftKey=True), None, 1000, 1000),
    ("shift firefox lines", wheel(deltaMode=1, deltaY=3, deltaX=0, shiftKey=True), None, 1000, 1000),
    ("shift firefox page", wheel(deltaMode=2, deltaY=1, deltaX=0, shiftKey=True), None, 1000, 640),
    ("firefox tilt", wheel(deltaMode=1, deltaY=0, deltaX=3), None, 1000, 1000),
    ("after pan 199ms", NOTCH_UP, PAN, 1199, 1000),
    ("after pan 200ms", NOTCH_UP, PAN, 1200, 1000),
    ("after pan sure wheel", wheel(deltaMode=1, deltaY=3, deltaX=0), PAN, 1050, 1000),
    ("after pan pinch", wheel(deltaMode=0, deltaY=3, deltaX=0, ctrlKey=True), PAN, 1050, 1000),
    ("after wheel", NOTCH_UP, {"kind": "wheel?", "at": 1000}, 1050, 1000),
]


def _actions(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return dict(zip([s for s, *_ in ACTIONS], result["actions"], strict=True))


def _zoom(got: dict[str, Any], f: float) -> None:
    act = got["act"]
    assert act["type"] == "zoom"
    assert act["f"] == pytest.approx(f)
    assert (act["x"], act["y"]) == (300, 200)  # the cursor


def _pan(got: dict[str, Any], dx: float, dy: float) -> None:
    assert got["act"] == {"type": "pan", "dx": pytest.approx(dx), "dy": pytest.approx(dy)}


def test_a_mouse_wheel_zooms_by_steps_at_the_cursor(result: dict[str, Any]) -> None:
    got = _actions(result)
    _zoom(got["notch up"], S)
    _zoom(got["notch down"], 1 / S)
    _zoom(got["two notches"], S**2)
    _zoom(got["three notches"], S**2)  # at most two steps in one event
    _zoom(got["three notches down"], S**-2)
    _zoom(got["firefox three lines"], 1 / S)  # lines are one step
    _zoom(got["firefox one line up"], S)
    assert got["sure wheel zero"]["act"] is None
    assert got["notch up"]["kind"] == "wheel?"
    assert got["notch up"]["at"] == 1000
    assert got["firefox three lines"]["kind"] == "wheel"


def test_a_pinch_zooms_as_before(result: dict[str, Any]) -> None:
    got = _actions(result)
    _zoom(got["pinch"], math.exp(-0.03))
    _zoom(got["pinch out"], math.exp(0.1))
    assert got["pinch"]["kind"] == "pinch"


def test_two_fingers_pan_by_their_deltas(result: dict[str, Any]) -> None:
    got = _actions(result)
    _pan(got["two fingers"], -3, -7)
    assert got["two fingers"]["kind"] == "pan"
    _pan(got["firefox tilt"], -48, 0)  # three lines of 16px


def test_shift_pans_sideways_only(result: dict[str, Any]) -> None:
    got = _actions(result)
    _pan(got["shift chrome"], -100, 0)
    _pan(got["shift deltaY"], 100, 0)
    _pan(got["shift firefox lines"], -48, 0)
    _pan(got["shift firefox page"], -640, 0)
    assert got["shift chrome"]["kind"] == "hpan"


def test_a_notch_in_a_trackpad_stroke_keeps_panning(result: dict[str, Any]) -> None:
    got = _actions(result)
    _pan(got["after pan 199ms"], 0, 100)
    assert got["after pan 199ms"]["kind"] == "pan"
    _zoom(got["after pan 200ms"], S)
    assert got["after pan 200ms"]["kind"] == "wheel?"
    _zoom(got["after pan sure wheel"], 1 / S)
    assert got["after pan sure wheel"]["kind"] == "wheel"
    _zoom(got["after pan pinch"], math.exp(-0.03))
    assert got["after pan pinch"]["kind"] == "pinch"
    _zoom(got["after wheel"], S)


def key(k: str, **mods: Any) -> dict[str, Any]:
    return {"key": k} | mods


# (scene, event, action)
KEYS: list[tuple[str, dict[str, Any], Any]] = [
    ("left", key("ArrowLeft"), {"type": "pan", "dx": 80, "dy": 0}),
    ("right", key("ArrowRight"), {"type": "pan", "dx": -80, "dy": 0}),
    ("up", key("ArrowUp"), {"type": "pan", "dx": 0, "dy": 80}),
    ("down", key("ArrowDown"), {"type": "pan", "dx": 0, "dy": -80}),
    ("shift left", key("ArrowLeft", shiftKey=True), {"type": "pan", "dx": 320, "dy": 0}),
    ("shift right", key("ArrowRight", shiftKey=True), {"type": "pan", "dx": -320, "dy": 0}),
    ("shift up", key("ArrowUp", shiftKey=True), {"type": "pan", "dx": 0, "dy": 320}),
    ("shift down", key("ArrowDown", shiftKey=True), {"type": "pan", "dx": 0, "dy": -320}),
    ("repeat", key("ArrowRight", repeat=True), {"type": "pan", "dx": -80, "dy": 0}),
    ("plus", key("+"), {"type": "zoom", "f": 1.25}),
    ("plus shifted", key("+", shiftKey=True), {"type": "zoom", "f": 1.25}),
    ("equals", key("="), {"type": "zoom", "f": 1.25}),
    ("minus", key("-"), {"type": "zoom", "f": 0.8}),
    ("zero", key("0"), {"type": "fit"}),
    ("numpad plus", key("+", code="NumpadAdd"), {"type": "zoom", "f": 1.25}),
    ("numpad minus", key("-", code="NumpadSubtract"), {"type": "zoom", "f": 0.8}),
    ("numpad zero", key("0", code="Numpad0"), {"type": "fit"}),
    ("a", key("a"), None),
    ("enter", key("Enter"), None),
    ("escape", key("Escape"), None),
    ("space", key(" "), None),
    ("tab", key("Tab"), None),
    ("one", key("1"), None),
    ("ctrl", key("ArrowRight", ctrlKey=True), None),
    ("cmd", key("+", metaKey=True), None),
    ("alt", key("ArrowLeft", altKey=True), None),
    ("ctrl zero", key("0", ctrlKey=True), None),
    ("composing", key("ArrowDown", isComposing=True), None),
    ("prevented", key("ArrowUp", defaultPrevented=True), None),
]


def test_key_action_maps_the_keys(result: dict[str, Any]) -> None:
    got = dict(zip([s for s, _, _ in KEYS], result["keys"], strict=True))
    assert got == {s: a for s, _, a in KEYS}


# target name -> does the graph take the key
OWNS: dict[str, bool] = {
    "none": True,
    "html": True,
    "body": True,
    "main": True,  # the screen's container, focused on each move
    "gxview": True,
    "box": True,  # a box in the graph (role=button div)
    "inbox": True,
    "v-anchor": True,  # an anchor without href is no link
    "v-not-editable": True,
    "v-input": False,
    "v-textarea": False,
    "v-select": False,
    "v-button": False,
    "v-link": False,
    "v-summary": False,
    "v-iframe": False,
    "v-editable": False,
    "v-in-editable": False,
    "bar": False,
    "tools": False,
    "panel": False,
    "in-panel": False,
}


def test_owns_key_leaves_other_inputs_alone(result: dict[str, Any]) -> None:
    assert result["owns"] == OWNS


# A stroke of wheel events (each within WHEEL.stick of the one before) keeps the kind it started with when that kind
# came from the values alone (pan, wheel?); a sure kind (wheel by lines, pinch, hpan) starts a stroke of its own.
STROKE_PAN = wheel(deltaMode=0, deltaY=6, deltaX=1, wheelDeltaY=-18)
FLING = wheel(deltaMode=0, deltaY=40, deltaX=0, wheelDeltaY=-120)  # a fast stroke's notch-like value
PAN_VALUES = wheel(deltaMode=0, deltaY=-6, deltaX=2, wheelDeltaY=18)
LINES = wheel(deltaMode=1, deltaY=3, deltaX=0)
PINCH = wheel(deltaMode=0, deltaY=3, deltaX=0, ctrlKey=True)
SHIFT = wheel(deltaMode=0, deltaY=-100, deltaX=0, shiftKey=True)
CHAINS: dict[str, list[tuple[dict[str, Any], float]]] = {
    "trackpad stroke": [(STROKE_PAN, 1000), *[(FLING, 1000 + 150 * i) for i in range(1, 6)]],
    "wheel stroke": [(NOTCH_UP, 1000), (PAN_VALUES, 1150)],
    "after lines": [(STROKE_PAN, 1000), (LINES, 1050), (NOTCH_UP, 1100)],
    "after pinch": [(STROKE_PAN, 1000), (PINCH, 1050), (NOTCH_UP, 1100)],
    "after shift": [(STROKE_PAN, 1000), (SHIFT, 1050), (NOTCH_UP, 1100)],
    "pinch then pan values": [(NOTCH_UP, 1000), (PINCH, 1050), (PAN_VALUES, 1100)],
}


def _chains(result: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return dict(zip(CHAINS, result["chains"], strict=True))


def test_a_trackpad_stroke_keeps_panning_past_the_stick_time(result: dict[str, Any]) -> None:
    got = _chains(result)["trackpad stroke"]
    assert [r["kind"] for r in got] == ["pan"] * 6  # 750ms in all, 150ms between each
    assert [r["at"] for r in got] == [1000 + 150 * i for i in range(6)]
    for r in got[1:]:
        _pan(r, 0, -40)


def test_a_wheel_stroke_keeps_zooming(result: dict[str, Any]) -> None:
    first, second = _chains(result)["wheel stroke"]
    _zoom(first, S)
    assert second["kind"] == "wheel?"
    _zoom(second, S)  # deltaY −6: in, one step


def test_a_sure_kind_starts_a_stroke_of_its_own(result: dict[str, Any]) -> None:
    got = _chains(result)
    assert [r["kind"] for r in got["after lines"]] == ["pan", "wheel", "wheel?"]
    assert [r["kind"] for r in got["after pinch"]] == ["pan", "pinch", "wheel?"]
    assert [r["kind"] for r in got["after shift"]] == ["pan", "hpan", "wheel?"]
    _zoom(got["after shift"][2], S)
    assert [r["kind"] for r in got["pinch then pan values"]] == ["wheel?", "pinch", "pan"]
