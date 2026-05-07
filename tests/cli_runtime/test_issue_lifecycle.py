import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from tests.cli_runtime.harness import CliRuntimeHarness, main


def _runtime_modules():
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
        from spec_dock_runtime.application import contracts as app_contracts
        from spec_dock_runtime.application import issue_lifecycle as app_issue_lifecycle
        from spec_dock_runtime.application import ports as app_ports
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.infra import contracts as infra_contracts
    finally:
        sys.path.pop(0)
    return app_contracts, app_issue_lifecycle, app_ports, domain_models, infra_contracts


class _StubNodeReader:
    def load_node_records(self):
        return []


class _StubActiveStateStore:
    def __init__(self, infra_contracts) -> None:
        self._infra_contracts = infra_contracts

    def load_active_manifest(self, specdock_dir: Path):
        del specdock_dir
        return self._infra_contracts.ActiveManifestLoadResult(
            manifest=self._infra_contracts.ActiveManifest(
                initiative=None,
                epic=None,
                issue=self._infra_contracts.ActiveManifestEntry(
                    id="iss-00101",
                    path="spec-dock/initiatives/init-00001/epics/epic-00002/issues/iss-00101",
                ),
            ),
            source="agent.active",
            warnings=[],
        )


class TestIssueLifecycleApplication(unittest.TestCase):
    def test_issue_finish_clear_active_failure_includes_recovery_guidance(self) -> None:
        app_contracts, app_issue_lifecycle, app_ports, domain_models, infra_contracts = _runtime_modules()
        original_close_node = app_issue_lifecycle.close_node
        original_clear_active = app_issue_lifecycle.clear_active
        try:
            for already_closed in (False, True):
                with self.subTest(already_closed=already_closed):
                    close_calls = []

                    def fake_close_node(req, ports):
                        close_calls.append((req, ports))
                        return app_contracts.CloseNodeResult(
                            node_id="iss-00101",
                            node_kind="issue",
                            github_issue_number=101,
                            issue_snapshot=domain_models.IssueSnapshot(
                                issue_number=101,
                                state="CLOSED",
                                title="First issue",
                                labels=[],
                                updated_at="2026-05-05T00:00:00Z",
                                url="https://github.com/example/repo/issues/101",
                            ),
                            already_closed=already_closed,
                            warnings=[],
                        )

                    def fake_clear_active(req, ports):
                        del req, ports
                        raise RuntimeError("clear active failed")

                    app_issue_lifecycle.close_node = fake_close_node
                    app_issue_lifecycle.clear_active = fake_clear_active

                    with tempfile.TemporaryDirectory() as tmp:
                        repo_root = Path(tmp)
                        ports = app_ports.Ports(
                            node_reader=_StubNodeReader(),
                            repo_root=repo_root,
                            specdock_dir=repo_root / "spec-dock",
                            active_state_store=_StubActiveStateStore(infra_contracts),
                        )
                        with self.assertRaises(RuntimeError) as raised:
                            app_issue_lifecycle.issue_finish(app_contracts.IssueFinishRequest(), ports)

                    message = str(raised.exception)
                    self.assertEqual(len(close_calls), 1)
                    self.assertIn("issue finish failed after GitHub close/already-closed step", message)
                    self.assertIn("GitHub issue #101 may have been closed successfully", message)
                    self.assertIn("may already have been closed", message)
                    self.assertIn("Active selection was not cleared.", message)
                    self.assertIn("spec-dock/scripts/spec-dock active show", message)
                    self.assertIn("spec-dock/scripts/spec-dock issue finish", message)
                    self.assertIn("spec-dock/scripts/spec-dock active set <issue-id> --checkout", message)
                    self.assertIn("manual active recovery", message)
                    self.assertIn("clear active failed", message)
        finally:
            app_issue_lifecycle.close_node = original_close_node
            app_issue_lifecycle.clear_active = original_clear_active


