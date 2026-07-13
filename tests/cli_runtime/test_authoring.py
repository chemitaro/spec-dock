import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any
import zipfile

import pytest

from tests.cli_runtime.harness import CliRuntimeHarness, main

_DEFERRED_COMMANDS: tuple[tuple[list[str], str, str], ...] = ()

_FORBIDDEN_AUTHORITY_CLAIMS = (
    "canonical docs",
    ".assurance.json",
    "authorized profile",
    "set-authorized-profile",
    "success",
    "adoption_status",
    "adopted",
    "reviewer pass",
    "execution-ready",
    "pr-ready",
    "merge-ready",
)


class TestAuthoringCli(CliRuntimeHarness):
    def test_authoring_help_exposes_deferred_command_groups(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(target, ["authoring", "--help"])

            assert p.returncode == 0, p.stdout + p.stderr
            assert "Run ChatGPT authoring helper commands" in p.stdout
            for expected in ("preflight", "pack", "backend", "validate", "approval"):
                assert expected in p.stdout
            assert "authoring preflight github-sync" in p.stdout
            assert "authoring pack prepare" in p.stdout
            for _args, command, _next_issue in _DEFERRED_COMMANDS:
                assert command in p.stdout

    def test_authoring_pack_prepare_help_exposes_inputs_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(target, ["authoring", "pack", "prepare", "--help"])

            assert p.returncode == 0, p.stdout + p.stderr
            assert "--preflight" in p.stdout
            assert "--output-dir" in p.stdout
            assert "--format" in p.stdout
            assert "--mode" in p.stdout
            assert "--force" not in p.stdout

    def test_authoring_backend_invoke_help_exposes_contract_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(target, ["authoring", "backend", "invoke", "--help"])

            assert p.returncode == 0, p.stdout + p.stderr
            assert "--prompt-pack" in p.stdout
            assert "--output-dir" in p.stdout
            assert "--backend-command" in p.stdout
            assert "--oracle" not in p.stdout
            assert "--evidence-mode" in p.stdout
            assert "--dry-run" in p.stdout
            assert "--force" not in p.stdout

    def test_authoring_pack_review_help_exposes_implemented_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(target, ["authoring", "pack", "review", "--help"])

            assert p.returncode == 0, p.stdout + p.stderr
            assert "--input" in p.stdout
            assert "--format" in p.stdout
            assert "--evidence-mode" in p.stdout
            assert "--report-path" in p.stdout
            assert "Deferred ZIP review skeleton" not in p.stdout

    def test_authoring_pack_stage_help_exposes_implemented_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(target, ["authoring", "pack", "stage", "--help"])

            assert p.returncode == 0, p.stdout + p.stderr
            assert "--input" in p.stdout
            assert "--stage-dir" in p.stdout
            assert "--dry-run" in p.stdout
            assert "--format" in p.stdout
            assert "Deferred ZIP staging skeleton" not in p.stdout

    def test_authoring_validate_initiative_epic_candidates_help_exposes_implemented_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(target, ["authoring", "validate", "initiative-epic-candidates", "--help"])

            assert p.returncode == 0, p.stdout + p.stderr
            assert "--input" in p.stdout
            assert "--expected-parent-initiative" in p.stdout
            assert "--review-report" in p.stdout
            assert "--report-path" in p.stdout
            assert "Deferred" not in p.stdout

    def test_authoring_validate_epic_issue_candidates_help_exposes_implemented_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(target, ["authoring", "validate", "epic-issue-candidates", "--help"])

            assert p.returncode == 0, p.stdout + p.stderr
            assert "--input" in p.stdout
            assert "--expected-parent-epic" in p.stdout
            assert "--review-report" in p.stdout
            assert "--report-path" in p.stdout
            assert "Deferred" not in p.stdout

    def test_authoring_validate_issue_draft_adoption_help_exposes_implemented_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(target, ["authoring", "validate", "issue-draft-adoption", "--help"])

            assert p.returncode == 0, p.stdout + p.stderr
            assert "--input" in p.stdout
            assert "--issue-dir" in p.stdout
            assert "--review-report" in p.stdout
            assert "--expected-review-digest" in p.stdout
            assert "--expected-draft-pack-digest" in p.stdout
            assert "--report-path" in p.stdout
            assert "Deferred" not in p.stdout

    def test_authoring_validate_selected_skeleton_fill_help_exposes_implemented_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(target, ["authoring", "validate", "selected-skeleton-fill", "--help"])

            assert p.returncode == 0, p.stdout + p.stderr
            assert "--input" in p.stdout
            assert "--issue-dir" in p.stdout
            assert "--assurance" in p.stdout
            assert "--selected-skeleton" in p.stdout
            assert "--review-report" in p.stdout
            assert "--expected-review-digest" in p.stdout
            assert "--expected-profile" in p.stdout
            assert "--report-path" in p.stdout
            assert "Deferred" not in p.stdout

    def test_authoring_approval_check_help_exposes_implemented_contract_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(target, ["authoring", "approval", "check", "--help"])

            assert p.returncode == 0, p.stdout + p.stderr
            for expected in (
                "--input",
                "--approval",
                "--candidate-kind",
                "--candidate-evidence",
                "--expected-parent-initiative",
                "--expected-parent-epic",
                "--expected-requested-scope",
                "--expected-effective-scope",
                "--expected-candidate-pack-digest",
                "--expected-candidate-evidence-digest",
                "--expected-source-manifest-hash",
                "--review-report",
                "--evidence-mode",
                "--format",
                "--report-path",
            ):
                assert expected in p.stdout
            assert "--force" not in p.stdout
            assert "Deferred" not in p.stdout

    @pytest.mark.parametrize(
        ("kind", "parent_flag", "parent_id", "scope"),
        (
            ("epic-issue", "--expected-parent-epic", "epic-00295", "epic:epic-00295"),
            ("initiative-epic", "--expected-parent-initiative", "init-local-00003", "initiative:init-local-00003"),
        ),
    )
    def test_authoring_approval_check_valid_human_approval_passes(
        self, kind: str, parent_flag: str, parent_id: str, scope: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(repo / ".specdock-authoring" / "staged" / kind, kind=kind)
            approval = _write_approval_evidence(stage_dir / "approval.json", stage_dir, kind=kind, scope=scope)

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "approval",
                    "check",
                    "--input",
                    str(stage_dir),
                    "--approval",
                    str(approval),
                    "--candidate-kind",
                    kind,
                    parent_flag,
                    parent_id,
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert payload["approval_gate_passed"] is True
            assert payload["authority"] == "evidence_only"
            assert payload["adoption_status"] == "unreviewed"
            assert payload["bundle_generation_not_promotion"] is True
            assert payload["node_creation_performed"] is False
            assert payload["canonical_written"] is False
            assert payload["assurance_mutated"] is False
            assert payload["reviewer_pass_claimed"] is False
            assert payload["execution_ready"] is False
            assert payload["pr_ready"] is False
            assert payload["comparisons"]["candidate_pack_digest"] == "match"

    def test_authoring_approval_check_missing_approval_blocks_candidate_validation_alone(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(repo / ".specdock-authoring" / "staged" / "missing", kind="epic-issue")

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "approval",
                    "check",
                    "--input",
                    str(stage_dir),
                    "--candidate-kind",
                    "epic-issue",
                    "--expected-parent-epic",
                    "epic-00295",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "blocked"
            assert "missing_approval_evidence" in payload["findings"]
            assert payload["approval_gate_passed"] is False

    @pytest.mark.parametrize(
        ("approval_mutator", "expected_status", "finding_or_comparison"),
        (
            ("stale-digest", "stale", "candidate_pack_digest_mismatch"),
            ("requested-scope-mismatch", "blocked", "requested_scope_mismatch"),
            ("effective-scope-mismatch", "blocked", "effective_scope_mismatch"),
            ("self-approval", "rejected", "self_approval_forbidden"),
            ("forbidden-claim", "rejected", "forbidden_authority_claim:execution-ready"),
            ("sensitive-statement", "rejected", "secret_like_payload:token"),
        ),
    )
    def test_authoring_approval_check_rejects_stale_mismatched_or_unsafe_approval(
        self, approval_mutator: str, expected_status: str, finding_or_comparison: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(
                repo / ".specdock-authoring" / "staged" / approval_mutator, kind="epic-issue"
            )
            approval = _write_approval_evidence(
                stage_dir / "approval.json",
                stage_dir,
                kind="epic-issue",
                scope="epic:epic-00295",
                mutator=approval_mutator,
            )

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "approval",
                    "check",
                    "--input",
                    str(stage_dir),
                    "--approval",
                    str(approval),
                    "--candidate-kind",
                    "epic-issue",
                    "--expected-parent-epic",
                    "epic-00295",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == expected_status
            assert finding_or_comparison in payload["findings"] or finding_or_comparison in payload["comparison"]

    def test_authoring_approval_check_separates_candidate_evidence_file_digest_and_source_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(repo / ".specdock-authoring" / "staged" / "evidence", kind="epic-issue")
            approval = _write_approval_evidence(
                stage_dir / "approval.json", stage_dir, kind="epic-issue", scope="epic:epic-00295"
            )
            candidate_evidence = stage_dir / "candidate-evidence.json"
            candidate_evidence.write_text(
                json.dumps({"source_manifest_hash": "old-source"}, sort_keys=True) + "\n", encoding="utf-8"
            )

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "approval",
                    "check",
                    "--input",
                    str(stage_dir),
                    "--approval",
                    str(approval),
                    "--candidate-kind",
                    "epic-issue",
                    "--candidate-evidence",
                    str(candidate_evidence),
                    "--expected-parent-epic",
                    "epic-00295",
                    "--expected-candidate-evidence-digest",
                    "wrong",
                    "--expected-source-manifest-hash",
                    "hash",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "stale"
            assert payload["candidate_evidence_file_digest"]
            assert "candidate_evidence_file_digest_mismatch" in payload["comparison"]
            assert "source_manifest_hash_mismatch" not in payload["comparison"]

    def test_authoring_approval_check_candidate_evidence_source_hash_cannot_mask_stale_pack_source_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(
                repo / ".specdock-authoring" / "staged" / "stale-source", kind="epic-issue"
            )
            fixture = _write_approval_fixture(
                stage_dir,
                kind="epic-issue",
                expected_scope="epic-00295",
                mutator="source-hash-mismatch",
            )

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "approval",
                    "check",
                    "--input",
                    str(stage_dir),
                    "--approval",
                    str(fixture["approval"]),
                    "--candidate-kind",
                    "epic-issue",
                    "--candidate-evidence",
                    str(fixture["candidate_evidence"]),
                    "--expected-parent-epic",
                    "epic-00295",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "stale"
            assert payload["observed_source_manifest_hash"] == "hash"
            assert "source_manifest_hash_mismatch" in payload["comparison"]

    def test_authoring_approval_check_report_paths_and_text_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(repo / ".specdock-authoring" / "staged" / "report", kind="epic-issue")
            approval = _write_approval_evidence(
                stage_dir / "approval.json", stage_dir, kind="epic-issue", scope="epic:epic-00295"
            )
            safe_report = repo / ".specdock-authoring" / "approval" / "report.json"

            text = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "approval",
                    "check",
                    "--input",
                    str(stage_dir),
                    "--approval",
                    str(approval),
                    "--candidate-kind",
                    "epic-issue",
                    "--expected-parent-epic",
                    "epic-00295",
                    "--report-path",
                    str(safe_report),
                ],
            )

            assert text.returncode == 0, text.stdout + text.stderr
            assert "authority=evidence_only" in text.stdout
            assert "node_creation_performed=false" in text.stdout
            assert "canonical_written=false" in text.stdout
            report_payload = json.loads(safe_report.read_text(encoding="utf-8"))
            assert report_payload["status"] == "pass"

            unsafe_report = repo / "spec-dock" / "active" / "issue" / "approval-report.json"
            unsafe = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "approval",
                    "check",
                    "--input",
                    str(stage_dir),
                    "--approval",
                    str(approval),
                    "--candidate-kind",
                    "epic-issue",
                    "--expected-parent-epic",
                    "epic-00295",
                    "--report-path",
                    str(unsafe_report),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(unsafe)
            assert unsafe.returncode == 1, unsafe.stdout + unsafe.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_report_path:canonical-docs" in payload["findings"]
            assert not unsafe_report.exists()

    def test_authoring_validate_initiative_epic_candidates_valid_stage_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(
                repo / ".specdock-authoring" / "staged" / "initiative", kind="initiative-epic"
            )

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "initiative-epic-candidates",
                    "--input",
                    str(stage_dir),
                    "--expected-parent-initiative",
                    "init-local-00003",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert payload["authority"] == "evidence_only"
            assert payload["adoption_status"] == "unreviewed"
            assert payload["candidate_kind"] == "initiative-epic"
            assert payload["candidate_count"] == 2
            assert payload["valid_candidate_count"] == 2
            assert payload["node_creation_performed"] is False
            assert payload["canonical_written"] is False
            assert payload["assurance_mutated"] is False
            assert payload["reviewer_pass_claimed"] is False
            assert payload["execution_ready"] is False
            assert payload["pr_ready"] is False

    def test_authoring_validate_epic_issue_candidates_valid_stage_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(repo / ".specdock-authoring" / "staged" / "issue", kind="epic-issue")

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "epic-issue-candidates",
                    "--input",
                    str(stage_dir),
                    "--expected-parent-epic",
                    "epic-00295",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert payload["candidate_kind"] == "epic-issue"
            assert payload["candidate_count"] == 3
            assert payload["valid_candidate_count"] == 3
            assert payload["review_gate_passed"] is True

    def test_authoring_validate_epic_issue_candidates_rejects_backslash_candidate_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(repo / ".specdock-authoring" / "staged" / "issue", kind="epic-issue")
            index_path = stage_dir / "specdock-authoring-pack" / "candidates" / "issues" / "index.json"
            index = json.loads(index_path.read_text(encoding="utf-8"))
            index["candidates"][0]["path"] = "candidates\\..\\..\\outside.json"
            index_path.write_text(json.dumps(index, sort_keys=True) + "\n", encoding="utf-8")

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "epic-issue-candidates",
                    "--input",
                    str(stage_dir),
                    "--expected-parent-epic",
                    "epic-00295",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "path_separator_backslash:candidates\\..\\..\\outside.json" in payload["findings"]

    def test_authoring_validate_candidates_blocks_passed_review_without_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(repo / ".specdock-authoring" / "staged" / "issue", kind="epic-issue")
            review_report = stage_dir / "review-report.json"
            review_report.write_text(
                json.dumps(
                    {
                        "status": "pass",
                        "authority": "evidence_only",
                        "adoption_status": "unreviewed",
                        "bundle_generation_not_promotion": True,
                    },
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "epic-issue-candidates",
                    "--input",
                    str(stage_dir),
                    "--expected-parent-epic",
                    "epic-00295",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "blocked"
            assert payload["review_gate_passed"] is False
            assert "missing_review_digest" in payload["findings"]

    @pytest.mark.parametrize(
        ("field", "value", "expected_finding"),
        (
            ("authority", "canonical", "review_report_authority_not_evidence_only"),
            ("adoption_status", "adopted", "review_report_adoption_status_not_unreviewed"),
            (
                "bundle_generation_not_promotion",
                False,
                "review_report_bundle_generation_not_promotion_not_true",
            ),
        ),
    )
    def test_authoring_validate_candidates_rejects_review_report_authority_boundary(
        self, field: str, value: object, expected_finding: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(repo / ".specdock-authoring" / "staged" / "issue", kind="epic-issue")
            report_path = stage_dir / "review-report.json"
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report[field] = value
            report_path.write_text(json.dumps(report, sort_keys=True) + "\n", encoding="utf-8")

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "epic-issue-candidates",
                    "--input",
                    str(stage_dir),
                    "--expected-parent-epic",
                    "epic-00295",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert payload["review_gate_passed"] is False
            assert expected_finding in payload["findings"]

    @pytest.mark.parametrize("symlink_kind", ("leaf", "ancestor"))
    def test_authoring_validate_candidates_rejects_symlink_review_report_input(self, symlink_kind: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(repo / ".specdock-authoring" / "staged" / "issue", kind="epic-issue")
            original = stage_dir / "review-report.json"
            outside = repo / "outside-review-report.json"
            outside.write_bytes(original.read_bytes())
            original.unlink()
            if symlink_kind == "leaf":
                original.symlink_to(outside)
            else:
                linked = stage_dir / "linked"
                linked.symlink_to(outside.parent, target_is_directory=True)
                original = linked / outside.name

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "epic-issue-candidates",
                    "--input",
                    str(stage_dir),
                    "--review-report",
                    str(original),
                    "--expected-parent-epic",
                    "epic-00295",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1
            assert payload["status"] == "rejected"
            assert "unsafe_review_report_path:symlink" in payload["findings"]

    def test_authoring_approval_check_valid_epic_issue_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(repo / ".specdock-authoring" / "staged" / "approval", kind="epic-issue")
            fixture = _write_approval_fixture(stage_dir, kind="epic-issue", expected_scope="epic-00295")
            before = _protected_tree_snapshot(repo)

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "approval",
                    "check",
                    "--input",
                    str(stage_dir),
                    "--approval",
                    str(fixture["approval"]),
                    "--candidate-kind",
                    "epic-issue",
                    "--expected-parent-epic",
                    "epic-00295",
                    "--expected-candidate-pack-digest",
                    str(fixture["candidate_pack_digest"]),
                    "--candidate-evidence",
                    str(fixture["candidate_evidence"]),
                    "--expected-candidate-evidence-digest",
                    str(fixture["candidate_evidence_digest"]),
                    "--expected-source-hash",
                    "hash",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert payload["approval_gate_passed"] is True
            assert payload["review_gate_passed"] is True
            assert payload["authority"] == "evidence_only"
            assert payload["adoption_status"] == "unreviewed"
            assert payload["node_creation_performed"] is False
            assert payload["canonical_written"] is False
            assert payload["assurance_mutated"] is False
            assert payload["reviewer_pass_claimed"] is False
            assert payload["execution_ready"] is False
            assert payload["pr_ready"] is False
            assert _protected_tree_snapshot(repo) == before

    def test_authoring_approval_check_valid_initiative_epic_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(
                repo / ".specdock-authoring" / "staged" / "approval-epic", kind="initiative-epic"
            )
            fixture = _write_approval_fixture(stage_dir, kind="initiative-epic", expected_scope="init-local-00003")

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "approval",
                    "check",
                    "--input",
                    str(stage_dir),
                    "--approval",
                    str(fixture["approval"]),
                    "--candidate-kind",
                    "initiative-epic",
                    "--expected-parent-initiative",
                    "init-local-00003",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert payload["candidate_kind"] == "initiative-epic"

    def test_authoring_approval_check_blocks_missing_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(
                repo / ".specdock-authoring" / "staged" / "missing-approval", kind="epic-issue"
            )

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "approval",
                    "check",
                    "--input",
                    str(stage_dir),
                    "--approval",
                    str(stage_dir / "missing-approval.json"),
                    "--candidate-kind",
                    "epic-issue",
                    "--expected-parent-epic",
                    "epic-00295",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode != 0
            assert payload["status"] == "blocked"
            assert "missing_approval_evidence" in payload["findings"]

    @pytest.mark.parametrize(
        ("mutator", "expected_status", "expected_fragment"),
        (
            ("missing-candidate-pack-digest", "fail", "missing_or_invalid_field:candidate_pack.candidate_pack_digest"),
            ("non-approved", "blocked", "approval_not_approved"),
            ("invalid-timestamp", "fail", "missing_or_invalid_field:approved_at"),
            ("invalid-schema-version", "fail", "invalid_schema_version:approval"),
            ("malformed-json", "fail", "invalid_json:approval"),
            ("non-object-json", "fail", "non_object_json:approval"),
            ("binary-approval", "fail", "binary_payload:approval"),
            ("oversized-approval", "rejected", "oversized_entry:approval"),
        ),
    )
    def test_authoring_approval_check_malformed_approval_evidence_fails_closed(
        self, mutator: str, expected_status: str, expected_fragment: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(repo / ".specdock-authoring" / "staged" / mutator, kind="epic-issue")
            fixture = _write_approval_fixture(
                stage_dir, kind="epic-issue", expected_scope="epic-00295", mutator=mutator
            )

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "approval",
                    "check",
                    "--input",
                    str(stage_dir),
                    "--approval",
                    str(fixture["approval"]),
                    "--candidate-kind",
                    "epic-issue",
                    "--expected-parent-epic",
                    "epic-00295",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode != 0
            assert payload["status"] == expected_status
            assert expected_fragment in json.dumps(payload, sort_keys=True)

    def test_authoring_approval_check_allows_omitted_approval_source_hash_without_expected_source_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(
                repo / ".specdock-authoring" / "staged" / "optional-source-hash",
                kind="epic-issue",
            )
            fixture = _write_approval_fixture(
                stage_dir,
                kind="epic-issue",
                expected_scope="epic-00295",
                mutator="missing-source-manifest-hash",
            )

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "approval",
                    "check",
                    "--input",
                    str(stage_dir),
                    "--approval",
                    str(fixture["approval"]),
                    "--candidate-kind",
                    "epic-issue",
                    "--expected-parent-epic",
                    "epic-00295",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert "missing_or_invalid_field:candidate_pack.source_manifest_hash" not in payload["findings"]
            assert "source_manifest_hash_mismatch" not in payload["comparison"]

    @pytest.mark.parametrize(
        ("mutator", "expected_status", "expected_fragment"),
        (
            ("candidate-pack-digest-mismatch", "stale", "candidate_pack_digest_mismatch"),
            ("candidate-evidence-digest-mismatch", "stale", "candidate_evidence_file_digest_mismatch"),
            ("source-hash-mismatch", "stale", "source_manifest_hash_mismatch"),
            ("scope-mismatch", "blocked", "requested_scope_mismatch"),
            ("approval-scope-mismatch", "blocked", "approval_scope_mismatch"),
            ("candidate-kind-mismatch", "blocked", "candidate_kind_mismatch"),
            ("self-approval", "rejected", "self_approval_forbidden"),
            ("forbidden-claim", "rejected", "forbidden_authority_claim:execution_ready"),
            ("forbidden-extra-field", "rejected", "forbidden_authority_claim:execution-ready"),
            ("top-level-execution-ready", "rejected", "forbidden_authority_claim:execution_ready"),
            ("nested-pr-ready", "rejected", "forbidden_authority_claim:pr_ready"),
            ("secret-text", "rejected", "secret_like_payload:token"),
        ),
    )
    def test_authoring_approval_check_negative_contracts(
        self, mutator: str, expected_status: str, expected_fragment: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(repo / ".specdock-authoring" / "staged" / mutator, kind="epic-issue")
            fixture = _write_approval_fixture(
                stage_dir, kind="epic-issue", expected_scope="epic-00295", mutator=mutator
            )

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "approval",
                    "check",
                    "--input",
                    str(stage_dir),
                    "--approval",
                    str(fixture["approval"]),
                    "--candidate-kind",
                    "epic-issue",
                    "--expected-parent-epic",
                    "epic-00295",
                    "--expected-candidate-pack-digest",
                    "wrong" if mutator == "candidate-pack-digest-mismatch" else str(fixture["candidate_pack_digest"]),
                    "--candidate-evidence",
                    str(fixture["candidate_evidence"]),
                    "--expected-candidate-evidence-digest",
                    "wrong"
                    if mutator == "candidate-evidence-digest-mismatch"
                    else str(fixture["candidate_evidence_digest"]),
                    "--expected-source-hash",
                    "wrong" if mutator == "source-hash-mismatch" else "hash",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode != 0
            assert payload["status"] == expected_status
            assert expected_fragment in json.dumps(payload, sort_keys=True)

    @pytest.mark.parametrize(
        ("candidate_kind", "parent_flag", "expected_fragment"),
        (
            ("epic-issue", "--expected-parent-epic", "--expected-parent-epic is required"),
            ("initiative-epic", "--expected-parent-initiative", "--expected-parent-initiative is required"),
        ),
    )
    def test_authoring_approval_check_requires_parent_scope_flag(
        self, candidate_kind: str, parent_flag: str, expected_fragment: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(
                repo / ".specdock-authoring" / "staged" / f"missing-{parent_flag.strip('-')}",
                kind=candidate_kind,
            )
            fixture = _write_approval_fixture(
                stage_dir,
                kind=candidate_kind,
                expected_scope="epic-00295" if candidate_kind == "epic-issue" else "init-local-00003",
            )

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "approval",
                    "check",
                    "--input",
                    str(stage_dir),
                    "--approval",
                    str(fixture["approval"]),
                    "--candidate-kind",
                    candidate_kind,
                    "--format",
                    "json",
                ],
            )

            assert p.returncode != 0
            assert expected_fragment in p.stderr

    def test_authoring_approval_check_writes_safe_report_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(
                repo / ".specdock-authoring" / "staged" / "approval-report", kind="epic-issue"
            )
            fixture = _write_approval_fixture(stage_dir, kind="epic-issue", expected_scope="epic-00295")
            report_path = repo / ".specdock-authoring" / "approval" / "approval-report.json"

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "approval",
                    "check",
                    "--input",
                    str(stage_dir),
                    "--approval",
                    str(fixture["approval"]),
                    "--candidate-kind",
                    "epic-issue",
                    "--expected-parent-epic",
                    "epic-00295",
                    "--report-path",
                    str(report_path),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            report_payload = json.loads(report_path.read_text(encoding="utf-8"))
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert report_payload["status"] == "pass"
            assert report_payload["node_creation_performed"] is False

    @pytest.mark.parametrize(
        ("report_kind", "expected_finding"),
        (
            ("canonical-docs", "unsafe_report_path:canonical-docs"),
            ("assurance", "unsafe_report_path:assurance"),
            ("symlink", "unsafe_report_path:symlink"),
            ("broken-symlink", "unsafe_report_path:symlink"),
        ),
    )
    def test_authoring_approval_check_rejects_unsafe_report_path(self, report_kind: str, expected_finding: str) -> None:
        if report_kind in {"symlink", "broken-symlink"} and not hasattr(os, "symlink"):
            pytest.skip("symlink unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(
                repo / ".specdock-authoring" / "staged" / "approval-unsafe-report", kind="epic-issue"
            )
            fixture = _write_approval_fixture(stage_dir, kind="epic-issue", expected_scope="epic-00295")
            if report_kind == "canonical-docs":
                report_path = repo / "spec-dock" / "active" / "issue" / "artifacts" / "approval-report.json"
            elif report_kind == "assurance":
                report_path = repo / ".specdock-authoring" / ".assurance.json"
            elif report_kind == "symlink":
                outside = repo / "outside-report.json"
                outside.write_text("{}\n", encoding="utf-8")
                report_path = repo / ".specdock-authoring" / "approval" / "symlink-report.json"
                report_path.parent.mkdir(parents=True, exist_ok=True)
                report_path.symlink_to(outside)
            else:
                outside = repo / "missing-outside-report.json"
                report_path = repo / ".specdock-authoring" / "approval" / "broken-symlink-report.json"
                report_path.parent.mkdir(parents=True, exist_ok=True)
                report_path.symlink_to(outside)

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "approval",
                    "check",
                    "--input",
                    str(stage_dir),
                    "--approval",
                    str(fixture["approval"]),
                    "--candidate-kind",
                    "epic-issue",
                    "--expected-parent-epic",
                    "epic-00295",
                    "--report-path",
                    str(report_path),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode != 0
            assert payload["status"] == "rejected"
            assert expected_finding in payload["findings"]
            if report_kind == "symlink":
                assert outside.read_text(encoding="utf-8") == "{}\n"
            elif report_kind == "broken-symlink":
                assert not outside.exists()
            else:
                assert not report_path.exists()

    def test_authoring_validate_candidates_accepts_documented_source_manifest_hash_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(
                repo / ".specdock-authoring" / "staged" / "source-flag", kind="epic-issue"
            )

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "epic-issue-candidates",
                    "--input",
                    str(stage_dir),
                    "--expected-parent-epic",
                    "epic-00295",
                    "--expected-source-manifest-hash",
                    "hash",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert payload["expected_source_manifest_hash"] == "hash"
            assert payload["observed_source_manifest_hash"] == "hash"

    @pytest.mark.parametrize(
        ("review_status", "expected_status"),
        (
            ("stale", "stale"),
            ("rejected", "rejected"),
            ("fail", "fail"),
            ("blocked", "blocked"),
            ("needs-human", "blocked"),
        ),
    )
    def test_authoring_validate_review_report_non_pass_statuses_skip_candidates(
        self, review_status: str, expected_status: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(
                repo / ".specdock-authoring" / "staged" / review_status,
                kind="epic-issue",
                review_status=review_status,
            )

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "epic-issue-candidates",
                    "--input",
                    str(stage_dir),
                    "--expected-parent-epic",
                    "epic-00295",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode != 0
            assert payload["status"] == expected_status
            assert payload["review_status"] == review_status
            assert payload["review_gate_passed"] is False
            assert payload["candidate_count"] == 0

    @pytest.mark.parametrize(
        ("mutator", "expected_status", "finding"),
        (
            ("parent-mismatch", "stale", "parent_epic_mismatch"),
            ("source-hash-mismatch", "stale", "source_manifest_hash_mismatch"),
            ("review-digest-mismatch", "stale", "review_digest_mismatch"),
            ("duplicate-id", "fail", "duplicate_candidate_id"),
            ("overlap", "fail", "overlapping_boundary"),
            ("missing-authority-claims", "fail", "authority_claims"),
            ("invalid-schema-version", "fail", "invalid_schema_version"),
            ("unsupported-grade", "fail", "unsupported_grade"),
            ("unsupported-profile", "fail", "unsupported_profile"),
            ("authorized-profile", "rejected", "authorized_profile"),
            ("secret-text", "rejected", "secret_like_payload:token"),
            ("raw-transcript", "rejected", "raw_transcript:raw transcript"),
            ("forbidden-claim", "rejected", "forbidden_authority_claim:pr-ready"),
            ("path-traversal", "rejected", "path_traversal"),
            ("windows-drive-draft", "rejected", "host_local_path"),
            ("windows-backslash-draft", "rejected", "path_separator_backslash"),
            ("host-local-path", "rejected", "host_local_path"),
            ("secret-path", "rejected", "secret_path"),
            ("secret-draft-path", "rejected", "secret_path"),
            ("hidden-path", "rejected", "hidden_path"),
            ("unsupported-suffix", "rejected", "unsupported_suffix"),
            ("symlink-draft", "rejected", "symlink_entry"),
            ("symlink-unindexed-file", "rejected", "symlink_entry:unindexed-link.md"),
            ("executable-draft", "rejected", "executable_entry"),
            ("binary-draft", "rejected", "binary_payload"),
            ("oversized-draft", "rejected", "oversized_entry"),
            ("candidate-id-mismatch", "fail", "candidate_identity_mismatch"),
            ("empty-index", "fail", "empty_candidates"),
        ),
    )
    def test_authoring_validate_epic_issue_candidates_negative_contracts(
        self, mutator: str, expected_status: str, finding: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(
                repo / ".specdock-authoring" / "staged" / mutator,
                kind="epic-issue",
                mutator=mutator,
            )

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "epic-issue-candidates",
                    "--input",
                    str(stage_dir),
                    "--expected-parent-epic",
                    "epic-00295",
                    "--expected-source-hash",
                    "hash",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode != 0
            assert payload["status"] == expected_status
            assert finding in json.dumps(payload, sort_keys=True)
            assert "abc123secret" not in p.stdout

    def test_authoring_validate_candidates_rejects_unsafe_report_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(repo / ".specdock-authoring" / "staged" / "report", kind="epic-issue")
            unsafe_report = repo / "spec-dock" / "active" / "issue" / "artifacts" / "candidate-report.json"

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "epic-issue-candidates",
                    "--input",
                    str(stage_dir),
                    "--expected-parent-epic",
                    "epic-00295",
                    "--report-path",
                    str(unsafe_report),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode != 0
            assert payload["status"] == "rejected"
            assert "unsafe_report_path:canonical-docs" in payload["findings"]
            assert not unsafe_report.exists()

    @pytest.mark.parametrize(
        ("report_name", "expected_finding"),
        (
            (".assurance.json", "unsafe_report_path:assurance"),
            ("symlink-report.json", "unsafe_report_path:symlink"),
        ),
    )
    def test_authoring_validate_candidates_rejects_other_unsafe_report_paths(
        self, report_name: str, expected_finding: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(repo / ".specdock-authoring" / "staged" / report_name, kind="epic-issue")
            report_path = repo / ".specdock-authoring" / report_name
            if report_name == "symlink-report.json":
                outside = repo / "outside-report.json"
                outside.write_text("", encoding="utf-8")
                report_path.symlink_to(outside)

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "epic-issue-candidates",
                    "--input",
                    str(stage_dir),
                    "--expected-parent-epic",
                    "epic-00295",
                    "--report-path",
                    str(report_path),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode != 0
            assert payload["status"] == "rejected"
            assert expected_finding in payload["findings"]

    def test_authoring_validate_candidates_handles_binary_review_report_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(
                repo / ".specdock-authoring" / "staged" / "binary-report", kind="epic-issue"
            )
            review_report = repo / "binary-review-report.json"
            review_report.write_bytes(b"\xff\xfe\x00")

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "epic-issue-candidates",
                    "--input",
                    str(stage_dir),
                    "--expected-parent-epic",
                    "epic-00295",
                    "--review-report",
                    str(review_report),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode != 0
            assert payload["status"] == "fail"
            assert payload["findings"] == ["malformed_review_report"]
            assert "Traceback" not in p.stderr

    def test_authoring_validate_initiative_epic_candidates_rejects_unknown_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(
                repo / ".specdock-authoring" / "staged" / "unknown-epic-dependency",
                kind="initiative-epic",
                mutator="unknown-epic-dependency",
            )

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "initiative-epic-candidates",
                    "--input",
                    str(stage_dir),
                    "--expected-parent-initiative",
                    "init-local-00003",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode != 0
            assert payload["status"] == "fail"
            assert "unknown_epic_candidate_dependency" in json.dumps(payload, sort_keys=True)

    def test_authoring_validate_initiative_epic_candidates_accepts_same_index_forward_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(
                repo / ".specdock-authoring" / "staged" / "forward-epic-dependency",
                kind="initiative-epic",
                mutator="forward-epic-dependency",
            )

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "initiative-epic-candidates",
                    "--input",
                    str(stage_dir),
                    "--expected-parent-initiative",
                    "init-local-00003",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"

    def test_authoring_validate_issue_draft_adoption_valid_payload_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_issue_draft_adoption_fixture(repo)

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "issue-draft-adoption",
                    "--input",
                    str(fixture["input"]),
                    "--issue-dir",
                    str(fixture["issue_dir"]),
                    "--review-report",
                    str(fixture["review_report"]),
                    "--expected-review-digest",
                    str(fixture["review_digest"]),
                    "--expected-draft-pack-digest",
                    str(fixture["draft_pack_digest"]),
                    "--expected-source-hash",
                    "source-hash",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert payload["validation_kind"] == "issue-draft-adoption"
            assert payload["authority"] == "evidence_only"
            assert payload["adoption_status"] == "unreviewed"
            assert payload["review_gate_passed"] is True
            assert payload["issue_id"] == "iss-00303"
            assert payload["draft_count"] == 3
            assert payload["valid_draft_count"] == 3
            assert payload["eal_disposition_required"] is True
            assert payload["canonical_targets"] == {
                "requirement": "requirement.md",
                "design": "design.md",
                "plan": "plan.md",
                "report_evidence": "report.md",
            }
            assert payload["canonical_written"] is False
            assert payload["assurance_mutated"] is False
            assert payload["reviewer_pass_claimed"] is False
            assert payload["execution_ready"] is False
            assert payload["pr_ready"] is False

    def test_authoring_validate_issue_draft_adoption_text_output_valid_payload_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_issue_draft_adoption_fixture(repo)

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "issue-draft-adoption",
                    "--input",
                    str(fixture["input"]),
                    "--issue-dir",
                    str(fixture["issue_dir"]),
                    "--review-report",
                    str(fixture["review_report"]),
                    "--expected-review-digest",
                    str(fixture["review_digest"]),
                    "--expected-draft-pack-digest",
                    str(fixture["draft_pack_digest"]),
                    "--expected-source-hash",
                    "source-hash",
                ],
            )

            assert p.returncode == 0, p.stdout + p.stderr
            _assert_text_output_preserves_draft_validation_boundary(p.stdout)
            assert "status=pass" in p.stdout
            assert "authoring validate issue-draft-adoption" in p.stdout
            assert "draft_count=3" in p.stdout
            assert "valid_draft_count=3" in p.stdout

    def test_authoring_validate_issue_draft_adoption_detects_review_digest_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_issue_draft_adoption_fixture(repo)

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "issue-draft-adoption",
                    "--input",
                    str(fixture["input"]),
                    "--issue-dir",
                    str(fixture["issue_dir"]),
                    "--review-report",
                    str(fixture["review_report"]),
                    "--expected-review-digest",
                    "wrong",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode != 0
            assert payload["status"] == "stale"
            assert "review_digest_mismatch" in payload["comparison"]

    def test_authoring_validate_issue_draft_adoption_blocks_passed_review_without_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_issue_draft_adoption_fixture(repo)
            Path(fixture["review_report"]).write_text(
                json.dumps(_evidence_review_report("pass"), sort_keys=True) + "\n", encoding="utf-8"
            )

            payload = _run_issue_draft_adoption_json(self, repo, fixture)

            assert payload["status"] == "blocked"
            assert payload["review_gate_passed"] is False
            assert "missing_review_digest" in payload["findings"]

    def test_authoring_validate_issue_draft_adoption_rejects_review_report_authority_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_issue_draft_adoption_fixture(repo)
            report = _evidence_review_report("pass", "draft-pack-hash")
            report["authority"] = "canonical"
            Path(fixture["review_report"]).write_text(json.dumps(report, sort_keys=True) + "\n", encoding="utf-8")

            payload = _run_issue_draft_adoption_json(self, repo, fixture)

            assert payload["status"] == "rejected"
            assert payload["review_gate_passed"] is False
            assert "review_report_authority_not_evidence_only" in payload["findings"]

    @pytest.mark.parametrize("symlink_kind", ("leaf", "ancestor"))
    def test_authoring_validate_issue_draft_adoption_rejects_symlink_review_report_input(
        self, symlink_kind: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_issue_draft_adoption_fixture(repo)
            original = Path(fixture["review_report"])
            outside = repo / "outside-review-report.json"
            outside.write_bytes(original.read_bytes())
            original.unlink()
            if symlink_kind == "leaf":
                original.symlink_to(outside)
                review_report = original
            else:
                linked = original.parent / "linked"
                linked.symlink_to(outside.parent, target_is_directory=True)
                review_report = linked / outside.name

            payload = _run_issue_draft_adoption_json(
                self,
                repo,
                fixture,
                "--review-report",
                str(review_report),
            )

            assert payload["status"] == "rejected"
            assert "unsafe_review_report_path:symlink" in payload["findings"]

    def test_authoring_validate_issue_draft_adoption_rejects_backslash_draft_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_issue_draft_adoption_fixture(repo)
            input_path = Path(fixture["input"])
            payload = json.loads(input_path.read_text(encoding="utf-8"))
            payload["drafts"]["requirement"]["path"] = "artifacts\\..\\outside.md"
            input_path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")

            result = _run_issue_draft_adoption_json(self, repo, fixture)

            assert result["status"] == "rejected"
            assert "path_separator_backslash:artifacts\\..\\outside.md" in result["findings"]

    @pytest.mark.parametrize(
        ("review_status", "expected_status", "expected_fragment"),
        (
            ("stale", "stale", "review_not_pass:stale"),
            ("rejected", "rejected", "review_not_pass:rejected"),
            ("fail", "fail", "review_not_pass:fail"),
            ("blocked", "blocked", "review_not_pass:blocked"),
            ("needs-human", "blocked", "unsupported_review_status:needs-human"),
        ),
    )
    def test_authoring_validate_issue_draft_adoption_review_status_matrix(
        self, review_status: str, expected_status: str, expected_fragment: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_issue_draft_adoption_fixture(repo)
            Path(fixture["review_report"]).write_text(
                json.dumps({"status": review_status}, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            payload = _run_issue_draft_adoption_json(self, repo, fixture)

            assert payload["status"] == expected_status
            assert expected_fragment in json.dumps(payload, sort_keys=True)

    @pytest.mark.parametrize(
        ("mutator", "expected_status", "expected_fragment"),
        (
            ("issue-id-mismatch", "stale", "issue_id_mismatch"),
            ("parent-mismatch", "stale", "parent_epic_mismatch"),
            ("missing-draft-pack-digest", "fail", "missing_or_invalid_field:draft_pack_digest"),
            ("missing-eal-disposition", "fail", "missing_or_invalid_field:eal_disposition_required"),
            ("missing-draft-sha", "fail", "missing_or_invalid_field:drafts.requirement.sha256"),
            ("merge-ready-claim", "rejected", "forbidden_authority_claim:merge_ready"),
            ("pr-delivery-claim", "rejected", "forbidden_authority_claim:pr_delivery"),
            ("top-level-execution-ready", "rejected", "forbidden_authority_claim:execution_ready"),
            ("nested-pr-delivery", "rejected", "forbidden_authority_claim:pr_delivery"),
            ("unsafe-target", "rejected", "path_traversal:../requirement.md"),
            ("assurance-target", "rejected", "forbidden_canonical_target:requirement"),
            ("extra-canonical-target", "rejected", "unexpected_canonical_target:appendix"),
            ("canonical-doc-path", "rejected", "canonical_doc_path:drafts.requirement"),
            ("symlink-ancestor", "rejected", "symlink_entry:artifacts/linkdir/requirement-draft.md"),
        ),
    )
    def test_authoring_validate_issue_draft_adoption_negative_matrix(
        self, mutator: str, expected_status: str, expected_fragment: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_issue_draft_adoption_fixture(repo, mutator=mutator)

            payload = _run_issue_draft_adoption_json(self, repo, fixture)

            assert payload["status"] == expected_status
            assert expected_fragment in json.dumps(payload, sort_keys=True)

    def test_authoring_validate_issue_draft_adoption_detects_draft_digest_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_issue_draft_adoption_fixture(repo)

            payload = _run_issue_draft_adoption_json(
                self,
                repo,
                fixture,
                "--expected-draft-pack-digest",
                "wrong",
            )

            assert payload["status"] == "stale"
            assert "draft_pack_digest_mismatch" in payload["comparison"]

    def test_authoring_validate_issue_draft_adoption_binds_to_review_pack_digest_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_issue_draft_adoption_fixture(repo)
            Path(fixture["review_report"]).write_text(
                json.dumps(_evidence_review_report("pass", "different-pack"), sort_keys=True) + "\n",
                encoding="utf-8",
            )

            payload = _run_issue_draft_adoption_json(self, repo, fixture)

            assert payload["status"] == "stale"
            assert payload["expected_draft_pack_digest"] == "different-pack"
            assert payload["observed_draft_pack_digest"] == "draft-pack-hash"
            assert "draft_pack_digest_mismatch" in payload["comparison"]

    def test_authoring_validate_issue_draft_adoption_detects_source_hash_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_issue_draft_adoption_fixture(repo)

            payload = _run_issue_draft_adoption_json(
                self,
                repo,
                fixture,
                "--expected-source-hash",
                "wrong",
            )

            assert payload["status"] == "stale"
            assert "source_manifest_hash_mismatch" in payload["comparison"]

    @pytest.mark.parametrize(
        ("mutator", "expected_status", "expected_fragment"),
        (
            ("missing-input", "blocked", "missing_json:issue-draft-adoption"),
            ("malformed-input", "fail", "invalid_json:issue-draft-adoption"),
            ("non-object-input", "fail", "non_object_json:issue-draft-adoption"),
        ),
    )
    def test_authoring_validate_issue_draft_adoption_input_json_matrix(
        self, mutator: str, expected_status: str, expected_fragment: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_issue_draft_adoption_fixture(repo, mutator=mutator)

            payload = _run_issue_draft_adoption_json(self, repo, fixture)

            assert payload["status"] == expected_status
            assert expected_fragment in json.dumps(payload, sort_keys=True)

    @pytest.mark.parametrize(
        ("report_name", "expected_fragment"),
        (
            ("report.md", "unsafe_report_path:canonical-docs"),
            (".assurance.json", "unsafe_report_path:assurance"),
        ),
    )
    def test_authoring_validate_issue_draft_adoption_rejects_unsafe_report_path(
        self, report_name: str, expected_fragment: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_issue_draft_adoption_fixture(repo)
            report_path = Path(fixture["issue_dir"]) / report_name

            payload = _run_issue_draft_adoption_json(
                self,
                repo,
                fixture,
                "--report-path",
                str(report_path),
            )

            assert payload["status"] == "rejected"
            assert expected_fragment in payload["findings"]
            assert not report_path.exists()

    def test_authoring_validate_issue_draft_adoption_rejects_symlink_report_path(self) -> None:
        if not hasattr(os, "symlink"):
            pytest.skip("symlink unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_issue_draft_adoption_fixture(repo)
            outside = repo / "outside-report.json"
            outside.write_text("{}\n", encoding="utf-8")
            report_path = repo / ".specdock-authoring" / "issue-draft" / "symlink-report.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.symlink_to(outside)

            payload = _run_issue_draft_adoption_json(
                self,
                repo,
                fixture,
                "--report-path",
                str(report_path),
            )

            assert payload["status"] == "rejected"
            assert "unsafe_report_path:symlink" in payload["findings"]
            assert outside.read_text(encoding="utf-8") == "{}\n"

    def test_authoring_validate_issue_draft_adoption_writes_safe_noncanonical_report_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_issue_draft_adoption_fixture(repo)
            report_path = repo / ".specdock-authoring" / "issue-draft" / "validation-report.json"

            payload = _run_issue_draft_adoption_json(
                self,
                repo,
                fixture,
                "--report-path",
                str(report_path),
                expected_returncode=0,
            )

            report_payload = json.loads(report_path.read_text(encoding="utf-8"))
            assert payload["status"] == "pass"
            assert report_payload["status"] == "pass"
            assert report_payload["validation_kind"] == "issue-draft-adoption"

    def test_authoring_validate_issue_draft_adoption_blocks_missing_issue_node(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_issue_draft_adoption_fixture(repo, mutator="missing-issue-node")

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "issue-draft-adoption",
                    "--input",
                    str(fixture["input"]),
                    "--issue-dir",
                    str(fixture["issue_dir"]),
                    "--review-report",
                    str(fixture["review_report"]),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode != 0
            assert payload["status"] == "blocked"
            assert payload["findings"] == ["missing_issue_node"]
            assert payload["node_creation_performed"] is False

    def test_authoring_validate_issue_draft_adoption_blocks_missing_review_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_issue_draft_adoption_fixture(repo)
            missing_report = Path(fixture["review_report"]).with_name("missing-review-report.json")

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "issue-draft-adoption",
                    "--input",
                    str(fixture["input"]),
                    "--issue-dir",
                    str(fixture["issue_dir"]),
                    "--review-report",
                    str(missing_report),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode != 0
            assert payload["status"] == "blocked"
            assert payload["findings"] == ["missing_review_report"]

    def test_authoring_validate_issue_draft_adoption_rejects_authority_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_issue_draft_adoption_fixture(repo, mutator="forbidden-claim")

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "issue-draft-adoption",
                    "--input",
                    str(fixture["input"]),
                    "--issue-dir",
                    str(fixture["issue_dir"]),
                    "--review-report",
                    str(fixture["review_report"]),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode != 0
            assert payload["status"] == "rejected"
            assert "forbidden_authority_claim:canonical_written" in payload["findings"]

    def test_authoring_validate_issue_draft_adoption_text_output_rejects_authority_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_issue_draft_adoption_fixture(repo, mutator="forbidden-claim")

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "issue-draft-adoption",
                    "--input",
                    str(fixture["input"]),
                    "--issue-dir",
                    str(fixture["issue_dir"]),
                    "--review-report",
                    str(fixture["review_report"]),
                ],
            )

            assert p.returncode != 0
            _assert_text_output_preserves_draft_validation_boundary(p.stdout)
            assert "status=rejected" in p.stdout
            assert "forbidden_authority_claim:canonical_written" in p.stdout

    def test_authoring_validate_selected_skeleton_fill_valid_payload_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_selected_skeleton_fixture(repo)

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "selected-skeleton-fill",
                    "--input",
                    str(fixture["input"]),
                    "--issue-dir",
                    str(fixture["issue_dir"]),
                    "--assurance",
                    str(fixture["assurance"]),
                    "--selected-skeleton",
                    str(fixture["selected_skeleton"]),
                    "--review-report",
                    str(fixture["review_report"]),
                    "--expected-profile",
                    "standard",
                    "--expected-source-hash",
                    "source-hash",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert payload["validation_kind"] == "selected-skeleton-fill"
            assert payload["observed_profile"] == "standard"
            assert payload["expected_source_manifest_hash"] == "source-hash"
            assert payload["observed_source_manifest_hash"] == "source-hash"
            assert payload["section_count"] == 3
            assert payload["valid_section_count"] == 3
            assert payload["canonical_written"] is False
            assert payload["assurance_mutated"] is False
            assert payload["execution_ready"] is False

    def test_authoring_validate_selected_skeleton_fill_text_output_valid_payload_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_selected_skeleton_fixture(repo)

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "selected-skeleton-fill",
                    "--input",
                    str(fixture["input"]),
                    "--issue-dir",
                    str(fixture["issue_dir"]),
                    "--assurance",
                    str(fixture["assurance"]),
                    "--selected-skeleton",
                    str(fixture["selected_skeleton"]),
                    "--review-report",
                    str(fixture["review_report"]),
                    "--expected-profile",
                    "standard",
                    "--expected-source-hash",
                    "source-hash",
                ],
            )

            assert p.returncode == 0, p.stdout + p.stderr
            _assert_text_output_preserves_draft_validation_boundary(p.stdout)
            assert "status=pass" in p.stdout
            assert "authoring validate selected-skeleton-fill" in p.stdout
            assert "section_count=3" in p.stdout
            assert "valid_section_count=3" in p.stdout

    def test_authoring_validate_selected_skeleton_fill_rejects_secret_section_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_selected_skeleton_fixture(repo, mutator="secret-path")

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "selected-skeleton-fill",
                    "--input",
                    str(fixture["input"]),
                    "--issue-dir",
                    str(fixture["issue_dir"]),
                    "--assurance",
                    str(fixture["assurance"]),
                    "--selected-skeleton",
                    str(fixture["selected_skeleton"]),
                    "--review-report",
                    str(fixture["review_report"]),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode != 0
            assert payload["status"] == "rejected"
            assert "secret_path" in json.dumps(payload, sort_keys=True)

    def test_authoring_validate_selected_skeleton_fill_blocks_missing_issue_node(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_selected_skeleton_fixture(repo, mutator="missing-issue-node")

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "selected-skeleton-fill",
                    "--input",
                    str(fixture["input"]),
                    "--issue-dir",
                    str(fixture["issue_dir"]),
                    "--assurance",
                    str(fixture["assurance"]),
                    "--selected-skeleton",
                    str(fixture["selected_skeleton"]),
                    "--review-report",
                    str(fixture["review_report"]),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode != 0
            assert payload["status"] == "blocked"
            assert payload["findings"] == ["missing_issue_node"]

    def test_authoring_validate_selected_skeleton_fill_detects_section_hash_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_selected_skeleton_fixture(repo, mutator="section-hash-mismatch")

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "selected-skeleton-fill",
                    "--input",
                    str(fixture["input"]),
                    "--issue-dir",
                    str(fixture["issue_dir"]),
                    "--assurance",
                    str(fixture["assurance"]),
                    "--selected-skeleton",
                    str(fixture["selected_skeleton"]),
                    "--review-report",
                    str(fixture["review_report"]),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode != 0
            assert payload["status"] == "stale"
            assert "section_sha256_mismatch:requirement" in payload["comparison"]

    def test_authoring_validate_selected_skeleton_fill_detects_source_hash_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_selected_skeleton_fixture(repo)

            payload = _run_selected_skeleton_fill_json(
                self,
                repo,
                fixture,
                "--expected-source-hash",
                "wrong",
            )

            assert payload["status"] == "stale"
            assert "source_manifest_hash_mismatch" in payload["comparison"]
            assert payload["expected_source_manifest_hash"] == "wrong"
            assert payload["observed_source_manifest_hash"] == "source-hash"

    @pytest.mark.parametrize(
        ("mutator", "expected_status", "expected_fragment"),
        (
            ("missing-input", "blocked", "missing_json:selected-skeleton-fill"),
            ("malformed-input", "fail", "invalid_json:selected-skeleton-fill"),
            ("missing-assurance", "blocked", "missing_json:assurance"),
            ("invalid-assurance", "fail", "invalid_json:assurance"),
            ("missing-selected-skeleton", "blocked", "missing_json:selected-skeleton"),
            ("invalid-selected-skeleton", "fail", "invalid_json:selected-skeleton"),
        ),
    )
    def test_authoring_validate_selected_skeleton_fill_prerequisite_json_matrix(
        self, mutator: str, expected_status: str, expected_fragment: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_selected_skeleton_fixture(repo, mutator=mutator)

            payload = _run_selected_skeleton_fill_json(self, repo, fixture, "--expected-profile", "standard")

            assert payload["status"] == expected_status
            assert expected_fragment in json.dumps(payload, sort_keys=True)

    @pytest.mark.parametrize(
        ("mutator", "expected_status", "expected_fragment"),
        (
            ("missing-section", "fail", "missing_section_fill:plan"),
            ("extra-section", "fail", "extra_section_fill:extra"),
            ("duplicate-section", "fail", "duplicate_section_fill:requirement"),
            ("empty-inventory", "fail", "selected_skeleton.required_sections"),
            ("selected-profile-mismatch", "stale", "selected_profile_mismatch"),
            ("assurance-profile-mismatch", "stale", "selected_profile_assurance_mismatch"),
            ("forbidden-claim", "rejected", "forbidden_authority_claim:execution_ready"),
            ("merge-ready-claim", "rejected", "forbidden_authority_claim:merge_ready"),
            ("pr-delivery-claim", "rejected", "forbidden_authority_claim:pr_delivery"),
            ("top-level-execution-ready", "rejected", "forbidden_authority_claim:execution_ready"),
            ("nested-pr-delivery", "rejected", "forbidden_authority_claim:pr_delivery"),
            ("missing-draft-pack-digest", "fail", "missing_or_invalid_field:draft_pack_digest"),
            ("draft-pack-digest-mismatch", "stale", "draft_pack_digest_mismatch"),
            ("canonical-doc-path", "rejected", "canonical_doc_path:section_fills.requirement"),
            ("symlink-ancestor", "rejected", "symlink_entry:artifacts/linkdir/requirement-fill.md"),
            ("missing-template-hash", "fail", "missing_or_invalid_field:template_hash"),
            (
                "missing-selected-skeleton-hash",
                "fail",
                "missing_or_invalid_field:selected_skeleton.selected_skeleton_hash",
            ),
            ("missing-section-sha", "fail", "missing_or_invalid_field:section_fills.requirement.sha256"),
            ("template-hash-mismatch", "stale", "template_hash_mismatch"),
            ("selected-skeleton-hash-mismatch", "stale", "selected_skeleton_hash_mismatch"),
        ),
    )
    def test_authoring_validate_selected_skeleton_fill_negative_matrix(
        self, mutator: str, expected_status: str, expected_fragment: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_selected_skeleton_fixture(repo, mutator=mutator)

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "validate",
                    "selected-skeleton-fill",
                    "--input",
                    str(fixture["input"]),
                    "--issue-dir",
                    str(fixture["issue_dir"]),
                    "--assurance",
                    str(fixture["assurance"]),
                    "--selected-skeleton",
                    str(fixture["selected_skeleton"]),
                    "--review-report",
                    str(fixture["review_report"]),
                    "--expected-profile",
                    "standard",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode != 0
            assert payload["status"] == expected_status
            assert expected_fragment in json.dumps(payload, sort_keys=True)

    def test_authoring_validate_selected_skeleton_fill_binds_to_reviewed_pack_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_selected_skeleton_fixture(repo)
            Path(fixture["review_report"]).write_text(
                json.dumps(_evidence_review_report("pass", "unrelated-pack"), sort_keys=True) + "\n",
                encoding="utf-8",
            )

            payload = _run_selected_skeleton_fill_json(self, repo, fixture, "--expected-profile", "standard")

            assert payload["status"] == "stale"
            assert payload["review_gate_passed"] is False
            assert payload["expected_draft_pack_digest"] == "unrelated-pack"
            assert payload["observed_draft_pack_digest"] == "selected-pack-hash"
            assert "draft_pack_digest_mismatch" in payload["comparison"]

    def test_authoring_validate_selected_skeleton_fill_rejects_review_report_authority_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_selected_skeleton_fixture(repo)
            report = _evidence_review_report("pass", "selected-pack-hash")
            report["bundle_generation_not_promotion"] = False
            Path(fixture["review_report"]).write_text(json.dumps(report, sort_keys=True) + "\n", encoding="utf-8")

            payload = _run_selected_skeleton_fill_json(self, repo, fixture, "--expected-profile", "standard")

            assert payload["status"] == "rejected"
            assert payload["review_gate_passed"] is False
            assert "review_report_bundle_generation_not_promotion_not_true" in payload["findings"]

    def test_authoring_validate_selected_skeleton_fill_rejects_symlink_report_path(self) -> None:
        if not hasattr(os, "symlink"):
            pytest.skip("symlink unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            fixture = _write_selected_skeleton_fixture(repo)
            outside = repo / "outside-report.json"
            outside.write_text("{}\n", encoding="utf-8")
            report_path = repo / ".specdock-authoring" / "selected" / "symlink-report.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.symlink_to(outside)

            payload = _run_selected_skeleton_fill_json(
                self,
                repo,
                fixture,
                "--report-path",
                str(report_path),
            )

            assert payload["status"] == "rejected"
            assert "unsafe_report_path:symlink" in payload["findings"]
            assert outside.read_text(encoding="utf-8") == "{}\n"

    def test_authoring_provider_and_dogfood_wrapper_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            assert main(["init", str(repo)]) == 0
            repo_root = Path(__file__).resolve().parents[2]
            wrapper_roots = (
                repo_root / "src/spec_dock/assets/spec_dock/scripts/authoring-pack",
                repo_root / "spec-dock/scripts/authoring-pack",
                repo / "spec-dock/scripts/authoring-pack",
            )
            issue_fixture = _write_issue_draft_adoption_fixture(repo)
            fixture = _write_selected_skeleton_fixture(repo)
            selected_payloads = []
            issue_payloads = []
            for index, wrapper_root in enumerate(wrapper_roots):
                issue_wrapper = wrapper_root / "validate_issue_draft_adoption.py"
                selected_wrapper = wrapper_root / "validate_selected_skeleton_fill.py"
                issue_candidates_wrapper = wrapper_root / "validate_issue_candidates.py"
                initiative_candidates_wrapper = wrapper_root / "validate_initiative_epic_candidates.py"
                selected_report = repo / ".specdock-authoring" / f"selected-wrapper-report-{index}.json"
                issue_report = repo / ".specdock-authoring" / f"issue-wrapper-report-{index}.json"
                issue_help = subprocess.run(
                    [sys.executable, str(issue_wrapper), "--help"],
                    cwd=str(repo),
                    env=self._runtime_env(repo, {"PATH": os.environ.get("PATH", ""), "PYTHONDONTWRITEBYTECODE": "1"}),
                    capture_output=True,
                    text=True,
                )
                selected_help = subprocess.run(
                    [sys.executable, str(selected_wrapper), "--help"],
                    cwd=str(repo / "spec-dock"),
                    env=self._runtime_env(repo, {"PATH": os.environ.get("PATH", ""), "PYTHONDONTWRITEBYTECODE": "1"}),
                    capture_output=True,
                    text=True,
                )
                issue_candidates_help = subprocess.run(
                    [sys.executable, str(issue_candidates_wrapper), "--help"],
                    cwd=str(repo),
                    env=self._runtime_env(repo, {"PATH": os.environ.get("PATH", ""), "PYTHONDONTWRITEBYTECODE": "1"}),
                    capture_output=True,
                    text=True,
                )
                initiative_candidates_help = subprocess.run(
                    [sys.executable, str(initiative_candidates_wrapper), "--help"],
                    cwd=str(repo),
                    env=self._runtime_env(repo, {"PATH": os.environ.get("PATH", ""), "PYTHONDONTWRITEBYTECODE": "1"}),
                    capture_output=True,
                    text=True,
                )
                issue_run = subprocess.run(
                    [
                        sys.executable,
                        str(issue_wrapper),
                        "--input",
                        str(issue_fixture["input"]),
                        "--issue-dir",
                        str(issue_fixture["issue_dir"]),
                        "--review-report",
                        str(issue_fixture["review_report"]),
                        "--report-path",
                        str(issue_report),
                        "--format",
                        "json",
                    ],
                    cwd=str(repo),
                    env=self._runtime_env(repo, {"PATH": os.environ.get("PATH", ""), "PYTHONDONTWRITEBYTECODE": "1"}),
                    capture_output=True,
                    text=True,
                )
                selected_run = subprocess.run(
                    [
                        sys.executable,
                        str(selected_wrapper),
                        "--input",
                        str(fixture["input"]),
                        "--issue-dir",
                        str(fixture["issue_dir"]),
                        "--assurance",
                        str(fixture["assurance"]),
                        "--selected-skeleton",
                        str(fixture["selected_skeleton"]),
                        "--review-report",
                        str(fixture["review_report"]),
                        "--report-path",
                        str(selected_report),
                        "--format",
                        "json",
                    ],
                    cwd=str(repo),
                    env=self._runtime_env(repo, {"PATH": os.environ.get("PATH", ""), "PYTHONDONTWRITEBYTECODE": "1"}),
                    capture_output=True,
                    text=True,
                )

                assert issue_help.returncode == 0, issue_help.stdout + issue_help.stderr
                assert "issue-draft-adoption" in issue_help.stdout
                assert "--review-report" in issue_help.stdout
                assert "--pack-tree" not in issue_help.stdout
                assert "--output-dir" not in issue_help.stdout
                assert issue_candidates_help.returncode == 0, (
                    issue_candidates_help.stdout + issue_candidates_help.stderr
                )
                assert "--expected-parent-epic" in issue_candidates_help.stdout
                assert initiative_candidates_help.returncode == 0, (
                    initiative_candidates_help.stdout + initiative_candidates_help.stderr
                )
                assert "--expected-parent-initiative" in initiative_candidates_help.stdout
                assert selected_help.returncode == 0, selected_help.stdout + selected_help.stderr
                assert "--input" in selected_help.stdout
                assert "--issue-dir" in selected_help.stdout
                assert "--selected-skeleton" in selected_help.stdout
                assert "--review-report" in selected_help.stdout
                assert "--pack-tree" not in selected_help.stdout
                assert "--output-dir" not in selected_help.stdout
                issue_payload = json.loads(issue_run.stdout)
                selected_payload = json.loads(selected_run.stdout)
                assert issue_run.returncode == 0, issue_run.stdout + issue_run.stderr
                assert selected_run.returncode == 0, selected_run.stdout + selected_run.stderr
                assert issue_payload["validation_kind"] == "issue-draft-adoption"
                assert selected_payload["validation_kind"] == "selected-skeleton-fill"
                assert issue_payload["status"] == "pass"
                assert selected_payload["status"] == "pass"
                assert issue_report.is_file()
                assert selected_report.is_file()
                issue_payloads.append(issue_payload)
                selected_payloads.append(selected_payload)

            assert {payload["validation_kind"] for payload in issue_payloads} == {"issue-draft-adoption"}
            assert {payload["validation_kind"] for payload in selected_payloads} == {"selected-skeleton-fill"}

    @pytest.mark.parametrize(("args", "command", "next_issue"), _DEFERRED_COMMANDS)
    def test_authoring_deferred_commands_fail_closed_with_stable_diagnostics(
        self, args: list[str], command: str, next_issue: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(target, args)

            assert p.returncode != 0, p.stdout + p.stderr
            assert f"spec-dock: deferred (authoring) command={command}" in p.stdout
            assert "status=deferred" in p.stdout
            assert "authority=evidence_only" in p.stdout
            assert f"next_issue={next_issue}" in p.stdout
            assert "reason=not_implemented_in_this_issue" in p.stdout

            output = (p.stdout + p.stderr).lower()
            for forbidden in _FORBIDDEN_AUTHORITY_CLAIMS:
                assert forbidden not in output

    def test_authoring_pack_review_valid_zip_passes_with_evidence_only_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(pack_zip), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert payload["authority"] == "evidence_only"
            assert payload["adoption_status"] == "unreviewed"
            assert payload["bundle_generation_not_promotion"] is True
            assert payload["input_kind"] == "zip"
            assert payload["fallback"] is False

    def test_authoring_pack_review_accepts_prepare_contract_without_manifest_source_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            manifest = _base_authoring_pack_manifest()
            manifest.pop("source_manifest_hash", None)
            pack_zip = _write_authoring_pack_zip(
                repo / "prepare-contract.zip",
                metadata_overrides={
                    "manifest.json": json.dumps(manifest, sort_keys=True) + "\n",
                    "stale-if.json": json.dumps({"source_manifest_hash_changes": "hash"}, sort_keys=True) + "\n",
                },
            )

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(pack_zip), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"

    def test_authoring_pack_review_does_not_treat_constraint_text_as_authority_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(
                repo / "constraints.zip",
                metadata_overrides={
                    "safe-output-constraints.md": (
                        "Do not claim reviewer pass, PR-ready, or PR delivery.\n"
                        "Forbidden payloads include credential, private key, token, and secret material.\n"
                        "Policy labels may mention api key: without a value.\n"
                    )
                },
            )

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(pack_zip), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"

    def test_authoring_pack_review_rejects_sensitive_constraint_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(
                repo / "constraint-secret.zip",
                metadata_overrides={
                    "safe-output-constraints.md": (
                        "Do not leak token=SHOULD_REJECT, api key: sk-live-example, "
                        "private_key: abcdefgh, or raw transcript text.\n"
                    )
                },
            )

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(pack_zip), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "secret_like_payload:token" in payload["findings"]
            assert "secret_like_payload:api_key" in payload["findings"]
            assert "secret_like_payload:private key" in payload["findings"]
            assert "raw_transcript:raw transcript" in payload["findings"]

    def test_authoring_pack_review_redacts_sensitive_findings_in_report_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            report_path = repo / ".specdock-authoring" / "review-report.json"
            pack_zip = _write_authoring_pack_zip(
                repo / "report-secret.zip",
                metadata_overrides={
                    "drafts/issue/iss-00301/requirement.md": (
                        "token=SHOULD_NOT_APPEAR\nprivate_key: abcdefgh\nraw transcript: browser text\n"
                    )
                },
            )

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "review",
                    "--input",
                    str(pack_zip),
                    "--report-path",
                    str(report_path),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            report_text = report_path.read_text(encoding="utf-8")
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "secret_like_payload:token" in report_text
            assert "secret_like_payload:private key" in report_text
            assert "raw_transcript:raw transcript" in report_text
            assert "SHOULD_NOT_APPEAR" not in report_text
            assert "abcdefgh" not in report_text
            assert "browser text" not in report_text

    def test_authoring_pack_review_writes_json_report_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            report_path = repo / ".specdock-authoring" / "review" / "review-report.json"

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "review",
                    "--input",
                    str(pack_zip),
                    "--report-path",
                    str(report_path),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            report_payload = json.loads(report_path.read_text(encoding="utf-8"))
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert report_payload["status"] == "pass"
            assert report_payload["authority"] == "evidence_only"

    def test_authoring_pack_review_report_preserves_local_context_evidence_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            report_path = repo / ".specdock-authoring" / "review" / "local-context-report.json"

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "review",
                    "--input",
                    str(pack_zip),
                    "--evidence-mode",
                    "local-context",
                    "--report-path",
                    str(report_path),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            report_payload = json.loads(report_path.read_text(encoding="utf-8"))
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["evidence_mode"] == "local-context"
            assert report_payload["evidence_mode"] == "local-context"
            assert report_payload["pack_digest"]["content_sha256"]

    def test_authoring_pack_review_derives_evidence_mode_from_pack_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            provenance = {
                "evidence_mode": "local-context",
                "sync_state": "local_context",
                "github_sync": "not_verified",
                "provided_context_paths": ["source.txt"],
                "unsynced_reason": "test local-context evidence",
                "source_manifest_hash": "hash",
                "authority": "evidence_only",
                "adoption_status": "unreviewed",
                "bundle_generation_not_promotion": True,
            }
            pack_zip = _write_authoring_pack_zip(
                repo / "local-context.zip",
                metadata_overrides={"provenance.json": json.dumps(provenance, sort_keys=True) + "\n"},
            )

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(pack_zip), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["evidence_mode"] == "local-context"

    @pytest.mark.parametrize("input_kind", ("zip", "tree"))
    def test_authoring_pack_review_rejects_semantically_inconsistent_provenance(self, input_kind: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            provenance = {
                "evidence_mode": "github-synced",
                "sync_state": "blocked",
                "github_sync": "failed",
                "source_manifest_hash": "hash",
                "authority": "evidence_only",
                "adoption_status": "unreviewed",
                "bundle_generation_not_promotion": True,
            }
            if input_kind == "zip":
                input_path = _write_authoring_pack_zip(
                    repo / "inconsistent.zip",
                    metadata_overrides={"provenance.json": json.dumps(provenance, sort_keys=True) + "\n"},
                )
            else:
                input_path = _write_authoring_pack_tree(repo / "inconsistent-tree")
                (input_path / "specdock-authoring-pack" / "provenance.json").write_text(
                    json.dumps(provenance, sort_keys=True) + "\n", encoding="utf-8"
                )

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(input_path), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1
            assert payload["status"] == "rejected"
            assert "provenance_github_sync_not_verified" in payload["findings"]
            assert "provenance_sync_state_not_synced" in payload["findings"]
            assert payload["pack_digest"]["content_sha256"] is None

    def test_authoring_pack_review_text_preserves_local_context_evidence_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "review",
                    "--input",
                    str(pack_zip),
                    "--evidence-mode",
                    "local-context",
                ],
            )

            assert p.returncode == 0, p.stdout + p.stderr
            assert "evidence_mode=local-context" in p.stdout

    def test_authoring_pack_review_rejects_unsafe_zip_without_extracting(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            sentinel = repo.parent / "escaped.txt"
            pack_zip = _write_authoring_pack_zip(
                repo / "unsafe.zip",
                extra_entries={"specdock-authoring-pack/../../escaped.txt": "escape\n"},
            )

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(pack_zip), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert any("path_traversal" in finding for finding in payload["findings"])
            assert not sentinel.exists()

    @pytest.mark.parametrize(
        ("variant", "expected_status", "expected_finding"),
        (
            ("wrong-root", "rejected", "wrong_root"),
            ("missing-metadata", "fail", "missing_metadata:manifest.json"),
            ("source-hash-mismatch", "stale", "source_hash_mismatch"),
            ("invalid-authority", "rejected", "invalid_authority"),
            ("invalid-adoption-status", "rejected", "invalid_adoption_status"),
            (
                "invalid-bundle-generation-not-promotion",
                "rejected",
                "invalid_bundle_generation_not_promotion",
            ),
        ),
    )
    def test_authoring_pack_review_classifies_root_metadata_and_hash_failures(
        self, variant: str, expected_status: str, expected_finding: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / f"{variant}.zip", variant=variant)

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(pack_zip), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == expected_status
            assert expected_finding in payload["findings"]

    @pytest.mark.parametrize(
        "metadata_path",
        (
            "manifest.json",
            "source-manifest.json",
            "provenance.json",
            "stale-if.json",
            "adoption/adoption-map.json",
            "adoption/eal-candidates.json",
        ),
    )
    def test_authoring_pack_review_fails_for_invalid_required_json_metadata(self, metadata_path: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(
                repo / "invalid-json.zip",
                metadata_overrides={metadata_path: "{invalid json"},
            )

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(pack_zip), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "fail"
            assert f"invalid_json:{metadata_path}" in payload["findings"]

    def test_authoring_pack_review_rejects_unsafe_report_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            report_path = (
                repo
                / "spec-dock"
                / "initiatives"
                / "init-local-00001"
                / "epics"
                / "epic-00001"
                / "issues"
                / "iss-00001"
                / ".assurance.json"
            )

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "review",
                    "--input",
                    str(pack_zip),
                    "--report-path",
                    str(report_path),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_report_path:assurance" in payload["findings"]
            assert not report_path.exists()

    def test_authoring_pack_review_rejects_canonical_report_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            report_path = (
                repo
                / "spec-dock"
                / "initiatives"
                / "init-local-00001"
                / "epics"
                / "epic-00001"
                / "issues"
                / "iss-00001"
                / "artifacts"
                / "review-report.json"
            )

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "review",
                    "--input",
                    str(pack_zip),
                    "--report-path",
                    str(report_path),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_report_path:canonical-docs" in payload["findings"]
            assert not report_path.exists()

    def test_authoring_pack_review_rejects_relative_canonical_report_path_from_specdock_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            specdock_cwd = repo / "spec-dock"
            report_path = Path("active") / "issue" / "review-report.json"

            p = _run_authoring_capture_from_cwd(
                self,
                repo,
                specdock_cwd,
                [
                    "authoring",
                    "pack",
                    "review",
                    "--input",
                    str(pack_zip),
                    "--report-path",
                    str(report_path),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_report_path:canonical-docs" in payload["findings"]
            assert not (specdock_cwd / report_path).exists()

    def test_authoring_pack_review_rejects_symlink_parent_report_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            outside = repo / "outside"
            outside.mkdir()
            link_dir = repo / ".specdock-authoring" / "review-link"
            link_dir.parent.mkdir(parents=True)
            link_dir.symlink_to(outside)
            report_path = link_dir / "review-report.json"

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "review",
                    "--input",
                    str(pack_zip),
                    "--report-path",
                    str(report_path),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_report_path:symlink" in payload["findings"]
            assert not (outside / "review-report.json").exists()

    def test_authoring_pack_review_rejects_nested_symlink_ancestor_report_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            outside = repo / "outside"
            nested = outside / "existing"
            nested.mkdir(parents=True)
            link_dir = repo / ".specdock-authoring" / "review-link"
            link_dir.parent.mkdir(parents=True)
            link_dir.symlink_to(outside)
            report_path = link_dir / "existing" / "review-report.json"

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "review",
                    "--input",
                    str(pack_zip),
                    "--report-path",
                    str(report_path),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_report_path:symlink" in payload["findings"]
            assert not (nested / "review-report.json").exists()

    def test_authoring_pack_review_rejects_symlink_ancestor_to_external_report_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = _create_synced_git_repo(base)
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            external = base / "external"
            nested = external / "existing"
            nested.mkdir(parents=True)
            link_dir = repo / ".specdock-authoring" / "external-link"
            link_dir.parent.mkdir(parents=True)
            link_dir.symlink_to(external)
            report_path = link_dir / "existing" / "review-report.json"

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "review",
                    "--input",
                    str(pack_zip),
                    "--report-path",
                    str(report_path),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_report_path:symlink" in payload["findings"]
            assert not (nested / "review-report.json").exists()

    def test_authoring_pack_review_rejected_findings_take_precedence_over_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(
                repo / "stale-and-rejected.zip",
                variant="source-hash-mismatch",
                extra_entries={"specdock-authoring-pack/issue/claim.md": "PR delivery complete\n"},
            )

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(pack_zip), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "source_hash_mismatch" in payload["findings"]
            assert "forbidden_authority_claim:pr delivery" in payload["findings"]

    @pytest.mark.parametrize(
        ("case_name", "entry_name", "entry_payload", "expected_finding"),
        (
            (
                "absolute-path",
                "specdock-authoring-pack//Users/alice/draft.md",
                "x\n",
                "path_traversal:/Users/alice/draft.md",
            ),
            (
                "host-local-path",
                "specdock-authoring-pack/Users/alice/draft.md",
                "x\n",
                "host_local_path:Users/alice/draft.md",
            ),
            ("hidden-path", "specdock-authoring-pack/.hidden.md", "x\n", "hidden_path:.hidden.md"),
            ("secret-path", "specdock-authoring-pack/secrets/token.md", "x\n", "secret_path:secrets/token.md"),
            (
                "windows-backslash-traversal",
                "specdock-authoring-pack/safe\\..\\..\\evil.md",
                "x\n",
                "path_separator_backslash:safe\\..\\..\\evil.md",
            ),
            (
                "windows-drive-path",
                "specdock-authoring-pack/C:/Users/alice/evil.md",
                "x\n",
                "host_local_path:C:/Users/alice/evil.md",
            ),
            ("unsupported-suffix", "specdock-authoring-pack/issue/run.sh", "x\n", "unsupported_suffix:issue/run.sh"),
            (
                "binary-payload",
                "specdock-authoring-pack/issue/binary.md",
                b"\xff\xfe",
                "binary_payload:issue/binary.md",
            ),
            ("nested-archive", "specdock-authoring-pack/issue/archive.zip", "x\n", "nested_archive:issue/archive.zip"),
        ),
    )
    def test_authoring_pack_review_rejects_unsafe_zip_entry_categories(
        self, case_name: str, entry_name: str, entry_payload: str | bytes, expected_finding: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(
                repo / f"{case_name}.zip",
                extra_entries={entry_name: entry_payload},
            )

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(pack_zip), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert expected_finding in payload["findings"]

    def test_authoring_pack_review_rejects_authority_claims_in_required_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(
                repo / "adopted-metadata.zip",
                metadata_overrides={
                    "adoption/eal-candidates.json": json.dumps(
                        {"candidates": [], "authority": "canonical", "adoption_status": "adopted"},
                        sort_keys=True,
                    )
                    + "\n"
                },
            )

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(pack_zip), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "invalid_authority:adoption/eal-candidates.json" in payload["findings"]
            assert "invalid_adoption_status:adoption/eal-candidates.json" in payload["findings"]

    def test_authoring_pack_review_rejects_executable_zip_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            executable_info = zipfile.ZipInfo("specdock-authoring-pack/issue/executable.md")
            executable_info.external_attr = 0o100755 << 16
            pack_zip = _write_authoring_pack_zip(repo / "executable.zip", extra_infos=[(executable_info, "x\n")])

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(pack_zip), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "executable_entry:issue/executable.md" in payload["findings"]

    def test_authoring_pack_review_rejects_oversized_zip_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(
                repo / "oversized.zip",
                extra_entries={"specdock-authoring-pack/issue/large.md": "x" * 2_000_001},
            )

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(pack_zip), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "oversized_entry:issue/large.md" in payload["findings"]

    def test_authoring_pack_review_rejects_oversized_zip_total(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(
                repo / "oversized-total.zip",
                extra_entries={
                    f"specdock-authoring-pack/issue/large-{index}.md": "x" * 1_900_000 for index in range(6)
                },
            )

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(pack_zip), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "oversized_total" in payload["findings"]

    def test_authoring_pack_review_rejects_symlink_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            symlink_info = zipfile.ZipInfo("specdock-authoring-pack/issue/link.md")
            symlink_info.external_attr = 0o120777 << 16
            pack_zip = _write_authoring_pack_zip(repo / "symlink.zip", extra_infos=[(symlink_info, "target")])

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(pack_zip), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "symlink_entry:issue/link.md" in payload["findings"]

    def test_authoring_pack_review_rejects_encrypted_entry_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            encrypted_name = "specdock-authoring-pack/issue/encrypted.md"
            pack_zip = _write_authoring_pack_zip(
                repo / "encrypted.zip",
                extra_entries={encrypted_name: "encrypted-looking\n"},
            )
            _mark_zip_entry_encrypted(pack_zip, encrypted_name)

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(pack_zip), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "encrypted_entry:issue/encrypted.md" in payload["findings"]

    def test_authoring_pack_review_rejects_forbidden_authority_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(
                repo / "forbidden.zip",
                extra_entries={"specdock-authoring-pack/issue/plan.md": "reviewer pass and PR-ready\n"},
            )

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(pack_zip), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "forbidden_authority_claim:reviewer pass" in payload["findings"]

    @pytest.mark.parametrize(
        ("claim_text", "expected_finding"),
        (
            ("canonical adoption complete\n", "forbidden_authority_claim:canonical adoption"),
            (".assurance.json mutation complete\n", "forbidden_authority_claim:.assurance.json mutation"),
            ("authorized_profile decision complete\n", "forbidden_authority_claim:authorized_profile decision"),
            ("reviewer pass complete\n", "forbidden_authority_claim:reviewer pass"),
            ("execution-ready complete\n", "forbidden_authority_claim:execution-ready"),
            ("PR-ready complete\n", "forbidden_authority_claim:pr-ready"),
            ("PR delivery complete\n", "forbidden_authority_claim:pr delivery"),
            ("mergeable PR complete\n", "forbidden_authority_claim:mergeable pr"),
        ),
    )
    def test_authoring_pack_review_rejects_forbidden_authority_claim_contract(
        self, claim_text: str, expected_finding: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(
                repo / "forbidden-contract.zip",
                extra_entries={"specdock-authoring-pack/issue/claim.md": claim_text},
            )

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(pack_zip), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert expected_finding in payload["findings"]

    @pytest.mark.parametrize(
        ("case_name", "payload_text", "expected_finding"),
        (
            ("token", "token=abc123\n", "secret_like_payload:token"),
            ("json-token", '{"token": "abc123"}\n', "secret_like_payload:token"),
            ("yaml-secret", "secret: abc123\n", "secret_like_payload:secret"),
            ("json-api-key", '{"api_key": "abc123"}\n', "secret_like_payload:api_key"),
            ("credential", "credential material\n", "secret_like_payload:credential"),
            ("private-key", "private key block\n", "secret_like_payload:private key"),
            ("raw-transcript", "raw transcript from browser\n", "raw_transcript:raw transcript"),
        ),
    )
    def test_authoring_pack_review_rejects_secret_and_raw_transcript_payloads(
        self, case_name: str, payload_text: str, expected_finding: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(
                repo / f"{case_name}.zip",
                extra_entries={"specdock-authoring-pack/issue/notes.md": payload_text},
            )

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(pack_zip), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert expected_finding in payload["findings"]

    def test_authoring_pack_review_tree_fallback_reports_lower_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            tree = _write_authoring_pack_tree(repo / "tree-pack")

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(tree), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert payload["input_kind"] == "tree"
            assert payload["fallback"] is True
            assert payload["authority_level"] == "lower_than_zip_review"
            assert payload["missing_evidence"] == ["zip-central-directory"]

    def test_authoring_pack_review_tree_fallback_rejects_symlink_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            tree = _write_authoring_pack_tree(repo / "tree-pack")
            external = repo / "external.md"
            external.write_text("external host-local content\n", encoding="utf-8")
            symlink_path = tree / "specdock-authoring-pack" / "issue" / "symlink.md"
            symlink_path.symlink_to(external)

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(tree), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "symlink_entry:issue/symlink.md" in payload["findings"]

    def test_authoring_pack_review_tree_fallback_rejects_executable_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            tree = _write_authoring_pack_tree(repo / "tree-pack")
            executable_path = tree / "specdock-authoring-pack" / "issue" / "executable.md"
            executable_path.write_text("x\n", encoding="utf-8")
            executable_path.chmod(0o755)

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(tree), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "executable_entry:issue/executable.md" in payload["findings"]

    def test_authoring_pack_review_rejects_symlinked_tree_input_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            tree = _write_authoring_pack_tree(repo / "real-tree")
            tree_link = repo / "tree-link"
            tree_link.symlink_to(tree)

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(tree_link), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "symlink_input_root" in payload["findings"]

    @pytest.mark.parametrize(
        ("case_name", "rel_path", "payload_value", "expected_finding"),
        (
            ("unsupported", "issue/tool.sh", "x\n", "unsupported_suffix:issue/tool.sh"),
            ("nested", "issue/archive.zip", "x\n", "nested_archive:issue/archive.zip"),
            ("binary", "issue/binary.md", b"\xff\xfe", "binary_payload:issue/binary.md"),
            ("oversized", "issue/large.md", "x" * 2_000_001, "oversized_entry:issue/large.md"),
        ),
        ids=("unsupported", "nested", "binary", "oversized"),
    )
    def test_authoring_pack_review_tree_fallback_rejects_unsafe_file_categories(
        self, case_name: str, rel_path: str, payload_value: str | bytes, expected_finding: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            tree = _write_authoring_pack_tree(repo / f"tree-{case_name}")
            unsafe_path = tree / "specdock-authoring-pack" / rel_path
            unsafe_path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(payload_value, bytes):
                unsafe_path.write_bytes(payload_value)
            else:
                unsafe_path.write_text(payload_value, encoding="utf-8")

            p = _run_authoring_capture(
                self,
                repo,
                ["authoring", "pack", "review", "--input", str(tree), "--format", "json"],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert expected_finding in payload["findings"]

    def test_authoring_pack_stage_valid_zip_writes_stage_outputs_and_preserves_canonical_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            candidate_payload = {"candidates": [{"source": "issue/requirement.md", "target": "issue.requirement"}]}
            pack_zip = _write_authoring_pack_zip(
                repo / "valid.zip",
                metadata_overrides={
                    "issue/requirement.md": "# Draft requirement\n\ncontent-sensitive-stage-evidence\n",
                    "adoption/eal-candidates.json": json.dumps(candidate_payload, sort_keys=True) + "\n",
                },
            )
            stage_dir = repo / ".specdock-authoring" / "staged" / "valid"
            protected_before = _protected_specdock_snapshot(repo)

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "stage",
                    "--input",
                    str(pack_zip),
                    "--stage-dir",
                    str(stage_dir),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert (stage_dir / "review-report.json").is_file()
            assert (stage_dir / "dry-run-diff.md").is_file()
            assert (stage_dir / "adoption" / "eal-candidates.json").is_file()
            assert (stage_dir / ".specdock-stage-owner.json").is_file()
            assert (stage_dir / "specdock-authoring-pack" / "manifest.json").is_file()
            dry_run_diff = (stage_dir / "dry-run-diff.md").read_text(encoding="utf-8")
            staged_candidates = json.loads((stage_dir / "adoption" / "eal-candidates.json").read_text(encoding="utf-8"))
            assert "issue/requirement.md" in dry_run_diff
            assert "content-sensitive-stage-evidence" in dry_run_diff
            assert staged_candidates == candidate_payload
            assert "specdock-authoring-pack/manifest.json" in payload["staged_files"]
            owner = json.loads((stage_dir / ".specdock-stage-owner.json").read_text(encoding="utf-8"))
            review_report = json.loads((stage_dir / "review-report.json").read_text(encoding="utf-8"))
            assert review_report["pack_digest"]["algorithm"] == "sha256-tree-v1"
            assert review_report["pack_digest"]["content_sha256"]
            assert owner["authority"] == "evidence_only"
            assert owner["adoption_status"] == "unreviewed"
            assert owner["bundle_generation_not_promotion"] is True
            assert owner["created_at"].endswith("Z")
            assert owner["input_path"] == str(pack_zip)
            assert owner["input_sha256"]
            assert owner["input_kind"] == "zip"
            assert "issue_id" in owner
            assert _protected_specdock_snapshot(repo) == protected_before

    def test_authoring_pack_stage_dry_run_does_not_write_stage_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            stage_dir = repo / ".specdock-authoring" / "staged" / "dry-run"
            protected_before = _protected_specdock_snapshot(repo)

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "stage",
                    "--input",
                    str(pack_zip),
                    "--stage-dir",
                    str(stage_dir),
                    "--dry-run",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert payload["dry_run"] is True
            assert "review-report.json" in payload["staged_files"]
            assert not stage_dir.exists()
            assert _protected_specdock_snapshot(repo) == protected_before

    def test_authoring_pack_stage_rejects_owned_stage_dir_with_symlink_descendant(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            stage_dir = repo / ".specdock-authoring" / "staged" / "symlink"
            stage_dir.mkdir(parents=True)
            (stage_dir / ".specdock-stage-owner.json").write_text(
                json.dumps(
                    {
                        "authority": "evidence_only",
                        "adoption_status": "unreviewed",
                        "bundle_generation_not_promotion": True,
                        "created_at": "2026-07-08T00:00:00Z",
                        "input_path": str(pack_zip),
                        "input_kind": "zip",
                    },
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            (stage_dir / "specdock-authoring-pack").symlink_to(repo / "spec-dock" / "active" / "issue")

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "stage",
                    "--input",
                    str(pack_zip),
                    "--stage-dir",
                    str(stage_dir),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_stage_target:symlink_descendant" in payload["findings"]

    def test_authoring_pack_stage_rejects_nested_symlink_ancestor_stage_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            outside = repo / "outside"
            nested = outside / "existing"
            nested.mkdir(parents=True)
            link_dir = repo / ".specdock-authoring" / "stage-link"
            link_dir.parent.mkdir(parents=True)
            link_dir.symlink_to(outside)
            stage_dir = link_dir / "existing" / "stage"

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "stage",
                    "--input",
                    str(pack_zip),
                    "--stage-dir",
                    str(stage_dir),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_stage_target:symlink" in payload["findings"]
            assert not (nested / "stage").exists()

    def test_authoring_pack_stage_rejects_symlink_ancestor_to_external_stage_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = _create_synced_git_repo(base)
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            external = base / "external"
            nested = external / "existing"
            nested.mkdir(parents=True)
            link_dir = repo / ".specdock-authoring" / "external-stage-link"
            link_dir.parent.mkdir(parents=True)
            link_dir.symlink_to(external)
            stage_dir = link_dir / "existing" / "stage"

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "stage",
                    "--input",
                    str(pack_zip),
                    "--stage-dir",
                    str(stage_dir),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_stage_target:symlink" in payload["findings"]
            assert not (nested / "stage").exists()

    def test_authoring_pack_stage_rejects_malformed_owned_marker_before_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            stage_dir = repo / ".specdock-authoring" / "staged" / "malformed-owner"
            stage_dir.mkdir(parents=True)
            preserved = stage_dir / "user-file.txt"
            preserved.write_text("do not delete\n", encoding="utf-8")
            (stage_dir / ".specdock-stage-owner.json").write_text("{bad json", encoding="utf-8")

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "stage",
                    "--input",
                    str(pack_zip),
                    "--stage-dir",
                    str(stage_dir),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_stage_target:non_owned_existing" in payload["findings"]
            assert preserved.read_text(encoding="utf-8") == "do not delete\n"

    def test_authoring_pack_stage_text_output_preserves_review_boundary_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            stage_dir = repo / ".specdock-authoring" / "staged" / "text"

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "stage",
                    "--input",
                    str(pack_zip),
                    "--stage-dir",
                    str(stage_dir),
                ],
            )

            output = p.stdout.lower()
            assert p.returncode == 0, p.stdout + p.stderr
            assert "status=pass" in output
            assert "review_authority=evidence_only" in output
            assert "review_adoption_status=unreviewed" in output
            assert "review_bundle_generation_not_promotion=true" in output
            assert "reviewer pass" not in output
            assert "execution-ready" not in output
            assert "pr-ready" not in output

    def test_authoring_pack_stage_rejects_non_pass_review_input_without_staging_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(
                repo / "rejected.zip",
                extra_entries={"specdock-authoring-pack/issue/claim.md": "PR delivery complete\n"},
            )
            stage_dir = repo / ".specdock-authoring" / "staged" / "rejected"

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "stage",
                    "--input",
                    str(pack_zip),
                    "--stage-dir",
                    str(stage_dir),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "review_not_pass" in payload["findings"]
            assert not (stage_dir / "specdock-authoring-pack").exists()

    def test_authoring_pack_stage_rejects_unsafe_stage_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            unsafe_stage = repo / "spec-dock" / "active" / "issue"

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "stage",
                    "--input",
                    str(pack_zip),
                    "--stage-dir",
                    str(unsafe_stage),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_stage_target:canonical-docs" in payload["findings"]

    def test_authoring_pack_stage_rejects_direct_canonical_issue_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            canonical_issue = (
                repo
                / "spec-dock"
                / "initiatives"
                / "init-local-00001"
                / "epics"
                / "epic-00001"
                / "issues"
                / "iss-00001"
            )

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "stage",
                    "--input",
                    str(pack_zip),
                    "--stage-dir",
                    str(canonical_issue),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_stage_target:canonical-docs" in payload["findings"]
            assert not (canonical_issue / "specdock-authoring-pack").exists()

    def test_authoring_pack_stage_rejects_relative_canonical_target_from_specdock_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            specdock_cwd = repo / "spec-dock"
            stage_dir = Path("active") / "issue" / "staged-pack"

            p = _run_authoring_capture_from_cwd(
                self,
                repo,
                specdock_cwd,
                [
                    "authoring",
                    "pack",
                    "stage",
                    "--input",
                    str(pack_zip),
                    "--stage-dir",
                    str(stage_dir),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_stage_target:canonical-docs" in payload["findings"]
            assert not (specdock_cwd / stage_dir / "specdock-authoring-pack").exists()

    def test_authoring_pack_stage_rejects_assurance_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            assurance_target = repo / "spec-dock" / ".assurance.json"

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "stage",
                    "--input",
                    str(pack_zip),
                    "--stage-dir",
                    str(assurance_target),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_stage_target:assurance" in payload["findings"]
            assert not assurance_target.exists()

    def test_authoring_pack_stage_rejects_file_stage_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            stage_target = repo / ".specdock-authoring" / "stage-file"
            stage_target.parent.mkdir(parents=True)
            stage_target.write_text("not a directory\n", encoding="utf-8")

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "stage",
                    "--input",
                    str(pack_zip),
                    "--stage-dir",
                    str(stage_target),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_stage_target:not_directory" in payload["findings"]

    def test_authoring_preflight_github_sync_passes_for_clean_synced_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            repo = _create_synced_git_repo(target)

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "preflight",
                    "github-sync",
                    "--repo-root",
                    str(repo),
                    "--source-path",
                    "source.txt",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert payload["evidence_mode"] == "github-synced"
            assert payload["sync_state"] == "synced"
            assert payload["github_sync"] == "verified"
            assert payload["requested_ref"] == "main"
            assert payload["effective_ref"] == "main"
            assert payload["local_head"] == payload["remote_head"]
            assert payload["source_manifest_hash"]
            assert payload["source_hash_mismatch_checked"] is False
            assert payload["source_paths"] == ["source.txt"]
            assert "source.txt" in payload["source_hashes"]
            assert payload["schema_version"] == 1
            assert payload["receipt_kind"] == "spec-dock.authoring.github-sync-preflight"
            assert payload["fetch"]["status"] == "success"
            assert payload["fetch"]["policy_id"] == "origin-fetch-v1"
            assert payload["fetch"]["executable"] == "git"
            assert payload["fetch"]["argv"] == ["fetch", "--prune", "origin"]
            assert payload["fetch"]["attempts"] == [
                {
                    "attempt_number": 1,
                    "duration_ms": payload["fetch"]["attempts"][0]["duration_ms"],
                    "return_code": 0,
                    "termination": "exited",
                    "failure_class": None,
                    "confidence": "certain",
                    "retryable": False,
                    "diagnostic": {
                        "code": None,
                        "excerpt": None,
                        "redacted_sha256": None,
                        "source_byte_count": 0,
                        "excerpt_byte_count": 0,
                        "truncated": False,
                        "redaction_applied": False,
                    },
                }
            ]

            text_result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "preflight",
                    "github-sync",
                    "--repo-root",
                    str(repo),
                    "--source-path",
                    "source.txt",
                ],
            )
            assert text_result.returncode == 0, text_result.stdout + text_result.stderr
            assert "status=pass" in text_result.stdout
            assert "evidence_mode=github-synced" in text_result.stdout
            assert "sync_state=synced" in text_result.stdout
            assert "github_sync=verified" in text_result.stdout
            assert "receipt_schema_version=1" in text_result.stdout
            assert "receipt_kind=spec-dock.authoring.github-sync-preflight" in text_result.stdout
            assert "fetch_status=success" in text_result.stdout
            assert "fetch_attempt_count=1" in text_result.stdout
            assert "fetch_failure_class=null" in text_result.stdout
            assert "fetch_classification_confidence=certain" in text_result.stdout
            assert "fetch_timeout_seconds=60.0" in text_result.stdout

    def test_authoring_preflight_injected_spawn_failure_is_typed_and_blocked(self) -> None:
        runtime_root = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        if str(runtime_root) not in sys.path:
            sys.path.insert(0, str(runtime_root))

        from spec_dock_runtime.application.authoring_pack.github_sync_preflight import (
            GitHubSyncPreflightRequest,
            run_github_sync_preflight,
        )
        from spec_dock_runtime.domain.authoring_pack.preflight_contract import GitProcessOutcome

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))

            def spawn_failure(_request):
                return GitProcessOutcome(
                    return_code=None,
                    termination="spawn_error",
                    stdout=b"",
                    stderr=b"raw traceback must remain private",
                    duration_ms=3,
                    os_error_kind="FileNotFoundError",
                )

            result = run_github_sync_preflight(
                GitHubSyncPreflightRequest(repo_root=repo, source_paths=("source.txt",)),
                fetch_executor=spawn_failure,
            )
            payload = result.to_dict()

            assert payload["status"] == "blocked"
            assert payload["github_sync"] == "failed"
            assert "origin_fetch_failed" in payload["blockers"]
            assert payload["fetch"]["policy_id"] == "origin-fetch-v1"
            assert payload["fetch"]["status"] == "failed"
            assert payload["fetch"]["attempts"][0]["failure_class"] == "spawn_failure"
            assert payload["fetch"]["attempts"][0]["return_code"] is None
            assert "raw traceback" not in str(payload)

    def test_authoring_preflight_retries_transient_fetch_with_same_shape_then_passes(self) -> None:
        runtime_root = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        if str(runtime_root) not in sys.path:
            sys.path.insert(0, str(runtime_root))

        from spec_dock_runtime.application.authoring_pack.github_sync_preflight import (
            GitHubSyncPreflightRequest,
            run_github_sync_preflight,
        )
        from spec_dock_runtime.domain.authoring_pack.preflight_contract import GitProcessOutcome

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            requests = []
            outcomes = iter(
                [
                    GitProcessOutcome(1, "exited", b"", b"Connection reset by peer", 2),
                    GitProcessOutcome(0, "exited", b"", b"", 3),
                ]
            )
            sleeps = []

            def fake_fetch(request):
                requests.append(request)
                return next(outcomes)

            result = run_github_sync_preflight(
                GitHubSyncPreflightRequest(repo_root=repo, source_paths=("source.txt",)),
                fetch_executor=fake_fetch,
                fetch_sleeper=sleeps.append,
            )
            payload = result.to_dict()

            assert payload["status"] == "pass"
            assert payload["fetch"]["status"] == "success"
            assert len(payload["fetch"]["attempts"]) == 2
            assert payload["fetch"]["attempts"][0]["failure_class"] == "transient_transport"
            assert payload["fetch"]["attempts"][0]["retryable"] is True
            assert requests[0] is requests[1]
            assert requests[0].argv == requests[1].argv == ("fetch", "--prune", "origin")
            assert sleeps == [0.25]

    def test_authoring_preflight_github_sync_checks_default_source_path_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            target = repo / "outside-default-source"
            target.mkdir()
            default_path = repo / "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack"
            default_path.parent.mkdir(parents=True, exist_ok=True)
            default_path.symlink_to(target, target_is_directory=True)

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "preflight",
                    "github-sync",
                    "--repo-root",
                    str(repo),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1
            assert payload["status"] == "blocked"
            assert any(item.startswith("unsafe_source_path:symlink:") for item in payload["blockers"])

    def test_authoring_preflight_does_not_dirty_consumer_repo_with_runtime_bytecode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            script = repo / "spec-dock" / "scripts" / "spec-dock"
            env = self._runtime_env(repo, {"PATH": os.environ.get("PATH", "")})
            env.pop("PYTHONDONTWRITEBYTECODE", None)

            p = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "authoring",
                    "preflight",
                    "github-sync",
                    "--repo-root",
                    str(repo),
                    "--source-path",
                    "source.txt",
                    "--format",
                    "json",
                ],
                cwd=str(repo),
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert "untracked_files" not in payload["blockers"]
            runtime_root = repo / "spec-dock" / "scripts" / "spec_dock_runtime"
            assert not any(path.name == "__pycache__" for path in runtime_root.rglob("__pycache__"))
            assert not any(path.suffix in {".pyc", ".pyo"} for path in runtime_root.rglob("*"))
            assert _git(repo, "status", "--porcelain=v1").stdout == ""

    @pytest.mark.parametrize(
        ("mutate", "reason"),
        (
            (lambda repo: (repo / "source.txt").write_text("dirty\n", encoding="utf-8"), "dirty_tracked"),
            (lambda repo: _stage_change(repo), "staged_changes"),
            (lambda repo: (repo / "untracked.txt").write_text("new\n", encoding="utf-8"), "untracked_files"),
        ),
    )
    def test_authoring_preflight_github_sync_blocks_unsafe_worktree_states(self, mutate, reason: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            mutate(repo)

            payload = _run_preflight_json(self, repo, expected_returncode=1)

            assert payload["status"] == "blocked"
            assert reason in payload["blockers"]
            assert payload["github_sync"] != "verified"

    @pytest.mark.parametrize(
        ("mutate", "expected_status", "reason"),
        (
            ("ahead", "blocked", "ahead_of_remote"),
            ("behind", "stale", "behind_remote"),
            ("diverged", "blocked", "diverged_from_remote"),
        ),
    )
    def test_authoring_preflight_github_sync_blocks_ahead_behind_and_diverged(
        self, mutate, expected_status: str, reason: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            {
                "ahead": _make_ahead,
                "behind": _make_behind,
                "diverged": _make_diverged,
            }[mutate](repo)

            payload = _run_preflight_json(self, repo, expected_returncode=1)

            assert payload["status"] == expected_status
            assert reason in payload["blockers"]

    def test_authoring_preflight_github_sync_fetches_before_remote_comparison(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            other = repo.parent / "other"
            _git(repo.parent, "clone", str(repo.parent / "remote.git"), str(other))
            _git(other, "checkout", "main")
            _git(other, "config", "user.name", "Test User")
            _git(other, "config", "user.email", "test@example.com")
            (other / "source.txt").write_text("remote-only\n", encoding="utf-8")
            _git(other, "add", "source.txt")
            _git(other, "commit", "-m", "remote-only")
            _git(other, "push", "origin", "main")

            payload = _run_preflight_json(self, repo, expected_returncode=1)

            assert payload["status"] == "stale"
            assert "behind_remote" in payload["blockers"]
            assert payload["local_head"] != payload["remote_head"]

    def test_authoring_preflight_github_sync_blocks_missing_explicit_source_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))

            payload = _run_preflight_json(self, repo, "--source-path", "missing.py", expected_returncode=1)

            assert payload["status"] == "blocked"
            assert "missing_source_path:missing.py" in payload["blockers"]
            assert payload["github_sync"] != "verified"

    def test_authoring_preflight_github_sync_blocks_missing_origin_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            _git(repo.parent, "--git-dir", str(repo.parent / "remote.git"), "update-ref", "-d", "refs/heads/main")
            _git(repo, "update-ref", "-d", "refs/remotes/origin/main")

            payload = _run_preflight_json(self, repo, expected_returncode=1)

            assert payload["status"] == "blocked"
            assert "remote_branch_missing" in payload["blockers"]

    def test_authoring_preflight_github_sync_blocks_non_origin_upstream(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            _git(repo, "remote", "add", "fork", (repo.parent / "remote.git").as_posix())
            _git(repo, "update-ref", "refs/remotes/fork/main", _git(repo, "rev-parse", "HEAD").stdout.strip())
            _git(repo, "branch", "--set-upstream-to=fork/main", "main")

            payload = _run_preflight_json(self, repo, expected_returncode=1)

            assert payload["status"] == "blocked"
            assert "origin_mismatch" in payload["blockers"]

    def test_authoring_preflight_github_sync_blocks_connector_unavailable_observer(self) -> None:
        runtime_root = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        if str(runtime_root) not in sys.path:
            sys.path.insert(0, str(runtime_root))

        from spec_dock_runtime.application.authoring_pack.github_sync_preflight import (
            GitHubSyncPreflightRequest,
            run_github_sync_preflight,
        )
        from spec_dock_runtime.domain.authoring_pack.preflight_contract import (
            GitVisibleRef,
        )

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))

            result = run_github_sync_preflight(
                GitHubSyncPreflightRequest(repo_root=repo, source_paths=("source.txt",)),
                remote_observer=lambda _repo, requested_ref, _fallback: GitVisibleRef(
                    state="connector_unavailable",
                    requested_ref=requested_ref,
                    effective_ref=None,
                    remote_head=None,
                    blockers=("connector_unavailable",),
                ),
            )

            assert result.status == "blocked"
            assert result.github_sync == "failed"
            assert "connector_unavailable" in result.blockers

    def test_authoring_preflight_github_sync_blocks_unresolved_ref_without_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))

            payload = _run_preflight_json(self, repo, "--ref", "missing", expected_returncode=1)

            assert payload["status"] == "blocked"
            assert payload["requested_ref"] == "missing"
            assert payload["effective_ref"] is None
            assert "remote_branch_missing" in payload["blockers"]

    def test_authoring_preflight_github_sync_records_explicit_default_branch_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))

            payload = _run_preflight_json(
                self,
                repo,
                "--ref",
                "missing",
                "--allow-default-branch-fallback",
                expected_returncode=0,
            )

            assert payload["status"] == "pass"
            assert payload["requested_ref"] == "missing"
            assert payload["effective_ref"] == "main"

    def test_authoring_preflight_github_sync_blocks_unknown_default_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            _git(
                repo.parent, "--git-dir", str(repo.parent / "remote.git"), "symbolic-ref", "HEAD", "refs/heads/missing"
            )
            _git(repo, "symbolic-ref", "--delete", "refs/remotes/origin/HEAD")

            payload = _run_preflight_json(
                self,
                repo,
                "--ref",
                "missing",
                "--allow-default-branch-fallback",
                expected_returncode=1,
            )

            assert payload["status"] == "blocked"
            assert "default_branch_unknown" in payload["blockers"]

    def test_authoring_preflight_github_sync_reports_source_hash_mismatch_as_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))

            payload = _run_preflight_json(
                self,
                repo,
                "--expected-source-hash",
                "not-the-current-hash",
                expected_returncode=1,
            )

            assert payload["status"] == "stale"
            assert payload["source_hash_mismatch_checked"] is True
            assert "source_hash_mismatch" in payload["blockers"]
            assert payload["expected_source_hash"] == "not-the-current-hash"
            assert payload["current_source_hash"] == payload["source_manifest_hash"]

    def test_authoring_preflight_source_manifest_ignores_python_cache_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            package = repo / "package"
            cache = package / "__pycache__"
            cache.mkdir(parents=True)
            (package / "module.py").write_text("VALUE = 1\n", encoding="utf-8")
            (cache / "module.cpython-312.pyc").write_bytes(b"cache")

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "preflight",
                    "github-sync",
                    "--repo-root",
                    str(repo),
                    "--evidence-mode",
                    "local-context",
                    "--source-path",
                    "package",
                    "--diff-summary",
                    "local source manifest fixture",
                    "--unsynced-reason",
                    "testing cache exclusion",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert "package/module.py" in payload["source_hashes"]
            assert all("__pycache__" not in path for path in payload["source_hashes"])
            assert all(not path.endswith(".pyc") for path in payload["source_hashes"])

    def test_authoring_preflight_rejects_symlinked_source_manifest_inputs(self) -> None:
        if not hasattr(os, "symlink"):
            pytest.skip("symlink unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = _create_synced_git_repo(root)
            outside = root / "outside.txt"
            outside.write_text("secret\n", encoding="utf-8")
            package = repo / "package"
            package.mkdir()
            (package / "safe.py").write_text("VALUE = 1\n", encoding="utf-8")
            (package / "linked.py").symlink_to(outside)
            source_link = repo / "source-link.txt"
            source_link.symlink_to(outside)

            child_payload = _run_preflight_json(
                self,
                repo,
                "--evidence-mode",
                "local-context",
                "--source-path",
                "package",
                "--diff-summary",
                "local source manifest fixture",
                "--unsynced-reason",
                "testing symlink rejection",
                expected_returncode=1,
            )
            direct_payload = _run_preflight_json(
                self,
                repo,
                "--evidence-mode",
                "local-context",
                "--source-path",
                "source-link.txt",
                "--diff-summary",
                "local source manifest fixture",
                "--unsynced-reason",
                "testing symlink rejection",
                expected_returncode=1,
            )

            assert child_payload["status"] == "blocked"
            assert "unsafe_source_path:symlink:package/linked.py" in child_payload["blockers"]
            assert "package/linked.py" not in child_payload["source_hashes"]
            assert direct_payload["status"] == "blocked"
            assert "unsafe_source_path:symlink:source-link.txt" in direct_payload["blockers"]
            assert "source-link.txt" not in direct_payload["source_hashes"]

    def test_authoring_preflight_rejects_missing_local_context_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))

            payload = _run_preflight_json(
                self,
                repo,
                "--evidence-mode",
                "local-context",
                "--provided-context-path",
                "missing.md",
                "--unsynced-reason",
                "testing missing context rejection",
                expected_returncode=1,
            )

            assert payload["status"] == "blocked"
            assert "missing_context_path:missing.md" in payload["blockers"]
            assert payload["provided_context_paths"] == ["missing.md"]

    def test_authoring_preflight_github_sync_compares_expected_manifest_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            manifest = repo / "expected.json"
            manifest.write_text(json.dumps({"source_manifest_hash": "old"}) + "\n", encoding="utf-8")
            _git(repo, "add", "expected.json")
            _git(repo, "commit", "-m", "add expected manifest")
            _git(repo, "push", "origin", "main")

            payload = _run_preflight_json(
                self,
                repo,
                "--expected-source-manifest",
                str(manifest),
                expected_returncode=1,
            )

            assert payload["status"] == "stale"
            assert payload["source_hash_mismatch_checked"] is True
            assert "source_hash_mismatch" in payload["blockers"]

    def test_authoring_preflight_local_context_emits_lower_authority_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "preflight",
                    "github-sync",
                    "--repo-root",
                    str(repo),
                    "--evidence-mode",
                    "local-context",
                    "--provided-context-path",
                    "source.txt",
                    "--unsynced-reason",
                    "local-only review packet",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert payload["github_sync"] == "not_verified"
            assert payload["sync_state"] == "local_context"
            assert payload["adoption_requires"] == "explicit_eal_disposition"
            assert payload["provided_context_paths"] == ["source.txt"]
            assert payload["unsynced_reason"] == "local-only review packet"

    def test_authoring_preflight_local_context_reports_source_hash_mismatch_as_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "preflight",
                    "github-sync",
                    "--repo-root",
                    str(repo),
                    "--evidence-mode",
                    "local-context",
                    "--provided-context-path",
                    "source.txt",
                    "--unsynced-reason",
                    "local-only review packet",
                    "--expected-source-hash",
                    "not-the-current-hash",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "stale"
            assert payload["github_sync"] == "not_verified"
            assert payload["source_hash_mismatch_checked"] is True
            assert "source_hash_mismatch" in payload["blockers"]
            assert payload["expected_source_hash"] == "not-the-current-hash"
            assert payload["current_source_hash"] == payload["source_manifest_hash"]

    @pytest.mark.parametrize(
        ("args", "reason"),
        (
            (["--provided-context-path", "source.txt"], "missing_unsynced_reason"),
            (["--unsynced-reason", "dirty local state"], "missing_context_provenance"),
        ),
    )
    def test_authoring_preflight_local_context_blocks_missing_provenance(self, args: list[str], reason: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "preflight",
                    "github-sync",
                    "--repo-root",
                    str(repo),
                    "--evidence-mode",
                    "local-context",
                    "--format",
                    "json",
                    *args,
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "blocked"
            assert reason in payload["blockers"]

    def test_authoring_preflight_diagnostics_avoid_forbidden_authority_claims(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))

            outputs = [
                _run_authoring_capture(self, repo, ["authoring", "preflight", "github-sync", "--repo-root", str(repo)]),
                _run_authoring_capture(
                    self,
                    repo,
                    [
                        "authoring",
                        "preflight",
                        "github-sync",
                        "--repo-root",
                        str(repo),
                        "--expected-source-hash",
                        "old",
                    ],
                ),
                _run_authoring_capture(
                    self,
                    repo,
                    [
                        "authoring",
                        "preflight",
                        "github-sync",
                        "--repo-root",
                        str(repo),
                        "--evidence-mode",
                        "local-context",
                        "--diff-summary",
                        "local edits",
                        "--unsynced-reason",
                        "offline review",
                    ],
                ),
            ]

            for p in outputs:
                output = "\n".join(
                    line
                    for line in (p.stdout + p.stderr).lower().splitlines()
                    if not line.startswith("fetch_status=")
                )
                for forbidden in _FORBIDDEN_AUTHORITY_CLAIMS:
                    assert forbidden not in output

    def test_authoring_preflight_dogfood_runtime_path_exposes_implemented_local_context(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "spec-dock" / "scripts" / "spec-dock"

        p = subprocess.run(
            [
                str(script),
                "authoring",
                "preflight",
                "github-sync",
                "--repo-root",
                str(repo_root),
                "--evidence-mode",
                "local-context",
                "--diff-summary",
                "dogfood mirror smoke",
                "--unsynced-reason",
                "mirror behavior smoke",
                "--format",
                "json",
            ],
            cwd=str(repo_root),
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            capture_output=True,
            text=True,
        )

        payload = _json_stdout(p)
        assert p.returncode == 0, p.stdout + p.stderr
        assert payload["status"] == "pass"
        assert payload["github_sync"] == "not_verified"
        assert payload["sync_state"] == "local_context"
        assert (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py" in payload["source_paths"]
        )
        assert "spec-dock/scripts/spec_dock_runtime/commands/authoring.py" in payload["source_paths"]
        assert all("__pycache__" not in path for path in payload["source_hashes"])
        assert all(not path.endswith(".pyc") for path in payload["source_hashes"])

    def test_authoring_pack_review_and_stage_dogfood_runtime_path(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "spec-dock" / "scripts" / "spec-dock"

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            stage_dir = repo / ".specdock-authoring" / "staged" / "dogfood"

            review = subprocess.run(
                [
                    str(script),
                    "authoring",
                    "pack",
                    "review",
                    "--input",
                    str(pack_zip),
                    "--format",
                    "json",
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )
            stage = subprocess.run(
                [
                    str(script),
                    "authoring",
                    "pack",
                    "stage",
                    "--input",
                    str(pack_zip),
                    "--stage-dir",
                    str(stage_dir),
                    "--format",
                    "json",
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            review_payload = _json_stdout(review)
            stage_payload = _json_stdout(stage)
            assert review.returncode == 0, review.stdout + review.stderr
            assert stage.returncode == 0, stage.stdout + stage.stderr
            assert review_payload["status"] == "pass"
            assert stage_payload["status"] == "pass"
            assert (stage_dir / "review-report.json").is_file()

    def test_authoring_validate_candidate_dogfood_runtime_path(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "spec-dock" / "scripts" / "spec-dock"

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(
                repo / ".specdock-authoring" / "staged" / "dogfood-candidates", kind="epic-issue"
            )

            p = subprocess.run(
                [
                    str(script),
                    "authoring",
                    "validate",
                    "epic-issue-candidates",
                    "--input",
                    str(stage_dir),
                    "--expected-parent-epic",
                    "epic-00295",
                    "--format",
                    "json",
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert payload["candidate_kind"] == "epic-issue"
            assert payload["node_creation_performed"] is False
            assert payload["canonical_written"] is False

    def test_authoring_pack_dogfood_runtime_path_rejects_pr_delivery_claim_and_preserves_stage_text_boundary(
        self,
    ) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "spec-dock" / "scripts" / "spec-dock"

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            forbidden_zip = _write_authoring_pack_zip(
                repo / "forbidden.zip",
                extra_entries={"specdock-authoring-pack/issue/claim.md": "PR delivery complete\n"},
            )
            valid_zip = _write_authoring_pack_zip(repo / "valid.zip")
            stage_dir = repo / ".specdock-authoring" / "staged" / "dogfood-text"

            review = subprocess.run(
                [
                    str(script),
                    "authoring",
                    "pack",
                    "review",
                    "--input",
                    str(forbidden_zip),
                    "--format",
                    "json",
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )
            stage = subprocess.run(
                [
                    str(script),
                    "authoring",
                    "pack",
                    "stage",
                    "--input",
                    str(valid_zip),
                    "--stage-dir",
                    str(stage_dir),
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            review_payload = _json_stdout(review)
            stage_output = stage.stdout.lower()
            assert review.returncode == 1, review.stdout + review.stderr
            assert stage.returncode == 0, stage.stdout + stage.stderr
            assert "forbidden_authority_claim:pr delivery" in review_payload["findings"]
            assert "review_authority=evidence_only" in stage_output
            assert "review_adoption_status=unreviewed" in stage_output
            assert "review_bundle_generation_not_promotion=true" in stage_output

    @pytest.mark.parametrize(
        "script_root",
        (
            Path("src/spec_dock/assets/spec_dock/scripts/authoring-pack"),
            Path("spec-dock/scripts/authoring-pack"),
        ),
    )
    def test_authoring_pack_compatibility_scripts_delegate_to_runtime_contract(self, script_root: Path) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        review_script = repo_root / script_root / "review_chatgpt_authoring_pack.py"
        stage_script = repo_root / script_root / "stage_chatgpt_authoring_pack.py"

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            report_path = repo / ".specdock-authoring" / "compat" / "review-report.json"
            stage_dir = repo / ".specdock-authoring" / "compat" / "stage"

            review = subprocess.run(
                [
                    sys.executable,
                    str(review_script),
                    "--input",
                    str(pack_zip),
                    "--report-path",
                    str(report_path),
                    "--format",
                    "json",
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )
            stage = subprocess.run(
                [
                    sys.executable,
                    str(stage_script),
                    "--input",
                    str(pack_zip),
                    "--stage-dir",
                    str(stage_dir),
                    "--format",
                    "json",
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            review_payload = _json_stdout(review)
            stage_payload = _json_stdout(stage)
            assert review.returncode == 0, review.stdout + review.stderr
            assert stage.returncode == 0, stage.stdout + stage.stderr
            assert review_payload["status"] == "pass"
            assert stage_payload["status"] == "pass"
            assert json.loads(report_path.read_text(encoding="utf-8"))["authority"] == "evidence_only"
            assert "/Users/" not in review_script.read_text(encoding="utf-8")
            assert "/Users/" not in stage_script.read_text(encoding="utf-8")

    @pytest.mark.parametrize(
        "script_root",
        (
            Path("src/spec_dock/assets/spec_dock/scripts/authoring-pack"),
            Path("spec-dock/scripts/authoring-pack"),
        ),
    )
    def test_authoring_pack_compatibility_review_accepts_legacy_output_dir_args(self, script_root: Path) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        review_script = repo_root / script_root / "review_chatgpt_authoring_pack.py"

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip, preflight = _write_legacy_review_fixture(repo)
            output_dir = repo / ".specdock-authoring" / "legacy-review"
            extract_dir = repo / ".specdock-authoring" / "legacy-extract"

            review = subprocess.run(
                [
                    sys.executable,
                    str(review_script),
                    "--input",
                    str(pack_zip),
                    "--preflight",
                    str(preflight),
                    "--output-dir",
                    str(output_dir),
                    "--input-kind",
                    "zip",
                    "--extract-dir",
                    str(extract_dir),
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            payload = _json_stdout(review)
            report_payload = json.loads((output_dir / "validation-report.json").read_text(encoding="utf-8"))
            assert review.returncode == 0, review.stdout + review.stderr
            assert payload["status"] == "pass"
            assert report_payload["status"] == "pass"
            assert report_payload["authority"] == "evidence_only"
            assert report_payload["pack_digest"]["content_sha256"]
            assert (extract_dir / "specdock-authoring-pack" / "README.md").is_file()

    def test_authoring_pack_compatibility_review_honors_non_passing_preflight(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        review_script = (
            repo_root / "src/spec_dock/assets/spec_dock/scripts/authoring-pack/review_chatgpt_authoring_pack.py"
        )
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip, preflight = _write_legacy_review_fixture(repo, status="stale")

            review = subprocess.run(
                [
                    sys.executable,
                    str(review_script),
                    "--input",
                    str(pack_zip),
                    "--preflight",
                    str(preflight),
                    "--output-dir",
                    str(repo / ".specdock-authoring" / "legacy-review"),
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            payload = _json_stdout(review)
            assert review.returncode != 0
            assert payload["status"] == "stale"
            assert "preflight status is not pass: stale" in payload["errors"]

    @pytest.mark.parametrize(
        "script_root",
        (
            Path("src/spec_dock/assets/spec_dock/scripts/authoring-pack"),
            Path("spec-dock/scripts/authoring-pack"),
        ),
    )
    def test_authoring_pack_compatibility_review_rejects_unsafe_legacy_output_dir(self, script_root: Path) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        review_script = repo_root / script_root / "review_chatgpt_authoring_pack.py"

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            output_dir = repo / "spec-dock" / "active" / "issue" / "legacy-review"

            review = subprocess.run(
                [
                    sys.executable,
                    str(review_script),
                    "--input",
                    str(pack_zip),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            payload = _json_stdout(review)
            assert review.returncode == 1, review.stdout + review.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_report_path:canonical-docs" in payload["findings"]
            assert not (output_dir / "validation-report.json").exists()

    @pytest.mark.parametrize(
        "script_root",
        (
            Path("src/spec_dock/assets/spec_dock/scripts/authoring-pack"),
            Path("spec-dock/scripts/authoring-pack"),
        ),
    )
    def test_authoring_pack_compatibility_review_rejects_symlink_legacy_output_dir(self, script_root: Path) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        review_script = repo_root / script_root / "review_chatgpt_authoring_pack.py"

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            outside = repo / "outside"
            outside.mkdir()
            output_dir = repo / ".specdock-authoring" / "legacy-link"
            output_dir.parent.mkdir(parents=True)
            output_dir.symlink_to(outside)

            review = subprocess.run(
                [
                    sys.executable,
                    str(review_script),
                    "--input",
                    str(pack_zip),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            payload = _json_stdout(review)
            assert review.returncode == 1, review.stdout + review.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_report_path:symlink" in payload["findings"]
            assert not (outside / "validation-report.json").exists()

    def test_authoring_pack_compatibility_review_handles_encrypted_zip_without_traceback(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        review_script = (
            repo_root / "src/spec_dock/assets/spec_dock/scripts/authoring-pack/review_chatgpt_authoring_pack.py"
        )

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            encrypted_name = "specdock-authoring-pack/issue/requirement.md"
            pack_zip = _write_authoring_pack_zip(repo / "encrypted.zip")
            _mark_zip_entry_encrypted(pack_zip, encrypted_name)
            output_dir = repo / ".specdock-authoring" / "legacy-encrypted"

            review = subprocess.run(
                [
                    sys.executable,
                    str(review_script),
                    "--input",
                    str(pack_zip),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            payload = _json_stdout(review)
            report_payload = json.loads((output_dir / "validation-report.json").read_text(encoding="utf-8"))
            assert review.returncode == 1, review.stdout + review.stderr
            assert "traceback" not in review.stderr.lower()
            assert payload["status"] == "rejected"
            assert report_payload["status"] == "rejected"
            assert report_payload["pack_digest"]["content_sha256"] is None

    def test_authoring_pack_compatibility_review_skips_digest_for_rejected_oversized_zip(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        review_script = (
            repo_root / "src/spec_dock/assets/spec_dock/scripts/authoring-pack/review_chatgpt_authoring_pack.py"
        )

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(
                repo / "oversized.zip",
                extra_entries={"specdock-authoring-pack/issue/large.md": "x" * 2_000_001},
            )
            output_dir = repo / ".specdock-authoring" / "legacy-oversized"

            review = subprocess.run(
                [
                    sys.executable,
                    str(review_script),
                    "--input",
                    str(pack_zip),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            payload = _json_stdout(review)
            report_payload = json.loads((output_dir / "validation-report.json").read_text(encoding="utf-8"))
            assert review.returncode == 1, review.stdout + review.stderr
            assert payload["status"] == "rejected"
            assert report_payload["pack_digest"]["content_sha256"] is None

    @pytest.mark.parametrize(
        "script_root",
        (
            Path("src/spec_dock/assets/spec_dock/scripts/authoring-pack"),
            Path("spec-dock/scripts/authoring-pack"),
        ),
    )
    def test_authoring_pack_compatibility_review_rejects_duplicate_zip_entries(self, script_root: Path) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        review_script = repo_root / script_root / "review_chatgpt_authoring_pack.py"

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            duplicate = zipfile.ZipInfo("specdock-authoring-pack/issue/requirement.md")
            pack_zip = _write_authoring_pack_zip(
                repo / "duplicate.zip",
                extra_infos=[(duplicate, "# Duplicate requirement\n")],
            )
            output_dir = repo / ".specdock-authoring" / "legacy-duplicate"

            review = subprocess.run(
                [
                    sys.executable,
                    str(review_script),
                    "--input",
                    str(pack_zip),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            payload = _json_stdout(review)
            report_payload = json.loads((output_dir / "validation-report.json").read_text(encoding="utf-8"))
            assert review.returncode == 1, review.stdout + review.stderr
            assert payload["status"] == "rejected"
            assert "duplicate_entry:issue/requirement.md" in payload["findings"]
            assert report_payload["status"] == "rejected"

    @pytest.mark.parametrize(
        ("metadata_name", "metadata_payload"),
        (
            ("manifest.json", "[]\n"),
            ("provenance.json", '"not-object"\n'),
            ("source-manifest.json", "[]\n"),
            ("stale-if.json", "[]\n"),
            ("adoption/adoption-map.json", "[]\n"),
            ("adoption/eal-candidates.json", "[]\n"),
        ),
    )
    def test_authoring_pack_compatibility_review_fails_non_object_metadata(
        self, metadata_name: str, metadata_payload: str
    ) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        review_script = (
            repo_root / "src/spec_dock/assets/spec_dock/scripts/authoring-pack/review_chatgpt_authoring_pack.py"
        )

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(
                repo / "non-object-metadata.zip",
                metadata_overrides={metadata_name: metadata_payload},
            )
            output_dir = repo / ".specdock-authoring" / "legacy-non-object"

            review = subprocess.run(
                [
                    sys.executable,
                    str(review_script),
                    "--input",
                    str(pack_zip),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            payload = _json_stdout(review)
            assert review.returncode == 1, review.stdout + review.stderr
            assert payload["status"] == "fail"
            assert f"non_object_json:{metadata_name}" in payload["findings"]

    @pytest.mark.parametrize(
        ("metadata_name", "metadata_payload", "expected_finding"),
        (
            ("provenance.json", "{}\n", "missing_or_invalid_field:provenance.json.evidence_mode"),
            (
                "source-manifest.json",
                json.dumps({"source_manifest_hash": "hash"}, sort_keys=True) + "\n",
                "missing_or_invalid_field:source-manifest.json.source_hashes",
            ),
        ),
    )
    def test_authoring_pack_compatibility_review_fails_missing_metadata_contract_fields(
        self, metadata_name: str, metadata_payload: str, expected_finding: str
    ) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        review_script = (
            repo_root / "src/spec_dock/assets/spec_dock/scripts/authoring-pack/review_chatgpt_authoring_pack.py"
        )

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(
                repo / "missing-metadata-fields.zip",
                metadata_overrides={metadata_name: metadata_payload},
            )
            output_dir = repo / ".specdock-authoring" / "legacy-missing-fields"

            review = subprocess.run(
                [
                    sys.executable,
                    str(review_script),
                    "--input",
                    str(pack_zip),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            payload = _json_stdout(review)
            assert review.returncode == 1, review.stdout + review.stderr
            assert payload["status"] == "fail"
            assert expected_finding in payload["findings"]

    def test_authoring_pack_compatibility_review_allows_null_authorized_profile_candidate(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        review_script = (
            repo_root / "src/spec_dock/assets/spec_dock/scripts/authoring-pack/review_chatgpt_authoring_pack.py"
        )

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            candidate_payload = {
                "schema_version": 1,
                "authority": "evidence_only",
                "adoption_status": "unreviewed",
                "bundle_generation_not_promotion": True,
                "candidate_id": "candidate-001",
                "candidate_kind": "issue",
                "slug": "candidate-001",
                "title": "Candidate 001",
                "parent_trace": {"epic_id": "epic-00295"},
                "boundary": {"summary": "boundary", "scope": ["scope"], "non_scope": ["other"], "dependencies": []},
                "grade_recommendation": {"grade": "standard", "advisory_only": True},
                "profile_recommendation": {
                    "profile": None,
                    "advisory_only": True,
                    "ignored_for_authority": True,
                    "authorized_profile": None,
                },
                "draft_files": {"requirement": "requirement.md", "design": "design.md", "plan": "plan.md"},
                "authority_claims": _candidate_authority_claims(),
            }
            pack_zip = _write_authoring_pack_zip(
                repo / "null-authorized-profile.zip",
                extra_entries={
                    "specdock-authoring-pack/candidates/issues/candidate-001/candidate.json": json.dumps(
                        candidate_payload, sort_keys=True
                    )
                    + "\n",
                },
            )
            output_dir = repo / ".specdock-authoring" / "legacy-null-authorized-profile"

            review = subprocess.run(
                [
                    sys.executable,
                    str(review_script),
                    "--input",
                    str(pack_zip),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            payload = _json_stdout(review)
            assert review.returncode == 0, review.stdout + review.stderr
            assert payload["status"] == "pass"
            assert "forbidden_authority_claim:authorized_profile" not in payload["findings"]

    @pytest.mark.parametrize(
        "script_root",
        (
            Path("src/spec_dock/assets/spec_dock/scripts/authoring-pack"),
            Path("spec-dock/scripts/authoring-pack"),
        ),
    )
    def test_authoring_pack_compatibility_legacy_review_report_can_stage_same_tree(self, script_root: Path) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        review_script = repo_root / script_root / "review_chatgpt_authoring_pack.py"
        stage_script = repo_root / script_root / "stage_chatgpt_authoring_pack.py"

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            tree = _write_authoring_pack_tree(repo / "tree-pack")
            review_output = repo / ".specdock-authoring" / "legacy-review-stage"
            stage_output = repo / ".specdock-authoring" / "legacy-stage"

            review = subprocess.run(
                [
                    sys.executable,
                    str(review_script),
                    "--input",
                    str(tree),
                    "--output-dir",
                    str(review_output),
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )
            stage = subprocess.run(
                [
                    sys.executable,
                    str(stage_script),
                    "--review-report",
                    str(review_output / "validation-report.json"),
                    "--pack-tree",
                    str(tree),
                    "--issue-dir",
                    str(repo / "spec-dock" / "active" / "issue"),
                    "--output-dir",
                    str(stage_output),
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            review_payload = _json_stdout(review)
            stage_payload = _json_stdout(stage)
            report_payload = json.loads((review_output / "validation-report.json").read_text(encoding="utf-8"))
            assert review.returncode == 0, review.stdout + review.stderr
            assert stage.returncode == 0, stage.stdout + stage.stderr
            assert review_payload["status"] == "pass"
            assert report_payload["pack_digest"]["content_sha256"] == _legacy_authoring_tree_digest(tree)
            assert stage_payload["status"] == "pass"
            assert (stage_output / "specdock-authoring-pack" / "manifest.json").is_file()

    def test_authoring_pack_compatibility_stage_honors_legacy_review_report_gate(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        stage_script = (
            repo_root / "src/spec_dock/assets/spec_dock/scripts/authoring-pack/stage_chatgpt_authoring_pack.py"
        )

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            tree = _write_authoring_pack_tree(repo / "tree-pack")
            review_report = repo / "legacy-review.json"
            output_dir = repo / ".specdock-authoring" / "legacy-stage"
            review_report.write_text(json.dumps({"status": "rejected"}, sort_keys=True) + "\n", encoding="utf-8")

            stage = subprocess.run(
                [
                    sys.executable,
                    str(stage_script),
                    "--review-report",
                    str(review_report),
                    "--pack-tree",
                    str(tree),
                    "--issue-dir",
                    str(repo / "spec-dock" / "active" / "issue"),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            payload = _json_stdout(stage)
            assert stage.returncode == 1, stage.stdout + stage.stderr
            assert payload["status"] == "rejected"
            assert "legacy_review_report_not_pass" in payload["findings"]
            assert not (output_dir / "specdock-authoring-pack").exists()

    def test_authoring_pack_compatibility_stage_rejects_stale_legacy_review_report(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        stage_script = (
            repo_root / "src/spec_dock/assets/spec_dock/scripts/authoring-pack/stage_chatgpt_authoring_pack.py"
        )

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            tree = _write_authoring_pack_tree(repo / "tree-pack")
            review_report = repo / "legacy-review.json"
            output_dir = repo / ".specdock-authoring" / "legacy-stage"
            review_report.write_text(
                json.dumps({"status": "pass", "pack_digest": {"content_sha256": "different"}}, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            stage = subprocess.run(
                [
                    sys.executable,
                    str(stage_script),
                    "--review-report",
                    str(review_report),
                    "--pack-tree",
                    str(tree),
                    "--issue-dir",
                    str(repo / "spec-dock" / "active" / "issue"),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            payload = _json_stdout(stage)
            assert stage.returncode == 1, stage.stdout + stage.stderr
            assert payload["status"] == "stale"
            assert "legacy_review_report_not_pass" in payload["findings"]
            assert not (output_dir / "specdock-authoring-pack").exists()

    def test_authoring_pack_compatibility_stage_reviews_input_before_legacy_digest(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        stage_script = (
            repo_root / "src/spec_dock/assets/spec_dock/scripts/authoring-pack/stage_chatgpt_authoring_pack.py"
        )

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack_zip = _write_authoring_pack_zip(
                repo / "oversized.zip",
                extra_entries={"specdock-authoring-pack/issue/large.md": "x" * 2_000_001},
            )
            review_report = repo / "legacy-review.json"
            output_dir = repo / ".specdock-authoring" / "legacy-stage"
            review_report.write_text(
                json.dumps({"status": "pass", "pack_digest": {"content_sha256": "digest"}}, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            stage = subprocess.run(
                [
                    sys.executable,
                    str(stage_script),
                    "--review-report",
                    str(review_report),
                    "--input",
                    str(pack_zip),
                    "--stage-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            payload = _json_stdout(stage)
            assert stage.returncode == 1, stage.stdout + stage.stderr
            assert payload["status"] == "stale"
            assert "legacy_review_report_not_pass" in payload["findings"]
            assert not (output_dir / "specdock-authoring-pack").exists()

    def test_authoring_pack_compatibility_stage_handles_encrypted_zip_digest_without_traceback(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        stage_script = (
            repo_root / "src/spec_dock/assets/spec_dock/scripts/authoring-pack/stage_chatgpt_authoring_pack.py"
        )

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            encrypted_name = "specdock-authoring-pack/issue/requirement.md"
            pack_zip = _write_authoring_pack_zip(repo / "encrypted.zip")
            _mark_zip_entry_encrypted(pack_zip, encrypted_name)
            review_report = repo / "legacy-review.json"
            output_dir = repo / ".specdock-authoring" / "legacy-stage"
            review_report.write_text(
                json.dumps({"status": "pass", "pack_digest": {"content_sha256": "digest"}}, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            stage = subprocess.run(
                [
                    sys.executable,
                    str(stage_script),
                    "--review-report",
                    str(review_report),
                    "--input",
                    str(pack_zip),
                    "--stage-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            payload = _json_stdout(stage)
            assert stage.returncode == 1, stage.stdout + stage.stderr
            assert "traceback" not in stage.stderr.lower()
            assert payload["status"] == "stale"
            assert "legacy_review_report_not_pass" in payload["findings"]
            assert not (output_dir / "specdock-authoring-pack").exists()

    def test_authoring_pack_compatibility_stage_accepts_matching_legacy_review_report(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        stage_script = (
            repo_root / "src/spec_dock/assets/spec_dock/scripts/authoring-pack/stage_chatgpt_authoring_pack.py"
        )

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            tree = _write_authoring_pack_tree(repo / "tree-pack")
            review_report = repo / "legacy-review.json"
            output_dir = repo / ".specdock-authoring" / "legacy-stage"
            review_report.write_text(
                json.dumps(
                    {
                        "status": "pass",
                        "pack_digest": {"content_sha256": _legacy_authoring_tree_digest(tree)},
                    },
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )

            stage = subprocess.run(
                [
                    sys.executable,
                    str(stage_script),
                    "--review-report",
                    str(review_report),
                    "--pack-tree",
                    str(tree),
                    "--issue-dir",
                    str(repo / "spec-dock" / "active" / "issue"),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=str(repo),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            payload = _json_stdout(stage)
            assert stage.returncode == 0, stage.stdout + stage.stderr
            assert payload["status"] == "pass"
            assert (output_dir / "specdock-authoring-pack" / "issue" / "requirement.md").is_file()

    def test_authoring_pack_prepare_generates_deterministic_prompt_pack_from_github_synced_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            preflight = repo / "preflight.json"
            output_one = repo / "pack-one"
            output_two = repo / "pack-two"
            preflight_payload = _run_preflight_json(self, repo)
            preflight.write_text(json.dumps(preflight_payload, sort_keys=True) + "\n", encoding="utf-8")

            first = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "prepare",
                    "--preflight",
                    str(preflight),
                    "--output-dir",
                    str(output_one),
                    "--mode",
                    "issue",
                    "--format",
                    "json",
                ],
            )
            second = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "prepare",
                    "--preflight",
                    str(preflight),
                    "--output-dir",
                    str(output_two),
                    "--mode",
                    "issue",
                    "--format",
                    "json",
                ],
            )

            first_payload = _json_stdout(first)
            assert first.returncode == 0, first.stdout + first.stderr
            assert second.returncode == 0, second.stdout + second.stderr
            assert first_payload["status"] == "pass"
            assert first_payload["authority"] == "evidence_only"
            assert first_payload["adoption_status"] == "unreviewed"
            assert first_payload["bundle_generation_not_promotion"] is True
            assert first_payload["evidence_mode"] == "github-synced"
            assert first_payload["github_sync"] == "verified"

            required_files = {
                ".specdock-authoring-pack",
                "manifest.json",
                "provenance.json",
                "source-manifest.json",
                "stale-if.json",
                "safe-output-constraints.md",
                "chatgpt-use-prompt.md",
                "expected-output-contract.md",
            }
            assert set(first_payload["output_files"]) == required_files
            for rel_path in required_files:
                assert (output_one / rel_path).exists()

            assert _normalized_pack_payload(output_one) == _normalized_pack_payload(output_two)
            manifest = json.loads((output_one / "manifest.json").read_text(encoding="utf-8"))
            assert manifest["expected_output_root"] == "specdock-authoring-pack/"
            assert manifest["authority"] == "evidence_only"
            prompt = (output_one / "chatgpt-use-prompt.md").read_text(encoding="utf-8")
            assert "specdock-authoring-pack/" in prompt
            assert "Do not claim canonical adoption" in prompt

    def test_authoring_pack_prepare_preserves_local_context_lower_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            preflight = repo / "local-preflight.json"
            output_dir = repo / "local-pack"
            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "preflight",
                    "github-sync",
                    "--repo-root",
                    str(repo),
                    "--evidence-mode",
                    "local-context",
                    "--provided-context-path",
                    "source.txt",
                    "--unsynced-reason",
                    "offline review",
                    "--format",
                    "json",
                ],
            )
            preflight_payload = _json_stdout(p)
            preflight.write_text(json.dumps(preflight_payload, sort_keys=True) + "\n", encoding="utf-8")

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "prepare",
                    "--preflight",
                    str(preflight),
                    "--output-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            provenance = json.loads((output_dir / "provenance.json").read_text(encoding="utf-8"))
            assert result.returncode == 0, result.stdout + result.stderr
            assert payload["status"] == "pass"
            assert provenance["sync_state"] == "local_context"
            assert provenance["github_sync"] == "not_verified"
            assert provenance["provided_context_paths"] == ["source.txt"]
            assert provenance["adoption_requires"] == "explicit_eal_disposition"

    def test_authoring_pack_prepare_fails_closed_for_stale_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            preflight = repo / "stale-preflight.json"
            output_dir = repo / "stale-pack"
            payload = _run_preflight_json(self, repo, "--expected-source-hash", "old", expected_returncode=1)
            preflight.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "prepare",
                    "--preflight",
                    str(preflight),
                    "--output-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
            )

            pack_payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert pack_payload["status"] == "stale"
            assert pack_payload["output_files"] == []
            assert (output_dir / "diagnostics.json").is_file()

    def test_authoring_pack_prepare_fails_closed_for_blocked_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            preflight = repo / "blocked-preflight.json"
            output_dir = repo / "blocked-pack"
            payload = _run_preflight_json(self, repo, "--ref", "missing", expected_returncode=1)
            preflight.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "prepare",
                    "--preflight",
                    str(preflight),
                    "--output-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
            )

            pack_payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert pack_payload["status"] == "blocked"
            assert pack_payload["output_files"] == []
            assert not (output_dir / "manifest.json").exists()
            assert (output_dir / "diagnostics.json").is_file()

    def test_authoring_pack_prepare_fails_closed_for_missing_required_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            preflight = repo / "missing-preflight.json"
            output_dir = repo / "missing-pack"
            preflight.write_text(
                json.dumps(
                    {
                        "status": "pass",
                        "evidence_mode": "github-synced",
                        "sync_state": "synced",
                        "github_sync": "verified",
                    },
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "prepare",
                    "--preflight",
                    str(preflight),
                    "--output-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "fail"
            assert "missing_source_manifest_hash" in payload["blockers"]
            assert "missing_source_hashes" in payload["blockers"]
            assert payload["output_files"] == []
            assert not (output_dir / "manifest.json").exists()
            assert (output_dir / "diagnostics.json").is_file()

    def test_authoring_pack_prepare_rejects_inconsistent_source_manifest_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            preflight = repo / "mismatched-preflight.json"
            output_dir = repo / "mismatched-pack"
            preflight.write_text(
                json.dumps(
                    {
                        "status": "pass",
                        "evidence_mode": "github-synced",
                        "sync_state": "synced",
                        "github_sync": "verified",
                        "source_manifest_hash": "old",
                        "source_paths": ["source.txt"],
                        "source_hashes": {"source.txt": "hash"},
                    },
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "prepare",
                    "--preflight",
                    str(preflight),
                    "--output-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "fail"
            assert "source_manifest_hash_mismatch" in payload["blockers"]
            assert payload["output_files"] == []
            assert not (output_dir / "manifest.json").exists()

    def test_authoring_pack_prepare_filters_cache_entries_from_explicit_source_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            preflight = repo / "preflight.json"
            source_manifest = repo / "source-manifest.json"
            output_dir = repo / "pack"
            preflight_payload = _run_preflight_json(self, repo)
            preflight.write_text(json.dumps(preflight_payload, sort_keys=True) + "\n", encoding="utf-8")
            source_manifest.write_text(
                json.dumps(
                    {
                        "source_manifest_hash": "fixture-hash",
                        "source_paths": ["package", "package/__pycache__"],
                        "source_hashes": {
                            "package/module.py": "source",
                            "package/__pycache__/module.cpython-312.pyc": "cache",
                            "package/old.pyo": "cache",
                        },
                    },
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "prepare",
                    "--preflight",
                    str(preflight),
                    "--source-manifest",
                    str(source_manifest),
                    "--output-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            generated = json.loads((output_dir / "source-manifest.json").read_text(encoding="utf-8"))
            assert result.returncode == 0, result.stdout + result.stderr
            assert payload["status"] == "pass"
            assert "package/module.py" in generated["source_hashes"]
            assert all("__pycache__" not in path for path in generated["source_hashes"])
            assert all(not path.endswith((".pyc", ".pyo")) for path in generated["source_hashes"])
            assert "package/__pycache__" not in generated["source_paths"]
            assert generated["source_manifest_hash"] == _manifest_hash(generated["source_hashes"])

    def test_authoring_pack_prepare_rejects_canonical_output_target_and_achieved_claims(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            preflight_payload = _run_preflight_json(self, repo)
            preflight_payload["reviewer_pass"] = True
            preflight = repo / "preflight.json"
            preflight.write_text(json.dumps(preflight_payload, sort_keys=True) + "\n", encoding="utf-8")
            canonical_output = repo / "spec-dock" / "active" / "issue" / "artifacts" / "pack"

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "prepare",
                    "--preflight",
                    str(preflight),
                    "--output-dir",
                    str(canonical_output),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "rejected"
            assert "canonical_output_target" in payload["blockers"]
            assert "forbidden_achieved_claim:reviewer_pass" in payload["blockers"]

    def test_authoring_pack_prepare_rejects_symlinked_output_entries(self) -> None:
        if not hasattr(os, "symlink"):
            pytest.skip("symlink unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            preflight = repo / "preflight.json"
            output_dir = repo / "pack"
            preflight_payload = _run_preflight_json(self, repo)
            preflight.write_text(json.dumps(preflight_payload, sort_keys=True) + "\n", encoding="utf-8")
            output_dir.mkdir()
            target = repo / "spec-dock" / ".assurance.json"
            Path(output_dir / "manifest.json").symlink_to(target)

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "prepare",
                    "--preflight",
                    str(preflight),
                    "--output-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_output_entry_symlink:manifest.json" in payload["blockers"]
            assert not target.exists()

    def test_authoring_pack_prepare_rejects_symlinked_output_dir(self) -> None:
        if not hasattr(os, "symlink"):
            pytest.skip("symlink unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            preflight = repo / "preflight.json"
            outside = repo / "outside"
            output_dir = repo / "pack-link"
            preflight_payload = _run_preflight_json(self, repo)
            preflight.write_text(json.dumps(preflight_payload, sort_keys=True) + "\n", encoding="utf-8")
            outside.mkdir()
            output_dir.symlink_to(outside)

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "prepare",
                    "--preflight",
                    str(preflight),
                    "--output-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_output_dir_symlink" in payload["blockers"]
            assert not (outside / "manifest.json").exists()

    def test_authoring_pack_prepare_rejects_broken_symlinked_output_dir(self) -> None:
        if not hasattr(os, "symlink"):
            pytest.skip("symlink unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            preflight = repo / "preflight.json"
            outside = repo / "missing-outside"
            output_dir = repo / "pack-link"
            preflight_payload = _run_preflight_json(self, repo)
            preflight.write_text(json.dumps(preflight_payload, sort_keys=True) + "\n", encoding="utf-8")
            output_dir.symlink_to(outside)

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "prepare",
                    "--preflight",
                    str(preflight),
                    "--output-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_output_dir_symlink" in payload["blockers"]
            assert not (outside / "manifest.json").exists()

    def test_authoring_pack_prepare_rejects_existing_output_below_symlinked_parent(self) -> None:
        if not hasattr(os, "symlink"):
            pytest.skip("symlink unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            preflight = repo / "preflight.json"
            outside = repo / "outside"
            outside_existing = outside / "existing"
            linked_parent = repo / "linked-parent"
            output_dir = linked_parent / "existing" / "pack"
            preflight_payload = _run_preflight_json(self, repo)
            preflight.write_text(json.dumps(preflight_payload, sort_keys=True) + "\n", encoding="utf-8")
            outside_existing.mkdir(parents=True)
            linked_parent.symlink_to(outside, target_is_directory=True)

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "prepare",
                    "--preflight",
                    str(preflight),
                    "--output-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_output_parent_symlink" in payload["blockers"]
            assert not (outside_existing / "pack" / "manifest.json").exists()
            assert not (outside_existing / "pack" / "diagnostics.json").exists()

    def test_authoring_pack_prepare_rejects_initiatives_root_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            preflight = repo / "preflight.json"
            output_dir = repo / "spec-dock" / "initiatives"
            preflight_payload = _run_preflight_json(self, repo)
            preflight.write_text(json.dumps(preflight_payload, sort_keys=True) + "\n", encoding="utf-8")

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "prepare",
                    "--preflight",
                    str(preflight),
                    "--output-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "rejected"
            assert "canonical_output_target" in payload["blockers"]
            assert not (output_dir / "manifest.json").exists()

    def test_authoring_pack_prepare_reports_non_object_json_inputs_as_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            preflight = repo / "preflight.json"
            source_manifest = repo / "source-manifest.json"
            output_dir = repo / "pack"
            preflight_payload = _run_preflight_json(self, repo)
            preflight.write_text(json.dumps(preflight_payload, sort_keys=True) + "\n", encoding="utf-8")
            source_manifest.write_text("[]\n", encoding="utf-8")

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "prepare",
                    "--preflight",
                    str(preflight),
                    "--source-manifest",
                    str(source_manifest),
                    "--output-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "fail"
            assert "pack_input_unreadable" in payload["blockers"]
            assert (output_dir / "diagnostics.json").is_file()

    def test_authoring_pack_prepare_rejects_symlinked_diagnostics_output(self) -> None:
        if not hasattr(os, "symlink"):
            pytest.skip("symlink unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            preflight = repo / "stale-preflight.json"
            output_dir = repo / "pack"
            output_dir.mkdir()
            target = repo / "spec-dock" / ".assurance.json"
            Path(output_dir / "diagnostics.json").symlink_to(target)
            payload = _run_preflight_json(self, repo, "--expected-source-hash", "old", expected_returncode=1)
            preflight.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "prepare",
                    "--preflight",
                    str(preflight),
                    "--output-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
            )

            pack_payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert pack_payload["status"] == "rejected"
            assert "unsafe_output_entry_symlink:diagnostics.json" in pack_payload["blockers"]
            assert not target.exists()

    def test_authoring_pack_prepare_rejects_unsafe_source_and_context_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            preflight = repo / "unsafe-preflight.json"
            output_dir = repo / "unsafe-pack"
            preflight.write_text(
                json.dumps(
                    {
                        "status": "pass",
                        "evidence_mode": "local-context",
                        "sync_state": "local_context",
                        "github_sync": "not_verified",
                        "source_manifest_hash": _manifest_hash({"../secret.txt": "hash"}),
                        "source_paths": ["/Users/example/private.txt"],
                        "source_hashes": {"../secret.txt": "hash"},
                        "provided_context_paths": [".env"],
                        "unsynced_reason": "unsafe path fixture",
                    },
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "prepare",
                    "--preflight",
                    str(preflight),
                    "--output-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_source_path:/Users/example/private.txt" in payload["blockers"]
            assert "unsafe_source_path:../secret.txt" in payload["blockers"]
            assert "unsafe_source_path:.env" in payload["blockers"]

    def test_authoring_pack_prepare_rejects_unsafe_local_context_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            preflight = repo / "unsafe-text-preflight.json"
            output_dir = repo / "unsafe-text-pack"
            preflight.write_text(
                json.dumps(
                    {
                        "status": "pass",
                        "evidence_mode": "local-context",
                        "sync_state": "local_context",
                        "github_sync": "not_verified",
                        "source_manifest_hash": _manifest_hash({"source.txt": "hash"}),
                        "source_paths": ["source.txt"],
                        "source_hashes": {"source.txt": "hash"},
                        "provided_context_paths": ["source.txt"],
                        "diff_summary": "/Users/example/.env changed",
                        "unsynced_reason": "local token review",
                    },
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "prepare",
                    "--preflight",
                    str(preflight),
                    "--output-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_context_text:diff_summary" in payload["blockers"]
            assert "unsafe_context_text:unsynced_reason" in payload["blockers"]

    def test_authoring_pack_prepare_prompt_guidance_contains_lower_authority_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            preflight = repo / "local-preflight.json"
            output_dir = repo / "pack"
            preflight.write_text(
                (
                    Path(__file__).resolve().parents[2]
                    / "tests/fixtures/authoring_pack/prepare/valid-local-context-preflight.json"
                ).read_text(encoding="utf-8"),
                encoding="utf-8",
            )

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "pack",
                    "prepare",
                    "--preflight",
                    str(preflight),
                    "--output-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
            )

            prompt = (output_dir / "chatgpt-use-prompt.md").read_text(encoding="utf-8")
            assert result.returncode == 0, result.stdout + result.stderr
            assert "sync_state: `local_context`" in prompt
            assert "github_sync: `not_verified`" in prompt
            assert "adoption_requires: `explicit_eal_disposition`" in prompt
            assert "provided_context_paths: `source.txt`" in prompt
            assert "diff_summary: `fixture local diff summary`" in prompt
            assert "unsynced_reason: `fixture local context`" in prompt
            assert "`.assurance.json` mutation" in prompt
            assert "`authorized_profile` decision" in prompt

    def test_authoring_pack_prepare_dogfood_runtime_path_smoke(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "spec-dock" / "scripts" / "spec-dock"
        with tempfile.TemporaryDirectory() as tmp:
            preflight = Path(tmp) / "preflight.json"
            output_dir = Path(tmp) / "pack"
            source_hashes: dict[str, object] = {"source.txt": "hash"}
            preflight.write_text(
                json.dumps(
                    {
                        "status": "pass",
                        "evidence_mode": "local-context",
                        "sync_state": "local_context",
                        "github_sync": "not_verified",
                        "source_manifest_hash": _manifest_hash(source_hashes),
                        "source_paths": ["source.txt"],
                        "source_hashes": source_hashes,
                        "provided_context_paths": ["source.txt"],
                        "unsynced_reason": "dogfood mirror smoke",
                    },
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )

            p = subprocess.run(
                [
                    str(script),
                    "authoring",
                    "pack",
                    "prepare",
                    "--preflight",
                    str(preflight),
                    "--output-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
                cwd=str(repo_root),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert (output_dir / "manifest.json").is_file()

    def test_authoring_backend_invoke_unset_backend_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            output_dir = repo / "invoke-output"

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "blocked"
            assert payload["backend_source"] == "unset"
            assert "backend_command_unset:set_SPECDOCK_CHATGPT_COMMAND" in payload["blockers"]
            assert (output_dir / "invocation-summary.json").is_file()

    def test_authoring_backend_invoke_rejects_symlink_prompt_pack_path(self) -> None:
        if not hasattr(os, "symlink"):
            pytest.skip("symlink unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            link = repo / "pack-link"
            link.symlink_to(pack, target_is_directory=True)
            output_dir = repo / "invoke-output"

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(link),
                    "--output-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "blocked"
            assert "prompt_pack_symlink_path" in payload["blockers"]
            assert (output_dir / "invocation-summary.json").is_file()

    def test_authoring_backend_invoke_rejects_absolute_symlink_prompt_pack_outside_repo(self) -> None:
        if not hasattr(os, "symlink"):
            pytest.skip("symlink unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = _create_synced_git_repo(root)
            pack = _write_valid_prompt_pack(repo / "pack")
            link = root / "external-pack-link"
            link.symlink_to(pack, target_is_directory=True)

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(link),
                    "--output-dir",
                    str(repo / "invoke-output"),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "blocked"
            assert "prompt_pack_symlink_path" in payload["blockers"]

    def test_authoring_backend_invoke_cli_backend_command_overrides_env_and_dry_run_skips_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            output_dir = repo / "invoke-output"
            sentinel = repo / "sentinel.txt"
            backend = _write_fake_backend(repo / "backend.py", sentinel)

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(output_dir),
                    "--backend-command",
                    f"{sys.executable} {backend}",
                    "--slug",
                    "explicit-slug",
                    "--prompt",
                    "literal ; shell text",
                    "--dry-run",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 0, result.stdout + result.stderr
            assert payload["status"] == "pass"
            assert payload["backend_source"] == "cli"
            assert payload["dry_run"] is True
            assert not sentinel.exists()
            assert "--slug" in payload["invocation_argv"]
            assert "explicit-slug" in payload["invocation_argv"]
            assert "-p" in payload["invocation_argv"]
            assert "literal ; shell text" in payload["invocation_argv"]
            assert "--output-dir" not in payload["invocation_argv"]
            assert (output_dir / "invocation-summary.json").is_file()

    def test_authoring_backend_invoke_cli_backend_command_overrides_conflicting_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            cli_backend = _write_fake_backend(repo / "cli.py", repo / "cli.txt")
            primary_backend = _write_fake_backend(repo / "primary.py", repo / "primary.txt")
            fallback_backend = _write_fake_backend(repo / "fallback.py", repo / "fallback.txt")

            result = self._run_runtime_capture(
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(repo / "invoke-output"),
                    "--backend-command",
                    f"{sys.executable} {cli_backend}",
                    "--format",
                    "json",
                ],
                env={
                    "PATH": os.environ.get("PATH", ""),
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "SPECDOCK_CHATGPT_COMMAND": f"{sys.executable} {primary_backend}",
                    "ORACLE_CHATGPT_COMMAND": f"{sys.executable} {fallback_backend}",
                },
            )

            payload = _json_stdout(result)
            assert result.returncode == 0, result.stdout + result.stderr
            assert payload["backend_source"] == "cli"
            assert (repo / "cli.txt").is_file()
            assert not (repo / "primary.txt").exists()
            assert not (repo / "fallback.txt").exists()

    def test_authoring_backend_invoke_passes_argv_without_shell(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            captured = repo / "captured-argv.json"
            backend = _write_fake_backend(repo / "backend.py", captured)

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(repo / "invoke-output"),
                    "--backend-command",
                    f"{sys.executable} {backend}",
                    "--slug",
                    "argv-slug",
                    "--prompt",
                    "literal ; touch should-not-run",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            captured_argv = json.loads(captured.read_text(encoding="utf-8"))
            assert result.returncode == 0, result.stdout + result.stderr
            assert payload["status"] == "pass"
            assert "literal ; touch should-not-run" in captured_argv
            assert "--oracle" not in captured_argv
            assert "--output-dir" not in captured_argv
            assert not (repo / "should-not-run").exists()
            assert captured_argv.count("--file") == 7

    @pytest.mark.parametrize("retired_implementation", ("standard", "personal"))
    def test_authoring_backend_invoke_rejects_retired_oracle_selector(self, retired_implementation: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))

            result = self._run_runtime_capture(
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(repo / "pack"),
                    "--output-dir",
                    str(repo / "invoke-output"),
                    "--oracle",
                    retired_implementation,
                ],
            )

            assert result.returncode == 2
            assert f"unrecognized arguments: --oracle {retired_implementation}" in result.stderr

    def test_authoring_backend_invoke_redacts_summary_argv_and_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            captured = repo / "captured-argv.json"
            backend = _write_fake_backend(repo / "backend.py", captured)
            output_dir = repo / "invoke-output"

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(output_dir),
                    "--backend-command",
                    f"{sys.executable} {backend} --token=secret-value --config=/Users/example/.oracle/config.json --cache=/tmp",
                    "--prompt",
                    "read /private/tmp/local-context.txt and /var/folders",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            summary = json.loads((output_dir / "invocation-summary.json").read_text(encoding="utf-8"))
            assert result.returncode == 0, result.stdout + result.stderr
            assert "--token=secret-value" not in json.dumps(payload)
            assert "--token=secret-value" not in json.dumps(summary)
            assert "/Users/example/.oracle/config.json" not in json.dumps(summary)
            assert "/private/tmp/local-context.txt" not in json.dumps(summary)
            assert "--cache=/tmp" not in json.dumps(summary)
            assert "/var/folders" not in json.dumps(summary)
            assert str(pack.resolve()) not in json.dumps(summary)
            assert "[redacted]" in summary["backend_argv"]
            assert "[redacted]" in summary["invocation_argv"]

    def test_authoring_backend_invoke_redacts_separate_secret_option_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            output_dir = repo / "invoke-output"
            captured = repo / "captured-argv.json"
            backend = _write_fake_backend(repo / "backend.py", captured)

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(output_dir),
                    "--backend-command",
                    f"{sys.executable} {backend} --token abc123 --password hunter2 --api-key rawkey",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            summary = json.loads((output_dir / "invocation-summary.json").read_text(encoding="utf-8"))
            serialized = json.dumps(payload)
            summary_serialized = json.dumps(summary)
            assert result.returncode == 0, result.stdout + result.stderr
            assert "abc123" not in serialized
            assert "hunter2" not in serialized
            assert "rawkey" not in serialized
            assert "abc123" not in summary_serialized
            assert "hunter2" not in summary_serialized
            assert "rawkey" not in summary_serialized
            assert summary["backend_argv"].count("[redacted]") >= 3
            assert summary["invocation_argv"].count("[redacted]") >= 3

    def test_authoring_backend_invoke_primary_env_precedes_oracle_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            output_dir = repo / "invoke-output"
            primary_backend = _write_fake_backend(repo / "primary.py", repo / "primary.txt")
            fallback_backend = _write_fake_backend(repo / "fallback.py", repo / "fallback.txt")

            result = self._run_runtime_capture(
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(output_dir),
                    "--format",
                    "json",
                ],
                env={
                    "PATH": os.environ.get("PATH", ""),
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "SPECDOCK_CHATGPT_COMMAND": f"{sys.executable} {primary_backend}",
                    "ORACLE_CHATGPT_COMMAND": f"{sys.executable} {fallback_backend}",
                },
            )

            payload = _json_stdout(result)
            assert result.returncode == 0, result.stdout + result.stderr
            assert payload["backend_source"] == "env:SPECDOCK_CHATGPT_COMMAND"
            assert payload["compatibility_fallback"] is False
            assert (repo / "primary.txt").is_file()
            assert not (repo / "fallback.txt").exists()

    def test_authoring_backend_invoke_oracle_fallback_when_primary_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            fallback_backend = _write_fake_backend(repo / "fallback.py", repo / "fallback.txt")

            result = self._run_runtime_capture(
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(repo / "invoke-output"),
                    "--format",
                    "json",
                ],
                env={
                    "PATH": os.environ.get("PATH", ""),
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "SPECDOCK_CHATGPT_COMMAND": "",
                    "ORACLE_CHATGPT_COMMAND": f"{sys.executable} {fallback_backend}",
                },
            )

            payload = _json_stdout(result)
            assert result.returncode == 0, result.stdout + result.stderr
            assert payload["backend_source"] == "env:ORACLE_CHATGPT_COMMAND"
            assert payload["compatibility_fallback"] is True
            assert (repo / "fallback.txt").is_file()

    def test_authoring_backend_invoke_missing_metadata_and_unsafe_output_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            (pack / "manifest.json").write_text("{}", encoding="utf-8")

            missing = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(repo / "invoke-output"),
                    "--backend-command",
                    sys.executable,
                    "--format",
                    "json",
                ],
            )
            missing_payload = _json_stdout(missing)
            assert missing.returncode == 1, missing.stdout + missing.stderr
            assert missing_payload["status"] == "blocked"
            assert "missing_manifest_field:schema_version" in missing_payload["blockers"]

    def test_authoring_backend_invoke_invalid_utf8_metadata_returns_json_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            (pack / "manifest.json").write_bytes(b"\xff")

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(repo / "invoke-output"),
                    "--backend-command",
                    sys.executable,
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "blocked"
            assert "manifest_json_unreadable" in payload["blockers"]

    def test_authoring_backend_invoke_rejects_manifest_files_outside_prompt_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            manifest_path = pack / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"].extend(["../source.txt", str(repo / "source.txt")])
            manifest_path.write_text(json.dumps(manifest, sort_keys=True) + "\n", encoding="utf-8")

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(repo / "invoke-output"),
                    "--backend-command",
                    sys.executable,
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "blocked"
            assert "unsafe_manifest_file:parent-traversal" in payload["blockers"]
            assert "unsafe_manifest_file:absolute-path" in payload["blockers"]
            assert str(repo / "source.txt") not in json.dumps(payload)

    def test_authoring_backend_invoke_rejects_unsafe_output_target_with_valid_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")

            unsafe = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(repo / "spec-dock" / "active" / "issue" / "artifacts" / "invoke"),
                    "--backend-command",
                    sys.executable,
                    "--format",
                    "json",
                ],
            )
            unsafe_payload = _json_stdout(unsafe)
            assert unsafe.returncode == 1, unsafe.stdout + unsafe.stderr
            assert unsafe_payload["status"] == "rejected"
            assert "canonical_output_target" in unsafe_payload["blockers"]

    def test_authoring_backend_invoke_rejects_file_output_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            output_file = repo / "invoke-output"
            output_file.write_text("not a directory\n", encoding="utf-8")

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(output_file),
                    "--backend-command",
                    sys.executable,
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            serialized = json.dumps(payload)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_output_dir_not_directory" in payload["blockers"]
            assert str(output_file) not in serialized

    def test_authoring_backend_invoke_rejects_symlinked_output_parent(self) -> None:
        if not hasattr(os, "symlink"):
            pytest.skip("symlink unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            canonical = repo / "spec-dock" / "active" / "issue" / "artifacts"
            canonical.mkdir(parents=True, exist_ok=True)
            link = repo / "out-link"
            Path(link).symlink_to(canonical)

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(link / "nested"),
                    "--backend-command",
                    sys.executable,
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "rejected"
            assert "canonical_output_target" in payload["blockers"]
            assert "unsafe_output_parent_symlink" in payload["blockers"]

    def test_authoring_backend_invoke_rejects_noncanonical_symlinked_output_parent(self) -> None:
        if not hasattr(os, "symlink"):
            pytest.skip("symlink unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            target = repo / "ordinary-output-root"
            target.mkdir()
            link = repo / "ordinary-output-link"
            Path(link).symlink_to(target)

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(link / "nested"),
                    "--backend-command",
                    sys.executable,
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_output_parent_symlink" in payload["blockers"]
            assert not (target / "nested" / "invocation-summary.json").exists()

    def test_authoring_backend_invoke_rejects_relative_symlinked_output_parent(self) -> None:
        if not hasattr(os, "symlink"):
            pytest.skip("symlink unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            target = repo / "ordinary-output-root"
            target.mkdir()
            link = repo / "relative-output-link"
            Path(link).symlink_to(target)

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    "relative-output-link/nested",
                    "--backend-command",
                    sys.executable,
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_output_parent_symlink" in payload["blockers"]
            assert not (target / "nested" / "invocation-summary.json").exists()

    def test_authoring_backend_invoke_blocks_missing_prompt_pack_and_prompt_file_symlink(self) -> None:
        if not hasattr(os, "symlink"):
            pytest.skip("symlink unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            missing = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(repo / "missing-pack"),
                    "--output-dir",
                    str(repo / "invoke-output"),
                    "--backend-command",
                    sys.executable,
                    "--format",
                    "json",
                ],
            )
            missing_payload = _json_stdout(missing)
            assert missing.returncode == 1, missing.stdout + missing.stderr
            assert missing_payload["status"] == "blocked"
            assert "prompt_pack_missing" in missing_payload["blockers"]

            pack = _write_valid_prompt_pack(repo / "pack")
            (pack / "chatgpt-use-prompt.md").unlink()
            Path(pack / "chatgpt-use-prompt.md").symlink_to(repo / "source.txt")
            symlinked = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(repo / "symlink-output"),
                    "--backend-command",
                    sys.executable,
                    "--format",
                    "json",
                ],
            )
            symlinked_payload = _json_stdout(symlinked)
            assert symlinked.returncode == 1, symlinked.stdout + symlinked.stderr
            assert symlinked_payload["status"] == "blocked"
            assert "unsafe_prompt_pack_file_symlink:chatgpt-use-prompt.md" in symlinked_payload["blockers"]

    def test_authoring_backend_invoke_malformed_command_blocks_without_shell(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(repo / "invoke-output"),
                    "--backend-command",
                    '"unterminated',
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "blocked"
            assert "malformed_backend_command:cli" in payload["blockers"]

    def test_authoring_backend_invoke_timeout_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            slow_backend = repo / "slow_backend.py"
            slow_backend.write_text("import time\ntime.sleep(3)\n", encoding="utf-8")

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(repo / "invoke-output"),
                    "--backend-command",
                    f"{sys.executable} {slow_backend}",
                    "--timeout-seconds",
                    "0.01",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "blocked"
            assert "backend_timeout" in payload["blockers"]

    def test_authoring_backend_invoke_backend_os_error_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            non_executable = repo / "not-executable.py"
            non_executable.write_text("print('nope')\n", encoding="utf-8")

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(repo / "invoke-output"),
                    "--backend-command",
                    str(non_executable),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "blocked"
            assert "backend_os_error" in payload["blockers"]

    def test_authoring_backend_invoke_missing_executable_blocks_with_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            output_dir = repo / "invoke-output"

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(output_dir),
                    "--backend-command",
                    str(repo / "missing-executable"),
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            summary = json.loads((output_dir / "invocation-summary.json").read_text(encoding="utf-8"))
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "blocked"
            assert "backend_command_not_found" in payload["blockers"]
            assert summary["status"] == "blocked"

    def test_authoring_backend_invoke_rejects_symlinked_summary(self) -> None:
        if not hasattr(os, "symlink"):
            pytest.skip("symlink unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            output_dir = repo / "invoke-output"
            output_dir.mkdir()
            target = repo / "spec-dock" / ".assurance.json"
            Path(output_dir / "invocation-summary.json").symlink_to(target)

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(output_dir),
                    "--backend-command",
                    sys.executable,
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "rejected"
            assert "unsafe_output_entry:invocation-summary.json" in payload["blockers"]
            assert not target.exists()

    def test_authoring_backend_invoke_rejects_secret_manifest_attachment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            manifest_path = pack / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"] = [*manifest["files"], "secrets/token.txt"]
            manifest_path.write_text(json.dumps(manifest, sort_keys=True) + "\n", encoding="utf-8")
            (pack / "secrets").mkdir()
            (pack / "secrets" / "token.txt").write_text("token\n", encoding="utf-8")

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(repo / "invoke-output"),
                    "--backend-command",
                    sys.executable,
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "blocked"
            assert "unsafe_manifest_file:secret-path:secrets/token.txt" in payload["blockers"]

    @pytest.mark.parametrize(
        "relative_path",
        ("id_rsa", "keys/private_key.txt", "certificates/key.pem", "legacy-attachments/000-.env"),
    )
    def test_authoring_backend_invoke_rejects_credential_like_manifest_attachments(self, relative_path: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            attachment = pack / relative_path
            attachment.parent.mkdir(parents=True, exist_ok=True)
            attachment.write_text("credential material\n", encoding="utf-8")
            manifest_path = pack / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"] = [*manifest["files"], relative_path]
            manifest_path.write_text(json.dumps(manifest, sort_keys=True) + "\n", encoding="utf-8")
            sentinel = repo / "backend-called.json"
            backend = _write_fake_backend(repo / "backend.py", sentinel)

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(repo / "invoke-output"),
                    "--backend-command",
                    f"{sys.executable} {backend}",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "blocked"
            assert any(item.startswith("unsafe_manifest_file:secret-path:") for item in payload["blockers"])
            assert not sentinel.exists()

    def test_authoring_backend_invoke_rejects_unsynced_github_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            provenance_path = pack / "provenance.json"
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            provenance["github_sync"] = "failed"
            provenance["sync_state"] = "blocked"
            provenance_path.write_text(json.dumps(provenance, sort_keys=True) + "\n", encoding="utf-8")

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(repo / "invoke-output"),
                    "--backend-command",
                    sys.executable,
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "blocked"
            assert "provenance_github_sync_not_verified" in payload["blockers"]
            assert "provenance_sync_state_not_synced" in payload["blockers"]

    def test_authoring_backend_invoke_backend_non_zero_timeout_redaction_and_local_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack", evidence_mode="local-context")
            failing_backend = repo / "fail_backend.py"
            failing_backend.write_text(
                "import sys\n"
                "print('secret=/Users/example/.env token=abc123 password=hunter2 key=rawkey sk-testsecret12345')\n"
                "print('DATABASE_PASSWORD=hunter2 MY_API_KEY=rawkey SERVICE_TOKEN=abc123 CUSTOM_SECRET=value')\n"
                "print('--token abc123 --password hunter2 --api-key rawkey')\n"
                "print('--secret value --credential rawcred', file=sys.stderr)\n"
                "print('ghp_abcdefghijklmnop xoxb-1234567890-secret AKIAABCDEFGHIJKLMNOP')\n"
                "print('/private/tmp/file /tmp /tmp/raw-local /var/folders /var/folders/raw-local', file=sys.stderr)\n"
                "raise SystemExit(7)\n",
                encoding="utf-8",
            )

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(repo / "invoke-output"),
                    "--backend-command",
                    f"{sys.executable} {failing_backend}",
                    "--evidence-mode",
                    "local-context",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            summary = json.loads((repo / "invoke-output" / "invocation-summary.json").read_text(encoding="utf-8"))
            serialized = json.dumps(payload)
            summary_serialized = json.dumps(summary)
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "blocked"
            assert "backend_exit_code:7" in payload["blockers"]
            assert payload["local_context_requires_eal_disposition"] is True
            assert payload["stdout"] == ""
            assert payload["stderr"] == ""
            assert payload["stdout_bytes"] > 0
            assert payload["stderr_bytes"] > 0
            assert payload["stream_output_disposition"] == "not_persisted"
            assert summary["stream_output_disposition"] == "not_persisted"
            assert "/Users/example/.env" not in serialized
            assert "token=abc123" not in serialized
            assert "password=hunter2" not in serialized
            assert "key=rawkey" not in serialized
            assert "DATABASE_PASSWORD=hunter2" not in serialized
            assert "MY_API_KEY=rawkey" not in serialized
            assert "SERVICE_TOKEN=abc123" not in serialized
            assert "CUSTOM_SECRET=value" not in serialized
            assert "--token abc123" not in serialized
            assert "--password hunter2" not in serialized
            assert "--api-key rawkey" not in serialized
            assert "--secret value" not in serialized
            assert "--credential rawcred" not in serialized
            assert "ghp_abcdefghijklmnop" not in serialized
            assert "xoxb-1234567890-secret" not in serialized
            assert "AKIAABCDEFGHIJKLMNOP" not in serialized
            assert "/Users/example/.env" not in summary_serialized
            assert "token=abc123" not in summary_serialized
            assert "password=hunter2" not in summary_serialized
            assert "key=rawkey" not in summary_serialized
            assert "DATABASE_PASSWORD=hunter2" not in summary_serialized
            assert "MY_API_KEY=rawkey" not in summary_serialized
            assert "SERVICE_TOKEN=abc123" not in summary_serialized
            assert "CUSTOM_SECRET=value" not in summary_serialized
            assert "--token abc123" not in summary_serialized
            assert "--password hunter2" not in summary_serialized
            assert "--api-key rawkey" not in summary_serialized
            assert "--secret value" not in summary_serialized
            assert "--credential rawcred" not in summary_serialized
            assert "ghp_abcdefghijklmnop" not in summary_serialized
            assert "xoxb-1234567890-secret" not in summary_serialized
            assert "AKIAABCDEFGHIJKLMNOP" not in summary_serialized
            assert " /tmp " not in payload["stderr"]
            assert "/tmp/raw-local" not in payload["stderr"]
            assert "/var/folders " not in payload["stderr"]
            assert "/var/folders/raw-local" not in payload["stderr"]

    def test_authoring_backend_invoke_decodes_non_utf8_backend_streams(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            pack = _write_valid_prompt_pack(repo / "pack")
            backend = repo / "non_utf8_backend.py"
            output_dir = repo / "invoke-output"
            backend.write_text(
                "import sys\n"
                "sys.stdout.buffer.write(b'prefix-\\xff-suffix')\n"
                "sys.stderr.buffer.write(b'err-\\xfe')\n"
                "raise SystemExit(9)\n",
                encoding="utf-8",
            )

            result = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(output_dir),
                    "--backend-command",
                    f"{sys.executable} {backend}",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(result)
            summary = json.loads((output_dir / "invocation-summary.json").read_text(encoding="utf-8"))
            assert result.returncode == 1, result.stdout + result.stderr
            assert payload["status"] == "blocked"
            assert "backend_exit_code:9" in payload["blockers"]
            assert payload["stdout"] == ""
            assert payload["stderr"] == ""
            assert payload["stdout_bytes"] > 0
            assert payload["stderr_bytes"] > 0
            assert payload["stream_output_disposition"] == "not_persisted"
            assert summary["stdout"] == ""
            assert summary["stderr"] == ""

    def test_authoring_backend_invoke_dogfood_runtime_path_smoke(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "spec-dock" / "scripts" / "spec-dock"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = _write_valid_prompt_pack(root / "pack")
            backend = _write_fake_backend(root / "backend.py", root / "sentinel.txt")

            p = subprocess.run(
                [
                    str(script),
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(root / "invoke-output"),
                    "--backend-command",
                    f"{sys.executable} {backend}",
                    "--format",
                    "json",
                ],
                cwd=str(repo_root),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert (root / "sentinel.txt").is_file()

    def test_authoring_backend_invoke_dogfood_runtime_rejects_unsafe_manifest_files(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "spec-dock" / "scripts" / "spec-dock"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = _write_valid_prompt_pack(root / "pack")
            manifest_path = pack / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"].extend(["../outside.txt", str(root / "outside.txt")])
            manifest_path.write_text(json.dumps(manifest, sort_keys=True) + "\n", encoding="utf-8")

            p = subprocess.run(
                [
                    str(script),
                    "authoring",
                    "backend",
                    "invoke",
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(root / "invoke-output"),
                    "--backend-command",
                    sys.executable,
                    "--format",
                    "json",
                ],
                cwd=str(repo_root),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "blocked"
            assert "unsafe_manifest_file:parent-traversal" in payload["blockers"]
            assert "unsafe_manifest_file:absolute-path" in payload["blockers"]
            assert str(root / "outside.txt") not in json.dumps(payload)

    def test_authoring_backend_invoke_compatibility_script_smoke(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        script = (
            repo_root
            / "src"
            / "spec_dock"
            / "assets"
            / "spec_dock"
            / "scripts"
            / "authoring-pack"
            / "invoke_chatgpt_backend.py"
        )
        dogfood_script = repo_root / "spec-dock" / "scripts" / "authoring-pack" / "invoke_chatgpt_backend.py"
        assert os.access(script, os.X_OK)
        assert os.access(dogfood_script, os.X_OK)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = _write_valid_prompt_pack(root / "pack")
            captured = root / "captured.json"
            backend = _write_fake_backend(root / "backend.py", captured)

            p = self._run_wrapper_capture(
                script,
                [
                    "--prompt-pack",
                    str(pack),
                    "--output-dir",
                    str(root / "invoke-output"),
                    "--backend-command",
                    f"{sys.executable} {backend}",
                    "--slug",
                    "compat-slug",
                    "--prompt",
                    "compat prompt",
                    "--format",
                    "json",
                ],
                env={
                    "PATH": os.environ.get("PATH", ""),
                    "PYTHONDONTWRITEBYTECODE": "1",
                },
                cwd=repo_root,
            )

            payload = _json_stdout(p)
            captured_argv = json.loads(captured.read_text(encoding="utf-8"))
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert captured_argv[:2] == ["--slug", "compat-slug"]
            assert "--oracle" not in captured_argv
            assert "--slug" in captured_argv
            assert "compat-slug" in captured_argv
            assert "-p" in captured_argv
            assert "compat prompt" in captured_argv
            assert captured_argv.count("--file") == 7
            assert (root / "invoke-output" / "invocation-summary.json").is_file()

    @pytest.mark.parametrize("retired_implementation", ("standard", "personal"))
    def test_authoring_backend_invoke_compatibility_script_rejects_retired_oracle_selector(
        self, retired_implementation: str
    ) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        script = (
            repo_root
            / "src"
            / "spec_dock"
            / "assets"
            / "spec_dock"
            / "scripts"
            / "authoring-pack"
            / "invoke_chatgpt_backend.py"
        )

        p = self._run_wrapper_capture(
            script,
            ["--oracle", retired_implementation],
            env={
                "PATH": os.environ.get("PATH", ""),
                "PYTHONDONTWRITEBYTECODE": "1",
            },
            cwd=repo_root,
        )

        assert p.returncode == 2
        assert f"unrecognized arguments: --oracle {retired_implementation}" in p.stderr

    def test_authoring_backend_invoke_compatibility_script_legacy_file_mode(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        script = (
            repo_root
            / "src"
            / "spec_dock"
            / "assets"
            / "spec_dock"
            / "scripts"
            / "authoring-pack"
            / "invoke_chatgpt_backend.py"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prompt = root / "prompt.md"
            contract = root / "contract.md"
            extra = root / "extra.md"
            captured = root / "captured.json"
            backend = _write_fake_backend(root / "backend.py", captured)
            prompt.write_text("legacy prompt\n", encoding="utf-8")
            contract.write_text("legacy contract\n", encoding="utf-8")
            extra.write_text("legacy extra\n", encoding="utf-8")

            p = self._run_wrapper_capture(
                script,
                [
                    "--slug",
                    "legacy-slug",
                    "-p",
                    "legacy prompt text",
                    "--file",
                    str(prompt),
                    "--file",
                    str(contract),
                    "--file",
                    str(extra),
                    "--backend-command",
                    f"{sys.executable} {backend}",
                    "--format",
                    "json",
                ],
                env={
                    "PATH": os.environ.get("PATH", ""),
                    "PYTHONDONTWRITEBYTECODE": "1",
                },
                cwd=repo_root,
            )

            payload = _json_stdout(p)
            captured_argv = json.loads(captured.read_text(encoding="utf-8"))
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert "legacy-slug" in captured_argv
            assert "legacy prompt text" in captured_argv
            assert captured_argv.count("--file") == 10
            assert any("extra.md" in item for item in captured_argv)

    def test_authoring_backend_invoke_compatibility_script_legacy_prompt_only_mode(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        script = (
            repo_root
            / "src"
            / "spec_dock"
            / "assets"
            / "spec_dock"
            / "scripts"
            / "authoring-pack"
            / "invoke_chatgpt_backend.py"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            captured = root / "captured.json"
            backend = _write_fake_backend(root / "backend.py", captured)

            p = self._run_wrapper_capture(
                script,
                [
                    "--slug",
                    "legacy-slug",
                    "-p",
                    "legacy prompt text",
                    "--backend-command",
                    f"{sys.executable} {backend}",
                    "--format",
                    "json",
                ],
                env={
                    "PATH": os.environ.get("PATH", ""),
                    "PYTHONDONTWRITEBYTECODE": "1",
                },
                cwd=repo_root,
            )

            payload = _json_stdout(p)
            captured_argv = json.loads(captured.read_text(encoding="utf-8"))
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert "legacy-slug" in captured_argv
            assert "legacy prompt text" in captured_argv
            assert captured_argv.count("--file") == 7

    def test_authoring_backend_invoke_compatibility_script_legacy_file_mode_blocks_missing_file(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        script = (
            repo_root
            / "src"
            / "spec_dock"
            / "assets"
            / "spec_dock"
            / "scripts"
            / "authoring-pack"
            / "invoke_chatgpt_backend.py"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            backend = _write_fake_backend(root / "backend.py", root / "captured.json")

            p = self._run_wrapper_capture(
                script,
                [
                    "--slug",
                    "legacy-slug",
                    "-p",
                    "legacy prompt text",
                    "--file",
                    str(root / "missing.md"),
                    "--backend-command",
                    f"{sys.executable} {backend}",
                    "--format",
                    "json",
                ],
                env={
                    "PATH": os.environ.get("PATH", ""),
                    "PYTHONDONTWRITEBYTECODE": "1",
                },
                cwd=repo_root,
            )

            assert p.returncode != 0
            assert "legacy --file attachment is not a readable file" in p.stderr

    def test_authoring_backend_invoke_compatibility_script_blocks_credential_like_legacy_file(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        script = (
            repo_root
            / "src"
            / "spec_dock"
            / "assets"
            / "spec_dock"
            / "scripts"
            / "authoring-pack"
            / "invoke_chatgpt_backend.py"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = _create_synced_git_repo(root)
            attachment = repo / ".env"
            attachment.write_text("SECRET_VALUE=not-forwarded\n", encoding="utf-8")
            sentinel = repo / "captured.json"
            backend = _write_fake_backend(repo / "backend.py", sentinel)

            p = self._run_wrapper_capture(
                script,
                [
                    "--file",
                    str(attachment),
                    "--backend-command",
                    f"{sys.executable} {backend}",
                    "--format",
                    "json",
                ],
                env={"PATH": os.environ.get("PATH", ""), "PYTHONDONTWRITEBYTECODE": "1"},
                cwd=repo,
            )

            assert p.returncode != 0
            assert "forbidden credential-like path" in p.stderr
            assert "SECRET_VALUE" not in p.stderr
            assert not sentinel.exists()

    def test_authoring_backend_invoke_compatibility_script_rejects_symlinked_legacy_file(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "src/spec_dock/assets/spec_dock/scripts/authoring-pack/invoke_chatgpt_backend.py"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = _create_synced_git_repo(root)
            outside = root / "outside.md"
            outside.write_text("not forwarded\n", encoding="utf-8")
            attachment = repo / "notes.md"
            attachment.symlink_to(outside)
            sentinel = repo / "captured.json"
            backend = _write_fake_backend(repo / "backend.py", sentinel)

            p = self._run_wrapper_capture(
                script,
                [
                    "--file",
                    str(attachment),
                    "--backend-command",
                    f"{sys.executable} {backend}",
                    "--format",
                    "json",
                ],
                env={"PATH": os.environ.get("PATH", ""), "PYTHONDONTWRITEBYTECODE": "1"},
                cwd=repo,
            )

            assert p.returncode != 0
            assert "must not be a symlink" in p.stderr
            assert "not forwarded" not in p.stderr
            assert not sentinel.exists()

    def test_authoring_backend_invoke_compatibility_script_rejects_symlink_ancestor_escape(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "src/spec_dock/assets/spec_dock/scripts/authoring-pack/invoke_chatgpt_backend.py"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = _create_synced_git_repo(root)
            outside_dir = root / "outside"
            outside_dir.mkdir()
            (outside_dir / "notes.md").write_text("not forwarded\n", encoding="utf-8")
            (repo / "linked").symlink_to(outside_dir, target_is_directory=True)
            attachment = repo / "linked" / "notes.md"
            sentinel = repo / "captured.json"
            backend = _write_fake_backend(repo / "backend.py", sentinel)

            p = self._run_wrapper_capture(
                script,
                [
                    "--file",
                    str(attachment),
                    "--backend-command",
                    f"{sys.executable} {backend}",
                    "--format",
                    "json",
                ],
                env={"PATH": os.environ.get("PATH", ""), "PYTHONDONTWRITEBYTECODE": "1"},
                cwd=repo,
            )

            assert p.returncode != 0
            assert "resolves outside the repository" in p.stderr
            assert "not forwarded" not in p.stderr
            assert not sentinel.exists()


def _run_preflight_json(
    testcase: CliRuntimeHarness,
    repo: Path,
    *extra_args: str,
    expected_returncode: int = 0,
) -> dict[str, Any]:
    p = _run_authoring_capture(
        testcase,
        repo,
        [
            "authoring",
            "preflight",
            "github-sync",
            "--repo-root",
            str(repo),
            "--source-path",
            "source.txt",
            "--format",
            "json",
            *extra_args,
        ],
    )
    assert p.returncode == expected_returncode, p.stdout + p.stderr
    return _json_stdout(p)


def _run_authoring_capture(
    testcase: CliRuntimeHarness, repo: Path, args: list[str]
) -> subprocess.CompletedProcess[str]:
    return testcase._run_runtime_capture(
        repo,
        args,
        env={"PATH": os.environ.get("PATH", ""), "PYTHONDONTWRITEBYTECODE": "1"},
    )


def _run_authoring_capture_from_cwd(
    testcase: CliRuntimeHarness, repo: Path, cwd: Path, args: list[str]
) -> subprocess.CompletedProcess[str]:
    script = repo / "spec-dock" / "scripts" / "spec-dock"
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=str(cwd),
        env=testcase._runtime_env(repo, {"PATH": os.environ.get("PATH", ""), "PYTHONDONTWRITEBYTECODE": "1"}),
        capture_output=True,
        text=True,
    )


def _json_stdout(p: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    try:
        payload = json.loads(p.stdout)
    except json.JSONDecodeError as error:
        raise AssertionError(p.stdout + p.stderr) from error
    assert isinstance(payload, dict)
    return payload


def _protected_tree_snapshot(repo: Path) -> dict[str, str]:
    protected_root = repo / "spec-dock"
    snapshot: dict[str, str] = {}
    for path in sorted(item for item in protected_root.rglob("*") if item.is_file() and not item.is_symlink()):
        snapshot[path.relative_to(protected_root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snapshot


def _assert_text_output_preserves_draft_validation_boundary(output: str) -> None:
    lowered = output.lower()
    assert "authority=evidence_only" in lowered
    assert "adoption_status=unreviewed" in lowered
    assert "canonical_written=false" in lowered
    assert "assurance_mutated=false" in lowered
    assert "execution_ready=false" in lowered
    assert "pr_ready=false" in lowered
    assert "canonical adoption" not in lowered
    assert "adopted" not in lowered
    assert "reviewer pass" not in lowered
    assert "execution-ready" not in lowered
    assert "execution ready" not in lowered
    assert "pr-ready" not in lowered
    assert "pr ready" not in lowered
    assert "execution_ready=true" not in lowered
    assert "pr_ready=true" not in lowered


def _run_issue_draft_adoption_json(
    testcase: CliRuntimeHarness,
    repo: Path,
    fixture: dict[str, str | Path],
    *extra_args: str,
    expected_returncode: int = 1,
) -> dict[str, Any]:
    p = _run_authoring_capture(
        testcase,
        repo,
        [
            "authoring",
            "validate",
            "issue-draft-adoption",
            "--input",
            str(fixture["input"]),
            "--issue-dir",
            str(fixture["issue_dir"]),
            "--review-report",
            str(fixture["review_report"]),
            "--format",
            "json",
            *extra_args,
        ],
    )
    assert p.returncode == expected_returncode, p.stdout + p.stderr
    return _json_stdout(p)


def _run_selected_skeleton_fill_json(
    testcase: CliRuntimeHarness,
    repo: Path,
    fixture: dict[str, Path],
    *extra_args: str,
    expected_returncode: int = 1,
) -> dict[str, Any]:
    p = _run_authoring_capture(
        testcase,
        repo,
        [
            "authoring",
            "validate",
            "selected-skeleton-fill",
            "--input",
            str(fixture["input"]),
            "--issue-dir",
            str(fixture["issue_dir"]),
            "--assurance",
            str(fixture["assurance"]),
            "--selected-skeleton",
            str(fixture["selected_skeleton"]),
            "--review-report",
            str(fixture["review_report"]),
            "--format",
            "json",
            *extra_args,
        ],
    )
    assert p.returncode == expected_returncode, p.stdout + p.stderr
    return _json_stdout(p)


def _normalized_pack_payload(pack_dir: Path) -> dict[str, str]:
    payload: dict[str, str] = {}
    for path in sorted(item for item in pack_dir.rglob("*") if item.is_file()):
        rel_path = path.relative_to(pack_dir).as_posix()
        payload[rel_path] = path.read_text(encoding="utf-8") if path.stat().st_size else ""
    return payload


def _protected_specdock_snapshot(repo: Path) -> dict[str, str]:
    protected_paths = [
        repo / "spec-dock" / "active" / scope / name
        for scope in ("initiative", "epic", "issue")
        for name in ("requirement.md", "design.md", "plan.md")
    ]
    protected_paths.extend(sorted((repo / "spec-dock").rglob(".assurance.json")))
    snapshot: dict[str, str] = {}
    for path in protected_paths:
        if path.exists() and path.is_file():
            snapshot[path.relative_to(repo).as_posix()] = path.read_text(encoding="utf-8")
    return snapshot


def _write_authoring_pack_tree(pack_dir: Path) -> Path:
    root = pack_dir / "specdock-authoring-pack"
    entries = _authoring_pack_entries()
    for name, value in entries.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")
    return pack_dir


def _legacy_authoring_tree_digest(pack_dir: Path) -> str:
    root = pack_dir / "specdock-authoring-pack"
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        rel_path = path.relative_to(root).as_posix()
        digest.update(rel_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_text(encoding="utf-8").encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def _write_legacy_review_fixture(repo: Path, *, status: str = "pass") -> tuple[Path, Path]:
    source_path = "source.txt"
    source_sha = hashlib.sha256((repo / source_path).read_bytes()).hexdigest()
    repository = {
        "full_name": "local/spec-dock-test",
        "requested_ref": "main",
        "observed_ref": "main",
    }
    source = {"path": source_path, "sha256": source_sha, "role": "context"}
    stale_if = [{"kind": "source_hash_changed", "source_paths": [source_path]}]
    preflight = repo / "legacy-preflight.json"
    preflight.write_text(
        json.dumps(
            {
                "authority": "evidence_only",
                "adoption_status": "unreviewed",
                "bundle_generation_not_promotion": True,
                "status": status,
                "repository": repository,
                "sources": [source],
                "stale_if": stale_if,
                "safe_output_constraints": {
                    "expected_zip_root": "specdock-authoring-pack/",
                    "forbidden_claims": ["reviewer pass", "authority: canonical"],
                },
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    entries = {
        "manifest.json": {
            "authority": "evidence_only",
            "adoption_status": "unreviewed",
            "bundle_generation_not_promotion": True,
            "pack_id": "legacy-test-pack",
            "expected_zip_root": "specdock-authoring-pack/",
            "schema_version": "1",
        },
        "provenance.json": {
            "authority": "evidence_only",
            "repository": repository,
            "source": "chatgpt_zip_authoring_pack",
        },
        "source-manifest.json": {"sources": [source]},
        "stale-if.json": {"stale_if": stale_if},
        "adoption/adoption-map.json": {
            "items": [
                {
                    "source_path": source_path,
                    "target": "evidence-only",
                    "adoption_status": "unreviewed",
                    "required_local_validation": ["spec-reviewer"],
                }
            ]
        },
    }
    pack_zip = repo / "legacy-valid.zip"
    with zipfile.ZipFile(pack_zip, "w") as archive:
        for name, payload in entries.items():
            archive.writestr(f"specdock-authoring-pack/{name}", json.dumps(payload, sort_keys=True) + "\n")
        archive.writestr("specdock-authoring-pack/README.md", "draft evidence\n")
    return pack_zip, preflight


def _write_authoring_pack_zip(
    zip_path: Path,
    *,
    variant: str | None = None,
    extra_entries: dict[str, str | bytes] | None = None,
    extra_infos: list[tuple[zipfile.ZipInfo, str | bytes]] | None = None,
    metadata_overrides: dict[str, str] | None = None,
) -> Path:
    entries = _authoring_pack_entries()
    root = "specdock-authoring-pack"
    if variant == "missing-metadata":
        entries.pop("manifest.json")
    if variant in {"invalid-authority", "invalid-adoption-status", "invalid-bundle-generation-not-promotion"}:
        manifest = json.loads(entries["manifest.json"])
        if variant == "invalid-authority":
            manifest["authority"] = "canonical"
        if variant == "invalid-adoption-status":
            manifest["adoption_status"] = "adopted"
        if variant == "invalid-bundle-generation-not-promotion":
            manifest["bundle_generation_not_promotion"] = False
        entries["manifest.json"] = json.dumps(manifest, sort_keys=True) + "\n"
    if variant == "source-hash-mismatch":
        entries["stale-if.json"] = json.dumps({"source_manifest_hash": "different"}, sort_keys=True) + "\n"
    if variant == "wrong-root":
        root = "wrong-root"
    for metadata_path, value in (metadata_overrides or {}).items():
        entries[metadata_path] = value
    with zipfile.ZipFile(zip_path, "w") as archive:
        for entry_name, entry_value in entries.items():
            archive.writestr(f"{root}/{entry_name}", entry_value)
        for extra_name, extra_value in (extra_entries or {}).items():
            archive.writestr(extra_name, extra_value)
        for extra_info, extra_value in extra_infos or ():
            archive.writestr(extra_info, extra_value)
    return zip_path


def _mark_zip_entry_encrypted(zip_path: Path, entry_name: str) -> None:
    data = bytearray(zip_path.read_bytes())
    encoded_name = entry_name.encode("utf-8")
    _set_zip_general_purpose_bit(data, b"PK\x03\x04", encoded_name, flags_offset=6, name_length_offset=26)
    _set_zip_general_purpose_bit(data, b"PK\x01\x02", encoded_name, flags_offset=8, name_length_offset=28)
    zip_path.write_bytes(data)


def _set_zip_general_purpose_bit(
    data: bytearray,
    signature: bytes,
    encoded_name: bytes,
    *,
    flags_offset: int,
    name_length_offset: int,
) -> None:
    offset = 0
    while True:
        offset = data.find(signature, offset)
        if offset < 0:
            raise AssertionError(f"zip entry not found for encryption patch: {encoded_name!r}")
        name_length = int.from_bytes(data[offset + name_length_offset : offset + name_length_offset + 2], "little")
        if signature == b"PK\x03\x04":
            name_start = offset + 30
        else:
            name_start = offset + 46
        name = bytes(data[name_start : name_start + name_length])
        if name == encoded_name:
            flags_start = offset + flags_offset
            flags = int.from_bytes(data[flags_start : flags_start + 2], "little") | 0x1
            data[flags_start : flags_start + 2] = flags.to_bytes(2, "little")
            return
        offset += 4


def _authoring_pack_entries() -> dict[str, str]:
    source_manifest = {
        "source_hashes": {"src/example.py": "abc123"},
        "source_manifest_hash": "hash",
    }
    manifest = _base_authoring_pack_manifest()
    return {
        "manifest.json": json.dumps(manifest, sort_keys=True) + "\n",
        "provenance.json": json.dumps(
            {
                "evidence_mode": "github-synced",
                "sync_state": "synced",
                "github_sync": "verified",
                "source_manifest_hash": "hash",
            },
            sort_keys=True,
        )
        + "\n",
        "source-manifest.json": json.dumps(source_manifest, sort_keys=True) + "\n",
        "stale-if.json": json.dumps({"source_manifest_hash": "hash"}, sort_keys=True) + "\n",
        "safe-output-constraints.md": "authority: evidence_only\nadoption_status: unreviewed\n",
        "adoption/adoption-map.json": json.dumps({"items": []}, sort_keys=True) + "\n",
        "adoption/eal-candidates.json": json.dumps({"candidates": []}, sort_keys=True) + "\n",
        "issue/requirement.md": "# Draft requirement\n",
    }


def _write_candidate_stage(
    stage_dir: Path,
    *,
    kind: str,
    review_status: str = "pass",
    mutator: str | None = None,
) -> Path:
    root = stage_dir / "specdock-authoring-pack"
    source_manifest_hash = "different" if mutator == "source-hash-mismatch" else "hash"
    (root / "source-manifest.json").parent.mkdir(parents=True, exist_ok=True)
    (root / "source-manifest.json").write_text(
        json.dumps(
            {"source_manifest_hash": source_manifest_hash, "source_hashes": {"src/example.py": "abc123"}},
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    candidate_root = root / ("candidates/epics" if kind == "initiative-epic" else "candidates/issues")
    count = 2 if kind == "initiative-epic" else 3
    index_candidates: list[dict[str, str]] = []
    for number in range(1, count + 1):
        candidate_id = f"candidate-{number:03d}"
        if mutator == "duplicate-id" and number == 2:
            candidate_id = "candidate-001"
        candidate_dir = candidate_root / candidate_id
        candidate_dir.mkdir(parents=True, exist_ok=True)
        title = f"Candidate {number}"
        slug = f"candidate-{number}"
        draft_files = {"requirement": "requirement.md", "design": "design.md", "plan": "plan.md"}
        if mutator == "path-traversal" and number == 1:
            draft_files["requirement"] = "../requirement.md"
        if mutator == "windows-drive-draft" and number == 1:
            draft_files["requirement"] = "C:/Users/alice/requirement.md"
        if mutator == "windows-backslash-draft" and number == 1:
            draft_files["requirement"] = "..\\..\\outside.md"
        if mutator == "hidden-path" and number == 1:
            draft_files["requirement"] = ".hidden.md"
            (candidate_dir / ".hidden.md").write_text("# Hidden\n", encoding="utf-8")
        if mutator == "unsupported-suffix" and number == 1:
            draft_files["requirement"] = "notes.txt"
            (candidate_dir / "notes.txt").write_text("notes\n", encoding="utf-8")
        if mutator == "secret-draft-path" and number == 1:
            draft_files["requirement"] = "token-secret.md"
            (candidate_dir / "token-secret.md").write_text("# Secret-looking path\n", encoding="utf-8")
        if mutator == "symlink-draft" and number == 1:
            target = candidate_dir / "real-requirement.md"
            target.write_text("# Real requirement\n", encoding="utf-8")
            link = candidate_dir / "linked-requirement.md"
            link.symlink_to(target)
            draft_files["requirement"] = "linked-requirement.md"
        for filename in ("requirement.md", "design.md", "plan.md"):
            text = f"# {title} {filename}\n"
            if mutator == "secret-text" and number == 1 and filename == "requirement.md":
                text = "token=abc123secret\n"
            if mutator == "raw-transcript" and number == 1 and filename == "requirement.md":
                text = "raw transcript\n"
            if mutator == "forbidden-claim" and number == 1 and filename == "requirement.md":
                text = "PR-ready\n"
            path = candidate_dir / filename
            path.write_text(text, encoding="utf-8")
            if mutator == "executable-draft" and number == 1 and filename == "requirement.md":
                path.chmod(0o755)
            if mutator == "binary-draft" and number == 1 and filename == "requirement.md":
                path.write_bytes(b"\xff\xfe\x00")
            if mutator == "oversized-draft" and number == 1 and filename == "requirement.md":
                path.write_text("x" * 2_000_001, encoding="utf-8")
        parent_trace: dict[str, str]
        if kind == "initiative-epic":
            parent_trace = {"initiative_id": "init-local-00003"}
            payload: dict[str, object] = {
                "schema_version": 1,
                "authority": "evidence_only",
                "adoption_status": "unreviewed",
                "bundle_generation_not_promotion": True,
                "candidate_id": candidate_id,
                "candidate_kind": "epic",
                "slug": slug,
                "title": title,
                "approval_gate": "human_approval_before_epic_node_creation",
                "parent_trace": parent_trace,
                "boundary": _candidate_boundary(number, overlap=mutator == "overlap" and number == 1),
                "epic_boundary": {
                    "scope": [f"epic scope {number}"],
                    "non_scope": ["other"],
                    "depends_on_epic_candidates": [],
                },
                "draft_files": draft_files,
                "authority_claims": _candidate_authority_claims(),
            }
            if mutator == "unknown-epic-dependency" and number == 1:
                payload["epic_boundary"] = {
                    "scope": [f"epic scope {number}"],
                    "non_scope": ["other"],
                    "depends_on_epic_candidates": ["candidate-999"],
                }
            if mutator == "forward-epic-dependency" and number == 1:
                payload["epic_boundary"] = {
                    "scope": [f"epic scope {number}"],
                    "non_scope": ["other"],
                    "depends_on_epic_candidates": ["candidate-002"],
                }
        else:
            parent_trace = {"epic_id": "different" if mutator == "parent-mismatch" and number == 1 else "epic-00295"}
            payload = {
                "schema_version": 1,
                "authority": "evidence_only",
                "adoption_status": "unreviewed",
                "bundle_generation_not_promotion": True,
                "candidate_id": candidate_id,
                "candidate_kind": "issue",
                "slug": slug,
                "title": title,
                "parent_trace": parent_trace,
                "boundary": _candidate_boundary(number, overlap=mutator == "overlap" and number == 1),
                "grade_recommendation": {
                    "grade": "advanced" if mutator == "unsupported-grade" and number == 1 else "standard",
                    "advisory_only": True,
                },
                "profile_recommendation": {
                    "profile": "advanced" if mutator == "unsupported-profile" and number == 1 else None,
                    "advisory_only": True,
                    "ignored_for_authority": True,
                    "authorized_profile": "standard" if mutator == "authorized-profile" and number == 1 else None,
                },
                "draft_files": draft_files,
                "authority_claims": _candidate_authority_claims(),
            }
            if mutator == "missing-authority-claims" and number == 1:
                payload.pop("authority_claims")
            if mutator == "invalid-schema-version" and number == 1:
                payload.pop("schema_version")
            if mutator == "candidate-id-mismatch" and number == 1:
                payload["candidate_id"] = "candidate-different"
        (candidate_dir / "candidate.json").write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
        index_candidates.append({
            "candidate_id": candidate_id,
            "slug": slug,
            "title": title,
            "path": f"candidates/{'epics' if kind == 'initiative-epic' else 'issues'}/{candidate_id}/candidate.json",
        })
    index = {
        "schema_version": 1,
        "authority": "evidence_only",
        "adoption_status": "unreviewed",
        "bundle_generation_not_promotion": True,
        "parent_trace": {"initiative_id": "init-local-00003"}
        if kind == "initiative-epic"
        else {"epic_id": "epic-00295"},
        "candidates": [] if mutator == "empty-index" else index_candidates,
    }
    if mutator == "host-local-path":
        index["candidates"] = [
            {
                "candidate_id": "candidate-host",
                "slug": "candidate-host",
                "title": "Candidate host",
                "path": "Users/example/candidate.json",
            }
        ]
    if mutator == "secret-path":
        index["candidates"] = [
            {
                "candidate_id": "candidate-secret",
                "slug": "candidate-secret",
                "title": "Candidate secret",
                "path": "secrets/candidate.json",
            }
        ]
    (candidate_root / "index.json").write_text(json.dumps(index, sort_keys=True) + "\n", encoding="utf-8")
    digest = _candidate_tree_digest(root)
    if mutator == "symlink-unindexed-file":
        target = root / "unindexed-target.md"
        target.write_text("# Unindexed target\n", encoding="utf-8")
        (root / "unindexed-link.md").symlink_to(target)
    if mutator == "review-digest-mismatch":
        digest = "wrong"
    (stage_dir / "review-report.json").write_text(
        json.dumps(
            {
                "status": review_status,
                "authority": "evidence_only",
                "adoption_status": "unreviewed",
                "bundle_generation_not_promotion": True,
                "pack_digest": {"content_sha256": digest},
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return stage_dir


def _write_approval_fixture(
    stage_dir: Path,
    *,
    kind: str,
    expected_scope: str,
    mutator: str | None = None,
) -> dict[str, str | Path]:
    pack_root = stage_dir / "specdock-authoring-pack"
    candidate_evidence = stage_dir / "candidate-evidence.json"
    candidate_evidence.write_text(
        json.dumps(
            {
                "kind": kind,
                "scope": expected_scope,
                "candidate_count": 2,
                "source_manifest_hash": "different" if mutator == "source-hash-mismatch" else "hash",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    candidate_pack_digest = _candidate_tree_digest(pack_root)
    candidate_evidence_digest = hashlib.sha256(candidate_evidence.read_bytes()).hexdigest()
    approval_path = stage_dir / "approval.json"
    expected_scope_value = expected_scope if ":" in expected_scope else _approval_scope_value(kind, expected_scope)
    requested_scope = _approval_scope_value(kind, "different") if mutator == "scope-mismatch" else expected_scope_value
    approver_kind = "chatgpt" if mutator == "self-approval" else "human"
    source_hash = "different" if mutator == "source-hash-mismatch" else "hash"
    scope_type, scope_id = requested_scope.split(":", 1)
    payload: dict[str, object] = {
        "schema_version": 2 if mutator == "invalid-schema-version" else 1,
        "approval_evidence_kind": "candidate_decomposition_approval",
        "approval_scope": (
            "initiative-epic-node-creation"
            if (kind == "initiative-epic") != (mutator == "approval-scope-mismatch")
            else "epic-issue-node-creation"
        ),
        "approval_status": "needs-work" if mutator == "non-approved" else "approved",
        "candidate_kind": (
            "initiative-epic"
            if kind == "epic-issue" and mutator == "candidate-kind-mismatch"
            else "epic-issue"
            if kind == "initiative-epic" and mutator == "candidate-kind-mismatch"
            else kind
        ),
        "candidate_pack": {
            "digest_algorithm": "sha256-tree-v1",
            "candidate_pack_digest": (
                "different" if mutator == "candidate-pack-digest-mismatch" else candidate_pack_digest
            ),
            "source_manifest_hash": source_hash,
        },
        "requested_scope": {"scope_type": scope_type, "scope_id": scope_id},
        "effective_scope": {"scope_type": scope_type, "scope_id": scope_id},
        "approver": {"actor_type": approver_kind, "id": "maintainer"},
        "approval_statement": (
            "token=abc123secret"
            if mutator == "secret-text"
            else "Human approval recorded for evidence-only candidate decomposition."
        ),
        "approved_at": "2026-07-08" if mutator == "invalid-timestamp" else "2026-07-08T00:00:00Z",
        "authority_boundary": _candidate_authority_claims(),
    }
    if mutator == "missing-candidate-pack-digest":
        assert isinstance(payload["candidate_pack"], dict)
        payload["candidate_pack"].pop("candidate_pack_digest")
    if mutator == "missing-source-manifest-hash":
        assert isinstance(payload["candidate_pack"], dict)
        payload["candidate_pack"].pop("source_manifest_hash")
    if mutator == "forbidden-claim":
        payload["authority_boundary"] = {**_candidate_authority_claims(), "execution_ready": True}
    if mutator == "forbidden-extra-field":
        payload["notes"] = "execution-ready"
    if mutator == "top-level-execution-ready":
        payload["execution_ready"] = True
    if mutator == "nested-pr-ready":
        payload["metadata"] = {"pr_ready": True}
    if mutator == "malformed-json":
        text = "{invalid json"
    elif mutator == "non-object-json":
        text = json.dumps(["not", "object"]) + "\n"
    elif mutator == "binary-approval":
        approval_path.write_bytes(b"\xff\xfe\x00")
        return {
            "approval": approval_path,
            "candidate_evidence": candidate_evidence,
            "candidate_pack_digest": candidate_pack_digest,
            "candidate_evidence_digest": candidate_evidence_digest,
        }
    elif mutator == "oversized-approval":
        text = "x" * 2_000_001
    else:
        text = json.dumps(payload, sort_keys=True) + "\n"
    approval_path.write_text(text, encoding="utf-8")
    return {
        "approval": approval_path,
        "candidate_evidence": candidate_evidence,
        "candidate_pack_digest": candidate_pack_digest,
        "candidate_evidence_digest": candidate_evidence_digest,
    }


def _approval_scope_value(kind: str, scope_id: str) -> str:
    return f"{'initiative' if kind == 'initiative-epic' else 'epic'}:{scope_id}"


def _write_approval_evidence(
    approval_path: Path,
    stage_dir: Path,
    *,
    kind: str,
    scope: str,
    mutator: str | None = None,
) -> Path:
    pack_root = stage_dir / "specdock-authoring-pack"
    scope_type, scope_id = scope.split(":", 1)
    requested_scope = {"scope_type": scope_type, "scope_id": scope_id}
    effective_scope = {"scope_type": scope_type, "scope_id": scope_id}
    if mutator == "requested-scope-mismatch":
        requested_scope = {"scope_type": scope_type, "scope_id": "different"}
    if mutator == "effective-scope-mismatch":
        effective_scope = {"scope_type": scope_type, "scope_id": "different"}
    statement = "I approve this candidate decomposition for the stated scope before node creation."
    if mutator == "forbidden-claim":
        statement = "I approve this decomposition and claim execution-ready."
    if mutator == "sensitive-statement":
        statement = "I approve this decomposition. token=abc123secret"
    payload = {
        "schema_version": 1,
        "approval_evidence_kind": "candidate_decomposition_approval",
        "approval_status": "approved",
        "approval_scope": "initiative-epic-node-creation" if kind == "initiative-epic" else "epic-issue-node-creation",
        "candidate_kind": kind,
        "requested_scope": requested_scope,
        "effective_scope": effective_scope,
        "candidate_pack": {
            "digest_algorithm": "sha256-tree-v1",
            "candidate_pack_digest": "stale" if mutator == "stale-digest" else _candidate_tree_digest(pack_root),
            "source_manifest_hash": "hash",
            "candidate_ids": ["candidate-001"],
        },
        "approver": {
            "actor_type": "assistant" if mutator == "self-approval" else "human",
            "id": "ChatGPT" if mutator == "self-approval" else "iwasawayuuta",
            "role": "scope_owner",
        },
        "approved_at": "2026-07-08T00:00:00Z",
        "approval_statement": statement,
        "authority_boundary": _candidate_authority_claims(),
    }
    approval_path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    return approval_path


def _candidate_boundary(number: int, *, overlap: bool = False) -> dict[str, Any]:
    scope = [f"scope {number}"]
    non_scope = [f"scope {number}" if overlap else f"non-scope {number}"]
    return {"summary": f"boundary {number}", "scope": scope, "non_scope": non_scope, "dependencies": []}


def _candidate_authority_claims() -> dict[str, bool]:
    return {
        "node_creation_performed": False,
        "canonical_written": False,
        "assurance_mutated": False,
        "reviewer_pass_claimed": False,
        "execution_ready": False,
        "pr_ready": False,
    }


def _draft_authority_claims() -> dict[str, bool]:
    return {
        "canonical_adoption": False,
        "canonical_written": False,
        "assurance_mutation": False,
        "authorized_profile_decision": False,
        "reviewer_pass": False,
        "execution_ready": False,
        "pr_ready": False,
        "merge_ready": False,
        "pr_delivery": False,
        "pr_delivered": False,
    }


def _candidate_tree_digest(pack_root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in pack_root.rglob("*") if item.is_file() and not item.is_symlink()):
        rel_path = path.relative_to(pack_root).as_posix()
        digest.update(rel_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).hexdigest().encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def _write_issue_draft_adoption_fixture(repo: Path, *, mutator: str | None = None) -> dict[str, str | Path]:
    issue_dir = (
        repo / "spec-dock" / "initiatives" / "init-local-00003" / "epics" / "epic-00295" / "issues" / "iss-00303"
    )
    issue_dir.mkdir(parents=True, exist_ok=True)
    (issue_dir / ".meta.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "type": "issue",
                "id": "iss-00303",
                "parent_id": "epic-00295",
                "initiative_id": "init-local-00003",
                "epic_id": "epic-00295",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    artifact_dir = issue_dir / "artifacts"
    artifact_dir.mkdir(exist_ok=True)
    draft_hashes: dict[str, str] = {}
    draft_paths: dict[str, str] = {}
    for name in ("requirement", "design", "plan"):
        path = artifact_dir / f"{name}-draft.md"
        path.write_text(f"# {name}\n\nDraft content for {name}.\n", encoding="utf-8")
        draft_hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        draft_paths[name] = f"artifacts/{name}-draft.md"
    review_report = repo / ".specdock-authoring" / "issue-draft" / "review-report.json"
    review_report.parent.mkdir(parents=True, exist_ok=True)
    review_report.write_text(
        json.dumps(_evidence_review_report("pass", "draft-pack-hash"), sort_keys=True) + "\n",
        encoding="utf-8",
    )
    review_digest = hashlib.sha256(review_report.read_bytes()).hexdigest()
    payload = {
        "schema_version": "issue-draft-adoption-v1",
        "issue_id": "iss-00303",
        "parent_epic_id": "epic-00295",
        "parent_initiative_id": "init-local-00003",
        "source_manifest_hash": "source-hash",
        "draft_pack_digest": "draft-pack-hash",
        "canonical_targets": {
            "requirement": "requirement.md",
            "design": "design.md",
            "plan": "plan.md",
            "report_evidence": "report.md",
        },
        "eal_disposition_required": True,
        "drafts": {name: {"path": draft_paths[name], "sha256": digest} for name, digest in draft_hashes.items()},
        "authority_claims": _draft_authority_claims(),
    }
    if mutator == "forbidden-claim":
        payload["authority_claims"]["canonical_written"] = True  # type: ignore[index]
    if mutator == "merge-ready-claim":
        payload["authority_claims"]["merge_ready"] = True  # type: ignore[index]
    if mutator == "pr-delivery-claim":
        payload["authority_claims"]["pr_delivery"] = True  # type: ignore[index]
    if mutator == "top-level-execution-ready":
        payload["execution_ready"] = True
    if mutator == "nested-pr-delivery":
        payload["state"] = {"pr_delivery": True}
    if mutator == "canonical-doc-path":
        payload["drafts"]["requirement"]["path"] = "requirement.md"  # type: ignore[index]
    if mutator == "symlink-ancestor":
        outside = repo / "outside-drafts"
        outside.mkdir()
        outside_requirement = outside / "requirement-draft.md"
        outside_requirement.write_text("# outside requirement\n", encoding="utf-8")
        linkdir = artifact_dir / "linkdir"
        linkdir.symlink_to(outside, target_is_directory=True)
        payload["drafts"]["requirement"]["path"] = "artifacts/linkdir/requirement-draft.md"  # type: ignore[index]
        payload["drafts"]["requirement"]["sha256"] = hashlib.sha256(  # type: ignore[index]
            outside_requirement.read_bytes()
        ).hexdigest()
    if mutator == "issue-id-mismatch":
        payload["issue_id"] = "iss-99999"
    if mutator == "parent-mismatch":
        payload["parent_epic_id"] = "epic-99999"
    if mutator == "missing-draft-pack-digest":
        payload.pop("draft_pack_digest")
    if mutator == "missing-eal-disposition":
        payload.pop("eal_disposition_required")
    if mutator == "missing-draft-sha":
        payload["drafts"]["requirement"].pop("sha256")  # type: ignore[index]
    if mutator == "unsafe-target":
        payload["canonical_targets"]["requirement"] = "../requirement.md"  # type: ignore[index]
    if mutator == "assurance-target":
        payload["canonical_targets"]["requirement"] = ".assurance.json"  # type: ignore[index]
    if mutator == "extra-canonical-target":
        payload["canonical_targets"]["appendix"] = "notes.md"  # type: ignore[index]
    if mutator == "missing-issue-node":
        shutil.rmtree(issue_dir)
    input_path = review_report.parent / "issue-draft-adoption.json"
    if mutator == "malformed-input":
        input_path.write_text("{not-json\n", encoding="utf-8")
    elif mutator == "non-object-input":
        input_path.write_text("[]\n", encoding="utf-8")
    elif mutator != "missing-input":
        input_path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "input": input_path,
        "issue_dir": issue_dir,
        "review_report": review_report,
        "review_digest": review_digest,
        "draft_pack_digest": "draft-pack-hash",
    }


def _write_selected_skeleton_fixture(repo: Path, *, mutator: str | None = None) -> dict[str, Path]:
    issue_dir = (
        repo / "spec-dock" / "initiatives" / "init-local-00003" / "epics" / "epic-00295" / "issues" / "iss-00303"
    )
    issue_dir.mkdir(parents=True, exist_ok=True)
    (issue_dir / ".meta.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "type": "issue",
                "id": "iss-00303",
                "parent_id": "epic-00295",
                "initiative_id": "init-local-00003",
                "epic_id": "epic-00295",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    sections = ("requirement", "design", "plan")
    artifact_dir = issue_dir / "artifacts"
    artifact_dir.mkdir(exist_ok=True)
    for section in sections:
        (artifact_dir / f"{section}-fill.md").write_text(
            f"# {section}\n\nFilled {section} section.\n", encoding="utf-8"
        )
    assurance = issue_dir / ".assurance.json"
    assurance_profile = "strict" if mutator == "assurance-profile-mismatch" else "standard"
    assurance.write_text(
        json.dumps(
            {"schema_version": 1, "issue_id": "iss-00303", "classification": {"authorized_profile": assurance_profile}},
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    selected_skeleton = repo / ".specdock-authoring" / "selected-skeleton.json"
    selected_skeleton.parent.mkdir(parents=True, exist_ok=True)
    required_sections = [] if mutator == "empty-inventory" else list(sections)
    selected_profile = "strict" if mutator == "selected-profile-mismatch" else "standard"
    selected_skeleton_payload = {
        "issue_id": "iss-00303",
        "selected_profile": selected_profile,
        "required_sections": required_sections,
        "template_hash": "template-hash",
        "selected_skeleton_hash": "selected-skeleton-hash",
    }
    if mutator == "missing-selected-skeleton-hash":
        selected_skeleton_payload.pop("selected_skeleton_hash")
    selected_skeleton.write_text(json.dumps(selected_skeleton_payload, sort_keys=True) + "\n", encoding="utf-8")
    section_fills: list[dict[str, str]] = []
    for section in sections:
        path = artifact_dir / f"{section}-fill.md"
        section_fills.append({
            "section_id": section,
            "path": f"artifacts/{section}-fill.md",
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    if mutator == "secret-path":
        section_fills[0]["path"] = "secrets/requirement.md"
    if mutator == "section-hash-mismatch":
        section_fills[0]["sha256"] = "wrong"
    if mutator == "missing-section-sha":
        section_fills[0].pop("sha256")
    if mutator == "missing-section":
        section_fills = [item for item in section_fills if item["section_id"] != "plan"]
    if mutator == "extra-section":
        section_fills.append({"section_id": "extra", "path": "artifacts/requirement-fill.md"})
    if mutator == "duplicate-section":
        section_fills.append({"section_id": "requirement", "path": "artifacts/design-fill.md"})
    if mutator == "canonical-doc-path":
        section_fills[0]["path"] = "requirement.md"
    if mutator == "symlink-ancestor":
        outside = repo / "outside-sections"
        outside.mkdir()
        outside_requirement = outside / "requirement-fill.md"
        outside_requirement.write_text("# outside requirement\n", encoding="utf-8")
        linkdir = artifact_dir / "linkdir"
        linkdir.symlink_to(outside, target_is_directory=True)
        section_fills[0]["path"] = "artifacts/linkdir/requirement-fill.md"
        section_fills[0]["sha256"] = hashlib.sha256(outside_requirement.read_bytes()).hexdigest()
    if mutator == "forbidden-claim":
        authority_claims = _draft_authority_claims()
        authority_claims["execution_ready"] = True
    elif mutator == "merge-ready-claim":
        authority_claims = _draft_authority_claims()
        authority_claims["merge_ready"] = True
    elif mutator == "pr-delivery-claim":
        authority_claims = _draft_authority_claims()
        authority_claims["pr_delivery"] = True
    else:
        authority_claims = _draft_authority_claims()
    input_path = repo / ".specdock-authoring" / "selected-skeleton-fill.json"
    template_hash = "wrong" if mutator == "template-hash-mismatch" else "template-hash"
    selected_skeleton_hash = "wrong" if mutator == "selected-skeleton-hash-mismatch" else "selected-skeleton-hash"
    selected_payload: dict[str, object] = {
        "schema_version": "selected-skeleton-fill-v1",
        "issue_id": "iss-00303",
        "template_hash": template_hash,
        "selected_skeleton_hash": selected_skeleton_hash,
        "source_manifest_hash": "source-hash",
        "draft_pack_digest": "selected-pack-hash",
        "section_fills": section_fills,
        "authority_claims": authority_claims,
    }
    if mutator == "top-level-execution-ready":
        selected_payload["execution_ready"] = True
    if mutator == "nested-pr-delivery":
        selected_payload["state"] = {"pr_delivery": True}
    if mutator == "missing-draft-pack-digest":
        selected_payload.pop("draft_pack_digest")
    if mutator == "draft-pack-digest-mismatch":
        selected_payload["draft_pack_digest"] = "different-pack"
    if mutator == "missing-template-hash":
        selected_payload.pop("template_hash")
    if mutator == "malformed-input":
        input_path.write_text("{not-json\n", encoding="utf-8")
    elif mutator != "missing-input":
        input_path.write_text(json.dumps(selected_payload, sort_keys=True) + "\n", encoding="utf-8")
    if mutator == "missing-assurance":
        assurance.unlink()
    if mutator == "invalid-assurance":
        assurance.write_text("{not-json\n", encoding="utf-8")
    if mutator == "missing-selected-skeleton":
        selected_skeleton.unlink()
    if mutator == "invalid-selected-skeleton":
        selected_skeleton.write_text("{not-json\n", encoding="utf-8")
    if mutator == "missing-issue-node":
        issue_dir = repo / "spec-dock" / "missing-issue-node"
    review_report = repo / ".specdock-authoring" / "selected" / "review-report.json"
    review_report.parent.mkdir(parents=True, exist_ok=True)
    review_report.write_text(
        json.dumps(_evidence_review_report("pass", "selected-pack-hash"), sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "input": input_path,
        "issue_dir": issue_dir,
        "assurance": assurance,
        "selected_skeleton": selected_skeleton,
        "review_report": review_report,
    }


def _evidence_review_report(status: str, digest: str | None = None) -> dict[str, object]:
    payload: dict[str, object] = {
        "status": status,
        "authority": "evidence_only",
        "adoption_status": "unreviewed",
        "bundle_generation_not_promotion": True,
    }
    if digest is not None:
        payload["pack_digest"] = {"content_sha256": digest}
    return payload


def _base_authoring_pack_manifest() -> dict[str, object]:
    return {
        "schema_version": 1,
        "authority": "evidence_only",
        "adoption_status": "unreviewed",
        "bundle_generation_not_promotion": True,
        "source_manifest_hash": "hash",
        "expected_output_root": "specdock-authoring-pack/",
    }


def _write_valid_prompt_pack(pack_dir: Path, *, evidence_mode: str = "github-synced") -> Path:
    pack_dir.mkdir(parents=True, exist_ok=True)
    (pack_dir / ".specdock-authoring-pack").write_bytes(b"")
    sync_state = "local_context" if evidence_mode == "local-context" else "synced"
    github_sync = "not_verified" if evidence_mode == "local-context" else "verified"
    manifest = {
        "schema_version": 1,
        "generated_by": "test fixture",
        "expected_output_root": "specdock-authoring-pack/",
        "required_metadata": ["manifest.json"],
        "files": [
            "manifest.json",
            "provenance.json",
            "source-manifest.json",
            "stale-if.json",
            "safe-output-constraints.md",
            "chatgpt-use-prompt.md",
            "expected-output-contract.md",
        ],
        "authority": "evidence_only",
        "adoption_status": "unreviewed",
        "bundle_generation_not_promotion": True,
    }
    provenance = {
        "evidence_mode": evidence_mode,
        "sync_state": sync_state,
        "github_sync": github_sync,
        "source_manifest_hash": "hash",
        "authority": "evidence_only",
        "adoption_status": "unreviewed",
        "bundle_generation_not_promotion": True,
    }
    if evidence_mode == "local-context":
        provenance.update({
            "provided_context_paths": ["source.txt"],
            "unsynced_reason": "fixture local-context evidence",
            "adoption_requires": "explicit_eal_disposition",
        })
    source_manifest = {
        "source_paths": ["source.txt"],
        "source_hashes": {"source.txt": "hash"},
        "source_manifest_hash": "hash",
    }
    for name, payload in (
        ("manifest.json", manifest),
        ("provenance.json", provenance),
        ("source-manifest.json", source_manifest),
        ("stale-if.json", {}),
    ):
        (pack_dir / name).write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    (pack_dir / "safe-output-constraints.md").write_text("constraints\n", encoding="utf-8")
    (pack_dir / "chatgpt-use-prompt.md").write_text("prompt\n", encoding="utf-8")
    (pack_dir / "expected-output-contract.md").write_text("contract\n", encoding="utf-8")
    return pack_dir


def _write_fake_backend(path: Path, sentinel: Path) -> Path:
    path.write_text(
        "from pathlib import Path\n"
        "import json\n"
        "import sys\n"
        f"Path({str(sentinel)!r}).write_text(json.dumps(sys.argv[1:]), encoding='utf-8')\n",
        encoding="utf-8",
    )
    return path


def _manifest_hash(source_hashes: dict[str, object]) -> str:
    payload = json.dumps(source_hashes, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _create_synced_git_repo(root: Path) -> Path:
    if shutil.which("git") is None:
        pytest.skip("git not available")
    remote = root / "remote.git"
    repo = root / "repo"
    _git(root, "init", "--bare", str(remote))
    _git(remote, "config", "gc.auto", "0")
    _git(remote, "config", "maintenance.auto", "false")
    _git(root, "clone", str(remote), str(repo))
    _git(repo, "config", "gc.auto", "0")
    _git(repo, "config", "maintenance.auto", "false")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "user.email", "test@example.com")
    assert main(["init", str(repo)]) == 0
    (repo / "source.txt").write_text("source\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial")
    _git(repo, "branch", "-M", "main")
    _git(repo, "push", "-u", "origin", "main")
    _git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
    return repo


def _stage_change(repo: Path) -> None:
    (repo / "source.txt").write_text("staged\n", encoding="utf-8")
    _git(repo, "add", "source.txt")


def _make_ahead(repo: Path) -> None:
    (repo / "source.txt").write_text("ahead\n", encoding="utf-8")
    _git(repo, "add", "source.txt")
    _git(repo, "commit", "-m", "ahead")


def _make_behind(repo: Path) -> None:
    other = repo.parent / "other"
    _git(repo.parent, "clone", str(repo.parent / "remote.git"), str(other))
    _git(other, "checkout", "main")
    _git(other, "config", "user.name", "Test User")
    _git(other, "config", "user.email", "test@example.com")
    (other / "source.txt").write_text("behind\n", encoding="utf-8")
    _git(other, "add", "source.txt")
    _git(other, "commit", "-m", "behind")
    _git(other, "push", "origin", "main")
    _git(repo, "fetch", "origin", "main")


def _make_diverged(repo: Path) -> None:
    _make_behind(repo)
    (repo / "source.txt").write_text("diverged\n", encoding="utf-8")
    _git(repo, "add", "source.txt")
    _git(repo, "commit", "-m", "diverged")


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)
    if p.returncode != 0:
        raise AssertionError(f"git failed: {args}\nstdout={p.stdout}\nstderr={p.stderr}")
    return p
