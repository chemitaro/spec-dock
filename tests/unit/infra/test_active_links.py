from __future__ import annotations

import os
from typing import TYPE_CHECKING

from spec_dock.runtime.domain.active_links import plan_links
from spec_dock.runtime.infra.active_links import sync_active_links

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

ISSUE = "initiatives/init-00001-a/epics/epic-00002-b/issues/iss-00003-c"
CHAIN = (
    ("initiative", "initiatives/init-00001-a"),
    ("epic", "initiatives/init-00001-a/epics/epic-00002-b"),
    ("issue", ISSUE),
)


def _workspace(tmp_path: Path) -> Path:
    specdock = tmp_path / "spec-dock"
    (specdock / ISSUE).mkdir(parents=True)
    for role in ("initiative", "epic", "issue"):
        (specdock / "system/active-none" / role).mkdir(parents=True)
    return specdock


def _statuses(outcomes: tuple[object, ...]) -> list[tuple[str, str]]:
    return [(item.role, item.status) for item in outcomes]  # type: ignore[attr-defined]


def test_missing_links_are_created_as_relative_symlinks(tmp_path: Path) -> None:
    specdock = _workspace(tmp_path)
    links = sync_active_links(specdock, plan_links(CHAIN), dry_run=False)
    assert _statuses(links) == [("initiative", "succeeded"), ("epic", "succeeded"), ("issue", "succeeded")]
    assert str((specdock / "active/issue").readlink()) == "../" + ISSUE
    assert (specdock / "active/issue").resolve() == (specdock / ISSUE).resolve()


def test_matching_links_are_unchanged_and_stale_symlinks_are_replaced(tmp_path: Path) -> None:
    specdock = _workspace(tmp_path)
    sync_active_links(specdock, plan_links(()), dry_run=False)
    links = sync_active_links(specdock, plan_links(CHAIN[:2]), dry_run=False)
    assert _statuses(links) == [("initiative", "succeeded"), ("epic", "succeeded"), ("issue", "unchanged")]
    assert str((specdock / "active/epic").readlink()) == "../initiatives/init-00001-a/epics/epic-00002-b"
    assert str((specdock / "active/issue").readlink()) == "../system/active-none/issue"
    assert sorted(path.name for path in (specdock / "active").iterdir()) == ["epic", "initiative", "issue"]


def test_real_files_and_directories_at_role_names_are_left_untouched(tmp_path: Path) -> None:
    specdock = _workspace(tmp_path)
    (specdock / "active/issue").mkdir(parents=True)
    (specdock / "active/issue/notes.md").write_bytes(b"mine")
    (specdock / "active/epic").write_bytes(b"also mine")
    links = sync_active_links(specdock, plan_links(CHAIN), dry_run=False)
    assert [(item.role, item.status, item.reason) for item in links] == [
        ("initiative", "succeeded", None),
        ("epic", "skipped", "occupied"),
        ("issue", "skipped", "occupied"),
    ]
    assert (specdock / "active/issue/notes.md").read_bytes() == b"mine"
    assert (specdock / "active/epic").read_bytes() == b"also mine"


def test_redirected_or_non_directory_active_root_receives_no_writes(tmp_path: Path) -> None:
    specdock = _workspace(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "context-pack.md").write_bytes(b"outside")
    (specdock / "active").symlink_to(outside)
    links = sync_active_links(specdock, plan_links(CHAIN), dry_run=False)
    assert {(item.status, item.reason) for item in links} == {("skipped", "active_not_directory")}
    assert sorted(path.name for path in outside.iterdir()) == ["context-pack.md"]
    (specdock / "active").unlink()
    (specdock / "active").write_bytes(b"file")
    links = sync_active_links(specdock, plan_links(CHAIN), dry_run=False)
    assert {(item.status, item.reason) for item in links} == {("skipped", "active_not_directory")}
    assert (specdock / "active").read_bytes() == b"file"


def test_missing_link_targets_are_reported_instead_of_creating_dangling_links(tmp_path: Path) -> None:
    specdock = _workspace(tmp_path)
    (specdock / "system/active-none/issue").rmdir()
    links = sync_active_links(specdock, plan_links(CHAIN[:2]), dry_run=False)
    assert [(item.role, item.status, item.reason) for item in links][2] == ("issue", "skipped", "target_missing")
    assert not (specdock / "active/issue").is_symlink()


