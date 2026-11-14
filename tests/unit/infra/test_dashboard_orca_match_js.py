"""Pure orca-web matching and status decisions under node (iss-00591 T-06〜T-08)."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import textwrap

import pytest

CORE = Path(__file__).resolve().parents[3] / "src/spec_dock/assets/dashboard/core"
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node is not installed")


def run_node(script: str, tmp_path: Path) -> None:
    runner = tmp_path / "check.mjs"
    runner.write_text(
        'import assert from "node:assert/strict";\n'
        + f"const logic = await import({json.dumps((CORE / 'orca_match.js').as_uri())});\n"
        + textwrap.dedent(script)
    )
    done = subprocess.run([NODE, str(runner)], capture_output=True, text=True, timeout=30)  # type: ignore[list-item]
    assert done.returncode == 0, done.stderr


def test_path_matches_are_normalized_unique_and_do_not_roll_up(tmp_path: Path) -> None:
    run_node(
        """
        const structure = {worktrees: {status: "ok", paths: ["/repo", "/one"]}, scopes: [
          {id: "epic-00001", worktrees: []},
          {id: "iss-00002", worktrees: [{path: "/one/", branch: "feature"}]},
          {id: "iss-00003", worktrees: [{path: "/one", branch: "other"}]},
        ]};
        const matched = {id: "a", path: "/one///", branch: null, project: null};
        const unknown = {id: "iss-00002", issue: "iss-00002", path: null, branch: null, project: null};
        const summary = {schema: "orca-web.worktree-summary/v1", worktrees: [matched, unknown, null, 42]};
        const result = logic.matchWorktrees(structure, summary);
        assert.equal(result.status, "ok");
        assert.deepEqual([...result.byScope], [["iss-00002", [matched]]]);
        assert.equal(result.byScope.has("epic-00001"), false);
        assert.deepEqual(["/", "///", "/one///", "", null, 5].map(logic.normPath), ["/", "/", "/one", "", null, null]);
    """,
        tmp_path,
    )


def test_branch_matches_need_a_project_hint_and_keep_record_then_summary_order(tmp_path: Path) -> None:
    run_node(
        """
        const structure = {worktrees: {status: "ok", paths: ["/repo/", "/first", "/second"]}, scopes: [
          {id: "epic-00001", worktrees: null},
          {id: "iss-00002", worktrees: [{path: "/first", branch: "first"}, {path: "/second", branch: "second"}]},
          {id: "iss-00003", worktrees: [{path: "/third", branch: "first"}]},
        ]};
        const a = {id: "a", path: "/elsewhere-a", branch: "second", project: {id: "p"}};
        const b = {id: "b", path: "/second", branch: "first", project: null};
        const c = {id: "c", path: "/elsewhere-c", branch: "first", project: {id: "p"}};
        const d = {id: "d", path: "/first", branch: null, project: {id: "other"}};
        const hint = {id: "main", path: "/repo", branch: "main", project: {id: "p"}};
        const excluded = [
          {id: "wrong", path: "/elsewhere", branch: "second", project: {id: "wrong", name: "p"}},
          {id: "issue-only", path: null, branch: null, project: null, issue: "iss-00002"},
          {id: "no-project", path: null, branch: "first", project: null},
          {id: "bad-project", path: null, branch: "first", project: {id: 7}},
        ];
        const summary = {schema: "orca-web.worktree-summary/v1", worktrees: [a, b, c, d, hint, ...excluded]};
        const result = logic.matchWorktrees(structure, summary);
        assert.deepEqual([...result.byScope], [["iss-00002", [c, d, a, b]]]);
        // Path wins even if its branch names a different Scope's first record.
        const pathWins = {path: "/third", branch: "second", project: {id: "p"}};
        assert.deepEqual(logic.matchWorktrees(structure, {...summary, worktrees: [hint, pathWins]}).byScope.get("iss-00003"), [pathWins]);
        const noHints = {...structure, worktrees: {status: "ok", paths: []}};
        assert.deepEqual([...logic.matchWorktrees(noHints, summary).byScope], [["iss-00002", [d, b]]]);
    """,
        tmp_path,
    )


def test_unreadable_records_invalid_documents_and_connection_states(tmp_path: Path) -> None:
    run_node(
        """
        assert.equal(logic.SUMMARY_SCHEMA, "orca-web.worktree-summary/v1");
        const valid = {schema: logic.SUMMARY_SCHEMA, worktrees: [], connection: {state: "connected"}, stale: true};
        const structure = {worktrees: {status: "ok", paths: []}, scopes: []};
        for (const summary of [null, {}, {schema: "other", worktrees: []}, {schema: logic.SUMMARY_SCHEMA, worktrees: {}}]) {
          assert.equal(logic.summaryValid(summary), false);
          const result = logic.matchWorktrees(structure, summary);
          assert.equal(result.status, "invalid");
          assert.equal(result.byScope.size, 0);
          assert.equal(logic.orcaStatus({enabled: true, read: "ok", summary}), "unreachable");
        }
        for (const structure of [null, {}, {worktrees: {status: "unreadable", paths: ["/repo"]}}]) {
          const result = logic.matchWorktrees(structure, valid);
          assert.equal(result.status, "no-records");
          assert.equal(result.byScope.size, 0);
          assert.equal(logic.matchWorktrees(structure, null).status, "no-records");
        }
        assert.equal(logic.summaryValid(valid), true);
        assert.equal(logic.orcaStatus({enabled: false, read: "failed", summary: null}), "off");
        assert.equal(logic.orcaStatus({enabled: true, read: "none", summary: null}), "loading");
        assert.equal(logic.orcaStatus({enabled: true, read: "failed", summary: valid}), "unreachable");
        for (const [state, expected] of [["connected", "ok"], ["unreachable", "orca-unreachable"], ["starting", "orca-starting"], ["other", "unreachable"], ["toString", "unreachable"], ["constructor", "unreachable"], ["__proto__", "unreachable"], [null, "unreachable"]]) {
          assert.equal(logic.orcaStatus({enabled: true, read: "ok", summary: {...valid, connection: {state}}}), expected);
        }
    """,
        tmp_path,
    )


def test_merged_worktree_keeps_identity_and_combines_agents_and_counts(tmp_path: Path) -> None:
    run_node(
        """
        const first = {id: "first", path: "/first", branch: "one", project: {id: "p"},
          agents: [{id: "a"}], counts: {working: 1, waiting: "bad", total: 2}};
        const second = {id: "second", path: "/second", branch: "two", project: {id: "other"},
          agents: [{id: "b"}, {id: "c"}], counts: {working: 2, waiting: 1, total: 3, unknown: null}};
        assert.equal(logic.mergedWorktree([]), null);
        assert.equal(logic.mergedWorktree([first]), first);
        const merged = logic.mergedWorktree([first, second]);
        assert.deepEqual(merged, {id: "first", path: "/first", branch: "one", project: {id: "p"},
          agents: [{id: "a"}, {id: "b"}, {id: "c"}], counts: {working: 3, waiting: 1, total: 5, unknown: 0}});
        assert.deepEqual(first.counts, {working: 1, waiting: "bad", total: 2});
        assert.equal(first.agents.length, 1);
    """,
        tmp_path,
    )
