from __future__ import annotations

import fcntl
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import signal
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest

from tests.cli_runtime.harness import CliRuntimeHarness, main


def _make_uvx(bin_dir: Path, log: Path) -> None:
    uvx = bin_dir / "uvx"
    uvx.write_text(
        f"#!/bin/sh\nprintf '%s\\n' \"$@\" > {log}\nprintf 'child stdout\\n'\nprintf 'child stderr\\n' >&2\nexit 7\n",
        encoding="utf-8",
    )
    uvx.chmod(0o755)


def _wait_for(path: Path, process: subprocess.Popen[str], *, timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            return
        if process.poll() is not None:
            raise AssertionError(f"helper exited early: {process.returncode}")
        time.sleep(0.01)
    raise AssertionError(f"timed out waiting for {path}")


class TestProviderLifecycleHandoff(CliRuntimeHarness):
    def test_t11_frozen_bootstrap_rejects_visible_root_replacement(self, tmp_path: Path) -> None:
        script = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts/spec-dock"
        loader = importlib.machinery.SourceFileLoader("frozen_spec_dock_bootstrap_visible_binding", str(script))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        assert spec is not None
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)

        root = tmp_path / "root"
        root.mkdir()
        root_fd = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            expected = os.fstat(root_fd)
            moved = tmp_path / "moved-root"
            root.rename(moved)
            root.mkdir()
            with pytest.raises(module._UnsafeBindingError, match="repository root binding changed"):
                module._validate_visible_root(str(root), expected)
        finally:
            os.close(root_fd)

    def test_t11_consumer_hook_parent_io_failure_is_detection_failure_with_exit_zero(
        self, monkeypatch, capsys, tmp_path: Path
    ) -> None:
        script = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts/spec-dock"
        loader = importlib.machinery.SourceFileLoader("frozen_spec_dock_bootstrap", str(script))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        assert spec is not None
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)

        worktree = tmp_path / "worktree"
        worktree.mkdir()
        root_fd = os.open(worktree, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        bound_fd = os.open(worktree, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        value = os.fstat(bound_fd)
        request = SimpleNamespace(
            bound_cwd_fd=bound_fd,
            bound_device=value.st_dev,
            bound_inode=value.st_ino,
            detection_argv=("make", "-n", "init"),
            execution_argv=("make", "init"),
            result_format="worktree-create-json-v1",
            result_payload={"id": "demo", "warnings": []},
        )

        def fail_pipe():
            raise OSError(5, "pipe failed")

        monkeypatch.setattr(module.os, "pipe", fail_pipe)
        try:
            assert module._consumer_hook(request, root_fd) == 0
        finally:
            module._close(root_fd)
            module._close(bound_fd)

        captured = capsys.readouterr()
        payload = json.loads(captured.out)
        assert payload["bootstrap_status"] == "detection_failed"
        assert payload["bootstrap_command"] == "make -n init"
        assert payload["bootstrap_exit_code"] is None
        assert payload["warnings"][-1] == "consumer hook failed: [Errno 5] pipe failed"
        assert captured.err == ""

    def test_t11_consumer_hook_binding_mismatch_is_detection_failure_with_exit_zero(
        self, capsys, tmp_path: Path
    ) -> None:
        script = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts/spec-dock"
        loader = importlib.machinery.SourceFileLoader("frozen_spec_dock_bootstrap_binding", str(script))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        assert spec is not None
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)

        worktree = tmp_path / "worktree"
        worktree.mkdir()
        root_fd = os.open(worktree, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        bound_fd = os.open(worktree, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        value = os.fstat(bound_fd)
        request = SimpleNamespace(
            bound_cwd_fd=bound_fd,
            bound_device=value.st_dev,
            bound_inode=value.st_ino + 1,
            detection_argv=("make", "-n", "init"),
            execution_argv=("make", "init"),
            result_format="worktree-create-json-v1",
            result_payload={"id": "demo", "warnings": []},
        )

        try:
            assert module._consumer_hook(request, root_fd) == 0
        finally:
            module._close(root_fd)
            module._close(bound_fd)

        captured = capsys.readouterr()
        payload = json.loads(captured.out)
        assert payload["bootstrap_status"] == "detection_failed"
        assert payload["warnings"][-1] == "unsafe worktree binding"
        assert captured.err == ""

    def test_t09_worktree_create_read_tree_child_retains_source_and_target_leases_after_parent_sigkill(
        self, tmp_path: Path
    ) -> None:
        target = tmp_path / "target"
        target.mkdir()
        assert main(["init", str(target)]) == 0
        self._init_origin_repo(target)
        (target / "README.md").write_text("baseline\n", encoding="utf-8")
        self._run_git(target, ["add", "-A"])
        self._run_git(target, ["commit", "-m", "baseline"])

        worktree_root = tmp_path / "worktrees"
        fake_bin = tmp_path / "fake-bin"
        fake_bin.mkdir()
        ready = tmp_path / "read-tree-ready"
        release = tmp_path / "read-tree-release"
        done = tmp_path / "read-tree-done"
        real_git = shutil.which("git")
        assert real_git is not None
        fake_git = fake_bin / "git"
        fake_git.write_text(
            "#!/bin/sh\n"
            'if [ "$1" = "read-tree" ]; then\n'
            f"  : > {shlex.quote(str(ready))}\n"
            f"  while [ ! -f {shlex.quote(str(release))} ]; do sleep 0.01; done\n"
            f"  : > {shlex.quote(str(done))}\n"
            "fi\n"
            f'exec {shlex.quote(real_git)} "$@"\n',
            encoding="utf-8",
        )
        fake_git.chmod(0o755)

        env = os.environ.copy()
        env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"
        env["SPEC_DOCK_WORKTREE_ROOT"] = str(worktree_root)
        script = target / "spec-dock" / "scripts" / "spec-dock"
        process = subprocess.Popen(
            [sys.executable, str(script), "worktree", "create", "demo"],
            cwd=target,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        worktree_path = worktree_root / target.name / f"{target.name}-demo"
        source_contender: int | None = None
        target_contender: int | None = None
        try:
            _wait_for(ready, process)
            assert worktree_path.is_dir()

            source_contender = os.open(target, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            with pytest.raises(BlockingIOError):
                fcntl.flock(source_contender, fcntl.LOCK_EX | fcntl.LOCK_NB)
            target_contender = os.open(worktree_path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            with pytest.raises(BlockingIOError):
                fcntl.flock(target_contender, fcntl.LOCK_EX | fcntl.LOCK_NB)

            process.send_signal(signal.SIGKILL)
            process.wait(timeout=5)

            with pytest.raises(BlockingIOError):
                fcntl.flock(source_contender, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with pytest.raises(BlockingIOError):
                fcntl.flock(target_contender, fcntl.LOCK_EX | fcntl.LOCK_NB)

            release.touch()
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline and not done.exists():
                time.sleep(0.01)
            assert done.exists()

            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                try:
                    fcntl.flock(source_contender, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    fcntl.flock(target_contender, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    time.sleep(0.01)
            else:
                raise AssertionError("read-tree helper did not release source and target leases")
        finally:
            release.touch()
            if process.poll() is None:
                process.kill()
            process.wait(timeout=5)
            if source_contender is not None:
                os.close(source_contender)
            if target_contender is not None:
                os.close(target_contender)

    def test_t09_update_uninstall_exec_and_helper_lease_lifetime_are_terminal(self, tmp_path: Path) -> None:
        target = tmp_path / "target"
        target.mkdir()
        assert main(["init", str(target)]) == 0
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        log = tmp_path / "uvx-args"
        _make_uvx(bin_dir, log)
        env = os.environ.copy()
        env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"

        update = subprocess.run(
            [sys.executable, str(target / "spec-dock/scripts/spec-dock"), "update", str(target)],
            cwd=target,
            env=env,
            capture_output=True,
            text=True,
        )
        assert update.returncode == 7
        assert update.stdout == "child stdout\n"
        assert update.stderr == "child stderr\n"
        assert log.read_text(encoding="utf-8").splitlines() == [
            "--no-cache",
            "--from",
            "git+https://github.com/chemitaro/spec-dock",
            "spec-dock",
            "update",
            str(target),
        ]

        uninstall = subprocess.run(
            [
                sys.executable,
                str(target / "spec-dock/scripts/spec-dock"),
                "uninstall",
                str(target),
                "--apply",
                "--keep-specs",
                "--json",
            ],
            cwd=target,
            env=env,
            capture_output=True,
            text=True,
        )
        assert uninstall.returncode == 7
        assert uninstall.stdout == "child stdout\n"
        assert uninstall.stderr == "child stderr\n"
        assert log.read_text(encoding="utf-8").splitlines()[-5:] == [
            "uninstall",
            str(target),
            "--apply",
            "--keep-specs",
            "--json",
        ]

        missing_env = {"PATH": str(tmp_path / "empty-bin")}
        (tmp_path / "empty-bin").mkdir()
        missing = subprocess.run(
            [sys.executable, str(target / "spec-dock/scripts/spec-dock"), "update", str(target)],
            cwd=target,
            env=missing_env,
            capture_output=True,
            text=True,
        )
        assert missing.returncode == 127
        assert missing.stdout == ""
        assert (
            missing.stderr == "error: uvx could not be executed. Install uv/uvx or ensure uvx is on PATH, then retry.\n"
        )

        runtime_scripts = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
        root_fd = os.open(target, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            root_stat = os.fstat(root_fd)
            fcntl.flock(root_fd, fcntl.LOCK_EX)
            marker = tmp_path / "child-ready"
            child_code = (
                "from pathlib import Path; import time; "
                f"Path({str(marker)!r}).write_text('ready', encoding='utf-8'); time.sleep(2)"
            )
            helper_env = os.environ.copy()
            helper_env["PYTHONPATH"] = str(runtime_scripts)
            helper = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "spec_dock_runtime.infra.git_helper",
                    "--lease-fd",
                    str(root_fd),
                    "--expected-device",
                    str(root_stat.st_dev),
                    "--expected-inode",
                    str(root_stat.st_ino),
                    "--cwd-fd",
                    str(root_fd),
                    "--",
                    sys.executable,
                    "-c",
                    child_code,
                ],
                env=helper_env,
                pass_fds=(root_fd,),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            _wait_for(marker, helper)
            helper.send_signal(signal.SIGKILL)
            helper.wait(timeout=5)
        finally:
            os.close(root_fd)

        contender = os.open(target, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            with __import__("pytest").raises(BlockingIOError):
                fcntl.flock(contender, fcntl.LOCK_EX | fcntl.LOCK_NB)
            time.sleep(2.2)
            fcntl.flock(contender, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            os.close(contender)

    def test_t04_terminal_handoff_preserves_symlink_target_for_external_admission(self, tmp_path: Path) -> None:
        target = (tmp_path / "target").resolve()
        target.mkdir()
        assert main(["init", str(target)]) == 0
        link = tmp_path / "target-link"
        link.symlink_to(target, target_is_directory=True)

        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        log = tmp_path / "uvx-args"
        _make_uvx(bin_dir, log)
        env = os.environ.copy()
        env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
        script = target / "spec-dock/scripts/spec-dock"

        update = subprocess.run(
            [sys.executable, str(script), "update", str(link)],
            cwd=target,
            env=env,
            capture_output=True,
            text=True,
        )
        assert update.returncode == 7
        assert log.read_text(encoding="utf-8").splitlines()[-1] == str(link)

        uninstall = subprocess.run(
            [sys.executable, str(script), "uninstall", str(link), "--apply"],
            cwd=target,
            env=env,
            capture_output=True,
            text=True,
        )
        assert uninstall.returncode == 7
        assert log.read_text(encoding="utf-8").splitlines()[-2] == str(link)

    def test_t04_git_write_helper_cannot_be_shadowed_by_consumer_module(self, tmp_path: Path) -> None:
        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime.infra import git_cli

            target = tmp_path / "target"
            target.mkdir()
            marker = tmp_path / "shadowed"
            shadow_package = target / "spec_dock_runtime" / "infra"
            shadow_package.mkdir(parents=True)
            (target / "spec_dock_runtime" / "__init__.py").write_text("", encoding="utf-8")
            (shadow_package / "__init__.py").write_text("", encoding="utf-8")
            (shadow_package / "git_helper.py").write_text(
                f"from pathlib import Path; Path({str(marker)!r}).write_text('shadowed', encoding='utf-8')\n"
                "raise SystemExit(97)\n",
                encoding="utf-8",
            )

            result = git_cli._run_git_write(target, [sys.executable, "-c", "print('provider-helper')"])
        finally:
            sys.path.pop(0)

        assert result.stdout == "provider-helper\n"
        assert not marker.exists()
