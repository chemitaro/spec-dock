"""DOM boundaries for dashboard marks and the open button (iss-00592 T-02)."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import textwrap

import pytest

DASHBOARD = Path(__file__).resolve().parents[3] / "src/spec_dock/assets/dashboard"
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node is not installed")


DOM = """
class Slot {
  constructor(scope = "iss-00001", max = "2") {
    this.dataset = {orcaScope: scope, orcaMax: max};
    this.children = [];
    this.replacements = 0;
  }
  replaceChildren(...children) {this.children = children; this.replacements++;}
  append(child) {this.children.push(child);}
  set innerHTML(value) {throw new Error("scripts must use the element API");}
}
const rootOf = (...slots) => ({querySelectorAll(selector) {
  assert.equal(selector, "[data-orca-scope]"); return slots;
}});
"""


def run_node(script: str, tmp_path: Path) -> None:
    runner = tmp_path / "check.mjs"
    runner.write_text(
        'import assert from "node:assert/strict";\n'
        + f"const ui = await import({json.dumps((DASHBOARD / 'views/_shared/orca_marks.js').as_uri())});\n"
        + DOM
        + textwrap.dedent(script)
    )
    done = subprocess.run([NODE, str(runner)], capture_output=True, text=True, timeout=30)  # type: ignore[list-item]
    assert done.returncode == 0, done.stderr


def test_paint_preserves_children_for_equal_views_and_paints_new_slots(tmp_path: Path) -> None:
    run_node(
        """
        const one = new Slot(), other = new Slot("iss-00002", "4"), missing = new Slot("iss-00003");
        missing.children = [{stale: true}];
        const structure = {};
        const worktree = {id: "w", agents: [{id: "a"}]};
        let clock = 60000, reads = 0;
        Date.now = () => {reads++; return clock;};
        const builds = [], renders = [];
        const module = {
          buildMarks(w, options) {
            assert.equal(w, worktree); builds.push(options);
            return {marks: [{elapsed: clock < 120000 ? "1m" : "2m"}], overflow: null};
          },
          renderAgentMarks(slot, w, options) {
            assert.equal(w, worktree); renders.push(options); slot.replaceChildren({mark: "working"});
          },
        };
        const orca = {status: () => "ok", marks: () => module, forScope(data, id) {
          assert.equal(data, structure); return id === "iss-00003" ? [] : [worktree];
        }};
        const ctx = {orca};
        const root = rootOf(one, other, missing);
        ui.paintOrcaMarks(root, ctx, structure);
        assert.equal(reads, 1);
        assert.deepEqual(builds, [{now: 60000, max: 2}, {now: 60000, max: 4}]);
        assert.deepEqual(renders, [{size: "sm", max: 2, now: 60000}, {size: "sm", max: 4, now: 60000}]);
        assert.deepEqual(missing.children, []);
        const first = one.children[0], second = other.children[0];
        ui.paintOrcaMarks(root, ctx, structure);
        assert.equal(renders.length, 2);
        assert.equal(one.children[0], first);
        assert.equal(other.children[0], second);
        clock = 120000;
        ui.paintOrcaMarks(root, ctx, structure);
        assert.equal(renders.length, 4);
        assert.notEqual(one.children[0], first);
        const fresh = new Slot();
        ui.paintOrcaMarks(rootOf(fresh), ctx, structure);
        assert.equal(renders.length, 5);
        assert.equal(fresh.children.length, 1);
        """,
        tmp_path,
    )


def test_paint_clears_unavailable_slots_and_recovers(tmp_path: Path) -> None:
    run_node(
        """
        const slot = new Slot();
        let status = "ok", available = true, renders = 0;
        const module = {buildMarks: () => ({marks: [{id: "a"}], overflow: null}),
          renderAgentMarks(slot) {renders++; slot.replaceChildren({id: "a"});}};
        const ctx = {orca: {status: () => status, marks: () => available ? module : null,
          forScope: () => [{id: "w"}]}};
        const root = rootOf(slot);
        for (const unavailable of ["off", "loading", "unreachable", "orca-unreachable", "orca-starting"]) {
          ui.paintOrcaMarks(root, ctx, {});
          assert.equal(slot.children.length, 1);
          status = unavailable;
          ui.paintOrcaMarks(root, ctx, {});
          assert.deepEqual(slot.children, []);
          status = "ok";
        }
        ui.paintOrcaMarks(root, ctx, {});
        available = false;
        ui.paintOrcaMarks(root, ctx, {});
        assert.deepEqual(slot.children, []);
        available = true;
        ui.paintOrcaMarks(root, ctx, {});
        assert.equal(renders, 7);
        ui.paintOrcaMarks(root, {orca: null}, {});
        assert.deepEqual(slot.children, []);
        """,
        tmp_path,
    )


def test_paint_isolates_component_failures_and_retries_cleared_slots(tmp_path: Path) -> None:
    run_node(
        """
        for (const failAt of ["build", "render", "lookup"]) {
          const bad = new Slot("bad"), good = new Slot("good");
          let failing = false;
          let version = 1;
          const module = {
            buildMarks(w) {
              if (failing && w.id === "bad" && failAt === "build") throw new Error("broken build");
              return {marks: [{version}], overflow: null};
            },
            renderAgentMarks(slot) {
              slot.replaceChildren({partial: failing});
              if (failing && slot === bad && failAt === "render") throw new Error("broken render");
            },
          };
          const ctx = {orca: {status: () => "ok", marks: () => module, forScope(_, id) {
            if (failing && id === "bad" && failAt === "lookup") throw new Error("broken lookup");
            return [{id}];
          }}};
          const root = rootOf(bad, good);
          ui.paintOrcaMarks(root, ctx, {});
          const oldGood = good.children[0];
          failing = true; version = 2;
          assert.doesNotThrow(() => ui.paintOrcaMarks(root, ctx, {}));
          assert.deepEqual(bad.children, []);
          assert.notEqual(good.children[0], oldGood);
          failing = false; version = 1;
          ui.paintOrcaMarks(root, ctx, {});
          assert.equal(bad.children.length, 1);
        }
        """,
        tmp_path,
    )


def test_open_button_preserves_script_and_frame_until_target_changes(tmp_path: Path) -> None:
    run_node(
        """
        const slot = new Slot();
        const doc = {createElement(tag) {assert.equal(tag, "script"); return {dataset: {}};}};
        let status = "ok", list = [{id: "first"}, {id: "second"}];
        const structure = {};
        const orca = {origin: "http://127.0.0.1:8791", status: () => status,
          forScope: data => {assert.equal(data, structure); return list;}};
        const input = {orca, structure, scopeId: "iss-00001", embed: false, theme: "light"};
        const button = ui.createOpenButton(slot, {doc});
        button.update(input);
        assert.equal(slot.children.length, 1);
        const script = slot.children[0];
        assert.equal(script.src, "http://127.0.0.1:8791/embed/open-button.js");
        assert.deepEqual(script.dataset, {worktree: "first", theme: "light", size: "sm"});
        const frame = {tag: "iframe"};
        slot.append(frame);
        button.update(input);
        assert.equal(slot.children[0], script);
        assert.equal(slot.children[1], frame);
        button.update({...input, theme: "dark"});
        assert.equal(slot.children.length, 1);
        assert.notEqual(slot.children[0], script);
        assert.deepEqual(slot.children[0].dataset, {worktree: "first", theme: "dark", size: "sm"});
        const dark = slot.children[0];
        button.update({...input, theme: "dark", scopeId: "iss-00002"});
        assert.notEqual(slot.children[0], dark);
        list = [{id: "changed"}];
        button.update(input);
        assert.equal(slot.children[0].dataset.worktree, "changed");
        button.update({...input, embed: true});
        assert.deepEqual(slot.children, []);
        button.update(input);
        assert.equal(slot.children.length, 1);
        for (const unavailable of ["off", "loading", "unreachable", "orca-unreachable", "orca-starting"]) {
          status = unavailable;
          button.update(input);
          assert.deepEqual(slot.children, []);
          status = "ok";
          button.update(input);
          assert.equal(slot.children.length, 1);
        }
        for (const invalid of [[], [{}], [{id: ""}], [{id: 12}]]) {
          list = invalid; button.update(input); assert.deepEqual(slot.children, []);
        }
        list = [{id: "first"}];
        button.update(input);
        const beforeReset = slot.children[0];
        button.reset();
        assert.deepEqual(slot.children, []);
        button.update(input);
        assert.notEqual(slot.children[0], beforeReset);
        button.update({...input, orca: null});
        assert.deepEqual(slot.children, []);
        const fresh = new Slot();
        ui.createOpenButton(fresh, {doc}).update(input);
        assert.equal(fresh.children.length, 1);
        """,
        tmp_path,
    )


def test_slots_have_shared_layout_rules_and_scripts_use_element_api() -> None:
    css = (DASHBOARD / "app.css").read_text()
    assert "\n.sd-orca { display: inline-flex; flex: none; margin-left: auto; }" in css
    assert "\n.sd-orca:empty { display: none; }" in css
    assert ".orca-mark" not in css
    source = (DASHBOARD / "views/_shared/orca_marks.js").read_text()
    assert 'doc.createElement("script")' in source
    assert "innerHTML" not in source
    assert "dataset.width" not in source
    assert "dataset.label" not in source
