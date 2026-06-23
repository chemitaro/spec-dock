import os
from pathlib import Path
import subprocess


def test_static_analysis_script_summarizes_failure_and_runs_later_phases(tmp_path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    uv_stub = fake_bin / "uv"
    uv_stub.write_text(
        """#!/usr/bin/env bash
set -u

printf 'stub uv: %s\\n' "$*"

if [ "$1" = "run" ] && [ "$2" = "ruff" ] && [ "$3" = "check" ]; then
  exit 7
fi

exit 0
""",
        encoding="utf-8",
    )
    uv_stub.chmod(0o755)

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"

    result = subprocess.run(
        [str(repo_root / "scripts/static_analysis/run.sh")],
        cwd=repo_root,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr

    assert result.returncode == 1
    assert "==> ruff check" in output
    assert "==> ruff format check" in output
    assert "==> mypy" in output
    assert "- ruff check: fail (7)" in output
    assert "- ruff format check: pass" in output
    assert "- mypy: pass" in output
