"""Normal wheel distribution and real, isolated console utilities (Issue #413)."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import zipfile

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10
    import tomli as tomllib

from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.cli_runtime.test_cli_vnext_contract import LEAF_PATHS
from tests.cli_runtime.test_issue413_work_start import committed_workspace
from tests.integration.test_issue413_assets import uninitialized_worktree

ROOT = Path(__file__).resolve().parents[2]


def test_fresh_wheel_contains_one_normal_runtime_and_context_free_utilities(tmp_path: Path) -> None:
    wheel_dir = tmp_path / "wheels"
    subprocess.run(["uv", "build", "--wheel", "--out-dir", str(wheel_dir)], cwd=ROOT, check=True, capture_output=True)
    wheel = next(wheel_dir.glob("*.whl"))
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        expected_runtime = {
            "spec_dock/" + path.relative_to(ROOT / "src/spec_dock").as_posix()
            for path in (ROOT / "src/spec_dock/runtime").rglob("*.py")
        }
        assert {
            name for name in names if name.startswith("spec_dock/runtime/") and name.endswith(".py")
        } == expected_runtime
        assert "spec_dock/runtime/cli/options.py" in names
        assert not any("/scripts/spec_dock_runtime/" in name for name in names)
        assert not any("__pycache__" in name or name.endswith((".pyc", ".pyo")) for name in names)
        assert "spec_dock/assets/spec_dock/.gitignore" in names
        assert "spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md" in names
        assert "spec_dock/assets/static-inventory.json" in names
        assert json.loads(archive.read("spec_dock/assets/spec_dock/workspace.json")) == {
            "schema_version": 3,
            "writer_protocol": "specdock.worktree-writer/v1",
        }
        assert (
            archive.read("spec_dock/assets/spec_dock/scripts/spec-dock")
            == (ROOT / "src/spec_dock/shim_vnext.py").read_bytes()
        )
        assert (
            archive.read("spec_dock/assets/spec_dock/scripts/README.md")
            == (ROOT / "src/spec_dock/assets/spec_dock/scripts/README.md").read_bytes()
        )

    # The real sdist build must ship the same package, including hidden assets.
    sdist_dir = tmp_path / "sdist"
    subprocess.run(["uv", "build", "--sdist", "--out-dir", str(sdist_dir)], cwd=ROOT, check=True, capture_output=True)
    unpacked = tmp_path / "unpacked"
    with tarfile.open(next(sdist_dir.glob("*.tar.gz"))) as archive:
        archive.extractall(unpacked, filter="data") if sys.version_info >= (3, 12) else archive.extractall(unpacked)
    source = next(unpacked.iterdir())
    derived_dir = tmp_path / "derived-wheel"
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(derived_dir)], cwd=source, check=True, capture_output=True
    )
    with zipfile.ZipFile(next(derived_dir.glob("*.whl"))) as archive:
        assert {name for name in names if name.startswith("spec_dock/")} == {
            name for name in archive.namelist() if name.startswith("spec_dock/")
        }

    environment = {key: value for key, value in os.environ.items() if key not in {"PYTHONPATH", "PYTHONHOME"}}
    venv = tmp_path / "installed"
    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True, capture_output=True, env=environment)
    python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    subprocess.run(
        [str(python), "-m", "pip", "install", "--no-deps", str(wheel)],
        check=True,
        capture_output=True,
        env=environment,
    )
    package_path = subprocess.check_output(
        [str(python), "-I", "-c", "import spec_dock; print(spec_dock.__file__)"], text=True, env=environment
    ).strip()
    assert Path(package_path).is_relative_to(venv)
    probe = subprocess.run(
        [
            str(python),
            "-I",
            "-c",
            "import sys; from spec_dock.cli import main; "
            "main(['--project', '/missing', '--help']); "
            "assert not any(name.startswith(('spec_dock.runtime.application', "
            "'spec_dock.runtime.commands', 'spec_dock.runtime.infra', "
            "'spec_dock.runtime.domain.operation', 'spec_dock.fixed_bundle', "
            "'spec_dock.runtime_loader')) for name in sys.modules)",
        ],
        capture_output=True,
        text=True,
        env=environment,
        check=False,
    )
    assert probe.returncode == 0, probe.stderr
    Path(package_path).with_name("version.txt").write_text("9.9.9\n", encoding="utf-8")
    expected_version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    console = venv / ("Scripts/spec-dock.exe" if os.name == "nt" else "bin/spec-dock")
    outside = tmp_path / "outside"
    outside.mkdir()
    environment.update(PATH="", PYTHONDONTWRITEBYTECODE="1")
    calls = [["--help"], ["--version"], *([*leaf.split(), "--help"] for leaf in LEAF_PATHS)]
    calls.extend(["completion", shell] for shell in ("bash", "zsh", "fish"))
    for arguments in calls:
        completed = subprocess.run(
            [str(console), "--project", str(outside / "missing"), *arguments, "--json"],
            cwd=outside,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 0, (arguments, completed.stdout, completed.stderr)
        payload = json.loads(completed.stdout)
        assert payload["schema_version"] == "specdock.cli/v2"
        assert payload["status"] == "succeeded"
        assert payload["exit_code"] == completed.returncode
        assert payload["data"]["kind"] == "utility"
        assert payload["effects"] == []
        assert "operation_id" not in payload
        if arguments == ["--version"]:
            assert payload["data"]["version"] == expected_version
        assert not completed.stderr
    invalid = subprocess.run(
        [str(console), "--project", str(outside / "missing"), "work", "release", "--json"],
        cwd=outside,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert invalid.returncode == 2
    assert not invalid.stderr
    assert json.loads(invalid.stdout)["schema_version"] == "specdock.cli/v2"
    assert not tuple(outside.iterdir())

    consumer = committed_workspace(tmp_path / "consumer")
    validation_environment = dict(environment, PATH=os.environ.get("PATH", ""))
    for flags in ([], ["--ci"]):
        if flags:
            (consumer / "spec-dock/workspace.json").write_bytes(b"private uncommitted declaration")
            next((consumer / "spec-dock/initiatives").rglob(".meta.json")).write_bytes(b"private uncommitted metadata")
        before = tree_digest(consumer)
        validation = subprocess.run(
            [str(console), "--project", str(consumer), "workspace", "validate", *flags, "--json"],
            cwd=outside,
            env=validation_environment,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        assert validation.returncode == 0, validation.stdout + validation.stderr
        payload = json.loads(validation.stdout)
        assert payload["data"]["kind"] == "validation" and payload["data"]["result"]["valid"] is True
        assert payload["data"]["result"]["snapshot_source"] == ("HEAD" if flags else "working-tree")
        assert payload["data"]["result"]["node_count"] == 1 and payload["effects"] == []
        assert not validation.stderr and "private" not in validation.stdout
        assert tree_digest(consumer) == before
        assert not (consumer / "spec-dock/.agent").exists() and not (consumer / ".git/spec-dock").exists()

    installed_shim = Path(package_path).with_name("assets") / "spec_dock/scripts/spec-dock"
    consumer_shim = consumer / "spec-dock/scripts/spec-dock"
    consumer_shim.parent.mkdir()
    consumer_shim.write_bytes(installed_shim.read_bytes())
    console_environment = dict(
        validation_environment, PATH=str(console.parent) + os.pathsep + validation_environment["PATH"]
    )
    before = tree_digest(consumer)
    delegated = subprocess.run(
        [sys.executable, "-I", str(consumer_shim), "--version", "--json"],
        cwd=outside,
        env=console_environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert delegated.returncode == 0, delegated.stdout + delegated.stderr
    assert json.loads(delegated.stdout)["data"]["version"] == expected_version and not delegated.stderr
    assert tree_digest(consumer) == before

    initialized = uninitialized_worktree(tmp_path / "new-consumer")
    git_before = tree_digest(initialized / ".git")
    init = subprocess.run(
        [str(console), "installation", "init", str(initialized), "--yes", "--json"],
        cwd=outside,
        env=console_environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert init.returncode == 0, init.stdout + init.stderr
    payload = json.loads(init.stdout)
    assert payload["data"]["result"]["package_version"] == expected_version and not init.stderr
    assert payload["data"]["result"]["target"] == str(initialized)
    assert json.loads((initialized / "spec-dock/workspace.json").read_bytes()) == {
        "schema_version": 3,
        "writer_protocol": "specdock.worktree-writer/v1",
    }
    assert not (initialized / "spec-dock/scripts/spec_dock_runtime").exists()
    assert not (initialized / "spec-dock/.agent").exists() and tree_digest(initialized / ".git") == git_before
    shown_before = tree_digest(initialized)
    show = subprocess.run(
        [str(console), "installation", "show", "--target", str(initialized), "--json"],
        cwd=outside,
        env=console_environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert show.returncode == 0, show.stdout + show.stderr
    assert all(asset["classification"] == "current" for asset in json.loads(show.stdout)["data"]["result"]["assets"])
    assert not show.stderr and tree_digest(initialized) == shown_before
