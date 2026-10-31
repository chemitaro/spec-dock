"""The CUE spec type ships inside the wheel, also when the wheel is built from the sdist (iss-00472 AC-08).

The builds start from a copy of the build inputs: an in-tree build reads a leftover `*.egg-info/SOURCES.txt`,
which can list files that the package-data configuration no longer includes.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
TYPE_SOURCE = ROOT / "src/spec_dock/cue"


def _clean_source(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    source.mkdir()
    for name in ("pyproject.toml", "setup.py", "README.md", "LICENSE"):
        shutil.copy2(ROOT / name, source / name)
    shutil.copytree(
        ROOT / "src",
        source / "src",
        ignore=shutil.ignore_patterns("*.egg-info", "__pycache__", "*.pyc", "*.pyo"),
        symlinks=True,
    )
    return source


def _type_files(archive: zipfile.ZipFile) -> dict[str, bytes]:
    return {name: archive.read(name) for name in archive.namelist() if name.startswith("spec_dock/cue/")}


def test_fresh_and_sdist_built_wheels_carry_every_type_file_unchanged(tmp_path: Path) -> None:
    expected = {
        "spec_dock/" + path.relative_to(ROOT / "src/spec_dock").as_posix(): path.read_bytes()
        for path in sorted(TYPE_SOURCE.rglob("*.cue"))
    }
    assert "spec_dock/cue/v1/base.cue" in expected

    source = _clean_source(tmp_path)
    wheels = tmp_path / "wheels"
    subprocess.run(["uv", "build", "--wheel", "--out-dir", str(wheels)], cwd=source, check=True, capture_output=True)
    with zipfile.ZipFile(next(wheels.glob("*.whl"))) as archive:
        assert _type_files(archive) == expected

    sdists = tmp_path / "sdist"
    subprocess.run(["uv", "build", "--sdist", "--out-dir", str(sdists)], cwd=source, check=True, capture_output=True)
    unpacked = tmp_path / "unpacked"
    with tarfile.open(next(sdists.glob("*.tar.gz"))) as archive:
        archive.extractall(unpacked, filter="data") if sys.version_info >= (3, 12) else archive.extractall(unpacked)
    derived = tmp_path / "derived"
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(derived)],
        cwd=next(unpacked.iterdir()),
        check=True,
        capture_output=True,
    )
    with zipfile.ZipFile(next(derived.glob("*.whl"))) as archive:
        assert _type_files(archive) == expected


def test_the_installed_wheel_finds_its_type_directory(tmp_path: Path) -> None:
    wheels = tmp_path / "wheels"
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(wheels)],
        cwd=_clean_source(tmp_path),
        check=True,
        capture_output=True,
    )
    environment = {key: value for key, value in os.environ.items() if key not in {"PYTHONPATH", "PYTHONHOME"}}
    venv = tmp_path / "installed"
    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True, capture_output=True, env=environment)
    python = venv / "bin/python"
    subprocess.run(
        [str(python), "-m", "pip", "install", "--no-deps", "--no-index", str(next(wheels.glob("*.whl")))],
        check=True,
        capture_output=True,
        env=environment,
    )
    probe = (
        "from spec_dock.runtime.infra.cue_schemas import schema_directory, shipped_schemas; "
        "print(shipped_schemas()); print(schema_directory('specdock/v1'))"
    )
    output = subprocess.check_output([str(python), "-I", "-c", probe], text=True, env=environment).splitlines()
    assert output[0] == "('specdock/v1',)"
    directory = Path(output[1])
    assert directory.is_relative_to(venv) and (directory / "base.cue").is_file()
