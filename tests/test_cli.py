import re
import sys
import shutil
import tempfile
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
            self.assertTrue((target / ".spec-dock" / "current").is_dir())
            self.assertTrue((target / ".spec-dock" / "completed").is_dir())
            self.assertTrue((target / ".spec-dock" / "templates" / "discussions").is_dir())
            self.assertTrue((target / ".spec-dock" / "current" / "discussions").is_dir())
            self.assertTrue(
                (target / ".spec-dock" / "templates" / "discussions" / "_template.md").is_file()
            )
            self.assertTrue(
                (target / ".spec-dock" / "current" / "discussions" / "_template.md").is_file()
            )

            self.assertTrue(
                (target / ".spec-dock" / "docs" / "spec-dock-guide.md").is_file()
            )
            self.assertTrue(
                (target / ".spec-dock" / "scripts" / "spec-dock-close.sh").is_file()
            )
            self.assertTrue(
                (
                    target
                    / ".codex"
                    / "skills"
                    / "spec-driven-tdd-workflow"
                    / "SKILL.md"
                ).is_file()
            )
            self.assertTrue(
                (
                    target
                    / ".github"
                    / "workflows"
                    / "spec-dock-close.yml"
                ).is_file()
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
            self.assertTrue(
                (
                    target
                    / ".github"
                    / "workflows"
                    / "spec-dock-close.yml"
                ).is_file()
            )
            self.assertTrue((target / ".spec-dock" / "templates" / "discussions").is_dir())
            self.assertTrue((target / ".spec-dock" / "current" / "discussions").is_dir())
            self.assertTrue(
                (target / ".spec-dock" / "templates" / "discussions" / "_template.md").is_file()
            )
            self.assertTrue(
                (target / ".spec-dock" / "current" / "discussions" / "_template.md").is_file()
            )

    def test_init_fails_without_force_when_spec_dock_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Second init without --force should fail.
            self.assertNotEqual(main(["init", str(target)]), 0)

    def test_update_keeps_current_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            requirement = target / ".spec-dock" / "current" / "requirement.md"
            requirement.write_text(requirement.read_text(encoding="utf-8") + "\nMOD\n", encoding="utf-8")

            note = target / ".spec-dock" / "current" / "discussions" / "note.md"
            note.write_text("# Note\n", encoding="utf-8")

            self.assertEqual(main(["update", str(target)]), 0)
            self.assertTrue(requirement.read_text(encoding="utf-8").rstrip().endswith("MOD"))
            self.assertTrue(note.is_file())
            self._assert_version_file(target)

    def test_update_reset_current_overwrites_current(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            requirement = target / ".spec-dock" / "current" / "requirement.md"
            requirement.write_text(requirement.read_text(encoding="utf-8") + "\nMOD\n", encoding="utf-8")

            note = target / ".spec-dock" / "current" / "discussions" / "note.md"
            note.write_text("# Note\n", encoding="utf-8")

            self.assertEqual(main(["update", "--reset-current", str(target)]), 0)
            self.assertFalse(requirement.read_text(encoding="utf-8").rstrip().endswith("MOD"))
            self.assertFalse(note.exists())
            self.assertTrue(
                (target / ".spec-dock" / "current" / "discussions" / "_template.md").is_file()
            )
            self._assert_version_file(target)

    def test_update_does_not_create_discussions_without_reset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            shutil.rmtree(target / ".spec-dock" / "current" / "discussions")
            self.assertFalse((target / ".spec-dock" / "current" / "discussions").exists())

            self.assertEqual(main(["update", str(target)]), 0)

            # update should not touch an existing current by default.
            self.assertFalse((target / ".spec-dock" / "current" / "discussions").exists())
            self.assertTrue(
                (target / ".spec-dock" / "templates" / "discussions" / "_template.md").is_file()
            )
            self._assert_version_file(target)
