"""Local Scope creation reserves IDs and rejects invalid ancestry offline."""

from __future__ import annotations

import json
from multiprocessing import Process, Queue
from pathlib import Path
import subprocess
import sys

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.create_local_scope import (  # noqa: E402
    AncestorState,
    create_local_scope,
    plan_local_scope_create,
)
from spec_dock_runtime.domain.lifecycle import GithubBackend  # noqa: E402
from spec_dock_runtime.domain.registry import LocalIdRegistry, reserve_local_id  # noqa: E402
from spec_dock_runtime.infra.control_store import ControlState, WorktreeRegistration, store_control  # noqa: E402
from spec_dock_runtime.infra.git_cli import git_common_directory  # noqa: E402
from spec_dock_runtime.infra.github_status_cache import cached_github_ancestor_open  # noqa: E402
from spec_dock_runtime.infra.json_store import atomic_write_json  # noqa: E402
from spec_dock_runtime.infra.operation_journal import JournalStore  # noqa: E402
from spec_dock_runtime.infra.registry_store import RegistryStore  # noqa: E402
from tests.cli_runtime import harness  # noqa: E402


@pytest.mark.parametrize(
    ("kind", "expected"),
    [
        ("initiative", "init-local-00001"),
        ("epic", "epic-local-00001"),
        ("issue", "iss-local-00001"),
    ],
)
def test_each_kind_has_its_own_monotone_local_id_space(kind: str, expected: str) -> None:
    state = LocalIdRegistry.empty()
    next_state, allocated = reserve_local_id(state, kind=kind, observed_ids=())
    assert allocated == expected
    assert allocated in next_state.reserved


def test_reservation_gap_is_never_reused_after_failed_create() -> None:
    state = LocalIdRegistry.empty()
    state, first = reserve_local_id(state, kind="issue", observed_ids=("iss-local-00007",))
    assert first == "iss-local-00008"
    state, second = reserve_local_id(state, kind="issue", observed_ids=("iss-local-00007",))
    assert second == "iss-local-00009"


def test_allocator_rejects_corrupt_persisted_high_water() -> None:
    with pytest.raises(ValueError, match="registry"):
        LocalIdRegistry(1, (0, -1, 0), frozenset())
    with pytest.raises(ValueError, match="registry"):
        LocalIdRegistry(1, (0, 0, 0), frozenset({"iss-local-00001"}))


def test_parent_kind_is_explicit_and_local_ancestors_must_be_open() -> None:
    with pytest.raises(ValueError, match="parent"):
        plan_local_scope_create(kind="epic", title="Plan", parent=None, ancestors=())
    parent = AncestorState("init-local-00001", "initiative", "local", "open", False)
    plan = plan_local_scope_create(kind="epic", title="Plan", parent=parent, ancestors=(parent,))
    assert plan.kind == "epic"
    assert plan.parent_id == parent.id
    assert not plan.needs_network
    with pytest.raises(ValueError, match="parent kind"):
        plan_local_scope_create(kind="issue", title="Build", parent=parent, ancestors=(parent,))
    with pytest.raises(ValueError, match="terminal"):
        plan_local_scope_create(
            kind="epic",
            title="Plan",
            parent=AncestorState(parent.id, parent.kind, "local", "completed", False),
            ancestors=(),
        )


def test_github_ancestor_requires_saved_open_cache_and_warns_stale() -> None:
    github_parent = AncestorState("init-00001", "initiative", "github", "open", True)
    plan = plan_local_scope_create(kind="epic", title="Plan", parent=github_parent, ancestors=())
    assert plan.warnings == ("ancestor status is from a stale GitHub cache",)
    with pytest.raises(ValueError, match="stale status"):
        plan_local_scope_create(
            kind="epic",
            title="Plan",
            parent=AncestorState("init-00001", "initiative", "github", "open", False),
            ancestors=(),
        )
    assert not plan.needs_network
    for state in ("unknown", "completed", "not-planned"):
        with pytest.raises(ValueError, match="ancestor"):
            plan_local_scope_create(
                kind="epic",
                title="Plan",
                parent=AncestorState("init-00001", "initiative", "github", state, True),
                ancestors=(),
            )


