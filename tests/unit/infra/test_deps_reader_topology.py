import json
import sys
from pathlib import Path


def _runtime_modules():
    runtime_scripts_dir = (
        Path(__file__).resolve().parents[3]
        / "src"
        / "spec_dock"
        / "assets"
        / "spec_dock"
        / "scripts"
    )
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.domain import tree as domain_tree
        from spec_dock_runtime.infra import deps_reader
    finally:
        sys.path.pop(0)
    return domain_models, domain_tree, deps_reader


def _write_meta(path: Path, depends_on: list[str]) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / ".meta.json").write_text(
        json.dumps({"schema_version": 1, "depends_on": depends_on}),
        encoding="utf-8",
    )


def _seed(
    domain_models,
    *,
    kind: str,
    node_id: str,
    path: Path,
    parent_id: str | None,
    initiative_id: str | None,
    epic_id: str | None,
):
    return domain_models.SpecNodeSeed(
        kind=kind,
        id=node_id,
        title=node_id,
        slug=node_id,
        path=path,
        meta_path=path / ".meta.json",
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=None,
    )


def test_load_issue_depends_on_map_retains_empty_epic_topology_context(tmp_path) -> None:
    domain_models, domain_tree, deps_reader = _runtime_modules()
    specdock_dir = tmp_path / "repo" / "spec-dock"
    init_path = specdock_dir / "initiatives" / "init-00101-platform"
    empty_epic_path = init_path / "epics" / "epic-00202-empty"
    target_epic_path = init_path / "epics" / "epic-00300-target"
    target_issue_path = target_epic_path / "issues" / "iss-00301-target"

    _write_meta(init_path, [])
    _write_meta(empty_epic_path, [])
    _write_meta(target_epic_path, [])
    _write_meta(target_issue_path, ["epic-00202"])

    graph = domain_tree.build_graph(
        [
            _seed(
                domain_models,
                kind="initiative",
                node_id="init-00101",
                path=init_path,
                parent_id=None,
                initiative_id=None,
                epic_id=None,
            ),
            _seed(
                domain_models,
                kind="epic",
                node_id="epic-00202",
                path=empty_epic_path,
                parent_id="init-00101",
                initiative_id="init-00101",
                epic_id=None,
            ),
            _seed(
                domain_models,
                kind="epic",
                node_id="epic-00300",
                path=target_epic_path,
                parent_id="init-00101",
                initiative_id="init-00101",
                epic_id=None,
            ),
            _seed(
                domain_models,
                kind="issue",
                node_id="iss-00301",
                path=target_issue_path,
                parent_id="epic-00300",
                initiative_id="init-00101",
                epic_id="epic-00300",
            ),
        ]
    )

    result = deps_reader.load_issue_depends_on_map(specdock_dir, graph)

    assert result.issue_depends_on_map["iss-00301"] == []
    assert "deps_ref_expanded_to_empty" in result.warnings
    assert result.raw_node_depends_on_map["iss-00301"] == ["epic-00202"]
    assert result.dependency_contexts_by_issue_id["iss-00301"] == [
        deps_reader.DepsDependencyContext(
            source_node_id="iss-00301",
            source_issue_id="iss-00301",
            target_node_id="epic-00202",
            target_node_kind="epic",
            target_issue_ids=(),
            expansion="empty",
        )
    ]


def test_load_issue_depends_on_map_expands_non_empty_epic_and_keeps_raw_context(tmp_path) -> None:
    domain_models, domain_tree, deps_reader = _runtime_modules()
    specdock_dir = tmp_path / "repo" / "spec-dock"
    init_path = specdock_dir / "initiatives" / "init-00101-platform"
    blocker_epic_path = init_path / "epics" / "epic-00202-blockers"
    target_epic_path = init_path / "epics" / "epic-00300-target"
    target_issue_path = target_epic_path / "issues" / "iss-00301-target"
    blocker_one_path = blocker_epic_path / "issues" / "iss-00401-one"
    blocker_two_path = blocker_epic_path / "issues" / "iss-00402-two"

    for path, depends_on in [
        (init_path, []),
        (blocker_epic_path, []),
        (target_epic_path, []),
        (target_issue_path, ["epic-00202"]),
        (blocker_one_path, []),
        (blocker_two_path, []),
    ]:
        _write_meta(path, depends_on)

    graph = domain_tree.build_graph(
        [
            _seed(
                domain_models,
                kind="initiative",
                node_id="init-00101",
                path=init_path,
                parent_id=None,
                initiative_id=None,
                epic_id=None,
            ),
            _seed(
                domain_models,
                kind="epic",
                node_id="epic-00202",
                path=blocker_epic_path,
                parent_id="init-00101",
                initiative_id="init-00101",
                epic_id=None,
            ),
            _seed(
                domain_models,
                kind="epic",
                node_id="epic-00300",
                path=target_epic_path,
                parent_id="init-00101",
                initiative_id="init-00101",
                epic_id=None,
            ),
            _seed(
                domain_models,
                kind="issue",
                node_id="iss-00301",
                path=target_issue_path,
                parent_id="epic-00300",
                initiative_id="init-00101",
                epic_id="epic-00300",
            ),
            _seed(
                domain_models,
                kind="issue",
                node_id="iss-00401",
                path=blocker_one_path,
                parent_id="epic-00202",
                initiative_id="init-00101",
                epic_id="epic-00202",
            ),
            _seed(
                domain_models,
                kind="issue",
                node_id="iss-00402",
                path=blocker_two_path,
                parent_id="epic-00202",
                initiative_id="init-00101",
                epic_id="epic-00202",
            ),
        ]
    )

    result = deps_reader.load_issue_depends_on_map(specdock_dir, graph)

    assert result.issue_depends_on_map["iss-00301"] == ["iss-00401", "iss-00402"]
    assert result.raw_node_depends_on_map["iss-00301"] == ["epic-00202"]
    assert result.dependency_contexts_by_issue_id["iss-00301"] == [
        deps_reader.DepsDependencyContext(
            source_node_id="iss-00301",
            source_issue_id="iss-00301",
            target_node_id="epic-00202",
            target_node_kind="epic",
            target_issue_ids=("iss-00401", "iss-00402"),
            expansion="expanded",
        )
    ]
