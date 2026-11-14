"""The pure agent choice of the agents tab under node (iss-00593 T-01〜T-03, D-01)."""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
import textwrap

import pytest

LOGIC = Path(__file__).resolve().parents[3] / "src/spec_dock/assets/dashboard/views/_shared/agents_logic.js"
NODE = shutil.which("node")
node = pytest.mark.skipif(NODE is None, reason="node is not installed")

SANDBOX = "allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox"

COMMON = """
const agent = (id, extra = {}) => ({id, mark: "working", agentType: "claude", detail: "/embed/agent?id=" + encodeURIComponent(id), ...extra});
const tree = (id, branch, agents) => ({id, path: "/w/" + id, branch, agents});
const ids = (list) => list.map((item) => item.id);
const none = new Set();
"""


def run_node(script: str, tmp_path: Path) -> None:
    runner = tmp_path / "check.mjs"
    runner.write_text(
        'import assert from "node:assert/strict";\n'
        + f"const logic = await import({json.dumps(LOGIC.as_uri())});\n"
        + COMMON
        + textwrap.dedent(script)
    )
    done = subprocess.run([NODE, str(runner)], capture_output=True, text=True, timeout=30)  # type: ignore[list-item]
    assert done.returncode == 0, done.stderr


def test_the_logic_module_is_pure() -> None:
    source = LOGIC.read_text(encoding="utf-8")
    assert not re.search(r"^\s*import\b", source, re.MULTILINE)
    for word in ("window", "document", "fetch", "postMessage", "/api/", "location", "localStorage"):
        assert word not in source, word


@node
def test_visibility_table(tmp_path: Path) -> None:  # T-01
    run_node(
        """
        const one = [{id: "a"}];
        const two = [{id: "a"}, {id: "b"}];
        const base = {status: "ok", problem: null, records: 1, agents: one, invalid: 0, invalidIds: none, wanted: null, goneIds: none, embed: false};
        const v = (patch) => logic.agentsVisibility({...base, ...patch});
        const hidden = {show: false, reason: null};
        assert.deepEqual(v({status: "off", agents: []}), hidden);
        assert.deepEqual(v({status: "off", agents: [], problem: "bad orca_web"}), {show: true, reason: "config"});
        for (const status of ["off", "ok", "loading", "unreachable", "orca-unreachable", "orca-starting"]) {
          assert.deepEqual(v({status, records: 0, problem: status === "off" ? "bad" : null}), hidden, status);
          assert.deepEqual(v({status, records: 0, wanted: "a", goneIds: new Set(["a"])}), hidden, status);
        }
        for (const status of ["loading", "unreachable", "orca-unreachable", "orca-starting"]) {
          assert.deepEqual(v({status, agents: []}), {show: true, reason: status});
        }
        assert.deepEqual(v({agents: two}), {show: true, reason: null});
        assert.deepEqual(v({agents: []}), hidden);
        assert.deepEqual(v({agents: [], wanted: "a"}), {show: true, reason: null});
        assert.deepEqual(v({agents: [], wanted: "gone:a"}), {show: true, reason: null});
        assert.deepEqual(v({agents: [], goneIds: new Set(["a"])}), {show: true, reason: null});
        assert.deepEqual(v({agents: [], invalid: 1}), {show: true, reason: "shape"});
        assert.deepEqual(v({agents: one, invalid: 1, invalidIds: new Set(["x"])}), {show: true, reason: null});
        assert.deepEqual(v({agents: one, invalid: 1, invalidIds: new Set(["b"]), wanted: "b"}), {show: true, reason: "shape"});
        assert.deepEqual(v({agents: [], invalid: 1, invalidIds: new Set(["b"]), wanted: "b"}), {show: true, reason: "shape"});
        assert.deepEqual(v({embed: true}), {show: true, reason: "embed"});
        assert.deepEqual(v({embed: true, status: "unreachable"}), {show: true, reason: "embed"});
        assert.deepEqual(v({embed: true, problem: "bad"}), {show: true, reason: "config"});
        assert.deepEqual(v({embed: true, status: "off", problem: null}), hidden);
        assert.deepEqual(v({problem: "bad"}), {show: true, reason: "config"});
        assert.deepEqual(v({status: "strange"}), hidden);
        assert.deepEqual(v({status: undefined}), hidden);
        // Missing sets and counts are read as empty.
        assert.deepEqual(logic.agentsVisibility({status: "ok", records: 1, agents: one}), {show: true, reason: null});
        assert.deepEqual(logic.agentsVisibility({status: "ok", records: 1, agents: []}), hidden);
        """,
        tmp_path,
    )


