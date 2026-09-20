from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

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


class TestRuntimeHandoff(CliRuntimeHarness):
    def test_consumer_hook_parent_io_failure_is_detection_failure_with_exit_zero(
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

    def test_consumer_hook_binding_mismatch_is_detection_failure_with_exit_zero(
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

    def test_external_installer_handoff_preserves_symlink_target(self, tmp_path: Path) -> None:
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

    def test_relative_update_and_uninstall_targets_use_invoking_cwd_and_preserve_symlink_text(
        self, tmp_path: Path
    ) -> None:
        managed = tmp_path / "A" / "managed"
        managed.mkdir(parents=True)
        assert main(["init", str(managed)]) == 0
        caller = tmp_path / "C"
        caller.mkdir()
        sibling = tmp_path / "B"
        sibling.mkdir()
        link = caller / "target-link"
        link.symlink_to(sibling, target_is_directory=True)

        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        log = tmp_path / "uvx-args"
        _make_uvx(bin_dir, log)
        env = os.environ.copy()
        env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
        script = managed / "spec-dock/scripts/spec-dock"
        cases = (
            (".", caller.absolute()),
            ("../B", sibling.absolute()),
            (str(sibling.absolute()), sibling.absolute()),
            (str(link), link),
        )

        for command in ("update", "uninstall"):
            for raw_target, expected_target in cases:
                argv = [sys.executable, str(script), command, raw_target]
                if command == "uninstall":
                    argv.append("--apply")
                result = subprocess.run(
                    argv,
                    cwd=caller,
                    env=env,
                    capture_output=True,
                    text=True,
                )
                assert result.returncode == 7
                logged = log.read_text(encoding="utf-8").splitlines()
                assert logged[-1 if command == "update" else -2] == str(expected_target)


    def test_bound_cwd_git_helper_cannot_be_shadowed_by_consumer_module(self, tmp_path: Path) -> None:
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

            target_fd = os.open(target, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try:
                result = git_cli._run_git_in_bound_cwd(
                    [sys.executable, "-c", "import os; print(os.getcwd())"],
                    cwd_fd=target_fd,
                )
            finally:
                os.close(target_fd)
        finally:
            sys.path.pop(0)

        assert result.stdout == f"{target}\n"
        assert not marker.exists()
