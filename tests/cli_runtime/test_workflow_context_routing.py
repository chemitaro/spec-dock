from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestWorkflowContextRoutingHardCutover(CliRuntimeHarness):
    def test_issue_execution_guidance_is_plan_centric_without_dynamic_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Plan centric")
            self._write_substantive_requirement(issue_dir)
            self._write_executable_plan(issue_dir)
            self._classify(target)

            result = self._run_runtime_capture(target, ["guidance", "issue-execution"])

            assert result.returncode == 0, result.stdout + result.stderr
            assert "## Step Assurance" not in result.stdout
            assert "## Context Packets" not in result.stdout
            assert "- may_execute_approved_plan: true" in result.stdout
            assert "- contract_source: spec-dock/active/issue/plan.md" in result.stdout
            assert "- evidence_ledger: spec-dock/active/issue/report.md" in result.stdout
            payload = self._read_projected_runbook(target)
            assert payload["state"] == "ready"
            assert payload["next_action"] == "execute-approved-plan"
            assert payload["may_execute_approved_plan"] is True
            assert payload["contract_source"] == "spec-dock/active/issue/plan.md"
            assert payload["evidence_ledger"] == "spec-dock/active/issue/report.md"
            assert "step_assurance" not in payload
            assert "context_packets" not in payload
            projected_markdown = (target / "spec-dock/active/current-runbook.md").read_text(encoding="utf-8")
            assert "## Step Assurance" not in projected_markdown
            assert "## Context Packets" not in projected_markdown
            assert "selected_step" not in projected_markdown

    def test_issue_execution_does_not_require_old_structured_step_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="No old heading")
            self._write_substantive_requirement(issue_dir)
            self._write_substantive_design(issue_dir)
            (issue_dir / "plan.md").write_text(
                "# Plan\n\n"
                "## Step Closure Contract\n"
                "- Execute the approved implementation plan in order.\n"
                "- Verification obligations are recorded here.\n",
                encoding="utf-8",
            )
            self._write_report_evidence(issue_dir)
            self._classify(target)

            result = self._run_runtime_capture(target, ["guidance", "issue-execution"])

            assert result.returncode == 0, result.stdout + result.stderr
            payload = self._read_projected_runbook(target)
            assert payload["state"] == "ready"
            assert payload["next_action"] == "execute-approved-plan"
            assert payload["may_execute_approved_plan"] is True
            assert payload["reason_code"] != "workflow-plan-unselectable"
            assert "selected_step" not in json.dumps(payload)

    def test_placeholder_plan_blocks_without_dynamic_step_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Placeholder plan")
            self._write_substantive_requirement(issue_dir)
            self._write_substantive_design(issue_dir)
            (issue_dir / "plan.md").write_text("# Plan\n\nNo structured implementation steps.\n", encoding="utf-8")
            self._write_report_evidence(issue_dir)
            self._classify(target)

            result = self._run_runtime_capture(target, ["guidance", "issue-execution"])

            assert result.returncode == 0, result.stdout + result.stderr
            payload = self._read_projected_runbook(target)
            assert payload["state"] == "blocked"
            assert payload["next_action"] == "issue-planning-required"
            assert payload["reason_code"] == "plan-not-executable"
            assert payload["may_execute_approved_plan"] is False
            assert payload["authority"]["authorized_profile"] == "standard"
            assert "step_assurance" not in payload
            assert "context_packets" not in payload

    def test_invalid_assurance_fails_closed_without_strict_current_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Invalid assurance")
            self._write_substantive_requirement(issue_dir)
            self._write_executable_plan(issue_dir)
            (issue_dir / ".assurance.json").write_text("{not-json\n", encoding="utf-8")

            result = self._run_runtime_capture(target, ["guidance", "issue-execution"])

            assert result.returncode == 0, result.stdout + result.stderr
            payload = self._read_projected_runbook(target)
            assert payload["state"] == "classification-required"
            assert payload["reason_code"] == "authority-invalid"
            assert payload["may_execute_approved_plan"] is False
            assert payload["authority"]["authorized_profile"] == "unavailable"
            assert payload["authority"]["obligation_source"] == "unavailable"

    def test_context_packet_projection_storage_no_longer_blocks_issue_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Context packets ignored")
            self._write_substantive_requirement(issue_dir)
            self._write_executable_plan(issue_dir)
            self._classify(target)
            packet_dir = target / "spec-dock/.agent/context-packets"
            outside = target / "outside-context-packets"
            outside.mkdir()
            packet_dir.parent.mkdir(parents=True, exist_ok=True)
            packet_dir.symlink_to(outside, target_is_directory=True)

            result = self._run_runtime_capture(target, ["guidance", "issue-execution"])

            assert result.returncode == 0, result.stdout + result.stderr
            payload = self._read_projected_runbook(target)
            assert payload["state"] == "ready"
            assert payload["next_action"] == "execute-approved-plan"
            assert payload["may_execute_approved_plan"] is True
            assert "context_packets" not in payload

    def _classify(self, target: Path) -> None:
        classify = self._run_runtime_capture(
            target,
            ["assurance", "classify", "--stage", "requirement", "--format", "json"],
        )
        assert classify.returncode == 0, classify.stdout + classify.stderr

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
            "- Implement runtime behavior with observable CLI output.\n\n"
            "## 受け入れ条件\n"
            "- The command returns deterministic plan-centric guidance.\n",
            encoding="utf-8",
        )

    def _write_substantive_design(self, issue_dir: Path) -> None:
        (issue_dir / "design.md").write_text(
            "---\n"
            "種別: 設計書（Issue）\n"
            'ID: "iss-00301"\n'
            '状態: "approved"\n'
            "---\n\n"
            "# Design\n\n"
            "## 全体像\n"
            "- Guidance execution checks planning artifacts before execution.\n\n"
            "## 責務\n"
            "- The runtime validates readiness and the plan remains the execution contract.\n",
            encoding="utf-8",
        )

    def _write_executable_plan(self, issue_dir: Path) -> None:
        self._write_substantive_design(issue_dir)
        (issue_dir / "plan.md").write_text(
            "# Plan\n\n"
            "## 実装ステップ\n\n"
            "### 実装ステップ S01 — Implement plan-centric guidance\n"
            "- Planned contract: guidance points to plan.md and report.md.\n"
            "- Green verification: unit tests.\n"
            "- Reviewer gate: code-reviewer.\n",
            encoding="utf-8",
        )
        self._write_report_evidence(issue_dir)

    def _write_report_evidence(self, issue_dir: Path) -> None:
        (issue_dir / "report.md").write_text(
            "# Report\n\n"
            "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
            "| ID | adoption_status | source | target | rationale | evidence | next_action |\n"
            "|---|---|---|---|---|---|---|\n"
            "| EAL-001 | adopted | fixture | design.md | ready evidence | discussions/draft.md | pass |\n\n"
            "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
            "| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |\n"
            "|---|---|---|---|---|---|---|\n"
            "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
            "| design | docs | none | adopted | pass | no | execute approved plan |\n"
            "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
            "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
            "| role | scope | draft path | source paths | intended targets | adoption_status | reflected_to | diff_guard_result | integration result | rejected portions | blockers | reviewer result | promotion decision |\n"
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
            "| system-architect | iss-00301 | discussions/draft.md | active docs | design.md | partially_adopted | design.md | orchestrator inspection pass | source input integrated; not promotion evidence | none | prior reviewer evidence missing; resolved by manual authoring fallback D-003 | pass | execute manual-authored canonical docs |\n\n"
            "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
            "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
            "|---|---|---|---|---|---|\n"
            "| standard | system-architect / implementation-planner | skipped | skip reason: fixture uses manual plan evidence | pass | ready |\n"
            "| strict | manual fallback | unavailable | manual authoring fallback with source inspection and residual risk | pass | ready |\n\n"
            "#### レビューゲート状態（Reviewer Gate Status）\n"
            "| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | no findings |\n",
            encoding="utf-8",
        )

    def _commit_baseline(self, target: Path) -> None:
        subprocess.run(["git", "add", "."], cwd=target, check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"], cwd=target, check=True, capture_output=True, text=True
        )
        subprocess.run(
            ["git", "config", "user.name", "SpecDock Test"], cwd=target, check=True, capture_output=True, text=True
        )
        subprocess.run(["git", "commit", "-m", "baseline"], cwd=target, check=True, capture_output=True, text=True)
