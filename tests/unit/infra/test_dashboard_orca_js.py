"""The shared orca-web reader, using a fake external module and clock (iss-00591 T-09)."""

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
        + f"const {{createOrca}} = await import({json.dumps((CORE / 'orca.js').as_uri())});\n"
        + "const flush = () => new Promise((resolve) => setImmediate(resolve));\n"
        + textwrap.dedent(script)
    )
    done = subprocess.run([NODE, str(runner)], capture_output=True, text=True, timeout=30)  # type: ignore[list-item]
    assert done.returncode == 0, done.stderr


def test_disabled_configs_have_no_external_effects(tmp_path: Path) -> None:
    run_node(
        """
        for (const config of [null, {}, {enabled: false, origin: "http://127.0.0.1:8791"}, {enabled: true}, {enabled: true, origin: 8791}]) {
          const unexpected = () => {throw new Error("disabled reader must do nothing");};
          const orca = createOrca(config, {importModule: unexpected, addStylesheet: unexpected, setTimer: unexpected});
          assert.equal(orca.status(), "off");
          assert.equal(orca.summary(), null);
          assert.equal(orca.marks(), null);
          assert.equal(orca.origin, null);
          assert.deepEqual(orca.forScope(null, "iss-00001"), []);
          orca.subscribe(unexpected)();
          orca.stop();
        }
    """,
        tmp_path,
    )


def test_one_watcher_notifies_caches_matches_and_discards_failed_reads(tmp_path: Path) -> None:
    run_node(
        """
        const origin = "http://127.0.0.1:8791";
        const imports = [], styles = [];
        let callbacks, watching = 0, stops = 0;
        const marks = {watchWorktreeSummary(base, options) {
          assert.equal(base, origin);
          watching++;
          callbacks = options;
          return {stop() {stops++;}};
        }};
        const orca = createOrca({enabled: true, origin}, {
          importModule(url) {imports.push(url); return Promise.resolve(marks);},
          addStylesheet(url) {styles.push(url);},
          setTimer() {throw new Error("successful import must not schedule a retry");},
        });
        assert.equal(orca.status(), "loading");
        assert.equal(orca.summary(), null);
        assert.equal(orca.marks(), null);
        assert.deepEqual(orca.forScope({}, "iss-00001"), []);
        let notices = 0;
        orca.subscribe(() => {throw new Error("subscriber failed");});
        const unsubscribe = orca.subscribe(() => notices++);
        await flush();
        assert.deepEqual(styles, [origin + "/embed/agent-marks.css"]);
        assert.deepEqual(imports, [origin + "/embed/agent-marks.js"]);
        assert.equal(watching, 1);
        assert.equal(orca.marks(), marks);
        assert.equal(orca.origin, origin);
        const structure = {worktrees: {status: "ok", paths: ["/repo", "/one"]}, scopes: [
          {id: "iss-00001", worktrees: [{path: "/one", branch: "feature"}]},
        ]};
        const worktree = {id: "w", path: "/one", branch: "feature", project: {id: "p"}};
        const document = {schema: "orca-web.worktree-summary/v1", connection: {state: "connected"}, worktrees: [worktree]};
        callbacks.onDocument(document);
        assert.equal(orca.status(), "ok");
        assert.equal(orca.summary(), document);
        assert.equal(notices, 1);
        callbacks.onDocument(document);
        assert.equal(notices, 1);
        const matched = orca.forScope(structure, "iss-00001");
        assert.deepEqual(matched, [worktree]);
        assert.equal(orca.forScope(structure, "iss-00001"), matched);
        assert.notEqual(orca.forScope({...structure}, "iss-00001"), matched);
        const cached = orca.forScope(structure, "iss-00001");
        callbacks.onDocument({...document});
        assert.equal(notices, 2);
        assert.notEqual(orca.forScope(structure, "iss-00001"), cached);
        callbacks.onDocument({...document, connection: {state: "starting"}});
        assert.equal(orca.status(), "orca-starting");
        assert.equal(orca.summary(), null);
        assert.deepEqual(orca.forScope(structure, "iss-00001"), []);
        callbacks.onDocument({...document, connection: {state: "unreachable"}});
        assert.equal(orca.status(), "orca-unreachable");
        callbacks.onDocument({schema: "different", worktrees: []});
        assert.equal(orca.status(), "unreachable");
        callbacks.onDocument(document);
        callbacks.onError(new Error("offline"));
        assert.equal(orca.status(), "unreachable");
        assert.equal(orca.summary(), null);
        assert.deepEqual(orca.forScope(structure, "iss-00001"), []);
        const before = notices;
        callbacks.onError(new Error("still offline"));
        assert.equal(notices, before);
        unsubscribe();
        callbacks.onDocument(document);
        assert.equal(notices, before);
        orca.stop();
        orca.stop();
        assert.equal(stops, 1);
        callbacks.onError(new Error("late error"));
        assert.equal(orca.status(), "ok");
    """,
        tmp_path,
    )


