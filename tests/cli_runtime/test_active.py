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
