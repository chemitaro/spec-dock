"""Scope directories are `<catalog>/<ID>`, flat and found directly (contract C3, iss-00455)."""

from __future__ import annotations

from pathlib import Path, PurePosixPath

import pytest

from spec_dock.runtime.infra.catalog_tree import CatalogTree, MisplacedDirectory


def _make(catalog: Path, *relatives: str) -> None:
    for relative in relatives:
        (catalog / relative).mkdir(parents=True, exist_ok=True)


def test_scope_directories_are_the_direct_children_named_by_their_id(tmp_path: Path) -> None:
    _make(tmp_path, "init-00423", "epic-00424/artifacts", "iss-00454", "iss-100000", "epic-00424/discussions/iss-00001")
    tree = CatalogTree(tmp_path)
    found = tree.require("iss-00454")
    assert (found.scope_id, found.relative, found.path) == (
        "iss-00454",
        PurePosixPath("iss-00454"),
        tmp_path / "iss-00454",
    )
    assert tree.find(" ISS-00454 ") == found
    assert tree.find("iss-00001") is None and tree.find("iss-00455") is None
    assert [item.scope_id for item in tree.directories()] == ["epic-00424", "init-00423", "iss-00454", "iss-100000"]
    with pytest.raises(LookupError):
        tree.require("iss-00455")


@pytest.mark.parametrize("invalid", ["init-local-00002", "iss-454", "iss-000454", "iss-00454-foo", "iss-00000"])
def test_names_that_are_not_ids_are_refused(tmp_path: Path, invalid: str) -> None:
    with pytest.raises(ValueError):
        CatalogTree(tmp_path).find(invalid)


def test_names_shaped_like_ids_and_leftover_nesting_are_misplaced(tmp_path: Path) -> None:
    _make(
        tmp_path,
        "iss-00454-foo",
        "iss-000454",
        "iss-454",
        "iss-00000",
        "init-00423-storage/epics/epic-00424-catalog",
        "epic-00424/issues/iss-00455-old",
        "epic-00424/epics",
        "epic-00424/artifacts/iss-00001",
        "epic-00424/discussions/iss-00002-topic",
        "iss-00456",
        "notes",
        "issue-00457",
        "adr-00001",
    )
    assert CatalogTree(tmp_path).misplaced() == (
        MisplacedDirectory(PurePosixPath("epic-00424/epics"), "nested"),
        MisplacedDirectory(PurePosixPath("epic-00424/issues"), "nested"),
        MisplacedDirectory(PurePosixPath("init-00423-storage"), "name"),
        MisplacedDirectory(PurePosixPath("iss-00000"), "name"),
        MisplacedDirectory(PurePosixPath("iss-000454"), "name"),
        MisplacedDirectory(PurePosixPath("iss-00454-foo"), "name"),
        MisplacedDirectory(PurePosixPath("iss-454"), "name"),
    )
    assert [item.scope_id for item in CatalogTree(tmp_path).directories()] == ["epic-00424", "iss-00456"]


def test_hidden_directories_links_and_files_are_never_scopes(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    _make(outside, "init-00009")
    catalog = tmp_path / "catalog"
    _make(catalog, ".runtime/staging/init-00005", ".iss-00006", "init-00001/.workbench/epic-00006")
    (catalog / "init-00008").symlink_to(outside / "init-00009", target_is_directory=True)
    (catalog / "init-00010").write_text("x", encoding="utf-8")
    (catalog / "iss-00011-file").write_text("x", encoding="utf-8")
    tree = CatalogTree(catalog)
    assert [item.scope_id for item in tree.directories()] == ["init-00001"]
    assert tree.find("init-00008") is None and tree.find("init-00010") is None and tree.find("init-00005") is None
    assert tree.misplaced() == ()


def test_an_untracked_new_scope_is_visible_at_once(tmp_path: Path) -> None:
    tree = CatalogTree(tmp_path)
    assert tree.find("init-00002") is None
    _make(tmp_path, "init-00002")
    assert tree.require("init-00002").relative == PurePosixPath("init-00002")


def test_an_upper_case_id_name_is_misplaced_even_where_case_is_ignored(tmp_path: Path) -> None:
    _make(tmp_path, "ISS-00454")
    tree = CatalogTree(tmp_path)
    assert tree.find("iss-00454") is None and tree.directories() == ()
    assert tree.misplaced() == (MisplacedDirectory(PurePosixPath("ISS-00454"), "name"),)
