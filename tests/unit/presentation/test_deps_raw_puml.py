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
        from spec_dock_runtime.application import contracts as app_contracts
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.presentation import json_state as presentation_json_state
    finally:
        sys.path.pop(0)
    return app_contracts, domain_models, presentation_json_state


def _node(domain_models, kind, node_id, title, *, parent_id=None, initiative_id=None, epic_id=None):
    path = Path(f"/repo/spec-dock/{node_id}")
    return domain_models.SpecNode(
        kind=kind,
        id=node_id,
        title=title,
        slug=node_id,
        path=path,
        meta_path=path / ".meta.json",
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=None,
    )


def _status(domain_models, issue_id, effective_status="open"):
    return domain_models.IssueStatusSnapshot(
        issue_id=issue_id,
        authority="derived",
        effective_status=effective_status,
        source="local",
        stale=False,
        last_sync_at="2026-06-18T00:00:00Z",
        github_number=None,
    )


def _eval(domain_models, *, ready):
    return domain_models.DepsEvaluation(
        ready=ready,
        guard_reason="ready" if ready else "blocked",
        blockers=[] if ready else ["iss-blocker"],
        blockers_top=[] if ready else ["iss-blocker"],
        closure=[],
    )


def _state(
    *,
    raw_node_depends_on_map,
    extra_nodes=None,
    issue_statuses=None,
    deps_eval_by_id=None,
    active_issue_id=None,
):
    app_contracts, domain_models, presentation_json_state = _runtime_modules()
    nodes = {
        "init-a": _node(domain_models, "initiative", "init-a", "Initiative A"),
        "epic-a": _node(
            domain_models,
            "epic",
            "epic-a",
            "Epic A",
            parent_id="init-a",
            initiative_id="init-a",
        ),
        "iss-a": _node(
            domain_models,
            "issue",
            "iss-a",
            "Issue A",
            parent_id="epic-a",
            initiative_id="init-a",
            epic_id="epic-a",
        ),
        "iss-b": _node(
            domain_models,
            "issue",
            "iss-b",
            "Issue B",
            parent_id="epic-a",
            initiative_id="init-a",
            epic_id="epic-a",
        ),
    }
    nodes.update(extra_nodes or {})
    statuses = {node_id: _status(domain_models, node_id) for node_id, node in nodes.items() if node.kind == "issue"}
    statuses.update(issue_statuses or {})
    evals = {
        node_id: _eval(domain_models, ready=True)
        for node_id, node in nodes.items()
        if node.kind == "issue"
    }
    evals.update(deps_eval_by_id or {})
    return (
        app_contracts.SyncStateResult(
            graph=domain_models.SpecGraph(nodes_by_id=nodes),
            active=domain_models.ActiveSelection(
                initiative_id="init-a",
                epic_id="epic-a",
                issue_id=active_issue_id,
            )
            if active_issue_id
            else None,
            issue_statuses=statuses,
            progress=domain_models.ProgressMap(by_node_id={}, counts={}),
            deps_state=domain_models.DepsState(nodes=[], warnings=[]),
            deps_eval_by_id=evals,
            generated_at="2026-06-18T00:00:00Z",
            warnings=[],
            deps_preflight_error=None,
            repo_root=Path("/repo"),
            raw_node_depends_on_map=raw_node_depends_on_map,
        ),
        presentation_json_state,
        domain_models,
    )


def _render(**kwargs):
    state, presentation_json_state, _domain_models = _state(**kwargs)
    return presentation_json_state.render_deps_raw_artifact(state).puml_text


def test_tc_s02_001_issue_to_issue_edge_with_ancestors():
    puml = _render(raw_node_depends_on_map={"iss-b": ["iss-a"]})

    assert puml.startswith("@startuml\n")
    assert "left to right direction" in puml
    assert "skinparam shadowing false" in puml
    assert "skinparam linetype ortho" in puml
    assert "skinparam packageStyle rectangle" in puml
    assert 'package "init-a\\nInitiative A" as Ninit_a <<initiative>> {' in puml
    assert 'package "epic-a\\nEpic A" as Nepic_a <<epic>> {' in puml
    assert 'rectangle "iss-a\\nIssue A\\nReady" as Niss_a #D5E8D4' in puml
    assert 'rectangle "iss-b\\nIssue B\\nReady" as Niss_b #D5E8D4' in puml
    assert "Niss_a --> Niss_b : blocks" in puml


