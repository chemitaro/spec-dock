import json
from pathlib import Path
import tempfile

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestCliWorkflow(CliRuntimeHarness):
    def test_workflow_next_no_active_returns_issue_start_guidance_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            result = self._run_runtime_capture(
                target,
                ["workflow", "next", "issue-execution", "--format", "json"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            payload = json.loads(result.stdout)
            assert payload["state"] == "no-active"
            assert payload["next_action"] == "issue-start-required"
            assert payload["commands"] == ["./spec-dock/scripts/spec-dock issue start <issue-id>"]
            joined = json.dumps(payload, ensure_ascii=False)
            assert "requirement" not in joined
            assert "implementation" not in joined

    def test_workflow_status_and_next_detect_scaffold_requirement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_workflow_fixture(target, issue_number=301, title="Capture requirement")

            status = self._run_runtime_capture(target, ["workflow", "status", "--format", "json"])
            next_result = self._run_runtime_capture(
                target,
                ["workflow", "next", "issue-planning", "--format", "json"],
            )

            assert status.returncode == 0, status.stdout + status.stderr
            assert next_result.returncode == 0, next_result.stdout + next_result.stderr
            status_payload = json.loads(status.stdout)
            next_payload = json.loads(next_result.stdout)
            assert status_payload["state"] == "requirement-capture"
            assert next_payload["state"] == "requirement-capture"
            assert next_payload["next_action"] == "requirement-capture-required"

    def test_workflow_next_missing_assurance_requires_classification_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Implement feature")
            self._write_substantive_requirement(issue_dir)

            result = self._run_runtime_capture(
                target,
                ["workflow", "next", "issue-execution", "--format", "markdown"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            assert "state: classification-required" in result.stdout
            assert "./spec-dock/scripts/spec-dock assurance classify --stage requirement" in result.stdout
            assert "./spec-dock/scripts/spec-dock assurance verify" in result.stdout
            assert "Do not start implementation" in result.stdout

    def test_workflow_next_malformed_assurance_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Invalid assurance")
            self._write_substantive_requirement(issue_dir)
            (issue_dir / "assurance.json").write_text("{not-json\n", encoding="utf-8")

            result = self._run_runtime_capture(
                target,
                ["workflow", "next", "issue-execution", "--format", "json"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            payload = json.loads(result.stdout)
            assert payload["state"] == "classification-required"
            assert payload["reason_code"] == "authority-invalid"
            assert payload["authority"]["obligation_source"] == "authorized_profile"
            assert payload["authority"]["authorized_profile"] == "strict"
            assert payload["details"]

            markdown = self._run_runtime_capture(
                target,
                ["workflow", "next", "issue-execution", "--format", "markdown"],
            )

            assert markdown.returncode == 0, markdown.stdout + markdown.stderr
            assert "## Details" in markdown.stdout
            assert "line=1" in markdown.stdout

    def test_workflow_next_unknown_target_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            result = self._run_runtime_capture(
                target,
                ["workflow", "next", "unknown-target", "--format", "json"],
            )

            assert result.returncode != 0
            assert "invalid choice" in result.stderr
            assert "current-runbook" not in result.stdout

    def test_workflow_status_ready_uses_valid_assurance_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Ready issue")
            self._write_substantive_requirement(issue_dir)
            classify = self._run_runtime_capture(
                target,
                ["assurance", "classify", "--stage", "requirement", "--format", "json"],
            )
            assert classify.returncode == 0, classify.stdout + classify.stderr

            result = self._run_runtime_capture(target, ["workflow", "status", "--format", "json"])

            assert result.returncode == 0, result.stdout + result.stderr
            payload = json.loads(result.stdout)
            assert payload["state"] == "ready"
            assert payload["reason_code"] == "assurance-valid"
            assert payload["authority"]["authorized_profile"] == "standard"
            assert payload["authority"]["obligation_source"] == "authorized_profile"

    def _create_workflow_fixture(self, target: Path, *, issue_number: int, title: str) -> Path:
        self._create_same_repo_linked_hierarchy(
            target,
            initiative_issue_number=101,
            epic_issue_number=201,
            issue_issue_number=issue_number,
            issue_title=title,
        )
        issue_id = f"iss-{issue_number:05d}"
        self._run_runtime(target, ["active", "set", "--id", issue_id])
        return self._find_issue_dir_by_id(target, issue_id)

    def _find_issue_dir_by_id(self, target: Path, issue_id: str) -> Path:
        for meta_path in sorted((target / "spec-dock" / "initiatives").glob("**/.meta.json")):
            payload = json.loads(meta_path.read_text(encoding="utf-8"))
            if payload.get("type") == "issue" and payload.get("id") == issue_id:
                return meta_path.parent
        raise AssertionError(f"issue not found: {issue_id}")

    def _write_substantive_requirement(self, issue_dir: Path) -> None:
        (issue_dir / "requirement.md").write_text(
            "---\n"
            "種別: 要件定義書（Issue）\n"
            "ID: \"iss-00301\"\n"
            "状態: \"approved\"\n"
            "---\n\n"
            "# Requirement\n\n"
            "## 目的\n"
            "- Implement a concrete runtime behavior with observable CLI output.\n\n"
            "## 受け入れ条件\n"
            "- The command returns deterministic state and guidance.\n",
            encoding="utf-8",
        )
