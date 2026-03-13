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


class TestCliWrappers(CliRuntimeHarness):
    def test_wrappers_are_executable(self) -> None:
        if os.name == "nt":
            self.skipTest("Wrapper executable bit checks are for macOS/Linux only.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            issue_dir = epic_dir / "issues" / "iss-local-00001-add-refresh-token"

            wrappers = [
                init_dir / "epics" / "new-epic",
                epic_dir / "issues" / "new-issue",
            ]
            for wrapper in wrappers:
                self.assertTrue(wrapper.is_file(), f"missing wrapper: {wrapper}")
                self.assertTrue(os.access(wrapper, os.X_OK), f"wrapper is not executable: {wrapper}")

    def test_new_epic_wrapper_creates_local_epic(self) -> None:
        if os.name == "nt":
            self.skipTest("This test executes bash wrapper scripts; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            wrapper = init_dir / "epics" / "new-epic"

            bin_dir = target / ".bin-no-gh"
            bin_dir.mkdir(parents=True, exist_ok=True)
            for cmd in ("bash", "python3", "dirname"):
                cmd_path = shutil.which(cmd)
                self.assertIsNotNone(cmd_path, f"{cmd} not available")
                link_path = bin_dir / cmd
                try:
                    os.symlink(cmd_path, link_path)
                except OSError:
                    shutil.copy2(cmd_path, link_path)
                    link_path.chmod(0o755)

            p = self._run_wrapper_capture(wrapper, ["JWT Auth"], env={"PATH": str(bin_dir)})
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertTrue((init_dir / "epics" / "epic-local-00001-jwt-auth" / ".meta.json").is_file())

    def test_new_issue_wrapper_creates_github_issue_by_default(self) -> None:
        if os.name == "nt":
            self.skipTest("This test executes bash wrapper scripts; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
            )
            wrapper = epic_dir / "issues" / "new-issue"

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

            p = self._run_wrapper_capture(
                wrapper,
                ["Add refresh token"],
                env={"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"},
            )
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            issue_meta_path = epic_dir / "issues" / "iss-00123-add-refresh-token" / ".meta.json"
            self.assertTrue(issue_meta_path.is_file())
            issue_meta = json.loads(issue_meta_path.read_text(encoding="utf-8"))
            self.assertEqual(issue_meta["id"], "iss-00123")
            self.assertEqual(issue_meta["github"]["issue_number"], 123)

    def test_new_nodes_do_not_include_new_adr_wrapper(self) -> None:
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
            self.assertFalse((issue_dir / "adrs").exists())
            self.assertFalse((issue_dir / "discussions" / "new-adr").exists())

    def test_wrappers_reject_invalid_args(self) -> None:
        if os.name == "nt":
            self.skipTest("This test executes bash wrapper scripts; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            issue_dir = epic_dir / "issues" / "iss-local-00001-add-refresh-token"
            wrappers = [
                init_dir / "epics" / "new-epic",
                epic_dir / "issues" / "new-issue",
            ]

            for wrapper in wrappers:
                p0 = self._run_wrapper_capture(wrapper, [])
                self.assertNotEqual(p0.returncode, 0)
                self.assertIn("usage:", p0.stderr)

                p2 = self._run_wrapper_capture(wrapper, ["one", "two"])
                self.assertNotEqual(p2.returncode, 0)
                self.assertIn("usage:", p2.stderr)

    def test_wrapper_fails_when_meta_missing_or_invalid(self) -> None:
        if os.name == "nt":
            self.skipTest("This test executes bash wrapper scripts; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            wrapper = init_dir / "epics" / "new-epic"
            meta_path = init_dir / ".meta.json"

            meta_path.unlink()
            p_missing = self._run_wrapper_capture(wrapper, ["JWT Auth"])
            self.assertNotEqual(p_missing.returncode, 0)
            self.assertIn("missing .meta.json", p_missing.stderr)

            self._write_text_force(meta_path, "{ invalid json")
            p_invalid = self._run_wrapper_capture(wrapper, ["JWT Auth"])
            self.assertNotEqual(p_invalid.returncode, 0)
            self.assertIn("invalid .meta.json", p_invalid.stderr)

    def test_wrapper_fails_when_only_legacy_meta_json_exists(self) -> None:
        if os.name == "nt":
            self.skipTest("This test executes bash wrapper scripts; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            wrapper = init_dir / "epics" / "new-epic"
            dot_meta_path = init_dir / ".meta.json"
            legacy_meta_path = init_dir / "meta.json"

            dot_meta_path.rename(legacy_meta_path)
            self.assertTrue(legacy_meta_path.is_file())
            self.assertFalse(dot_meta_path.exists())

            p = self._run_wrapper_capture(wrapper, ["JWT Auth"])
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("missing .meta.json", p.stderr)
            self.assertFalse(dot_meta_path.exists())
            self.assertTrue(legacy_meta_path.is_file())
            self.assertFalse((init_dir / "epics" / "epic-local-00001-jwt-auth" / ".meta.json").is_file())

    def test_wrapper_fails_when_runtime_not_found(self) -> None:
        if os.name == "nt":
            self.skipTest("This test executes bash wrapper scripts; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            wrapper = init_dir / "epics" / "new-epic"
            runtime_script = target / "spec-dock" / "scripts" / "spec-dock"
            runtime_backup = target / "spec-dock" / "scripts" / "spec-dock.bak"
            runtime_script.rename(runtime_backup)

            p = self._run_wrapper_capture(wrapper, ["JWT Auth"])
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("runtime script not found", p.stderr)
            self.assertIn("spec-dock init", p.stderr)

    def test_runtime_entrypoint_fails_fast_when_runtime_module_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            runtime_app = target / "spec-dock" / "scripts" / "spec_dock_runtime" / "app.py"
            runtime_backup = target / "spec-dock" / "scripts" / "spec_dock_runtime" / "app.py.bak"
            runtime_app.rename(runtime_backup)

            p = self._run_runtime_capture(target, ["sync"])
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("runtime module missing", p.stderr)
            self.assertIn("spec-dock update", p.stderr)

    def test_new_epic_wrapper_does_not_require_gh_even_with_github_parent(self) -> None:
        if os.name == "nt":
            self.skipTest("This test executes bash wrapper scripts; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--github-issue", "123", "--title", "Auth platform"])

            init_dir = target / "spec-dock" / "initiatives" / "init-00123-auth-platform"
            wrapper = init_dir / "epics" / "new-epic"

            bin_dir = target / ".bin-no-gh"
            bin_dir.mkdir(parents=True, exist_ok=True)
            for cmd in ("bash", "python3", "dirname"):
                cmd_path = shutil.which(cmd)
                self.assertIsNotNone(cmd_path, f"{cmd} not available")
                link_path = bin_dir / cmd
                try:
                    os.symlink(cmd_path, link_path)
                except OSError:
                    shutil.copy2(cmd_path, link_path)
                    link_path.chmod(0o755)

            p = self._run_wrapper_capture(wrapper, ["JWT Auth"], env={"PATH": str(bin_dir)})
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertTrue((init_dir / "epics" / "epic-local-00001-jwt-auth" / ".meta.json").is_file())

    def test_new_issue_wrapper_fails_without_gh_and_shows_guidance(self) -> None:
        if os.name == "nt":
            self.skipTest("This test executes bash wrapper scripts; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
            )
            wrapper = epic_dir / "issues" / "new-issue"

            bin_dir = target / ".bin-no-gh"
            bin_dir.mkdir(parents=True, exist_ok=True)
            for cmd in ("bash", "python3", "dirname"):
                cmd_path = shutil.which(cmd)
                self.assertIsNotNone(cmd_path, f"{cmd} not available")
                link_path = bin_dir / cmd
                try:
                    os.symlink(cmd_path, link_path)
                except OSError:
                    shutil.copy2(cmd_path, link_path)
                    link_path.chmod(0o755)

            p = self._run_wrapper_capture(wrapper, ["Add refresh token"], env={"PATH": str(bin_dir)})
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("option 1)", p.stderr)
            self.assertIn("option 2)", p.stderr)
            self.assertIn("--no-github", p.stderr)
            self.assertEqual(list((epic_dir / "issues").glob("iss-*")), [])

