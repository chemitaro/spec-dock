from __future__ import annotations

import stat
from typing import TYPE_CHECKING

from tests.cli_runtime.harness import CliRuntimeHarness, main

if TYPE_CHECKING:
    from pathlib import Path


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
        assert "runtime-generation-drift" in blocked.stderr
        assert self._run_git(target, ["branch", "--show-current"]).stdout.strip() == before_branch
        assert self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip() == before_head
