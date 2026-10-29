"""Read-only catalog observation, the linked-catalog guard and the catalog write helper (contracts C3, C4)."""

from __future__ import annotations

import json
import shutil
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.application.canonical_catalog import (
    catalog_changes,
    observe_catalog,
    require_linked,
    resolve_layout,
)
from spec_dock.runtime.application.canonical_errors import CanonicalCommandError
from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.infra import canonical_git as cg
from spec_dock.runtime.infra.catalog_lock import CatalogLock
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.canonical_repo import add_worktree, bare_remote, clone, environment, git, isolate_user_state


@pytest.fixture
def isolated(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    return isolate_user_state(monkeypatch, tmp_path)


pytestmark = pytest.mark.usefixtures("isolated")


if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def main(tmp_path: Path) -> Path:
    return clone(bare_remote(tmp_path / "remote.git"), tmp_path / "main")


def _catalog(main: Path, *, lock: bool = True, link: bool = True) -> Path:
    oid = cg.create_initial_commit(main)
    cg.push_initial(main, oid)
    cg.fetch_canonical(main)
    catalog = main / "spec-dock/.canonical"
    cg.add_catalog_worktree(main, catalog, mode="track")
    if lock:
        cg.lock_worktree(main, catalog)
    if link:
        (main / "spec-dock/initiatives").symlink_to(".canonical")
    return catalog


def _observe(checkout: Path, *, container: bool = False):  # type: ignore[no-untyped-def]
    context = resolve_context(str(checkout), checkout)
    return observe_catalog(resolve_layout(context), environment(container=container), timeout=30)


def test_the_layout_finds_the_main_checkout_from_a_linked_worktree(main: Path, tmp_path: Path) -> None:
    linked = add_worktree(main, tmp_path / "linked", "feature")
    layout = resolve_layout(resolve_context(str(linked), linked))
    assert (layout.main_checkout, layout.checkout, layout.common_dir) == (main, linked, main / ".git")


def test_a_bare_clone_has_no_main_checkout(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path / "remote.git")
    git(remote, "worktree", "add", "-q", str(tmp_path / "tree"), "main")
    tree = (tmp_path / "tree").resolve()
    with pytest.raises(CanonicalCommandError) as raised:
        resolve_layout(resolve_context(str(tree), tree))
    assert raised.value.code == "CANONICAL_UNSUPPORTED_LAYOUT" and raised.value.recovery


def test_no_catalog_and_no_registration_is_absent(main: Path) -> None:
    observed = _observe(main)
    assert observed.state == "absent" and observed.registered is None
    assert observed.exclude_missing == ("/spec-dock/.canonical/", "/spec-dock/initiatives", "!/spec-dock/initiatives/")
    assert [(view.state, view.expected) for view in observed.links] == [("absent", ".canonical")]


def test_a_locked_registered_catalog_with_its_link_is_ready(main: Path) -> None:
    _catalog(main)
    observed = _observe(main)
    assert (observed.state, observed.locked, observed.moved) == ("ready", True, False)
    assert [view.state for view in observed.links] == ["correct"]


def test_an_unlocked_catalog_is_still_ready_but_reports_the_lock(main: Path) -> None:
    _catalog(main, lock=False)
    assert (_observe(main).state, _observe(main).locked) == ("ready", False)


def test_a_cleaned_catalog_with_its_registration_left_is_re_addable(main: Path) -> None:
    catalog = _catalog(main)
    shutil.rmtree(catalog)
    observed = _observe(main)
    assert observed.state == "readd" and observed.registered is not None and observed.registered.path == catalog
    assert [view.state for view in observed.links] == ["wrong_link"]


def test_a_moved_main_checkout_needs_repair_or_is_foreign_in_a_container(main: Path, tmp_path: Path) -> None:
    _catalog(main)
    moved = tmp_path / "moved"
    main.rename(moved)
    observed = _observe(moved)
    assert (observed.state, observed.moved) == ("repair", True)
    assert observed.registered is not None and observed.registered.path == main / "spec-dock/.canonical"
    assert _observe(moved, container=True).state == "foreign"


def test_a_registration_at_another_path_is_elsewhere(main: Path, tmp_path: Path) -> None:
    oid = cg.create_initial_commit(main)
    cg.push_initial(main, oid)
    cg.fetch_canonical(main)
    git(
        main,
        "worktree",
        "add",
        "-q",
        "--track",
        "-b",
        "spec-dock/canonical",
        str(tmp_path / "other"),
        "origin/spec-dock/canonical",
    )
    observed = _observe(main)
    assert observed.state == "elsewhere" and observed.registered is not None
    assert observed.registered.path == (tmp_path / "other").resolve()
    shutil.rmtree(tmp_path / "other")
    assert _observe(main).state == "elsewhere"


@pytest.mark.parametrize("kind", ["file", "directory", "empty", "foreign-git"])
def test_anything_else_at_the_catalog_path_is_occupied(main: Path, kind: str) -> None:
    catalog = main / "spec-dock/.canonical"
    if kind == "file":
        catalog.write_text("x", encoding="utf-8")
    elif kind == "foreign-git":
        catalog.mkdir()
        (catalog / ".git").write_text("gitdir: /nowhere/worktrees/x\n", encoding="utf-8")
    else:
        catalog.mkdir()
        if kind == "directory":
            (catalog / "plan.md").write_text("x", encoding="utf-8")
    assert _observe(main).state == "occupied"


def test_observation_writes_nothing(main: Path, tmp_path: Path) -> None:
    _catalog(main)
    linked = add_worktree(main, tmp_path / "linked", "feature")
    (main / "spec-dock/.canonical/init-00001-plan").mkdir()
    before = tree_digest(main), tree_digest(linked)
    _observe(linked)
    assert (tree_digest(main), tree_digest(linked)) == before


def test_require_linked_returns_the_catalog_tree_through_a_correct_link(main: Path) -> None:
    catalog = _catalog(main)
    (catalog / "init-00007").mkdir()
    linked = require_linked(resolve_context(str(main), main), environment=environment())
    assert linked.catalog == catalog and linked.tree.require("init-00007").path == catalog / "init-00007"


@pytest.mark.parametrize("damage", ["no-link", "wrong-link", "no-catalog", "unfinished-checkout"])
def test_require_linked_refuses_without_writing(main: Path, damage: str) -> None:
    catalog = _catalog(main)
    link = main / "spec-dock/initiatives"
    if damage == "no-link":
        link.unlink()
    elif damage == "wrong-link":
        link.unlink()
        link.symlink_to(str(catalog))
    elif damage == "unfinished-checkout":
        admin = cg.read_gitdir(catalog)
        assert admin is not None
        (admin / "index").unlink()  # a timed-out git worktree add: a sync must not see every file as deleted
    else:
        shutil.rmtree(catalog)
    before = tree_digest(main)
    with pytest.raises(CanonicalCommandError) as raised:
        require_linked(resolve_context(str(main), main), environment=environment())
    assert raised.value.code == "CANONICAL_NOT_LINKED"
    assert raised.value.recovery == ("spec-dock canonical link",)
    assert tree_digest(main) == before


def test_require_linked_stops_for_a_mounted_checkout_and_an_old_git(main: Path, tmp_path: Path) -> None:
    _catalog(main)
    moved = tmp_path / "moved"
    main.rename(moved)
    context = resolve_context(str(moved), moved)
    with pytest.raises(CanonicalCommandError) as raised:
        require_linked(context, environment=environment(container=True))
    assert raised.value.code == "CANONICAL_FOREIGN_CHECKOUT"
    with pytest.raises(CanonicalCommandError) as old:
        require_linked(context, environment=environment(git_version=(2, 37, 0)))
    assert old.value.code == "CANONICAL_GIT_TOO_OLD"


def test_catalog_changes_writes_one_changeset_inside_the_lock(main: Path) -> None:
    catalog = _catalog(main)
    with catalog_changes(catalog, command="scope create") as changes:
        (catalog / "init-00001-plan").mkdir()
        changes.add("init-00001-plan")
        changes.delete("init-00002-old")
        assert changes.staging() == catalog / ".runtime/staging"
        with pytest.raises(CanonicalCommandError) as busy, catalog_changes(catalog, command="other", timeout=0):
            pass
        assert busy.value.code == "CANONICAL_LOCK_BUSY"
    assert changes.written is not None and changes.written.parent == catalog / ".runtime/changesets"
    payload = json.loads(changes.written.read_text(encoding="utf-8"))
    assert payload["paths"] == ["init-00001-plan"] and payload["deletions"] == ["init-00002-old"]
    assert payload["origin"] == "command" and payload["command"] == "scope create"
    assert git(catalog, "status", "--porcelain", "--ignored", "--", ".runtime").startswith("!! .runtime/")


def test_catalog_changes_records_what_was_written_before_an_error(main: Path) -> None:
    catalog = _catalog(main)
    with pytest.raises(RuntimeError), catalog_changes(catalog, command="scope create") as changes:
        changes.add("init-00001-plan")
        raise RuntimeError("publication failed")
    assert changes.written is not None
    with catalog_changes(catalog, command="noop") as nothing:
        pass
    assert nothing.written is None


@pytest.mark.parametrize("payload", [b'{"format": 2}\n', b"broken", None, "directory"])
def test_catalog_changes_refuses_an_unknown_format_before_writing(main: Path, payload: bytes | str | None) -> None:
    catalog = _catalog(main)
    marker = catalog / ".spec-dock-canonical.json"
    if payload is None:
        marker.unlink()
    elif payload == "directory":
        marker.unlink()
        marker.mkdir()  # unreadable as a file (IsADirectoryError), like a permission failure
    else:
        assert isinstance(payload, bytes)
        marker.write_bytes(payload)
    with pytest.raises(CanonicalCommandError) as raised, catalog_changes(catalog, command="scope create") as changes:
        changes.add("init-00001-plan")
    assert raised.value.code == "CANONICAL_FORMAT_UNSUPPORTED"
    assert not (catalog / ".runtime").exists()


def test_catalog_changes_maps_a_held_lock_to_lock_busy(main: Path) -> None:
    catalog = _catalog(main)
    with (
        CatalogLock(catalog, timeout=0),
        pytest.raises(CanonicalCommandError) as raised,
        catalog_changes(catalog, command="scope create", timeout=0),
    ):
        pass
    assert raised.value.code == "CANONICAL_LOCK_BUSY" and raised.value.exit_code == 3
    assert ".runtime" not in {entry.name for entry in catalog.iterdir()}
