"""The accepted Start planning API decides entirely from memory observations."""

from pathlib import Path

from spec_dock.runtime.application.contracts import GitWorktreeRecord
from spec_dock.runtime.application.project_context import ProjectContext
from spec_dock.runtime.application.scope_query import ScopeView
from spec_dock.runtime.application.start_snapshot import LocalInput
from spec_dock.runtime.application.worktree_observation import SelectionObservation, WorktreeSelection
from spec_dock.runtime.domain.dependency_vnext import ReadinessResult
from spec_dock.runtime.domain.lifecycle import GithubBackend, StatusObservation
from spec_dock.runtime.domain.work_target import PhysicalIdentity


def test_start_plan_freezes_target_fixed_commit_and_exact_input_hashes() -> None:
    from spec_dock.runtime.application.start_plan import (
        StartLiveObservations,
        StartLocalSnapshot,
        StartRequest,
        plan_start,
    )

    root = Path("/fixture")
    clone = PhysicalIdentity("posix", "1", "2")
    worktree = PhysicalIdentity("posix", "1", "3")
    context = ProjectContext(root, root / ".git", clone, worktree, "a" * 40, "main", {})
    target = ScopeView(
        "init-00001",
        "initiative",
        "Fixture",
        None,
        GithubBackend(1, "example", "repo"),
        root / "spec-dock/initiatives/init-00001-fixture",
        0,
        StatusObservation("unknown", "github", "unknown", None, None, False),
        "gh:example/repo#1",
    )
    selection = SelectionObservation("empty", None, None, "main")
    inventory = (WorktreeSelection(str(root), selection, (), worktree, GitWorktreeRecord(root, "a" * 40, "main")),)
    snapshot = StartLocalSnapshot(
        target, (LocalInput("spec-dock/workspace.json", b"{}", (1, 4)),), selection, inventory
    )
    request = StartRequest("init-00001", None, "HEAD", False, None, None)
    observed = StartLiveObservations(
        "init-00001-fixture", "a" * 40, True, ReadinessResult("init-00001", True, (), False)
    )
    plan = plan_start(request, context, snapshot, observed)
    assert plan.target_id == "init-00001"
    assert plan.github_ref == "gh:example/repo#1"
    assert plan.branch == "init-00001-fixture"
    assert plan.resolved_tip == "a" * 40
    assert plan.create_branch is True
    assert plan.expected_local_hashes == (
        ("spec-dock/workspace.json", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"),
    )
    assert plan.old_selection_handle is None
    assert plan.switch_allowed is False
    assert plan.selection.action == "publish"
