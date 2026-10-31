"""iss-00475 R-01〜R-04: the shipped explanation design system and its thin skeleton."""

from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

import pytest

from spec_dock.runtime.infra.static_assets import package_static_assets

REPO_ROOT = Path(__file__).resolve().parents[3]
PROVIDER_ROOT = REPO_ROOT / "src/spec_dock/assets/spec_dock/design-system"
DOGFOOD_ROOT = REPO_ROOT / "spec-dock/design-system"
VENDOR_MANIFEST = REPO_ROOT / "src/spec_dock/assets/vendor/manifest.json"

DESIGN_SYSTEM_FILES = (
    "ds.css",
    "ds.js",
    "explanation-skeleton.html",
    "vendor/marked.LICENSE.md",
    "vendor/marked.umd.js",
)
# SHA-256 of japanese-explanatory-html design system 1.0.0 when it was copied (2026-10-31).
# SpecDock's copy is authoritative; the user's skill is never read by tests (hermetic).
UPSTREAM_COPY_SHA256 = {
    "ds.css": "b6fb9e3ea931e3593ad93d61b0ace454287e93a4502680cb0755811302ff2d24",
    "vendor/marked.umd.js": "21568877a938d2c4e7d74e27f18e60da96bb73a68809610ca39216e1efebae62",
    "vendor/marked.LICENSE.md": "8e3a3f82f59a60958f56ca08f445647c32a4733dc7ca6c2c46f6eb898471ab9c",
}
SKELETON_MARKER = "<!-- spec-dock:explanation-skeleton -->"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_design_system_files_are_static_assets_in_the_package() -> None:
    shipped = {a.path: a for a in package_static_assets() if a.path.startswith("spec-dock/design-system/")}
    assert sorted(shipped) == [f"spec-dock/design-system/{name}" for name in DESIGN_SYSTEM_FILES]
    for name in DESIGN_SYSTEM_FILES:
        asset = shipped[f"spec-dock/design-system/{name}"]
        assert asset.payload == (PROVIDER_ROOT / name).read_bytes()
        assert asset.mode == 0o644 and not asset.init_only


@pytest.mark.parametrize("name", DESIGN_SYSTEM_FILES)
def test_dogfood_copy_matches_the_provider_byte_exact(name: str) -> None:
    assert (DOGFOOD_ROOT / name).read_bytes() == (PROVIDER_ROOT / name).read_bytes()


@pytest.mark.parametrize("name", sorted(UPSTREAM_COPY_SHA256))
def test_unmodified_files_match_the_upstream_copy(name: str) -> None:
    assert _sha256(PROVIDER_ROOT / name) == UPSTREAM_COPY_SHA256[name]


def _js_constant(source: str, name: str) -> str:
    match = re.search(rf'const {name} = "([^"]+)";', source)
    assert match, name
    return match.group(1)


def test_ds_js_part_versions_match_the_bundled_manifest() -> None:
    source = (PROVIDER_ROOT / "ds.js").read_text(encoding="utf-8")
    versions = {p["name"]: p["version"] for p in json.loads(VENDOR_MANIFEST.read_text(encoding="utf-8"))["packages"]}
    assert _js_constant(source, "PLANTUML_VERSION") == versions["@plantuml/core"]
    assert _js_constant(source, "HLJS_VERSION") == versions["@highlightjs/cdn-assets"]


def test_ds_js_reads_the_vendor_meta_and_its_own_marked() -> None:
    source = (PROVIDER_ROOT / "ds.js").read_text(encoding="utf-8")
    assert 'meta[name="ds-vendor-base"]' in source
    assert '"vendor/marked.umd.js"' in source
    assert "document.currentScript" in source
    assert "plantuml/${PLANTUML_VERSION}/" in source and "highlightjs/${HLJS_VERSION}/" in source
    assert "https://unpkg.com/@plantuml/core@${PLANTUML_VERSION}/" in source
    assert "https://unpkg.com/@highlightjs/cdn-assets@${HLJS_VERSION}/" in source
    assert _js_constant(source, "VERSION").startswith("1.0.0+specdock.")


class _Shape(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, dict[str, str | None]]] = []
        self.sources: list[str] = []
        self._in_source = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        self.tags.append((tag, attributes))
        if tag == "script" and attributes.get("id") == "ds-source":
            self._in_source = True
            self.sources.append("")

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._in_source = False

    def handle_data(self, data: str) -> None:
        if self._in_source:
            self.sources[-1] += data


@pytest.fixture(scope="module")
def skeleton() -> tuple[str, _Shape]:
    text = (PROVIDER_ROOT / "explanation-skeleton.html").read_text(encoding="utf-8")
    shape = _Shape()
    shape.feed(text)
    return text, shape


def test_skeleton_has_exactly_one_markdown_source_with_a_title(skeleton: tuple[str, _Shape]) -> None:
    _text, shape = skeleton
    sources = [a for t, a in shape.tags if t == "script" and a.get("id") == "ds-source"]
    assert len(sources) == 1 and sources[0].get("type") == "text/markdown"
    body = shape.sources[0].lstrip("\n")
    front = re.match(r"---\n(.*?)\n---\n", body, re.S)
    assert front and re.search(r"^title: \S", front.group(1), re.M)


def test_skeleton_loads_only_the_shared_design_system(skeleton: tuple[str, _Shape]) -> None:
    text, shape = skeleton
    styles = [a for t, a in shape.tags if t == "link" and a.get("rel") == "stylesheet"]
    scripts = [a for t, a in shape.tags if t == "script" and a.get("id") != "ds-source"]
    assert [a.get("href") for a in styles] == ["../../../design-system/ds.css"]
    assert [a.get("src") for a in scripts] == ["../../../design-system/ds.js"]
    assert not [t for t, _a in shape.tags if t == "style"]
    assert "http://" not in text and "https://" not in text


def test_skeleton_carries_the_marker_a_diagram_and_a_code_block_without_placeholders(
    skeleton: tuple[str, _Shape],
) -> None:
    _text, shape = skeleton
    body = shape.sources[0]
    assert body.count(SKELETON_MARKER) == 1
    assert len(re.findall(r"^```plantuml\b", body, re.M)) == 1
    assert re.search(r"^```(?!plantuml)[a-z]+\s*$", body, re.M)
    assert not re.search(r"<[A-Z_]+>|\{\{", body)