def test_issue_requires_a_matching_open_initiative_ancestor() -> None:
    initiative = AncestorState("init-local-00001", "initiative", "local", "open", False)
    epic = AncestorState("epic-local-00002", "epic", "local", "open", False, initiative.id)
    with pytest.raises(ValueError, match="ancestor"):
        plan_local_scope_create(kind="issue", title="Build", parent=epic, ancestors=())
    assert (
        plan_local_scope_create(kind="issue", title="Build", parent=epic, ancestors=(initiative,)).parent_id == epic.id
    )
    with pytest.raises(ValueError, match="ancestor"):
        plan_local_scope_create(
            kind="issue",
            title="Build",
            parent=epic,
            ancestors=(AncestorState("init-local-00003", "initiative", "local", "open", False),),
        )


def test_github_ancestor_requires_matching_saved_open_observation(tmp_path: Path) -> None:
    backend = GithubBackend(1, "example", "repo")
    with pytest.raises(ValueError, match="missing"):
        cached_github_ancestor_open(tmp_path, "init-00001", backend)
    path = tmp_path / ".agent" / "github-status-cache.json"
    atomic_write_json(
        path,
        {
            "schema_version": 1,
            "items": {
                "init-00001": {
                    "github_ref": "gh:example/repo#1",
                    "state": "open",
                    "observed_at": "2026-09-24T00:00:00Z",
                }
            },
        },
    )
    assert cached_github_ancestor_open(tmp_path, "init-00001", backend)
    with pytest.raises(ValueError, match="identity"):
        cached_github_ancestor_open(tmp_path, "init-00001", GithubBackend(2, "example", "repo"))


def _reserve_in_worktree(common_dir: str, repo_root: str, results: Queue[str]) -> None:
    allocated = RegistryStore(Path(common_dir)).reserve(kind="issue", repo_root=Path(repo_root), timeout=5.0)
    results.put(allocated)


def test_two_linked_worktrees_share_history_aware_monotone_reservations(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    linked = tmp_path / "linked"
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    existing = (
        repo / "spec-dock/initiatives/init-local-00001-plan/epics/epic-local-00001-plan/issues/iss-local-00007-build"
    )
    existing.mkdir(parents=True)
    (existing / ".meta.json").write_text(json.dumps({"id": "iss-local-00007"}), encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "--", "spec-dock"], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "worktree", "add", "--detach", str(linked)], check=True, capture_output=True
    )
    (existing / ".meta.json").unlink()
    (linked / existing.relative_to(repo) / ".meta.json").unlink()
    common_dir = git_common_directory(repo)
    registrations = tuple(
        WorktreeRegistration(name, str(root), 3, "specdock.writer/v1", "engine-a", True)
        for name, root in (("main", repo), ("linked", linked))
    )
    store_control(
        common_dir, ControlState(3, "specdock.writer/v1", 1, "engine-a", "ready", registrations), expected_epoch=None
    )
    results: Queue[str] = Queue()
    children = [
        Process(target=_reserve_in_worktree, args=(str(common_dir), str(root), results)) for root in (repo, linked)
    ]
    for child in children:
        child.start()
    try:
        allocated = {results.get(timeout=10) for _ in children}
    finally:
        for child in children:
            child.join(timeout=10)
            if child.is_alive():
                child.kill()
                child.join(timeout=5)
    assert allocated == {"iss-local-00008", "iss-local-00009"}
    state, identity = RegistryStore(common_dir).load()
    assert identity is not None
    assert state.high_water[2] == 9
    assert {"iss-local-00008", "iss-local-00009"} <= state.reserved


def _ready_repo(tmp_path: Path) -> tuple[dict[str, object], Path]:
    repo = tmp_path / "repo"
    assert harness.main(["init", str(repo)]) == 0
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    (repo / "readme.txt").write_text("fixture\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "--", "readme.txt"], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
        check=True,
        capture_output=True,
    )
    common_dir = git_common_directory(repo)
    registration = WorktreeRegistration("main", str(repo), 3, "specdock.writer/v1", "engine-a", True)
    store_control(
        common_dir,
        ControlState(3, "specdock.writer/v1", 1, "engine-a", "ready", (registration,)),
        expected_epoch=None,
    )
    common = {
        "repo_root": repo,
        "common_dir": common_dir,
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 1,
        "updated_at": "2026-09-24T00:00:00Z",
    }
    return common, common_dir


