import contextlib
import io
from pathlib import Path
import sys
import tempfile


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
        from spec_dock_runtime.application import (
            contracts as app_contracts,
            ports as app_ports,
            validate_tree as app_validate_tree,
        )
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.infra import contracts as infra_contracts
        from spec_dock_runtime.presentation import (
            cli_text as presentation_cli_text,
            contracts as presentation_contracts,
        )
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


def _runtime_cli_bootstrap_module():
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
        from spec_dock_runtime.cli import bootstrap as cli_bootstrap
    finally:
        sys.path.pop(0)
    return cli_bootstrap


class _StubReader:
    def __init__(self, records):
        self.records = records
        self.calls = 0

    def load_node_records(self):
        self.calls += 1
        return self.records


class TestRuntimeValidateS02:
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

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            initiative_dir = repo_root / "spec-dock" / "initiatives" / "init-00001-auth-platform"
            initiative_dir.mkdir(parents=True, exist_ok=True)
            (initiative_dir / ".meta.json").write_text("{}\n", encoding="utf-8")
            for name in ("requirement.md", "design.md", "plan.md", "report.md"):
                (initiative_dir / name).write_text(f"{name}\n", encoding="utf-8")

            reader = _StubReader(
                [
                    infra_contracts.StoredMetaRecord(
                        kind="initiative",
                        id="init-00001",
                        title="Auth Platform",
                        slug="auth-platform",
                        path=initiative_dir.as_posix(),
                        parent_id=None,
                        initiative_id=None,
                        epic_id=None,
                        github_issue_number=1,
                        meta_path=(initiative_dir / ".meta.json").as_posix(),
                        github_repo_owner="example",
                        github_repo_name="repo",
                    )
                ]
            )
            ports = app_ports.Ports(node_reader=reader, repo_root=repo_root)
            result = app_validate_tree.validate_tree(app_contracts.ValidateTreeRequest(), ports)

            assert reader.calls == 1
            assert result.checked_node_count == 1
            assert result.report.errors == []
            assert result.report.warnings == []

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

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            issue_dir = (
                repo_root
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
            )
            issue_dir.mkdir(parents=True, exist_ok=True)
            (issue_dir / ".meta.json").write_text("{}\n", encoding="utf-8")
            for name in ("requirement.md", "design.md", "plan.md", "report.md"):
                (issue_dir / name).write_text(f"{name}\n", encoding="utf-8")

            reader = _StubReader(
                [
                    infra_contracts.StoredMetaRecord(
                        kind="issue",
                        id="iss-00003",
                        title="Add Refresh Token",
                        slug="add-refresh-token",
                        path=issue_dir.as_posix(),
                        parent_id=None,
                        initiative_id="init-00001",
                        epic_id="epic-00002",
                        github_issue_number=3,
                        meta_path=(issue_dir / ".meta.json").as_posix(),
                        github_repo_owner="example",
                        github_repo_name="repo",
                    )
                ]
            )
            ports = app_ports.Ports(node_reader=reader, repo_root=repo_root)
            result = app_validate_tree.validate_tree(app_contracts.ValidateTreeRequest(), ports)

        assert result.checked_node_count == 1
        assert result.report.errors
        assert "issue missing parent_id" in result.report.errors[0]

    def test_validate_tree_use_case_rejects_local_only_legacy_contract_state(self) -> None:
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

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            initiative_dir = repo_root / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            initiative_dir.mkdir(parents=True, exist_ok=True)
            (initiative_dir / ".meta.json").write_text("{}\n", encoding="utf-8")
            for name in ("requirement.md", "design.md", "plan.md", "report.md"):
                (initiative_dir / name).write_text(f"{name}\n", encoding="utf-8")

            reader = _StubReader(
                [
                    infra_contracts.StoredMetaRecord(
                        kind="initiative",
                        id="init-local-00001",
                        title="Auth Platform",
                        slug="auth-platform",
                        path=initiative_dir.as_posix(),
                        parent_id=None,
                        initiative_id=None,
                        epic_id=None,
                        github_issue_number=None,
                        meta_path=(initiative_dir / ".meta.json").as_posix(),
                    )
                ]
            )
            ports = app_ports.Ports(node_reader=reader, repo_root=repo_root)
            result = app_validate_tree.validate_tree(app_contracts.ValidateTreeRequest(), ports)

        assert result.checked_node_count == 1
        assert result.report.errors
        assert "initiative missing github.issue_number" in result.report.errors[0]

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
        assert ok.stdout_lines == ["spec-dock: ok (validate) nodes=3"]
        assert ok.stderr_lines == []

        ng = presentation_cli_text.render_validate_text(
            app_contracts.ValidationResult(
                report=domain_models.ValidationReport(errors=["broken tree"], warnings=[]),
                checked_node_count=3,
            )
        )
        assert ng.stdout_lines == []
        assert ng.stderr_lines == ["broken tree"]

    def test_app_minimal_validate_reader_seam(self) -> None:
        (
            _runtime_app,
            _app_contracts,
            _app_ports,
            _app_validate_tree,
            _domain_models,
            infra_contracts,
            _presentation_cli_text,
            _presentation_contracts,
        ) = _runtime_modules()
        from spec_dock_runtime.cli import bootstrap as cli_bootstrap

        calls: dict[str, object] = {}
        original_load_node_records = cli_bootstrap.infra_fs_repo.load_node_records
        expected_records = [
            infra_contracts.StoredMetaRecord(
                kind="initiative",
                id="init-00001",
                title="Auth Platform",
                slug="auth-platform",
                path="/repo/spec-dock/initiatives/init-00001-auth-platform",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=1,
                meta_path="/repo/spec-dock/initiatives/init-00001-auth-platform/.meta.json",
                github_repo_owner="example",
                github_repo_name="repo",
            )
        ]

        def _fake_load_node_records(specdock_dir):
            calls["specdock_dir"] = specdock_dir
            return expected_records

        cli_bootstrap.infra_fs_repo.load_node_records = _fake_load_node_records
        try:
            reader = cli_bootstrap._NodeReader(specdock_dir=Path("/repo/spec-dock"))
            records = reader.load_node_records()
        finally:
            cli_bootstrap.infra_fs_repo.load_node_records = original_load_node_records

        assert calls.get("specdock_dir") == Path("/repo/spec-dock")
        assert records == expected_records

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
        from spec_dock_runtime.cli import bootstrap as cli_bootstrap

        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_ensure_no_legacy_meta_json = runtime_app._ensure_no_legacy_meta_json
        original_application_validate_tree = cli_bootstrap.application_validate_tree

        runtime_app._find_specdock_dir = lambda: Path("/repo/spec-dock")
        runtime_app._ensure_no_legacy_meta_json = lambda _specdock_dir: None
        cli_bootstrap.application_validate_tree = lambda _req, _ports: app_contracts.ValidationResult(
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
            cli_bootstrap.application_validate_tree = original_application_validate_tree

        assert exit_code == 0
        assert stdout.getvalue() == "spec-dock: ok (validate) nodes=2\n"
        assert stderr.getvalue() == ""

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
        from spec_dock_runtime.cli import bootstrap as cli_bootstrap

        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_ensure_no_legacy_meta_json = runtime_app._ensure_no_legacy_meta_json
        original_application_validate_tree = cli_bootstrap.application_validate_tree

        runtime_app._find_specdock_dir = lambda: Path("/repo/spec-dock")
        runtime_app._ensure_no_legacy_meta_json = lambda _specdock_dir: None
        cli_bootstrap.application_validate_tree = lambda _req, _ports: app_contracts.ValidationResult(
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
            cli_bootstrap.application_validate_tree = original_application_validate_tree

        assert exit_code == 1
        assert stdout.getvalue() == ""
        assert "error: broken tree" in stderr.getvalue()

    def test_legacy_validate_path_delegates_to_use_case_and_renderer(self) -> None:
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
        from spec_dock_runtime.cli import bootstrap as cli_bootstrap

        calls: dict[str, object] = {}
        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_ensure_no_legacy_meta_json = runtime_app._ensure_no_legacy_meta_json
        original_application_validate_tree = cli_bootstrap.application_validate_tree

        def _fake_validate_tree(req, ports):
            calls["req"] = req
            calls["ports"] = ports
            return app_contracts.ValidationResult(
                report=domain_models.ValidationReport(errors=[], warnings=[]),
                checked_node_count=1,
            )

        runtime_app._find_specdock_dir = lambda: Path("/repo/spec-dock")
        runtime_app._ensure_no_legacy_meta_json = lambda _specdock_dir: None
        cli_bootstrap.application_validate_tree = _fake_validate_tree
        try:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = runtime_app.main(["validate"])
        finally:
            runtime_app._find_specdock_dir = original_find_specdock_dir
            runtime_app._ensure_no_legacy_meta_json = original_ensure_no_legacy_meta_json
            cli_bootstrap.application_validate_tree = original_application_validate_tree

        assert exit_code == 0
        assert stdout.getvalue() == "spec-dock: ok (validate) nodes=1\n"
        assert stderr.getvalue() == ""
        req = calls.get("req")
        ports = calls.get("ports")
        assert isinstance(req, app_contracts.ValidateTreeRequest)
        assert ports is not None
        assert ports.repo_root == Path("/repo")
        assert ports.specdock_dir == Path("/repo/spec-dock")

    def test_issue_78_validate_uses_current_specdock_even_when_legacy_hidden_workspace_exists(self) -> None:
        cli_bootstrap = _runtime_cli_bootstrap_module()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            current_specdock = repo_root / "spec-dock"
            legacy_specdock = repo_root / ".spec-dock"
            current_specdock.mkdir(parents=True, exist_ok=True)
            legacy_specdock.mkdir(parents=True, exist_ok=True)

            calls: dict[str, object] = {}
            original_load_node_records = cli_bootstrap.infra_fs_repo.load_node_records

            def _fake_load_node_records(specdock_dir):
                calls["specdock_dir"] = specdock_dir
                return []

            cli_bootstrap.infra_fs_repo.load_node_records = _fake_load_node_records
            try:
                reader = cli_bootstrap._NodeReader(specdock_dir=current_specdock)
                records = reader.load_node_records()
            finally:
                cli_bootstrap.infra_fs_repo.load_node_records = original_load_node_records

        assert records == []
        assert calls.get("specdock_dir") == current_specdock
        assert calls.get("specdock_dir") != legacy_specdock
