import contextlib
import io
import json
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
        from spec_dock_runtime import app as runtime_app
        from spec_dock_runtime.application import check_deps as app_check_deps
        from spec_dock_runtime.application import contracts as app_contracts
        from spec_dock_runtime.application import ports as app_ports
        from spec_dock_runtime.application import status_context as app_status_context
        from spec_dock_runtime.application import validate_tree as app_validate_tree
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.infra import contracts as infra_contracts
        from spec_dock_runtime.presentation import cli_text as presentation_cli_text
        from spec_dock_runtime.presentation import json_state as presentation_json_state
    finally:
        sys.path.pop(0)

    return (
        runtime_app,
        app_check_deps,
        app_contracts,
        app_ports,
        app_status_context,
        app_validate_tree,
        domain_models,
        infra_contracts,
        presentation_cli_text,
        presentation_json_state,
    )


def _sample_records(infra_contracts):
    return [
        infra_contracts.StoredMetaRecord(
            kind="initiative",
            id="init-local-00001",
            title="Auth Platform",
            slug="auth-platform",
            path="/repo/spec-dock/initiatives/init-local-00001-auth-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=101,
            meta_path="/repo/spec-dock/initiatives/init-local-00001-auth-platform/.meta.json",
        ),
        infra_contracts.StoredMetaRecord(
            kind="epic",
            id="epic-local-00001",
            title="JWT Auth",
            slug="jwt-auth",
            path="/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=201,
            meta_path="/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/.meta.json",
        ),
        infra_contracts.StoredMetaRecord(
            kind="issue",
            id="iss-local-00001",
            title="Dependency",
            slug="dependency",
            path="/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00001-dependency",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
            meta_path="/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00001-dependency/.meta.json",
        ),
        infra_contracts.StoredMetaRecord(
            kind="issue",
            id="iss-local-00002",
            title="Target",
            slug="target",
            path="/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00002-target",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=302,
            meta_path="/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00002-target/.meta.json",
        ),
    ]


class _StubNodeReader:
    def __init__(self, records):
        self.records = list(records)

    def load_node_records(self):
        return list(self.records)


class _StubDepsTopologyReader:
    def __init__(self, issue_depends_on_map, warnings=None):
        self.issue_depends_on_map = dict(issue_depends_on_map)
        self.warnings = list(warnings or [])
        self.calls = 0

    def load_issue_depends_on_map(self, specdock_dir, graph):
        del specdock_dir, graph
        self.calls += 1
        _, _, _, _, _, _, _, infra_contracts, _, _ = _runtime_modules()
        return infra_contracts.DepsTopologyLoadResult(
            issue_depends_on_map=dict(self.issue_depends_on_map),
            warnings=list(self.warnings),
        )


class _StubDerivedStateReader:
    def __init__(self, status_by_id):
        self.status_by_id = dict(status_by_id)

    def load_cached_issue_status_by_id(self, specdock_dir):
        del specdock_dir
        return dict(self.status_by_id)


class _StubIssueGateway:
    def __init__(self, snapshots=None, fail=False):
        self.snapshots = list(snapshots or [])
        self.fail = fail

    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        if self.fail:
            raise RuntimeError("gh failed")
        return list(self.snapshots)


class _StubActiveStateStore:
    def __init__(self, issue_id):
        self.issue_id = issue_id

    def load_active_issue_id(self, specdock_dir):
        del specdock_dir
        return self.issue_id