@node
def test_pick_agent_table(tmp_path: Path) -> None:  # T-02 pickAgent
    run_node(
        """
        const a = {id: "a"}, b = {id: "b"}, c = {id: "c"};
        const pick = (agents, wanted, goneIds) => logic.pickAgent(agents, wanted, goneIds);
        const nothing = {selected: null, gone: false, remember: null, addGone: null, addGoneStale: false};
        assert.deepEqual(pick([a], null, none), {selected: a, gone: false, remember: "a", addGone: null, addGoneStale: false});
        assert.deepEqual(pick([a], null), {selected: a, gone: false, remember: "a", addGone: null, addGoneStale: false});
        assert.deepEqual(pick([a, b], null, none), nothing);
        assert.deepEqual(pick([], null, none), nothing);
        for (const agents of [[a, b], [a, b, c], [b, c, a]]) {
          assert.deepEqual(pick(agents, "b", none), {selected: b, gone: false, remember: null, addGone: null, addGoneStale: false});
        }
        assert.deepEqual(pick([a], "b", none), {selected: null, gone: true, remember: "gone:b", addGone: "b", addGoneStale: false});
        assert.deepEqual(pick([a, c], "b", none), {selected: null, gone: true, remember: "gone:b", addGone: "b", addGoneStale: false});
        assert.deepEqual(pick([], "b", none), {selected: null, gone: true, remember: "gone:b", addGone: "b", addGoneStale: false});
        for (const agents of [[], [a], [a, b]]) {
          assert.deepEqual(pick(agents, "gone:b", none), {selected: null, gone: true, remember: null, addGone: "b", addGoneStale: true});
        }
        assert.deepEqual(pick([a, b], "b", new Set(["b"])), {selected: null, gone: true, remember: "gone:b", addGone: null, addGoneStale: false});
        assert.deepEqual(pick([a], "a", new Set(["a"])), {selected: null, gone: true, remember: "gone:a", addGone: null, addGoneStale: false});
        assert.deepEqual(pick([], "a", new Set(["a"])), {selected: null, gone: true, remember: "gone:a", addGone: null, addGoneStale: false});
        assert.deepEqual(pick([a], null, new Set(["b"])), {selected: null, gone: true, remember: null, addGone: null, addGoneStale: false});
        assert.deepEqual(pick([a, b], "a", new Set(["b"])), {selected: a, gone: false, remember: null, addGone: null, addGoneStale: false});
        """,
        tmp_path,
    )


@node
def test_strip_form_and_memory(tmp_path: Path) -> None:  # T-02 stripForm and the memory
    run_node(
        """
        const a = {id: "a"}, b = {id: "b"};
        assert.equal(logic.stripForm([a], a, false), "label");
        assert.equal(logic.stripForm([a], null, true), "switch");
        assert.equal(logic.stripForm([a], null, false), "switch");
        assert.equal(logic.stripForm([a, b], a, false), "switch");
        assert.equal(logic.stripForm([a, b], null, false), "switch");

        const mem = logic.createAgentMemory();
        assert.deepEqual({...mem, gone: [...mem.gone]}, {scopeId: null, gone: [], picked: null, drift: null});
        assert.equal(logic.memoryFor(mem, "iss-00001"), mem);
        logic.noteGone(mem, "a", {stale: false});
        logic.noteDrift(mem, "b");
        mem.picked = "c";
        logic.memoryFor(mem, "iss-00001"); // the same Scope keeps everything
        assert.deepEqual([...mem.gone], ["a"]);
        assert.equal(mem.drift, "b");
        assert.equal(mem.picked, "c");
        logic.memoryFor(mem, "iss-00002"); // another Scope drops it
        assert.equal(mem.scopeId, "iss-00002");
        assert.deepEqual([...mem.gone], []);
        assert.equal(mem.picked, null);
        assert.equal(mem.drift, null);

        logic.forgetGone(mem, "x");
        assert.equal(mem.picked, "x");
        logic.noteGone(mem, "x", {stale: true}); // an old gone:x in the query after the person picked x
        assert.deepEqual([...mem.gone], []);
        assert.equal(mem.picked, "x");
        logic.noteGone(mem, "y", {stale: true}); // an old gone:y for another id
        assert.deepEqual([...mem.gone], ["y"]);
        assert.equal(mem.picked, "x");
        logic.noteGone(mem, "x", {stale: false}); // x really went away
        assert.deepEqual([...mem.gone].sort(), ["x", "y"]);
        assert.equal(mem.picked, null);
        logic.noteGone(mem, "z");
        assert.deepEqual([...mem.gone].sort(), ["x", "y", "z"]);

        logic.noteDrift(mem, "x");
        assert.equal(mem.drift, "x");
        logic.forgetGone(mem, "y");
        assert.deepEqual([...mem.gone], []);
        assert.equal(mem.drift, null);
        assert.equal(mem.picked, "y");
        """,
        tmp_path,
    )


