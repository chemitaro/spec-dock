import sys
import tempfile
import unittest
from unittest.mock import patch
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
        from spec_dock_runtime.application import close_node as app_close_node
        from spec_dock_runtime.application import contracts as app_contracts
        from spec_dock_runtime.application import ports as app_ports
        from spec_dock_runtime.cli import bootstrap as cli_bootstrap
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.infra import github_cli as infra_github_cli
        from spec_dock_runtime.infra import contracts as infra_contracts
    finally:
        sys.path.pop(0)
    return app_close_node, app_contracts, app_ports, cli_bootstrap, domain_models, infra_github_cli, infra_contracts


def _record(
    infra_contracts,
    *,
    repo_root: Path,
    kind: str,
    node_id: str,
    slug: str,
    parent_id: str | None,
    initiative_id: str | None,
    epic_id: str | None,
    github_issue_number: int | None,
    github_repo_owner: str | None = None,
    github_repo_name: str | None = None,
):
    if kind == "initiative":
        node_dir = repo_root / "spec-dock" / "initiatives" / f"{node_id}-{slug}"
    elif kind == "epic":
        node_dir = (
            repo_root
            / "spec-dock"
            / "initiatives"
            / "init-local-00001-auth-platform"
            / "epics"
            / f"{node_id}-{slug}"
        )
    else:
        node_dir = (
            repo_root
            / "spec-dock"
            / "initiatives"
            / "init-local-00001-auth-platform"
            / "epics"
            / "epic-local-00001-jwt-auth"
            / "issues"
            / f"{node_id}-{slug}"
        )
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=node_id,
        slug=slug,
        path=node_dir.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(node_dir / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )


def _snapshot(domain_models, *, issue_number: int, state: str, repo_owner: str = "example", repo_name: str = "repo"):
    return domain_models.IssueSnapshot(
        issue_number=issue_number,
        state=state,
        title=f"Issue {issue_number}",
        labels=[],
        updated_at="2026-04-09T00:00:00Z",
        url=f"https://github.com/{repo_owner}/{repo_name}/issues/{issue_number}",
        repo_owner=repo_owner,
        repo_name=repo_name,
    )


class _StubNodeReader:
    def __init__(self, records):
        self.records = list(records)

    def load_node_records(self):
        return list(self.records)


class _StubIssueGateway:
    def __init__(self, *, view_snapshots=None, close_snapshot=None, close_error: str | None = None):
        self.view_snapshots = list(view_snapshots or [])
        self.close_snapshot = close_snapshot
        self.close_error = close_error
        self.view_calls = []
        self.close_calls = []

    def issue_view_snapshot(self, repo_root, issue_number, *, repo_slug=None):
        self.view_calls.append((str(repo_root), int(issue_number), repo_slug))
        if not self.view_snapshots:
            raise RuntimeError("missing issue view snapshot stub")
        return self.view_snapshots.pop(0)

    def issue_close(self, repo_root, issue_number, *, repo_slug=None):
        self.close_calls.append((str(repo_root), int(issue_number), repo_slug))
        if self.close_error is not None:
            raise RuntimeError(self.close_error)
        if self.close_snapshot is None:
            raise RuntimeError("missing issue close snapshot stub")
        return self.close_snapshot


class _StubGitGateway:
    def __init__(self, origin_repo_slug: str | None):
        self.origin_repo_slug_value = origin_repo_slug

    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return self.origin_repo_slug_value


