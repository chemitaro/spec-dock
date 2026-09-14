from __future__ import annotations

from pathlib import Path
import stat
import sys

import pytest

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestGenerationCheckout(CliRuntimeHarness):
    def test_t10_existing_and_new_checkout_are_pinned_and_generation_safe(self, tmp_path: Path) -> None:
        target = tmp_path / "target"
        target.mkdir()
        assert main(["init", str(target)]) == 0
        self._init_origin_repo(target)
        (target / "README.md").write_text("baseline\n", encoding="utf-8")
        self._run_git(target, ["add", "README.md"])
        self._run_git(target, ["commit", "-m", "baseline"])
        self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"])
        self._run_runtime(target, ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"])
        self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Refresh token", "--github-issue", "3"])
        self._run_git(target, ["add", "-A"])
        self._run_git(target, ["commit", "-m", "spec-dock workspace"])
        before_head = self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip()
        started = self._run_runtime_capture(target, ["issue", "start", "3"])
        assert started.returncode == 0, started.stderr
        assert self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip() == before_head
        assert self._run_git(target, ["branch", "--show-current"]).stdout.strip() == "iss-00003-refresh-token"
        assert self._run_git(target, ["status", "--porcelain"]).stdout == ""

        self._run_runtime(target, ["active", "clear"])
        self._run_git(target, ["switch", "-"])
        existing = self._run_runtime_capture(target, ["issue", "start", "3"])
        assert existing.returncode == 0, existing.stderr
        assert self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip() == before_head

        self._run_runtime(target, ["active", "clear"])
        self._run_git(target, ["switch", "-"])
        hooks = target / ".git" / "hooks"
        for hook_name in ("post-checkout", "reference-transaction", "post-index-change"):
            hook = hooks / hook_name
            hook.write_text("#!/bin/sh\nexit 91\n", encoding="utf-8")
            hook.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            try:
                blocked = self._run_runtime_capture(target, ["issue", "start", "3"])
                assert blocked.returncode != 0
                assert "capability" in blocked.stderr.lower()
                assert self._run_git(target, ["branch", "--show-current"]).stdout.strip() != "iss-00003-refresh-token"
            finally:
                hook.unlink()

    def test_t10_existing_branch_rejects_provider_generation_drift_before_mutation(self, tmp_path: Path) -> None:
        target = tmp_path / "target"
        target.mkdir()
        assert main(["init", str(target)]) == 0
        self._init_origin_repo(target)
        (target / "README.md").write_text("baseline\n", encoding="utf-8")
        self._run_git(target, ["add", "README.md"])
        self._run_git(target, ["commit", "-m", "baseline"])
        self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"])
        self._run_runtime(target, ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"])
        self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Refresh token", "--github-issue", "3"])
        self._run_git(target, ["add", "-A"])
        self._run_git(target, ["commit", "-m", "spec-dock workspace"])
        self._run_git(target, ["config", "core.fsmonitor", "false"])

        started = self._run_runtime_capture(target, ["issue", "start", "3"])
        assert started.returncode == 0, started.stderr
        self._run_runtime(target, ["active", "clear"])
        self._run_git(target, ["switch", "-"])

        provider_doc = target / "spec-dock" / "docs" / "README.md"
        provider_doc.write_text(provider_doc.read_text(encoding="utf-8") + "\nnew generation\n", encoding="utf-8")
        self._run_git(target, ["add", str(provider_doc.relative_to(target))])
        self._run_git(target, ["commit", "-m", "change provider generation"])
        before_branch = self._run_git(target, ["branch", "--show-current"]).stdout.strip()
        before_head = self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip()

        blocked = self._run_runtime_capture(target, ["issue", "start", "3"])

        assert blocked.returncode != 0
        assert "runtime-generation-change-blocked" in blocked.stderr
        assert self._run_git(target, ["branch", "--show-current"]).stdout.strip() == before_branch
        assert self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip() == before_head

    @pytest.mark.parametrize("attribute", ("diff=custom", "merge=custom"))
    def test_t10_effective_diff_and_merge_attributes_are_rejected_before_mutation(
        self,
        tmp_path: Path,
        attribute: str,
    ) -> None:
        target = tmp_path / "target"
        target.mkdir()
        assert main(["init", str(target)]) == 0
        self._init_origin_repo(target)
        self._run_git(target, ["add", "-A"])
        self._run_git(target, ["commit", "-m", "baseline"])
        attributes = target / ".gitattributes"
        attributes.write_text(f"spec-dock/docs/README.md {attribute}\n", encoding="utf-8")
        self._run_git(target, ["add", ".gitattributes"])
        self._run_git(target, ["commit", "-m", "configure Git attribute"])
        before_branch = self._run_git(target, ["branch", "--show-current"]).stdout.strip()
        before_head = self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip()

        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime.infra import git_cli

            pinned_commit = self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip()
            assessment = git_cli.assess_capabilities(
                target,
                pinned_commit=pinned_commit,
                closure_paths=git_cli._PROVIDER_CLOSURE_PATHS,
                branch="main",
                check_other_worktree=False,
            )
        finally:
            sys.path.pop(0)

        assert not assessment.allowed
        assert f"attribute-enabled:{attribute.split('=', 1)[0]}=custom" in assessment.reasons
        assert self._run_git(target, ["branch", "--show-current"]).stdout.strip() == before_branch
        assert self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip() == before_head

    def test_t10_capability_guard_covers_materialized_tree_outside_provider_closure(self, tmp_path: Path) -> None:
        target = tmp_path / "target"
        target.mkdir()
        assert main(["init", str(target)]) == 0
        self._init_origin_repo(target)
        self._run_git(target, ["add", "-A"])
        self._run_git(target, ["commit", "-m", "baseline"])
        pinned_commit = self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip()
        self._run_git(
            target,
            ["update-index", "--add", "--cacheinfo", f"160000,{pinned_commit},external/submodule"],
        )
        self._run_git(target, ["commit", "-m", "record external submodule"])
        before_branch = self._run_git(target, ["branch", "--show-current"]).stdout.strip()
        before_head = self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip()

        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime.infra import git_cli

            assessment = git_cli.assess_capabilities(
                target,
                pinned_commit=before_head,
                closure_paths=git_cli._PROVIDER_CLOSURE_PATHS,
                branch=before_branch,
                check_other_worktree=False,
            )
        finally:
            sys.path.pop(0)

        assert not assessment.allowed
        assert "submodule:external/submodule" in assessment.reasons
        assert self._run_git(target, ["branch", "--show-current"]).stdout.strip() == before_branch
        assert self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip() == before_head

    def test_t10_sparse_checkout_effective_values_and_skip_worktree_are_rejected(self, tmp_path: Path) -> None:
        target = tmp_path / "target"
        target.mkdir()
        assert main(["init", str(target)]) == 0
        self._init_origin_repo(target)
        (target / "README.md").write_text("baseline\n", encoding="utf-8")
        self._run_git(target, ["add", "-A"])
        self._run_git(target, ["commit", "-m", "baseline"])
        self._run_git(target, ["sparse-checkout", "init", "--no-cone"])
        self._run_git(target, ["sparse-checkout", "set", "README.md"])
        self._run_git(target, ["config", "core.sparseCheckout", "TRUE"])
        before_branch = self._run_git(target, ["branch", "--show-current"]).stdout.strip()
        before_head = self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip()

        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime.infra import git_cli

            assessment = git_cli.assess_capabilities(
                target,
                pinned_commit=before_head,
                closure_paths=git_cli._PROVIDER_CLOSURE_PATHS,
                branch=before_branch,
                check_other_worktree=False,
            )
        finally:
            sys.path.pop(0)

        assert not assessment.allowed
        assert "sparse-checkout-enabled" in assessment.reasons
        assert "skip-worktree-bit-set" in assessment.reasons
        assert self._run_git(target, ["branch", "--show-current"]).stdout.strip() == before_branch
        assert self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip() == before_head
