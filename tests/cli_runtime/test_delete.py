import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

from tests.cli_runtime.harness import CliRuntimeHarness, main




import contextlib
import pytest
_MISSING = object()


class _CallProbe:
    def __init__(self, *, side_effect=_MISSING, return_value=_MISSING):
        self.calls = []
        self._side_effect = side_effect
        self._return_value = return_value

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        if self._side_effect is not _MISSING:
            if isinstance(self._side_effect, BaseException):
                raise self._side_effect
            return self._side_effect(*args, **kwargs)
        if self._return_value is not _MISSING:
            return self._return_value
        return None

    def assert_called_once_with(self, *args, **kwargs):
        assert self.calls == [(args, kwargs)]


@contextlib.contextmanager
def _patch_object(target, name, replacement=_MISSING, *, side_effect=_MISSING, return_value=_MISSING):
    original = getattr(target, name)
    if replacement is _MISSING:
        replacement = _CallProbe(side_effect=side_effect, return_value=return_value)
    setattr(target, name, replacement)
    try:
        yield replacement
    finally:
        setattr(target, name, original)
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
    def _register_cleanup(self, cleanup) -> None:
        self._cleanups = getattr(self, "_cleanups", [])
        self._cleanups.append(cleanup)

    def teardown_method(self) -> None:
        for cleanup in reversed(getattr(self, "_cleanups", [])):
            cleanup()
        self._cleanups = []

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
                "    issues = []\n"
                "    for number in range(1, 1000):\n"
                "        item = {\n"
                "            'number': number,\n"
                "            'state': 'OPEN',\n"
                "            'title': f'Issue {number}',\n"
                "            'labels': [],\n"
                "            'updatedAt': '2026-04-09T00:00:00Z',\n"
                "            'url': f'https://github.com/{EXPECTED_REPO}/issues/{number}',\n"
                "        }\n"
                "        if number == EXPECTED_NUMBER:\n"
                "            item.update(state)\n"
                "        issues.append(item)\n"
                "    print(json.dumps(issues))\n"
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
        self._register_cleanup(lambda: target.exists() and shutil.rmtree(target))
        assert main(["init", str(target)]) == 0
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
        assert issue_dir.is_dir()

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

    def _read_delete_auto_sync_artifacts(self, target: Path) -> dict[str, str | None]:
        paths = (
            target / "spec-dock" / ".agent" / "index-all.json",
            target / "spec-dock" / ".agent" / "index.json",
            target / "spec-dock" / ".agent" / "deps-issues.json",
            target / "spec-dock" / "deps-issues.puml",
            target / "spec-dock" / "dashboard.md",
        )
        return {
            path.relative_to(target).as_posix(): path.read_text(encoding="utf-8") if path.exists() else None
            for path in paths
        }

    def _assert_delete_auto_sync_artifacts_absent(self, target: Path, node_id: str) -> None:
        specdock_dir = target / "spec-dock"
        index_all = json.loads((specdock_dir / ".agent" / "index-all.json").read_text(encoding="utf-8"))
        index = json.loads((specdock_dir / ".agent" / "index.json").read_text(encoding="utf-8"))
        deps_issues = json.loads((specdock_dir / ".agent" / "deps-issues.json").read_text(encoding="utf-8"))
        dashboard = (specdock_dir / "dashboard.md").read_text(encoding="utf-8")
        deps_puml = (specdock_dir / "deps-issues.puml").read_text(encoding="utf-8")

        assert node_id not in index_all["nodes"]
        assert node_id not in index["nodes"]
        assert node_id not in deps_issues["nodes"]
        assert not any(
                edge.get("from") == node_id or edge.get("to") == node_id
                for edge in deps_issues.get("edges", [])
                if isinstance(edge, dict)
            )
        assert node_id not in dashboard
        assert node_id not in deps_puml

    def _inject_delete_post_sync_artifact_failure(self, target: Path) -> None:
        writer_path = target / "spec-dock" / "scripts" / "spec_dock_runtime" / "infra" / "artifact_writer.py"
        original = writer_path.read_text(encoding="utf-8")
        writer_path.write_text(
            original.replace(
                "def _write_text(path: Path, text: str) -> None:\n",
                (
                    "def _write_text(path: Path, text: str) -> None:\n"
                    "    if path.name == 'dashboard.md':\n"
                    "        raise RuntimeError('injected artifact writer failure')\n"
                ),
                1,
            ),
            encoding="utf-8",
        )

    def test_delete_issue_by_positional_target_removes_local_leaf_and_closes_remote(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        target, issue_dir, state_path, env = self._setup_delete_target_repo(issue_number=56)
        p = self._run_runtime_capture(target, ["delete", "iss-00056", "--yes"], env=env)
        assert p.returncode == 0, p.stdout + p.stderr
        assert "spec-dock: ok (delete) target=iss-00056" in p.stdout
        assert not issue_dir.exists()
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert state["state"] == "CLOSED"

    def test_delete_issue_auto_syncs_index_dashboard_and_dependency_projection(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        target, issue_dir, _state_path, env = self._setup_delete_target_repo(issue_number=56)
        self._run_runtime(
            target,
            ["new", "issue", "--epic", "2", "--title", "Survivor issue", "--github-issue", "58"],
            env=env,
        )
        self._run_runtime(target, ["deps", "add", "--from", "iss-00058", "--to", "iss-00056"], env=env)
        self._run_runtime(target, ["sync"], env=env)
        before = self._read_delete_auto_sync_artifacts(target)
        assert any("iss-00056" in (text or "") for text in before.values())

        p = self._run_runtime_capture(target, ["delete", "--id", "iss-00056", "--force", "--yes"], env=env)

        assert p.returncode == 0, p.stdout + p.stderr
        assert "spec-dock: ok (delete) target=iss-00056" in p.stdout
        assert p.stderr.strip() == ""
        assert not issue_dir.exists()
        self._assert_delete_auto_sync_artifacts_absent(target, "iss-00056")

    def test_delete_issue_post_sync_artifact_failure_returns_nonzero_with_recovery_guidance(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        target, issue_dir, _state_path, env = self._setup_delete_target_repo(issue_number=56)
        self._run_runtime(target, ["sync"], env=env)
        self._inject_delete_post_sync_artifact_failure(target)

        p = self._run_runtime_capture(target, ["delete", "--id", "iss-00056", "--yes"], env=env)

        assert p.returncode == 1, p.stdout + p.stderr
        assert "spec-dock: ok (delete) target=iss-00056" in p.stdout
        assert "spec-dock: failed (delete auto-sync) target=iss-00056" in p.stderr
        assert "mutation succeeded" in p.stderr
        assert "derived artifacts may be stale or partially written" in p.stderr
        assert "./spec-dock/scripts/spec-dock sync" in p.stderr
        assert not issue_dir.exists()

    def test_delete_preflight_failure_does_not_run_post_sync_or_refresh_artifacts(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        target, issue_dir, _state_path, env = self._setup_delete_target_repo(issue_number=56)
        self._run_runtime(target, ["sync"], env=env)
        before = self._read_delete_auto_sync_artifacts(target)

        p = self._run_runtime_capture(target, ["delete", "--id", "iss-00999", "--yes"], env=env)

        assert p.returncode == 1, p.stdout + p.stderr
        assert "spec-dock: blocked (delete) status=target_not_found" in p.stderr
        assert issue_dir.exists()
        assert before == self._read_delete_auto_sync_artifacts(target)

    def test_delete_issue_by_id_flag_removes_local_leaf_and_closes_remote(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        target, issue_dir, state_path, env = self._setup_delete_target_repo(issue_number=56)
        p = self._run_runtime_capture(target, ["delete", "--id", "iss-00056", "--yes"], env=env)
        assert p.returncode == 0, p.stdout + p.stderr
        assert "spec-dock: ok (delete) target=iss-00056" in p.stdout
        assert not issue_dir.exists()
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert state["state"] == "CLOSED"

    def test_delete_issue_by_github_issue_flag_removes_local_leaf_and_closes_remote(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        target, issue_dir, state_path, env = self._setup_delete_target_repo(issue_number=56)
        p = self._run_runtime_capture(target, ["delete", "--github-issue", "56", "--yes"], env=env)
        assert p.returncode == 0, p.stdout + p.stderr
        assert "spec-dock: ok (delete) target=iss-00056" in p.stdout
        assert not issue_dir.exists()
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert state["state"] == "CLOSED"

    def test_delete_issue_with_recursive_flag_is_accepted_noop_and_succeeds(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        target, issue_dir, state_path, env = self._setup_delete_target_repo(issue_number=56)
        p = self._run_runtime_capture(target, ["delete", "--id", "iss-00056", "--recursive", "--yes"], env=env)
        assert p.returncode == 0, p.stdout + p.stderr
        assert "spec-dock: ok (delete) target=iss-00056" in p.stdout
        assert not issue_dir.exists()
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert state["state"] == "CLOSED"

    def test_delete_issue_when_remote_already_closed_returns_ok_noop_and_removes_local_leaf(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        target, issue_dir, state_path, env = self._setup_delete_target_repo(
            issue_number=56,
            issue_state="CLOSED",
        )
        p = self._run_runtime_capture(target, ["delete", "--id", "iss-00056", "--yes", "--json"], env=env)
        assert p.returncode == 0, p.stdout + p.stderr
        payload = json.loads(p.stdout)
        assert payload["status"] == "ok"
        assert payload["target_id"] == "iss-00056"
        assert payload["remote_close"]["closed"] == []
        assert payload["remote_close"]["noop_already_closed"] == ["example/repo#56"]
        assert not issue_dir.exists()
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert state["state"] == "CLOSED"

    def test_delete_issue_remote_close_failed_keeps_local_leaf(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        target, issue_dir, state_path, env = self._setup_delete_target_repo(
            issue_number=56,
            close_should_fail=True,
        )
        p = self._run_runtime_capture(target, ["delete", "--id", "iss-00056", "--yes", "--json"], env=env)
        assert p.returncode == 1, p.stdout + p.stderr
        payload = json.loads(p.stdout)
        assert payload["status"] == "remote_close_failed"
        assert payload["target_id"] == "iss-00056"
        assert payload["deleted_node_ids"] == []
        assert payload["remote_close"]["failed"] == ["example/repo#56"]
        assert issue_dir.exists()
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert state["state"] == "OPEN"

    def test_delete_issue_target_invalid_metadata_returns_structured_json(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        target, issue_dir, state_path, env = self._setup_delete_target_repo(issue_number=56)
        meta_path = issue_dir / ".meta.json"
        meta_path.chmod(meta_path.stat().st_mode | 0o200)
        meta_path.write_text("{invalid-json", encoding="utf-8")
        p = self._run_runtime_capture(target, ["delete", "--id", "iss-00056", "--yes", "--json"], env=env)
        assert p.returncode == 1, p.stdout + p.stderr
        payload = json.loads(p.stdout)
        assert payload["status"] == "metadata_validation_failed"
        assert payload["target_id"] == "iss-00056"
        assert payload["offending_node_ids"] == ["iss-00056"]
        assert payload["remote_close"]["closed"] == []
        assert payload["remote_close"]["noop_already_closed"] == []
        assert payload["remote_close"]["failed"] == []
        assert payload["remote_close"]["skipped_not_attempted"] == []
        assert p.stderr == ""
        assert issue_dir.exists()
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert state["state"] == "OPEN"

    def test_delete_issue_target_invalid_metadata_positional_returns_structured_json(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        target, issue_dir, state_path, env = self._setup_delete_target_repo(issue_number=56)
        meta_path = issue_dir / ".meta.json"
        meta_path.chmod(meta_path.stat().st_mode | 0o200)
        meta_path.write_text("{invalid-json", encoding="utf-8")
        p = self._run_runtime_capture(target, ["delete", "iss-00056", "--yes", "--json"], env=env)
        assert p.returncode == 1, p.stdout + p.stderr
        payload = json.loads(p.stdout)
        assert payload["status"] == "metadata_validation_failed"
        assert payload["target_id"] == "iss-00056"
        assert payload["offending_node_ids"] == ["iss-00056"]
        assert payload["remote_close"]["closed"] == []
        assert payload["remote_close"]["noop_already_closed"] == []
        assert payload["remote_close"]["failed"] == []
        assert payload["remote_close"]["skipped_not_attempted"] == []
        assert p.stderr == ""
        assert issue_dir.exists()
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert state["state"] == "OPEN"

    def test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        target, issue56_dir, state_path, env = self._setup_delete_target_repo(issue_number=56)
        self._run_runtime(
            target,
            [
                "new",
                "epic",
                "--initiative",
                "1",
                "--title",
                "Survivor epic",
                "--github-issue",
                "20",
            ],
        )
        self._run_runtime(
            target,
            [
                "new",
                "issue",
                "--epic",
                "20",
                "--title",
                "Survivor issue",
                "--github-issue",
                "58",
            ],
        )
        self._run_runtime(target, ["deps", "add", "--from", "iss-00058", "--to", "iss-00056"])

        issue58_matches = list((target / "spec-dock" / "initiatives").rglob("iss-00058-*"))
        assert len(issue58_matches) == 1
        issue58_dir = issue58_matches[0]
        issue58_meta_path = issue58_dir / ".meta.json"
        assert "iss-00056" in [str(item).lower() for item in json.loads(issue58_meta_path.read_text(encoding="utf-8")).get("depends_on", [])]

        deleted = self._run_runtime_capture(
            target,
            ["delete", "--id", "iss-00056", "--force", "--yes", "--json"],
            env=env,
        )
        assert deleted.returncode == 0, deleted.stdout + deleted.stderr
        deleted_payload = json.loads(deleted.stdout)
        assert deleted_payload["status"] == "ok"
        assert deleted_payload["target_id"] == "iss-00056"
        assert not issue56_dir.exists()

        scrubbed_meta = json.loads(issue58_meta_path.read_text(encoding="utf-8"))
        assert "iss-00056" not in [str(item).lower() for item in scrubbed_meta.get("depends_on", [])]

        validated = self._run_runtime_capture(target, ["validate"], env=env)
        assert validated.returncode == 0, validated.stdout + validated.stderr

        synced = self._run_runtime_capture(target, ["sync"], env=env)
        assert synced.returncode == 0, synced.stdout + synced.stderr
        deps_payload = json.loads((target / "spec-dock" / ".agent" / "deps-issues.json").read_text(encoding="utf-8"))
        assert not any(
                edge.get("from") == "iss-00058" and edge.get("to") == "iss-00056"
                for edge in deps_payload.get("edges", [])
                if isinstance(edge, dict)
            )

        activated = self._run_runtime_capture(target, ["active", "set", "--id", "iss-00058", "--force"], env=env)
        assert activated.returncode == 0, activated.stdout + activated.stderr
        assert "spec-dock: ok (active set)" in activated.stdout
        assert "iss-00056" not in activated.stdout + activated.stderr
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert state["state"] == "CLOSED"


class TestFsRepoDeleteTree:
    def _register_cleanup(self, cleanup) -> None:
        self._cleanups = getattr(self, "_cleanups", [])
        self._cleanups.append(cleanup)

    def teardown_method(self) -> None:
        for cleanup in reversed(getattr(self, "_cleanups", [])):
            cleanup()
        self._cleanups = []

    def test_delete_tree_retries_permission_error_for_readonly_meta(self) -> None:
        infra_fs_repo = _runtime_fs_repo()
        temp_root = Path(tempfile.mkdtemp())
        self._register_cleanup(lambda: temp_root.exists() and shutil.rmtree(temp_root, ignore_errors=True))

        target = temp_root / "iss-00056-target"
        target.mkdir(parents=True, exist_ok=True)
        meta_path = target / ".meta.json"
        meta_path.write_text("{}\n", encoding="utf-8")
        meta_path.chmod(meta_path.stat().st_mode & ~0o222)

        def _remove_readonly_file(path: str) -> None:
            file_path = Path(path)
            assert file_path.stat().st_mode & 0o200 != 0
            file_path.unlink()

        def _fake_rmtree(path, onerror=None):
            assert callable(onerror)
            onerror(
                _remove_readonly_file,
                (Path(path) / ".meta.json").as_posix(),
                (PermissionError, PermissionError("read-only file"), None),
            )
            Path(path).rmdir()

        with _patch_object(infra_fs_repo.shutil, "rmtree", side_effect=_fake_rmtree):
            infra_fs_repo.delete_tree(target)

        assert not target.exists()
