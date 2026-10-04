"""Standalone provider shims delegate to PATH without Git control or repository Python."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from spec_dock.runtime.infra.tree_backup import tree_digest

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.skipif(os.name != "posix", reason="native POSIX executable script fixtures")


def shim_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    root = tmp_path / "consumer"
    script = root / "spec-dock/scripts/spec-dock"
    script.parent.mkdir(parents=True)
    script.write_bytes((ROOT / "src/spec_dock/assets/spec_dock/scripts/spec-dock").read_bytes())
    script.chmod(0o755)
    executables = tmp_path / "bin"
    executables.mkdir()
    return root, script, executables


def executable(path: Path, body: str) -> None:
    path.write_text(f"#!{sys.executable}\n{body}\n", encoding="utf-8")
    path.chmod(0o755)


def invoke(script: Path, cwd: Path, executables: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", str(script), *args],
        cwd=cwd,
        env=dict(os.environ, PATH=str(executables), PYTHONDONTWRITEBYTECODE="1"),
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )


def test_shim_forwards_exact_arguments_working_directory_and_exit_without_git(
    tmp_path: Path,
) -> None:
    root, script, executables = shim_fixture(tmp_path)
    executable(
        executables / "spec-dock", "import json, os, sys; print(json.dumps([sys.argv[1:], os.getcwd()])); sys.exit(17)"
    )
    cwd = root / "nested"
    cwd.mkdir()
    arguments = ["--project", str(tmp_path / "missing"), "--help", "--", "a b", "日本語", "line\nnext", "$(never)`,"]
    before = tree_digest(root)
    result = invoke(script, cwd, executables, *arguments)
    assert result.returncode == 17, result.stdout + result.stderr
    assert json.loads(result.stdout) == [arguments, str(cwd)] and not result.stderr
    assert tree_digest(root) == before and not (root / ".git").exists()


@pytest.mark.parametrize("json_mode", [False, True])
def test_missing_external_console_reports_installation_guidance_without_creating_control(
    tmp_path: Path, json_mode: bool
) -> None:
    root, script, executables = shim_fixture(tmp_path)
    before = tree_digest(root)
    result = invoke(script, root, executables, "--help", *(["--json"] if json_mode else []))
    assert result.returncode == 3
    if json_mode:
        payload = json.loads(result.stdout)
        assert payload["schema_version"] == "specdock.cli/v2" and payload["exit_code"] == 3
        assert payload["error"]["code"] == "EXTERNAL_CLI_UNAVAILABLE" and payload["effects"] == []
        assert "install" in payload["error"]["message"] and not result.stderr
        assert "operation_id" not in payload
    else:
        assert not result.stdout and "install" in result.stderr
    assert "control" not in result.stdout + result.stderr
    assert tree_digest(root) == before


@pytest.mark.parametrize("kind", ["symlink", "hardlink", "copy", "older-copy"])
def test_shim_rejects_a_path_candidate_that_would_delegate_recursively(tmp_path: Path, kind: str) -> None:
    root, script, executables = shim_fixture(tmp_path)
    candidate = executables / "spec-dock"
    if kind == "symlink":
        candidate.symlink_to(script)
    elif kind == "hardlink":
        os.link(script, candidate)
    elif kind == "copy":
        candidate.write_bytes(script.read_bytes())
        candidate.chmod(0o755)
    else:
        executable(
            candidate,
            '"""Standalone repository shim: delegate only to the absolute pinned engine."""\nraise SystemExit(99)',
        )
    before = tree_digest(root)
    result = invoke(script, root, executables, "--help", "--json")
    assert result.returncode == 3, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "specdock.cli/v2" and payload["error"]["code"] == "SHIM_RECURSION"
    assert payload["effects"] == [] and not result.stderr
    assert tree_digest(root) == before


def test_shim_accepts_a_symlink_to_a_real_external_console(tmp_path: Path) -> None:
    root, script, executables = shim_fixture(tmp_path)
    console = tmp_path / "real-console"
    executable(console, 'print("external help")')
    (executables / "spec-dock").symlink_to(console)
    before = tree_digest(root)
    result = invoke(script, root, executables, "--help")
    assert result.returncode == 0 and result.stdout == "external help\n" and not result.stderr
    assert tree_digest(root) == before


def test_shim_preserves_the_external_consoles_native_stderr(tmp_path: Path) -> None:
    root, script, executables = shim_fixture(tmp_path)
    executable(
        executables / "spec-dock", 'import sys; sys.stderr.write("native console error\\nsecond line\\n"); sys.exit(5)'
    )
    result = invoke(script, root, executables, "workspace", "validate")
    assert result.returncode == 5 and not result.stdout
    assert result.stderr == "native console error\nsecond line\n"


def test_shim_does_not_interpret_json_after_double_dash_as_a_common_flag(tmp_path: Path) -> None:
    root, script, executables = shim_fixture(tmp_path)
    result = invoke(script, root, executables, "--", "--json")
    assert result.returncode == 3 and not result.stdout and "install" in result.stderr


def test_native_spec_symlink_uses_isolated_python_and_forwards_help_without_git(tmp_path: Path) -> None:
    root, script, executables = shim_fixture(tmp_path)
    shortcut = root / "spec"
    shortcut.symlink_to(script)
    (executables / "python3").symlink_to(sys.executable)
    executable(executables / "spec-dock", "import json, sys; print(json.dumps(sys.argv[1:]))")
    (script.parent / "json.py").write_text("raise SystemExit(91)")
    (script.parent / "shutil.py").write_text("raise SystemExit(92)")
    before = tree_digest(root)
    result = subprocess.run(
        [str(shortcut), "-h"],
        cwd=root,
        env=dict(os.environ, PATH=str(executables)),
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0 and json.loads(result.stdout) == ["-h"] and not result.stderr
    assert tree_digest(root) == before and not (root / ".git").exists()


def test_shim_prevents_caller_pythonpath_from_loading_repository_code_in_the_console(tmp_path: Path) -> None:
    root, script, executables = shim_fixture(tmp_path)
    poison = tmp_path / "poison"
    poison.mkdir()
    (poison / "json.py").write_text("raise SystemExit(91)")
    executable(
        executables / "spec-dock",
        'import json, os; print(json.dumps([os.environ.get("PYTHONPATH"), os.environ.get("SPEC_DOCK_WORKTREE_ROOT")]))',
    )
    before = tree_digest(root)
    result = subprocess.run(
        [sys.executable, "-I", str(script), "--help"],
        cwd=root,
        env=dict(os.environ, PATH=str(executables), PYTHONPATH=str(poison), SPEC_DOCK_WORKTREE_ROOT="keep-this"),
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0 and json.loads(result.stdout) == [None, "keep-this"] and not result.stderr
    assert tree_digest(root) == before
