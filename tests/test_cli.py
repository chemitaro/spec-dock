import re
import os
import sys
import tempfile
import subprocess
import unittest
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

try:
    from spec_dock.cli import main
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from spec_dock.cli import main


def _expected_spec_dock_version() -> str:
    try:
        return version("spec-dock")
    except PackageNotFoundError:
        text = (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(
            encoding="utf-8"
        )
        match = re.search(r'(?m)^version\s*=\s*"([^"]+)"\s*$', text)
        if not match:
            raise AssertionError("failed to read version from pyproject.toml")
        return match.group(1)


class TestCli(unittest.TestCase):
    def _run_runtime(self, target: Path, args: list[str], *, env: dict[str, str] | None = None) -> None:
        script = target / ".spec-dock" / "scripts" / "spec-dock"
        self.assertTrue(script.is_file(), f"runtime script missing: {script}")

        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)

        p = subprocess.run(
            [sys.executable, str(script), *args],
            cwd=str(target),
            env=merged_env,
            capture_output=True,
            text=True,
        )
        if p.returncode != 0:
            raise AssertionError(
                "runtime command failed:\n"
                f"- cmd: {args}\n"
                f"- stdout:\n{p.stdout}\n"
                f"- stderr:\n{p.stderr}\n"
            )

    def _assert_version_file(self, target: Path) -> None:
        version_file = target / ".spec-dock" / "spec-dock.version"
        self.assertTrue(version_file.is_file())
        self.assertEqual(version_file.read_text(encoding="utf-8").strip(), _expected_spec_dock_version())

    def test_init_creates_expected_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)

            exit_code = main(["init", str(target)])
            self.assertEqual(exit_code, 0)

            self._assert_version_file(target)

            self.assertTrue((target / ".spec-dock" / "docs").is_dir())
            self.assertTrue((target / ".spec-dock" / "templates").is_dir())
            self.assertTrue((target / ".spec-dock" / "scripts").is_dir())
            self.assertTrue((target / ".spec-dock" / "initiatives").is_dir())
            self.assertTrue((target / ".spec-dock" / "active").is_dir())
            self.assertTrue((target / ".spec-dock" / ".work").is_dir())
            self.assertTrue((target / ".spec-dock" / ".gitignore").is_file())
            gitignore = (target / ".spec-dock" / ".gitignore").read_text(encoding="utf-8")
            self.assertIn(".work/", gitignore)
            self.assertIn("active/", gitignore)

            self.assertTrue(
                (target / ".spec-dock" / "docs" / "spec-dock-guide.md").is_file()
            )
            self.assertTrue((target / ".spec-dock" / "docs" / "README.md").is_file())
            self.assertTrue((target / ".spec-dock" / "docs" / "github.md").is_file())
            self.assertTrue((target / ".spec-dock" / "docs" / "sync.md").is_file())

            # Runtime script exists; legacy close scripts must not be present.
            scripts_dir = target / ".spec-dock" / "scripts"
            self.assertTrue((scripts_dir / "spec-dock").is_file())
            self.assertEqual(list(scripts_dir.glob("spec-dock-close*.sh")), [])

            # Legacy (v1) templates should not be installed.
            templates_dir = target / ".spec-dock" / "templates"
            for legacy in ("requirement.md", "design.md", "plan.md", "report.md"):
                self.assertFalse((templates_dir / legacy).exists(), f"legacy template leaked: {legacy}")
            self.assertEqual(list(templates_dir.rglob("current")), [])
            self.assertEqual(list(templates_dir.rglob("completed")), [])

            self.assertTrue(
                (
                    target
                    / ".codex"
                    / "skills"
                    / "spec-driven-tdd-workflow"
                    / "SKILL.md"
                ).is_file()
            )
            self.assertFalse(
                (target / ".github" / "workflows" / "spec-dock-close.yml").exists()
            )

    def test_init_no_skill_skips_skill_install(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)

            exit_code = main(["init", "--no-skill", str(target)])
            self.assertEqual(exit_code, 0)

            self._assert_version_file(target)

            self.assertFalse(
                (
                    target
                    / ".codex"
                    / "skills"
                    / "spec-driven-tdd-workflow"
                    / "SKILL.md"
                ).exists()
            )
            self.assertFalse((target / ".github" / "workflows" / "spec-dock-close.yml").exists())

    def test_init_fails_without_force_when_spec_dock_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Second init without --force should fail.
            self.assertNotEqual(main(["init", str(target)]), 0)

    def test_update_keeps_initiatives_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            marker = target / ".spec-dock" / "initiatives" / "marker.txt"
            marker.write_text("keep\n", encoding="utf-8")

            # Simulate legacy (v1) leftovers that v2 should prune on update.
            legacy_workflow = target / ".github" / "workflows" / "spec-dock-close.yml"
            legacy_workflow.parent.mkdir(parents=True, exist_ok=True)
            legacy_workflow.write_text("legacy\n", encoding="utf-8")

            legacy_symlink = target / ".spec-dock" / "current-initiative"
            created_symlink = False
            try:
                # v1 style link target (so v2 can safely prune without deleting v2-generated shortcuts).
                os.symlink("initiative/current", legacy_symlink)
                created_symlink = True
            except OSError:
                # Some environments may restrict symlinks; workflow pruning is still validated.
                created_symlink = False

            self.assertEqual(main(["update", str(target)]), 0)
            self.assertTrue(marker.is_file())
            self._assert_version_file(target)
            self.assertFalse(legacy_workflow.exists())
            if created_symlink:
                self.assertFalse(legacy_symlink.is_symlink())

    def test_new_and_active_and_sync(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Create nodes without touching GitHub.
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            # Parent ids accept shorthand numeric forms (e.g. `1` -> `init-local-0001` / `epic-local-0001`).
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_dir = (
                target
                / ".spec-dock"
                / "initiatives"
                / "init-local-0001-auth-platform"
                / "epics"
                / "epic-local-0001-jwt-auth"
                / "issues"
                / "iss-local-0001-add-refresh-token"
            )
            self.assertTrue((issue_dir / "requirement.md").is_file())
            self.assertTrue((issue_dir / "design.md").is_file())
            self.assertTrue((issue_dir / "plan.md").is_file())
            self.assertTrue((issue_dir / "report.md").is_file())

            # Active issue id also accepts shorthand numeric form.
            self._run_runtime(target, ["active", "set", "--issue", "1"])
            self.assertTrue((target / ".spec-dock" / ".work" / "current.json").is_file())
            self.assertTrue(
                (target / ".spec-dock" / "active" / "issue").exists()
                or (target / ".spec-dock" / "active" / "issue.path").is_file()
            )
            self.assertTrue((target / ".spec-dock" / "active" / "context-pack.md").is_file())

            self._run_runtime(target, ["sync"])
            self.assertTrue((target / ".spec-dock" / ".work" / "state.json").is_file())
            self.assertTrue((target / ".spec-dock" / ".work" / "tree.json").is_file())

            # Index: flat nodes (agent-friendly).
            state = (target / ".spec-dock" / ".work" / "state.json").read_text(encoding="utf-8")
            self.assertIn("\"nodes\"", state)
            self.assertNotIn("\"tree\"", state)

            # Tree: nested layer view (human-friendly).
            tree = (target / ".spec-dock" / ".work" / "tree.json").read_text(encoding="utf-8")
            self.assertIn("\"tree\"", tree)
            self.assertIn("\"id\": \"init-local-0001\"", tree)
            self.assertIn("\"id\": \"epic-local-0001\"", tree)
            self.assertIn("\"id\": \"iss-local-0001\"", tree)
            self._run_runtime(target, ["validate"])

    def test_new_no_github_does_not_invoke_gh(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Provide a fake `gh` binary that always errors; --no-github must not call it.
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
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"], env=test_env)
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"], env=test_env)
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"], env=test_env)

    def test_new_nodes_default_to_github_issue_creation(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Provide a fake `gh` binary that returns unique issue URLs per `issue create`.
            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            counter = bin_dir / "counter.txt"
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                f"counter_file='{counter.as_posix()}'\n"
                'if [[ \"$1\" == \"issue\" && \"$2\" == \"create\" ]]; then\n'
                "  n=0\n"
                "  if [[ -f \"$counter_file\" ]]; then\n"
                "    n=$(cat \"$counter_file\")\n"
                "  fi\n"
                "  n=$((n+1))\n"
                "  echo \"$n\" > \"$counter_file\"\n"
                "  issue_num=$((122 + n))\n"
                "  echo \"https://github.com/example/repo/issues/${issue_num}\"\n"
                "  exit 0\n"
                "fi\n"
                "echo \"unexpected gh args: $@\" >&2\n"
                "exit 1\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            # Default: GitHub issue is created and its number becomes the node id suffix.
            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform"], env=test_env)
            self._run_runtime(target, ["new", "epic", "--initiative", "123", "--title", "JWT auth"], env=test_env)
            self._run_runtime(target, ["new", "issue", "--epic", "124", "--title", "Add refresh token"], env=test_env)

            init_dir = target / ".spec-dock" / "initiatives" / "init-0123-auth-platform"
            epic_dir = init_dir / "epics" / "epic-0124-jwt-auth"
            issue_dir = epic_dir / "issues" / "iss-0125-add-refresh-token"
            self.assertTrue(init_dir.is_dir())
            self.assertTrue(epic_dir.is_dir())
            self.assertTrue(issue_dir.is_dir())

            init_meta = (init_dir / "meta.json").read_text(encoding="utf-8")
            epic_meta = (epic_dir / "meta.json").read_text(encoding="utf-8")
            issue_meta = (issue_dir / "meta.json").read_text(encoding="utf-8")
            self.assertIn('\"id\": \"init-0123\"', init_meta)
            self.assertIn('\"issue_number\": 123', init_meta)
            self.assertIn('\"id\": \"epic-0124\"', epic_meta)
            self.assertIn('\"issue_number\": 124', epic_meta)
            self.assertIn('\"id\": \"iss-0125\"', issue_meta)
            self.assertIn('\"issue_number\": 125', issue_meta)

    def test_new_issue_can_create_github_issue_and_use_its_number(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Create parent nodes locally, but create the issue on GitHub (default).
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

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
                ["new", "issue", "--epic", "1", "--title", "Add refresh token"],
                env=test_env,
            )

            issue_dir = (
                target
                / ".spec-dock"
                / "initiatives"
                / "init-local-0001-auth-platform"
                / "epics"
                / "epic-local-0001-jwt-auth"
                / "issues"
                / "iss-0123-add-refresh-token"
            )
            self.assertTrue(issue_dir.is_dir())
            meta = (issue_dir / "meta.json").read_text(encoding="utf-8")
            self.assertIn('\"id\": \"iss-0123\"', meta)
            self.assertIn('\"issue_number\": 123', meta)
