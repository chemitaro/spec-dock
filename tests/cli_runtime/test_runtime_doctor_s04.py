import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

import pytest

_SECRET_TOKEN = "ghp_secret_token_value"


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime import app as runtime_app
        from spec_dock_runtime.application import contracts as app_contracts, doctor as app_doctor, ports as app_ports
        from spec_dock_runtime.infra import contracts as infra_contracts
    finally:
        sys.path.pop(0)
    return runtime_app, app_contracts, app_doctor, app_ports, infra_contracts


def _runtime_fs_repo():
    runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.infra import fs_repo as infra_fs_repo
    finally:
        sys.path.pop(0)
    return infra_fs_repo


def _runtime_doctor_command():
    runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.commands import doctor as command_doctor
    finally:
        sys.path.pop(0)
    return command_doctor


def _runtime_github_capability_cli():
    runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.infra import github_capability_cli
    finally:
        sys.path.pop(0)
    return github_capability_cli


def _render_doctor_text(app_contracts, result):
    runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.presentation.cli_text import render_doctor_text
    finally:
        sys.path.pop(0)
    del app_contracts
    return render_doctor_text(result)


def _record(
    infra_contracts,
    *,
    kind: str,
    node_id: str,
    title: str,
    path: Path,
    parent_id: str | None,
    initiative_id: str | None,
    epic_id: str | None,
    github_issue_number: int | None = None,
    github_repo_owner: str | None = None,
    github_repo_name: str | None = None,
):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
        meta_path=(path / ".meta.json").as_posix(),
    )


def _write_required_docs(node_dir: Path) -> None:
    node_dir.mkdir(parents=True, exist_ok=True)
    (node_dir / ".meta.json").write_text("{}\n", encoding="utf-8")
    for name in ("requirement.md", "design.md", "plan.md", "report.md"):
        (node_dir / name).write_text(f"{name}\n", encoding="utf-8")


def _write_record_artifacts(record) -> None:
    node_dir = Path(record.path)
    node_dir.mkdir(parents=True, exist_ok=True)
    meta_payload = {
        "type": record.kind,
        "id": record.id,
        "title": record.title,
        "slug": record.slug,
    }
    if record.parent_id is not None:
        meta_payload["parent_id"] = record.parent_id
    if record.initiative_id is not None:
        meta_payload["initiative_id"] = record.initiative_id
    if record.epic_id is not None:
        meta_payload["epic_id"] = record.epic_id
    if record.github_issue_number is not None:
        meta_payload["github"] = {"issue_number": int(record.github_issue_number)}
        if record.github_repo_owner is not None and record.github_repo_name is not None:
            meta_payload["github"]["repo_owner"] = record.github_repo_owner
            meta_payload["github"]["repo_name"] = record.github_repo_name
    (node_dir / ".meta.json").write_text(json.dumps(meta_payload), encoding="utf-8")
    for name in ("requirement.md", "design.md", "plan.md", "report.md"):
        (node_dir / name).write_text(f"{name}\n", encoding="utf-8")


def _build_valid_records(infra_contracts, *, specdock_dir: Path):
    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    issue_dir = epic_dir / "issues" / "iss-local-00001-add-refresh-token"
    records = [
        _record(
            infra_contracts,
            kind="initiative",
            node_id="init-local-00001",
            title="Auth Platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=101,
            github_repo_owner="example",
            github_repo_name="repo",
        ),
        _record(
            infra_contracts,
            kind="epic",
            node_id="epic-local-00001",
            title="JWT Auth",
            path=epic_dir,
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=102,
            github_repo_owner="example",
            github_repo_name="repo",
        ),
        _record(
            infra_contracts,
            kind="issue",
            node_id="iss-local-00001",
            title="Add Refresh Token",
            path=issue_dir,
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=103,
            github_repo_owner="example",
            github_repo_name="repo",
        ),
    ]
    for record in records:
        _write_record_artifacts(record)
    return (records, issue_dir)


class _StubNodeReader:
    def __init__(self, records):
        self._records = list(records)

    def load_node_records(self):
        return list(self._records)


class _FailingNodeReader:
    def __init__(self, message: str):
        self._message = message

    def load_node_records(self):
        raise RuntimeError(self._message)


class _StubActiveStateStore:
    def __init__(self, load_result):
        self._load_result = load_result

    def load_active_manifest(self, specdock_dir):
        del specdock_dir
        return self._load_result


class _StubGitGateway:
    def __init__(self, origin_slug: str | None):
        self._origin_slug = origin_slug

    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return self._origin_slug


class _StubGitHubCapabilityGateway:
    def __init__(self, diagnostics):
        self.diagnostics = list(diagnostics)
        self.requests = []

    def probe(self, request):
        self.requests.append(request)
        return list(self.diagnostics)


class _StubRawDepsTopologyReader:
    def __init__(self, infra_contracts, raw_node_depends_on_map):
        self._infra_contracts = infra_contracts
        self._raw_node_depends_on_map = {node_id: list(dep_ids) for node_id, dep_ids in raw_node_depends_on_map.items()}

    def load_issue_depends_on_map(self, specdock_dir, graph):
        del specdock_dir, graph
        return self._infra_contracts.DepsTopologyLoadResult(
            issue_depends_on_map={},
            warnings=[],
        )

    def load_node_dependency_resolutions(self, specdock_dir, graph):
        del specdock_dir, graph
        return {
            node_id: [
                self._infra_contracts.DirectDependencyResolution(
                    raw_ref=dep_id,
                    resolved_node_id=dep_id,
                )
                for dep_id in dep_ids
            ]
            for node_id, dep_ids in self._raw_node_depends_on_map.items()
        }