def test_failed_imports_retry_with_fresh_urls_and_stop_cancels_pending_retry(tmp_path: Path) -> None:
    run_node(
        """
        const origin = "http://127.0.0.1:8791";
        const imports = [], styles = [], timers = new Map(), cleared = [];
        let nextId = 0, watches = 0, stops = 0;
        const deps = {
          importModule(url) {
            imports.push(url);
            if (imports.length < 3) throw new Error("import failed");
            return Promise.resolve({watchWorktreeSummary() {watches++; return {stop() {stops++;}};}});
          },
          addStylesheet(url) {styles.push(url);},
          setTimer(fn, ms) {assert.equal(ms, 10000); timers.set(nextId, fn); return nextId++;},
          clearTimer(id) {cleared.push(id); timers.delete(id);},
        };
        const orca = createOrca({enabled: true, origin}, deps);
        await flush();
        assert.equal(orca.status(), "unreachable");
        assert.equal(orca.summary(), null);
        assert.equal(watches, 0);
        assert.equal(timers.size, 1);
        const tick = async () => {const [id, fn] = timers.entries().next().value; timers.delete(id); fn(); await flush();};
        await tick();
        assert.equal(timers.size, 1);
        assert.equal(watches, 0);
        await tick();
        assert.equal(timers.size, 0);
        assert.equal(watches, 1);
        assert.equal(styles.length, 1);
        assert.deepEqual(imports, [origin + "/embed/agent-marks.js", origin + "/embed/agent-marks.js?r=1", origin + "/embed/agent-marks.js?r=2"]);
        orca.stop();
        assert.equal(stops, 1);
        const pending = createOrca({enabled: true, origin}, {
          ...deps, importModule() {throw new Error("offline");}, retryMs: 25,
          setTimer(fn, ms) {assert.equal(ms, 25); timers.set(nextId, fn); return nextId++;},
        });
        await flush();
        assert.equal(timers.size, 1);
        const pendingId = timers.keys().next().value;
        pending.stop();
        pending.stop();
        assert.equal(timers.size, 0);
        assert.deepEqual(cleared, [pendingId]);
    """,
        tmp_path,
    )


def test_stop_during_pending_import_never_starts_a_watcher_or_retry(tmp_path: Path) -> None:
    run_node(
        """
        for (const succeed of [true, false]) {
          let resolve, reject;
          const importing = new Promise((yes, no) => {resolve = yes; reject = no;});
          const orca = createOrca({enabled: true, origin: "http://127.0.0.1:8791"}, {
            importModule: () => importing, addStylesheet() {},
            setTimer() {throw new Error("stopped reader must not retry");},
          });
          orca.stop();
          if (succeed) resolve({watchWorktreeSummary() {throw new Error("stopped reader must not watch");}});
          else reject(new Error("import failed after stop"));
          await flush();
          assert.equal(orca.marks(), null);
          assert.equal(orca.status(), "loading");
        }
    """,
        tmp_path,
    )


def test_async_import_failure_notifies_and_can_be_stopped_by_its_subscriber(tmp_path: Path) -> None:
    run_node(
        """
        const orca = createOrca({enabled: true, origin: "http://127.0.0.1:8791"}, {
          importModule: () => Promise.reject(new Error("offline")), addStylesheet() {},
          setTimer() {throw new Error("subscriber stopped the reader");},
        });
        let notices = 0;
        orca.subscribe(() => {notices++; orca.stop();});
        await flush();
        assert.equal(notices, 1);
        assert.equal(orca.status(), "unreachable");
        assert.equal(orca.summary(), null);
    """,
        tmp_path,
    )
