"""A fresh CI checkout validates only through a commit-pinned external engine."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess

from tests.cli_runtime.test_scope_github_vnext import _ready_repo

SCRIPT = Path(__file__).resolve().parents[2] / ".github/scripts/specdock-ci-validate.sh"
PACKAGE = Path(__file__).resolve().parents[2] / "src/spec_dock"
PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"


def _source_checkout(root: Path) -> str:
    (root / "src").mkdir(parents=True)
    shutil.copytree(PACKAGE, root / "src/spec_dock", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copy2(PYPROJECT, root / "pyproject.toml")
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "--all"], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "fixed source",
        ],
        check=True,
    )
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()


def test_ci_validator_checks_source_sha_and_keeps_target_unmodified(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    sha = _source_checkout(source)
    common = _ready_repo(tmp_path / "consumer")
    target = common["repo_root"]
    assert isinstance(target, Path)
    shutil.rmtree(target / ".git/spec-dock")
    before = (target / "spec-dock/workspace.json").read_bytes()
    verified = subprocess.run(
        ["bash", str(SCRIPT), str(source), str(target), sha], capture_output=True, text=True, check=False
    )
    assert verified.returncode == 0, verified.stderr
    assert f"SpecDock CI source={sha} distribution=" in verified.stdout
    assert json.loads(verified.stdout.splitlines()[-1])["data"]["valid"] is True
    assert (target / "spec-dock/workspace.json").read_bytes() == before
    assert not (target / ".git/spec-dock").exists()
    rejected = subprocess.run(
        ["bash", str(SCRIPT), str(source), str(target), "0" * 40], capture_output=True, text=True, check=False
    )
    assert rejected.returncode == 3 and "SHA mismatch" in rejected.stderr
