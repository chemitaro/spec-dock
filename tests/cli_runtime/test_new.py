import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from types import SimpleNamespace

import pytest

from tests.cli_runtime.harness import (
    CliRuntimeHarness,
    main,
)


class TestCliNew(CliRuntimeHarness):
    def _init_origin_repo(self, target: Path, *, owner: str = "example", repo: str = "repo") -> None:
        if shutil.which("git") is None:
            pytest.skip("git not available")
        self._run_git(target, ["init"])
        self._run_git(target, ["remote", "add", "origin", f"https://github.com/{owner}/{repo}.git"])

    def _create_same_repo_linked_hierarchy(self, target: Path) -> None:
        self._init_origin_repo(target)
        self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"])
        self._run_runtime(target, ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"])
        self._run_runtime(
            target,
            ["new", "issue", "--epic", "2", "--title", "Add refresh token", "--github-issue", "3"],
        )

    def _write_runtime_clock(self, target: Path, *, now_iso: str, today: str) -> None:
        runtime_clock = target / "spec-dock" / "scripts" / "spec_dock_runtime" / "infra" / "clock.py"
        runtime_clock.write_text(
            (
                "from __future__ import annotations\n\n"
                f"def now_iso() -> str:\n    return {now_iso!r}\n\n"
                f"def today() -> str:\n    return {today!r}\n"
            ),
            encoding="utf-8",
        )

    def _assert_auto_sync_artifacts_include(
        self,
        target: Path,
        node_id: str,
        *,
        require_node_in_working_artifacts: bool = True,
    ) -> None:
        specdock_dir = target / "spec-dock"
        agent_dir = specdock_dir / ".agent"
        index_all_path = agent_dir / "index-all.json"
        index_path = agent_dir / "index.json"
        tree_all_path = agent_dir / "tree-all.json"
        tree_path = agent_dir / "tree.json"
        deps_issues_path = agent_dir / "deps-issues.json"
        tree_all_puml_path = specdock_dir / "tree-all.puml"
        tree_puml_path = specdock_dir / "tree.puml"
        deps_issues_puml_path = specdock_dir / "deps-issues.puml"
        dashboard_path = specdock_dir / "dashboard.md"
        artifact_paths = (
            index_all_path,
            index_path,
            tree_all_path,
            tree_path,
            deps_issues_path,
            tree_all_puml_path,
            tree_puml_path,
            deps_issues_puml_path,
            dashboard_path,
        )
        for artifact_path in artifact_paths:
            assert artifact_path.is_file(), f"missing artifact: {artifact_path}"

        index_all = json.loads(index_all_path.read_text(encoding="utf-8"))
        tree_all = json.loads(tree_all_path.read_text(encoding="utf-8"))
        tree = json.loads(tree_path.read_text(encoding="utf-8"))
        deps_issues = json.loads(deps_issues_path.read_text(encoding="utf-8"))
        assert node_id in index_all["nodes"]
        assert node_id in self._collect_tree_node_ids(tree_all)
        assert deps_issues["projection"] == "issue-readiness-with-dependency-context"
        assert deps_issues["deps"]["valid"]
        assert deps_issues["source"] == {"sync_state": "readiness_evaluation", "schema_version": 2}
        for text_path in (tree_all_puml_path, tree_puml_path, deps_issues_puml_path):
            assert "@startuml" in text_path.read_text(encoding="utf-8")
        if node_id.startswith("iss-"):
            assert node_id in tree_all_puml_path.read_text(encoding="utf-8")
        if require_node_in_working_artifacts:
            index = json.loads(index_path.read_text(encoding="utf-8"))
            assert node_id in index["nodes"]
            assert node_id in self._collect_tree_node_ids(tree)
            if node_id.startswith("iss-"):
                assert node_id in deps_issues["nodes"]
                assert node_id in tree_puml_path.read_text(encoding="utf-8")
                assert node_id in deps_issues_puml_path.read_text(encoding="utf-8")
            assert node_id in dashboard_path.read_text(encoding="utf-8")

    def _collect_tree_node_ids(self, tree_payload: dict[str, object]) -> set[str]:
        node_ids: set[str] = set()
        roots = tree_payload.get("tree")
        if not isinstance(roots, list):
            return node_ids
        for initiative in roots:
            if not isinstance(initiative, dict):
                continue
            init_id = initiative.get("id")
            if isinstance(init_id, str):
                node_ids.add(init_id)
            epics = initiative.get("epics")
            if not isinstance(epics, list):
                continue
            for epic in epics:
                if not isinstance(epic, dict):
                    continue
                epic_id = epic.get("id")
                if isinstance(epic_id, str):
                    node_ids.add(epic_id)
                issues = epic.get("issues")
                if not isinstance(issues, list):
                    continue
                for issue in issues:
                    if not isinstance(issue, dict):
                        continue
                    issue_id = issue.get("id")
                    if isinstance(issue_id, str):
                        node_ids.add(issue_id)
        return node_ids

    def _read_create_auto_sync_artifacts(self, target: Path) -> dict[str, str | None]:
        artifact_paths = (
            target / "spec-dock" / ".agent" / "index-all.json",
            target / "spec-dock" / ".agent" / "index.json",
            target / "spec-dock" / ".agent" / "tree-all.json",
            target / "spec-dock" / ".agent" / "tree.json",
            target / "spec-dock" / ".agent" / "deps-issues.json",
            target / "spec-dock" / "tree-all.puml",
            target / "spec-dock" / "tree.puml",
            target / "spec-dock" / "deps-issues.puml",
            target / "spec-dock" / "dashboard.md",
        )
        return {
            path.relative_to(target).as_posix(): path.read_text(encoding="utf-8") if path.exists() else None
            for path in artifact_paths
        }

    def _install_gh_issue_list_stub(
        self,
        target: Path,
        *,
        issue_numbers: list[int],
        log_path: Path | None = None,
    ) -> dict[str, str]:
        bin_dir = target / ".bin-gh-list"
        bin_dir.mkdir(parents=True, exist_ok=True)
        self._make_gh_issue_list_stub(
            bin_dir,
            issues=[
                {
                    "number": issue_number,
                    "state": "OPEN",
                    "title": f"Issue {issue_number}",
                    "labels": [],
                    "updatedAt": f"2026-05-13T00:00:{issue_number:02d}Z",
                    "url": f"https://github.com/example/repo/issues/{issue_number}",
                }
                for issue_number in issue_numbers
            ],
            log_path=log_path,
        )
        return {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

    def test_new_initiative_auto_syncs_index_and_dashboard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)
            log_path = target / ".gh.log"
            test_env = self._install_gh_issue_list_stub(target, issue_numbers=[1], log_path=log_path)

            self._run_runtime(
                target,
                ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"],
                env=test_env,
            )

            self._assert_auto_sync_artifacts_include(
                target,
                "init-00001",
                require_node_in_working_artifacts=False,
            )
            assert "issue list" in log_path.read_text(encoding="utf-8")

    def test_new_epic_auto_syncs_index_and_dashboard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)
            test_env = self._install_gh_issue_list_stub(target, issue_numbers=[1, 2])
            self._run_runtime(
                target,
                ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"],
                env=test_env,
            )

            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"],
                env=test_env,
            )

            self._assert_auto_sync_artifacts_include(
                target,
                "epic-00002",
                require_node_in_working_artifacts=False,
            )

    def test_new_issue_auto_syncs_index_and_dashboard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)
            test_env = self._install_gh_issue_list_stub(target, issue_numbers=[1, 2, 3])
            self._run_runtime(
                target,
                ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"],
                env=test_env,
            )
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"],
                env=test_env,
            )

            self._run_runtime(
                target,
                ["new", "issue", "--epic", "2", "--title", "Add refresh token", "--github-issue", "3"],
                env=test_env,
            )

            self._assert_auto_sync_artifacts_include(target, "iss-00003")

    def test_new_issue_auto_sync_preserves_local_only_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)
            test_env = self._install_gh_issue_list_stub(target, issue_numbers=[1, 2, 3, 4])
            self._run_runtime(
                target,
                ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"],
                env=test_env,
            )
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"],
                env=test_env,
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "2", "--title", "Local holder", "--github-issue", "3"],
                env=test_env,
            )
            local_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-local-holder"
            )
            self._remove_github_link(local_issue_dir)

            self._run_runtime(
                target,
                ["new", "issue", "--epic", "2", "--title", "Linked followup", "--github-issue", "4"],
                env=test_env,
            )

            self._assert_auto_sync_artifacts_include(target, "iss-00003")
            self._assert_auto_sync_artifacts_include(target, "iss-00004")

    def test_new_failure_paths_do_not_run_post_sync_or_refresh_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)
            log_path = target / ".gh.log"
            test_env = self._install_gh_issue_list_stub(target, issue_numbers=[1, 2, 3], log_path=log_path)
            self._run_runtime(
                target,
                ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"],
                env=test_env,
            )
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"],
                env=test_env,
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "2", "--title", "Add refresh token", "--github-issue", "3"],
                env=test_env,
            )

            cases = (
                ["new", "initiative", "--title", "Duplicate initiative", "--github-issue", "1"],
                ["new", "epic", "--initiative", "missing", "--title", "Missing parent", "--github-issue", "4"],
                ["new", "issue", "--epic", "missing", "--title", "Missing parent", "--github-issue", "5"],
            )
            for argv in cases:
                case_label = " ".join(argv)
                before_artifacts = self._read_create_auto_sync_artifacts(target)
                log_path.write_text("", encoding="utf-8")

                p = self._run_runtime_capture(target, argv, env=test_env)

                assert p.returncode != 0, f"{case_label}: {p.stdout}{p.stderr}"
                assert before_artifacts == self._read_create_auto_sync_artifacts(target), (
                    f"{case_label}: argv={argv!r}"
                )
                assert log_path.read_text(encoding="utf-8") == "", f"{case_label}: argv={argv!r}"

    def test_new_node_id_option_is_parser_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            p = self._run_runtime_capture(
                target,
                [
                    "new",
                    "issue",
                    "--epic",
                    "2",
                    "--id",
                    "iss-00003",
                    "--title",
                    "Duplicate ID",
                    "--github-issue",
                    "4",
                ],
            )
            assert p.returncode == 2, p.stdout + p.stderr
            assert "unrecognized arguments: --id iss-00003" in p.stderr

    def test_new_rejects_duplicate_id_width_agnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            p = self._run_runtime_capture(
                target,
                [
                    "new",
                    "issue",
                    "--epic",
                    "2",
                    "--github-issue",
                    "3",
                    "--title",
                    "Duplicate by numeric id",
                ],
            )
            assert p.returncode != 0, p.stdout + p.stderr
            assert "github.issue_number=3" in p.stderr
            assert "issue:iss-00003" in p.stderr

    def test_new_rejects_duplicate_github_issue_link_with_conflict_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)

            self._run_runtime(target, ["new", "initiative", "--title", "Linked initiative", "--github-issue", "1"])
            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "2"])
            self._run_runtime(target, ["new", "epic", "--initiative", "2", "--title", "JWT auth", "--github-issue", "3"])

            p = self._run_runtime_capture(
                target,
                ["new", "issue", "--epic", "3", "--title", "Add refresh token", "--github-issue", "1"],
            )
            assert p.returncode != 0, p.stdout + p.stderr
            assert "github.issue_number=1" in p.stderr
            assert "initiative:init-00001" in p.stderr
            assert "spec-dock/initiatives/init-00001-linked-initiative/.meta.json" in p.stderr
            assert "different GitHub issue number" in p.stderr
            assert "--github-issue" not in p.stderr

            created = list((target / "spec-dock" / "initiatives").rglob("iss-00001-*"))
            assert created == []

    def test_new_issue_persists_current_repo_scope_when_origin_is_resolved(self) -> None:
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"])
            self._run_runtime(target, ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"])
            self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Current issue", "--github-issue", "123"])

            issue_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-current-issue"
                / ".meta.json"
            )
            issue_meta = json.loads(issue_meta_path.read_text(encoding="utf-8"))
            assert issue_meta["github"]["issue_number"] == 123
            assert issue_meta["github"]["repo_owner"] == "current"
            assert issue_meta["github"]["repo_name"] == "repo"

    def test_new_rejects_unsafe_slug(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            # User-provided --slug must be safe for filesystem paths.
            self._run_runtime_expect_fail(
                target,
                [
                    "new",
                    "issue",
                    "--epic",
                    "2",
                    "--title",
                    "Custom slug test",
                    "--slug",
                    "bad slug!!",
                    "--github-issue",
                    "4",
                ],
            )

    def test_new_rejects_uppercase_slug(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._run_runtime_expect_fail(
                target,
                [
                    "new",
                    "initiative",
                    "--title",
                    "Auth platform",
                    "--slug",
                    "Bad-Slug",
                ],
            )

    def test_new_derives_kebab_slug_from_title(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)

            self._run_runtime(
                target,
                ["new", "initiative", "--title", "Add Refresh Token", "--github-issue", "1"],
            )
            init_dir = target / "spec-dock" / "initiatives" / "init-00001-add-refresh-token"
            assert init_dir.is_dir()
            meta = json.loads((init_dir / ".meta.json").read_text(encoding="utf-8"))
            assert meta["slug"] == "add-refresh-token"

    def test_new_rejects_invalid_slug_before_gh_issue_create(self) -> None:
        pytest.skip(
            "S06 replacement: tests.unit.commands.test_runtime_new_s08 covers pre-GitHub input validation."
        )
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                f'echo "$@" >> "{log_path.as_posix()}"\n'
                'if [[ "$1" == "issue" && "$2" == "create" ]]; then\n'
                '  echo "https://github.com/example/repo/issues/999"\n'
                "  exit 0\n"
                "fi\n"
                "exit 0\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            p = self._run_runtime_capture(
                target,
                [
                    "new",
                    "initiative",
                    "--create-github-issue",
                    "--title",
                    "Add Refresh Token",
                    "--slug",
                    "Bad!Slug",
                ],
                env=test_env,
            )
            assert p.returncode != 0, p.stdout + p.stderr
            assert "--slug" in p.stderr
            assert "expected regex" in p.stderr

            if log_path.exists():
                assert log_path.read_text(encoding="utf-8").strip() == ""
            assert list((target / "spec-dock" / "initiatives").glob("*")) == []

    def test_new_missing_rules_source_fails_before_gh_issue_create(self) -> None:
        pytest.skip(
            "S06 replacement: tests.unit.commands.test_runtime_new_s08 covers missing-rules preflight before GitHub create."
        )
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)

            (target / "spec-dock" / "docs" / "rules" / "initiative" / "epics.md").unlink()

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                f'echo "$@" >> "{log_path.as_posix()}"\n'
                'if [[ "$1" == "issue" && "$2" == "create" ]]; then\n'
                '  echo "https://github.com/example/repo/issues/999"\n'
                "  exit 0\n"
                "fi\n"
                "exit 0\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            p = self._run_runtime_capture(
                target,
                [
                    "new",
                    "initiative",
                    "--create-github-issue",
                    "--title",
                    "Add Refresh Token",
                ],
                env=test_env,
            )
            assert p.returncode != 0, p.stdout + p.stderr
            assert "Missing rules source" in p.stderr
            assert "epics.md" in p.stderr

            if log_path.exists():
                assert log_path.read_text(encoding="utf-8").strip() == ""
            assert list((target / "spec-dock" / "initiatives").glob("*")) == []

    def test_new_nodes_create_rules_symlinks_without_wrappers(self) -> None:
        pytest.skip(
            "S06 replacement: tests.unit.commands.test_runtime_new_s08 covers create-plan rules symlink materialization."
        )
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            init_dir = target / "spec-dock" / "initiatives" / "init-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-00002-jwt-auth"
            issue_dir = epic_dir / "issues" / "iss-00003-add-refresh-token"
            expected_rules_links = {
                init_dir / "epics" / "rules.md": target / "spec-dock" / "docs" / "rules" / "initiative" / "epics.md",
                init_dir / "discussions" / "rules.md": (
                    target / "spec-dock" / "docs" / "rules" / "initiative" / "discussions.md"
                ),
                epic_dir / "issues" / "rules.md": target / "spec-dock" / "docs" / "rules" / "epic" / "issues.md",
                epic_dir / "discussions" / "rules.md": target / "spec-dock" / "docs" / "rules" / "epic" / "discussions.md",
                issue_dir / "discussions" / "rules.md": target / "spec-dock" / "docs" / "rules" / "issue" / "discussions.md",
            }
            for link_path, target_path in expected_rules_links.items():
                assert link_path.is_symlink(), f"missing rules symlink: {link_path}"
                assert link_path.resolve() == target_path.resolve()
                assert str(link_path.readlink()) == os.path.relpath(target_path, start=link_path.parent)

            assert not (init_dir / "epics" / "new-epic").exists()
            assert not (epic_dir / "issues" / "new-issue").exists()

            for scope_dir in (init_dir, epic_dir, issue_dir):
                assert not (scope_dir / "adrs").exists()
                assert not (scope_dir / "artifacts").exists()
                assert list((scope_dir / "discussions").glob("new-*")) == []

    def test_new_doc_adr_increments_id_within_scope_discussions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            p_one = self._run_runtime_capture(
                target,
                ["new", "doc", "adr", "--issue", "iss-00003", "--title", "Decision one"],
            )
            p_two = self._run_runtime_capture(
                target,
                ["new", "doc", "adr", "--issue", "iss-00003", "--title", "Decision two"],
            )
            assert p_one.returncode == 0, p_one.stdout + p_one.stderr
            assert p_two.returncode == 0, p_two.stdout + p_two.stderr

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
            )
            discussions_dir = issue_dir / "discussions"
            created_one = sorted(discussions_dir.glob("*-adr-decision-one.md"))
            created_two = sorted(discussions_dir.glob("*-adr-decision-two.md"))
            assert len(created_one) == 1
            assert len(created_two) == 1
            assert re.search(r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-adr-decision-one\.md$", created_one[0].name)
            assert re.search(r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-adr-decision-two\.md$", created_two[0].name)
            assert re.search(r"id=[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-adr\b", p_one.stdout)
            assert re.search(r"id=[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-adr\b", p_two.stdout)
            assert list(issue_dir.glob("adrs")) == []

    def test_new_doc_scope_shorthand_resolves_local_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            p_init = self._run_runtime_capture(
                target,
                ["new", "doc", "scratch", "--initiative", "1", "--title", "Initiative note"],
            )
            p_epic = self._run_runtime_capture(
                target,
                ["new", "doc", "scratch", "--epic", "2", "--title", "Epic note"],
            )
            p_issue = self._run_runtime_capture(
                target,
                ["new", "doc", "scratch", "--issue", "3", "--title", "Issue note"],
            )
            assert p_init.returncode == 0, p_init.stdout + p_init.stderr
            assert p_epic.returncode == 0, p_epic.stdout + p_epic.stderr
            assert p_issue.returncode == 0, p_issue.stdout + p_issue.stderr
            assert "scope=init-00001" in p_init.stdout
            assert "scope=epic-00002" in p_epic.stdout
            assert "scope=iss-00003" in p_issue.stdout

            init_dir = target / "spec-dock" / "initiatives" / "init-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-00002-jwt-auth"
            issue_dir = epic_dir / "issues" / "iss-00003-add-refresh-token"
            assert len(sorted((init_dir / "discussions").glob("*-scratch-initiative-note.md"))) == 1
            assert len(sorted((epic_dir / "discussions").glob("*-scratch-epic-note.md"))) == 1
            assert len(sorted((issue_dir / "discussions").glob("*-scratch-issue-note.md"))) == 1

    def test_new_doc_uses_timestamp_family_across_discussion_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            self._run_runtime(target, ["new", "doc", "disc", "--issue", "iss-00003", "--title", "Discussion one"])
            self._run_runtime(target, ["new", "doc", "adr", "--issue", "iss-00003", "--title", "Decision one"])
            self._run_runtime(target, ["new", "doc", "research", "--issue", "iss-00003", "--title", "Research one"])
            self._run_runtime(target, ["new", "doc", "interview", "--issue", "iss-00003", "--title", "Interview one"])
            self._run_runtime(target, ["new", "doc", "scratch", "--issue", "iss-00003", "--title", "Scratch one"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
            )
            discussions_dir = issue_dir / "discussions"
            assert len(sorted(discussions_dir.glob("*-disc-discussion-one.md"))) == 1
            assert len(sorted(discussions_dir.glob("*-adr-decision-one.md"))) == 1
            assert len(sorted(discussions_dir.glob("*-research-research-one.md"))) == 1
            assert len(sorted(discussions_dir.glob("*-interview-interview-one.md"))) == 1
            assert len(sorted(discussions_dir.glob("*-scratch-scratch-one.md"))) == 1

    def test_new_doc_creates_draft_artifacts_from_scope_specific_templates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            cases = (
                (
                    ["new", "doc", "draft-requirement", "--initiative", "init-00001", "--title", "Requirement Draft"],
                    target / "spec-dock" / "initiatives" / "init-00001-auth-platform" / "discussions",
                    "draft-requirement",
                    "templates/initiative/requirement.md",
                    "requirement.md",
                    "要件定義（何を、なぜ行うか）",
                ),
                (
                    ["new", "doc", "draft-design", "--issue", "iss-00003", "--title", "Design Draft"],
                    target
                    / "spec-dock"
                    / "initiatives"
                    / "init-00001-auth-platform"
                    / "epics"
                    / "epic-00002-jwt-auth"
                    / "issues"
                    / "iss-00003-add-refresh-token"
                    / "discussions",
                    "draft-design",
                    "templates/issue/design.md",
                    "design.md",
                    "設計（どう実現するか）",
                ),
                (
                    ["new", "doc", "draft-plan", "--epic", "epic-00002", "--title", "Plan Draft"],
                    target
                    / "spec-dock"
                    / "initiatives"
                    / "init-00001-auth-platform"
                    / "epics"
                    / "epic-00002-jwt-auth"
                    / "discussions",
                    "draft-plan",
                    "templates/epic/plan.md",
                    "plan.md",
                    "計画（Issue と実施順序）",
                ),
            )

            for command, discussions_dir, doc_type, template_source, _intended_target, body_heading in cases:
                p = self._run_runtime_capture(target, command)
                assert p.returncode == 0, p.stdout + p.stderr
                assert f"type={doc_type}" in p.stdout
                created = sorted(discussions_dir.glob(f"*-{doc_type}-*.md"))
                assert len(created) == 1
                assert re.search(rf"^[0-9]{{8}}t[0-9]{{6}}z(?:-[0-9]{{2}})?-{doc_type}-[a-z0-9-]+\.md$", created[0].name)
                content = created[0].read_text(encoding="utf-8")
                frontmatter = content.split("---", 2)[1]
                assert "状態: \"draft | approved\"" in frontmatter
                assert "adoption_status" not in frontmatter
                assert "template_source" not in frontmatter
                assert "created_by_role" not in frontmatter
                assert "Canonical `" not in content
                assert "remains main-orchestrator-only" not in content
                canonical_source = target / "spec-dock" / template_source
                assert canonical_source.is_file(), f"missing source template: {canonical_source}"
                canonical_text = canonical_source.read_text(encoding="utf-8")
                assert canonical_text.splitlines()[1] in content
                assert body_heading in content

    def test_new_doc_note_is_retired_with_scratch_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            p = self._run_runtime_capture(
                target,
                ["new", "doc", "note", "--issue", "iss-00003", "--title", "Note one"],
            )

            assert p.returncode != 0, p.stdout + p.stderr
            assert "note" in p.stderr
            assert "retired" in p.stderr
            assert "scratch" in p.stderr
            assert "invalid choice" not in p.stderr

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
            )
            assert list((issue_dir / "discussions").glob("*-note-note-one.md")) == []

    def test_new_doc_stdout_uses_slugless_id_and_discussions_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            p = self._run_runtime_capture(
                target,
                ["new", "doc", "disc", "--issue", "iss-00003", "--title", "Discussion one"],
            )
            assert p.returncode == 0, p.stdout + p.stderr

            assert re.search((
                    r"spec-dock: ok \(new doc\) type=disc "
                    r"id=[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-disc "
                    r"scope=iss-00003 "
                    r"path=spec-dock/.*/discussions/[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-disc-discussion-one\.md"
                ), p.stdout)
            assert "discussion-one" not in re.search(r"id=([^\s]+)", p.stdout).group(1)

    def test_new_doc_creates_pr_repair_batch_with_generated_identity_and_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            self._write_runtime_clock(
                target,
                now_iso="2026-03-12T01:02:03+00:00",
                today="2026-03-12",
            )

            p = self._run_runtime_capture(
                target,
                ["new", "doc", "pr-repair-batch", "--issue", "iss-00003", "--title", "PR Repair Batch"],
            )

            assert p.returncode == 0, p.stdout + p.stderr
            assert re.search(
                (
                    r"spec-dock: ok \(new doc\) type=pr-repair-batch "
                    r"id=20260312t010203z-pr-repair-batch "
                    r"scope=iss-00003 "
                    r"path=spec-dock/.*/discussions/"
                    r"20260312t010203z-pr-repair-batch-pr-repair-batch\.md"
                ),
                p.stdout,
            )

            created = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / "discussions"
                / "20260312t010203z-pr-repair-batch-pr-repair-batch.md"
            )
            assert created.is_file()
            content = created.read_text(encoding="utf-8")
            assert '種別: pr-repair-batch' in content
            assert 'ID: "20260312t010203z-pr-repair-batch"' in content
            assert 'タイトル: "PR Repair Batch"' in content
            assert '親: ["iss-00003"]' in content
            assert "# 20260312t010203z-pr-repair-batch PR Repair Batch" in content
            assert "observed GitHub Actions CI failures" in content
            assert "`check_failure:<actions_job_or_workflow_name>`" in content
            assert "External/non-Actions check state" in content
            assert "triage review findings, CI failures" not in content
            assert "`check_failure:<job_or_check_name>`" not in content
            assert "No required check failure remains." not in content

    def test_new_doc_renders_body_date_from_same_utc_instant_as_doc_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            self._write_runtime_clock(
                target,
                now_iso="2026-03-12T00:30:00+00:00",
                today="2026-03-11",
            )

            self._run_runtime(target, ["new", "doc", "scratch", "--issue", "iss-00003", "--title", "UTC date check"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
            )
            created = issue_dir / "discussions" / "20260312t003000z-scratch-utc-date-check.md"
            assert created.is_file()
            assert "2026-03-12" in created.read_text(encoding="utf-8")
            assert "2026-03-11" not in created.read_text(encoding="utf-8")

    def test_new_doc_ignores_unrelated_files_for_timestamp_allocation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
            )
            discussions_dir = issue_dir / "discussions"
            (discussions_dir / "foo.md").write_text("nonconforming\n", encoding="utf-8")
            (discussions_dir / "009-disc-migrated.md").write_text("existing new format\n", encoding="utf-8")
            (discussions_dir / "1000-adr-legacy-overflow.md").write_text("4-digit should be ignored\n", encoding="utf-8")

            self._run_runtime(target, ["new", "doc", "adr", "--issue", "iss-00003", "--title", "Decision one"])

            assert len(sorted(discussions_dir.glob("*-adr-decision-one.md"))) == 1
            assert list(discussions_dir.glob("001-adr-*.md")) == []

    def test_new_doc_rejects_malformed_discussion_doc_candidates(self) -> None:
        cases = (
            "002-bogus-random.md",
            "foo-adr-kickoff.md",
            "bogus-01-adr-kickoff.md",
        )
        for malformed_name in cases:
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp)
                assert main(["init", str(target)]) == 0
                self._create_same_repo_linked_hierarchy(target)

                issue_dir = (
                    target
                    / "spec-dock"
                    / "initiatives"
                    / "init-00001-auth-platform"
                    / "epics"
                    / "epic-00002-jwt-auth"
                    / "issues"
                    / "iss-00003-add-refresh-token"
                )
                discussions_dir = issue_dir / "discussions"
                (discussions_dir / malformed_name).write_text("nonconforming type\n", encoding="utf-8")

                p = self._run_runtime_capture(
                    target,
                    ["new", "doc", "adr", "--issue", "iss-00003", "--title", "Decision one"],
                )

                assert p.returncode != 0, p.stdout + p.stderr
                assert "Malformed discussion document filename" in p.stderr
                assert malformed_name in p.stderr
                assert len(sorted(discussions_dir.glob("*-adr-decision-one.md"))) == 0

    def test_new_doc_rejects_timestamp_shaped_malformed_discussion_doc_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
            )
            discussions_dir = issue_dir / "discussions"
            malformed_name = "20260312t010203z-00-disc-malformed.md"
            (discussions_dir / malformed_name).write_text("nonconforming type\n", encoding="utf-8")

            p = self._run_runtime_capture(
                target,
                ["new", "doc", "adr", "--issue", "iss-00003", "--title", "Decision one"],
            )

            assert p.returncode != 0, p.stdout + p.stderr
            assert "Malformed discussion document filename" in p.stderr
            assert malformed_name in p.stderr
            assert len(sorted(discussions_dir.glob("*-adr-decision-one.md"))) == 0

    def test_new_doc_preserves_legacy_files_without_reusing_sequence_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
            )
            discussions_dir = issue_dir / "discussions"
            (discussions_dir / "001-adr-first.md").write_text("first\n", encoding="utf-8")
            (discussions_dir / "001-disc-second.md").write_text("second\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["new", "doc", "scratch", "--issue", "iss-00003", "--title", "Note one"])
            assert p.returncode == 0, p.stdout + p.stderr
            assert re.search(r"id=[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-scratch\b", p.stdout)
            assert len(sorted(discussions_dir.glob("*-scratch-note-one.md"))) == 1

    def test_new_doc_rejects_invalid_slug(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            p = self._run_runtime_capture(
                target,
                [
                    "new",
                    "doc",
                    "adr",
                    "--issue",
                    "iss-00003",
                    "--title",
                    "Decision one",
                    "--slug",
                    "Bad!Slug",
                ],
            )
            assert p.returncode != 0, p.stdout + p.stderr
            assert "--slug" in p.stderr
            assert "expected regex" in p.stderr

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
            )
            discussions_dir = issue_dir / "discussions"
            assert list(discussions_dir.glob("001-adr-*.md")) == []

    def test_new_doc_rejects_unexpected_sequence_override_option(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(
                target,
                [
                    "new",
                    "doc",
                    "adr",
                    "--issue",
                    "iss-00003",
                    "--seq",
                    "1",
                    "--title",
                    "Decision one",
                ],
            )
            assert p.returncode == 2, p.stdout + p.stderr
            assert "unrecognized arguments: --seq 1" in p.stderr

    def test_new_discussion_per_type_commands_are_not_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            for per_type in ("adr", "disc", "research", "interview", "scratch", "note"):
                p = self._run_runtime_capture(
                    target,
                    ["new", per_type, "--issue", "iss-00003", "--title", "Doc title"],
                )
                assert p.returncode == 2, p.stdout + p.stderr
                assert f"invalid choice: '{per_type}'" in p.stderr

    def test_new_help_exposes_only_doc_discussion_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p_new = self._run_runtime_capture(target, ["new", "--help"])
            assert p_new.returncode == 0, p_new.stdout + p_new.stderr
            assert " doc " in p_new.stdout
            assert "\n    adr" not in p_new.stdout
            assert "\n    disc" not in p_new.stdout
            assert "\n    research" not in p_new.stdout
            assert "\n    interview" not in p_new.stdout
            assert "\n    scratch" not in p_new.stdout
            assert "\n    note" not in p_new.stdout

            p_doc = self._run_runtime_capture(target, ["new", "doc", "--help"])
            assert p_doc.returncode == 0, p_doc.stdout + p_doc.stderr
            assert "adr" in p_doc.stdout
            assert "disc" in p_doc.stdout
            assert "research" in p_doc.stdout
            assert "interview" in p_doc.stdout
            assert "scratch" in p_doc.stdout
            assert "pr-repair-batch" in p_doc.stdout
            assert "note" in p_doc.stdout
            assert "--template-file" not in p_doc.stdout
            assert "--body-file" not in p_doc.stdout
            assert "--basename" not in p_doc.stdout
            assert "--doc-id" not in p_doc.stdout
            assert "--id" not in p_doc.stdout
            assert "--seq" not in p_doc.stdout

            for forbidden_option in ("--template-file", "--body-file", "--basename", "--doc-id", "--id"):
                p_forbidden = self._run_runtime_capture(
                    target,
                    [
                        "new",
                        "doc",
                        "pr-repair-batch",
                        "--issue",
                        "iss-00003",
                        "--title",
                        "PR Repair Batch",
                        forbidden_option,
                        "x",
                    ],
                )
                assert p_forbidden.returncode == 2, p_forbidden.stdout + p_forbidden.stderr
                assert "unrecognized arguments" in p_forbidden.stderr

    def test_new_node_help_does_not_expose_local_creation_options(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            for kind in ("initiative", "epic", "issue"):
                p = self._run_runtime_capture(target, ["new", kind, "--help"])
                assert p.returncode == 0, p.stdout + p.stderr
                assert "--create-github-issue" in p.stdout
                assert "--github-issue" in p.stdout
                assert "--no-github" not in p.stdout
                assert "--id" not in p.stdout

    def test_internal_issue_status_resolution_marks_cached_source(self) -> None:
        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2]
            / "src"
            / "spec_dock"
            / "assets"
            / "spec_dock"
            / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime import app as runtime_app
        finally:
            sys.path.pop(0)

        nodes = {
            "iss-00301": SimpleNamespace(
                id="iss-00301",
                type="issue",
                github_issue_number=301,
                epic_id="epic-00201",
                initiative_id="init-00101",
            )
        }
        resolved = runtime_app._resolve_issue_statuses(
            nodes,
            github=False,
            issue_index={},
            cached_issue_status_by_id={"iss-00301": "done"},
        )

        assert resolved["iss-00301"].status == "done"
        assert resolved["iss-00301"].source == "cache"

    def test_new_doc_rejects_unknown_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(
                target,
                ["new", "doc", "unknown", "--issue", "iss-00003", "--title", "Doc title"],
            )
            assert p.returncode == 1, p.stdout + p.stderr
            assert "Unknown discussion doc type: unknown" in p.stderr
            assert "invalid choice" not in p.stderr

    def test_new_nodes_do_not_generate_readme_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            init_dir = target / "spec-dock" / "initiatives" / "init-00001-auth-platform"
            readmes = list(init_dir.rglob("README.md"))
            assert readmes == []

    def test_new_no_github_is_parser_error_and_does_not_invoke_gh(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            # Provide a fake `gh` binary that always errors; --no-github must fail before invoking it.
            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                "echo \"gh should not be invoked in --no-github mode\" >&2\n"
                "exit 1\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            p = self._run_runtime_capture(
                target,
                ["new", "initiative", "--no-github", "--title", "Auth platform"],
                env=test_env,
            )
            assert p.returncode == 2, p.stdout + p.stderr
            assert "unrecognized arguments: --no-github" in p.stderr
            assert "'--no-github' is not supported" not in p.stderr
            assert "gh should not be invoked" not in p.stderr

    def test_new_no_github_is_parser_error_for_initiative_epic_and_issue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            cases = [
                ["new", "initiative", "--no-github", "--title", "Another initiative"],
                ["new", "epic", "--no-github", "--initiative", "1", "--title", "Another epic"],
                ["new", "issue", "--no-github", "--epic", "2", "--title", "Another issue"],
            ]
            for argv in cases:
                case_label = " ".join(argv)
                p = self._run_runtime_capture(target, argv)
                assert p.returncode == 2, f"{case_label}: {p.stdout}{p.stderr}"
                assert "unrecognized arguments: --no-github" in p.stderr, f"{case_label}: argv={argv!r}"
                assert "'--no-github' is not supported" not in p.stderr, f"{case_label}: argv={argv!r}"

    def test_new_rejects_invalid_title_before_gh_issue_create(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                f'echo "$@" >> "{log_path.as_posix()}"\n'
                'if [[ "$1" == "issue" && "$2" == "create" ]]; then\n'
                '  echo "https://github.com/example/repo/issues/999"\n'
                "  exit 0\n"
                "fi\n"
                "exit 0\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            p = self._run_runtime_capture(
                target,
                ["new", "initiative", "--create-github-issue", "--title", "日本語"],
                env=test_env,
            )
            assert p.returncode != 0, p.stdout + p.stderr
            assert "--title" in p.stderr
            assert "expected regex" in p.stderr

            if log_path.exists():
                assert log_path.read_text(encoding="utf-8").strip() == ""
            assert list((target / "spec-dock" / "initiatives").glob("*")) == []

    def test_new_initiative_and_epic_default_to_github_create_when_gh_is_available(self) -> None:
        pytest.skip(
            "S06 replacement: tests.unit.commands.test_runtime_new_s08 covers default GitHub create mode matrix."
        )
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)

            # Default for initiative/epic is GitHub create; `gh` must be invoked even without explicit flags.
            bin_dir = target / ".bin-gh"
            bin_dir.mkdir(parents=True, exist_ok=True)
            called_path = target / ".gh.called"
            count_path = target / ".gh.count"
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                f'echo "$@" >> "{called_path.as_posix()}"\n'
                'if [[ "$1" == "issue" && "$2" == "create" ]]; then\n'
                f'  count=$(cat "{count_path.as_posix()}" 2>/dev/null || echo 0)\n'
                '  count=$((count + 1))\n'
                f'  printf "%s" "$count" > "{count_path.as_posix()}"\n'
                '  if [[ "$count" == "1" ]]; then\n'
                '    echo "https://github.com/example/repo/issues/123"\n'
                "  else\n"
                '    echo "https://github.com/example/repo/issues/124"\n'
                "  fi\n"
                "  exit 0\n"
                "fi\n"
                'if [[ "$1" == "issue" && "$2" == "list" ]]; then\n'
                '  echo "[{\\"number\\":123,\\"state\\":\\"OPEN\\",\\"title\\":\\"Issue 123\\",\\"labels\\":[],\\"updatedAt\\":\\"2026-05-13T00:00:03Z\\",\\"url\\":\\"https://github.com/example/repo/issues/123\\"},{\\"number\\":124,\\"state\\":\\"OPEN\\",\\"title\\":\\"Issue 124\\",\\"labels\\":[],\\"updatedAt\\":\\"2026-05-13T00:00:04Z\\",\\"url\\":\\"https://github.com/example/repo/issues/124\\"}]"\n'
                "  exit 0\n"
                "fi\n"
                "echo \"unexpected gh args: $@\" >&2\n"
                "exit 1\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform"], env=test_env)
            self._run_runtime(target, ["new", "epic", "--initiative", "init-00123", "--title", "JWT auth"], env=test_env)

            init_dir = target / "spec-dock" / "initiatives" / "init-00123-auth-platform"
            epic_dir = init_dir / "epics" / "epic-00124-jwt-auth"
            assert init_dir.is_dir()
            assert epic_dir.is_dir()
            assert called_path.exists(), "gh was not invoked"

            init_meta = json.loads((init_dir / ".meta.json").read_text(encoding="utf-8"))
            epic_meta = json.loads((epic_dir / ".meta.json").read_text(encoding="utf-8"))
            assert init_meta["id"] == "init-00123"
            assert epic_meta["id"] == "epic-00124"
            assert init_meta["github"]["issue_number"] == 123
            assert epic_meta["github"]["issue_number"] == 124
            assert init_meta["github"]["repo_owner"] == "example"
            assert init_meta["github"]["repo_name"] == "repo"
            assert epic_meta["github"]["repo_owner"] == "example"
            assert epic_meta["github"]["repo_name"] == "repo"
            self._assert_spec_dock_meta_marker(init_meta)
            self._assert_spec_dock_meta_marker(epic_meta)
            self._assert_readonly_on_posix(init_dir / ".meta.json")
            self._assert_readonly_on_posix(epic_dir / ".meta.json")

    def test_new_initiative_warns_and_continues_when_readonly_lock_fails(self) -> None:
        pytest.skip(
            "S06 replacement: tests.unit.commands.test_runtime_new_s08 covers create-lock failure guidance."
        )
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                'if [[ \"$1\" == \"issue\" && \"$2\" == \"create\" ]]; then\n'
                "  echo \"https://github.com/example/repo/issues/123\"\n"
                "  exit 0\n"
                "fi\n"
                'if [[ \"$1\" == \"issue\" && \"$2\" == \"list\" ]]; then\n'
                '  echo "[{\\"number\\":123,\\"state\\":\\"OPEN\\",\\"title\\":\\"Issue 123\\",\\"labels\\":[],\\"updatedAt\\":\\"2026-05-13T00:00:03Z\\",\\"url\\":\\"https://github.com/example/repo/issues/123\\"}]"\n'
                "  exit 0\n"
                "fi\n"
                "echo \"unexpected gh args: $@\" >&2\n"
                "exit 1\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            runtime_fs_repo = (
                target / "spec-dock" / "scripts" / "spec_dock_runtime" / "infra" / "fs_repo.py"
            )
            assert runtime_fs_repo.is_file()
            runtime_fs_repo.write_text(
                runtime_fs_repo.read_text(encoding="utf-8")
                + "\n\n"
                + "def _try_make_readonly(path):\n"
                + '    return False, "simulated"\n',
                encoding="utf-8",
            )

            p = self._run_runtime_capture(
                target,
                ["new", "initiative", "--title", "Auth platform"],
                env={"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"},
            )
            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: (warn)" in p.stderr

            init_dir = target / "spec-dock" / "initiatives" / "init-00123-auth-platform"
            assert (init_dir / ".meta.json").is_file()

    def test_new_github_flags_are_mutually_exclusive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p1 = self._run_runtime_capture(
                target,
                [
                    "new",
                    "initiative",
                    "--title",
                    "Auth platform 2",
                    "--create-github-issue",
                    "--github-issue",
                    "123",
                ],
            )
            assert p1.returncode == 2, p1.stdout + p1.stderr
            assert "not allowed with argument" in p1.stderr

            p2 = self._run_runtime_capture(
                target,
                [
                    "new",
                    "epic",
                    "--initiative",
                    "1",
                    "--title",
                    "JWT auth",
                    "--create-github-issue",
                    "--no-github",
                ],
            )
            assert p2.returncode == 2, p2.stdout + p2.stderr
            assert "unrecognized arguments: --no-github" in p2.stderr
            assert "not allowed with argument" not in p2.stderr

            p3 = self._run_runtime_capture(
                target,
                [
                    "new",
                    "initiative",
                    "--title",
                    "Auth platform 3",
                    "--github-issue",
                    "123",
                    "--no-github",
                ],
            )
            assert p3.returncode == 2, p3.stdout + p3.stderr
            assert "unrecognized arguments: --no-github" in p3.stderr
            assert "not allowed with argument" not in p3.stderr

            p4 = self._run_runtime_capture(
                target,
                [
                    "new",
                    "epic",
                    "--initiative",
                    "1",
                    "--title",
                    "JWT auth 2",
                    "--github-issue",
                    "123",
                    "--no-github",
                ],
            )
            assert p4.returncode == 2, p4.stdout + p4.stderr
            assert "unrecognized arguments: --no-github" in p4.stderr
            assert "not allowed with argument" not in p4.stderr

            p5 = self._run_runtime_capture(
                target,
                [
                    "new",
                    "issue",
                    "--epic",
                    "1",
                    "--title",
                    "Issue 1",
                    "--create-github-issue",
                    "--github-issue",
                    "123",
                ],
            )
            assert p5.returncode == 2, p5.stdout + p5.stderr
            assert "not allowed with argument" in p5.stderr

            p6 = self._run_runtime_capture(
                target,
                [
                    "new",
                    "issue",
                    "--epic",
                    "1",
                    "--title",
                    "Issue 2",
                    "--create-github-issue",
                    "--no-github",
                ],
            )
            assert p6.returncode == 2, p6.stdout + p6.stderr
            assert "unrecognized arguments: --no-github" in p6.stderr
            assert "not allowed with argument" not in p6.stderr

    def test_new_issue_create_github_issue_flag_alias_is_accepted(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"])
            self._run_runtime(target, ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                'if [[ \"$1\" == \"issue\" && \"$2\" == \"create\" ]]; then\n'
                "  echo \"https://github.com/example/repo/issues/123\"\n"
                "  exit 0\n"
                "fi\n"
                'if [[ \"$1\" == \"issue\" && \"$2\" == \"list\" ]]; then\n'
                '  echo "[{\\"number\\":1,\\"state\\":\\"OPEN\\",\\"title\\":\\"Issue 1\\",\\"labels\\":[],\\"updatedAt\\":\\"2026-05-13T00:00:01Z\\",\\"url\\":\\"https://github.com/example/repo/issues/1\\"},{\\"number\\":2,\\"state\\":\\"OPEN\\",\\"title\\":\\"Issue 2\\",\\"labels\\":[],\\"updatedAt\\":\\"2026-05-13T00:00:02Z\\",\\"url\\":\\"https://github.com/example/repo/issues/2\\"},{\\"number\\":123,\\"state\\":\\"OPEN\\",\\"title\\":\\"Issue 123\\",\\"labels\\":[],\\"updatedAt\\":\\"2026-05-13T00:00:03Z\\",\\"url\\":\\"https://github.com/example/repo/issues/123\\"}]"\n'
                "  exit 0\n"
                "fi\n"
                "echo \"unexpected gh args: $@\" >&2\n"
                "exit 1\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "2", "--title", "Add refresh token", "--create-github-issue"],
                env=test_env,
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-add-refresh-token"
            )
            assert issue_dir.is_dir()

    def test_new_issue_can_create_github_issue_and_use_its_number(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"])
            self._run_runtime(target, ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"])

            # Provide a fake `gh` binary so the test doesn't require network/auth.
            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                'if [[ \"$1\" == \"issue\" && \"$2\" == \"create\" ]]; then\n'
                "  echo \"https://github.com/example/repo/issues/123\"\n"
                "  exit 0\n"
                "fi\n"
                'if [[ \"$1\" == \"issue\" && \"$2\" == \"list\" ]]; then\n'
                '  echo "[{\\"number\\":1,\\"state\\":\\"OPEN\\",\\"title\\":\\"Issue 1\\",\\"labels\\":[],\\"updatedAt\\":\\"2026-05-13T00:00:01Z\\",\\"url\\":\\"https://github.com/example/repo/issues/1\\"},{\\"number\\":2,\\"state\\":\\"OPEN\\",\\"title\\":\\"Issue 2\\",\\"labels\\":[],\\"updatedAt\\":\\"2026-05-13T00:00:02Z\\",\\"url\\":\\"https://github.com/example/repo/issues/2\\"},{\\"number\\":123,\\"state\\":\\"OPEN\\",\\"title\\":\\"Issue 123\\",\\"labels\\":[],\\"updatedAt\\":\\"2026-05-13T00:00:03Z\\",\\"url\\":\\"https://github.com/example/repo/issues/123\\"}]"\n'
                "  exit 0\n"
                "fi\n"
                "echo \"unexpected gh args: $@\" >&2\n"
                "exit 1\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "2", "--title", "Add refresh token"],
                env=test_env,
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-add-refresh-token"
            )
            assert issue_dir.is_dir()
            meta = json.loads((issue_dir / ".meta.json").read_text(encoding="utf-8"))
            assert meta["id"] == "iss-00123"
            assert meta["github"]["issue_number"] == 123
            self._assert_spec_dock_meta_marker(meta)
            self._assert_readonly_on_posix(issue_dir / ".meta.json")

    def test_new_fails_preflight_on_legacy_meta_without_creating_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--title", "Parent initiative", "--github-issue", "1"])
            self._run_runtime(target, ["new", "epic", "--initiative", "1", "--title", "Parent epic", "--github-issue", "2"])
            self._run_runtime(target, ["new", "initiative", "--title", "Legacy holder", "--github-issue", "3"])

            initiatives_root = target / "spec-dock" / "initiatives"
            parent_init_dir = initiatives_root / "init-00001-parent-initiative"
            parent_epic_dir = parent_init_dir / "epics" / "epic-00002-parent-epic"
            legacy_init_dir = initiatives_root / "init-00003-legacy-holder"
            dot_meta_path = legacy_init_dir / ".meta.json"
            legacy_meta_path = legacy_init_dir / "meta.json"
            dot_meta_path.rename(legacy_meta_path)
            assert not dot_meta_path.exists()
            assert legacy_meta_path.is_file()

            before_inits = sorted(p.name for p in initiatives_root.glob("init-*"))
            before_epics = sorted(p.name for p in (parent_init_dir / "epics").glob("epic-*"))
            before_issues = sorted(p.name for p in (parent_epic_dir / "issues").glob("iss-*"))

            p_init = self._run_runtime_capture(
                target,
                ["new", "initiative", "--title", "Should fail initiative", "--github-issue", "4"],
            )
            assert p_init.returncode != 0, p_init.stdout + p_init.stderr
            assert "Unsupported legacy meta.json detected" in p_init.stderr
            assert str(legacy_meta_path) in p_init.stderr

            p_epic = self._run_runtime_capture(
                target,
                ["new", "epic", "--initiative", "1", "--title", "Should fail epic", "--github-issue", "5"],
            )
            assert p_epic.returncode != 0, p_epic.stdout + p_epic.stderr
            assert "Unsupported legacy meta.json detected" in p_epic.stderr
            assert str(legacy_meta_path) in p_epic.stderr

            p_issue = self._run_runtime_capture(
                target,
                ["new", "issue", "--epic", "2", "--title", "Should fail issue", "--github-issue", "6"],
            )
            assert p_issue.returncode != 0, p_issue.stdout + p_issue.stderr
            assert "Unsupported legacy meta.json detected" in p_issue.stderr
            assert str(legacy_meta_path) in p_issue.stderr

            assert before_inits == sorted(p.name for p in initiatives_root.glob("init-*"))
            assert before_epics == sorted(p.name for p in (parent_init_dir / "epics").glob("epic-*"))
            assert before_issues == sorted(p.name for p in (parent_epic_dir / "issues").glob("iss-*"))
