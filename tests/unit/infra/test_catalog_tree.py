"""Scope directories are `<catalog>/<bucket>/<ID>`, flat and found directly (contract C3, iss-00455, iss-00460)."""

from __future__ import annotations

from pathlib import Path, PurePosixPath

import pytest

from spec_dock.runtime.infra.catalog_tree import CatalogTree, MisplacedDirectory

LOW = "00000-00999"


def _make(catalog: Path, *relatives: str) -> None:
    for relative in relatives:
        (catalog / relative).mkdir(parents=True, exist_ok=True)


def test_scope_directories_are_named_by_their_id_under_their_numbers_bucket(tmp_path: Path) -> None:
    _make(
        tmp_path,
        f"{LOW}/init-00423",
        f"{LOW}/epic-00424/artifacts",
        f"{LOW}/iss-00454",
        "02000-02999/iss-02114",
        "100000-100999/iss-100000",
        f"{LOW}/epic-00424/discussions/iss-00001",
    )
    tree = CatalogTree(tmp_path)
    found = tree.require("iss-00454")
    assert (found.scope_id, found.relative, found.path) == (
        "iss-00454",
        PurePosixPath(f"{LOW}/iss-00454"),
        tmp_path / LOW / "iss-00454",
    )
    assert tree.find(" ISS-00454 ") == found
    assert tree.find("iss-00001") is None and tree.find("iss-00455") is None
    assert [item.relative.as_posix() for item in tree.directories()] == [
        f"{LOW}/epic-00424",
        f"{LOW}/init-00423",
        f"{LOW}/iss-00454",
        "02000-02999/iss-02114",
        "100000-100999/iss-100000",
    ]
    assert tree.require("iss-100000").path == tmp_path / "100000-100999" / "iss-100000"
    with pytest.raises(LookupError):
        tree.require("iss-00455")


@pytest.mark.parametrize("invalid", ["init-local-00002", "iss-454", "iss-000454", "iss-00454-foo", "iss-00000"])
def test_names_that_are_not_ids_are_refused(tmp_path: Path, invalid: str) -> None:
    with pytest.raises(ValueError):
        CatalogTree(tmp_path).find(invalid)


def test_a_flat_or_wrongly_bucketed_id_is_no_scope_directory(tmp_path: Path) -> None:
    _make(tmp_path, "iss-00454", f"{LOW}/iss-01454", "01000-01999/iss-00455")
    tree = CatalogTree(tmp_path)
    assert tree.directories() == ()
    assert tree.find("iss-00454") is None and tree.find("iss-01454") is None and tree.find("iss-00455") is None


def test_everything_outside_its_bucket_is_misplaced_with_the_reason_and_place(tmp_path: Path) -> None:
    _make(
        tmp_path,
        "iss-00454",
        "iss-00454-foo",
        "ISS-00456",
        "init-00423-storage/epics/epic-00424-catalog",
        "0-999/iss-00457",
        "00000-00998",
        f"{LOW}/iss-01454",
        f"{LOW}/iss-00458-foo",
        f"{LOW}/iss-000459",
        f"{LOW}/iss-459",
        f"{LOW}/ISS-00460",
        f"{LOW}/epic-00424/issues/iss-00455-old",
        f"{LOW}/epic-00424/epics",
        f"{LOW}/epic-00424/artifacts/iss-00001",
        f"{LOW}/epic-00424/discussions/iss-00002-topic",
        f"{LOW}/iss-00461",
        f"{LOW}/notes",
        "notes",
        "issue-00462",
        "adr-00001",
    )
    assert CatalogTree(tmp_path).misplaced() == (
        MisplacedDirectory(PurePosixPath("0-999"), "bucket"),
        MisplacedDirectory(PurePosixPath("00000-00998"), "bucket"),
        MisplacedDirectory(PurePosixPath(f"{LOW}/ISS-00460"), "name"),
        MisplacedDirectory(PurePosixPath(f"{LOW}/epic-00424/epics"), "nested"),
        MisplacedDirectory(PurePosixPath(f"{LOW}/epic-00424/issues"), "nested"),
        MisplacedDirectory(PurePosixPath(f"{LOW}/iss-000459"), "name"),
        MisplacedDirectory(PurePosixPath(f"{LOW}/iss-00458-foo"), "name"),
        MisplacedDirectory(PurePosixPath(f"{LOW}/iss-01454"), "bucket", PurePosixPath("01000-01999/iss-01454")),
        MisplacedDirectory(PurePosixPath(f"{LOW}/iss-459"), "name"),
        MisplacedDirectory(PurePosixPath("ISS-00456"), "root"),
        MisplacedDirectory(PurePosixPath("init-00423-storage"), "root"),
        MisplacedDirectory(PurePosixPath("iss-00454"), "root", PurePosixPath(f"{LOW}/iss-00454")),
        MisplacedDirectory(PurePosixPath("iss-00454-foo"), "root"),
    )
    assert [item.scope_id for item in CatalogTree(tmp_path).directories()] == ["epic-00424", "iss-00461"]


def test_hidden_directories_links_and_files_are_never_buckets_or_scopes(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    _make(outside, "init-00009", "bucket/init-00012")
    catalog = tmp_path / "catalog"
    _make(
        catalog,
        f".runtime/staging/{LOW}/init-00005",
        f"{LOW}/.iss-00006",
        f"{LOW}/init-00001/.workbench/epic-00006",
        ".01000-01999/iss-01001",
    )
    (catalog / LOW / "init-00008").symlink_to(outside / "init-00009", target_is_directory=True)
    (catalog / LOW / "init-00010").write_text("x", encoding="utf-8")
    (catalog / LOW / "iss-00011-file").write_text("x", encoding="utf-8")
    (catalog / "02000-02999").symlink_to(outside / "bucket", target_is_directory=True)
    (catalog / "03000-03999").write_text("x", encoding="utf-8")
    (catalog / "iss-00013").write_text("x", encoding="utf-8")
    tree = CatalogTree(catalog)
    assert [item.scope_id for item in tree.directories()] == ["init-00001"]
    assert tree.find("init-00008") is None and tree.find("init-00010") is None and tree.find("init-00005") is None
    assert tree.find("iss-01001") is None and tree.find("init-02012") is None
    assert tree.misplaced() == ()


def test_an_untracked_new_scope_is_visible_at_once(tmp_path: Path) -> None:
    tree = CatalogTree(tmp_path)
    assert tree.find("init-00002") is None
    _make(tmp_path, f"{LOW}/init-00002")
    assert tree.require("init-00002").relative == PurePosixPath(f"{LOW}/init-00002")


def test_an_upper_case_id_name_is_misplaced_even_where_case_is_ignored(tmp_path: Path) -> None:
    _make(tmp_path, f"{LOW}/ISS-00454")
    tree = CatalogTree(tmp_path)
    assert tree.find("iss-00454") is None and tree.directories() == ()
    assert tree.misplaced() == (MisplacedDirectory(PurePosixPath(f"{LOW}/ISS-00454"), "name"),)