class TestCliIssueLifecycle(CliRuntimeHarness):
    def _commit_all(self, target: Path, message: str) -> None:
        self._run_git(target, ["add", "-A"])
        self._run_git(
            target,
            ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", message],
        )

    def _prepare_clean_repo_with_two_issues(self, target: Path) -> None:
        self.assertEqual(main(["init", str(target)]), 0)
        self._init_origin_repo(target)
        self._run_git(
            target,
            ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
        )
        self._create_same_repo_linked_hierarchy(target, issue_issue_number=101, issue_title="First issue")
        self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Second issue", "--github-issue", "102"])
        self._commit_all(target, "spec tree")

    def _make_gh_stub(
        self,
        bin_dir: Path,
        *,
        states: dict[int, str],
        fail_view_numbers: set[int] | None = None,
        fail_close_numbers: set[int] | None = None,
    ) -> Path:
        state_path = bin_dir / "gh-state.json"
        payload = {
            str(number): {
                "number": int(number),
                "state": state,
                "title": f"Issue {number}",
                "labels": [],
                "updatedAt": "2026-05-05T00:00:00Z",
                "url": f"https://github.com/example/repo/issues/{number}",
            }
            for number, state in states.items()
        }
        state_path.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")
        fail_numbers = sorted(int(number) for number in (fail_view_numbers or set()))
        fail_close = sorted(int(number) for number in (fail_close_numbers or set()))
        gh_path = bin_dir / "gh"
        gh_path.write_text(
            (
                "#!/usr/bin/env python3\n"
                "import json\n"
                "import sys\n"
                "from pathlib import Path\n\n"
                f"STATE_PATH = Path({state_path.as_posix()!r})\n"
                f"FAIL_VIEW = {fail_numbers!r}\n"
                f"FAIL_CLOSE = {fail_close!r}\n"
                "args = sys.argv[1:]\n"
                "state = json.loads(STATE_PATH.read_text(encoding='utf-8'))\n"
                "if args[:2] == ['issue', 'list']:\n"
                "    print(json.dumps(list(state.values())))\n"
                "    raise SystemExit(0)\n"
                "if args[:2] == ['issue', 'view']:\n"
                "    number = int(args[2])\n"
                "    if number in FAIL_VIEW:\n"
                "        print(f'view failed: {number}', file=sys.stderr)\n"
                "        raise SystemExit(1)\n"
                "    print(json.dumps(state[str(number)]))\n"
                "    raise SystemExit(0)\n"
                "if args[:2] == ['issue', 'close']:\n"
                "    number = int(args[2])\n"
                "    if number in FAIL_CLOSE:\n"
                "        print(f'close failed: {number}', file=sys.stderr)\n"
                "        raise SystemExit(1)\n"
                "    item = state[str(number)]\n"
                "    item['state'] = 'CLOSED'\n"
                "    STATE_PATH.write_text(json.dumps(state) + '\\n', encoding='utf-8')\n"
                "    raise SystemExit(0)\n"
                "print(f'unexpected gh args: {args}', file=sys.stderr)\n"
                "raise SystemExit(99)\n"
            ),
            encoding="utf-8",
        )
        gh_path.chmod(0o755)
        return state_path

    def _active_issue_id(self, target: Path) -> str | None:
        active_path = target / "spec-dock" / ".agent" / "active.json"
        if not active_path.exists():
            return None
        active = json.loads(active_path.read_text(encoding="utf-8"))
        issue = active.get("issue")
        if not isinstance(issue, dict):
            return None
        return issue.get("id")

    def test_issue_start_sets_active_and_checks_out_issue_branch(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["issue", "start", "--id", "iss-00101"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok (issue start)", p.stdout)
            self.assertIn("issue=iss-00101", p.stdout)
            self.assertIn("spec-dock: ok (issue checkout) branch=iss-00101-first-issue", p.stdout)
            self.assertEqual(self._active_issue_id(target), "iss-00101")
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            self.assertEqual(current, "iss-00101-first-issue")

    def test_issue_start_rejects_non_issue_node(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["issue", "start", "--id", "epic-00002"], env=test_env)
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("issue start only accepts issue nodes", p.stderr)
            self.assertIsNone(self._active_issue_id(target))

    def test_issue_start_blocks_different_open_issue_from_active_issue_branch(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["issue", "start", "101"], env=test_env)
            before = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")
            before_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()

            p = self._run_runtime_capture(target, ["issue", "start", "102"], env=test_env)
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("issue start blocked: unfinished active issue branch", p.stderr)
            self.assertIn("current active issue: iss-00101", p.stderr)
            self.assertIn("current branch: iss-00101-first-issue", p.stderr)
            self.assertIn("requested issue: iss-00102", p.stderr)
            self.assertIn("github state: OPEN", p.stderr)
            self.assertIn("issue finish", p.stderr)
            self.assertIn("issue start iss-00102 -f", p.stderr)
            self.assertIn("active set iss-00102 --checkout", p.stderr)
            self.assertEqual((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"), before)
            after_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            self.assertEqual(after_branch, before_branch)

    def test_direct_active_set_checkout_bypasses_issue_lifecycle_guard(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00102-second-issue"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta.pop("github", None)
            self._write_json_force(issue_meta, meta)
            self._commit_all(target, "make second issue locally ready")
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["issue", "start", "101"], env=test_env)
            self._commit_all(target, "active first issue")
            active_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            self.assertEqual(active_branch, "iss-00101-first-issue")
            self.assertEqual(self._active_issue_id(target), "iss-00101")

            p = self._run_runtime_capture(target, ["active", "set", "iss-00102", "--checkout"])

            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok (active set)", p.stdout)
            self.assertNotIn("issue start blocked", p.stderr)
            self.assertEqual(self._active_issue_id(target), "iss-00102")
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            self.assertEqual(current, "iss-00102-second-issue")

    def test_issue_start_allows_different_issue_from_closed_active_issue_branch(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["issue", "start", "101"], env=test_env)
            self._commit_all(target, "active closed issue")
            active_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            self.assertEqual(active_branch, "iss-00101-first-issue")
            self.assertEqual(self._active_issue_id(target), "iss-00101")
            self._make_gh_stub(bin_dir, states={101: "CLOSED", 102: "OPEN"})

            p = self._run_runtime_capture(target, ["issue", "start", "102"], env=test_env)

            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertNotIn("issue start blocked", p.stderr)
            self.assertIn("spec-dock: ok (issue start)", p.stdout)
            self.assertIn("issue=iss-00102", p.stdout)
            self.assertEqual(self._active_issue_id(target), "iss-00102")
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            self.assertEqual(current, "iss-00102-second-issue")

    def test_issue_start_blocks_when_active_issue_github_state_unknown(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["issue", "start", "101"], env=test_env)
            before = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")
            before_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()

            unknown_bin_dir = Path(bin_tmp)
            self._make_gh_stub(unknown_bin_dir, states={101: "OPEN", 102: "OPEN"}, fail_view_numbers={101})
            p = self._run_runtime_capture(target, ["issue", "start", "102"], env=test_env)

            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("issue start blocked: unfinished active issue branch", p.stderr)
            self.assertIn("github state: UNKNOWN", p.stderr)
            self.assertIn("Next commands:", p.stderr)
            self.assertIn("spec-dock/scripts/spec-dock issue finish", p.stderr)
            self.assertIn("spec-dock/scripts/spec-dock issue start iss-00102 -f", p.stderr)
            self.assertIn("spec-dock/scripts/spec-dock active set iss-00102 --checkout", p.stderr)
            self.assertEqual((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"), before)
            after_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            self.assertEqual(after_branch, before_branch)

    def test_issue_start_force_bypasses_only_lifecycle_guard_not_dependency_guard(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00102-second-issue"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["depends_on"] = ["iss-00101"]
            self._write_json_force(issue_meta, meta)
            self._commit_all(target, "add dependency")

            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["issue", "start", "101"], env=test_env)
            self._commit_all(target, "active first issue")

            p = self._run_runtime_capture(target, ["issue", "start", "102", "-f"], env=test_env)
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("active set blocked", p.stderr)
            self.assertNotIn("spec-dock: ok (issue start)", p.stdout)
            self.assertEqual(self._active_issue_id(target), "iss-00101")
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            self.assertEqual(current, "iss-00101-first-issue")

    def test_issue_start_rejects_legacy_force_short_options(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            uppercase = self._run_runtime_capture(target, ["issue", "start", "102", "-F"])
            old_t = self._run_runtime_capture(target, ["issue", "start", "102", "-t"])

            self.assertNotEqual(uppercase.returncode, 0, uppercase.stdout + uppercase.stderr)
            self.assertIn("unrecognized arguments: -F", uppercase.stderr)
            self.assertNotEqual(old_t.returncode, 0, old_t.stdout + old_t.stderr)
            self.assertIn("unrecognized arguments: -t", old_t.stderr)

    def test_issue_start_force_switches_when_dependency_ready_and_warns(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["issue", "start", "101"], env=test_env)
            self._commit_all(target, "active first issue")

            p = self._run_runtime_capture(target, ["issue", "start", "--github-issue", "102", "--force"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok (issue start)", p.stdout)
            self.assertIn("issue=iss-00102", p.stdout)
            self.assertIn("issue start forced=true", p.stderr)
            self.assertEqual(self._active_issue_id(target), "iss-00102")
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            self.assertEqual(current, "iss-00102-second-issue")

    def test_issue_start_from_main_and_same_issue_restart_do_not_trigger_guard(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            first = self._run_runtime_capture(target, ["issue", "start", "101"], env=test_env)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self._commit_all(target, "active first issue")
            same = self._run_runtime_capture(target, ["issue", "start", "101"], env=test_env)
            self.assertEqual(same.returncode, 0, same.stdout + same.stderr)
            self.assertNotIn("issue start blocked", same.stderr)
            self._commit_all(target, "same issue restart")

            self._run_git(target, ["checkout", "main"])
            main_start = self._run_runtime_capture(target, ["issue", "start", "102"], env=test_env)
            self.assertEqual(main_start.returncode, 0, main_start.stdout + main_start.stderr)
            self.assertNotIn("issue start blocked", main_start.stderr)
            self.assertEqual(self._active_issue_id(target), "iss-00102")

    def test_issue_start_from_non_issue_branch_allows_switching_open_active_issue(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            first = self._run_runtime_capture(target, ["issue", "start", "101"], env=test_env)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self._commit_all(target, "active first issue")
            self._run_git(target, ["checkout", "-b", "maintenance-check"])

            p = self._run_runtime_capture(target, ["issue", "start", "102"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertNotIn("issue start blocked", p.stderr)
            self.assertIn("spec-dock: ok (issue start)", p.stdout)
            self.assertEqual(self._active_issue_id(target), "iss-00102")
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            self.assertEqual(current, "iss-00102-second-issue")

    def test_issue_finish_closes_open_issue_and_clears_active(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=101, issue_title="First issue")
            self._run_runtime(target, ["active", "set", "--id", "iss-00101", "--force"])
            bin_dir = Path(bin_tmp)
            state_path = self._make_gh_stub(bin_dir, states={101: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["issue", "finish"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok (issue finish)", p.stdout)
            self.assertIn("issue=iss-00101", p.stdout)
            self.assertIn("github=#101", p.stdout)
            self.assertIn("active_cleared=true", p.stdout)
            self.assertIn("already_closed=false", p.stdout)
            self.assertIsNone(self._active_issue_id(target))
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["101"]["state"], "CLOSED")

    def test_issue_finish_already_closed_clears_active(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=101, issue_title="First issue")
            self._run_runtime(target, ["active", "set", "--id", "iss-00101", "--force"])
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "CLOSED"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["issue", "finish"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("already_closed=true", p.stdout)
            self.assertIsNone(self._active_issue_id(target))

    def test_issue_finish_failures_leave_active_unchanged(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            no_active = self._run_runtime_capture(target, ["issue", "finish"])
            self.assertNotEqual(no_active.returncode, 0, no_active.stdout + no_active.stderr)
            self.assertIn("issue finish requires an active issue", no_active.stderr)
            self.assertIn("Recovery:", no_active.stderr)
            self.assertIn("issue start <issue>", no_active.stderr)
            self.assertIn("active set <issue> --checkout", no_active.stderr)
            self.assertIsNone(self._active_issue_id(target))

            self._create_same_repo_linked_hierarchy(target, issue_issue_number=101, issue_title="First issue")
            linked_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00101-first-issue"
                / ".meta.json"
            )
            linked_meta = json.loads(linked_meta_path.read_text(encoding="utf-8"))
            unlinked_meta = dict(linked_meta)
            unlinked_meta.pop("github", None)
            self._write_json_force(linked_meta_path, unlinked_meta)
            self._run_runtime(target, ["active", "set", "--id", "iss-00101", "--force"])
            no_link = self._run_runtime_capture(target, ["issue", "finish"])
            self.assertNotEqual(no_link.returncode, 0, no_link.stdout + no_link.stderr)
            self.assertIn("issue finish failed while closing GitHub issue", no_link.stderr)
            self.assertIn("Active selection was not cleared.", no_link.stderr)
            self.assertIn("Recovery:", no_link.stderr)
            self.assertIn("spec-dock/scripts/spec-dock issue finish", no_link.stderr)
            self.assertIn("spec-dock/scripts/spec-dock active show", no_link.stderr)
            self.assertIn("Node is not linked to a GitHub issue", no_link.stderr)
            self.assertEqual(self._active_issue_id(target), "iss-00101")

            active_path = target / "spec-dock" / ".agent" / "active.json"
            stale_active = json.loads(active_path.read_text(encoding="utf-8"))
            stale_active["issue"]["id"] = "iss-00999"
            self._write_json_force(active_path, stale_active)
            node_not_found = self._run_runtime_capture(target, ["issue", "finish"])
            self.assertNotEqual(node_not_found.returncode, 0, node_not_found.stdout + node_not_found.stderr)
            self.assertIn("issue finish failed while closing GitHub issue", node_not_found.stderr)
            self.assertIn("Active selection was not cleared.", node_not_found.stderr)
            self.assertIn("Recovery:", node_not_found.stderr)
            self.assertIn("spec-dock/scripts/spec-dock issue finish", node_not_found.stderr)
            self.assertIn("spec-dock/scripts/spec-dock active show", node_not_found.stderr)
            self.assertIn("Node not found: iss-00999", node_not_found.stderr)
            self.assertEqual(self._active_issue_id(target), "iss-00999")

            self._write_json_force(linked_meta_path, linked_meta)
            self._run_runtime(target, ["active", "set", "--id", "iss-00101", "--force"])
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN"}, fail_view_numbers={101})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            close_failure = self._run_runtime_capture(target, ["issue", "finish"], env=test_env)
            self.assertNotEqual(close_failure.returncode, 0, close_failure.stdout + close_failure.stderr)
            self.assertIn("issue finish failed while closing GitHub issue", close_failure.stderr)
            self.assertIn("Active selection was not cleared.", close_failure.stderr)
            self.assertIn("Recovery:", close_failure.stderr)
            self.assertIn("spec-dock/scripts/spec-dock issue finish", close_failure.stderr)
            self.assertIn("spec-dock/scripts/spec-dock active show", close_failure.stderr)
            self.assertIn("view failed: 101", close_failure.stderr)
            self.assertEqual(self._active_issue_id(target), "iss-00101")

            self._make_gh_stub(bin_dir, states={101: "OPEN"}, fail_close_numbers={101})
            close_command_failure = self._run_runtime_capture(target, ["issue", "finish"], env=test_env)
            self.assertNotEqual(close_command_failure.returncode, 0, close_command_failure.stdout + close_command_failure.stderr)
            self.assertIn("issue finish failed while closing GitHub issue", close_command_failure.stderr)
            self.assertIn("Active selection was not cleared.", close_command_failure.stderr)
            self.assertIn("Recovery:", close_command_failure.stderr)
            self.assertIn("spec-dock/scripts/spec-dock issue finish", close_command_failure.stderr)
            self.assertIn("spec-dock/scripts/spec-dock active show", close_command_failure.stderr)
            self.assertIn("close failed: 101", close_command_failure.stderr)
            self.assertEqual(self._active_issue_id(target), "iss-00101")