class TestRuntimeCloseS12(unittest.TestCase):
    def _ports(self, *, repo_root: Path, records, issue_gateway):
        _app_close_node, _app_contracts, app_ports, _cli_bootstrap, _domain_models, _infra_github_cli, _infra_contracts = _runtime_modules()
        return app_ports.Ports(
            node_reader=_StubNodeReader(records),
            repo_root=repo_root,
            specdock_dir=repo_root / "spec-dock",
            issue_gateway=issue_gateway,
        )

    def test_close_node_fails_when_target_has_no_linked_github_issue(self) -> None:
        app_close_node, app_contracts, _app_ports, _cli_bootstrap, _domain_models, _infra_github_cli, infra_contracts = _runtime_modules()
        repo_root = Path("/repo")
        records = [
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="initiative",
                node_id="init-local-00001",
                slug="auth-platform",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=101,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00001",
                slug="jwt-auth",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=201,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00001",
                slug="target",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=None,
            ),
        ]
        issue_gateway = _StubIssueGateway()
        ports = self._ports(repo_root=repo_root, records=records, issue_gateway=issue_gateway)

        with self.assertRaisesRegex(RuntimeError, "not linked to a GitHub issue"):
            app_close_node.close_node(
                app_contracts.CloseNodeRequest(
                    target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None)
                ),
                ports,
            )

        self.assertEqual(issue_gateway.view_calls, [])
        self.assertEqual(issue_gateway.close_calls, [])

    def test_close_node_gh_failure_leaves_local_tree_unchanged(self) -> None:
        app_close_node, app_contracts, _app_ports, _cli_bootstrap, domain_models, _infra_github_cli, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            issue_record = _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00001",
                slug="target",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=301,
                github_repo_owner="example",
                github_repo_name="repo",
            )
            issue_dir = Path(issue_record.path)
            issue_dir.mkdir(parents=True, exist_ok=True)
            (issue_dir / "requirement.md").write_text("# requirement\n", encoding="utf-8")
            records = [
                _record(
                    infra_contracts,
                    repo_root=repo_root,
                    kind="initiative",
                    node_id="init-local-00001",
                    slug="auth-platform",
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=101,
                ),
                _record(
                    infra_contracts,
                    repo_root=repo_root,
                    kind="epic",
                    node_id="epic-local-00001",
                    slug="jwt-auth",
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=201,
                ),
                issue_record,
            ]
            issue_gateway = _StubIssueGateway(
                view_snapshots=[
                    _snapshot(domain_models, issue_number=301, state="OPEN"),
                    _snapshot(domain_models, issue_number=301, state="OPEN"),
                ],
                close_error="gh issue close failed",
            )
            ports = self._ports(repo_root=repo_root, records=records, issue_gateway=issue_gateway)

            with self.assertRaisesRegex(RuntimeError, "gh issue close failed"):
                app_close_node.close_node(
                    app_contracts.CloseNodeRequest(
                        target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None)
                    ),
                    ports,
                )

            self.assertTrue(issue_dir.is_dir())
            self.assertTrue((issue_dir / "requirement.md").is_file())
            self.assertEqual(
                issue_gateway.close_calls,
                [(str(repo_root), 301, "example/repo")],
            )

    def test_close_node_already_closed_returns_success_noop(self) -> None:
        app_close_node, app_contracts, _app_ports, _cli_bootstrap, domain_models, _infra_github_cli, infra_contracts = _runtime_modules()
        repo_root = Path("/repo")
        records = [
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="initiative",
                node_id="init-local-00001",
                slug="auth-platform",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=101,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00001",
                slug="jwt-auth",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=201,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00001",
                slug="target",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=301,
                github_repo_owner="example",
                github_repo_name="repo",
            ),
        ]
        issue_gateway = _StubIssueGateway(
            view_snapshots=[_snapshot(domain_models, issue_number=301, state="CLOSED")]
        )
        ports = self._ports(repo_root=repo_root, records=records, issue_gateway=issue_gateway)

        result = app_close_node.close_node(
            app_contracts.CloseNodeRequest(
                target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None)
            ),
            ports,
        )

        self.assertTrue(result.already_closed)
        self.assertEqual(result.node_id, "iss-local-00001")
        self.assertEqual(result.node_kind, "issue")
        self.assertEqual(result.github_issue_number, 301)
        self.assertEqual(result.issue_snapshot.state, "CLOSED")
        self.assertEqual(issue_gateway.close_calls, [])

    def test_close_node_read_after_close_race_returns_success_noop(self) -> None:
        app_close_node, app_contracts, _app_ports, _cli_bootstrap, domain_models, _infra_github_cli, infra_contracts = _runtime_modules()
        repo_root = Path("/repo")
        records = [
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="initiative",
                node_id="init-local-00001",
                slug="auth-platform",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=101,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00001",
                slug="jwt-auth",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=201,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00001",
                slug="target",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=301,
                github_repo_owner="example",
                github_repo_name="repo",
            ),
        ]
        issue_gateway = _StubIssueGateway(
            view_snapshots=[
                _snapshot(domain_models, issue_number=301, state="OPEN"),
                _snapshot(domain_models, issue_number=301, state="CLOSED"),
            ],
            close_error="already closed by another writer",
        )
        ports = self._ports(repo_root=repo_root, records=records, issue_gateway=issue_gateway)

        result = app_close_node.close_node(
            app_contracts.CloseNodeRequest(
                target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None)
            ),
            ports,
        )

        self.assertTrue(result.already_closed)
        self.assertEqual(result.issue_snapshot.state, "CLOSED")
        self.assertEqual(len(issue_gateway.view_calls), 2)
        self.assertEqual(issue_gateway.close_calls, [(str(repo_root), 301, "example/repo")])

    def test_close_node_non_cascade_for_epic_target(self) -> None:
        app_close_node, app_contracts, _app_ports, _cli_bootstrap, domain_models, _infra_github_cli, infra_contracts = _runtime_modules()
        repo_root = Path("/repo")
        records = [
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="initiative",
                node_id="init-local-00001",
                slug="auth-platform",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=101,
                github_repo_owner="example",
                github_repo_name="repo",
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00001",
                slug="jwt-auth",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=201,
                github_repo_owner="example",
                github_repo_name="repo",
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00001",
                slug="child",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=301,
                github_repo_owner="example",
                github_repo_name="repo",
            ),
        ]
        issue_gateway = _StubIssueGateway(
            view_snapshots=[_snapshot(domain_models, issue_number=201, state="OPEN")],
            close_snapshot=_snapshot(domain_models, issue_number=201, state="CLOSED"),
        )
        ports = self._ports(repo_root=repo_root, records=records, issue_gateway=issue_gateway)

        result = app_close_node.close_node(
            app_contracts.CloseNodeRequest(
                target=app_contracts.TargetRef(kind="node_id", node_id="epic-local-00001", github_issue_number=None)
            ),
            ports,
        )

        self.assertFalse(result.already_closed)
        self.assertEqual(result.node_kind, "epic")
        self.assertEqual(result.github_issue_number, 201)
        self.assertEqual(issue_gateway.close_calls, [(str(repo_root), 201, "example/repo")])

    def test_close_node_non_cascade_for_initiative_target(self) -> None:
        app_close_node, app_contracts, _app_ports, _cli_bootstrap, domain_models, _infra_github_cli, infra_contracts = _runtime_modules()
        repo_root = Path("/repo")
        records = [
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="initiative",
                node_id="init-local-00001",
                slug="auth-platform",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=101,
                github_repo_owner="example",
                github_repo_name="repo",
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00001",
                slug="jwt-auth",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=201,
                github_repo_owner="example",
                github_repo_name="repo",
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00001",
                slug="child",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=301,
                github_repo_owner="example",
                github_repo_name="repo",
            ),
        ]
        issue_gateway = _StubIssueGateway(
            view_snapshots=[_snapshot(domain_models, issue_number=101, state="OPEN")],
            close_snapshot=_snapshot(domain_models, issue_number=101, state="CLOSED"),
        )
        ports = self._ports(repo_root=repo_root, records=records, issue_gateway=issue_gateway)

        result = app_close_node.close_node(
            app_contracts.CloseNodeRequest(
                target=app_contracts.TargetRef(kind="node_id", node_id="init-local-00001", github_issue_number=None)
            ),
            ports,
        )

        self.assertFalse(result.already_closed)
        self.assertEqual(result.node_kind, "initiative")
        self.assertEqual(result.github_issue_number, 101)
        self.assertEqual(issue_gateway.close_calls, [(str(repo_root), 101, "example/repo")])

    def test_close_node_unlinked_parent_fails_without_touching_linked_child(self) -> None:
        app_close_node, app_contracts, _app_ports, _cli_bootstrap, _domain_models, _infra_github_cli, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            init_record = _record(
                infra_contracts,
                repo_root=repo_root,
                kind="initiative",
                node_id="init-local-00001",
                slug="auth-platform",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=None,
            )
            init_dir = Path(init_record.path)
            init_dir.mkdir(parents=True, exist_ok=True)
            (init_dir / "requirement.md").write_text("# requirement\n", encoding="utf-8")
            records = [
                init_record,
                _record(
                    infra_contracts,
                    repo_root=repo_root,
                    kind="epic",
                    node_id="epic-local-00001",
                    slug="jwt-auth",
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=201,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
                _record(
                    infra_contracts,
                    repo_root=repo_root,
                    kind="issue",
                    node_id="iss-local-00001",
                    slug="child",
                    parent_id="epic-local-00001",
                    initiative_id="init-local-00001",
                    epic_id="epic-local-00001",
                    github_issue_number=301,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
            ]
            issue_gateway = _StubIssueGateway()
            ports = self._ports(repo_root=repo_root, records=records, issue_gateway=issue_gateway)

            with self.assertRaisesRegex(RuntimeError, "not linked to a GitHub issue"):
                app_close_node.close_node(
                    app_contracts.CloseNodeRequest(
                        target=app_contracts.TargetRef(kind="node_id", node_id="init-local-00001", github_issue_number=None)
                    ),
                    ports,
                )

            self.assertTrue(init_dir.is_dir())
            self.assertEqual(issue_gateway.view_calls, [])
            self.assertEqual(issue_gateway.close_calls, [])

    def test_close_node_github_issue_target_resolves_current_unscoped_node_with_repo_scope(self) -> None:
        app_close_node, app_contracts, app_ports, _cli_bootstrap, domain_models, _infra_github_cli, infra_contracts = _runtime_modules()
        repo_root = Path("/repo")
        records = [
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="initiative",
                node_id="init-local-00001",
                slug="auth-platform",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=101,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00001",
                slug="jwt-auth",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=201,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00001",
                slug="target",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=301,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00002",
                slug="foreign",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=301,
                github_repo_owner="other",
                github_repo_name="repo",
            ),
        ]
        issue_gateway = _StubIssueGateway(
            view_snapshots=[_snapshot(domain_models, issue_number=301, state="CLOSED")]
        )
        ports = app_ports.Ports(
            node_reader=_StubNodeReader(records),
            repo_root=repo_root,
            specdock_dir=repo_root / "spec-dock",
            issue_gateway=issue_gateway,
            git_gateway=_StubGitGateway("example/repo"),
        )

        result = app_close_node.close_node(
            app_contracts.CloseNodeRequest(
                target=app_contracts.TargetRef(
                    kind="github_issue",
                    node_id=None,
                    github_issue_number=301,
                    github_repo_owner="example",
                    github_repo_name="repo",
                )
            ),
            ports,
        )

        self.assertEqual(result.node_id, "iss-local-00001")
        self.assertEqual(issue_gateway.view_calls, [(str(repo_root), 301, "example/repo")])

    def test_close_node_github_issue_target_raises_for_ambiguous_unscoped_match(self) -> None:
        app_close_node, app_contracts, _app_ports, _cli_bootstrap, _domain_models, _infra_github_cli, infra_contracts = _runtime_modules()
        repo_root = Path("/repo")
        records = [
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="initiative",
                node_id="init-local-00001",
                slug="auth-platform",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=101,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00001",
                slug="jwt-auth",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=201,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00001",
                slug="target",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=301,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00002",
                slug="other",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=301,
            ),
        ]
        ports = self._ports(repo_root=repo_root, records=records, issue_gateway=_StubIssueGateway())

        with self.assertRaisesRegex(RuntimeError, "Ambiguous github.issue_number=301"):
            app_close_node.close_node(
                app_contracts.CloseNodeRequest(
                    target=app_contracts.TargetRef(kind="github_issue", node_id=None, github_issue_number=301)
                ),
                ports,
            )

    def test_close_node_github_issue_target_raises_when_repo_scope_does_not_match(self) -> None:
        app_close_node, app_contracts, _app_ports, _cli_bootstrap, _domain_models, _infra_github_cli, infra_contracts = _runtime_modules()
        repo_root = Path("/repo")
        records = [
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="initiative",
                node_id="init-local-00001",
                slug="auth-platform",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=101,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00001",
                slug="jwt-auth",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=201,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00001",
                slug="target",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=301,
                github_repo_owner="example",
                github_repo_name="repo",
            ),
        ]
        ports = self._ports(repo_root=repo_root, records=records, issue_gateway=_StubIssueGateway())

        with self.assertRaisesRegex(RuntimeError, "No node found for github.issue_number=301 in repo scope"):
            app_close_node.close_node(
                app_contracts.CloseNodeRequest(
                    target=app_contracts.TargetRef(
                        kind="github_issue",
                        node_id=None,
                        github_issue_number=301,
                        github_repo_owner="other",
                        github_repo_name="repo",
                    )
                ),
                ports,
            )

    def test_bootstrap_registers_close_node_use_case(self) -> None:
        _app_close_node, app_contracts, _app_ports, cli_bootstrap, _domain_models, _infra_github_cli, _infra_contracts = _runtime_modules()
        runtime = cli_bootstrap.build_runtime(Path("/repo/spec-dock"))
        self.assertTrue(callable(runtime.use_cases.close_node))
        with self.assertRaisesRegex(RuntimeError, "No nodes found"):
            runtime.use_cases.close_node(
                app_contracts.CloseNodeRequest(
                    target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None)
                )
            )

    def test_bootstrap_issue_gateway_forwards_issue_close(self) -> None:
        _app_close_node, _app_contracts, _app_ports, cli_bootstrap, _domain_models, _infra_github_cli, _infra_contracts = _runtime_modules()
        gateway = cli_bootstrap._IssueGateway()
        with patch.object(cli_bootstrap.infra_github_cli, "issue_close", return_value="closed") as issue_close:
            result = gateway.issue_close(Path("/repo"), 301, repo_slug="example/repo")

        self.assertEqual(result, "closed")
        issue_close.assert_called_once_with(Path("/repo"), issue_number=301, repo_slug="example/repo")

    def test_issue_close_raw_adds_repo_scope_and_reloads_snapshot(self) -> None:
        _app_close_node, _app_contracts, _app_ports, _cli_bootstrap, _domain_models, infra_github_cli, _infra_contracts = _runtime_modules()
        repo_root = Path("/repo")

        class _Completed:
            def __init__(self, stdout="", stderr=""):
                self.stdout = stdout
                self.stderr = stderr

        calls = []

        def _fake_run(cmd, cwd, capture_output, text, check):
            del capture_output, text, check
            calls.append((list(cmd), cwd))
            return _Completed()

        with patch.object(infra_github_cli, "ensure_gh_available"), patch.object(
            infra_github_cli, "issue_view_snapshot_raw", return_value={"number": 301, "state": "CLOSED", "title": "Issue 301", "labels": [], "updatedAt": "t", "url": "https://github.com/example/repo/issues/301"}
        ) as issue_view_snapshot_raw, patch.object(infra_github_cli.subprocess, "run", side_effect=_fake_run):
            raw = infra_github_cli.issue_close_raw(repo_root, issue_number=301, repo_slug="example/repo")

        self.assertEqual(raw["state"], "CLOSED")
        self.assertEqual(calls, [(["gh", "issue", "close", "301", "--repo", "example/repo"], str(repo_root))])
        issue_view_snapshot_raw.assert_called_once_with(repo_root, issue_number=301, repo_slug="example/repo")

    def test_issue_close_raw_raises_with_close_command_context(self) -> None:
        _app_close_node, _app_contracts, _app_ports, _cli_bootstrap, _domain_models, infra_github_cli, _infra_contracts = _runtime_modules()
        repo_root = Path("/repo")

        with patch.object(infra_github_cli, "ensure_gh_available"), patch.object(
            infra_github_cli.subprocess,
            "run",
            side_effect=infra_github_cli.subprocess.CalledProcessError(
                returncode=1,
                cmd=["gh", "issue", "close", "301"],
                stderr="boom",
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "gh failed: gh issue close 301"):
                infra_github_cli.issue_close_raw(repo_root, issue_number=301)

    def test_close_node_raises_when_close_and_fallback_view_both_fail(self) -> None:
        app_close_node, app_contracts, _app_ports, _cli_bootstrap, domain_models, _infra_github_cli, infra_contracts = _runtime_modules()
        repo_root = Path("/repo")
        records = [
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="initiative",
                node_id="init-local-00001",
                slug="auth-platform",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=101,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00001",
                slug="jwt-auth",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=201,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00001",
                slug="target",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=301,
                github_repo_owner="example",
                github_repo_name="repo",
            ),
        ]
        issue_gateway = _StubIssueGateway(
            view_snapshots=[_snapshot(domain_models, issue_number=301, state="OPEN")],
            close_error="close failed",
        )
        ports = self._ports(repo_root=repo_root, records=records, issue_gateway=issue_gateway)

        with self.assertRaisesRegex(RuntimeError, "close failed"):
            app_close_node.close_node(
                app_contracts.CloseNodeRequest(
                    target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None)
                ),
                ports,
            )


if __name__ == "__main__":
    unittest.main()
