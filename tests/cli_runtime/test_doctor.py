from pathlib import Path
import tempfile

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestDoctorHistoricalConsumerInvariance(CliRuntimeHarness):
    def test_validate_and_doctor_invariance_negative_control_keeps_required_path_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                issue_issue_number=101,
                issue_title="Structural negative control",
            )
            issue_dirs = sorted((target / "spec-dock" / "initiatives").glob("**/iss-00101-*"))
            assert len(issue_dirs) == 1
            missing_report = issue_dirs[0] / "report.md"
            missing_report.unlink()

            validated = self._run_runtime_capture(target, ["validate"])
            diagnosed = self._run_runtime_capture(target, ["doctor"])

            assert validated.returncode != 0, validated.stdout + validated.stderr
            assert "Missing required artifact" in validated.stderr
            assert "report.md" in validated.stderr
            assert diagnosed.returncode != 0, diagnosed.stdout + diagnosed.stderr
            assert "[missing_artifact]" in diagnosed.stderr
            assert "report.md" in diagnosed.stderr
