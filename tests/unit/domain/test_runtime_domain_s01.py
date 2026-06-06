import ast
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
        from spec_dock_runtime import app as runtime_app
        from spec_dock_runtime import ids as legacy_ids
        from spec_dock_runtime.domain import ids as domain_ids
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.domain import tree as domain_tree
        from spec_dock_runtime.domain import validation as domain_validation
    finally:
        sys.path.pop(0)

    return runtime_app, legacy_ids, domain_ids, domain_models, domain_tree, domain_validation


class TestRuntimeDomainS01:
    def test_domain_ids_title_helpers(self) -> None:
        _, _, domain_ids, _, _, _ = _runtime_modules()

        title, slug = domain_ids.resolve_input_title_and_slug("Add Refresh Token", None)
        assert title == "Add Refresh Token"
        assert slug == "add-refresh-token"

    def test_domain_ids_parse_format_helpers(self) -> None:
        _, _, domain_ids, _, _, _ = _runtime_modules()

        assert domain_ids.format_id("epic", 7) == "epic-00007"
        assert domain_ids.parse_id("EPIC-local-00007") == ("epic", True, 7)

    def test_domain_ids_deps_sort_key_helper(self) -> None:
        _, _, domain_ids, _, _, _ = _runtime_modules()

        node_ids = ["iss-local-00002", "iss-00010", "iss-local-00001", "iss-00002"]
        assert sorted(node_ids, key=domain_ids.deps_node_sort_key) == [
            "iss-00002",
            "iss-00010",
            "iss-local-00001",
            "iss-local-00002",
        ]

    def test_build_graph_from_node_seeds(self) -> None:
        _, _, _, domain_models, domain_tree, _ = _runtime_modules()

        seed = domain_models.SpecNodeSeed(
            kind="initiative",
            id="init-local-00001",
            title="Auth Platform",
            slug="auth-platform",
            path=Path("/repo/spec-dock/initiatives/init-local-00001-auth-platform"),
            meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-auth-platform/.meta.json"),
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        )
        graph = domain_tree.build_graph([seed])

        assert "init-local-00001" in graph.nodes_by_id
        assert graph.nodes_by_id["init-local-00001"].kind == "initiative"

    def test_validate_graph_and_deps_detects_structural_error(self) -> None:
        _, _, _, domain_models, domain_tree, domain_validation = _runtime_modules()

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
                github_issue_number=None,
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
                github_issue_number=None,
            ),
            domain_models.SpecNodeSeed(
                kind="issue",
                id="iss-local-00001",
                title="Add Refresh Token",
                slug="add-refresh-token",
                path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00001-add-refresh-token"
                ),
                meta_path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00001-add-refresh-token/.meta.json"
                ),
                parent_id="epic-local-99999",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=None,
            ),
        ]
        graph = domain_tree.build_graph(seeds)
        report = domain_validation.validate_graph_and_deps(graph, repo_root=Path("/repo"))

        assert report.warnings == []
        assert report.errors == [
            "initiative missing github.issue_number: "
            "spec-dock/initiatives/init-local-00001-auth-platform/.meta.json. "
            "initiative/epic/issue nodes must have explicit GitHub linkage under the create contract."
        ]
        assert not any("Missing required artifact" in error for error in report.errors)

    def test_legacy_ids_module_delegates_to_domain(self) -> None:
        _, legacy_ids, domain_ids, _, _, _ = _runtime_modules()

        calls: list[str] = []
        original_parse_id = domain_ids.parse_id

        def _fake_parse_id(value: str) -> tuple[str, bool, int]:
            calls.append(value)
            return ("iss", False, 42)

        domain_ids.parse_id = _fake_parse_id
        try:
            resolved = legacy_ids._parse_id("iss-00042")
        finally:
            domain_ids.parse_id = original_parse_id

        assert resolved == ("iss", False, 42)
        assert calls == ["iss-00042"]

    def test_app_validate_nodes_delegates_to_domain_validation(self) -> None:
        runtime_app, _, _, domain_models, _, _ = _runtime_modules()

        calls: dict[str, object] = {}
        original_build_graph = runtime_app._domain_build_graph
        original_validate_graph_and_deps = runtime_app._domain_validate_graph_and_deps

        def _fake_build_graph(seeds):
            calls["seeds"] = seeds
            return domain_models.SpecGraph(nodes_by_id={})

        def _fake_validate_graph_and_deps(graph, repo_root=None):
            calls["graph"] = graph
            calls["repo_root"] = repo_root
            return domain_models.ValidationReport(errors=[], warnings=[])

        runtime_app._domain_build_graph = _fake_build_graph
        runtime_app._domain_validate_graph_and_deps = _fake_validate_graph_and_deps
        try:
            nodes = {
                "init-local-00001": runtime_app._Node(
                    type="initiative",
                    id="init-local-00001",
                    title="Auth Platform",
                    slug="auth-platform",
                    path=Path("/repo/spec-dock/initiatives/init-local-00001-auth-platform"),
                    meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-auth-platform/.meta.json"),
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                )
            }
            runtime_app._validate_nodes(nodes, repo_root=Path("/repo"))
        finally:
            runtime_app._domain_build_graph = original_build_graph
            runtime_app._domain_validate_graph_and_deps = original_validate_graph_and_deps

        seeds = calls.get("seeds")
        assert isinstance(seeds, list)
        assert len(seeds) == 1
        assert seeds[0].id == "init-local-00001"
        assert calls.get("repo_root") == Path("/repo")

    def test_app_validate_github_issue_numbers_unique_delegates_to_domain_validation(self) -> None:
        runtime_app, _, _, domain_models, _, _ = _runtime_modules()

        calls: dict[str, object] = {}
        original_build_graph = runtime_app._domain_build_graph
        original_validate_unique = runtime_app._domain_validate_github_issue_numbers_unique

        def _fake_build_graph(seeds):
            calls["seeds"] = seeds
            return domain_models.SpecGraph(nodes_by_id={})

        def _fake_validate_unique(graph, repo_root=None):
            calls["graph"] = graph
            calls["repo_root"] = repo_root

        runtime_app._domain_build_graph = _fake_build_graph
        runtime_app._domain_validate_github_issue_numbers_unique = _fake_validate_unique
        try:
            nodes = {
                "iss-local-00001": runtime_app._Node(
                    type="issue",
                    id="iss-local-00001",
                    title="Add Refresh Token",
                    slug="add-refresh-token",
                    path=Path(
                        "/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00001-add-refresh-token"
                    ),
                    meta_path=Path(
                        "/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00001-add-refresh-token/.meta.json"
                    ),
                    parent_id="epic-local-00001",
                    initiative_id="init-local-00001",
                    epic_id="epic-local-00001",
                    github_issue_number=123,
                )
            }
            runtime_app._validate_github_issue_numbers_unique(nodes, repo_root=Path("/repo"))
        finally:
            runtime_app._domain_build_graph = original_build_graph
            runtime_app._domain_validate_github_issue_numbers_unique = original_validate_unique

        seeds = calls.get("seeds")
        assert isinstance(seeds, list)
        assert len(seeds) == 1
        assert seeds[0].id == "iss-local-00001"
        assert calls.get("repo_root") == Path("/repo")

    def test_domain_modules_have_no_shell_io_imports(self) -> None:
        _, _, _, _, _, domain_validation = _runtime_modules()
        module_paths = [
            domain_validation.__file__,
            domain_validation.__file__.replace("validation.py", "ids.py"),
            domain_validation.__file__.replace("validation.py", "models.py"),
            domain_validation.__file__.replace("validation.py", "tree.py"),
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
            imported_roots: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_roots.add(alias.name.split(".", 1)[0])
                if isinstance(node, ast.ImportFrom) and node.module:
                    imported_roots.add(node.module.split(".", 1)[0])

            assert imported_roots.isdisjoint(forbidden_import_roots), (
                f"forbidden import detected in {module_path}: {sorted(imported_roots & forbidden_import_roots)}"
            )
