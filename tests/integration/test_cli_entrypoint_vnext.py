"""The supported entrypoint uses an ordinary external package without Git control."""

import json
import os
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

from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.cli_runtime.test_issue413_work_start import committed_workspace


@pytest.fixture(scope="module")
def installed_console(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Exercise a non-editable wheel outside the source checkout."""
    root = Path(__file__).resolve().parents[2]
    outside = tmp_path_factory.mktemp("entrypoint-wheel").resolve()
    environment = {key: value for key, value in os.environ.items() if key not in {"PYTHONPATH", "PYTHONHOME"}}
    wheels = outside / "wheels"
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(wheels)],
        cwd=root,
        env=environment,
        check=True,
        capture_output=True,
    )
    wheel = next(wheels.glob("*.whl"))
    venv = outside / "installed"
    subprocess.run([sys.executable, "-m", "venv", str(venv)], env=environment, check=True, capture_output=True)
    python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    subprocess.run(
        [str(python), "-m", "pip", "install", "--no-index", "--no-deps", str(wheel)],
        env=environment,
        check=True,
        capture_output=True,
    )
    imported = subprocess.check_output(
        [str(python), "-I", "-c", "import spec_dock; print(spec_dock.__file__)"],
        text=True,
        env=environment,
        cwd=outside,
    ).strip()
    assert Path(imported).is_relative_to(venv)
    assert not Path(imported).is_relative_to(root)
    return venv / ("Scripts/spec-dock.exe" if os.name == "nt" else "bin/spec-dock")


def _console(
    executable: Path, arguments: list[str], *, cwd: Path, environment: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    isolated = {key: value for key, value in os.environ.items() if key not in {"PYTHONPATH", "PYTHONHOME"}}
    isolated.update(PYTHONDONTWRITEBYTECODE="1", GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    if environment is not None:
        isolated.update(environment)
    return subprocess.run(
        [str(executable), *arguments], cwd=cwd, env=isolated, capture_output=True, text=True, check=False, timeout=30
    )


def test_installed_console_starts_syncs_and_finishes_an_issue_without_control(
    installed_console: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from tests.cli_runtime.test_issue413_contract import add_scope
    from tests.cli_runtime.test_issue413_finish import github_fixture

    root = committed_workspace((tmp_path / "consumer").resolve())
    initiative = root / "spec-dock/initiatives/init-00001-fixture"
    epic = add_scope(root, "epic-00002", "epic", "init-00001", initiative)
    issue = add_scope(root, "iss-00003", "issue", "epic-00002", epic)
    subprocess.run(["git", "-C", str(root), "add", "."], check=True, capture_output=True)
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
            "scopes",
        ],
        check=True,
        capture_output=True,
    )
    before = {path: path.read_bytes() for path in (root / "spec-dock").rglob("*") if path.is_file()}
    log = github_fixture(tmp_path, monkeypatch, {"1": "open", "2": "open", "3": "open"})
    started = _console(
        installed_console,
        ["work", "start", "iss-00003", "--branch", "issue-three", "--base", "HEAD", "--json"],
        cwd=root,
    )
    assert started.returncode == 0, started.stdout + started.stderr
    start = json.loads(started.stdout)
    assert start["schema_version"] == "specdock.cli/v2" and not started.stderr
    assert start["data"]["started"] is True and start["data"]["branch_after"] == "issue-three"
    record = root / "spec-dock/.agent/work-target" / f"target-{start['data']['selection_token']}.json"
    assert record.is_file()
    captured = record.read_bytes()
    assert json.loads(captured)["scope_id"] == "iss-00003"
    assert (
        subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"], text=True).strip()
        == "issue-three"
    )
    synced = _console(installed_console, ["workspace", "sync", "--source", "github", "--json"], cwd=root)
    assert synced.returncode == 0, synced.stdout + synced.stderr
    sync = json.loads(synced.stdout)
    assert not synced.stderr and sync["effects"] == []
    assert sync["data"]["complete"] is True
    assert sync["data"]["counts"] == [
        {"scope_id": "init-00001", "direct_selected_count": 0, "descendant_selected_count": 1, "complete": True},
        {"scope_id": "epic-00002", "direct_selected_count": 0, "descendant_selected_count": 1, "complete": True},
        {"scope_id": "iss-00003", "direct_selected_count": 1, "descendant_selected_count": 0, "complete": True},
    ]
    assert sync["data"]["worktrees"][0]["selection"]["scope_id"] == "iss-00003"
    assert sync["data"]["worktrees"][0]["process_state"] == "not_observed"
    assert record.read_bytes() == captured
    finished = _console(installed_console, ["work", "finish", "@current", "--yes", "--json"], cwd=root)
    assert finished.returncode == 0, finished.stdout + finished.stderr
    finish = json.loads(finished.stdout)
    assert not finished.stderr and finish["data"]["completed"] is True
    assert finish["data"]["branch_after"] == "issue-three" and finish["data"]["selection_token"] is None
    assert not record.exists()
    assert (
        subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"], text=True).strip()
        == "issue-three"
    )
    assert not (root / ".git/spec-dock").exists()
    assert all(path.read_bytes() == exact for path, exact in before.items())
    assert json.loads((issue / ".meta.json").read_bytes())["github"]["issue_number"] == 3
    requests = [json.loads(line) for line in log.read_text().splitlines()]
    assert [(row["method"], row["number"]) for row in requests if row["method"] == "PATCH"] == [("PATCH", 3)]
    assert json.loads((tmp_path / "remote-states.json").read_bytes()) == {"1": "open", "2": "open", "3": "completed"}


def test_package_version_ignores_retired_fixed_distribution_version_file(tmp_path: Path) -> None:
    import spec_dock

    package = tmp_path / "spec_dock"
    package.mkdir()
    shutil.copy2(Path(spec_dock.__file__), package / "__init__.py")
    (package / "version.txt").write_text("9.9.9\n", encoding="utf-8")
    project = tomllib.loads((Path(__file__).resolve().parents[2] / "pyproject.toml").read_text(encoding="utf-8"))
    assert runpy.run_path(str(package / "__init__.py"))["__version__"] == project["project"]["version"]


def test_public_entrypoint_and_static_shim_use_normal_package() -> None:
    import spec_dock.cli as package_cli

    root = Path(__file__).resolve().parents[2]
    assert not hasattr(package_cli, "legacy_installer_main")
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["project"]["scripts"]["spec-dock"] == "spec_dock.cli:main"
    assert (root / "src/spec_dock/assets/spec_dock/scripts/spec-dock").read_bytes() == (
        root / "src/spec_dock/shim_vnext.py"
    ).read_bytes()


def test_installed_help_needs_no_git_repository_or_pin(installed_console: Path, tmp_path: Path) -> None:
    output = _console(
        installed_console,
        ["--project", str(tmp_path / "missing"), "--help", "--json"],
        cwd=tmp_path,
        environment={"PATH": ""},
    )
    assert output.returncode == 0, output.stdout + output.stderr
    payload = json.loads(output.stdout)
    assert payload["schema_version"] == "specdock.cli/v2" and payload["status"] == "succeeded"
    assert payload["data"]["kind"] == "utility" and payload["effects"] == [] and not output.stderr
    assert "scope" in payload["data"]["text"] and "work" in payload["data"]["text"]
    assert not tuple(tmp_path.iterdir())


def test_installed_entrypoint_rejects_retired_installer_before_write(installed_console: Path, tmp_path: Path) -> None:
    output = _console(installed_console, ["init", str(tmp_path), "--json"], cwd=tmp_path)
    assert output.returncode == 2, output.stdout + output.stderr
    payload = json.loads(output.stdout)
    assert payload["schema_version"] == "specdock.cli/v2" and payload["status"] == "failed"
    assert payload["error"]["code"] in {"USAGE_ERROR", "COMMAND_REMOVED"}
    assert payload["effects"] == [] and not output.stderr and not tuple(tmp_path.iterdir())


@pytest.mark.parametrize("flags", [[], ["--ci"]], ids=["working-tree", "head"])
def test_installed_validation_needs_no_control_and_writes_nothing(
    installed_console: Path, tmp_path: Path, flags: list[str]
) -> None:
    root = committed_workspace((tmp_path / "consumer").resolve())
    before = tree_digest(root)
    output = _console(installed_console, ["workspace", "validate", *flags, "--json"], cwd=root)
    assert output.returncode == 0, output.stdout + output.stderr
    payload = json.loads(output.stdout)
    assert payload["schema_version"] == "specdock.cli/v2" and payload["status"] == "succeeded"
    assert payload["data"]["result"]["valid"] is True and payload["effects"] == [] and not output.stderr
    assert tree_digest(root) == before
    assert not (root / ".git/spec-dock").exists() and not (root / "spec-dock/.agent").exists()


@pytest.mark.parametrize(
    "locator",
    [
        b"not JSON",
        b'{"executable":"relative/path","distribution_digest":"tampered"}',
        b'{"schema_version":1,"executable":"/missing/engine","distribution_root":"/missing/lib"}',
        b'{"schema_version":1,"distribution_digest":"disagrees-with-control"}',
    ],
    ids=["invalid-json", "relative-tampered", "missing-package", "mismatched-digest"],
)
def test_retired_locators_are_not_execution_authority(installed_console: Path, tmp_path: Path, locator: bytes) -> None:
    root = committed_workspace((tmp_path / "consumer").resolve())
    control = root / ".git/spec-dock/control"
    control.mkdir(parents=True)
    (control / "engine.json").write_bytes(locator)
    (control / "control.json").write_bytes(b'{"engine_digest":"another-retired-digest"}')
    before = tree_digest(root)
    output = _console(installed_console, ["scope", "show", "init-00001", "--json"], cwd=root)
    assert output.returncode == 0, output.stdout + output.stderr
    payload = json.loads(output.stdout)
    assert payload["schema_version"] == "specdock.cli/v2" and payload["effects"] == [] and not output.stderr
    assert payload["data"]["result"]["scope"]["id"] == "init-00001"
    assert tree_digest(root) == before


def _installed_shim(console: Path, root: Path) -> Path:
    python = console.parent / ("python.exe" if os.name == "nt" else "python")
    probe = _console(
        python,
        [
            "-I",
            "-c",
            "from importlib.resources import files; print(files('spec_dock').joinpath('assets/spec_dock/scripts/spec-dock'))",
        ],
        cwd=root,
    )
    assert probe.returncode == 0, probe.stdout + probe.stderr
    asset = Path(probe.stdout.strip())
    assert asset.is_relative_to(console.parent.parent)
    shim = root / "spec-dock/scripts/spec-dock"
    shim.parent.mkdir()
    shim.write_bytes(asset.read_bytes())
    shim.chmod(0o755)
    return shim


@pytest.mark.skipif(os.name != "posix", reason="native POSIX env -S shim execution")
def test_installed_shim_ignores_checkout_python_and_hostile_git_environment(
    installed_console: Path, tmp_path: Path
) -> None:
    root = committed_workspace((tmp_path / "consumer").resolve())
    shim = _installed_shim(installed_console, root)
    marker = tmp_path / "checkout-imported"
    hostile_code = f"from pathlib import Path\nPath({str(marker)!r}).write_text('unsafe')\n"
    (root / "sitecustomize.py").write_text(hostile_code)
    local_package = root / "spec_dock"
    local_package.mkdir()
    (local_package / "__init__.py").write_text(hostile_code)
    local_runtime = root / "spec-dock/scripts/spec_dock_runtime"
    local_runtime.mkdir()
    (local_runtime / "__init__.py").write_text(hostile_code)
    hostile = committed_workspace((tmp_path / "hostile").resolve())
    metadata = hostile / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    metadata.write_text(json.dumps(dict(json.loads(metadata.read_bytes()), title="Hostile")))
    environment = {
        "PATH": str(installed_console.parent) + os.pathsep + os.environ["PATH"],
        "PYTHONPATH": str(root),
        "GIT_DIR": str(hostile / ".git"),
        "GIT_WORK_TREE": str(hostile),
    }
    output = _console(shim, ["scope", "show", "init-00001", "--json"], cwd=root, environment=environment)
    assert output.returncode == 0, output.stdout + output.stderr
    payload = json.loads(output.stdout)
    assert payload["data"]["result"]["scope"]["title"] == "Fixture"
    assert payload["effects"] == [] and not output.stderr and not marker.exists()
    assert not (root / ".git/spec-dock").exists()


@pytest.mark.skipif(os.name != "posix", reason="native POSIX external console symlink")
def test_path_shim_accepts_a_symlink_to_the_installed_console(installed_console: Path, tmp_path: Path) -> None:
    root = committed_workspace((tmp_path / "consumer").resolve())
    shim = _installed_shim(installed_console, root)
    aliases = tmp_path / "aliases"
    aliases.mkdir()
    (aliases / "spec-dock").symlink_to(installed_console)
    output = _console(
        shim,
        ["scope", "show", "init-00001", "--json"],
        cwd=root,
        environment={"PATH": str(aliases) + os.pathsep + os.environ["PATH"]},
    )
    assert output.returncode == 0, output.stdout + output.stderr
    assert json.loads(output.stdout)["data"]["result"]["scope"]["id"] == "init-00001" and not output.stderr


def test_two_consumers_use_one_package_and_resolve_the_requested_git_root(
    installed_console: Path, tmp_path: Path
) -> None:
    consumers = [committed_workspace((tmp_path / name).resolve()) for name in ("first", "second")]
    for root in consumers:
        metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
        metadata.write_text(json.dumps(dict(json.loads(metadata.read_bytes()), title=root.name)))
    first, second = consumers
    first_shim = _installed_shim(installed_console, first)
    environment = {"PATH": str(installed_console.parent) + os.pathsep + os.environ["PATH"]}
    for cwd, arguments, expected in (
        (first, ["scope", "show", "init-00001", "--json"], "first"),
        (second, ["scope", "show", "init-00001", "--json"], "second"),
        (first, ["--project", str(second), "scope", "show", "init-00001", "--json"], "second"),
    ):
        executable = first_shim if os.name == "posix" else installed_console
        output = _console(executable, arguments, cwd=cwd, environment=environment)
        assert output.returncode == 0, output.stdout + output.stderr
        payload = json.loads(output.stdout)
        assert payload["data"]["result"]["scope"]["title"] == expected
        assert payload["effects"] == [] and not output.stderr
    for root in consumers:
        output = _console(installed_console, ["workspace", "sync", "--json"], cwd=root)
        assert output.returncode == 0, output.stdout + output.stderr
        assert [row["path"] for row in json.loads(output.stdout)["data"]["worktrees"]] == [str(root)]
        assert not (root / ".git/spec-dock").exists() and not (root / "spec-dock/.agent").exists()
    subdirectory = second / "spec-dock"
    refused = _console(installed_console, ["--project", str(subdirectory), "scope", "list", "--json"], cwd=first)
    assert refused.returncode == 3, refused.stdout + refused.stderr
    assert json.loads(refused.stdout)["effects"] == [] and not refused.stderr
