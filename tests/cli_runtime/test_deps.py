import json
import os
from pathlib import Path
import shutil
import stat
import tempfile

import pytest

from tests.cli_runtime.harness import (
    CliRuntimeHarness,
    main,
)


class TestCliDeps(CliRuntimeHarness):
    def test_deps_check_rejects_github_and_no_github_together(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00003", "--github", "--no-github"])
            assert p.returncode == 2, p.stdout + p.stderr
            assert "not allowed with argument" in p.stderr

    def _create_local_compat_hierarchy(
        self,
        target: Path,
        *,
        owner: str = "example",
        repo: str = "repo",
        initiative_issue_number: int = 101,
        epic_issue_number: int = 201,
        initiative_title: str = "Auth platform",
        epic_title: str = "JWT auth",
        issues: tuple[tuple[int, str], ...] = ((301, "Add refresh token"),),
    ) -> dict[str, str]:
        self._create_same_repo_linked_hierarchy(
            target,
            owner=owner,
            repo=repo,
            initiative_issue_number=initiative_issue_number,
            epic_issue_number=epic_issue_number,
            issue_issue_number=issues[0][0],
            initiative_title=initiative_title,
            epic_title=epic_title,
            issue_title=issues[0][1],
        )
        for issue_number, title in issues[1:]:
            self._run_runtime(
                target,
                [
                    "new",
                    "issue",
                    "--epic",
                    str(epic_issue_number),
                    "--title",
                    title,
                    "--github-issue",
                    str(issue_number),
                ],
            )
        return self._materialize_local_compat_ids(target)

    def _drop_github_repo_scope(self, node_dir: Path) -> None:
        meta_path = node_dir / ".meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        github = meta.get("github")
        assert isinstance(github, dict)
        github_dict = dict(github)
        github_dict.pop("repo_owner", None)
        github_dict.pop("repo_name", None)
        meta["github"] = github_dict
        self._write_json_force(meta_path, meta)

    def _set_meta_depends_on(self, node_dir: Path, depends_on: object) -> None:
        meta_path = node_dir / ".meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["depends_on"] = depends_on
        self._write_json_force(meta_path, meta)

    def _set_meta_schema_version(self, node_dir: Path, schema_version: int) -> None:
        meta_path = node_dir / ".meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["schema_version"] = schema_version
        self._write_json_force(meta_path, meta)

    def _find_meta_path_by_id(self, target: Path, node_id: str) -> Path:
        for meta_path in sorted((target / "spec-dock" / "initiatives").glob("**/.meta.json")):
            payload = json.loads(meta_path.read_text(encoding="utf-8"))
            if payload.get("id") == node_id:
                return meta_path
        raise AssertionError(f"meta path not found for node id: {node_id}")

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
        return {
            **os.environ,
            "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}",
        }

    def _read_deps_projection_artifacts(self, target: Path) -> dict[str, str | None]:
        paths = (
            target / "spec-dock" / ".agent" / "deps-issues.json",
            target / "spec-dock" / "deps-issues.puml",
        )
        return {
            path.relative_to(target).as_posix(): path.read_text(encoding="utf-8") if path.exists() else None
            for path in paths
        }

    def _assert_deps_projection_has_edge(self, target: Path, from_id: str, to_id: str) -> None:
        specdock_dir = target / "spec-dock"
        deps_json_path = specdock_dir / ".agent" / "deps-issues.json"
        deps_puml_path = specdock_dir / "deps-issues.puml"
        assert deps_json_path.is_file(), f"missing artifact: {deps_json_path}"
        assert deps_puml_path.is_file(), f"missing artifact: {deps_puml_path}"
        deps_issues = json.loads(deps_json_path.read_text(encoding="utf-8"))
        assert any(edge.get("from") == from_id and edge.get("to") == to_id for edge in deps_issues["edges"])
        deps_puml = deps_puml_path.read_text(encoding="utf-8")
        assert from_id in deps_puml
        assert to_id in deps_puml
        assert ": blocks" in deps_puml

    def _assert_deps_projection_lacks_edge(self, target: Path, from_id: str, to_id: str) -> None:
        deps_json_path = target / "spec-dock" / ".agent" / "deps-issues.json"
        deps_puml_path = target / "spec-dock" / "deps-issues.puml"
        assert deps_json_path.is_file(), f"missing artifact: {deps_json_path}"
        assert deps_puml_path.is_file(), f"missing artifact: {deps_puml_path}"
        deps_issues = json.loads(deps_json_path.read_text(encoding="utf-8"))
        assert not any(edge.get("from") == from_id and edge.get("to") == to_id for edge in deps_issues["edges"])
        deps_puml = deps_puml_path.read_text(encoding="utf-8")
        assert ": blocks" not in deps_puml

    def _create_deps_auto_sync_fixture(self, target: Path, *, log_path: Path) -> dict[str, str]:
        self._init_origin_repo(target)
        test_env = self._install_gh_issue_list_stub(
            target,
            issue_numbers=[101, 201, 301, 302],
            log_path=log_path,
        )
        self._run_runtime(
            target,
            ["new", "initiative", "--title", "Auth platform", "--github-issue", "101"],
            env=test_env,
        )
        self._run_runtime(
            target,
            ["new", "epic", "--initiative", "101", "--title", "JWT auth", "--github-issue", "201"],
            env=test_env,
        )
        self._run_runtime(
            target,
            ["new", "issue", "--epic", "201", "--title", "From issue", "--github-issue", "301"],
            env=test_env,
        )
        self._run_runtime(
            target,
            ["new", "issue", "--epic", "201", "--title", "To issue", "--github-issue", "302"],
            env=test_env,
        )
        log_path.write_text("", encoding="utf-8")
        return {
            "env": test_env,
            "from_id": "iss-00301",
            "to_id": "iss-00302",
        }

    def _create_cross_epic_inherited_dependency_fixture(self, target: Path) -> dict[str, str]:
        self._create_same_repo_linked_hierarchy(
            target,
            owner="example",
            repo="repo",
            initiative_issue_number=101,
            epic_issue_number=201,
            issue_issue_number=301,
            issue_title="From issue",
        )
        self._run_runtime(
            target,
            [
                "new",
                "epic",
                "--initiative",
                "101",
                "--github-issue",
                "202",
                "--title",
                "Dependency epic",
            ],
        )
        self._run_runtime(
            target,
            [
                "new",
                "issue",
                "--epic",
                "202",
                "--github-issue",
                "302",
                "--title",
                "To issue",
            ],
        )
        from_issue_id = "iss-00301"
        to_issue_id = "iss-00302"
        from_epic_id = "epic-00201"
        to_epic_id = "epic-00202"
        self._set_meta_depends_on(self._find_meta_path_by_id(target, from_epic_id).parent, [to_epic_id])
        return {
            "iss-00301": from_issue_id,
            "iss-00302": to_issue_id,
            "epic-00201": from_epic_id,
            "epic-00202": to_epic_id,
        }

    def _create_mixed_node_dependency_fixture(self, target: Path) -> dict[str, str]:
        self._create_same_repo_linked_hierarchy(
            target,
            owner="example",
            repo="repo",
            initiative_issue_number=101,
            epic_issue_number=201,
            issue_issue_number=301,
            issue_title="From issue",
        )
        self._run_runtime(
            target,
            ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Sibling issue"],
        )
        self._run_runtime(
            target,
            ["new", "initiative", "--github-issue", "102", "--title", "Dependency initiative"],
        )
        self._run_runtime(
            target,
            ["new", "epic", "--initiative", "102", "--github-issue", "202", "--title", "Dependency epic"],
        )
        self._run_runtime(
            target,
            ["new", "issue", "--epic", "202", "--github-issue", "303", "--title", "Dependency issue"],
        )
        return {
            "init-00101": "init-00101",
            "iss-00301": "iss-00301",
            "epic-00202": "epic-00202",
        }

    def _make_gh_issue_list_and_view_stub(
        self,
        bin_dir: Path,
        *,
        issues: list[dict[str, object]],
    ) -> None:
        normalized: list[dict[str, object]] = []
        for issue in issues:
            item = dict(issue)
            number = item.get("number")
            url = item.get("url")
            if isinstance(number, int) and not (
                isinstance(url, str) and url.startswith("https://github.com/")
            ):
                item["url"] = f"https://github.com/example/repo/issues/{number}"
            normalized.append(item)

        gh_path = bin_dir / "gh"
        gh_path.write_text(
            (
                "#!/usr/bin/env python3\n"
                "import json\n"
                "import sys\n\n"
                f"ISSUES = {json.dumps(normalized, ensure_ascii=False)}\n"
                "ISSUES_BY_NUMBER = {\n"
                "    int(item['number']): item\n"
                "    for item in ISSUES\n"
                "    if isinstance(item.get('number'), int)\n"
                "}\n\n"
                "args = sys.argv[1:]\n"
                "if args[:2] == ['issue', 'list']:\n"
                "    print(json.dumps(ISSUES))\n"
                "    raise SystemExit(0)\n"
                "if args[:2] == ['issue', 'view']:\n"
                "    number = int(args[2])\n"
                "    item = ISSUES_BY_NUMBER.get(number)\n"
                "    if item is None:\n"
                "        print('issue not found: ' + str(number), file=sys.stderr)\n"
                "        raise SystemExit(1)\n"
                "    print(json.dumps({'number': number, 'url': item['url']}))\n"
                "    raise SystemExit(0)\n"
                "print(f'unexpected gh args: {args}', file=sys.stderr)\n"
                "raise SystemExit(99)\n"
            ),
            encoding="utf-8",
        )
        gh_path.chmod(0o755)

    def test_sync_deps_progress_aggregation_for_epic_and_initiative(self) -> None:
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
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "202", "--title", "OAuth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "303", "--title", "Second epic issue"],
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 202, "state": "OPEN", "title": "Epic2", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 303, "state": "OPEN", "title": "Second", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr

            index = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            nodes = index["nodes"]
            assert nodes["epic-00201"]["progress"] == {"total": 2, "done": 1, "open": 1, "unknown": 0}
            assert nodes["epic-00202"]["progress"] == {"total": 1, "done": 0, "open": 1, "unknown": 0}
            assert nodes["init-00101"]["progress"] == {"total": 3, "done": 1, "open": 2, "unknown": 0}
            assert nodes["iss-00301"]["status"] == "done"
            assert nodes["iss-00302"]["status"] == "open"
            assert nodes["iss-00303"]["status"] == "open"

    def test_sync_deps_empty_open_epic_blocks_with_node_context(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Empty init"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "Empty epic"],
            )
            self._run_runtime(target, ["new", "initiative", "--github-issue", "102", "--title", "Work init"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "102", "--github-issue", "202", "--title", "Work epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "301", "--title", "Target issue"],
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00102-work-init"
                / "epics"
                / "epic-00202-work-epic"
                / "issues"
                / "iss-00301-target-issue"
            )
            self._set_meta_depends_on(issue_dir, [201])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Empty init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Empty epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 102, "state": "OPEN", "title": "Work init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 202, "state": "OPEN", "title": "Work epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr

            index = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            nodes = index["nodes"]
            assert nodes["epic-00201"]["progress"] == {"total": 0, "done": 0, "open": 0, "unknown": 0}
            assert nodes["init-00101"]["progress"] == {"total": 0, "done": 0, "open": 0, "unknown": 0}
            assert not nodes["iss-00301"]["deps"]["ready"]
            assert nodes["iss-00301"]["deps"]["depends_on"] == ["epic-00201"]
            assert nodes["iss-00301"]["deps"]["blockers_top"] == ["epic-00201"]

    def test_sync_deps_ignores_parent_github_closed_for_done(self) -> None:
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
                    {"number": 101, "state": "CLOSED", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "CLOSED", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr

            index = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            nodes = index["nodes"]
            assert nodes["epic-00201"]["progress"] == {"total": 2, "done": 0, "open": 2, "unknown": 0}
            assert nodes["init-00101"]["progress"] == {"total": 2, "done": 0, "open": 2, "unknown": 0}
            assert not nodes["iss-00302"]["deps"]["ready"]
            assert nodes["iss-00302"]["deps"]["depends_on"] == ["iss-00301"]

    def test_sync_deps_active_leaf_makes_epic_and_initiative_doing(self) -> None:
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
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Active issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Sibling issue"],
            )
            self._run_runtime(target, ["active", "set", "iss-00301", "--force"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Active", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Sibling", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr

            deps_issues = json.loads((target / "spec-dock" / ".agent" / "deps-issues.json").read_text(encoding="utf-8"))
            nodes = deps_issues["nodes"]
            assert nodes["iss-00301"]["state"] == "doing"
            assert nodes["iss-00302"]["state"] == "ready"

    def test_sync_deps_active_epic_makes_initiative_doing(self) -> None:
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
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Child issue"],
            )
            self._run_runtime(target, ["active", "set", "epic-00201", "--force"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Child", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr

            deps_issues = json.loads((target / "spec-dock" / ".agent" / "deps-issues.json").read_text(encoding="utf-8"))
            nodes = deps_issues["nodes"]
            assert nodes["iss-00301"]["state"] == "ready"

    def test_deps_check_no_deps_is_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
            )

            p = self._run_runtime_capture(target, ["deps", "check", local_ids["iss-00301"]])
            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok (deps check)" in p.stdout
            assert "ready=true" in p.stdout

    def test_deps_check_accepts_explicit_id_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
            )

            p = self._run_runtime_capture(
                target, ["deps", "check", "--id", local_ids["iss-00301"], "--json"]
            )
            assert p.returncode == 0, p.stdout + p.stderr
            assert f'"target": "{local_ids["iss-00301"]}"' in p.stdout

    def test_deps_check_accepts_explicit_github_issue_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123)

            p = self._run_runtime_capture(target, ["deps", "check", "--github-issue", "123", "--json"])
            assert p.returncode in (0, 3), p.stdout + p.stderr
            assert '"target": "iss-00123"' in p.stdout

    def test_deps_check_github_issue_flag_is_ambiguous_with_current_foreign_overlap_but_id_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123, issue_title="Current issue")
            self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Foreign mirror", "--github-issue", "124"])

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

            ambiguous = self._run_runtime_capture(target, ["deps", "check", "--github-issue", "123"])
            assert ambiguous.returncode != 0, ambiguous.stdout + ambiguous.stderr
            assert "Ambiguous github.issue_number=123" in ambiguous.stderr

            by_id = self._run_runtime_capture(target, ["deps", "check", "--id", "iss-00123", "--json"])
            assert by_id.returncode in (0, 3), by_id.stdout + by_id.stderr
            assert '"target": "iss-00123"' in by_id.stdout

    def test_deps_check_repo_scoped_url_resolves_exact_match_when_number_is_ambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123, issue_title="Current issue")
            self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Foreign mirror", "--github-issue", "124"])

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

            ambiguous = self._run_runtime_capture(target, ["deps", "check", "123"])
            assert ambiguous.returncode != 0, ambiguous.stdout + ambiguous.stderr
            assert "Ambiguous github.issue_number=123" in ambiguous.stderr

            by_url = self._run_runtime_capture(target, ["deps", "check", "https://github.com/other/repo/issues/123", "--json"])
            assert by_url.returncode in (0, 3), by_url.stdout + by_url.stderr
            assert '"target": "iss-00124"' in by_url.stdout

    def test_deps_check_repo_scoped_url_fails_closed_when_repo_scope_does_not_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123, issue_title="Current issue")

            mismatch = self._run_runtime_capture(target, ["deps", "check", "https://github.com/other/repo/issues/123"])
            assert mismatch.returncode == 1, mismatch.stdout + mismatch.stderr
            assert "No node found for github.issue_number=123 in repo scope (other/repo)" in mismatch.stderr
            assert "spec-dock: ok (deps check)" not in mismatch.stdout

    def test_deps_check_repo_scoped_current_url_resolves_unscoped_current_node(self) -> None:
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
            self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Foreign mirror", "--github-issue", "124"])

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
                ["deps", "check", "https://github.com/current/repo/issues/123", "--json"],
            )
            assert by_url.returncode in (0, 3), by_url.stdout + by_url.stderr
            assert '"target": "iss-00123"' in by_url.stdout

    def test_deps_numeric_ref_prefers_current_repo_scope_when_foreign_same_number_exists(self) -> None:
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                issue_issue_number=123,
                issue_title="Current blocker",
            )
            self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Foreign mirror", "--github-issue", "125"])
            self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Target issue", "--github-issue", "124"])

            foreign_issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00125-foreign-mirror"
                / ".meta.json"
            )
            foreign_meta = json.loads(foreign_issue_meta.read_text(encoding="utf-8"))
            foreign_meta["github"] = {"issue_number": 123, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(foreign_issue_meta, foreign_meta)

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00124-target-issue"
            )
            self._set_meta_depends_on(target_issue_dir, [123])

            p = self._run_runtime_capture(target, ["deps", "check", "--id", "iss-00124", "--json"])
            assert p.returncode == 3, p.stdout + p.stderr
            data = json.loads(p.stdout)
            assert data["target"] == "iss-00124"
            assert data["effective_depends_on"] == ["iss-00123"]

    def test_deps_numeric_ref_rejects_foreign_only_match_when_current_repo_known(self) -> None:
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=124, issue_title="Target issue")
            self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Foreign mirror", "--github-issue", "125"])

            foreign_issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00125-foreign-mirror"
                / ".meta.json"
            )
            foreign_meta = json.loads(foreign_issue_meta.read_text(encoding="utf-8"))
            foreign_meta["github"] = {"issue_number": 123, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(foreign_issue_meta, foreign_meta)

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00124-target-issue"
            )
            self._set_meta_depends_on(target_issue_dir, [123])

            p = self._run_runtime_capture(target, ["deps", "check", "--id", "iss-00124"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert "No node found for github.issue_number=123 in current repo scope (example/repo)" in p.stderr
            assert "Create/link the node first." in p.stderr

    def test_deps_numeric_ref_fail_closed_when_scope_mixed_and_current_repo_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123, issue_title="Current blocker")
            self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Foreign mirror", "--github-issue", "125"])
            self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Target issue", "--github-issue", "124"])
            self._drop_github_repo_scope(
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-current-blocker"
            )
            self._run_git(target, ["remote", "remove", "origin"])

            foreign_issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00125-foreign-mirror"
                / ".meta.json"
            )
            foreign_meta = json.loads(foreign_issue_meta.read_text(encoding="utf-8"))
            foreign_meta["github"] = {"issue_number": 123, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(foreign_issue_meta, foreign_meta)

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00124-target-issue"
            )
            self._set_meta_depends_on(target_issue_dir, [123])

            p = self._run_runtime_capture(target, ["deps", "check", "--id", "iss-00124"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert "Ambiguous github.issue_number=123" in p.stderr
            assert "fail-closed" in p.stderr

    @pytest.mark.parametrize(
        "ref",
        (
            "other/repo#123",
            "https://github.com/other/repo/issues/123",
        ),
        ids=("owner-repo-number", "github-url"),
    )
    def test_deps_scoped_ref_forms_resolve_exact_repo_match(self, ref: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=123, issue_title="Current blocker")
            self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Foreign mirror", "--github-issue", "125"])
            self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Target issue", "--github-issue", "124"])

            foreign_issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00125-foreign-mirror"
                / ".meta.json"
            )
            foreign_meta = json.loads(foreign_issue_meta.read_text(encoding="utf-8"))
            foreign_meta["github"] = {"issue_number": 123, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(foreign_issue_meta, foreign_meta)

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00124-target-issue"
            )
            self._set_meta_depends_on(target_issue_dir, [ref])
            p = self._run_runtime_capture(target, ["deps", "check", "--id", "iss-00124", "--json"])
            assert p.returncode == 3, p.stdout + p.stderr
            data = json.loads(p.stdout)
            assert data["target"] == "iss-00124"
            assert data["effective_depends_on"] == ["iss-00125"]

    @pytest.mark.parametrize(
        "ref",
        (
            "missing/repo#123",
            "https://github.com/missing/repo/issues/123",
        ),
        ids=("owner-repo-number", "github-url"),
    )
    def test_deps_scoped_ref_forms_fail_closed_when_repo_scope_does_not_match(self, ref: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=124, issue_title="Target issue")
            self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Foreign mirror", "--github-issue", "125"])

            foreign_issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00125-foreign-mirror"
                / ".meta.json"
            )
            foreign_meta = json.loads(foreign_issue_meta.read_text(encoding="utf-8"))
            foreign_meta["github"] = {"issue_number": 123, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(foreign_issue_meta, foreign_meta)

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00124-target-issue"
            )
            self._set_meta_depends_on(target_issue_dir, [ref])
            p = self._run_runtime_capture(target, ["deps", "check", "--id", "iss-00124"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert "Unresolved dependency ref:" in p.stderr
            assert "No node found for github.issue_number=123 in repo scope (missing/repo)" in p.stderr

    @pytest.mark.parametrize(
        "ref",
        (
            "current/repo#123",
            "https://github.com/current/repo/issues/123",
        ),
        ids=("owner-repo-number", "github-url"),
    )
    def test_deps_scoped_ref_forms_resolve_current_repo_scope_to_unscoped_current_node(self, ref: str) -> None:
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
                issue_title="Current blocker",
            )
            self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Foreign mirror", "--github-issue", "125"])
            self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Target issue", "--github-issue", "124"])
            self._drop_github_repo_scope(
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-current-blocker"
            )

            foreign_issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00125-foreign-mirror"
                / ".meta.json"
            )
            foreign_meta = json.loads(foreign_issue_meta.read_text(encoding="utf-8"))
            foreign_meta["github"] = {"issue_number": 123, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(foreign_issue_meta, foreign_meta)

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00124-target-issue"
            )
            self._set_meta_depends_on(target_issue_dir, [ref])
            p = self._run_runtime_capture(target, ["deps", "check", "--id", "iss-00124", "--json"])
            assert p.returncode == 3, p.stdout + p.stderr
            data = json.loads(p.stdout)
            assert data["target"] == "iss-00124"
            assert data["effective_depends_on"] == ["iss-00123"]

    def test_deps_check_rejects_conflict_between_positional_target_and_id_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            p = self._run_runtime_capture(target, ["deps", "check", "123", "--id", "iss-local-00001"])
            assert p.returncode != 0, p.stdout + p.stderr
            assert "choose exactly one" in p.stderr

    def test_deps_check_rejects_non_positive_github_issue_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            p = self._run_runtime_capture(target, ["deps", "check", "--github-issue", "0"])
            assert p.returncode != 0, p.stdout + p.stderr
            assert "positive integer" in p.stderr

    def test_deps_check_returns_ready_and_blockers_and_closure_json(self) -> None:
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
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "402", "--title", "Done issue"],
            )
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "203", "--title", "Transitive epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "203", "--github-issue", "403", "--title", "Transitive blocker"],
            )

            main_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-main-epic"
                / "issues"
                / "iss-00301-target-issue"
            )
            self._set_meta_depends_on(main_issue_dir, ["epic-00202"])
            blocker_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00202-deps-epic"
                / "issues"
                / "iss-00401-open-blocker"
            )
            self._set_meta_depends_on(blocker_issue_dir, [403])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Main epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 202, "state": "OPEN", "title": "Deps epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 203, "state": "OPEN", "title": "Trans epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 401, "state": "OPEN", "title": "Blocker", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 402, "state": "CLOSED", "title": "Done", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 403, "state": "OPEN", "title": "Transitive", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00301", "--github", "--json"], env=test_env)
            assert p.returncode == 3, p.stdout + p.stderr
            data = json.loads(p.stdout)
            assert list(data.keys()) == [
                    "schema_version",
                    "target",
                    "target_status",
                    "ready",
                    "effective_depends_on",
                    "blockers",
                    "issue_blockers",
                    "node_blockers",
                    "satisfied_dependencies",
                    "dependency_contexts",
                    "nodes",
                    "warnings",
                ]
            assert data["schema_version"] == 2
            assert data["target"] == "iss-00301"
            assert not data["ready"]
            assert data["effective_depends_on"] == ["iss-00401", "iss-00403"]
            assert data["blockers"] == ["iss-00401", "iss-00403"]
            assert data["issue_blockers"] == ["iss-00401", "iss-00403"]
            assert data["node_blockers"] == []
            assert data["satisfied_dependencies"] == []
            assert data["dependency_contexts"] == [
                {
                    "source_node_id": "iss-00301",
                    "source_issue_id": "iss-00301",
                    "target_node_id": "epic-00202",
                    "target_node_kind": "epic",
                    "target_issue_ids": ["iss-00401", "iss-00402"],
                    "expansion": "expanded",
                    "lifecycle_state": "open",
                    "lifecycle_source": "github",
                    "dependency_disposition": "blocking",
                    "disposition_basis": "descendant_issue_open",
                }
            ]
            assert data["warnings"] == []

    def test_deps_check_json_reports_empty_open_epic_as_node_blocker(self) -> None:
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
                ["new", "epic", "--initiative", "101", "--github-issue", "202", "--title", "Empty blocker"],
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
                    {"number": 201, "state": "OPEN", "title": "Main epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 202, "state": "OPEN", "title": "Empty blocker", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00301", "--github", "--json"], env=test_env)
            assert p.returncode == 3, p.stdout + p.stderr
            data = json.loads(p.stdout)
            assert data["schema_version"] == 2
            assert not data["ready"]
            assert data["blockers"] == ["epic-00202"]
            assert data["issue_blockers"] == []
            assert data["node_blockers"] == [
                {
                    "node_id": "epic-00202",
                    "reason": "empty_open",
                    "state": "open",
                    "state_source": "github",
                    "source_issue_id": "iss-00301",
                    "lifecycle_state": "open",
                    "lifecycle_source": "github",
                    "dependency_disposition": "blocking",
                    "disposition_basis": "empty_open_container",
                }
            ]

    def test_deps_check_json_exits_zero_for_empty_closed_epic_context(self) -> None:
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
                ["new", "epic", "--initiative", "101", "--github-issue", "202", "--title", "Closed dependency"],
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
                    {"number": 201, "state": "OPEN", "title": "Main epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 202, "state": "CLOSED", "title": "Closed dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00301", "--github", "--json"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr
            data = json.loads(p.stdout)
            assert data["schema_version"] == 2
            assert data["ready"]
            assert data["blockers"] == []
            assert data["node_blockers"] == []
            assert data["satisfied_dependencies"] == [
                {
                    "source_node_id": "iss-00301",
                    "source_issue_id": "iss-00301",
                    "target_node_id": "epic-00202",
                    "target_node_kind": "epic",
                    "target_issue_ids": [],
                    "expansion": "empty",
                    "lifecycle_state": "closed",
                    "lifecycle_source": "github",
                    "dependency_disposition": "satisfied",
                    "disposition_basis": "lifecycle_closed",
                }
            ]

    @pytest.mark.skip(reason="S04: covered by TestCheckDepsApplication.test_no_github_uses_cached_status_and_last_sync_without_fetching_github")
    def test_deps_check_without_github_uses_index_snapshot_when_present(self) -> None:
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
                    {"number": 301, "state": "CLOSED", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p_sync = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            assert p_sync.returncode == 0, p_sync.stdout + p_sync.stderr

            index_all_path = target / "spec-dock" / ".agent" / "index-all.json"
            index_todo_path = target / "spec-dock" / ".agent" / "index.json"
            index_all = json.loads(index_all_path.read_text(encoding="utf-8"))
            index_todo = json.loads(index_todo_path.read_text(encoding="utf-8"))
            shadow = dict(index_all["nodes"]["iss-00301"])
            shadow["status"] = "open"
            index_todo["nodes"]["iss-00301"] = shadow
            index_todo_path.write_text(json.dumps(index_todo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            guard_log = bin_dir / "gh-guard.log"
            guard_log.unlink(missing_ok=True)
            self._make_gh_issue_list_stub(bin_dir, issues=[], fail=True, log_path=guard_log)

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--no-github", "--json"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr
            assert not guard_log.exists(), "gh must not be invoked with --no-github"
            data = json.loads(p.stdout)
            assert data["ready"]
            assert data["blockers"] == []
            assert data["nodes"]["iss-00301"]["state"] == "done"
            assert data["target_status"]["source"] == "cache"
            assert data["target_status"]["stale"]
            assert data["target_status"]["last_sync_at"] == "t"
            assert data["nodes"]["iss-00302"]["source"] == "cache"

    @pytest.mark.skip(reason="S04: covered by TestCheckDepsApplication.test_no_github_missing_cache_defaults_to_unknown_and_blocks")
    def test_deps_check_no_github_falls_back_to_unknown_when_snapshot_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)

            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
                issue_title="Dep issue",
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
            self._set_meta_depends_on(issue_dir, ["iss-00301"])

            (target / "spec-dock" / ".agent" / "index-all.json").unlink(missing_ok=True)
            (target / "spec-dock" / ".agent" / "index.json").unlink(missing_ok=True)

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--no-github", "--json"])
            assert p.returncode == 3, p.stdout + p.stderr
            data = json.loads(p.stdout)
            assert not data["ready"]
            assert data["blockers"] == ["iss-00301"]
            assert data["nodes"]["iss-00301"]["state"] == "unknown"
            assert data["nodes"]["iss-00301"]["source"] == "cache"
            assert data["target_status"]["source"] == "cache"
            assert data["target_status"]["stale"]
            assert data["target_status"]["last_sync_at"] is None

    def test_deps_check_missing_target_reports_runtime_target_requirement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            p = self._run_runtime_capture(target, ["deps", "check"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert "target is required" in p.stderr

    @pytest.mark.parametrize(
        "form",
        (
            "301",
            "#301",
            "https://github.com/example/repo/issues/301",
        ),
        ids=("number", "hash-number", "github-url"),
    )
    def test_deps_check_accepts_github_number_forms_and_urls(self, form: str) -> None:
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
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Add refresh token"],
            )
            issue_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00301-add-refresh-token"
                / ".meta.json"
            )
            issue_meta = json.loads(issue_meta_path.read_text(encoding="utf-8"))
            issue_meta["github"] = {"issue_number": 301, "repo_owner": "example", "repo_name": "repo"}
            self._write_json_force(issue_meta_path, issue_meta)

            p = self._run_runtime_capture(target, ["deps", "check", form, "--json"])
            assert p.returncode == 0, p.stdout + p.stderr
            data = json.loads(p.stdout)
            assert data["target"] == "iss-00301"
            assert data["ready"]

    @pytest.mark.skip(reason="S04: covered by TestCheckDepsApplication.test_github_snapshots_drive_ready_and_blocked_states_without_cli")
    def test_deps_check_default_github_ready_when_deps_closed(self) -> None:
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
                    {"number": 301, "state": "CLOSED", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--json"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr
            data = json.loads(p.stdout)
            assert data["ready"]
            assert data["effective_depends_on"] == []
            assert data["blockers"] == []
            assert data["nodes"]["iss-00301"]["state"] == "done"

    @pytest.mark.skip(reason="S04: covered by TestCheckDepsApplication.test_no_github_uses_cached_status_and_last_sync_without_fetching_github")
    def test_deps_check_no_github_uses_synced_index_status(self) -> None:
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
                    {"number": 301, "state": "CLOSED", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p_sync = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            assert p_sync.returncode == 0, p_sync.stdout + p_sync.stderr

            # Guard: `deps check --no-github` must not fetch GitHub.
            guard_log = bin_dir / "gh-guard.log"
            guard_log.unlink(missing_ok=True)
            self._make_gh_issue_list_stub(bin_dir, issues=[], fail=True, log_path=guard_log)

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--no-github", "--json"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr
            assert not guard_log.exists(), "gh must not be invoked with --no-github"
            data = json.loads(p.stdout)
            assert data["ready"]
            assert data["blockers"] == []
            assert data["nodes"]["iss-00301"]["state"] == "done"

    @pytest.mark.skip(reason="S04: covered by TestCheckDepsApplication.test_no_github_missing_cache_defaults_to_unknown_and_blocks")
    def test_deps_check_no_github_missing_index_defaults_unknown(self) -> None:
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

            (target / "spec-dock" / ".agent" / "index-all.json").unlink(missing_ok=True)
            (target / "spec-dock" / ".agent" / "index.json").unlink(missing_ok=True)

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--no-github", "--json"])
            assert p.returncode == 3, p.stdout + p.stderr
            data = json.loads(p.stdout)
            assert not data["ready"]
            assert data["blockers"] == ["iss-00301"]
            assert data["nodes"]["iss-00301"]["state"] == "unknown"

    @pytest.mark.skip(reason="S04: covered by TestCheckDepsApplication.test_github_snapshots_drive_ready_and_blocked_states_without_cli")
    def test_deps_check_github_blocked_when_dep_open(self) -> None:
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

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--github", "--json"], env=test_env)
            assert p.returncode == 3, p.stdout + p.stderr
            data = json.loads(p.stdout)
            assert not data["ready"]
            assert data["effective_depends_on"] == ["iss-00301"]
            assert data["blockers"] == ["iss-00301"]

    @pytest.mark.skip(reason="S04: covered by TestCheckDepsApplication.test_github_index_incomplete_warns_and_leaves_missing_dependency_unknown")
    def test_deps_check_github_index_incomplete_warns_and_blocks(self) -> None:
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
            # Missing 301 on purpose.
            self._make_gh_issue_list_and_view_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--github", "--json"], env=test_env)
            assert p.returncode == 3, p.stdout + p.stderr
            assert p.stderr.strip() == ""
            data = json.loads(p.stdout)
            assert "gh_fetch_failed" in data["warnings"]
            assert data["blockers"] == ["iss-00301"]

    @pytest.mark.skip(reason="S04: covered by TestCheckDepsApplication.test_github_fetch_failure_warns_and_blocks_on_unknown_dependency")
    def test_deps_check_github_fetch_failure_warns_and_blocks(self) -> None:
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
            self._make_gh_issue_list_stub(bin_dir, issues=[], fail=True)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--github", "--json"], env=test_env)
            assert p.returncode == 3, p.stdout + p.stderr
            assert p.stderr.strip() == ""
            data = json.loads(p.stdout)
            assert "gh_fetch_failed" in data["warnings"]
            assert data["blockers"] == ["iss-00301"]

    def test_deps_check_json_stdout_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
            )

            p = self._run_runtime_capture(target, ["deps", "check", local_ids["iss-00301"], "--json"])
            assert p.returncode == 0, p.stdout + p.stderr
            data = json.loads(p.stdout)  # must be valid JSON
            assert data["ready"]
            assert data["target_status"]["source"] == "local"
            assert p.stderr.strip() == ""

    def test_deps_check_missing_meta_depends_on_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
            )
            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
            )
            self._set_meta_depends_on(issue_dir, ["iss-local-99999"])
            issue_meta_path = issue_dir / ".meta.json"
            issue_meta = json.loads(issue_meta_path.read_text(encoding="utf-8"))
            issue_meta.pop("depends_on", None)
            self._write_json_force(issue_meta_path, issue_meta)

            p = self._run_runtime_capture(target, ["deps", "check", local_ids["iss-00301"], "--json"])
            assert p.returncode == 0, p.stdout + p.stderr
            data = json.loads(p.stdout)
            assert data["ready"]
            assert data["effective_depends_on"] == []

    def test_deps_check_missing_meta_depends_on_ignores_stale_legacy_deps_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
            )
            issue_meta_path = issue_dir / ".meta.json"
            issue_meta = json.loads(issue_meta_path.read_text(encoding="utf-8"))
            issue_meta.pop("depends_on", None)
            self._write_json_force(issue_meta_path, issue_meta)

            # Legacy stale file must not be used as a fallback source.
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-99999"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", local_ids["iss-00301"], "--json"])
            assert p.returncode == 0, p.stdout + p.stderr
            data = json.loads(p.stdout)
            assert data["ready"]
            assert data["effective_depends_on"] == []

    def test_materialize_local_compat_ids_assigns_authentic_per_kind_local_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issues=((301, "Issue one"), (407, "Issue two")),
            )

            assert local_ids == {
                    "init-00101": "init-local-00001",
                    "epic-00201": "epic-local-00001",
                    "iss-00301": "iss-local-00001",
                    "iss-00407": "iss-local-00002",
                }

            spec_root = target / "spec-dock" / "initiatives"
            init_dir = spec_root / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            issue_dir = epic_dir / "issues" / "iss-local-00002-issue-two"
            assert init_dir.is_dir()
            assert epic_dir.is_dir()
            assert issue_dir.is_dir()
            assert not (spec_root / "init-00101-auth-platform").exists()
            assert not (epic_dir.parent / "epic-00201-jwt-auth").exists()
            assert not (issue_dir.parent / "iss-00407-issue-two").exists()

            issue_meta = json.loads((issue_dir / ".meta.json").read_text(encoding="utf-8"))
            assert issue_meta["id"] == "iss-local-00002"
            assert issue_meta["epic_id"] == "epic-local-00001"
            assert issue_meta["initiative_id"] == "init-local-00001"
            assert "github" not in issue_meta

            requirement = (issue_dir / "requirement.md").read_text(encoding="utf-8")
            assert "iss-local-00002" in requirement
            assert "iss-00407" not in requirement

    def test_meta_json_parse_error_fails_with_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
            )
            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00301-add-refresh-token"
            )
            self._write_text_force(issue_dir / ".meta.json", "{\n")  # invalid JSON

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00301"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert ".meta.json" in p.stderr
            assert "Invalid JSON" in p.stderr

    def test_meta_schema_error_fails_with_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
            )
            self._remove_all_github_links(target)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00301-add-refresh-token"
            )
            meta_path = issue_dir / ".meta.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            meta["depends_on"] = {"invalid": "type"}
            self._write_json_force(meta_path, meta)

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00301"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert ".meta.json" in p.stderr
            assert "depends_on must be a list" in p.stderr

    def test_meta_schema_root_non_object_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
            )
            self._remove_all_github_links(target)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00301-add-refresh-token"
            )
            self._write_text_force(issue_dir / ".meta.json", "[]\n")

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00301"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert ".meta.json" in p.stderr
            assert "expected object" in p.stderr

    def test_meta_schema_rejects_object_dep_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
            )
            self._remove_all_github_links(target)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00301-add-refresh-token"
            )
            self._set_meta_depends_on(issue_dir, [{}])

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00301"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert ".meta.json" in p.stderr
            assert "depends_on[0]" in p.stderr
            assert "must be a string or int" in p.stderr

    def test_meta_schema_rejects_boolean_dep_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
            )
            self._remove_all_github_links(target)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00301-add-refresh-token"
            )
            meta_path = issue_dir / ".meta.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            meta["depends_on"] = [True]
            self._write_json_force(meta_path, meta)

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00301"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert ".meta.json" in p.stderr
            assert "depends_on[0]" in p.stderr

    def test_meta_schema_version_must_be_1(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
            )
            self._remove_all_github_links(target)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00301-add-refresh-token"
            )
            self._set_meta_depends_on(issue_dir, [])
            self._set_meta_schema_version(issue_dir, 2)

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00301"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert ".meta.json" in p.stderr
            assert "schema_version must be 1" in p.stderr

    def test_meta_schema_version_missing_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
            )
            self._remove_all_github_links(target)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00301-add-refresh-token"
            )
            self._set_meta_depends_on(issue_dir, [])
            issue_meta_path = issue_dir / ".meta.json"
            issue_meta = json.loads(issue_meta_path.read_text(encoding="utf-8"))
            issue_meta.pop("schema_version", None)
            self._write_json_force(issue_meta_path, issue_meta)

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00301"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert ".meta.json" in p.stderr
            assert "schema_version must be 1" in p.stderr

    def test_meta_schema_version_rejects_boolean_true(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
            )
            self._remove_all_github_links(target)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00301-add-refresh-token"
            )
            self._set_meta_depends_on(issue_dir, [])
            issue_meta_path = issue_dir / ".meta.json"
            issue_meta = json.loads(issue_meta_path.read_text(encoding="utf-8"))
            issue_meta["schema_version"] = True
            self._write_json_force(issue_meta_path, issue_meta)

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00301"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert ".meta.json" in p.stderr
            assert "schema_version must be 1" in p.stderr

    def test_deps_unresolved_ref_reports_ref_and_deps_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
                issue_title="Issue one",
            )
            self._remove_all_github_links(target)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00301-issue-one"
            )
            self._set_meta_depends_on(issue_dir, ["iss-99999"])

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00301"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert "iss-99999" in p.stderr
            assert ".meta.json" in p.stderr

    def test_deps_canonicalizes_width_variants(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Issue one"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Issue two"])
            self._remove_all_github_links(target)

            issue_two_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00302-issue-two"
            )
            self._set_meta_depends_on(issue_two_dir, ["iss-301"])

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--json"])
            assert p.returncode == 3, p.stdout + p.stderr
            data = json.loads(p.stdout)
            assert data["effective_depends_on"] == ["iss-00301"]

    def test_deps_github_number_requires_imported_node(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
                issue_title="Issue one",
            )
            self._remove_all_github_links(target)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00301-issue-one"
            )
            self._set_meta_depends_on(issue_dir, [123])

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00301"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert "123" in p.stderr
            assert ".meta.json" in p.stderr

    @pytest.mark.skip(reason="S04: covered by TestCheckDepsApplication.test_effective_depends_on_merges_parents_and_dedups_without_cli")
    def test_deps_effective_depends_on_merges_parents_and_dedups(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Dep one"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Dep two"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "303", "--title", "Target"])
            self._run_runtime(target, ["new", "initiative", "--github-issue", "102", "--title", "External deps"])
            self._run_runtime(target, ["new", "epic", "--initiative", "102", "--github-issue", "202", "--title", "External epic"])
            self._run_runtime(target, ["new", "issue", "--epic", "202", "--github-issue", "401", "--title", "External issue"])
            self._remove_all_github_links(target)

            init_dir = target / "spec-dock" / "initiatives" / "init-00101-auth-platform"
            epic_dir = init_dir / "epics" / "epic-00201-jwt-auth"
            target_issue_dir = epic_dir / "issues" / "iss-00303-target"

            # Parent initiative/epic both depend on the same dep (dedup expected).
            self._set_meta_depends_on(init_dir, ["iss-401"])
            self._set_meta_depends_on(epic_dir, ["iss-00401"])
            self._set_meta_depends_on(target_issue_dir, ["iss-00302"])

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00303", "--json"])
            assert p.returncode == 3, p.stdout + p.stderr
            data = json.loads(p.stdout)
            assert data["effective_depends_on"] == ["iss-00302", "iss-00401"]

    @pytest.mark.skip(reason="S04: covered by TestCheckDepsApplication.test_effective_depends_on_merges_epic_and_initiative_without_cli")
    def test_deps_effective_depends_on_merges_epic_and_initiative(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Dep one"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Dep two"])
            self._run_runtime(target, ["new", "initiative", "--github-issue", "102", "--title", "External deps"])
            self._run_runtime(target, ["new", "epic", "--initiative", "102", "--github-issue", "202", "--title", "External epic"])
            self._run_runtime(target, ["new", "issue", "--epic", "202", "--github-issue", "401", "--title", "External issue one"])
            self._run_runtime(target, ["new", "issue", "--epic", "202", "--github-issue", "402", "--title", "External issue two"])
            self._remove_all_github_links(target)

            init_dir = target / "spec-dock" / "initiatives" / "init-00101-auth-platform"
            epic_dir = init_dir / "epics" / "epic-00201-jwt-auth"

            self._set_meta_depends_on(init_dir, ["iss-00401"])
            self._set_meta_depends_on(epic_dir, ["iss-00402"])

            p = self._run_runtime_capture(target, ["deps", "check", "epic-00201", "--json"])
            assert p.returncode == 3, p.stdout + p.stderr
            data = json.loads(p.stdout)
            assert data["effective_depends_on"] == ["iss-00401", "iss-00402"]

    def test_deps_check_initiative_and_epic_target_status_does_not_fall_back_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issues=((301, "Issue one"),),
            )

            for target_id in (local_ids["init-00101"], local_ids["epic-00201"]):
                case_label = f"target_id={target_id}"
                p_json = self._run_runtime_capture(target, ["deps", "check", target_id, "--json"])
                assert p_json.returncode == 0, f"{case_label}: {p_json.stdout}{p_json.stderr}"
                data = json.loads(p_json.stdout)
                assert data["target"] == target_id, case_label
                assert data["target_status"]["source"] == "local", case_label
                assert data["target_status"]["authority"] == "local", case_label
                assert not data["target_status"]["stale"], case_label

                p_text = self._run_runtime_capture(target, ["deps", "check", target_id])
                assert p_text.returncode == 0, f"{case_label}: {p_text.stdout}{p_text.stderr}"
                assert "source=local" in p_text.stdout, case_label
                assert "stale=false" in p_text.stdout, case_label

    def test_deps_check_initiative_and_epic_target_status_uses_github_when_linked(self) -> None:
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

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {
                        "number": 101,
                        "state": "OPEN",
                        "title": "Initiative",
                        "labels": [],
                        "updatedAt": "2026-03-20T10:00:00Z",
                        "url": "u",
                    },
                    {
                        "number": 201,
                        "state": "OPEN",
                        "title": "Epic",
                        "labels": [],
                        "updatedAt": "2026-03-20T11:00:00Z",
                        "url": "u",
                    },
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            for target_id, expected_last_sync_at in (
                ("init-00101", "2026-03-20T10:00:00Z"),
                ("epic-00201", "2026-03-20T11:00:00Z"),
            ):
                case_label = f"target_id={target_id}, expected_last_sync_at={expected_last_sync_at}"
                p_json = self._run_runtime_capture(
                    target,
                    ["deps", "check", target_id, "--github", "--json"],
                    env=test_env,
                )
                assert p_json.returncode == 0, f"{case_label}: {p_json.stdout}{p_json.stderr}"
                data = json.loads(p_json.stdout)
                assert data["target"] == target_id, case_label
                assert data["target_status"]["authority"] == "github", case_label
                assert data["target_status"]["effective_status"] == "open", case_label
                assert data["target_status"]["source"] == "github", case_label
                assert not data["target_status"]["stale"], case_label
                assert data["target_status"]["last_sync_at"] == expected_last_sync_at, case_label

                p_text = self._run_runtime_capture(target, ["deps", "check", target_id, "--github"], env=test_env)
                assert p_text.returncode == 0, f"{case_label}: {p_text.stdout}{p_text.stderr}"
                assert "source=github" in p_text.stdout, case_label
                assert "stale=false" in p_text.stdout, case_label

    def test_deps_self_dependency_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
                issue_title="Issue one",
            )
            self._remove_all_github_links(target)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00301-issue-one"
            )
            self._set_meta_depends_on(issue_dir, ["iss-00301"])

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00301"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert "iss-00301" in p.stderr
            assert "Raw node dependency self edge detected: iss-00301" in p.stderr

    def test_deps_descendant_dependency_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
                issue_title="Issue one",
            )
            init_dir = target / "spec-dock" / "initiatives" / "init-00101-auth-platform"
            self._set_meta_depends_on(init_dir, ["iss-00301"])

            p = self._run_runtime_capture(target, ["deps", "check", "init-00101"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert "Raw node dependency targets descendant: init-00101 -> iss-00301" in p.stderr
            assert "iss-00301" in p.stderr

    def test_deps_cycle_detected_in_reachable_graph(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Issue one"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Issue two"])
            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
            )
            issue_one_dir = epic_dir / "issues" / "iss-00301-issue-one"
            issue_two_dir = epic_dir / "issues" / "iss-00302-issue-two"

            self._set_meta_depends_on(issue_one_dir, ["iss-00302"])
            self._set_meta_depends_on(issue_two_dir, ["iss-00301"])

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00301"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert "iss-00301" in p.stderr
            assert "iss-00302" in p.stderr
            assert "->" in p.stderr

    def test_deps_check_ignores_unreachable_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Target"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Cycle a"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "303", "--title", "Cycle b"])
            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
            )
            cycle_a_dir = epic_dir / "issues" / "iss-00302-cycle-a"
            cycle_b_dir = epic_dir / "issues" / "iss-00303-cycle-b"
            self._set_meta_depends_on(cycle_a_dir, ["iss-00303"])
            self._set_meta_depends_on(cycle_b_dir, ["iss-00302"])

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00301", "--json"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert "Dependency cycle detected" in p.stderr
            assert "iss-00302" in p.stderr
            assert "iss-00303" in p.stderr

    def test_sync_fails_on_deps_structural_error_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Target"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Cycle a"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "303", "--title", "Cycle b"])
            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
            )
            cycle_a_dir = epic_dir / "issues" / "iss-00302-cycle-a"
            cycle_b_dir = epic_dir / "issues" / "iss-00303-cycle-b"
            self._set_meta_depends_on(cycle_a_dir, ["iss-00303"])
            self._set_meta_depends_on(cycle_b_dir, ["iss-00302"])

            p = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert "iss-00302" in p.stderr
            assert "iss-00303" in p.stderr
            assert "->" in p.stderr

    def test_validate_fails_on_existing_empty_container_raw_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "Empty a"])
            self._run_runtime(target, ["new", "epic", "--initiative", "101", "--github-issue", "202", "--title", "Empty b"])
            init_dir = target / "spec-dock" / "initiatives" / "init-00101-auth-platform"
            epic_a_dir = init_dir / "epics" / "epic-00201-empty-a"
            epic_b_dir = init_dir / "epics" / "epic-00202-empty-b"
            self._set_meta_depends_on(epic_a_dir, ["epic-00202"])
            self._set_meta_depends_on(epic_b_dir, ["epic-00201"])

            p = self._run_runtime_capture(target, ["validate"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert "Dependency cycle detected" in p.stderr
            assert "epic-00201" in p.stderr
            assert "epic-00202" in p.stderr

    def test_sync_fails_on_existing_empty_container_raw_cycle_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "Empty a"])
            self._run_runtime(target, ["new", "epic", "--initiative", "101", "--github-issue", "202", "--title", "Empty b"])
            init_dir = target / "spec-dock" / "initiatives" / "init-00101-auth-platform"
            epic_a_dir = init_dir / "epics" / "epic-00201-empty-a"
            epic_b_dir = init_dir / "epics" / "epic-00202-empty-b"
            self._set_meta_depends_on(epic_a_dir, ["epic-00202"])
            self._set_meta_depends_on(epic_b_dir, ["epic-00201"])

            p = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            assert p.returncode == 1, p.stdout + p.stderr
            assert "Dependency cycle detected" in p.stderr
            assert "epic-00201" in p.stderr
            assert "epic-00202" in p.stderr

    def test_sync_force_sets_deps_valid_false_and_emits_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Target"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Cycle a"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "303", "--title", "Cycle b"])
            agent_dir = target / "spec-dock" / ".agent"
            self._run_runtime(target, ["sync", "--no-github", "--no-update-active"])
            baseline_index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            assert baseline_index["deps"]["valid"]
            assert baseline_index["deps"]["issue_edges"] == []
            assert baseline_index["deps"]["error"] is None

            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
            )
            cycle_a_dir = epic_dir / "issues" / "iss-00302-cycle-a"
            cycle_b_dir = epic_dir / "issues" / "iss-00303-cycle-b"
            self._set_meta_depends_on(cycle_a_dir, ["iss-00303"])
            self._set_meta_depends_on(cycle_b_dir, ["iss-00302"])

            (agent_dir / "index.json").unlink(missing_ok=True)
            (agent_dir / "tree.json").unlink(missing_ok=True)
            deps_raw_puml_path = target / "spec-dock" / "deps-raw.puml"
            deps_raw_puml_path.write_text(
                "@startuml\nrectangle \"stale edge\" as STALE\n@enduml\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active", "--force"])
            assert p.returncode == 0, p.stdout + p.stderr
            assert "deps_preflight_failed" in p.stderr
            assert (agent_dir / "index.json").is_file()
            assert (agent_dir / "tree.json").is_file()
            assert (agent_dir / "index-all.json").is_file()
            assert (agent_dir / "tree-all.json").is_file()

            index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            assert index["projection"] == "current-future"
            assert "source" not in index
            assert not index["deps"]["valid"]
            assert index["deps"]["issue_edges"] == []
            assert "Dependency cycle detected" in str(index["deps"]["error"])
            assert "deps_preflight_failed" in index["warnings"]
            assert index["nodes"]["iss-00301"]["deps"] is None
            assert index["nodes"]["iss-00302"]["deps"] is None
            assert index["nodes"]["iss-00303"]["deps"] is None

            index_all = json.loads((agent_dir / "index-all.json").read_text(encoding="utf-8"))
            assert index_all["projection"] == "full-history"
            assert "source" not in index_all
            assert not index_all["deps"]["valid"]
            assert index_all["deps"]["issue_edges"] == []
            assert "Dependency cycle detected" in str(index_all["deps"]["error"])
            assert "deps_preflight_failed" in index_all["warnings"]
            assert index_all["nodes"]["iss-00301"]["deps"] is None
            assert index_all["nodes"]["iss-00302"]["deps"] is None
            assert index_all["nodes"]["iss-00303"]["deps"] is None

            tree = json.loads((agent_dir / "tree.json").read_text(encoding="utf-8"))
            assert not tree["deps"]["valid"]
            assert tree["deps"]["issue_edges"] == []
            assert "Dependency cycle detected" in str(tree["deps"]["error"])
            assert "deps_preflight_failed" in tree["warnings"]
            tree_issues = tree["tree"][0]["epics"][0]["issues"]
            tree_issue_deps = {issue["id"]: issue.get("deps") for issue in tree_issues}
            assert tree_issue_deps["iss-00301"] is None
            assert tree_issue_deps["iss-00302"] is None
            assert tree_issue_deps["iss-00303"] is None

            tree_all = json.loads((agent_dir / "tree-all.json").read_text(encoding="utf-8"))
            assert not tree_all["deps"]["valid"]
            assert tree_all["deps"]["issue_edges"] == []
            assert "Dependency cycle detected" in str(tree_all["deps"]["error"])
            assert "deps_preflight_failed" in tree_all["warnings"]
            tree_all_issues = tree_all["tree"][0]["epics"][0]["issues"]
            tree_all_issue_deps = {issue["id"]: issue.get("deps") for issue in tree_all_issues}
            assert tree_all_issue_deps["iss-00301"] is None
            assert tree_all_issue_deps["iss-00302"] is None
            assert tree_all_issue_deps["iss-00303"] is None

            deps_issues = json.loads((agent_dir / "deps-issues.json").read_text(encoding="utf-8"))
            assert deps_issues["projection"] == "issue-readiness-with-dependency-context"
            assert deps_issues["source"] == {"sync_state": "readiness_evaluation", "schema_version": 2}
            assert not deps_issues["deps"]["valid"]
            assert "Dependency cycle detected" in str(deps_issues["deps"]["error"])
            assert deps_issues["nodes"] == {}
            assert deps_issues["edges"] == []

            tree_all_puml = (target / "spec-dock" / "tree-all.puml").read_text(encoding="utf-8")
            tree_todo_puml = (target / "spec-dock" / "tree.puml").read_text(encoding="utf-8")
            deps_issues_puml = (target / "spec-dock" / "deps-issues.puml").read_text(encoding="utf-8")
            deps_raw_puml = deps_raw_puml_path.read_text(encoding="utf-8")
            dashboard = (target / "spec-dock" / "dashboard.md").read_text(encoding="utf-8")
            for text in (tree_all_puml, tree_todo_puml, deps_issues_puml, deps_raw_puml, dashboard):
                assert "deps_preflight_failed" in text
                assert "deps.valid=false" in text
                assert "--force" in text
            assert "title deps-raw - DEPS_DISABLED" in deps_raw_puml
            assert "stale edge" not in deps_raw_puml

            assert not (agent_dir / "deps.json").exists()
            assert not (agent_dir / "deps.puml").exists()
            assert not (agent_dir / "deps.todo.puml").exists()

    def test_sync_force_removes_legacy_v1_deps_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
                issue_title="Target",
            )
            agent_dir = target / "spec-dock" / ".agent"
            agent_dir.mkdir(parents=True, exist_ok=True)
            (agent_dir / "deps.json").write_text("{\"stale\": true}\n", encoding="utf-8")
            (agent_dir / "deps.puml").write_text("@startuml\n@enduml\n", encoding="utf-8")
            (agent_dir / "deps.todo.puml").write_text("@startuml\n@enduml\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active", "--force"])
            assert p.returncode == 0, p.stdout + p.stderr

            assert not (agent_dir / "deps.json").exists()
            assert not (agent_dir / "deps.puml").exists()
            assert not (agent_dir / "deps.todo.puml").exists()

    def test_deps_commands_do_not_mutate_meta_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
            )
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00301-add-refresh-token"
                / ".meta.json"
            )
            before = issue_meta.read_text(encoding="utf-8")
            p = self._run_runtime_capture(target, ["deps", "check", "iss-00301", "--json"])
            assert p.returncode in (0, 3), p.stdout + p.stderr
            after = issue_meta.read_text(encoding="utf-8")
            assert after == before

    def test_deps_add_updates_meta_json_and_returns_updated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                issues=((301, "From issue"), (302, "To issue")),
            )
            from_id = local_ids["iss-00301"]
            to_id = local_ids["iss-00302"]

            p = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_id, "--to", to_id],
            )
            assert p.returncode == 0, p.stdout + p.stderr
            assert p.stderr.strip() == ""
            assert p.stdout.strip() == "\n".join(
                    [
                        f"spec-dock: ok (deps add) from={from_id} to={to_id} result=updated",
                        "spec-dock: ok (deps add auto-sync)",
                    ]
                )

            from_meta: dict[str, object] | None = None
            for meta_path in sorted((target / "spec-dock" / "initiatives").glob("**/.meta.json")):
                payload = json.loads(meta_path.read_text(encoding="utf-8"))
                if payload.get("id") == from_id:
                    from_meta = payload
                    break
            assert from_meta is not None
            assert from_meta is not None
            assert from_meta.get("depends_on") == [to_id]

    def test_deps_add_updated_path_auto_syncs_dependency_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            log_path = target / ".gh.log"
            fixture = self._create_deps_auto_sync_fixture(target, log_path=log_path)
            from_id = fixture["from_id"]
            to_id = fixture["to_id"]

            before = self._read_deps_projection_artifacts(target)
            p = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_id, "--to", to_id],
                env=fixture["env"],
            )

            assert p.returncode == 0, p.stdout + p.stderr
            assert "result=updated" in p.stdout
            assert before != self._read_deps_projection_artifacts(target)
            self._assert_deps_projection_has_edge(target, from_id, to_id)
            assert "issue list" in log_path.read_text(encoding="utf-8")

    def test_deps_add_duplicate_returns_unchanged_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                issues=((301, "From issue"), (302, "To issue")),
            )
            from_id = local_ids["iss-00301"]
            to_id = local_ids["iss-00302"]

            first = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_id, "--to", to_id],
            )
            assert first.returncode == 0, first.stdout + first.stderr

            from_meta_path: Path | None = None
            for meta_path in sorted((target / "spec-dock" / "initiatives").glob("**/.meta.json")):
                payload = json.loads(meta_path.read_text(encoding="utf-8"))
                if payload.get("id") == from_id:
                    from_meta_path = meta_path
                    break
            assert from_meta_path is not None
            assert from_meta_path is not None

            before_second = from_meta_path.read_text(encoding="utf-8")
            second = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_id, "--to", to_id],
            )
            assert second.returncode == 0, second.stdout + second.stderr
            assert second.stderr.strip() == ""
            assert second.stdout.strip() == "\n".join(
                    [
                        f"spec-dock: ok (deps add) from={from_id} to={to_id} result=unchanged",
                        "spec-dock: skipped (deps add auto-sync) reason=unchanged",
                    ]
                )

            after_second = from_meta_path.read_text(encoding="utf-8")
            assert after_second == before_second
            from_meta = json.loads(after_second)
            assert from_meta.get("depends_on") == [to_id]

    def test_deps_add_duplicate_skips_post_sync_and_does_not_claim_refresh(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            log_path = target / ".gh.log"
            fixture = self._create_deps_auto_sync_fixture(target, log_path=log_path)
            from_id = fixture["from_id"]
            to_id = fixture["to_id"]

            first = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_id, "--to", to_id],
                env=fixture["env"],
            )
            assert first.returncode == 0, first.stdout + first.stderr
            log_path.write_text("", encoding="utf-8")
            before = self._read_deps_projection_artifacts(target)

            second = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_id, "--to", to_id],
                env=fixture["env"],
            )

            assert second.returncode == 0, second.stdout + second.stderr
            assert "result=unchanged" in second.stdout
            assert "spec-dock: skipped (deps add auto-sync) reason=unchanged" in second.stdout
            assert "refreshed" not in second.stdout + second.stderr
            assert before == self._read_deps_projection_artifacts(target)
            assert log_path.read_text(encoding="utf-8") == ""

    def test_deps_add_duplicate_epic_shorthand_direct_ref_returns_unchanged_without_duplicate_storage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                owner="example",
                repo="repo",
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
                issue_title="Issue A",
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Issue B"],
            )
            self._run_runtime(
                target,
                [
                    "new",
                    "epic",
                    "--initiative",
                    "101",
                    "--github-issue",
                    "202",
                    "--title",
                    "Dependency epic",
                ],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "303", "--title", "Dependency issue"],
            )
            from_id = "epic-00201"
            to_id = "epic-00202"
            from_meta_path = self._find_meta_path_by_id(target, from_id)
            shorthand_refs: list[object] = [
                202,
                "202",
                "example/repo#202",
                "https://github.com/example/repo/issues/202",
            ]

            for shorthand_ref in shorthand_refs:
                case_label = f"shorthand_ref={shorthand_ref!r}"
                self._set_meta_depends_on(from_meta_path.parent, [shorthand_ref])
                before = from_meta_path.read_text(encoding="utf-8")

                p = self._run_runtime_capture(
                    target,
                    ["deps", "add", "--from", from_id, "--to", to_id],
                )

                assert p.returncode == 0, f"{case_label}: {p.stdout}{p.stderr}"
                assert p.stderr.strip() == "", case_label
                assert p.stdout.strip() == "\n".join(
                    [
                        f"spec-dock: ok (deps add) from={from_id} to={to_id} result=unchanged",
                        "spec-dock: skipped (deps add auto-sync) reason=unchanged",
                    ]
                ), case_label
                assert from_meta_path.read_text(encoding="utf-8") == before, case_label
                after = json.loads(from_meta_path.read_text(encoding="utf-8"))
                assert after.get("depends_on") == [shorthand_ref], case_label

    def test_deps_add_inherited_only_edge_adds_direct_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_cross_epic_inherited_dependency_fixture(target)
            from_id = local_ids["iss-00301"]
            to_id = local_ids["iss-00302"]
            from_meta_path = self._find_meta_path_by_id(target, from_id)

            before = json.loads(from_meta_path.read_text(encoding="utf-8"))
            before_refs = before.get("depends_on", [])
            assert not any(str(dep) == to_id for dep in before_refs if isinstance(dep, (str, int)))

            p = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_id, "--to", to_id],
            )
            assert p.returncode == 0, p.stdout + p.stderr
            assert p.stderr.strip() == ""
            assert p.stdout.strip() == "\n".join(
                    [
                        f"spec-dock: ok (deps add) from={from_id} to={to_id} result=updated",
                        "spec-dock: ok (deps add auto-sync)",
                    ]
                )

            after = json.loads(from_meta_path.read_text(encoding="utf-8"))
            assert after.get("depends_on") == [to_id]

    @pytest.mark.parametrize(
        ("from_key", "to_key"),
        (
            ("iss-00301", "epic-00202"),
            ("init-00101", "epic-00202"),
        ),
        ids=("issue-to-unrelated-epic", "initiative-to-unrelated-epic"),
    )
    def test_deps_add_mixed_kind_direct_dependency_updates_meta_json_and_returns_updated(
        self,
        from_key: str,
        to_key: str,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_mixed_node_dependency_fixture(target)
            from_id = local_ids[from_key]
            to_id = local_ids[to_key]
            from_meta_path = self._find_meta_path_by_id(target, from_id)

            p = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_id, "--to", to_id],
            )
            assert p.returncode == 0, p.stdout + p.stderr
            assert p.stderr.strip() == ""
            assert p.stdout.strip() == "\n".join(
                [
                    f"spec-dock: ok (deps add) from={from_id} to={to_id} result=updated",
                    "spec-dock: ok (deps add auto-sync)",
                ]
            )

            after = json.loads(from_meta_path.read_text(encoding="utf-8"))
            assert after.get("depends_on") == [to_id]

    def test_deps_remove_updates_meta_json_and_returns_updated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                issues=((301, "From issue"), (302, "To issue")),
            )
            from_id = local_ids["iss-00301"]
            to_id = local_ids["iss-00302"]

            added = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_id, "--to", to_id],
            )
            assert added.returncode == 0, added.stdout + added.stderr

            removed = self._run_runtime_capture(
                target,
                ["deps", "remove", "--from", from_id, "--to", to_id],
            )
            assert removed.returncode == 0, removed.stdout + removed.stderr
            assert removed.stderr.strip() == ""
            assert removed.stdout.strip() == "\n".join(
                    [
                        f"spec-dock: ok (deps remove) from={from_id} to={to_id} result=updated",
                        "spec-dock: ok (deps remove auto-sync)",
                    ]
                )

            from_meta: dict[str, object] | None = None
            for meta_path in sorted((target / "spec-dock" / "initiatives").glob("**/.meta.json")):
                payload = json.loads(meta_path.read_text(encoding="utf-8"))
                if payload.get("id") == from_id:
                    from_meta = payload
                    break
            assert from_meta is not None
            assert from_meta is not None
            assert from_meta.get("depends_on") == []

    @pytest.mark.parametrize(
        ("from_key", "to_key"),
        (
            ("iss-00301", "epic-00202"),
            ("init-00101", "epic-00202"),
        ),
        ids=("issue-to-unrelated-epic", "initiative-to-unrelated-epic"),
    )
    def test_deps_remove_mixed_kind_direct_dependency_updates_meta_json_and_returns_updated(
        self,
        from_key: str,
        to_key: str,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_mixed_node_dependency_fixture(target)
            from_id = local_ids[from_key]
            to_id = local_ids[to_key]
            from_meta_path = self._find_meta_path_by_id(target, from_id)
            self._set_meta_depends_on(from_meta_path.parent, [to_id])

            p = self._run_runtime_capture(
                target,
                ["deps", "remove", "--from", from_id, "--to", to_id],
            )
            assert p.returncode == 0, p.stdout + p.stderr
            assert p.stderr.strip() == ""
            assert p.stdout.strip() == "\n".join(
                [
                    f"spec-dock: ok (deps remove) from={from_id} to={to_id} result=updated",
                    "spec-dock: ok (deps remove auto-sync)",
                ]
            )

            after = json.loads(from_meta_path.read_text(encoding="utf-8"))
            assert after.get("depends_on") == []

    def test_deps_remove_updated_path_auto_syncs_dependency_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            log_path = target / ".gh.log"
            fixture = self._create_deps_auto_sync_fixture(target, log_path=log_path)
            from_id = fixture["from_id"]
            to_id = fixture["to_id"]
            added = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_id, "--to", to_id],
                env=fixture["env"],
            )
            assert added.returncode == 0, added.stdout + added.stderr
            self._assert_deps_projection_has_edge(target, from_id, to_id)
            log_path.write_text("", encoding="utf-8")
            before = self._read_deps_projection_artifacts(target)

            removed = self._run_runtime_capture(
                target,
                ["deps", "remove", "--from", from_id, "--to", to_id],
                env=fixture["env"],
            )

            assert removed.returncode == 0, removed.stdout + removed.stderr
            assert "result=updated" in removed.stdout
            assert before != self._read_deps_projection_artifacts(target)
            self._assert_deps_projection_lacks_edge(target, from_id, to_id)
            assert "issue list" in log_path.read_text(encoding="utf-8")

    def test_deps_remove_inherited_only_edge_returns_edge_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_cross_epic_inherited_dependency_fixture(target)
            from_id = local_ids["iss-00301"]
            to_id = local_ids["iss-00302"]
            from_meta_path = self._find_meta_path_by_id(target, from_id)
            before = from_meta_path.read_text(encoding="utf-8")

            p = self._run_runtime_capture(
                target,
                ["deps", "remove", "--from", from_id, "--to", to_id],
            )
            assert p.returncode == 1, p.stdout + p.stderr
            assert p.stdout.strip() == ""
            assert "code=edge_not_found" in p.stderr

            after = from_meta_path.read_text(encoding="utf-8")
            assert after == before

    def test_deps_remove_removes_shorthand_direct_refs_by_issue_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                owner="example",
                repo="repo",
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
                issue_title="From issue",
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "To issue"],
            )
            from_id = "iss-00301"
            to_id = "iss-00302"
            from_meta_path = self._find_meta_path_by_id(target, from_id)
            shorthand_refs: list[object] = [
                302,
                "302",
                "example/repo#302",
                "https://github.com/example/repo/issues/302",
            ]

            for shorthand_ref in shorthand_refs:
                case_label = f"shorthand_ref={shorthand_ref!r}"
                self._set_meta_depends_on(from_meta_path.parent, [shorthand_ref])
                p = self._run_runtime_capture(
                    target,
                    ["deps", "remove", "--from", from_id, "--to", to_id],
                )
                assert p.returncode == 0, f"{case_label}: {p.stdout}{p.stderr}"
                assert p.stderr.strip() == "", case_label
                assert p.stdout.strip() == "\n".join(
                        [
                            f"spec-dock: ok (deps remove) from={from_id} to={to_id} result=updated",
                            "spec-dock: ok (deps remove auto-sync)",
                        ]
                    ), case_label
                after = json.loads(from_meta_path.read_text(encoding="utf-8"))
                assert after.get("depends_on") == [], case_label

    def test_deps_remove_removes_shorthand_direct_refs_by_epic_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                owner="example",
                repo="repo",
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
                issue_title="Issue A",
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Issue B"],
            )
            self._run_runtime(
                target,
                [
                    "new",
                    "epic",
                    "--initiative",
                    "101",
                    "--github-issue",
                    "202",
                    "--title",
                    "Dependency epic",
                ],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "303", "--title", "Dependency issue"],
            )
            from_id = "epic-00201"
            to_id = "epic-00202"
            from_meta_path = self._find_meta_path_by_id(target, from_id)
            shorthand_refs: list[object] = [
                202,
                "202",
                "example/repo#202",
                "https://github.com/example/repo/issues/202",
            ]

            for shorthand_ref in shorthand_refs:
                case_label = f"shorthand_ref={shorthand_ref!r}"
                self._set_meta_depends_on(from_meta_path.parent, [shorthand_ref])
                p = self._run_runtime_capture(
                    target,
                    ["deps", "remove", "--from", from_id, "--to", to_id],
                )
                assert p.returncode == 0, f"{case_label}: {p.stdout}{p.stderr}"
                assert p.stderr.strip() == "", case_label
                assert p.stdout.strip() == "\n".join(
                    [
                        f"spec-dock: ok (deps remove) from={from_id} to={to_id} result=updated",
                        "spec-dock: ok (deps remove auto-sync)",
                    ]
                ), case_label
                after = json.loads(from_meta_path.read_text(encoding="utf-8"))
                assert after.get("depends_on") == [], case_label

    def test_deps_add_broken_current_graph_fails_preflight_before_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                issues=((301, "From issue"), (302, "Cycle A"), (303, "Cycle B")),
            )
            from_id = local_ids["iss-00301"]
            to_id = local_ids["iss-00302"]
            cycle_b_id = local_ids["iss-00303"]

            meta_paths_by_id: dict[str, Path] = {}
            for meta_path in sorted((target / "spec-dock" / "initiatives").glob("**/.meta.json")):
                payload = json.loads(meta_path.read_text(encoding="utf-8"))
                node_id = payload.get("id")
                if isinstance(node_id, str):
                    meta_paths_by_id[node_id] = meta_path

            self._set_meta_depends_on(meta_paths_by_id[from_id].parent, [to_id])
            self._set_meta_depends_on(meta_paths_by_id[to_id].parent, [cycle_b_id])
            self._set_meta_depends_on(meta_paths_by_id[cycle_b_id].parent, [to_id])

            before = meta_paths_by_id[from_id].read_text(encoding="utf-8")
            p = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_id, "--to", to_id],
            )
            assert p.returncode == 1, p.stdout + p.stderr
            assert p.stdout.strip() == ""
            assert "preflight validate failed" in p.stderr
            assert "Dependency cycle detected" in p.stderr
            assert "result=unchanged" not in p.stderr
            assert "result=unchanged" not in p.stdout

            after = meta_paths_by_id[from_id].read_text(encoding="utf-8")
            assert after == before

    def test_deps_add_malformed_meta_json_returns_preflight_validate_failed_and_no_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                issues=((301, "From issue"), (302, "Broken issue")),
            )
            from_id = local_ids["iss-00301"]
            to_id = local_ids["iss-00302"]

            from_meta_path = self._find_meta_path_by_id(target, from_id)
            broken_meta_path = self._find_meta_path_by_id(target, to_id)
            before = from_meta_path.read_text(encoding="utf-8")
            self._write_text_force(broken_meta_path, "{\n")

            p = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_id, "--to", to_id],
            )
            assert p.returncode == 1, p.stdout + p.stderr
            assert p.stdout.strip() == ""
            assert "code=preflight_validate_failed" in p.stderr
            assert "Invalid JSON" in p.stderr

            after = from_meta_path.read_text(encoding="utf-8")
            assert after == before

    def test_deps_add_invalid_depends_on_schema_returns_preflight_validate_failed_and_no_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                issues=((301, "From issue"), (302, "Broken issue")),
            )
            from_id = local_ids["iss-00301"]
            to_id = local_ids["iss-00302"]

            from_meta_path = self._find_meta_path_by_id(target, from_id)
            broken_meta_path = self._find_meta_path_by_id(target, to_id)
            before = from_meta_path.read_text(encoding="utf-8")
            self._set_meta_depends_on(broken_meta_path.parent, {"invalid": "type"})

            p = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_id, "--to", to_id],
            )
            assert p.returncode == 1, p.stdout + p.stderr
            assert p.stdout.strip() == ""
            assert "code=preflight_validate_failed" in p.stderr
            assert "depends_on must be a list" in p.stderr

            after = from_meta_path.read_text(encoding="utf-8")
            assert after == before

    def test_deps_remove_not_found_returns_edge_not_found_and_no_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                issues=((301, "From issue"), (302, "To issue")),
            )
            from_id = local_ids["iss-00301"]
            to_id = local_ids["iss-00302"]
            from_meta_path = self._find_meta_path_by_id(target, from_id)
            before = from_meta_path.read_text(encoding="utf-8")

            p = self._run_runtime_capture(
                target,
                ["deps", "remove", "--from", from_id, "--to", to_id],
            )
            assert p.returncode == 1, p.stdout + p.stderr
            assert p.stdout.strip() == ""
            assert "code=edge_not_found" in p.stderr

            after = from_meta_path.read_text(encoding="utf-8")
            assert after == before

    def test_deps_remove_epic_direct_dependency_updates_meta_json_and_returns_updated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
                issue_title="Issue A",
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Issue B"],
            )
            from_id = "epic-00201"
            self._run_runtime(
                target,
                [
                    "new",
                    "epic",
                    "--initiative",
                    "101",
                    "--github-issue",
                    "202",
                    "--title",
                    "Dependency epic",
                ],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "303", "--title", "Dependency issue"],
            )
            to_id = "epic-00202"
            from_meta_path = self._find_meta_path_by_id(target, from_id)
            self._set_meta_depends_on(from_meta_path.parent, [to_id])

            p = self._run_runtime_capture(
                target,
                ["deps", "remove", "--from", from_id, "--to", to_id],
            )
            assert p.returncode == 0, p.stdout + p.stderr
            assert p.stderr.strip() == ""
            assert p.stdout.strip() == "\n".join(
                    [
                        f"spec-dock: ok (deps remove) from={from_id} to={to_id} result=updated",
                        "spec-dock: ok (deps remove auto-sync)",
                    ]
                )

            after = json.loads(from_meta_path.read_text(encoding="utf-8"))
            assert after.get("depends_on") == []

    def test_deps_remove_initiative_direct_dependency_updates_meta_json_and_returns_updated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
                issue_title="Issue A",
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Issue B"],
            )
            from_id = "init-00101"
            self._run_runtime(
                target,
                [
                    "new",
                    "initiative",
                    "--github-issue",
                    "102",
                    "--title",
                    "Dependency initiative",
                ],
            )
            to_id = "init-00102"
            from_meta_path = self._find_meta_path_by_id(target, from_id)
            self._set_meta_depends_on(from_meta_path.parent, [to_id])

            p = self._run_runtime_capture(
                target,
                ["deps", "remove", "--from", from_id, "--to", to_id],
            )
            assert p.returncode == 0, p.stdout + p.stderr
            assert p.stderr.strip() == ""
            assert p.stdout.strip() == "\n".join(
                    [
                        f"spec-dock: ok (deps remove) from={from_id} to={to_id} result=updated",
                        "spec-dock: ok (deps remove auto-sync)",
                    ]
                )

            after = json.loads(from_meta_path.read_text(encoding="utf-8"))
            assert after.get("depends_on") == []

    def test_deps_remove_unresolved_target_returns_edge_not_found_and_no_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                issues=((301, "From issue"), (302, "To issue")),
            )
            from_id = local_ids["iss-00301"]
            from_meta_path = self._find_meta_path_by_id(target, from_id)
            before = from_meta_path.read_text(encoding="utf-8")

            p = self._run_runtime_capture(
                target,
                ["deps", "remove", "--from", from_id, "--to", "iss-local-99999"],
            )
            assert p.returncode == 1, p.stdout + p.stderr
            assert p.stdout.strip() == ""
            assert "code=edge_not_found" in p.stderr

            after = from_meta_path.read_text(encoding="utf-8")
            assert after == before

    @pytest.mark.parametrize(
        "argv",
        (
            ["deps", "add", "--from", "FROM_ID", "--to", "iss-00999"],
            ["deps", "remove", "--from", "FROM_ID", "--to", "iss-00999"],
        ),
        ids=("add-invalid-target", "remove-invalid-target"),
    )
    def test_deps_invalid_target_does_not_run_post_sync_or_refresh_projection(self, argv: list[str]) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            log_path = target / ".gh.log"
            fixture = self._create_deps_auto_sync_fixture(target, log_path=log_path)
            from_id = fixture["from_id"]
            log_path.write_text("", encoding="utf-8")
            before = self._read_deps_projection_artifacts(target)
            command = [from_id if arg == "FROM_ID" else arg for arg in argv]

            p = self._run_runtime_capture(target, command, env=fixture["env"])

            assert p.returncode == 1, p.stdout + p.stderr
            assert p.stdout.strip() == ""
            assert before == self._read_deps_projection_artifacts(target)
            assert log_path.read_text(encoding="utf-8") == ""

    def test_deps_remove_unresolved_source_returns_edge_not_found_and_no_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                issues=((301, "From issue"), (302, "To issue")),
            )
            to_id = local_ids["iss-00302"]
            to_meta_path = self._find_meta_path_by_id(target, to_id)
            before = to_meta_path.read_text(encoding="utf-8")

            p = self._run_runtime_capture(
                target,
                ["deps", "remove", "--from", "iss-local-99998", "--to", to_id],
            )
            assert p.returncode == 1, p.stdout + p.stderr
            assert p.stdout.strip() == ""
            assert "code=edge_not_found" in p.stderr

            after = to_meta_path.read_text(encoding="utf-8")
            assert after == before

    def test_deps_remove_write_failure_returns_write_failed_and_no_write(self) -> None:
        if os.name != "posix":
            pytest.skip("POSIX permission bits are required for this test")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                issues=((301, "From issue"), (302, "To issue")),
            )
            from_id = local_ids["iss-00301"]
            to_id = local_ids["iss-00302"]

            added = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_id, "--to", to_id],
            )
            assert added.returncode == 0, added.stdout + added.stderr

            from_meta_path = self._find_meta_path_by_id(target, from_id)
            from_issue_dir = from_meta_path.parent
            before = from_meta_path.read_text(encoding="utf-8")
            original_mode = stat.S_IMODE(from_issue_dir.stat().st_mode)
            try:
                from_issue_dir.chmod(0o555)
                removed = self._run_runtime_capture(
                    target,
                    ["deps", "remove", "--from", from_id, "--to", to_id],
                )
            finally:
                from_issue_dir.chmod(original_mode)

            assert removed.returncode == 1, removed.stdout + removed.stderr
            assert removed.stdout.strip() == ""
            assert "code=write_failed" in removed.stderr

            after = from_meta_path.read_text(encoding="utf-8")
            assert after == before
            assert json.loads(after).get("depends_on") == [to_id]

    def test_deps_remove_broken_current_graph_fails_preflight_before_edge_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                issues=((301, "From issue"), (302, "Cycle A"), (303, "Cycle B")),
            )
            from_id = local_ids["iss-00301"]
            to_id = local_ids["iss-00302"]
            cycle_b_id = local_ids["iss-00303"]

            to_meta_path = self._find_meta_path_by_id(target, to_id)
            cycle_b_meta_path = self._find_meta_path_by_id(target, cycle_b_id)
            from_meta_path = self._find_meta_path_by_id(target, from_id)

            self._set_meta_depends_on(to_meta_path.parent, [cycle_b_id])
            self._set_meta_depends_on(cycle_b_meta_path.parent, [to_id])

            before = from_meta_path.read_text(encoding="utf-8")
            p = self._run_runtime_capture(
                target,
                ["deps", "remove", "--from", from_id, "--to", to_id],
            )
            assert p.returncode == 1, p.stdout + p.stderr
            assert p.stdout.strip() == ""
            assert "code=preflight_validate_failed" in p.stderr
            assert "code=edge_not_found" not in p.stderr

            after = from_meta_path.read_text(encoding="utf-8")
            assert after == before

    def test_deps_add_epic_direct_dependency_updates_meta_json_and_returns_updated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
                issue_title="Issue A",
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Issue B"],
            )
            from_id = "epic-00201"
            self._run_runtime(
                target,
                [
                    "new",
                    "epic",
                    "--initiative",
                    "101",
                    "--github-issue",
                    "202",
                    "--title",
                    "Dependency epic",
                ],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "303", "--title", "Dependency issue"],
            )
            to_id = "epic-00202"
            from_meta_path = self._find_meta_path_by_id(target, from_id)

            p = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_id, "--to", to_id],
            )
            assert p.returncode == 0, p.stdout + p.stderr
            assert p.stderr.strip() == ""
            assert p.stdout.strip() == "\n".join(
                    [
                        f"spec-dock: ok (deps add) from={from_id} to={to_id} result=updated",
                        "spec-dock: ok (deps add auto-sync)",
                    ]
                )

            after = json.loads(from_meta_path.read_text(encoding="utf-8"))
            assert after.get("depends_on") == [to_id]

    def test_deps_add_empty_initiative_direct_dependency_updates_meta_json_and_returns_updated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
                issue_title="Issue A",
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Issue B"],
            )
            from_id = "init-00101"
            self._run_runtime(
                target,
                [
                    "new",
                    "initiative",
                    "--github-issue",
                    "102",
                    "--title",
                    "Dependency initiative",
                ],
            )
            to_id = "init-00102"
            from_meta_path = self._find_meta_path_by_id(target, from_id)

            p = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_id, "--to", to_id],
            )
            assert p.returncode == 0, p.stdout + p.stderr
            assert "deps_ref_expanded_to_empty" in p.stderr
            assert p.stdout.strip() == "\n".join(
                    [
                        f"spec-dock: ok (deps add) from={from_id} to={to_id} result=updated",
                        "spec-dock: ok (deps add auto-sync)",
                    ]
                )

            after = json.loads(from_meta_path.read_text(encoding="utf-8"))
            assert after.get("depends_on") == [to_id]

    def test_deps_add_unresolved_target_returns_invalid_add_unresolved_and_no_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                issues=((301, "From issue"), (302, "To issue")),
            )
            from_id = local_ids["iss-00301"]
            from_meta_path = self._find_meta_path_by_id(target, from_id)
            before = from_meta_path.read_text(encoding="utf-8")

            p = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_id, "--to", "iss-local-99999"],
            )
            assert p.returncode == 1, p.stdout + p.stderr
            assert p.stdout.strip() == ""
            assert "code=invalid_add_unresolved" in p.stderr

            after = from_meta_path.read_text(encoding="utf-8")
            assert after == before

    def test_deps_add_unresolved_source_returns_invalid_add_unresolved_and_no_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                issues=((301, "From issue"), (302, "To issue")),
            )
            to_id = local_ids["iss-00302"]
            to_meta_path = self._find_meta_path_by_id(target, to_id)
            before = to_meta_path.read_text(encoding="utf-8")

            p = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", "iss-local-99998", "--to", to_id],
            )
            assert p.returncode == 1, p.stdout + p.stderr
            assert p.stdout.strip() == ""
            assert "code=invalid_add_unresolved" in p.stderr

            after = to_meta_path.read_text(encoding="utf-8")
            assert after == before

    def test_deps_add_self_dependency_returns_invalid_add_self_dependency_and_no_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                issues=((301, "Solo issue"),),
            )
            issue_id = local_ids["iss-00301"]
            issue_meta_path = self._find_meta_path_by_id(target, issue_id)
            before = issue_meta_path.read_text(encoding="utf-8")

            p = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", issue_id, "--to", issue_id],
            )
            assert p.returncode == 1, p.stdout + p.stderr
            assert p.stdout.strip() == ""
            assert "code=invalid_add_self_dependency" in p.stderr

            after = issue_meta_path.read_text(encoding="utf-8")
            assert after == before

    def test_deps_add_cycle_request_returns_invalid_add_cycle_and_no_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                issues=((301, "Issue A"), (302, "Issue B")),
            )
            from_id = local_ids["iss-00301"]
            to_id = local_ids["iss-00302"]
            from_meta_path = self._find_meta_path_by_id(target, from_id)

            first = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", to_id, "--to", from_id],
            )
            assert first.returncode == 0, first.stdout + first.stderr

            before = from_meta_path.read_text(encoding="utf-8")
            second = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_id, "--to", to_id],
            )
            assert second.returncode == 1, second.stdout + second.stderr
            assert second.stdout.strip() == ""
            assert "code=invalid_add_cycle" in second.stderr

            after = from_meta_path.read_text(encoding="utf-8")
            assert after == before

    @pytest.mark.parametrize(
        ("from_key", "to_key", "expected_code", "expected_detail"),
        (
            ("epic-00201", "epic-00201", "invalid_add_self_dependency", "Self dependency is not allowed"),
            ("iss-00301", "epic-00201", "invalid_add_cycle", "targets ancestor/container"),
            ("epic-00201", "iss-00301", "invalid_add_cycle", "targets descendant"),
            ("epic-00201", "init-00101", "invalid_add_cycle", "targets ancestor/container"),
        ),
        ids=("self", "issue-to-parent", "parent-to-child", "epic-to-initiative"),
    )
    def test_deps_add_invalid_node_candidate_returns_invalid_add_cycle_and_no_write(
        self,
        from_key: str,
        to_key: str,
        expected_code: str,
        expected_detail: str,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
                issue_title="Issue A",
            )
            from_meta_path = self._find_meta_path_by_id(target, from_key)
            before = from_meta_path.read_text(encoding="utf-8")

            p = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_key, "--to", to_key],
            )
            assert p.returncode == 1, p.stdout + p.stderr
            assert p.stdout.strip() == ""
            assert f"code={expected_code}" in p.stderr
            assert expected_detail in p.stderr

            after = from_meta_path.read_text(encoding="utf-8")
            assert after == before

    def test_deps_add_empty_epic_raw_cycle_returns_invalid_add_cycle_and_no_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
                issue_title="Issue A",
            )
            self._run_runtime(
                target,
                [
                    "new",
                    "epic",
                    "--initiative",
                    "101",
                    "--github-issue",
                    "202",
                    "--title",
                    "Empty dependency epic",
                ],
            )
            self._run_runtime(
                target,
                [
                    "new",
                    "epic",
                    "--initiative",
                    "101",
                    "--github-issue",
                    "203",
                    "--title",
                    "Another empty dependency epic",
                ],
            )
            first_id = "epic-00202"
            second_id = "epic-00203"
            first_meta_path = self._find_meta_path_by_id(target, first_id)
            second_meta_path = self._find_meta_path_by_id(target, second_id)
            self._set_meta_depends_on(second_meta_path.parent, [first_id])
            before = first_meta_path.read_text(encoding="utf-8")

            p = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", first_id, "--to", second_id],
            )
            assert p.returncode == 1, p.stdout + p.stderr
            assert p.stdout.strip() == ""
            assert "code=invalid_add_cycle" in p.stderr
            assert "Dependency cycle detected" in p.stderr

            after = first_meta_path.read_text(encoding="utf-8")
            assert after == before

    def test_deps_add_candidate_compiled_cycle_returns_invalid_add_cycle_and_no_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=101,
                epic_issue_number=201,
                issue_issue_number=301,
                issue_title="Issue A",
            )
            self._run_runtime(
                target,
                [
                    "new",
                    "epic",
                    "--initiative",
                    "101",
                    "--github-issue",
                    "202",
                    "--title",
                    "Dependency epic",
                ],
            )
            self._run_runtime(
                target,
                [
                    "new",
                    "issue",
                    "--epic",
                    "202",
                    "--github-issue",
                    "302",
                    "--title",
                    "Issue B",
                ],
            )
            from_id = "iss-00301"
            target_epic_id = "epic-00202"
            issue_b_id = "iss-00302"
            from_meta_path = self._find_meta_path_by_id(target, from_id)
            issue_b_meta_path = self._find_meta_path_by_id(target, issue_b_id)
            self._set_meta_depends_on(issue_b_meta_path.parent, [from_id])
            before = from_meta_path.read_text(encoding="utf-8")

            p = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_id, "--to", target_epic_id],
            )
            assert p.returncode == 1, p.stdout + p.stderr
            assert p.stdout.strip() == ""
            assert "code=invalid_add_cycle" in p.stderr
            assert "Dependency cycle detected" in p.stderr

            after = from_meta_path.read_text(encoding="utf-8")
            assert after == before

    def test_deps_add_missing_required_flag_returns_parser_error_exit_two_and_no_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            local_ids = self._create_local_compat_hierarchy(
                target,
                issues=((301, "Issue A"), (302, "Issue B")),
            )
            from_id = local_ids["iss-00301"]
            from_meta_path = self._find_meta_path_by_id(target, from_id)
            before = from_meta_path.read_text(encoding="utf-8")

            p = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_id],
            )
            assert p.returncode == 2, p.stdout + p.stderr
            assert "usage:" in p.stderr
            assert "--to" in p.stderr

            after = from_meta_path.read_text(encoding="utf-8")
            assert after == before
