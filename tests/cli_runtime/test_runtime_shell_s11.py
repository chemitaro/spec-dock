import argparse
import ast
import contextlib
import io
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

_LEGACY_HELPER_MODULES = {"io_json", "github", "render_md", "render_puml", "active", "nodes", "ids"}


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
        from spec_dock_runtime import app as runtime_app
        from spec_dock_runtime.application import contracts as app_contracts
        from spec_dock_runtime.cli import dispatch as cli_dispatch
        from spec_dock_runtime.cli import parser as cli_parser
        from spec_dock_runtime.cli import registry as cli_registry
        from spec_dock_runtime.commands import contracts as cmd_contracts
        from spec_dock_runtime.domain import models as domain_models
    finally:
        sys.path.pop(0)
    return (
        runtime_app,
        app_contracts,
        cli_dispatch,
        cli_parser,
        cli_registry,
        cmd_contracts,
        domain_models,
    )


def _iter_import_modules(tree: ast.AST) -> list[str]:
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        if isinstance(node, ast.ImportFrom):
            if node.module is None:
                imported.extend(alias.name for alias in node.names if alias.name != "*")
                continue
            imported.append(node.module)
            if node.module == "spec_dock_runtime":
                imported.extend(f"{node.module}.{alias.name}" for alias in node.names if alias.name != "*")
    return imported


def _normalize_import_module(imported: str) -> str:
    return imported.removeprefix("spec_dock_runtime.")


def _import_root(imported: str) -> str:
    return _normalize_import_module(imported).split(".", 1)[0]


