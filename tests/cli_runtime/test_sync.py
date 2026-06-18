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


import pytest
class TestCliSync(CliRuntimeHarness):
    def _set_meta_depends_on(self, node_dir: Path, depends_on: object) -> None:
        meta_path = node_dir / ".meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["depends_on"] = depends_on
        self._write_json_force(meta_path, meta)

    def test_sync_rejects_github_and_no_github_together(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-github"])
            assert p.returncode == 2, p.stdout + p.stderr
            assert "not allowed with argument" in p.stderr

    def test_new_and_active_and_sync(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

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
            assert (issue_dir / "requirement.md").is_file()
            assert (issue_dir / "design.md").is_file()
            assert (issue_dir / "plan.md").is_file()
            assert (issue_dir / "report.md").is_file()

            # Placeholders should be rendered in generated files.
            requirement = (issue_dir / "requirement.md").read_text(encoding="utf-8")
            assert "<ISS_ID>" not in requirement
            assert "<ISS_TITLE>" not in requirement
            assert "iss-00003" in requirement

            # Active pointers are set by a single target argument (node id or GitHub issue number).
            self._run_runtime(target, ["active", "set", "iss-00003", "--force"])
            assert (target / "spec-dock" / ".agent" / "active.json").is_file()
            assert (
                (target / "spec-dock" / "active" / "issue").exists()
                or (target / "spec-dock" / "active" / "issue.path").is_file()
            )
            assert (target / "spec-dock" / "active" / "context-pack.md").is_file()

            self._run_runtime(target, ["sync"])
            assert (target / "spec-dock" / ".agent" / "index.json").is_file()
            assert (target / "spec-dock" / ".agent" / "tree.json").is_file()
            context_pack = (target / "spec-dock" / "active" / "context-pack.md").read_text(encoding="utf-8")
            assert "- entry: `spec-dock/.agent/active.json`" in context_pack
            assert "- default working set: `spec-dock/.agent/index.json`" in context_pack
            assert "- default dependency view: `spec-dock/.agent/deps-issues.json`" in context_pack
            assert "- escalation only: `spec-dock/.agent/index-all.json`" in context_pack
            assert "- Start with `spec-dock/.agent/active.json`." in context_pack
            assert "- For normal work, read `spec-dock/.agent/index.json` and `spec-dock/.agent/deps-issues.json`." in context_pack
            assert "- Read `spec-dock/.agent/index-all.json` only when full-history context is needed." in context_pack
            assert "human guidance" in context_pack

            # Index: flat nodes (agent-friendly).
            state = (target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8")
            assert "\"nodes\"" in state
            assert "\"tree\"" not in state

            # Tree: nested layer view (human-friendly).
            tree_text = (target / "spec-dock" / ".agent" / "tree.json").read_text(encoding="utf-8")
            tree = json.loads(tree_text)
            assert "tree" in tree

            index = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            index_nodes = index["nodes"]

            init_item = tree["tree"][0]
            assert init_item["id"] == "init-00001"
            assert init_item["type"] == "initiative"
            assert "epics" in init_item

            epic_item = init_item["epics"][0]
            assert epic_item["id"] == "epic-00002"
            assert epic_item["type"] == "epic"
            assert "issues" in epic_item

            issue_item = epic_item["issues"][0]
            assert issue_item["id"] == "iss-00003"
            assert issue_item["type"] == "issue"

            # `tree.json` nodes match the same node schema as `index.json` nodes.
            assert issue_item == index_nodes["iss-00003"]
            self._run_runtime(target, ["validate"])

    def test_sync_builds_flat_adr_mirror_and_clears_stale_entries_after_rename_and_delete(self) -> None:
        pytest.skip(
            "S06 replacement: tests.unit.presentation.test_runtime_sync_s07 covers ADR mirror rebuild and symlink semantics."
        )
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            if not self._can_create_symlink(target):
                pytest.skip("symlinks not supported in test environment")

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
            assert adrs_dir.is_dir()
            assert sorted(path.name for path in adrs_dir.iterdir()) == sorted([initiative_doc.name, issue_doc.name])
            for source in (initiative_doc, issue_doc):
                link_path = adrs_dir / source.name
                assert link_path.is_symlink(), f"missing ADR mirror symlink: {link_path}"
                assert not os.readlink(link_path).startswith("/"), os.readlink(link_path)
                assert link_path.resolve() == source.resolve()

            renamed_issue_doc = issue_doc.with_name(issue_doc.name.replace("-issue-decision.md", "-issue-decision-renamed.md"))
            issue_doc.rename(renamed_issue_doc)

            self._run_runtime(target, ["sync"])

            assert not (adrs_dir / issue_doc.name).exists()
            renamed_link = adrs_dir / renamed_issue_doc.name
            assert renamed_link.is_symlink(), f"missing renamed ADR mirror symlink: {renamed_link}"
            assert renamed_link.resolve() == renamed_issue_doc.resolve()

            renamed_issue_doc.unlink()

            self._run_runtime(target, ["sync"])

            assert sorted(path.name for path in adrs_dir.iterdir()) == [initiative_doc.name]
            assert not renamed_link.exists()

    def test_sync_emits_all_and_todo_json_views(self) -> None:
        pytest.skip(
            "S06 replacement: tests.unit.presentation.test_runtime_sync_s07 covers sync artifact paths and projections."
        )
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            self._run_runtime(target, ["sync"])

            agent_dir = target / "spec-dock" / ".agent"
            index_all_path = agent_dir / "index-all.json"
            tree_all_path = agent_dir / "tree-all.json"
            index_todo_path = agent_dir / "index.json"
            tree_todo_path = agent_dir / "tree.json"

            assert index_all_path.is_file()
            assert tree_all_path.is_file()
            assert index_todo_path.is_file()
            assert tree_todo_path.is_file()

            index_all = json.loads(index_all_path.read_text(encoding="utf-8"))
            tree_all = json.loads(tree_all_path.read_text(encoding="utf-8"))
            index_todo = json.loads(index_todo_path.read_text(encoding="utf-8"))
            tree_todo = json.loads(tree_todo_path.read_text(encoding="utf-8"))

            assert index_all["schema_version"] == 2
            assert tree_all["schema_version"] == 2
            assert index_todo["schema_version"] == 2
            assert tree_todo["schema_version"] == 2
            assert index_all["projection"] == "full-history"
            assert "source" not in index_all
            assert index_todo["projection"] == "current-future"
            assert "source" not in index_todo

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

            assert index_all_nodes != set()
            assert index_all_nodes == tree_all_nodes
            assert index_todo_nodes == tree_todo_nodes
            assert index_todo_nodes.issubset(index_all_nodes)
            assert index_all_nodes == index_todo_nodes

            def _assert_repo_relative_node_paths(nodes: dict[str, object]) -> None:
                for item in nodes.values():
                    assert isinstance(item, dict)
                    node_path = item.get("path")
                    assert isinstance(node_path, str)
                    assert isinstance(node_path, str)
                    assert node_path.startswith("spec-dock/"), node_path
                    assert not Path(node_path).is_absolute(), node_path
                    assert not node_path.startswith(str(target)), node_path

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
                    assert isinstance(node_path, str)
                    assert isinstance(node_path, str)
                    assert node_path.startswith("spec-dock/"), node_path
                    assert not Path(node_path).is_absolute(), node_path
                    assert not node_path.startswith(str(target)), node_path

    def test_sync_compiles_shorthand_to_issue_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
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
            assert p.returncode == 0, p.stdout + p.stderr

            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            index_todo = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))

            expected_edges = [
                {"from": "iss-00301", "to": "iss-00401", "kind": "depends_on"},
                {"from": "iss-00301", "to": "iss-00402", "kind": "depends_on"},
            ]
            assert index_all["deps"]["issue_edges"] == expected_edges
            assert index_todo["deps"]["issue_edges"] == expected_edges
            for edge in expected_edges:
                assert edge["from"].startswith("iss-")
                assert edge["to"].startswith("iss-")

    def test_sync_warns_when_shorthand_expands_to_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

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
            assert p.returncode == 0, p.stdout + p.stderr
            assert "deps_ref_expanded_to_empty" in p.stderr

            index = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            assert index["deps"]["issue_edges"] == []

            deps_issues = json.loads((target / "spec-dock" / ".agent" / "deps-issues.json").read_text(encoding="utf-8"))
            assert deps_issues["schema_version"] == 2
            assert deps_issues["projection"] == "issue-readiness-with-dependency-context"
            assert deps_issues["nodes"]["iss-00301"]["ready"] is False
            assert deps_issues["nodes"]["iss-00301"]["node_blockers"] == [
                {
                    "node_id": "init-00102",
                    "reason": "empty_unknown",
                    "state": "unknown",
                    "state_source": "none",
                    "source_issue_id": "iss-00301",
                },
                {
                    "node_id": "epic-00202",
                    "reason": "empty_unknown",
                    "state": "unknown",
                    "state_source": "none",
                    "source_issue_id": "iss-00301",
                },
            ]
            assert deps_issues["nodes"]["init-00102"]["type"] == "initiative"
            assert deps_issues["nodes"]["epic-00202"]["type"] == "epic"
            assert [
                (edge["from"], edge["to"], edge["state"], edge["relation"])
                for edge in deps_issues["edges"]
            ] == [
                ("iss-00301", "init-00102", "blocking", "raw_direct"),
                ("iss-00301", "epic-00202", "blocking", "raw_direct"),
            ]

    def test_sync_fails_on_unresolved_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

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
            assert p.returncode == 1, p.stdout + p.stderr
            assert "iss-99999" in p.stderr
            assert ".meta.json" in p.stderr

    def test_sync_fails_on_descendant_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

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
            assert p.returncode == 1, p.stdout + p.stderr
            assert str(deps_path) in p.stderr
            assert "iss-00301" in p.stderr

    def test_sync_fails_on_self_or_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

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
            assert p_self.returncode == 1, p_self.stdout + p_self.stderr
            assert "iss-00301" in p_self.stderr
            assert str(issue_one_deps_path) in p_self.stderr

            # Shorthand self (issue depends on own epic) must also fail.
            self._set_meta_depends_on(issue_one_dir, ["epic-00201"])
            p_shorthand_self = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            assert p_shorthand_self.returncode == 1, p_shorthand_self.stdout + p_shorthand_self.stderr
            assert "iss-00301" in p_shorthand_self.stderr
            assert "epic-00201" in p_shorthand_self.stderr
            assert str(issue_one_deps_path) in p_shorthand_self.stderr

            # Cycle dependency must fail.
            self._set_meta_depends_on(issue_one_dir, ["iss-00302"])
            self._set_meta_depends_on(issue_two_dir, ["iss-00301"])
            p_cycle = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            assert p_cycle.returncode == 1, p_cycle.stdout + p_cycle.stderr
            assert "iss-00301" in p_cycle.stderr
            assert "iss-00302" in p_cycle.stderr
            assert "->" in p_cycle.stderr

    def test_sync_derives_deps_fields_ready_and_blockers(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
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
            assert p.returncode == 0, p.stdout + p.stderr

            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            nodes = index_all["nodes"]
            assert nodes["iss-00301"]["status"] == "done"
            assert nodes["iss-00301"]["deps"] == {"ready": True, "depends_on": [], "blockers_top": []}
            assert nodes["iss-00302"]["deps"] == {"ready": True, "depends_on": [], "blockers_top": []}
            assert nodes["iss-00303"]["deps"] == {"ready": False, "depends_on": ["iss-00302"], "blockers_top": ["iss-00302"]}

            tree = json.loads((target / "spec-dock" / ".agent" / "tree.json").read_text(encoding="utf-8"))
            tree_issue = [i for i in tree["tree"][0]["epics"][0]["issues"] if i["id"] == "iss-00303"][0]
            assert tree_issue["deps"] == nodes["iss-00303"]["deps"]

    def test_local_only_issue_is_open_and_ready_without_deps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
                issue_title="Unknown issue",
            )
            self._materialize_local_compat_ids(target)

            p = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            assert p.returncode == 0, p.stdout + p.stderr

            index = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            issue = index["nodes"]["iss-local-00001"]
            assert issue["status"] == "open"
            assert issue["authority"] == "local"
            assert issue["effective_status"] == "open"
            assert issue["source"] == "local"
            assert not issue["stale"]
            assert issue["last_sync_at"] is None
            assert issue["deps"] == {"ready": True, "depends_on": [], "blockers_top": []}

    def test_sync_outputs_are_deterministically_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

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
            assert p1.returncode == 0, p1.stdout + p1.stderr
            index1 = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))

            p2 = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            assert p2.returncode == 0, p2.stdout + p2.stderr
            index2 = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))

            assert index1["deps"]["issue_edges"] == [
                    {"from": "iss-00302", "to": "iss-00301", "kind": "depends_on"},
                    {"from": "iss-00303", "to": "iss-00302", "kind": "depends_on"},
                    {"from": "iss-00304", "to": "iss-00301", "kind": "depends_on"},
                    {"from": "iss-00304", "to": "iss-00303", "kind": "depends_on"},
                ]
            assert index2["deps"]["issue_edges"] == index1["deps"]["issue_edges"]

            deps1 = index1["nodes"]["iss-00304"]["deps"]
            deps2 = index2["nodes"]["iss-00304"]["deps"]
            assert deps1 == deps2
            assert deps1["depends_on"] == ["iss-00301", "iss-00302", "iss-00303"]
            assert deps1["blockers_top"] == deps1["depends_on"][: len(deps1["blockers_top"])]

    def test_sync_emits_deps_issues_json_and_puml_todo_only(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
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
            assert p.returncode == 0, p.stdout + p.stderr

            deps_issues_path = target / "spec-dock" / ".agent" / "deps-issues.json"
            deps_issues_puml_path = target / "spec-dock" / "deps-issues.puml"
            assert deps_issues_path.is_file()
            assert deps_issues_puml_path.is_file()

            deps_issues = json.loads(deps_issues_path.read_text(encoding="utf-8"))
            assert deps_issues["schema_version"] == 2
            assert deps_issues["projection"] == "issue-readiness-with-dependency-context"
            assert deps_issues["source"] == {"sync_state": "readiness_evaluation", "schema_version": 2}
            assert set(deps_issues["nodes"].keys()) == {
                "iss-00301",
                "iss-00302",
                "iss-00303",
                "iss-00304",
                "iss-00305",
            }

            node_302 = deps_issues["nodes"]["iss-00302"]
            node_304 = deps_issues["nodes"]["iss-00304"]
            node_305 = deps_issues["nodes"]["iss-00305"]
            assert node_302["ready"] == False
            assert node_302["depends_on"] == ["iss-00303"]
            assert node_302["state"] == "blocked"
            assert node_304["ready"] == True
            assert node_304["depends_on"] == []
            assert node_304["state"] == "ready"
            assert node_305["ready"] == True
            assert node_305["depends_on"] == []
            assert node_305["state"] == "ready"

            edge_pairs = [(edge["from"], edge["to"], edge["state"], edge["relation"]) for edge in deps_issues["edges"]]
            assert edge_pairs == [
                ("iss-00302", "iss-00303", "blocking", "compiled_issue"),
                ("iss-00304", "iss-00301", "satisfied", "raw_direct"),
            ]

            puml = deps_issues_puml_path.read_text(encoding="utf-8")
            assert "iss-00302" in puml
            assert "iss-00303" in puml
            assert "iss-00301" in puml
            assert "iss-00305" in puml
            assert "satisfied" in puml
            assert "Niss_00303 --> Niss_00302 : blocks" in puml

    def test_sync_todo_projection_excludes_done_and_empty_branches(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
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
            assert p.returncode == 0, p.stdout + p.stderr

            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            index_todo = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            tree_todo = json.loads((target / "spec-dock" / ".agent" / "tree.json").read_text(encoding="utf-8"))
            deps_issues = json.loads((target / "spec-dock" / ".agent" / "deps-issues.json").read_text(encoding="utf-8"))

            assert "iss-00301" in index_all["nodes"]  # done issue remains in all
            assert "iss-00401" in index_all["nodes"]  # done-only branch remains in all

            # todo projection: done issues + empty ancestors are removed.
            todo_nodes = set(index_todo["nodes"].keys())
            assert "iss-00301" not in todo_nodes
            assert "iss-00401" not in todo_nodes
            assert "epic-00202" not in todo_nodes
            assert "init-00102" not in todo_nodes
            assert "iss-00302" in todo_nodes
            assert "iss-00303" in todo_nodes
            assert "epic-00201" in todo_nodes
            assert "init-00101" in todo_nodes

            # deps.issue_edges for todo keeps only edges with both endpoints in todo issues.
            assert index_todo["deps"]["issue_edges"] == [{"from": "iss-00302", "to": "iss-00303", "kind": "depends_on"}]

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

            assert collect_tree_ids(tree_todo["tree"]) == todo_nodes

            # deps-issues is readiness context, not a todo-only issue set.
            todo_issue_ids = {
                node_id
                for node_id, item in index_todo["nodes"].items()
                if isinstance(item, dict) and item.get("type") == "issue"
            }
            assert set(deps_issues["nodes"].keys()).issuperset(todo_issue_ids)

    def test_sync_emits_tree_puml_ready_board_at_spec_dock_root(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
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
            assert p_active.returncode == 0, p_active.stdout + p_active.stderr

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
            assert p.returncode == 0, p.stdout + p.stderr

            tree_all_puml_path = target / "spec-dock" / "tree-all.puml"
            tree_todo_puml_path = target / "spec-dock" / "tree.puml"
            assert tree_all_puml_path.is_file()
            assert tree_todo_puml_path.is_file()

            tree_all_puml = tree_all_puml_path.read_text(encoding="utf-8")
            assert "iss-00301\\n[DONE]" in tree_all_puml
            assert "iss-00302\\n[BLOCKED]" in tree_all_puml
            assert "iss-00303\\n[READY]" in tree_all_puml
            assert "iss-00305\\n[DOING]" in tree_all_puml
            assert "iss-00306\\n[UNKNOWN]" in tree_all_puml
            assert "blockers:" in tree_all_puml

            tree_todo_puml = tree_todo_puml_path.read_text(encoding="utf-8")
            assert "iss-00301" not in tree_todo_puml
            assert "iss-00302" in tree_todo_puml
            assert "iss-00303" in tree_todo_puml
            assert "iss-00305" in tree_todo_puml
            assert "iss-00306" in tree_todo_puml

    def test_sync_emits_dashboard_md_at_spec_dock_root(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
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
            assert p.returncode == 0, p.stdout + p.stderr

            dashboard_path = target / "spec-dock" / "dashboard.md"
            assert dashboard_path.is_file()
            dashboard = dashboard_path.read_text(encoding="utf-8")
            assert "spec-dock/.agent/index.json" in dashboard
            assert "spec-dock/tree.puml" in dashboard
            assert "spec-dock/deps-issues.puml" in dashboard
            assert "spec-dock/deps-raw.puml" in dashboard
            assert "## Ready" in dashboard
            assert "## Blocked" in dashboard
            assert "## Unknown" in dashboard
            assert "`iss-00303`" in dashboard
            assert "`iss-00302`" in dashboard
            assert "blockers: iss-00303" in dashboard
            assert "`iss-00304`" in dashboard
            assert "`iss-00301`" not in dashboard
            assert "spec-dock/deps-raw.puml" in p.stdout

            deps_raw_path = target / "spec-dock" / "deps-raw.puml"
            assert deps_raw_path.is_file()
            deps_raw = deps_raw_path.read_text(encoding="utf-8")
            assert "@startuml" in deps_raw
            assert "iss-00303" in deps_raw
            assert "iss-00302" in deps_raw

    def test_spec_dock_gitignore_ignores_human_facing_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            gitignore = (target / "spec-dock" / ".gitignore").read_text(encoding="utf-8")
            assert "tree-all.puml" in gitignore
            assert "tree.puml" in gitignore
            assert "deps-issues.puml" in gitignore
            assert "deps-raw.puml" in gitignore
            assert "dashboard.md" in gitignore
            assert "/adrs/" in gitignore

    def test_spec_dock_gitignore_behavior_matches_git_check_ignore(self) -> None:
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._run_git(target, ["init"])

            (target / "spec-dock" / "dashboard.md").write_text("dashboard\n", encoding="utf-8")
            (target / "spec-dock" / "deps-raw.puml").write_text("@startuml\n@enduml\n", encoding="utf-8")
            adrs_doc = target / "spec-dock" / "adrs" / "example.md"
            adrs_doc.parent.mkdir(parents=True, exist_ok=True)
            adrs_doc.write_text("adr\n", encoding="utf-8")
            nested_adrs_doc = target / "spec-dock" / "docs" / "adrs" / "example.md"
            nested_adrs_doc.parent.mkdir(parents=True, exist_ok=True)
            nested_adrs_doc.write_text("nested adr\n", encoding="utf-8")
            assert (target / "spec-dock" / "docs" / "README.md").is_file()

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
            assert ignored_dashboard.returncode == 0, ignored_dashboard.stdout + ignored_dashboard.stderr
            assert "spec-dock/dashboard.md" in ignored_dashboard.stdout

            ignored_deps_raw = _run_check_ignore("spec-dock/deps-raw.puml")
            assert ignored_deps_raw.returncode == 0, ignored_deps_raw.stdout + ignored_deps_raw.stderr
            assert "spec-dock/deps-raw.puml" in ignored_deps_raw.stdout

            ignored_adr = _run_check_ignore("spec-dock/adrs/example.md")
            assert ignored_adr.returncode == 0, ignored_adr.stdout + ignored_adr.stderr
            assert "spec-dock/adrs/example.md" in ignored_adr.stdout

            not_ignored_doc = _run_check_ignore("spec-dock/docs/README.md")
            assert not_ignored_doc.returncode == 1, not_ignored_doc.stdout + not_ignored_doc.stderr
            not_ignored_nested_adrs = _run_check_ignore("spec-dock/docs/adrs/example.md")
            assert not_ignored_nested_adrs.returncode == 1, not_ignored_nested_adrs.stdout + not_ignored_nested_adrs.stderr

    def test_sync_force_does_not_update_active_from_branch(self) -> None:
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

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
            assert active.get("issue") is None

            self._run_runtime(target, ["sync", "--no-github", "--force"])
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            assert active.get("issue") is None

    def test_sync_updates_active_from_branch_id(self) -> None:
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

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
            assert active["initiative"]["id"] == "init-00001"
            assert active["epic"]["id"] == "epic-00002"
            assert active["issue"]["id"] == "iss-00003"

    def test_issue_71_runtime_bundle_validate_sync_and_sync_github_surface(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)

            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
            )

            p_validate = self._run_runtime_capture(target, ["validate"])
            assert p_validate.returncode == 0, p_validate.stdout + p_validate.stderr

            p_sync = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            assert p_sync.returncode == 0, p_sync.stdout + p_sync.stderr

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
            assert p_sync_github.returncode == 0, p_sync_github.stdout + p_sync_github.stderr

            index = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            assert "iss-00301" in index["nodes"]

    def test_sync_default_github_populates_issue_statuses(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
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
            assert p.returncode == 0, p.stdout + p.stderr

            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            nodes = index_all["nodes"]
            assert nodes["iss-00301"]["status"] == "done"
            assert nodes["iss-00301"]["github"]["state"] == "CLOSED"
            assert nodes["iss-00301"]["source"] == "github"
            assert not nodes["iss-00301"]["stale"]
            assert nodes["iss-00301"]["last_sync_at"] == "t"
            assert nodes["iss-00302"]["status"] == "open"
            assert nodes["iss-00302"]["github"]["state"] == "OPEN"
            assert nodes["iss-00302"]["source"] == "github"
            assert not nodes["iss-00302"]["stale"]
            assert nodes["iss-00302"]["last_sync_at"] == "t"
            index_todo = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            assert "iss-00301" not in index_todo["nodes"]

            guard_log = bin_dir / "gh-guard-sync-no-github.log"
            guard_log.unlink(missing_ok=True)
            self._make_gh_issue_list_stub(bin_dir, issues=[], fail=True, log_path=guard_log)

            p_cache = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"], env=test_env)
            assert p_cache.returncode == 0, p_cache.stdout + p_cache.stderr
            assert not guard_log.exists(), "gh must not be invoked with sync --no-github"
            index_all_cache = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            cache_nodes = index_all_cache["nodes"]
            assert cache_nodes["iss-00301"]["source"] == "cache"
            assert cache_nodes["iss-00301"]["stale"]
            assert cache_nodes["iss-00301"]["last_sync_at"] == "t"
            assert cache_nodes["iss-00302"]["source"] == "cache"
            assert cache_nodes["iss-00302"]["stale"]
            assert cache_nodes["iss-00302"]["last_sync_at"] == "t"

    def test_sync_generates_index_deps_and_deps_issues_artifacts(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
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
            assert p.returncode == 0, p.stdout + p.stderr

            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            assert index_all["projection"] == "full-history"
            assert index_all["deps"]["valid"]
            assert index_all["deps"]["error"] is None
            assert index_all["deps"]["issue_edges"] == [
                    {"from": "iss-00301", "to": "iss-00303", "kind": "depends_on"},
                    {"from": "iss-00302", "to": "iss-00301", "kind": "depends_on"},
                ]
            assert index_all["nodes"]["iss-00301"]["deps"]["depends_on"] == []
            assert index_all["nodes"]["iss-00301"]["deps"]["ready"]

            index_todo = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            assert index_todo["projection"] == "current-future"
            assert index_todo["deps"]["valid"]
            assert index_todo["deps"]["error"] is None
            assert index_todo["deps"]["issue_edges"] == []
            nodes = index_todo["nodes"]
            assert "iss-00301" not in nodes
            assert nodes["iss-00302"]["deps"]["depends_on"] == []
            assert nodes["iss-00302"]["deps"]["ready"]

            deps_issues_path = target / "spec-dock" / ".agent" / "deps-issues.json"
            deps_issues_puml_path = target / "spec-dock" / "deps-issues.puml"
            assert deps_issues_path.is_file()
            assert deps_issues_puml_path.is_file()
            deps_issues = json.loads(deps_issues_path.read_text(encoding="utf-8"))
            assert deps_issues["projection"] == "issue-readiness-with-dependency-context"
            assert deps_issues["source"] == {"sync_state": "readiness_evaluation", "schema_version": 2}
            assert deps_issues["deps"]["valid"]
            assert deps_issues["deps"]["error"] is None
            assert "iss-00301" in deps_issues["nodes"]  # satisfied context remains visible
            assert "iss-00302" in deps_issues["nodes"]
            assert "iss-00303" in deps_issues["nodes"]

            deps_issues_puml = deps_issues_puml_path.read_text(encoding="utf-8")
            assert "iss-00302" in deps_issues_puml
            assert "iss-00303" in deps_issues_puml
            assert "iss-00301" in deps_issues_puml

            # Legacy v1 deps artifacts are no longer generated.
            assert not (target / "spec-dock" / ".agent" / "deps.json").exists()
            assert not (target / "spec-dock" / ".agent" / "deps.puml").exists()
            assert not (target / "spec-dock" / ".agent" / "deps.todo.puml").exists()

    def test_sync_github_passes_gh_limit_to_gh(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
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

            p = self._run_runtime_capture(target, ["sync", "--gh-limit", "10000", "--no-update-active"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr

            assert log_path.is_file()
            lines = [line for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            assert lines != []
            argv = lines[-1].split()
            assert "--limit" in argv
            i = argv.index("--limit")
            assert i + 1 < len(argv)
            assert argv[i + 1] == "10000"

    def test_sync_github_index_incomplete_warns_and_marks_unknown(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
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
            assert p.returncode == 0, p.stdout + p.stderr
            assert "gh_fetch_failed" in p.stderr

            index = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            nodes = index["nodes"]
            assert nodes["iss-00301"]["status"] == "unknown"
            assert nodes["iss-00301"]["github"] == {"issue_number": 301, "repo_owner": "example", "repo_name": "repo"}

    def test_sync_github_fetch_failure_warns_and_continues(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
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
            assert p.returncode == 0, p.stdout + p.stderr
            assert "gh_fetch_failed" in p.stderr

            index = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            nodes = index["nodes"]
            assert nodes["iss-00301"]["status"] == "unknown"
