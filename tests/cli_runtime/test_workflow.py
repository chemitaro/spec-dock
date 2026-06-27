import json
from pathlib import Path
import subprocess
import tempfile

import pytest

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestCliWorkflow(CliRuntimeHarness):
    def test_guidance_no_active_returns_issue_start_guidance_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            result = self._run_runtime_capture(
                target,
                ["guidance", "issue-execution"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            assert result.stdout.startswith("# Guidance: issue-execution")
            payload = self._read_projected_runbook(target)
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
                ["guidance", "issue-planning"],
            )

            assert status.returncode == 0, status.stdout + status.stderr
            assert next_result.returncode == 0, next_result.stdout + next_result.stderr
            status_payload = json.loads(status.stdout)
            next_payload = self._read_projected_runbook(target)
            assert status_payload["state"] == "requirement-capture"
            assert "- state: requirement-capture" in next_result.stdout
            assert "- next_action: requirement-capture-required" in next_result.stdout
            assert "- reason_code: requirement-scaffold" in next_result.stdout
            assert "- `./spec-dock/scripts/spec-dock active show`" in next_result.stdout
            assert "- Do not classify assurance or start execution from a scaffold requirement." in next_result.stdout
            assert next_payload["state"] == "requirement-capture"
            assert next_payload["next_action"] == "requirement-capture-required"

    def test_guidance_missing_assurance_uses_strict_legacy_execution_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Implement feature")
            self._write_substantive_requirement(issue_dir)
            self._write_executable_plan(issue_dir)

            result = self._run_runtime_capture(
                target,
                ["guidance", "issue-execution"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            assert "state: ready" in result.stdout
            assert "reason_code: strict-legacy-missing-assurance" in result.stdout
            assert "authorized_profile=strict" in result.stdout
            assert "execute-approved-plan" in result.stdout
            assert "may_execute_approved_plan: true" in result.stdout

    def test_guidance_malformed_assurance_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Invalid assurance")
            self._write_substantive_requirement(issue_dir)
            (issue_dir / "assurance.json").write_text("{not-json\n", encoding="utf-8")

            result = self._run_runtime_capture(
                target,
                ["guidance", "issue-execution"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            payload = self._read_projected_runbook(target)
            assert payload["state"] == "classification-required"
            assert payload["reason_code"] == "authority-invalid"
            assert payload["may_execute_approved_plan"] is False
            assert payload["authority"]["obligation_source"] == "unavailable"
            assert payload["authority"]["authorized_profile"] == "unavailable"
            assert payload["details"]

            markdown = self._run_runtime_capture(
                target,
                ["guidance", "issue-execution"],
            )

            assert markdown.returncode == 0, markdown.stdout + markdown.stderr
            assert "## Details" in markdown.stdout
            assert "line=1" in markdown.stdout

    def test_guidance_unknown_target_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            result = self._run_runtime_capture(
                target,
                ["guidance", "unknown-target"],
            )

            assert result.returncode != 0
            assert "invalid choice" in result.stderr
            assert "current-runbook" not in result.stdout
            for rel_path in (
                "spec-dock/.agent/runbooks/current-runbook.json",
                "spec-dock/.agent/runbooks/current-runbook.md",
                "spec-dock/active/current-runbook.json",
                "spec-dock/active/current-runbook.md",
            ):
                assert not (target / rel_path).exists()

    def test_workflow_status_ready_uses_valid_assurance_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Ready issue")
            self._write_substantive_requirement(issue_dir)
            self._write_executable_plan(issue_dir)
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

    @pytest.mark.parametrize("filename", ["requirement.md", "design.md", "plan.md"])
    def test_guidance_blocks_stale_source_binding(self, filename: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Stale issue")
            self._write_substantive_requirement(issue_dir)
            self._write_executable_plan(issue_dir)
            classify = self._run_runtime_capture(
                target,
                ["assurance", "classify", "--stage", "requirement", "--format", "json"],
            )
            assert classify.returncode == 0, classify.stdout + classify.stderr
            if filename == "requirement.md":
                (issue_dir / filename).write_text(
                    "---\n"
                    "種別: 要件定義書（Issue）\n"
                    'ID: "iss-00301"\n'
                    '状態: "approved"\n'
                    "---\n\n"
                    "# Requirement\n\n"
                    "This requirement was changed after assurance classification.\n\n"
                    "## Acceptance Criteria\n\n"
                    "- Updated acceptance criteria remains substantive.\n",
                    encoding="utf-8",
                )
            else:
                (issue_dir / filename).write_text(
                    f"# Changed {filename}\n\nThis planning artifact changed after assurance classification.\n",
                    encoding="utf-8",
                )

            result = self._run_runtime_capture(
                target,
                ["guidance", "issue-execution"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            payload = self._read_projected_runbook(target)
            assert payload["state"] == "classification-required"
            assert payload["reason_code"] == "authority-invalid"
            assert payload["next_action"] == "assurance-classification-required"
            assert payload["may_execute_approved_plan"] is False
            assert filename.removesuffix(".md") in " ".join(payload["details"])

    def test_guidance_writes_ignored_runbook_projection_without_tracked_diff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_workflow_fixture(target, issue_number=301, title="Projected runbook")
            self._commit_baseline(target)

            result = self._run_runtime_capture(
                target,
                ["guidance", "issue-planning"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            assert result.stdout.startswith("# Guidance: issue-planning")
            payload = self._read_projected_runbook(target)
            assert payload["projection"]["written"] is True
            assert payload["projection"]["paths"] == [
                "spec-dock/.agent/runbooks/current-runbook.json",
                "spec-dock/.agent/runbooks/current-runbook.md",
                "spec-dock/active/current-runbook.json",
                "spec-dock/active/current-runbook.md",
            ]
            assert payload["projection"]["audience"] == "human"
            assert payload["projection"]["authority"] == "non-canonical"
            assert payload["projection"]["refresh_command"] == "./spec-dock/scripts/spec-dock guidance issue-planning"
            for rel_path in payload["projection"]["paths"]:
                assert (target / rel_path).is_file()
            projected = json.loads(
                (target / "spec-dock/.agent/runbooks/current-runbook.json").read_text(encoding="utf-8")
            )
            assert projected["state"] == "requirement-capture"
            assert projected["projection"]["written"] is True
            assert projected["projection"]["audience"] == "human"
            projected_markdown = (target / "spec-dock/active/current-runbook.md").read_text(encoding="utf-8")
            assert "Human-facing projection" in projected_markdown
            assert "not agent handoff authority" in projected_markdown
            status = subprocess.run(
                ["git", "status", "--short"],
                cwd=target,
                capture_output=True,
                text=True,
                check=True,
            )
            assert status.stdout == ""

    def test_guidance_ignores_stale_runbook_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Current issue")
            self._write_substantive_requirement(issue_dir)
            stale_payload = {
                "schema_version": "workflow-runbook-v1",
                "workflow_target": "issue-planning",
                "state": "ready",
                "next_action": "stale-next-action",
                "reason_code": "stale-projection",
                "active_issue_id": "iss-99999",
            }
            runbook_dir = target / "spec-dock/.agent/runbooks"
            active_dir = target / "spec-dock/active"
            runbook_dir.mkdir(parents=True, exist_ok=True)
            active_dir.mkdir(parents=True, exist_ok=True)
            (runbook_dir / "current-runbook.json").write_text(json.dumps(stale_payload) + "\n", encoding="utf-8")
            (active_dir / "current-runbook.json").write_text(json.dumps(stale_payload) + "\n", encoding="utf-8")

            result = self._run_runtime_capture(
                target,
                ["guidance", "issue-planning"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            assert "active_issue: iss-00301" in result.stdout
            assert "stale-next-action" not in result.stdout
            assert "iss-99999" not in result.stdout
            payload = self._read_projected_runbook(target)
            assert payload["active_issue_id"] == "iss-00301"
            assert payload["state"] == "ready"
            assert payload["next_action"] == "planning-ready"
            assert payload["may_execute_approved_plan"] is False

    def _read_projected_runbook(self, target: Path) -> dict:
        return json.loads((target / "spec-dock/.agent/runbooks/current-runbook.json").read_text(encoding="utf-8"))

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
            'ID: "iss-00301"\n'
            '状態: "approved"\n'
            "---\n\n"
            "# Requirement\n\n"
            "## 目的\n"
            "- Implement a concrete runtime behavior with observable CLI output.\n\n"
            "## 受け入れ条件\n"
            "- The command returns deterministic state and guidance.\n",
            encoding="utf-8",
        )

    def _write_executable_plan(self, issue_dir: Path) -> None:
        (issue_dir / "plan.md").write_text(
            "# Plan\n\n"
            "### 実装ステップ S01 — Implement deterministic workflow guidance\n"
            "- 対象ファイル: scripts/spec_dock_runtime/application/workflow.py\n",
            encoding="utf-8",
        )

    def _commit_baseline(self, target: Path) -> None:
        subprocess.run(["git", "add", "."], cwd=target, check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=target,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "SpecDock Test"],
            cwd=target,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(["git", "commit", "-m", "baseline"], cwd=target, check=True, capture_output=True, text=True)
