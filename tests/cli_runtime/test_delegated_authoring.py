import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestDelegatedAuthoringCli(CliRuntimeHarness):
    def tearDown(self) -> None:
        for tmp in getattr(self, "_tmpdir", []):
            tmp.cleanup()
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
        baseline = _write_git_status_baseline(target)
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# draft"), encoding="utf-8")

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

        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("status=pass", p.stdout)
        self.assertIn("reason=ok", p.stdout)

    def test_diff_guard_rejects_forbidden_path(self) -> None:
        target = self._make_target_repo_with_scope()
        _commit_all(target)
        baseline = _write_git_status_baseline(target)
        (_issue_dir(target) / "design.md").write_text("# forbidden\n", encoding="utf-8")

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
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=forbidden_diff", p.stdout)
        self.assertIn("reason=canonical_doc", p.stdout)

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
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delegated-authoring diff-guard)", p.stdout)

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
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delegated-authoring diff-guard)", p.stdout)

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
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delegated-authoring diff-guard)", p.stdout)

    def test_diff_guard_allows_explicit_existing_discussion_update(self) -> None:
        target = self._make_target_repo_with_scope()
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-01-disc-agent-draft.md"
        discussion.write_text("---\nadoption_status: unreviewed\n---\n# initial\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_git_status_baseline(target)
        discussion.write_text("---\nadoption_status: unreviewed\n---\n# updated\n", encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
                "--allow-existing-discussion",
                str(discussion.relative_to(target)),
            ],
        )

        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delegated-authoring diff-guard)", p.stdout)

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
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=canonical_doc", p.stdout)

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
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=canonical_doc", p.stdout)

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
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=canonical_doc", p.stdout)

    def test_diff_guard_rejects_allowlisted_update_when_previous_state_was_accepted(self) -> None:
        target = self._make_target_repo_with_scope()
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-01-disc-agent-draft.md"
        discussion.write_text("---\nstatus: accepted\n---\n# accepted\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_git_status_baseline(target)
        discussion.write_text("---\nstatus: proposed\n---\n# rewritten\n", encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
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
        self.assertIn("reason=existing_discussion_not_proposed", p.stdout)

    def test_diff_guard_rejects_dirty_baseline_discussion_state_rewrite(self) -> None:
        target = self._make_target_repo_with_scope()
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-01-disc-agent-draft.md"
        discussion.write_text("---\nadoption_status: unreviewed\n---\n# initial\n", encoding="utf-8")
        _commit_all(target)
        discussion.write_text("---\nstatus: accepted\n---\n# dirty before run\n", encoding="utf-8")
        baseline = _write_git_status_baseline(target)
        discussion.write_text("---\nstatus: proposed\n---\n# rewritten by delegated run\n", encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
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
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=dirty_baseline_discussion", p.stdout)

    def test_diff_guard_rejects_committed_symlinked_discussions_dir_without_diff(self) -> None:
        target = self._make_target_repo_with_scope()
        discussions_dir = _issue_dir(target) / "discussions"
        external_discussions = target / "external-discussions"
        external_discussions.mkdir()
        (discussions_dir / "rules.md").unlink()
        discussions_dir.rmdir()
        discussions_dir.symlink_to(external_discussions, target_is_directory=True)
        _commit_all(target)
        baseline = _write_git_status_baseline(target)

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
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=discussions_dir_symlink", p.stdout)

    def test_diff_guard_rejects_committed_discussion_symlink_without_diff(self) -> None:
        target = self._make_target_repo_with_scope()
        symlink = _issue_dir(target) / "discussions" / "20260525t010203z-disc-link.md"
        symlink.symlink_to(_issue_dir(target) / "design.md")
        _commit_all(target)
        baseline = _write_git_status_baseline(target)

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
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=discussion_symlink", p.stdout)

    def test_diff_guard_rejects_ignored_env_file_written_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text(".env*\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_git_status_baseline(target)
        (target / ".env.local").write_text("SECRET=delegated\n", encoding="utf-8")
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-disc-agent-draft.md"
        discussion.write_text(_draft_text("# delegated draft"), encoding="utf-8")

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
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=env_file", p.stdout)

    def test_diff_guard_rejects_nested_ignored_env_file_written_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text("**/.env*\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_git_status_baseline(target)
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
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=env_file", p.stdout)

    def test_diff_guard_rejects_ignored_env_directory_descendant_written_after_baseline(self) -> None:
        target = self._make_target_repo_with_scope()
        (target / ".gitignore").write_text("**/.env*\n", encoding="utf-8")
        _commit_all(target)
        baseline = _write_git_status_baseline(target)
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
                "--scope",
                "iss-00003",
                "--baseline-status",
                str(baseline),
            ],
        )

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring diff-guard)", p.stdout)
        self.assertIn("reason=env_file", p.stdout)

    def test_diff_guard_rejects_non_utf8_head_discussion_without_crashing(self) -> None:
        target = self._make_target_repo_with_scope()
        discussion = _issue_dir(target) / "discussions" / "20260525t010203z-01-disc-agent-draft.md"
        discussion.write_bytes(b"---\nadoption_status: unreviewed\n---\n# invalid \xff\n")
        _commit_all(target)
        baseline = _write_git_status_baseline(target)
        discussion.write_text("---\nadoption_status: unreviewed\n---\n# valid working tree\n", encoding="utf-8")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "diff-guard",
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
        self.assertIn("reason=existing_discussion_head_non_utf8", p.stdout)

    def _make_target_repo_with_scope(self) -> Path:
        self._tmpdir = getattr(self, "_tmpdir", [])
        tmp = tempfile.TemporaryDirectory()
        self._tmpdir.append(tmp)
        target = Path(tmp.name)
        self.assertEqual(main(["init", str(target)]), 0)
        self._create_same_repo_linked_hierarchy(target, issue_issue_number=3, issue_title="Delegated authoring")
        return target


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


def _write_git_status_baseline(target: Path) -> Path:
    baseline = _external_baseline_path()
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=target,
        capture_output=True,
        text=True,
        check=True,
    )
    baseline.write_text(result.stdout, encoding="utf-8")
    return baseline


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


def _draft_text(body: str) -> str:
    return f"---\nadoption_status: unreviewed\n---\n{body}\n"


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
