"""Contract C7: the shipped version file and the check workflow sample (AC-434-06)."""

from __future__ import annotations

from pathlib import Path
import re
import sys

from spec_dock.runtime.application.canonical_check import (
    CI_VERSION_FILE,
    WORKFLOW_BRANCH_LINE,
    WORKFLOW_DESTINATION,
    WORKFLOW_SAMPLE,
)
from spec_dock.runtime.infra.static_assets import package_static_assets

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - Python 3.10 uses the declared tomli dependency
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "src/spec_dock/assets/spec_dock"


def test_the_version_file_names_the_pyproject_version_on_one_line() -> None:
    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    payload = (ASSETS / "system/spec-dock-version").read_bytes()
    assert payload == f"{version}\n".encode("ascii")
    assert not payload.startswith(b"v")


def test_the_version_file_and_workflow_sample_are_ordinary_static_assets() -> None:
    assets = {asset.path: asset for asset in package_static_assets()}
    assert CI_VERSION_FILE == "spec-dock/system/spec-dock-version"
    assert WORKFLOW_SAMPLE == "spec-dock/docs/ci/spec-dock-check.yml"
    for path in (CI_VERSION_FILE, WORKFLOW_SAMPLE):
        asset = assets[path]
        assert asset.mode == 0o644 and not asset.init_only
        assert asset.payload == (ASSETS / path.removeprefix("spec-dock/")).read_bytes()


def test_the_workflow_sample_installs_the_pinned_version_and_runs_the_check() -> None:
    sample = (ASSETS / "docs/ci/spec-dock-check.yml").read_text(encoding="utf-8")
    assert WORKFLOW_DESTINATION == ".github/workflows/spec-dock-check.yml"
    assert WORKFLOW_BRANCH_LINE == "branches: [main]"
    assert sample.startswith("name: SpecDock check\non:\n  pull_request:\n  push:\n")
    branch_lines = [line for line in sample.splitlines() if WORKFLOW_BRANCH_LINE in line]
    assert len(branch_lines) == 1 and re.fullmatch(r"    branches: \[main\]\s+#.*", branch_lines[0])
    assert "permissions:\n  contents: read\n" in sample
    assert "runs-on: ubuntu-latest" in sample and "uses: actions/checkout@v4" in sample
    install = (
        'run: pipx install "spec-dock @ git+https://github.com/chemitaro/spec-dock@v'
        '$(cat spec-dock/system/spec-dock-version)"'
    )
    assert sample.count(install) == 1
    assert sample.rstrip().endswith("run: spec-dock canonical check --json")
    for forbidden in ("secrets.", "GITHUB_TOKEN", "contents: write", "workspace validate"):
        assert forbidden not in sample
