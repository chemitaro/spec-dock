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


class TestCliImport(CliRuntimeHarness):
    _STANDARD_INITIATIVE_ID = "init-00001"
    _STANDARD_INITIATIVE_DIRNAME = "init-00001-auth-platform"
    _STANDARD_EPIC_ID = "epic-00002"
    _STANDARD_EPIC_DIRNAME = "epic-00002-jwt-auth"

    def _create_linked_parents(
        self,
        target: Path,
        *,
        owner: str = "example",
        repo: str = "repo",
        initiative_issue_number: int = 1,
        epic_issue_number: int = 2,
        initiative_title: str = "Auth platform",
        epic_title: str = "JWT auth",
    ) -> None:
        self._init_origin_repo(target, owner=owner, repo=repo)
        self._run_runtime(
            target,
            [
                "new",
                "initiative",
                "--title",
                initiative_title,
                "--github-issue",
                str(initiative_issue_number),
            ],
        )
        self._run_runtime(
            target,
            [
                "new",
                "epic",
                "--initiative",
                str(initiative_issue_number),
                "--title",
                epic_title,
                "--github-issue",
                str(epic_issue_number),
            ],
        )

    def _create_standard_linked_hierarchy(
        self,
        target: Path,
        *,
        owner: str = "example",
        repo: str = "repo",
        issue_issue_number: int = 3,
        issue_title: str = "Add refresh token",
    ) -> None:
        self._create_same_repo_linked_hierarchy(
            target,
            owner=owner,
            repo=repo,
            initiative_issue_number=1,
            epic_issue_number=2,
            issue_issue_number=issue_issue_number,
            initiative_title="Auth platform",
            epic_title="JWT auth",
            issue_title=issue_title,
        )

    def _standard_initiative_meta_path(self, target: Path) -> Path:
        return target / "spec-dock" / "initiatives" / self._STANDARD_INITIATIVE_DIRNAME / ".meta.json"

    def _standard_epic_meta_path(self, target: Path) -> Path:
        return (
            target
            / "spec-dock"
            / "initiatives"
            / self._STANDARD_INITIATIVE_DIRNAME
            / "epics"
            / self._STANDARD_EPIC_DIRNAME
            / ".meta.json"
        )

    def _strip_repo_scope(self, meta_path: Path) -> None:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        github = meta.get("github")
        self.assertIsInstance(github, dict)
        github_dict = github
        github_dict.pop("repo_owner", None)
        github_dict.pop("repo_name", None)
        self._write_json_force(meta_path, meta)

    def _make_standard_parents_unscoped(self, target: Path) -> None:
        self._strip_repo_scope(self._standard_initiative_meta_path(target))
        self._strip_repo_scope(self._standard_epic_meta_path(target))

    def test_import_aborts_without_local_changes_when_gh_issue_view_fails(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_linked_parents(target, initiative_title="Parent initiative", epic_title="Parent epic")

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir, failing_numbers={99999})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "99999", "--title", "Imported issue", "--epic", "epic-00002"],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)

            imported = list((target / "spec-dock" / "initiatives").rglob("iss-99999-*"))
            self.assertEqual(imported, [])
            self.assertFalse((target / "spec-dock" / ".agent" / "index.json").exists())
            self.assertFalse((target / "spec-dock" / ".agent" / "tree.json").exists())

    def test_import_fails_preflight_on_legacy_meta_without_creating_nodes(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Import target lineage (canonical .meta.json)
            self._create_linked_parents(target, initiative_title="Parent initiative", epic_title="Parent epic")
            # Unrelated legacy file to trigger preflight failure.
            self._run_runtime(target, ["new", "initiative", "--title", "Legacy holder", "--github-issue", "99"])

            legacy_init_dir = target / "spec-dock" / "initiatives" / "init-00099-legacy-holder"
            dot_meta_path = legacy_init_dir / ".meta.json"
            legacy_meta_path = legacy_init_dir / "meta.json"
            dot_meta_path.rename(legacy_meta_path)
            self.assertFalse(dot_meta_path.exists())
            self.assertTrue(legacy_meta_path.is_file())

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "99999", "--title", "Imported issue", "--epic", "epic-00002"],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("Unsupported legacy meta.json detected", p.stderr)
            self.assertIn(str(legacy_meta_path), p.stderr)

            imported = list((target / "spec-dock" / "initiatives").rglob("iss-99999-*"))
            self.assertEqual(imported, [])
            self.assertFalse((target / "spec-dock" / ".agent" / "index.json").exists())
            self.assertFalse((target / "spec-dock" / ".agent" / "tree.json").exists())

    def test_import_initiative_creates_node_and_runs_sync_without_updating_active(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_git(target, ["init"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )
            self._run_git(target, ["checkout", "-b", "feature/init-00010-check"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "initiative", "10", "--title", "Auth platform"],
                env=test_env,
            )
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok (import initiative)", p.stdout)
            self.assertIn("id=init-00010", p.stdout)
            self.assertIn("path=", p.stdout)
            self.assertIn("github=#10", p.stdout)

            init_dir = target / "spec-dock" / "initiatives" / "init-00010-auth-platform"
            self.assertTrue(init_dir.is_dir())
            meta = json.loads((init_dir / ".meta.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["id"], "init-00010")
            self.assertEqual(meta["github"]["issue_number"], 10)
            self._assert_spec_dock_meta_marker(meta)
            self._assert_readonly_on_posix(init_dir / ".meta.json")
            self.assertTrue((target / "spec-dock" / ".agent" / "index.json").is_file())
            self.assertTrue((target / "spec-dock" / ".agent" / "tree.json").is_file())
            self.assertFalse((target / "spec-dock" / ".agent" / "active.json").exists())

    def test_import_epic_and_initiative_create_nodes(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            self._run_runtime(target, ["import", "initiative", "10", "--title", "Auth platform"], env=test_env)
            self._run_runtime(target, ["import", "epic", "11", "--title", "JWT auth", "--initiative", "10"], env=test_env)

            init_dir = target / "spec-dock" / "initiatives" / "init-00010-auth-platform"
            epic_dir = init_dir / "epics" / "epic-00011-jwt-auth"
            self.assertTrue(init_dir.is_dir())
            self.assertTrue(epic_dir.is_dir())

            init_meta = json.loads((init_dir / ".meta.json").read_text(encoding="utf-8"))
            epic_meta = json.loads((epic_dir / ".meta.json").read_text(encoding="utf-8"))
            self.assertEqual(init_meta["id"], "init-00010")
            self.assertEqual(init_meta["github"]["issue_number"], 10)
            self.assertEqual(epic_meta["id"], "epic-00011")
            self.assertEqual(epic_meta["parent_id"], "init-00010")
            self.assertEqual(epic_meta["initiative_id"], "init-00010")
            self.assertEqual(epic_meta["github"]["issue_number"], 11)
            self._assert_spec_dock_meta_marker(init_meta)
            self._assert_spec_dock_meta_marker(epic_meta)
            self._assert_readonly_on_posix(init_dir / ".meta.json")
            self._assert_readonly_on_posix(epic_dir / ".meta.json")

            expected_rules_links = {
                init_dir / "epics" / "rules.md": target / "spec-dock" / "docs" / "rules" / "initiative" / "epics.md",
                init_dir / "discussions" / "rules.md": (
                    target / "spec-dock" / "docs" / "rules" / "initiative" / "discussions.md"
                ),
                epic_dir / "issues" / "rules.md": target / "spec-dock" / "docs" / "rules" / "epic" / "issues.md",
                epic_dir / "discussions" / "rules.md": target / "spec-dock" / "docs" / "rules" / "epic" / "discussions.md",
            }
            for link_path, target_path in expected_rules_links.items():
                self.assertTrue(link_path.is_symlink(), f"missing imported rules symlink: {link_path}")
                self.assertEqual(link_path.resolve(), target_path.resolve())
                self.assertEqual(os.readlink(link_path), os.path.relpath(target_path, start=link_path.parent))

            for scope_dir in (
                init_dir / "epics",
                init_dir / "discussions",
                epic_dir / "issues",
                epic_dir / "discussions",
            ):
                self.assertEqual(list(scope_dir.glob("new-*")), [], f"unexpected wrapper(s) in {scope_dir}")

    def test_import_issue_creates_node_and_runs_sync_without_updating_active(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_git(target, ["init"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )
            self._run_git(target, ["checkout", "-b", "feature/iss-00123-check"])

            self._create_linked_parents(target)
            self._run_runtime(target, ["active", "set", "epic-00002"])

            active_path = target / "spec-dock" / ".agent" / "active.json"
            before = active_path.read_text(encoding="utf-8")

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Add refresh token", "--epic", "epic-00002"],
                env=test_env,
            )
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok (import issue)", p.stdout)
            self.assertIn("id=iss-00123", p.stdout)
            self.assertIn("epic=epic-00002", p.stdout)
            self.assertIn("initiative=init-00001", p.stdout)
            self.assertIn("path=", p.stdout)
            self.assertIn("github=#123", p.stdout)

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
            self.assertTrue((target / "spec-dock" / ".agent" / "index.json").is_file())
            self.assertTrue((target / "spec-dock" / ".agent" / "tree.json").is_file())

            after = active_path.read_text(encoding="utf-8")
            self.assertEqual(before, after)

    def test_import_accepts_number_hash_and_url_equivalently(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        targets = [
            "123",
            "#123",
            "https://github.com/example/repo/issues/123",
        ]
        for issue_target in targets:
            with self.subTest(issue_target=issue_target):
                with tempfile.TemporaryDirectory() as tmp:
                    target = Path(tmp)
                    self.assertEqual(main(["init", str(target)]), 0)
                    self._create_linked_parents(target)

                    bin_dir = target / ".bin"
                    bin_dir.mkdir(parents=True, exist_ok=True)
                    log_path = target / ".gh.log"
                    self._make_gh_issue_view_stub(bin_dir, log_path=log_path)
                    test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                    self._run_runtime(
                        target,
                        ["import", "issue", issue_target, "--title", "Imported issue", "--epic", "epic-00002"],
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
                        / "iss-00123-imported-issue"
                    )
                    self.assertTrue(issue_dir.is_dir())
                    log = log_path.read_text(encoding="utf-8")
                    self.assertIn("issue view 123", log)
                    self.assertNotIn("--repo other/repo", log)

    def test_import_rejects_foreign_repo_url_without_opt_in(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_linked_parents(target)
            self._make_standard_parents_unscoped(target)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            self._make_gh_issue_view_stub(bin_dir, log_path=log_path)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                [
                    "import",
                    "issue",
                    "https://github.com/other/repo/issues/123",
                    "--title",
                    "Imported issue",
                    "--epic",
                    "epic-00002",
                ],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("foreign GitHub issue URL", p.stderr)
            self.assertIn("single-repo", p.stderr)
            self.assertIn("--allow-foreign-url", p.stderr)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-imported-issue"
            )
            self.assertFalse(issue_dir.exists())
            self.assertFalse(log_path.exists())

    def test_import_rejects_foreign_repo_url_even_with_opt_in(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_linked_parents(target)
            self._make_standard_parents_unscoped(target)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            self._make_gh_issue_view_stub(bin_dir, log_path=log_path)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                [
                    "import",
                    "issue",
                    "https://github.com/other/repo/issues/123",
                    "--allow-foreign-url",
                    "--title",
                    "Imported issue",
                    "--epic",
                    "epic-00002",
                ],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("foreign GitHub issue URL", p.stderr)
            self.assertIn("single-repo", p.stderr)
            self.assertIn("--allow-foreign-url", p.stderr)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-imported-issue"
            )
            self.assertFalse(issue_dir.exists())
            self.assertFalse(log_path.exists())

    def test_import_rejects_non_canonical_url_like_target(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_linked_parents(target)
            self._make_standard_parents_unscoped(target)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                [
                    "import",
                    "issue",
                    "git@github.com:other/repo/issues/123",
                    "--title",
                    "Imported issue",
                    "--epic",
                    "epic-00002",
                ],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("Invalid target", p.stderr)

    def test_import_url_rejects_when_origin_is_not_configured(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_linked_parents(target)
            self._make_standard_parents_unscoped(target)
            self._run_git(target, ["remote", "remove", "origin"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                [
                    "import",
                    "issue",
                    "https://github.com/example/repo/issues/123",
                    "--title",
                    "Imported issue",
                    "--epic",
                    "epic-00002",
                ],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("Cannot verify GitHub URL repository", p.stderr)

    def test_import_url_rejects_when_origin_is_not_github(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_linked_parents(target)
            self._run_git(target, ["remote", "set-url", "origin", "https://example.com/owner/repo.git"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                [
                    "import",
                    "issue",
                    "https://github.com/example/repo/issues/123",
                    "--title",
                    "Imported issue",
                    "--epic",
                    "epic-00002",
                ],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("Cannot verify GitHub URL repository", p.stderr)

    def test_import_accepts_canonical_url_when_origin_is_ssh_remote(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_linked_parents(target)
            self._run_git(target, ["remote", "set-url", "origin", "git@github.com:example/repo.git"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                [
                    "import",
                    "issue",
                    "https://github.com/example/repo/issues/123",
                    "--title",
                    "Imported issue",
                    "--epic",
                    "epic-00002",
                ],
                env=test_env,
            )
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok (import issue)", p.stdout)

    def test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_linked_parents(target)
            self._run_git(
                target,
                ["remote", "set-url", "origin", "https://token@github.com/example/repo.git"],
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                [
                    "import",
                    "issue",
                    "https://github.com/example/repo/issues/123",
                    "--title",
                    "Imported issue",
                    "--epic",
                    "epic-00002",
                ],
                env=test_env,
            )
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok (import issue)", p.stdout)

    def test_import_issue_uses_active_epic_when_parent_not_specified(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_linked_parents(target)
            self._run_runtime(target, ["active", "set", "epic-00002"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            self._run_runtime(target, ["import", "issue", "123", "--title", "Add refresh token"], env=test_env)
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

    def test_import_epic_uses_active_initiative_when_parent_not_specified(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_linked_parents(target)
            self._run_runtime(target, ["active", "set", "init-00001"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            self._run_runtime(target, ["import", "epic", "124", "--title", "JWT auth"], env=test_env)
            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00124-jwt-auth"
            )
            self.assertTrue(epic_dir.is_dir())

    def test_import_issue_requires_parent_when_no_epic_and_active_unavailable(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_linked_parents(target)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["import", "issue", "123", "--title", "Add refresh token"], env=test_env)
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("--epic", p.stderr)

    def test_import_parent_fallback_errors_on_stale_active(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_linked_parents(target)

            broken_active = {
                "schema_version": 2,
                "updated_at": "2026-01-01T00:00:00+00:00",
                "initiative": {"id": "init-local-99999", "path": "spec-dock/initiatives/init-local-99999-x"},
                "epic": {"id": "epic-local-99999", "path": "spec-dock/initiatives/init-local-99999-x/epics/epic-local-99999-y"},
                "issue": None,
            }
            (target / "spec-dock" / ".agent" / "active.json").write_text(
                json.dumps(broken_active, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["import", "issue", "123", "--title", "Add refresh token"], env=test_env)
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("--epic", p.stderr)

    def test_import_rejects_invalid_or_wrong_type_parent_id(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_linked_parents(target)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p1 = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Add refresh token", "--epic", "init-00001"],
                env=test_env,
            )
            self.assertNotEqual(p1.returncode, 0, p1.stdout + p1.stderr)

            p2 = self._run_runtime_capture(
                target,
                ["import", "issue", "124", "--title", "Add refresh token", "--epic", "epic-99999"],
                env=test_env,
            )
            self.assertNotEqual(p2.returncode, 0, p2.stdout + p2.stderr)

            p3 = self._run_runtime_capture(
                target,
                ["import", "epic", "125", "--title", "JWT auth", "--initiative", "epic-00002"],
                env=test_env,
            )
            self.assertNotEqual(p3.returncode, 0, p3.stdout + p3.stderr)

    def test_import_rejects_already_linked_github_issue_number(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_linked_parents(target)
            self._make_standard_parents_unscoped(target)
            self._run_runtime(target, ["new", "initiative", "--title", "Linked initiative", "--github-issue", "123"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Add refresh token", "--epic", "epic-00002"],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("already linked", p.stderr)
            self.assertIn("different GitHub issue number", p.stderr)
            self.assertNotIn("--github-issue", p.stderr)

    def test_import_rejects_same_repo_url_duplicate_when_existing_link_omits_repo_fields(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_standard_linked_hierarchy(target, issue_issue_number=123, issue_title="Current issue")
            self._make_standard_parents_unscoped(target)

            current_issue_meta = (
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
            current_meta = json.loads(current_issue_meta.read_text(encoding="utf-8"))
            self.assertEqual(current_meta["github"]["issue_number"], 123)
            self.assertEqual(current_meta["github"]["repo_owner"], "example")
            self.assertEqual(current_meta["github"]["repo_name"], "repo")
            # Simulate legacy unscoped linkage persisted before S03L write-time normalization.
            current_meta["github"] = {"issue_number": 123}
            self._write_json_force(current_issue_meta, current_meta)
            current_meta = json.loads(current_issue_meta.read_text(encoding="utf-8"))
            self.assertNotIn("repo_owner", current_meta["github"])
            self.assertNotIn("repo_name", current_meta["github"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                [
                    "import",
                    "issue",
                    "https://github.com/example/repo/issues/123",
                    "--title",
                    "Duplicate current issue",
                    "--epic",
                    "epic-00002",
                ],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("already linked", p.stderr)
            self.assertIn("repo=example/repo", p.stderr)
            self.assertIn("github.issue_number=123", p.stderr)

            duplicate_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-duplicate-current-issue"
            )
            self.assertFalse(duplicate_issue_dir.exists())

    def test_import_persists_current_repo_scope_when_origin_is_resolved(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_linked_parents(target)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Current issue", "--epic", "epic-00002"],
                env=test_env,
            )
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            imported_meta_path = (
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
            imported_meta = json.loads(imported_meta_path.read_text(encoding="utf-8"))
            self.assertEqual(imported_meta["github"]["issue_number"], 123)
            self.assertEqual(imported_meta["github"]["repo_owner"], "example")
            self.assertEqual(imported_meta["github"]["repo_name"], "repo")

    def test_import_rejects_same_issue_number_between_unscoped_and_foreign_when_current_repo_unknown(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_standard_linked_hierarchy(target, issue_issue_number=123, issue_title="Current issue")
            self._make_standard_parents_unscoped(target)
            current_issue_meta = (
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
            self._strip_repo_scope(current_issue_meta)
            self._run_git(target, ["remote", "remove", "origin"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                [
                    "import",
                    "issue",
                    "https://github.com/other/repo/issues/123",
                    "--allow-foreign-url",
                    "--title",
                    "Foreign issue",
                    "--epic",
                    "epic-00002",
                ],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("Cannot verify GitHub URL repository", p.stderr)
            self.assertIn("single-repo", p.stderr)
            self.assertIn("GitHub-backed identity", p.stderr)
            self.assertIn("--allow-foreign-url", p.stderr)

            foreign_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-local-00001-foreign-issue"
            )
            self.assertFalse(foreign_issue_dir.exists())

    def test_import_rejects_foreign_repo_when_current_repo_unknown_without_writes(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_linked_parents(target)
            self._make_standard_parents_unscoped(target)
            self._run_git(target, ["remote", "remove", "origin"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            issues_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
            )
            p = self._run_runtime_capture(
                target,
                [
                    "import",
                    "issue",
                    "https://github.com/other/repo/issues/123",
                    "--allow-foreign-url",
                    "--title",
                    "Foreign issue",
                    "--epic",
                    "epic-00002",
                ],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("single-repo", p.stderr)
            self.assertIn("GitHub-backed identity", p.stderr)
            self.assertEqual(sorted(issues_dir.glob("*-foreign-issue")), [])

            p = self._run_runtime_capture(
                target,
                [
                    "new",
                    "issue",
                    "--epic",
                    "epic-00002",
                    "--title",
                    "Current issue",
                    "--github-issue",
                    "123",
                ],
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("origin remote is missing", p.stderr)

            self.assertEqual(sorted(issues_dir.glob("*-current-issue")), [])

    def test_import_rejects_foreign_repo_when_current_repo_is_resolved(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_standard_linked_hierarchy(target, issue_issue_number=123, issue_title="Current issue")
            self._make_standard_parents_unscoped(target)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                [
                    "import",
                    "issue",
                    "https://github.com/other/repo/issues/123",
                    "--allow-foreign-url",
                    "--title",
                    "Foreign issue",
                    "--epic",
                    "epic-00002",
                ],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("single-repo", p.stderr)
            self.assertIn("GitHub-backed identity", p.stderr)
            self.assertIn("foreign GitHub issue URL", p.stderr)

            current_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-current-issue"
            )
            foreign_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-local-00001-foreign-issue"
            )
            self.assertTrue(current_issue_dir.is_dir())
            self.assertFalse(foreign_issue_dir.exists())

            current_meta = json.loads((current_issue_dir / ".meta.json").read_text(encoding="utf-8"))
            self.assertEqual(current_meta["id"], "iss-00123")
            self.assertEqual(current_meta["github"]["issue_number"], 123)

    def test_import_rejects_foreign_repo_duplicate_attempts_without_writes(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_linked_parents(target)
            self._make_standard_parents_unscoped(target)
            self._run_git(target, ["remote", "remove", "origin"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                [
                    "import",
                    "issue",
                    "https://github.com/other/repo/issues/123",
                    "--allow-foreign-url",
                    "--title",
                    "Foreign issue duplicate",
                    "--epic",
                    "epic-00002",
                ],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("single-repo", p.stderr)
            self.assertIn("GitHub-backed identity", p.stderr)
            self.assertEqual(sorted((target / "spec-dock" / "initiatives").rglob("iss-local-00001-*")), [])

    def test_import_rejects_invalid_slug_and_invalid_title(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_linked_parents(target)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            self._make_gh_issue_view_stub(bin_dir, log_path=log_path)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p1 = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Add refresh token", "--epic", "epic-00002", "--slug", "Bad!Slug"],
                env=test_env,
            )
            self.assertNotEqual(p1.returncode, 0, p1.stdout + p1.stderr)
            self.assertIn("--slug", p1.stderr)
            self.assertIn("expected regex", p1.stderr)

            p2 = self._run_runtime_capture(
                target,
                ["import", "issue", "124", "--title", "!!!", "--epic", "epic-00002"],
                env=test_env,
            )
            self.assertNotEqual(p2.returncode, 0, p2.stdout + p2.stderr)
            self.assertIn("--title", p2.stderr)
            self.assertIn("expected regex", p2.stderr)
            if log_path.exists():
                self.assertEqual(log_path.read_text(encoding="utf-8").strip(), "")

            imported = list((target / "spec-dock" / "initiatives").rglob("iss-00124-*"))
            self.assertEqual(imported, [])

    def test_import_rejects_invalid_title_before_gh_issue_view(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_linked_parents(target)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            self._make_gh_issue_view_stub(bin_dir, log_path=log_path)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "日本語", "--epic", "epic-00002"],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("--title", p.stderr)
            self.assertIn("expected regex", p.stderr)
            if log_path.exists():
                self.assertEqual(log_path.read_text(encoding="utf-8").strip(), "")

            imported = list((target / "spec-dock" / "initiatives").rglob("iss-00123-*"))
            self.assertEqual(imported, [])

    def test_import_fails_when_sync_preflight_fails(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_linked_parents(target)

            init_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / ".meta.json"
            )
            data = json.loads(init_meta.read_text(encoding="utf-8"))
            data["slug"] = "BrokenSlug"
            self._write_json_force(init_meta, data)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            self._make_gh_issue_view_stub(bin_dir, log_path=log_path)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Add refresh token", "--epic", "epic-00002"],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("preflight validate failed", p.stderr)
            self.assertIn("slug must be lowercase", p.stderr)
            if log_path.exists():
                self.assertEqual(log_path.read_text(encoding="utf-8").strip(), "")

            imported = list((target / "spec-dock" / "initiatives").rglob("iss-00123-*"))
            self.assertEqual(imported, [])

    def test_import_fails_preflight_on_partial_scope_linkage_before_duplicate_or_gh_view(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_standard_linked_hierarchy(target, issue_issue_number=123, issue_title="Current issue")

            current_issue_meta = (
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
            current_meta = json.loads(current_issue_meta.read_text(encoding="utf-8"))
            current_meta["github"] = {"issue_number": 123, "repo_owner": "example"}
            self._write_json_force(current_issue_meta, current_meta)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            self._make_gh_issue_view_stub(bin_dir, log_path=log_path)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Duplicate current issue", "--epic", "epic-00002"],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("preflight validate failed", p.stderr)
            self.assertIn("Invalid github.repo_owner/repo_name", p.stderr)
            self.assertIn("both fields are required", p.stderr)
            self.assertNotIn("already linked", p.stderr)
            if log_path.exists():
                self.assertEqual(log_path.read_text(encoding="utf-8").strip(), "")

            duplicate_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-duplicate-current-issue"
            )
            self.assertFalse(duplicate_issue_dir.exists())

    def test_import_fails_preflight_when_required_artifact_is_missing_without_creating_node(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_standard_linked_hierarchy(target, issue_title="Existing issue")

            missing_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-existing-issue"
                / "report.md"
            )
            missing_path.unlink(missing_ok=False)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            self._make_gh_issue_view_stub(bin_dir, log_path=log_path)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Imported issue", "--epic", "epic-00002"],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("preflight validate failed", p.stderr)
            self.assertIn("Missing required artifact", p.stderr)
            self.assertIn("report.md", p.stderr)
            if log_path.exists():
                self.assertEqual(log_path.read_text(encoding="utf-8").strip(), "")

            imported = list((target / "spec-dock" / "initiatives").rglob("iss-00123-*"))
            self.assertEqual(imported, [])

    def test_import_rejects_ambiguous_parent_id_shorthand_when_both_local_and_github_exist(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Create both GitHub and local variants with the same numeric suffix.
            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--github-issue", "10", "--title", "GitHub initiative"])
            github_dir = target / "spec-dock" / "initiatives" / "init-00010-github-initiative"
            local_dir = target / "spec-dock" / "initiatives" / "init-local-00010-local-initiative"
            shutil.copytree(github_dir, local_dir)
            local_meta_path = local_dir / ".meta.json"
            local_meta = json.loads(local_meta_path.read_text(encoding="utf-8"))
            local_meta["id"] = "init-local-00010"
            local_meta["slug"] = "local-initiative"
            local_meta["title"] = "Local initiative"
            local_meta.pop("github", None)
            self._write_json_force(local_meta_path, local_meta)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "epic", "11", "--title", "JWT auth", "--initiative", "10"],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("ambiguous", p.stderr.lower())

            imported = list((target / "spec-dock" / "initiatives").rglob("epic-00011-*"))
            self.assertEqual(imported, [])

    def test_import_aborts_without_local_changes_when_gh_issue_view_returns_non_json(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_linked_parents(target, initiative_title="Parent initiative", epic_title="Parent epic")

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                'if [[ \"$1\" == \"issue\" && \"$2\" == \"view\" ]]; then\n'
                "  echo \"NOT_JSON\"\n"
                "  exit 0\n"
                "fi\n"
                "echo \"unexpected gh args: $@\" >&2\n"
                "exit 99\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Imported issue", "--epic", "epic-00002"],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)

            imported = list((target / "spec-dock" / "initiatives").rglob("iss-00123-*"))
            self.assertEqual(imported, [])
            self.assertFalse((target / "spec-dock" / ".agent" / "index.json").exists())
            self.assertFalse((target / "spec-dock" / ".agent" / "tree.json").exists())

    def test_import_does_not_migrate_legacy_active_manifest(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_linked_parents(target)

            init_path = "spec-dock/initiatives/init-00001-auth-platform"
            epic_path = f"{init_path}/epics/epic-00002-jwt-auth"

            legacy_dir = target / "spec-dock" / ".work"
            legacy_dir.mkdir(parents=True, exist_ok=True)
            legacy_active_path = legacy_dir / "active.json"
            legacy_active_path.write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "updated_at": "2026-01-01T00:00:00+00:00",
                        "initiative": {"id": "init-00001", "path": init_path},
                        "epic": {"id": "epic-00002", "path": epic_path},
                        "issue": None,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            self._run_runtime(target, ["import", "issue", "123", "--title", "Add refresh token"], env=test_env)

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
            self.assertFalse((target / "spec-dock" / ".agent" / "active.json").exists())
            self.assertTrue(legacy_active_path.is_file())
