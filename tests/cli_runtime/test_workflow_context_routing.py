from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestWorkflowContextRouting(CliRuntimeHarness):
    def test_workflow_next_issue_execution_includes_step_assurance_and_context_packets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Context routing")
            self._write_substantive_requirement(issue_dir)
            self._write_plan_and_report(issue_dir)
            self._classify(target)
            self._commit_baseline(target)

            result = self._run_runtime_capture(
                target,
                ["workflow", "next", "issue-execution", "--format", "json"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            payload = json.loads(result.stdout)
            assert payload["state"] == "ready"
            assert payload["step_assurance"]["selected_step"]["id"] == "S02"
            assert payload["step_assurance"]["worker"] == "dev-coder"
            assert payload["step_assurance"]["context_mode"] == "recent_fork"
            assert payload["step_assurance"]["verification"] == ["unit_tests"]
            assert payload["step_assurance"]["reviewers"] == ["code-reviewer"]
            assert payload["context_packets"]["written"] is True
            assert all(
                ref["path"].startswith("spec-dock/.agent/context-packets/")
                for ref in payload["context_packets"]["refs"]
            )
            assert all(ref["sha256"] for ref in payload["context_packets"]["refs"])

            events = payload["context_packets"]["invocation_events"]
            dev_event = next(event for event in events if event["role"] == "dev-coder")
            assert dev_event["reasoning_effort"] == "medium"
            assert dev_event["context_mode"] == "recent_fork"
            assert dev_event["policy_version"] == "context-routing-policy-v1"
            assert dev_event["packet_hash"]
            assert dev_event["fork_turn_count"] == 0
            assert dev_event["include_categories"]
            assert "private_reasoning" in dev_event["exclude_categories"]
            assert dev_event["returned_evidence_refs"]

            projected = json.loads(
                (target / "spec-dock/.agent/context-packets/current-context-packets.json").read_text(encoding="utf-8")
            )
            assert projected["step_assurance"]["selected_step"]["id"] == "S02"
            projected_runbook = json.loads(
                (target / "spec-dock/.agent/runbooks/current-runbook.json").read_text(encoding="utf-8")
            )
            assert projected_runbook["step_assurance"]["selected_step"]["id"] == "S02"
            assert projected_runbook["context_packets"]["refs"]
            projected_markdown = (target / "spec-dock/active/current-runbook.md").read_text(encoding="utf-8")
            assert "## Step Assurance" in projected_markdown
            assert "## Context Packets" in projected_markdown
            status = subprocess.run(
                ["git", "status", "--short"],
                cwd=target,
                capture_output=True,
                text=True,
                check=True,
            )
            assert status.stdout == ""

    def test_workflow_next_dirty_worktree_forces_bounded_continuation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Context routing")
            self._write_substantive_requirement(issue_dir)
            self._write_plan_and_report(issue_dir)
            self._classify(target)
            self._commit_baseline(target)
            (target / "untracked-note.txt").write_text("local scratch\n", encoding="utf-8")

            result = self._run_runtime_capture(
                target,
                ["workflow", "next", "issue-execution", "--format", "json"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            payload = json.loads(result.stdout)
            assert payload["step_assurance"]["selected_step"]["id"] == "S02"
            assert payload["step_assurance"]["context_mode"] == "bounded_packet"
            assert payload["step_assurance"]["continuation"] == {
                "eligible": False,
                "context_mode": "bounded_packet",
                "reason_codes": ["worktree_not_clean"],
            }
            event = next(
                event for event in payload["context_packets"]["invocation_events"] if event["role"] == "dev-coder"
            )
            assert event["context_mode"] == "bounded_packet"

    def test_workflow_next_does_not_skip_step_from_scaffold_report_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Context routing")
            self._write_substantive_requirement(issue_dir)
            self._write_plan_and_report(issue_dir)
            (issue_dir / "report.md").write_text(
                "# Report\n\n"
                "#### 対象\n"
                "- Step: S01, S02, ...\n\n"
                "### セッションログ（2026-06-23 S01）\n\n"
                "#### 対象\n"
                "- Step: S01\n\n"
                "#### ステップ契約の完了証跡\n"
                "| ステップ | 結果 |\n"
                "|---|---|\n"
                "| S01 | fail |\n",
                encoding="utf-8",
            )
            self._classify(target)

            result = self._run_runtime_capture(
                target,
                ["workflow", "next", "issue-execution", "--format", "json"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            payload = json.loads(result.stdout)
            assert payload["step_assurance"]["selected_step"]["id"] == "S01"

    def test_workflow_next_does_not_skip_step_from_red_phase_pass_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Context routing")
            self._write_substantive_requirement(issue_dir)
            self._write_plan_and_report(issue_dir)
            (issue_dir / "report.md").write_text(
                "# Report\n\n"
                "### セッションログ（2026-06-23 S01）\n\n"
                "#### 対象\n"
                "- Step: S01\n\n"
                "#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）\n"
                "| ステップ | フェーズ | 結果 |\n"
                "|---|---|---|\n"
                "| S01 | Red | pass |\n",
                encoding="utf-8",
            )
            self._classify(target)

            result = self._run_runtime_capture(
                target,
                ["workflow", "next", "issue-execution", "--format", "json"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            payload = json.loads(result.stdout)
            assert payload["step_assurance"]["selected_step"]["id"] == "S01"

    def test_workflow_next_routes_plan_derived_task_kinds(self) -> None:
        cases = [
            ("docs-only", "doc-writer", "low", "minimal_packet", ["docs_inspection"], ["spec-reviewer"]),
            (
                "migration rollback",
                "dev-coder",
                "high",
                "bounded_packet",
                ["unit_tests", "integration_tests", "rollback_plan"],
                ["code-reviewer", "qa-reviewer"],
            ),
            (
                "security privacy",
                "dev-coder",
                "xhigh",
                "bounded_packet",
                ["unit_tests", "security_review", "privacy_review"],
                ["code-reviewer", "qa-reviewer", "spec-reviewer"],
            ),
        ]
        for marker, worker, reasoning_effort, context_mode, verification, reviewers in cases:
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp)
                assert main(["init", str(target)]) == 0
                issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Context routing")
                self._write_substantive_requirement(issue_dir)
                self._write_single_step_plan_and_empty_report(issue_dir, marker)
                self._classify(target)
                self._commit_baseline(target)

                result = self._run_runtime_capture(
                    target,
                    ["workflow", "next", "issue-execution", "--format", "json"],
                )

                assert result.returncode == 0, result.stdout + result.stderr
                payload = json.loads(result.stdout)
                assert payload["step_assurance"]["selected_step"]["id"] == "S01"
                assert payload["step_assurance"]["worker"] == worker
                assert payload["step_assurance"]["reasoning_effort"] == reasoning_effort
                assert payload["step_assurance"]["context_mode"] == context_mode
                assert payload["step_assurance"]["verification"] == verification
                assert payload["step_assurance"]["reviewers"] == reviewers
                event = next(
                    event for event in payload["context_packets"]["invocation_events"] if event["role"] == worker
                )
                assert event["reasoning_effort"] == reasoning_effort

    def test_workflow_next_markdown_includes_step_assurance_and_packet_refs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Context routing")
            self._write_substantive_requirement(issue_dir)
            self._write_plan_and_report(issue_dir)
            self._classify(target)

            result = self._run_runtime_capture(
                target,
                ["workflow", "next", "issue-execution", "--format", "markdown"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            assert "## Step Assurance" in result.stdout
            assert "- selected_step: S02" in result.stdout
            assert "## Context Packets" in result.stdout
            assert "spec-dock/.agent/context-packets/current-context-packets.json" in result.stdout

    def test_missing_assurance_uses_strict_legacy_step_assurance_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Missing assurance")
            self._write_substantive_requirement(issue_dir)
            self._write_plan_and_report(issue_dir)

            result = self._run_runtime_capture(
                target,
                ["workflow", "next", "issue-execution", "--format", "json"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            payload = json.loads(result.stdout)
            assert payload["state"] == "ready"
            assert payload["reason_code"] == "strict-legacy-missing-assurance"
            assert payload["authority"]["authorized_profile"] == "strict"
            assert payload["step_assurance"]["selected_step"]["id"] == "S02"
            assert payload["context_packets"]["written"] is True

    def test_invalid_context_policy_degrades_worker_and_fails_closed_reviewers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Context routing")
            self._write_substantive_requirement(issue_dir)
            self._write_plan_and_report(issue_dir)
            self._classify(target)
            (target / "spec-dock/system/assurance/context-routing-policy.json").write_text(
                "{not-json\n", encoding="utf-8"
            )

            result = self._run_runtime_capture(
                target,
                ["workflow", "next", "issue-execution", "--format", "json"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            payload = json.loads(result.stdout)
            assert payload["step_assurance"]["policy"]["status"] == "invalid"
            assert payload["step_assurance"]["context_mode"] == "bounded_packet"
            reviewer_event = next(
                event for event in payload["context_packets"]["invocation_events"] if event["role"] == "code-reviewer"
            )
            assert reviewer_event["context_mode"] == "clean_room"
            assert reviewer_event["packet_hash"] is None
            assert reviewer_event["missing_reason"] == "context_policy_invalid"

    def test_invalid_context_policy_degrades_docs_worker_to_bounded_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Context routing")
            self._write_substantive_requirement(issue_dir)
            self._write_single_step_plan_and_empty_report(issue_dir, "docs-only")
            self._classify(target)
            (target / "spec-dock/system/assurance/context-routing-policy.json").write_text(
                "{not-json\n", encoding="utf-8"
            )

            result = self._run_runtime_capture(
                target,
                ["workflow", "next", "issue-execution", "--format", "json"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            payload = json.loads(result.stdout)
            assert payload["step_assurance"]["worker"] == "doc-writer"
            assert payload["step_assurance"]["policy"]["status"] == "invalid"
            assert payload["step_assurance"]["context_mode"] == "bounded_packet"

    def test_context_packet_write_failure_blocks_ready_issue_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Context routing")
            self._write_substantive_requirement(issue_dir)
            self._write_plan_and_report(issue_dir)
            self._classify(target)
            packet_dir = target / "spec-dock/.agent/context-packets"
            outside = target / "outside-context-packets"
            assert not packet_dir.exists()
            outside.mkdir()
            packet_dir.parent.mkdir(parents=True, exist_ok=True)
            packet_dir.symlink_to(outside, target_is_directory=True)

            result = self._run_runtime_capture(
                target,
                ["workflow", "next", "issue-execution", "--format", "json"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            payload = json.loads(result.stdout)
            assert payload["state"] == "blocked"
            assert payload["reason_code"] == "context-packet-write-failure"
            assert payload["context_packets"]["written"] is False
            assert payload["projection"]["written"] is True

    def test_valid_context_policy_exclusions_apply_to_packet_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Context routing")
            self._write_substantive_requirement(issue_dir)
            self._write_plan_and_report(issue_dir)
            self._classify(target)
            policy_path = target / "spec-dock/system/assurance/context-routing-policy.json"
            policy = json.loads(policy_path.read_text(encoding="utf-8"))
            policy["reviewer_exclusions"] = [*policy["reviewer_exclusions"], "custom_reviewer_exclusion"]
            policy_path.write_text(json.dumps(policy), encoding="utf-8")

            result = self._run_runtime_capture(
                target,
                ["workflow", "next", "issue-execution", "--format", "json"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            payload = json.loads(result.stdout)
            reviewer_event = next(
                event for event in payload["context_packets"]["invocation_events"] if event["role"] == "code-reviewer"
            )
            assert "custom_reviewer_exclusion" in reviewer_event["exclude_categories"]

    def test_unselectable_step_does_not_prompt_implementation_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Context routing")
            self._write_substantive_requirement(issue_dir)
            (issue_dir / "plan.md").write_text("# Plan\n\nNo structured implementation steps.\n", encoding="utf-8")
            (issue_dir / "report.md").write_text("# Report\n", encoding="utf-8")
            self._classify(target)

            result = self._run_runtime_capture(
                target,
                ["workflow", "next", "issue-execution", "--format", "json"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            payload = json.loads(result.stdout)
            assert payload["state"] == "blocked"
            assert payload["next_action"] == "issue-planning-required"
            assert payload["reason_code"] == "workflow-plan-unselectable"
            assert payload["step_assurance"]["selected_step"]["id"] == "issue-wide"
            assert payload["step_assurance"]["worker"] is None
            assert payload["step_assurance"]["context_mode"] == "minimal_packet"
            assert payload["step_assurance"]["verification"] == []
            assert "context_packets" not in payload

    def test_scaffold_plan_step_does_not_prompt_implementation_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_workflow_fixture(target, issue_number=301, title="Context routing")
            self._write_substantive_requirement(issue_dir)
            (issue_dir / "report.md").write_text("# Report\n", encoding="utf-8")
            self._classify(target)

            result = self._run_runtime_capture(
                target,
                ["workflow", "next", "issue-execution", "--format", "json"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            payload = json.loads(result.stdout)
            assert payload["state"] == "blocked"
            assert payload["reason_code"] == "workflow-plan-unselectable"
            assert payload["step_assurance"]["selected_step"]["id"] == "issue-wide"
            assert "context_packets" not in payload

    def _classify(self, target: Path) -> None:
        classify = self._run_runtime_capture(
            target,
            ["assurance", "classify", "--stage", "requirement", "--format", "json"],
        )
        assert classify.returncode == 0, classify.stdout + classify.stderr

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
            "- The command returns deterministic context routing projection.\n",
            encoding="utf-8",
        )

    def _write_plan_and_report(self, issue_dir: Path) -> None:
        (issue_dir / "plan.md").write_text(
            "# Plan\n\n"
            "## 実装ステップ\n\n"
            "### 実装ステップ S01 — Step Assurance と Context Routing policy を固定する\n"
            "- 対象ファイル: domain/context_routing.py\n\n"
            "### 実装ステップ S02 — Context Packet と Runbook projection へ接続する\n"
            "- 対象ファイル: application / infra / presentation / CLI tests\n"
            "- Green 検証: unit_tests\n\n"
            "## ドキュメント影響の解消ステップ S90\n"
            "- docs impact gate\n",
            encoding="utf-8",
        )
        (issue_dir / "report.md").write_text(
            "# Report\n\n"
            "### セッションログ（2026-06-23 10:00 - 10:30）\n\n"
            "#### 対象\n"
            "- Step: S01\n\n"
            "#### ステップ契約の完了証跡\n"
            "| ステップ | 結果 |\n"
            "|---|---|\n"
            "| S01 | pass |\n\n"
            "#### メモ\n"
            "- Reviewer context remains fail-closed for unavailable policy.\n",
            encoding="utf-8",
        )

    def _write_single_step_plan_and_empty_report(self, issue_dir: Path, marker: str) -> None:
        (issue_dir / "plan.md").write_text(
            f"# Plan\n\n## 実装ステップ S01 — Plan-derived routing\n- Task marker: {marker}\n",
            encoding="utf-8",
        )
        (issue_dir / "report.md").write_text("# Report\n", encoding="utf-8")

    def _commit_baseline(self, target: Path) -> None:
        subprocess.run(["git", "add", "."], cwd=target, check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"], cwd=target, check=True, capture_output=True, text=True
        )
        subprocess.run(
            ["git", "config", "user.name", "SpecDock Test"], cwd=target, check=True, capture_output=True, text=True
        )
        subprocess.run(["git", "commit", "-m", "baseline"], cwd=target, check=True, capture_output=True, text=True)
