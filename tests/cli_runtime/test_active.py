import json
import os
from pathlib import Path
import shutil
import tempfile

import pytest

from tests.cli_runtime.harness import (
    CliRuntimeHarness,
    main,
)


class TestCliActive(CliRuntimeHarness):
    def _set_meta_depends_on(self, node_dir: Path, depends_on: object) -> None:
        meta_path = node_dir / ".meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["depends_on"] = depends_on
        self._write_json_force(meta_path, meta)

    def test_active_set_initiative_and_epic_keep_missing_layers_as_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            # Initiative-only active: epic/issue are placeholders.
            self._run_runtime(target, ["active", "set", "init-00001"])
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            assert isinstance(active.get("initiative"), dict)
            assert active.get("epic") is None
            assert active.get("issue") is None
            assert active["initiative"]["path"] == "spec-dock/initiatives/init-00001-auth-platform"
            assert not active["initiative"]["path"].startswith(str(target))
            assert "init-00001" in self._read_active_pointer_text(target, "initiative", "requirement.md")
            assert "Active Epic: なし" in self._read_active_pointer_text(target, "epic", "README.md")
            assert "Active Issue: なし" in self._read_active_pointer_text(target, "issue", "README.md")

            # Epic-only active: issue is a placeholder.
            self._run_runtime(target, ["active", "set", "epic-00002"])
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            assert isinstance(active.get("initiative"), dict)
            assert isinstance(active.get("epic"), dict)
            assert active.get("issue") is None
            assert active["epic"]["path"] == (
                "spec-dock/initiatives/init-00001-auth-platform/epics/epic-00002-jwt-auth"
            )
            assert not active["epic"]["path"].startswith(str(target))
            assert "epic-00002" in self._read_active_pointer_text(target, "epic", "requirement.md")
            assert "Active Issue: なし" in self._read_active_pointer_text(target, "issue", "README.md")

            # Clear: all placeholders.
            self._run_runtime(target, ["active", "clear"])
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            assert active.get("initiative") is None
            assert active.get("epic") is None
            assert active.get("issue") is None
            assert "Active Initiative: なし" in self._read_active_pointer_text(target, "initiative", "README.md")
            assert "Active Epic: なし" in self._read_active_pointer_text(target, "epic", "README.md")
            assert "Active Issue: なし" in self._read_active_pointer_text(target, "issue", "README.md")

    def test_active_set_rejects_legacy_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            # Legacy flags were removed in favor of a single `target` argument.
            self._run_runtime_expect_fail(target, ["active", "set", "--issue", "1"])

    def test_active_set_rejects_removed_readiness_and_checkout_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            for flag in ("--github", "--no-github", "--force", "--checkout"):
                p = self._run_runtime_capture(target, ["active", "set", "iss-00003", flag])
                assert p.returncode == 2, p.stdout + p.stderr
                assert "error:" in p.stderr

    def test_active_set_accepts_explicit_id_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            p = self._run_runtime_capture(target, ["active", "set", "--id", "iss-00003"])
            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok (active set)" in p.stdout

            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            assert active["issue"]["id"] == "iss-00003"

    def test_active_set_accepts_explicit_github_issue_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123)

            p = self._run_runtime_capture(target, ["active", "set", "--github-issue", "123"])
            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok (active set)" in p.stdout

            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            assert active["issue"]["id"] == "iss-00123"

    @pytest.mark.skip(
        reason="S05: covered by TestSetActiveApplication.test_set_active_resolves_id_and_repo_scoped_github_target_without_cli"
    )
    def test_active_set_github_issue_flag_is_ambiguous_with_current_foreign_overlap_but_id_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123, issue_title="Current issue")
            self._run_runtime(
                target, ["new", "issue", "--epic", "2", "--title", "Foreign mirror", "--github-issue", "124"]
            )

            foreign_issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00124-foreign-mirror"
                / ".meta.json"
            )
            foreign_meta = json.loads(foreign_issue_meta.read_text(encoding="utf-8"))
            foreign_meta["github"] = {"issue_number": 123, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(foreign_issue_meta, foreign_meta)

            ambiguous = self._run_runtime_capture(target, ["active", "set", "--github-issue", "123", "--force"])
            assert ambiguous.returncode != 0, ambiguous.stdout + ambiguous.stderr
            assert "Ambiguous github.issue_number=123" in ambiguous.stderr

            by_id = self._run_runtime_capture(target, ["active", "set", "--id", "iss-00123", "--force"])
            assert by_id.returncode == 0, by_id.stdout + by_id.stderr
            assert "spec-dock: ok (active set)" in by_id.stdout

            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            assert active["issue"]["id"] == "iss-00123"

    @pytest.mark.skip(
        reason="S05: covered by TestSetActiveApplication.test_set_active_resolves_id_and_repo_scoped_github_target_without_cli"
    )
    def test_active_set_repo_scoped_url_resolves_exact_match_when_number_is_ambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123, issue_title="Current issue")
            self._run_runtime(
                target, ["new", "issue", "--epic", "2", "--title", "Foreign mirror", "--github-issue", "124"]
            )

            foreign_issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00124-foreign-mirror"
                / ".meta.json"
            )
            foreign_meta = json.loads(foreign_issue_meta.read_text(encoding="utf-8"))
            foreign_meta["github"] = {"issue_number": 123, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(foreign_issue_meta, foreign_meta)

            ambiguous = self._run_runtime_capture(target, ["active", "set", "123", "--force"])
            assert ambiguous.returncode != 0, ambiguous.stdout + ambiguous.stderr
            assert "Ambiguous github.issue_number=123" in ambiguous.stderr

            by_url = self._run_runtime_capture(
                target, ["active", "set", "https://github.com/other/repo/issues/123", "--force"]
            )
            assert by_url.returncode == 0, by_url.stdout + by_url.stderr
            assert "spec-dock: ok (active set)" in by_url.stdout

            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            assert active["issue"]["id"] == "iss-00124"

    def test_active_set_repo_scoped_url_fails_closed_when_repo_scope_does_not_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123, issue_title="Current issue")

            mismatch = self._run_runtime_capture(
                target,
                ["active", "set", "https://github.com/other/repo/issues/123"],
            )
            assert mismatch.returncode != 0, mismatch.stdout + mismatch.stderr
            assert "No node found for github.issue_number=123 in repo scope (other/repo)" in mismatch.stderr
            assert "spec-dock: ok (active set)" not in mismatch.stdout

    def test_active_set_repo_scoped_current_url_resolves_unscoped_current_node(self) -> None:
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                owner="current",
                repo="repo",
                issue_issue_number=123,
                issue_title="Current issue",
            )
            self._run_runtime(
                target, ["new", "issue", "--epic", "2", "--title", "Foreign mirror", "--github-issue", "124"]
            )

            foreign_issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00124-foreign-mirror"
                / ".meta.json"
            )
            foreign_meta = json.loads(foreign_issue_meta.read_text(encoding="utf-8"))
            foreign_meta["github"] = {"issue_number": 123, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(foreign_issue_meta, foreign_meta)

            by_url = self._run_runtime_capture(
                target,
                ["active", "set", "https://github.com/current/repo/issues/123"],
            )
            assert by_url.returncode == 0, by_url.stdout + by_url.stderr
            assert "spec-dock: ok (active set)" in by_url.stdout

            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            assert active["issue"]["id"] == "iss-00123"

    def test_active_set_rejects_non_canonical_url_like_target_and_keeps_active_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123, issue_title="Current issue")
            self._run_runtime(
                target, ["new", "issue", "--epic", "2", "--title", "Baseline issue", "--github-issue", "124"]
            )

            baseline = self._run_runtime_capture(target, ["active", "set", "iss-00124"])
            assert baseline.returncode == 0, baseline.stdout + baseline.stderr
            active_path = target / "spec-dock" / ".agent" / "active.json"
            before = active_path.read_text(encoding="utf-8")
            baseline_active = json.loads(before)
            assert baseline_active["issue"]["id"] == "iss-00124"

            invalid = self._run_runtime_capture(
                target,
                ["active", "set", "git@github.com:owner/repo/issues/123"],
            )
            assert invalid.returncode != 0, invalid.stdout + invalid.stderr
            assert "Invalid target" in invalid.stderr

            after = active_path.read_text(encoding="utf-8")
            assert after == before

    def test_active_set_rejects_conflict_between_positional_target_and_id_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            p = self._run_runtime_capture(
                target,
                ["active", "set", "123", "--id", "iss-local-00001"],
            )
            assert p.returncode != 0, p.stdout + p.stderr
            assert "choose exactly one" in p.stderr

    def test_active_set_rejects_conflict_between_id_and_github_issue_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            p = self._run_runtime_capture(
                target,
                ["active", "set", "--id", "iss-local-00001", "--github-issue", "123"],
            )
            assert p.returncode != 0, p.stdout + p.stderr
            assert "choose exactly one" in p.stderr

    def test_active_set_rejects_non_positive_github_issue_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            p = self._run_runtime_capture(target, ["active", "set", "--github-issue", "0"])
            assert p.returncode != 0, p.stdout + p.stderr
            assert "positive integer" in p.stderr

    @pytest.mark.skip(
        reason="S05: covered by TestSetActiveApplication.test_set_active_checkout_uses_git_gateway_branch_decision_without_cli_git"
    )
    def test_active_set_github_issue_checkout_sets_active(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._init_origin_repo(target)
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )

            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123)

            # Make the working tree clean so checkout is allowed.
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "spec tree"],
            )

            # Provide a fake `gh` binary outside the git repo (keep working tree clean).
            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    'if [[ "$1" == "issue" && "$2" == "checkout" ]]; then\n'
                    '  n="$3"\n'
                    '  branch="gh-issue-${n}"\n'
                    '  git checkout -b "$branch" >/dev/null 2>&1 || git checkout "$branch" >/dev/null 2>&1\n'
                    "  exit 0\n"
                    "fi\n"
                    'echo "unexpected gh args: $@" >&2\n'
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                self._run_runtime(target, ["active", "set", "123", "--checkout", "--force"], env=test_env)
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "iss-00123-add-refresh-token"
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            assert active["issue"]["id"] == "iss-00123"
            assert active["issue"]["path"] == (
                "spec-dock/initiatives/init-00001-auth-platform/epics/"
                "epic-00002-jwt-auth/issues/iss-00123-add-refresh-token"
            )
            assert not active["issue"]["path"].startswith(str(target))

    @pytest.mark.skip(
        reason="S05: covered by TestSetActiveApplication.test_set_active_resolves_id_and_repo_scoped_github_target_without_cli"
    )
    def test_active_set_local_only_node_does_not_rename_branch(self) -> None:
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._init_origin_repo(target)
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )
            self._run_git(target, ["checkout", "-b", "feature/local-keep-branch"])

            self._create_same_repo_linked_hierarchy(target)
            self._materialize_local_compat_ids(target)
            self._run_runtime(target, ["active", "set", "iss-local-00001", "--force"])

            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "feature/local-keep-branch"

    @pytest.mark.skip(
        reason="S05: covered by TestSetActiveApplication.test_set_active_checkout_uses_git_gateway_branch_decision_without_cli_git"
    )
    def test_active_set_detached_head_creates_desired_branch(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._init_origin_repo(target)
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )

            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123)
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "spec tree"],
            )

            self._run_git(target, ["checkout", "--detach"])
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "HEAD"

            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    'if [[ "$1" == "issue" && "$2" == "checkout" ]]; then\n'
                    "  exit 0\n"
                    "fi\n"
                    'if [[ "$1" == "issue" && "$2" == "develop" ]]; then\n'
                    "  exit 0\n"
                    "fi\n"
                    'echo "unexpected gh args: $@" >&2\n'
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                p = self._run_runtime_capture(target, ["active", "set", "123", "--checkout", "--force"], env=test_env)
                assert p.returncode == 0, p.stdout + p.stderr

            desired = "iss-00123-add-refresh-token"
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == desired

    @pytest.mark.skip(
        reason="S05: covered by TestSetActiveApplication.test_set_active_checkout_uses_git_gateway_branch_decision_without_cli_git"
    )
    def test_active_set_reuses_existing_desired_branch_without_gh_checkout(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._init_origin_repo(target)
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )
            base_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()

            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123)
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "spec tree"],
            )

            desired = "iss-00123-add-refresh-token"
            self._run_git(target, ["checkout", "-b", desired])
            self._run_git(target, ["checkout", base_branch])

            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                counter = bin_dir / "counter.txt"
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    f"counter_file='{counter.as_posix()}'\n"
                    'if [[ "$1" == "issue" && "$2" == "checkout" ]]; then\n'
                    "  c=0\n"
                    '  if [[ -f "$counter_file" ]]; then\n'
                    '    c=$(cat "$counter_file")\n'
                    "  fi\n"
                    '  echo $((c+1)) > "$counter_file"\n'
                    "  exit 0\n"
                    "fi\n"
                    'if [[ "$1" == "issue" && "$2" == "develop" ]]; then\n'
                    "  c=0\n"
                    '  if [[ -f "$counter_file" ]]; then\n'
                    '    c=$(cat "$counter_file")\n'
                    "  fi\n"
                    '  echo $((c+1)) > "$counter_file"\n'
                    "  exit 0\n"
                    "fi\n"
                    'echo "unexpected gh args: $@" >&2\n'
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                p = self._run_runtime_capture(target, ["active", "set", "123", "--checkout", "--force"], env=test_env)
                assert p.returncode == 0, p.stdout + p.stderr
                assert "spec-dock: (warn)" in p.stderr
                assert "reusing existing branch" in p.stderr
                assert "content is not verified" in p.stderr

                if counter.exists():
                    assert counter.read_text(encoding="utf-8").strip() == "0"

            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == desired

    @pytest.mark.skip(
        reason="S05: covered by TestSetActiveApplication.test_set_active_checkout_uses_git_gateway_branch_decision_without_cli_git"
    )
    def test_active_set_reuses_existing_branch_recomputes_desired_after_checkout_for_github_issue_target(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._init_origin_repo(target)
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )
            base_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()

            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123)
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "spec tree"],
            )

            # Prepare an existing desired branch whose .meta.json.slug differs from the base branch.
            desired_before = "iss-00123-add-refresh-token"
            self._run_git(target, ["checkout", "-b", desired_before])
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["slug"] = "refresh-token"
            self._write_json_force(issue_meta, meta)
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "change slug"],
            )
            self._run_git(target, ["checkout", base_branch])

            # Ensure the reuse branch path does not call gh.
            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                counter = bin_dir / "counter.txt"
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    f"counter_file='{counter.as_posix()}'\n"
                    'if [[ "$1" == "issue" && "$2" == "checkout" ]]; then\n'
                    "  c=0\n"
                    '  if [[ -f "$counter_file" ]]; then\n'
                    '    c=$(cat "$counter_file")\n'
                    "  fi\n"
                    '  echo $((c+1)) > "$counter_file"\n'
                    "  exit 0\n"
                    "fi\n"
                    'if [[ "$1" == "issue" && "$2" == "develop" ]]; then\n'
                    "  c=0\n"
                    '  if [[ -f "$counter_file" ]]; then\n'
                    '    c=$(cat "$counter_file")\n'
                    "  fi\n"
                    '  echo $((c+1)) > "$counter_file"\n'
                    "  exit 0\n"
                    "fi\n"
                    'echo "unexpected gh args: $@" >&2\n'
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                p = self._run_runtime_capture(target, ["active", "set", "123", "--checkout", "--force"], env=test_env)
                assert p.returncode == 0, p.stdout + p.stderr
                if counter.exists():
                    assert counter.read_text(encoding="utf-8").strip() == "0"

            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "iss-00123-add-refresh-token"

    @pytest.mark.skip(
        reason="S05: covered by TestSetActiveApplication.test_set_active_checkout_uses_git_gateway_branch_decision_without_cli_git"
    )
    def test_active_set_reuses_existing_branch_recomputes_desired_after_checkout_for_node_id_target(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._init_origin_repo(target)
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )
            base_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()

            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123)
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "spec tree"],
            )

            # Prepare an existing desired branch whose .meta.json.slug differs from the base branch.
            desired_before = "iss-00123-add-refresh-token"
            self._run_git(target, ["checkout", "-b", desired_before])
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["slug"] = "refresh-token"
            self._write_json_force(issue_meta, meta)
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "change slug"],
            )
            self._run_git(target, ["checkout", base_branch])

            # Ensure the reuse branch path does not call gh.
            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                counter = bin_dir / "counter.txt"
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    f"counter_file='{counter.as_posix()}'\n"
                    'if [[ "$1" == "issue" && "$2" == "checkout" ]]; then\n'
                    "  c=0\n"
                    '  if [[ -f "$counter_file" ]]; then\n'
                    '    c=$(cat "$counter_file")\n'
                    "  fi\n"
                    '  echo $((c+1)) > "$counter_file"\n'
                    "  exit 0\n"
                    "fi\n"
                    'if [[ "$1" == "issue" && "$2" == "develop" ]]; then\n'
                    "  c=0\n"
                    '  if [[ -f "$counter_file" ]]; then\n'
                    '    c=$(cat "$counter_file")\n'
                    "  fi\n"
                    '  echo $((c+1)) > "$counter_file"\n'
                    "  exit 0\n"
                    "fi\n"
                    'echo "unexpected gh args: $@" >&2\n'
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                p = self._run_runtime_capture(
                    target, ["active", "set", "iss-00123", "--checkout", "--force"], env=test_env
                )
                assert p.returncode == 0, p.stdout + p.stderr
                if counter.exists():
                    assert counter.read_text(encoding="utf-8").strip() == "0"

            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "iss-00123-add-refresh-token"

    @pytest.mark.skip(
        reason="S05: covered by TestActiveDomain.test_branch_decision_falls_back_to_id_for_non_ascii_or_invalid_slug_without_git"
    )
    def test_active_set_fallbacks_to_id_when_id_slug_is_non_ascii(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )

            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123)

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-add-refresh-token"
                / ".meta.json"
            )
            data = json.loads(issue_meta.read_text(encoding="utf-8"))
            data["slug"] = "日本語"
            self._write_json_force(issue_meta, data)
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "non-ascii slug"],
            )

            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    'if [[ "$1" == "issue" && "$2" == "checkout" ]]; then\n'
                    '  n="$3"\n'
                    '  branch="gh-issue-${n}"\n'
                    '  git checkout -b "$branch" >/dev/null 2>&1 || git checkout "$branch" >/dev/null 2>&1\n'
                    "  exit 0\n"
                    "fi\n"
                    'if [[ "$1" == "issue" && "$2" == "develop" ]]; then\n'
                    '  n="$3"\n'
                    '  branch="gh-issue-${n}"\n'
                    '  git checkout -b "$branch" >/dev/null 2>&1 || git checkout "$branch" >/dev/null 2>&1\n'
                    "  exit 0\n"
                    "fi\n"
                    'echo "unexpected gh args: $@" >&2\n'
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                p = self._run_runtime_capture(target, ["active", "set", "123", "--checkout", "--force"], env=test_env)
                assert p.returncode == 0, p.stdout + p.stderr
                assert "spec-dock: (warn)" in p.stderr
                assert "non-ascii" in p.stderr
                assert "fallback to id" in p.stderr

            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "iss-00123"

    @pytest.mark.skip(
        reason="S05: covered by TestActiveDomain.test_branch_decision_falls_back_to_id_for_non_ascii_or_invalid_slug_without_git"
    )
    def test_active_set_fallbacks_to_id_when_id_slug_is_invalid_ref(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )

            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123)

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-add-refresh-token"
                / ".meta.json"
            )
            data = json.loads(issue_meta.read_text(encoding="utf-8"))
            data["slug"] = "a..b"
            self._write_json_force(issue_meta, data)
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "invalid-ref slug"],
            )

            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    'if [[ "$1" == "issue" && "$2" == "checkout" ]]; then\n'
                    '  n="$3"\n'
                    '  branch="gh-issue-${n}"\n'
                    '  git checkout -b "$branch" >/dev/null 2>&1 || git checkout "$branch" >/dev/null 2>&1\n'
                    "  exit 0\n"
                    "fi\n"
                    'if [[ "$1" == "issue" && "$2" == "develop" ]]; then\n'
                    '  n="$3"\n'
                    '  branch="gh-issue-${n}"\n'
                    '  git checkout -b "$branch" >/dev/null 2>&1 || git checkout "$branch" >/dev/null 2>&1\n'
                    "  exit 0\n"
                    "fi\n"
                    'echo "unexpected gh args: $@" >&2\n'
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                p = self._run_runtime_capture(target, ["active", "set", "123", "--checkout", "--force"], env=test_env)
                assert p.returncode == 0, p.stdout + p.stderr
                assert "spec-dock: (warn)" in p.stderr
                assert "invalid ref" in p.stderr
                assert "fallback to id" in p.stderr

            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "iss-00123"

    @pytest.mark.skip(
        reason="S05: covered by TestSetActiveApplication.test_set_active_resolves_id_and_repo_scoped_github_target_without_cli"
    )
    def test_active_set_parses_hash_and_url_targets(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._init_origin_repo(target)
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )

            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123)
            issue_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-add-refresh-token"
                / ".meta.json"
            )
            issue_meta = json.loads(issue_meta_path.read_text(encoding="utf-8"))
            issue_meta["github"] = {"issue_number": 123, "repo_owner": "example", "repo_name": "repo"}
            self._write_json_force(issue_meta_path, issue_meta)

            # Make the working tree clean so checkout is allowed.
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "spec tree"],
            )

            # Provide a fake `gh` binary that records invocations and checks out a branch.
            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                counter = bin_dir / "counter.txt"
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    f"counter_file='{counter.as_posix()}'\n"
                    'if [[ "$1" == "issue" && "$2" == "checkout" ]]; then\n'
                    '  n="$3"\n'
                    '  branch="gh-issue-${n}"\n'
                    '  git checkout -b "$branch" >/dev/null 2>&1 || git checkout "$branch" >/dev/null 2>&1\n'
                    "  c=0\n"
                    '  if [[ -f "$counter_file" ]]; then\n'
                    '    c=$(cat "$counter_file")\n'
                    "  fi\n"
                    '  echo $((c+1)) > "$counter_file"\n'
                    "  exit 0\n"
                    "fi\n"
                    'echo "unexpected gh args: $@" >&2\n'
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                # Both `#123` and repo-scoped issue URL should be accepted and behave the same.
                # Default is no-checkout, so gh should not be invoked.
                self._run_runtime(target, ["active", "set", "#123", "--force"], env=test_env)
                self._run_runtime(
                    target, ["active", "set", "https://github.com/example/repo/issues/123", "--force"], env=test_env
                )
                assert not counter.exists()

            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            assert active["issue"]["id"] == "iss-00123"

    @pytest.mark.skip(
        reason="S05: covered by TestSetActiveApplication.test_set_active_resolves_id_and_repo_scoped_github_target_without_cli"
    )
    def test_active_set_github_issue_number_requires_linked_node(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._init_origin_repo(target)
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )

            self._create_same_repo_linked_hierarchy(target)

            # Make the working tree clean so checkout is allowed.
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "spec tree"],
            )

            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                counter = bin_dir / "counter.txt"
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    f"counter_file='{counter.as_posix()}'\n"
                    'if [[ "$1" == "issue" && "$2" == "checkout" ]]; then\n'
                    '  n="$3"\n'
                    '  branch="gh-issue-${n}"\n'
                    '  git checkout -b "$branch" >/dev/null 2>&1 || git checkout "$branch" >/dev/null 2>&1\n'
                    "  c=0\n"
                    '  if [[ -f "$counter_file" ]]; then\n'
                    '    c=$(cat "$counter_file")\n'
                    "  fi\n"
                    '  echo $((c+1)) > "$counter_file"\n'
                    "  exit 0\n"
                    "fi\n"
                    'echo "unexpected gh args: $@" >&2\n'
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                # GitHub issue number requires a linked node; command fails without checkout side effects.
                self._run_runtime_expect_fail(target, ["active", "set", "999"], env=test_env)
                assert not counter.exists()

    @pytest.mark.skip(
        reason="S05: covered by TestSetActiveApplication.test_set_active_deps_guard_blocks_without_writing_and_force_writes_with_warning_without_cli"
    )
    def test_active_set_blocked_by_deps_refuses_without_force(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Dep issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Target issue"],
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00302-target-issue"
            )
            self._set_meta_depends_on(issue_dir, [301])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            # Baseline: active is set to the dependency issue (ready).
            self._run_runtime(target, ["active", "set", "iss-00301", "--force"])
            before = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")

            # Blocked: active must not be updated.
            p = self._run_runtime_capture(target, ["active", "set", "iss-00302", "--github"], env=test_env)
            assert p.returncode == 1, p.stdout + p.stderr
            assert "iss-00301" in p.stderr

            after = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")
            assert after == before

    @pytest.mark.skip(
        reason="S05: covered by TestSetActiveApplication.test_set_active_deps_guard_blocks_without_writing_and_force_writes_with_warning_without_cli"
    )
    def test_active_set_force_allows_blocked_target_and_warns(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Dep issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Target issue"],
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00302-target-issue"
            )
            self._set_meta_depends_on(issue_dir, [301])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["active", "set", "iss-00302", "--github", "--force"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: (warn)" in p.stderr
            assert "iss-00301" in p.stderr

            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            assert active["issue"]["id"] == "iss-00302"

    @pytest.mark.skip(
        reason="S05: covered by TestSetActiveApplication.test_set_active_deps_guard_blocks_without_writing_and_force_writes_with_warning_without_cli"
    )
    def test_active_set_is_blocked_when_deps_not_ready(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "Main epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Target issue"],
            )
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "202", "--title", "Deps epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "401", "--title", "Open blocker"],
            )

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-main-epic"
                / "issues"
                / "iss-00301-target-issue"
            )
            self._set_meta_depends_on(target_issue_dir, ["epic-00202"])

            baseline = self._run_runtime_capture(target, ["active", "set", "iss-00401", "--force"])
            assert baseline.returncode == 0, baseline.stdout + baseline.stderr
            before = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Main", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 202, "state": "OPEN", "title": "Deps", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 401, "state": "OPEN", "title": "Blocker", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["active", "set", "iss-00301", "--github"], env=test_env)
            assert p.returncode == 1, p.stdout + p.stderr
            assert "iss-00401" in p.stderr
            assert "epic-00202" not in p.stderr
            after = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")
            assert after == before

    @pytest.mark.skip(
        reason="S05: covered by TestSetActiveApplication.test_set_active_deps_guard_blocks_without_writing_and_force_writes_with_warning_without_cli"
    )
    def test_active_set_force_overrides_deps_guard(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "Main epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Target issue"],
            )
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "202", "--title", "Deps epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "401", "--title", "Open blocker"],
            )

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-main-epic"
                / "issues"
                / "iss-00301-target-issue"
            )
            self._set_meta_depends_on(target_issue_dir, ["epic-00202"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Main", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 202, "state": "OPEN", "title": "Deps", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 401, "state": "OPEN", "title": "Blocker", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["active", "set", "iss-00301", "--github", "--force"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr
            assert "deps_blocked" in p.stderr
            assert "iss-00401" in p.stderr
            assert "epic-00202" not in p.stderr

            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            assert active["issue"]["id"] == "iss-00301"

    def test_active_set_ignores_unreachable_dependency_cycle_and_only_patches_active_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target, ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"]
            )
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Cycle A"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Cycle B"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "303", "--title", "Target C"])

            # Prepare cached `.agent/index*.json` / `.agent/tree*.json` to verify active-only patching.
            self._run_runtime(target, ["sync", "--no-github", "--no-update-active"])

            agent_dir = target / "spec-dock" / ".agent"
            assert (agent_dir / "index-all.json").is_file()
            assert (agent_dir / "tree-all.json").is_file()
            assert (agent_dir / "index.json").is_file()
            assert (agent_dir / "tree.json").is_file()

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
            )
            self._set_meta_depends_on(issue_dir / "iss-00301-cycle-a", ["iss-00302"])
            self._set_meta_depends_on(issue_dir / "iss-00302-cycle-b", ["iss-00301"])

            p = self._run_runtime_capture(target, ["active", "set", "iss-00303"])
            assert p.returncode == 0, p.stdout + p.stderr
            active = json.loads((agent_dir / "active.json").read_text(encoding="utf-8"))
            assert active["issue"]["id"] == "iss-00303"

            # `active set` must not run `sync`: cached active field must remain unchanged.
            state_index_all = json.loads((agent_dir / "index-all.json").read_text(encoding="utf-8"))
            state_tree_all = json.loads((agent_dir / "tree-all.json").read_text(encoding="utf-8"))
            state_index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            state_tree = json.loads((agent_dir / "tree.json").read_text(encoding="utf-8"))
            for state in (state_index_all, state_tree_all, state_index, state_tree):
                assert state["active"]["issue"]["id"] == "iss-00303"

    @pytest.mark.skip(
        reason="S05: covered by TestSetActiveApplication.test_set_active_github_uses_live_issue_state_and_no_github_uses_cache_without_cli"
    )
    def test_active_set_without_github_uses_synced_index_for_deps_guard(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Dep issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Target issue"],
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00302-target-issue"
            )
            self._set_meta_depends_on(issue_dir, [301])

            # Baseline: set ready dep issue to active without live GitHub setup calls.
            self._run_runtime(target, ["active", "set", "iss-00301", "--no-github", "--force"])
            before = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            # 1) Dependency is OPEN on GitHub -> index says open -> blocked.
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            p_sync_open = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            assert p_sync_open.returncode == 0, p_sync_open.stdout + p_sync_open.stderr

            # Guard: `active set --no-github` must not fetch GitHub.
            guard_log_open = bin_dir / "gh-guard-open.log"
            guard_log_open.unlink(missing_ok=True)
            self._make_gh_issue_list_stub(bin_dir, issues=[], fail=True, log_path=guard_log_open)

            p_blocked = self._run_runtime_capture(target, ["active", "set", "iss-00302", "--no-github"], env=test_env)
            assert p_blocked.returncode == 1, p_blocked.stdout + p_blocked.stderr
            assert "iss-00301" in p_blocked.stderr
            after_blocked = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")
            assert after_blocked == before
            assert not guard_log_open.exists(), "gh must not be invoked with --no-github"

            # 2) Dependency is CLOSED on GitHub -> index says done -> allowed.
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            p_sync_closed = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            assert p_sync_closed.returncode == 0, p_sync_closed.stdout + p_sync_closed.stderr

            # Inject a conflicting snapshot in todo view.
            # `--no-github` deps guard must still prefer `index-all.json`.
            index_all_path = target / "spec-dock" / ".agent" / "index-all.json"
            index_todo_path = target / "spec-dock" / ".agent" / "index.json"
            index_all = json.loads(index_all_path.read_text(encoding="utf-8"))
            index_todo = json.loads(index_todo_path.read_text(encoding="utf-8"))
            shadow = dict(index_all["nodes"]["iss-00301"])
            shadow["status"] = "open"
            index_todo["nodes"]["iss-00301"] = shadow
            index_todo_path.write_text(json.dumps(index_todo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            # Guard again: no gh calls on active set with --no-github.
            guard_log_closed = bin_dir / "gh-guard-closed.log"
            guard_log_closed.unlink(missing_ok=True)
            self._make_gh_issue_list_stub(bin_dir, issues=[], fail=True, log_path=guard_log_closed)

            p_allowed = self._run_runtime_capture(target, ["active", "set", "iss-00302", "--no-github"], env=test_env)
            assert p_allowed.returncode == 0, p_allowed.stdout + p_allowed.stderr
            assert not guard_log_closed.exists(), "gh must not be invoked with --no-github"
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            assert active["issue"]["id"] == "iss-00302"

            # The cached index statuses must survive a successful active set,
            # so `--no-github` deps checks can continue to use `.agent/index.json`.
            guard_log_after = bin_dir / "gh-guard-after-active.log"
            guard_log_after.unlink(missing_ok=True)
            self._make_gh_issue_list_stub(bin_dir, issues=[], fail=True, log_path=guard_log_after)
            p_after = self._run_runtime_capture(
                target, ["deps", "check", "iss-00302", "--no-github", "--json"], env=test_env
            )
            assert p_after.returncode == 0, p_after.stdout + p_after.stderr
            assert not guard_log_after.exists(), "gh must not be invoked with --no-github"
            data = json.loads(p_after.stdout)
            assert data["ready"]
            assert data["blockers"] == []
            assert data["nodes"]["iss-00301"]["state"] == "done"

    @pytest.mark.skip(
        reason="S05: covered by TestSetActiveApplication.test_set_active_github_uses_live_issue_state_and_no_github_uses_cache_without_cli"
    )
    def test_active_set_default_github_uses_live_state_for_deps_guard(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Dep issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Target issue"],
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00302-target-issue"
            )
            self._set_meta_depends_on(issue_dir, [301])

            # Baseline active state is established cache-only so setup cannot hit real gh.
            self._run_runtime(target, ["active", "set", "iss-00301", "--no-github", "--force"])
            before = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            log_open = bin_dir / "gh-live-open.log"
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
                log_path=log_open,
            )
            p_blocked = self._run_runtime_capture(target, ["active", "set", "iss-00302"], env=test_env)
            assert p_blocked.returncode == 1, p_blocked.stdout + p_blocked.stderr
            assert log_open.exists(), "active set default must invoke gh for live deps state"
            assert "iss-00301" in p_blocked.stderr
            after_blocked = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")
            assert after_blocked == before

            log_closed = bin_dir / "gh-live-closed.log"
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
                log_path=log_closed,
            )
            p_allowed = self._run_runtime_capture(target, ["active", "set", "iss-00302"], env=test_env)
            assert p_allowed.returncode == 0, p_allowed.stdout + p_allowed.stderr
            assert log_closed.exists(), "active set default must invoke gh for live deps state"
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            assert active["issue"]["id"] == "iss-00302"

    @pytest.mark.skip(
        reason="S05: covered by TestSetActiveApplication.test_set_active_github_uses_live_issue_state_and_no_github_uses_cache_without_cli"
    )
    def test_active_set_without_github_uses_index_snapshot_when_present(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "Main epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Target issue"],
            )
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "202", "--title", "Deps epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "401", "--title", "Done blocker"],
            )

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-main-epic"
                / "issues"
                / "iss-00301-target-issue"
            )
            self._set_meta_depends_on(target_issue_dir, ["epic-00202"])

            baseline = self._run_runtime_capture(target, ["active", "set", "iss-00301", "--force"])
            assert baseline.returncode == 0, baseline.stdout + baseline.stderr

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Main", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 202, "state": "OPEN", "title": "Deps", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 401, "state": "CLOSED", "title": "Blocker", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p_sync = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            assert p_sync.returncode == 0, p_sync.stdout + p_sync.stderr

            index_all_path = target / "spec-dock" / ".agent" / "index-all.json"
            index_todo_path = target / "spec-dock" / ".agent" / "index.json"
            index_all = json.loads(index_all_path.read_text(encoding="utf-8"))
            index_todo = json.loads(index_todo_path.read_text(encoding="utf-8"))
            shadow = dict(index_all["nodes"]["iss-00401"])
            shadow["status"] = "open"
            index_todo["nodes"]["iss-00401"] = shadow
            index_todo_path.write_text(json.dumps(index_todo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            guard_log = bin_dir / "gh-guard-snapshot.log"
            guard_log.unlink(missing_ok=True)
            self._make_gh_issue_list_stub(bin_dir, issues=[], fail=True, log_path=guard_log)

            p = self._run_runtime_capture(target, ["active", "set", "iss-00301", "--no-github"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr
            assert not guard_log.exists(), "gh must not be invoked with --no-github"
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            assert active["issue"]["id"] == "iss-00301"

    @pytest.mark.skip(
        reason="S05: covered by TestSetActiveApplication.test_set_active_deps_guard_blocks_without_writing_and_force_writes_with_warning_without_cli"
    )
    def test_active_set_without_github_blocks_when_snapshot_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "Main epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Target issue"],
            )
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "202", "--title", "Deps epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "401", "--title", "Unknown blocker"],
            )

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-main-epic"
                / "issues"
                / "iss-00301-target-issue"
            )
            self._set_meta_depends_on(target_issue_dir, ["epic-00202"])

            baseline = self._run_runtime_capture(target, ["active", "set", "iss-00401", "--force"])
            assert baseline.returncode == 0, baseline.stdout + baseline.stderr
            before = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")

            (target / "spec-dock" / ".agent" / "index-all.json").unlink(missing_ok=True)
            (target / "spec-dock" / ".agent" / "index.json").unlink(missing_ok=True)

            p = self._run_runtime_capture(target, ["active", "set", "iss-00301"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert "iss-00401" in p.stderr
            assert "epic-00202" not in p.stderr
            after = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")
            assert after == before

    @pytest.mark.skip(
        reason="S05: covered by TestSetActiveApplication.test_set_active_resolves_id_and_repo_scoped_github_target_without_cli"
    )
    def test_active_set_without_github_local_issue_without_deps_is_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
                issue_title="Unknown issue",
            )
            self._materialize_local_compat_ids(target)
            self._run_runtime(target, ["active", "clear"])

            agent_dir = target / "spec-dock" / ".agent"
            (agent_dir / "index-all.json").unlink(missing_ok=True)
            (agent_dir / "index.json").unlink(missing_ok=True)

            before = (agent_dir / "active.json").read_text(encoding="utf-8")
            p = self._run_runtime_capture(target, ["active", "set", "iss-local-00001"])
            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok (active set)" in p.stdout
            after = (agent_dir / "active.json").read_text(encoding="utf-8")
            assert after != before
            active = json.loads(after)
            assert active["issue"]["id"] == "iss-local-00001"

    def test_active_set_epic_and_initiative_ignore_dependency_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target, ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "Main epic"]
            )
            self._run_runtime(
                target, ["new", "epic", "--initiative", "101", "--github-issue", "202", "--title", "Blocker epic"]
            )
            self._run_runtime(
                target, ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Target issue"]
            )
            self._run_runtime(
                target, ["new", "issue", "--epic", "202", "--github-issue", "401", "--title", "Blocker issue"]
            )

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-main-epic"
                / "issues"
                / "iss-00301-target-issue"
            )
            self._set_meta_depends_on(target_issue_dir, ["epic-00202"])

            self._run_runtime(target, ["sync", "--no-github", "--no-update-active"])
            agent_dir = target / "spec-dock" / ".agent"
            self._run_runtime(target, ["active", "clear"])

            selected_epic = self._run_runtime_capture(target, ["active", "set", "epic-00201"])
            assert selected_epic.returncode == 0, selected_epic.stdout + selected_epic.stderr
            active_after_epic = json.loads((agent_dir / "active.json").read_text(encoding="utf-8"))
            assert active_after_epic["initiative"]["id"] == "init-00101"
            assert active_after_epic["epic"]["id"] == "epic-00201"
            assert active_after_epic["issue"] is None

            self._run_runtime(target, ["active", "clear"])
            selected_init = self._run_runtime_capture(target, ["active", "set", "init-00101"])
            assert selected_init.returncode == 0, selected_init.stdout + selected_init.stderr
            active_after_init = json.loads((agent_dir / "active.json").read_text(encoding="utf-8"))
            assert active_after_init["initiative"]["id"] == "init-00101"
            assert active_after_init["epic"] is None
            assert active_after_init["issue"] is None

    @pytest.mark.skip(
        reason="S05: covered by TestSetActiveApplication.test_set_active_checkout_uses_git_gateway_branch_decision_without_cli_git"
    )
    def test_active_set_issue_auto_checkouts_when_github_linked(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._init_origin_repo(target)
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )

            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123)

            # Make the working tree clean so checkout is allowed.
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "spec tree"],
            )

            # Provide a fake `gh` binary that records invocations and checks out a branch.
            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                counter = bin_dir / "counter.txt"
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    f"counter_file='{counter.as_posix()}'\n"
                    'if [[ "$1" == "issue" && "$2" == "checkout" ]]; then\n'
                    '  n="$3"\n'
                    '  branch="gh-issue-${n}"\n'
                    '  git checkout -b "$branch" >/dev/null 2>&1 || git checkout "$branch" >/dev/null 2>&1\n'
                    "  c=0\n"
                    '  if [[ -f "$counter_file" ]]; then\n'
                    '    c=$(cat "$counter_file")\n'
                    "  fi\n"
                    '  echo $((c+1)) > "$counter_file"\n'
                    "  exit 0\n"
                    "fi\n"
                    'echo "unexpected gh args: $@" >&2\n'
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                # Explicit checkout should switch branches, but gh should not be invoked.
                self._run_runtime(target, ["active", "set", "iss-0123", "--checkout", "--force"], env=test_env)
                assert not counter.exists()

            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            assert active["issue"]["id"] == "iss-00123"
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "iss-00123-add-refresh-token"

    @pytest.mark.skip(reason="S01 removed active set checkout; issue start owns checkout and branch re-resolution")
    def test_active_set_re_resolves_node_after_checkout_when_id_format_changes(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._init_origin_repo(target)
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )
            base_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()

            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123)

            # Make the working tree clean so checkout is allowed.
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "spec tree"],
            )

            # Prepare the checkout branch where the node id format differs (e.g. iss-00123 -> iss-0123).
            self._run_git(target, ["checkout", "-b", "gh-issue-123"])
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["id"] = "iss-0123"
            self._write_json_force(issue_meta, meta)
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "change id format"],
            )
            self._run_git(target, ["checkout", base_branch])

            # Provide a fake `gh` binary that checks out the prepared branch.
            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    'if [[ "$1" == "issue" && "$2" == "checkout" ]]; then\n'
                    '  n="$3"\n'
                    '  branch="gh-issue-${n}"\n'
                    '  git checkout "$branch" >/dev/null 2>&1\n'
                    "  exit 0\n"
                    "fi\n"
                    'echo "unexpected gh args: $@" >&2\n'
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                # Active is resolved before checkout and must remain stable.
                self._run_runtime(target, ["active", "set", "iss-00123", "--checkout", "--force"], env=test_env)

            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            assert active["issue"]["id"] == "iss-00123"

    def test_active_set_github_issue_checkout_refuses_dirty_working_tree(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._init_origin_repo(target)
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )

            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123)

            # Provide a fake `gh` binary (should not be invoked due to dirty tree).
            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                'echo "gh should not be invoked when working tree is dirty" >&2\n'
                "exit 1\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            self._run_runtime_expect_fail(target, ["active", "set", "123", "--checkout"], env=test_env)
            assert not (target / "spec-dock" / ".agent" / "active.json").exists()
