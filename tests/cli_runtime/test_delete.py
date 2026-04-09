import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from tests.cli_runtime.harness import CliRuntimeHarness, main


def _runtime_fs_repo():
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
        from spec_dock_runtime.infra import fs_repo as infra_fs_repo
    finally:
        sys.path.pop(0)
    return infra_fs_repo


class TestCliDelete(CliRuntimeHarness):
    def _make_gh_issue_close_stub(
        self,
        bin_dir: Path,
        *,
        issue_number: int,
        owner: str = "example",
        repo: str = "repo",
        issue_state: str = "OPEN",
        close_should_fail: bool = False,
    ) -> Path:
        normalized_state = str(issue_state).strip().upper()
        if normalized_state not in {"OPEN", "CLOSED"}:
            raise AssertionError(f"unsupported issue_state for gh stub: {issue_state}")
        state_path = bin_dir / "gh-state.json"
        state_path.write_text(
            json.dumps(
                {
                    "number": int(issue_number),
                    "state": normalized_state,
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
                f"EXPECTED_NUMBER = {int(issue_number)!r}\n"
                f"EXPECTED_REPO = {f'{owner}/{repo}'.lower()!r}\n"
                f"CLOSE_SHOULD_FAIL = {bool(close_should_fail)!r}\n"
                "args = sys.argv[1:]\n"
                "state = json.loads(STATE_PATH.read_text(encoding='utf-8'))\n"
                "def _validate_issue_command(command_name):\n"
                "    if len(args) < 3:\n"
                "        print(f'gh stub mismatch ({command_name}): missing issue number args={args}', file=sys.stderr)\n"
                "        raise SystemExit(98)\n"
                "    raw_number = str(args[2]).strip()\n"
                "    if raw_number != str(EXPECTED_NUMBER):\n"
                "        print(\n"
                "            f'gh stub mismatch ({command_name}): expected issue {EXPECTED_NUMBER}, got {raw_number}; args={args}',\n"
                "            file=sys.stderr,\n"
                "        )\n"
                "        raise SystemExit(98)\n"
                "    if '--repo' not in args:\n"
                "        print(f'gh stub mismatch ({command_name}): missing --repo; args={args}', file=sys.stderr)\n"
                "        raise SystemExit(98)\n"
                "    repo_index = args.index('--repo')\n"
                "    if repo_index + 1 >= len(args):\n"
                "        print(f'gh stub mismatch ({command_name}): missing repo slug value; args={args}', file=sys.stderr)\n"
                "        raise SystemExit(98)\n"
                "    actual_repo = str(args[repo_index + 1]).strip().lower()\n"
                "    if actual_repo != EXPECTED_REPO:\n"
                "        print(\n"
                "            f'gh stub mismatch ({command_name}): expected repo {EXPECTED_REPO}, got {actual_repo}; args={args}',\n"
                "            file=sys.stderr,\n"
                "        )\n"
                "        raise SystemExit(98)\n"
                "if args[:2] == ['issue', 'view']:\n"
                "    _validate_issue_command('issue view')\n"
                "    print(json.dumps(state))\n"
                "    raise SystemExit(0)\n"
                "if args[:2] == ['issue', 'close']:\n"
                "    _validate_issue_command('issue close')\n"
                "    if CLOSE_SHOULD_FAIL:\n"
                "        print('simulated close failure', file=sys.stderr)\n"
                "        raise SystemExit(1)\n"
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

    def _setup_delete_target_repo(
        self,
        *,
        issue_number: int = 56,
        issue_state: str = "OPEN",
        close_should_fail: bool = False,
    ) -> tuple[Path, Path, Path, dict[str, str]]:
        target = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: target.exists() and shutil.rmtree(target))
        self.assertEqual(main(["init", str(target)]), 0)
        self._create_same_repo_linked_hierarchy(
            target,
            initiative_issue_number=1,
            epic_issue_number=2,
            issue_issue_number=issue_number,
        )
        issue_dir = (
            target
            / "spec-dock"
            / "initiatives"
            / "init-00001-auth-platform"
            / "epics"
            / "epic-00002-jwt-auth"
            / "issues"
            / f"iss-{issue_number:05d}-add-refresh-token"
        )
        self.assertTrue(issue_dir.is_dir())

        bin_dir = target / ".bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        state_path = self._make_gh_issue_close_stub(
            bin_dir,
            issue_number=issue_number,
            issue_state=issue_state,
            close_should_fail=close_should_fail,
        )
        env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
        return target, issue_dir, state_path, env

    def test_delete_issue_by_positional_target_removes_local_leaf_and_closes_remote(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")

        target, issue_dir, state_path, env = self._setup_delete_target_repo(issue_number=56)
        p = self._run_runtime_capture(target, ["delete", "iss-00056", "--yes"], env=env)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delete) target=iss-00056", p.stdout)
        self.assertFalse(issue_dir.exists())
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["state"], "CLOSED")

    def test_delete_issue_by_id_flag_removes_local_leaf_and_closes_remote(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")

        target, issue_dir, state_path, env = self._setup_delete_target_repo(issue_number=56)
        p = self._run_runtime_capture(target, ["delete", "--id", "iss-00056", "--yes"], env=env)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delete) target=iss-00056", p.stdout)
        self.assertFalse(issue_dir.exists())
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["state"], "CLOSED")

    def test_delete_issue_by_github_issue_flag_removes_local_leaf_and_closes_remote(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")

        target, issue_dir, state_path, env = self._setup_delete_target_repo(issue_number=56)
        p = self._run_runtime_capture(target, ["delete", "--github-issue", "56", "--yes"], env=env)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delete) target=iss-00056", p.stdout)
        self.assertFalse(issue_dir.exists())
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["state"], "CLOSED")

    def test_delete_issue_with_recursive_flag_is_accepted_noop_and_succeeds(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")

        target, issue_dir, state_path, env = self._setup_delete_target_repo(issue_number=56)
        p = self._run_runtime_capture(target, ["delete", "--id", "iss-00056", "--recursive", "--yes"], env=env)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delete) target=iss-00056", p.stdout)
        self.assertFalse(issue_dir.exists())
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["state"], "CLOSED")

    def test_delete_issue_when_remote_already_closed_returns_ok_noop_and_removes_local_leaf(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")

        target, issue_dir, state_path, env = self._setup_delete_target_repo(
            issue_number=56,
            issue_state="CLOSED",
        )
        p = self._run_runtime_capture(target, ["delete", "--id", "iss-00056", "--yes", "--json"], env=env)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        payload = json.loads(p.stdout)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["target_id"], "iss-00056")
        self.assertEqual(payload["remote_close"]["closed"], [])
        self.assertEqual(payload["remote_close"]["noop_already_closed"], ["example/repo#56"])
        self.assertFalse(issue_dir.exists())
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["state"], "CLOSED")

    def test_delete_issue_remote_close_failed_keeps_local_leaf(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")

        target, issue_dir, state_path, env = self._setup_delete_target_repo(
            issue_number=56,
            close_should_fail=True,
        )
        p = self._run_runtime_capture(target, ["delete", "--id", "iss-00056", "--yes", "--json"], env=env)
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        payload = json.loads(p.stdout)
        self.assertEqual(payload["status"], "remote_close_failed")
        self.assertEqual(payload["target_id"], "iss-00056")
        self.assertEqual(payload["deleted_node_ids"], [])
        self.assertEqual(payload["remote_close"]["failed"], ["example/repo#56"])
        self.assertTrue(issue_dir.exists())
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["state"], "OPEN")

    def test_delete_issue_target_invalid_metadata_returns_structured_json(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a python gh stub with shebang; skip on Windows.")

        target, issue_dir, state_path, env = self._setup_delete_target_repo(issue_number=56)
        meta_path = issue_dir / ".meta.json"
        meta_path.chmod(meta_path.stat().st_mode | 0o200)
        meta_path.write_text("{invalid-json", encoding="utf-8")
        p = self._run_runtime_capture(target, ["delete", "--id", "iss-00056", "--yes", "--json"], env=env)
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        payload = json.loads(p.stdout)
        self.assertEqual(payload["status"], "metadata_validation_failed")
        self.assertEqual(payload["target_id"], "iss-00056")
        self.assertEqual(payload["offending_node_ids"], ["iss-00056"])
        self.assertEqual(payload["remote_close"]["closed"], [])
        self.assertEqual(payload["remote_close"]["noop_already_closed"], [])
        self.assertEqual(payload["remote_close"]["failed"], [])
        self.assertEqual(payload["remote_close"]["skipped_not_attempted"], [])
        self.assertEqual(p.stderr, "")
        self.assertTrue(issue_dir.exists())
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["state"], "OPEN")


class TestFsRepoDeleteTree(unittest.TestCase):
    def test_delete_tree_retries_permission_error_for_readonly_meta(self) -> None:
        infra_fs_repo = _runtime_fs_repo()
        temp_root = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: temp_root.exists() and shutil.rmtree(temp_root, ignore_errors=True))

        target = temp_root / "iss-00056-target"
        target.mkdir(parents=True, exist_ok=True)
        meta_path = target / ".meta.json"
        meta_path.write_text("{}\n", encoding="utf-8")
        meta_path.chmod(meta_path.stat().st_mode & ~0o222)

        def _remove_readonly_file(path: str) -> None:
            file_path = Path(path)
            self.assertNotEqual(file_path.stat().st_mode & 0o200, 0)
            file_path.unlink()

        def _fake_rmtree(path, onerror=None):
            self.assertTrue(callable(onerror))
            onerror(
                _remove_readonly_file,
                (Path(path) / ".meta.json").as_posix(),
                (PermissionError, PermissionError("read-only file"), None),
            )
            Path(path).rmdir()

        with mock.patch.object(infra_fs_repo.shutil, "rmtree", side_effect=_fake_rmtree):
            infra_fs_repo.delete_tree(target)

        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
