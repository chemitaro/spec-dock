import sys
from pathlib import Path

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
        from spec_dock_runtime.domain import deps as domain_deps
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.domain import tree as domain_tree
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
