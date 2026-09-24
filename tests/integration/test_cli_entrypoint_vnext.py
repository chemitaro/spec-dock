"""The future supported entrypoint pins an external engine distribution."""

import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from spec_dock.runtime_loader import (
    EnginePin,
    digest_distribution,
    read_engine_pin,
    verify_engine_pin,
    write_engine_pin,
)


def _fixture_engine(tmp_path: Path) -> tuple[Path, Path, Path]:
    checkout = tmp_path / "checkout"
    checkout.mkdir()
    installed = tmp_path / "installed"
    package = installed / "spec_dock"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("VERSION = 'fixed'\n", encoding="utf-8")
    executable = installed / "bin" / "spec-dock"
    executable.parent.mkdir()
    executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    executable.chmod(0o755)
    return checkout, installed, executable


def test_external_engine_pin_uses_absolute_package_and_digest(tmp_path: Path) -> None:
    checkout, distribution, executable = _fixture_engine(tmp_path)
    pin = EnginePin(executable, distribution, digest_distribution(distribution))
    verified = verify_engine_pin(pin, checkout_root=checkout)
    assert verified.executable == executable
    (distribution / "spec_dock" / "__init__.py").write_text("VERSION = 'changed'\n", encoding="utf-8")
    with pytest.raises(ValueError, match="digest"):
        verify_engine_pin(pin, checkout_root=checkout)


def test_checkout_runtime_and_symlinked_engine_are_rejected(tmp_path: Path) -> None:
    checkout, distribution, executable = _fixture_engine(tmp_path)
    local_package = checkout / "spec_dock"
    local_package.mkdir()
    (local_package / "__init__.py").write_text("local\n", encoding="utf-8")
    local_executable = checkout / "spec-dock"
    local_executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    local_executable.chmod(0o755)
    with pytest.raises(ValueError, match="checkout"):
        verify_engine_pin(EnginePin(local_executable, checkout, digest_distribution(checkout)), checkout_root=checkout)
    alias = tmp_path / "engine-link"
    alias.symlink_to(executable)
    with pytest.raises(ValueError, match="symlink"):
        verify_engine_pin(EnginePin(alias, distribution, digest_distribution(distribution)), checkout_root=checkout)


def test_executable_tamper_and_relative_pin_are_rejected(tmp_path: Path) -> None:
    checkout, distribution, executable = _fixture_engine(tmp_path)
    pin = EnginePin(executable, distribution, digest_distribution(distribution))
    executable.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="digest"):
        verify_engine_pin(pin, checkout_root=checkout)
    with pytest.raises(ValueError, match="absolute"):
        verify_engine_pin(EnginePin(Path("spec-dock"), distribution, pin.distribution_digest), checkout_root=checkout)


def test_engine_locator_matches_control_and_verifies_full_distribution(tmp_path: Path) -> None:
    checkout, distribution, executable = _fixture_engine(tmp_path)
    digest = digest_distribution(distribution)
    common = tmp_path / "common"
    control = common / "spec-dock/control"
    control.mkdir(parents=True)
    (control / "engine.json").write_text(
        json.dumps({
            "schema_version": 1,
            "executable": str(executable),
            "distribution_root": str(distribution),
            "distribution_digest": digest,
        }),
        encoding="utf-8",
    )
    (control / "control.json").write_text(json.dumps({"engine_digest": digest}), encoding="utf-8")
    assert read_engine_pin(common, checkout_root=checkout).distribution_digest == digest
    (control / "control.json").write_text(json.dumps({"engine_digest": "a" * 64}), encoding="utf-8")
    with pytest.raises(ValueError, match="disagree"):
        read_engine_pin(common, checkout_root=checkout)


def test_engine_locator_does_not_replace_an_existing_pin(tmp_path: Path) -> None:
    checkout, distribution, executable = _fixture_engine(tmp_path)
    digest = digest_distribution(distribution)
    common = tmp_path / "common"
    common.mkdir()
    verified = verify_engine_pin(EnginePin(executable, distribution, digest), checkout_root=checkout)
    write_engine_pin(common, verified)
    path = common / "spec-dock/control/engine.json"
    before = path.read_bytes()
    write_engine_pin(common, verified)
    assert path.read_bytes() == before
    with pytest.raises(ValueError, match="another distribution"):
        write_engine_pin(common, type(verified)(executable, distribution, "a" * 64))
    assert path.read_bytes() == before


def test_external_package_cli_runs_without_checkout_runtime_import(tmp_path: Path) -> None:
    source_package = Path(__file__).resolve().parents[2] / "src/spec_dock"
    distribution = tmp_path / "fixed-engine"
    library = distribution / "lib"
    library.mkdir(parents=True)
    shutil.copytree(
        source_package,
        library / "spec_dock",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )
    executable = distribution / "bin/spec-dock"
    executable.parent.mkdir()
    executable.write_text(
        f"#!{sys.executable}\nimport sys\nsys.path.insert(0, {str(library)!r})\n"
        "from spec_dock.external_cli import main\nraise SystemExit(main())\n",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    repo = tmp_path / "consumer"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    environment = {"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1"}
    help_result = subprocess.run(
        [str(executable), "help"], cwd=repo, env=environment, capture_output=True, text=True, check=False
    )
    assert help_result.returncode == 0, help_result.stderr
    installed = subprocess.run(
        [str(executable), "installation", "init", str(repo), "--yes", "--json"],
        cwd=repo,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert installed.returncode == 0, installed.stderr
    assert (repo / "spec-dock/workspace.json").is_file()
    assert read_engine_pin(repo / ".git", checkout_root=repo).executable == executable
    shim = repo / "spec-dock/scripts/spec-dock"
    shim.write_bytes((Path(__file__).resolve().parents[2] / "src/spec_dock/shim_vnext.py").read_bytes())
    shim.chmod(0o755)
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    fake = fake_bin / "spec-dock"
    fake.write_text("#!/bin/sh\necho SPOOF\n", encoding="utf-8")
    fake.chmod(0o755)
    environment["PATH"] = f"{fake_bin}:/usr/bin:/bin"
    marker = tmp_path / "checkout-imported"
    (repo / "sitecustomize.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('unsafe')\n", encoding="utf-8"
    )
    environment["PYTHONPATH"] = str(repo)
    through_shim = subprocess.run(
        [str(shim), "--version"], cwd=repo, env=environment, capture_output=True, text=True, check=False
    )
    assert through_shim.returncode == 0, through_shim.stderr
    assert "SPOOF" not in through_shim.stdout
    assert through_shim.stdout.startswith("spec-dock ")
    scoped = subprocess.run(
        [str(shim), "scope", "list", "--json"],
        cwd=repo,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert scoped.returncode == 0, scoped.stderr
    assert json.loads(scoped.stdout)["status"] == "succeeded"
    assert not marker.exists()
    alternate = tmp_path / "other-engine"
    shutil.copytree(distribution, alternate)
    alternate_executable = alternate / "bin/spec-dock"
    alternate_executable.write_text(
        f"#!{sys.executable}\nimport sys\nsys.path.insert(0, {str(alternate / 'lib')!r})\n"
        "from spec_dock.external_cli import main\nraise SystemExit(main())\n",
        encoding="utf-8",
    )
    alternate_executable.chmod(0o755)
    safe_environment = {key: value for key, value in environment.items() if key != "PYTHONPATH"}
    rejected = subprocess.run(
        [str(alternate_executable), "scope", "list", "--json"],
        cwd=repo,
        env=safe_environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert rejected.returncode == 3 and "differs from repository pin" in rejected.stderr