def test_dry_run_reports_the_plan_without_creating_replacing_or_removing(tmp_path: Path) -> None:
    specdock = _workspace(tmp_path)
    sync_active_links(specdock, plan_links(()), dry_run=False)
    (specdock / "active/context-pack.md").write_bytes(b"old")
    before = {
        path.name: str(path.readlink()) if path.is_symlink() else path.read_bytes()
        for path in (specdock / "active").iterdir()
    }
    links = sync_active_links(specdock, plan_links(CHAIN[:2]), dry_run=True)
    assert _statuses(links) == [("initiative", "planned"), ("epic", "planned"), ("issue", "unchanged")]
    after = {
        path.name: str(path.readlink()) if path.is_symlink() else path.read_bytes()
        for path in (specdock / "active").iterdir()
    }
    assert after == before


def test_dry_run_does_not_create_the_active_directory(tmp_path: Path) -> None:
    specdock = _workspace(tmp_path)
    links = sync_active_links(specdock, plan_links(CHAIN), dry_run=True)
    assert {item.status for item in links} == {"planned"}
    assert not (specdock / "active").exists()


def test_a_failed_role_write_is_reported_without_leaving_staged_links_or_stopping_others(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    specdock = _workspace(tmp_path)
    real_symlink = os.symlink

    def failing_symlink(source: str, destination: str, **kwargs: int) -> None:
        if destination == "epic":
            raise PermissionError("denied")
        real_symlink(source, destination, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(os, "symlink", failing_symlink)
    links = sync_active_links(specdock, plan_links(CHAIN), dry_run=False)
    assert [(item.role, item.status) for item in links] == [
        ("initiative", "succeeded"),
        ("epic", "skipped"),
        ("issue", "succeeded"),
    ]
    assert links[1].reason is not None and "denied" in links[1].reason
    assert sorted(path.name for path in (specdock / "active").iterdir()) == ["initiative", "issue"]


def test_active_mkdir_failure_is_reported_not_raised(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    specdock = _workspace(tmp_path)

    def failing_mkdir(*args: object, **kwargs: object) -> None:
        raise PermissionError("denied")

    monkeypatch.setattr(os, "mkdir", failing_mkdir)
    links = sync_active_links(specdock, plan_links(CHAIN), dry_run=False)
    assert {item.status for item in links} == {"skipped"}


def test_unreadable_link_target_is_a_skipped_role_not_an_exception(tmp_path: Path) -> None:
    specdock = _workspace(tmp_path)
    fallback = specdock / "system/active-none"
    fallback.chmod(0)
    try:
        links = sync_active_links(specdock, plan_links(CHAIN[:2]), dry_run=False)
    finally:
        fallback.chmod(0o755)
    assert [(item.role, item.status) for item in links] == [
        ("initiative", "succeeded"),
        ("epic", "succeeded"),
        ("issue", "skipped"),
    ]


def test_active_root_swapped_after_inspection_never_receives_writes_or_deletes_outside(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    specdock = _workspace(tmp_path)
    active = specdock / "active"
    active.mkdir()
    (active / "context-pack.md").write_bytes(b"old")
    outside = tmp_path / "outside"
    outside.mkdir()
    for name in ("issue", "context-pack.md"):
        (outside / name).write_bytes(b"outside user file")
    real_symlink = os.symlink
    swapped: list[bool] = []

    def racing_symlink(*args: object, **kwargs: object) -> None:
        if not swapped:
            swapped.append(True)
            active.rename(specdock / "active-moved")
            active.symlink_to(outside)
        real_symlink(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(os, "symlink", racing_symlink)
    sync_active_links(specdock, plan_links(CHAIN), dry_run=False)
    assert sorted(path.name for path in outside.iterdir()) == ["context-pack.md", "issue"]
    assert all((outside / name).read_bytes() == b"outside user file" for name in ("issue", "context-pack.md"))


def test_a_file_placed_after_the_role_check_is_preserved_instead_of_replaced(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    specdock = _workspace(tmp_path)
    sync_active_links(specdock, plan_links(()), dry_run=False)
    issue = specdock / "active/issue"
    real_readlink = os.readlink

    def racing_readlink(name: str, **kwargs: int) -> str:
        observed = real_readlink(name, **kwargs)  # type: ignore[arg-type]
        if name == "issue":
            issue.unlink()
            issue.write_bytes(b"checked out by a concurrent writer")
        return observed

    monkeypatch.setattr(os, "readlink", racing_readlink)
    links = sync_active_links(specdock, plan_links(CHAIN), dry_run=False)
    assert (links[2].role, links[2].status, links[2].reason) == ("issue", "skipped", "occupied")
    assert not issue.is_symlink() and issue.read_bytes() == b"checked out by a concurrent writer"
    assert sorted(path.name for path in (specdock / "active").iterdir()) == ["epic", "initiative", "issue"]
