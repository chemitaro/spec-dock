import ast
import sys
import unittest
from pathlib import Path


def _runtime_modules():
    runtime_scripts_dir = (
        Path(__file__).resolve().parents[2]
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
        from spec_dock_runtime.domain import status as domain_status
        from spec_dock_runtime.domain import tree as domain_tree
    finally:
        sys.path.pop(0)

    return domain_deps, domain_models, domain_status, domain_tree


def _shared_graph(domain_models, domain_tree):
    seeds = [
        domain_models.SpecNodeSeed(
            kind="initiative",
            id="init-local-00001",
            title="Auth Platform",
            slug="auth-platform",
            path=Path("/repo/spec-dock/initiatives/init-local-00001-auth-platform"),
            meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-auth-platform/.meta.json"),
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=101,
        ),
        domain_models.SpecNodeSeed(
            kind="epic",
            id="epic-local-00001",
            title="JWT Auth",
            slug="jwt-auth",
            path=Path("/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth"),
            meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/.meta.json"),
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=201,
        ),
        domain_models.SpecNodeSeed(
            kind="issue",
            id="iss-local-00001",
            title="Dependency One",
            slug="dependency-one",
            path=Path(
                "/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00001-dependency-one"
            ),
            meta_path=Path(
                "/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00001-dependency-one/.meta.json"
            ),
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
        ),
        domain_models.SpecNodeSeed(
            kind="issue",
            id="iss-local-00002",
            title="Dependency Two",
            slug="dependency-two",
            path=Path(
                "/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00002-dependency-two"
            ),
            meta_path=Path(
                "/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00002-dependency-two/.meta.json"
            ),
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=302,
        ),
        domain_models.SpecNodeSeed(
            kind="issue",
            id="iss-local-00003",
            title="Target Issue",
            slug="target-issue",
            path=Path(
                "/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00003-target-issue"
            ),
            meta_path=Path(
                "/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00003-target-issue/.meta.json"
            ),
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=303,
        ),
    ]
    return domain_tree.build_graph(seeds)


class TestRuntimeDomainS03(unittest.TestCase):
    def test_resolve_issue_statuses_selects_source(self) -> None:
        _domain_deps, domain_models, domain_status, domain_tree = _runtime_modules()

        graph = _shared_graph(domain_models, domain_tree)
        snapshots = [
            domain_models.IssueSnapshot(
                issue_number=301,
                state="CLOSED",
                title="Dependency One",
                labels=[],
                updated_at="2026-01-01T00:00:00Z",
                url="https://example.invalid/301",
            )
        ]
        cached = {
            "iss-local-00001": "open",
            "iss-local-00002": "done",
            "iss-local-00003": "open",
        }

        github_statuses = domain_status.resolve_issue_statuses(
            graph,
            github_enabled=True,
            issue_snapshots=snapshots,
            cached_issue_status_by_id=cached,
        )
        self.assertEqual(github_statuses["iss-local-00001"].status, "done")
        self.assertEqual(github_statuses["iss-local-00001"].source, "github")
        self.assertEqual(github_statuses["iss-local-00002"].status, "unknown")
        self.assertEqual(github_statuses["iss-local-00002"].source, "unknown")

        cache_statuses = domain_status.resolve_issue_statuses(
            graph,
            github_enabled=False,
            issue_snapshots=snapshots,
            cached_issue_status_by_id=cached,
        )
        self.assertEqual(cache_statuses["iss-local-00001"].status, "open")
        self.assertEqual(cache_statuses["iss-local-00001"].source, "cache")
        self.assertEqual(cache_statuses["iss-local-00002"].status, "done")
        self.assertEqual(cache_statuses["iss-local-00002"].source, "cache")

    def test_build_progress_map_aggregates_counts(self) -> None:
        _domain_deps, domain_models, domain_status, domain_tree = _runtime_modules()

        graph = _shared_graph(domain_models, domain_tree)
        issue_statuses = {
            "iss-local-00001": domain_models.IssueStatusSnapshot("iss-local-00001", "done", "github", 301),
            "iss-local-00002": domain_models.IssueStatusSnapshot("iss-local-00002", "open", "github", 302),
            "iss-local-00003": domain_models.IssueStatusSnapshot("iss-local-00003", "unknown", "unknown", 303),
        }

        progress = domain_status.build_progress_map(graph, issue_statuses)
        self.assertEqual(progress.by_node_id["epic-local-00001"], {"total": 3, "done": 1, "open": 1, "unknown": 1})
        self.assertEqual(progress.by_node_id["init-local-00001"], {"total": 3, "done": 1, "open": 1, "unknown": 1})
        self.assertEqual(progress.counts, {"total": 3, "done": 1, "open": 1, "unknown": 1})

    def test_build_effective_deps_map_merges_parent_dependencies(self) -> None:
        domain_deps, domain_models, _domain_status, domain_tree = _runtime_modules()

        graph = _shared_graph(domain_models, domain_tree)
        issue_depends_on_map = {
            "init-local-00001": ["iss-local-00002"],
            "epic-local-00001": ["iss-local-00001"],
            "iss-local-00003": ["iss-local-00001"],
        }

        effective = domain_deps.build_effective_deps_map(graph, issue_depends_on_map)
        self.assertEqual(effective["iss-local-00003"], ["iss-local-00001", "iss-local-00002"])

    def test_evaluate_readiness_uses_explicit_issue_depends_on_map(self) -> None:
        domain_deps, domain_models, _domain_status, domain_tree = _runtime_modules()

        graph = _shared_graph(domain_models, domain_tree)
        issue_statuses = {
            "iss-local-00001": domain_models.IssueStatusSnapshot("iss-local-00001", "open", "cache", 301),
            "iss-local-00002": domain_models.IssueStatusSnapshot("iss-local-00002", "open", "cache", 302),
            "iss-local-00003": domain_models.IssueStatusSnapshot("iss-local-00003", "open", "cache", 303),
        }
        issue_depends_on_map = {
            "iss-local-00001": ["iss-local-00002"],
            "iss-local-00002": [],
            "iss-local-00003": ["iss-local-00001"],
        }

        result = domain_deps.evaluate_readiness(
            graph,
            issue_depends_on_map,
            domain_models.NodeId("iss-local-00003"),
            issue_statuses,
        )
        self.assertFalse(result.ready)
        self.assertEqual(result.guard_reason, "blocked")
        self.assertEqual(result.blockers, ["iss-local-00001", "iss-local-00002"])
        self.assertEqual(result.blockers_top, ["iss-local-00001", "iss-local-00002"])
        self.assertEqual(result.closure, ["iss-local-00001", "iss-local-00002"])

    def test_evaluate_readiness_reports_unknown_guard_reason(self) -> None:
        domain_deps, domain_models, _domain_status, domain_tree = _runtime_modules()

        graph = _shared_graph(domain_models, domain_tree)
        issue_statuses = {
            "iss-local-00001": domain_models.IssueStatusSnapshot("iss-local-00001", "open", "cache", 301),
            "iss-local-00002": domain_models.IssueStatusSnapshot("iss-local-00002", "unknown", "cache", 302),
            "iss-local-00003": domain_models.IssueStatusSnapshot("iss-local-00003", "open", "cache", 303),
        }
        issue_depends_on_map = {
            "iss-local-00001": ["iss-local-00002"],
            "iss-local-00002": [],
            "iss-local-00003": ["iss-local-00001"],
        }

        result = domain_deps.evaluate_readiness(
            graph,
            issue_depends_on_map,
            domain_models.NodeId("iss-local-00003"),
            issue_statuses,
        )
        self.assertFalse(result.ready)
        self.assertEqual(result.guard_reason, "unknown")

    def test_inspect_target_deps_active_decoration_only(self) -> None:
        domain_deps, domain_models, _domain_status, domain_tree = _runtime_modules()

        graph = _shared_graph(domain_models, domain_tree)
        issue_statuses = {
            "iss-local-00001": domain_models.IssueStatusSnapshot("iss-local-00001", "open", "cache", 301),
            "iss-local-00002": domain_models.IssueStatusSnapshot("iss-local-00002", "done", "cache", 302),
            "iss-local-00003": domain_models.IssueStatusSnapshot("iss-local-00003", "open", "cache", 303),
        }
        issue_depends_on_map = {
            "iss-local-00001": ["iss-local-00002"],
            "iss-local-00002": [],
            "iss-local-00003": ["iss-local-00001"],
        }

        without_active = domain_deps.inspect_target_deps(
            graph,
            issue_depends_on_map,
            domain_models.NodeId("iss-local-00003"),
            issue_statuses,
            active_issue_id=None,
        )
        with_active = domain_deps.inspect_target_deps(
            graph,
            issue_depends_on_map,
            domain_models.NodeId("iss-local-00003"),
            issue_statuses,
            active_issue_id="iss-local-00001",
        )

        self.assertEqual(without_active.evaluation, with_active.evaluation)
        self.assertNotEqual(
            without_active.node_states["iss-local-00001"].status,
            with_active.node_states["iss-local-00001"].status,
        )
        self.assertEqual(with_active.node_states["iss-local-00001"].status, "doing")

    def test_build_deps_state_and_cycle_validation(self) -> None:
        domain_deps, domain_models, _domain_status, domain_tree = _runtime_modules()

        graph = _shared_graph(domain_models, domain_tree)

        with self.assertRaises(RuntimeError):
            domain_deps.validate_deps_cycles(
                {
                    "iss-local-00001": ["iss-local-00002"],
                    "iss-local-00002": ["iss-local-00001"],
                }
            )

        issue_statuses = {
            "iss-local-00001": domain_models.IssueStatusSnapshot("iss-local-00001", "open", "cache", 301),
            "iss-local-00002": domain_models.IssueStatusSnapshot("iss-local-00002", "done", "cache", 302),
            "iss-local-00003": domain_models.IssueStatusSnapshot("iss-local-00003", "open", "cache", 303),
        }
        state = domain_deps.build_deps_state(
            graph,
            {
                "iss-local-00001": ["iss-local-00002"],
                "iss-local-00002": [],
                "iss-local-00003": ["iss-local-00001"],
            },
            issue_statuses,
            domain_models.ActiveSelection(
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                issue_id="iss-local-00001",
            ),
            warnings=["gh_index_incomplete"],
        )
        self.assertEqual(state.warnings, ["gh_index_incomplete"])
        by_id = {node.node_id: node for node in state.nodes}
        self.assertEqual(by_id["iss-local-00001"].status, "doing")
        self.assertTrue(by_id["iss-local-00001"].ready)
        self.assertEqual(by_id["iss-local-00003"].status, "blocked")
        self.assertFalse(by_id["iss-local-00003"].ready)

    def test_domain_modules_have_no_shell_io_imports(self) -> None:
        domain_deps, _domain_models, domain_status, _domain_tree = _runtime_modules()
        module_paths = [
            domain_status.__file__,
            domain_deps.__file__,
            domain_status.__file__.replace("status.py", "active.py"),
        ]
        forbidden_import_roots = {
            "argparse",
            "json",
            "os",
            "shutil",
            "subprocess",
            "sys",
        }

        for module_path in module_paths:
            source = Path(module_path).read_text(encoding="utf-8")
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        root = alias.name.split(".", 1)[0]
                        self.assertNotIn(root, forbidden_import_roots, f"Forbidden import '{root}' in {module_path}")
                elif isinstance(node, ast.ImportFrom):
                    if node.module is None:
                        continue
                    root = node.module.split(".", 1)[0]
                    self.assertNotIn(root, forbidden_import_roots, f"Forbidden import '{root}' in {module_path}")


if __name__ == "__main__":
    unittest.main()