@node
def test_scope_agents(tmp_path: Path) -> None:  # T-02 scopeAgents
    run_node(
        """
        const a = agent("a"), b = agent("b", {agentType: 7}), c = agent("c");
        const real = agent("chat:agent-session:x_y-1");
        const first = tree("w1", "one", [a, b]);
        const second = tree("w2", null, [c, real]);
        const result = logic.scopeAgents([first, second]);
        assert.deepEqual(Object.keys(result).sort(), ["agents", "invalid", "invalidIds"]);
        assert.deepEqual(ids(result.agents), ["a", "b", "c", "chat:agent-session:x_y-1"]);
        assert.equal(result.invalid, 0);
        assert.deepEqual([...result.invalidIds], []);
        assert.deepEqual(result.agents[0], {id: "a", agentType: "claude", branch: "one", worktreeId: "w1", detail: "/embed/agent?id=a", raw: a});
        assert.equal(result.agents[1].agentType, null);
        assert.equal(result.agents[2].branch, null);
        assert.equal(result.agents[2].worktreeId, "w2");
        assert.equal(result.agents[3].detail, "/embed/agent?id=chat%3Aagent-session%3Ax_y-1");

        const bad = [
          {id: "p", detail: "/embed/agent?id=q"},             // id A, detail B
          {id: "r", detail: "/embed/other?id=r"},             // another path
          {id: "s", detail: "/embed/agent?id=s&x=1"},         // carries &
          {id: "t", detail: 5},                               // not a string
          {id: "u&v", detail: "/embed/agent?id=u&v"},          // not encoded
          {detail: "/embed/agent?id="},                       // no id
          {id: "", detail: "/embed/agent?id="},               // empty id
          {id: 9, detail: "/embed/agent?id=9"},               // id not a string
          null,
          "w",
        ];
        const mixed = logic.scopeAgents([tree("w3", "three", [a, ...bad, agent("a", {agentType: "codex"}), {id: "a", detail: "x"}, {id: "p", detail: "y"}])]);
        assert.deepEqual(ids(mixed.agents), ["a"]);
        assert.equal(mixed.agents[0].agentType, "claude"); // the first one wins
        assert.equal(mixed.invalid, bad.length);
        assert.deepEqual([...mixed.invalidIds].sort(), ["p", "r", "s", "t", "u&v"]);

        for (const input of [null, undefined, {}, "x", 3]) {
          const empty = logic.scopeAgents(input);
          assert.deepEqual(empty.agents, []);
          assert.equal(empty.invalid, 0);
          assert.deepEqual([...empty.invalidIds], []);
        }
        const odd = logic.scopeAgents([null, 4, {id: "w4", branch: "b", agents: null}, {id: "w5", branch: 3, agents: [agent("d")]}]);
        assert.deepEqual(ids(odd.agents), ["d"]);
        assert.equal(odd.agents[0].branch, null);
        assert.equal(odd.invalid, 0);
        """,
        tmp_path,
    )


@node
def test_agent_frame_and_sandbox(tmp_path: Path) -> None:  # T-03
    run_node(
        f"""
        const item = {{id: "chat:a b", agentType: "claude", branch: "chemitaro/iss-00001", detail: "/embed/agent?id=chat%3Aa%20b"}};
        const frame = logic.agentFrame("http://127.0.0.1:8791", item, "dark");
        assert.deepEqual(frame, {{src: "http://127.0.0.1:8791/embed/agent?id=chat%3Aa%20b&theme=dark", title: "エージェント：claude・chemitaro/iss-00001"}});
        assert.deepEqual(logic.agentFrame("http://127.0.0.1:8791", item, "dark"), frame);
        assert.equal(logic.agentFrame("http://127.0.0.1:8791", item, "light").src.endsWith("&theme=light"), true);
        assert.equal(logic.agentFrame("http://127.0.0.1:8791", {{...item, agentType: null, branch: null}}, "light").title, "エージェント：種類不明・ブランチ不明");
        for (const theme of ["auto", null, undefined, "", "DARK"]) assert.equal(logic.agentFrame("http://127.0.0.1:8791", item, theme), null);
        for (const origin of [null, undefined, 5]) assert.equal(logic.agentFrame(origin, item, "dark"), null);
        assert.equal(logic.agentFrame("http://127.0.0.1:8791", null, "dark"), null);
        assert.equal(logic.AGENT_SANDBOX, {json.dumps(SANDBOX)});
        assert.equal(logic.AGENT_SANDBOX.includes("allow-forms"), false);
        assert.equal(logic.AGENT_SANDBOX.includes("allow-top-navigation"), false);
        """,
        tmp_path,
    )
