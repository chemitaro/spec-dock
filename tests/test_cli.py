import tempfile
import unittest
from pathlib import Path

from spec_dock.cli import main


class TestCli(unittest.TestCase):
    def test_init_creates_expected_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)

            exit_code = main(["init", str(target)])
            self.assertEqual(exit_code, 0)

            self.assertTrue((target / ".spec-dock" / "docs").is_dir())
            self.assertTrue((target / ".spec-dock" / "templates").is_dir())
            self.assertTrue((target / ".spec-dock" / "scripts").is_dir())
            self.assertTrue((target / ".spec-dock" / "current").is_dir())
            self.assertTrue((target / ".spec-dock" / "completed").is_dir())

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

    def test_update_keeps_current_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            requirement = target / ".spec-dock" / "current" / "requirement.md"
            requirement.write_text(requirement.read_text(encoding="utf-8") + "\nMOD\n", encoding="utf-8")

            self.assertEqual(main(["update", str(target)]), 0)
            self.assertTrue(requirement.read_text(encoding="utf-8").rstrip().endswith("MOD"))

    def test_update_reset_current_overwrites_current(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            requirement = target / ".spec-dock" / "current" / "requirement.md"
            requirement.write_text(requirement.read_text(encoding="utf-8") + "\nMOD\n", encoding="utf-8")

            self.assertEqual(main(["update", "--reset-current", str(target)]), 0)
            self.assertFalse(requirement.read_text(encoding="utf-8").rstrip().endswith("MOD"))

