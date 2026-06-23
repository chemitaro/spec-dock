from pathlib import Path
import sys


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
    deps_preflight_error=None,
    high_level_statuses_by_node_id=None,
    dependency_contexts_by_issue_id=None,
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
            deps_preflight_error=deps_preflight_error,
            repo_root=Path("/repo"),
            raw_node_depends_on_map=raw_node_depends_on_map,
            high_level_statuses_by_node_id=high_level_statuses_by_node_id or {},
            dependency_contexts_by_issue_id=dependency_contexts_by_issue_id or {},
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
    assert "Niss_a --> Niss_b : raw_direct" in puml


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

    assert "Nepic_a --> Nepic_b : raw_direct" in puml
    assert 'package "epic-a\\nEpic A" as Nepic_a <<epic>> {' in puml
    assert 'package "epic-b\\nEpic B" as Nepic_b <<epic>> {' in puml
    assert "Niss_a -->" not in puml
    assert "--> Niss_b" not in puml


def test_tc_s02_003_epic_issue_mixed_edge():
    puml = _render(raw_node_depends_on_map={"iss-a": ["epic-a"]})

    assert "Nepic_a --> Niss_a : raw_direct" in puml
    assert 'package "epic-a\\nEpic A" as Nepic_a <<epic>> {' in puml
    assert 'rectangle "iss-a\\nIssue A\\nReady" as Niss_a #D5E8D4' in puml


def test_tc_s02_004_initiative_issue_mixed_edge():
    puml = _render(raw_node_depends_on_map={"iss-a": ["init-a"]})

    assert "Ninit_a --> Niss_a : raw_direct" in puml
    assert 'package "init-a\\nInitiative A" as Ninit_a <<initiative>> {' in puml
    assert 'rectangle "iss-a\\nIssue A\\nReady" as Niss_a #D5E8D4' in puml


def test_tc_s04_003_high_level_participant_state_comes_from_payload():
    _unused_app_contracts, domain_models, presentation_json_state = _runtime_modules()
    state, _unused, _unused_domain = _state(
        raw_node_depends_on_map={"iss-a": ["epic-a"]},
        high_level_statuses_by_node_id={
            "init-a": domain_models.DepsHighLevelStatus(
                node_id="init-a",
                state="open",
                source="descendant",
            ),
            "epic-a": domain_models.DepsHighLevelStatus(
                node_id="epic-a",
                state="unknown",
                source="none",
            ),
        },
    )

    puml = presentation_json_state.render_deps_raw_artifact(state).puml_text

    assert "| high-level unknown |<#EEEEEE> |" in puml
    assert "raw direct dependencies; not readiness authority" in puml
    assert 'package "init-a\\nInitiative A\\nOpen (descendant)" as Ninit_a <<initiative>> #FFFFFF {' in puml
    assert 'package "epic-a\\nEpic A\\nUnknown (none)" as Nepic_a <<epic>> #EEEEEE {' in puml
    assert "Nepic_a --> Niss_a : raw_direct" in puml


def test_tc_s04_004_completed_high_level_source_is_not_raw_participant():
    _unused_app_contracts, domain_models, presentation_json_state = _runtime_modules()
    state, _unused, _unused_domain = _state(
        raw_node_depends_on_map={"epic-a": ["init-a"]},
        issue_statuses={
            "iss-a": _status(domain_models, "iss-a", "done"),
            "iss-b": _status(domain_models, "iss-b", "done"),
        },
        high_level_statuses_by_node_id={
            "epic-a": domain_models.DepsHighLevelStatus(
                node_id="epic-a",
                state="open",
                source="github",
            ),
            "init-a": domain_models.DepsHighLevelStatus(
                node_id="init-a",
                state="open",
                source="github",
            ),
        },
    )

    puml = presentation_json_state.render_deps_raw_artifact(state).puml_text

    assert "Nepic_a --> Ninit_a : raw_direct" not in puml
    assert 'note "No raw direct dependencies to render" as Empty' in puml


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

    assert "Ninit_a --> Nepic_a : raw_direct" in puml
    assert 'package "epic-a\\nEpic A" as Nepic_a <<epic>> {' in puml
    assert "iss-a" not in puml
    assert "iss-b" not in puml


