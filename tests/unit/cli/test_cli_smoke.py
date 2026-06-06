import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestCliSmoke(CliRuntimeHarness):
    def setUp(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("bash") is None:
            self.skipTest("bash not available")

    def test_active_set_legacy_flag_reports_parser_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            result = self._run_runtime_capture(target, ["active", "set", "--issue", "1"])

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("unrecognized arguments: --issue", result.stderr)
        self.assertIn("Hint:", result.stderr)

    def test_active_set_by_id_succeeds_through_runtime_subprocess(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_same_repo_linked_hierarchy(target)

            result = self._run_runtime_capture(target, ["active", "set", "--id", "iss-00003", "--force"])

            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("spec-dock: ok (active set)", result.stdout)
        self.assertEqual(result.stderr, "")
        self.assertEqual(active["issue"]["id"], "iss-00003")


if __name__ == "__main__":
    unittest.main()
