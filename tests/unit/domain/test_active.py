import sys
import unittest
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
        from spec_dock_runtime.domain import active as domain_active
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.domain import tree as domain_tree
    finally:
        sys.path.pop(0)
    return domain_active, domain_models, domain_tree


class TestActiveDomain(unittest.TestCase):
    def _graph(self):
        _domain_active, domain_models, domain_tree = _runtime_modules()
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
                    github_issue_number=101,
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
                    github_issue_number=201,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
                domain_models.SpecNodeSeed(
                    kind="issue",
                    id="iss-00123",
                    title="Add Refresh Token",
                    slug="add-refresh-token",
                    path=root / "epics" / "epic-00002-delivery" / "issues" / "iss-00123-add-refresh-token",
                    meta_path=root / "epics" / "epic-00002-delivery" / "issues" / "iss-00123-add-refresh-token" / ".meta.json",
                    parent_id="epic-00002",
                    initiative_id="init-00001",
                    epic_id="epic-00002",
                    github_issue_number=123,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
            ]
        )

    def test_select_active_chain_resolves_missing_layers_as_placeholders_without_cli(self) -> None:
        _domain_active, domain_models, domain_tree = _runtime_modules()
        graph = self._graph()

        initiative = domain_tree.select_active_chain(graph, domain_models.NodeId("init-00001"))
        self.assertEqual(initiative.initiative_id, "init-00001")
        self.assertIsNone(initiative.epic_id)
        self.assertIsNone(initiative.issue_id)

        epic = domain_tree.select_active_chain(graph, domain_models.NodeId("epic-00002"))
        self.assertEqual(epic.initiative_id, "init-00001")
        self.assertEqual(epic.epic_id, "epic-00002")
        self.assertIsNone(epic.issue_id)

        issue = domain_tree.select_active_chain(graph, domain_models.NodeId("iss-00123"))
        self.assertEqual(issue.initiative_id, "init-00001")
        self.assertEqual(issue.epic_id, "epic-00002")
        self.assertEqual(issue.issue_id, "iss-00123")

    def test_branch_decision_falls_back_to_id_for_non_ascii_or_invalid_slug_without_git(self) -> None:
        domain_active, _domain_models, _domain_tree = _runtime_modules()
        node = self._graph().nodes_by_id["iss-00123"]

        normal = domain_active.resolve_branch_decision(node)
        self.assertEqual(normal.desired, "iss-00123-add-refresh-token")
        self.assertEqual(normal.warnings, ())

        non_ascii_node = node.__class__(**{**node.__dict__, "slug": "日本語"})
        non_ascii = domain_active.resolve_branch_decision(non_ascii_node)
        self.assertEqual(non_ascii.desired, "iss-00123")
        self.assertIn("non-ascii", non_ascii.warnings[0])

        invalid_ref = domain_active.resolve_branch_decision(node, candidate_is_valid=False)
        self.assertEqual(invalid_ref.desired, "iss-00123")
        self.assertIn("invalid ref", invalid_ref.warnings[0])

    def test_infer_active_node_from_branch_prefers_repo_scoped_issue_match_without_cli(self) -> None:
        domain_active, _domain_models, _domain_tree = _runtime_modules()
        graph = self._graph()

        node, reason = domain_active.infer_active_node_from_branch(
            graph,
            branch="feature/issue-123-refresh",
            current_repo_slug="example/repo",
        )

        self.assertIsNotNone(node)
        self.assertEqual(node.id, "iss-00123")
        self.assertIn("matched github.issue_number=123", reason)


if __name__ == "__main__":
    unittest.main()
