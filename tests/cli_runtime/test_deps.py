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


class TestCliDeps(CliRuntimeHarness):
    def test_sync_deps_progress_aggregation_for_epic_and_initiative(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

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
                ["new", "epic", "--initiative", "101", "--github-issue", "202", "--title", "OAuth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "303", "--title", "Second epic issue"],
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 202, "state": "OPEN", "title": "Epic2", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 303, "state": "OPEN", "title": "Second", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            index = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            nodes = index["nodes"]
            self.assertEqual(nodes["epic-00201"]["progress"], {"total": 2, "done": 1, "open": 1, "unknown": 0})
            self.assertEqual(nodes["epic-00202"]["progress"], {"total": 1, "done": 0, "open": 1, "unknown": 0})
            self.assertEqual(nodes["init-00101"]["progress"], {"total": 3, "done": 1, "open": 2, "unknown": 0})
            self.assertEqual(nodes["iss-00301"]["status"], "done")
            self.assertEqual(nodes["iss-00302"]["status"], "open")
            self.assertEqual(nodes["iss-00303"]["status"], "open")

    def test_sync_deps_empty_epic_and_initiative_are_done_and_non_blocking(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Empty init"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "Empty epic"],
            )
            self._run_runtime(target, ["new", "initiative", "--github-issue", "102", "--title", "Work init"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "102", "--github-issue", "202", "--title", "Work epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "301", "--title", "Target issue"],
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00102-work-init"
                / "epics"
                / "epic-00202-work-epic"
                / "issues"
                / "iss-00301-target-issue"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [201]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Empty init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Empty epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 102, "state": "OPEN", "title": "Work init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 202, "state": "OPEN", "title": "Work epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            index = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            nodes = index["nodes"]
            self.assertEqual(nodes["epic-00201"]["progress"], {"total": 0, "done": 0, "open": 0, "unknown": 0})
            self.assertEqual(nodes["init-00101"]["progress"], {"total": 0, "done": 0, "open": 0, "unknown": 0})
            self.assertTrue(nodes["iss-00301"]["deps"]["ready"])
            self.assertEqual(nodes["iss-00301"]["deps"]["depends_on"], [])
            self.assertEqual(nodes["iss-00301"]["deps"]["blockers_top"], [])

    def test_sync_deps_ignores_parent_github_closed_for_done(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

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
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "CLOSED", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "CLOSED", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            index = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            nodes = index["nodes"]
            self.assertEqual(nodes["epic-00201"]["progress"], {"total": 2, "done": 0, "open": 2, "unknown": 0})
            self.assertEqual(nodes["init-00101"]["progress"], {"total": 2, "done": 0, "open": 2, "unknown": 0})
            self.assertFalse(nodes["iss-00302"]["deps"]["ready"])
            self.assertEqual(nodes["iss-00302"]["deps"]["depends_on"], ["iss-00301"])

    def test_sync_deps_active_leaf_makes_epic_and_initiative_doing(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Active issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Sibling issue"],
            )
            self._run_runtime(target, ["active", "set", "iss-00301", "--force"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Active", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Sibling", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            deps_issues = json.loads((target / "spec-dock" / ".agent" / "deps-issues.json").read_text(encoding="utf-8"))
            nodes = deps_issues["nodes"]
            self.assertEqual(nodes["iss-00301"]["state"], "doing")
            self.assertEqual(nodes["iss-00302"]["state"], "ready")

    def test_sync_deps_active_epic_makes_initiative_doing(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Child issue"],
            )
            self._run_runtime(target, ["active", "set", "epic-00201", "--force"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Child", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            deps_issues = json.loads((target / "spec-dock" / ".agent" / "deps-issues.json").read_text(encoding="utf-8"))
            nodes = deps_issues["nodes"]
            self.assertEqual(nodes["iss-00301"]["state"], "ready")

    def test_deps_check_no_deps_is_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok (deps check)", p.stdout)
            self.assertIn("ready=true", p.stdout)

    def test_deps_check_accepts_explicit_id_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            p = self._run_runtime_capture(target, ["deps", "check", "--id", "iss-local-00001", "--json"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn('"target": "iss-local-00001"', p.stdout)

    def test_deps_check_accepts_explicit_github_issue_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Add refresh token", "--github-issue", "123"])

            p = self._run_runtime_capture(target, ["deps", "check", "--github-issue", "123", "--json"])
            self.assertIn(p.returncode, (0, 3), p.stdout + p.stderr)
            self.assertIn('"target": "iss-00123"', p.stdout)

    def test_deps_check_github_issue_flag_is_ambiguous_with_current_foreign_overlap_but_id_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Current issue", "--github-issue", "123"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Foreign mirror"])

            foreign_issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-foreign-mirror"
                / ".meta.json"
            )
            foreign_meta = json.loads(foreign_issue_meta.read_text(encoding="utf-8"))
            foreign_meta["github"] = {"issue_number": 123, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(foreign_issue_meta, foreign_meta)

            ambiguous = self._run_runtime_capture(target, ["deps", "check", "--github-issue", "123"])
            self.assertNotEqual(ambiguous.returncode, 0, ambiguous.stdout + ambiguous.stderr)
            self.assertIn("Ambiguous github.issue_number=123", ambiguous.stderr)

            by_id = self._run_runtime_capture(target, ["deps", "check", "--id", "iss-00123", "--json"])
            self.assertIn(by_id.returncode, (0, 3), by_id.stdout + by_id.stderr)
            self.assertIn('"target": "iss-00123"', by_id.stdout)

    def test_deps_check_repo_scoped_url_resolves_exact_match_when_number_is_ambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Current issue", "--github-issue", "123"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Foreign mirror"])

            foreign_issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-foreign-mirror"
                / ".meta.json"
            )
            foreign_meta = json.loads(foreign_issue_meta.read_text(encoding="utf-8"))
            foreign_meta["github"] = {"issue_number": 123, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(foreign_issue_meta, foreign_meta)

            ambiguous = self._run_runtime_capture(target, ["deps", "check", "123"])
            self.assertNotEqual(ambiguous.returncode, 0, ambiguous.stdout + ambiguous.stderr)
            self.assertIn("Ambiguous github.issue_number=123", ambiguous.stderr)

            by_url = self._run_runtime_capture(target, ["deps", "check", "https://github.com/other/repo/issues/123", "--json"])
            self.assertIn(by_url.returncode, (0, 3), by_url.stdout + by_url.stderr)
            self.assertIn('"target": "iss-local-00001"', by_url.stdout)

    def test_deps_numeric_ref_prefers_current_repo_scope_when_foreign_same_number_exists(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/example/repo.git"])

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Current blocker", "--github-issue", "123"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Foreign mirror"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Target issue", "--github-issue", "124"])

            foreign_issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-foreign-mirror"
                / ".meta.json"
            )
            foreign_meta = json.loads(foreign_issue_meta.read_text(encoding="utf-8"))
            foreign_meta["github"] = {"issue_number": 123, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(foreign_issue_meta, foreign_meta)

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-00124-target-issue"
            )
            (target_issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [123]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "--id", "iss-00124", "--json"])
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            data = json.loads(p.stdout)
            self.assertEqual(data["target"], "iss-00124")
            self.assertEqual(data["effective_depends_on"], ["iss-00123"])

    def test_deps_numeric_ref_rejects_foreign_only_match_when_current_repo_known(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/example/repo.git"])

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Foreign mirror"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Target issue", "--github-issue", "124"])

            foreign_issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-foreign-mirror"
                / ".meta.json"
            )
            foreign_meta = json.loads(foreign_issue_meta.read_text(encoding="utf-8"))
            foreign_meta["github"] = {"issue_number": 123, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(foreign_issue_meta, foreign_meta)

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-00124-target-issue"
            )
            (target_issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [123]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "--id", "iss-00124"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("No node found for github.issue_number=123 in current repo scope (example/repo)", p.stderr)
            self.assertIn("Create/link the node first.", p.stderr)

    def test_deps_numeric_ref_fail_closed_when_scope_mixed_and_current_repo_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Current blocker", "--github-issue", "123"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Foreign mirror"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Target issue", "--github-issue", "124"])

            foreign_issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-foreign-mirror"
                / ".meta.json"
            )
            foreign_meta = json.loads(foreign_issue_meta.read_text(encoding="utf-8"))
            foreign_meta["github"] = {"issue_number": 123, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(foreign_issue_meta, foreign_meta)

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-00124-target-issue"
            )
            (target_issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [123]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "--id", "iss-00124"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("Ambiguous github.issue_number=123", p.stderr)
            self.assertIn("mixed scoped/unscoped linkage", p.stderr)
            self.assertIn("fail-closed", p.stderr)

    def test_deps_scoped_ref_forms_resolve_exact_repo_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Current blocker", "--github-issue", "123"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Foreign mirror"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Target issue", "--github-issue", "124"])

            foreign_issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-foreign-mirror"
                / ".meta.json"
            )
            foreign_meta = json.loads(foreign_issue_meta.read_text(encoding="utf-8"))
            foreign_meta["github"] = {"issue_number": 123, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(foreign_issue_meta, foreign_meta)

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-00124-target-issue"
            )
            forms = (
                "other/repo#123",
                "https://github.com/other/repo/issues/123",
            )
            for ref in forms:
                with self.subTest(ref=ref):
                    (target_issue_dir / "deps.json").write_text(
                        json.dumps({"schema_version": 1, "depends_on": [ref]}, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8",
                    )
                    p = self._run_runtime_capture(target, ["deps", "check", "--id", "iss-00124", "--json"])
                    self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
                    data = json.loads(p.stdout)
                    self.assertEqual(data["target"], "iss-00124")
                    self.assertEqual(data["effective_depends_on"], ["iss-local-00001"])

    def test_deps_check_rejects_conflict_between_positional_target_and_id_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            p = self._run_runtime_capture(target, ["deps", "check", "123", "--id", "iss-local-00001"])
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("choose exactly one", p.stderr)

    def test_deps_check_rejects_non_positive_github_issue_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            p = self._run_runtime_capture(target, ["deps", "check", "--github-issue", "0"])
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("positive integer", p.stderr)

    def test_deps_check_returns_ready_and_blockers_and_closure_json(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "Main epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Target issue"],
            )
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "202", "--title", "Deps epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "401", "--title", "Open blocker"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "402", "--title", "Done issue"],
            )
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "203", "--title", "Transitive epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "203", "--github-issue", "403", "--title", "Transitive blocker"],
            )

            main_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-main-epic"
                / "issues"
                / "iss-00301-target-issue"
            )
            (main_issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["epic-00202"]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            blocker_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00202-deps-epic"
                / "issues"
                / "iss-00401-open-blocker"
            )
            (blocker_issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [403]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Main epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 202, "state": "OPEN", "title": "Deps epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 203, "state": "OPEN", "title": "Trans epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 401, "state": "OPEN", "title": "Blocker", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 402, "state": "CLOSED", "title": "Done", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 403, "state": "OPEN", "title": "Transitive", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00301", "--github", "--json"], env=test_env)
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            data = json.loads(p.stdout)
            self.assertEqual(
                list(data.keys()),
                [
                    "schema_version",
                    "target",
                    "target_status",
                    "ready",
                    "effective_depends_on",
                    "blockers",
                    "nodes",
                    "warnings",
                ],
            )
            self.assertEqual(data["target"], "iss-00301")
            self.assertFalse(data["ready"])
            self.assertEqual(data["effective_depends_on"], ["iss-00401", "iss-00403"])
            self.assertEqual(data["blockers"], ["iss-00401", "iss-00403"])
            self.assertEqual(data["warnings"], [])

    def test_deps_check_without_github_uses_index_snapshot_when_present(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

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
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p_sync = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p_sync.returncode, 0, p_sync.stdout + p_sync.stderr)

            index_all_path = target / "spec-dock" / ".agent" / "index-all.json"
            index_todo_path = target / "spec-dock" / ".agent" / "index.json"
            index_all = json.loads(index_all_path.read_text(encoding="utf-8"))
            index_todo = json.loads(index_todo_path.read_text(encoding="utf-8"))
            shadow = dict(index_all["nodes"]["iss-00301"])
            shadow["status"] = "open"
            index_todo["nodes"]["iss-00301"] = shadow
            index_todo_path.write_text(json.dumps(index_todo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            guard_log = bin_dir / "gh-guard.log"
            guard_log.unlink(missing_ok=True)
            self._make_gh_issue_list_stub(bin_dir, issues=[], fail=True, log_path=guard_log)

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--json"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertFalse(guard_log.exists(), "gh must not be invoked without --github")
            data = json.loads(p.stdout)
            self.assertTrue(data["ready"])
            self.assertEqual(data["blockers"], [])
            self.assertEqual(data["nodes"]["iss-00301"]["state"], "done")
            self.assertEqual(data["target_status"]["source"], "cache")
            self.assertTrue(data["target_status"]["stale"])
            self.assertEqual(data["target_status"]["last_sync_at"], "t")
            self.assertEqual(data["nodes"]["iss-00302"]["source"], "cache")

    def test_deps_check_without_github_falls_back_to_unknown_when_snapshot_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

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
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            (target / "spec-dock" / ".agent" / "index-all.json").unlink(missing_ok=True)
            (target / "spec-dock" / ".agent" / "index.json").unlink(missing_ok=True)

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--json"])
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            data = json.loads(p.stdout)
            self.assertFalse(data["ready"])
            self.assertEqual(data["blockers"], ["iss-00301"])
            self.assertEqual(data["nodes"]["iss-00301"]["state"], "unknown")
            self.assertEqual(data["target_status"]["source"], "cache")
            self.assertTrue(data["target_status"]["stale"])
            self.assertIsNone(data["target_status"]["last_sync_at"])
            self.assertEqual(data["target_status"]["source"], "cache")
            self.assertTrue(data["target_status"]["stale"])
            self.assertIsNone(data["target_status"]["last_sync_at"])

    def test_deps_check_missing_target_reports_runtime_target_requirement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            p = self._run_runtime_capture(target, ["deps", "check"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("target is required", p.stderr)

    def test_deps_check_accepts_github_number_forms_and_urls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Add refresh token"],
            )
            issue_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00301-add-refresh-token"
                / ".meta.json"
            )
            issue_meta = json.loads(issue_meta_path.read_text(encoding="utf-8"))
            issue_meta["github"] = {"issue_number": 301, "repo_owner": "example", "repo_name": "repo"}
            self._write_json_force(issue_meta_path, issue_meta)

            forms = [
                "301",
                "#301",
                "https://github.com/example/repo/issues/301",
            ]
            for form in forms:
                p = self._run_runtime_capture(target, ["deps", "check", form, "--json"])
                self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
                data = json.loads(p.stdout)
                self.assertEqual(data["target"], "iss-00301")
                self.assertFalse(data["ready"])

    def test_deps_check_github_ready_when_deps_closed(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

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
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--github", "--json"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            data = json.loads(p.stdout)
            self.assertTrue(data["ready"])
            self.assertEqual(data["effective_depends_on"], [])
            self.assertEqual(data["blockers"], [])
            self.assertEqual(data["nodes"]["iss-00301"]["state"], "done")

    def test_deps_check_without_github_uses_synced_index_status(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

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
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p_sync = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p_sync.returncode, 0, p_sync.stdout + p_sync.stderr)

            # Guard: `deps check` without --github must not fetch GitHub.
            guard_log = bin_dir / "gh-guard.log"
            guard_log.unlink(missing_ok=True)
            self._make_gh_issue_list_stub(bin_dir, issues=[], fail=True, log_path=guard_log)

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--json"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertFalse(guard_log.exists(), "gh must not be invoked without --github")
            data = json.loads(p.stdout)
            self.assertTrue(data["ready"])
            self.assertEqual(data["blockers"], [])
            self.assertEqual(data["nodes"]["iss-00301"]["state"], "done")

    def test_deps_check_without_github_missing_index_defaults_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

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
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            (target / "spec-dock" / ".agent" / "index.json").unlink(missing_ok=True)

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--json"])
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            data = json.loads(p.stdout)
            self.assertFalse(data["ready"])
            self.assertEqual(data["blockers"], ["iss-00301"])
            self.assertEqual(data["nodes"]["iss-00301"]["state"], "unknown")

    def test_deps_check_github_blocked_when_dep_open(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

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
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--github", "--json"], env=test_env)
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            data = json.loads(p.stdout)
            self.assertFalse(data["ready"])
            self.assertEqual(data["effective_depends_on"], ["iss-00301"])
            self.assertEqual(data["blockers"], ["iss-00301"])

    def test_deps_check_github_index_incomplete_warns_and_blocks(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

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
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            # Missing 301 on purpose.
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--github", "--json"], env=test_env)
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            self.assertEqual(p.stderr.strip(), "")
            data = json.loads(p.stdout)
            self.assertIn("gh_index_incomplete", data["warnings"])
            self.assertEqual(data["blockers"], ["iss-00301"])

    def test_deps_check_github_fetch_failure_warns_and_blocks(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

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
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(bin_dir, issues=[], fail=True)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--github", "--json"], env=test_env)
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            self.assertEqual(p.stderr.strip(), "")
            data = json.loads(p.stdout)
            self.assertIn("gh_fetch_failed", data["warnings"])
            self.assertEqual(data["blockers"], ["iss-00301"])

    def test_deps_check_json_stdout_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001", "--json"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            data = json.loads(p.stdout)  # must be valid JSON
            self.assertTrue(data["ready"])
            self.assertEqual(data["target_status"]["source"], "local")
            self.assertEqual(p.stderr.strip(), "")

    def test_deps_check_missing_deps_json_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001", "--json"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            data = json.loads(p.stdout)
            self.assertTrue(data["ready"])
            self.assertEqual(data["effective_depends_on"], [])

    def test_deps_json_parse_error_fails_with_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
            )
            (issue_dir / "deps.json").write_text("{\n", encoding="utf-8")  # invalid JSON

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("deps.json", p.stderr)
            self.assertIn("Invalid JSON", p.stderr)

    def test_deps_json_schema_error_fails_with_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 2, "depends_on": []}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("deps.json", p.stderr)
            self.assertIn("schema_version", p.stderr)

    def test_deps_json_schema_rejects_boolean_dep_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [True]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("deps.json", p.stderr)
            self.assertIn("depends_on[0]", p.stderr)

    def test_deps_unresolved_ref_reports_ref_and_deps_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue one"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-issue-one"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-99999"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("iss-local-99999", p.stderr)
            self.assertIn("deps.json", p.stderr)

    def test_deps_canonicalizes_width_variants(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue one"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue two"])

            issue_two_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00002-issue-two"
            )
            (issue_two_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-1"]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00002", "--json"])
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            data = json.loads(p.stdout)
            self.assertEqual(data["effective_depends_on"], ["iss-local-00001"])

    def test_deps_github_number_requires_imported_node(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue one"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-issue-one"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [123]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("123", p.stderr)
            self.assertIn("deps.json", p.stderr)

    def test_deps_effective_depends_on_merges_parents_and_dedups(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Dep one"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Dep two"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Target"])

            # Dependency targets must not be within the same hierarchy, otherwise parent-merge would
            # create a self-dependency for that issue. Create an external dep issue.
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "External deps"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "2", "--title", "External epic"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "2", "--title", "External issue"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            target_issue_dir = epic_dir / "issues" / "iss-local-00003-target"

            # Parent initiative/epic both depend on the same dep (dedup expected).
            (init_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-4"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            (epic_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00004"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            (target_issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00002"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00003", "--json"])
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            data = json.loads(p.stdout)
            self.assertEqual(data["effective_depends_on"], ["iss-local-00002", "iss-local-00004"])

    def test_deps_effective_depends_on_merges_epic_and_initiative(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Dep one"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Dep two"])

            # External deps (must not be under the same parents as the target epic).
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "External deps"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "2", "--title", "External epic"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "2", "--title", "External issue one"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "2", "--title", "External issue two"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"

            (init_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00003"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            (epic_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00004"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "epic-local-00001", "--json"])
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            data = json.loads(p.stdout)
            self.assertEqual(data["effective_depends_on"], ["iss-local-00003", "iss-local-00004"])

    def test_deps_check_initiative_and_epic_target_status_does_not_fall_back_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue one"])

            for target_id in ("init-local-00001", "epic-local-00001"):
                with self.subTest(target_id=target_id):
                    p_json = self._run_runtime_capture(target, ["deps", "check", target_id, "--json"])
                    self.assertEqual(p_json.returncode, 0, p_json.stdout + p_json.stderr)
                    data = json.loads(p_json.stdout)
                    self.assertEqual(data["target"], target_id)
                    self.assertEqual(data["target_status"]["source"], "local")
                    self.assertEqual(data["target_status"]["authority"], "local")
                    self.assertFalse(data["target_status"]["stale"])

                    p_text = self._run_runtime_capture(target, ["deps", "check", target_id])
                    self.assertEqual(p_text.returncode, 0, p_text.stdout + p_text.stderr)
                    self.assertIn("source=local", p_text.stdout)
                    self.assertIn("stale=false", p_text.stdout)

    def test_deps_check_initiative_and_epic_target_status_uses_github_when_linked(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {
                        "number": 101,
                        "state": "OPEN",
                        "title": "Initiative",
                        "labels": [],
                        "updatedAt": "2026-03-20T10:00:00Z",
                        "url": "u",
                    },
                    {
                        "number": 201,
                        "state": "OPEN",
                        "title": "Epic",
                        "labels": [],
                        "updatedAt": "2026-03-20T11:00:00Z",
                        "url": "u",
                    },
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            for target_id, expected_last_sync_at in (
                ("init-00101", "2026-03-20T10:00:00Z"),
                ("epic-00201", "2026-03-20T11:00:00Z"),
            ):
                with self.subTest(target_id=target_id):
                    p_json = self._run_runtime_capture(
                        target,
                        ["deps", "check", target_id, "--github", "--json"],
                        env=test_env,
                    )
                    self.assertEqual(p_json.returncode, 0, p_json.stdout + p_json.stderr)
                    data = json.loads(p_json.stdout)
                    self.assertEqual(data["target"], target_id)
                    self.assertEqual(data["target_status"]["authority"], "github")
                    self.assertEqual(data["target_status"]["effective_status"], "open")
                    self.assertEqual(data["target_status"]["source"], "github")
                    self.assertFalse(data["target_status"]["stale"])
                    self.assertEqual(data["target_status"]["last_sync_at"], expected_last_sync_at)

                    p_text = self._run_runtime_capture(target, ["deps", "check", target_id, "--github"], env=test_env)
                    self.assertEqual(p_text.returncode, 0, p_text.stdout + p_text.stderr)
                    self.assertIn("source=github", p_text.stdout)
                    self.assertIn("stale=false", p_text.stdout)

    def test_deps_self_dependency_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue one"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-issue-one"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00001"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("iss-local-00001", p.stderr)
            self.assertIn("self edge produced", p.stderr)

    def test_deps_descendant_dependency_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue one"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            deps_path = init_dir / "deps.json"
            deps_path.write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00001"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "init-local-00001"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn(str(deps_path), p.stderr)
            self.assertIn("iss-local-00001", p.stderr)

    def test_deps_cycle_detected_in_reachable_graph(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue one"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue two"])

            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
            )
            issue_one_dir = epic_dir / "issues" / "iss-local-00001-issue-one"
            issue_two_dir = epic_dir / "issues" / "iss-local-00002-issue-two"

            (issue_one_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00002"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            (issue_two_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00001"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("iss-local-00001", p.stderr)
            self.assertIn("iss-local-00002", p.stderr)
            self.assertIn("->", p.stderr)

    def test_deps_check_ignores_unreachable_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Target"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Cycle a"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Cycle b"])

            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
            )
            cycle_a_dir = epic_dir / "issues" / "iss-local-00002-cycle-a"
            cycle_b_dir = epic_dir / "issues" / "iss-local-00003-cycle-b"
            (cycle_a_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00003"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            (cycle_b_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00002"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001", "--json"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("Dependency cycle detected", p.stderr)
            self.assertIn("iss-local-00002", p.stderr)
            self.assertIn("iss-local-00003", p.stderr)

    def test_sync_fails_on_deps_structural_error_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Target"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Cycle a"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Cycle b"])

            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
            )
            cycle_a_dir = epic_dir / "issues" / "iss-local-00002-cycle-a"
            cycle_b_dir = epic_dir / "issues" / "iss-local-00003-cycle-b"
            (cycle_a_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00003"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            (cycle_b_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00002"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("iss-local-00002", p.stderr)
            self.assertIn("iss-local-00003", p.stderr)
            self.assertIn("->", p.stderr)

    def test_sync_force_sets_deps_valid_false_and_emits_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Target"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Cycle a"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Cycle b"])

            agent_dir = target / "spec-dock" / ".agent"
            self._run_runtime(target, ["sync", "--no-update-active"])
            baseline_index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            self.assertTrue(baseline_index["deps"]["valid"])
            self.assertEqual(baseline_index["deps"]["issue_edges"], [])
            self.assertIsNone(baseline_index["deps"]["error"])

            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
            )
            cycle_a_dir = epic_dir / "issues" / "iss-local-00002-cycle-a"
            cycle_b_dir = epic_dir / "issues" / "iss-local-00003-cycle-b"
            (cycle_a_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00003"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            (cycle_b_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00002"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            (agent_dir / "index.json").unlink(missing_ok=True)
            (agent_dir / "tree.json").unlink(missing_ok=True)

            p = self._run_runtime_capture(target, ["sync", "--no-update-active", "--force"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("deps_preflight_failed", p.stderr)
            self.assertTrue((agent_dir / "index.json").is_file())
            self.assertTrue((agent_dir / "tree.json").is_file())
            self.assertTrue((agent_dir / "index-all.json").is_file())
            self.assertTrue((agent_dir / "tree-all.json").is_file())

            index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            self.assertFalse(index["deps"]["valid"])
            self.assertEqual(index["deps"]["issue_edges"], [])
            self.assertIn("Dependency cycle detected", str(index["deps"]["error"]))
            self.assertIn("deps_preflight_failed", index["warnings"])
            self.assertIsNone(index["nodes"]["iss-local-00001"]["deps"])
            self.assertIsNone(index["nodes"]["iss-local-00002"]["deps"])
            self.assertIsNone(index["nodes"]["iss-local-00003"]["deps"])

            index_all = json.loads((agent_dir / "index-all.json").read_text(encoding="utf-8"))
            self.assertFalse(index_all["deps"]["valid"])
            self.assertEqual(index_all["deps"]["issue_edges"], [])
            self.assertIn("Dependency cycle detected", str(index_all["deps"]["error"]))
            self.assertIn("deps_preflight_failed", index_all["warnings"])
            self.assertIsNone(index_all["nodes"]["iss-local-00001"]["deps"])
            self.assertIsNone(index_all["nodes"]["iss-local-00002"]["deps"])
            self.assertIsNone(index_all["nodes"]["iss-local-00003"]["deps"])

            tree = json.loads((agent_dir / "tree.json").read_text(encoding="utf-8"))
            self.assertFalse(tree["deps"]["valid"])
            self.assertEqual(tree["deps"]["issue_edges"], [])
            self.assertIn("Dependency cycle detected", str(tree["deps"]["error"]))
            self.assertIn("deps_preflight_failed", tree["warnings"])
            tree_issues = tree["tree"][0]["epics"][0]["issues"]
            tree_issue_deps = {issue["id"]: issue.get("deps") for issue in tree_issues}
            self.assertIsNone(tree_issue_deps["iss-local-00001"])
            self.assertIsNone(tree_issue_deps["iss-local-00002"])
            self.assertIsNone(tree_issue_deps["iss-local-00003"])

            tree_all = json.loads((agent_dir / "tree-all.json").read_text(encoding="utf-8"))
            self.assertFalse(tree_all["deps"]["valid"])
            self.assertEqual(tree_all["deps"]["issue_edges"], [])
            self.assertIn("Dependency cycle detected", str(tree_all["deps"]["error"]))
            self.assertIn("deps_preflight_failed", tree_all["warnings"])
            tree_all_issues = tree_all["tree"][0]["epics"][0]["issues"]
            tree_all_issue_deps = {issue["id"]: issue.get("deps") for issue in tree_all_issues}
            self.assertIsNone(tree_all_issue_deps["iss-local-00001"])
            self.assertIsNone(tree_all_issue_deps["iss-local-00002"])
            self.assertIsNone(tree_all_issue_deps["iss-local-00003"])

            deps_issues = json.loads((agent_dir / "deps-issues.json").read_text(encoding="utf-8"))
            self.assertFalse(deps_issues["deps"]["valid"])
            self.assertIn("Dependency cycle detected", str(deps_issues["deps"]["error"]))
            self.assertEqual(deps_issues["nodes"], {})
            self.assertEqual(deps_issues["edges"], [])

            tree_all_puml = (target / "spec-dock" / "tree-all.puml").read_text(encoding="utf-8")
            tree_todo_puml = (target / "spec-dock" / "tree.puml").read_text(encoding="utf-8")
            deps_issues_puml = (target / "spec-dock" / "deps-issues.puml").read_text(encoding="utf-8")
            dashboard = (target / "spec-dock" / "dashboard.md").read_text(encoding="utf-8")
            for text in (tree_all_puml, tree_todo_puml, deps_issues_puml, dashboard):
                self.assertIn("deps_preflight_failed", text)
                self.assertIn("deps.valid=false", text)
                self.assertIn("--force", text)

            self.assertFalse((agent_dir / "deps.json").exists())
            self.assertFalse((agent_dir / "deps.puml").exists())
            self.assertFalse((agent_dir / "deps.todo.puml").exists())

    def test_sync_force_removes_legacy_v1_deps_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Target"])

            agent_dir = target / "spec-dock" / ".agent"
            agent_dir.mkdir(parents=True, exist_ok=True)
            (agent_dir / "deps.json").write_text("{\"stale\": true}\n", encoding="utf-8")
            (agent_dir / "deps.puml").write_text("@startuml\n@enduml\n", encoding="utf-8")
            (agent_dir / "deps.todo.puml").write_text("@startuml\n@enduml\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["sync", "--no-update-active", "--force"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            self.assertFalse((agent_dir / "deps.json").exists())
            self.assertFalse((agent_dir / "deps.puml").exists())
            self.assertFalse((agent_dir / "deps.todo.puml").exists())

    def test_deps_commands_do_not_mutate_meta_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
                / ".meta.json"
            )
            before = issue_meta.read_text(encoding="utf-8")
            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001", "--json"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            after = issue_meta.read_text(encoding="utf-8")
            self.assertEqual(after, before)
