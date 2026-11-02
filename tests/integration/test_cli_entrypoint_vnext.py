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
from tests.support.canonical_repo import clone, git
from tests.support.canonical_scopes import REPOSITORY, CanonicalWorld
from tests.support.legacy_contracts_g1 import chain_world, select_record


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


@pytest.fixture
def consumer(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    """A linked schema-4 consumer (init-1 / epic-2 / iss-3) with the fake GitHub on PATH and a saved snapshot.

    Only reading commands run through the installed console: a writing command would ensure the periodic sync
    job, which only the in-process stand-in scheduler may do in tests.
    """
    world = chain_world(tmp_path, monkeypatch, capsys)
    assert world.run("scope", "show", "init-00001")[0] == 0
    return world


def _second_clone(world: CanonicalWorld, name: str) -> Path:
    """Another linked clone of the same origin; its catalog has none of the first clone's Scope directories."""
    path = clone(world.tmp_path / "remote.git", world.tmp_path / name)
    git(path, "remote", "set-url", "origin", str(world.tmp_path / "remote.git"))
    code, payload = world.run("canonical", "link", checkout=path)
    assert code == 0, payload
    git(path, "remote", "set-url", "origin", f"https://github.com/{REPOSITORY}.git")
    return path


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
    installed_console: Path, consumer: CanonicalWorld
) -> None:
    # iss-00440: start and finish ensure the periodic sync job, so they run in process (with the stand-in
    # scheduler; see tests/cli_runtime/test_issue440_g1_work_finish.py's lifecycle tests). The installed console
    # observes the started selection without control and without changing it.
    root = consumer.main
    record = select_record(consumer, "iss-00003", 3, branch="main")
    captured = record.read_bytes()
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
    assert not (root / ".git/spec-dock").exists()
    assert consumer.fake().writes() == []


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


def test_installed_validation_needs_no_control_and_writes_nothing(
    installed_console: Path, consumer: CanonicalWorld
) -> None:
    # iss-00440: the `--ci` (HEAD) variant validated committed .meta.json and was removed with legacy mode.
    root = consumer.main
    before = tree_digest(root)
    output = _console(installed_console, ["workspace", "validate", "--json"], cwd=root)
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
def test_retired_locators_are_not_execution_authority(
    installed_console: Path, consumer: CanonicalWorld, locator: bytes
) -> None:
    root = consumer.main
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
    installed_console: Path, consumer: CanonicalWorld, tmp_path: Path
) -> None:
    root = consumer.main
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
    # The hostile clone's catalog has no Scope directories, so a read through it reports directory_found false.
    hostile = _second_clone(consumer, "hostile")
    environment = {
        "PATH": str(installed_console.parent) + os.pathsep + os.environ["PATH"],
        "PYTHONPATH": str(root),
        "GIT_DIR": str(hostile / ".git"),
        "GIT_WORK_TREE": str(hostile),
    }
    output = _console(shim, ["scope", "show", "init-00001", "--json"], cwd=root, environment=environment)
    assert output.returncode == 0, output.stdout + output.stderr
    payload = json.loads(output.stdout)
    assert payload["data"]["result"]["scope"]["directory_found"] is True
    assert payload["effects"] == [] and not output.stderr and not marker.exists()
    assert not (root / ".git/spec-dock").exists()


@pytest.mark.skipif(os.name != "posix", reason="native POSIX external console symlink")
def test_path_shim_accepts_a_symlink_to_the_installed_console(
    installed_console: Path, consumer: CanonicalWorld, tmp_path: Path
) -> None:
    root = consumer.main
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
    installed_console: Path, consumer: CanonicalWorld
) -> None:
    # Both clones read one fake GitHub; only the first clone's catalog has the Scope directories.
    first, second = consumer.main, _second_clone(consumer, "second")
    first_shim = _installed_shim(installed_console, first)
    environment = {"PATH": str(installed_console.parent) + os.pathsep + os.environ["PATH"]}
    for cwd, arguments, expected in (
        (first, ["scope", "show", "init-00001", "--json"], True),
        (second, ["scope", "show", "init-00001", "--json"], False),
        (first, ["--project", str(second), "scope", "show", "init-00001", "--json"], False),
    ):
        executable = first_shim if os.name == "posix" else installed_console
        output = _console(executable, arguments, cwd=cwd, environment=environment)
        assert output.returncode == 0, output.stdout + output.stderr
        payload = json.loads(output.stdout)
        assert payload["data"]["result"]["scope"]["directory_found"] is expected
        assert payload["effects"] == [] and not output.stderr
    for root in (first, second):
        output = _console(installed_console, ["workspace", "sync", "--json"], cwd=root)
        assert output.returncode == 0, output.stdout + output.stderr
        assert [row["path"] for row in json.loads(output.stdout)["data"]["worktrees"]] == [str(root)]
        assert not (root / ".git/spec-dock").exists() and not (root / "spec-dock/.agent").exists()
    subdirectory = second / "spec-dock"
    refused = _console(installed_console, ["--project", str(subdirectory), "scope", "list", "--json"], cwd=first)
    assert refused.returncode == 3, refused.stdout + refused.stderr
    assert json.loads(refused.stdout)["effects"] == [] and not refused.stderr
