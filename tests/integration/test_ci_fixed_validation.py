"""A verified CI checkout validates through an externally installed ordinary wheel."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import stat
import subprocess

import pytest

from tests.cli_runtime.test_issue413_work_start import committed_workspace

SCRIPT = Path(__file__).resolve().parents[2] / ".github/scripts/specdock-ci-validate.sh"
PACKAGE = Path(__file__).resolve().parents[2] / "src/spec_dock"
PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"
PROVIDER = Path(__file__).resolve().parents[2]
WORKFLOW = Path(__file__).resolve().parents[2] / ".github/workflows/ci.yml"


def test_ci_workflow_uses_verified_read_only_wheel_validator() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert workflow.count("bash .github/scripts/specdock-ci-validate.sh") == 1
    assert "${{ github.sha }}" in workflow
    for forbidden in ("spec-dock sync", "spec-dock/scripts/spec-dock", "workspace sync"):
        assert forbidden not in workflow
    script = SCRIPT.read_text(encoding="utf-8")
    assert "rev-parse --verify 'HEAD^{commit}'" in script
    assert '"$actual_sha" != "$expected_sha"' in script
    assert "fixed_bundle" not in script and "runtime_loader" not in script
    assert 'python-version: "3.11"' in workflow and "python -m pip install uv" in workflow


def _source_checkout(root: Path, *, broken_build: bool = False) -> str:
    (root / "src").mkdir(parents=True)
    shutil.copytree(PACKAGE, root / "src/spec_dock", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copy2(PYPROJECT, root / "pyproject.toml")
    for name in ("README.md", "setup.py"):
        shutil.copy2(PROVIDER / name, root / name)
    builder = root / "src/spec_dock/fixed_bundle.py"
    builder.write_text(
        f"from pathlib import Path\nPath({str(root.parent / 'retired-builder-ran')!r}).touch()\n"
        "raise RuntimeError('retired fixed builder executed')\n",
        encoding="utf-8",
    )
    if broken_build:
        setup = root / "setup.py"
        setup.write_text(
            f"from pathlib import Path\nPath({str(root.parent / 'build-reached')!r}).touch()\n"
            "raise RuntimeError('fixture wheel build refused')\n",
            encoding="utf-8",
        )
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


def _target_checkout(root: Path, *, installed: bool = False) -> Path:
    root.mkdir()
    target = committed_workspace((root / "repo").resolve())
    if installed:
        control = target / ".git/spec-dock/control"
        control.mkdir(parents=True)
        (control / "engine.json").write_bytes(b"opaque retired locator")
    active = target / "spec-dock/active"
    active.mkdir()
    (active / "issue").symlink_to("../system/active-none/issue", target_is_directory=True)
    generated = target / "spec-dock/.agent"
    generated.mkdir()
    (generated / "index.json").write_text('{"sentinel": true}\n', encoding="utf-8")
    (generated / "index.json").chmod(0o640)
    return target


def _snapshot(root: Path) -> dict[str, tuple[str, int, bytes | str | None]]:
    result = {}
    for path in (root, *root.rglob("*")):
        mode = path.lstat().st_mode
        kind, value = (
            ("link", str(path.readlink()))
            if stat.S_ISLNK(mode)
            else ("file", path.read_bytes())
            if stat.S_ISREG(mode)
            else ("directory", None)
        )
        result[str(path.relative_to(root))] = (kind, stat.S_IMODE(mode), value)
    return result


def _validate(source: Path, target: Path, sha: str) -> subprocess.CompletedProcess[str]:
    source_before = _snapshot(source)
    before = _snapshot(target)
    result = subprocess.run(
        ["bash", str(SCRIPT), str(source), str(target), sha], capture_output=True, text=True, check=False
    )
    assert _snapshot(target) == before
    assert _snapshot(source) == source_before
    return result


def test_ci_validator_checks_source_sha_and_keeps_target_unmodified(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    sha = _source_checkout(source)
    target = _target_checkout(tmp_path / "consumer")
    verified = _validate(source, target, sha)
    assert verified.returncode == 0, verified.stdout + verified.stderr
    assert f"SpecDock CI source={sha} wheel_sha256=" in verified.stdout
    result = json.loads(verified.stdout.splitlines()[-1])
    assert result["schema_version"] == "specdock.cli/v2"
    assert result["data"]["result"]["valid"] is True
    assert result["data"]["result"]["snapshot_source"] == "HEAD" and result["effects"] == []
    assert not (target / ".git/spec-dock").exists()
    marker = tmp_path / "build-reached"
    assert not marker.exists()
    assert not (tmp_path / "retired-builder-ran").exists()
    rejected = _validate(source, target, "0" * 40)
    assert rejected.returncode == 3 and "SHA mismatch" in rejected.stderr
    assert not marker.exists()


@pytest.mark.parametrize("case", ["tracked-dirty", "untracked-dirty", "short-sha", "non-hex-sha"])
def test_ci_validator_rejects_untrusted_source_before_build(tmp_path: Path, case: str) -> None:
    source = tmp_path / "source"
    source.mkdir()
    sha = _source_checkout(source)
    target = _target_checkout(tmp_path / "consumer", installed=True)
    if case == "tracked-dirty":
        with (source / "pyproject.toml").open("a", encoding="utf-8") as file:
            file.write("\n# uncommitted\n")
    elif case == "untracked-dirty":
        (source / "untracked.txt").write_text("uncommitted", encoding="utf-8")
    elif case == "short-sha":
        sha = sha[:12]
    else:
        sha = "g" * 40
    rejected = _validate(source, target, sha)
    dirty = case.endswith("dirty")
    assert rejected.returncode == (3 if dirty else 2)
    assert ("checkout is dirty" if dirty else "complete Git commit ID") in rejected.stderr
    assert not (tmp_path / "build-reached").exists()
    assert not (tmp_path / "retired-builder-ran").exists()


def test_ci_validator_stops_on_failed_wheel_build_without_touching_target(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    sha = _source_checkout(source, broken_build=True)
    target = _target_checkout(tmp_path / "consumer", installed=True)
    rejected = _validate(source, target, sha)
    assert rejected.returncode != 0 and "fixture wheel build refused" in rejected.stderr
    assert (tmp_path / "build-reached").exists()
    assert not (tmp_path / "retired-builder-ran").exists()
    assert "SpecDock CI source=" not in rejected.stdout
