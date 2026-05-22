import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestCliWorktree(CliRuntimeHarness):
    def _prepare_git_repo(self, target: Path) -> None:
        if shutil.which("git") is None:
            self.skipTest("git not available")
        self.assertEqual(main(["init", str(target)]), 0)
        self._run_git(target, ["init"])
        self._run_git(target, ["add", "-A"])
        self._run_git(
            target,
            ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "init"],
        )

    def test_worktree_create_uses_sibling_container_auto_id_and_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            target.mkdir()
            self._prepare_git_repo(target)

            p = self._run_runtime_capture(target, ["worktree", "create"])

            self.assertEqual(p.returncode, 0, p.stderr)
            current_branch = self._run_git(target, ["branch", "--show-current"]).stdout.strip()
            expected_path = (target.parent / "sample-repo-worktrees" / "sample-repo-wt1").resolve()
            self.assertIn(f"id=wt1", p.stdout)
            self.assertIn(f"path={expected_path}", p.stdout)
            self.assertIn("bootstrap status=skipped", p.stdout)
            self.assertTrue(expected_path.is_dir())
            self.assertTrue((expected_path / "spec-dock" / "scripts" / "spec-dock").is_file())
            worktree_list = self._run_git(target, ["worktree", "list", "--porcelain"]).stdout
            self.assertIn(str(expected_path), worktree_list)
            self.assertIn(f"branch refs/heads/{current_branch}-wt1", worktree_list)

    def test_worktree_create_retries_collisions_and_accepts_label(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            target.mkdir()
            self._prepare_git_repo(target)
            first = self._run_runtime_capture(target, ["worktree", "create", "feature"])
            second = self._run_runtime_capture(target, ["worktree", "create", "feature"])

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            current_branch = self._run_git(target, ["branch", "--show-current"]).stdout.strip()
            self.assertIn(f"id=feature branch={current_branch}-feature", first.stdout)
            self.assertIn(f"id=feature2 branch={current_branch}-feature2", second.stdout)

    def test_worktree_create_retries_auto_id_collisions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            target.mkdir()
            self._prepare_git_repo(target)
            first = self._run_runtime_capture(target, ["worktree", "create"])
            second = self._run_runtime_capture(target, ["worktree", "create"])

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            current_branch = self._run_git(target, ["branch", "--show-current"]).stdout.strip()
            self.assertIn(f"id=wt1 branch={current_branch}-wt1", first.stdout)
            self.assertIn(f"id=wt2 branch={current_branch}-wt2", second.stdout)

    def test_worktree_create_rejects_invalid_labels_without_creating_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            target.mkdir()
            self._prepare_git_repo(target)

            for label in (
                "bad_label",
                "Bad",
                "bad.label",
                "bad/label",
                "bad label",
                " label",
                " ",
                "bad;label",
                "bad$label",
                "bad&label",
            ):
                with self.subTest(label=label):
                    p = self._run_runtime_capture(target, ["worktree", "create", label])

                    self.assertNotEqual(p.returncode, 0)
                    self.assertIn("invalid worktree label", p.stderr)
            self.assertFalse((target.parent / "sample-repo-worktrees").exists())

    def test_worktree_create_help_exposes_optional_label(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            target.mkdir()
            self._prepare_git_repo(target)

            p = self._run_runtime_capture(target, ["worktree", "create", "--help"])

            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("worktree create [-h] [label]", p.stdout)
            self.assertIn("Optional lowercase label", p.stdout)

    def test_worktree_create_uses_current_branch_with_slash_for_branch_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            target.mkdir()
            self._prepare_git_repo(target)
            self._run_git(target, ["checkout", "-b", "feature/base"])

            p = self._run_runtime_capture(target, ["worktree", "create", "slice"])

            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("id=slice branch=feature/base-slice", p.stdout)

    def test_worktree_create_runs_make_init_when_available(self) -> None:
        if shutil.which("make") is None:
            self.skipTest("make not available")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            target.mkdir()
            (target / "Makefile").write_text("init:\n\t@echo initialized > .init-ran\n", encoding="utf-8")
            self._prepare_git_repo(target)

            p = self._run_runtime_capture(target, ["worktree", "create", "setup"])

            worktree_path = target.parent / "sample-repo-worktrees" / "sample-repo-setup"
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("bootstrap status=succeeded", p.stdout)
            self.assertEqual((worktree_path / ".init-ran").read_text(encoding="utf-8").strip(), "initialized")

    def test_worktree_create_keeps_worktree_when_make_init_fails(self) -> None:
        if shutil.which("make") is None:
            self.skipTest("make not available")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            target.mkdir()
            (target / "Makefile").write_text("init:\n\t@exit 7\n", encoding="utf-8")
            self._prepare_git_repo(target)

            p = self._run_runtime_capture(target, ["worktree", "create", "setup"])

            worktree_path = target.parent / "sample-repo-worktrees" / "sample-repo-setup"
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("bootstrap status=failed", p.stdout)
            self.assertIn("spec-dock: (warn) make init failed:", p.stderr)
            self.assertTrue(worktree_path.is_dir())
            current_branch = self._run_git(target, ["branch", "--show-current"]).stdout.strip()
            self.assertIn(
                f"branch refs/heads/{current_branch}-setup",
                self._run_git(target, ["worktree", "list", "--porcelain"]).stdout,
            )

    def test_worktree_create_keeps_worktree_when_make_init_detection_fails(self) -> None:
        if shutil.which("make") is None:
            self.skipTest("make not available")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            target.mkdir()
            (target / "Makefile").write_text("include missing.mk\ninit:\n\t@true\n", encoding="utf-8")
            self._prepare_git_repo(target)

            p = self._run_runtime_capture(target, ["worktree", "create", "detect"])

            worktree_path = target.parent / "sample-repo-worktrees" / "sample-repo-detect"
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("bootstrap status=detection_failed", p.stdout)
            self.assertIn("spec-dock: (warn) make init detection failed:", p.stderr)
            self.assertTrue(worktree_path.is_dir())

    def test_worktree_create_fails_from_detached_head(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            target.mkdir()
            self._prepare_git_repo(target)
            head = self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip()
            self._run_git(target, ["checkout", "--detach", head])

            p = self._run_runtime_capture(target, ["worktree", "create"])

            self.assertNotEqual(p.returncode, 0)
            self.assertIn("detached HEAD is not supported", p.stderr)
            self.assertFalse((target.parent / "sample-repo-worktrees").exists())

    def test_worktree_create_fails_outside_git_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "plain-dir"
            target.mkdir()
            self.assertEqual(main(["init", str(target)]), 0)

            p = self._run_runtime_capture(target, ["worktree", "create"])

            self.assertNotEqual(p.returncode, 0)
            self.assertIn("git failed: git rev-parse --abbrev-ref HEAD", p.stderr)

    def test_worktree_create_fails_when_container_path_is_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            target.mkdir()
            self._prepare_git_repo(target)
            (target.parent / "sample-repo-worktrees").write_text("not a directory\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["worktree", "create"])

            self.assertNotEqual(p.returncode, 0)
            self.assertIn("failed to create worktree container", p.stderr)
            self.assertIn("artifact_state=path_exists:False,branch_exists:False,record_exists:False", p.stderr)
            self.assertFalse((target.parent / "sample-repo-worktrees" / "sample-repo-wt1").exists())

    def test_worktree_create_treats_non_collision_git_add_failure_as_fatal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
            sys_path_inserted = False

            if str(runtime_scripts_dir) not in sys.path:
                sys.path.insert(0, str(runtime_scripts_dir))
                sys_path_inserted = True
            try:
                from spec_dock_runtime.application import contracts as app_contracts
                from spec_dock_runtime.application import ports as app_ports
                from spec_dock_runtime.application import worktree as app_worktree
            finally:
                if sys_path_inserted:
                    sys.path.pop(0)

            class FakeGitGateway:
                def __init__(self) -> None:
                    self.list_calls = 0

                def current_branch_or_none(self, repo_root):
                    return "main"

                def worktree_list(self, repo_root):
                    self.list_calls += 1
                    if self.list_calls == 1:
                        return [app_contracts.GitWorktreeRecord(path=Path(tmp) / "repo", head="abc", branch="main")]
                    return [
                        app_contracts.GitWorktreeRecord(path=Path(tmp) / "repo", head="abc", branch="main"),
                        app_contracts.GitWorktreeRecord(
                            path=Path(tmp) / "repo-worktrees" / "repo-wt1",
                            head="abc",
                            branch="main-wt1",
                        ),
                    ]

                def local_branch_exists(self, repo_root, branch):
                    return False

                def check_ref_format_branch(self, repo_root, branch):
                    return True

                def add_worktree_with_new_branch(self, repo_root, *, path, branch):
                    raise RuntimeError("git failed: git worktree add\nfatal: cannot lock ref 'refs/heads/main-wt1': Permission denied")

            class FakeBootstrapGateway:
                def run_make_init_if_available(self, worktree_path):
                    raise AssertionError("bootstrap must not run after git add failure")

            ports = app_ports.Ports(
                node_reader=object(),
                repo_root=Path(tmp) / "repo",
                git_gateway=FakeGitGateway(),
                bootstrap_gateway=FakeBootstrapGateway(),
            )

            with self.assertRaises(RuntimeError) as raised:
                app_worktree.worktree_create(app_contracts.WorktreeCreateRequest(), ports)

            message = str(raised.exception)
            self.assertIn("non-retryable", message)
            self.assertIn("cannot lock ref", message)
            self.assertIn("artifact_state=path_exists:False,branch_exists:False,record_exists:True", message)
            self.assertNotIn("exhausted candidate attempts", message)

    def test_worktree_create_retries_git_add_collision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
            sys_path_inserted = False

            if str(runtime_scripts_dir) not in sys.path:
                sys.path.insert(0, str(runtime_scripts_dir))
                sys_path_inserted = True
            try:
                from spec_dock_runtime.application import contracts as app_contracts
                from spec_dock_runtime.application import ports as app_ports
                from spec_dock_runtime.application import worktree as app_worktree
            finally:
                if sys_path_inserted:
                    sys.path.pop(0)

            class FakeGitGateway:
                def __init__(self) -> None:
                    self.add_calls: list[tuple[Path, str]] = []

                def current_branch_or_none(self, repo_root):
                    return "main"

                def worktree_list(self, repo_root):
                    return [app_contracts.GitWorktreeRecord(path=Path(tmp) / "repo", head="abc", branch="main")]

                def local_branch_exists(self, repo_root, branch):
                    return False

                def check_ref_format_branch(self, repo_root, branch):
                    return True

                def add_worktree_with_new_branch(self, repo_root, *, path, branch):
                    self.add_calls.append((path, branch))
                    if len(self.add_calls) == 1:
                        raise RuntimeError("git failed: fatal: a branch named 'main-wt1' already exists")

            class FakeBootstrapGateway:
                def run_make_init_if_available(self, worktree_path):
                    return app_contracts.BootstrapResult(
                        status="skipped",
                        command="make init",
                        exit_code=None,
                        warnings=[],
                    )

            git_gateway = FakeGitGateway()
            ports = app_ports.Ports(
                node_reader=object(),
                repo_root=Path(tmp) / "repo",
                git_gateway=git_gateway,
                bootstrap_gateway=FakeBootstrapGateway(),
            )

            result = app_worktree.worktree_create(app_contracts.WorktreeCreateRequest(), ports)

            self.assertEqual(result.id, "wt2")
            self.assertEqual([branch for _, branch in git_gateway.add_calls], ["main-wt1", "main-wt2"])

    def test_worktree_create_normalizes_container_from_linked_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            target.mkdir()
            self._prepare_git_repo(target)
            first = self._run_runtime_capture(target, ["worktree", "create", "outer"])
            self.assertEqual(first.returncode, 0, first.stderr)
            linked = target.parent / "sample-repo-worktrees" / "sample-repo-outer"

            p = subprocess.run(
                [str(linked / "spec-dock" / "scripts" / "spec-dock"), "worktree", "create", "inner"],
                cwd=str(linked),
                env=os.environ.copy(),
                capture_output=True,
                text=True,
            )

            expected = (target.parent / "sample-repo-worktrees" / "sample-repo-inner").resolve()
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn(f"path={expected}", p.stdout)
            current_branch = self._run_git(linked, ["branch", "--show-current"]).stdout.strip()
            self.assertIn(f"branch={current_branch}-inner", p.stdout)
            self.assertTrue(expected.is_dir())
