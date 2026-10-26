"""canonical `branch show/create/switch`: names from the GitHub slug marker, no specs at the base (iss-00431)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.support.canonical_repo import add_worktree, git
from tests.support.canonical_scopes import CanonicalWorld

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "plan", title="日本語の計画")
    return world


def _branch_with_specs(world: CanonicalWorld) -> str:
    """A pre-migration branch whose tree tracks spec-dock/initiatives."""
    old = add_worktree(world.main, world.tmp_path / "old", "legacy-specs")
    (old / "spec-dock/initiatives").unlink(missing_ok=True)
    (old / "spec-dock/initiatives/init-00001-plan").mkdir(parents=True)
    (old / "spec-dock/initiatives/init-00001-plan/requirement.md").write_text("# r\n", encoding="utf-8")
    git(old, "add", "-f", "spec-dock/initiatives")
    git(old, "commit", "-qm", "specs")
    git(world.main, "worktree", "remove", "--force", str(old))
    return git(world.main, "rev-parse", "legacy-specs")


def test_branch_show_uses_the_id_and_github_slug(world: CanonicalWorld) -> None:
    code, payload = world.run("branch", "show", "init-00001")
    assert code == 0, payload
    assert payload["data"]["result"]["name"] == "init-00001-plan"
    assert payload["data"]["result"]["tip"] is None


def test_branch_create_makes_the_branch_at_the_base(world: CanonicalWorld) -> None:
    head = git(world.main, "rev-parse", "HEAD")
    code, payload = world.run("branch", "create", "init-00001", "--base", "HEAD", "--yes")
    assert code == 0, payload
    assert payload["data"]["result"]["created"] is True
    assert git(world.main, "rev-parse", "init-00001-plan") == head


def test_branch_create_refuses_a_base_with_specs(world: CanonicalWorld) -> None:
    _branch_with_specs(world)
    code, payload = world.run("branch", "create", "init-00001", "--base", "legacy-specs", "--yes")
    assert (code, payload["error"]["code"]) == (3, "CANONICAL_BASE_HAS_SPECS")
    assert git(world.main, "rev-parse", "--verify", "--quiet", "init-00001-plan", check=False) == ""


def test_branch_switch_checks_out_and_keeps_the_selection(world: CanonicalWorld) -> None:
    git(world.main, "branch", "init-00001-plan")
    world.select("init-00001", 1)
    code, payload = world.run("branch", "switch", "init-00001", "--yes")
    assert code == 0, payload
    assert payload["data"]["result"]["switched"] is True
    assert git(world.main, "branch", "--show-current") == "init-00001-plan"
    assert world.run("active", "show")[1]["data"]["selection"]["scope_id"] == "init-00001"


def test_branch_switch_refuses_a_branch_with_specs(world: CanonicalWorld) -> None:
    _branch_with_specs(world)
    before = git(world.main, "rev-parse", "HEAD"), git(world.main, "branch", "--show-current")
    code, payload = world.run("branch", "switch", "init-00001", "--name", "legacy-specs", "--yes")
    assert (code, payload["error"]["code"]) == (3, "CANONICAL_BASE_HAS_SPECS")
    assert payload["recovery"]["instructions"]
    assert (git(world.main, "rev-parse", "HEAD"), git(world.main, "branch", "--show-current")) == before
    assert (world.main / "spec-dock/initiatives").is_symlink()


def test_a_failed_check_after_creating_the_branch_is_partial(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.application import canonical_branches

    real = canonical_branches._branch_tip
    calls: list[str] = []

    def moved(context: object, name: str, timeout: float) -> str | None:
        calls.append(name)
        tip = real(context, name, timeout)  # type: ignore[arg-type]
        return "0" * 40 if tip is not None else None

    monkeypatch.setattr(canonical_branches, "_branch_tip", moved)
    code, payload = world.run("branch", "create", "init-00001", "--base", "HEAD", "--yes")
    assert (code, payload["status"]) == (6, "partial"), payload
    assert [(item["kind"], item["status"]) for item in payload["effects"]] == [("git.branch.create", "succeeded")]
    assert payload["error"]["code"] == "BRANCH_VERIFICATION_FAILED"


def test_a_failed_check_after_switching_is_partial(world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    from spec_dock.runtime.application import canonical_branches

    git(world.main, "branch", "init-00001-plan")
    real = canonical_branches._verify_selection
    calls: list[int] = []

    def changed_after_checkout(context: object, expected: object) -> None:
        calls.append(1)
        if len(calls) > 1:
            raise ValueError("direct selection changed during the Git branch operation")
        real(context, expected)  # type: ignore[arg-type]

    monkeypatch.setattr(canonical_branches, "_verify_selection", changed_after_checkout)
    code, payload = world.run("branch", "switch", "init-00001", "--yes")
    assert (code, payload["status"]) == (6, "partial"), payload
    assert [(item["kind"], item["status"]) for item in payload["effects"]] == [("git.checkout", "succeeded")]
    assert payload["error"]["code"] == "CHECKOUT_VERIFICATION_FAILED"