def test_tc_s02_002_parent_level_package_endpoint_edge():
    _unused_app_contracts, domain_models, presentation_json_state = _runtime_modules()
    extra_nodes = {
        "epic-b": _node(
            domain_models,
            "epic",
            "epic-b",
            "Epic B",
            parent_id="init-a",
            initiative_id="init-a",
        )
    }
    state, _unused, _unused_domain = _state(
        raw_node_depends_on_map={"epic-b": ["epic-a"]},
        extra_nodes=extra_nodes,
    )

    puml = presentation_json_state.render_deps_raw_artifact(state).puml_text

    assert "Nepic_a --> Nepic_b : blocks" in puml
    assert 'package "epic-a\\nEpic A" as Nepic_a <<epic>> {' in puml
    assert 'package "epic-b\\nEpic B" as Nepic_b <<epic>> {' in puml
    assert "Niss_a -->" not in puml
    assert "--> Niss_b" not in puml


def test_tc_s02_003_epic_issue_mixed_edge():
    puml = _render(raw_node_depends_on_map={"iss-a": ["epic-a"]})

    assert "Nepic_a --> Niss_a : blocks" in puml
    assert 'package "epic-a\\nEpic A" as Nepic_a <<epic>> {' in puml
    assert 'rectangle "iss-a\\nIssue A\\nReady" as Niss_a #D5E8D4' in puml


def test_tc_s02_004_initiative_issue_mixed_edge():
    puml = _render(raw_node_depends_on_map={"iss-a": ["init-a"]})

    assert "Ninit_a --> Niss_a : blocks" in puml
    assert 'package "init-a\\nInitiative A" as Ninit_a <<initiative>> {' in puml
    assert 'rectangle "iss-a\\nIssue A\\nReady" as Niss_a #D5E8D4' in puml


def test_tc_s02_005_nonparticipants_omitted_and_ancestors_retained():
    _unused_app_contracts, domain_models, presentation_json_state = _runtime_modules()
    extra_nodes = {
        "iss-unrelated": _node(
            domain_models,
            "issue",
            "iss-unrelated",
            "Unrelated",
            parent_id="epic-a",
            initiative_id="init-a",
            epic_id="epic-a",
        )
    }
    state, _unused, _unused_domain = _state(
        raw_node_depends_on_map={"iss-b": ["iss-a"]},
        extra_nodes=extra_nodes,
    )

    puml = presentation_json_state.render_deps_raw_artifact(state).puml_text

    assert 'package "init-a\\nInitiative A" as Ninit_a <<initiative>> {' in puml
    assert 'package "epic-a\\nEpic A" as Nepic_a <<epic>> {' in puml
    assert "iss-a" in puml
    assert "iss-b" in puml
    assert "iss-unrelated" not in puml


def test_tc_s02_006_parent_participant_without_descendant_issue_expansion():
    puml = _render(raw_node_depends_on_map={"epic-a": ["init-a"]})

    assert "Ninit_a --> Nepic_a : blocks" in puml
    assert 'package "epic-a\\nEpic A" as Nepic_a <<epic>> {' in puml
    assert "iss-a" not in puml
    assert "iss-b" not in puml


def test_tc_s02_007_done_closed_participant_included():
    _unused_app_contracts, domain_models, presentation_json_state = _runtime_modules()
    state, _unused, _unused_domain = _state(
        raw_node_depends_on_map={"iss-b": ["iss-a"]},
        issue_statuses={"iss-a": _status(domain_models, "iss-a", "done")},
    )

    puml = presentation_json_state.render_deps_raw_artifact(state).puml_text

    assert 'rectangle "iss-a\\nIssue A\\nDone" as Niss_a #E3E3E3' in puml
    assert "Niss_a --> Niss_b : blocks" in puml


def test_tc_s02_008_zero_raw_direct_dependencies_valid_note():
    puml = _render(raw_node_depends_on_map={})

    assert puml.startswith("@startuml\n")
    assert "left to right direction" in puml
    assert "skinparam shadowing false" in puml
    assert "skinparam linetype ortho" in puml
    assert "skinparam packageStyle rectangle" in puml
    assert 'note "No raw direct dependencies to render" as Empty' in puml
    assert puml.endswith("@enduml\n")
