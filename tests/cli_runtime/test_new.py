import json
import os
from pathlib import Path
import re
import shutil
import subprocess
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

    def _find_issue_dir_by_id(self, target: Path, issue_id: str) -> Path:
        for meta_path in sorted((target / "spec-dock" / "initiatives").glob("**/.meta.json")):
            payload = json.loads(meta_path.read_text(encoding="utf-8"))
            if payload.get("type") == "issue" and payload.get("id") == issue_id:
                return meta_path.parent
        raise AssertionError(f"issue not found: {issue_id}")

    def _artifact_tree_snapshot(self, issue_dir: Path) -> tuple[tuple[str, str, str], ...] | None:
        artifacts_dir = issue_dir / "artifacts"
        if not artifacts_dir.exists():
            return None
        snapshot: list[tuple[str, str, str]] = []
        for path in sorted(artifacts_dir.rglob("*"), key=lambda item: item.as_posix()):
            rel = path.relative_to(artifacts_dir).as_posix()
            if path.is_symlink():
                snapshot.append((rel, "symlink", str(path.readlink())))
            elif path.is_dir():
                snapshot.append((rel, "dir", ""))
            else:
                snapshot.append((rel, "file", path.read_text(encoding="utf-8")))
        return tuple(snapshot)

    def test_new_issue_creates_thin_design_and_plan_templates_without_assurance_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            init_dir = target / "spec-dock" / "initiatives" / "init-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-00002-jwt-auth"
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

            expected_documents = {"requirement.md", "design.md", "plan.md", "report.md"}
            for node_dir in (init_dir, epic_dir, issue_dir):
                assert {path.name for path in node_dir.glob("*.md")} == expected_documents
                assert not (node_dir / ".assurance.json").exists()

            validation = self._run_runtime_capture(target, ["validate"])
            assert validation.returncode == 0, validation.stdout + validation.stderr
            expected_headings = {
                "design.md": (
                    "設計目標",
                    "Current / Target",
                    "責務・Interface",
                    "data / failure",
                    "変更対象",
                    "移行・互換性・rollback",
                    "testability",
                    "risk",
                ),
                "plan.md": (
                    "Planning Level",
                    "目標",
                    "順序・依存",
                    "実装step",
                    "検証",
                    "rollback",
                    "exit / handoff",
                ),
            }
            expected_kinds = {
                "design.md": "設計書（Issue）",
                "plan.md": "実装計画書（Issue）",
            }
            for filename in ("design.md", "plan.md"):
                text = (issue_dir / filename).read_text(encoding="utf-8")
                assert f"種別: {expected_kinds[filename]}" in text
                assert '状態: "draft"' in text
                assert "artifact_state:" not in text
                assert "assurance classify" not in text
                assert "assurance compose" not in text
                for heading in expected_headings[filename]:
                    assert f"## {heading}" in text
                assert "spec-dock:managed-section begin" not in text

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
                assert before_artifacts == self._read_create_auto_sync_artifacts(target), f"{case_label}: argv={argv!r}"
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
            self._run_runtime(
                target, ["new", "epic", "--initiative", "2", "--title", "JWT auth", "--github-issue", "3"]
            )

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
            self._run_runtime(
                target, ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"]
            )
            self._run_runtime(
                target, ["new", "issue", "--epic", "2", "--title", "Current issue", "--github-issue", "123"]
            )

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
        pytest.skip("S06 replacement: tests.unit.commands.test_runtime_new_s08 covers pre-GitHub input validation.")
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
                epic_dir / "discussions" / "rules.md": target
                / "spec-dock"
                / "docs"
                / "rules"
                / "epic"
                / "discussions.md",
                issue_dir / "discussions" / "rules.md": target
                / "spec-dock"
                / "docs"
                / "rules"
                / "issue"
                / "discussions.md",
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

    def test_new_artifact_blank_issue_omits_blank_token_and_uses_artifacts_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            self._write_runtime_clock(target, now_iso="2026-03-12T01:02:03+00:00", today="2026-03-11")

            p = self._run_runtime_capture(
                target,
                ["new", "artifact", "--issue", "iss-00003", "--title", "Working Notes"],
            )

            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok (new artifact) type=blank id=20260312t010203z scope=iss-00003" in p.stdout
            issue_dir = self._find_issue_dir_by_id(target, "iss-00003")
            created = issue_dir / "artifacts" / "20260312t010203z-working-notes.md"
            assert created.is_file()
            assert "blank" not in created.name
            content = created.read_text(encoding="utf-8")
            assert 'ID: "20260312t010203z"' in content
            assert "2026-03-12" in content
            assert "2026-03-11" not in content

    def test_new_artifact_typed_epic_success_and_scope_shorthand(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            self._write_runtime_clock(target, now_iso="2026-03-12T01:02:03+00:00", today="2026-03-12")

            p = self._run_runtime_capture(
                target,
                ["new", "artifact", "research", "--epic", "2", "--title", "Research One"],
            )

            assert p.returncode == 0, p.stdout + p.stderr
            assert "type=research id=20260312t010203z-research scope=epic-00002" in p.stdout
            epic_dir = (
                target / "spec-dock" / "initiatives" / "init-00001-auth-platform" / "epics" / "epic-00002-jwt-auth"
            )
            created = epic_dir / "artifacts" / "20260312t010203z-research-research-one.md"
            assert created.is_file()
            assert 'ID: "20260312t010203z-research"' in created.read_text(encoding="utf-8")

    def test_new_artifact_full_direct_catalog_success(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            self._write_runtime_clock(target, now_iso="2026-03-12T01:02:03+00:00", today="2026-03-12")
            issue_dir = self._find_issue_dir_by_id(target, "iss-00003")

            cases = (
                (
                    "blank",
                    "Working Title",
                    "20260312t010203z",
                    "20260312t010203z-working-title.md",
                    (
                        "種別: artifact",
                        'template: "blank"',
                        "自由形式で事実、メモ、図、リンク、検討",
                        "Requirement / Design / Plan または accepted ADR",
                    ),
                ),
                (
                    "research",
                    "research Title",
                    "20260312t010203z-01-research",
                    "20260312t010203z-01-research-research-title.md",
                    (
                        "種別: research",
                        "一つの source-grounded investigation",
                        "複数の証拠を統合",
                        "`disc` を使います",
                    ),
                ),
                (
                    "interview",
                    "interview Title",
                    "20260312t010203z-02-interview",
                    "20260312t010203z-02-interview-interview-title.md",
                    (
                        "種別: interview",
                        "明示的な質問と回答",
                        "## Question",
                        "## Answer",
                    ),
                ),
                (
                    "disc",
                    "disc Title",
                    "20260312t010203z-03-disc",
                    "20260312t010203z-03-disc-disc-title.md",
                    (
                        "種別: disc",
                        "複数の証拠を統合",
                        "trade-off",
                        "`research` を使います",
                    ),
                ),
                (
                    "decision-candidate",
                    "decision-candidate Title",
                    "20260312t010203z-04-decision-candidate",
                    "20260312t010203z-04-decision-candidate-decision-candidate-title.md",
                    (
                        "種別: decision-candidate",
                        "未採用の decision option",
                        "durable authority ではありません",
                        "明示的な判断後",
                    ),
                ),
                (
                    "adr",
                    "adr Title",
                    "20260312t010203z-05-adr",
                    "20260312t010203z-05-adr-adr-title.md",
                    (
                        "種別: ADR（Architecture Decision Record）",
                        'authority: "draft"',
                        "mirror_eligible: false",
                        "明示的に `accepted`",
                    ),
                ),
            )
            for artifact_type, title, artifact_id, filename, content_markers in cases:
                p = self._run_runtime_capture(
                    target,
                    ["new", "artifact", artifact_type, "--issue", "iss-00003", "--title", title],
                )
                assert p.returncode == 0, p.stdout + p.stderr
                expected_path = (
                    "spec-dock/initiatives/init-00001-auth-platform/epics/epic-00002-jwt-auth/"
                    f"issues/iss-00003-add-refresh-token/artifacts/{filename}"
                )
                assert (
                    f"spec-dock: ok (new artifact) type={artifact_type} "
                    f"id={artifact_id} scope=iss-00003 path={expected_path}"
                ) in p.stdout
                created = issue_dir / "artifacts" / filename
                assert created.is_file()
                content = created.read_text(encoding="utf-8")
                assert f'ID: "{artifact_id}"' in content
                assert f'タイトル: "{title}"' in content
                assert '親: ["iss-00003"]' in content
                assert "2026-03-12" in content
                assert f"# {artifact_id} {title}" in content
                for marker in content_markers:
                    assert marker in content

            created_names = sorted(path.name for path in (issue_dir / "artifacts").glob("*.md"))
            assert created_names == sorted(["rules.md", *(filename for _, _, _, filename, _ in cases)])

    @pytest.mark.parametrize(
        ("artifact_type", "template_marker", "authority_marker", "route_sections"),
        (
            (
                "research",
                'template: "research"',
                'authority: "evidence"',
                "## Question\n\n- Final question\n\n## Source\n\n- Final source\n\n"
                "## Findings\n\n- Final finding\n\n## Reflection\n\n- Final reflection\n",
            ),
            (
                "interview",
                'template: "interview"',
                'authority: "evidence"',
                "## Question\n\n- Final question\n\n## Answer\n\n- Final answer\n\n"
                "## Reflection\n\n- Final reflection\n",
            ),
            (
                "disc",
                'template: "disc"',
                'authority: "evidence"',
                "## Inputs\n\n- Final input\n\n## Synthesis\n\n- Final synthesis\n\n"
                "## Options and trade-offs\n\n- Final option\n\n## Reflection\n\n- Final reflection\n",
            ),
            (
                "decision-candidate",
                'template: "decision-candidate"',
                'authority: "draft"',
                "## Context\n\n- Final context\n\n## Options\n\n- Final option\n\n"
                "## Candidate\n\n- Final candidate\n\n## Reflection\n\n- Final reflection\n",
            ),
        ),
    )
    def test_issue_359_grill_route_creates_exactly_one_artifact_without_scope_mutation(
        self,
        artifact_type: str,
        template_marker: str,
        authority_marker: str,
        route_sections: str,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            self._write_runtime_clock(target, now_iso="2026-03-12T01:02:03+00:00", today="2026-03-12")
            issue_dir = self._find_issue_dir_by_id(target, "iss-00003")
            artifacts_dir = issue_dir / "artifacts"
            title = f"Issue 359 {artifact_type}"
            collision_seed = self._run_runtime_capture(
                target,
                ["new", "artifact", artifact_type, "--issue", "iss-00003", "--title", title],
            )
            assert collision_seed.returncode == 0, collision_seed.stdout + collision_seed.stderr
            protected_paths = (
                issue_dir / "requirement.md",
                issue_dir / "design.md",
                issue_dir / "plan.md",
                issue_dir / "report.md",
                issue_dir / ".meta.json",
                target / "spec-dock" / ".agent" / "active.json",
                target / "spec-dock" / ".agent" / "deps-issues.json",
            )
            protected_before = {path: path.read_bytes() if path.is_file() else None for path in protected_paths}
            artifact_tree_before = self._artifact_tree_snapshot(issue_dir)
            assert artifact_tree_before is not None
            artifact_entries_before = {entry[0]: entry for entry in artifact_tree_before}

            result = self._run_runtime_capture(
                target,
                [
                    "new",
                    "artifact",
                    artifact_type,
                    "--issue",
                    "iss-00003",
                    "--title",
                    title,
                ],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            artifact_tree_after = self._artifact_tree_snapshot(issue_dir)
            assert artifact_tree_after is not None
            artifact_entries_after = {entry[0]: entry for entry in artifact_tree_after}
            added = set(artifact_entries_after) - set(artifact_entries_before)
            assert len(added) == 1
            created = artifacts_dir / added.pop()
            assert created.is_file()
            assert created.suffix == ".md"
            created_before_finalize = created.read_text(encoding="utf-8")
            artifact_id = re.search(r'(?m)^ID: "([^"]+)"$', created_before_finalize)
            assert artifact_id is not None
            assert "-01-" in artifact_id.group(1)
            helper = target / ".agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py"
            artifact_rel = created.relative_to(target).as_posix()
            identity_result = subprocess.run(
                [
                    sys.executable,
                    str(helper),
                    "identity",
                    "--repo-root",
                    str(target),
                    "--artifact",
                    artifact_rel,
                ],
                cwd=target,
                capture_output=True,
                check=False,
            )
            assert identity_result.returncode == 0, identity_result.stderr.decode()
            identity = json.loads(identity_result.stdout)
            finalize_result = subprocess.run(
                [
                    sys.executable,
                    str(helper),
                    "finalize",
                    "--repo-root",
                    str(target),
                    "--artifact",
                    artifact_rel,
                    "--expected-device",
                    str(identity["device"]),
                    "--expected-inode",
                    str(identity["inode"]),
                    "--expected-ctime-ns",
                    str(identity["ctime_ns"]),
                ],
                cwd=target,
                input=route_sections.encode(),
                capture_output=True,
                check=False,
            )
            assert finalize_result.returncode == 0, finalize_result.stderr.decode()
            finalized = created.read_text(encoding="utf-8")
            for preserved in (
                f'ID: "{artifact_id.group(1)}"',
                f'タイトル: "{title}"',
                '親: ["iss-00003"]',
                template_marker,
                authority_marker,
                f"# {artifact_id.group(1)} {title}",
            ):
                assert preserved in finalized
            assert finalized.endswith(route_sections)
            artifact_tree_finalized = self._artifact_tree_snapshot(issue_dir)
            assert artifact_tree_finalized is not None
            artifact_entries_after = {entry[0]: entry for entry in artifact_tree_finalized}
            assert set(artifact_entries_after) - set(artifact_entries_before) == {created.name}
            assert f"path={created.relative_to(target).as_posix()}" in result.stdout
            assert set(artifact_entries_before) <= set(artifact_entries_after)
            for rel, entry_before in artifact_entries_before.items():
                assert artifact_entries_after[rel] == entry_before
            assert {path: path.read_bytes() if path.is_file() else None for path in protected_paths} == protected_before

    @pytest.mark.parametrize(
        "artifact_args",
        (
            ["new", "artifact", "research", "--title", "Missing selector"],
            [
                "new",
                "artifact",
                "research",
                "--issue",
                "iss-00003",
                "--epic",
                "epic-00002",
                "--title",
                "Multiple selectors",
            ],
            ["new", "artifact", "research", "--issue", "iss-00003", "--title", ""],
        ),
    )
    def test_issue_359_artifact_input_failures_are_zero_write(self, artifact_args: list[str]) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            issue_dir = self._find_issue_dir_by_id(target, "iss-00003")
            protected_paths = (
                issue_dir / "requirement.md",
                issue_dir / "design.md",
                issue_dir / "plan.md",
                issue_dir / "report.md",
                issue_dir / ".meta.json",
                target / "spec-dock" / ".agent" / "active.json",
                target / "spec-dock" / ".agent" / "deps-issues.json",
            )
            artifact_tree_before = self._artifact_tree_snapshot(issue_dir)
            protected_before = {path: path.read_bytes() if path.is_file() else None for path in protected_paths}

            result = self._run_runtime_capture(target, artifact_args)

            assert result.returncode != 0, result.stdout + result.stderr
            assert self._artifact_tree_snapshot(issue_dir) == artifact_tree_before
            assert {path: path.read_bytes() if path.is_file() else None for path in protected_paths} == protected_before

    def test_new_artifact_unsupported_types_fail_no_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            issue_dir = self._find_issue_dir_by_id(target, "iss-00003")

            for artifact_type in (
                "analysis",
                "pr-repair-batch",
                "draft-requirement",
                "draft-design",
                "draft-plan",
                "scratch",
                "note",
                "unknown",
            ):
                artifact_tree_before = self._artifact_tree_snapshot(issue_dir)
                p = self._run_runtime_capture(
                    target,
                    ["new", "artifact", artifact_type, "--issue", "iss-00003", "--title", f"{artifact_type} one"],
                )

                assert p.returncode != 0, p.stdout + p.stderr
                assert (
                    f"Cannot create artifact type: {artifact_type}. "
                    "Current artifact types: blank, research, interview, disc, decision-candidate, adr"
                ) in p.stderr
                assert self._artifact_tree_snapshot(issue_dir) == artifact_tree_before

    def test_new_artifact_rejects_scope_mismatch_and_unsafe_filesystem_no_write(self, monkeypatch) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            init_dir = target / "spec-dock" / "initiatives" / "init-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-00002-jwt-auth"
            issue_dir = self._find_issue_dir_by_id(target, "iss-00003")

            before = (self._artifact_tree_snapshot(epic_dir), self._artifact_tree_snapshot(issue_dir))
            mismatch = self._run_runtime_capture(
                target,
                ["new", "artifact", "--issue", "epic-00002", "--title", "Wrong Scope"],
            )
            assert mismatch.returncode != 0, mismatch.stdout + mismatch.stderr
            assert "--issue" in mismatch.stderr
            assert (self._artifact_tree_snapshot(epic_dir), self._artifact_tree_snapshot(issue_dir)) == before

            if self._can_create_symlink(target):
                external_dir = target / "outside-artifacts"
                external_dir.mkdir()
                artifacts_dir = issue_dir / "artifacts"
                shutil.rmtree(artifacts_dir)
                artifacts_dir.symlink_to(external_dir)
                symlinked_dir = self._run_runtime_capture(
                    target,
                    ["new", "artifact", "--issue", "iss-00003", "--title", "Unsafe Directory"],
                )
                assert symlinked_dir.returncode != 0, symlinked_dir.stdout + symlinked_dir.stderr
                assert "Destination already exists" in symlinked_dir.stderr
                assert list(external_dir.iterdir()) == []
                artifacts_dir.unlink()

                self._write_runtime_clock(
                    target,
                    now_iso="2026-03-12T01:02:03+00:00",
                    today="2026-03-12",
                )
                artifacts_dir.mkdir()
                rules_source = target / "spec-dock" / "docs" / "rules" / "issue" / "artifacts.md"
                (artifacts_dir / "rules.md").symlink_to(rules_source)
                external_file = target / "outside-artifact.md"
                external_file.write_text("sentinel\n", encoding="utf-8")
                unsafe_slot = artifacts_dir / "20260312t010203z-adr-unsafe-slot.md"
                unsafe_slot.symlink_to(external_file)
                slot_result = self._run_runtime_capture(
                    target,
                    ["new", "artifact", "adr", "--issue", "iss-00003", "--title", "Unsafe Slot"],
                )
                assert slot_result.returncode != 0, slot_result.stdout + slot_result.stderr
                assert "Unsafe artifact file" in slot_result.stderr
                assert external_file.read_text(encoding="utf-8") == "sentinel\n"
                unsafe_slot.unlink()

            monkeypatch.setenv("SPEC_DOCK_CREATE_LOCK_WAIT_SECONDS", "0")
            lock_path = target / "spec-dock" / "system" / ".runtime" / "create.lock"
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path.write_text("token=holder\npid=1\nuser=test\ncreated_unix=9999999999\n", encoding="utf-8")
            before_lock = self._artifact_tree_snapshot(issue_dir)
            lock_result = self._run_runtime_capture(
                target,
                ["new", "artifact", "disc", "--issue", "iss-00003", "--title", "Locked"],
            )
            assert lock_result.returncode != 0, lock_result.stdout + lock_result.stderr
            assert "create lock acquisition failed" in lock_result.stderr
            assert "No files were written" in lock_result.stderr
            assert self._artifact_tree_snapshot(issue_dir) == before_lock

    def test_new_artifact_stdout_uses_slugless_id_and_artifacts_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            p = self._run_runtime_capture(
                target,
                ["new", "artifact", "disc", "--issue", "iss-00003", "--title", "Discussion one"],
            )
            assert p.returncode == 0, p.stdout + p.stderr

            assert re.search(
                (
                    r"spec-dock: ok \(new artifact\) type=disc "
                    r"id=[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-disc "
                    r"scope=iss-00003 "
                    r"path=spec-dock/.*/artifacts/[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-disc-discussion-one\.md"
                ),
                p.stdout,
            )
            assert "discussion-one" not in re.search(r"id=([^\s]+)", p.stdout).group(1)

    def test_new_artifact_malformed_artifact_candidates_block_but_discussions_do_not(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            issue_dir = self._find_issue_dir_by_id(target, "iss-00003")
            discussions_dir = issue_dir / "discussions"
            artifacts_dir = issue_dir / "artifacts"
            discussions_dir.mkdir(exist_ok=True)
            (discussions_dir / "20260312t010203z-00-disc-malformed.md").write_text(
                "legacy malformed\n", encoding="utf-8"
            )

            p = self._run_runtime_capture(
                target, ["new", "artifact", "adr", "--issue", "iss-00003", "--title", "Decision one"]
            )
            assert p.returncode == 0, p.stdout + p.stderr
            assert len(sorted(artifacts_dir.glob("*-adr-decision-one.md"))) == 1

            malformed_name = "20260312t010203z-00-disc-malformed.md"
            (artifacts_dir / malformed_name).write_text("artifact malformed\n", encoding="utf-8")
            p = self._run_runtime_capture(
                target, ["new", "artifact", "adr", "--issue", "iss-00003", "--title", "Decision two"]
            )
            assert p.returncode != 0, p.stdout + p.stderr
            assert "Malformed artifact filename" in p.stderr
            assert malformed_name in p.stderr
            assert len(sorted(artifacts_dir.glob("*-adr-decision-two.md"))) == 0

    def test_new_artifact_preserves_grandfathered_legacy_artifact_basenames(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            issue_dir = self._find_issue_dir_by_id(target, "iss-00003")
            artifacts_dir = issue_dir / "artifacts"
            for filename in (
                "001-adr-token-rotation.md",
                "002-disc-api-options.md",
                "001-note-kickoff-memo.md",
            ):
                (artifacts_dir / filename).write_text("legacy artifact\n", encoding="utf-8")

            p = self._run_runtime_capture(
                target, ["new", "artifact", "adr", "--issue", "iss-00003", "--title", "Decision one"]
            )

            assert p.returncode == 0, p.stdout + p.stderr
            assert len(sorted(artifacts_dir.glob("*-adr-decision-one.md"))) == 1

    def test_new_artifact_old_node_setup_preserves_discussions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            issue_dir = self._find_issue_dir_by_id(target, "iss-00003")
            discussions_dir = issue_dir / "discussions"
            shutil.rmtree(issue_dir / "artifacts")
            discussions_dir.mkdir()
            (discussions_dir / "rules.md").write_text("legacy issue discussion rules\n", encoding="utf-8")
            (discussions_dir / "20260312t010203z-research-existing.md").write_text(
                "legacy research\n",
                encoding="utf-8",
            )
            discussions_before = sorted(path.name for path in discussions_dir.glob("*.md"))
            assert not (issue_dir / "artifacts").exists()

            p = self._run_runtime_capture(
                target,
                ["new", "artifact", "research", "--issue", "iss-00003", "--title", "Research One"],
            )
            assert p.returncode == 0, p.stdout + p.stderr
            rules_link = issue_dir / "artifacts" / "rules.md"
            target_rules = target / "spec-dock" / "docs" / "rules" / "issue" / "artifacts.md"
            assert rules_link.is_symlink()
            assert rules_link.resolve() == target_rules.resolve()
            assert str(rules_link.readlink()) == os.path.relpath(target_rules, start=rules_link.parent)
            assert sorted(path.name for path in discussions_dir.glob("*.md")) == discussions_before

    def test_new_artifact_rejects_invalid_slug_before_setup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            issue_dir = self._find_issue_dir_by_id(target, "iss-00003")

            p = self._run_runtime_capture(
                target,
                [
                    "new",
                    "artifact",
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
            assert sorted(path.name for path in (issue_dir / "artifacts").glob("*.md")) == ["rules.md"]

    def test_new_artifact_blank_rejects_ambiguous_supported_type_slug_before_setup(self) -> None:
        cases = (
            (["new", "artifact", "blank", "--issue", "iss-00003", "--title", "Research Notes"], "research-notes"),
            (
                [
                    "new",
                    "artifact",
                    "blank",
                    "--issue",
                    "iss-00003",
                    "--title",
                    "Choice",
                    "--slug",
                    "adr-choice",
                ],
                "adr-choice",
            ),
        )
        for command, slug in cases:
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp)
                assert main(["init", str(target)]) == 0
                self._create_same_repo_linked_hierarchy(target)
                issue_dir = self._find_issue_dir_by_id(target, "iss-00003")

                p = self._run_runtime_capture(target, command)

                assert p.returncode != 0, p.stdout + p.stderr
                assert "Ambiguous blank artifact slug" in p.stderr
                assert slug in p.stderr
                assert sorted(path.name for path in (issue_dir / "artifacts").glob("*.md")) == ["rules.md"]

    def test_new_artifact_rejects_unexpected_sequence_override_option(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(
                target,
                ["new", "artifact", "adr", "--issue", "iss-00003", "--seq", "1", "--title", "Decision one"],
            )
            assert p.returncode == 2, p.stdout + p.stderr
            assert "unrecognized arguments: --seq 1" in p.stderr

    def test_new_help_exposes_artifact_and_removes_doc_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p_new = self._run_runtime_capture(target, ["new", "--help"])
            assert p_new.returncode == 0, p_new.stdout + p_new.stderr
            assert "artifact" in p_new.stdout
            assert " doc " not in p_new.stdout
            assert "\n    adr" not in p_new.stdout
            assert "\n    disc" not in p_new.stdout
            assert "\n    research" not in p_new.stdout
            assert "\n    interview" not in p_new.stdout
            assert "\n    scratch" not in p_new.stdout
            assert "\n    note" not in p_new.stdout

            p_artifact = self._run_runtime_capture(target, ["new", "artifact", "--help"])
            assert p_artifact.returncode == 0, p_artifact.stdout + p_artifact.stderr
            assert "blank" in p_artifact.stdout
            assert "research" in p_artifact.stdout
            assert "interview" in p_artifact.stdout
            assert "decision-candidate" in p_artifact.stdout
            assert "adr" in p_artifact.stdout
            assert "pr-repair-batch" not in p_artifact.stdout
            assert "draft-plan" not in p_artifact.stdout
            assert "analysis" not in p_artifact.stdout
            assert "scratch" not in p_artifact.stdout
            assert "note" not in p_artifact.stdout
            assert "--template-file" not in p_artifact.stdout
            assert "--body-file" not in p_artifact.stdout
            assert "--basename" not in p_artifact.stdout
            assert "--doc-id" not in p_artifact.stdout
            assert "--id" not in p_artifact.stdout
            assert "--seq" not in p_artifact.stdout

            p_doc = self._run_runtime_capture(
                target, ["new", "doc", "adr", "--issue", "iss-00003", "--title", "Doc title"]
            )
            assert p_doc.returncode == 2, p_doc.stdout + p_doc.stderr
            assert "invalid choice: 'doc'" in p_doc.stderr
            assert "new artifact" not in p_doc.stderr

            for forbidden_option in ("--template-file", "--body-file", "--basename", "--doc-id", "--id"):
                p_forbidden = self._run_runtime_capture(
                    target,
                    [
                        "new",
                        "artifact",
                        "adr",
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
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
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

    def test_new_artifact_rejects_unknown_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(
                target,
                ["new", "artifact", "unknown", "--issue", "iss-00003", "--title", "Doc title"],
            )
            assert p.returncode == 1, p.stdout + p.stderr
            assert (
                "Cannot create artifact type: unknown. "
                "Current artifact types: blank, research, interview, disc, decision-candidate, adr"
            ) in p.stderr
            assert "invalid choice" not in p.stderr

    def test_new_nodes_generate_only_workbench_readmes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            init_dir = target / "spec-dock" / "initiatives" / "init-00001-auth-platform"
            readmes = sorted(path.relative_to(init_dir) for path in init_dir.rglob("README.md"))
            assert readmes == [
                Path(".workbench/README.md"),
                Path("epics/epic-00002-jwt-auth/.workbench/README.md"),
                Path("epics/epic-00002-jwt-auth/issues/iss-00003-add-refresh-token/.workbench/README.md"),
            ]
            readme_bytes = {(init_dir / relative_path).read_bytes() for relative_path in readmes}
            assert len(readme_bytes) == 1
            assert list(init_dir.rglob(".gitkeep")) == []

    def test_workbench_no_backfill_preserves_existing_scopes_across_all_triggers(self) -> None:
        def _snapshot(path: Path) -> tuple[tuple[str, str, bytes | str, int], ...]:
            entries: list[tuple[str, str, bytes | str, int]] = []
            for entry in sorted(path.rglob("*"), key=lambda item: item.as_posix()):
                relative = entry.relative_to(path).as_posix()
                stat = entry.lstat()
                if entry.is_symlink():
                    entries.append((relative, "symlink", str(entry.readlink()), stat.st_mtime_ns))
                elif entry.is_dir():
                    entries.append((relative, "dir", "", stat.st_mtime_ns))
                else:
                    entries.append((relative, "file", entry.read_bytes(), stat.st_mtime_ns))
            return tuple(entries)

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            init_dir = target / "spec-dock" / "initiatives" / "init-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-00002-jwt-auth"
            issue_dir = epic_dir / "issues" / "iss-00003-add-refresh-token"
            workbenches = (
                target / "spec-dock" / ".workbench",
                init_dir / ".workbench",
                epic_dir / ".workbench",
                issue_dir / ".workbench",
            )
            for index, workbench in enumerate(workbenches):
                (workbench / "README.md").unlink()
                nested = workbench / "nested"
                nested.mkdir()
                payload = nested / f"payload-{index}.bin"
                payload.write_bytes(bytes((0, 255, index, 10, 13)))
                (workbench / "empty").mkdir()
                if self._can_create_symlink(target):
                    (workbench / "payload-link").symlink_to(payload.relative_to(workbench))

            expected = {workbench: _snapshot(workbench) for workbench in workbenches}

            operations = (
                ("force init", lambda: main(["init", str(target), "--force"])),
                ("update", lambda: main(["update", str(target)])),
                ("validate", lambda: self._run_runtime(target, ["validate"])),
                ("sync", lambda: self._run_runtime(target, ["sync", "--no-github", "--no-update-active"])),
                ("active", lambda: self._run_runtime(target, ["active", "set", "--id", "iss-00003"])),
                (
                    "artifact",
                    lambda: self._run_runtime(
                        target,
                        ["new", "artifact", "blank", "--issue", "iss-00003", "--title", "Working Notes"],
                    ),
                ),
                (
                    "adr",
                    lambda: self._run_runtime(
                        target,
                        ["new", "artifact", "adr", "--issue", "iss-00003", "--title", "Decision One"],
                    ),
                ),
            )
            for label, operation in operations:
                result = operation()
                if isinstance(result, int):
                    assert result == 0, label
                for workbench in workbenches:
                    assert _snapshot(workbench) == expected[workbench], label
                    assert not (workbench / "README.md").exists(), label

            self._run_runtime(
                target,
                [
                    "new",
                    "issue",
                    "--epic",
                    "2",
                    "--title",
                    "Future child",
                    "--github-issue",
                    "4",
                ],
            )
            child_readme = epic_dir / "issues" / "iss-00004-future-child" / ".workbench" / "README.md"
            assert child_readme.is_file()
            for workbench in workbenches:
                assert _snapshot(workbench) == expected[workbench]
                assert not (workbench / "README.md").exists()

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
                'echo "gh should not be invoked in --no-github mode" >&2\n'
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
                "  count=$((count + 1))\n"
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
                'echo "unexpected gh args: $@" >&2\n'
                "exit 1\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform"], env=test_env)
            self._run_runtime(
                target, ["new", "epic", "--initiative", "init-00123", "--title", "JWT auth"], env=test_env
            )

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
        pytest.skip("S06 replacement: tests.unit.commands.test_runtime_new_s08 covers create-lock failure guidance.")
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
                'if [[ "$1" == "issue" && "$2" == "create" ]]; then\n'
                '  echo "https://github.com/example/repo/issues/123"\n'
                "  exit 0\n"
                "fi\n"
                'if [[ "$1" == "issue" && "$2" == "list" ]]; then\n'
                '  echo "[{\\"number\\":123,\\"state\\":\\"OPEN\\",\\"title\\":\\"Issue 123\\",\\"labels\\":[],\\"updatedAt\\":\\"2026-05-13T00:00:03Z\\",\\"url\\":\\"https://github.com/example/repo/issues/123\\"}]"\n'
                "  exit 0\n"
                "fi\n"
                'echo "unexpected gh args: $@" >&2\n'
                "exit 1\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            runtime_fs_repo = target / "spec-dock" / "scripts" / "spec_dock_runtime" / "infra" / "fs_repo.py"
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
            self._run_runtime(
                target, ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"]
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                'if [[ "$1" == "issue" && "$2" == "create" ]]; then\n'
                '  echo "https://github.com/example/repo/issues/123"\n'
                "  exit 0\n"
                "fi\n"
                'if [[ "$1" == "issue" && "$2" == "list" ]]; then\n'
                '  echo "[{\\"number\\":1,\\"state\\":\\"OPEN\\",\\"title\\":\\"Issue 1\\",\\"labels\\":[],\\"updatedAt\\":\\"2026-05-13T00:00:01Z\\",\\"url\\":\\"https://github.com/example/repo/issues/1\\"},{\\"number\\":2,\\"state\\":\\"OPEN\\",\\"title\\":\\"Issue 2\\",\\"labels\\":[],\\"updatedAt\\":\\"2026-05-13T00:00:02Z\\",\\"url\\":\\"https://github.com/example/repo/issues/2\\"},{\\"number\\":123,\\"state\\":\\"OPEN\\",\\"title\\":\\"Issue 123\\",\\"labels\\":[],\\"updatedAt\\":\\"2026-05-13T00:00:03Z\\",\\"url\\":\\"https://github.com/example/repo/issues/123\\"}]"\n'
                "  exit 0\n"
                "fi\n"
                'echo "unexpected gh args: $@" >&2\n'
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
            self._run_runtime(
                target, ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"]
            )

            # Provide a fake `gh` binary so the test doesn't require network/auth.
            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                'if [[ "$1" == "issue" && "$2" == "create" ]]; then\n'
                '  echo "https://github.com/example/repo/issues/123"\n'
                "  exit 0\n"
                "fi\n"
                'if [[ "$1" == "issue" && "$2" == "list" ]]; then\n'
                '  echo "[{\\"number\\":1,\\"state\\":\\"OPEN\\",\\"title\\":\\"Issue 1\\",\\"labels\\":[],\\"updatedAt\\":\\"2026-05-13T00:00:01Z\\",\\"url\\":\\"https://github.com/example/repo/issues/1\\"},{\\"number\\":2,\\"state\\":\\"OPEN\\",\\"title\\":\\"Issue 2\\",\\"labels\\":[],\\"updatedAt\\":\\"2026-05-13T00:00:02Z\\",\\"url\\":\\"https://github.com/example/repo/issues/2\\"},{\\"number\\":123,\\"state\\":\\"OPEN\\",\\"title\\":\\"Issue 123\\",\\"labels\\":[],\\"updatedAt\\":\\"2026-05-13T00:00:03Z\\",\\"url\\":\\"https://github.com/example/repo/issues/123\\"}]"\n'
                "  exit 0\n"
                "fi\n"
                'echo "unexpected gh args: $@" >&2\n'
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
            self._run_runtime(
                target, ["new", "epic", "--initiative", "1", "--title", "Parent epic", "--github-issue", "2"]
            )
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
