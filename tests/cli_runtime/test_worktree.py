import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestCliWorktree(CliRuntimeHarness):
    def _worktree_env(self, root: Path | str) -> dict[str, str]:
        return {"SPEC_DOCK_WORKTREE_ROOT": str(root)}

    def _assert_no_sibling_container(self, target: Path) -> None:
        self.assertFalse((target.parent / f"{target.name}-worktrees").exists())

    def _run_runtime_capture_exact_env(self, target: Path, args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
        script = target / "spec-dock" / "scripts" / "spec-dock"
        self.assertTrue(script.is_file(), f"runtime script missing: {script}")
        return subprocess.run(
            [sys.executable, str(script), *args],
            cwd=str(target),
            env=env,
            capture_output=True,
            text=True,
        )

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

    def test_worktree_create_requires_env_without_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            target.mkdir()
            self._prepare_git_repo(target)

            env = os.environ.copy()
            env.pop("SPEC_DOCK_WORKTREE_ROOT", None)
            p = self._run_runtime_capture_exact_env(target, ["worktree", "create"], env=env)

            self.assertNotEqual(p.returncode, 0)
            self.assertIn("SPEC_DOCK_WORKTREE_ROOT is required", p.stderr)
            self.assertIn("export SPEC_DOCK_WORKTREE_ROOT", p.stderr)
            self._assert_no_sibling_container(target)
            self.assertFalse((Path(tmp) / "worktrees").exists())
            self.assertNotIn("-wt1", self._run_git(target, ["branch", "--list"]).stdout)

    def test_worktree_create_rejects_blank_env_without_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            target.mkdir()
            self._prepare_git_repo(target)

            p = self._run_runtime_capture(target, ["worktree", "create"], env=self._worktree_env("   "))

            self.assertNotEqual(p.returncode, 0)
            self.assertIn("SPEC_DOCK_WORKTREE_ROOT is required", p.stderr)
            self._assert_no_sibling_container(target)
            self.assertNotIn("-wt1", self._run_git(target, ["branch", "--list"]).stdout)

    def test_worktree_create_uses_central_root_auto_id_and_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            central_root = Path(tmp) / "central-worktrees"
            target.mkdir()
            self._prepare_git_repo(target)

            p = self._run_runtime_capture(target, ["worktree", "create"], env=self._worktree_env(central_root))

            self.assertEqual(p.returncode, 0, p.stderr)
            current_branch = self._run_git(target, ["branch", "--show-current"]).stdout.strip()
            expected_path = central_root / "sample-repo" / "sample-repo-wt1"
            self.assertIn(f"id=wt1", p.stdout)
            self.assertIn(f"path={expected_path}", p.stdout)
            self.assertIn("bootstrap status=skipped", p.stdout)
            self.assertTrue(expected_path.is_dir())
            self.assertTrue((expected_path / "spec-dock" / "scripts" / "spec-dock").is_file())
            self._assert_no_sibling_container(target)
            worktree_list = self._run_git(target, ["worktree", "list", "--porcelain"]).stdout
            self.assertIn(str(expected_path.resolve()), worktree_list)
            self.assertIn(f"branch refs/heads/{current_branch}-wt1", worktree_list)

    def test_worktree_create_retries_collisions_and_accepts_label(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            central_root = Path(tmp) / "central-worktrees"
            target.mkdir()
            self._prepare_git_repo(target)
            first = self._run_runtime_capture(target, ["worktree", "create", "feature"], env=self._worktree_env(central_root))
            second = self._run_runtime_capture(target, ["worktree", "create", "feature"], env=self._worktree_env(central_root))

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            current_branch = self._run_git(target, ["branch", "--show-current"]).stdout.strip()
            self.assertIn(f"id=feature branch={current_branch}-feature", first.stdout)
            self.assertIn(f"id=feature2 branch={current_branch}-feature2", second.stdout)

    def test_worktree_create_retries_auto_id_collisions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            central_root = Path(tmp) / "central-worktrees"
            target.mkdir()
            self._prepare_git_repo(target)
            first = self._run_runtime_capture(target, ["worktree", "create"], env=self._worktree_env(central_root))
            second = self._run_runtime_capture(target, ["worktree", "create"], env=self._worktree_env(central_root))

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            current_branch = self._run_git(target, ["branch", "--show-current"]).stdout.strip()
            self.assertIn(f"id=wt1 branch={current_branch}-wt1", first.stdout)
            self.assertIn(f"id=wt2 branch={current_branch}-wt2", second.stdout)

    def test_worktree_create_rejects_relative_root_without_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            target.mkdir()
            self._prepare_git_repo(target)

            p = self._run_runtime_capture(target, ["worktree", "create"], env=self._worktree_env("relative/worktrees"))

            self.assertNotEqual(p.returncode, 0)
            self.assertIn("invalid SPEC_DOCK_WORKTREE_ROOT", p.stderr)
            self.assertIn("raw='relative/worktrees'", p.stderr)
            self.assertIn("cause=path is relative", p.stderr)
            self.assertIn("export SPEC_DOCK_WORKTREE_ROOT", p.stderr)
            self._assert_no_sibling_container(target)

    def test_worktree_create_rejects_file_root_without_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            root_file = Path(tmp) / "root-file"
            root_file.write_text("not a directory\n", encoding="utf-8")
            target.mkdir()
            self._prepare_git_repo(target)

            p = self._run_runtime_capture(target, ["worktree", "create"], env=self._worktree_env(root_file))

            self.assertNotEqual(p.returncode, 0)
            self.assertIn("invalid SPEC_DOCK_WORKTREE_ROOT", p.stderr)
            self.assertIn("cause=path is not a directory", p.stderr)
            self.assertIn(str(root_file), p.stderr)
            self.assertFalse((Path(tmp) / "root-file" / "sample-repo").exists())

    def test_worktree_create_rejects_broken_symlink_root_without_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            target.mkdir()
            self._prepare_git_repo(target)
            if not self._can_create_symlink(Path(tmp)):
                self.skipTest("symlink not available")
            broken = Path(tmp) / "broken-root"
            os.symlink(Path(tmp) / "missing-root", broken)

            p = self._run_runtime_capture(target, ["worktree", "create"], env=self._worktree_env(broken))

            self.assertNotEqual(p.returncode, 0)
            self.assertIn("invalid SPEC_DOCK_WORKTREE_ROOT", p.stderr)
            self.assertIn("cause=path is a broken symlink", p.stderr)
            self.assertFalse((Path(tmp) / "missing-root").exists())

    def test_worktree_create_accepts_directory_symlink_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            real_root = Path(tmp) / "real-worktrees"
            symlink_root = Path(tmp) / "linked-worktrees"
            target.mkdir()
            real_root.mkdir()
            self._prepare_git_repo(target)
            if not self._can_create_symlink(Path(tmp)):
                self.skipTest("symlink not available")
            os.symlink(real_root, symlink_root)

            p = self._run_runtime_capture(target, ["worktree", "create"], env=self._worktree_env(symlink_root))

            expected_path = symlink_root / "sample-repo" / "sample-repo-wt1"
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn(f"path={expected_path}", p.stdout)
            self.assertTrue(expected_path.is_dir())

    def test_worktree_create_expands_tilde_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            fake_home = Path(tmp) / "home"
            root = fake_home / "workspace" / "worktrees"
            target.mkdir()
            fake_home.mkdir()
            self._prepare_git_repo(target)
            env = self._worktree_env("~/workspace/worktrees")
            env["HOME"] = str(fake_home)

            p = self._run_runtime_capture(target, ["worktree", "create"], env=env)

            expected_path = root / "sample-repo" / "sample-repo-wt1"
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn(f"path={expected_path}", p.stdout)
            self.assertTrue(expected_path.is_dir())

    def test_worktree_create_rejects_invalid_labels_without_creating_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            central_root = Path(tmp) / "central-worktrees"
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
                    p = self._run_runtime_capture(
                        target,
                        ["worktree", "create", label],
                        env=self._worktree_env(central_root),
                    )

                    self.assertNotEqual(p.returncode, 0)
                    self.assertIn("invalid worktree label", p.stderr)
                    self.assertFalse((central_root / "sample-repo").exists())
                    self.assertFalse((target / ".init-ran").exists())
            self._assert_no_sibling_container(target)
            self.assertNotIn("-bad", self._run_git(target, ["branch", "--list"]).stdout)

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
            central_root = Path(tmp) / "central-worktrees"
            target.mkdir()
            self._prepare_git_repo(target)
            self._run_git(target, ["checkout", "-b", "feature/base"])

            p = self._run_runtime_capture(target, ["worktree", "create", "slice"], env=self._worktree_env(central_root))

            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("id=slice branch=feature/base-slice", p.stdout)

    def test_worktree_create_runs_make_init_when_available(self) -> None:
        if shutil.which("make") is None:
            self.skipTest("make not available")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            central_root = Path(tmp) / "central-worktrees"
            target.mkdir()
            (target / "Makefile").write_text("init:\n\t@echo initialized > .init-ran\n", encoding="utf-8")
            self._prepare_git_repo(target)

            p = self._run_runtime_capture(target, ["worktree", "create", "setup"], env=self._worktree_env(central_root))

            worktree_path = central_root / "sample-repo" / "sample-repo-setup"
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("bootstrap status=succeeded", p.stdout)
            self.assertEqual((worktree_path / ".init-ran").read_text(encoding="utf-8").strip(), "initialized")

    def test_worktree_create_keeps_worktree_when_make_init_fails(self) -> None:
        if shutil.which("make") is None:
            self.skipTest("make not available")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            central_root = Path(tmp) / "central-worktrees"
            target.mkdir()
            (target / "Makefile").write_text("init:\n\t@exit 7\n", encoding="utf-8")
            self._prepare_git_repo(target)

            p = self._run_runtime_capture(target, ["worktree", "create", "setup"], env=self._worktree_env(central_root))

            worktree_path = central_root / "sample-repo" / "sample-repo-setup"
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
            central_root = Path(tmp) / "central-worktrees"
            target.mkdir()
            (target / "Makefile").write_text("include missing.mk\ninit:\n\t@true\n", encoding="utf-8")
            self._prepare_git_repo(target)

            p = self._run_runtime_capture(target, ["worktree", "create", "detect"], env=self._worktree_env(central_root))

            worktree_path = central_root / "sample-repo" / "sample-repo-detect"
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("bootstrap status=detection_failed", p.stdout)
            self.assertIn("spec-dock: (warn) make init detection failed:", p.stderr)
            self.assertTrue(worktree_path.is_dir())

    def test_worktree_create_fails_from_detached_head(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            central_root = Path(tmp) / "central-worktrees"
            target.mkdir()
            self._prepare_git_repo(target)
            head = self._run_git(target, ["rev-parse", "HEAD"]).stdout.strip()
            self._run_git(target, ["checkout", "--detach", head])

            p = self._run_runtime_capture(target, ["worktree", "create"], env=self._worktree_env(central_root))

            self.assertNotEqual(p.returncode, 0)
            self.assertIn("detached HEAD is not supported", p.stderr)
            self.assertFalse((target.parent / "sample-repo-worktrees").exists())

    def test_worktree_create_fails_outside_git_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "plain-dir"
            central_root = Path(tmp) / "central-worktrees"
            target.mkdir()
            self.assertEqual(main(["init", str(target)]), 0)

            p = self._run_runtime_capture(target, ["worktree", "create"], env=self._worktree_env(central_root))

            self.assertNotEqual(p.returncode, 0)
            self.assertIn("git failed: git rev-parse --abbrev-ref HEAD", p.stderr)

    def test_worktree_create_fails_when_namespace_path_is_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            central_root = Path(tmp) / "central-worktrees"
            target.mkdir()
            central_root.mkdir()
            self._prepare_git_repo(target)
            (central_root / "sample-repo").write_text("not a directory\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["worktree", "create"], env=self._worktree_env(central_root))

            self.assertNotEqual(p.returncode, 0)
            self.assertIn("failed to create worktree container", p.stderr)
            self.assertIn("SPEC_DOCK_WORKTREE_ROOT", p.stderr)
            self.assertIn("artifact_state=path_exists:False,branch_exists:False,record_exists:False", p.stderr)
            self.assertFalse((central_root / "sample-repo" / "sample-repo-wt1").exists())

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
                            path=Path(tmp) / "central-worktrees" / "repo" / "repo-wt1",
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

            class FakeEnvironmentGateway:
                def getenv(self, name):
                    return str(Path(tmp) / "central-worktrees")

            ports = app_ports.Ports(
                node_reader=object(),
                repo_root=Path(tmp) / "repo",
                git_gateway=FakeGitGateway(),
                bootstrap_gateway=FakeBootstrapGateway(),
                environment_gateway=FakeEnvironmentGateway(),
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

            class FakeEnvironmentGateway:
                def getenv(self, name):
                    return str(Path(tmp) / "central-worktrees")

            git_gateway = FakeGitGateway()
            ports = app_ports.Ports(
                node_reader=object(),
                repo_root=Path(tmp) / "repo",
                git_gateway=git_gateway,
                bootstrap_gateway=FakeBootstrapGateway(),
                environment_gateway=FakeEnvironmentGateway(),
            )

            result = app_worktree.worktree_create(app_contracts.WorktreeCreateRequest(), ports)

            self.assertEqual(result.id, "wt2")
            self.assertEqual([branch for _, branch in git_gateway.add_calls], ["main-wt1", "main-wt2"])
            self.assertEqual(
                [path for path, _ in git_gateway.add_calls],
                [
                    Path(tmp) / "central-worktrees" / "repo" / "repo-wt1",
                    Path(tmp) / "central-worktrees" / "repo" / "repo-wt2",
                ],
            )

    def test_worktree_create_normalizes_container_from_linked_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            central_root = Path(tmp) / "central-worktrees"
            target.mkdir()
            self._prepare_git_repo(target)
            first = self._run_runtime_capture(target, ["worktree", "create", "outer"], env=self._worktree_env(central_root))
            self.assertEqual(first.returncode, 0, first.stderr)
            linked = central_root / "sample-repo" / "sample-repo-outer"
            env = os.environ.copy()
            env["SPEC_DOCK_WORKTREE_ROOT"] = str(central_root)

            p = subprocess.run(
                [str(linked / "spec-dock" / "scripts" / "spec-dock"), "worktree", "create", "inner"],
                cwd=str(linked),
                env=env,
                capture_output=True,
                text=True,
            )

            expected = central_root / "sample-repo" / "sample-repo-inner"
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn(f"path={expected}", p.stdout)
            current_branch = self._run_git(linked, ["branch", "--show-current"]).stdout.strip()
            self.assertIn(f"branch={current_branch}-inner", p.stdout)
            self.assertTrue(expected.is_dir())
