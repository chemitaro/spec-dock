import json
import os
import shutil
import subprocess
import sys
import tempfile
from unittest import mock
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

    def test_worktree_list_and_show_json_resolve_agent_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            central_root = Path(tmp) / "central-worktrees"
            duplicate_parent = central_root / target.name / "duplicates"
            duplicate = duplicate_parent / "sample-repo-alpha"
            target.mkdir()
            self._prepare_git_repo(target)

            create = self._run_runtime_capture(target, ["worktree", "create", "alpha"], env=self._worktree_env(central_root))
            self.assertEqual(create.returncode, 0, create.stderr)

            listed = self._run_runtime_capture(target, ["worktree", "list", "--json"], env=self._worktree_env(central_root))
            self.assertEqual(listed.returncode, 0, listed.stderr)
            payload = json.loads(listed.stdout)
            self.assertEqual(payload["status"], "ok")
            alpha = next(item for item in payload["worktrees"] if item["id"] == "alpha")
            self.assertTrue(alpha["managed"])
            self.assertFalse(alpha["main"])
            self.assertFalse(alpha["current"])
            self.assertTrue(alpha["removable"])
            text_listed = self._run_runtime_capture(target, ["worktree", "list"], env=self._worktree_env(central_root))
            self.assertEqual(text_listed.returncode, 0, text_listed.stderr)
            self.assertIn("id=alpha", text_listed.stdout)
            self.assertIn("managed=true", text_listed.stdout)
            self.assertIn("removable=true", text_listed.stdout)

            for selector in (alpha["id"], alpha["path"]):
                shown = self._run_runtime_capture(target, ["worktree", "show", selector, "--json"], env=self._worktree_env(central_root))
                self.assertEqual(shown.returncode, 0, shown.stderr)
                shown_payload = json.loads(shown.stdout)
                self.assertEqual(shown_payload["worktree"]["path"], alpha["path"])

            text_shown = self._run_runtime_capture(target, ["worktree", "show", alpha["id"]], env=self._worktree_env(central_root))
            self.assertEqual(text_shown.returncode, 0, text_shown.stderr)
            self.assertIn("id=alpha", text_shown.stdout)
            self.assertIn("managed=true", text_shown.stdout)

            shown_by_basename = self._run_runtime_capture(
                target,
                ["worktree", "show", alpha["basename"], "--json"],
                env=self._worktree_env(central_root),
            )
            self.assertEqual(shown_by_basename.returncode, 0, shown_by_basename.stderr)
            self.assertEqual(json.loads(shown_by_basename.stdout)["worktree"]["path"], alpha["path"])

            duplicate_parent.mkdir(parents=True)
            self._run_git(target, ["worktree", "add", "-b", "manual-alpha", str(duplicate)])

            ambiguous = self._run_runtime_capture(
                target,
                ["worktree", "show", alpha["basename"], "--json"],
                env=self._worktree_env(central_root),
            )
            self.assertNotEqual(ambiguous.returncode, 0)
            ambiguous_payload = json.loads(ambiguous.stdout)
            self.assertEqual(ambiguous_payload["status"], "error")
            self.assertEqual(ambiguous_payload["error"]["code"], "ambiguous_target")
            self.assertEqual({item["id"] for item in ambiguous_payload["candidates"]}, {"alpha", "alpha~2"})
            self.assertTrue(all(item["basename"] == alpha["basename"] for item in ambiguous_payload["candidates"]))

            branch_only = self._run_runtime_capture(
                target,
                ["worktree", "show", alpha["branch"], "--json"],
                env=self._worktree_env(central_root),
            )
            self.assertNotEqual(branch_only.returncode, 0)
            error_payload = json.loads(branch_only.stdout)
            self.assertEqual(error_payload["status"], "error")
            self.assertEqual(error_payload["error"]["code"], "unsupported_branch_target")

    def test_worktree_list_json_fails_fast_when_root_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            target.mkdir()
            self._prepare_git_repo(target)

            p = self._run_runtime_capture(target, ["worktree", "list", "--json"], env=self._worktree_env("relative/worktrees"))

            self.assertNotEqual(p.returncode, 0)
            payload = json.loads(p.stdout)
            self.assertEqual(payload["status"], "error")
            self.assertEqual(payload["error"]["code"], "invalid_worktree_root")

    def test_worktree_json_commands_fail_fast_for_invalid_root_variants(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            target.mkdir()
            self._prepare_git_repo(target)
            root_file = Path(tmp) / "root-file"
            root_file.write_text("not a directory\n", encoding="utf-8")
            broken_symlink = Path(tmp) / "broken-root"
            if not self._can_create_symlink(Path(tmp)):
                self.skipTest("symlink unavailable")
            os.symlink(Path(tmp) / "missing-root", broken_symlink)
            cases: list[tuple[str, dict[str, str], str]] = [
                ("missing", {}, "worktree_root_required"),
                ("blank", self._worktree_env("   "), "worktree_root_required"),
                ("relative", self._worktree_env("relative/worktrees"), "invalid_worktree_root"),
                ("file", self._worktree_env(root_file), "invalid_worktree_root"),
                ("broken-symlink", self._worktree_env(broken_symlink), "invalid_worktree_root"),
            ]
            commands = (
                ["worktree", "list", "--json"],
                ["worktree", "show", "anything", "--json"],
                ["worktree", "remove", "anything", "--json"],
            )
            base_env = os.environ.copy()
            base_env.pop("SPEC_DOCK_WORKTREE_ROOT", None)

            for label, env_update, expected_code in cases:
                env = dict(base_env)
                env.update(env_update)
                for command in commands:
                    with self.subTest(root=label, command=" ".join(command)):
                        p = self._run_runtime_capture_exact_env(target, command, env=env)
                        self.assertNotEqual(p.returncode, 0)
                        self.assertEqual(p.stderr, "")
                        payload = json.loads(p.stdout)
                        self.assertEqual(payload["status"], "error")
                        self.assertEqual(payload["error"]["code"], expected_code)
                        self.assertEqual(self._run_git(target, ["worktree", "list", "--porcelain"]).returncode, 0)

    def test_worktree_list_json_classifies_unmanaged_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            central_root = Path(tmp) / "central-worktrees"
            unmanaged = Path(tmp) / "manual-worktree"
            target.mkdir()
            self._prepare_git_repo(target)
            self._run_git(target, ["worktree", "add", "-b", "manual", str(unmanaged)])

            listed = self._run_runtime_capture(target, ["worktree", "list", "--json"], env=self._worktree_env(central_root))

            self.assertEqual(listed.returncode, 0, listed.stderr)
            payload = json.loads(listed.stdout)
            manual = next(item for item in payload["worktrees"] if item["basename"] == "manual-worktree")
            self.assertFalse(manual["managed"])
            self.assertFalse(manual["removable"])
            self.assertIn("unmanaged", manual["remove_blockers"])

    def test_worktree_remove_clean_managed_target_keeps_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "repositories" / "sample-repo"
            central_root = Path(tmp) / "central-worktrees"
            target.parent.mkdir()
            target.mkdir()
            self._prepare_git_repo(target)

            created = self._run_runtime_capture(target, ["worktree", "create", "done"], env=self._worktree_env(central_root))
            self.assertEqual(created.returncode, 0, created.stderr)
            worktree_path = central_root / "sample-repo" / "sample-repo-done"
            branch = self._run_git(target, ["branch", "--list", "*-done", "--format=%(refname:short)"]).stdout.strip()

            removed = self._run_runtime_capture(
                target,
                ["worktree", "remove", "done", "--json"],
                env=self._worktree_env(central_root),
            )

            self.assertEqual(removed.returncode, 0, removed.stderr)
            payload = json.loads(removed.stdout)
            self.assertEqual(payload["status"], "ok")
            self.assertTrue(payload["removed_record"])
            self.assertTrue(payload["removed_directory"])
            self.assertFalse(payload["branch_deleted"])
            self.assertFalse(worktree_path.exists())
            self.assertNotIn(str(worktree_path), self._run_git(target, ["worktree", "list", "--porcelain"]).stdout)
            self.assertIn(branch, self._run_git(target, ["branch", "--list", branch]).stdout)

    def test_worktree_remove_dirty_default_fails_and_force_removes_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            central_root = Path(tmp) / "central-worktrees"
            target.mkdir()
            self._prepare_git_repo(target)

            created = self._run_runtime_capture(target, ["worktree", "create", "dirty"], env=self._worktree_env(central_root))
            self.assertEqual(created.returncode, 0, created.stderr)
            worktree_path = central_root / "sample-repo" / "sample-repo-dirty"
            (worktree_path / "cache.tmp").write_text("dirty\n", encoding="utf-8")

            failed = self._run_runtime_capture(
                target,
                ["worktree", "remove", "dirty", "--json"],
                env=self._worktree_env(central_root),
            )
            self.assertNotEqual(failed.returncode, 0)
            failed_payload = json.loads(failed.stdout)
            self.assertEqual(failed_payload["error"]["code"], "git_worktree_remove_failed")
            self.assertTrue(worktree_path.exists())

            forced = self._run_runtime_capture(
                target,
                ["worktree", "remove", "dirty", "--force", "--json"],
                env=self._worktree_env(central_root),
            )
            self.assertEqual(forced.returncode, 0, forced.stderr)
            forced_payload = json.loads(forced.stdout)
            self.assertTrue(forced_payload["removed_record"])
            self.assertTrue(forced_payload["removed_directory"])
            self.assertFalse(worktree_path.exists())

    def test_worktree_remove_locked_default_fails_and_force_follows_git(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            central_root = Path(tmp) / "central-worktrees"
            target.mkdir()
            self._prepare_git_repo(target)

            created = self._run_runtime_capture(target, ["worktree", "create", "locked"], env=self._worktree_env(central_root))
            self.assertEqual(created.returncode, 0, created.stderr)
            worktree_path = central_root / "sample-repo" / "sample-repo-locked"
            lock = self._run_git(target, ["worktree", "lock", str(worktree_path)], check=False)
            if lock.returncode != 0:
                self.skipTest(f"git worktree lock unavailable: {lock.stderr}")

            failed = self._run_runtime_capture(
                target,
                ["worktree", "remove", "locked", "--json"],
                env=self._worktree_env(central_root),
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertTrue(worktree_path.exists())
            failed_payload = json.loads(failed.stdout)
            self.assertEqual(failed_payload["error"]["code"], "git_worktree_remove_failed")

            forced = self._run_runtime_capture(
                target,
                ["worktree", "remove", "locked", "--force", "--json"],
                env=self._worktree_env(central_root),
            )
            if forced.returncode != 0:
                unlock = self._run_git(target, ["worktree", "unlock", str(worktree_path)], check=False)
                self.assertEqual(unlock.returncode, 0, unlock.stderr)
                self.skipTest(f"git worktree remove --force did not remove locked worktree: {forced.stderr or forced.stdout}")
            forced_payload = json.loads(forced.stdout)
            self.assertTrue(forced_payload["removed_record"])
            self.assertTrue(forced_payload["removed_directory"])
            self.assertFalse(worktree_path.exists())

    def test_worktree_remove_rejects_branch_target_and_invalid_root_without_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            central_root = Path(tmp) / "central-worktrees"
            target.mkdir()
            self._prepare_git_repo(target)
            created = self._run_runtime_capture(target, ["worktree", "create", "branchy"], env=self._worktree_env(central_root))
            self.assertEqual(created.returncode, 0, created.stderr)
            listed = self._run_runtime_capture(target, ["worktree", "list", "--json"], env=self._worktree_env(central_root))
            branchy = next(item for item in json.loads(listed.stdout)["worktrees"] if item["id"] == "branchy")

            branch_target = self._run_runtime_capture(
                target,
                ["worktree", "remove", branchy["branch"], "--json"],
                env=self._worktree_env(central_root),
            )
            self.assertNotEqual(branch_target.returncode, 0)
            branch_payload = json.loads(branch_target.stdout)
            self.assertEqual(branch_payload["error"]["code"], "unsupported_branch_target")
            self.assertTrue(Path(branchy["path"]).exists())
            self.assertIn(branchy["path"], self._run_git(target, ["worktree", "list", "--porcelain"]).stdout)

            invalid_root = self._run_runtime_capture(
                target,
                ["worktree", "remove", "branchy", "--json"],
                env=self._worktree_env("relative/worktrees"),
            )
            self.assertNotEqual(invalid_root.returncode, 0)
            invalid_payload = json.loads(invalid_root.stdout)
            self.assertEqual(invalid_payload["error"]["code"], "invalid_worktree_root")
            self.assertTrue(Path(branchy["path"]).exists())
            self.assertIn(branchy["path"], self._run_git(target, ["worktree", "list", "--porcelain"]).stdout)

    def test_worktree_remove_rejects_main_and_delete_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            central_root = Path(tmp) / "central-worktrees"
            target.mkdir()
            self._prepare_git_repo(target)

            main_remove = self._run_runtime_capture(
                target,
                ["worktree", "remove", "main", "--force", "--json"],
                env=self._worktree_env(central_root),
            )
            self.assertNotEqual(main_remove.returncode, 0)
            payload = json.loads(main_remove.stdout)
            self.assertEqual(payload["error"]["code"], "remove_blocked")
            self.assertIn("main_worktree", payload["remove_blockers"])
            self.assertTrue(target.exists())

            delete_alias = self._run_runtime_capture(target, ["worktree", "delete", "main"], env=self._worktree_env(central_root))
            self.assertNotEqual(delete_alias.returncode, 0)
            self.assertIn("invalid choice", delete_alias.stderr)

    def test_worktree_remove_rejects_current_unmanaged_and_ambiguous_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            central_root = Path(tmp) / "central-worktrees"
            unmanaged = Path(tmp) / "manual-worktree"
            duplicate_parent = Path(tmp) / "duplicates"
            duplicate = duplicate_parent / "sample-repo-dupe"
            target.mkdir()
            duplicate_parent.mkdir()
            self._prepare_git_repo(target)

            first = self._run_runtime_capture(target, ["worktree", "create", "current"], env=self._worktree_env(central_root))
            self.assertEqual(first.returncode, 0, first.stderr)
            current_path = central_root / "sample-repo" / "sample-repo-current"
            env = self._worktree_env(central_root)
            current_remove = subprocess.run(
                [str(current_path / "spec-dock" / "scripts" / "spec-dock"), "worktree", "remove", "current", "--force", "--json"],
                cwd=str(current_path),
                env={**os.environ.copy(), **env},
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(current_remove.returncode, 0)
            current_payload = json.loads(current_remove.stdout)
            self.assertEqual(current_payload["error"]["code"], "remove_blocked")
            self.assertIn("current_worktree", current_payload["remove_blockers"])
            self.assertTrue(current_path.exists())

            self._run_git(target, ["worktree", "add", "-b", "manual", str(unmanaged)])
            unmanaged_remove = self._run_runtime_capture(
                target,
                ["worktree", "remove", unmanaged.name, "--force", "--json"],
                env=self._worktree_env(central_root),
            )
            self.assertNotEqual(unmanaged_remove.returncode, 0)
            unmanaged_payload = json.loads(unmanaged_remove.stdout)
            self.assertEqual(unmanaged_payload["error"]["code"], "remove_blocked")
            self.assertIn("unmanaged", unmanaged_payload["remove_blockers"])
            self.assertTrue(unmanaged.exists())

            dupe_created = self._run_runtime_capture(target, ["worktree", "create", "dupe"], env=self._worktree_env(central_root))
            self.assertEqual(dupe_created.returncode, 0, dupe_created.stderr)
            self._run_git(target, ["worktree", "add", "-b", "dupe", str(duplicate)])
            stable_id_remove = self._run_runtime_capture(
                target,
                ["worktree", "remove", "dupe", "--json"],
                env=self._worktree_env(central_root),
            )
            self.assertEqual(stable_id_remove.returncode, 0, stable_id_remove.stderr)
            stable_payload = json.loads(stable_id_remove.stdout)
            self.assertEqual(stable_payload["resolved_target"]["id"], "dupe")
            self.assertTrue(duplicate.exists())

    def test_worktree_remove_containment_blocks_namespace_and_symlink_escape_before_git_remove(self) -> None:
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

            repo_root = Path(tmp) / "repo"
            central_root = Path(tmp) / "central"
            namespace = central_root / "repo"
            escaped = Path(tmp) / "escaped"
            repo_root.mkdir()
            namespace.mkdir(parents=True)
            escaped.mkdir()
            if not self._can_create_symlink(Path(tmp)):
                self.skipTest("symlink unavailable")
            symlink_path = namespace / "repo-escape"
            os.symlink(escaped, symlink_path)

            class FakeGitGateway:
                def __init__(self, records):
                    self.records = records
                    self.remove_calls: list[Path] = []

                def worktree_list(self, repo_root_arg):
                    return self.records

                def remove_worktree(self, repo_root_arg, *, path, force):
                    self.remove_calls.append(path)

            class FakeEnvironmentGateway:
                def __init__(self, root):
                    self.root = root

                def getenv(self, name):
                    return str(self.root)

            class FakeFilesystemGateway:
                def path_exists(self, path):
                    return path.exists()

                def remove_tree(self, path):
                    raise AssertionError("remove_tree must not be called")

            for target, record_path in (
                (str(namespace), namespace),
                (str(symlink_path), symlink_path),
            ):
                git_gateway = FakeGitGateway(
                    [
                        app_contracts.GitWorktreeRecord(path=repo_root, head="abc", branch="main"),
                        app_contracts.GitWorktreeRecord(path=record_path, head="def", branch=f"main-{target}"),
                    ]
                )
                ports = app_ports.Ports(
                    node_reader=object(),
                    repo_root=repo_root,
                    git_gateway=git_gateway,
                    environment_gateway=FakeEnvironmentGateway(central_root),
                    filesystem_gateway=FakeFilesystemGateway(),
                )

                with self.assertRaises(app_contracts.WorktreeCommandError) as raised:
                    app_worktree.worktree_remove(app_contracts.WorktreeRemoveRequest(target=target, force=True), ports)

                self.assertEqual(raised.exception.code, "remove_blocked")
                self.assertEqual(git_gateway.remove_calls, [])
                self.assertTrue(record_path.exists())

            symlink_root = Path(tmp) / "central-with-symlink-namespace"
            symlink_root.mkdir()
            namespace_symlink = symlink_root / "repo"
            os.symlink(escaped, namespace_symlink)
            namespace_symlink_record = namespace_symlink / "repo-linked"
            namespace_symlink_record.touch()
            git_gateway = FakeGitGateway(
                [
                    app_contracts.GitWorktreeRecord(path=repo_root, head="abc", branch="main"),
                    app_contracts.GitWorktreeRecord(path=namespace_symlink_record, head="def", branch="main-linked"),
                ]
            )
            ports = app_ports.Ports(
                node_reader=object(),
                repo_root=repo_root,
                git_gateway=git_gateway,
                environment_gateway=FakeEnvironmentGateway(symlink_root),
                filesystem_gateway=FakeFilesystemGateway(),
            )

            with self.assertRaises(app_contracts.WorktreeCommandError) as raised:
                app_worktree.worktree_remove(
                    app_contracts.WorktreeRemoveRequest(target=str(namespace_symlink_record), force=True),
                    ports,
                )

            self.assertEqual(raised.exception.code, "remove_blocked")
            self.assertEqual(git_gateway.remove_calls, [])
            self.assertTrue(namespace_symlink_record.exists())

    def test_worktree_remove_cleans_leftover_directory_and_reports_cleanup_failure(self) -> None:
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

            repo_root = Path(tmp) / "repo"
            central_root = Path(tmp) / "central"
            worktree_path = central_root / "repo" / "repo-leftover"
            repo_root.mkdir()
            worktree_path.mkdir(parents=True)

            class FakeGitGateway:
                def __init__(self) -> None:
                    self.remove_calls: list[tuple[Path, bool]] = []

                def worktree_list(self, repo_root_arg):
                    return [
                        app_contracts.GitWorktreeRecord(path=repo_root, head="abc", branch="main"),
                        app_contracts.GitWorktreeRecord(path=worktree_path, head="def", branch="main-leftover"),
                    ]

                def remove_worktree(self, repo_root_arg, *, path, force):
                    self.remove_calls.append((path, force))

            class FakeEnvironmentGateway:
                def getenv(self, name):
                    return str(central_root)

            class FakeFilesystemGateway:
                def __init__(self, *, fail: bool = False) -> None:
                    self.fail = fail
                    self.remove_calls: list[Path] = []

                def path_exists(self, path):
                    return True

                def remove_tree(self, path):
                    self.remove_calls.append(path)
                    if self.fail:
                        raise RuntimeError("cleanup denied")

            git_gateway = FakeGitGateway()
            filesystem_gateway = FakeFilesystemGateway()
            ports = app_ports.Ports(
                node_reader=object(),
                repo_root=repo_root,
                git_gateway=git_gateway,
                environment_gateway=FakeEnvironmentGateway(),
                filesystem_gateway=filesystem_gateway,
            )

            result = app_worktree.worktree_remove(app_contracts.WorktreeRemoveRequest(target="leftover"), ports)

            self.assertTrue(result.removed_record)
            self.assertTrue(result.removed_directory)
            self.assertEqual(git_gateway.remove_calls, [(worktree_path, False)])
            self.assertEqual(filesystem_gateway.remove_calls, [worktree_path])

            failing_fs = FakeFilesystemGateway(fail=True)
            failing_ports = app_ports.Ports(
                node_reader=object(),
                repo_root=repo_root,
                git_gateway=FakeGitGateway(),
                environment_gateway=FakeEnvironmentGateway(),
                filesystem_gateway=failing_fs,
            )

            with self.assertRaises(app_contracts.WorktreeCommandError) as raised:
                app_worktree.worktree_remove(app_contracts.WorktreeRemoveRequest(target="leftover"), failing_ports)

            self.assertEqual(raised.exception.code, "post_remove_cleanup_failed")
            self.assertTrue(raised.exception.removed_record)
            self.assertFalse(raised.exception.removed_directory)
            self.assertEqual(failing_fs.remove_calls, [worktree_path])

    def test_worktree_remove_ambiguous_basename_stops_before_git_remove(self) -> None:
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

            repo_root = Path(tmp) / "repo"
            repo_root.mkdir()
            first = Path(tmp) / "central" / "repo" / "repo-first"
            second = Path(tmp) / "manual" / "repo-first"

            class FakeGitGateway:
                def __init__(self) -> None:
                    self.remove_calls: list[Path] = []

                def remove_worktree(self, repo_root_arg, *, path, force):
                    self.remove_calls.append(path)

            class FakeEnvironmentGateway:
                def getenv(self, name):
                    return str(Path(tmp) / "central")

            class FakeFilesystemGateway:
                def path_exists(self, path):
                    return True

                def remove_tree(self, path):
                    raise AssertionError("remove_tree must not be called")

            inventory = [
                app_contracts.WorktreeRecordView(
                    id="first",
                    path=first,
                    basename="repo-first",
                    branch="main-first",
                    head="abc",
                    managed=True,
                    main=False,
                    current=False,
                    path_exists=True,
                    record_exists=True,
                    removable=True,
                    remove_blockers=[],
                ),
                app_contracts.WorktreeRecordView(
                    id="second",
                    path=second,
                    basename="repo-first",
                    branch="manual-first",
                    head="def",
                    managed=False,
                    main=False,
                    current=False,
                    path_exists=True,
                    record_exists=True,
                    removable=False,
                    remove_blockers=["unmanaged"],
                ),
            ]
            git_gateway = FakeGitGateway()
            ports = app_ports.Ports(
                node_reader=object(),
                repo_root=repo_root,
                git_gateway=git_gateway,
                environment_gateway=FakeEnvironmentGateway(),
                filesystem_gateway=FakeFilesystemGateway(),
            )

            with mock.patch.object(app_worktree, "_build_inventory", return_value=inventory):
                with self.assertRaises(app_contracts.WorktreeCommandError) as raised:
                    app_worktree.worktree_remove(
                        app_contracts.WorktreeRemoveRequest(target="repo-first", force=True),
                        ports,
                    )

            self.assertEqual(raised.exception.code, "ambiguous_target")
            self.assertEqual(len(raised.exception.candidates), 2)
            self.assertEqual(git_gateway.remove_calls, [])

    def test_worktree_invalid_root_short_circuits_git_gateway(self) -> None:
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

            repo_root = Path(tmp) / "repo"
            repo_root.mkdir()
            root_file = Path(tmp) / "root-file"
            root_file.write_text("not dir\n", encoding="utf-8")
            broken = Path(tmp) / "broken"
            if not self._can_create_symlink(Path(tmp)):
                self.skipTest("symlink unavailable")
            os.symlink(Path(tmp) / "missing", broken)

            class ExplodingGitGateway:
                def __init__(self) -> None:
                    self.calls = 0

                def worktree_list(self, repo_root_arg):
                    self.calls += 1
                    raise AssertionError("git gateway must not be called")

            class FakeEnvironmentGateway:
                def __init__(self, value) -> None:
                    self.value = value

                def getenv(self, name):
                    return self.value

            for value in (None, "   ", "relative/root", str(root_file), str(broken)):
                git_gateway = ExplodingGitGateway()
                ports = app_ports.Ports(
                    node_reader=object(),
                    repo_root=repo_root,
                    git_gateway=git_gateway,
                    environment_gateway=FakeEnvironmentGateway(value),
                    filesystem_gateway=object(),
                )
                for call in (
                    lambda: app_worktree.worktree_list(app_contracts.WorktreeListRequest(), ports),
                    lambda: app_worktree.worktree_show(app_contracts.WorktreeShowRequest(target="x"), ports),
                    lambda: app_worktree.worktree_remove(app_contracts.WorktreeRemoveRequest(target="x"), ports),
                ):
                    with self.assertRaises(app_contracts.WorktreeCommandError):
                        call()
                self.assertEqual(git_gateway.calls, 0)

    def test_worktree_inventory_reports_stale_records_and_duplicate_ids(self) -> None:
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

            repo_root = Path(tmp) / "repo"
            central_root = Path(tmp) / "central"
            namespace = central_root / "repo"
            repo_root.mkdir()
            namespace.mkdir(parents=True)
            duplicate_a = namespace / "repo-dupe"
            duplicate_b_parent = Path(tmp) / "manual"
            duplicate_b = duplicate_b_parent / "dupe"
            duplicate_a.mkdir()
            duplicate_b.mkdir(parents=True)
            stale = namespace / "repo-stale"

            class FakeGitGateway:
                def worktree_list(self, repo_root_arg):
                    return [
                        app_contracts.GitWorktreeRecord(path=repo_root, head="abc", branch="main"),
                        app_contracts.GitWorktreeRecord(path=duplicate_a, head="def", branch="main-dupe"),
                        app_contracts.GitWorktreeRecord(path=duplicate_b, head="ghi", branch="manual-dupe"),
                        app_contracts.GitWorktreeRecord(path=stale, head="jkl", branch="main-stale"),
                    ]

            class FakeEnvironmentGateway:
                def getenv(self, name):
                    return str(central_root)

            ports = app_ports.Ports(
                node_reader=object(),
                repo_root=repo_root,
                git_gateway=FakeGitGateway(),
                environment_gateway=FakeEnvironmentGateway(),
            )

            result = app_worktree.worktree_list(app_contracts.WorktreeListRequest(), ports)

            ids = [item.id for item in result.worktrees]
            self.assertEqual(len(ids), len(set(ids)))
            self.assertIn("dupe", ids)
            self.assertIn("dupe~2", ids)
            stale_view = next(item for item in result.worktrees if item.id == "stale")
            self.assertFalse(stale_view.path_exists)
            self.assertTrue(stale_view.record_exists)
            self.assertIn("path_missing", stale_view.remove_blockers)

            shown = app_worktree.worktree_show(app_contracts.WorktreeShowRequest(target="dupe~2"), ports)
            self.assertEqual(shown.worktree.path, duplicate_b)
            unsuffixed = app_worktree.worktree_show(app_contracts.WorktreeShowRequest(target="dupe"), ports)
            self.assertEqual(unsuffixed.worktree.path, duplicate_a)
