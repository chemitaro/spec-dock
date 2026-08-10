from pathlib import Path
import tempfile

import pytest

from tests.cli_runtime.harness import CliRuntimeHarness, main
from tests.cli_runtime.s09_invariance import (
    S09_LEGACY_EVIDENCE_MUTATIONS,
    apply_s09_legacy_evidence_mutation,
    normalize_s09_process_result,
)


class TestDoctorHistoricalConsumerInvariance(CliRuntimeHarness):
    @pytest.mark.parametrize("mutation", S09_LEGACY_EVIDENCE_MUTATIONS)
    def test_validate_and_doctor_legacy_evidence_mutation_invariance(self, mutation: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            observations = []
            for label, mutation_name in (("baseline", None), ("mutated", mutation)):
                target = root / label
                target.mkdir(parents=True)
                assert main(["init", str(target)]) == 0
                self._create_same_repo_linked_hierarchy(
                    target,
                    issue_issue_number=101,
                    issue_title="Historical evidence target",
                )
                self._run_runtime(target, ["active", "set", "--id", "iss-00101"])
                mutated_paths = (
                    apply_s09_legacy_evidence_mutation(target, mutation_name, issue_id="iss-00101")
                    if mutation_name is not None
                    else ()
                )
                before = {path: path.read_bytes() for path in mutated_paths}

                validated = self._run_runtime_capture(target, ["validate"])
                diagnosed = self._run_runtime_capture(target, ["doctor"])

                observations.append((
                    normalize_s09_process_result(validated, repo_root=target),
                    normalize_s09_process_result(diagnosed, repo_root=target),
                ))
                assert {path: path.read_bytes() for path in mutated_paths} == before

        assert observations[1] == observations[0], mutation

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