class RuntimeShellS11Tests(unittest.TestCase):
    def test_import_scan_detects_legacy_helper_import_styles(self) -> None:
        tree = ast.parse(
            "import spec_dock_runtime.io_json\n"
            "from spec_dock_runtime import io_json\n"
            "from .. import io_json\n"
        )
        imported = _iter_import_modules(tree)
        self.assertIn("spec_dock_runtime.io_json", imported)
        self.assertIn("io_json", imported)

        roots = {_import_root(module) for module in imported}
        self.assertIn("io_json", roots & _LEGACY_HELPER_MODULES)

    def test_import_root_normalizes_fully_qualified_layer_modules(self) -> None:
        tree = ast.parse(
            "import spec_dock_runtime.domain.ids\n"
            "from spec_dock_runtime import infra\n"
        )
        imported = _iter_import_modules(tree)
        roots = {_import_root(module) for module in imported}
        self.assertIn("domain", roots)
        self.assertIn("infra", roots)

    def test_parser_help_and_argparse_failure_regression(self) -> None:
        (_runtime_app, _app_contracts, _cli_dispatch, cli_parser, cli_registry, _cmd_contracts, _domain_models) = (
            _runtime_modules()
        )

        registry = cli_registry.build_registry()
        parser = cli_parser.build_parser(registry)

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as cm:
                parser.parse_args(["new", "--help"])
        self.assertEqual(cm.exception.code, 0)
        self.assertIn("Create a new initiative", stdout.getvalue())

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as cm:
                parser.parse_args(["active", "set", "--initiative", "1"])
        self.assertEqual(cm.exception.code, 2)
        error_text = stderr.getvalue()
        self.assertIn("unrecognized arguments: --initiative", error_text)
        self.assertIn("'active set' supports explicit targets:", error_text)
        self.assertIn("active set --id <node-id>", error_text)

    def test_dispatch_business_exit_ownership(self) -> None:
        (_runtime_app, _app_contracts, cli_dispatch, _cli_parser, _cli_registry, cmd_contracts, _domain_models) = (
            _runtime_modules()
        )

        class _Args(cmd_contracts.CommandArgs):
            pass

        def _add_arguments(_parser):
            return None

        def _args_factory(_ns):
            return _Args()

        def _run(_args, _use_cases):
            return cmd_contracts.CommandOutcome(
                exit_code=3,
                text=SimpleNamespace(
                    stdout_lines=[],
                    stderr_lines=["spec-dock: blocked (deps check) target=iss-local-00001 ready=false blockers=1"],
                    warnings=["deps_topology_external_ref:iss-local-99999"],
                ),
            )

        registry = cmd_contracts.CommandRegistry(
            items={
                "dummy": cmd_contracts.CommandSpec(
                    add_arguments=_add_arguments,
                    args_factory=_args_factory,
                    run=_run,
                )
            }
        )
        ns = argparse.Namespace(command_key="dummy")
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = cli_dispatch.dispatch(ns, registry, None)  # type: ignore[arg-type]
        self.assertEqual(exit_code, 3)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(
            stderr.getvalue().splitlines(),
            [
                "spec-dock: (warn) deps_topology_external_ref:iss-local-99999",
                "spec-dock: blocked (deps check) target=iss-local-00001 ready=false blockers=1",
            ],
        )

    def test_representative_command_wrapper_smoke(self) -> None:
        (_runtime_app, app_contracts, cli_dispatch, cli_parser, cli_registry, _cmd_contracts, domain_models) = (
            _runtime_modules()
        )

        captured: dict[str, object] = {}

        def _unexpected(_req):
            raise AssertionError("Unexpected use case call")

        def _set_active(req):
            captured["request"] = req
            return app_contracts.ActiveSetResult(
                selection=domain_models.ActiveSelection(
                    initiative_id="init-00123",
                    epic_id=None,
                    issue_id=None,
                ),
                branch=None,
                manifest_written=True,
                pointer_updated=True,
                warnings=[],
            )

        use_cases = app_contracts.UseCases(
            create_initiative=_unexpected,
            create_epic=_unexpected,
            create_issue=_unexpected,
            create_discussion_doc=_unexpected,
            import_initiative=_unexpected,
            import_epic=_unexpected,
            import_issue=_unexpected,
            set_active=_set_active,
            show_active=_unexpected,
            clear_active=_unexpected,
            sync=_unexpected,
            check_deps=_unexpected,
            validate_tree=_unexpected,
        )

        registry = cli_registry.build_registry()
        parser = cli_parser.build_parser(registry)
        ns = parser.parse_args(["active", "set", "123"])
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = cli_dispatch.dispatch(ns, registry, use_cases)

        self.assertEqual(exit_code, 0)
        request = captured.get("request")
        self.assertIsNotNone(request)
        self.assertEqual(request.target.kind, "github_issue")
        self.assertEqual(request.target.github_issue_number, 123)
        self.assertIn("spec-dock: ok (active set) target=github#123", stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")

    def test_close_command_wrapper_smoke(self) -> None:
        (_runtime_app, app_contracts, cli_dispatch, cli_parser, cli_registry, _cmd_contracts, domain_models) = (
            _runtime_modules()
        )

        captured: dict[str, object] = {}

        def _close_node(req):
            captured["request"] = req
            return app_contracts.CloseNodeResult(
                node_id="iss-local-00001",
                node_kind="issue",
                github_issue_number=123,
                issue_snapshot=domain_models.IssueSnapshot(
                    issue_number=123,
                    state="CLOSED",
                    title="Issue 123",
                    labels=[],
                    updated_at="2026-04-09T00:00:00Z",
                    url="https://github.com/example/repo/issues/123",
                    repo_owner="example",
                    repo_name="repo",
                ),
                already_closed=False,
                warnings=[],
            )

        use_cases = app_contracts.UseCases(
            create_initiative=lambda req: None,  # type: ignore[return-value]
            create_epic=lambda req: None,  # type: ignore[return-value]
            create_issue=lambda req: None,  # type: ignore[return-value]
            create_discussion_doc=lambda req: None,  # type: ignore[return-value]
            import_initiative=lambda req: None,  # type: ignore[return-value]
            import_epic=lambda req: None,  # type: ignore[return-value]
            import_issue=lambda req: None,  # type: ignore[return-value]
            set_active=lambda req: None,  # type: ignore[return-value]
            show_active=lambda req: None,  # type: ignore[return-value]
            clear_active=lambda req: None,  # type: ignore[return-value]
            sync=lambda req: None,  # type: ignore[return-value]
            check_deps=lambda req: None,  # type: ignore[return-value]
            validate_tree=lambda req: None,  # type: ignore[return-value]
            close_node=_close_node,
        )

        registry = cli_registry.build_registry()
        parser = cli_parser.build_parser(registry)
        ns = parser.parse_args(["close", "--github-issue", "123"])
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = cli_dispatch.dispatch(ns, registry, use_cases)

        self.assertEqual(exit_code, 0)
        request = captured.get("request")
        self.assertIsNotNone(request)
        self.assertEqual(request.target.kind, "github_issue")
        self.assertEqual(request.target.github_issue_number, 123)
        self.assertIn("spec-dock: ok (close) target=github#123", stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")

    def test_deps_json_stdout_only_and_text_warning_regression(self) -> None:
        (_runtime_app, app_contracts, cli_dispatch, cli_parser, cli_registry, _cmd_contracts, domain_models) = (
            _runtime_modules()
        )

        inspection = domain_models.TargetDepsInspection(
            target_id=domain_models.NodeId("iss-local-00001"),
            evaluation=domain_models.DepsEvaluation(
                ready=True,
                guard_reason="ready",
                blockers=[],
                blockers_top=[],
                closure=[],
            ),
            node_states={},
            effective_depends_on=[],
            warnings=[],
        )
        result = app_contracts.DepsCheckResult(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
            inspection=inspection,
            warnings=["gh_fetch_failed"],
        )

        use_cases = app_contracts.UseCases(
            create_initiative=lambda req: None,  # type: ignore[return-value]
            create_epic=lambda req: None,  # type: ignore[return-value]
            create_issue=lambda req: None,  # type: ignore[return-value]
            create_discussion_doc=lambda req: None,  # type: ignore[return-value]
            import_initiative=lambda req: None,  # type: ignore[return-value]
            import_epic=lambda req: None,  # type: ignore[return-value]
            import_issue=lambda req: None,  # type: ignore[return-value]
            set_active=lambda req: None,  # type: ignore[return-value]
            show_active=lambda req: None,  # type: ignore[return-value]
            clear_active=lambda req: None,  # type: ignore[return-value]
            sync=lambda req: None,  # type: ignore[return-value]
            check_deps=lambda req: result,
            validate_tree=lambda req: None,  # type: ignore[return-value]
        )

        registry = cli_registry.build_registry()
        parser = cli_parser.build_parser(registry)

        ns_json = parser.parse_args(["deps", "check", "iss-local-00001", "--json"])
        stdout_json = io.StringIO()
        stderr_json = io.StringIO()
        with contextlib.redirect_stdout(stdout_json), contextlib.redirect_stderr(stderr_json):
            exit_code_json = cli_dispatch.dispatch(ns_json, registry, use_cases)
        self.assertEqual(exit_code_json, 0)
        self.assertEqual(stderr_json.getvalue(), "")
        payload = json.loads(stdout_json.getvalue())
        self.assertEqual(payload["warnings"], ["gh_fetch_failed"])

        ns_text = parser.parse_args(["deps", "check", "iss-local-00001"])
        stdout_text = io.StringIO()
        stderr_text = io.StringIO()
        with contextlib.redirect_stdout(stdout_text), contextlib.redirect_stderr(stderr_text):
            exit_code_text = cli_dispatch.dispatch(ns_text, registry, use_cases)
        self.assertEqual(exit_code_text, 0)
        self.assertIn("spec-dock: ok (deps check)", stdout_text.getvalue())
        self.assertIn("spec-dock: (warn) gh_fetch_failed", stderr_text.getvalue())

    def test_staged_delegation_path_regression(self) -> None:
        (runtime_app, _app_contracts, _cli_dispatch, _cli_parser, _cli_registry, _cmd_contracts, _domain_models) = (
            _runtime_modules()
        )

        calls: list[object] = []

        class _ParserStub:
            def parse_args(self, argv):
                calls.append(("parse_args", list(argv)))
                return argparse.Namespace(command_key="validate")

        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_build_registry = runtime_app._cli_build_registry
        original_build_parser = runtime_app._cli_build_parser
        original_build_runtime = runtime_app._cli_build_runtime
        original_dispatch = runtime_app._cli_dispatch

        runtime_app._find_specdock_dir = lambda: Path("/tmp/repo/spec-dock")
        runtime_app._cli_build_registry = lambda: "registry"
        runtime_app._cli_build_parser = lambda registry: _ParserStub()
        runtime_app._cli_build_runtime = lambda _specdock_dir: SimpleNamespace(use_cases="use_cases")
        runtime_app._cli_dispatch = lambda ns, registry, use_cases: (
            calls.append(("dispatch", ns.command_key, registry, use_cases)) or 17
        )

        try:
            exit_code = runtime_app.main(["validate"])
        finally:
            runtime_app._find_specdock_dir = original_find_specdock_dir
            runtime_app._cli_build_registry = original_build_registry
            runtime_app._cli_build_parser = original_build_parser
            runtime_app._cli_build_runtime = original_build_runtime
            runtime_app._cli_dispatch = original_dispatch

        self.assertEqual(exit_code, 17)
        self.assertEqual(
            calls,
            [
                ("parse_args", ["validate"]),
                ("dispatch", "validate", "registry", "use_cases"),
            ],
        )

    def test_rollback_ready_wrapper_swap_smoke(self) -> None:
        (_runtime_app, app_contracts, cli_dispatch, cli_parser, cli_registry, cmd_contracts, _domain_models) = (
            _runtime_modules()
        )

        registry = cli_registry.build_registry()
        original_spec = registry.items["validate"]

        def _run_swapped(_args, _use_cases):
            return cmd_contracts.CommandOutcome(
                exit_code=9,
                text=SimpleNamespace(
                    stdout_lines=["spec-dock: ok (swapped wrapper)"],
                    stderr_lines=[],
                    warnings=[],
                ),
            )

        registry.items["validate"] = cmd_contracts.CommandSpec(
            add_arguments=original_spec.add_arguments,
            args_factory=original_spec.args_factory,
            run=_run_swapped,
        )

        parser = cli_parser.build_parser(registry)
        ns = parser.parse_args(["validate"])
        use_cases = app_contracts.UseCases(
            create_initiative=lambda req: None,  # type: ignore[return-value]
            create_epic=lambda req: None,  # type: ignore[return-value]
            create_issue=lambda req: None,  # type: ignore[return-value]
            create_discussion_doc=lambda req: None,  # type: ignore[return-value]
            import_initiative=lambda req: None,  # type: ignore[return-value]
            import_epic=lambda req: None,  # type: ignore[return-value]
            import_issue=lambda req: None,  # type: ignore[return-value]
            set_active=lambda req: None,  # type: ignore[return-value]
            show_active=lambda req: None,  # type: ignore[return-value]
            clear_active=lambda req: None,  # type: ignore[return-value]
            sync=lambda req: None,  # type: ignore[return-value]
            check_deps=lambda req: None,  # type: ignore[return-value]
            validate_tree=lambda req: None,  # type: ignore[return-value]
        )

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = cli_dispatch.dispatch(ns, registry, use_cases)
        self.assertEqual(exit_code, 9)
        self.assertEqual(stdout.getvalue().strip(), "spec-dock: ok (swapped wrapper)")

    def test_final_api_call_site_and_structural_regression(self) -> None:
        (runtime_app, _app_contracts, _cli_dispatch, _cli_parser, _cli_registry, _cmd_contracts, _domain_models) = (
            _runtime_modules()
        )

        app_source_path = Path(runtime_app.__file__)
        app_source = app_source_path.read_text(encoding="utf-8")
        app_tree = ast.parse(app_source)
        main_node = next(
            (
                node
                for node in app_tree.body
                if isinstance(node, ast.FunctionDef) and node.name == "main"
            ),
            None,
        )
        self.assertIsNotNone(main_node, "main() not found in app.py")

        call_names: set[str] = set()
        for node in ast.walk(main_node):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name):
                call_names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                call_names.add(node.func.attr)

        self.assertIn("_cli_build_registry", call_names)
        self.assertIn("_cli_build_parser", call_names)
        self.assertIn("_cli_build_runtime", call_names)
        self.assertIn("_cli_dispatch", call_names)

        legacy_helper_calls = {
            "_new_initiative",
            "_new_epic",
            "_new_issue",
            "_new_doc",
            "_active_set",
            "_active_show",
            "_active_clear",
            "_sync",
            "_deps_check",
            "_import_initiative",
            "_import_epic",
            "_import_issue",
            "_validate",
        }
        self.assertTrue(call_names.isdisjoint(legacy_helper_calls))

        runtime_root = app_source_path.parent
        layer_dirs = ("commands", "application", "infra", "presentation", "cli")
        for layer_dir in layer_dirs:
            for module_path in sorted((runtime_root / layer_dir).glob("*.py")):
                if module_path.name == "__init__.py":
                    continue
                tree = ast.parse(module_path.read_text(encoding="utf-8"))
                for imported in _iter_import_modules(tree):
                    root = _import_root(imported)
                    self.assertNotIn(
                        root,
                        _LEGACY_HELPER_MODULES,
                        f"legacy helper direct import in {module_path}: {imported}",
                    )

        # commands/* must stay as thin shell layer: no direct domain/infra/app imports.
        commands_dir = app_source_path.parent / "commands"
        for module_path in sorted(commands_dir.glob("*.py")):
            if module_path.name == "__init__.py":
                continue
            tree = ast.parse(module_path.read_text(encoding="utf-8"))
            for imported in _iter_import_modules(tree):
                root = _import_root(imported)
                self.assertNotIn(root, {"domain", "infra", "app"}, f"forbidden import in {module_path}: {imported}")

        # application/* may only refer to infra through contracts.
        application_dir = app_source_path.parent / "application"
        for module_path in sorted(application_dir.glob("*.py")):
            if module_path.name == "__init__.py":
                continue
            tree = ast.parse(module_path.read_text(encoding="utf-8"))
            for imported in _iter_import_modules(tree):
                root = _import_root(imported)
                if root != "infra":
                    continue
                self.assertEqual(
                    _normalize_import_module(imported),
                    "infra.contracts",
                    f"application layer must not import infra concrete module: {module_path}: {imported}",
                )

        # infra/* must not depend on shell/entrypoint layers.
        infra_dir = app_source_path.parent / "infra"
        forbidden_infra_roots = {"app", "cli", "commands"}
        for module_path in sorted(infra_dir.glob("*.py")):
            if module_path.name == "__init__.py":
                continue
            tree = ast.parse(module_path.read_text(encoding="utf-8"))
            for imported in _iter_import_modules(tree):
                root = _import_root(imported)
                self.assertNotIn(
                    root,
                    forbidden_infra_roots,
                    f"infra layer must not depend on shell layers: {module_path}: {imported}",
                )

    def test_app_no_command_wrapper_regression(self) -> None:
        (runtime_app, _app_contracts, _cli_dispatch, _cli_parser, _cli_registry, _cmd_contracts, _domain_models) = (
            _runtime_modules()
        )

        app_source_path = Path(runtime_app.__file__)
        app_tree = ast.parse(app_source_path.read_text(encoding="utf-8"))
        function_names = {
            node.name
            for node in app_tree.body
            if isinstance(node, ast.FunctionDef)
        }
        forbidden_wrappers = {
            "_new_initiative",
            "_new_epic",
            "_new_issue",
            "_new_doc",
            "_import_initiative",
            "_import_epic",
            "_import_issue",
            "_active_set",
            "_active_show",
            "_active_clear",
            "_sync",
            "_deps_check",
            "_validate",
            "_new_ports",
            "_run_new_node",
            "_run_new_doc",
            "_run_import_node",
        }
        self.assertTrue(
            function_names.isdisjoint(forbidden_wrappers),
            f"forbidden command wrappers remain in app.py: {sorted(function_names & forbidden_wrappers)}",
        )

        bootstrap_source_path = app_source_path.parent / "cli" / "bootstrap.py"
        bootstrap_source = bootstrap_source_path.read_text(encoding="utf-8")
        self.assertIn("application_create_initiative(req, ports)", bootstrap_source)
        self.assertIn("application_import_issue(req, ports)", bootstrap_source)
        self.assertIn("application_set_active(req, ports)", bootstrap_source)
        self.assertIn("application_sync(req, ports)", bootstrap_source)
        self.assertIn("application_check_deps(req, ports)", bootstrap_source)
        self.assertIn("application_validate_tree(req, ports)", bootstrap_source)
        self.assertIn("from ..application.create_node import create_initiative as application_create_initiative", bootstrap_source)
        self.assertIn("from ..application.import_node import import_issue as application_import_issue", bootstrap_source)
        self.assertNotIn("from .. import app as runtime_app", bootstrap_source)
        self.assertNotIn("runtime_app._application_", bootstrap_source)
        self.assertNotIn("runtime_app._new_", bootstrap_source)
        self.assertNotIn("runtime_app._import_", bootstrap_source)
        self.assertNotIn("runtime_app._active_", bootstrap_source)
        self.assertNotIn("runtime_app._sync(", bootstrap_source)
        self.assertNotIn("runtime_app._deps_check(", bootstrap_source)
        self.assertNotIn("runtime_app._validate(", bootstrap_source)


if __name__ == "__main__":
    unittest.main()
