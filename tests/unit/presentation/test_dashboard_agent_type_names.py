"""The agents' kinds named by orca-web's marks component on the graphs (iss-00674 T-02).

`countTitle` of `views/graph/unscoped.js` under node with a synthetic component, then `views/graph.js` and
`views/allgraph.js` with the fake DOM and the fake orca (`tests/js/dashboard_graph_command_screen.mjs`,
`tests/js/dashboard_allgraph_command_screen.mjs`): with a component that knows antigravity (a run's `orca.names`) the
count's title of the Unscoped row, the worktree's panel and the agent's panel name it "Antigravity"; without one they
keep the raw text. Every value is synthetic.
"""

from __future__ import annotations

import json
import subprocess
import textwrap
from typing import TYPE_CHECKING, Any

import pytest

from tests.unit.presentation import (
    test_dashboard_allgraph_command_screen as AS,
    test_dashboard_graph_command_screen as GS,
)
from tests.unit.presentation.test_dashboard_graph_command import ag, summary, wt
from tests.unit.presentation.test_dashboard_graph_js import ASSETS, _node
from tests.unit.presentation.test_dashboard_graph_unscoped import git, row

if TYPE_CHECKING:
    from pathlib import Path

UNSCOPED = ASSETS / "views" / "graph" / "unscoped.js"


def test_count_title_names_each_part_from_the_component(tmp_path: Path) -> None:
    """R-01, R-02, F-01: the parts' kinds by the component's labels; raw text or "agent" otherwise."""
    script = tmp_path / "check.mjs"
    script.write_text(
        'import assert from "node:assert/strict";\n'
        + f"const U = await import({json.dumps(UNSCOPED.as_uri())});\n"
        + textwrap.dedent(
            """
            const shape = {viewBox: "0 0 16 16", paths: []};
            const names = {
              AGENT_ICONS: {claude: {label: "Claude", ...shape}, antigravity: {label: "Antigravity", ...shape}, other: {label: "ほかの種類", ...shape}},
              iconKey: (t) => (t === "claude" || t === "claude-agent-teams" ? "claude" : t === "antigravity" ? t : t ? "other" : "none"),
            };
            const item = {count: 4, countParts: [
              {agentType: "antigravity", index: 1, n: 1}, {agentType: "claude-agent-teams", index: 2, n: 1},
              {agentType: "cursor", index: 3, n: 1}, {agentType: null, index: 4, n: 1},
            ]};
            assert.equal(U.countTitle(item, names), "4 agents in progress — Antigravity #1: 1, Claude #2: 1, cursor #3: 1, agent #4: 1");
            const plain = "4 agents in progress — antigravity #1: 1, claude-agent-teams #2: 1, cursor #3: 1, agent #4: 1";
            assert.equal(U.countTitle(item), plain);
            for (const marks of [null, {}, {AGENT_ICONS: names.AGENT_ICONS, iconKey: () => { throw new Error("broken"); }}]) {
              assert.equal(U.countTitle(item, marks), plain);
            }
            assert.equal(U.countTitle({count: 0}, names), null);
            """
        )
    )
    done = subprocess.run([_node(), str(script)], capture_output=True, text=True, timeout=60, check=False)
    assert done.returncode == 0, done.stderr


def _ag(agent_id: str, parent: str | None = None) -> dict[str, Any]:
    return ag(agent_id, parent=parent, agentType="antigravity") | {"w": 36}


DOC = git(row("/w/u-a", "topic-a")) | {"revision": "r1"}
SUMMARY = summary(
    wt("wt-main", "/w/r", "main", [_ag("a-coord")], main=True),
    wt("wt-a", "/w/u-a", "topic-a", [_ag("a-1", parent="a-coord")]),
)
STEPS = [{"tap": '[data-cmd-wt="wt-a"]'}, {"click": '.panel [data-wt-agent="a-1"]'}]


