import json
import os
from pathlib import Path
import shutil
import tempfile

import pytest

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestCliSmoke(CliRuntimeHarness):
    def setup_method(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("bash") is None:
            pytest.skip("bash not available")

    def test_active_set_legacy_flag_reports_parser_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            result = self._run_runtime_capture(target, ["active", "set", "--issue", "1"])

        assert result.returncode == 2
        assert result.stdout == ""
        assert "unrecognized arguments: --issue" in result.stderr
        assert "Hint:" in result.stderr

    def test_active_set_by_id_succeeds_through_runtime_subprocess(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            result = self._run_runtime_capture(target, ["active", "set", "--id", "iss-00003", "--force"])

            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))

        assert result.returncode == 0, result.stdout + result.stderr
        assert "spec-dock: ok (active set)" in result.stdout
        assert result.stderr == ""
        assert active["issue"]["id"] == "iss-00003"