class TestRuntimeDepsS04(unittest.TestCase):
    def test_status_context_source_selection(self) -> None:
        (
            _runtime_app,
            _app_check_deps,
            _app_contracts,
            _app_ports,
            app_status_context,
            app_validate_tree,
            domain_models,
            infra_contracts,
            _presentation_cli_text,
            _presentation_json_state,
        ) = _runtime_modules()
        records = _sample_records(infra_contracts)
        graph = app_validate_tree.build_graph([app_validate_tree._to_spec_node_seed(record) for record in records])

        snapshots = [
            domain_models.IssueSnapshot(
                issue_number=301,
                state="CLOSED",
                title="Dependency",
                labels=[],
                updated_at="t",
                url="u",
            )
        ]
        context_gh = app_status_context.resolve_issue_status_context(
            graph,
            github_enabled=True,
            issue_snapshots=snapshots,
            cached_issue_status_by_id={"iss-local-00001": "open"},
        )
        self.assertEqual(context_gh.issue_statuses["iss-local-00001"].status, "done")
        self.assertEqual(context_gh.issue_statuses["iss-local-00001"].source, "github")

        context_cache = app_status_context.resolve_issue_status_context(
            graph,
            github_enabled=False,
            issue_snapshots=snapshots,
            cached_issue_status_by_id={"iss-local-00001": "open"},
        )
        self.assertEqual(context_cache.issue_statuses["iss-local-00001"].status, "open")
        self.assertEqual(context_cache.issue_statuses["iss-local-00001"].source, "cache")

    def test_check_deps_use_case_and_cycle_fail_fast(self) -> None:
        (
            _runtime_app,
            app_check_deps,
            app_contracts,
            app_ports,
            _app_status_context,
            _app_validate_tree,
            _domain_models,
            infra_contracts,
            _presentation_cli_text,
            _presentation_json_state,
        ) = _runtime_modules()
        records = _sample_records(infra_contracts)

        ports = app_ports.Ports(
            node_reader=_StubNodeReader(records),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
            derived_state_reader=_StubDerivedStateReader(
                {"iss-local-00001": "open", "iss-local-00002": "open"}
            ),
            issue_gateway=_StubIssueGateway([]),
            active_state_store=_StubActiveStateStore("iss-local-00002"),
            deps_topology_reader=_StubDepsTopologyReader(
                {"iss-local-00001": [], "iss-local-00002": ["iss-local-00001"]}
            ),
        )
        result = app_check_deps.check_deps(
            app_contracts.CheckDepsRequest(
                target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00002", github_issue_number=None),
                use_github=False,
                issue_limit=10000,
            ),
            ports,
        )
        self.assertFalse(result.inspection.evaluation.ready)
        self.assertEqual(result.inspection.evaluation.blockers, ["iss-local-00001"])
        self.assertEqual(result.warnings, [])

        cycle_ports = app_ports.Ports(
            node_reader=_StubNodeReader(records),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
            derived_state_reader=_StubDerivedStateReader({}),
            issue_gateway=_StubIssueGateway([]),
            active_state_store=_StubActiveStateStore(None),
            deps_topology_reader=_StubDepsTopologyReader(
                {
                    "iss-local-00001": ["iss-local-00002"],
                    "iss-local-00002": ["iss-local-00001"],
                }
            ),
        )
        with self.assertRaises(RuntimeError):
            app_check_deps.check_deps(
                app_contracts.CheckDepsRequest(
                    target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00002", github_issue_number=None),
                    use_github=False,
                    issue_limit=10000,
                ),
                cycle_ports,
            )

    def test_validate_tree_reconnects_topology_provider(self) -> None:
        (
            _runtime_app,
            _app_check_deps,
            app_contracts,
            app_ports,
            _app_status_context,
            app_validate_tree,
            _domain_models,
            infra_contracts,
            _presentation_cli_text,
            _presentation_json_state,
        ) = _runtime_modules()
        records = _sample_records(infra_contracts)
        deps_reader = _StubDepsTopologyReader(
            {"iss-local-00001": ["iss-local-00002"], "iss-local-00002": ["iss-local-00001"]}
        )
        ports = app_ports.Ports(
            node_reader=_StubNodeReader(records),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
            deps_topology_reader=deps_reader,
        )
        result = app_validate_tree.validate_tree(app_contracts.ValidateTreeRequest(), ports)
        self.assertEqual(deps_reader.calls, 1)
        self.assertTrue(result.report.errors)
        self.assertIn("Dependency cycle detected", result.report.errors[0])

    def test_deps_renderers(self) -> None:
        (
            _runtime_app,
            _app_check_deps,
            app_contracts,
            _app_ports,
            _app_status_context,
            _app_validate_tree,
            domain_models,
            _infra_contracts,
            presentation_cli_text,
            presentation_json_state,
        ) = _runtime_modules()
        inspection = domain_models.TargetDepsInspection(
            target_id=domain_models.NodeId("iss-local-00002"),
            evaluation=domain_models.DepsEvaluation(
                ready=False,
                guard_reason="blocked",
                blockers=["iss-local-00001"],
                blockers_top=["iss-local-00001"],
                closure=["iss-local-00001"],
            ),
            node_states={
                "iss-local-00001": domain_models.DepsNodeState(
                    node_id="iss-local-00001",
                    status="blocked",
                    ready=False,
                    blockers_top=["iss-local-00001"],
                    effective_depends_on=["iss-local-00001"],
                )
            },
            effective_depends_on=["iss-local-00001"],
            warnings=[],
        )
        result = app_contracts.DepsCheckResult(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00002", github_issue_number=None),
            inspection=inspection,
            warnings=["gh_fetch_failed"],
        )

        text = presentation_cli_text.render_deps_check_text(result)
        self.assertIn("spec-dock: blocked (deps check)", text.stderr_lines[0])
        self.assertEqual(text.warnings, ["gh_fetch_failed"])

        payload = json.loads(presentation_json_state.render_deps_check_json(result))
        self.assertEqual(payload["target"], "iss-local-00002")
        self.assertEqual(payload["blockers"], ["iss-local-00001"])
        self.assertEqual(payload["warnings"], ["gh_fetch_failed"])

    def test_legacy_deps_path_delegates_and_exit_codes(self) -> None:
        (
            runtime_app,
            app_check_deps,
            app_contracts,
            _app_ports,
            _app_status_context,
            _app_validate_tree,
            domain_models,
            _infra_contracts,
            presentation_cli_text,
            presentation_json_state,
        ) = _runtime_modules()
        from spec_dock_runtime.cli import bootstrap as cli_bootstrap

        inspection_blocked = domain_models.TargetDepsInspection(
            target_id=domain_models.NodeId("iss-local-00002"),
            evaluation=domain_models.DepsEvaluation(
                ready=False,
                guard_reason="blocked",
                blockers=["iss-local-00001"],
                blockers_top=["iss-local-00001"],
                closure=["iss-local-00001"],
            ),
            node_states={},
            effective_depends_on=["iss-local-00001"],
            warnings=[],
        )
        blocked_result = app_contracts.DepsCheckResult(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00002", github_issue_number=None),
            inspection=inspection_blocked,
            warnings=["gh_fetch_failed"],
        )

        calls = {}
        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_application_check_deps = cli_bootstrap.application_check_deps
        original_render_deps_check_text = runtime_app._render_deps_check_text
        original_render_deps_check_json = runtime_app._render_deps_check_json
        try:
            runtime_app._find_specdock_dir = lambda: Path("/repo/spec-dock")

            def _fake_check_deps(req, ports):
                calls["req"] = req
                calls["ports"] = ports
                return blocked_result

            cli_bootstrap.application_check_deps = _fake_check_deps
            runtime_app._render_deps_check_text = presentation_cli_text.render_deps_check_text
            runtime_app._render_deps_check_json = presentation_json_state.render_deps_check_json

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = runtime_app.main(["deps", "check", "iss-local-1"])

            self.assertEqual(exit_code, 3)
            self.assertEqual(stdout.getvalue(), "")
            stderr_lines = [line for line in stderr.getvalue().splitlines() if line.strip()]
            self.assertTrue(stderr_lines[0].startswith("spec-dock: (warn) gh_fetch_failed"))
            self.assertIn("spec-dock: blocked (deps check)", stderr_lines[1])
            self.assertEqual(calls["req"].target.kind, "node_id")
            self.assertEqual(calls["req"].target.node_id, "iss-local-1")
        finally:
            runtime_app._find_specdock_dir = original_find_specdock_dir
            cli_bootstrap.application_check_deps = original_application_check_deps
            runtime_app._render_deps_check_text = original_render_deps_check_text
            runtime_app._render_deps_check_json = original_render_deps_check_json

        ready_result = app_contracts.DepsCheckResult(
            target=app_contracts.TargetRef(kind="github_issue", node_id=None, github_issue_number=123),
            inspection=domain_models.TargetDepsInspection(
                target_id=domain_models.NodeId("iss-00123"),
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
            ),
            warnings=[],
        )

        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_application_check_deps = cli_bootstrap.application_check_deps
        original_render_deps_check_json = runtime_app._render_deps_check_json
        try:
            runtime_app._find_specdock_dir = lambda: Path("/repo/spec-dock")
            cli_bootstrap.application_check_deps = lambda req, ports: ready_result
            runtime_app._render_deps_check_json = presentation_json_state.render_deps_check_json

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = runtime_app.main(["deps", "check", "#123", "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr.getvalue().strip(), "")
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["target"], "iss-00123")
            self.assertTrue(payload["ready"])
        finally:
            runtime_app._find_specdock_dir = original_find_specdock_dir
            cli_bootstrap.application_check_deps = original_application_check_deps
            runtime_app._render_deps_check_json = original_render_deps_check_json

        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_application_check_deps = cli_bootstrap.application_check_deps
        try:
            runtime_app._find_specdock_dir = lambda: Path("/repo/spec-dock")
            cli_bootstrap.application_check_deps = lambda req, ports: (_ for _ in ()).throw(RuntimeError("boom"))

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = runtime_app.main(["deps", "check", "iss-local-00001"])
            self.assertEqual(exit_code, 1)
            self.assertIn("error: boom", stderr.getvalue())
        finally:
            runtime_app._find_specdock_dir = original_find_specdock_dir
            cli_bootstrap.application_check_deps = original_application_check_deps
