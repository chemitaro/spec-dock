"""Find Scope directories in the catalog by name, wherever the nesting puts them (contract C3)."""

from __future__ import annotations

from pathlib import Path, PurePosixPath

import pytest

from spec_dock.runtime.infra.catalog_tree import CatalogTree, ScopeDirectoryAmbiguous


def _make(catalog: Path, *relatives: str) -> None:
    for relative in relatives:
        (catalog / relative).mkdir(parents=True, exist_ok=True)


def test_scopes_are_found_by_name_regardless_of_nesting(tmp_path: Path) -> None:
    _make(
        tmp_path,
        "init-00423-storage/epics/epic-00424-catalog/issues/iss-00429-link",
        "init-00001-other/epics/iss-00430-misplaced",
    )
    tree = CatalogTree(tmp_path)
    found = tree.require("iss-00429")
    assert found.relative == PurePosixPath("init-00423-storage/epics/epic-00424-catalog/issues/iss-00429-link")
    assert found.path == tmp_path / found.relative and found.scope_id == "iss-00429"
    assert tree.require("iss-00430").relative == PurePosixPath("init-00001-other/epics/iss-00430-misplaced")
    assert tree.find("epic-00424") is not None and tree.find("iss-00431") is None
    assert [item.scope_id for item in tree.directories()] == [
        "init-00001",
        "iss-00430",
        "init-00423",
        "epic-00424",
        "iss-00429",
    ]


def test_two_directories_with_one_id_are_ambiguous(tmp_path: Path) -> None:
    _make(tmp_path, "init-00001-one", "init-00002-two/epics/init-00001-copy")
    tree = CatalogTree(tmp_path)
    with pytest.raises(ScopeDirectoryAmbiguous) as raised:
        tree.find("init-00001")
    assert len(raised.value.matches) == 2
    assert set(tree.duplicates()) == {"init-00001"}


def test_hidden_directories_links_and_non_scope_names_are_skipped(tmp_path: Path) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    _make(outside, "init-00009-outside")
    _make(tmp_path / "catalog", ".runtime/staging/init-00005-staged", "init-00001-plan/.workbench/epic-00006-scratch")
    _make(tmp_path / "catalog", "init-00001-plan/artifacts", "notes", "init-local-00003-old", "init-00007-Bad_Slug")
    (tmp_path / "catalog/init-00008-link").symlink_to(outside / "init-00009-outside", target_is_directory=True)
    (tmp_path / "catalog/init-00010-file").write_text("x", encoding="utf-8")
    tree = CatalogTree(tmp_path / "catalog")
    assert [item.scope_id for item in tree.directories()] == ["init-00001"]
    with pytest.raises(LookupError):
        tree.require("init-00005")


def test_an_untracked_new_scope_is_visible_and_invalid_ids_are_refused(tmp_path: Path) -> None:
    tree = CatalogTree(tmp_path)
    with pytest.raises(ValueError):
        tree.find("init-local-00002")
    _make(tmp_path, "init-00002-new")
    assert CatalogTree(tmp_path).require("init-00002").relative == PurePosixPath("init-00002-new")
