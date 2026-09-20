from __future__ import annotations

import json
import shlex
import stat
from typing import TYPE_CHECKING

import pytest

from tests.cli_runtime.harness import CliRuntimeHarness, main

if TYPE_CHECKING:
    from pathlib import Path


class TestCheckoutSafety(CliRuntimeHarness):
    def _prepare_issue_start_repo(self, target: Path) -> str:
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
        return self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip()

    def test_issue_start_existing_and_new_checkout_use_fixed_commit_and_clean_tree(self, tmp_path: Path) -> None:
        target = tmp_path / "target"
        initial_head = self._prepare_issue_start_repo(target)
        expected_branch = "iss-00003-refresh-token"

        started = self._run_runtime_capture(target, ["issue", "start", "3"])
        assert started.returncode == 0, started.stderr
        assert self._run_git(target, ["branch", "--show-current"]).stdout.strip() == expected_branch
        assert self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip() == initial_head
        assert self._run_git(target, ["status", "--porcelain"]).stdout == ""
        active_path = target / "spec-dock" / ".agent" / "active.json"
        assert json.loads(active_path.read_text(encoding="utf-8"))["issue"]["id"] == "iss-00003"

        self._run_runtime(target, ["active", "clear"])
        self._run_git(target, ["switch", "-"])
        (target / "README.md").write_text("base branch advanced\n", encoding="utf-8")
        self._run_git(target, ["add", "README.md"])
        self._run_git(target, ["commit", "-m", "advance base branch"])
        advanced_base_head = self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip()
        assert advanced_base_head != initial_head
        assert self._run_git(target, ["rev-parse", f"refs/heads/{expected_branch}"]).stdout.strip() == initial_head

        started_existing = self._run_runtime_capture(target, ["issue", "start", "3"])
        assert started_existing.returncode == 0, started_existing.stderr
        assert self._run_git(target, ["branch", "--show-current"]).stdout.strip() == expected_branch
        assert self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip() == initial_head
        assert self._run_git(target, ["rev-parse", f"refs/heads/{expected_branch}"]).stdout.strip() == initial_head
        assert self._run_git(target, ["status", "--porcelain"]).stdout == ""
        assert json.loads(active_path.read_text(encoding="utf-8"))["issue"]["id"] == "iss-00003"

    def test_existing_branch_can_use_different_tooling_version(self, tmp_path: Path) -> None:
        target = tmp_path / "target"
        self._prepare_issue_start_repo(target)
        self._run_git(target, ["config", "core.fsmonitor", "false"])

        started = self._run_runtime_capture(target, ["issue", "start", "3"])
        assert started.returncode == 0, started.stderr
        self._run_runtime(target, ["active", "clear"])
        self._run_git(target, ["switch", "-"])

        provider_doc = target / "spec-dock" / "docs" / "README.md"
        provider_doc.write_text(provider_doc.read_text(encoding="utf-8") + "\nnew generation\n", encoding="utf-8")
        self._run_git(target, ["add", str(provider_doc.relative_to(target))])
        self._run_git(target, ["commit", "-m", "change provider generation"])
        result = self._run_runtime_capture(target, ["issue", "start", "3"])
        assert result.returncode == 0, result.stderr
        assert self._run_git(target, ["branch", "--show-current"]).stdout.strip() == "iss-00003-refresh-token"

    @pytest.mark.parametrize(
        "provider_configuration",
        ("executable-hook", "fsmonitor", "diff-attribute", "merge-attribute", "sparse-checkout"),
    )
    def test_issue_start_accepts_clean_repo_without_provider_capability_gate(
        self,
        tmp_path: Path,
        provider_configuration: str,
    ) -> None:
        target = tmp_path / "target"
        expected_head = self._prepare_issue_start_repo(target)
        hook_log = tmp_path / "post-checkout-args"

        if provider_configuration == "executable-hook":
            hooks = target / ".git" / "hooks"
            hook = hooks / "post-checkout"
            hook.write_text(
                f"#!/bin/sh\nprintf '%s\\n' \"$@\" > {shlex.quote(str(hook_log))}\nexit 0\n",
                encoding="utf-8",
            )
            hook.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            self._run_git(target, ["config", "core.hooksPath", str(hooks)])
        elif provider_configuration == "fsmonitor":
            fsmonitor_hook = tmp_path / "fsmonitor-hook"
            fsmonitor_hook.write_text("#!/bin/sh\nprintf 'token\\0'\n", encoding="utf-8")
            fsmonitor_hook.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            self._run_git(target, ["config", "core.fsmonitor", str(fsmonitor_hook)])
            self._run_git(target, ["config", "core.fsmonitorHookVersion", "2"])
        elif provider_configuration in {"diff-attribute", "merge-attribute"}:
            attribute = provider_configuration.removesuffix("-attribute")
            (target / ".gitattributes").write_text(
                f"spec-dock/docs/README.md {attribute}=custom\n",
                encoding="utf-8",
            )
            self._run_git(target, ["add", ".gitattributes"])
            self._run_git(target, ["commit", "-m", f"set {attribute} attribute"])
            expected_head = self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip()
        elif provider_configuration == "sparse-checkout":
            self._run_git(target, ["sparse-checkout", "init", "--no-cone"])
            self._run_git(target, ["sparse-checkout", "set", "/*"])
            expected_head = self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip()
        else:
            raise AssertionError(f"unhandled provider configuration: {provider_configuration}")

        assert self._run_git(target, ["status", "--porcelain"]).stdout == ""
        started = self._run_runtime_capture(target, ["issue", "start", "3"])
        assert started.returncode == 0, started.stderr
        assert self._run_git(target, ["branch", "--show-current"]).stdout.strip() == "iss-00003-refresh-token"
        assert self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip() == expected_head
        assert self._run_git(target, ["status", "--porcelain"]).stdout == ""
        active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
        assert active["issue"]["id"] == "iss-00003"
        if provider_configuration == "executable-hook":
            assert hook_log.is_file()
            assert len(hook_log.read_text(encoding="utf-8").splitlines()) == 3

    def test_issue_start_rejects_dirty_worktree_before_checkout(self, tmp_path: Path) -> None:
        target = tmp_path / "target"
        self._prepare_issue_start_repo(target)
        active_path = target / "spec-dock" / ".agent" / "active.json"
        before_active = active_path.read_bytes() if active_path.exists() else None
        before_active_exists = active_path.exists()
        before_branch = self._run_git(target, ["branch", "--show-current"]).stdout.strip()
        before_head = self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip()
        (target / "README.md").write_text("uncommitted change\n", encoding="utf-8")
        dirty_status = self._run_git(target, ["status", "--porcelain"]).stdout
        assert dirty_status

        result = self._run_runtime_capture(target, ["issue", "start", "3"])

        assert result.returncode != 0
        assert "working tree is not clean" in result.stderr.lower()
        assert self._run_git(target, ["branch", "--show-current"]).stdout.strip() == before_branch
        assert self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip() == before_head
        assert active_path.exists() is before_active_exists
        assert (active_path.read_bytes() if active_path.exists() else None) == before_active
        assert self._run_git(target, ["status", "--porcelain"]).stdout == dirty_status