def test_tc_s04_004_done_dependency_is_omitted_from_active_raw_view():
    _unused_app_contracts, domain_models, presentation_json_state = _runtime_modules()
    state, _unused, _unused_domain = _state(
        raw_node_depends_on_map={"iss-b": ["iss-a"]},
        issue_statuses={"iss-a": _status(domain_models, "iss-a", "done")},
    )

    puml = presentation_json_state.render_deps_raw_artifact(state).puml_text

    assert "iss-a" not in puml
    assert "Niss_a --> Niss_b : raw_direct" not in puml
    assert 'note "No raw direct dependencies to render" as Empty' in puml


def test_tc_s04_005_satisfied_high_level_dependency_is_omitted_from_active_raw_view():
    _unused_app_contracts, domain_models, presentation_json_state = _runtime_modules()
    state, _unused, _unused_domain = _state(
        raw_node_depends_on_map={"iss-a": ["epic-a"]},
        dependency_contexts_by_issue_id={
            "iss-a": [
                domain_models.DepsDependencyContext(
                    source_node_id="iss-a",
                    source_issue_id="iss-a",
                    target_node_id="epic-a",
                    target_node_kind="epic",
                    target_issue_ids=("iss-done",),
                    expansion="expanded",
                    lifecycle_state="open",
                    lifecycle_source="github",
                    dependency_disposition="satisfied",
                    disposition_basis="all_descendant_issues_done",
                )
            ]
        },
        high_level_statuses_by_node_id={
            "epic-a": domain_models.DepsHighLevelStatus(
                node_id="epic-a",
                state="open",
                source="github",
            )
        },
    )

    puml = presentation_json_state.render_deps_raw_artifact(state).puml_text

    assert "epic-a" not in puml
    assert "Nepic_a --> Niss_a : raw_direct" not in puml
    assert 'note "No raw direct dependencies to render" as Empty' in puml


def test_tc_s04_006_satisfied_high_level_source_dependency_is_omitted_from_active_raw_view():
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
        dependency_contexts_by_issue_id={
            "iss-b": [
                domain_models.DepsDependencyContext(
                    source_node_id="epic-b",
                    source_issue_id="iss-b",
                    target_node_id="epic-a",
                    target_node_kind="epic",
                    target_issue_ids=("iss-done",),
                    expansion="expanded",
                )
            ]
        },
        deps_eval_by_id={
            "iss-b": domain_models.DepsEvaluation(
                ready=True,
                guard_reason="ready",
                blockers=[],
                blockers_top=[],
                closure=[],
                satisfied_dependencies=[
                    domain_models.DepsDependencyContext(
                        source_node_id="epic-b",
                        source_issue_id="iss-b",
                        target_node_id="epic-a",
                        target_node_kind="epic",
                        target_issue_ids=("iss-done",),
                        expansion="expanded",
                        lifecycle_state="open",
                        lifecycle_source="github",
                        dependency_disposition="satisfied",
                        disposition_basis="all_descendant_issues_done",
                    )
                ],
            )
        },
        high_level_statuses_by_node_id={
            "epic-a": domain_models.DepsHighLevelStatus(
                node_id="epic-a",
                state="open",
                source="github",
            ),
            "epic-b": domain_models.DepsHighLevelStatus(
                node_id="epic-b",
                state="open",
                source="github",
            ),
        },
    )

    puml = presentation_json_state.render_deps_raw_artifact(state).puml_text

    assert "epic-a" not in puml
    assert "epic-b" not in puml
    assert "Nepic_a --> Nepic_b : raw_direct" not in puml
    assert 'note "No raw direct dependencies to render" as Empty' in puml


