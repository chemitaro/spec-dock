"""The future supported entrypoint pins an external engine distribution."""

import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10
    import tomli as tomllib

import pytest

from spec_dock.runtime_loader import (
    EnginePin,
    digest_distribution,
    read_engine_pin,
    verify_engine_pin,
    write_engine_pin,
)
from tests.cli_runtime.test_scope_github_vnext import _ready_repo


def test_fixed_distribution_builder_isolation_and_digest(tmp_path: Path) -> None:
    from spec_dock.fixed_bundle import build_fixed_engine

    distribution = tmp_path / "engine"
    executable = build_fixed_engine(distribution)
    assert executable == distribution / "bin/spec-dock"
    assert executable.is_file()
    repo = tmp_path / "consumer"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    output = subprocess.run(
        [str(executable), "--help", "--json"],
        cwd=repo,
        env={"PATH": "/usr/bin:/bin", "PYTHONPATH": str(repo)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert output.returncode == 0, output.stderr
    assert json.loads(output.stdout)["status"] == "succeeded"
    assert len(digest_distribution(distribution)) == 64


def test_fixed_engine_ci_validate_requires_no_repository_control_and_writes_nothing(tmp_path: Path) -> None:
    from spec_dock.fixed_bundle import build_fixed_engine

    common = _ready_repo(tmp_path)
    repo = common["repo_root"]
    assert isinstance(repo, Path)
    control_directory = repo / ".git/spec-dock"
    shutil.rmtree(control_directory)
    before = (repo / "spec-dock/workspace.json").read_bytes()
    executable = build_fixed_engine(tmp_path / "engine")
    result = subprocess.run(
        [str(executable), "workspace", "validate", "--ci", "--json"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "succeeded"
    assert payload["data"]["valid"] is True
    assert payload["effects"] == []
    assert (repo / "spec-dock/workspace.json").read_bytes() == before
    assert not control_directory.exists()
    ordinary = subprocess.run(
        [str(executable), "workspace", "validate", "--json"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert ordinary.returncode != 0


def test_fixed_distribution_version_comes_from_its_own_bytes(tmp_path: Path) -> None:
    import spec_dock

    package = tmp_path / "spec_dock"
    package.mkdir()
    shutil.copy2(Path(spec_dock.__file__), package / "__init__.py")
    (package / "version.txt").write_text("9.9.9\n", encoding="utf-8")
    assert runpy.run_path(str(package / "__init__.py"))["__version__"] == "9.9.9"


def test_fixed_distribution_builder_rejects_checkout_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import spec_dock.fixed_bundle as builder

    checkout = tmp_path / "repo"
    source = checkout / "src/spec_dock"
    source.mkdir(parents=True)
    (source / "__init__.py").write_text("\n")
    (source / "fixed_bundle.py").write_text("\n")
    subprocess.run(["git", "init", "-q", str(checkout)], check=True)
    monkeypatch.setattr(builder, "__file__", str(source / "fixed_bundle.py"))
    with pytest.raises(ValueError, match="checkout"):
        builder.build_fixed_engine(checkout / "engine")


def test_wheel_layout_is_not_a_fixed_mutating_engine(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import spec_dock.external_cli as module

    checkout = tmp_path / "consumer"
    checkout.mkdir()
    distribution = tmp_path / "venv"
    package = distribution / "lib/python3.12/site-packages/spec_dock"
    assets = package / "assets"
    assets.mkdir(parents=True)
    package_file = package / "external_cli.py"
    package_file.write_text("# wheel package\n", encoding="utf-8")
    executable = distribution / "bin/spec-dock"
    executable.parent.mkdir()
    executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    executable.chmod(0o755)
    monkeypatch.setattr(module, "__file__", str(package_file))
    monkeypatch.setattr(module, "ASSETS", assets)
    with pytest.raises(ValueError, match="fixed distribution layout"):
        module._executing_engine(executable=executable, checkout_root=checkout)


def test_public_entrypoints_use_fixed_engine() -> None:
    root = Path(__file__).resolve().parents[2]
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["project"]["scripts"]["spec-dock"] == "spec_dock.cli:main"
    assert (root / "src/spec_dock/assets/spec_dock/scripts/spec-dock").read_bytes() == (
        root / "src/spec_dock/shim_vnext.py"
    ).read_bytes()


def test_package_entrypoint_exposes_read_only_help_without_repository_pin(capsys: pytest.CaptureFixture[str]) -> None:
    from spec_dock.cli import main

    assert main(["--help", "--json"]) == 0
    output = capsys.readouterr()
    assert json.loads(output.out)["status"] == "succeeded"
    assert "scope" in output.out and "work" in output.out


def test_public_entrypoint_rejects_retired_installer_before_write(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.cli import main

    assert main(["init", str(tmp_path), "--json"]) == 2
    output = capsys.readouterr()
    assert json.loads(output.out)["error"]["code"] in {"USAGE_ERROR", "COMMAND_REMOVED"}
    assert not (tmp_path / "spec-dock").exists()


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
    (library / "spec_dock/version.txt").write_text("0.2.4\n", encoding="utf-8")
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
    outside_show = subprocess.run(
        [str(executable), "installation", "show", "--target", str(repo), "--json"],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert outside_show.returncode == 0, outside_show.stderr
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
    hostile = tmp_path / "hostile-repo"
    hostile.mkdir()
    subprocess.run(["git", "-C", str(hostile), "init", "-q"], check=True)
    hostile_environment = {
        **environment,
        "GIT_DIR": str(hostile / ".git"),
        "GIT_WORK_TREE": str(hostile),
    }
    isolated = subprocess.run(
        [str(shim), "scope", "list", "--json"],
        cwd=repo,
        env=hostile_environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert isolated.returncode == 0, isolated.stdout + isolated.stderr
    assert json.loads(isolated.stdout)["status"] == "succeeded"
    original_engine = executable.read_bytes()
    start_of_code = original_engine.index(b"\n") + 1
    tamper_marker = tmp_path / "tampered-engine-ran"
    executable.write_bytes(
        original_engine[:start_of_code]
        + f"from pathlib import Path\nPath({str(tamper_marker)!r}).write_text('unsafe')\n".encode()
        + original_engine[start_of_code:]
    )
    refused = subprocess.run(
        [str(shim), "--version"], cwd=repo, env=environment, capture_output=True, text=True, check=False
    )
    refused_json = subprocess.run(
        [str(shim), "scope", "list", "--json"],
        cwd=repo,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    executable.write_bytes(original_engine)
    assert refused.returncode != 0
    assert refused_json.returncode == 3 and refused_json.stderr == ""
    shim_error = json.loads(refused_json.stdout)
    assert shim_error["schema_version"] == "specdock.cli/v1"
    assert shim_error["error"]["code"] == "ENGINE_PREFLIGHT_FAILED"
    assert shim_error["effects"] == []
    assert not tamper_marker.exists()
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
    assert rejected.returncode == 3 and rejected.stderr == ""
    engine_error = json.loads(rejected.stdout)
    assert engine_error["schema_version"] == "specdock.cli/v1"
    assert engine_error["error"]["code"] == "ENGINE_PREFLIGHT_FAILED"
    assert engine_error["effects"] == []


def test_two_consumers_share_one_fixed_engine_without_shared_control(tmp_path: Path) -> None:
    from spec_dock.fixed_bundle import build_fixed_engine

    executable = build_fixed_engine(tmp_path / "engine")
    common_dirs: list[Path] = []
    for name in ("first", "second"):
        repo = tmp_path / name
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        installed = subprocess.run(
            [str(executable), "installation", "init", str(repo), "--yes", "--json"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )
        assert installed.returncode == 0, installed.stderr
        created = subprocess.run(
            [
                str(repo / "spec-dock/scripts/spec-dock"),
                "scope",
                "create",
                "initiative",
                "--backend",
                "local",
                "--title",
                name,
                "--json",
            ],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )
        assert created.returncode == 0, created.stderr
        assert json.loads(created.stdout)["status"] == "succeeded"
        common_dirs.append(repo / ".git/spec-dock/control")
    assert common_dirs[0] != common_dirs[1]
    for control in common_dirs:
        assert (control / "engine.json").is_file()
    first, second = tmp_path / "first", tmp_path / "second"
    wrong_cwd = subprocess.run(
        [str(first / "spec-dock/scripts/spec-dock"), "scope", "list", "--json"],
        cwd=second,
        capture_output=True,
        text=True,
        check=False,
    )
    assert wrong_cwd.returncode != 0
    wrong_project = subprocess.run(
        [str(first / "spec-dock/scripts/spec-dock"), "--project", str(second), "scope", "list", "--json"],
        cwd=first,
        capture_output=True,
        text=True,
        check=False,
    )
    assert wrong_project.returncode != 0
    third = tmp_path / "third"
    third.mkdir()
    subprocess.run(["git", "init", "-q", str(third)], check=True)
    wrong_init = subprocess.run(
        [str(first / "spec-dock/scripts/spec-dock"), "installation", "init", str(third), "--yes", "--json"],
        cwd=first,
        capture_output=True,
        text=True,
        check=False,
    )
    assert wrong_init.returncode != 0
    assert not (third / "spec-dock").exists()