def _graph_runs(tmp_path: Path) -> dict[str, list[dict[str, Any]]]:
    runs = [
        {
            "name": name,
            "orca": {"summary": SUMMARY, "names": names},
            "doc": DOC,
            "range": rng,
            "steps": STEPS if rng == "all" else [],
        }
        for name, names, rng in (
            ("named", True, "all"),
            ("plain", False, "all"),
            ("named-next", True, "next"),
            ("plain-next", False, "next"),
        )
    ]
    return GS._run(tmp_path, {"doc": DOC, "runs": runs})["runs"]


@pytest.fixture(scope="module")
def graph(tmp_path_factory: pytest.TempPathFactory) -> dict[str, list[dict[str, Any]]]:
    return _graph_runs(tmp_path_factory.mktemp("agent-names-graph"))


@pytest.mark.parametrize(("name", "kind"), [("named", "Antigravity"), ("plain", "antigravity")])
def test_the_graph_panels_name_the_kind(graph: dict[str, list[dict[str, Any]]], name: str, kind: str) -> None:
    """R-01, R-02: the worktree's panel lists the agent, the agent's panel heads and titles its chat by the name."""
    first, wtp, chat = graph[name]
    assert wtp["row"]["panel"]["wt"] == "wt-a" and wtp["row"]["panel"]["agentTexts"] == [kind]
    assert chat["panel"]["agent"] == "a-1"
    assert chat["panel"]["text"].startswith(f"{kind} · ")
    assert chat["panel"]["iframe"]["title"] == f"エージェント：{kind}・topic-a"
    assert all(it["count"] is None for it in first["row"]["items"])


@pytest.mark.parametrize(("name", "kind"), [("named-next", "Antigravity"), ("plain-next", "antigravity")])
def test_the_graph_count_title_names_the_kind(graph: dict[str, list[dict[str, Any]]], name: str, kind: str) -> None:
    """R-01, R-02: drawCommand passes the component, so the drawn count's title names the commanding agent."""
    count = graph[name][0]["row"]["items"][0]["count"]
    assert count["title"] == f"1 agent in progress — {kind} #1: 1" and count["aria"] == count["title"]


A_DOCS = {
    AS.key("a"): AS.doc("/w/a", {"iss-00002": "/w/a-2"}, git=(("/w/a-x", "topic-x"),)),
    AS.key("c"): AS.doc("/w/c", {"iss-00002": "/w/c-2"}),
}


def _a_ag(agent_id: str, parent: str | None = None) -> dict[str, Any]:
    return AS.ag(agent_id, parent=parent) | {"agentType": "antigravity"}


A_SUMMARY = AS.summary(
    AS.wt("wt-a", "/w/a", "main", [_a_ag("a-coord")], AS.PROJ["a"], main=True),
    AS.wt("wt-ax", "/w/a-x", "topic-x", [_a_ag("x-1", parent="a-coord")], AS.PROJ["a"]),
)


@pytest.mark.parametrize(("names", "kind"), [(True, "Antigravity"), (False, "antigravity")])
def test_the_cross_count_title_names_the_kind(tmp_path: Path, names: bool, kind: str) -> None:
    """R-01, R-02: the cross-repository structure's drawCommand passes the component too."""
    run = {
        "name": "x",
        "orca": {"summary": A_SUMMARY, "names": names},
        "repos": AS.REPOS,
        "docs": A_DOCS,
        "range": "next",
        "steps": [{"tap": '[data-cmd-agent="a-coord"]'}],
    }
    path = tmp_path / "request.json"
    path.write_text(json.dumps({"runs": [run]}), encoding="utf-8")
    done = subprocess.run(
        [_node(), str(AS.HARNESS), str(ASSETS), str(path)], capture_output=True, text=True, timeout=600, check=False
    )
    assert done.returncode == 0, done.stderr
    first, chat = json.loads(done.stdout)["runs"]["x"]["shots"]
    titles = [it["countTitle"] for it in first["bandItems"] if it["countTitle"]]
    assert titles == [f"1 agent in progress — {kind} #1: 1"]
    assert chat["panel"]["agent"] == "a-coord" and chat["panel"]["head"].startswith(f"{kind} · ")
