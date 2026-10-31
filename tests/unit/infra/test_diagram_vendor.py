"""iss-00475 R-05/R-06: the bundled diagram parts and their serving entry point."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import pytest

from spec_dock.runtime.infra import diagram_vendor
from spec_dock.runtime.infra.diagram_vendor import (
    DIAGRAM_VENDOR_META_NAME,
    DiagramVendorError,
    DiagramVendorFile,
    diagram_vendor_files,
    read_diagram_vendor_file,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
VENDOR_ROOT = REPO_ROOT / "src/spec_dock/assets/vendor"

# Pinned in the Epic design (K5) and iss-00475 R-05; independent of the manifest under test.
EXPECTED_PATHS = (
    "highlightjs/11.11.1/LICENSE",
    "highlightjs/11.11.1/highlight.min.js",
    "plantuml/1.2026.6/LICENSE",
    "plantuml/1.2026.6/emoji.js",
    "plantuml/1.2026.6/openiconic.js",
    "plantuml/1.2026.6/plantuml.js",
    "plantuml/1.2026.6/viz-global.js",
)


@pytest.fixture
def vendor_copy(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "vendor"
    shutil.copytree(VENDOR_ROOT, root)
    monkeypatch.setattr(diagram_vendor, "_vendor_root", lambda: root)
    return root


def test_meta_name_is_the_k5_contract() -> None:
    assert DIAGRAM_VENDOR_META_NAME == "ds-vendor-base"


def test_files_list_exactly_the_pinned_parts_with_licenses() -> None:
    files = diagram_vendor_files()
    assert tuple(f.path for f in files) == EXPECTED_PATHS
    assert all(isinstance(f, DiagramVendorFile) for f in files)
    by_path = {f.path: f for f in files}
    assert by_path["plantuml/1.2026.6/plantuml.js"].content_type == "text/javascript; charset=utf-8"
    assert by_path["plantuml/1.2026.6/LICENSE"].content_type == "text/plain; charset=utf-8"


def test_each_listed_file_reads_back_with_its_manifest_digest() -> None:
    for item in diagram_vendor_files():
        payload = read_diagram_vendor_file(item.path)
        assert payload is not None
        assert hashlib.sha256(payload).hexdigest() == item.sha256


def test_licenses_name_the_upstream_projects() -> None:
    assert b"PlantUML" in (read_diagram_vendor_file("plantuml/1.2026.6/LICENSE") or b"")
    assert b"BSD 3-Clause" in (read_diagram_vendor_file("highlightjs/11.11.1/LICENSE") or b"")


def test_manifest_records_the_npm_sources() -> None:
    manifest = json.loads((VENDOR_ROOT / "manifest.json").read_text(encoding="utf-8"))
    packages = {p["name"]: p for p in manifest["packages"]}
    assert packages["@plantuml/core"]["version"] == "1.2026.6"
    assert packages["@highlightjs/cdn-assets"]["version"] == "11.11.1"
    assert all(p["npm_integrity"].startswith("sha512-") for p in packages.values())


@pytest.mark.parametrize(
    "path",
    [
        "",
        "manifest.json",
        "plantuml/1.2026.6/README.md",
        "plantuml/1.2026.6/../1.2026.6/plantuml.js",
        "../vendor/plantuml/1.2026.6/plantuml.js",
        "/plantuml/1.2026.6/plantuml.js",
        "plantuml\\1.2026.6\\plantuml.js",
        "plantuml/1.2026.6/plantuml.js/",
    ],
)
def test_paths_outside_the_manifest_return_nothing(path: str) -> None:
    assert read_diagram_vendor_file(path) is None


def test_tampered_part_is_an_error(vendor_copy: Path) -> None:
    (vendor_copy / "plantuml/1.2026.6/plantuml.js").write_bytes(b"replaced")
    with pytest.raises(DiagramVendorError):
        read_diagram_vendor_file("plantuml/1.2026.6/plantuml.js")
    assert read_diagram_vendor_file("highlightjs/11.11.1/highlight.min.js") is not None


def test_missing_listed_part_is_an_error(vendor_copy: Path) -> None:
    (vendor_copy / "plantuml/1.2026.6/emoji.js").unlink()
    with pytest.raises(DiagramVendorError):
        read_diagram_vendor_file("plantuml/1.2026.6/emoji.js")


@pytest.mark.parametrize(
    "mutate",
    [
        lambda m: m.update(schema_version="other"),
        lambda m: m["files"].append(dict(m["files"][0])),
        lambda m: m["files"].reverse(),
        lambda m: m["files"][0].update(path="../escape"),
        lambda m: m["files"][0].update(sha256="xyz"),
    ],
    ids=["schema", "duplicate", "order", "unsafe-path", "bad-digest"],
)
def test_broken_manifest_is_an_error(vendor_copy: Path, mutate: object) -> None:
    manifest_path = vendor_copy / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mutate(manifest)  # type: ignore[operator]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(DiagramVendorError):
        diagram_vendor_files()
