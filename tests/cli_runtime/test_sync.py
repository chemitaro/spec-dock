import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

from tests.cli_runtime.harness import (
    CliRuntimeHarness,
    _EXPECTED_MANAGED_SKILL_NAMES,
    _expected_spec_dock_version,
    main,
)


class TestCliSync(CliRuntimeHarness):
    def _set_meta_depends_on(self, node_dir: Path, depends_on: object) -> None:
        meta_path = node_dir / ".meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["depends_on"] = depends_on
        self._write_json_force(meta_path, meta)

    def test_sync_rejects_github_and_no_github_together(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-github"])
            self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
            self.assertIn("not allowed with argument", p.stderr)

    def test_new_and_active_and_sync(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
            )
            self.assertTrue((issue_dir / "requirement.md").is_file())
            self.assertTrue((issue_dir / "design.md").is_file())
            self.assertTrue((issue_dir / "plan.md").is_file())
            self.assertTrue((issue_dir / "report.md").is_file())

            # Placeholders should be rendered in generated files.
            requirement = (issue_dir / "requirement.md").read_text(encoding="utf-8")
            self.assertNotIn("<ISS_ID>", requirement)
            self.assertNotIn("<ISS_TITLE>", requirement)
            self.assertIn("iss-00003", requirement)

            # Active pointers are set by a single target argument (node id or GitHub issue number).
            self._run_runtime(target, ["active", "set", "iss-00003", "--force"])
            self.assertTrue((target / "spec-dock" / ".agent" / "active.json").is_file())
            self.assertTrue(
                (target / "spec-dock" / "active" / "issue").exists()
                or (target / "spec-dock" / "active" / "issue.path").is_file()
            )
            self.assertTrue((target / "spec-dock" / "active" / "context-pack.md").is_file())

            self._run_runtime(target, ["sync"])
            self.assertTrue((target / "spec-dock" / ".agent" / "index.json").is_file())
            self.assertTrue((target / "spec-dock" / ".agent" / "tree.json").is_file())
            context_pack = (target / "spec-dock" / "active" / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- entry: `spec-dock/.agent/active.json`", context_pack)
            self.assertIn("- default working set: `spec-dock/.agent/index.json`", context_pack)
            self.assertIn("- default dependency view: `spec-dock/.agent/deps-issues.json`", context_pack)
            self.assertIn("- escalation only: `spec-dock/.agent/index-all.json`", context_pack)
            self.assertIn("- Start with `spec-dock/.agent/active.json`.", context_pack)
            self.assertIn(
                "- For normal work, read `spec-dock/.agent/index.json` and `spec-dock/.agent/deps-issues.json`.",
                context_pack,
            )
            self.assertIn(
                "- Read `spec-dock/.agent/index-all.json` only when full-history context is needed.",
                context_pack,
            )
            self.assertIn("human guidance", context_pack)

            # Index: flat nodes (agent-friendly).
            state = (target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8")
            self.assertIn("\"nodes\"", state)
            self.assertNotIn("\"tree\"", state)

            # Tree: nested layer view (human-friendly).
            tree_text = (target / "spec-dock" / ".agent" / "tree.json").read_text(encoding="utf-8")
            tree = json.loads(tree_text)
            self.assertIn("tree", tree)

            index = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            index_nodes = index["nodes"]

            init_item = tree["tree"][0]
            self.assertEqual(init_item["id"], "init-00001")
            self.assertEqual(init_item["type"], "initiative")
            self.assertIn("epics", init_item)

            epic_item = init_item["epics"][0]
            self.assertEqual(epic_item["id"], "epic-00002")
            self.assertEqual(epic_item["type"], "epic")
            self.assertIn("issues", epic_item)

            issue_item = epic_item["issues"][0]
            self.assertEqual(issue_item["id"], "iss-00003")
            self.assertEqual(issue_item["type"], "issue")

            # `tree.json` nodes match the same node schema as `index.json` nodes.
            self.assertEqual(issue_item, index_nodes["iss-00003"])
            self._run_runtime(target, ["validate"])

    def test_sync_builds_flat_adr_mirror_and_clears_stale_entries_after_rename_and_delete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            if not self._can_create_symlink(target):
                self.skipTest("symlinks not supported in test environment")

            self._create_same_repo_linked_hierarchy(target)
            self._run_runtime(target, ["new", "doc", "adr", "--initiative", "init-00001", "--title", "Initiative decision"])
            self._run_runtime(target, ["new", "doc", "adr", "--issue", "iss-00003", "--title", "Issue decision"])

            specdock_dir = target / "spec-dock"
            initiative_dir = specdock_dir / "initiatives" / "init-00001-auth-platform"
            issue_dir = (
                initiative_dir
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
            )
            initiative_doc = next((initiative_dir / "discussions").glob("*-adr-initiative-decision.md"))
            issue_doc = next((issue_dir / "discussions").glob("*-adr-issue-decision.md"))

            self._run_runtime(target, ["sync"])

            adrs_dir = specdock_dir / "adrs"
            self.assertTrue(adrs_dir.is_dir())
            self.assertEqual(
                sorted(path.name for path in adrs_dir.iterdir()),
                sorted([initiative_doc.name, issue_doc.name]),
            )
            for source in (initiative_doc, issue_doc):
                link_path = adrs_dir / source.name
                self.assertTrue(link_path.is_symlink(), f"missing ADR mirror symlink: {link_path}")
                self.assertFalse(os.readlink(link_path).startswith("/"), os.readlink(link_path))
                self.assertEqual(link_path.resolve(), source.resolve())

            renamed_issue_doc = issue_doc.with_name(issue_doc.name.replace("-issue-decision.md", "-issue-decision-renamed.md"))
            issue_doc.rename(renamed_issue_doc)

            self._run_runtime(target, ["sync"])

            self.assertFalse((adrs_dir / issue_doc.name).exists())
            renamed_link = adrs_dir / renamed_issue_doc.name
            self.assertTrue(renamed_link.is_symlink(), f"missing renamed ADR mirror symlink: {renamed_link}")
            self.assertEqual(renamed_link.resolve(), renamed_issue_doc.resolve())

            renamed_issue_doc.unlink()

            self._run_runtime(target, ["sync"])

            self.assertEqual(sorted(path.name for path in adrs_dir.iterdir()), [initiative_doc.name])
            self.assertFalse(renamed_link.exists())

    def test_sync_emits_all_and_todo_json_views(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            self._run_runtime(target, ["sync"])

            agent_dir = target / "spec-dock" / ".agent"
            index_all_path = agent_dir / "index-all.json"
            tree_all_path = agent_dir / "tree-all.json"
            index_todo_path = agent_dir / "index.json"
            tree_todo_path = agent_dir / "tree.json"

            self.assertTrue(index_all_path.is_file())
            self.assertTrue(tree_all_path.is_file())
            self.assertTrue(index_todo_path.is_file())
            self.assertTrue(tree_todo_path.is_file())

            index_all = json.loads(index_all_path.read_text(encoding="utf-8"))
            tree_all = json.loads(tree_all_path.read_text(encoding="utf-8"))
            index_todo = json.loads(index_todo_path.read_text(encoding="utf-8"))
            tree_todo = json.loads(tree_todo_path.read_text(encoding="utf-8"))

            self.assertEqual(index_all["schema_version"], 2)
            self.assertEqual(tree_all["schema_version"], 2)
            self.assertEqual(index_todo["schema_version"], 2)
            self.assertEqual(tree_todo["schema_version"], 2)
            self.assertEqual(index_all["projection"], "full-history")
            self.assertNotIn("source", index_all)
            self.assertEqual(index_todo["projection"], "current-future")
            self.assertNotIn("source", index_todo)

            def _collect_tree_node_ids(items: list[dict[str, object]]) -> set[str]:
                ids: set[str] = set()
                for initiative in items:
                    init_id = initiative.get("id")
                    if isinstance(init_id, str):
                        ids.add(init_id)

                    for epic in initiative.get("epics", []):
                        if not isinstance(epic, dict):
                            continue
                        epic_id = epic.get("id")
                        if isinstance(epic_id, str):
                            ids.add(epic_id)

                        for issue in epic.get("issues", []):
                            if not isinstance(issue, dict):
                                continue
                            issue_id = issue.get("id")
                            if isinstance(issue_id, str):
                                ids.add(issue_id)
                return ids

            index_all_nodes = set(index_all["nodes"].keys())
            tree_all_nodes = _collect_tree_node_ids(tree_all["tree"])
            index_todo_nodes = set(index_todo["nodes"].keys())
            tree_todo_nodes = _collect_tree_node_ids(tree_todo["tree"])

            self.assertNotEqual(index_all_nodes, set())
            self.assertEqual(index_all_nodes, tree_all_nodes)
            self.assertEqual(index_todo_nodes, tree_todo_nodes)
            self.assertTrue(index_todo_nodes.issubset(index_all_nodes))
            self.assertEqual(index_all_nodes, index_todo_nodes)

            def _assert_repo_relative_node_paths(nodes: dict[str, object]) -> None:
                for item in nodes.values():
                    self.assertIsInstance(item, dict)
                    node_path = item.get("path")
                    self.assertIsInstance(node_path, str)
                    assert isinstance(node_path, str)
                    self.assertTrue(node_path.startswith("spec-dock/"), node_path)
                    self.assertFalse(Path(node_path).is_absolute(), node_path)
                    self.assertFalse(node_path.startswith(str(target)), node_path)

            def _iter_tree_nodes(items: list[dict[str, object]]):
                for initiative in items:
                    yield initiative
                    for epic in initiative.get("epics", []):
                        if not isinstance(epic, dict):
                            continue
                        yield epic
                        for issue in epic.get("issues", []):
                            if isinstance(issue, dict):
                                yield issue

            _assert_repo_relative_node_paths(index_all["nodes"])
            _assert_repo_relative_node_paths(index_todo["nodes"])
            for tree_payload in (tree_all, tree_todo):
                for node_item in _iter_tree_nodes(tree_payload["tree"]):
                    node_path = node_item.get("path")
                    self.assertIsInstance(node_path, str)
                    assert isinstance(node_path, str)
                    self.assertTrue(node_path.startswith("spec-dock/"), node_path)
                    self.assertFalse(Path(node_path).is_absolute(), node_path)
                    self.assertFalse(node_path.startswith(str(target)), node_path)

    def test_sync_compiles_shorthand_to_issue_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Main init"])
            self._run_runtime(target, ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "Main epic"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Target issue"])

            self._run_runtime(target, ["new", "initiative", "--github-issue", "102", "--title", "Deps init"])
            self._run_runtime(target, ["new", "epic", "--initiative", "102", "--github-issue", "202", "--title", "Deps epic"])
            self._run_runtime(target, ["new", "issue", "--epic", "202", "--github-issue", "401", "--title", "Dep issue 1"])
            self._run_runtime(target, ["new", "issue", "--epic", "202", "--github-issue", "402", "--title", "Dep issue 2"])

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-main-init"
                / "epics"
                / "epic-00201-main-epic"
                / "issues"
                / "iss-00301-target-issue"
            )
            self._set_meta_depends_on(target_issue_dir, ["epic-00202", "102", 401])

            p = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            index_todo = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))

            expected_edges = [
                {"from": "iss-00301", "to": "iss-00401", "kind": "depends_on"},
                {"from": "iss-00301", "to": "iss-00402", "kind": "depends_on"},
            ]
            self.assertEqual(index_all["deps"]["issue_edges"], expected_edges)
            self.assertEqual(index_todo["deps"]["issue_edges"], expected_edges)
            for edge in expected_edges:
                self.assertTrue(edge["from"].startswith("iss-"))
                self.assertTrue(edge["to"].startswith("iss-"))

    def test_sync_warns_when_shorthand_expands_to_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Main init"])
            self._run_runtime(target, ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "Main epic"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Target issue"])

            self._run_runtime(target, ["new", "initiative", "--github-issue", "102", "--title", "Empty init"])
            self._run_runtime(target, ["new", "epic", "--initiative", "102", "--github-issue", "202", "--title", "Empty epic"])

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-main-init"
                / "epics"
                / "epic-00201-main-epic"
                / "issues"
                / "iss-00301-target-issue"
            )
            self._set_meta_depends_on(target_issue_dir, ["epic-00202", "init-00102"])

            p = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("deps_ref_expanded_to_empty", p.stderr)

            index = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(index["deps"]["issue_edges"], [])

    def test_sync_fails_on_unresolved_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
                initiative_title="Main init",
                epic_title="Main epic",
                issue_title="Target issue",
            )

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-main-init"
                / "epics"
                / "epic-00201-main-epic"
                / "issues"
                / "iss-00301-target-issue"
            )
            self._set_meta_depends_on(target_issue_dir, ["iss-99999"])

            p = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("iss-99999", p.stderr)
            self.assertIn(".meta.json", p.stderr)

    def test_sync_fails_on_descendant_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
                initiative_title="Main init",
                epic_title="Main epic",
                issue_title="Target issue",
            )

            init_dir = target / "spec-dock" / "initiatives" / "init-00101-main-init"
            deps_path = init_dir / ".meta.json"
            self._set_meta_depends_on(init_dir, ["iss-00301"])

            p = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn(str(deps_path), p.stderr)
            self.assertIn("iss-00301", p.stderr)

    def test_sync_fails_on_self_or_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Main init"])
            self._run_runtime(target, ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "Main epic"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Issue one"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Issue two"])

            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-main-init"
                / "epics"
                / "epic-00201-main-epic"
            )
            issue_one_dir = epic_dir / "issues" / "iss-00301-issue-one"
            issue_two_dir = epic_dir / "issues" / "iss-00302-issue-two"
            issue_one_deps_path = issue_one_dir / ".meta.json"

            # Self dependency must fail.
            self._set_meta_depends_on(issue_one_dir, ["iss-00301"])
            p_self = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            self.assertEqual(p_self.returncode, 1, p_self.stdout + p_self.stderr)
            self.assertIn("iss-00301", p_self.stderr)
            self.assertIn(str(issue_one_deps_path), p_self.stderr)

            # Shorthand self (issue depends on own epic) must also fail.
            self._set_meta_depends_on(issue_one_dir, ["epic-00201"])
            p_shorthand_self = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            self.assertEqual(p_shorthand_self.returncode, 1, p_shorthand_self.stdout + p_shorthand_self.stderr)
            self.assertIn("iss-00301", p_shorthand_self.stderr)
            self.assertIn("epic-00201", p_shorthand_self.stderr)
            self.assertIn(str(issue_one_deps_path), p_shorthand_self.stderr)

            # Cycle dependency must fail.
            self._set_meta_depends_on(issue_one_dir, ["iss-00302"])
            self._set_meta_depends_on(issue_two_dir, ["iss-00301"])
            p_cycle = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            self.assertEqual(p_cycle.returncode, 1, p_cycle.stdout + p_cycle.stderr)
            self.assertIn("iss-00301", p_cycle.stderr)
            self.assertIn("iss-00302", p_cycle.stderr)
            self.assertIn("->", p_cycle.stderr)

    def test_sync_derives_deps_fields_ready_and_blockers(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Done dep"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Open mid"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "303", "--title", "Open target"],
            )

            issue_mid_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00302-open-mid"
            )
            issue_target_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00303-open-target"
            )
            self._set_meta_depends_on(issue_mid_dir, [301])
            self._set_meta_depends_on(issue_target_dir, [302])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Done dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Open mid", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 303, "state": "OPEN", "title": "Open target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            nodes = index_all["nodes"]
            self.assertEqual(nodes["iss-00301"]["status"], "done")
            self.assertEqual(nodes["iss-00301"]["deps"], {"ready": True, "depends_on": [], "blockers_top": []})
            self.assertEqual(nodes["iss-00302"]["deps"], {"ready": True, "depends_on": [], "blockers_top": []})
            self.assertEqual(
                nodes["iss-00303"]["deps"],
                {"ready": False, "depends_on": ["iss-00302"], "blockers_top": ["iss-00302"]},
            )

            tree = json.loads((target / "spec-dock" / ".agent" / "tree.json").read_text(encoding="utf-8"))
            tree_issue = [i for i in tree["tree"][0]["epics"][0]["issues"] if i["id"] == "iss-00303"][0]
            self.assertEqual(tree_issue["deps"], nodes["iss-00303"]["deps"])

    def test_local_only_issue_is_open_and_ready_without_deps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
                issue_title="Unknown issue",
            )
            self._materialize_local_compat_ids(target)

            p = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            index = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            issue = index["nodes"]["iss-local-00001"]
            self.assertEqual(issue["status"], "open")
            self.assertEqual(issue["authority"], "local")
            self.assertEqual(issue["effective_status"], "open")
            self.assertEqual(issue["source"], "local")
            self.assertFalse(issue["stale"])
            self.assertIsNone(issue["last_sync_at"])
            self.assertEqual(issue["deps"], {"ready": True, "depends_on": [], "blockers_top": []})

    def test_sync_outputs_are_deterministically_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Issue one"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Issue two"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "303", "--title", "Issue three"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "304", "--title", "Issue target"])

            issues_root = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
            )
            self._set_meta_depends_on(issues_root / "iss-00302-issue-two", ["iss-00301"])
            self._set_meta_depends_on(issues_root / "iss-00303-issue-three", ["iss-00302"])
            self._set_meta_depends_on(issues_root / "iss-00304-issue-target", ["iss-00303", "iss-00301"])

            p1 = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            self.assertEqual(p1.returncode, 0, p1.stdout + p1.stderr)
            index1 = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))

            p2 = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            self.assertEqual(p2.returncode, 0, p2.stdout + p2.stderr)
            index2 = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))

            self.assertEqual(
                index1["deps"]["issue_edges"],
                [
                    {"from": "iss-00302", "to": "iss-00301", "kind": "depends_on"},
                    {"from": "iss-00303", "to": "iss-00302", "kind": "depends_on"},
                    {"from": "iss-00304", "to": "iss-00301", "kind": "depends_on"},
                    {"from": "iss-00304", "to": "iss-00303", "kind": "depends_on"},
                ],
            )
            self.assertEqual(index2["deps"]["issue_edges"], index1["deps"]["issue_edges"])

            deps1 = index1["nodes"]["iss-00304"]["deps"]
            deps2 = index2["nodes"]["iss-00304"]["deps"]
            self.assertEqual(deps1, deps2)
            self.assertEqual(deps1["depends_on"], ["iss-00301", "iss-00302", "iss-00303"])
            self.assertEqual(deps1["blockers_top"], deps1["depends_on"][: len(deps1["blockers_top"])])

    def test_sync_emits_deps_issues_json_and_puml_todo_only(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Done prereq"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Open blocked"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "303", "--title", "Open prereq"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "304", "--title", "Open done dep"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "305", "--title", "Open isolated"],
            )

            issues_root = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
            )
            self._set_meta_depends_on(issues_root / "iss-00302-open-blocked", [303])
            self._set_meta_depends_on(issues_root / "iss-00304-open-done-dep", [301])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Done", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Blocked", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 303, "state": "OPEN", "title": "Prereq", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 304, "state": "OPEN", "title": "Done dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 305, "state": "OPEN", "title": "Isolated", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            deps_issues_path = target / "spec-dock" / ".agent" / "deps-issues.json"
            deps_issues_puml_path = target / "spec-dock" / "deps-issues.puml"
            self.assertTrue(deps_issues_path.is_file())
            self.assertTrue(deps_issues_puml_path.is_file())

            deps_issues = json.loads(deps_issues_path.read_text(encoding="utf-8"))
            self.assertEqual(deps_issues["schema_version"], 1)
            self.assertEqual(deps_issues["projection"], "open-issues-dependency-view")
            self.assertEqual(
                deps_issues["source"],
                {"index": "spec-dock/.agent/index.json", "schema_version": 2},
            )
            self.assertEqual(
                set(deps_issues["nodes"].keys()),
                {"iss-00302", "iss-00303", "iss-00304", "iss-00305"},
            )

            node_302 = deps_issues["nodes"]["iss-00302"]
            node_304 = deps_issues["nodes"]["iss-00304"]
            node_305 = deps_issues["nodes"]["iss-00305"]
            self.assertEqual(node_302["ready"], False)
            self.assertEqual(node_302["depends_on"], ["iss-00303"])
            self.assertEqual(node_302["state"], "blocked")
            self.assertEqual(node_304["ready"], True)
            self.assertEqual(node_304["depends_on"], [])
            self.assertEqual(node_304["state"], "ready")
            self.assertEqual(node_305["ready"], True)
            self.assertEqual(node_305["depends_on"], [])
            self.assertEqual(node_305["state"], "ready")

            edge_pairs = [(edge["from"], edge["to"]) for edge in deps_issues["edges"]]
            self.assertEqual(edge_pairs, [("iss-00302", "iss-00303")])

            puml = deps_issues_puml_path.read_text(encoding="utf-8")
            self.assertIn("iss-00302", puml)
            self.assertIn("iss-00303", puml)
            self.assertIn("iss-00305", puml)
            self.assertNotIn("iss-00301", puml)
            self.assertIn("Niss_00303 --> Niss_00302 : blocks", puml)

    def test_sync_todo_projection_excludes_done_and_empty_branches(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)

            # Branch A: mixed done/open issues.
            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Done prereq"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Open target"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "303", "--title", "Open mid"],
            )

            # Branch B: done-only; should be removed from todo projection.
            self._run_runtime(target, ["new", "initiative", "--github-issue", "102", "--title", "Legacy platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "102", "--github-issue", "202", "--title", "Legacy epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "401", "--title", "Done legacy issue"],
            )

            issues_root = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
            )
            self._set_meta_depends_on(issues_root / "iss-00302-open-target", [303])
            self._set_meta_depends_on(issues_root / "iss-00303-open-mid", [301])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init A", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic A", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Done prereq", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Open target", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 303, "state": "OPEN", "title": "Open mid", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 102, "state": "OPEN", "title": "Init B", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 202, "state": "OPEN", "title": "Epic B", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 401, "state": "CLOSED", "title": "Done legacy", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            index_todo = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            tree_todo = json.loads((target / "spec-dock" / ".agent" / "tree.json").read_text(encoding="utf-8"))
            deps_issues = json.loads((target / "spec-dock" / ".agent" / "deps-issues.json").read_text(encoding="utf-8"))

            self.assertIn("iss-00301", index_all["nodes"])  # done issue remains in all
            self.assertIn("iss-00401", index_all["nodes"])  # done-only branch remains in all

            # todo projection: done issues + empty ancestors are removed.
            todo_nodes = set(index_todo["nodes"].keys())
            self.assertNotIn("iss-00301", todo_nodes)
            self.assertNotIn("iss-00401", todo_nodes)
            self.assertNotIn("epic-00202", todo_nodes)
            self.assertNotIn("init-00102", todo_nodes)
            self.assertIn("iss-00302", todo_nodes)
            self.assertIn("iss-00303", todo_nodes)
            self.assertIn("epic-00201", todo_nodes)
            self.assertIn("init-00101", todo_nodes)

            # deps.issue_edges for todo keeps only edges with both endpoints in todo issues.
            self.assertEqual(
                index_todo["deps"]["issue_edges"],
                [{"from": "iss-00302", "to": "iss-00303", "kind": "depends_on"}],
            )

            # tree.json node set must match index.json todo node set.
            def collect_tree_ids(items: list[dict]) -> set[str]:
                ids: set[str] = set()
                for init_item in items:
                    ids.add(init_item["id"])
                    for epic_item in init_item.get("epics", []):
                        ids.add(epic_item["id"])
                        for issue_item in epic_item.get("issues", []):
                            ids.add(issue_item["id"])
                return ids

            self.assertEqual(collect_tree_ids(tree_todo["tree"]), todo_nodes)

            # deps-issues nodes should match todo issue set from index.json.
            todo_issue_ids = {
                node_id
                for node_id, item in index_todo["nodes"].items()
                if isinstance(item, dict) and item.get("type") == "issue"
            }
            self.assertEqual(set(deps_issues["nodes"].keys()), todo_issue_ids)

    def test_sync_emits_tree_puml_ready_board_at_spec_dock_root(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Done issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Blocked issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "303", "--title", "Ready issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "304", "--title", "Ready second"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "305", "--title", "Doing issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "306", "--title", "Unknown issue"],
            )

            issues_root = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
            )
            self._set_meta_depends_on(issues_root / "iss-00302-blocked-issue", [303])
            self._set_meta_depends_on(issues_root / "iss-00304-ready-second", [301])

            p_active = self._run_runtime_capture(target, ["active", "set", "305", "--force", "--no-checkout"])
            self.assertEqual(p_active.returncode, 0, p_active.stdout + p_active.stderr)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Done", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Blocked", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 303, "state": "OPEN", "title": "Ready", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 304, "state": "OPEN", "title": "Ready2", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 305, "state": "OPEN", "title": "Doing", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            tree_all_puml_path = target / "spec-dock" / "tree-all.puml"
            tree_todo_puml_path = target / "spec-dock" / "tree.puml"
            self.assertTrue(tree_all_puml_path.is_file())
            self.assertTrue(tree_todo_puml_path.is_file())

            tree_all_puml = tree_all_puml_path.read_text(encoding="utf-8")
            self.assertIn("iss-00301\\n[DONE]", tree_all_puml)
            self.assertIn("iss-00302\\n[BLOCKED]", tree_all_puml)
            self.assertIn("iss-00303\\n[READY]", tree_all_puml)
            self.assertIn("iss-00305\\n[DOING]", tree_all_puml)
            self.assertIn("iss-00306\\n[UNKNOWN]", tree_all_puml)
            self.assertIn("blockers:", tree_all_puml)

            tree_todo_puml = tree_todo_puml_path.read_text(encoding="utf-8")
            self.assertNotIn("iss-00301", tree_todo_puml)
            self.assertIn("iss-00302", tree_todo_puml)
            self.assertIn("iss-00303", tree_todo_puml)
            self.assertIn("iss-00305", tree_todo_puml)
            self.assertIn("iss-00306", tree_todo_puml)

    def test_sync_emits_dashboard_md_at_spec_dock_root(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Done issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Blocked issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "303", "--title", "Ready issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "304", "--title", "Unknown issue"],
            )

            issues_root = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
            )
            self._set_meta_depends_on(issues_root / "iss-00302-blocked-issue", [303])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Done", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Blocked", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 303, "state": "OPEN", "title": "Ready", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            dashboard_path = target / "spec-dock" / "dashboard.md"
            self.assertTrue(dashboard_path.is_file())
            dashboard = dashboard_path.read_text(encoding="utf-8")
            self.assertIn("spec-dock/.agent/index.json", dashboard)
            self.assertIn("spec-dock/tree.puml", dashboard)
            self.assertIn("spec-dock/deps-issues.puml", dashboard)
            self.assertIn("## Ready", dashboard)
            self.assertIn("## Blocked", dashboard)
            self.assertIn("## Unknown", dashboard)
            self.assertIn("`iss-00303`", dashboard)
            self.assertIn("`iss-00302`", dashboard)
            self.assertIn("blockers: iss-00303", dashboard)
            self.assertIn("`iss-00304`", dashboard)
            self.assertNotIn("`iss-00301`", dashboard)

    def test_spec_dock_gitignore_ignores_human_facing_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            gitignore = (target / "spec-dock" / ".gitignore").read_text(encoding="utf-8")
            self.assertIn("tree-all.puml", gitignore)
            self.assertIn("tree.puml", gitignore)
            self.assertIn("deps-issues.puml", gitignore)
            self.assertIn("dashboard.md", gitignore)
            self.assertIn("/adrs/", gitignore)

    def test_spec_dock_gitignore_behavior_matches_git_check_ignore(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_git(target, ["init"])

            (target / "spec-dock" / "dashboard.md").write_text("dashboard\n", encoding="utf-8")
            adrs_doc = target / "spec-dock" / "adrs" / "example.md"
            adrs_doc.parent.mkdir(parents=True, exist_ok=True)
            adrs_doc.write_text("adr\n", encoding="utf-8")
            nested_adrs_doc = target / "spec-dock" / "docs" / "adrs" / "example.md"
            nested_adrs_doc.parent.mkdir(parents=True, exist_ok=True)
            nested_adrs_doc.write_text("nested adr\n", encoding="utf-8")
            self.assertTrue((target / "spec-dock" / "docs" / "README.md").is_file())

            isolated_home = target / ".git-home"
            isolated_xdg = target / ".git-xdg"
            isolated_home.mkdir(parents=True, exist_ok=True)
            isolated_xdg.mkdir(parents=True, exist_ok=True)
            check_ignore_env = os.environ.copy()
            check_ignore_env.update(
                {
                    "GIT_CONFIG_NOSYSTEM": "1",
                    "GIT_CONFIG_GLOBAL": os.devnull,
                    "HOME": str(isolated_home),
                    "XDG_CONFIG_HOME": str(isolated_xdg),
                }
            )

            def _run_check_ignore(path: str) -> subprocess.CompletedProcess[str]:
                return subprocess.run(
                    [
                        "git",
                        "-c",
                        f"core.excludesfile={os.devnull}",
                        "check-ignore",
                        "--no-index",
                        path,
                    ],
                    cwd=str(target),
                    env=check_ignore_env,
                    capture_output=True,
                    text=True,
                    check=False,
                )

            ignored_dashboard = _run_check_ignore("spec-dock/dashboard.md")
            self.assertEqual(
                ignored_dashboard.returncode,
                0,
                ignored_dashboard.stdout + ignored_dashboard.stderr,
            )
            self.assertIn("spec-dock/dashboard.md", ignored_dashboard.stdout)

            ignored_adr = _run_check_ignore("spec-dock/adrs/example.md")
            self.assertEqual(ignored_adr.returncode, 0, ignored_adr.stdout + ignored_adr.stderr)
            self.assertIn("spec-dock/adrs/example.md", ignored_adr.stdout)

            not_ignored_doc = _run_check_ignore("spec-dock/docs/README.md")
            self.assertEqual(
                not_ignored_doc.returncode,
                1,
                not_ignored_doc.stdout + not_ignored_doc.stderr,
            )
            not_ignored_nested_adrs = _run_check_ignore("spec-dock/docs/adrs/example.md")
            self.assertEqual(
                not_ignored_nested_adrs.returncode,
                1,
                not_ignored_nested_adrs.stdout + not_ignored_nested_adrs.stderr,
            )

    def test_sync_force_does_not_update_active_from_branch(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "spec tree"],
            )

            # Branch name includes the node id. Without --force, `sync` would update active.
            self._run_git(target, ["checkout", "-b", "feature/iss-00003-test"])

            self._run_runtime(target, ["active", "clear"])
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertIsNone(active.get("issue"))

            self._run_runtime(target, ["sync", "--no-github", "--force"])
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertIsNone(active.get("issue"))

    def test_sync_updates_active_from_branch_id(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "spec tree"],
            )

            # Branch name includes the node id.
            self._run_git(target, ["checkout", "-b", "feature/iss-00003-test"])

            self._run_runtime(target, ["sync"])
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertEqual(active["initiative"]["id"], "init-00001")
            self.assertEqual(active["epic"]["id"], "epic-00002")
            self.assertEqual(active["issue"]["id"], "iss-00003")

    def test_issue_71_runtime_bundle_validate_sync_and_sync_github_surface(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)

            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
            )

            p_validate = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(p_validate.returncode, 0, p_validate.stdout + p_validate.stderr)

            p_sync = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            self.assertEqual(p_sync.returncode, 0, p_sync.stdout + p_sync.stderr)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Issue", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            p_sync_github = self._run_runtime_capture(
                target,
                ["sync", "--github", "--no-update-active"],
                env=test_env,
            )
            self.assertEqual(p_sync_github.returncode, 0, p_sync_github.stdout + p_sync_github.stderr)

            index = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            self.assertIn("iss-00301", index["nodes"])

    def test_sync_default_github_populates_issue_statuses(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Add refresh token"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Rotate refresh token"],
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Issue 301", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Issue 302", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            nodes = index_all["nodes"]
            self.assertEqual(nodes["iss-00301"]["status"], "done")
            self.assertEqual(nodes["iss-00301"]["github"]["state"], "CLOSED")
            self.assertEqual(nodes["iss-00301"]["source"], "github")
            self.assertFalse(nodes["iss-00301"]["stale"])
            self.assertEqual(nodes["iss-00301"]["last_sync_at"], "t")
            self.assertEqual(nodes["iss-00302"]["status"], "open")
            self.assertEqual(nodes["iss-00302"]["github"]["state"], "OPEN")
            self.assertEqual(nodes["iss-00302"]["source"], "github")
            self.assertFalse(nodes["iss-00302"]["stale"])
            self.assertEqual(nodes["iss-00302"]["last_sync_at"], "t")
            index_todo = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            self.assertNotIn("iss-00301", index_todo["nodes"])

            guard_log = bin_dir / "gh-guard-sync-no-github.log"
            guard_log.unlink(missing_ok=True)
            self._make_gh_issue_list_stub(bin_dir, issues=[], fail=True, log_path=guard_log)

            p_cache = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"], env=test_env)
            self.assertEqual(p_cache.returncode, 0, p_cache.stdout + p_cache.stderr)
            self.assertFalse(guard_log.exists(), "gh must not be invoked with sync --no-github")
            index_all_cache = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            cache_nodes = index_all_cache["nodes"]
            self.assertEqual(cache_nodes["iss-00301"]["source"], "cache")
            self.assertTrue(cache_nodes["iss-00301"]["stale"])
            self.assertEqual(cache_nodes["iss-00301"]["last_sync_at"], "t")
            self.assertEqual(cache_nodes["iss-00302"]["source"], "cache")
            self.assertTrue(cache_nodes["iss-00302"]["stale"])
            self.assertEqual(cache_nodes["iss-00302"]["last_sync_at"], "t")

    def test_sync_generates_index_deps_and_deps_issues_artifacts(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Dep issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Target issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "303", "--title", "Open blocker"],
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00302-target-issue"
            )
            self._set_meta_depends_on(issue_dir, [301])
            done_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00301-dep-issue"
            )
            self._set_meta_depends_on(done_issue_dir, [303])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 303, "state": "OPEN", "title": "Blocker", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            self.assertEqual(index_all["projection"], "full-history")
            self.assertTrue(index_all["deps"]["valid"])
            self.assertIsNone(index_all["deps"]["error"])
            self.assertEqual(
                index_all["deps"]["issue_edges"],
                [
                    {"from": "iss-00301", "to": "iss-00303", "kind": "depends_on"},
                    {"from": "iss-00302", "to": "iss-00301", "kind": "depends_on"},
                ],
            )
            self.assertEqual(index_all["nodes"]["iss-00301"]["deps"]["depends_on"], [])
            self.assertTrue(index_all["nodes"]["iss-00301"]["deps"]["ready"])

            index_todo = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(index_todo["projection"], "current-future")
            self.assertTrue(index_todo["deps"]["valid"])
            self.assertIsNone(index_todo["deps"]["error"])
            self.assertEqual(index_todo["deps"]["issue_edges"], [])
            nodes = index_todo["nodes"]
            self.assertNotIn("iss-00301", nodes)
            self.assertEqual(nodes["iss-00302"]["deps"]["depends_on"], [])
            self.assertTrue(nodes["iss-00302"]["deps"]["ready"])

            deps_issues_path = target / "spec-dock" / ".agent" / "deps-issues.json"
            deps_issues_puml_path = target / "spec-dock" / "deps-issues.puml"
            self.assertTrue(deps_issues_path.is_file())
            self.assertTrue(deps_issues_puml_path.is_file())
            deps_issues = json.loads(deps_issues_path.read_text(encoding="utf-8"))
            self.assertEqual(deps_issues["projection"], "open-issues-dependency-view")
            self.assertEqual(
                deps_issues["source"],
                {"index": "spec-dock/.agent/index.json", "schema_version": 2},
            )
            self.assertTrue(deps_issues["deps"]["valid"])
            self.assertIsNone(deps_issues["deps"]["error"])
            self.assertNotIn("iss-00301", deps_issues["nodes"])  # done issue is filtered from todo projection
            self.assertIn("iss-00302", deps_issues["nodes"])
            self.assertIn("iss-00303", deps_issues["nodes"])

            deps_issues_puml = deps_issues_puml_path.read_text(encoding="utf-8")
            self.assertIn("iss-00302", deps_issues_puml)
            self.assertIn("iss-00303", deps_issues_puml)
            self.assertNotIn("iss-00301", deps_issues_puml)

            # Legacy v1 deps artifacts are no longer generated.
            self.assertFalse((target / "spec-dock" / ".agent" / "deps.json").exists())
            self.assertFalse((target / "spec-dock" / ".agent" / "deps.puml").exists())
            self.assertFalse((target / "spec-dock" / ".agent" / "deps.todo.puml").exists())

    def test_sync_github_passes_gh_limit_to_gh(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[{"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"}],
                log_path=log_path,
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--gh-limit", "123", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            self.assertTrue(log_path.is_file())
            lines = [line for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            self.assertNotEqual(lines, [])
            argv = lines[-1].split()
            self.assertIn("--limit", argv)
            i = argv.index("--limit")
            self.assertLess(i + 1, len(argv))
            self.assertEqual(argv[i + 1], "123")

    def test_sync_github_index_incomplete_warns_and_marks_unknown(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Add refresh token"],
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            # Missing 301 on purpose.
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("gh_fetch_failed", p.stderr)

            index = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            nodes = index["nodes"]
            self.assertEqual(nodes["iss-00301"]["status"], "unknown")
            self.assertEqual(
                nodes["iss-00301"]["github"],
                {"issue_number": 301, "repo_owner": "example", "repo_name": "repo"},
            )

    def test_sync_github_fetch_failure_warns_and_continues(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Add refresh token"],
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(bin_dir, issues=[], fail=True)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("gh_fetch_failed", p.stderr)

            index = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            nodes = index["nodes"]
            self.assertEqual(nodes["iss-00301"]["status"], "unknown")
