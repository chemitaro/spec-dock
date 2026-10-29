"""Catalog file operations for canonical Scope writes."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.infra.canonical_scaffold import (
    BucketOccupied,
    copy_scope_template_at,
    prepare_bucket,
    remove_empty_bucket,
)

if TYPE_CHECKING:
    from pathlib import Path


def test_a_template_copy_renders_strips_title_and_parent_lines_and_rebases_doc_links(tmp_path: Path) -> None:
    root = tmp_path.resolve()
    template = root / "template"
    template.mkdir()
    (template / "plan.md").write_text(
        '---\nID: "<ISS_ID>"\nタイトル: "<ISS_TITLE>"\n---\n# <ISS_TITLE>\n詳細: [G](../../../../../../docs/a.md)\n',
        "utf-8",
    )
    destination = root / "iss-00007"
    destination.mkdir()
    descriptor = os.open(destination, os.O_RDONLY | os.O_DIRECTORY)
    try:
        created = copy_scope_template_at(
            template, destination, descriptor, {"<ISS_ID>": "iss-00007", "<ISS_TITLE>": "葉"}
        )
    finally:
        os.close(descriptor)
    assert created == [destination / "plan.md"]
    assert (destination / "plan.md").read_text(
        "utf-8"
    ) == '---\nID: "iss-00007"\n---\n# 葉\n詳細: [G](../../../docs/a.md)\n'


def test_a_missing_bucket_is_created_as_a_real_directory_and_an_existing_one_is_kept(tmp_path: Path) -> None:
    catalog = tmp_path.resolve()
    assert prepare_bucket(catalog, "00000-00999") is True
    assert (catalog / "00000-00999").is_dir() and not (catalog / "00000-00999").is_symlink()
    assert prepare_bucket(catalog, "00000-00999") is False


@pytest.mark.parametrize("kind", ["symlink", "file"])
def test_a_symlink_or_file_in_the_bucket_place_stops(tmp_path: Path, kind: str) -> None:
    catalog = tmp_path.resolve()
    elsewhere = catalog / "elsewhere"
    elsewhere.mkdir()
    if kind == "symlink":
        (catalog / "00000-00999").symlink_to(elsewhere)
    else:
        (catalog / "00000-00999").write_text("x", "utf-8")
    with pytest.raises(BucketOccupied) as raised:
        prepare_bucket(catalog, "00000-00999")
    assert raised.value.path == catalog / "00000-00999"
    assert list(elsewhere.iterdir()) == []


def test_only_an_emptied_bucket_is_removed(tmp_path: Path) -> None:
    catalog = tmp_path.resolve()
    (catalog / "00000-00999/iss-00001").mkdir(parents=True)
    assert remove_empty_bucket(catalog, "00000-00999") is False
    (catalog / "00000-00999/iss-00001").rmdir()
    assert remove_empty_bucket(catalog, "00000-00999") is True
    assert not (catalog / "00000-00999").exists()
    assert remove_empty_bucket(catalog, "00000-00999") is False
