from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import hashlib
import zipfile

import pytest

from tests.cli_runtime.harness import CliRuntimeHarness, main


_DEFERRED_COMMANDS = (
    (
        ["authoring", "validate", "issue-draft-adoption"],
        "authoring validate issue-draft-adoption",
        "iss-00303",
    ),
    (
        ["authoring", "validate", "selected-skeleton-fill"],
        "authoring validate selected-skeleton-fill",
        "iss-00303",
    ),
    (["authoring", "approval", "check"], "authoring approval check", "iss-00305"),
)

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

    def test_authoring_validate_initiative_epic_candidates_valid_stage_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(repo / ".specdock-authoring" / "staged" / "initiative", kind="initiative-epic")

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

    def test_authoring_validate_candidates_accepts_documented_source_manifest_hash_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            stage_dir = _write_candidate_stage(repo / ".specdock-authoring" / "staged" / "source-flag", kind="epic-issue")

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
            ("host-local-path", "rejected", "host_local_path"),
            ("secret-path", "rejected", "secret_path"),
            ("secret-draft-path", "rejected", "secret_path"),
            ("hidden-path", "rejected", "hidden_path"),
            ("unsupported-suffix", "rejected", "unsupported_suffix"),
            ("symlink-draft", "rejected", "symlink_entry"),
            ("executable-draft", "rejected", "executable_entry"),
            ("binary-draft", "rejected", "binary_payload"),
            ("oversized-draft", "rejected", "oversized_entry"),
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
            stage_dir = _write_candidate_stage(repo / ".specdock-authoring" / "staged" / "binary-report", kind="epic-issue")
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
                        "token=SHOULD_NOT_APPEAR\n"
                        "private_key: abcdefgh\n"
                        "raw transcript: browser text\n"
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
            ("absolute-path", "specdock-authoring-pack//Users/alice/draft.md", "x\n", "path_traversal:/Users/alice/draft.md"),
            ("host-local-path", "specdock-authoring-pack/Users/alice/draft.md", "x\n", "host_local_path:Users/alice/draft.md"),
            ("hidden-path", "specdock-authoring-pack/.hidden.md", "x\n", "hidden_path:.hidden.md"),
            ("secret-path", "specdock-authoring-pack/secrets/token.md", "x\n", "secret_path:secrets/token.md"),
            ("unsupported-suffix", "specdock-authoring-pack/issue/run.sh", "x\n", "unsupported_suffix:issue/run.sh"),
            ("binary-payload", "specdock-authoring-pack/issue/binary.md", b"\xff\xfe", "binary_payload:issue/binary.md"),
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
                    "adoption/eal-candidates.json": json.dumps(candidate_payload, sort_keys=True) + "\n"
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

    def test_authoring_preflight_github_sync_blocks_missing_origin_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
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
                output = (p.stdout + p.stderr).lower()
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
        assert "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py" in payload["source_paths"]
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
            stage_dir = _write_candidate_stage(repo / ".specdock-authoring" / "staged" / "dogfood-candidates", kind="epic-issue")

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
            pack_zip = _write_authoring_pack_zip(repo / "valid.zip")
            output_dir = repo / ".specdock-authoring" / "legacy-review"

            review = subprocess.run(
                [
                    sys.executable,
                    str(review_script),
                    "--input",
                    str(pack_zip),
                    "--preflight",
                    str(repo / "preflight.json"),
                    "--output-dir",
                    str(output_dir),
                    "--input-kind",
                    "zip",
                    "--extract-dir",
                    str(repo / ".specdock-authoring" / "legacy-extract"),
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

    @pytest.mark.parametrize(
        "script_root",
        (
            Path("src/spec_dock/assets/spec_dock/scripts/authoring-pack"),
            Path("spec-dock/scripts/authoring-pack"),
        ),
    )
    def test_authoring_pack_compatibility_review_rejects_unsafe_legacy_output_dir(
        self, script_root: Path
    ) -> None:
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
    def test_authoring_pack_compatibility_review_rejects_symlink_legacy_output_dir(
        self, script_root: Path
    ) -> None:
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
        review_script = repo_root / "src/spec_dock/assets/spec_dock/scripts/authoring-pack/review_chatgpt_authoring_pack.py"

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
        review_script = repo_root / "src/spec_dock/assets/spec_dock/scripts/authoring-pack/review_chatgpt_authoring_pack.py"

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
    def test_authoring_pack_compatibility_legacy_review_report_can_stage_same_tree(
        self, script_root: Path
    ) -> None:
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
        stage_script = repo_root / "src/spec_dock/assets/spec_dock/scripts/authoring-pack/stage_chatgpt_authoring_pack.py"

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
        stage_script = repo_root / "src/spec_dock/assets/spec_dock/scripts/authoring-pack/stage_chatgpt_authoring_pack.py"

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            tree = _write_authoring_pack_tree(repo / "tree-pack")
            review_report = repo / "legacy-review.json"
            output_dir = repo / ".specdock-authoring" / "legacy-stage"
            review_report.write_text(
                json.dumps({"status": "pass", "pack_digest": {"content_sha256": "different"}}, sort_keys=True)
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
            assert stage.returncode == 1, stage.stdout + stage.stderr
            assert payload["status"] == "stale"
            assert "legacy_review_report_not_pass" in payload["findings"]
            assert not (output_dir / "specdock-authoring-pack").exists()

    def test_authoring_pack_compatibility_stage_reviews_input_before_legacy_digest(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        stage_script = repo_root / "src/spec_dock/assets/spec_dock/scripts/authoring-pack/stage_chatgpt_authoring_pack.py"

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
        stage_script = repo_root / "src/spec_dock/assets/spec_dock/scripts/authoring-pack/stage_chatgpt_authoring_pack.py"

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
        stage_script = repo_root / "src/spec_dock/assets/spec_dock/scripts/authoring-pack/stage_chatgpt_authoring_pack.py"

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
            second_payload = _json_stdout(second)
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
            os.symlink(target, output_dir / "manifest.json")

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
            os.symlink(target, output_dir / "diagnostics.json")
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
                        "source_manifest_hash": "hash",
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
                        "source_manifest_hash": "hash",
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
                (Path(__file__).resolve().parents[2] / "tests/fixtures/authoring_pack/prepare/valid-local-context-preflight.json").read_text(
                    encoding="utf-8"
                ),
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
            preflight.write_text(
                json.dumps(
                    {
                        "status": "pass",
                        "evidence_mode": "local-context",
                        "sync_state": "local_context",
                        "github_sync": "not_verified",
                        "source_manifest_hash": "hash",
                        "source_paths": ["source.txt"],
                        "source_hashes": {"source.txt": "hash"},
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
            assert "--output-dir" not in captured_argv
            assert not (repo / "should-not-run").exists()
            assert captured_argv.count("--file") == 7

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
            os.symlink(canonical, link)

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
            os.symlink(target, link)

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
            os.symlink(target, link)

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
            os.symlink(repo / "source.txt", pack / "chatgpt-use-prompt.md")
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
                    "\"unterminated",
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
            os.symlink(target, output_dir / "invocation-summary.json")

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
            assert "[redacted-path]" in payload["stderr"]
            assert "sk-[redacted]" in payload["stdout"]
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
            assert "prefix-" in payload["stdout"]
            assert "err-" in payload["stderr"]
            assert summary["stdout"] == payload["stdout"]
            assert summary["stderr"] == payload["stderr"]

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
        script = repo_root / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts" / "authoring-pack" / "invoke_chatgpt_backend.py"
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
            assert "--slug" in captured_argv
            assert "compat-slug" in captured_argv
            assert "-p" in captured_argv
            assert "compat prompt" in captured_argv
            assert captured_argv.count("--file") == 7
            assert (root / "invoke-output" / "invocation-summary.json").is_file()

    def test_authoring_backend_invoke_compatibility_script_legacy_file_mode(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts" / "authoring-pack" / "invoke_chatgpt_backend.py"
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
        script = repo_root / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts" / "authoring-pack" / "invoke_chatgpt_backend.py"
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
        script = repo_root / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts" / "authoring-pack" / "invoke_chatgpt_backend.py"
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


def _run_preflight_json(
    testcase: CliRuntimeHarness,
    repo: Path,
    *extra_args: str,
    expected_returncode: int = 0,
) -> dict[str, object]:
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


def _json_stdout(p: subprocess.CompletedProcess[str]) -> dict[str, object]:
    try:
        payload = json.loads(p.stdout)
    except json.JSONDecodeError as error:
        raise AssertionError(p.stdout + p.stderr) from error
    assert isinstance(payload, dict)
    return payload


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
        for name, value in entries.items():
            archive.writestr(f"{root}/{name}", value)
        for name, value in (extra_entries or {}).items():
            archive.writestr(name, value)
        for info, value in extra_infos or ():
            archive.writestr(info, value)
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
        "provenance.json": json.dumps({"evidence_mode": "github-synced"}, sort_keys=True) + "\n",
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
        json.dumps({"source_manifest_hash": source_manifest_hash, "source_hashes": {"src/example.py": "abc123"}}, sort_keys=True)
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
                "epic_boundary": {"scope": [f"epic scope {number}"], "non_scope": ["other"], "depends_on_epic_candidates": []},
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
        (candidate_dir / "candidate.json").write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
        index_candidates.append(
            {
                "candidate_id": candidate_id,
                "slug": slug,
                "title": title,
                "path": f"candidates/{'epics' if kind == 'initiative-epic' else 'issues'}/{candidate_id}/candidate.json",
            }
        )
    index = {
        "schema_version": 1,
        "authority": "evidence_only",
        "adoption_status": "unreviewed",
        "bundle_generation_not_promotion": True,
        "parent_trace": {"initiative_id": "init-local-00003"} if kind == "initiative-epic" else {"epic_id": "epic-00295"},
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
    if mutator == "review-digest-mismatch":
        digest = "wrong"
    (stage_dir / "review-report.json").write_text(
        json.dumps({"status": review_status, "pack_digest": {"content_sha256": digest}}, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return stage_dir


def _candidate_boundary(number: int, *, overlap: bool = False) -> dict[str, list[str]]:
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


def _candidate_tree_digest(pack_root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in pack_root.rglob("*") if item.is_file() and not item.is_symlink()):
        rel_path = path.relative_to(pack_root).as_posix()
        digest.update(rel_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).hexdigest().encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


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
    _git(root, "clone", str(remote), str(repo))
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
