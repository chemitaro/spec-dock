import contextlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import pytest

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestDelegatedAuthoringCli(CliRuntimeHarness):
    def teardown_method(self) -> None:
        for tmp in getattr(self, "_tmpdir", []):
            with contextlib.suppress(OSError):
                tmp.cleanup()
        self._tmpdir = []

    def test_manifest_command_is_deprecated_blocked_and_writes_no_artifacts(self) -> None:
        target = self._make_target_repo_with_scope()
        authority_file = target / "input-authority.json"
        authority_file.write_text("{}\n", encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "manifest",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--target",
                "design",
                "--host-surface",
                "cli",
                "--input-authority-file",
                str(authority_file),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring manifest)" in p.stdout
        assert "status=deprecated" in p.stdout
        assert "reason=deprecated_scope_local_discussion_drafts" in p.stdout
        assert "manifest_path=" not in p.stdout
        assert not (_issue_dir(target) / "artifacts" / "delegated-authoring").exists()

    def test_scoped_context_subcommand_is_not_registered(self) -> None:
        target = self._make_target_repo_with_scope()

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "scoped-context",
                "--help",
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "invalid choice" in p.stderr
        assert "{manifest,baseline-status,diff-guard}" in p.stderr
        assert "--discussion" + "-file" not in p.stdout + p.stderr

    def test_baseline_status_writes_content_hash_snapshot(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        design = _issue_dir(target) / "design.md"
        design.write_text("# pre-existing orchestrator draft\n", encoding="utf-8")
        baseline = _external_baseline_path()

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "baseline-status",
                "--output",
                str(baseline),
            ],
        )

        assert p.returncode == 0, p.stdout + p.stderr
        assert "spec-dock: ok (delegated-authoring baseline-status)" in p.stdout
        assert "reason=baseline_status_written" in p.stdout
        baseline_text = baseline.read_text(encoding="utf-8")
        assert "# spec-dock delegated-authoring baseline-status v1" in baseline_text
        assert "# file-state-sha256\t" in baseline_text
        assert "design.md" in baseline_text

    def test_diff_guard_rejects_raw_symlink_payload_change_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        if not self._can_create_symlink(target):
            pytest.skip("symlink creation is unavailable")
        (target / ".gitignore").write_text("manual-tests/*\n", encoding="utf-8")
        manual_tests = target / "manual-tests"
        manual_tests.mkdir()
        delegated_link = manual_tests / "delegated-link"
        delegated_link.symlink_to("payload//target")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        delegated_link.unlink()
        delegated_link.symlink_to("payload/target")
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "manual-tests/delegated-link" in p.stdout
        assert "reason=symlink" in p.stdout

    def test_baseline_status_rejects_repo_local_output(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = target / "baseline-status.txt"

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "baseline-status",
                "--output",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring baseline-status)" in p.stdout
        assert "reason=baseline_status_inside_repo" in p.stdout

    def test_diff_guard_allows_new_flat_artifact_markdown(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode == 0, p.stdout + p.stderr
        assert "spec-dock: ok (delegated-authoring diff-guard)" in p.stdout
        assert "status=pass" in p.stdout
        assert "reason=ok" in p.stdout

    def test_diff_guard_rejects_future_discussion_output_even_when_allow_existing_discussion_is_set(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
                "--allow-existing-discussion",
                str(discussion.relative_to(target)),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=future_noncompliant_discussion_output" in p.stdout
        assert "reason=expected_exactly_one_new_artifact_draft count=0" in p.stdout

    def test_diff_guard_allows_valid_artifact_when_allow_existing_discussion_is_unchanged(self) -> None:
        target = self._make_target_repo_with_scope()
        legacy_discussion = _issue_dir(target) / "discussions" / "001-legacy-evidence.md"
        legacy_discussion.write_text("# legacy evidence\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        artifact = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        artifact.write_text(_draft_text("# draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
                "--allow-existing-discussion",
                str(legacy_discussion.relative_to(target)),
            ],
        )

        assert p.returncode == 0, p.stdout + p.stderr
        assert "spec-dock: ok (delegated-authoring diff-guard)" in p.stdout
        assert "status=pass" in p.stdout
        assert "reason=ok" in p.stdout
        assert "reason=existing_artifact_update_unsupported" not in p.stdout

    def test_diff_guard_rejects_existing_artifact_update_even_when_allow_existing_discussion_is_set(self) -> None:
        target = self._make_target_repo_with_scope()
        artifact = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        artifact.write_text(_draft_text("# initial"), encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        artifact.write_text(_draft_text("# updated"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
                "--allow-existing-discussion",
                str(artifact.relative_to(target)),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=existing_artifact_update_unsupported" in p.stdout

    def test_diff_guard_rejects_artifacts_rules_md_output(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        rules = _issue_dir(target) / "artifacts" / "rules.md"
        rules.unlink()
        rules.write_text(_draft_text("# draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "path=spec-dock/initiatives/init-00001-auth-platform/epics/epic-00002-jwt-auth/issues/iss-00003-delegated-authoring/artifacts/rules.md" in p.stdout
        assert "reason=artifact_name_noncompliant" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_artifact_created_by_different_authorized_role"
    )
    def test_diff_guard_rejects_new_artifact_from_different_authorized_role(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# draft", role="implementation-planner"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=new_artifact_created_by_role_mismatch" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_new_artifact_without_required_provenance"
    )
    def test_diff_guard_rejects_new_artifact_without_required_provenance(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text("---\nadoption_status: unreviewed\n---\n# draft\n", encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=new_artifact_missing_provenance:" in p.stdout
        assert "created_by_role" in p.stdout
        assert "diff_guard_result" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_multiple_new_artifact_drafts"
    )
    def test_diff_guard_rejects_multiple_new_artifact_drafts(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        discussions_dir = _issue_dir(target) / "artifacts"
        first = discussions_dir / "20260525t010203z-disc-first-draft.md"
        second = discussions_dir / "20260525t010204z-disc-second-draft.md"
        first.write_text(_draft_text("# first"), encoding="utf-8")
        second.write_text(_draft_text("# second"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=expected_exactly_one_new_artifact_draft count=2" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_zero_new_artifact_drafts"
    )
    def test_diff_guard_rejects_zero_new_artifact_drafts(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=expected_exactly_one_new_artifact_draft count=0" in p.stdout

    def test_diff_guard_parser_requires_role(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "the following arguments are required: --role" in p.stderr

    def test_diff_guard_parser_requires_baseline_status(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "the following arguments are required: --baseline-status" in p.stderr

    def test_diff_guard_allows_unborn_repo_baseline_without_head(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        baseline_lines = [
            line for line in baseline.read_text(encoding="utf-8").splitlines() if not line.startswith("# head\t")
        ]
        baseline.write_text("\n".join(baseline_lines) + "\n", encoding="utf-8")
        fake_tmp = tempfile.TemporaryDirectory()
        self._tmpdir.append(fake_tmp)
        fake_bin = Path(fake_tmp.name)
        real_git = shutil.which("git")
        assert real_git is not None
        fake_git = fake_bin / "git"
        fake_git.write_text(
            f'#!/bin/sh\nif [ "$1" = "rev-parse" ] && [ "$2" = "HEAD" ]; then\n  exit 128\nfi\nexec {real_git} "$@"\n',
            encoding="utf-8",
        )
        fake_git.chmod(0o755)
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
            env={"PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}"},
        )

        assert p.returncode == 0, p.stdout + p.stderr
        assert "spec-dock: ok (delegated-authoring diff-guard)" in p.stdout

    def test_diff_guard_rejects_unborn_baseline_when_current_head_exists(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        baseline_lines = [
            line for line in baseline.read_text(encoding="utf-8").splitlines() if not line.startswith("# head\t")
        ]
        baseline.write_text("\n".join(baseline_lines) + "\n", encoding="utf-8")
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=committed_side_effect" in p.stdout
        assert "baseline_head=unborn" in p.stdout

    def test_diff_guard_rejects_ignored_side_effect_written_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text("manual-tests/*\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        ignored = target / "manual-tests" / "delegated-output.txt"
        ignored.parent.mkdir()
        ignored.write_text("ignored side effect\n", encoding="utf-8")
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "manual-tests/delegated-output.txt" in p.stdout
        assert "reason=outside_target_artifacts" in p.stdout

    def test_diff_guard_ignores_unbounded_ignored_cache_written_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text(".venv/\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        ignored = target / ".venv" / "delegated-output.txt"
        ignored.parent.mkdir()
        ignored.write_text("ignored side effect\n", encoding="utf-8")
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode == 0, p.stdout + p.stderr
        assert "spec-dock: ok (delegated-authoring diff-guard)" in p.stdout
        assert ".venv" not in p.stdout

    def test_diff_guard_ignores_unbounded_empty_ignored_directory_written_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text(".venv/\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        (target / ".venv").mkdir()
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode == 0, p.stdout + p.stderr
        assert "spec-dock: ok (delegated-authoring diff-guard)" in p.stdout
        assert ".venv" not in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths"
    )
    def test_diff_guard_rejects_backdated_ignored_forbidden_root_written_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text("src/**\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        forbidden = target / "src" / "delegated.py"
        forbidden.parent.mkdir()
        forbidden.write_text("# ignored forbidden side effect\n", encoding="utf-8")
        baseline_mtime = baseline.stat().st_mtime
        os.utime(forbidden, (baseline_mtime - 10, baseline_mtime - 10))
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "src/delegated.py" in p.stdout
        assert "reason=forbidden_root" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths"
    )
    def test_diff_guard_rejects_modified_preexisting_ignored_file_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text("manual-tests/*\n", encoding="utf-8")
        cache = target / "manual-tests" / "preexisting.txt"
        cache.parent.mkdir()
        cache.write_text("pre-existing ignored cache\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        cache.write_text("delegated mutation\n", encoding="utf-8")
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "manual-tests/preexisting.txt" in p.stdout
        assert "reason=outside_target_artifacts" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths"
    )
    def test_diff_guard_rejects_modified_child_in_preexisting_ignored_guarded_directory(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text("manual-tests/*\n", encoding="utf-8")
        cache = target / "manual-tests" / "cache"
        cache.mkdir(parents=True)
        child = cache / "preexisting.txt"
        child.write_text("pre-existing ignored cache\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        child.write_text("delegated mutation\n", encoding="utf-8")
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "manual-tests/cache" in p.stdout
        assert "reason=outside_target_artifacts" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_allows_new_flat_artifact_markdown"
    )
    def test_diff_guard_ignores_preexisting_ignored_cache_from_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text("cache/*\n", encoding="utf-8")
        cache = target / "cache" / "preexisting.txt"
        cache.parent.mkdir()
        cache.write_text("pre-existing ignored cache\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode == 0, p.stdout + p.stderr
        assert "spec-dock: ok (delegated-authoring diff-guard)" in p.stdout
        assert "cache/preexisting.txt" not in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_allows_new_flat_artifact_markdown"
    )
    def test_diff_guard_allows_new_draft_artifact_discussion_markdown(self) -> None:
        for doc_type in ("draft-requirement", "draft-design", "draft-plan"):
            target = self._make_target_repo_with_scope()
            _commit_all(target)
            baseline = _write_delegated_authoring_baseline(self, target)
            discussions_dir = _issue_dir(target) / "artifacts"
            (discussions_dir / f"20260525t010203z-{doc_type}-agent-draft.md").write_text(
                _draft_text(f"# {doc_type}"),
                encoding="utf-8",
            )

            p = self._run_runtime_capture(
                target,
                [
                    "delegated-authoring",
                    "diff-guard",
                    "--role",
                    "system-architect",
                    "--scope",
                    "iss-00003",
                    "--baseline-status",
                    str(baseline),
                ],
            )

            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok (delegated-authoring diff-guard)" in p.stdout
            assert "status=pass" in p.stdout
            assert "reason=ok" in p.stdout

    def test_diff_guard_uses_bootstrapped_repo_root_from_subdirectory(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# delegated draft"), encoding="utf-8")
        subdir = target / "nested" / "cwd"
        subdir.mkdir(parents=True)

        p = self._run_runtime_capture_from_cwd(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
            cwd=subdir,
        )

        assert p.returncode == 0, p.stdout + p.stderr
        assert "spec-dock: ok (delegated-authoring diff-guard)" in p.stdout
        assert "reason=ok" in p.stdout

    def test_diff_guard_resolves_relative_baseline_status_from_repo_root_when_run_from_subdirectory(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        baseline_arg = os.path.relpath(baseline, start=target)
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# delegated draft"), encoding="utf-8")
        subdir = target / "nested" / "cwd"
        subdir.mkdir(parents=True)

        p = self._run_runtime_capture_from_cwd(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                baseline_arg,
            ],
            cwd=subdir,
        )

        assert p.returncode == 0, p.stdout + p.stderr
        assert "spec-dock: ok (delegated-authoring diff-guard)" in p.stdout
        assert "reason=ok" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths"
    )
    def test_diff_guard_rejects_forbidden_path(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        (_issue_dir(target) / "design.md").write_text("# forbidden\n", encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=forbidden_diff" in p.stdout
        assert "reason=canonical_doc" in p.stdout

    def test_diff_guard_active_issue_fallback_requires_exact_meta_id(self) -> None:
        target = self._make_target_repo_with_scope()
        issue_dir = _issue_dir(target)
        (issue_dir / ".meta.json").unlink()
        active_issue = target / "spec-dock" / "active" / "issue"
        if active_issue.exists() or active_issue.is_symlink():
            active_issue.unlink()
        active_issue.symlink_to(issue_dir, target_is_directory=True)
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion = issue_dir / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# delegated draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=scope_not_found" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_allows_new_flat_artifact_markdown"
    )
    def test_diff_guard_ignores_unchanged_preexisting_dirty_canonical_doc(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        design = _issue_dir(target) / "design.md"
        design.write_text("# pre-existing orchestrator draft\n", encoding="utf-8")
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# delegated draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode == 0, p.stdout + p.stderr
        assert "spec-dock: ok (delegated-authoring diff-guard)" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_allows_new_flat_artifact_markdown"
    )
    def test_diff_guard_ignores_unchanged_preexisting_dirty_path_with_space(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        notes = target / "manual notes.md"
        notes.write_text("# pre-existing notes\n", encoding="utf-8")
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# delegated draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode == 0, p.stdout + p.stderr
        assert "spec-dock: ok (delegated-authoring diff-guard)" in p.stdout

    def test_diff_guard_uses_escaped_baseline_path_fields(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        notes = target / "manual\tnotes.md"
        notes.write_text("# pre-existing notes\n", encoding="utf-8")
        baseline = _write_delegated_authoring_baseline(self, target)
        assert '"manual\\tnotes.md"' in baseline.read_text(encoding="utf-8")
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# delegated draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode == 0, p.stdout + p.stderr
        assert "spec-dock: ok (delegated-authoring diff-guard)" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths"
    )
    def test_diff_guard_rejects_disappeared_baseline_forbidden_path(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        env_file = target / ".env.local"
        env_file.write_text("SECRET=before\n", encoding="utf-8")
        baseline = _write_delegated_authoring_baseline(self, target)
        env_file.unlink()
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# delegated draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=env_file" in p.stdout

    def test_diff_guard_does_not_parse_arrow_filename_as_rename(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        notes = target / "manual -> notes.md"
        notes.write_text("# pre-existing notes\n", encoding="utf-8")
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# delegated draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode == 0, p.stdout + p.stderr
        assert "spec-dock: ok (delegated-authoring diff-guard)" in p.stdout

    def test_diff_guard_parses_quoted_rename_baseline_arrow_path(self) -> None:
        target = self._make_target_repo_with_scope()
        original = target / "manual -> notes.md"
        original.write_text("# pre-existing notes\n", encoding="utf-8")
        _commit_all(target)
        renamed = target / "renamed notes.md"
        _run_git(target, ["mv", original.name, renamed.name])
        baseline = _write_delegated_authoring_baseline(self, target)
        baseline_text = baseline.read_text(encoding="utf-8")
        assert '"manual -> notes.md" -> "renamed notes.md"' in baseline_text
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# delegated draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode == 0, p.stdout + p.stderr
        assert "spec-dock: ok (delegated-authoring diff-guard)" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_existing_artifact_update_even_when_allowlisted"
    )
    def test_diff_guard_rejects_explicit_existing_artifact_update(self) -> None:
        target = self._make_target_repo_with_scope()
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-01-disc-agent-draft.md"
        discussion.write_text("---\nadoption_status: unreviewed\n---\n# initial\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion.write_text("---\nadoption_status: unreviewed\n---\n# updated\n", encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
                "--allow-existing-discussion",
                str(discussion.relative_to(target)),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=existing_artifact_update_unsupported" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_existing_artifact_update_even_when_allowlisted"
    )
    def test_diff_guard_rejects_explicit_existing_draft_artifact_update(self) -> None:
        target = self._make_target_repo_with_scope()
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-draft-requirement-agent-draft.md"
        discussion.write_text("---\nadoption_status: unreviewed\n---\n# initial\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion.write_text("---\nadoption_status: unreviewed\n---\n# updated\n", encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
                "--allow-existing-discussion",
                str(discussion.relative_to(target)),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=existing_artifact_update_unsupported" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths"
    )
    def test_diff_guard_rejects_preexisting_dirty_forbidden_path_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        design = _issue_dir(target) / "design.md"
        design.write_text("# pre-existing dirty forbidden edit\n", encoding="utf-8")
        baseline = _write_delegated_authoring_baseline(self, target)
        design.write_text("# delegated run edited dirty forbidden path\n", encoding="utf-8")
        before_baseline_ns = max(0, baseline.stat().st_mtime_ns - 1_000_000)
        os.utime(design, ns=(before_baseline_ns, before_baseline_ns))

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=canonical_doc" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths"
    )
    def test_diff_guard_rejects_committed_side_effect_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# committed draft"), encoding="utf-8")
        _commit_all(target)

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=committed_side_effect" in p.stdout
        assert "baseline_head=" in p.stdout
        assert "current_head=" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths"
    )
    def test_diff_guard_rejects_preexisting_dirty_forbidden_path_mode_change_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        design = _issue_dir(target) / "design.md"
        design.write_text("# pre-existing dirty forbidden edit\n", encoding="utf-8")
        baseline = _write_delegated_authoring_baseline(self, target)
        design.chmod(0o755)

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=canonical_doc" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths"
    )
    def test_diff_guard_rejects_mixed_baseline_forbidden_path_staged_change(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        design = _issue_dir(target) / "design.md"
        design.write_text("# staged before baseline\n", encoding="utf-8")
        _run_git(target, ["add", str(design.relative_to(target))])
        design.write_text("# worktree snapshot\n", encoding="utf-8")
        baseline = _write_delegated_authoring_baseline(self, target)
        design.write_text("# staged after baseline\n", encoding="utf-8")
        _run_git(target, ["add", str(design.relative_to(target))])
        design.write_text("# worktree snapshot\n", encoding="utf-8")
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# delegated draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=canonical_doc" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_existing_artifact_update_even_when_allowlisted"
    )
    def test_diff_guard_rejects_allowlisted_update_when_previous_state_was_accepted(self) -> None:
        target = self._make_target_repo_with_scope()
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-01-disc-agent-draft.md"
        discussion.write_text("---\nstatus: accepted\n---\n# accepted\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion.write_text("---\nstatus: proposed\n---\n# rewritten\n", encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
                "--allow-existing-discussion",
                str(discussion.relative_to(target)),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=existing_artifact_update_unsupported" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_allowlisted_existing_artifact_without_state_as_unsupported_update"
    )
    def test_diff_guard_rejects_allowlisted_update_when_current_draft_claims_non_editable_authority(
        self,
    ) -> None:
        cases = (
            (
                "20260525t010203z-draft-requirement-agent-draft.md",
                "---\nstatus: accepted\n---\n# accepted\n",
            ),
            (
                "20260525t010203z-draft-design-agent-draft.md",
                "---\nadoption_status: adopted\n---\n# adopted\n",
            ),
            (
                "20260525t010203z-draft-plan-agent-draft.md",
                "---\nstatus: stale\n---\n# stale\n",
            ),
        )
        for filename, current_text in cases:
            target = self._make_target_repo_with_scope()
            discussion = _issue_dir(target) / "artifacts" / filename
            discussion.write_text("---\nadoption_status: unreviewed\n---\n# initial\n", encoding="utf-8")
            _commit_all(target)
            baseline = _write_delegated_authoring_baseline(self, target)
            discussion.write_text(current_text, encoding="utf-8")

            p = self._run_runtime_capture(
                target,
                [
                    "delegated-authoring",
                    "diff-guard",
                    "--role",
                    "system-architect",
                    "--scope",
                    "iss-00003",
                    "--baseline-status",
                    str(baseline),
                    "--allow-existing-discussion",
                    str(discussion.relative_to(target)),
                ],
            )

            assert p.returncode != 0, p.stdout + p.stderr
            assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
            assert "reason=existing_artifact_update_unsupported" in p.stdout

    def test_diff_guard_rejects_dirty_baseline_artifact_state_rewrite(self) -> None:
        target = self._make_target_repo_with_scope()
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-01-disc-agent-draft.md"
        discussion.write_text("---\nadoption_status: unreviewed\n---\n# initial\n", encoding="utf-8")
        _commit_all(target)
        discussion.write_text("---\nstatus: accepted\n---\n# dirty before run\n", encoding="utf-8")
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion.write_text("---\nstatus: proposed\n---\n# rewritten by delegated run\n", encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
                "--allow-existing-discussion",
                str(discussion.relative_to(target)),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=dirty_baseline_artifact" in p.stdout

    def test_diff_guard_rejects_nested_dirty_baseline_artifact(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        nested = _issue_dir(target) / "artifacts" / "nested" / "20260525t010203z-disc-agent-draft.md"
        nested.parent.mkdir()
        nested.write_text("# dirty before run\n", encoding="utf-8")
        baseline = _write_delegated_authoring_baseline(self, target)

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=dirty_baseline_artifact" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_symlinked_discussions_dir_without_status_entries"
    )
    def test_diff_guard_rejects_committed_symlinked_discussions_dir_without_diff(self) -> None:
        target = self._make_target_repo_with_scope()
        discussions_dir = _issue_dir(target) / "artifacts"
        external_discussions = target / "external-discussions"
        external_discussions.mkdir()
        (discussions_dir / "rules.md").unlink()
        discussions_dir.rmdir()
        discussions_dir.symlink_to(external_discussions, target_is_directory=True)
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=artifacts_dir_symlink" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_artifact_symlink_without_status_entries"
    )
    def test_diff_guard_rejects_committed_artifact_symlink_without_diff(self) -> None:
        target = self._make_target_repo_with_scope()
        symlink = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-link.md"
        symlink.symlink_to(_issue_dir(target) / "design.md")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=artifact_symlink" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths"
    )
    def test_diff_guard_rejects_ignored_env_file_written_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text(".env*\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        (target / ".env.local").write_text("SECRET=delegated\n", encoding="utf-8")
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# delegated draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=env_file" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths"
    )
    def test_diff_guard_rejects_nested_ignored_env_file_written_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text("**/.env*\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        nested_dir = target / "tmp"
        nested_dir.mkdir()
        (nested_dir / ".env.secret").write_text("SECRET=delegated\n", encoding="utf-8")
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# delegated draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=env_file" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths"
    )
    def test_diff_guard_rejects_ignored_env_directory_descendant_written_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text("**/.env*\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        secret_dir = target / "tmp" / ".env.d"
        secret_dir.mkdir(parents=True)
        (secret_dir / "secret.txt").write_text("SECRET=delegated\n", encoding="utf-8")
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# delegated draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=env_file" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths"
    )
    def test_diff_guard_rejects_ignored_env_symlink_retargeted_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text(".env*\n", encoding="utf-8")
        first_target = target / "secret-a"
        second_target = target / "secret-b"
        first_target.write_text("SECRET=first\n", encoding="utf-8")
        second_target.write_text("SECRET=second\n", encoding="utf-8")
        ignored_symlink = target / ".env.local"
        ignored_symlink.symlink_to(first_target)
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        ignored_symlink.unlink()
        ignored_symlink.symlink_to(second_target)
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# delegated draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=env_file" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_allows_new_flat_artifact_markdown"
    )
    def test_diff_guard_ignores_unchanged_baseline_ignored_env_symlink(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text(".env*\n", encoding="utf-8")
        symlink_target = target / "secret-a"
        symlink_target.write_text("SECRET=first\n", encoding="utf-8")
        ignored_symlink = target / ".env.local"
        ignored_symlink.symlink_to(symlink_target)
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# delegated draft"), encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        assert p.returncode == 0, p.stdout + p.stderr
        assert "spec-dock: ok (delegated-authoring diff-guard)" in p.stdout

    @pytest.mark.skip(
        reason="S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_existing_artifact_update_even_when_allowlisted"
    )
    def test_diff_guard_rejects_non_utf8_head_discussion_without_crashing(self) -> None:
        target = self._make_target_repo_with_scope()
        discussion = _issue_dir(target) / "artifacts" / "20260525t010203z-01-disc-agent-draft.md"
        discussion.write_bytes(b"---\nadoption_status: unreviewed\n---\n# invalid \xff\n")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion.write_text("---\nadoption_status: unreviewed\n---\n# valid working tree\n", encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
                "--allow-existing-discussion",
                str(discussion.relative_to(target)),
            ],
        )

        assert p.returncode != 0, p.stdout + p.stderr
        assert "spec-dock: blocked (delegated-authoring diff-guard)" in p.stdout
        assert "reason=existing_artifact_update_unsupported" in p.stdout

    def _make_target_repo_with_scope(self) -> Path:
        self._tmpdir = getattr(self, "_tmpdir", [])
        tmp = tempfile.TemporaryDirectory()
        self._tmpdir.append(tmp)
        target = Path(tmp.name)
        assert main(["init", str(target)]) == 0
        self._create_same_repo_linked_hierarchy(target, issue_issue_number=3, issue_title="Delegated authoring")
        _create_legacy_discussions_fixture(target)
        return target

    def _run_runtime_capture_from_cwd(
        self,
        target: Path,
        args: list[str],
        *,
        cwd: Path,
    ) -> subprocess.CompletedProcess[str]:
        script = target / "spec-dock" / "scripts" / "spec-dock"
        assert script.is_file(), f"runtime script missing: {script}"
        return subprocess.run(
            [sys.executable, str(script), *args],
            cwd=str(cwd),
            env=self._runtime_env(target, None),
            capture_output=True,
            text=True,
        )


def _issue_dir(target: Path) -> Path:
    return (
        target
        / "spec-dock"
        / "initiatives"
        / "init-00001-auth-platform"
        / "epics"
        / "epic-00002-jwt-auth"
        / "issues"
        / "iss-00003-delegated-authoring"
    )


def _create_legacy_discussions_fixture(target: Path) -> None:
    discussions_dir = _issue_dir(target) / "discussions"
    discussions_dir.mkdir(exist_ok=True)
    rules_target = target / "spec-dock" / "docs" / "rules" / "issue" / "discussions.md"
    rules_path = discussions_dir / "rules.md"
    if not rules_path.exists():
        rules_path.symlink_to(os.path.relpath(rules_target, start=discussions_dir))


def _write_delegated_authoring_baseline(testcase: TestDelegatedAuthoringCli, target: Path) -> Path:
    baseline = _external_baseline_path()
    p = testcase._run_runtime_capture(
        target,
        [
            "delegated-authoring",
            "baseline-status",
            "--output",
            str(baseline),
        ],
    )
    assert p.returncode == 0, p.stdout + p.stderr
    return baseline


def _external_baseline_path() -> Path:
    return Path(tempfile.mkdtemp(prefix="spec-dock-baseline-")) / "baseline-status.txt"


def _draft_text(body: str, *, role: str = "system-architect") -> str:
    return (
        "---\n"
        f"created_by_role: {role}\n"
        "scope_id: iss-00003\n"
        "source_paths:\n"
        "  - spec-dock/active/issue/requirement.md\n"
        "intended_targets:\n"
        "  - spec-dock/active/issue/design.md\n"
        "adoption_status: unreviewed\n"
        "reflected_to: []\n"
        "diff_guard_result: pending\n"
        "---\n"
        f"{body}\n"
    )


def _commit_all(target: Path) -> None:
    _run_git(target, ["add", "."])
    _run_git(target, ["commit", "-m", "baseline"])


def _run_git(target: Path, args: list[str]) -> None:
    subprocess.run(
        ["git", "-c", "user.name=Spec Dock Test", "-c", "user.email=spec-dock@example.test", *args],
        cwd=target,
        capture_output=True,
        text=True,
        check=True,
    )