def test_tc_s04_007_unknown_high_level_source_dependency_remains_in_active_raw_view():
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
        issue_statuses={
            "iss-a": _status(domain_models, "iss-a", "done"),
            "iss-b": _status(domain_models, "iss-b", "done"),
        },
        dependency_contexts_by_issue_id={
            "iss-b": [
                domain_models.DepsDependencyContext(
                    source_node_id="epic-b",
                    source_issue_id="iss-b",
                    target_node_id="epic-a",
                    target_node_kind="epic",
                    target_issue_ids=("iss-a",),
                    expansion="expanded",
                    lifecycle_state="unknown",
                    lifecycle_source="none",
                    dependency_disposition="indeterminate",
                    disposition_basis="descendant_issue_unknown",
                )
            ]
        },
        deps_eval_by_id={
            "iss-b": domain_models.DepsEvaluation(
                ready=False,
                guard_reason="unknown",
                blockers=["epic-a"],
                blockers_top=["epic-a"],
                closure=[],
                node_blockers=[
                    domain_models.DepsNodeBlocker(
                        node_id="epic-a",
                        reason="lifecycle_unknown",
                        state="unknown",
                        state_source="none",
                        source_issue_id="iss-b",
                        lifecycle_state="unknown",
                        lifecycle_source="none",
                        dependency_disposition="indeterminate",
                        disposition_basis="descendant_issue_unknown",
                    )
                ],
            )
        },
        high_level_statuses_by_node_id={
            "epic-a": domain_models.DepsHighLevelStatus(
                node_id="epic-a",
                state="unknown",
                source="none",
            ),
            "epic-b": domain_models.DepsHighLevelStatus(
                node_id="epic-b",
                state="unknown",
                source="none",
            ),
        },
    )

    puml = presentation_json_state.render_deps_raw_artifact(state).puml_text

    assert "Nepic_a --> Nepic_b : raw_direct" in puml
    assert 'package "epic-a\\nEpic A\\nUnknown (none)" as Nepic_a <<epic>> #EEEEEE {' in puml
    assert 'package "epic-b\\nEpic B\\nUnknown (none)" as Nepic_b <<epic>> #EEEEEE {' in puml


def test_tc_s04_008_satisfied_high_level_source_dependency_with_raw_context_only_renders_active_edge():
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
        dependency_contexts_by_issue_id={
            "iss-b": [
                domain_models.DepsDependencyContext(
                    source_node_id="epic-b",
                    source_issue_id="iss-b",
                    target_node_id="epic-a",
                    target_node_kind="epic",
                    target_issue_ids=("iss-open",),
                    expansion="expanded",
                    lifecycle_state="open",
                    lifecycle_source="github",
                    dependency_disposition="blocking",
                    disposition_basis="descendant_issue_open",
                )
            ]
        },
        high_level_statuses_by_node_id={
            "epic-a": domain_models.DepsHighLevelStatus(
                node_id="epic-a",
                state="open",
                source="github",
            ),
            "epic-b": domain_models.DepsHighLevelStatus(
                node_id="epic-b",
                state="open",
                source="github",
            ),
        },
    )

    puml = presentation_json_state.render_deps_raw_artifact(state).puml_text

    assert "Nepic_a --> Nepic_b : raw_direct" in puml
    assert 'package "epic-a\\nEpic A\\nOpen (github)" as Nepic_a <<epic>> #FFFFFF {' in puml
    assert 'package "epic-b\\nEpic B\\nOpen (github)" as Nepic_b <<epic>> #FFFFFF {' in puml


def test_tc_s02_008_zero_raw_direct_dependencies_valid_note():
    puml = _render(raw_node_depends_on_map={})

    assert puml.startswith("@startuml\n")
    assert "left to right direction" in puml
    assert "skinparam shadowing false" in puml
    assert "skinparam linetype ortho" in puml
    assert "skinparam packageStyle rectangle" in puml
    assert 'note "No raw direct dependencies to render" as Empty' in puml
    assert puml.endswith("@enduml\n")


def test_tc_s04_001_disabled_raw_dependency_view_includes_failure_note():
    _unused_app_contracts, _unused_domain_models, presentation_json_state = _runtime_modules()
    state, _unused, _unused_domain = _state(
        raw_node_depends_on_map={"iss-b": ["iss-a"]},
        deps_preflight_error='Dependency cycle detected\niss-a -> "iss-b" \\ path',
    )

    puml = presentation_json_state.render_deps_raw_artifact(state).puml_text

    assert "title deps-raw - DEPS_DISABLED" in puml
    assert "deps_preflight_failed" in puml
    assert "deps.valid=false" in puml
    assert "mode=sync --force" in puml
    assert 'Dependency cycle detected iss-a -> \\"iss-b\\" \\\\ path' in puml
    assert "Niss_a --> Niss_b" not in puml
    assert puml.endswith("@enduml\n")
