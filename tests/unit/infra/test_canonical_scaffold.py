"""Catalog file operations for canonical Scope writes."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.infra.canonical_scaffold import copy_scope_template_at, move_directory

if TYPE_CHECKING:
    from pathlib import Path


def test_a_directory_moves_into_new_parents_and_never_replaces(tmp_path: Path) -> None:
    root = tmp_path.resolve()
    source = root / "init-00001-plan/epics/epic-00002-core"
    (source / "artifacts").mkdir(parents=True)
    (source / "plan.md").write_text("plan", encoding="utf-8")
    target = root / "init-00003-other/epics/epic-00002-core"
    move_directory(source, target)
    assert not source.exists() and (target / "plan.md").read_text(encoding="utf-8") == "plan"
    (source / "x").mkdir(parents=True)
    (source / "x" / "keep").write_text("keep", encoding="utf-8")
    with pytest.raises(FileExistsError):
        move_directory(source.parent, target.parent)
    assert (source / "x" / "keep").exists()


def test_a_template_copy_renders_and_strips_title_and_parent_lines(tmp_path: Path) -> None:
    root = tmp_path.resolve()
    template = root / "template"
    template.mkdir()
    (template / "plan.md").write_text('---\nID: "<ISS_ID>"\nタイトル: "<ISS_TITLE>"\n---\n# <ISS_TITLE>\n', "utf-8")
    destination = root / "iss-00007-leaf"
    destination.mkdir()
    descriptor = os.open(destination, os.O_RDONLY | os.O_DIRECTORY)
    try:
        created = copy_scope_template_at(template, destination, descriptor, {"<ISS_ID>": "iss-00007", "<ISS_TITLE>": "Leaf"})
    finally:
        os.close(descriptor)
    assert created == [destination / "plan.md"]
    assert (destination / "plan.md").read_text("utf-8") == '---\nID: "iss-00007"\n---\n# Leaf\n'
