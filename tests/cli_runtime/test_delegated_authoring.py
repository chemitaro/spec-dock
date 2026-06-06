import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestDelegatedAuthoringCli(CliRuntimeHarness):
    def tearDown(self) -> None:
        for tmp in getattr(self, "_tmpdir", []):
            try:
                tmp.cleanup()
            except OSError:
                pass
        super().tearDown()

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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring manifest)", p.stdout)
        self.assertIn("status=deprecated", p.stdout)
        self.assertIn("reason=deprecated_scope_local_discussion_drafts", p.stdout)
        self.assertNotIn("manifest_path=", p.stdout)
        self.assertFalse((_issue_dir(target) / "discussions" / "delegated-authoring").exists())

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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("invalid choice", p.stderr)
        self.assertIn("{manifest,baseline-status,diff-guard}", p.stderr)
        self.assertNotIn("--discussion" + "-file", p.stdout + p.stderr)

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

        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delegated-authoring baseline-status)", p.stdout)
        self.assertIn("reason=baseline_status_written", p.stdout)
        baseline_text = baseline.read_text(encoding="utf-8")
        self.assertIn("# spec-dock delegated-authoring baseline-status v1", baseline_text)
        self.assertIn("# file-state-sha256\t", baseline_text)
        self.assertIn("design.md", baseline_text)

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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring baseline-status)", p.stdout)
        self.assertIn("reason=baseline_status_inside_repo", p.stdout)

    def test_diff_guard_allows_new_flat_discussion_markdown(self) -> None:
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
            ],
        )

        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("status=pass", p.stdout)
        self.assertIn("reason=ok", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_discussion_created_by_different_authorized_role")
    def test_diff_guard_rejects_new_discussion_from_different_authorized_role(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# draft", role="spec-dock-implementation-planner"), encoding="utf-8")

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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=new_discussion_created_by_role_mismatch", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_new_discussion_without_required_provenance")
    def test_diff_guard_rejects_new_discussion_without_required_provenance(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-disc-agent-draft.md"
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=new_discussion_missing_provenance:", p.stdout)
        self.assertIn("created_by_role", p.stdout)
        self.assertIn("diff_guard_result", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_multiple_new_discussion_drafts")
    def test_diff_guard_rejects_multiple_new_discussion_drafts(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        discussions_dir = _issue_dir(target) / "discussions"
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=expected_exactly_one_new_discussion_draft count=2", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_zero_new_discussion_drafts")
    def test_diff_guard_rejects_zero_new_discussion_drafts(self) -> None:
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=expected_exactly_one_new_discussion_draft count=0", p.stdout)

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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("the following arguments are required: --role", p.stderr)

    def test_diff_guard_parser_requires_baseline_status(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
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
            ],
        )

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("the following arguments are required: --baseline-status", p.stderr)

    def test_diff_guard_allows_unborn_repo_baseline_without_head(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        baseline_lines = [
            line
            for line in baseline.read_text(encoding="utf-8").splitlines()
            if not line.startswith("# head\t")
        ]
        baseline.write_text("\n".join(baseline_lines) + "\n", encoding="utf-8")
        fake_tmp = tempfile.TemporaryDirectory()
        self._tmpdir.append(fake_tmp)
        fake_bin = Path(fake_tmp.name)
        real_git = shutil.which("git")
        self.assertIsNotNone(real_git)
        fake_git = fake_bin / "git"
        fake_git.write_text(
            "#!/bin/sh\n"
            "if [ \"$1\" = \"rev-parse\" ] && [ \"$2\" = \"HEAD\" ]; then\n"
            "  exit 128\n"
            "fi\n"
            f"exec {real_git} \"$@\"\n",
            encoding="utf-8",
        )
        fake_git.chmod(0o755)
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
            ],
            env={"PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}"},
        )

        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delegated-authoring diff-guard)", p.stdout)

    def test_diff_guard_rejects_unborn_baseline_when_current_head_exists(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        baseline_lines = [
            line
            for line in baseline.read_text(encoding="utf-8").splitlines()
            if not line.startswith("# head\t")
        ]
        baseline.write_text("\n".join(baseline_lines) + "\n", encoding="utf-8")
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
            ],
        )

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=committed_side_effect", p.stdout)
        self.assertIn("baseline_head=unborn", p.stdout)

    def test_diff_guard_rejects_ignored_side_effect_written_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text("manual-tests/*\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        ignored = target / "manual-tests" / "delegated-output.txt"
        ignored.parent.mkdir()
        ignored.write_text("ignored side effect\n", encoding="utf-8")
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
            ],
        )

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("manual-tests/delegated-output.txt", p.stdout)
        self.assertIn("reason=outside_target_discussions", p.stdout)

    def test_diff_guard_ignores_unbounded_ignored_cache_written_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text(".venv/\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        ignored = target / ".venv" / "delegated-output.txt"
        ignored.parent.mkdir()
        ignored.write_text("ignored side effect\n", encoding="utf-8")
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
            ],
        )

        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delegated-authoring diff-guard)", p.stdout)
        self.assertNotIn(".venv", p.stdout)

    def test_diff_guard_ignores_unbounded_empty_ignored_directory_written_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text(".venv/\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        (target / ".venv").mkdir()
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
            ],
        )

        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delegated-authoring diff-guard)", p.stdout)
        self.assertNotIn(".venv", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths")
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
            ],
        )

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("src/delegated.py", p.stdout)
        self.assertIn("reason=forbidden_root", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths")
    def test_diff_guard_rejects_modified_preexisting_ignored_file_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text("manual-tests/*\n", encoding="utf-8")
        cache = target / "manual-tests" / "preexisting.txt"
        cache.parent.mkdir()
        cache.write_text("pre-existing ignored cache\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        cache.write_text("delegated mutation\n", encoding="utf-8")
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
            ],
        )

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("manual-tests/preexisting.txt", p.stdout)
        self.assertIn("reason=outside_target_discussions", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths")
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
            ],
        )

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("manual-tests/cache", p.stdout)
        self.assertIn("reason=outside_target_discussions", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_allows_new_flat_discussion_markdown")
    def test_diff_guard_ignores_preexisting_ignored_cache_from_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text("cache/*\n", encoding="utf-8")
        cache = target / "cache" / "preexisting.txt"
        cache.parent.mkdir()
        cache.write_text("pre-existing ignored cache\n", encoding="utf-8")
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
            ],
        )

        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delegated-authoring diff-guard)", p.stdout)
        self.assertNotIn("cache/preexisting.txt", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_allows_new_flat_discussion_markdown")
    def test_diff_guard_allows_new_draft_artifact_discussion_markdown(self) -> None:
        for doc_type in ("draft-requirement", "draft-design", "draft-plan"):
            target = self._make_target_repo_with_scope()
            _commit_all(target)
            baseline = _write_delegated_authoring_baseline(self, target)
            discussions_dir = _issue_dir(target) / "discussions"
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

            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok (delegated-authoring diff-guard)", p.stdout)
            self.assertIn("status=pass", p.stdout)
            self.assertIn("reason=ok", p.stdout)

    def test_diff_guard_uses_bootstrapped_repo_root_from_subdirectory(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-disc-agent-draft.md"
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

        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=ok", p.stdout)

    def test_diff_guard_resolves_relative_baseline_status_from_repo_root_when_run_from_subdirectory(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        baseline_arg = os.path.relpath(baseline, start=target)
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-disc-agent-draft.md"
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

        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=ok", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths")
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=forbidden_diff", p.stdout)
        self.assertIn("reason=canonical_doc", p.stdout)

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
        discussion = issue_dir / "discussions" / "20260525t010203z-disc-agent-draft.md"
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=scope_not_found", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_allows_new_flat_discussion_markdown")
    def test_diff_guard_ignores_unchanged_preexisting_dirty_canonical_doc(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        design = _issue_dir(target) / "design.md"
        design.write_text("# pre-existing orchestrator draft\n", encoding="utf-8")
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-disc-agent-draft.md"
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

        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delegated-authoring diff-guard)", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_allows_new_flat_discussion_markdown")
    def test_diff_guard_ignores_unchanged_preexisting_dirty_path_with_space(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        notes = target / "manual notes.md"
        notes.write_text("# pre-existing notes\n", encoding="utf-8")
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-disc-agent-draft.md"
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

        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delegated-authoring diff-guard)", p.stdout)

    def test_diff_guard_uses_escaped_baseline_path_fields(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        notes = target / "manual\tnotes.md"
        notes.write_text("# pre-existing notes\n", encoding="utf-8")
        baseline = _write_delegated_authoring_baseline(self, target)
        self.assertIn('"manual\\tnotes.md"', baseline.read_text(encoding="utf-8"))
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-disc-agent-draft.md"
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

        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delegated-authoring diff-guard)", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths")
    def test_diff_guard_rejects_disappeared_baseline_forbidden_path(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        env_file = target / ".env.local"
        env_file.write_text("SECRET=before\n", encoding="utf-8")
        baseline = _write_delegated_authoring_baseline(self, target)
        env_file.unlink()
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-disc-agent-draft.md"
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=env_file", p.stdout)

    def test_diff_guard_does_not_parse_arrow_filename_as_rename(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        notes = target / "manual -> notes.md"
        notes.write_text("# pre-existing notes\n", encoding="utf-8")
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-disc-agent-draft.md"
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

        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delegated-authoring diff-guard)", p.stdout)

    def test_diff_guard_parses_quoted_rename_baseline_arrow_path(self) -> None:
        target = self._make_target_repo_with_scope()
        original = target / "manual -> notes.md"
        original.write_text("# pre-existing notes\n", encoding="utf-8")
        _commit_all(target)
        renamed = target / "renamed notes.md"
        _run_git(target, ["mv", original.name, renamed.name])
        baseline = _write_delegated_authoring_baseline(self, target)
        baseline_text = baseline.read_text(encoding="utf-8")
        self.assertIn('"manual -> notes.md" -> "renamed notes.md"', baseline_text)
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-disc-agent-draft.md"
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

        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delegated-authoring diff-guard)", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_existing_discussion_update_even_when_allowlisted")
    def test_diff_guard_rejects_explicit_existing_discussion_update(self) -> None:
        target = self._make_target_repo_with_scope()
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-01-disc-agent-draft.md"
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=existing_discussion_update_unsupported", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_existing_discussion_update_even_when_allowlisted")
    def test_diff_guard_rejects_explicit_existing_draft_artifact_update(self) -> None:
        target = self._make_target_repo_with_scope()
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-draft-requirement-agent-draft.md"
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=existing_discussion_update_unsupported", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths")
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=canonical_doc", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths")
    def test_diff_guard_rejects_committed_side_effect_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-disc-agent-draft.md"
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=committed_side_effect", p.stdout)
        self.assertIn("baseline_head=", p.stdout)
        self.assertIn("current_head=", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths")
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=canonical_doc", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths")
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
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-disc-agent-draft.md"
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=canonical_doc", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_existing_discussion_update_even_when_allowlisted")
    def test_diff_guard_rejects_allowlisted_update_when_previous_state_was_accepted(self) -> None:
        target = self._make_target_repo_with_scope()
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-01-disc-agent-draft.md"
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=existing_discussion_update_unsupported", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_allowlisted_existing_discussion_without_state_as_unsupported_update")
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
            with self.subTest(filename=filename):
                target = self._make_target_repo_with_scope()
                discussion = _issue_dir(target) / "discussions" / filename
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

                self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
                self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
                self.assertIn("reason=existing_discussion_update_unsupported", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_existing_discussion_update_even_when_allowlisted")
    def test_diff_guard_rejects_dirty_baseline_discussion_state_rewrite(self) -> None:
        target = self._make_target_repo_with_scope()
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-01-disc-agent-draft.md"
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=dirty_baseline_discussion", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_malformed_discussion_diffs")
    def test_diff_guard_rejects_nested_dirty_baseline_discussion(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        nested = _issue_dir(target) / "discussions" / "nested" / "20260525t010203z-disc-agent-draft.md"
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=dirty_baseline_discussion", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_symlinked_discussions_dir_without_status_entries")
    def test_diff_guard_rejects_committed_symlinked_discussions_dir_without_diff(self) -> None:
        target = self._make_target_repo_with_scope()
        discussions_dir = _issue_dir(target) / "discussions"
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=discussions_dir_symlink", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_discussion_symlink_without_status_entries")
    def test_diff_guard_rejects_committed_discussion_symlink_without_diff(self) -> None:
        target = self._make_target_repo_with_scope()
        symlink = _issue_dir(target) / "discussions" / "20260525t010203z-disc-link.md"
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=discussion_symlink", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths")
    def test_diff_guard_rejects_ignored_env_file_written_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text(".env*\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        (target / ".env.local").write_text("SECRET=delegated\n", encoding="utf-8")
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-disc-agent-draft.md"
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=env_file", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths")
    def test_diff_guard_rejects_nested_ignored_env_file_written_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text("**/.env*\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        nested_dir = target / "tmp"
        nested_dir.mkdir()
        (nested_dir / ".env.secret").write_text("SECRET=delegated\n", encoding="utf-8")
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-disc-agent-draft.md"
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=env_file", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths")
    def test_diff_guard_rejects_ignored_env_directory_descendant_written_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text("**/.env*\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        secret_dir = target / "tmp" / ".env.d"
        secret_dir.mkdir(parents=True)
        (secret_dir / "secret.txt").write_text("SECRET=delegated\n", encoding="utf-8")
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-disc-agent-draft.md"
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=env_file", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_forbidden_paths")
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
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-disc-agent-draft.md"
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=env_file", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_allows_new_flat_discussion_markdown")
    def test_diff_guard_ignores_unchanged_baseline_ignored_env_symlink(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text(".env*\n", encoding="utf-8")
        symlink_target = target / "secret-a"
        symlink_target.write_text("SECRET=first\n", encoding="utf-8")
        ignored_symlink = target / ".env.local"
        ignored_symlink.symlink_to(symlink_target)
        _commit_all(target)
        baseline = _write_delegated_authoring_baseline(self, target)
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-disc-agent-draft.md"
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

        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delegated-authoring diff-guard)", p.stdout)

    @unittest.skip("S05: covered by TestDelegatedAuthoringRuntimeDomain.test_diff_guard_rejects_existing_discussion_update_even_when_allowlisted")
    def test_diff_guard_rejects_non_utf8_head_discussion_without_crashing(self) -> None:
        target = self._make_target_repo_with_scope()
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-01-disc-agent-draft.md"
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

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=existing_discussion_update_unsupported", p.stdout)

    def _make_target_repo_with_scope(self) -> Path:
        self._tmpdir = getattr(self, "_tmpdir", [])
        tmp = tempfile.TemporaryDirectory()
        self._tmpdir.append(tmp)
        target = Path(tmp.name)
        self.assertEqual(main(["init", str(target)]), 0)
        self._create_same_repo_linked_hierarchy(target, issue_issue_number=3, issue_title="Delegated authoring")
        return target

    def _run_runtime_capture_from_cwd(
        self,
        target: Path,
        args: list[str],
        *,
        cwd: Path,
    ) -> subprocess.CompletedProcess[str]:
        script = target / "spec-dock" / "scripts" / "spec-dock"
        self.assertTrue(script.is_file(), f"runtime script missing: {script}")
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
    testcase.assertEqual(p.returncode, 0, p.stdout + p.stderr)
    return baseline


def _external_baseline_path() -> Path:
    return Path(tempfile.mkdtemp(prefix="spec-dock-baseline-")) / "baseline-status.txt"


def _draft_text(body: str, *, role: str = "spec-dock-system-architect") -> str:
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


if __name__ == "__main__":
    unittest.main()
