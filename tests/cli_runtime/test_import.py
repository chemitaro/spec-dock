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
    def test_import_aborts_without_local_changes_when_gh_issue_view_fails(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Parent initiative"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "Parent epic"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir, failing_numbers={99999})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "99999", "--title", "Imported issue", "--epic", "epic-local-00001"],
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
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Parent initiative"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "Parent epic"])
            # Unrelated legacy file to trigger preflight failure.
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Legacy holder"])

            legacy_init_dir = target / "spec-dock" / "initiatives" / "init-local-00002-legacy-holder"
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
                ["import", "issue", "99999", "--title", "Imported issue", "--epic", "epic-local-00001"],
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

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["active", "set", "epic-local-00001"])

            active_path = target / "spec-dock" / ".agent" / "active.json"
            before = active_path.read_text(encoding="utf-8")

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Add refresh token", "--epic", "epic-local-00001"],
                env=test_env,
            )
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok (import issue)", p.stdout)
            self.assertIn("id=iss-00123", p.stdout)
            self.assertIn("epic=epic-local-00001", p.stdout)
            self.assertIn("initiative=init-local-00001", p.stdout)
            self.assertIn("path=", p.stdout)
            self.assertIn("github=#123", p.stdout)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
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
                    if issue_target.startswith("https://"):
                        if shutil.which("git") is None:
                            self.skipTest("git not available")
                        self._run_git(target, ["init"])
                        self._run_git(target, ["remote", "add", "origin", "https://github.com/example/repo.git"])
                    self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
                    self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

                    bin_dir = target / ".bin"
                    bin_dir.mkdir(parents=True, exist_ok=True)
                    log_path = target / ".gh.log"
                    self._make_gh_issue_view_stub(bin_dir, log_path=log_path)
                    test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                    self._run_runtime(
                        target,
                        ["import", "issue", issue_target, "--title", "Imported issue", "--epic", "epic-local-00001"],
                        env=test_env,
                    )

                    issue_dir = (
                        target
                        / "spec-dock"
                        / "initiatives"
                        / "init-local-00001-auth-platform"
                        / "epics"
                        / "epic-local-00001-jwt-auth"
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
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/example/repo.git"])
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

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
                    "epic-local-00001",
                ],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("repository mismatch", p.stderr)
            self.assertIn("--allow-foreign-url", p.stderr)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-00123-imported-issue"
            )
            self.assertFalse(issue_dir.exists())
            self.assertFalse(log_path.exists())

    def test_import_allows_foreign_repo_url_with_opt_in(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/example/repo.git"])
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

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
                    "epic-local-00001",
                ],
                env=test_env,
            )
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok (import issue)", p.stdout)
            self.assertIn("github=#123", p.stdout)
            log = log_path.read_text(encoding="utf-8")
            self.assertIn("issue view 123 --json number,url --repo other/repo", log)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-00123-imported-issue"
            )
            meta = json.loads((issue_dir / ".meta.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["github"]["issue_number"], 123)
            self.assertEqual(meta["github"]["repo_owner"], "other")
            self.assertEqual(meta["github"]["repo_name"], "repo")

    def test_import_rejects_non_canonical_url_like_target(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

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
                    "epic-local-00001",
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
            self._run_git(target, ["init"])
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

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
                    "epic-local-00001",
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
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://example.com/owner/repo.git"])
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

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
                    "epic-local-00001",
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
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "git@github.com:example/repo.git"])
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

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
                    "epic-local-00001",
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
            self._run_git(target, ["init"])
            self._run_git(
                target,
                ["remote", "add", "origin", "https://token@github.com/example/repo.git"],
            )
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

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
                    "epic-local-00001",
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
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["active", "set", "epic-local-00001"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            self._run_runtime(target, ["import", "issue", "123", "--title", "Add refresh token"], env=test_env)
            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
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
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["active", "set", "init-local-00001"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            self._run_runtime(target, ["import", "epic", "124", "--title", "JWT auth"], env=test_env)
            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
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
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

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
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

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
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p1 = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Add refresh token", "--epic", "init-local-00001"],
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
                ["import", "epic", "125", "--title", "JWT auth", "--initiative", "epic-local-00001"],
                env=test_env,
            )
            self.assertNotEqual(p3.returncode, 0, p3.stdout + p3.stderr)

    def test_import_rejects_already_linked_github_issue_number(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--title", "Linked initiative", "--github-issue", "123"])
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Add refresh token", "--epic", "epic-local-00001"],
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
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/example/repo.git"])

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Current issue", "--github-issue", "123"])

            current_issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
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
                    "epic-local-00001",
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
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
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
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/example/repo.git"])

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Current issue", "--epic", "epic-local-00001"],
                env=test_env,
            )
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            imported_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
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
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Current issue", "--github-issue", "123"])

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
                    "epic-local-00001",
                ],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("fail-closed", p.stderr)
            self.assertIn("github linkage scope is ambiguous", p.stderr)
            self.assertIn("github.issue_number=123", p.stderr)

            foreign_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-foreign-issue"
            )
            self.assertFalse(foreign_issue_dir.exists())

    def test_new_rejects_same_issue_number_between_foreign_and_unscoped_when_current_repo_unknown(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            self._run_runtime(
                target,
                [
                    "import",
                    "issue",
                    "https://github.com/other/repo/issues/123",
                    "--allow-foreign-url",
                    "--title",
                    "Foreign issue",
                    "--epic",
                    "epic-local-00001",
                ],
                env=test_env,
            )

            issues_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
            )
            imported_foreign_dirs = sorted(issues_dir.glob("*-foreign-issue"))
            self.assertEqual(len(imported_foreign_dirs), 1, imported_foreign_dirs)
            foreign_issue_dir = imported_foreign_dirs[0]
            self.assertTrue(foreign_issue_dir.is_dir())
            foreign_meta = json.loads((foreign_issue_dir / ".meta.json").read_text(encoding="utf-8"))
            self.assertEqual(foreign_meta["github"]["issue_number"], 123)
            self.assertEqual(foreign_meta["github"]["repo_owner"], "other")
            self.assertEqual(foreign_meta["github"]["repo_name"], "repo")

            p = self._run_runtime_capture(
                target,
                [
                    "new",
                    "issue",
                    "--epic",
                    "epic-local-00001",
                    "--title",
                    "Current issue",
                    "--github-issue",
                    "123",
                ],
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("fail-closed", p.stderr)
            self.assertIn("github linkage scope is ambiguous", p.stderr)
            self.assertIn("repo=(current-or-unknown) github.issue_number=123", p.stderr)

            self.assertEqual(sorted(issues_dir.glob("*-current-issue")), [])

    def test_import_allows_same_issue_number_between_current_and_foreign_when_current_repo_resolved(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/example/repo.git"])
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Current issue", "--github-issue", "123"])

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
                    "epic-local-00001",
                ],
                env=test_env,
            )
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            current_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-00123-current-issue"
            )
            foreign_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-foreign-issue"
            )
            self.assertTrue(current_issue_dir.is_dir())
            self.assertTrue(foreign_issue_dir.is_dir())

            current_meta = json.loads((current_issue_dir / ".meta.json").read_text(encoding="utf-8"))
            foreign_meta = json.loads((foreign_issue_dir / ".meta.json").read_text(encoding="utf-8"))
            self.assertEqual(current_meta["id"], "iss-00123")
            self.assertEqual(current_meta["github"]["issue_number"], 123)
            self.assertEqual(foreign_meta["id"], "iss-local-00001")
            self.assertEqual(foreign_meta["github"]["issue_number"], 123)
            self.assertEqual(foreign_meta["github"]["repo_owner"], "other")
            self.assertEqual(foreign_meta["github"]["repo_name"], "repo")

    def test_import_rejects_duplicate_github_link_for_same_foreign_repo(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            self._run_runtime(
                target,
                [
                    "import",
                    "issue",
                    "https://github.com/other/repo/issues/123",
                    "--allow-foreign-url",
                    "--title",
                    "Foreign issue",
                    "--epic",
                    "epic-local-00001",
                ],
                env=test_env,
            )

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
                    "epic-local-00001",
                ],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("already linked", p.stderr)
            self.assertIn("repo=other/repo", p.stderr)
            self.assertIn("github.issue_number=123", p.stderr)

    def test_import_rejects_invalid_slug_and_invalid_title(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            self._make_gh_issue_view_stub(bin_dir, log_path=log_path)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p1 = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Add refresh token", "--epic", "epic-local-00001", "--slug", "Bad!Slug"],
                env=test_env,
            )
            self.assertNotEqual(p1.returncode, 0, p1.stdout + p1.stderr)
            self.assertIn("--slug", p1.stderr)
            self.assertIn("expected regex", p1.stderr)

            p2 = self._run_runtime_capture(
                target,
                ["import", "issue", "124", "--title", "!!!", "--epic", "epic-local-00001"],
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
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            self._make_gh_issue_view_stub(bin_dir, log_path=log_path)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "日本語", "--epic", "epic-local-00001"],
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
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            init_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
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
                ["import", "issue", "123", "--title", "Add refresh token", "--epic", "epic-local-00001"],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("preflight validate failed", p.stderr)
            self.assertIn("slug must be lowercase", p.stderr)
            if log_path.exists():
                self.assertEqual(log_path.read_text(encoding="utf-8").strip(), "")

            imported = list((target / "spec-dock" / "initiatives").rglob("iss-00123-*"))
            self.assertEqual(imported, [])

    def test_import_fails_preflight_when_required_artifact_is_missing_without_creating_node(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Existing issue"])

            missing_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-existing-issue"
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
                ["import", "issue", "123", "--title", "Imported issue", "--epic", "epic-local-00001"],
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
            self._run_runtime(target, ["new", "initiative", "--github-issue", "10", "--title", "GitHub initiative"])
            self._run_runtime(target, ["new", "initiative", "--no-github", "--id", "10", "--title", "Local initiative"])

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

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Parent initiative"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "Parent epic"])

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
                ["import", "issue", "123", "--title", "Imported issue", "--epic", "epic-local-00001"],
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

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            init_path = "spec-dock/initiatives/init-local-00001-auth-platform"
            epic_path = f"{init_path}/epics/epic-local-00001-jwt-auth"

            legacy_dir = target / "spec-dock" / ".work"
            legacy_dir.mkdir(parents=True, exist_ok=True)
            legacy_active_path = legacy_dir / "active.json"
            legacy_active_path.write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "updated_at": "2026-01-01T00:00:00+00:00",
                        "initiative": {"id": "init-local-00001", "path": init_path},
                        "epic": {"id": "epic-local-00001", "path": epic_path},
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
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-00123-add-refresh-token"
            )
            self.assertTrue(issue_dir.is_dir())
            self.assertFalse((target / "spec-dock" / ".agent" / "active.json").exists())
            self.assertTrue(legacy_active_path.is_file())
