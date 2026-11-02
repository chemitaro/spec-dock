"""deps-raw.puml renderer output for the payload the canonical dashboard builds (domain/canonical_dashboard.deps_raw).

Which Scopes take part (done or satisfied dependencies, ancestors) is decided by the canonical dashboard builder;
these tests feed hand-built payloads straight into the renderer.
"""

from __future__ import annotations

from typing import Any

from spec_dock.runtime.presentation.puml import render_deps_raw_puml


def _issue(issue_id: str, title: str, state: str = "ready") -> dict[str, Any]:
    return {"id": issue_id, "title": title, "state": state}


def _epic(epic_id: str, title: str, issues: list[dict[str, Any]], **state: str) -> dict[str, Any]:
    return {"id": epic_id, "title": title, **state, "issues": issues}


def _initiative(epics: list[dict[str, Any]], **state: str) -> dict[str, Any]:
    return {"id": "init-a", "title": "Initiative A", **state, "epics": epics}


def _render(tree: list[dict[str, Any]], edges: list[tuple[str, str]]) -> str:
    return render_deps_raw_puml({"tree": tree, "edges": [{"from": dependent, "to": to} for dependent, to in edges]})


def _issues_ab() -> list[dict[str, Any]]:
    return [_issue("iss-a", "Issue A"), _issue("iss-b", "Issue B")]


def test_tc_s02_001_issue_to_issue_edge_with_ancestors() -> None:
    puml = _render([_initiative([_epic("epic-a", "Epic A", _issues_ab())])], [("iss-b", "iss-a")])

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


def test_tc_s02_002_parent_level_package_endpoint_edge() -> None:
    puml = _render(
        [_initiative([_epic("epic-a", "Epic A", []), _epic("epic-b", "Epic B", [])])],
        [("epic-b", "epic-a")],
    )

    assert "Nepic_a --> Nepic_b : raw_direct" in puml
    assert 'package "epic-a\\nEpic A" as Nepic_a <<epic>> {' in puml
    assert 'package "epic-b\\nEpic B" as Nepic_b <<epic>> {' in puml
    assert "Niss_a -->" not in puml
    assert "--> Niss_b" not in puml


def test_tc_s02_003_epic_issue_mixed_edge() -> None:
    puml = _render([_initiative([_epic("epic-a", "Epic A", [_issue("iss-a", "Issue A")])])], [("iss-a", "epic-a")])

    assert "Nepic_a --> Niss_a : raw_direct" in puml
    assert 'package "epic-a\\nEpic A" as Nepic_a <<epic>> {' in puml
    assert 'rectangle "iss-a\\nIssue A\\nReady" as Niss_a #D5E8D4' in puml


def test_tc_s02_004_initiative_issue_mixed_edge() -> None:
    puml = _render([_initiative([_epic("epic-a", "Epic A", [_issue("iss-a", "Issue A")])])], [("iss-a", "init-a")])

    assert "Ninit_a --> Niss_a : raw_direct" in puml
    assert 'package "init-a\\nInitiative A" as Ninit_a <<initiative>> {' in puml
    assert 'rectangle "iss-a\\nIssue A\\nReady" as Niss_a #D5E8D4' in puml


def test_tc_s04_003_high_level_participant_state_comes_from_payload() -> None:
    epic = _epic("epic-a", "Epic A", [_issue("iss-a", "Issue A")], state="unknown", state_source="none")
    puml = _render([_initiative([epic], state="open", state_source="descendant")], [("iss-a", "epic-a")])

    assert "| high-level unknown |<#EEEEEE> |" in puml
    assert "raw direct dependencies; not readiness authority" in puml
    assert 'package "init-a\\nInitiative A\\nOpen (descendant)" as Ninit_a <<initiative>> #FFFFFF {' in puml
    assert 'package "epic-a\\nEpic A\\nUnknown (none)" as Nepic_a <<epic>> #EEEEEE {' in puml
    assert "Nepic_a --> Niss_a : raw_direct" in puml


def test_tc_s02_008_zero_raw_direct_dependencies_valid_note() -> None:
    puml = _render([], [])

    assert puml.startswith("@startuml\n")
    assert "left to right direction" in puml
    assert "skinparam shadowing false" in puml
    assert "skinparam linetype ortho" in puml
    assert "skinparam packageStyle rectangle" in puml
    assert 'note "No raw direct dependencies to render" as Empty' in puml
    assert puml.endswith("@enduml\n")
