"""Pure dashboard mark and open-button decisions under node (iss-00592 T-01)."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import textwrap

import pytest

SHARED = Path(__file__).resolve().parents[3] / "src/spec_dock/assets/dashboard/views/_shared"
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node is not installed")


def run_node(script: str, tmp_path: Path) -> None:
    runner = tmp_path / "check.mjs"
    runner.write_text(
        'import assert from "node:assert/strict";\n'
        + f"const logic = await import({json.dumps((SHARED / 'orca_logic.js').as_uri())});\n"
        + textwrap.dedent(script)
    )
    done = subprocess.run([NODE, str(runner)], capture_output=True, text=True, timeout=30)  # type: ignore[list-item]
    assert done.returncode == 0, done.stderr


def test_slot_worktree_requires_ok_and_merges_matches(tmp_path: Path) -> None:
    run_node(
        """
        const structure = {};
        const first = {id: "one", path: "/one", branch: "a", project: {id: "p"},
          agents: [{id: "a"}], counts: {working: 1}};
        const second = {id: "two", agents: [{id: "b"}], counts: {working: 2, waiting: 1}};
        assert.equal(logic.slotWorktree(null, structure, "iss-00001"), null);
        for (const status of ["off", "loading", "unreachable", "orca-unreachable", "orca-starting"]) {
          assert.equal(logic.slotWorktree({status: () => status,
            forScope() {throw new Error("must not look up unavailable data");}}, structure, "iss-00001"), null);
        }
        let list = [];
        const orca = {status: () => "ok", forScope(data, id) {
          assert.equal(data, structure); assert.equal(id, "iss-00001"); return list;
        }};
        assert.equal(logic.slotWorktree(orca, structure, "iss-00001"), null);
        list = [first];
        assert.equal(logic.slotWorktree(orca, structure, "iss-00001"), first);
        list = [first, second];
        assert.deepEqual(logic.slotWorktree(orca, structure, "iss-00001"), {
          id: "one", path: "/one", branch: "a", project: {id: "p"},
          agents: [{id: "a"}, {id: "b"}], counts: {working: 3, waiting: 1},
        });
        assert.deepEqual(first.agents, [{id: "a"}]);
        """,
        tmp_path,
    )


def test_marks_key_tracks_the_component_view(tmp_path: Path) -> None:
    run_node(
        """
        assert.equal(logic.marksKey(null), "");
        const built = {marks: [{id: "a", mark: "working", elapsed: "now"}], overflow: null};
        assert.equal(logic.marksKey(built), '{"marks":[{"id":"a","mark":"working","elapsed":"now"}],"overflow":null}');
        assert.equal(logic.marksKey(built), logic.marksKey(JSON.parse(JSON.stringify(built))));
        for (const changed of [
          {marks: [{id: "a", mark: "working", elapsed: "1m"}], overflow: null},
          {marks: [{id: "a", mark: "waiting", elapsed: "now"}], overflow: null},
          {marks: built.marks, overflow: {count: 2, label: "ほか 2 件"}},
        ]) assert.notEqual(logic.marksKey(built), logic.marksKey(changed));
        """,
        tmp_path,
    )


def test_open_target_uses_first_id_only_when_available_and_not_embedded(tmp_path: Path) -> None:
    run_node(
        """
        const structure = {};
        let list = [{id: "first"}, {id: "second"}];
        let status = "ok";
        const orca = {status: () => status, forScope(data, id) {
          assert.equal(data, structure); assert.equal(id, "iss-00001"); return list;
        }};
        const input = {orca, structure, scopeId: "iss-00001", embed: false, theme: "dark"};
        assert.deepEqual(logic.openTarget(input), {key: "iss-00001|first|dark", worktreeId: "first"});
        assert.deepEqual(logic.openTarget({...input, theme: "light"}),
          {key: "iss-00001|first|light", worktreeId: "first"});
        const empty = {key: "", worktreeId: null};
        assert.deepEqual(logic.openTarget({...input, orca: null}), empty);
        assert.deepEqual(logic.openTarget({...input, embed: true}), empty);
        for (const value of ["off", "loading", "unreachable", "orca-unreachable", "orca-starting"]) {
          status = value; assert.deepEqual(logic.openTarget(input), empty);
        }
        status = "ok";
        for (const invalid of [[], [{}], [{id: ""}], [{id: null}], [{id: 123}, {id: "valid"}]]) {
          list = invalid; assert.deepEqual(logic.openTarget(input), empty);
        }
        """,
        tmp_path,
    )


def test_theme_of_prefers_explicit_theme_then_system(tmp_path: Path) -> None:
    run_node(
        """
        for (const theme of ["light", "dark"]) {
          assert.equal(logic.themeOf({documentElement: {dataset: {theme}}},
            () => {throw new Error("explicit theme must win");}), theme);
        }
        for (const theme of [undefined, "auto", "invalid"]) {
          for (const matches of [false, true]) {
            assert.equal(logic.themeOf({documentElement: {dataset: {theme}}}, query => {
              assert.equal(query, "(prefers-color-scheme: dark)"); return {matches};
            }), matches ? "dark" : "light");
          }
        }
        """,
        tmp_path,
    )
