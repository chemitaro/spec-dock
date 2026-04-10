import json
import os
import tempfile
from pathlib import Path

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestCliClose(CliRuntimeHarness):
    def _make_gh_issue_close_stub(
        self,
        bin_dir: Path,
        *,
        issue_number: int,
        owner: str = "example",
        repo: str = "repo",
    ) -> Path:
        state_path = bin_dir / "gh-state.json"
        state_path.write_text(
            json.dumps(
                {
                    "number": int(issue_number),
                    "state": "OPEN",
                    "title": f"Issue {issue_number}",
                    "labels": [],
                    "updatedAt": "2026-04-09T00:00:00Z",
                    "url": f"https://github.com/{owner}/{repo}/issues/{issue_number}",
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        gh_path = bin_dir / "gh"
        gh_path.write_text(
            (
                "#!/usr/bin/env python3\n"
                "import json\n"
                "import sys\n"
                "from pathlib import Path\n\n"
                f"STATE_PATH = Path({state_path.as_posix()!r})\n"
                "args = sys.argv[1:]\n"
                "state = json.loads(STATE_PATH.read_text(encoding='utf-8'))\n"
                "if args[:2] == ['issue', 'view']:\n"
                "    print(json.dumps(state))\n"
                "    raise SystemExit(0)\n"
                "if args[:2] == ['issue', 'close']:\n"
                "    state['state'] = 'CLOSED'\n"
                "    STATE_PATH.write_text(json.dumps(state) + '\\n', encoding='utf-8')\n"
                "    raise SystemExit(0)\n"
                "if args[:2] == ['issue', 'list']:\n"
                "    print(json.dumps([state]))\n"
                "    raise SystemExit(0)\n"
                "print(f'unexpected gh args: {args}', file=sys.stderr)\n"
                "raise SystemExit(99)\n"
            ),
            encoding="utf-8",
        )
        gh_path.chmod(0o755)
        return state_path

    def test_close_command_accepts_explicit_id_flag_and_keeps_local_tree(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=55)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00055-add-refresh-token"
            )
            self.assertTrue(issue_dir.is_dir())

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            state_path = self._make_gh_issue_close_stub(bin_dir, issue_number=55)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["close", "--id", "iss-00055"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok (close)", p.stdout)
            self.assertIn("node=iss-00055", p.stdout)
            self.assertIn("already_closed=false", p.stdout)
            self.assertTrue(issue_dir.is_dir())

            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["state"], "CLOSED")

    def test_close_command_accepts_explicit_github_issue_flag(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=55)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_close_stub(bin_dir, issue_number=55)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["close", "--github-issue", "55"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok (close)", p.stdout)
            self.assertIn("target=github#55", p.stdout)

    def test_close_command_accepts_positional_issue_number_target(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=55)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_close_stub(bin_dir, issue_number=55)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["close", "55"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok (close)", p.stdout)
            self.assertIn("target=github#55", p.stdout)

    def test_close_command_accepts_canonical_url_target(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=55)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_close_stub(bin_dir, issue_number=55)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["close", "https://github.com/example/repo/issues/55"],
                env=test_env,
            )
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok (close)", p.stdout)
            self.assertIn("target=github:example/repo#55", p.stdout)

    def test_close_then_sync_github_marks_issue_done(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=1,
                epic_issue_number=2,
                issue_issue_number=55,
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_close_stub(bin_dir, issue_number=55)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            close_result = self._run_runtime_capture(target, ["close", "55"], env=test_env)
            self.assertEqual(close_result.returncode, 0, close_result.stdout + close_result.stderr)

            sync_result = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(sync_result.returncode, 0, sync_result.stdout + sync_result.stderr)

            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            self.assertEqual(index_all["nodes"]["iss-00055"]["status"], "done")