class TestRuntimeDoctorS04:
    def test_doctor_command_surface_rejects_raw_github_api_arguments(self) -> None:
        import argparse

        command_doctor = _runtime_doctor_command()
        spec = command_doctor.command_specs()["doctor"]
        parser = argparse.ArgumentParser(prog="doctor")
        spec.add_arguments(parser)

        parsed = parser.parse_args([
            "--github-repo",
            "example/repo",
            "--github-pr",
            "123",
            "--github-head-sha",
            "abcde12345",
            "--github-extended",
        ])
        args = spec.args_factory(parsed)
        assert args.github_repo == "example/repo"
        assert args.github_pr == 123
        assert args.github_head_sha == "abcde12345"
        assert args.github_extended is True

        for forbidden in ("--api", "--endpoint", "--method", "--jq", "--header", "--raw"):
            with pytest.raises(SystemExit):
                parser.parse_args([forbidden, "value"])

    @pytest.mark.parametrize(
        "args",
        (
            ["--github-repo", "not-a-repo", "--github-pr", "123", "--github-head-sha", "abcde12345"],
            ["--github-repo", "example/repo", "--github-pr", "0", "--github-head-sha", "abcde12345"],
            ["--github-repo", "example/repo", "--github-pr", "123", "--github-head-sha", "not-a-sha"],
        ),
    )
    def test_doctor_command_surface_rejects_malformed_github_targets(self, args: list[str]) -> None:
        import argparse

        command_doctor = _runtime_doctor_command()
        spec = command_doctor.command_specs()["doctor"]
        parser = argparse.ArgumentParser(prog="doctor")
        spec.add_arguments(parser)

        with pytest.raises(SystemExit):
            parser.parse_args(args)

    def test_doctor_renders_targeted_github_permission_diagnostic_without_secret(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            diagnostic = app_contracts.GitHubCapabilityDiagnostic(
                code="github_token_permission_denied",
                capability="actions_read",
                status="permission_denied",
                token_source="GH_TOKEN",
                api="GET /repos/{repo}/actions/runs",
                severity="blocking",
                message=f"Resource not accessible by personal access token: {_SECRET_TOKEN}",
                recommended_next_action="fix_github_token_permissions",
                secret_redacted=True,
                stderr_sha256="abc123",
                group="core",
            )
            gateway = _StubGitHubCapabilityGateway([diagnostic])
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                github_capability_gateway=gateway,
            )

            result = app_doctor.doctor(
                app_contracts.DoctorRequest(
                    github_repo="example/repo",
                    github_pr=123,
                    github_head_sha="abcde12345",
                ),
                ports,
            )

            assert result.ok
            assert result.github_capability_diagnostics == [diagnostic]
            assert gateway.requests[0].github_repo == "example/repo"
            text = _render_doctor_text(app_contracts, result)
            rendered = "\n".join(text.stdout_lines + text.stderr_lines + text.warnings)
            assert "github capability diagnostics=1" in rendered
            assert "capability=actions_read" in rendered
            assert "status=permission_denied" in rendered
            assert "api=GET /repos/{repo}/actions/runs" in rendered
            assert "token_source=GH_TOKEN" in rendered
            assert "fix_github_token_permissions" in rendered
            assert _SECRET_TOKEN not in rendered

    def test_doctor_without_github_target_skips_capability_probe_without_structural_failure(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            gateway = _StubGitHubCapabilityGateway([])
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                github_capability_gateway=gateway,
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

            assert result.ok
            assert gateway.requests == []
            assert len(result.github_capability_diagnostics) == 1
            diagnostic = result.github_capability_diagnostics[0]
            assert diagnostic.capability == "actions_read"
            assert diagnostic.status == "target_unavailable"
            assert diagnostic.token_source == "unknown"
            text = _render_doctor_text(app_contracts, result)
            rendered = "\n".join(text.stdout_lines + text.stderr_lines + text.warnings)
            assert "status=target_unavailable" in rendered
            assert "capability=actions_read" in rendered

    def test_issue_222_s05_doctor_reports_actions_and_review_capabilities_without_checks_requirements(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            gateway = _StubGitHubCapabilityGateway([
                app_contracts.GitHubCapabilityDiagnostic(
                    code="github_capability_ok",
                    capability="actions_read",
                    status="ok",
                    token_source="gh_saved_auth",
                    api="GET /repos/{repo}/actions/runs",
                    severity="info",
                    message="ok",
                    recommended_next_action="none",
                    secret_redacted=True,
                    stderr_sha256=None,
                    group="core",
                ),
                app_contracts.GitHubCapabilityDiagnostic(
                    code="github_rate_limited",
                    capability="pull_reviews_read",
                    status="rate_limited",
                    token_source="gh_saved_auth",
                    api="GET /repos/{repo}/pulls/{pr}/reviews",
                    severity="warning",
                    message="GitHub API rate limit exceeded.",
                    recommended_next_action="retry_after_rate_limit_reset",
                    secret_redacted=True,
                    stderr_sha256="def456",
                    group="core",
                ),
                app_contracts.GitHubCapabilityDiagnostic(
                    code="github_auth_missing",
                    capability="issue_comments_read",
                    status="auth_missing",
                    token_source="gh_saved_auth",
                    api="GET /repos/{repo}/issues/{pr}/comments",
                    severity="blocking",
                    message="GitHub authentication is missing.",
                    recommended_next_action="authenticate_gh_or_set_token",
                    secret_redacted=True,
                    stderr_sha256="ghi789",
                    group="core",
                ),
                app_contracts.GitHubCapabilityDiagnostic(
                    code="github_schema_unavailable",
                    capability="pull_review_threads_read",
                    status="schema_unavailable",
                    token_source="gh_saved_auth",
                    api="GraphQL PullRequest.reviewDecision/reviewThreads",
                    severity="warning",
                    message="GitHub review thread GraphQL schema is unavailable.",
                    recommended_next_action="inspect_gh_version_or_api_schema",
                    secret_redacted=True,
                    stderr_sha256="jkl012",
                    group="core",
                ),
            ])
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                github_capability_gateway=gateway,
            )

            result = app_doctor.doctor(
                app_contracts.DoctorRequest(
                    github_repo="example/repo",
                    github_pr=123,
                    github_head_sha="abcde12345",
                    github_extended=True,
                ),
                ports,
            )

            assert result.ok
            assert gateway.requests[0].include_extended is True
            text = _render_doctor_text(app_contracts, result)
            rendered = "\n".join(text.stdout_lines + text.stderr_lines + text.warnings)
            assert "github capability diagnostics=4" in rendered
            assert "[github:core]" in rendered
            assert "[github:extended]" not in rendered
            assert "capability=actions_read status=ok" in rendered
            assert "capability=pull_reviews_read status=rate_limited" in rendered
            assert "capability=issue_comments_read status=auth_missing" in rendered
            assert "capability=pull_review_threads_read status=schema_unavailable" in rendered
            assert "check_runs_read" not in rendered
            assert "commit_statuses_read" not in rendered
            assert "status_check_rollup_read" not in rendered

    def test_doctor_distinguishes_auth_missing_from_permission_denied_without_gh_token(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            gateway = _StubGitHubCapabilityGateway([
                app_contracts.GitHubCapabilityDiagnostic(
                    code="github_auth_missing",
                    capability="pull_request_read",
                    status="auth_missing",
                    token_source="unknown",
                    api="gh pr view",
                    severity="blocking",
                    message="GitHub authentication is missing.",
                    recommended_next_action="authenticate_gh_or_set_token",
                    secret_redacted=True,
                    stderr_sha256="sha",
                    group="core",
                )
            ])
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                github_capability_gateway=gateway,
            )

            result = app_doctor.doctor(
                app_contracts.DoctorRequest(
                    github_repo="example/repo",
                    github_pr=123,
                    github_head_sha="abcde12345",
                ),
                ports,
            )

            text = _render_doctor_text(app_contracts, result)
            rendered = "\n".join(text.stdout_lines + text.stderr_lines + text.warnings)
            assert result.ok
            assert "token_source=unknown" in rendered
            assert "status=auth_missing" in rendered
            assert "status=permission_denied" not in rendered
            assert _SECRET_TOKEN not in rendered

    def test_doctor_renders_rate_transient_and_schema_statuses_distinctly(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        statuses = [
            ("github_rate_limited", "actions_read", "rate_limited"),
            ("github_transient_unknown", "pull_request_read", "transient_unknown"),
            ("github_schema_unavailable", "pull_review_comments_read", "schema_unavailable"),
        ]
        diagnostics = [
            app_contracts.GitHubCapabilityDiagnostic(
                code=code,
                capability=capability,
                status=status,
                token_source="GH_TOKEN",
                api="fixed api",
                severity="warning",
                message=status,
                recommended_next_action="retry_or_inspect_github",
                secret_redacted=True,
                stderr_sha256=status,
                group="core",
            )
            for code, capability, status in statuses
        ]
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                github_capability_gateway=_StubGitHubCapabilityGateway(diagnostics),
            )

            result = app_doctor.doctor(
                app_contracts.DoctorRequest(
                    github_repo="example/repo",
                    github_pr=123,
                    github_head_sha="abcde12345",
                ),
                ports,
            )

            text = _render_doctor_text(app_contracts, result)
            rendered = "\n".join(text.stdout_lines + text.stderr_lines + text.warnings)
            assert result.ok
            assert "status=rate_limited" in rendered
            assert "status=transient_unknown" in rendered
            assert "status=schema_unavailable" in rendered
            assert "status=permission_denied" not in rendered

    @pytest.mark.parametrize(
        "stderr", ('Unknown JSON field: "statusCheckRollup"', "unknown json field: statusCheckRollup")
    )
    def test_github_capability_cli_classifies_unknown_json_field_as_schema_unavailable(self, stderr: str) -> None:
        github_capability_cli = _runtime_github_capability_cli()
        completed = subprocess.CompletedProcess(["gh"], 1, "", stderr)

        diagnostic = github_capability_cli._diagnostic_from_completed_process(
            capability="status_check_rollup_read",
            group="core",
            api="gh pr view --json statusCheckRollup",
            completed=completed,
        )

        assert diagnostic.status == "schema_unavailable"
        assert diagnostic.code == "github_schema_unavailable"
        assert diagnostic.recommended_next_action == "inspect_gh_version_or_api_schema"
        assert diagnostic.secret_redacted is True

    def test_github_capability_cli_classifies_integration_permission_denied(self) -> None:
        github_capability_cli = _runtime_github_capability_cli()
        completed = subprocess.CompletedProcess(
            ["gh"],
            1,
            "",
            "GraphQL: Resource not accessible by integration",
        )

        diagnostic = github_capability_cli._diagnostic_from_completed_process(
            capability="check_runs_read",
            group="core",
            api="GET /repos/{repo}/commits/{sha}/check-runs",
            completed=completed,
        )

        assert diagnostic.status == "permission_denied"
        assert diagnostic.code == "github_token_permission_denied"
        assert diagnostic.recommended_next_action == "fix_github_token_permissions"
        assert diagnostic.secret_redacted is True

    def test_issue_222_s05_github_capability_cli_probes_actions_and_review_surfaces_without_checks_api(
        self, monkeypatch
    ) -> None:
        _runtime_app, app_contracts, _app_doctor, _app_ports, _infra_contracts = _runtime_modules()
        github_capability_cli = _runtime_github_capability_cli()
        commands: list[list[str]] = []

        def record_command(command, **_kwargs):
            commands.append(list(command))
            if command[:3] == ["gh", "pr", "view"]:
                return subprocess.CompletedProcess(
                    command,
                    0,
                    json.dumps({
                        "number": 123,
                        "headRefOid": "abcde12345",
                        "baseRefName": "release/1.0",
                        "headRefName": "feature/do-work",
                        "headRepositoryOwner": {"login": "example"},
                        "mergeable": "MERGEABLE",
                    }),
                    "",
                )
            return subprocess.CompletedProcess(command, 0, "{}", "")

        monkeypatch.setattr(github_capability_cli.subprocess, "run", record_command)

        diagnostics = github_capability_cli.GitHubCapabilityCliGateway().probe(
            app_contracts.GitHubCapabilityProbeRequest(
                github_repo="example/repo",
                github_pr=123,
                github_head_sha="abcde12345",
            )
        )

        assert [diagnostic.capability for diagnostic in diagnostics] == [
            "repo_metadata_read",
            "pull_request_read",
            "actions_read",
            "issue_comments_read",
            "pull_reviews_read",
            "pull_review_comments_read",
            "pull_review_threads_read",
        ]
        rendered_commands = "\n".join(" ".join(command) for command in commands)
        assert "number,headRefOid" in rendered_commands
        assert "gh api graphql" in rendered_commands
        assert "owner=example" in rendered_commands
        assert "name=repo" in rendered_commands
        assert "reviewDecision" in rendered_commands
        assert "reviewThreads(first:1)" in rendered_commands
        assert "mergeable" not in rendered_commands
        assert "baseRefName" not in rendered_commands
        assert "headRefName" not in rendered_commands
        assert "headRepositoryOwner" not in rendered_commands
        assert "repos/example/repo/compare/main...feature" not in rendered_commands
        assert "repos/example/repo/branches/main" not in rendered_commands
        assert "repos/example/repo/branches/main/protection" not in rendered_commands
        assert "/check-runs" not in rendered_commands
        assert "/status" not in rendered_commands
        assert "statusCheckRollup" not in rendered_commands

    def test_issue_222_s05_github_capability_cli_extended_does_not_probe_merge_blocker_metadata(
        self, monkeypatch
    ) -> None:
        _runtime_app, app_contracts, _app_doctor, _app_ports, _infra_contracts = _runtime_modules()
        github_capability_cli = _runtime_github_capability_cli()
        commands: list[list[str]] = []

        def record_command(command, **_kwargs):
            commands.append(list(command))
            if command[:3] == ["gh", "pr", "view"]:
                return subprocess.CompletedProcess(
                    command,
                    0,
                    json.dumps({
                        "number": 123,
                        "headRefOid": "abcde12345",
                        "baseRefName": "release/1.0",
                        "headRefName": "feature/do-work",
                        "headRepositoryOwner": {"login": "example"},
                        "mergeable": "MERGEABLE",
                    }),
                    "",
                )
            return subprocess.CompletedProcess(command, 0, "{}", "")

        monkeypatch.setattr(github_capability_cli.subprocess, "run", record_command)

        diagnostics = github_capability_cli.GitHubCapabilityCliGateway().probe(
            app_contracts.GitHubCapabilityProbeRequest(
                github_repo="example/repo",
                github_pr=123,
                github_head_sha="abcde12345",
                include_extended=True,
            )
        )

        assert [diagnostic.capability for diagnostic in diagnostics] == [
            "repo_metadata_read",
            "pull_request_read",
            "actions_read",
            "issue_comments_read",
            "pull_reviews_read",
            "pull_review_comments_read",
            "pull_review_threads_read",
        ]
        rendered_commands = "\n".join(" ".join(command) for command in commands)
        assert "reviewDecision" in rendered_commands
        assert "reviewThreads(first:1)" in rendered_commands
        assert "repos/example/repo/compare/" not in rendered_commands
        assert "repos/example/repo/branches/" not in rendered_commands
        assert "protection" not in rendered_commands
        assert "/check-runs" not in rendered_commands
        assert "/status" not in rendered_commands
        assert "statusCheckRollup" not in rendered_commands

    def test_github_capability_cli_token_source_uses_github_token_when_gh_token_absent(self, monkeypatch) -> None:
        github_capability_cli = _runtime_github_capability_cli()
        monkeypatch.delenv("GH_TOKEN", raising=False)
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_secret_github_token")

        assert github_capability_cli._token_source() == "GITHUB_TOKEN"

    def test_github_capability_cli_token_source_prefers_gh_token(self, monkeypatch) -> None:
        github_capability_cli = _runtime_github_capability_cli()
        monkeypatch.setenv("GH_TOKEN", "ghp_secret_gh_token")
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_secret_github_token")

        assert github_capability_cli._token_source() == "GH_TOKEN"

    def test_github_capability_cli_reports_missing_gh_as_auth_missing(self, monkeypatch) -> None:
        github_capability_cli = _runtime_github_capability_cli()

        def raise_missing_binary(*_args, **_kwargs):
            raise FileNotFoundError("gh")

        monkeypatch.setattr(github_capability_cli.subprocess, "run", raise_missing_binary)

        diagnostic = github_capability_cli._diagnostic_from_completed_process(
            capability="pull_request_read",
            group="core",
            api="gh pr view",
            completed=github_capability_cli._run_fixed_gh(["gh", "pr", "view", "13"]),
        )

        assert diagnostic.status == "auth_missing"
        assert diagnostic.code == "github_auth_missing"
        assert diagnostic.recommended_next_action == "authenticate_gh_or_set_token"
        assert diagnostic.secret_redacted is True
        assert diagnostic.stderr_sha256 is not None

    def test_doctor_detects_missing_artifact(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            (issue_dir / "plan.md").unlink(missing_ok=False)

            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
            )
            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

            assert not result.ok
            assert result.findings[0].code == "missing_artifact"
            assert "plan.md" in result.findings[0].message
            assert result.findings[0].guidance

    def test_doctor_detects_duplicate_discussion_sequence(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, _infra_contracts = _runtime_modules()
        ports = app_ports.Ports(
            node_reader=_FailingNodeReader(
                "Duplicate discussion sequence detected under /repo/spec-dock/x/discussions: seq=001 files=[001-adr-first.md, 001-disc-second.md]"
            ),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
        )
        result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

        assert not result.ok
        assert result.findings[0].code == "duplicate_seq"
        assert "Duplicate discussion sequence detected" in result.findings[0].message
        assert result.findings[0].guidance
        assert any("重複している discussion markdown" in line for line in result.findings[0].guidance)
        assert any("spec-dock/scripts/spec-dock validate" in line for line in result.findings[0].guidance)

    def test_doctor_detects_duplicate_discussion_timestamps(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        cases = (
            (
                "slot",
                (
                    "20260312t010203z-adr-first.md",
                    "20260312t010203z-disc-second.md",
                ),
                "Duplicate discussion timestamp slot detected",
            ),
            (
                "suffix",
                (
                    "20260312t010203z-01-adr-first.md",
                    "20260312t010203z-01-disc-second.md",
                ),
                "Duplicate discussion timestamp suffix detected",
            ),
        )

        for _label, filenames, expected_message in cases:
            with tempfile.TemporaryDirectory() as tmp:
                repo_root = Path(tmp)
                specdock_dir = repo_root / "spec-dock"
                records, issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
                discussions_dir = issue_dir / "discussions"
                discussions_dir.mkdir(parents=True, exist_ok=True)
                for filename in filenames:
                    (discussions_dir / filename).write_text(f"{filename}\n", encoding="utf-8")

                ports = app_ports.Ports(
                    node_reader=_StubNodeReader(records),
                    repo_root=repo_root,
                    specdock_dir=specdock_dir,
                )
                result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

                assert not result.ok
                assert result.findings[0].code == "duplicate_seq"
                assert expected_message in result.findings[0].message
                assert result.findings[0].guidance
                assert any("重複している discussion markdown" in line for line in result.findings[0].guidance)
                assert not any("重複 sequence" in line for line in result.findings[0].guidance)
                assert any("spec-dock/scripts/spec-dock validate" in line for line in result.findings[0].guidance)

    def test_doctor_detects_malformed_discussion_doc_filename(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, _infra_contracts = _runtime_modules()
        ports = app_ports.Ports(
            node_reader=_FailingNodeReader(
                "Malformed discussion document filename under /repo/spec-dock/x/discussions: "
                "20260329x-adr-kickoff.md. Expected `<ts>-<kind>-<slug>.md`, "
                "`<ts>-<nn>-<kind>-<slug>.md`, or grandfathered `<nnn>-<kind>-<slug>.md`."
            ),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
        )
        result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

        assert not result.ok
        assert result.findings[0].code == "malformed_discussion_doc"
        assert "Malformed discussion document filename" in result.findings[0].message
        assert result.findings[0].guidance
        assert any("discussions 配下" in line for line in result.findings[0].guidance)
        assert any("spec-dock/scripts/spec-dock validate" in line for line in result.findings[0].guidance)

    def test_doctor_detects_malformed_discussion_doc_filename_from_repo_backed_validation(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        infra_fs_repo = _runtime_fs_repo()

        class _RepoBackedNodeReader:
            def __init__(self, specdock_dir: Path):
                self._specdock_dir = specdock_dir

            def load_node_records(self):
                return infra_fs_repo.load_node_records(self._specdock_dir)

        cases = (
            "20260329x-adr-kickoff.md",
            "foo-adr-kickoff.md",
            "bogus-01-adr-kickoff.md",
        )
        for malformed_name in cases:
            with tempfile.TemporaryDirectory() as tmp:
                repo_root = Path(tmp)
                specdock_dir = repo_root / "spec-dock"
                _records, issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
                discussions_dir = issue_dir / "discussions"
                discussions_dir.mkdir(parents=True, exist_ok=True)
                (discussions_dir / malformed_name).write_text("# malformed\n", encoding="utf-8")

                ports = app_ports.Ports(
                    node_reader=_RepoBackedNodeReader(specdock_dir),
                    repo_root=repo_root,
                    specdock_dir=specdock_dir,
                )
                result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

                assert not result.ok
                assert result.findings[0].code == "malformed_discussion_doc"
                assert "Malformed discussion document filename under" in result.findings[0].message
                assert malformed_name in result.findings[0].message
                assert "Expected `<ts>-<kind>-<slug>.md`" in result.findings[0].message
                assert result.findings[0].guidance
                assert any("discussions 配下" in line for line in result.findings[0].guidance)
                assert any("spec-dock/scripts/spec-dock validate" in line for line in result.findings[0].guidance)

    def test_doctor_detects_duplicate_id(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            second_issue_dir = issue_dir.parent / "iss-local-1-add-refresh-token-alias"
            second_issue_record = _record(
                infra_contracts,
                kind="issue",
                node_id="iss-local-1",
                title="Add Refresh Token Alias",
                path=second_issue_dir,
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=104,
                github_repo_owner="example",
                github_repo_name="repo",
            )
            _write_record_artifacts(second_issue_record)
            records.append(second_issue_record)

            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
            )
            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

            assert not result.ok
            assert result.findings[0].code == "duplicate_id"
            assert "Duplicate numeric id detected" in result.findings[0].message
            assert result.findings[0].guidance
            assert any(".meta.json" in line for line in result.findings[0].guidance)
            assert any("spec-dock/scripts/spec-dock validate" in line for line in result.findings[0].guidance)

    def test_doctor_detects_exact_duplicate_id_message(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            duplicate_issue_dir = issue_dir.parent / "iss-local-00001-add-refresh-token-duplicate"
            duplicate_issue_record = _record(
                infra_contracts,
                kind="issue",
                node_id="iss-local-00001",
                title="Add Refresh Token Duplicate",
                path=duplicate_issue_dir,
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=105,
                github_repo_owner="example",
                github_repo_name="repo",
            )
            _write_record_artifacts(duplicate_issue_record)
            records.append(duplicate_issue_record)

            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
            )
            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

            assert not result.ok
            assert result.findings[0].code == "duplicate_id"
            assert "Duplicate id detected" in result.findings[0].message
            assert "Duplicate numeric id detected" not in result.findings[0].message
            assert result.findings[0].guidance

    def test_doctor_detects_raw_empty_container_dependency_cycle(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            records.pop()
            second_epic_dir = Path(records[0].path) / "epics" / "epic-local-00002-session-auth"
            second_epic_record = _record(
                infra_contracts,
                kind="epic",
                node_id="epic-local-00002",
                title="Session Auth",
                path=second_epic_dir,
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=104,
                github_repo_owner="example",
                github_repo_name="repo",
            )
            _write_record_artifacts(second_epic_record)
            records.append(second_epic_record)

            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubRawDepsTopologyReader(
                    infra_contracts,
                    {
                        "epic-local-00001": ["epic-local-00002"],
                        "epic-local-00002": ["epic-local-00001"],
                    },
                ),
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

            assert not result.ok
            assert result.findings[0].code == "validation_error"
            assert "Dependency cycle detected" in result.findings[0].message
            assert any("spec-dock/scripts/spec-dock validate" in line for line in result.findings[0].guidance)

    def test_doctor_detects_legacy_unscoped_github_linkage_when_current_repo_is_resolved(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            records[0] = _record(
                infra_contracts,
                kind="initiative",
                node_id="init-local-00001",
                title="Auth Platform",
                path=Path(records[0].path),
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=123,
            )
            _write_record_artifacts(records[0])
            records[2] = _record(
                infra_contracts,
                kind="issue",
                node_id="iss-local-00001",
                title="Add Refresh Token",
                path=Path(records[2].path),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=123,
                github_repo_owner="other",
                github_repo_name="repo",
            )
            _write_record_artifacts(records[2])

            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                git_gateway=_StubGitGateway("example/repo"),
            )
            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

            assert not result.ok
            assert result.findings[0].code == "broken_meta"
            assert "legacy unscoped github linkage" in result.findings[0].message

    def test_doctor_detects_broken_meta_when_reader_fails(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, _infra_contracts = _runtime_modules()
        ports = app_ports.Ports(
            node_reader=_FailingNodeReader("Invalid .meta.json (expected object): /repo/spec-dock/x/.meta.json"),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
        )

        result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
        assert not result.ok
        assert result.findings[0].code == "broken_meta"
        assert "Invalid .meta.json" in result.findings[0].message
        assert result.findings[0].guidance
        assert any(".meta.json" in line for line in result.findings[0].guidance)
        assert any("spec-dock/scripts/spec-dock validate" in line for line in result.findings[0].guidance)

    def test_doctor_detects_broken_meta_when_reader_reports_invalid_json_for_meta(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, _infra_contracts = _runtime_modules()
        ports = app_ports.Ports(
            node_reader=_FailingNodeReader(
                "Invalid JSON: /repo/spec-dock/initiatives/init-local-00001-alpha/.meta.json: Expecting value"
            ),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
        )

        result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
        assert not result.ok
        assert result.findings[0].code == "broken_meta"
        assert "Invalid JSON:" in result.findings[0].message

    def test_doctor_detects_broken_meta_when_required_field_is_missing(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            initiative_path = Path(records[0].path)
            records[0] = _record(
                infra_contracts,
                kind="initiative",
                node_id="init-local-00001",
                title="",
                path=initiative_path,
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=101,
                github_repo_owner="example",
                github_repo_name="repo",
            )
            _write_record_artifacts(records[0])
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
            assert not result.ok
            assert result.findings[0].code == "broken_meta"
            assert "Missing title in .meta.json" in result.findings[0].message

    def test_doctor_skips_stale_active_pointer_id_check_when_graph_is_unavailable(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            del records
            load_result = infra_contracts.ActiveManifestLoadResult(
                manifest=infra_contracts.ActiveManifest(
                    initiative=None,
                    epic=None,
                    issue=infra_contracts.ActiveManifestEntry(
                        id="iss-local-00001",
                        path=issue_dir.as_posix(),
                    ),
                ),
                source="agent.active",
                warnings=[],
            )
            ports = app_ports.Ports(
                node_reader=_FailingNodeReader(f"Invalid .meta.json (expected object): {issue_dir / '.meta.json'}"),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                active_state_store=_StubActiveStateStore(load_result),
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
            assert not result.ok
            codes = [finding.code for finding in result.findings]
            assert "broken_meta" in codes
            assert "stale_active_pointer" not in codes

    def test_doctor_detects_stale_active_pointer(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            load_result = infra_contracts.ActiveManifestLoadResult(
                manifest=infra_contracts.ActiveManifest(
                    initiative=infra_contracts.ActiveManifestEntry(
                        id="init-local-00001",
                        path="spec-dock/initiatives/init-local-00001-auth-platform",
                    ),
                    epic=None,
                    issue=infra_contracts.ActiveManifestEntry(
                        id="iss-local-99999",
                        path="spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-99999-missing",
                    ),
                ),
                source="agent.active",
                warnings=[],
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                active_state_store=_StubActiveStateStore(load_result),
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
            codes = [finding.code for finding in result.findings]
            assert "stale_active_pointer" in codes
            stale_finding = next(
                (finding for finding in result.findings if finding.code == "stale_active_pointer"), None
            )
            assert stale_finding is not None
            if stale_finding is None:
                pytest.fail("stale_active_pointer finding was not returned")
            assert stale_finding.guidance
            assert any("active clear" in line for line in stale_finding.guidance)
            assert any("active set <target>" in line for line in stale_finding.guidance)

    def test_doctor_detects_stale_active_pointer_for_absolute_path_outside_repo(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside_tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            outside_issue_dir = Path(outside_tmp) / "iss-local-00001-outside"
            _write_required_docs(outside_issue_dir)
            load_result = infra_contracts.ActiveManifestLoadResult(
                manifest=infra_contracts.ActiveManifest(
                    initiative=None,
                    epic=None,
                    issue=infra_contracts.ActiveManifestEntry(
                        id="iss-local-00001",
                        path=outside_issue_dir.as_posix(),
                    ),
                ),
                source="agent.active",
                warnings=[],
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                active_state_store=_StubActiveStateStore(load_result),
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
            codes = [finding.code for finding in result.findings]
            assert "stale_active_pointer" in codes
            stale_finding = next(
                (finding for finding in result.findings if finding.code == "stale_active_pointer"), None
            )
            assert stale_finding is not None
            if stale_finding is None:
                pytest.fail("stale_active_pointer finding was not returned")
            assert "issue.path" in stale_finding.message

    def test_doctor_detects_stale_active_pointer_when_manifest_path_points_to_file(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            readme_path = specdock_dir / "README.md"
            readme_path.write_text("not a node directory\n", encoding="utf-8")

            load_result = infra_contracts.ActiveManifestLoadResult(
                manifest=infra_contracts.ActiveManifest(
                    initiative=None,
                    epic=None,
                    issue=infra_contracts.ActiveManifestEntry(
                        id="iss-local-00001",
                        path="spec-dock/README.md",
                    ),
                ),
                source="agent.active",
                warnings=[],
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                active_state_store=_StubActiveStateStore(load_result),
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
            codes = [finding.code for finding in result.findings]
            assert "stale_active_pointer" in codes
            stale_finding = next(
                (finding for finding in result.findings if finding.code == "stale_active_pointer"), None
            )
            assert stale_finding is not None
            if stale_finding is None:
                pytest.fail("stale_active_pointer finding was not returned")
            assert "issue.path is not a directory" in stale_finding.message

    def test_doctor_detects_stale_active_pointer_id_mismatch_when_graph_ids_are_empty(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            existing_issue_dir = specdock_dir / "issues" / "iss-local-99999-existing"
            _write_required_docs(existing_issue_dir)
            load_result = infra_contracts.ActiveManifestLoadResult(
                manifest=infra_contracts.ActiveManifest(
                    initiative=None,
                    epic=None,
                    issue=infra_contracts.ActiveManifestEntry(
                        id="iss-local-99999",
                        path=existing_issue_dir.as_posix(),
                    ),
                ),
                source="agent.active",
                warnings=[],
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader([]),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                active_state_store=_StubActiveStateStore(load_result),
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
            codes = [finding.code for finding in result.findings]
            assert "stale_active_pointer" in codes
            stale_finding = next(
                (finding for finding in result.findings if finding.code == "stale_active_pointer"), None
            )
            assert stale_finding is not None
            if stale_finding is None:
                pytest.fail("stale_active_pointer finding was not returned")
            assert "issue.id=iss-local-99999 is not found in current graph" in stale_finding.message

    def test_doctor_reports_stale_active_pointer_when_manifest_is_invalid_and_missing(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            load_result = infra_contracts.ActiveManifestLoadResult(
                manifest=None,
                source="none",
                warnings=["active_manifest_invalid_shape:agent.active"],
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                active_state_store=_StubActiveStateStore(load_result),
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
            assert not result.ok
            codes = [finding.code for finding in result.findings]
            assert "stale_active_pointer" in codes
            stale_finding = next(
                (finding for finding in result.findings if finding.code == "stale_active_pointer"), None
            )
            assert stale_finding is not None
            if stale_finding is None:
                pytest.fail("stale_active_pointer finding was not returned")
            assert "active_manifest_invalid_shape:agent.active" in stale_finding.message
            assert any("active clear" in line for line in stale_finding.guidance)
            assert any("active set <target>" in line for line in stale_finding.guidance)
            assert "active_manifest_invalid_shape:agent.active" in result.warnings

    def test_doctor_detects_stale_create_lock(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            lock_path = specdock_dir / "system" / ".runtime" / "create.lock"
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path.write_text(
                "\n".join([
                    "token=abc",
                    "pid=1234",
                    "user=tester",
                    "created_unix=0",
                    "created_iso=2026-03-01",
                ])
                + "\n",
                encoding="utf-8",
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
            assert not result.ok
            finding = next((item for item in result.findings if item.code == "stale_create_lock"), None)
            assert finding is not None
            if finding is None:
                pytest.fail("stale_create_lock finding was not returned")
            assert "stale=true" in finding.message
            assert str(lock_path) in finding.message
            assert any("create 実行中プロセス" in line for line in finding.guidance)
            assert any(str(lock_path) in line for line in finding.guidance)

    def test_doctor_detects_invalid_create_lock_metadata(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            lock_path = specdock_dir / "system" / ".runtime" / "create.lock"
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path.write_text("pid=1234\n", encoding="utf-8")
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
            assert not result.ok
            finding = next((item for item in result.findings if item.code == "stale_create_lock"), None)
            assert finding is not None
            if finding is None:
                pytest.fail("stale_create_lock finding was not returned")
            assert "metadata=missing_fields" in finding.message
            assert str(lock_path) in finding.message

    def test_doctor_detects_non_stale_create_lock_contention(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            lock_path = specdock_dir / "system" / ".runtime" / "create.lock"
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path.write_text(
                "\n".join([
                    "token=running",
                    "pid=5678",
                    "user=tester",
                    f"created_unix={time.time():.6f}",
                    "created_iso=2026-03-18",
                ])
                + "\n",
                encoding="utf-8",
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
            assert not result.ok
            finding = next((item for item in result.findings if item.code == "stale_create_lock"), None)
            assert finding is not None
            if finding is None:
                pytest.fail("stale_create_lock finding was not returned")
            assert "stale=false" in finding.message
            assert "contention=true" in finding.message
            assert any("create 実行中" in line for line in finding.guidance)
            assert any("削除" in line for line in finding.guidance)

    def test_issue_78_doctor_reports_legacy_only_workspace_as_finding(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, _infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            legacy_dir = repo_root / ".spec-dock"
            legacy_dir.mkdir(parents=True, exist_ok=True)

            ports = app_ports.Ports(
                node_reader=_StubNodeReader([]),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
            )
            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

            assert not result.ok
            assert len(result.findings) == 1
            finding = result.findings[0]
            assert finding.code == "legacy_only_workspace"
            assert str(legacy_dir) in finding.message
            assert any("Do not rename '.spec-dock'" in line for line in finding.guidance)
            assert any("spec-dock init" in line for line in finding.guidance)
            assert any("migrate" in line.lower() for line in finding.guidance)

    def test_issue_78_doctor_reports_cleanup_pending_warning_for_valid_coexistence(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            legacy_dir = repo_root / ".spec-dock"
            legacy_dir.mkdir(parents=True, exist_ok=True)

            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
            )
            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

            assert result.ok
            assert result.findings == []
            assert "legacy_cleanup_pending" in result.warnings

    def test_issue_78_main_doctor_renders_cleanup_pending_warning_message(self) -> None:
        runtime_app, app_contracts, _app_doctor, _app_ports, _infra_contracts = _runtime_modules()
        from spec_dock_runtime.cli import bootstrap as cli_bootstrap

        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_application_doctor = cli_bootstrap.application_doctor
        runtime_app._find_specdock_dir = lambda: Path("/repo/spec-dock")
        cli_bootstrap.application_doctor = lambda _req, _ports: app_contracts.DoctorResult(
            ok=True,
            findings=[],
            warnings=["legacy_cleanup_pending"],
        )
        try:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = runtime_app.main(["doctor"])
        finally:
            runtime_app._find_specdock_dir = original_find_specdock_dir
            cli_bootstrap.application_doctor = original_application_doctor

        assert exit_code == 0
        assert stdout.getvalue() == "spec-dock: ok (doctor) findings=0\n"
        stderr_text = stderr.getvalue()
        assert "spec-dock: (warn) legacy '.spec-dock/' is still present." in stderr_text
        assert "legacy_cleanup_pending" not in stderr_text

    def test_issue_78_main_doctor_reaches_legacy_only_workspace_guidance(self) -> None:
        runtime_app, _app_contracts, _app_doctor, _app_ports, _infra_contracts = _runtime_modules()
        original_cwd = Path.cwd()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                repo_root = Path(tmp)
                (repo_root / ".spec-dock").mkdir(parents=True, exist_ok=True)
                os.chdir(repo_root)
                stdout = io.StringIO()
                stderr = io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    exit_code = runtime_app.main(["doctor"])
        finally:
            os.chdir(original_cwd)

        assert exit_code == 1
        assert stdout.getvalue() == ""
        stderr_text = stderr.getvalue()
        assert "spec-dock: doctor: findings=1" in stderr_text
        assert "[legacy_only_workspace]" in stderr_text
        assert "Do not rename '.spec-dock'" in stderr_text
        assert "spec-dock init" in stderr_text

    def test_main_doctor_delegates_to_use_case(self) -> None:
        runtime_app, app_contracts, _app_doctor, _app_ports, _infra_contracts = _runtime_modules()
        from spec_dock_runtime.cli import bootstrap as cli_bootstrap

        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_application_doctor = cli_bootstrap.application_doctor
        runtime_app._find_specdock_dir = lambda: Path("/repo/spec-dock")
        cli_bootstrap.application_doctor = lambda _req, _ports: app_contracts.DoctorResult(
            ok=False,
            findings=[
                app_contracts.DoctorFinding(
                    code="missing_artifact",
                    message="Missing required artifact: kind=issue id=iss-local-00001 artifact=.../plan.md",
                    guidance=["復元してください。"],
                )
            ],
            warnings=[],
        )
        try:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = runtime_app.main(["doctor"])
        finally:
            runtime_app._find_specdock_dir = original_find_specdock_dir
            cli_bootstrap.application_doctor = original_application_doctor

        stderr_text = stderr.getvalue()
        assert exit_code == 1
        assert stdout.getvalue() == ""
        assert "spec-dock: doctor: findings=1" in stderr_text
        assert "[missing_artifact]" in stderr_text
        assert "  -> 復元してください。" in stderr_text

    def test_issue_78_main_doctor_keeps_not_found_when_no_workspace_exists(self) -> None:
        runtime_app, _app_contracts, _app_doctor, _app_ports, _infra_contracts = _runtime_modules()
        original_cwd = Path.cwd()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                repo_root = Path(tmp)
                os.chdir(repo_root)
                stdout = io.StringIO()
                stderr = io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    exit_code = runtime_app.main(["doctor"])
        finally:
            os.chdir(original_cwd)

        assert exit_code == 1
        assert stdout.getvalue() == ""
        assert "'spec-dock' not found. Run 'uvx ... spec-dock init' first." in stderr.getvalue()
