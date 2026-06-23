from pathlib import Path
import sys

import pytest


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
        from spec_dock_runtime.domain import deps as domain_deps, models as domain_models, tree as domain_tree
    finally:
        sys.path.pop(0)
    return domain_deps, domain_models, domain_tree


def _issue_status(domain_models, issue_id: str, status: str):
    return domain_models.IssueStatusSnapshot(
        issue_id=issue_id,
        authority="github",
        effective_status=status,
        source="github",
        stale=False,
        last_sync_at="2026-06-05T00:00:00Z",
        github_number=int(issue_id.rsplit("-", 1)[1]),
    )


class TestDepsDomain:
    def _graph(self):
        _domain_deps, domain_models, domain_tree = _runtime_modules()
        root = Path("/repo/spec-dock/initiatives/init-00001-platform")
        return domain_tree.build_graph(
            [
                domain_models.SpecNodeSeed(
                    kind="initiative",
                    id="init-00001",
                    title="Platform",
                    slug="platform",
                    path=root,
                    meta_path=root / ".meta.json",
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=1,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
                domain_models.SpecNodeSeed(
                    kind="epic",
                    id="epic-00002",
                    title="Delivery",
                    slug="delivery",
                    path=root / "epics" / "epic-00002-delivery",
                    meta_path=root / "epics" / "epic-00002-delivery" / ".meta.json",
                    parent_id="init-00001",
                    initiative_id="init-00001",
                    epic_id=None,
                    github_issue_number=2,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
                domain_models.SpecNodeSeed(
                    kind="issue",
                    id="iss-00003",
                    title="Target",
                    slug="target",
                    path=root / "epics" / "epic-00002-delivery" / "issues" / "iss-00003-target",
                    meta_path=root / "epics" / "epic-00002-delivery" / "issues" / "iss-00003-target" / ".meta.json",
                    parent_id="epic-00002",
                    initiative_id="init-00001",
                    epic_id="epic-00002",
                    github_issue_number=3,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
                domain_models.SpecNodeSeed(
                    kind="issue",
                    id="iss-00004",
                    title="Open blocker",
                    slug="open-blocker",
                    path=root / "epics" / "epic-00002-delivery" / "issues" / "iss-00004-open-blocker",
                    meta_path=root
                    / "epics"
                    / "epic-00002-delivery"
                    / "issues"
                    / "iss-00004-open-blocker"
                    / ".meta.json",
                    parent_id="epic-00002",
                    initiative_id="init-00001",
                    epic_id="epic-00002",
                    github_issue_number=4,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
                domain_models.SpecNodeSeed(
                    kind="issue",
                    id="iss-00005",
                    title="Done blocker",
                    slug="done-blocker",
                    path=root / "epics" / "epic-00002-delivery" / "issues" / "iss-00005-done-blocker",
                    meta_path=root
                    / "epics"
                    / "epic-00002-delivery"
                    / "issues"
                    / "iss-00005-done-blocker"
                    / ".meta.json",
                    parent_id="epic-00002",
                    initiative_id="init-00001",
                    epic_id="epic-00002",
                    github_issue_number=5,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
            ]
        )

    def test_inspect_target_deps_classifies_ready_blocked_done_and_unknown_without_cli(self) -> None:
        domain_deps, domain_models, _domain_tree = _runtime_modules()
        graph = self._graph()
        statuses = {
            "iss-00003": _issue_status(domain_models, "iss-00003", "open"),
            "iss-00004": _issue_status(domain_models, "iss-00004", "open"),
            "iss-00005": _issue_status(domain_models, "iss-00005", "done"),
        }

        inspection = domain_deps.inspect_target_deps(
            graph,
            issue_depends_on_map={"iss-00003": ["iss-00004", "iss-00005"], "iss-00004": ["iss-00005"]},
            target_id=domain_models.NodeId("iss-00003"),
            issue_statuses=statuses,
            active_issue_id=None,
        )

        assert not inspection.evaluation.ready
        assert inspection.evaluation.guard_reason == "blocked"
        assert inspection.evaluation.blockers == ["iss-00004"]
        assert inspection.node_states["iss-00003"].status == "blocked"
        assert inspection.node_states["iss-00004"].status == "ready"
        assert inspection.node_states["iss-00005"].status == "done"

        unknown_statuses = dict(statuses)
        unknown_statuses["iss-00004"] = _issue_status(domain_models, "iss-00004", "unknown")
        unknown = domain_deps.inspect_target_deps(
            graph,
            issue_depends_on_map={"iss-00003": ["iss-00004"]},
            target_id=domain_models.NodeId("iss-00003"),
            issue_statuses=unknown_statuses,
            active_issue_id=None,
        )
        assert unknown.evaluation.guard_reason == "unknown"
        assert unknown.node_states["iss-00004"].status == "unknown"

        missing = domain_deps.inspect_target_deps(
            graph,
            issue_depends_on_map={"iss-00003": ["iss-00004"]},
            target_id=domain_models.NodeId("iss-00003"),
            issue_statuses={"iss-00003": statuses["iss-00003"]},
            active_issue_id=None,
        )
        assert missing.evaluation.guard_reason == "unknown"
        assert missing.node_states["iss-00004"].status == "unknown"

    def test_effective_deps_merge_issue_epic_and_initiative_edges_without_cli(self) -> None:
        domain_deps, _domain_models, _domain_tree = _runtime_modules()
        graph = self._graph()

        effective = domain_deps.build_effective_deps_map(
            graph,
            {
                "init-00001": ["iss-00005"],
                "epic-00002": ["iss-00004"],
                "iss-00003": ["iss-00004", "iss-00005"],
            },
        )

        assert effective["iss-00003"] == ["iss-00004", "iss-00005"]

    def test_evaluate_readiness_blocks_empty_open_high_level_dependency(self) -> None:
        domain_deps, domain_models, _domain_tree = _runtime_modules()
        graph = self._graph()
        statuses = {"iss-00003": _issue_status(domain_models, "iss-00003", "open")}
        dependency_context = domain_models.DepsDependencyContext(
            source_node_id="iss-00003",
            source_issue_id="iss-00003",
            target_node_id="epic-00002",
            target_node_kind="epic",
            target_issue_ids=(),
            expansion="empty",
        )

        result = domain_deps.evaluate_readiness(
            graph,
            issue_depends_on_map={"iss-00003": []},
            target_id=domain_models.NodeId("iss-00003"),
            issue_statuses=statuses,
            dependency_contexts_by_issue_id={"iss-00003": [dependency_context]},
            high_level_statuses_by_node_id={
                "epic-00002": domain_models.DepsHighLevelStatus(
                    node_id="epic-00002",
                    state="open",
                    source="github",
                )
            },
        )

        assert not result.ready
        assert result.guard_reason == "blocked"
        assert result.blockers == ["epic-00002"]
        assert result.issue_blockers == []
        assert len(result.node_blockers) == 1
        assert result.node_blockers[0].node_id == "epic-00002"
        assert result.node_blockers[0].reason == "empty_open"
        assert result.node_blockers[0].lifecycle_state == "open"
        assert result.node_blockers[0].lifecycle_source == "github"
        assert result.node_blockers[0].dependency_disposition == "blocking"
        assert result.node_blockers[0].disposition_basis == "empty_open_container"
        assert result.dependency_contexts == [dependency_context]
        assert result.dependency_contexts[0].lifecycle_state == "open"
        assert result.dependency_contexts[0].lifecycle_source == "github"
        assert result.dependency_contexts[0].dependency_disposition == "blocking"
        assert result.dependency_contexts[0].disposition_basis == "empty_open_container"

    def test_evaluate_readiness_records_empty_closed_high_level_dependency_as_satisfied(self) -> None:
        domain_deps, domain_models, _domain_tree = _runtime_modules()
        graph = self._graph()
        statuses = {"iss-00003": _issue_status(domain_models, "iss-00003", "open")}
        dependency_context = domain_models.DepsDependencyContext(
            source_node_id="iss-00003",
            source_issue_id="iss-00003",
            target_node_id="epic-00002",
            target_node_kind="epic",
            target_issue_ids=(),
            expansion="empty",
        )

        result = domain_deps.evaluate_readiness(
            graph,
            issue_depends_on_map={"iss-00003": []},
            target_id=domain_models.NodeId("iss-00003"),
            issue_statuses=statuses,
            dependency_contexts_by_issue_id={"iss-00003": [dependency_context]},
            high_level_statuses_by_node_id={
                "epic-00002": domain_models.DepsHighLevelStatus(
                    node_id="epic-00002",
                    state="closed",
                    source="github",
                )
            },
        )

        assert result.ready
        assert result.guard_reason == "ready"
        assert result.blockers == []
        assert result.node_blockers == []
        assert result.satisfied_dependencies == [dependency_context]
        assert result.satisfied_dependencies[0].lifecycle_state == "closed"
        assert result.satisfied_dependencies[0].lifecycle_source == "github"
        assert result.satisfied_dependencies[0].dependency_disposition == "satisfied"
        assert result.satisfied_dependencies[0].disposition_basis == "lifecycle_closed"

    def test_evaluate_readiness_records_expanded_all_done_high_level_dependency_as_satisfied(self) -> None:
        domain_deps, domain_models, _domain_tree = _runtime_modules()
        graph = self._graph()
        statuses = {
            "iss-00003": _issue_status(domain_models, "iss-00003", "open"),
            "iss-00004": _issue_status(domain_models, "iss-00004", "done"),
            "iss-00005": _issue_status(domain_models, "iss-00005", "done"),
        }
        dependency_context = domain_models.DepsDependencyContext(
            source_node_id="iss-00003",
            source_issue_id="iss-00003",
            target_node_id="epic-00002",
            target_node_kind="epic",
            target_issue_ids=("iss-00004", "iss-00005"),
            expansion="expanded",
        )

        result = domain_deps.evaluate_readiness(
            graph,
            issue_depends_on_map={"iss-00003": ["iss-00004", "iss-00005"]},
            target_id=domain_models.NodeId("iss-00003"),
            issue_statuses=statuses,
            dependency_contexts_by_issue_id={"iss-00003": [dependency_context]},
            high_level_statuses_by_node_id={
                "epic-00002": domain_models.DepsHighLevelStatus(
                    node_id="epic-00002",
                    state="open",
                    source="github",
                )
            },
        )

        assert result.ready
        assert result.guard_reason == "ready"
        assert result.blockers == []
        assert result.node_blockers == []
        assert result.satisfied_dependencies == [dependency_context]
        assert result.satisfied_dependencies[0].lifecycle_state == "open"
        assert result.satisfied_dependencies[0].lifecycle_source == "github"
        assert result.satisfied_dependencies[0].dependency_disposition == "satisfied"
        assert result.satisfied_dependencies[0].disposition_basis == "all_descendant_issues_done"

    def test_evaluate_readiness_fails_closed_for_empty_unknown_high_level_dependency(self) -> None:
        domain_deps, domain_models, _domain_tree = _runtime_modules()
        graph = self._graph()
        statuses = {"iss-00003": _issue_status(domain_models, "iss-00003", "open")}
        dependency_context = domain_models.DepsDependencyContext(
            source_node_id="iss-00003",
            source_issue_id="iss-00003",
            target_node_id="epic-00002",
            target_node_kind="epic",
            target_issue_ids=(),
            expansion="empty",
        )

        result = domain_deps.evaluate_readiness(
            graph,
            issue_depends_on_map={"iss-00003": []},
            target_id=domain_models.NodeId("iss-00003"),
            issue_statuses=statuses,
            dependency_contexts_by_issue_id={"iss-00003": [dependency_context]},
            high_level_statuses_by_node_id={
                "epic-00002": domain_models.DepsHighLevelStatus(
                    node_id="epic-00002",
                    state="unknown",
                    source="none",
                )
            },
        )

        assert not result.ready
        assert result.guard_reason == "unknown"
        assert result.blockers == ["epic-00002"]
        assert result.issue_blockers == []
        assert len(result.node_blockers) == 1
        assert result.node_blockers[0].node_id == "epic-00002"
        assert result.node_blockers[0].reason == "empty_unknown"
        assert result.node_blockers[0].lifecycle_state == "unknown"
        assert result.node_blockers[0].lifecycle_source == "none"
        assert result.node_blockers[0].dependency_disposition == "indeterminate"
        assert result.node_blockers[0].disposition_basis == "empty_unknown_container"
        assert result.dependency_contexts == [dependency_context]
        assert result.dependency_contexts[0].lifecycle_state == "unknown"
        assert result.dependency_contexts[0].lifecycle_source == "none"
        assert result.dependency_contexts[0].dependency_disposition == "indeterminate"
        assert result.dependency_contexts[0].disposition_basis == "empty_unknown_container"

    def test_evaluate_readiness_fails_closed_for_unknown_descendant_high_level_dependency(self) -> None:
        domain_deps, domain_models, _domain_tree = _runtime_modules()
        graph = self._graph()
        statuses = {
            "iss-00003": _issue_status(domain_models, "iss-00003", "open"),
            "iss-00004": _issue_status(domain_models, "iss-00004", "unknown"),
        }
        dependency_context = domain_models.DepsDependencyContext(
            source_node_id="iss-00003",
            source_issue_id="iss-00003",
            target_node_id="epic-00002",
            target_node_kind="epic",
            target_issue_ids=("iss-00004",),
            expansion="expanded",
        )

        result = domain_deps.evaluate_readiness(
            graph,
            issue_depends_on_map={"iss-00003": ["iss-00004"], "iss-00004": []},
            target_id=domain_models.NodeId("iss-00003"),
            issue_statuses=statuses,
            dependency_contexts_by_issue_id={"iss-00003": [dependency_context]},
            high_level_statuses_by_node_id={
                "epic-00002": domain_models.DepsHighLevelStatus(
                    node_id="epic-00002",
                    state="open",
                    source="github",
                )
            },
        )

        assert not result.ready
        assert result.guard_reason == "unknown"
        assert result.blockers == ["iss-00004"]
        assert result.issue_blockers == ["iss-00004"]
        assert result.node_blockers == []
        assert result.satisfied_dependencies == []
        assert len(result.dependency_contexts) == 1
        assert result.dependency_contexts[0].dependency_disposition == "indeterminate"
        assert result.dependency_contexts[0].disposition_basis == "descendant_issue_unknown"

    def test_evaluate_readiness_records_done_descendant_high_level_dependency_as_satisfied(self) -> None:
        domain_deps, domain_models, _domain_tree = _runtime_modules()
        graph = self._graph()
        statuses = {
            "iss-00003": _issue_status(domain_models, "iss-00003", "open"),
            "iss-00005": _issue_status(domain_models, "iss-00005", "done"),
        }
        dependency_context = domain_models.DepsDependencyContext(
            source_node_id="iss-00003",
            source_issue_id="iss-00003",
            target_node_id="epic-00002",
            target_node_kind="epic",
            target_issue_ids=("iss-00005",),
            expansion="expanded",
        )

        result = domain_deps.evaluate_readiness(
            graph,
            issue_depends_on_map={"iss-00003": ["iss-00005"], "iss-00005": []},
            target_id=domain_models.NodeId("iss-00003"),
            issue_statuses=statuses,
            dependency_contexts_by_issue_id={"iss-00003": [dependency_context]},
            high_level_statuses_by_node_id={
                "epic-00002": domain_models.DepsHighLevelStatus(
                    node_id="epic-00002",
                    state="done",
                    source="descendant_aggregate",
                )
            },
        )

        assert result.ready
        assert result.guard_reason == "ready"
        assert result.blockers == []
        assert result.issue_blockers == []
        assert result.node_blockers == []
        assert result.satisfied_dependencies == [dependency_context]
        assert result.satisfied_dependencies[0].lifecycle_state == "done"
        assert result.satisfied_dependencies[0].lifecycle_source == "descendant_aggregate"
        assert result.satisfied_dependencies[0].dependency_disposition == "satisfied"
        assert result.satisfied_dependencies[0].disposition_basis == "all_descendant_issues_done"

    def test_evaluate_readiness_records_open_descendant_high_level_dependency_as_blocking(self) -> None:
        domain_deps, domain_models, _domain_tree = _runtime_modules()
        graph = self._graph()
        statuses = {
            "iss-00003": _issue_status(domain_models, "iss-00003", "open"),
            "iss-00004": _issue_status(domain_models, "iss-00004", "open"),
        }
        dependency_context = domain_models.DepsDependencyContext(
            source_node_id="iss-00003",
            source_issue_id="iss-00003",
            target_node_id="epic-00002",
            target_node_kind="epic",
            target_issue_ids=("iss-00004",),
            expansion="expanded",
        )

        result = domain_deps.evaluate_readiness(
            graph,
            issue_depends_on_map={"iss-00003": ["iss-00004"], "iss-00004": []},
            target_id=domain_models.NodeId("iss-00003"),
            issue_statuses=statuses,
            dependency_contexts_by_issue_id={"iss-00003": [dependency_context]},
            high_level_statuses_by_node_id={
                "epic-00002": domain_models.DepsHighLevelStatus(
                    node_id="epic-00002",
                    state="open",
                    source="github",
                )
            },
        )

        assert not result.ready
        assert result.guard_reason == "blocked"
        assert result.blockers == ["iss-00004"]
        assert result.issue_blockers == ["iss-00004"]
        assert result.node_blockers == []
        assert result.satisfied_dependencies == []
        assert len(result.dependency_contexts) == 1
        assert result.dependency_contexts[0].dependency_disposition == "blocking"
        assert result.dependency_contexts[0].disposition_basis == "descendant_issue_open"

    def test_evaluate_readiness_suppresses_descendant_blockers_for_closed_high_level_dependency(self) -> None:
        domain_deps, domain_models, _domain_tree = _runtime_modules()
        graph = self._graph()
        statuses = {
            "iss-00003": _issue_status(domain_models, "iss-00003", "open"),
            "iss-00004": _issue_status(domain_models, "iss-00004", "open"),
        }
        dependency_context = domain_models.DepsDependencyContext(
            source_node_id="iss-00003",
            source_issue_id="iss-00003",
            target_node_id="epic-00002",
            target_node_kind="epic",
            target_issue_ids=("iss-00004",),
            expansion="expanded",
        )

        result = domain_deps.evaluate_readiness(
            graph,
            issue_depends_on_map={"iss-00003": ["iss-00004"], "iss-00004": []},
            target_id=domain_models.NodeId("iss-00003"),
            issue_statuses=statuses,
            dependency_contexts_by_issue_id={"iss-00003": [dependency_context]},
            high_level_statuses_by_node_id={
                "epic-00002": domain_models.DepsHighLevelStatus(
                    node_id="epic-00002",
                    state="closed",
                    source="github",
                )
            },
        )

        assert result.ready
        assert result.guard_reason == "ready"
        assert result.blockers == []
        assert result.issue_blockers == []
        assert result.node_blockers == []
        assert result.satisfied_dependencies == [dependency_context]
        assert result.satisfied_dependencies[0].dependency_disposition == "satisfied"
        assert result.satisfied_dependencies[0].disposition_basis == "lifecycle_closed"

        inspection = domain_deps.inspect_target_deps(
            graph,
            issue_depends_on_map={"iss-00003": ["iss-00004"], "iss-00004": []},
            target_id=domain_models.NodeId("iss-00003"),
            issue_statuses=statuses,
            active_issue_id=None,
            dependency_contexts_by_issue_id={"iss-00003": [dependency_context]},
            high_level_statuses_by_node_id={
                "epic-00002": domain_models.DepsHighLevelStatus(
                    node_id="epic-00002",
                    state="closed",
                    source="github",
                )
            },
        )

        assert inspection.evaluation.ready
        assert inspection.effective_depends_on == []
        assert inspection.node_states["iss-00003"].ready
        assert inspection.node_states["iss-00003"].effective_depends_on == []

    def test_evaluate_readiness_keeps_direct_issue_dependency_when_closed_high_level_also_references_it(self) -> None:
        domain_deps, domain_models, _domain_tree = _runtime_modules()
        graph = self._graph()
        statuses = {
            "iss-00003": _issue_status(domain_models, "iss-00003", "open"),
            "iss-00004": _issue_status(domain_models, "iss-00004", "open"),
        }
        high_level_context = domain_models.DepsDependencyContext(
            source_node_id="iss-00003",
            source_issue_id="iss-00003",
            target_node_id="epic-00002",
            target_node_kind="epic",
            target_issue_ids=("iss-00004",),
            expansion="expanded",
        )
        direct_context = domain_models.DepsDependencyContext(
            source_node_id="iss-00003",
            source_issue_id="iss-00003",
            target_node_id="iss-00004",
            target_node_kind="issue",
            target_issue_ids=("iss-00004",),
            expansion="issue",
        )

        result = domain_deps.evaluate_readiness(
            graph,
            issue_depends_on_map={"iss-00003": ["iss-00004"], "iss-00004": []},
            target_id=domain_models.NodeId("iss-00003"),
            issue_statuses=statuses,
            dependency_contexts_by_issue_id={"iss-00003": [high_level_context, direct_context]},
            high_level_statuses_by_node_id={
                "epic-00002": domain_models.DepsHighLevelStatus(
                    node_id="epic-00002",
                    state="closed",
                    source="github",
                )
            },
        )

        assert not result.ready
        assert result.guard_reason == "blocked"
        assert result.blockers == ["iss-00004"]
        assert result.issue_blockers == ["iss-00004"]
        assert result.satisfied_dependencies == [high_level_context]

    def test_evaluate_readiness_keeps_open_high_level_path_when_closed_high_level_also_references_issue(self) -> None:
        domain_deps, domain_models, _domain_tree = _runtime_modules()
        graph = self._graph()
        statuses = {
            "iss-00003": _issue_status(domain_models, "iss-00003", "open"),
            "iss-00004": _issue_status(domain_models, "iss-00004", "open"),
        }
        closed_context = domain_models.DepsDependencyContext(
            source_node_id="iss-00003",
            source_issue_id="iss-00003",
            target_node_id="init-00001",
            target_node_kind="initiative",
            target_issue_ids=("iss-00004",),
            expansion="expanded",
        )
        open_context = domain_models.DepsDependencyContext(
            source_node_id="iss-00003",
            source_issue_id="iss-00003",
            target_node_id="epic-00002",
            target_node_kind="epic",
            target_issue_ids=("iss-00004",),
            expansion="expanded",
        )

        result = domain_deps.evaluate_readiness(
            graph,
            issue_depends_on_map={"iss-00003": ["iss-00004"], "iss-00004": []},
            target_id=domain_models.NodeId("iss-00003"),
            issue_statuses=statuses,
            dependency_contexts_by_issue_id={"iss-00003": [closed_context, open_context]},
            high_level_statuses_by_node_id={
                "init-00001": domain_models.DepsHighLevelStatus(
                    node_id="init-00001",
                    state="closed",
                    source="github",
                ),
                "epic-00002": domain_models.DepsHighLevelStatus(
                    node_id="epic-00002",
                    state="open",
                    source="github",
                ),
            },
        )

        assert not result.ready
        assert result.guard_reason == "blocked"
        assert result.issue_blockers == ["iss-00004"]
        assert [(c.target_node_id, c.dependency_disposition) for c in result.satisfied_dependencies] == [
            ("init-00001", "satisfied")
        ]
        assert [
            (c.target_node_id, c.dependency_disposition, c.disposition_basis)
            for c in result.dependency_contexts
        ] == [
            ("init-00001", "satisfied", "lifecycle_closed"),
            ("epic-00002", "blocking", "descendant_issue_open"),
        ]

    def test_evaluate_readiness_fails_closed_for_unknown_high_level_lifecycle_even_when_descendants_done(self) -> None:
        domain_deps, domain_models, _domain_tree = _runtime_modules()
        graph = self._graph()
        statuses = {
            "iss-00003": _issue_status(domain_models, "iss-00003", "open"),
            "iss-00005": _issue_status(domain_models, "iss-00005", "done"),
        }
        dependency_context = domain_models.DepsDependencyContext(
            source_node_id="iss-00003",
            source_issue_id="iss-00003",
            target_node_id="epic-00002",
            target_node_kind="epic",
            target_issue_ids=("iss-00005",),
            expansion="expanded",
        )

        result = domain_deps.evaluate_readiness(
            graph,
            issue_depends_on_map={"iss-00003": ["iss-00005"], "iss-00005": []},
            target_id=domain_models.NodeId("iss-00003"),
            issue_statuses=statuses,
            dependency_contexts_by_issue_id={"iss-00003": [dependency_context]},
            high_level_statuses_by_node_id={
                "epic-00002": domain_models.DepsHighLevelStatus(
                    node_id="epic-00002",
                    state="unknown",
                    source="none",
                )
            },
        )

        assert not result.ready
        assert result.guard_reason == "unknown"
        assert result.issue_blockers == []
        assert len(result.node_blockers) == 1
        assert result.node_blockers[0].node_id == "epic-00002"
        assert result.node_blockers[0].reason == "lifecycle_unknown"
        assert result.satisfied_dependencies == []
        assert len(result.dependency_contexts) == 1
        assert result.dependency_contexts[0].dependency_disposition == "indeterminate"
        assert result.dependency_contexts[0].disposition_basis == "descendant_issue_unknown"

    def test_evaluate_readiness_uses_unknown_descendant_as_blocker_surface_for_unknown_high_level(self) -> None:
        domain_deps, domain_models, _domain_tree = _runtime_modules()
        graph = self._graph()
        statuses = {
            "iss-00003": _issue_status(domain_models, "iss-00003", "open"),
            "iss-00004": _issue_status(domain_models, "iss-00004", "unknown"),
        }
        dependency_context = domain_models.DepsDependencyContext(
            source_node_id="iss-00003",
            source_issue_id="iss-00003",
            target_node_id="epic-00002",
            target_node_kind="epic",
            target_issue_ids=("iss-00004",),
            expansion="expanded",
        )

        result = domain_deps.evaluate_readiness(
            graph,
            issue_depends_on_map={"iss-00003": ["iss-00004"], "iss-00004": []},
            target_id=domain_models.NodeId("iss-00003"),
            issue_statuses=statuses,
            dependency_contexts_by_issue_id={"iss-00003": [dependency_context]},
            high_level_statuses_by_node_id={
                "epic-00002": domain_models.DepsHighLevelStatus(
                    node_id="epic-00002",
                    state="unknown",
                    source="descendant_aggregate",
                )
            },
        )

        assert not result.ready
        assert result.guard_reason == "unknown"
        assert result.issue_blockers == ["iss-00004"]
        assert result.node_blockers == []
        assert result.satisfied_dependencies == []
        assert len(result.dependency_contexts) == 1
        assert result.dependency_contexts[0].dependency_disposition == "indeterminate"
        assert result.dependency_contexts[0].disposition_basis == "descendant_issue_unknown"

    def test_evaluate_readiness_does_not_apply_node_blockers_to_done_source_issue(self) -> None:
        domain_deps, domain_models, _domain_tree = _runtime_modules()
        graph = self._graph()
        statuses = {"iss-00003": _issue_status(domain_models, "iss-00003", "done")}
        dependency_context = domain_models.DepsDependencyContext(
            source_node_id="iss-00003",
            source_issue_id="iss-00003",
            target_node_id="epic-00002",
            target_node_kind="epic",
            target_issue_ids=(),
            expansion="empty",
        )

        result = domain_deps.evaluate_readiness(
            graph,
            issue_depends_on_map={"iss-00003": []},
            target_id=domain_models.NodeId("iss-00003"),
            issue_statuses=statuses,
            dependency_contexts_by_issue_id={"iss-00003": [dependency_context]},
            high_level_statuses_by_node_id={
                "epic-00002": domain_models.DepsHighLevelStatus(
                    node_id="epic-00002",
                    state="open",
                    source="github",
                )
            },
        )

        assert result.ready
        assert result.guard_reason == "ready"
        assert result.blockers == []
        assert result.node_blockers == []

    def test_evaluate_readiness_does_not_apply_node_blockers_to_closed_source_issue(self) -> None:
        domain_deps, domain_models, _domain_tree = _runtime_modules()
        graph = self._graph()
        statuses = {"iss-00003": _issue_status(domain_models, "iss-00003", "closed")}
        dependency_context = domain_models.DepsDependencyContext(
            source_node_id="iss-00003",
            source_issue_id="iss-00003",
            target_node_id="epic-00002",
            target_node_kind="epic",
            target_issue_ids=(),
            expansion="empty",
        )

        result = domain_deps.evaluate_readiness(
            graph,
            issue_depends_on_map={"iss-00003": []},
            target_id=domain_models.NodeId("iss-00003"),
            issue_statuses=statuses,
            dependency_contexts_by_issue_id={"iss-00003": [dependency_context]},
            high_level_statuses_by_node_id={
                "epic-00002": domain_models.DepsHighLevelStatus(
                    node_id="epic-00002",
                    state="open",
                    source="github",
                )
            },
        )

        assert result.ready
        assert result.guard_reason == "ready"
        assert result.blockers == []
        assert result.node_blockers == []

    def _empty_epic_graph(self):
        _domain_deps, domain_models, domain_tree = _runtime_modules()
        root = Path("/repo/spec-dock/initiatives/init-00010-platform")
        return domain_tree.build_graph(
            [
                domain_models.SpecNodeSeed(
                    kind="initiative",
                    id="init-00010",
                    title="Platform",
                    slug="platform",
                    path=root,
                    meta_path=root / ".meta.json",
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=10,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
                domain_models.SpecNodeSeed(
                    kind="epic",
                    id="epic-00011",
                    title="First",
                    slug="first",
                    path=root / "epics" / "epic-00011-first",
                    meta_path=root / "epics" / "epic-00011-first" / ".meta.json",
                    parent_id="init-00010",
                    initiative_id="init-00010",
                    epic_id=None,
                    github_issue_number=11,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
                domain_models.SpecNodeSeed(
                    kind="epic",
                    id="epic-00012",
                    title="Second",
                    slug="second",
                    path=root / "epics" / "epic-00012-second",
                    meta_path=root / "epics" / "epic-00012-second" / ".meta.json",
                    parent_id="init-00010",
                    initiative_id="init-00010",
                    epic_id=None,
                    github_issue_number=12,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
            ]
        )

    def _future_cycle_graph(self):
        _domain_deps, domain_models, domain_tree = _runtime_modules()
        root = Path("/repo/spec-dock/initiatives/init-00020-platform")
        return domain_tree.build_graph(
            [
                domain_models.SpecNodeSeed(
                    kind="initiative",
                    id="init-00020",
                    title="Platform",
                    slug="platform",
                    path=root,
                    meta_path=root / ".meta.json",
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=20,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
                domain_models.SpecNodeSeed(
                    kind="epic",
                    id="epic-00021",
                    title="Empty source",
                    slug="empty-source",
                    path=root / "epics" / "epic-00021-empty-source",
                    meta_path=root / "epics" / "epic-00021-empty-source" / ".meta.json",
                    parent_id="init-00020",
                    initiative_id="init-00020",
                    epic_id=None,
                    github_issue_number=21,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
                domain_models.SpecNodeSeed(
                    kind="epic",
                    id="epic-00022",
                    title="Target parent",
                    slug="target-parent",
                    path=root / "epics" / "epic-00022-target-parent",
                    meta_path=root / "epics" / "epic-00022-target-parent" / ".meta.json",
                    parent_id="init-00020",
                    initiative_id="init-00020",
                    epic_id=None,
                    github_issue_number=22,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
                domain_models.SpecNodeSeed(
                    kind="issue",
                    id="iss-00023",
                    title="Target child",
                    slug="target-child",
                    path=root / "epics" / "epic-00022-target-parent" / "issues" / "iss-00023-target-child",
                    meta_path=root
                    / "epics"
                    / "epic-00022-target-parent"
                    / "issues"
                    / "iss-00023-target-child"
                    / ".meta.json",
                    parent_id="epic-00022",
                    initiative_id="init-00020",
                    epic_id="epic-00022",
                    github_issue_number=23,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
            ]
        )

    def _target_container_cycle_graph(self):
        _domain_deps, domain_models, domain_tree = _runtime_modules()
        root = Path("/repo/spec-dock/initiatives")
        return domain_tree.build_graph(
            [
                domain_models.SpecNodeSeed(
                    kind="initiative",
                    id="init-00001",
                    title="Future source",
                    slug="future-source",
                    path=root / "init-00001-future-source",
                    meta_path=root / "init-00001-future-source" / ".meta.json",
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=1,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
                domain_models.SpecNodeSeed(
                    kind="initiative",
                    id="init-00002",
                    title="Target container",
                    slug="target-container",
                    path=root / "init-00002-target-container",
                    meta_path=root / "init-00002-target-container" / ".meta.json",
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=2,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
                domain_models.SpecNodeSeed(
                    kind="issue",
                    id="iss-00002",
                    title="Target child",
                    slug="target-child",
                    path=root
                    / "init-00002-target-container"
                    / "issues"
                    / "iss-00002-target-child",
                    meta_path=root
                    / "init-00002-target-container"
                    / "issues"
                    / "iss-00002-target-child"
                    / ".meta.json",
                    parent_id="init-00002",
                    initiative_id="init-00002",
                    epic_id=None,
                    github_issue_number=20,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
            ]
        )

    def test_raw_node_dependency_cycle_between_empty_epics_is_rejected(self) -> None:
        domain_deps, _domain_models, _domain_tree = _runtime_modules()
        graph = self._empty_epic_graph()

        with pytest.raises(RuntimeError, match="Dependency cycle detected"):
            domain_deps.validate_raw_node_dependency_graph(
                graph,
                {
                    "epic-00011": ["epic-00012"],
                    "epic-00012": ["epic-00011"],
                },
            )

        with pytest.raises(RuntimeError, match="Dependency cycle detected"):
            domain_deps.ensure_node_dependency_add_would_be_valid(
                graph,
                {"epic-00011": ["epic-00012"]},
                from_node_id="epic-00012",
                to_node_id="epic-00011",
            )

    def test_raw_node_dependency_future_cycle_through_target_descendant_is_rejected(self) -> None:
        domain_deps, _domain_models, _domain_tree = _runtime_modules()
        graph = self._future_cycle_graph()

        with pytest.raises(RuntimeError, match="Dependency cycle detected"):
            domain_deps.validate_raw_node_dependency_graph(
                graph,
                {
                    "epic-00021": ["epic-00022"],
                    "iss-00023": ["epic-00021"],
                },
            )

        with pytest.raises(RuntimeError, match="Dependency cycle detected"):
            domain_deps.ensure_node_dependency_add_would_be_valid(
                graph,
                {"iss-00023": ["epic-00021"]},
                from_node_id="epic-00021",
                to_node_id="epic-00022",
            )

    def test_raw_node_dependency_candidate_rejects_target_container_future_cycle(self) -> None:
        domain_deps, _domain_models, _domain_tree = _runtime_modules()
        graph = self._target_container_cycle_graph()

        with pytest.raises(RuntimeError, match="Dependency cycle detected"):
            domain_deps.ensure_node_dependency_add_would_be_valid(
                graph,
                {"init-00002": ["init-00001"]},
                from_node_id="init-00001",
                to_node_id="iss-00002",
            )

    def test_raw_node_dependency_candidate_rejects_ancestor_container(self) -> None:
        domain_deps, _domain_models, _domain_tree = _runtime_modules()
        graph = self._graph()

        with pytest.raises(RuntimeError, match="ancestor"):
            domain_deps.ensure_node_dependency_add_would_be_valid(
                graph,
                {},
                from_node_id="iss-00003",
                to_node_id="epic-00002",
            )

        with pytest.raises(RuntimeError, match="ancestor"):
            domain_deps.ensure_node_dependency_add_would_be_valid(
                graph,
                {},
                from_node_id="epic-00002",
                to_node_id="init-00001",
            )

    def test_raw_node_dependency_candidate_rejects_descendant(self) -> None:
        domain_deps, _domain_models, _domain_tree = _runtime_modules()
        graph = self._graph()

        with pytest.raises(RuntimeError, match="descendant"):
            domain_deps.ensure_node_dependency_add_would_be_valid(
                graph,
                {},
                from_node_id="epic-00002",
                to_node_id="iss-00003",
            )

    def test_raw_node_dependency_candidate_rejects_self_dependency(self) -> None:
        domain_deps, _domain_models, _domain_tree = _runtime_modules()
        graph = self._graph()

        with pytest.raises(RuntimeError, match="self"):
            domain_deps.ensure_node_dependency_add_would_be_valid(
                graph,
                {},
                from_node_id="epic-00002",
                to_node_id="epic-00002",
            )
