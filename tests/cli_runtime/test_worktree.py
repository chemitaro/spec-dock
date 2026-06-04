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

    def _add_external_worktree(self, target: Path, path: Path, branch: str = "manual") -> None:
        self._run_git(target, ["worktree", "add", "-b", branch, str(path)])

    def _assert_unavailable_classification(self, item: dict[str, object], reason: str) -> None:
        self.assertIs(type(item["managed"]), bool)
        self.assertFalse(item["managed"])
        self.assertFalse(item["managed_classification_available"])
        self.assertEqual(item["classification_reason"], reason)
        self.assertEqual(item["origin"], "classification_unavailable")

    def test_worktree_record_payload_includes_classification_diagnostics(self) -> None:
        runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        sys_path_inserted = False

        if str(runtime_scripts_dir) not in sys.path:
            sys.path.insert(0, str(runtime_scripts_dir))
            sys_path_inserted = True
        try:
            from spec_dock_runtime.application import contracts as app_contracts
            from spec_dock_runtime.presentation import cli_text
        finally:
            if sys_path_inserted:
                sys.path.pop(0)

        cases = [
            (
                app_contracts.WorktreeRecordView(
                    id="managed",
                    path=Path("/tmp/repo-managed"),
                    basename="repo-managed",
                    branch="feature",
                    head="abc",
                    managed=True,
                    main=False,
                    current=False,
                    path_exists=True,
                    record_exists=True,
                    removable=True,
                    remove_blockers=[],
                    managed_classification_available=True,
                    classification_reason="root_valid",
                    origin="spec_dock_managed",
                ),
                "root_valid",
                "spec_dock_managed",
            ),
            (
                app_contracts.WorktreeRecordView(
                    id="external",
                    path=Path("/tmp/repo-external"),
                    basename="repo-external",
                    branch="other",
                    head="def",
                    managed=False,
                    main=False,
                    current=False,
                    path_exists=True,
                    record_exists=True,
                    removable=True,
                    remove_blockers=[],
                    managed_classification_available=True,
                    classification_reason="root_valid",
                    origin="external",
                ),
                "root_valid",
                "external",
            ),
            (
                app_contracts.WorktreeRecordView(
                    id="unknown",
                    path=Path("/tmp/repo-unknown"),
                    basename="repo-unknown",
                    branch=None,
                    head="123",
                    managed=False,
                    main=False,
                    current=False,
                    path_exists=True,
                    record_exists=True,
                    removable=True,
                    remove_blockers=[],
                    managed_classification_available=False,
                    classification_reason="root_missing",
                ),
                "root_missing",
                "classification_unavailable",
            ),
        ]

        for record, expected_reason, expected_origin in cases:
            with self.subTest(record=record.id):
                payload = cli_text._worktree_payload(record)

                self.assertIs(type(payload["managed"]), bool)
                self.assertIs(type(payload["managed_classification_available"]), bool)
                self.assertEqual(payload["classification_reason"], expected_reason)
                self.assertEqual(payload["origin"], expected_origin)

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

    def test_worktree_remove_help_uses_all_worktree_wording(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            target.mkdir()
            self._prepare_git_repo(target)

            top = self._run_runtime_capture(target, ["worktree", "--help"])
            leaf = self._run_runtime_capture(target, ["worktree", "remove", "--help"])

            self.assertEqual(top.returncode, 0, top.stderr)
            self.assertEqual(leaf.returncode, 0, leaf.stderr)
            self.assertIn("Remove a Git worktree without deleting its branch", top.stdout)
            self.assertNotIn("Remove a managed Git worktree", top.stdout)
            self.assertIn("Worktree id, absolute path, or directory basename", leaf.stdout)
            self.assertIn("Compatibility input", leaf.stdout)
            self.assertIn("fully deleted by", leaf.stdout)
            self.assertIn("default.", leaf.stdout)
            self.assertNotIn("Pass --force to git worktree remove", leaf.stdout)
            self.assertNotIn("Managed worktree id", leaf.stdout)

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
            self.assertIn("origin=spec_dock_managed", text_listed.stdout)
            self.assertIn("classification_reason=root_valid", text_listed.stdout)
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
            self.assertIn("origin=spec_dock_managed", text_shown.stdout)
            self.assertIn("classification_reason=root_valid", text_shown.stdout)

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
            for candidate in ambiguous_payload["candidates"]:
                self.assertIn("managed_classification_available", candidate)
                self.assertIn("classification_reason", candidate)
                self.assertIn("origin", candidate)

            branch_only = self._run_runtime_capture(
                target,
                ["worktree", "show", alpha["branch"], "--json"],
                env=self._worktree_env(central_root),
            )
            self.assertNotEqual(branch_only.returncode, 0)
            error_payload = json.loads(branch_only.stdout)
            self.assertEqual(error_payload["status"], "error")
            self.assertEqual(error_payload["error"]["code"], "unsupported_branch_target")

    def test_worktree_list_and_show_json_succeed_when_root_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            external = Path(tmp) / "manual-worktree"
            target.mkdir()
            self._prepare_git_repo(target)
            self._add_external_worktree(target, external)

            env = os.environ.copy()
            env.pop("SPEC_DOCK_WORKTREE_ROOT", None)
            listed = self._run_runtime_capture_exact_env(target, ["worktree", "list", "--json"], env=env)

            self.assertEqual(listed.returncode, 0, listed.stderr)
            payload = json.loads(listed.stdout)
            self.assertEqual(payload["status"], "ok")
            self.assertEqual({item["basename"] for item in payload["worktrees"]}, {"sample-repo", "manual-worktree"})
            for item in payload["worktrees"]:
                self._assert_unavailable_classification(item, "root_missing")

            shown = self._run_runtime_capture_exact_env(target, ["worktree", "show", external.name, "--json"], env=env)

            self.assertEqual(shown.returncode, 0, shown.stderr)
            shown_payload = json.loads(shown.stdout)
            self._assert_unavailable_classification(shown_payload["worktree"], "root_missing")
            self.assertEqual(shown_payload["worktree"]["basename"], external.name)

    def test_worktree_json_commands_report_unavailable_classification_for_invalid_root_variants(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            external = Path(tmp) / "manual-worktree"
            target.mkdir()
            self._prepare_git_repo(target)
            self._add_external_worktree(target, external)
            root_file = Path(tmp) / "root-file"
            root_file.write_text("not a directory\n", encoding="utf-8")
            if not self._can_create_symlink(Path(tmp)):
                self.skipTest("symlink unavailable")
            symlink_root = Path(tmp) / "symlink-root"
            symlink_root.mkdir()
            os.symlink(Path(tmp) / "escaped-namespace", symlink_root / "sample-repo")
            cases: list[tuple[str, dict[str, str], str]] = [
                ("blank", self._worktree_env("   "), "root_blank"),
                ("relative", self._worktree_env("relative/worktrees"), "root_invalid"),
                ("file", self._worktree_env(root_file), "root_invalid"),
                ("namespace-symlink", self._worktree_env(symlink_root), "namespace_symlink"),
            ]
            base_env = os.environ.copy()
            base_env.pop("SPEC_DOCK_WORKTREE_ROOT", None)

            for label, env_update, expected_reason in cases:
                env = dict(base_env)
                env.update(env_update)
                with self.subTest(root=label, command="list"):
                    listed = self._run_runtime_capture_exact_env(target, ["worktree", "list", "--json"], env=env)
                    self.assertEqual(listed.returncode, 0, listed.stderr)
                    payload = json.loads(listed.stdout)
                    self.assertEqual(payload["status"], "ok")
                    external_record = next(item for item in payload["worktrees"] if item["basename"] == external.name)
                    self._assert_unavailable_classification(external_record, expected_reason)

                with self.subTest(root=label, command="show"):
                    shown = self._run_runtime_capture_exact_env(target, ["worktree", "show", external.name, "--json"], env=env)
                    self.assertEqual(shown.returncode, 0, shown.stderr)
                    self._assert_unavailable_classification(json.loads(shown.stdout)["worktree"], expected_reason)

                with self.subTest(root=label, command="remove"):
                    removable = Path(tmp) / f"manual-remove-{label}"
                    self._add_external_worktree(target, removable, branch=f"manual-remove-{label}")
                    removed = self._run_runtime_capture_exact_env(target, ["worktree", "remove", removable.name, "--json"], env=env)
                    self.assertEqual(removed.returncode, 0, removed.stderr)
                    removed_payload = json.loads(removed.stdout)
                    self.assertEqual(removed_payload["status"], "ok")
                    self.assertTrue(removed_payload["removed_record"])
                    self.assertFalse(removed_payload["branch_deleted"])
                    self._assert_unavailable_classification(removed_payload["resolved_target"], expected_reason)
                    self.assertNotIn(str(removable), self._run_git(target, ["worktree", "list", "--porcelain"]).stdout)

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
            self.assertTrue(manual["removable"])
            self.assertEqual(manual["remove_blockers"], [])
            self.assertEqual(manual["origin"], "external")

            text_listed = self._run_runtime_capture(target, ["worktree", "list"], env=self._worktree_env(central_root))
            self.assertEqual(text_listed.returncode, 0, text_listed.stderr)
            self.assertIn("origin=external", text_listed.stdout)
            self.assertIn("classification_reason=root_valid", text_listed.stdout)

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

            created_again = self._run_runtime_capture(target, ["worktree", "create", "done2"], env=self._worktree_env(central_root))
            self.assertEqual(created_again.returncode, 0, created_again.stderr)
            text_removed = self._run_runtime_capture(target, ["worktree", "remove", "done2"], env=self._worktree_env(central_root))
            self.assertEqual(text_removed.returncode, 0, text_removed.stderr)
            self.assertIn("managed=true", text_removed.stdout)
            self.assertIn("origin=spec_dock_managed", text_removed.stdout)
            self.assertIn("classification_reason=root_valid", text_removed.stdout)
            self.assertIn("remove_blockers=-", text_removed.stdout)

    def test_worktree_remove_untracked_default_removes_directory_and_keeps_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            central_root = Path(tmp) / "central-worktrees"
            target.mkdir()
            self._prepare_git_repo(target)

            created = self._run_runtime_capture(target, ["worktree", "create", "dirty"], env=self._worktree_env(central_root))
            self.assertEqual(created.returncode, 0, created.stderr)
            worktree_path = central_root / "sample-repo" / "sample-repo-dirty"
            branch = self._run_git(target, ["branch", "--list", "*-dirty", "--format=%(refname:short)"]).stdout.strip()
            self.assertTrue(branch)
            (worktree_path / "cache.tmp").write_text("dirty\n", encoding="utf-8")

            removed = self._run_runtime_capture(
                target,
                ["worktree", "remove", "dirty", "--json"],
                env=self._worktree_env(central_root),
            )
            self.assertEqual(removed.returncode, 0, removed.stderr or removed.stdout)
            payload = json.loads(removed.stdout)
            self.assertEqual(payload["status"], "ok")
            self.assertTrue(payload["removed_record"])
            self.assertTrue(payload["removed_directory"])
            self.assertFalse(payload["branch_deleted"])
            self.assertFalse(worktree_path.exists())
            self.assertNotIn(str(worktree_path), self._run_git(target, ["worktree", "list", "--porcelain"]).stdout)
            self.assertIn(branch, self._run_git(target, ["branch", "--list", branch]).stdout)

    def test_worktree_remove_tracked_modification_default_removes_directory_and_keeps_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            central_root = Path(tmp) / "central-worktrees"
            target.mkdir()
            self._prepare_git_repo(target)

            created = self._run_runtime_capture(target, ["worktree", "create", "modified"], env=self._worktree_env(central_root))
            self.assertEqual(created.returncode, 0, created.stderr)
            worktree_path = central_root / "sample-repo" / "sample-repo-modified"
            branch = self._run_git(target, ["branch", "--list", "*-modified", "--format=%(refname:short)"]).stdout.strip()
            self.assertTrue(branch)
            tracked_file = worktree_path / "tracked.txt"
            tracked_file.write_text("tracked\n", encoding="utf-8")
            self._run_git(worktree_path, ["add", "tracked.txt"])
            self._run_git(
                worktree_path,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "add tracked"],
            )
            tracked_file.write_text("tracked modified\n", encoding="utf-8")

            removed = self._run_runtime_capture(
                target,
                ["worktree", "remove", "modified", "--json"],
                env=self._worktree_env(central_root),
            )
            self.assertEqual(removed.returncode, 0, removed.stderr or removed.stdout)
            payload = json.loads(removed.stdout)
            self.assertEqual(payload["status"], "ok")
            self.assertTrue(payload["removed_record"])
            self.assertTrue(payload["removed_directory"])
            self.assertFalse(payload["branch_deleted"])
            self.assertFalse(worktree_path.exists())
            self.assertNotIn(str(worktree_path), self._run_git(target, ["worktree", "list", "--porcelain"]).stdout)
            self.assertIn(branch, self._run_git(target, ["branch", "--list", branch]).stdout)

    def test_worktree_remove_force_compatibility_removes_dirty_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            central_root = Path(tmp) / "central-worktrees"
            target.mkdir()
            self._prepare_git_repo(target)

            created = self._run_runtime_capture(target, ["worktree", "create", "dirty"], env=self._worktree_env(central_root))
            self.assertEqual(created.returncode, 0, created.stderr)
            worktree_path = central_root / "sample-repo" / "sample-repo-dirty"
            branch = self._run_git(target, ["branch", "--list", "*-dirty", "--format=%(refname:short)"]).stdout.strip()
            self.assertTrue(branch)
            (worktree_path / "cache.tmp").write_text("dirty\n", encoding="utf-8")

            removed = self._run_runtime_capture(
                target,
                ["worktree", "remove", "dirty", "--force", "--json"],
                env=self._worktree_env(central_root),
            )
            self.assertEqual(removed.returncode, 0, removed.stderr or removed.stdout)
            payload = json.loads(removed.stdout)
            self.assertEqual(payload["status"], "ok")
            self.assertTrue(payload["removed_record"])
            self.assertTrue(payload["removed_directory"])
            self.assertFalse(payload["branch_deleted"])
            self.assertFalse(worktree_path.exists())
            self.assertNotIn(str(worktree_path), self._run_git(target, ["worktree", "list", "--porcelain"]).stdout)
            self.assertIn(branch, self._run_git(target, ["branch", "--list", branch]).stdout)

    def test_worktree_remove_locked_default_and_force_share_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-repo"
            central_root = Path(tmp) / "central-worktrees"
            target.mkdir()
            self._prepare_git_repo(target)

            cases = (("locked-default", []), ("locked-force", ["--force"]))
            results: list[tuple[str, Path, subprocess.CompletedProcess[str], dict[str, object]]] = []
            for label, extra_args in cases:
                created = self._run_runtime_capture(target, ["worktree", "create", label], env=self._worktree_env(central_root))
                self.assertEqual(created.returncode, 0, created.stderr)
                worktree_path = central_root / "sample-repo" / f"sample-repo-{label}"
                lock = self._run_git(target, ["worktree", "lock", str(worktree_path)], check=False)
                if lock.returncode != 0:
                    self.skipTest(f"git worktree lock unavailable: {lock.stderr}")

                listed = self._run_runtime_capture(target, ["worktree", "list", "--json"], env=self._worktree_env(central_root))
                self.assertEqual(listed.returncode, 0, listed.stderr)
                listed_payload = json.loads(listed.stdout)
                listed_record = next(item for item in listed_payload["worktrees"] if item["id"] == label)
                self.assertTrue(listed_record["removable"])
                self.assertEqual(listed_record["remove_blockers"], [])

                shown = self._run_runtime_capture(target, ["worktree", "show", label, "--json"], env=self._worktree_env(central_root))
                self.assertEqual(shown.returncode, 0, shown.stderr)
                shown_record = json.loads(shown.stdout)["worktree"]
                self.assertTrue(shown_record["removable"])
                self.assertEqual(shown_record["remove_blockers"], [])

                removed = self._run_runtime_capture(
                    target,
                    ["worktree", "remove", label, *extra_args, "--json"],
                    env=self._worktree_env(central_root),
                )
                results.append((label, worktree_path, removed, json.loads(removed.stdout)))

            default_result = results[0][2]
            force_result = results[1][2]
            self.assertEqual(default_result.returncode == 0, force_result.returncode == 0)

            if default_result.returncode == 0:
                for _label, worktree_path, _removed, payload in results:
                    self.assertEqual(payload["status"], "ok")
                    self.assertTrue(payload["removed_record"])
                    self.assertTrue(payload["removed_directory"])
                    self.assertTrue(payload["resolved_target"]["removable"])
                    self.assertEqual(payload["resolved_target"]["remove_blockers"], [])
                    self.assertFalse(worktree_path.exists())
            else:
                for _label, worktree_path, _removed, payload in results:
                    self.assertTrue(worktree_path.exists())
                    self.assertEqual(payload["error"]["code"], "git_worktree_remove_failed")

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
            self.assertIn("managed_classification_available", current_payload["worktree"])
            self.assertIn("classification_reason", current_payload["worktree"])
            self.assertIn("origin", current_payload["worktree"])
            self.assertTrue(current_path.exists())

            self._run_git(target, ["worktree", "add", "-b", "manual", str(unmanaged)])
            unmanaged_remove = self._run_runtime_capture(
                target,
                ["worktree", "remove", unmanaged.name, "--json"],
                env=self._worktree_env(central_root),
            )
            self.assertEqual(unmanaged_remove.returncode, 0, unmanaged_remove.stderr)
            unmanaged_payload = json.loads(unmanaged_remove.stdout)
            self.assertEqual(unmanaged_payload["status"], "ok")
            self.assertTrue(unmanaged_payload["removed_record"])
            self.assertTrue(unmanaged_payload["removed_directory"])
            self.assertFalse(unmanaged_payload["branch_deleted"])
            self.assertFalse(unmanaged_payload["resolved_target"]["managed"])
            self.assertTrue(unmanaged_payload["resolved_target"]["managed_classification_available"])
            self.assertEqual(unmanaged_payload["resolved_target"]["classification_reason"], "root_valid")
            self.assertEqual(unmanaged_payload["resolved_target"]["origin"], "external")
            self.assertFalse(unmanaged.exists())
            self.assertNotIn(str(unmanaged), self._run_git(target, ["worktree", "list", "--porcelain"]).stdout)
            self.assertIn("manual", self._run_git(target, ["branch", "--list", "manual"]).stdout)

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

    def test_worktree_remove_external_paths_are_not_blocked_by_managed_namespace_containment(self) -> None:
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
            central_sentinel = central_root / "sentinel"
            namespace_sentinel = namespace / "sentinel"
            central_sentinel.write_text("keep\n", encoding="utf-8")
            namespace_sentinel.write_text("keep\n", encoding="utf-8")

            class FakeGitGateway:
                def __init__(self, records):
                    self.records = records
                    self.remove_calls: list[tuple[Path, bool]] = []

                def worktree_list(self, repo_root_arg):
                    return self.records

                def remove_worktree(self, repo_root_arg, *, path, force):
                    self.remove_calls.append((path, force))

            class FakeEnvironmentGateway:
                def __init__(self, root):
                    self.root = root

                def getenv(self, name):
                    return str(self.root)

            class FakeFilesystemGateway:
                def path_exists(self, path):
                    return Path(path).exists() or os.path.lexists(path)

                def remove_target(self, path):
                    if Path(path) == symlink_path and Path(path).is_symlink():
                        Path(path).unlink()
                        return
                    raise AssertionError(f"remove_target must only be called for the external symlink target: {path}")

            git_gateway = FakeGitGateway(
                [
                    app_contracts.GitWorktreeRecord(path=repo_root, head="abc", branch="main"),
                    app_contracts.GitWorktreeRecord(path=symlink_path, head="def", branch="main-escape"),
                ]
            )
            ports = app_ports.Ports(
                node_reader=object(),
                repo_root=repo_root,
                git_gateway=git_gateway,
                environment_gateway=FakeEnvironmentGateway(central_root),
                filesystem_gateway=FakeFilesystemGateway(),
            )

            result = app_worktree.worktree_remove(
                app_contracts.WorktreeRemoveRequest(target=str(symlink_path), force=True),
                ports,
            )

            self.assertTrue(result.removed_record)
            self.assertEqual(git_gateway.remove_calls, [(symlink_path, True)])
            self.assertFalse(os.path.lexists(symlink_path))
            self.assertTrue(escaped.exists())
            self.assertTrue(central_sentinel.exists())
            self.assertTrue(namespace_sentinel.exists())

            for target, record_path, force in (
                (str(central_root), central_root, False),
                (str(central_root), central_root, True),
                (str(namespace), namespace, False),
                (str(namespace), namespace, True),
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
                    app_worktree.worktree_remove(app_contracts.WorktreeRemoveRequest(target=target, force=force), ports)

                self.assertEqual(raised.exception.code, "remove_blocked")
                self.assertIn("protected_cleanup_path", raised.exception.remove_blockers)
                self.assertEqual(git_gateway.remove_calls, [])
                self.assertTrue(record_path.exists())
                self.assertTrue(central_sentinel.exists())
                self.assertTrue(namespace_sentinel.exists())

            ancestor_worktree = Path(tmp) / "ancestor-worktree"
            nested_central_root = ancestor_worktree / "worktrees"
            nested_namespace = nested_central_root / "repo"
            ancestor_worktree.mkdir()
            nested_namespace.mkdir(parents=True)
            nested_sentinel = nested_namespace / "sentinel"
            nested_sentinel.write_text("keep\n", encoding="utf-8")
            git_gateway = FakeGitGateway(
                [
                    app_contracts.GitWorktreeRecord(path=repo_root, head="abc", branch="main"),
                    app_contracts.GitWorktreeRecord(path=ancestor_worktree, head="def", branch="main-ancestor"),
                ]
            )
            ports = app_ports.Ports(
                node_reader=object(),
                repo_root=repo_root,
                git_gateway=git_gateway,
                environment_gateway=FakeEnvironmentGateway(nested_central_root),
                filesystem_gateway=FakeFilesystemGateway(),
            )

            for force in (False, True):
                with self.subTest(target="ancestor_worktree", force=force):
                    with self.assertRaises(app_contracts.WorktreeCommandError) as raised:
                        app_worktree.worktree_remove(
                            app_contracts.WorktreeRemoveRequest(target=str(ancestor_worktree), force=force),
                            ports,
                        )

                    self.assertEqual(raised.exception.code, "remove_blocked")
                    self.assertIn("protected_cleanup_path", raised.exception.remove_blockers)
                    self.assertEqual(git_gateway.remove_calls, [])
                    self.assertTrue(nested_sentinel.exists())

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

            for force in (False, True):
                with self.subTest(target="namespace_symlink_record", force=force):
                    with self.assertRaises(app_contracts.WorktreeCommandError) as raised:
                        app_worktree.worktree_remove(
                            app_contracts.WorktreeRemoveRequest(target=str(namespace_symlink_record), force=force),
                            ports,
                        )

                    self.assertEqual(raised.exception.code, "remove_blocked")
                    self.assertIn("protected_cleanup_path", raised.exception.remove_blockers)
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

                def remove_target(self, path):
                    self.remove_calls.append(path)
                    if self.fail:
                        raise RuntimeError("cleanup denied")

            filesystem_gateway = FakeFilesystemGateway()
            git_gateway = FakeGitGateway()
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
            self.assertEqual(git_gateway.remove_calls, [(worktree_path, True)])
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

    def test_worktree_remove_git_failure_does_not_cleanup_target(self) -> None:
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
                    raise RuntimeError("git refused")

            class FakeEnvironmentGateway:
                def getenv(self, name):
                    return str(central_root)

            class CleanupMustNotRun:
                def path_exists(self, path):
                    raise AssertionError("cleanup existence check must not be called")

                def remove_target(self, path):
                    raise AssertionError("cleanup must not be called")

            git_gateway = FakeGitGateway()
            ports = app_ports.Ports(
                node_reader=object(),
                repo_root=repo_root,
                git_gateway=git_gateway,
                environment_gateway=FakeEnvironmentGateway(),
                filesystem_gateway=CleanupMustNotRun(),
            )

            with self.assertRaises(app_contracts.WorktreeCommandError) as raised:
                app_worktree.worktree_remove(app_contracts.WorktreeRemoveRequest(target="leftover"), ports)

            self.assertEqual(raised.exception.code, "git_worktree_remove_failed")
            self.assertEqual(git_gateway.remove_calls, [(worktree_path, True)])

    def test_worktree_remove_locked_default_uses_force_equivalent_git_call(self) -> None:
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
            worktree_path = central_root / "repo" / "repo-locked"
            repo_root.mkdir()
            worktree_path.mkdir(parents=True)

            class FakeGitGateway:
                def __init__(self) -> None:
                    self.remove_calls: list[tuple[Path, bool]] = []

                def worktree_list(self, repo_root_arg):
                    return [
                        app_contracts.GitWorktreeRecord(path=repo_root, head="abc", branch="main"),
                        app_contracts.GitWorktreeRecord(path=worktree_path, head="def", branch="main-locked", locked=True),
                    ]

                def remove_worktree(self, repo_root_arg, *, path, force):
                    self.remove_calls.append((path, force))

            class FakeEnvironmentGateway:
                def getenv(self, name):
                    return str(central_root)

            class FakeFilesystemGateway:
                def path_exists(self, path):
                    return False

                def remove_target(self, path):
                    raise AssertionError("cleanup should not run when path is already gone")

            git_gateway = FakeGitGateway()
            ports = app_ports.Ports(
                node_reader=object(),
                repo_root=repo_root,
                git_gateway=git_gateway,
                environment_gateway=FakeEnvironmentGateway(),
                filesystem_gateway=FakeFilesystemGateway(),
            )

            result = app_worktree.worktree_remove(app_contracts.WorktreeRemoveRequest(target="locked"), ports)

            self.assertTrue(result.removed_record)
            self.assertTrue(result.resolved_target.removable)
            self.assertEqual(result.resolved_target.remove_blockers, [])
            self.assertEqual(git_gateway.remove_calls, [(worktree_path, True)])

    def test_worktree_remove_uses_target_only_cleanup_for_remaining_directory(self) -> None:
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
            worktree_path = namespace / "repo-leftover"
            repo_root.mkdir()
            worktree_path.mkdir(parents=True)
            parent_sentinel = worktree_path.parent / "parent-sentinel"
            root_sentinel = central_root / "root-sentinel"
            namespace_sentinel = namespace / "namespace-sentinel"
            for sentinel in (parent_sentinel, root_sentinel, namespace_sentinel):
                sentinel.write_text("keep\n", encoding="utf-8")

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
                    return None

            class FakeEnvironmentGateway:
                def getenv(self, name):
                    return str(central_root)

            class FakeFilesystemGateway:
                def __init__(self) -> None:
                    self.remove_calls: list[Path] = []

                def path_exists(self, path):
                    return True

                def remove_target(self, path):
                    self.remove_calls.append(path)
                    shutil.rmtree(path)

            filesystem_gateway = FakeFilesystemGateway()
            git_gateway = FakeGitGateway()
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
            self.assertEqual(git_gateway.remove_calls, [(worktree_path, True)])
            self.assertEqual(filesystem_gateway.remove_calls, [worktree_path])
            self.assertFalse(worktree_path.exists())
            for sentinel in (parent_sentinel, root_sentinel, namespace_sentinel):
                self.assertTrue(sentinel.exists())

    def test_worktree_remove_reports_target_cleanup_failures(self) -> None:
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
                def worktree_list(self, repo_root_arg):
                    return [
                        app_contracts.GitWorktreeRecord(path=repo_root, head="abc", branch="main"),
                        app_contracts.GitWorktreeRecord(path=worktree_path, head="def", branch="main-leftover"),
                    ]

                def remove_worktree(self, repo_root_arg, *, path, force):
                    return None

            class FakeEnvironmentGateway:
                def getenv(self, name):
                    return str(central_root)

            class FailingFilesystemGateway:
                def __init__(self, mode):
                    self.mode = mode

                def path_exists(self, path):
                    if self.mode == "lstat":
                        raise RuntimeError("failed to inspect target path")
                    return True

                def remove_target(self, path):
                    messages = {
                        "unsupported": "unsupported target path type",
                        "unlink": "failed to remove target path",
                        "rmtree": "failed to remove directory tree",
                        "race": "failed to inspect target path",
                    }
                    raise RuntimeError(messages[self.mode])

            for mode in ("unsupported", "lstat", "unlink", "rmtree", "race"):
                with self.subTest(mode=mode):
                    ports = app_ports.Ports(
                        node_reader=object(),
                        repo_root=repo_root,
                        git_gateway=FakeGitGateway(),
                        environment_gateway=FakeEnvironmentGateway(),
                        filesystem_gateway=FailingFilesystemGateway(mode),
                    )

                    with self.assertRaises(app_contracts.WorktreeCommandError) as raised:
                        app_worktree.worktree_remove(app_contracts.WorktreeRemoveRequest(target="leftover"), ports)

                    self.assertEqual(raised.exception.code, "post_remove_cleanup_failed")
                    self.assertTrue(raised.exception.removed_record)
                    self.assertFalse(raised.exception.removed_directory)

    def test_fs_remove_target_unlinks_symlink_broken_symlink_and_regular_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            if not self._can_create_symlink(Path(tmp)):
                self.skipTest("symlink unavailable")
            runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
            sys_path_inserted = False

            if str(runtime_scripts_dir) not in sys.path:
                sys.path.insert(0, str(runtime_scripts_dir))
                sys_path_inserted = True
            try:
                from spec_dock_runtime.infra import fs_cli
            finally:
                if sys_path_inserted:
                    sys.path.pop(0)

            base = Path(tmp)
            target_dir = base / "target-dir"
            target_dir.mkdir()
            target_sentinel = target_dir / "sentinel"
            target_sentinel.write_text("keep\n", encoding="utf-8")
            symlink_path = base / "target-link"
            os.symlink(target_dir, symlink_path)
            broken_symlink = base / "broken-link"
            os.symlink(base / "missing-target", broken_symlink)
            regular_file = base / "target-file"
            regular_file.write_text("remove\n", encoding="utf-8")

            self.assertTrue(fs_cli.path_exists(symlink_path))
            self.assertTrue(fs_cli.path_exists(broken_symlink))
            self.assertTrue(fs_cli.path_exists(regular_file))

            fs_cli.remove_target(symlink_path)
            fs_cli.remove_target(broken_symlink)
            fs_cli.remove_target(regular_file)

            self.assertFalse(os.path.lexists(symlink_path))
            self.assertFalse(os.path.lexists(broken_symlink))
            self.assertFalse(regular_file.exists())
            self.assertTrue(target_sentinel.exists())

    def test_fs_remove_target_reports_lstat_unlink_rmtree_and_unsupported_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
            sys_path_inserted = False

            if str(runtime_scripts_dir) not in sys.path:
                sys.path.insert(0, str(runtime_scripts_dir))
                sys_path_inserted = True
            try:
                from spec_dock_runtime.infra import fs_cli
            finally:
                if sys_path_inserted:
                    sys.path.pop(0)

            base = Path(tmp)
            with self.assertRaises(RuntimeError) as missing:
                fs_cli.remove_target(base / "missing")
            self.assertIn("failed to inspect target path", str(missing.exception))

            regular_file = base / "target-file"
            regular_file.write_text("remove\n", encoding="utf-8")
            with mock.patch.object(Path, "unlink", side_effect=OSError("denied")):
                with self.assertRaises(RuntimeError) as unlink_failed:
                    fs_cli.remove_target(regular_file)
            self.assertIn("failed to remove target path", str(unlink_failed.exception))

            target_dir = base / "target-dir"
            target_dir.mkdir()
            with mock.patch.object(fs_cli.shutil, "rmtree", side_effect=OSError("denied")):
                with self.assertRaises(RuntimeError) as rmtree_failed:
                    fs_cli.remove_target(target_dir)
            self.assertIn("failed to remove directory tree", str(rmtree_failed.exception))

            if not hasattr(os, "mkfifo"):
                self.skipTest("mkfifo unavailable")
            fifo_path = base / "target-fifo"
            os.mkfifo(fifo_path)
            try:
                with self.assertRaises(RuntimeError) as unsupported:
                    fs_cli.remove_target(fifo_path)
            finally:
                fifo_path.unlink(missing_ok=True)
            self.assertIn("unsupported target path type", str(unsupported.exception))

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

                def remove_target(self, path):
                    raise AssertionError("remove_target must not be called")

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
                    removable=True,
                    remove_blockers=[],
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

    def test_worktree_remove_re_resolves_target_after_final_git_refresh(self) -> None:
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
            managed = namespace / "repo-managed"
            duplicate = Path(tmp) / "manual" / "repo-managed"
            managed.mkdir()
            duplicate.parent.mkdir()
            duplicate.mkdir()

            class FakeGitGateway:
                def __init__(self, refreshed_records):
                    self.calls = 0
                    self.refreshed_records = refreshed_records
                    self.remove_calls: list[Path] = []

                def worktree_list(self, repo_root_arg):
                    self.calls += 1
                    initial_records = [
                        app_contracts.GitWorktreeRecord(path=repo_root, head="abc", branch="main"),
                        app_contracts.GitWorktreeRecord(path=managed, head="def", branch="managed"),
                    ]
                    return initial_records if self.calls == 1 else self.refreshed_records

                def remove_worktree(self, repo_root_arg, *, path, force):
                    self.remove_calls.append(path)

            class FakeEnvironmentGateway:
                def getenv(self, name):
                    return str(central_root)

            class FakeFilesystemGateway:
                def path_exists(self, path):
                    return Path(path).exists()

                def remove_target(self, path):
                    raise AssertionError("remove_target must not be called")

            main_record = app_contracts.GitWorktreeRecord(path=repo_root, head="abc", branch="main")
            cases = (
                (
                    "changed_after_refresh",
                    [
                        main_record,
                        app_contracts.GitWorktreeRecord(path=managed, head="def", branch="managed"),
                        app_contracts.GitWorktreeRecord(path=duplicate, head="ghi", branch="manual-managed"),
                    ],
                    "remove_blocked",
                    "record_missing",
                ),
                (
                    "bare_after_refresh",
                    [
                        main_record,
                        app_contracts.GitWorktreeRecord(path=managed, head="def", branch="managed", bare=True),
                    ],
                    "remove_blocked",
                    "bare_worktree",
                ),
            )
            for label, refreshed_records, expected_code, expected_blocker in cases:
                with self.subTest(label=label):
                    git_gateway = FakeGitGateway(refreshed_records)
                    ports = app_ports.Ports(
                        node_reader=object(),
                        repo_root=repo_root,
                        git_gateway=git_gateway,
                        environment_gateway=FakeEnvironmentGateway(),
                        filesystem_gateway=FakeFilesystemGateway(),
                    )

                    with self.assertRaises(app_contracts.WorktreeCommandError) as raised:
                        app_worktree.worktree_remove(
                            app_contracts.WorktreeRemoveRequest(target="repo-managed", force=True),
                            ports,
                        )

                    self.assertEqual(raised.exception.code, expected_code)
                    if expected_blocker is not None:
                        self.assertIn(expected_blocker, raised.exception.remove_blockers)
                    self.assertEqual(git_gateway.remove_calls, [])

    def test_worktree_remove_hard_blockers_stop_before_git_remove_even_with_force(self) -> None:
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
            managed = namespace / "repo-managed"
            managed.mkdir()
            stale = namespace / "repo-stale"
            bare = namespace / "repo-bare"
            bare.mkdir()

            class FakeGitGateway:
                def __init__(self, records_by_call):
                    self.records_by_call = records_by_call
                    self.calls = 0
                    self.remove_calls: list[Path] = []

                def worktree_list(self, repo_root_arg):
                    index = min(self.calls, len(self.records_by_call) - 1)
                    self.calls += 1
                    return self.records_by_call[index]

                def remove_worktree(self, repo_root_arg, *, path, force):
                    self.remove_calls.append(path)

            class FakeEnvironmentGateway:
                def getenv(self, name):
                    return str(central_root)

            class FakeFilesystemGateway:
                def path_exists(self, path):
                    return Path(path).exists()

                def remove_target(self, path):
                    raise AssertionError("remove_target must not be called")

            main_record = app_contracts.GitWorktreeRecord(path=repo_root, head="abc", branch="main")
            cases = (
                ("main", "main", [[main_record]], "main_worktree"),
                ("current", "managed", [[main_record, app_contracts.GitWorktreeRecord(path=managed, head="def", branch="managed")]], "current_worktree"),
                ("bare", "bare", [[main_record, app_contracts.GitWorktreeRecord(path=bare, head="ghi", branch="bare", bare=True)]], "bare_worktree"),
                ("path_missing", "stale", [[main_record, app_contracts.GitWorktreeRecord(path=stale, head="jkl", branch="stale")]], "path_missing"),
                (
                    "record_missing",
                    "managed",
                    [
                        [main_record, app_contracts.GitWorktreeRecord(path=managed, head="def", branch="managed")],
                        [main_record],
                    ],
                    "record_missing",
                ),
            )
            for label, target, records_by_call, expected_blocker in cases:
                for force in (False, True):
                    with self.subTest(label=label, force=force):
                        git_gateway = FakeGitGateway(records_by_call)
                        repo_for_case = managed if label == "current" else repo_root
                        ports = app_ports.Ports(
                            node_reader=object(),
                            repo_root=repo_for_case,
                            git_gateway=git_gateway,
                            environment_gateway=FakeEnvironmentGateway(),
                            filesystem_gateway=FakeFilesystemGateway(),
                        )

                        with self.assertRaises(app_contracts.WorktreeCommandError) as raised:
                            app_worktree.worktree_remove(
                                app_contracts.WorktreeRemoveRequest(target=target, force=force),
                                ports,
                            )

                        self.assertEqual(raised.exception.code, "remove_blocked")
                        self.assertIn(expected_blocker, raised.exception.remove_blockers)
                        self.assertEqual(git_gateway.remove_calls, [])

    def test_worktree_remove_treats_broken_symlink_target_as_existing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            if not self._can_create_symlink(Path(tmp)):
                self.skipTest("symlink unavailable")
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
            broken = namespace / "repo-broken"
            os.symlink(Path(tmp) / "missing-target", broken)

            class FakeGitGateway:
                def __init__(self) -> None:
                    self.remove_calls: list[Path] = []

                def worktree_list(self, repo_root_arg):
                    return [
                        app_contracts.GitWorktreeRecord(path=repo_root, head="abc", branch="main"),
                        app_contracts.GitWorktreeRecord(path=broken, head="def", branch="main-broken"),
                    ]

                def remove_worktree(self, repo_root_arg, *, path, force):
                    self.remove_calls.append(path)

            class FakeEnvironmentGateway:
                def getenv(self, name):
                    return str(central_root)

            class FakeFilesystemGateway:
                def path_exists(self, path):
                    return os.path.lexists(path)

                def remove_target(self, path):
                    Path(path).unlink()

            git_gateway = FakeGitGateway()
            ports = app_ports.Ports(
                node_reader=object(),
                repo_root=repo_root,
                git_gateway=git_gateway,
                environment_gateway=FakeEnvironmentGateway(),
                filesystem_gateway=FakeFilesystemGateway(),
            )

            result = app_worktree.worktree_remove(app_contracts.WorktreeRemoveRequest(target=str(broken)), ports)

            self.assertTrue(result.removed_record)
            self.assertTrue(result.resolved_target.path_exists)
            self.assertEqual(result.resolved_target.remove_blockers, [])
            self.assertEqual(git_gateway.remove_calls, [broken])
            self.assertFalse(os.path.lexists(broken))

    def test_worktree_invalid_root_reads_git_records_before_classification(self) -> None:
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
            manual = Path(tmp) / "manual"
            manual.mkdir()

            class FakeGitGateway:
                def __init__(self) -> None:
                    self.calls = 0
                    self.remove_calls: list[Path] = []

                def worktree_list(self, repo_root_arg):
                    self.calls += 1
                    return [
                        app_contracts.GitWorktreeRecord(path=repo_root, head="abc", branch="main"),
                        app_contracts.GitWorktreeRecord(path=manual, head="def", branch="manual"),
                    ]

                def remove_worktree(self, repo_root_arg, *, path, force):
                    self.remove_calls.append(path)

            class FakeEnvironmentGateway:
                def __init__(self, value) -> None:
                    self.value = value

                def getenv(self, name):
                    return self.value

            class FakeFilesystemGateway:
                def path_exists(self, path):
                    return False

                def remove_target(self, path):
                    raise AssertionError("remove_target must not be called")

            cases = (
                (None, "root_missing"),
                ("   ", "root_blank"),
                ("relative/root", "root_invalid"),
                (str(root_file), "root_invalid"),
            )
            for value, expected_reason in cases:
                with self.subTest(value=value):
                    git_gateway = FakeGitGateway()
                    ports = app_ports.Ports(
                        node_reader=object(),
                        repo_root=repo_root,
                        git_gateway=git_gateway,
                        environment_gateway=FakeEnvironmentGateway(value),
                        filesystem_gateway=FakeFilesystemGateway(),
                    )

                    listed = app_worktree.worktree_list(app_contracts.WorktreeListRequest(), ports)
                    shown = app_worktree.worktree_show(app_contracts.WorktreeShowRequest(target="manual"), ports)
                    removed = app_worktree.worktree_remove(app_contracts.WorktreeRemoveRequest(target="manual"), ports)

                    self.assertEqual(git_gateway.calls, 4)
                    self.assertEqual(git_gateway.remove_calls, [manual])
                    for worktree in listed.worktrees:
                        self.assertFalse(worktree.managed)
                        self.assertFalse(worktree.managed_classification_available)
                        self.assertEqual(worktree.classification_reason, expected_reason)
                        self.assertEqual(worktree.origin, "classification_unavailable")
                    self.assertEqual(shown.worktree.path, manual)
                    self.assertEqual(shown.worktree.classification_reason, expected_reason)
                    self.assertTrue(removed.removed_record)
                    self.assertEqual(removed.resolved_target.classification_reason, expected_reason)

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
