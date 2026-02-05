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
    def _run_runtime(self, target: Path, args: list[str]) -> None:
        script = target / ".spec-dock" / "scripts" / "spec-dock"
        self.assertTrue(script.is_file(), f"runtime script missing: {script}")

        p = subprocess.run(
            [sys.executable, str(script), *args],
            cwd=str(target),
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
                os.symlink("initiatives", legacy_symlink)
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

            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--initiative", "init-0001", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "epic-0001", "--title", "Add refresh token"])

            issue_dir = (
                target
                / ".spec-dock"
                / "initiatives"
                / "init-0001-auth-platform"
                / "epics"
                / "epic-0001-jwt-auth"
                / "issues"
                / "iss-0001-add-refresh-token"
            )
            self.assertTrue((issue_dir / "requirement.md").is_file())
            self.assertTrue((issue_dir / "design.md").is_file())
            self.assertTrue((issue_dir / "plan.md").is_file())
            self.assertTrue((issue_dir / "report.md").is_file())

            self._run_runtime(target, ["active", "set", "--issue", "iss-0001"])
            self.assertTrue((target / ".spec-dock" / ".work" / "current.json").is_file())
            self.assertTrue(
                (target / ".spec-dock" / "active" / "issue").exists()
                or (target / ".spec-dock" / "active" / "issue.path").is_file()
            )
            self.assertTrue((target / ".spec-dock" / "active" / "context-pack.md").is_file())

            self._run_runtime(target, ["sync"])
            self.assertTrue((target / ".spec-dock" / ".work" / "state.json").is_file())
            self._run_runtime(target, ["validate"])
