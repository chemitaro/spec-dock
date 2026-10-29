"""I-4 follow-ups in iss-00432: canonical branch failures are observed again as the legacy branch_operations do."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.application import canonical_branches
from spec_dock.runtime.infra.git_process import GitProcessError, run_git
from tests.support.canonical_repo import git
from tests.support.canonical_scopes import CanonicalWorld

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, title="計画")
    return world


def _failing(monkeypatch: pytest.MonkeyPatch, verb: str, *, apply: bool, uncertain: bool, after=None) -> None:
    """Make the canonical `git <verb>` mutation fail, after applying it when `apply`."""

    def run(root, *args, mutation=False, **kwargs):
        if mutation and args and args[0] == verb:
            if apply:
                run_git(root, *args, mutation=mutation, **kwargs)
            if after is not None:
                after()
            raise GitProcessError(
                ("git", *args), b"injected failure", 1 if not uncertain else None, uncertain=uncertain
            )
        return run_git(root, *args, mutation=mutation, **kwargs)

    monkeypatch.setattr(canonical_branches, "run_git", run)


def test_a_create_failure_that_made_the_branch_at_the_base_is_succeeded_partial(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    _failing(monkeypatch, "branch", apply=True, uncertain=True)
    code, payload = world.run("branch", "create", "init-1", "--base", "HEAD", "--yes")
    assert (code, payload["status"]) == (6, "partial")
    assert payload["effects"] == [{"kind": "git.branch.create", "status": "succeeded", "target": "init-00001"}]
    assert payload["data"]["result"]["created"] is True


def test_a_certain_create_failure_without_a_ref_is_failed(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    _failing(monkeypatch, "branch", apply=False, uncertain=False)
    code, payload = world.run("branch", "create", "init-00001", "--base", "HEAD", "--yes")
    assert (code, payload["status"]) == (5, "failed")
    assert payload["effects"][0]["status"] == "failed"


def test_a_failed_reread_after_a_create_failure_keeps_the_effect_unknown(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    _failing(monkeypatch, "branch", apply=False, uncertain=False)
    monkeypatch.setattr(canonical_branches, "_branch_tip", _raise_after_first_call())
    code, payload = world.run("branch", "create", "init-00001", "--base", "HEAD", "--yes")
    assert (code, payload["status"]) == (6, "partial")
    assert payload["effects"][0]["status"] == "unknown"


def _raise_after_first_call():
    calls = {"count": 0}
    original = canonical_branches._branch_tip

    def tip(context, name, timeout):
        calls["count"] += 1
        if calls["count"] > 1:
            raise OSError("cannot read the ref")
        return original(context, name, timeout)

    return tip


def test_a_switch_failure_that_left_the_old_branch_clean_is_failed(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    git(world.main, "branch", "init-00001")
    world.select("init-00001", 1)
    _failing(monkeypatch, "checkout", apply=False, uncertain=False)
    code, payload = world.run("branch", "switch", "init-00001", "--yes")
    assert (code, payload["status"]) == (5, "failed")
    assert payload["effects"] == [{"kind": "git.checkout", "status": "failed", "target": "init-00001"}]


def test_a_switch_failure_that_moved_to_a_dirty_target_reports_the_verification(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    git(world.main, "branch", "init-00001")
    world.select("init-00001", 1)
    _failing(
        monkeypatch,
        "checkout",
        apply=True,
        uncertain=True,
        after=lambda: (world.main / "README.extra").write_text("dirty\n", encoding="utf-8"),
    )
    code, payload = world.run("branch", "switch", "init-00001", "--yes")
    assert (code, payload["status"]) == (6, "partial")
    assert payload["effects"][0]["status"] == "succeeded"
    assert "dirty" in payload["error"]["details"]["verification_error"]


def test_a_switch_that_leaves_a_dirty_worktree_is_a_verification_failure(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    git(world.main, "branch", "init-00001")
    world.select("init-00001", 1)

    def run(root, *args, mutation=False, **kwargs):
        output = run_git(root, *args, mutation=mutation, **kwargs)
        if mutation and args and args[0] == "checkout":
            (world.main / "README.extra").write_text("dirty\n", encoding="utf-8")
        return output

    monkeypatch.setattr(canonical_branches, "run_git", run)
    code, payload = world.run("branch", "switch", "init-00001", "--yes")
    assert (code, payload["status"], payload["error"]["code"]) == (6, "partial", "CHECKOUT_VERIFICATION_FAILED")


def test_a_worktree_whose_only_ignored_entry_is_its_link_is_removed_without_discard(world: CanonicalWorld) -> None:
    linked = world.worktree("wt")
    code, payload = world.run("worktree", "remove", str(linked), "--yes")
    assert code == 0, payload
    assert not linked.exists() and (world.catalog / "00000-00999/init-00001/requirement.md").is_file()


def test_other_ignored_content_still_needs_discard(world: CanonicalWorld) -> None:
    linked = world.worktree("wt")
    exclude = world.main / ".git/info/exclude"
    exclude.write_text(exclude.read_text(encoding="utf-8") + "*.junk\n", encoding="utf-8")
    (linked / "notes.junk").write_text("keep me\n", encoding="utf-8")
    code, payload = world.run("worktree", "remove", str(linked), "--yes")
    assert (code, payload["error"]["code"]) == (3, "PRECONDITION_FAILED")
    assert "--discard-ignored" in payload["error"]["message"] and (linked / "notes.junk").is_file()


def test_remove_runs_the_legacy_step_on_the_checked_record(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.application import canonical_worktrees
    from spec_dock.runtime.infra.work_target_store import WorkTargetStore

    linked = world.worktree("wt")
    world.select("init-00001", 1)
    original = canonical_worktrees._remove_captured_worktree

    def changed_first(namespace, context, entry, captured, held):
        with WorkTargetStore(context.root) as store:
            current = store.read()
            assert current.handle is not None
            store.remove_observed(current.handle)  # the selection changes after the expectation was checked
        return original(namespace, context, entry, captured, held)

    monkeypatch.setattr(canonical_worktrees, "_remove_captured_worktree", changed_first)
    code, payload = world.run("worktree", "remove", str(linked), "--yes", "--expect-current", "init-1")
    assert code != 0 and payload["status"] == "failed", payload
    assert linked.exists()


def test_create_reads_the_record_again_before_the_legacy_step(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.application import canonical_worktrees
    from spec_dock.runtime.infra.work_target_store import WorkTargetStore

    world.select("init-00001", 1)
    original = canonical_worktrees.check_canonical_expectation

    def then_change(context, namespace, **kwargs):
        warnings = original(context, namespace, **kwargs)
        with WorkTargetStore(context.root) as store:
            current = store.read()
            assert current.handle is not None
            store.remove_observed(current.handle)
        return warnings

    monkeypatch.setattr(canonical_worktrees, "check_canonical_expectation", then_change)
    before = git(world.main, "worktree", "list", "--porcelain")
    code, payload = world.run(
        "worktree", "create", "new-wt", "--base", "HEAD", "--yes", "--expect-current", "init-00001"
    )
    assert (code, payload["error"]["code"]) == (3, "PRECONDITION_FAILED")
    assert "changed after --expect-current" in payload["error"]["message"]
    assert git(world.main, "worktree", "list", "--porcelain") == before


def test_bootstrap_runs_the_legacy_step_on_the_checked_record(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.application import canonical_worktrees
    from spec_dock.runtime.infra.work_target_store import WorkTargetStore

    linked = world.worktree("wt")
    (linked / "Makefile").write_text("init:\n\t@true\n", encoding="utf-8")
    world.select("init-00001", 1)
    code, payload = world.run("worktree", "bootstrap", str(linked), "--dry-run", "--expect-current", "init-1")
    assert (code, payload["status"]) == (0, "planned"), payload
    original = canonical_worktrees._bootstrap_captured_target

    def changed_first(namespace, context, entry, captured, held):
        with WorkTargetStore(context.root) as store:
            current = store.read()
            assert current.handle is not None
            store.remove_observed(current.handle)  # the selection changes after the expectation was checked
        return original(namespace, context, entry, captured, held)

    monkeypatch.setattr(canonical_worktrees, "_bootstrap_captured_target", changed_first)
    code, payload = world.run("worktree", "bootstrap", str(linked), "--dry-run", "--expect-current", "init-00001")
    assert (code, payload["status"]) == (3, "failed"), payload
    assert "selection changed" in payload["error"]["message"] and payload["effects"] == []
