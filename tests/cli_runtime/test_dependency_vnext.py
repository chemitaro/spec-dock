"""Declared Scope dependencies remain distinct from inherited start prerequisites."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import stat
import sys
from typing import TYPE_CHECKING, cast

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.create_local_scope import AncestorState, create_local_scope  # noqa: E402
from spec_dock_runtime.application.dependency_vnext import (  # noqa: E402
    check_scope_readiness,
    list_scope_dependencies,
    mutate_scope_dependency,
)
from spec_dock_runtime.application.import_github_scope import import_github_scope  # noqa: E402
from spec_dock_runtime.application.scope_query import load_scope_views  # noqa: E402
from spec_dock_runtime.domain.dependency_vnext import evaluate_start_readiness  # noqa: E402
from spec_dock_runtime.domain.lifecycle import GithubBackend, StatusObservation  # noqa: E402
from spec_dock_runtime.infra.json_store import atomic_write_json, read_guarded_json  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import FakeGateway, _issue, _ready_repo  # noqa: E402

if TYPE_CHECKING:
    from spec_dock_runtime.infra.contracts import GithubIssueRecord


def _two_trees(tmp_path: Path):
    common = _ready_repo(tmp_path)
    created = []
    for label in ("A", "B"):
        initiative = create_local_scope(kind="initiative", title=f"Init {label}", parent=None, ancestors=(), **common)
        init_state = AncestorState(initiative.id, "initiative", "local", "open", False)
        epic = create_local_scope(kind="epic", title=f"Epic {label}", parent=init_state, ancestors=(), **common)
        epic_state = AncestorState(epic.id, "epic", "local", "open", False, initiative.id)
        issue = create_local_scope(
            kind="issue", title=f"Issue {label}", parent=epic_state, ancestors=(init_state,), **common
        )
        created.append((initiative, epic, issue))
    return common, created[0], created[1]


def _mutation_context(common: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in common.items() if key != "updated_at"}


def test_dependency_add_list_inheritance_duplicate_and_remove(tmp_path: Path) -> None:
    common, left, right = _two_trees(tmp_path)
    repo_root = cast("Path", common["repo_root"])
    before = (left[0].path / ".meta.json").read_bytes()
    added = mutate_scope_dependency(
        from_target=left[1].id, to_target=right[0].id, action="add", **_mutation_context(common)
    )
    assert added.changed
    declared = list_scope_dependencies(repo_root / "spec-dock", left[1].id)
    assert [(edge.target_id, edge.declared_by) for edge in declared.declared] == [(right[0].id, left[1].id)]
    child = list_scope_dependencies(repo_root / "spec-dock", left[2].id)
    assert child.declared == ()
    assert [(edge.target_id, edge.declared_by) for edge in child.effective] == [(right[0].id, left[1].id)]
    assert not mutate_scope_dependency(
        from_target=left[1].id, to_target=right[0].id, action="add", **_mutation_context(common)
    ).changed
    assert (left[0].path / ".meta.json").read_bytes() == before
    assert json.loads((left[1].path / ".meta.json").read_text())["depends_on"] == [right[0].id]
    removed = mutate_scope_dependency(
        from_target=left[1].id, to_target=right[0].id, action="remove", **_mutation_context(common)
    )
    assert removed.changed
    assert list_scope_dependencies(repo_root / "spec-dock", left[2].id).effective == ()
    with pytest.raises(LookupError, match="edge was not found"):
        mutate_scope_dependency(
            from_target=left[1].id, to_target=right[0].id, action="remove", **_mutation_context(common)
        )
    assert not mutate_scope_dependency(
        from_target=left[1].id, to_target=right[0].id, action="remove", missing_ok=True, **_mutation_context(common)
    ).changed


def test_dependency_rejects_self_ancestor_and_effective_cycle(tmp_path: Path) -> None:
    common, left, right = _two_trees(tmp_path)
    for source, target in ((left[0], left[0]), (left[0], left[1]), (left[2], left[0])):
        with pytest.raises(ValueError, match=r"self|ancestor|descendant"):
            mutate_scope_dependency(
                from_target=source.id, to_target=target.id, action="add", **_mutation_context(common)
            )
    mutate_scope_dependency(from_target=left[0].id, to_target=right[1].id, action="add", **_mutation_context(common))
    with pytest.raises(ValueError, match="cycle"):
        mutate_scope_dependency(
            from_target=right[1].id, to_target=left[2].id, action="add", **_mutation_context(common)
        )
    views = load_scope_views(cast("Path", common["repo_root"]) / "spec-dock")
    assert len(views) == 6


def test_dependency_rejects_cycle_through_parent_completion_wait(tmp_path: Path) -> None:
    common, left, right = _two_trees(tmp_path)
    mutate_scope_dependency(from_target=left[2].id, to_target=right[1].id, action="add", **_mutation_context(common))
    with pytest.raises(ValueError, match="cycle"):
        mutate_scope_dependency(
            from_target=right[1].id, to_target=left[0].id, action="add", **_mutation_context(common)
        )


@pytest.mark.parametrize("source_index", [0, 1, 2])
@pytest.mark.parametrize("target_index", [0, 1, 2])
def test_dependency_all_kind_pairs_preserve_unknown_fields_and_mode(
    tmp_path: Path, source_index: int, target_index: int
) -> None:
    common, left, right = _two_trees(tmp_path)
    source = left[source_index]
    destination = right[target_index]
    meta_path = source.path / ".meta.json"
    loaded = read_guarded_json(meta_path)
    assert loaded is not None and isinstance(loaded[0], dict)
    payload = dict(loaded[0])
    payload["custom_note"] = {"retain": True}
    atomic_write_json(meta_path, payload, expected_identity=loaded[1])
    before_mode = stat.S_IMODE(meta_path.stat().st_mode)
    result = mutate_scope_dependency(
        from_target=source.id,
        to_target=destination.id,
        action="add",
        **_mutation_context(common),
    )
    assert result.changed
    after = json.loads(meta_path.read_text(encoding="utf-8"))
    assert after["depends_on"] == [destination.id]
    assert after["custom_note"] == {"retain": True}
    assert stat.S_IMODE(meta_path.stat().st_mode) == before_mode


def test_readiness_checks_target_and_ancestors_without_waiting_for_children(tmp_path: Path) -> None:
    common, left, right = _two_trees(tmp_path)
    mutate_scope_dependency(from_target=left[2].id, to_target=right[0].id, action="add", **_mutation_context(common))
    specdock_dir = cast("Path", common["repo_root"]) / "spec-dock"
    views = load_scope_views(specdock_dir)
    raw: dict[str, tuple[str, ...]] = {view.id: () for view in views}
    raw[left[2].id] = (right[0].id,)
    assert evaluate_start_readiness(views, raw, left[0].id).ready
    child = evaluate_start_readiness(views, raw, left[2].id)
    assert not child.ready
    assert [(blocker.scope_id, blocker.required_state) for blocker in child.blockers] == [(right[0].id, "completed")]
    # Completed children do not substitute for their still-open parent.
    completed = StatusObservation("completed", "local", "local", "2026-09-25T00:00:00Z", None, False)
    with_completed_children = tuple(
        replace(view, status=completed) if view.id in (right[1].id, right[2].id) else view for view in views
    )
    parent_dependency = evaluate_start_readiness(with_completed_children, raw, left[2].id)
    assert not parent_dependency.ready


def test_readiness_rejects_unknown_and_requires_explicit_stale_opt_in(tmp_path: Path) -> None:
    common, left, right = _two_trees(tmp_path)
    views = load_scope_views(cast("Path", common["repo_root"]) / "spec-dock")
    raw: dict[str, tuple[str, ...]] = {view.id: () for view in views}
    raw[left[1].id] = (right[0].id,)
    cache = StatusObservation("completed", "github", "cache", "2026-09-25T00:00:00Z", None, True)
    unknown = StatusObservation("unknown", "github", "cache", None, None, True)
    github_views = tuple(
        replace(view, backend=GithubBackend(47, "example", "repo"), status=cache) if view.id == right[0].id else view
        for view in views
    )
    assert not evaluate_start_readiness(github_views, raw, left[1].id, source="cache", mode="start").ready
    assert evaluate_start_readiness(github_views, raw, left[1].id, source="cache", mode="start", allow_stale=True).ready
    unknown_views = tuple(replace(view, status=unknown) if view.id == right[0].id else view for view in github_views)
    assert not evaluate_start_readiness(
        unknown_views, raw, left[1].id, source="cache", mode="start", allow_stale=True
    ).ready
    live = StatusObservation("completed", "github", "github", "2026-09-25T00:00:00Z", None, False)
    assert evaluate_start_readiness(
        unknown_views, raw, left[1].id, source="github", mode="start", observations={right[0].id: live}
    ).ready
    assert not evaluate_start_readiness(unknown_views, raw, left[1].id, source="github", mode="start").ready
    with pytest.raises(ValueError, match="offline"):
        evaluate_start_readiness(unknown_views, raw, left[1].id, source="github", offline=True)


def test_readiness_live_observes_only_relevant_github_scope_without_mutation(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    local = create_local_scope(kind="initiative", title="Local", parent=None, ancestors=(), **common)
    imported = import_github_scope(
        kind="initiative",
        github_ref="gh:example/repo#47",
        repo_hint=None,
        title="Remote",
        parent_id=None,
        slug=None,
        gateway=FakeGateway(_issue()),
        **common,
    )
    specdock_dir = cast("Path", common["repo_root"]) / "spec-dock"
    before = (local.path / ".meta.json").read_bytes()
    assert check_scope_readiness(specdock_dir, local.id, source="github").ready
    mutate_scope_dependency(
        from_target=local.id,
        to_target=imported.id,
        action="add",
        **_mutation_context(common),
    )
    after_mutation = (local.path / ".meta.json").read_bytes()

    class CompletedGateway:
        calls = 0

        def get(self, repo_root: Path, repository: str, number: int) -> GithubIssueRecord:
            self.calls += 1
            assert repository == "example/repo" and number == 47
            return replace(_issue(), state="completed", raw_state="closed", state_reason="completed")

    gateway = CompletedGateway()
    assert not check_scope_readiness(specdock_dir, local.id, source="cache").ready
    assert check_scope_readiness(specdock_dir, local.id, source="github", gateway=gateway, for_start=True).ready
    assert gateway.calls == 1
    assert (local.path / ".meta.json").read_bytes() == after_mutation
    assert before != after_mutation