def test_local_initiative_epic_and_issue_scaffold_without_network(tmp_path: Path) -> None:
    common, common_dir = _ready_repo(tmp_path)
    initiative = create_local_scope(kind="initiative", title="Plan", parent=None, ancestors=(), **common)
    initiative_state = AncestorState(initiative.id, "initiative", "local", "open", False)
    epic = create_local_scope(
        kind="epic", title="Build", parent=initiative_state, ancestors=(initiative_state,), **common
    )
    epic_state = AncestorState(epic.id, "epic", "local", "open", False, initiative.id)
    issue = create_local_scope(kind="issue", title="Test", parent=epic_state, ancestors=(initiative_state,), **common)
    assert (initiative.id, epic.id, issue.id) == ("init-local-00001", "epic-local-00001", "iss-local-00001")
    for created in (initiative, epic, issue):
        payload = json.loads((created.path / ".meta.json").read_text(encoding="utf-8"))
        assert payload["id"] == created.id
        assert payload["schema_version"] == 3
        assert payload["backend"] == "local"
        assert (created.path / "requirement.md").exists()
        assert JournalStore(common_dir).load(created.operation_id).terminal_status == "succeeded"
    assert JournalStore(common_dir).pending() == ()


def test_scaffold_collision_after_id_reservation_does_not_block_other_writers(tmp_path: Path) -> None:
    common, common_dir = _ready_repo(tmp_path)
    repo = common["repo_root"]
    assert isinstance(repo, Path)
    collision = repo / "spec-dock/initiatives/init-local-00001-plan"
    collision.parent.mkdir(parents=True)
    collision.write_text("occupied\n", encoding="utf-8")
    with pytest.raises((RuntimeError, ValueError), match="Destination already exists"):
        create_local_scope(kind="initiative", title="Plan", parent=None, ancestors=(), **common)
    assert JournalStore(common_dir).pending() == ()
    second = create_local_scope(kind="initiative", title="Other", parent=None, ancestors=(), **common)
    assert second.id == "init-local-00002"


def test_parent_directory_swap_before_publication_cannot_redirect_child(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    common, common_dir = _ready_repo(tmp_path)
    initiative = create_local_scope(kind="initiative", title="Plan", parent=None, ancestors=(), **common)
    parent = AncestorState(initiative.id, "initiative", "local", "open", False)
    from spec_dock_runtime.application import create_node

    real_execute = create_node.execute_create_plan

    def swap_parent(plan: object, ports: object, **kwargs: object) -> object:
        removed = initiative.path.with_name(f"{initiative.path.name}-removed")
        initiative.path.rename(removed)
        initiative.path.mkdir()
        (initiative.path / "epics").mkdir()
        return real_execute(plan, ports, **kwargs)

    monkeypatch.setattr(create_node, "execute_create_plan", swap_parent)
    with pytest.raises((RuntimeError, ValueError), match="parent identity changed"):
        create_local_scope(kind="epic", title="Build", parent=parent, ancestors=(parent,), **common)
    assert list((initiative.path / "epics").iterdir()) == []
    assert JournalStore(common_dir).pending() == ()


def test_parent_swap_at_atomic_publish_never_writes_replacement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    common, common_dir = _ready_repo(tmp_path)
    initiative = create_local_scope(kind="initiative", title="Plan", parent=None, ancestors=(), **common)
    parent = AncestorState(initiative.id, "initiative", "local", "open", False)
    from spec_dock_runtime.application import create_node

    real_rename = create_node._rename_node_tree_no_replace_between_at

    def swap_at_rename(*args: object, **kwargs: object) -> object:
        removed = initiative.path.with_name(f"{initiative.path.name}-removed")
        initiative.path.rename(removed)
        initiative.path.mkdir()
        (initiative.path / "epics").mkdir()
        return real_rename(*args, **kwargs)

    monkeypatch.setattr(create_node, "_rename_node_tree_no_replace_between_at", swap_at_rename)
    with pytest.raises((RuntimeError, ValueError), match="parent identity changed after publication"):
        create_local_scope(kind="epic", title="Build", parent=parent, ancestors=(parent,), **common)
    assert list((initiative.path / "epics").iterdir()) == []
    assert len(JournalStore(common_dir).pending()) == 1
