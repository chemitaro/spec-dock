import contextlib
import io
import sys
import unittest
from pathlib import Path


def _runtime_modules():
    runtime_scripts_dir = (
        Path(__file__).resolve().parents[1]
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
        from spec_dock_runtime.application import ports as app_ports
        from spec_dock_runtime.application import validate_tree as app_validate_tree
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.infra import contracts as infra_contracts
        from spec_dock_runtime.presentation import cli_text as presentation_cli_text
        from spec_dock_runtime.presentation import contracts as presentation_contracts
    finally:
        sys.path.pop(0)

    return (
        runtime_app,
        app_contracts,
        app_ports,
        app_validate_tree,
        domain_models,
        infra_contracts,
        presentation_cli_text,
        presentation_contracts,
    )


class _StubReader:
    def __init__(self, records):
        self.records = records
        self.calls = 0

    def load_node_records(self):
        self.calls += 1
        return self.records


class TestRuntimeValidateS02(unittest.TestCase):
    def test_validate_tree_use_case_returns_result_with_checked_node_count(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_validate_tree,
            _domain_models,
            infra_contracts,
            _presentation_cli_text,
            _presentation_contracts,
        ) = _runtime_modules()

        reader = _StubReader(
            [
                infra_contracts.StoredMetaRecord(
                    kind="initiative",
                    id="init-local-00001",
                    title="Auth Platform",
                    slug="auth-platform",
                    path="/repo/spec-dock/initiatives/init-local-00001-auth-platform",
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                    meta_path="/repo/spec-dock/initiatives/init-local-00001-auth-platform/.meta.json",
                )
            ]
        )
        ports = app_ports.Ports(node_reader=reader, repo_root=Path("/repo"))
        result = app_validate_tree.validate_tree(app_contracts.ValidateTreeRequest(), ports)

        self.assertEqual(reader.calls, 1)
        self.assertEqual(result.checked_node_count, 1)
        self.assertEqual(result.report.errors, [])
        self.assertEqual(result.report.warnings, [])

    def test_validate_tree_use_case_returns_domain_error(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_validate_tree,
            _domain_models,
            infra_contracts,
            _presentation_cli_text,
            _presentation_contracts,
        ) = _runtime_modules()

        reader = _StubReader(
            [
                infra_contracts.StoredMetaRecord(
                    kind="issue",
                    id="iss-local-00001",
                    title="Add Refresh Token",
                    slug="add-refresh-token",
                    path="/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00001-add-refresh-token",
                    parent_id=None,
                    initiative_id="init-local-00001",
                    epic_id="epic-local-00001",
                    github_issue_number=None,
                    meta_path="/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00001-add-refresh-token/.meta.json",
                )
            ]
        )
        ports = app_ports.Ports(node_reader=reader, repo_root=Path("/repo"))
        result = app_validate_tree.validate_tree(app_contracts.ValidateTreeRequest(), ports)

        self.assertEqual(result.checked_node_count, 1)
        self.assertTrue(result.report.errors)
        self.assertIn("issue missing parent_id", result.report.errors[0])

    def test_render_validate_text_regression(self) -> None:
        (
            _runtime_app,
            app_contracts,
            _app_ports,
            _app_validate_tree,
            domain_models,
            _infra_contracts,
            presentation_cli_text,
            _presentation_contracts,
        ) = _runtime_modules()

        ok = presentation_cli_text.render_validate_text(
            app_contracts.ValidationResult(
                report=domain_models.ValidationReport(errors=[], warnings=[]),
                checked_node_count=3,
            )
        )
        self.assertEqual(ok.stdout_lines, ["spec-dock: ok (validate) nodes=3"])
        self.assertEqual(ok.stderr_lines, [])

        ng = presentation_cli_text.render_validate_text(
            app_contracts.ValidationResult(
                report=domain_models.ValidationReport(errors=["broken tree"], warnings=[]),
                checked_node_count=3,
            )
        )
        self.assertEqual(ng.stdout_lines, [])
        self.assertEqual(ng.stderr_lines, ["broken tree"])

    def test_app_minimal_validate_reader_seam(self) -> None:
        (
            runtime_app,
            _app_contracts,
            _app_ports,
            _app_validate_tree,
            _domain_models,
            infra_contracts,
            _presentation_cli_text,
            _presentation_contracts,
        ) = _runtime_modules()

        calls: dict[str, object] = {}
        original_scan_nodes = runtime_app._scan_nodes

        def _fake_scan_nodes(specdock_dir):
            calls["specdock_dir"] = specdock_dir
            return {
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

        runtime_app._scan_nodes = _fake_scan_nodes
        try:
            reader = runtime_app._AppValidateNodeReader(specdock_dir=Path("/repo/spec-dock"))
            records = reader.load_node_records()
        finally:
            runtime_app._scan_nodes = original_scan_nodes

        self.assertEqual(calls.get("specdock_dir"), Path("/repo/spec-dock"))
        self.assertEqual(
            records,
            [
                infra_contracts.StoredMetaRecord(
                    kind="initiative",
                    id="init-local-00001",
                    title="Auth Platform",
                    slug="auth-platform",
                    path="/repo/spec-dock/initiatives/init-local-00001-auth-platform",
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                    meta_path="/repo/spec-dock/initiatives/init-local-00001-auth-platform/.meta.json",
                )
            ],
        )

    def test_validate_exit_0_and_stdout_only(self) -> None:
        (
            runtime_app,
            app_contracts,
            _app_ports,
            _app_validate_tree,
            domain_models,
            _infra_contracts,
            _presentation_cli_text,
            _presentation_contracts,
        ) = _runtime_modules()

        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_ensure_no_legacy_meta_json = runtime_app._ensure_no_legacy_meta_json
        original_application_validate_tree = runtime_app._application_validate_tree

        runtime_app._find_specdock_dir = lambda: Path("/repo/spec-dock")
        runtime_app._ensure_no_legacy_meta_json = lambda _specdock_dir: None
        runtime_app._application_validate_tree = lambda _req, _ports: app_contracts.ValidationResult(
            report=domain_models.ValidationReport(errors=[], warnings=[]),
            checked_node_count=2,
        )
        try:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = runtime_app.main(["validate"])
        finally:
            runtime_app._find_specdock_dir = original_find_specdock_dir
            runtime_app._ensure_no_legacy_meta_json = original_ensure_no_legacy_meta_json
            runtime_app._application_validate_tree = original_application_validate_tree

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "spec-dock: ok (validate) nodes=2\n")
        self.assertEqual(stderr.getvalue(), "")

    def test_validate_exit_1_and_stderr_only(self) -> None:
        (
            runtime_app,
            app_contracts,
            _app_ports,
            _app_validate_tree,
            domain_models,
            _infra_contracts,
            _presentation_cli_text,
            _presentation_contracts,
        ) = _runtime_modules()

        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_ensure_no_legacy_meta_json = runtime_app._ensure_no_legacy_meta_json
        original_application_validate_tree = runtime_app._application_validate_tree

        runtime_app._find_specdock_dir = lambda: Path("/repo/spec-dock")
        runtime_app._ensure_no_legacy_meta_json = lambda _specdock_dir: None
        runtime_app._application_validate_tree = lambda _req, _ports: app_contracts.ValidationResult(
            report=domain_models.ValidationReport(errors=["broken tree"], warnings=[]),
            checked_node_count=2,
        )
        try:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = runtime_app.main(["validate"])
        finally:
            runtime_app._find_specdock_dir = original_find_specdock_dir
            runtime_app._ensure_no_legacy_meta_json = original_ensure_no_legacy_meta_json
            runtime_app._application_validate_tree = original_application_validate_tree

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("error: broken tree", stderr.getvalue())

    def test_legacy_validate_path_delegates_to_use_case_and_renderer(self) -> None:
        (
            runtime_app,
            app_contracts,
            _app_ports,
            _app_validate_tree,
            domain_models,
            _infra_contracts,
            _presentation_cli_text,
            presentation_contracts,
        ) = _runtime_modules()

        calls: dict[str, object] = {}
        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_ensure_no_legacy_meta_json = runtime_app._ensure_no_legacy_meta_json
        original_application_validate_tree = runtime_app._application_validate_tree

        def _fake_validate_tree(req, ports):
            calls["req"] = req
            calls["ports"] = ports
            return app_contracts.ValidationResult(
                report=domain_models.ValidationReport(errors=[], warnings=[]),
                checked_node_count=1,
            )

        runtime_app._find_specdock_dir = lambda: Path("/repo/spec-dock")
        runtime_app._ensure_no_legacy_meta_json = lambda _specdock_dir: None
        runtime_app._application_validate_tree = _fake_validate_tree
        try:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = runtime_app.main(["validate"])
        finally:
            runtime_app._find_specdock_dir = original_find_specdock_dir
            runtime_app._ensure_no_legacy_meta_json = original_ensure_no_legacy_meta_json
            runtime_app._application_validate_tree = original_application_validate_tree

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "spec-dock: ok (validate) nodes=1\n")
        self.assertEqual(stderr.getvalue(), "")
        req = calls.get("req")
        ports = calls.get("ports")
        self.assertIsInstance(req, app_contracts.ValidateTreeRequest)
        self.assertIsNotNone(ports)
        self.assertEqual(getattr(ports, "repo_root"), Path("/repo"))
        self.assertEqual(getattr(ports, "specdock_dir"), Path("/repo/spec-dock"))
