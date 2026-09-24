"""Declared Scope dependencies remain distinct from inherited start prerequisites."""

from __future__ import annotations

import json
from pathlib import Path
import stat
import sys
from typing import cast

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.create_local_scope import AncestorState, create_local_scope  # noqa: E402
from spec_dock_runtime.application.dependency_vnext import (  # noqa: E402
    list_scope_dependencies,
    mutate_scope_dependency,
)
from spec_dock_runtime.application.scope_query import load_scope_views  # noqa: E402
from spec_dock_runtime.infra.json_store import atomic_write_json, read_guarded_json  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import _ready_repo  # noqa: E402


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
