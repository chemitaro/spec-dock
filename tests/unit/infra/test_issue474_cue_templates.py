"""iss-00474 AC-07/AC-10: the CUE Scope templates ship under templates/cue/<kind>/ beside the unchanged .md ones."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "src/spec_dock/assets"
PROVIDER = ASSETS / "spec_dock"
DOGFOOD = ROOT / "spec-dock"
KINDS = ("initiative", "epic", "issue")
CUE_FILES = (
    ".workbench/README.md",
    "design.cue",
    "explanation.html",
    "plan.cue",
    "report.md",
    "requirement.cue",
)
MARKDOWN_FILES = (".workbench/README.md", "design.md", "plan.md", "report.md", "requirement.md")


def _files(directory: Path) -> list[str]:
    return sorted(path.relative_to(directory).as_posix() for path in directory.rglob("*") if path.is_file())


@pytest.mark.parametrize("kind", KINDS)
def test_each_kind_ships_the_cue_set_and_keeps_the_markdown_set(kind: str) -> None:
    assert _files(PROVIDER / "templates/cue" / kind) == sorted(CUE_FILES)
    # The previous CLI copies everything under templates/<kind>/; it must still find only the .md set there.
    assert _files(PROVIDER / "templates" / kind) == sorted(MARKDOWN_FILES)


@pytest.mark.parametrize("kind", KINDS)
def test_the_explanation_and_workbench_are_byte_copies(kind: str) -> None:
    directory = PROVIDER / "templates/cue" / kind
    skeleton = PROVIDER / "design-system/explanation-skeleton.html"
    assert (directory / "explanation.html").read_bytes() == skeleton.read_bytes()
    workbench = PROVIDER / "templates" / kind / ".workbench/README.md"
    assert (directory / ".workbench/README.md").read_bytes() == workbench.read_bytes()


@pytest.mark.parametrize("kind", KINDS)
def test_the_report_depends_on_the_cue_documents(kind: str) -> None:
    report = (PROVIDER / "templates/cue" / kind / "report.md").read_text(encoding="utf-8")
    assert '依存: ["requirement.cue", "design.cue", "plan.cue"]' in report
    assert "requirement.md" not in report
    assert "](../../../docs/authoring/report.md)" in report
    assert (PROVIDER / "templates/cue" / kind / "../../../docs/authoring/report.md").resolve().is_file()


@pytest.mark.parametrize("kind", KINDS)
def test_only_the_requirement_carries_the_assurance_markers(kind: str) -> None:
    directory = PROVIDER / "templates/cue" / kind
    requirement = (directory / "requirement.cue").read_text(encoding="utf-8")
    assert requirement.count('"{{ASSURANCE_LEVEL}}"') == 1 and requirement.count('"{{ASSURANCE_REASON}}"') == 1
    for name in CUE_FILES:
        if name != "requirement.cue":
            assert "{{ASSURANCE_" not in (directory / name).read_text(encoding="utf-8"), name


def test_the_inventory_lists_every_cue_template_with_its_digest_and_the_dogfood_copy_matches() -> None:
    inventory = json.loads((ASSETS / "static-inventory.json").read_text(encoding="utf-8"))
    entries = {entry["path"]: entry for entry in inventory["files"]}
    for kind in KINDS:
        for name in CUE_FILES:
            path = f"spec-dock/templates/cue/{kind}/{name}"
            entry = entries[path]
            source = ASSETS / entry["source"]
            assert entry["source"] == f"spec_dock/templates/cue/{kind}/{name}"
            assert entry["sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
            assert (entry["mode"], entry["init_only"]) == (420, False)
            assert (DOGFOOD / f"templates/cue/{kind}/{name}").read_bytes() == source.read_bytes()


def test_the_cue_examples_no_longer_live_among_the_test_fixtures() -> None:
    assert not (ROOT / "tests/fixtures/cue/v1/templates").exists()


def test_a_fresh_wheel_carries_every_cue_template_including_the_hidden_workbench(tmp_path: Path) -> None:
    wheel_dir = tmp_path / "wheel"
    subprocess.run(["uv", "build", "--wheel", "--out-dir", str(wheel_dir)], cwd=ROOT, check=True, capture_output=True)
    (wheel,) = wheel_dir.glob("*.whl")
    with zipfile.ZipFile(wheel) as archive:
        for kind in KINDS:
            for name in CUE_FILES:
                packaged = f"spec_dock/assets/spec_dock/templates/cue/{kind}/{name}"
                assert archive.read(packaged) == (PROVIDER / "templates/cue" / kind / name).read_bytes(), packaged
