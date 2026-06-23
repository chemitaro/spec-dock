import json
import os
import tempfile
from pathlib import Path

from tests.cli_runtime.harness import CliRuntimeHarness, main


import pytest


class TestCliClose(CliRuntimeHarness):
    def _make_gh_issue_close_stub(
        self,
        bin_dir: Path,
        *,
        issue_number: int,
        initial_state: str = "OPEN",
        fail_close: bool = False,
        owner: str = "example",
        repo: str = "repo",
    ) -> Path:
        state_path = bin_dir / "gh-state.json"
        log_path = bin_dir / "gh-calls.log"
        issues = {
            1: "OPEN",
            2: "OPEN",
            int(issue_number): initial_state,
        }
        state_path.write_text(
            json.dumps(
                {
                    str(number): {
                        "number": int(number),
                        "state": state,
                        "title": f"Issue {number}",
                        "labels": [],
                        "updatedAt": "2026-04-09T00:00:00Z",
                        "url": f"https://github.com/{owner}/{repo}/issues/{number}",
                    }
                    for number, state in issues.items()
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
                f"LOG_PATH = Path({log_path.as_posix()!r})\n"
                f"FAIL_CLOSE = {bool(fail_close)!r}\n"
                "args = sys.argv[1:]\n"
                "state = json.loads(STATE_PATH.read_text(encoding='utf-8'))\n"
                "LOG_PATH.write_text(LOG_PATH.read_text(encoding='utf-8') + ' '.join(args) + '\\n' if LOG_PATH.exists() else ' '.join(args) + '\\n', encoding='utf-8')\n"
                "if args[:2] == ['issue', 'view']:\n"
                "    print(json.dumps(state[str(int(args[2]))]))\n"
                "    raise SystemExit(0)\n"
                "if args[:2] == ['issue', 'close']:\n"
                "    if FAIL_CLOSE:\n"
                "        print(f'close failed: {args[2]}', file=sys.stderr)\n"
                "        raise SystemExit(1)\n"
                "    state[str(int(args[2]))]['state'] = 'CLOSED'\n"
                "    STATE_PATH.write_text(json.dumps(state) + '\\n', encoding='utf-8')\n"
                "    raise SystemExit(0)\n"
                "if args[:2] == ['issue', 'list']:\n"
                "    print(json.dumps(list(state.values())))\n"
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
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
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
            assert issue_dir.is_dir()

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            state_path = self._make_gh_issue_close_stub(bin_dir, issue_number=55)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["close", "--id", "iss-00055"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok (close)" in p.stdout
            assert "node=iss-00055" in p.stdout
            assert "already_closed=false" in p.stdout
            assert issue_dir.is_dir()

            state = json.loads(state_path.read_text(encoding="utf-8"))
            assert state["55"]["state"] == "CLOSED"

    def test_close_command_accepts_explicit_github_issue_flag(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=55)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_close_stub(bin_dir, issue_number=55)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["close", "--github-issue", "55"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok (close)" in p.stdout
            assert "target=github#55" in p.stdout

    def test_close_command_accepts_positional_issue_number_target(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=55)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_close_stub(bin_dir, issue_number=55)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["close", "55"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok (close)" in p.stdout
            assert "target=github#55" in p.stdout

    def test_close_command_accepts_canonical_url_target(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
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
            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok (close)" in p.stdout
            assert "target=github:example/repo#55" in p.stdout

    def test_close_refreshes_github_backed_derived_state_without_manual_sync(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
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
            assert close_result.returncode == 0, close_result.stdout + close_result.stderr

            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            assert index_all["nodes"]["iss-00055"]["status"] == "done"

    def test_close_already_closed_refreshes_github_backed_derived_state(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=1,
                epic_issue_number=2,
                issue_issue_number=55,
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_close_stub(bin_dir, issue_number=55, initial_state="CLOSED")
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            close_result = self._run_runtime_capture(target, ["close", "55"], env=test_env)
            assert close_result.returncode == 0, close_result.stdout + close_result.stderr
            assert "already_closed=true" in close_result.stdout

            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            assert index_all["nodes"]["iss-00055"]["status"] == "done"

    def test_close_failure_does_not_run_post_sync(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=55)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_close_stub(bin_dir, issue_number=55, fail_close=True)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["close", "55"], env=test_env)

            assert p.returncode != 0, p.stdout + p.stderr
            assert "close failed: 55" in p.stderr
            log = (bin_dir / "gh-calls.log").read_text(encoding="utf-8")
            assert "issue list" not in log
