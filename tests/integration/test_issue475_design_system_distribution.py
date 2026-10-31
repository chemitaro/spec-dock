"""iss-00475 AC-01/AC-04: installation places the design system; the wheel carries the diagram parts."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import TYPE_CHECKING
import zipfile

from spec_dock.cli import main
from spec_dock.runtime.infra.git_process import run_git

if TYPE_CHECKING:
    import pytest

ROOT = Path(__file__).resolve().parents[2]
PROVIDER_ROOT = ROOT / "src/spec_dock/assets/spec_dock/design-system"
DESIGN_SYSTEM_FILES = (
    "ds.css",
    "ds.js",
    "explanation-skeleton.html",
    "vendor/marked.LICENSE.md",
    "vendor/marked.umd.js",
)


def test_installation_init_places_the_design_system(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    run_git(target, "init", "-q", "--initial-branch=main", mutation=True)
    assert main(["installation", "init", str(target), "--yes", "--json"]) == 0
    created = json.loads(capsys.readouterr().out)["data"]["result"]["created_paths"]
    for name in DESIGN_SYSTEM_FILES:
        assert f"spec-dock/design-system/{name}" in created
        assert (target / "spec-dock/design-system" / name).read_bytes() == (PROVIDER_ROOT / name).read_bytes()
    assert not (target / "spec-dock/design-system/plantuml").exists()
    assert not any(path.name == "plantuml.js" for path in target.rglob("*"))


def test_fresh_wheel_contains_the_diagram_parts_and_manifest(tmp_path: Path) -> None:
    wheel_dir = tmp_path / "wheel"
    subprocess.run(["uv", "build", "--wheel", "--out-dir", str(wheel_dir)], cwd=ROOT, check=True, capture_output=True)
    (wheel,) = wheel_dir.glob("*.whl")
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        manifest = json.loads(archive.read("spec_dock/assets/vendor/manifest.json"))
        for entry in manifest["files"]:
            assert f"spec_dock/assets/vendor/{entry['path']}" in names
        assert (
            archive.read("spec_dock/assets/vendor/plantuml/1.2026.6/plantuml.js")
            == (ROOT / "src/spec_dock/assets/vendor/plantuml/1.2026.6/plantuml.js").read_bytes()
        )
