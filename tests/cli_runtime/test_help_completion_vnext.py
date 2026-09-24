"""Help and completion come from the same catalog without repository access."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.cli.catalog import LEAF_PATHS  # noqa: E402
from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402


def _run(tmp_path: Path, *args: str):
    return run_vnext(args, invocation_cwd=tmp_path, engine_digest="test-engine", engine_version="0.2.4")


def test_help_uses_catalog_and_does_not_require_project(tmp_path: Path) -> None:
    root = _run(tmp_path, "help")
    assert root.exit_code == 0
    assert "scope" in root.stdout and "installation" in root.stdout
    leaf = _run(tmp_path, "help", "work", "start", "--json")
    assert leaf.exit_code == 0
    assert "--switch-active" in json.loads(leaf.stdout)["data"]["help"]
    missing = _run(tmp_path, "help", "unknown", "--json")
    assert missing.exit_code == 3


def test_completions_include_every_catalog_leaf_without_writing_files(tmp_path: Path) -> None:
    before = tuple(tmp_path.iterdir())
    for shell in ("bash", "zsh", "fish"):
        output = _run(tmp_path, "completion", shell)
        assert output.exit_code == 0
        assert "spec-dock" in output.stdout
        for leaf in LEAF_PATHS:
            assert leaf.split()[0] in output.stdout
        if shell in ("bash", "zsh"):
            syntax = subprocess.run([shell, "-n"], input=output.stdout, text=True, capture_output=True, check=False)
            assert syntax.returncode == 0, syntax.stderr
    assert tuple(tmp_path.iterdir()) == before
