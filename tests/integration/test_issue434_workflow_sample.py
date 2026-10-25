"""The shipped check workflow's own commands work in a code checkout (AC-434-09, without GitHub Actions)."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from tests.support.canonical_check import (
    assets_with_ignore_rules,
    code_repository,
    commit,
    provider_root,
    source_checkout_with_ignore_rules,
)

SAMPLE = provider_root() / "src/spec_dock/assets/spec_dock/docs/ci/spec-dock-check.yml"


def _step_commands() -> dict[str, str]:
    """Map each step name to its single-line run command, as the sample writes them."""
    steps = re.findall(r"^      - name: (.+)\n        run: (.+)$", SAMPLE.read_text(encoding="utf-8"), re.MULTILINE)
    return dict(steps)


def _installed_console(tmp_path: Path) -> Path:
    """Build the provider wheel (with the canonical ignore rules) and install it outside every worktree."""
    source = tmp_path / "source"
    source_checkout_with_ignore_rules(source)
    wheels = tmp_path / "wheels"
    subprocess.run(["uv", "build", "--wheel", "--out-dir", str(wheels), str(source)], check=True, capture_output=True)
    venv = tmp_path / "installed"
    subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(venv)], check=True)
    (wheel,) = wheels.glob("*.whl")
    subprocess.run(
        ["uv", "pip", "install", "--python", str(venv / "bin/python"), str(wheel)], check=True, capture_output=True
    )
    return venv / "bin"


def _run_step(command: str, cwd: Path, path: str) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if key not in ("GH_TOKEN", "GITHUB_TOKEN")}
    env["PATH"] = path
    return subprocess.run(["bash", "-c", command], cwd=cwd, env=env, capture_output=True, text=True, check=False)


def test_the_sample_has_exactly_the_install_and_check_steps() -> None:
    assert set(_step_commands()) == {"Install SpecDock", "Check"}


def test_the_install_step_requests_the_version_named_by_the_version_file(tmp_path: Path) -> None:
    target = code_repository(tmp_path / "consumer", assets_with_ignore_rules())
    version = (target / "spec-dock/system/spec-dock-version").read_text(encoding="utf-8").strip()
    stub_bin = tmp_path / "stub-bin"
    stub_bin.mkdir()
    record = tmp_path / "pipx-argv.json"
    stub = stub_bin / "pipx"
    stub.write_text(
        f"#!{sys.executable}\nimport json, sys\nopen({str(record)!r}, 'w').write(json.dumps(sys.argv[1:]))\n",
        encoding="utf-8",
    )
    stub.chmod(0o755)
    result = _run_step(_step_commands()["Install SpecDock"], target, f"{stub_bin}{os.pathsep}/usr/bin:/bin")
    assert result.returncode == 0, result.stderr
    assert json.loads(record.read_text(encoding="utf-8")) == [
        "install",
        f"spec-dock @ git+https://github.com/chemitaro/spec-dock@v{version}",
    ]


def test_the_check_step_passes_a_clean_checkout_and_fails_a_checkout_with_specs(tmp_path: Path) -> None:
    console = _installed_console(tmp_path)
    git_dir = Path(shutil.which("git") or "/usr/bin/git").parent
    path = f"{console}{os.pathsep}{git_dir}{os.pathsep}/usr/bin:/bin"
    target = code_repository(tmp_path / "consumer", assets_with_ignore_rules())
    check = _step_commands()["Check"]

    passed = _run_step(check, target, path)
    assert passed.returncode == 0, passed.stdout + passed.stderr
    assert json.loads(passed.stdout)["data"]["result"]["valid"] is True

    (target / "spec-dock/initiatives/init-00001-plan").mkdir(parents=True)
    (target / "spec-dock/initiatives/init-00001-plan/requirement.md").write_text("spec\n", encoding="utf-8")
    commit(target, "a spec on the default branch")
    failed = _run_step(check, target, path)
    assert failed.returncode == 7, failed.stdout + failed.stderr
    assert json.loads(failed.stdout)["error"]["code"] == "CANONICAL_CHECK_FAILED"
