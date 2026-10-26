"""Observing and placing links, and appending the exclude lines, without ever replacing real content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.domain.canonical_layout import EXCLUDE_LINES
from spec_dock.runtime.infra.canonical_files import (
    LinkOccupied,
    append_exclude,
    observe_link,
    place_link,
    read_text_file,
)

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def spec_dock(tmp_path: Path) -> Path:
    directory = tmp_path / "checkout/spec-dock"
    directory.mkdir(parents=True)
    (tmp_path / "catalog").mkdir()
    return directory


def test_observation_distinguishes_absent_links_directories_and_files(spec_dock: Path, tmp_path: Path) -> None:
    link = spec_dock / "initiatives"
    assert observe_link(link).kind == "absent"
    link.symlink_to(tmp_path / "catalog")
    observed = observe_link(link)
    assert (observed.kind, observed.text, observed.resolved) == (
        "symlink",
        str(tmp_path / "catalog"),
        (tmp_path / "catalog").resolve(),
    )
    link.unlink()
    link.symlink_to(tmp_path / "missing")
    assert observe_link(link).resolved is None
    link.unlink()
    (link / "init-00001-x").mkdir(parents=True)
    (link / "init-00001-x/plan.md").write_text("x", encoding="utf-8")
    observed = observe_link(link)
    assert (observed.kind, observed.entries) == ("directory", 2)
    (spec_dock / "file").write_text("x", encoding="utf-8")
    assert observe_link(spec_dock / "file").kind == "file"


def test_placing_creates_a_missing_link_and_replaces_a_wrong_one(spec_dock: Path, tmp_path: Path) -> None:
    assert place_link(spec_dock, "initiatives", ".canonical") == "created"
    assert str((spec_dock / "initiatives").readlink()) == ".canonical"
    target = str(tmp_path / "catalog")
    assert place_link(spec_dock, "initiatives", target) == "replaced"
    assert str((spec_dock / "initiatives").readlink()) == target
    assert place_link(spec_dock, "initiatives", target) == "unchanged"
    assert sorted(entry.name for entry in spec_dock.iterdir()) == ["initiatives"]


def test_replacing_never_writes_inside_the_old_link_target(spec_dock: Path, tmp_path: Path) -> None:
    (spec_dock / "initiatives").symlink_to(tmp_path / "catalog")
    place_link(spec_dock, "initiatives", ".canonical")
    assert list((tmp_path / "catalog").iterdir()) == []


@pytest.mark.parametrize("kind", ["directory", "file"])
def test_real_content_is_never_replaced(spec_dock: Path, kind: str) -> None:
    occupied = spec_dock / "initiatives"
    if kind == "directory":
        occupied.mkdir()
        (occupied / "keep.md").write_text("keep", encoding="utf-8")
    else:
        occupied.write_text("keep", encoding="utf-8")
    with pytest.raises(LinkOccupied):
        place_link(spec_dock, "initiatives", ".canonical")
    assert (occupied / "keep.md" if kind == "directory" else occupied).read_text(encoding="utf-8") == "keep"
    assert sorted(entry.name for entry in spec_dock.iterdir()) == ["initiatives"]


def test_a_link_turned_into_a_directory_just_before_replacement_is_kept(
    spec_dock: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.infra import canonical_files

    link = spec_dock / "initiatives"
    link.symlink_to(tmp_path / "catalog")
    original = canonical_files._is_symlink_at

    def swap(directory_fd: int, name: str) -> bool:
        if name == "initiatives" and link.is_symlink():
            link.unlink()
            link.mkdir()
            (link / "new.md").write_text("new", encoding="utf-8")
        return original(directory_fd, name)

    monkeypatch.setattr(canonical_files, "_is_symlink_at", swap)
    with pytest.raises(LinkOccupied):
        place_link(spec_dock, "initiatives", ".canonical")
    assert (link / "new.md").read_text(encoding="utf-8") == "new"
    assert sorted(entry.name for entry in spec_dock.iterdir()) == ["initiatives"]


def test_a_redirected_spec_dock_directory_is_refused(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    (tmp_path / "spec-dock").symlink_to(real)
    with pytest.raises(OSError):
        place_link(tmp_path / "spec-dock", "initiatives", ".canonical")
    assert list(real.iterdir()) == []


def test_exclude_lines_are_appended_once_and_keep_the_file_mode(tmp_path: Path) -> None:
    common = tmp_path / ".git"
    common.mkdir()
    assert append_exclude(common, EXCLUDE_LINES) == EXCLUDE_LINES
    exclude = common / "info/exclude"
    first = exclude.read_text(encoding="utf-8")
    assert all(line in first.splitlines() for line in EXCLUDE_LINES)
    exclude.write_text("*.log\n/spec-dock/.canonical/\n", encoding="utf-8")
    exclude.chmod(0o640)
    assert append_exclude(common, EXCLUDE_LINES) == EXCLUDE_LINES
    assert exclude.read_text(encoding="utf-8").endswith(
        "/spec-dock/.canonical/\n/spec-dock/initiatives\n!/spec-dock/initiatives/\n"
    )
    assert exclude.stat().st_mode & 0o777 == 0o640
    assert append_exclude(common, EXCLUDE_LINES) == ()
    assert sorted(entry.name for entry in (common / "info").iterdir()) == ["exclude"]


def test_exclude_bytes_that_are_not_utf8_are_kept_as_they_were(tmp_path: Path) -> None:
    common = tmp_path / ".git"
    (common / "info").mkdir(parents=True)
    original = b"# caf\xe9 latin-1 comment\n/build/\n"
    (common / "info/exclude").write_bytes(original)
    append_exclude(common, EXCLUDE_LINES)
    assert (common / "info/exclude").read_bytes().startswith(original)


def test_reading_a_missing_text_file_gives_none(tmp_path: Path) -> None:
    assert read_text_file(tmp_path / "missing") is None
    (tmp_path / "present").write_text("a\n", encoding="utf-8")
    assert read_text_file(tmp_path / "present") == "a\n"
