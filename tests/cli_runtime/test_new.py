import json
import os
import re
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


class TestCliNew(CliRuntimeHarness):
    def _init_origin_repo(self, target: Path, *, owner: str = "example", repo: str = "repo") -> None:
        if shutil.which("git") is None:
            self.skipTest("git not available")
        self._run_git(target, ["init"])
        self._run_git(target, ["remote", "add", "origin", f"https://github.com/{owner}/{repo}.git"])

    def _create_same_repo_linked_hierarchy(self, target: Path) -> None:
        self._init_origin_repo(target)
        self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"])
        self._run_runtime(target, ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"])
        self._run_runtime(
            target,
            ["new", "issue", "--epic", "2", "--title", "Add refresh token", "--github-issue", "3"],
        )

    def _write_runtime_clock(self, target: Path, *, now_iso: str, today: str) -> None:
        runtime_clock = target / "spec-dock" / "scripts" / "spec_dock_runtime" / "infra" / "clock.py"
        runtime_clock.write_text(
            (
                "from __future__ import annotations\n\n"
                f"def now_iso() -> str:\n    return {now_iso!r}\n\n"
                f"def today() -> str:\n    return {today!r}\n"
            ),
            encoding="utf-8",
        )

    def _assert_auto_sync_artifacts_include(
        self,
        target: Path,
        node_id: str,
        *,
        require_node_in_working_artifacts: bool = True,
    ) -> None:
        specdock_dir = target / "spec-dock"
        agent_dir = specdock_dir / ".agent"
        index_all_path = agent_dir / "index-all.json"
        index_path = agent_dir / "index.json"
        tree_all_path = agent_dir / "tree-all.json"
        tree_path = agent_dir / "tree.json"
        deps_issues_path = agent_dir / "deps-issues.json"
        tree_all_puml_path = specdock_dir / "tree-all.puml"
        tree_puml_path = specdock_dir / "tree.puml"
        deps_issues_puml_path = specdock_dir / "deps-issues.puml"
        dashboard_path = specdock_dir / "dashboard.md"
        artifact_paths = (
            index_all_path,
            index_path,
            tree_all_path,
            tree_path,
            deps_issues_path,
            tree_all_puml_path,
            tree_puml_path,
            deps_issues_puml_path,
            dashboard_path,
        )
        for artifact_path in artifact_paths:
            with self.subTest(artifact=artifact_path.name, node_id=node_id):
                self.assertTrue(artifact_path.is_file(), f"missing artifact: {artifact_path}")

        index_all = json.loads(index_all_path.read_text(encoding="utf-8"))
        tree_all = json.loads(tree_all_path.read_text(encoding="utf-8"))
        tree = json.loads(tree_path.read_text(encoding="utf-8"))
        deps_issues = json.loads(deps_issues_path.read_text(encoding="utf-8"))
        self.assertIn(node_id, index_all["nodes"])
        self.assertIn(node_id, self._collect_tree_node_ids(tree_all))
        self.assertTrue(deps_issues["deps"]["valid"])
        self.assertEqual(
            deps_issues["source"],
            {"index": "spec-dock/.agent/index.json", "schema_version": 2},
        )
        for text_path in (tree_all_puml_path, tree_puml_path, deps_issues_puml_path):
            self.assertIn("@startuml", text_path.read_text(encoding="utf-8"))
        if node_id.startswith("iss-"):
            self.assertIn(node_id, tree_all_puml_path.read_text(encoding="utf-8"))
        if require_node_in_working_artifacts:
            index = json.loads(index_path.read_text(encoding="utf-8"))
            self.assertIn(node_id, index["nodes"])
            self.assertIn(node_id, self._collect_tree_node_ids(tree))
            if node_id.startswith("iss-"):
                self.assertIn(node_id, deps_issues["nodes"])
                self.assertIn(node_id, tree_puml_path.read_text(encoding="utf-8"))
                self.assertIn(node_id, deps_issues_puml_path.read_text(encoding="utf-8"))
            self.assertIn(node_id, dashboard_path.read_text(encoding="utf-8"))

    def _collect_tree_node_ids(self, tree_payload: dict[str, object]) -> set[str]:
        node_ids: set[str] = set()
        roots = tree_payload.get("tree")
        if not isinstance(roots, list):
            return node_ids
        for initiative in roots:
            if not isinstance(initiative, dict):
                continue
            init_id = initiative.get("id")
            if isinstance(init_id, str):
                node_ids.add(init_id)
            epics = initiative.get("epics")
            if not isinstance(epics, list):
                continue
            for epic in epics:
                if not isinstance(epic, dict):
                    continue
                epic_id = epic.get("id")
                if isinstance(epic_id, str):
                    node_ids.add(epic_id)
                issues = epic.get("issues")
                if not isinstance(issues, list):
                    continue
                for issue in issues:
                    if not isinstance(issue, dict):
                        continue
                    issue_id = issue.get("id")
                    if isinstance(issue_id, str):
                        node_ids.add(issue_id)
        return node_ids

    def _read_create_auto_sync_artifacts(self, target: Path) -> dict[str, str | None]:
        artifact_paths = (
            target / "spec-dock" / ".agent" / "index-all.json",
            target / "spec-dock" / ".agent" / "index.json",
            target / "spec-dock" / ".agent" / "tree-all.json",
            target / "spec-dock" / ".agent" / "tree.json",
            target / "spec-dock" / ".agent" / "deps-issues.json",
            target / "spec-dock" / "tree-all.puml",
            target / "spec-dock" / "tree.puml",
            target / "spec-dock" / "deps-issues.puml",
            target / "spec-dock" / "dashboard.md",
        )
        return {
            path.relative_to(target).as_posix(): path.read_text(encoding="utf-8") if path.exists() else None
            for path in artifact_paths
        }

    def _install_gh_issue_list_stub(
        self,
        target: Path,
        *,
        issue_numbers: list[int],
        log_path: Path | None = None,
    ) -> dict[str, str]:
        bin_dir = target / ".bin-gh-list"
        bin_dir.mkdir(parents=True, exist_ok=True)
        self._make_gh_issue_list_stub(
            bin_dir,
            issues=[
                {
                    "number": issue_number,
                    "state": "OPEN",
                    "title": f"Issue {issue_number}",
                    "labels": [],
                    "updatedAt": f"2026-05-13T00:00:{issue_number:02d}Z",
                    "url": f"https://github.com/example/repo/issues/{issue_number}",
                }
                for issue_number in issue_numbers
            ],
            log_path=log_path,
        )
        return {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

    def test_new_initiative_auto_syncs_index_and_dashboard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)
            log_path = target / ".gh.log"
            test_env = self._install_gh_issue_list_stub(target, issue_numbers=[1], log_path=log_path)

            self._run_runtime(
                target,
                ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"],
                env=test_env,
            )

            self._assert_auto_sync_artifacts_include(
                target,
                "init-00001",
                require_node_in_working_artifacts=False,
            )
            self.assertIn("issue list", log_path.read_text(encoding="utf-8"))

    def test_new_epic_auto_syncs_index_and_dashboard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)
            test_env = self._install_gh_issue_list_stub(target, issue_numbers=[1, 2])
            self._run_runtime(
                target,
                ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"],
                env=test_env,
            )

            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"],
                env=test_env,
            )

            self._assert_auto_sync_artifacts_include(
                target,
                "epic-00002",
                require_node_in_working_artifacts=False,
            )

    def test_new_issue_auto_syncs_index_and_dashboard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)
            test_env = self._install_gh_issue_list_stub(target, issue_numbers=[1, 2, 3])
            self._run_runtime(
                target,
                ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"],
                env=test_env,
            )
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"],
                env=test_env,
            )

            self._run_runtime(
                target,
                ["new", "issue", "--epic", "2", "--title", "Add refresh token", "--github-issue", "3"],
                env=test_env,
            )

            self._assert_auto_sync_artifacts_include(target, "iss-00003")

    def test_new_issue_auto_sync_preserves_local_only_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)
            test_env = self._install_gh_issue_list_stub(target, issue_numbers=[1, 2, 3, 4])
            self._run_runtime(
                target,
                ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"],
                env=test_env,
            )
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"],
                env=test_env,
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "2", "--title", "Local holder", "--github-issue", "3"],
                env=test_env,
            )
            local_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-local-holder"
            )
            self._remove_github_link(local_issue_dir)

            self._run_runtime(
                target,
                ["new", "issue", "--epic", "2", "--title", "Linked followup", "--github-issue", "4"],
                env=test_env,
            )

            self._assert_auto_sync_artifacts_include(target, "iss-00003")
            self._assert_auto_sync_artifacts_include(target, "iss-00004")

    def test_new_failure_paths_do_not_run_post_sync_or_refresh_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)
            log_path = target / ".gh.log"
            test_env = self._install_gh_issue_list_stub(target, issue_numbers=[1, 2, 3], log_path=log_path)
            self._run_runtime(
                target,
                ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"],
                env=test_env,
            )
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"],
                env=test_env,
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "2", "--title", "Add refresh token", "--github-issue", "3"],
                env=test_env,
            )

            cases = (
                ["new", "initiative", "--title", "Duplicate initiative", "--github-issue", "1"],
                ["new", "epic", "--initiative", "missing", "--title", "Missing parent", "--github-issue", "4"],
                ["new", "issue", "--epic", "missing", "--title", "Missing parent", "--github-issue", "5"],
            )
            for argv in cases:
                with self.subTest(argv=argv):
                    before_artifacts = self._read_create_auto_sync_artifacts(target)
                    log_path.write_text("", encoding="utf-8")

                    p = self._run_runtime_capture(target, argv, env=test_env)

                    self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
                    self.assertEqual(before_artifacts, self._read_create_auto_sync_artifacts(target))
                    self.assertEqual(log_path.read_text(encoding="utf-8"), "")

    def test_new_rejects_duplicate_id_with_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_same_repo_linked_hierarchy(target)

            p = self._run_runtime_capture(
                target,
                [
                    "new",
                    "issue",
                    "--epic",
                    "2",
                    "--id",
                    "iss-00003",
                    "--title",
                    "Duplicate ID",
                    "--github-issue",
                    "4",
                ],
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("Cannot combine '--id' with GitHub-backed node creation.", p.stderr)

    def test_new_rejects_duplicate_id_width_agnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_same_repo_linked_hierarchy(target)

            p = self._run_runtime_capture(
                target,
                [
                    "new",
                    "issue",
                    "--epic",
                    "2",
                    "--github-issue",
                    "3",
                    "--title",
                    "Duplicate by numeric id",
                ],
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("github.issue_number=3", p.stderr)
            self.assertIn("issue:iss-00003", p.stderr)

    def test_new_rejects_duplicate_github_issue_link_with_conflict_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)

            self._run_runtime(target, ["new", "initiative", "--title", "Linked initiative", "--github-issue", "1"])
            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "2"])
            self._run_runtime(target, ["new", "epic", "--initiative", "2", "--title", "JWT auth", "--github-issue", "3"])

            p = self._run_runtime_capture(
                target,
                ["new", "issue", "--epic", "3", "--title", "Add refresh token", "--github-issue", "1"],
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("github.issue_number=1", p.stderr)
            self.assertIn("initiative:init-00001", p.stderr)
            self.assertIn("spec-dock/initiatives/init-00001-linked-initiative/.meta.json", p.stderr)
            self.assertIn("different GitHub issue number", p.stderr)
            self.assertNotIn("--github-issue", p.stderr)

            created = list((target / "spec-dock" / "initiatives").rglob("iss-00001-*"))
            self.assertEqual(created, [])

    def test_new_issue_persists_current_repo_scope_when_origin_is_resolved(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"])
            self._run_runtime(target, ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"])
            self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Current issue", "--github-issue", "123"])

            issue_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-current-issue"
                / ".meta.json"
            )
            issue_meta = json.loads(issue_meta_path.read_text(encoding="utf-8"))
            self.assertEqual(issue_meta["github"]["issue_number"], 123)
            self.assertEqual(issue_meta["github"]["repo_owner"], "current")
            self.assertEqual(issue_meta["github"]["repo_name"], "repo")

    def test_new_rejects_unsafe_slug(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_same_repo_linked_hierarchy(target)

            # User-provided --slug must be safe for filesystem paths.
            self._run_runtime_expect_fail(
                target,
                [
                    "new",
                    "issue",
                    "--epic",
                    "2",
                    "--title",
                    "Custom slug test",
                    "--slug",
                    "bad slug!!",
                    "--github-issue",
                    "4",
                ],
            )

    def test_new_rejects_uppercase_slug(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime_expect_fail(
                target,
                [
                    "new",
                    "initiative",
                    "--title",
                    "Auth platform",
                    "--slug",
                    "Bad-Slug",
                ],
            )

    def test_new_derives_kebab_slug_from_title(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)

            self._run_runtime(
                target,
                ["new", "initiative", "--title", "Add Refresh Token", "--github-issue", "1"],
            )
            init_dir = target / "spec-dock" / "initiatives" / "init-00001-add-refresh-token"
            self.assertTrue(init_dir.is_dir())
            meta = json.loads((init_dir / ".meta.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["slug"], "add-refresh-token")

    def test_new_rejects_invalid_slug_before_gh_issue_create(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                f'echo "$@" >> "{log_path.as_posix()}"\n'
                'if [[ "$1" == "issue" && "$2" == "create" ]]; then\n'
                '  echo "https://github.com/example/repo/issues/999"\n'
                "  exit 0\n"
                "fi\n"
                "exit 0\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            p = self._run_runtime_capture(
                target,
                [
                    "new",
                    "initiative",
                    "--create-github-issue",
                    "--title",
                    "Add Refresh Token",
                    "--slug",
                    "Bad!Slug",
                ],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("--slug", p.stderr)
            self.assertIn("expected regex", p.stderr)

            if log_path.exists():
                self.assertEqual(log_path.read_text(encoding="utf-8").strip(), "")
            self.assertEqual(list((target / "spec-dock" / "initiatives").glob("*")), [])

    def test_new_missing_rules_source_fails_before_gh_issue_create(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)

            (target / "spec-dock" / "docs" / "rules" / "initiative" / "epics.md").unlink()

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                f'echo "$@" >> "{log_path.as_posix()}"\n'
                'if [[ "$1" == "issue" && "$2" == "create" ]]; then\n'
                '  echo "https://github.com/example/repo/issues/999"\n'
                "  exit 0\n"
                "fi\n"
                "exit 0\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            p = self._run_runtime_capture(
                target,
                [
                    "new",
                    "initiative",
                    "--create-github-issue",
                    "--title",
                    "Add Refresh Token",
                ],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("Missing rules source", p.stderr)
            self.assertIn("epics.md", p.stderr)

            if log_path.exists():
                self.assertEqual(log_path.read_text(encoding="utf-8").strip(), "")
            self.assertEqual(list((target / "spec-dock" / "initiatives").glob("*")), [])

    def test_new_nodes_create_rules_symlinks_without_wrappers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_same_repo_linked_hierarchy(target)

            init_dir = target / "spec-dock" / "initiatives" / "init-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-00002-jwt-auth"
            issue_dir = epic_dir / "issues" / "iss-00003-add-refresh-token"
            expected_rules_links = {
                init_dir / "epics" / "rules.md": target / "spec-dock" / "docs" / "rules" / "initiative" / "epics.md",
                init_dir / "discussions" / "rules.md": (
                    target / "spec-dock" / "docs" / "rules" / "initiative" / "discussions.md"
                ),
                epic_dir / "issues" / "rules.md": target / "spec-dock" / "docs" / "rules" / "epic" / "issues.md",
                epic_dir / "discussions" / "rules.md": target / "spec-dock" / "docs" / "rules" / "epic" / "discussions.md",
                issue_dir / "discussions" / "rules.md": target / "spec-dock" / "docs" / "rules" / "issue" / "discussions.md",
            }
            for link_path, target_path in expected_rules_links.items():
                self.assertTrue(link_path.is_symlink(), f"missing rules symlink: {link_path}")
                self.assertEqual(link_path.resolve(), target_path.resolve())
                self.assertEqual(os.readlink(link_path), os.path.relpath(target_path, start=link_path.parent))

            self.assertFalse((init_dir / "epics" / "new-epic").exists())
            self.assertFalse((epic_dir / "issues" / "new-issue").exists())

            for scope_dir in (init_dir, epic_dir, issue_dir):
                self.assertFalse((scope_dir / "adrs").exists())
                self.assertFalse((scope_dir / "artifacts").exists())
                self.assertEqual(list((scope_dir / "discussions").glob("new-*")), [])

    def test_new_doc_adr_increments_id_within_scope_discussions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_same_repo_linked_hierarchy(target)
            p_one = self._run_runtime_capture(
                target,
                ["new", "doc", "adr", "--issue", "iss-00003", "--title", "Decision one"],
            )
            p_two = self._run_runtime_capture(
                target,
                ["new", "doc", "adr", "--issue", "iss-00003", "--title", "Decision two"],
            )
            self.assertEqual(p_one.returncode, 0, p_one.stdout + p_one.stderr)
            self.assertEqual(p_two.returncode, 0, p_two.stdout + p_two.stderr)

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
            discussions_dir = issue_dir / "discussions"
            created_one = sorted(discussions_dir.glob("*-adr-decision-one.md"))
            created_two = sorted(discussions_dir.glob("*-adr-decision-two.md"))
            self.assertEqual(len(created_one), 1)
            self.assertEqual(len(created_two), 1)
            self.assertRegex(created_one[0].name, r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-adr-decision-one\.md$")
            self.assertRegex(created_two[0].name, r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-adr-decision-two\.md$")
            self.assertRegex(p_one.stdout, r"id=[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-adr\b")
            self.assertRegex(p_two.stdout, r"id=[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-adr\b")
            self.assertEqual(list(issue_dir.glob("adrs")), [])

    def test_new_doc_scope_shorthand_resolves_local_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_same_repo_linked_hierarchy(target)

            p_init = self._run_runtime_capture(
                target,
                ["new", "doc", "note", "--initiative", "1", "--title", "Initiative note"],
            )
            p_epic = self._run_runtime_capture(
                target,
                ["new", "doc", "note", "--epic", "2", "--title", "Epic note"],
            )
            p_issue = self._run_runtime_capture(
                target,
                ["new", "doc", "note", "--issue", "3", "--title", "Issue note"],
            )
            self.assertEqual(p_init.returncode, 0, p_init.stdout + p_init.stderr)
            self.assertEqual(p_epic.returncode, 0, p_epic.stdout + p_epic.stderr)
            self.assertEqual(p_issue.returncode, 0, p_issue.stdout + p_issue.stderr)
            self.assertIn("scope=init-00001", p_init.stdout)
            self.assertIn("scope=epic-00002", p_epic.stdout)
            self.assertIn("scope=iss-00003", p_issue.stdout)

            init_dir = target / "spec-dock" / "initiatives" / "init-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-00002-jwt-auth"
            issue_dir = epic_dir / "issues" / "iss-00003-add-refresh-token"
            self.assertEqual(len(sorted((init_dir / "discussions").glob("*-note-initiative-note.md"))), 1)
            self.assertEqual(len(sorted((epic_dir / "discussions").glob("*-note-epic-note.md"))), 1)
            self.assertEqual(len(sorted((issue_dir / "discussions").glob("*-note-issue-note.md"))), 1)

    def test_new_doc_uses_timestamp_family_across_discussion_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_same_repo_linked_hierarchy(target)
            self._run_runtime(target, ["new", "doc", "disc", "--issue", "iss-00003", "--title", "Discussion one"])
            self._run_runtime(target, ["new", "doc", "adr", "--issue", "iss-00003", "--title", "Decision one"])
            self._run_runtime(target, ["new", "doc", "research", "--issue", "iss-00003", "--title", "Research one"])
            self._run_runtime(target, ["new", "doc", "note", "--issue", "iss-00003", "--title", "Note one"])

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
            discussions_dir = issue_dir / "discussions"
            self.assertEqual(len(sorted(discussions_dir.glob("*-disc-discussion-one.md"))), 1)
            self.assertEqual(len(sorted(discussions_dir.glob("*-adr-decision-one.md"))), 1)
            self.assertEqual(len(sorted(discussions_dir.glob("*-research-research-one.md"))), 1)
            self.assertEqual(len(sorted(discussions_dir.glob("*-note-note-one.md"))), 1)

    def test_new_doc_stdout_uses_slugless_id_and_discussions_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_same_repo_linked_hierarchy(target)
            p = self._run_runtime_capture(
                target,
                ["new", "doc", "disc", "--issue", "iss-00003", "--title", "Discussion one"],
            )
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            self.assertRegex(
                p.stdout,
                (
                    r"spec-dock: ok \(new doc\) type=disc "
                    r"id=[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-disc "
                    r"scope=iss-00003 "
                    r"path=spec-dock/.*/discussions/[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-disc-discussion-one\.md"
                ),
            )
            self.assertNotIn("discussion-one", re.search(r"id=([^\s]+)", p.stdout).group(1))

    def test_new_doc_renders_body_date_from_same_utc_instant_as_doc_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_same_repo_linked_hierarchy(target)
            self._write_runtime_clock(
                target,
                now_iso="2026-03-12T00:30:00+00:00",
                today="2026-03-11",
            )

            self._run_runtime(target, ["new", "doc", "note", "--issue", "iss-00003", "--title", "UTC date check"])

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
            created = issue_dir / "discussions" / "20260312t003000z-note-utc-date-check.md"
            self.assertTrue(created.is_file())
            self.assertIn("2026-03-12", created.read_text(encoding="utf-8"))
            self.assertNotIn("2026-03-11", created.read_text(encoding="utf-8"))

    def test_new_doc_ignores_unrelated_files_for_timestamp_allocation(self) -> None:
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
            discussions_dir = issue_dir / "discussions"
            (discussions_dir / "foo.md").write_text("nonconforming\n", encoding="utf-8")
            (discussions_dir / "009-disc-migrated.md").write_text("existing new format\n", encoding="utf-8")
            (discussions_dir / "1000-adr-legacy-overflow.md").write_text("4-digit should be ignored\n", encoding="utf-8")

            self._run_runtime(target, ["new", "doc", "adr", "--issue", "iss-00003", "--title", "Decision one"])

            self.assertEqual(len(sorted(discussions_dir.glob("*-adr-decision-one.md"))), 1)
            self.assertEqual(list(discussions_dir.glob("001-adr-*.md")), [])

    def test_new_doc_rejects_malformed_discussion_doc_candidates(self) -> None:
        cases = (
            "002-bogus-random.md",
            "foo-adr-kickoff.md",
            "bogus-01-adr-kickoff.md",
        )
        for malformed_name in cases:
            with self.subTest(malformed_name=malformed_name):
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
                    discussions_dir = issue_dir / "discussions"
                    (discussions_dir / malformed_name).write_text("nonconforming type\n", encoding="utf-8")

                    p = self._run_runtime_capture(
                        target,
                        ["new", "doc", "adr", "--issue", "iss-00003", "--title", "Decision one"],
                    )

                    self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
                    self.assertIn("Malformed discussion document filename", p.stderr)
                    self.assertIn(malformed_name, p.stderr)
                    self.assertEqual(len(sorted(discussions_dir.glob("*-adr-decision-one.md"))), 0)

    def test_new_doc_rejects_timestamp_shaped_malformed_discussion_doc_candidates(self) -> None:
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
            discussions_dir = issue_dir / "discussions"
            malformed_name = "20260312t010203z-00-disc-malformed.md"
            (discussions_dir / malformed_name).write_text("nonconforming type\n", encoding="utf-8")

            p = self._run_runtime_capture(
                target,
                ["new", "doc", "adr", "--issue", "iss-00003", "--title", "Decision one"],
            )

            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("Malformed discussion document filename", p.stderr)
            self.assertIn(malformed_name, p.stderr)
            self.assertEqual(len(sorted(discussions_dir.glob("*-adr-decision-one.md"))), 0)

    def test_new_doc_preserves_legacy_files_without_reusing_sequence_names(self) -> None:
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
            discussions_dir = issue_dir / "discussions"
            (discussions_dir / "001-adr-first.md").write_text("first\n", encoding="utf-8")
            (discussions_dir / "001-disc-second.md").write_text("second\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["new", "doc", "note", "--issue", "iss-00003", "--title", "Note one"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertRegex(p.stdout, r"id=[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-note\b")
            self.assertEqual(len(sorted(discussions_dir.glob("*-note-note-one.md"))), 1)

    def test_new_doc_rejects_invalid_slug(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_same_repo_linked_hierarchy(target)

            p = self._run_runtime_capture(
                target,
                [
                    "new",
                    "doc",
                    "adr",
                    "--issue",
                    "iss-00003",
                    "--title",
                    "Decision one",
                    "--slug",
                    "Bad!Slug",
                ],
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("--slug", p.stderr)
            self.assertIn("expected regex", p.stderr)

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
            discussions_dir = issue_dir / "discussions"
            self.assertEqual(list(discussions_dir.glob("001-adr-*.md")), [])

    def test_new_doc_rejects_unexpected_sequence_override_option(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            p = self._run_runtime_capture(
                target,
                [
                    "new",
                    "doc",
                    "adr",
                    "--issue",
                    "iss-00003",
                    "--seq",
                    "1",
                    "--title",
                    "Decision one",
                ],
            )
            self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
            self.assertIn("unrecognized arguments: --seq 1", p.stderr)

    def test_new_discussion_per_type_commands_are_not_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            for per_type in ("adr", "disc", "research", "note"):
                p = self._run_runtime_capture(
                    target,
                    ["new", per_type, "--issue", "iss-00003", "--title", "Doc title"],
                )
                self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
                self.assertIn(f"invalid choice: '{per_type}'", p.stderr)

    def test_new_help_exposes_only_doc_discussion_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            p_new = self._run_runtime_capture(target, ["new", "--help"])
            self.assertEqual(p_new.returncode, 0, p_new.stdout + p_new.stderr)
            self.assertIn(" doc ", p_new.stdout)
            self.assertNotIn("\n    adr", p_new.stdout)
            self.assertNotIn("\n    disc", p_new.stdout)
            self.assertNotIn("\n    research", p_new.stdout)
            self.assertNotIn("\n    note", p_new.stdout)

            p_doc = self._run_runtime_capture(target, ["new", "doc", "--help"])
            self.assertEqual(p_doc.returncode, 0, p_doc.stdout + p_doc.stderr)
            self.assertIn("adr", p_doc.stdout)
            self.assertIn("disc", p_doc.stdout)
            self.assertIn("research", p_doc.stdout)
            self.assertIn("note", p_doc.stdout)
            self.assertNotIn("--id", p_doc.stdout)
            self.assertNotIn("--seq", p_doc.stdout)

    def test_internal_issue_status_resolution_marks_cached_source(self) -> None:
        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2]
            / "src"
            / "spec_dock"
            / "assets"
            / "spec_dock"
            / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime import app as runtime_app
        finally:
            sys.path.pop(0)

        nodes = {
            "iss-00301": SimpleNamespace(
                id="iss-00301",
                type="issue",
                github_issue_number=301,
                epic_id="epic-00201",
                initiative_id="init-00101",
            )
        }
        resolved = runtime_app._resolve_issue_statuses(
            nodes,
            github=False,
            issue_index={},
            cached_issue_status_by_id={"iss-00301": "done"},
        )

        self.assertEqual(resolved["iss-00301"].status, "done")
        self.assertEqual(resolved["iss-00301"].source, "cache")

    def test_new_doc_rejects_unknown_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            p = self._run_runtime_capture(
                target,
                ["new", "doc", "unknown", "--issue", "iss-00003", "--title", "Doc title"],
            )
            self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
            self.assertIn("invalid choice: 'unknown'", p.stderr)

    def test_new_nodes_do_not_generate_readme_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_same_repo_linked_hierarchy(target)

            init_dir = target / "spec-dock" / "initiatives" / "init-00001-auth-platform"
            readmes = list(init_dir.rglob("README.md"))
            self.assertEqual(readmes, [])

    def test_new_no_github_is_contract_error_and_does_not_invoke_gh(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Provide a fake `gh` binary that always errors; --no-github must fail before invoking it.
            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                "echo \"gh should not be invoked in --no-github mode\" >&2\n"
                "exit 1\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            p = self._run_runtime_capture(
                target,
                ["new", "initiative", "--no-github", "--title", "Auth platform"],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("'--no-github' is not supported for initiative", p.stderr)

    def test_new_no_github_is_rejected_for_initiative_epic_and_issue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_same_repo_linked_hierarchy(target)

            cases = [
                (["new", "initiative", "--no-github", "--title", "Another initiative"], "initiative"),
                (["new", "epic", "--no-github", "--initiative", "1", "--title", "Another epic"], "epic"),
                (["new", "issue", "--no-github", "--epic", "2", "--title", "Another issue"], "issue"),
            ]
            for argv, kind in cases:
                with self.subTest(kind=kind):
                    p = self._run_runtime_capture(target, argv)
                    self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
                    self.assertIn(f"'--no-github' is not supported for {kind}", p.stderr)

    def test_new_rejects_invalid_title_before_gh_issue_create(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                f'echo "$@" >> "{log_path.as_posix()}"\n'
                'if [[ "$1" == "issue" && "$2" == "create" ]]; then\n'
                '  echo "https://github.com/example/repo/issues/999"\n'
                "  exit 0\n"
                "fi\n"
                "exit 0\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            p = self._run_runtime_capture(
                target,
                ["new", "initiative", "--create-github-issue", "--title", "日本語"],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("--title", p.stderr)
            self.assertIn("expected regex", p.stderr)

            if log_path.exists():
                self.assertEqual(log_path.read_text(encoding="utf-8").strip(), "")
            self.assertEqual(list((target / "spec-dock" / "initiatives").glob("*")), [])

    def test_new_initiative_and_epic_default_to_github_create_when_gh_is_available(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)

            # Default for initiative/epic is GitHub create; `gh` must be invoked even without explicit flags.
            bin_dir = target / ".bin-gh"
            bin_dir.mkdir(parents=True, exist_ok=True)
            called_path = target / ".gh.called"
            count_path = target / ".gh.count"
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                f'echo "$@" >> "{called_path.as_posix()}"\n'
                'if [[ "$1" == "issue" && "$2" == "create" ]]; then\n'
                f'  count=$(cat "{count_path.as_posix()}" 2>/dev/null || echo 0)\n'
                '  count=$((count + 1))\n'
                f'  printf "%s" "$count" > "{count_path.as_posix()}"\n'
                '  if [[ "$count" == "1" ]]; then\n'
                '    echo "https://github.com/example/repo/issues/123"\n'
                "  else\n"
                '    echo "https://github.com/example/repo/issues/124"\n'
                "  fi\n"
                "  exit 0\n"
                "fi\n"
                "echo \"unexpected gh args: $@\" >&2\n"
                "exit 1\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform"], env=test_env)
            self._run_runtime(target, ["new", "epic", "--initiative", "init-00123", "--title", "JWT auth"], env=test_env)

            init_dir = target / "spec-dock" / "initiatives" / "init-00123-auth-platform"
            epic_dir = init_dir / "epics" / "epic-00124-jwt-auth"
            self.assertTrue(init_dir.is_dir())
            self.assertTrue(epic_dir.is_dir())
            self.assertTrue(called_path.exists(), "gh was not invoked")

            init_meta = json.loads((init_dir / ".meta.json").read_text(encoding="utf-8"))
            epic_meta = json.loads((epic_dir / ".meta.json").read_text(encoding="utf-8"))
            self.assertEqual(init_meta["id"], "init-00123")
            self.assertEqual(epic_meta["id"], "epic-00124")
            self.assertEqual(init_meta["github"]["issue_number"], 123)
            self.assertEqual(epic_meta["github"]["issue_number"], 124)
            self.assertEqual(init_meta["github"]["repo_owner"], "example")
            self.assertEqual(init_meta["github"]["repo_name"], "repo")
            self.assertEqual(epic_meta["github"]["repo_owner"], "example")
            self.assertEqual(epic_meta["github"]["repo_name"], "repo")
            self._assert_spec_dock_meta_marker(init_meta)
            self._assert_spec_dock_meta_marker(epic_meta)
            self._assert_readonly_on_posix(init_dir / ".meta.json")
            self._assert_readonly_on_posix(epic_dir / ".meta.json")

    def test_new_initiative_warns_and_continues_when_readonly_lock_fails(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                'if [[ \"$1\" == \"issue\" && \"$2\" == \"create\" ]]; then\n'
                "  echo \"https://github.com/example/repo/issues/123\"\n"
                "  exit 0\n"
                "fi\n"
                "echo \"unexpected gh args: $@\" >&2\n"
                "exit 1\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            runtime_fs_repo = (
                target / "spec-dock" / "scripts" / "spec_dock_runtime" / "infra" / "fs_repo.py"
            )
            self.assertTrue(runtime_fs_repo.is_file())
            runtime_fs_repo.write_text(
                runtime_fs_repo.read_text(encoding="utf-8")
                + "\n\n"
                + "def _try_make_readonly(path):\n"
                + '    return False, "simulated"\n',
                encoding="utf-8",
            )

            p = self._run_runtime_capture(
                target,
                ["new", "initiative", "--title", "Auth platform"],
                env={"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"},
            )
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: (warn)", p.stderr)

            init_dir = target / "spec-dock" / "initiatives" / "init-00123-auth-platform"
            self.assertTrue((init_dir / ".meta.json").is_file())

    def test_new_github_flags_are_mutually_exclusive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            p1 = self._run_runtime_capture(
                target,
                [
                    "new",
                    "initiative",
                    "--title",
                    "Auth platform 2",
                    "--create-github-issue",
                    "--github-issue",
                    "123",
                ],
            )
            self.assertEqual(p1.returncode, 2, p1.stdout + p1.stderr)
            self.assertIn("not allowed with argument", p1.stderr)

            p2 = self._run_runtime_capture(
                target,
                [
                    "new",
                    "epic",
                    "--initiative",
                    "1",
                    "--title",
                    "JWT auth",
                    "--create-github-issue",
                    "--no-github",
                ],
            )
            self.assertEqual(p2.returncode, 2, p2.stdout + p2.stderr)
            self.assertIn("not allowed with argument", p2.stderr)

            p3 = self._run_runtime_capture(
                target,
                [
                    "new",
                    "initiative",
                    "--title",
                    "Auth platform 3",
                    "--github-issue",
                    "123",
                    "--no-github",
                ],
            )
            self.assertEqual(p3.returncode, 2, p3.stdout + p3.stderr)
            self.assertIn("not allowed with argument", p3.stderr)

            p4 = self._run_runtime_capture(
                target,
                [
                    "new",
                    "epic",
                    "--initiative",
                    "1",
                    "--title",
                    "JWT auth 2",
                    "--github-issue",
                    "123",
                    "--no-github",
                ],
            )
            self.assertEqual(p4.returncode, 2, p4.stdout + p4.stderr)
            self.assertIn("not allowed with argument", p4.stderr)

            p5 = self._run_runtime_capture(
                target,
                [
                    "new",
                    "issue",
                    "--epic",
                    "1",
                    "--title",
                    "Issue 1",
                    "--create-github-issue",
                    "--github-issue",
                    "123",
                ],
            )
            self.assertEqual(p5.returncode, 2, p5.stdout + p5.stderr)
            self.assertIn("not allowed with argument", p5.stderr)

            p6 = self._run_runtime_capture(
                target,
                [
                    "new",
                    "issue",
                    "--epic",
                    "1",
                    "--title",
                    "Issue 2",
                    "--create-github-issue",
                    "--no-github",
                ],
            )
            self.assertEqual(p6.returncode, 2, p6.stdout + p6.stderr)
            self.assertIn("not allowed with argument", p6.stderr)

    def test_new_issue_create_github_issue_flag_alias_is_accepted(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"])
            self._run_runtime(target, ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                'if [[ \"$1\" == \"issue\" && \"$2\" == \"create\" ]]; then\n'
                "  echo \"https://github.com/example/repo/issues/123\"\n"
                "  exit 0\n"
                "fi\n"
                "echo \"unexpected gh args: $@\" >&2\n"
                "exit 1\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "2", "--title", "Add refresh token", "--create-github-issue"],
                env=test_env,
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-add-refresh-token"
            )
            self.assertTrue(issue_dir.is_dir())

    def test_new_issue_can_create_github_issue_and_use_its_number(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"])
            self._run_runtime(target, ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"])

            # Provide a fake `gh` binary so the test doesn't require network/auth.
            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                'if [[ \"$1\" == \"issue\" && \"$2\" == \"create\" ]]; then\n'
                "  echo \"https://github.com/example/repo/issues/123\"\n"
                "  exit 0\n"
                "fi\n"
                "echo \"unexpected gh args: $@\" >&2\n"
                "exit 1\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "2", "--title", "Add refresh token"],
                env=test_env,
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-add-refresh-token"
            )
            self.assertTrue(issue_dir.is_dir())
            meta = json.loads((issue_dir / ".meta.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["id"], "iss-00123")
            self.assertEqual(meta["github"]["issue_number"], 123)
            self._assert_spec_dock_meta_marker(meta)
            self._assert_readonly_on_posix(issue_dir / ".meta.json")

    def test_new_fails_preflight_on_legacy_meta_without_creating_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--title", "Parent initiative", "--github-issue", "1"])
            self._run_runtime(target, ["new", "epic", "--initiative", "1", "--title", "Parent epic", "--github-issue", "2"])
            self._run_runtime(target, ["new", "initiative", "--title", "Legacy holder", "--github-issue", "3"])

            initiatives_root = target / "spec-dock" / "initiatives"
            parent_init_dir = initiatives_root / "init-00001-parent-initiative"
            parent_epic_dir = parent_init_dir / "epics" / "epic-00002-parent-epic"
            legacy_init_dir = initiatives_root / "init-00003-legacy-holder"
            dot_meta_path = legacy_init_dir / ".meta.json"
            legacy_meta_path = legacy_init_dir / "meta.json"
            dot_meta_path.rename(legacy_meta_path)
            self.assertFalse(dot_meta_path.exists())
            self.assertTrue(legacy_meta_path.is_file())

            before_inits = sorted(p.name for p in initiatives_root.glob("init-*"))
            before_epics = sorted(p.name for p in (parent_init_dir / "epics").glob("epic-*"))
            before_issues = sorted(p.name for p in (parent_epic_dir / "issues").glob("iss-*"))

            p_init = self._run_runtime_capture(
                target,
                ["new", "initiative", "--title", "Should fail initiative", "--github-issue", "4"],
            )
            self.assertNotEqual(p_init.returncode, 0, p_init.stdout + p_init.stderr)
            self.assertIn("Unsupported legacy meta.json detected", p_init.stderr)
            self.assertIn(str(legacy_meta_path), p_init.stderr)

            p_epic = self._run_runtime_capture(
                target,
                ["new", "epic", "--initiative", "1", "--title", "Should fail epic", "--github-issue", "5"],
            )
            self.assertNotEqual(p_epic.returncode, 0, p_epic.stdout + p_epic.stderr)
            self.assertIn("Unsupported legacy meta.json detected", p_epic.stderr)
            self.assertIn(str(legacy_meta_path), p_epic.stderr)

            p_issue = self._run_runtime_capture(
                target,
                ["new", "issue", "--epic", "2", "--title", "Should fail issue", "--github-issue", "6"],
            )
            self.assertNotEqual(p_issue.returncode, 0, p_issue.stdout + p_issue.stderr)
            self.assertIn("Unsupported legacy meta.json detected", p_issue.stderr)
            self.assertIn(str(legacy_meta_path), p_issue.stderr)

            self.assertEqual(before_inits, sorted(p.name for p in initiatives_root.glob("init-*")))
            self.assertEqual(before_epics, sorted(p.name for p in (parent_init_dir / "epics").glob("epic-*")))
            self.assertEqual(before_issues, sorted(p.name for p in (parent_epic_dir / "issues").glob("iss-*")))
