"""The state marks: colors, shapes, the progress ring and the motion (iss-00574 T-04〜T-07).

The color checks read the values from `app.css` and compute the WCAG contrast. The JavaScript checks run
`core/ui.js` under node (required on CI, skipped locally without node).
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import textwrap

import pytest

ASSETS = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "dashboard"
APP_CSS = (ASSETS / "app.css").read_text()
STATES = ("ready", "doing", "blocked", "unknown", "done")


# --- T-04: colors ----------------------------------------------------------------------------------------------


def _block(selector: str) -> str:
    """The declarations of the first rule whose selector is exactly `selector` (light `:root` or dark theme)."""
    start = APP_CSS.index(selector + " {")
    depth, index = 0, APP_CSS.index("{", start)
    for end in range(index, len(APP_CSS)):
        depth += {"{": 1, "}": -1}.get(APP_CSS[end], 0)
        if depth == 0:
            return APP_CSS[index + 1 : end]
    raise AssertionError(selector)


def _tokens(block: str) -> dict[str, str]:
    return {name: value.strip() for name, value in re.findall(r"(--[a-z0-9-]+):\s*([^;]+);", block)}


LIGHT = _tokens(_block(":root"))
DARK = {**LIGHT, **_tokens(_block(':root[data-theme="dark"]'))}


def _rgba(value: str, tokens: dict[str, str]) -> tuple[float, float, float, float]:
    while value.startswith("var("):
        value = tokens[value[4:-1].split(",")[0].strip()]
    if value.startswith("#"):
        h = value[1:]
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0)
    found = re.fullmatch(r"rgb\((\d+) (\d+) (\d+) / (\d+)%\)", value)
    assert found, value
    r, g, b, a = (int(x) for x in found.groups())
    return (r, g, b, a / 100)


def _over(top: tuple[float, float, float, float], under: tuple[float, float, float, float]) -> tuple[float, ...]:
    a = top[3]
    return (*(top[i] * a + under[i] * (1 - a) for i in range(3)), 1.0)


def _luminance(color: tuple[float, ...]) -> float:
    def channel(c: float) -> float:
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in color[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    high, low = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("state", STATES)
def test_every_state_color_meets_wcag_aa(theme: str, state: str) -> None:
    tokens = LIGHT if theme == "light" else DARK
    surface = _rgba("var(--ds-surface)", tokens)
    mark = _rgba(f"var(--sd-{state})", tokens)
    for ground in ("--ds-bg", "--ds-bg-2", "--ds-surface", "--ds-surface-2"):
        assert _contrast(mark, _rgba(f"var({ground})", tokens)) >= 3.0, (theme, state, ground)
    chip = _over(_rgba(f"var(--sd-{state}-bg)", tokens), surface)
    assert _contrast(_rgba(f"var(--sd-{state}-ink)", tokens), chip) >= 4.5, (theme, state)
    # the mark on its own soft ground (the graph's box in progress, the chip's icon)
    assert _contrast(mark, chip) >= 3.0, (theme, state)


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_the_ring_track_is_visible(theme: str) -> None:
    tokens = LIGHT if theme == "light" else DARK
    track = _rgba("var(--sd-track)", tokens)
    for ground in ("--ds-bg", "--ds-surface"):
        assert _contrast(track, _rgba(f"var({ground})", tokens)) >= 3.0, (theme, ground)


def test_the_state_rules_use_only_the_state_tokens() -> None:
    for state in STATES:
        rule = re.search(rf'\[data-st="{state}"\]\s*\{{([^}}]*)\}}', APP_CSS)
        assert rule, state
        assert re.findall(r"var\((--[a-z0-9-]+)\)", rule.group(1)) == [
            f"--sd-{state}",
            f"--sd-{state}-bg",
            f"--sd-{state}-line",
            f"--sd-{state}-ink",
        ], state


def test_blocking_marks_are_yellow_not_danger() -> None:
    checks = {
        "views/_shared/parts.css": (
            r"\.sd-hm \{[^}]*\}",
            r'\.sd-bar i\[data-st="blocked"\][^}]*\}',
            r'\[data-st="blocked"\]\.sd-card \{[^}]*\}',
        ),
        "views/graph.css": (r"\.gx \.hm \{[^}]*\}",),
        "views/todos.css": (r"\.td-blocks \{[^}]*\}", r"\.td-blocks \.ds-icon \{[^}]*\}"),
    }
    for rel, patterns in checks.items():
        text = (ASSETS / rel).read_text()
        for pattern in patterns:
            found = re.search(pattern, text)
            assert found, (rel, pattern)
            assert "--ds-danger" not in found.group(0) and "--sd-blocked" in found.group(0), (rel, found.group(0))
    todos = (ASSETS / "views" / "todos.js").read_text()
    assert 'data-tone="blocked">${ic("person")}Scope を止めている' in todos
    overview = (ASSETS / "views" / "overview.js").read_text()
    assert 'data-tone="${board.blocked ? "blocked" : ""}"' in overview
    graph_css = (ASSETS / "views" / "graph.css").read_text()
    unknown = re.search(r'\.gx \.gx-box\[data-st="unknown"\] \{[^}]*\}', graph_css)
    assert unknown and "--ds-warn" not in unknown.group(0)


# --- T-07: motion only where it belongs ------------------------------------------------------------------------


def test_reduced_motion_hides_only_the_blinking_overlay() -> None:
    assert re.search(r'\.st-ico\[data-live="1"\] \.sd-nx \{[^}]*animation: sd-next', APP_CSS)
    reduced = re.findall(r"@media \(prefers-reduced-motion: reduce\) \{(.*?)\n\}", APP_CSS, re.S)
    # the reduced rule must win over the blinking rule: the same selector (an attribute selector raises it)
    assert any(
        re.search(r'\.st-ico\[data-live="1"\] \.sd-nx[^{]*\{[^}]*animation: none[^}]*opacity: 0', block)
        for block in reduced
    )


def test_list_screens_never_ask_for_motion_and_every_screen_draws_with_state_mark() -> None:
    lists = ["views/board.js", "views/overview.js", "views/todos.js", "views/_shared/search.js", "views/timeline.js"]
    for rel in lists:
        assert "motion: true" not in (ASSETS / rel).read_text(), rel
    for rel in ("views/graph.js", "views/scope.js"):
        assert "motion: true" in (ASSETS / rel).read_text(), rel
    for rel in (
        "views/graph.js",
        "views/_shared/scope_tabs.js",
        "views/board.js",
        "views/overview.js",
        "views/_shared/search.js",
    ):
        assert "stateMark(" in (ASSETS / rel).read_text(), rel
    graph = (ASSETS / "views" / "graph.js").read_text()
    for place in ('<div class="gx-r1">', '<p class="pn-why" data-st="${s.state}">'):  # the box and the panel's reason
        assert re.search(re.escape(place) + r"\$\{M\.stateMark\(s, V\.ix\.byId, \{ motion: true", graph), place
    assert "${M.stateChip(s, V.ix.byId, { motion: true })}" in graph  # the panel's chip


def test_the_shell_redraws_when_the_live_window_ends() -> None:
    app = (ASSETS / "app.js").read_text()
    assert "liveUntil" in app
    assert re.search(r"revision === state\.revision\)[\s\S]{0,300}liveUntil", app)


# --- T-05, T-06: the marks under node --------------------------------------------------------------------------


def _node() -> str:
    found = shutil.which("node")
    if found is None:
        if os.environ.get("CI"):
            pytest.fail("node is required on CI for the state marks check (iss-00574)")
        pytest.skip("node is not installed")
    return found


def _run(script: str, tmp_path: Path) -> dict:
    runner = tmp_path / "check.mjs"
    runner.write_text(
        f"const ui = await import({json.dumps((ASSETS / 'core' / 'ui.js').as_uri())});\n"
        "const out = {};\n" + textwrap.dedent(script) + "\nconsole.log(JSON.stringify(out));\n"
    )
    done = subprocess.run([_node(), str(runner)], capture_output=True, text=True, timeout=60, check=False)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout.strip().splitlines()[-1])


def _segments(svg: str) -> list[tuple[str, float]]:
    """(class, stroke width) of every arc path in a ring."""
    return [
        (cls, float(width))
        for cls, width in re.findall(r'<path class="([^"]*)" d="M[^"]*A[^"]*" [^>]*stroke-width="([\d.]+)"', svg)
    ]


def test_every_state_shape_fits_the_circle(tmp_path: Path) -> None:
    out = _run(
        """
        out.svg = Object.fromEntries(["ready", "doing", "blocked", "unknown", "done"].map((s) => [s, ui.stateIcon(s)]));
        out.ring = ui.stateIcon("doing", true, { progress: { done: 3, total: 8 } });
        """,
        tmp_path,
    )
    for state, svg in [*out["svg"].items(), ("ring", out["ring"])]:
        for attrs in re.findall(r"<circle ([^>]*)>", svg):
            radius = re.search(r'\br="([\d.]+)"', attrs)
            assert radius, (state, attrs)
            r = float(radius.group(1))
            width = re.search(r'stroke-width="([\d.]+)"', attrs)
            assert r + (float(width.group(1)) / 2 if width else 0) <= 10.5, (state, attrs)
        for x, y in re.findall(r"[MA][^\"]*?([\d.]+) ([\d.]+)(?=[A\"M]|$)", svg):
            assert math.hypot(float(x) - 12, float(y) - 12) <= 10.5, (state, x, y)
    assert 'aria-label="着手できる"' in out["svg"]["ready"]
    assert "<circle" in out["svg"]["blocked"] and out["svg"]["blocked"].count('class="on"') == 2  # ‖
    assert "?" not in out["svg"]["unknown"] and "<circle" in out["svg"]["unknown"]


def test_the_ring_shows_the_plan_steps(tmp_path: Path) -> None:
    out = _run(
        """
        const r = (done, total, live = false) => ui.progressRing(total == null ? null : { done, total }, { live });
        out.cases = { a: r(0, 8), b: r(4, 8), c: r(8, 8), d: r(3, 4), e: r(5, 13), f: r(0, null), g: r(0, 0) };
        out.live = { b: r(4, 8, true), c: r(8, 8, true), e: r(5, 13, true), f: r(0, null, true) };
        out.label = ui.stateIcon("doing", true, { progress: { done: 4, total: 8 } });
        out.epic = ui.stateIcon("doing", true, { progress: { done: 2, total: 5 }, unit: "配下" });
        """,
        tmp_path,
    )
    cases = out["cases"]
    for key, done, total in (("a", 0, 8), ("b", 4, 8), ("c", 8, 8), ("d", 3, 4)):
        segments = _segments(cases[key])
        assert len(segments) == total, key
        assert [cls for cls, _ in segments] == ["f"] * done + ["t"] * (total - done), key
        assert all(math.isclose(width, 3.6 if cls == "f" else 1.4) for cls, width in segments), key
        assert "sd-nx" not in cases[key]
    # more than 12 steps: a track circle and one arc of the done part
    assert len(_segments(cases["e"])) == 1 and 'class="t"' in cases["e"] and "<circle" in cases["e"]
    # no steps: the outline only
    for key in ("f", "g"):
        assert "<path" not in cases[key] and cases[key].count("<circle") == 1
    live = out["live"]
    assert _segments(live["b"])[-1] == ("sd-nx f", 3.6) and len(_segments(live["b"])) == 9
    assert re.search(r'<circle class="sd-nx"[^>]*r="3"', live["c"])  # all done: the center dot blinks
    assert "sd-nx" in live["e"]
    assert re.search(r'<circle class="sd-nx"[^>]*stroke-width="3.6"', live["f"])  # an overlay, not the outline
    assert 'aria-label="作業中（手順 4／8 終わった）"' in out["label"]
    assert 'aria-label="作業中（配下 2／5 終わった）"' in out["epic"]


def test_moved_time_liveness_and_idle_words(tmp_path: Path) -> None:
    out = _run(
        """
        const now = Date.parse("2026-11-05T12:00:00Z");
        const m = (min) => new Date(now - min * 60000).toISOString();
        const scopes = [
          { id: "epic-00001", kind: "epic", state: "doing", children: ["iss-00002", "iss-00003", "iss-00004"], active_at: m(500) },
          { id: "iss-00002", kind: "issue", state: "doing", children: [], active_at: m(300), progress: { done: 1, total: 4, modified_at: m(29) } },
          { id: "iss-00003", kind: "issue", state: "done", children: [], active_at: m(400) },
          { id: "iss-00004", kind: "issue", state: "doing", children: [], active_at: m(31), progress: null },
          { id: "iss-00005", kind: "issue", state: "doing", children: [], active_at: "?" },
        ];
        const byId = new Map(scopes.map((s) => [s.id, s]));
        const get = (id) => byId.get(id);
        out.moved = scopes.map((s) => ui.movedAt(s, byId));
        out.live = scopes.map((s) => ui.isLive(ui.movedAt(s, byId), now));
        out.idle = scopes.map((s) => ui.idleText(s, byId, now));
        out.words = [0, 59, 61, 47 * 60 + 59, 48 * 60, 72 * 60].map((min) => ui.idleWords(min * 60000));
        out.epicProgress = ui.scopeProgress(get("epic-00001"), byId);
        out.issueProgress = ui.scopeProgress(get("iss-00002"), byId);
        out.readyProgress = ui.scopeProgress({ ...get("iss-00002"), state: "ready" }, byId);
        out.boxLive = ui.stateMark(get("iss-00002"), byId, { now, motion: true });
        out.boxStill = ui.stateMark(get("iss-00004"), byId, { now, motion: true });
        out.listLive = ui.stateMark(get("iss-00002"), byId, { now, motion: false });
        out.ready = ui.stateMark({ id: "x", kind: "issue", state: "ready" }, byId, { now, motion: true });
        out.LIVE_MS = ui.LIVE_MS;
        """,
        tmp_path,
    )
    now = 1_793_880_000_000  # 2026-11-05T12:00:00Z
    assert out["moved"] == [now - 29 * 60000, now - 29 * 60000, now - 400 * 60000, now - 31 * 60000, None]
    assert out["live"] == [True, True, False, False, False]
    assert out["idle"] == ["", "", "", "31分動きなし", ""]  # a done Scope and an unknown time say nothing
    assert out["words"] == [
        "1分以内動きなし",
        "59分動きなし",
        "1時間動きなし",
        "47時間動きなし",
        "2日動きなし",
        "3日動きなし",
    ]
    assert out["epicProgress"] == {"done": 1, "total": 3}
    assert out["issueProgress"] == {"done": 1, "total": 4}
    assert out["readyProgress"] is None
    assert 'data-live="1"' in out["boxLive"] and "sd-nx" in out["boxLive"]
    assert "data-live" not in out["boxStill"] and "sd-nx" not in out["boxStill"]
    assert "data-live" not in out["listLive"] and "sd-nx" not in out["listLive"]
    assert len(_segments(out["listLive"])) == 4
    assert out["ready"] == _run('out.x = ui.stateIcon("ready");', tmp_path)["x"]
    assert out["LIVE_MS"] == 30 * 60 * 1000
