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

    def _find_issue_dir_by_id(self, target: Path, issue_id: str) -> Path:
        for meta_path in sorted((target / "spec-dock" / "initiatives").glob("**/.meta.json")):
            payload = json.loads(meta_path.read_text(encoding="utf-8"))
            if payload.get("type") == "issue" and payload.get("id") == issue_id:
                return meta_path.parent
        raise AssertionError(f"issue not found: {issue_id}")

    def _set_assurance_contract_profile(
        self,
        issue_dir: Path,
        profile: str,
        *,
        complexity_tier: str = "complex",
    ) -> None:
        from spec_dock.assets.spec_dock.scripts.spec_dock_runtime.domain.assurance import (
            FactValue,
            RiskFact,
            classify_risk_facts,
        )

        contract_path = issue_dir / ".assurance.json"
        payload = json.loads(contract_path.read_text(encoding="utf-8"))
        risk_values: dict[str, FactValue] | None = None
        if profile == "lite":
            risk_values = {
                "docs_only_change": "true",
                "explicit_lite_opt_in": "true",
                "lite_evidence_gate_passed": "true",
                "migration_or_persistence_change": "false",
                "public_contract_change": "false",
                "rollback_difficulty_high": "false",
                "runtime_behavior_change": "false",
                "security_or_privacy_sensitive": "false",
            }
            complexity_tier = "normal"
        elif profile == "standard":
            risk_values = {
                "docs_only_change": "unknown",
                "explicit_lite_opt_in": "false",
                "lite_evidence_gate_passed": "false",
                "migration_or_persistence_change": "unknown",
                "public_contract_change": "unknown",
                "rollback_difficulty_high": "unknown",
                "runtime_behavior_change": "unknown",
                "security_or_privacy_sensitive": "unknown",
            }
            complexity_tier = "normal"
        elif profile in ("strict", "critical"):
            risk_values = {
                "docs_only_change": "unknown",
                "explicit_lite_opt_in": "false",
                "lite_evidence_gate_passed": "false",
                "migration_or_persistence_change": "unknown",
                "public_contract_change": "true" if profile == "strict" else "unknown",
                "rollback_difficulty_high": "unknown",
                "runtime_behavior_change": "unknown",
                "security_or_privacy_sensitive": "true" if profile == "critical" else "unknown",
            }
        if risk_values is not None:
            risk_facts = tuple(
                RiskFact(
                    key=key,
                    value=value,
                    source="requirement",
                    reason_code=f"fact_default_{key}",
                )
                for key, value in sorted(risk_values.items())
            )
            payload["risk_facts"] = [fact.to_dict() for fact in risk_facts]
            payload["classification"] = classify_risk_facts(risk_facts).to_dict()
        payload["classification"]["authorized_profile"] = profile
        payload["classification"]["complexity_tier"] = complexity_tier
        if profile != "lite":
            payload["classification"]["lite_candidate"] = False
            payload["classification"]["lite_authorized"] = False
        payload["obligations"]["profile_preset"] = profile
        contract_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

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

    def _canonical_design_plan_snapshot(self, issue_dir: Path) -> tuple[tuple[str, str], ...]:
        return tuple(
            (filename, (issue_dir / filename).read_text(encoding="utf-8"))
            for filename in ("design.md", "plan.md")
        )

    def _assert_profile_draft_no_write_failure(
        self,
        target: Path,
        issue_dir: Path,
        command: list[str],
        expected_stderr: str,
    ) -> None:
        before = self._artifact_tree_snapshot(issue_dir)
        canonical_before = self._canonical_design_plan_snapshot(issue_dir)
        p = self._run_runtime_capture(target, command)
        assert p.returncode != 0, p.stdout + p.stderr
        assert expected_stderr in p.stderr
        if before is None:
            assert not (issue_dir / "artifacts").exists()
        else:
            after = self._artifact_tree_snapshot(issue_dir)
            assert after == before
        assert self._canonical_design_plan_snapshot(issue_dir) == canonical_before

    def test_new_issue_creates_assurance_compose_placeholders_for_design_and_plan(self) -> None:
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

            for filename in ("design.md", "plan.md"):
                text = (issue_dir / filename).read_text(encoding="utf-8")
                assert "artifact_state: awaiting-assurance-compose" in text
                assert "assurance classify --stage requirement" in text
                assert "assurance compose --artifact all" in text
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
                ["new", "artifact", "blank", "--issue", "iss-00003", "--title", "Working Notes"],
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
                        "型を先に決めず",
                    ),
                ),
                (
                    "research",
                    "research Title",
                    "20260312t010203z-01-research",
                    "20260312t010203z-01-research-research-title.md",
                    (
                        "種別: research",
                        "調査目的",
                        "source-grounded research evidence surface",
                    ),
                ),
                (
                    "interview",
                    "interview Title",
                    "20260312t010203z-02-interview",
                    "20260312t010203z-02-interview-interview-title.md",
                    (
                        "種別: interview",
                        "正式質問として扱う理由",
                        "one essential question",
                    ),
                ),
                (
                    "disc",
                    "disc Title",
                    "20260312t010203z-03-disc",
                    "20260312t010203z-03-disc-disc-title.md",
                    (
                        "種別: disc",
                        "対象論点",
                        "synthesis / reflection proposal",
                    ),
                ),
                (
                    "decision-candidate",
                    "decision-candidate Title",
                    "20260312t010203z-04-decision-candidate",
                    "20260312t010203z-04-decision-candidate-decision-candidate-title.md",
                    (
                        "種別: decision-candidate",
                        "判断候補",
                        "proposed decision",
                    ),
                ),
                (
                    "pr-repair-batch",
                    "pr-repair-batch Title",
                    "20260312t010203z-05-pr-repair-batch",
                    "20260312t010203z-05-pr-repair-batch-pr-repair-batch-title.md",
                    (
                        "種別: pr-repair-batch",
                        "PR / Observation Metadata",
                        "Required GitHub Actions CI failures",
                    ),
                ),
                (
                    "adr",
                    "adr Title",
                    "20260312t010203z-06-adr",
                    "20260312t010203z-06-adr-adr-title.md",
                    (
                        "種別: ADR（Architecture Decision Record）",
                        "ADR 化基準",
                        "accepted authority fields",
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

    def test_new_artifact_issue_draft_requirement_uses_issue_requirement_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            p = self._run_runtime_capture(
                target,
                ["new", "artifact", "draft-requirement", "--issue", "iss-00003", "--title", "Issue Requirement"],
            )

            assert p.returncode == 0, p.stdout + p.stderr
            issue_dir = self._find_issue_dir_by_id(target, "iss-00003")
            created = sorted((issue_dir / "artifacts").glob("*-draft-requirement-issue-requirement.md"))
            assert len(created) == 1
            content = created[0].read_text(encoding="utf-8")
            assert "Issue 要件定義" in content
            assert "artifact_state: awaiting-assurance-compose" not in content
            assert "Issue 設計書" not in content

    def test_new_artifact_issue_design_and_plan_use_authorized_profile_templates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            self._run_runtime(target, ["active", "set", "--id", "iss-00003"])
            self._run_runtime(target, ["assurance", "classify", "--stage", "requirement", "--format", "json"])

            issue_dir = self._find_issue_dir_by_id(target, "iss-00003")
            profile_cases = (
                ("lite", "normal", "Issue 設計書（Lite）", "Issue 実装計画書（Lite"),
                ("standard", "normal", "Issue 設計書（Standard）", "Issue 実装計画書（Standard"),
                ("strict", "complex", "Issue 設計書（Strict）", "Issue 実装計画書（Strict"),
                ("critical", "deep", "Issue 設計書（Critical）", "Issue 実装計画書（Critical"),
            )

            for profile, complexity_tier, design_heading, plan_heading in profile_cases:
                self._set_assurance_contract_profile(issue_dir, profile, complexity_tier=complexity_tier)
                cases = (
                    (
                        ["new", "artifact", "draft-design", "--issue", "iss-00003", "--title", f"{profile} Design"],
                        "draft-design",
                        design_heading,
                        f"templates/issue-profiles/{profile}/design.md",
                    ),
                    (
                        ["new", "artifact", "draft-plan", "--issue", "iss-00003", "--title", f"{profile} Plan"],
                        "draft-plan",
                        plan_heading,
                        f"templates/issue-profiles/{profile}/plan.md",
                    ),
                )
                for command, doc_type, profile_heading, template_source in cases:
                    before = set((issue_dir / "artifacts").glob(f"*-{doc_type}-*.md"))
                    canonical_before = self._canonical_design_plan_snapshot(issue_dir)
                    p = self._run_runtime_capture(target, command)
                    assert p.returncode == 0, p.stdout + p.stderr
                    assert f"type={doc_type}" in p.stdout
                    after = set((issue_dir / "artifacts").glob(f"*-{doc_type}-*.md"))
                    created = sorted(after - before)
                    assert len(created) == 1
                    assert self._canonical_design_plan_snapshot(issue_dir) == canonical_before
                    content = created[0].read_text(encoding="utf-8")
                    assert profile_heading in content
                    assert "artifact_state: awaiting-assurance-compose" not in content
                    assert "設計（どう実現するか）" not in content
                    assert "実装計画（実行契約 / Execution Contract）" not in content
                    assert "authority: accepted" not in content
                    assert "adoption_status: adopted" not in content
                    canonical_source = target / "spec-dock" / template_source
                    assert canonical_source.is_file(), f"missing source template: {canonical_source}"
                    if doc_type == "draft-plan" and profile == "lite":
                        assert "commit候補:" not in content
                        assert "static analysis / lint:" not in content
                        assert "PR 作成後の GitHub Actions" not in content
                    elif doc_type == "draft-plan":
                        assert "最終品質ゲート" in content or "最終安全ゲート" in content
                        assert "static analysis / lint:" in content
                        assert "tests:" in content
                        assert "report:" in content
                        assert "commit候補:" in content

    def test_new_artifact_issue_profile_drafts_fail_closed_without_valid_assurance_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            issue_dir = self._find_issue_dir_by_id(target, "iss-00003")

            commands = (
                ("draft-design", "Design Draft"),
                ("draft-plan", "Plan Draft"),
            )
            for doc_type, title in commands:
                self._assert_profile_draft_no_write_failure(
                    target,
                    issue_dir,
                    ["new", "artifact", doc_type, "--issue", "iss-00003", "--title", title],
                    "missing_assurance_contract",
                )

            (issue_dir / ".assurance.json").write_text("{not-json\n", encoding="utf-8")
            for doc_type, title in commands:
                self._assert_profile_draft_no_write_failure(
                    target,
                    issue_dir,
                    ["new", "artifact", doc_type, "--issue", "iss-00003", "--title", f"Invalid {title}"],
                    "invalid_json",
                )

            self._run_runtime(target, ["active", "set", "--id", "iss-00003"])
            self._run_runtime(target, ["assurance", "classify", "--stage", "requirement", "--format", "json"])
            (issue_dir / "requirement.md").write_text("# Changed requirement.md\n", encoding="utf-8")
            for doc_type, title in commands:
                self._assert_profile_draft_no_write_failure(
                    target,
                    issue_dir,
                    ["new", "artifact", doc_type, "--issue", "iss-00003", "--title", f"Stale {title}"],
                    "stale_source_binding",
                )

            self._run_runtime(target, ["active", "set", "--id", "iss-00003"])
            self._run_runtime(target, ["assurance", "classify", "--stage", "requirement", "--format", "json"])
            self._set_assurance_contract_profile(issue_dir, "enterprise")
            for doc_type, title in commands:
                self._assert_profile_draft_no_write_failure(
                    target,
                    issue_dir,
                    ["new", "artifact", doc_type, "--issue", "iss-00003", "--title", f"Unsupported {title}"],
                    "invalid_classification",
                )

    def test_new_artifact_issue_profile_drafts_fail_closed_for_invalid_profile_templates(self) -> None:
        cases = (
            ("missing", "Profile template not found"),
            ("directory", "Profile template is not a file"),
            ("empty-body", "Profile template body is empty"),
        )
        for template_state, expected_stderr in cases:
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp)
                assert main(["init", str(target)]) == 0
                self._create_same_repo_linked_hierarchy(target)
                self._run_runtime(target, ["active", "set", "--id", "iss-00003"])
                self._run_runtime(target, ["assurance", "classify", "--stage", "requirement", "--format", "json"])
                issue_dir = self._find_issue_dir_by_id(target, "iss-00003")
                plan_template = target / "spec-dock" / "templates" / "issue-profiles" / "standard" / "plan.md"
                plan_template.unlink()
                if template_state == "directory":
                    plan_template.mkdir()
                elif template_state == "empty-body":
                    plan_template.write_text(
                        '---\nprofile: "standard"\nartifact: "plan"\n---\n',
                        encoding="utf-8",
                    )

                self._assert_profile_draft_no_write_failure(
                    target,
                    issue_dir,
                    ["new", "artifact", "draft-plan", "--issue", "iss-00003", "--title", f"{template_state} Plan"],
                    expected_stderr,
                )

    def test_new_artifact_issue_profile_drafts_fail_closed_for_symlinked_profile_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            if not self._can_create_symlink(target):
                pytest.skip("symlink creation is not available")
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            self._run_runtime(target, ["active", "set", "--id", "iss-00003"])
            self._run_runtime(target, ["assurance", "classify", "--stage", "requirement", "--format", "json"])
            issue_dir = self._find_issue_dir_by_id(target, "iss-00003")
            external = target / "outside-plan.md"
            external.write_text("# Outside Plan\n", encoding="utf-8")
            plan_template = target / "spec-dock" / "templates" / "issue-profiles" / "standard" / "plan.md"
            plan_template.unlink()
            plan_template.symlink_to(external)

            self._assert_profile_draft_no_write_failure(
                target,
                issue_dir,
                ["new", "artifact", "draft-plan", "--issue", "iss-00003", "--title", "Symlink Plan"],
                "Profile template is symlinked",
            )

    def test_new_artifact_unsupported_types_fail_no_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            issue_dir = self._find_issue_dir_by_id(target, "iss-00003")

            for artifact_type in ("scratch", "note", "unknown"):
                artifact_files_before = sorted((issue_dir / "artifacts").glob("*.md"))
                p = self._run_runtime_capture(
                    target,
                    ["new", "artifact", artifact_type, "--issue", "iss-00003", "--title", f"{artifact_type} one"],
                )

                assert p.returncode != 0, p.stdout + p.stderr
                assert artifact_type in p.stderr
                assert sorted((issue_dir / "artifacts").glob("*.md")) == artifact_files_before

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

    def test_new_artifact_creates_pr_repair_batch_with_generated_identity_and_template(self) -> None:
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
                ["new", "artifact", "pr-repair-batch", "--issue", "iss-00003", "--title", "PR Repair Batch"],
            )

            assert p.returncode == 0, p.stdout + p.stderr
            assert re.search(
                (
                    r"spec-dock: ok \(new artifact\) type=pr-repair-batch "
                    r"id=20260312t010203z-pr-repair-batch "
                    r"scope=iss-00003 "
                    r"path=spec-dock/.*/artifacts/"
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
                / "artifacts"
                / "20260312t010203z-pr-repair-batch-pr-repair-batch.md"
            )
            assert created.is_file()
            content = created.read_text(encoding="utf-8")
            assert "種別: pr-repair-batch" in content
            assert 'ID: "20260312t010203z-pr-repair-batch"' in content
            assert 'タイトル: "PR Repair Batch"' in content
            assert '親: ["iss-00003"]' in content
            assert "# 20260312t010203z-pr-repair-batch PR Repair Batch" in content
            assert "Required GitHub Actions CI failures exist." in content
            assert "`check_failure:<actions_job_or_workflow_name>`" in content
            assert "External/non-Actions check state" in content
            assert "triage review findings, CI failures" not in content
            assert "`check_failure:<job_or_check_name>`" not in content
            assert "No required check failure remains." not in content

    def test_new_artifact_draft_scope_failures_do_not_setup_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            init_dir = target / "spec-dock" / "initiatives" / "init-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-00002-jwt-auth"

            for command, scope_dir in (
                (
                    [
                        "new",
                        "artifact",
                        "draft-requirement",
                        "--initiative",
                        "init-00001",
                        "--title",
                        "Requirement Draft",
                    ],
                    init_dir,
                ),
                (["new", "artifact", "draft-plan", "--epic", "epic-00002", "--title", "Plan Draft"], epic_dir),
            ):
                artifact_files_before = sorted((scope_dir / "artifacts").glob("*.md"))
                p = self._run_runtime_capture(target, command)
                assert p.returncode != 0, p.stdout + p.stderr
                assert "issue scope" in p.stderr
                assert sorted((scope_dir / "artifacts").glob("*.md")) == artifact_files_before

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
            assert "pr-repair-batch" in p_artifact.stdout
            assert "draft-plan" in p_artifact.stdout
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
            assert "Unknown artifact type: unknown" in p.stderr
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
