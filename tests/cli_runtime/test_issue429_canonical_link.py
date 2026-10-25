"""`spec-dock canonical link` and the link after `worktree create`, against bare temporary remotes (iss-00429)."""

from __future__ import annotations

import json
import os
import shutil
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.cli import main
from spec_dock.runtime.domain.canonical_content import CANONICAL_ROOT_FILES
from spec_dock.runtime.infra import canonical_git, runtime_environment
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.canonical_repo import (
    add_worktree,
    bare_remote,
    clone,
    environment,
    git,
    isolate_user_state,
)

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.usefixtures("isolated")

EXCLUDE = ("/spec-dock/.canonical/", "/spec-dock/initiatives", "!/spec-dock/initiatives/")


@pytest.fixture
def isolated(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    isolate_user_state(monkeypatch, tmp_path)
    inject(monkeypatch)


def inject(monkeypatch: pytest.MonkeyPatch, **options: Any) -> None:
    monkeypatch.setattr(
        runtime_environment, "detect_runtime_environment", lambda *args, **kwargs: environment(**options)
    )


def run(capsys: pytest.CaptureFixture[str], checkout: Path, *argv: str) -> tuple[int, dict[str, Any]]:
    code = main(["--project", str(checkout), *argv, "--json"])
    output = capsys.readouterr()
    return code, json.loads(output.out)


def link(capsys: pytest.CaptureFixture[str], checkout: Path, *extra: str) -> tuple[int, dict[str, Any]]:
    return run(capsys, checkout, "canonical", "link", *extra)


def effects(result: dict[str, Any]) -> list[tuple[str, str]]:
    return [(item["kind"], item["status"]) for item in result["effects"]]


@pytest.fixture
def remote(tmp_path: Path) -> Path:
    return bare_remote(tmp_path / "remote.git")


@pytest.fixture
def main_checkout(remote: Path, tmp_path: Path) -> Path:
    return clone(remote, tmp_path / "main")


def test_the_first_link_of_a_new_repository_creates_the_canonical_and_links_main(
    capsys: pytest.CaptureFixture[str], remote: Path, main_checkout: Path
) -> None:
    code, result = link(capsys, main_checkout)
    assert code == 0 and result["status"] == "succeeded", result
    catalog = main_checkout / "spec-dock/.canonical"
    assert effects(result) == [
        ("canonical.remote.create", "succeeded"),
        ("git.fetch", "succeeded"),
        ("git.worktree.add", "succeeded"),
        ("git.worktree.lock", "succeeded"),
        ("git.info.exclude", "succeeded"),
        ("canonical.link", "succeeded"),
    ]
    data = result["data"]["result"]
    assert data["catalog"] == str(catalog) and data["source"] == "new" and data["catalog_state"] == "ready"
    assert str((main_checkout / "spec-dock/initiatives").readlink()) == ".canonical"
    pushed = git(remote, "rev-parse", "refs/heads/spec-dock/canonical")
    assert git(remote, "rev-list", "--parents", "-n", "1", pushed) == pushed
    assert sorted(git(remote, "ls-tree", "--name-only", pushed).splitlines()) == sorted(CANONICAL_ROOT_FILES)
    (worktree,) = [item for item in canonical_git.list_worktrees(main_checkout) if item.branch == "spec-dock/canonical"]
    assert worktree.path == catalog and worktree.locked
    exclude = (main_checkout / ".git/info/exclude").read_text(encoding="utf-8").splitlines()
    assert all(line in exclude for line in EXCLUDE)
    assert git(main_checkout, "status", "--porcelain", "--untracked-files=all") == ""
    (main_checkout / "spec-dock/initiatives/init-00001-plan").mkdir()
    (main_checkout / "spec-dock/initiatives/init-00001-plan/plan.md").write_text("plan\n", encoding="utf-8")
    assert (catalog / "init-00001-plan/plan.md").read_text(encoding="utf-8") == "plan\n"


def test_linking_again_changes_nothing(capsys: pytest.CaptureFixture[str], main_checkout: Path) -> None:
    assert link(capsys, main_checkout)[0] == 0
    before = tree_digest(main_checkout)
    code, result = link(capsys, main_checkout)
    assert code == 0 and result["status"] == "unchanged"
    assert {status for _kind, status in effects(result)} == {"unchanged"}
    assert tree_digest(main_checkout) == before


def test_dry_run_plans_without_writing(capsys: pytest.CaptureFixture[str], remote: Path, main_checkout: Path) -> None:
    before = tree_digest(main_checkout), tree_digest(remote)
    code, result = link(capsys, main_checkout, "--dry-run")
    assert code == 0 and result["status"] == "planned"
    assert {status for _kind, status in effects(result)} == {"planned"}
    assert (tree_digest(main_checkout), tree_digest(remote)) == before


def test_a_second_clone_and_linked_worktrees_share_one_catalog_per_clone(
    capsys: pytest.CaptureFixture[str], remote: Path, main_checkout: Path, tmp_path: Path
) -> None:
    assert link(capsys, main_checkout)[0] == 0
    catalog = main_checkout / "spec-dock/.canonical"
    (catalog / "init-00001-plan").mkdir()
    (catalog / "init-00001-plan/plan.md").write_text("from the first clone\n", encoding="utf-8")
    git(catalog, "add", "-A")
    git(catalog, "commit", "-qm", "save")
    git(catalog, "push", "-q", "origin", "HEAD:refs/heads/spec-dock/canonical")

    other = clone(remote, tmp_path / "other")
    code, result = link(capsys, other)
    assert code == 0 and result["data"]["result"]["source"] == "remote", result
    assert (other / "spec-dock/initiatives/init-00001-plan/plan.md").read_text(
        encoding="utf-8"
    ) == "from the first clone\n"
    assert (
        git(other / "spec-dock/.canonical", "rev-parse", "--abbrev-ref", "@{upstream}") == "origin/spec-dock/canonical"
    )

    linked = add_worktree(main_checkout, tmp_path / "linked", "feature")
    code, result = link(capsys, linked)
    assert code == 0, result
    assert str((linked / "spec-dock/initiatives").readlink()) == str(catalog)
    (linked / "spec-dock/initiatives/init-00001-plan/design.md").write_text("from the worktree\n", encoding="utf-8")
    assert (main_checkout / "spec-dock/initiatives/init-00001-plan/design.md").read_text(
        encoding="utf-8"
    ) == "from the worktree\n"
    assert git(linked, "status", "--porcelain", "--untracked-files=all") == ""


def test_worktree_create_links_the_new_worktree_without_another_command(
    capsys: pytest.CaptureFixture[str], main_checkout: Path, tmp_path: Path
) -> None:
    assert link(capsys, main_checkout)[0] == 0
    code, result = run(
        capsys,
        main_checkout,
        "worktree",
        "create",
        "feature",
        "--base",
        "HEAD",
        "--root",
        str(tmp_path / "trees"),
        "--yes",
    )
    assert code == 0 and result["status"] == "succeeded", result
    created = (tmp_path / "trees/feature").resolve()
    assert ("canonical.link", "succeeded") in effects(result)
    assert result["data"]["result"]["canonical_link"] == {
        "path": str(created / "spec-dock/initiatives"),
        "state": "correct",
    }
    (created / "spec-dock/initiatives/init-00002-new").mkdir()
    assert (main_checkout / "spec-dock/.canonical/init-00002-new").is_dir()


def test_worktree_create_dry_run_plans_the_link(
    capsys: pytest.CaptureFixture[str], main_checkout: Path, tmp_path: Path
) -> None:
    assert link(capsys, main_checkout)[0] == 0
    code, result = run(
        capsys,
        main_checkout,
        "worktree",
        "create",
        "feature",
        "--base",
        "HEAD",
        "--root",
        str(tmp_path / "trees"),
        "--dry-run",
    )
    assert code == 0 and result["status"] == "planned"
    assert ("canonical.link", "planned") in effects(result)
    assert not (tmp_path / "trees").exists()


def test_worktree_create_with_expect_current_is_not_implemented(
    capsys: pytest.CaptureFixture[str], main_checkout: Path, tmp_path: Path
) -> None:
    code, result = run(
        capsys,
        main_checkout,
        "--expect-current",
        "init-00001",
        "worktree",
        "create",
        "feature",
        "--base",
        "HEAD",
        "--root",
        str(tmp_path / "trees"),
        "--yes",
    )
    assert code == 3 and result["error"]["code"] == "CANONICAL_NOT_IMPLEMENTED"
    assert not (tmp_path / "trees").exists()


def test_a_failed_link_after_worktree_create_is_a_warning_with_the_next_step(
    capsys: pytest.CaptureFixture[str], main_checkout: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert link(capsys, main_checkout)[0] == 0
    from spec_dock.runtime.infra.start_lock import StartLockBusy

    def busy(*args: object, **kwargs: object) -> None:
        raise StartLockBusy("another work start or branch switch holds the clone Start lock")

    monkeypatch.setattr("spec_dock.runtime.application.canonical_link.StartLock.__enter__", busy)
    code, result = run(
        capsys,
        main_checkout,
        "worktree",
        "create",
        "feature",
        "--base",
        "HEAD",
        "--root",
        str(tmp_path / "trees"),
        "--yes",
    )
    assert code == 0 and result["status"] == "succeeded", result
    (warning,) = [item for item in result["warnings"] if item["code"] == "START_LOCK_BUSY"]
    assert "spec-dock canonical link" in warning["details"]["next_step"]
    assert result["data"]["result"]["canonical_link"]["state"] == "failed"
    assert not os.path.lexists(tmp_path / "trees/feature/spec-dock/initiatives")


def _digests(*roots: Path) -> tuple[str, ...]:
    return tuple(tree_digest(root) for root in roots)


@pytest.mark.parametrize("kind", ["directory", "file"])
def test_a_real_entry_at_the_link_place_stops_without_writing_or_deleting(
    capsys: pytest.CaptureFixture[str], remote: Path, main_checkout: Path, kind: str
) -> None:
    occupied = main_checkout / "spec-dock/initiatives"
    if kind == "directory":
        (occupied / "init-00001-old").mkdir(parents=True)
        (occupied / "init-00001-old/plan.md").write_text("keep\n", encoding="utf-8")
    else:
        occupied.write_text("keep\n", encoding="utf-8")
    before = _digests(main_checkout, remote)
    code, result = link(capsys, main_checkout)
    assert code == 3 and result["status"] == "failed" and result["effects"] == []
    assert result["error"]["code"] == "CANONICAL_LINK_OCCUPIED"
    assert result["error"]["details"]["path"] == str(occupied)
    assert result["error"]["details"]["entries"] == (2 if kind == "directory" else None)
    assert "does not delete" in result["recovery"]["instructions"][0]
    assert _digests(main_checkout, remote) == before


def test_an_occupied_link_in_the_main_checkout_also_stops_a_linked_worktree(
    capsys: pytest.CaptureFixture[str], main_checkout: Path, tmp_path: Path
) -> None:
    assert link(capsys, main_checkout)[0] == 0
    linked = add_worktree(main_checkout, tmp_path / "linked", "feature")
    (main_checkout / "spec-dock/initiatives").unlink()
    (main_checkout / "spec-dock/initiatives").mkdir()
    before = _digests(main_checkout, linked)
    code, result = link(capsys, linked)
    assert code == 3 and result["error"]["code"] == "CANONICAL_LINK_OCCUPIED"
    assert _digests(main_checkout, linked) == before


@pytest.mark.parametrize("kind", ["file", "directory"])
def test_something_else_at_the_catalog_place_stops(
    capsys: pytest.CaptureFixture[str], main_checkout: Path, kind: str
) -> None:
    catalog = main_checkout / "spec-dock/.canonical"
    if kind == "file":
        catalog.write_text("x", encoding="utf-8")
    else:
        catalog.mkdir()
        (catalog / "notes.md").write_text("x", encoding="utf-8")
    before = tree_digest(main_checkout)
    code, result = link(capsys, main_checkout)
    assert code == 3 and result["error"]["code"] == "CANONICAL_PATH_OCCUPIED" and result["effects"] == []
    assert tree_digest(main_checkout) == before


@pytest.mark.parametrize("exists", [True, False])
def test_the_canonical_branch_checked_out_elsewhere_stops(
    capsys: pytest.CaptureFixture[str], main_checkout: Path, tmp_path: Path, exists: bool
) -> None:
    assert link(capsys, main_checkout)[0] == 0
    catalog = main_checkout / "spec-dock/.canonical"
    git(main_checkout, "worktree", "unlock", str(catalog))
    git(main_checkout, "worktree", "move", str(catalog), str(tmp_path / "elsewhere"))
    if not exists:
        shutil.rmtree(tmp_path / "elsewhere")
    before = sorted(path.name for path in (main_checkout / ".git/worktrees").iterdir())
    code, result = link(capsys, main_checkout)
    assert code == 3 and result["error"]["code"] == "CANONICAL_PATH_OCCUPIED", result
    assert result["error"]["details"]["registered_path"] == str((tmp_path / "elsewhere").resolve())
    step = result["recovery"]["instructions"][0]
    if exists:
        assert "switch to another branch" in step and "git worktree remove" not in step
    else:
        assert "git worktree unlock" in step and "git worktree remove" in step
    assert sorted(path.name for path in (main_checkout / ".git/worktrees").iterdir()) == before


def test_git_clean_removes_the_catalog_and_link_and_link_re_adds_them_without_prune(
    capsys: pytest.CaptureFixture[str], main_checkout: Path, tmp_path: Path
) -> None:
    assert link(capsys, main_checkout)[0] == 0
    gone = tmp_path / "gone"
    git(main_checkout, "worktree", "add", "-q", "-b", "gone", str(gone))
    shutil.rmtree(gone)
    git(main_checkout, "clean", "-ffdxq")
    assert not os.path.lexists(main_checkout / "spec-dock/.canonical")
    assert not os.path.lexists(main_checkout / "spec-dock/initiatives")
    code, status = run(capsys, main_checkout, "canonical", "status")
    assert code == 0 and status["data"]["catalog"]["state"] == "readd"
    assert status["data"]["catalog"]["next_step"] == "spec-dock canonical link"
    code, result = link(capsys, main_checkout)
    assert code == 0, result
    assert ("git.worktree.add", "succeeded") in effects(result) and ("git.worktree.lock", "succeeded") in effects(
        result
    )
    names = sorted(path.name for path in (main_checkout / ".git/worktrees").iterdir())
    assert "gone" in names
    assert str((main_checkout / "spec-dock/initiatives").readlink()) == ".canonical"


def test_a_moved_main_checkout_is_repaired_without_prune_and_warns(
    capsys: pytest.CaptureFixture[str], main_checkout: Path, tmp_path: Path
) -> None:
    assert link(capsys, main_checkout)[0] == 0
    linked = add_worktree(main_checkout, tmp_path / "linked", "feature")
    assert link(capsys, linked)[0] == 0
    moved = tmp_path / "moved"
    main_checkout.rename(moved)
    names = sorted(path.name for path in (moved / ".git/worktrees").iterdir())
    code, status = run(capsys, moved, "canonical", "status")
    assert code == 0 and status["data"]["catalog"]["state"] == "repair"
    assert status["data"]["catalog"]["next_step"] == "spec-dock canonical link"
    code, result = link(capsys, moved)
    assert code == 0, result
    assert ("git.worktree.repair", "succeeded") in effects(result)
    assert [item["code"] for item in result["warnings"]].count("CANONICAL_MAIN_MOVED") == 1
    assert sorted(path.name for path in (moved / ".git/worktrees").iterdir()) == names
    assert git(moved / "spec-dock/.canonical", "rev-parse", "--show-toplevel") == str(moved / "spec-dock/.canonical")
    # git also reconnected the linked worktree that did not move; its absolute link is re-pointed there
    code, result = link(capsys, linked)
    assert code == 0, result
    assert str((linked / "spec-dock/initiatives").readlink()) == str(moved / "spec-dock/.canonical")


def test_a_mounted_checkout_in_a_container_stops_before_repair(
    capsys: pytest.CaptureFixture[str], main_checkout: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert link(capsys, main_checkout)[0] == 0
    moved = tmp_path / "mounted"
    main_checkout.rename(moved)
    inject(monkeypatch, container=True)
    before = tree_digest(moved / ".git/worktrees"), tree_digest(moved / "spec-dock/.canonical")
    code, result = link(capsys, moved)
    assert code == 3 and result["error"]["code"] == "CANONICAL_FOREIGN_CHECKOUT" and result["effects"] == []
    assert (tree_digest(moved / ".git/worktrees"), tree_digest(moved / "spec-dock/.canonical")) == before
    code, status = run(capsys, moved, "canonical", "status")
    assert code == 0 and status["data"]["catalog"]["state"] == "foreign"


def test_checking_out_a_pre_migration_commit_and_back(
    capsys: pytest.CaptureFixture[str], main_checkout: Path, tmp_path: Path
) -> None:
    assert link(capsys, main_checkout)[0] == 0
    linked = add_worktree(main_checkout, tmp_path / "linked", "feature")
    assert link(capsys, linked)[0] == 0
    git(main_checkout, "checkout", "-q", "-b", "old-specs")
    (main_checkout / "spec-dock/initiatives").unlink()
    (main_checkout / "spec-dock/initiatives/init-00001-old").mkdir(parents=True)
    (main_checkout / "spec-dock/initiatives/init-00001-old/plan.md").write_text("old\n", encoding="utf-8")
    git(main_checkout, "add", "-A")
    git(main_checkout, "commit", "-qm", "pre-migration specs")
    code, status = run(capsys, linked, "canonical", "status")
    assert code == 0
    (occupied,) = [item for item in status["data"]["link"]["links"] if item["state"] == "occupied"]
    assert occupied["path"] == str(main_checkout / "spec-dock/initiatives")
    assert "switch back first" in status["data"]["link"]["next_step"]
    git(main_checkout, "checkout", "-q", "main")
    assert not os.path.lexists(main_checkout / "spec-dock/initiatives")
    code, result = link(capsys, main_checkout)
    assert code == 0, result
    assert str((main_checkout / "spec-dock/initiatives").readlink()) == ".canonical"


def test_an_old_git_stops_before_writing(
    capsys: pytest.CaptureFixture[str], remote: Path, main_checkout: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    inject(monkeypatch, git_version=(2, 37, 0))
    before = _digests(main_checkout, remote)
    code, result = link(capsys, main_checkout)
    assert code == 3 and result["error"]["code"] == "CANONICAL_GIT_TOO_OLD" and result["effects"] == []
    assert "2.38" in result["recovery"]["instructions"][0]
    assert _digests(main_checkout, remote) == before


def test_specs_on_the_default_branch_without_a_canonical_stop_as_not_migrated(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    remote = bare_remote(tmp_path / "legacy.git", files={"spec-dock/initiatives/init-00001-plan/plan.md": b"legacy\n"})
    checkout = clone(remote, tmp_path / "legacy")
    git(checkout, "rm", "-rq", "spec-dock/initiatives")
    git(checkout, "commit", "-qm", "local removal only")
    before = _digests(checkout, remote)
    code, result = link(capsys, checkout)
    assert code == 3 and result["error"]["code"] == "CANONICAL_NOT_MIGRATED" and result["effects"] == []
    assert "scripts/migrate-to-canonical/README.md" in result["recovery"]["instructions"][0]
    assert _digests(checkout, remote) == before


def test_an_unreachable_origin_stops_before_writing(
    capsys: pytest.CaptureFixture[str], main_checkout: Path, tmp_path: Path
) -> None:
    git(main_checkout, "remote", "set-url", "origin", str(tmp_path / "missing.git"))
    before = tree_digest(main_checkout)
    code, result = link(capsys, main_checkout)
    assert code == 5 and result["error"]["code"] == "GITHUB_UNAVAILABLE" and result["effects"] == []
    assert tree_digest(main_checkout) == before


def test_a_concurrent_first_creation_uses_the_canonical_pushed_first(
    capsys: pytest.CaptureFixture[str],
    remote: Path,
    main_checkout: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    other = clone(remote, tmp_path / "other")
    git(other, "config", "user.name", "Other PC")
    assert link(capsys, main_checkout)[0] == 0
    first = git(remote, "rev-parse", "refs/heads/spec-dock/canonical")
    monkeypatch.setattr(canonical_git, "remote_canonical", lambda *args, **kwargs: "absent")
    code, result = link(capsys, other)
    assert code == 0, result
    assert ("canonical.remote.create", "unchanged") in effects(result)
    assert result["data"]["result"]["source"] == "remote"
    assert git(remote, "rev-parse", "refs/heads/spec-dock/canonical") == first
    assert git(other / "spec-dock/.canonical", "rev-parse", "HEAD") == first


def test_an_unpushed_initial_local_branch_is_pushed_on_the_next_link(
    capsys: pytest.CaptureFixture[str], remote: Path, main_checkout: Path
) -> None:
    oid = canonical_git.create_initial_commit(main_checkout)
    git(main_checkout, "branch", "spec-dock/canonical", oid)
    code, result = link(capsys, main_checkout)
    assert code == 0, result
    assert ("canonical.remote.create", "succeeded") in effects(result)
    assert git(remote, "rev-parse", "refs/heads/spec-dock/canonical") == oid
    assert git(main_checkout / "spec-dock/.canonical", "rev-parse", "HEAD") == oid


def test_a_local_branch_with_content_and_no_remote_is_used_without_push(
    capsys: pytest.CaptureFixture[str], remote: Path, main_checkout: Path
) -> None:
    assert link(capsys, main_checkout)[0] == 0
    catalog = main_checkout / "spec-dock/.canonical"
    (catalog / "init-00001-plan").mkdir()
    (catalog / "init-00001-plan/plan.md").write_text("content\n", encoding="utf-8")
    git(catalog, "add", "-A")
    git(catalog, "commit", "-qm", "save")
    local = git(catalog, "rev-parse", "HEAD")
    git(remote, "update-ref", "-d", "refs/heads/spec-dock/canonical")
    git(main_checkout, "worktree", "unlock", str(catalog))
    git(main_checkout, "worktree", "remove", "--force", str(catalog))
    code, result = link(capsys, main_checkout)
    assert code == 0, result
    assert "canonical.remote.create" not in [kind for kind, _status in effects(result)]
    assert [item["code"] for item in result["warnings"]].count("CANONICAL_REMOTE_MISSING") == 1
    assert git(remote, "for-each-ref", "refs/heads/spec-dock") == ""
    assert git(catalog, "rev-parse", "HEAD") == local


def test_a_single_branch_clone_learns_to_fetch_the_canonical(
    capsys: pytest.CaptureFixture[str], remote: Path, main_checkout: Path, tmp_path: Path
) -> None:
    assert link(capsys, main_checkout)[0] == 0
    single = clone(remote, tmp_path / "single", "--single-branch", "--branch", "main")
    code, result = link(capsys, single)
    assert code == 0, result
    assert ("git.remote.set-branches", "succeeded") in effects(result)
    assert (
        git(single / "spec-dock/.canonical", "rev-parse", "--abbrev-ref", "@{upstream}") == "origin/spec-dock/canonical"
    )


def _hostile_hooks(checkout: Path) -> None:
    hooks = checkout.parent / f"{checkout.name}-hooks"
    hooks.mkdir()
    for name in ("post-checkout", "pre-push", "pre-commit", "post-merge", "reference-transaction"):
        hook = hooks / name
        hook.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        hook.chmod(0o755)
    git(checkout, "config", "core.hooksPath", str(hooks))
    git(checkout, "config", "commit.gpgSign", "true")
    git(checkout, "config", "gpg.program", "/nonexistent-gpg")


def test_failing_hooks_and_signing_do_not_stop_creation_or_import(
    capsys: pytest.CaptureFixture[str], remote: Path, main_checkout: Path, tmp_path: Path
) -> None:
    _hostile_hooks(main_checkout)
    assert link(capsys, main_checkout)[0] == 0
    other = clone(remote, tmp_path / "other")
    _hostile_hooks(other)
    code, result = link(capsys, other)
    assert code == 0, result


def test_a_failure_after_writing_is_partial_with_the_applied_effects(
    capsys: pytest.CaptureFixture[str], main_checkout: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.application import canonical_link

    def refuse(*args: object, **kwargs: object) -> None:
        raise OSError(5, "Input/output error")

    monkeypatch.setattr(canonical_link, "place_link", refuse)
    code, result = link(capsys, main_checkout)
    assert code == 6 and result["status"] == "partial", result
    statuses = dict(effects(result))
    assert statuses["git.worktree.add"] == "succeeded" and statuses["git.worktree.lock"] == "succeeded"
    assert statuses["canonical.link"] == "failed"
    assert result["recovery"]["instructions"][0].startswith("Run spec-dock canonical link again")
    monkeypatch.undo()
    isolate_user_state(monkeypatch, main_checkout.parent)
    inject(monkeypatch)
    code, result = link(capsys, main_checkout)
    assert code == 0 and ("canonical.link", "succeeded") in effects(result)


def test_schema_three_stops_as_not_migrated(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    remote = bare_remote(
        tmp_path / "v3.git", declaration={"schema_version": 3, "writer_protocol": "specdock.worktree-writer/v1"}
    )
    checkout = clone(remote, tmp_path / "v3")
    for leaf in ("link", "status"):
        code, result = run(capsys, checkout, "canonical", leaf)
        assert code == 3 and result["error"]["code"] == "CANONICAL_NOT_MIGRATED"
    assert not os.path.lexists(checkout / "spec-dock/.canonical")


def test_a_denied_write_after_access_allowed_it_names_the_sandbox(
    capsys: pytest.CaptureFixture[str], main_checkout: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.application import canonical_link

    def refuse(*args: object, **kwargs: object) -> None:
        raise PermissionError(1, "Operation not permitted")

    monkeypatch.setattr(canonical_link, "place_link", refuse)
    code, result = link(capsys, main_checkout)
    assert code == 6 and result["error"]["code"] == "CANONICAL_SANDBOX_DENIED"
    assert "normal terminal" in result["recovery"]["instructions"][0]


def test_a_start_lock_held_elsewhere_stops_canonical_link(
    capsys: pytest.CaptureFixture[str], main_checkout: Path
) -> None:
    from spec_dock.runtime.infra.start_lock import StartLock

    with StartLock(main_checkout / ".git", timeout=0):
        code, result = link(capsys, main_checkout)
    assert code == 6 and result["status"] == "partial", result
    assert result["error"]["code"] == "START_LOCK_BUSY"
    assert ("git.worktree.add", "not_attempted") in effects(result)


def test_a_complete_link_does_not_wait_for_the_start_lock(
    capsys: pytest.CaptureFixture[str], main_checkout: Path
) -> None:
    from spec_dock.runtime.infra.start_lock import StartLock

    assert link(capsys, main_checkout)[0] == 0
    with StartLock(main_checkout / ".git", timeout=0):
        code, result = link(capsys, main_checkout)
    assert code == 0 and result["status"] == "unchanged"


def test_running_inside_the_catalog_names_the_checkout_root(
    capsys: pytest.CaptureFixture[str], main_checkout: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert link(capsys, main_checkout)[0] == 0
    scope = main_checkout / "spec-dock/initiatives/init-00001-plan"
    scope.mkdir()
    monkeypatch.chdir(scope)
    for argv in (["canonical", "status"], ["scope", "list"]):
        code = main([*argv, "--json"])
        result = json.loads(capsys.readouterr().out)
        assert code == 3 and result["error"]["code"] == "CANONICAL_INSIDE_CATALOG", result
        assert "--project" in result["recovery"]["instructions"][0]


def test_a_schema_three_checkout_without_a_declaration_still_fails_as_before(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plain = tmp_path / "plain"
    plain.mkdir()
    git(plain, "init", "-q", "-b", "main")
    monkeypatch.chdir(plain)
    code = main(["scope", "list", "--json"])
    result = json.loads(capsys.readouterr().out)
    assert code == 3 and result["error"]["code"] == "PRECONDITION_FAILED"


def test_a_registration_written_through_an_alias_path_is_not_repaired(
    capsys: pytest.CaptureFixture[str], main_checkout: Path, tmp_path: Path
) -> None:
    assert link(capsys, main_checkout)[0] == 0
    alias = tmp_path / "alias"
    alias.symlink_to(main_checkout, target_is_directory=True)
    admin = canonical_git.read_gitdir(main_checkout / "spec-dock/.canonical")
    assert admin is not None
    (admin / "gitdir").write_text(str(alias / "spec-dock/.canonical/.git") + "\n", encoding="utf-8")
    (main_checkout / "spec-dock/.canonical/.git").write_text(
        f"gitdir: {alias}/.git/worktrees/{admin.name}\n", encoding="utf-8"
    )
    before = tree_digest(main_checkout / ".git/worktrees")
    code, result = link(capsys, main_checkout)
    assert code == 0 and result["status"] == "unchanged", result
    assert "git.worktree.repair" not in [kind for kind, _status in effects(result)]
    assert tree_digest(main_checkout / ".git/worktrees") == before


def test_a_registration_pointing_at_another_existing_directory_stops(
    capsys: pytest.CaptureFixture[str], main_checkout: Path, tmp_path: Path
) -> None:
    assert link(capsys, main_checkout)[0] == 0
    copy = tmp_path / "copy"
    copy.mkdir()
    admin = canonical_git.read_gitdir(main_checkout / "spec-dock/.canonical")
    assert admin is not None
    (admin / "gitdir").write_text(str(copy / ".git") + "\n", encoding="utf-8")
    before = tree_digest(main_checkout / ".git/worktrees")
    code, result = link(capsys, main_checkout)
    assert code == 3 and result["error"]["code"] == "CANONICAL_PATH_OCCUPIED" and result["effects"] == []
    assert tree_digest(main_checkout / ".git/worktrees") == before


def test_a_catalog_on_another_branch_names_the_switch_back(
    capsys: pytest.CaptureFixture[str], main_checkout: Path
) -> None:
    assert link(capsys, main_checkout)[0] == 0
    catalog = main_checkout / "spec-dock/.canonical"
    git(catalog, "switch", "-q", "-c", "scratch")
    code, result = link(capsys, main_checkout)
    assert code == 3 and result["error"]["code"] == "CANONICAL_PATH_OCCUPIED"
    assert "switch spec-dock/canonical" in result["recovery"]["instructions"][0]
    code, status = run(capsys, main_checkout, "canonical", "status")
    assert "switch spec-dock/canonical" in status["data"]["catalog"]["next_step"]


def test_a_single_branch_clone_of_a_new_repository_creates_the_canonical(
    capsys: pytest.CaptureFixture[str], remote: Path, tmp_path: Path
) -> None:
    single = clone(remote, tmp_path / "single-new", "--single-branch", "--branch", "main")
    code, result = link(capsys, single)
    assert code == 0, result
    assert ("git.remote.set-branches", "succeeded") in effects(result)
    assert (
        git(single / "spec-dock/.canonical", "rev-parse", "--abbrev-ref", "@{upstream}") == "origin/spec-dock/canonical"
    )
    fetch = git(single, "config", "--get-all", "remote.origin.fetch").splitlines()
    assert fetch.count("+refs/heads/spec-dock/canonical:refs/remotes/origin/spec-dock/canonical") == 1


def test_a_main_checkout_on_a_schema_three_commit_keeps_its_legacy_tree(
    capsys: pytest.CaptureFixture[str], main_checkout: Path, tmp_path: Path
) -> None:
    linked = add_worktree(main_checkout, tmp_path / "linked", "feature")
    git(main_checkout, "checkout", "-q", "-b", "legacy")
    (main_checkout / "spec-dock/workspace.json").write_text(
        '{"schema_version":3,"writer_protocol":"specdock.worktree-writer/v1"}\n', encoding="utf-8"
    )
    scope = main_checkout / "spec-dock/initiatives/init-00001-fixture"
    scope.mkdir(parents=True)
    metadata = {
        "schema_version": 3,
        "id": "init-00001",
        "type": "initiative",
        "title": "Fixture",
        "slug": "fixture",
        "parent_id": None,
        "initiative_id": None,
        "epic_id": None,
        "backend": "github",
        "github": {"issue_number": 1, "repo_owner": "example", "repo_name": "repo"},
        "lifecycle": None,
        "revision": 0,
        "depends_on": [],
        "created_at": "2026-09-30T00:00:00Z",
        "updated_at": "2026-09-30T00:00:00Z",
    }
    (scope / ".meta.json").write_text(json.dumps(metadata) + "\n", encoding="utf-8")
    for name in ("requirement.md", "design.md", "plan.md", "report.md"):
        (scope / name).write_text("# Fixture\n", encoding="utf-8")
    git(main_checkout, "add", "-A")
    git(main_checkout, "commit", "-qm", "legacy specs")
    legacy_before = tree_digest(main_checkout / "spec-dock/initiatives")
    code, result = link(capsys, linked)
    assert code == 0, result
    assert [item["code"] for item in result["warnings"]].count("CANONICAL_MAIN_NOT_MIGRATED") == 1
    assert (main_checkout / "spec-dock/.canonical").is_dir() and (linked / "spec-dock/initiatives").is_symlink()
    assert tree_digest(main_checkout / "spec-dock/initiatives") == legacy_before
    code, status = run(capsys, linked, "canonical", "status")
    assert [item["code"] for item in status["warnings"] if item["details"].get("item") == "link"] == [
        "CANONICAL_MAIN_NOT_MIGRATED"
    ]
    assert git(main_checkout, "status", "--porcelain") == ""
    code, listed = run(capsys, main_checkout, "scope", "list")
    assert code == 0 and [item["id"] for item in listed["data"]["result"]["items"]] == ["init-00001"]
