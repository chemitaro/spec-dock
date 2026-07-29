from __future__ import annotations

import importlib
from pathlib import Path
import sys


def _template_scaffolder():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        return importlib.import_module("spec_dock_runtime.infra.template_scaffolder")
    finally:
        sys.path.pop(0)


def test_copy_scaffolded_tree_uses_exact_copy_for_unchanged_utf8_bytes(tmp_path: Path) -> None:
    scaffolder = _template_scaffolder()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    fixture = source / "ordinary" / "note.txt"
    fixture.parent.mkdir(parents=True)
    source_bytes = b"first\r\nsecond\r\n"
    fixture.write_bytes(source_bytes)

    created = scaffolder.copy_scaffolded_tree(source, destination, {"<ISS_ID>": "iss-00001"})

    copied = destination / "ordinary" / "note.txt"
    assert created == [copied]
    assert copied.read_bytes() == source_bytes
    assert copied.read_bytes().count(b"\r\n") == 2


def test_copy_scaffolded_tree_still_renders_changed_placeholder_text(tmp_path: Path) -> None:
    scaffolder = _template_scaffolder()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    fixture = source / "requirement.md"
    fixture.parent.mkdir(parents=True)
    fixture.write_text("id=<ISS_ID>\n", encoding="utf-8")

    created = scaffolder.copy_scaffolded_tree(source, destination, {"<ISS_ID>": "iss-00001"})

    copied = destination / "requirement.md"
    assert created == [copied]
    assert copied.read_bytes() == b"id=iss-00001\n"


def test_copy_scaffolded_tree_exact_copy_is_path_agnostic(tmp_path: Path) -> None:
    scaffolder = _template_scaffolder()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source_bytes = b"unchanged\r\ntext\r\n"
    relative_paths = (
        Path(".workbench/README.md"),
        Path("ordinary/note.txt"),
        Path("nested/extensionless"),
    )
    for relative_path in relative_paths:
        fixture = source / relative_path
        fixture.parent.mkdir(parents=True, exist_ok=True)
        fixture.write_bytes(source_bytes)

    created = scaffolder.copy_scaffolded_tree(source, destination, {"<ISS_ID>": "iss-00001"})

    assert {path.relative_to(destination) for path in created} == set(relative_paths)
    assert all((destination / relative_path).read_bytes() == source_bytes for relative_path in relative_paths)
