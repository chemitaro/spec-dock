import contextlib
from pathlib import Path
import sys
import tempfile

import pytest

_MISSING = object()


class _CallProbe:
    def __init__(self, *, side_effect=_MISSING, return_value=_MISSING):
        self.calls = []
        self._side_effect = side_effect
        self._return_value = return_value

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        if self._side_effect is not _MISSING:
            if isinstance(self._side_effect, BaseException):
                raise self._side_effect
            return self._side_effect(*args, **kwargs)
        if self._return_value is not _MISSING:
            return self._return_value
        return None

    def assert_called_once_with(self, *args, **kwargs):
        assert self.calls == [(args, kwargs)]


@contextlib.contextmanager
def _patch_object(target, name, replacement=_MISSING, *, side_effect=_MISSING, return_value=_MISSING):
    original = getattr(target, name)
    if replacement is _MISSING:
        replacement = _CallProbe(side_effect=side_effect, return_value=return_value)
    setattr(target, name, replacement)
    try:
        yield replacement
    finally:
        setattr(target, name, original)


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
        from spec_dock_runtime.application import (
            close_node as app_close_node,
            contracts as app_contracts,
            ports as app_ports,
        )
        from spec_dock_runtime.cli import bootstrap as cli_bootstrap
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.infra import contracts as infra_contracts, github_cli as infra_github_cli
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


class _StubActiveStateStore:
    def __init__(
        self,
        infra_contracts,
        *,
        issue_id: str | None = "iss-local-00001",
        issue_authority: str | None = "approved",
        issue_grants=None,
        promotion_record=None,
    ) -> None:
        self._infra_contracts = infra_contracts
        self.issue_id = issue_id
        self.issue_authority = issue_authority
        self.issue_grants = tuple(issue_grants) if issue_grants is not None else ("issue_finish",)
        self.promotion_record = promotion_record

    def load_active_manifest(self, specdock_dir: Path):
        del specdock_dir
        issue_entry = None
        if self.issue_id is not None:
            promotion_record = self.promotion_record
            if promotion_record is None:
                promotion_record = {
                    "status": "approved",
                    "authority": "approved",
                    "source_revision": f"active:{self.issue_id}",
                    "approved_revision": f"active:{self.issue_id}",
                    "approved_hash": f"active:{self.issue_id}",
                    "reviewer_target_hash": f"active:{self.issue_id}",
                    "promotion_decision": "runtime_active_selection",
                }
            issue_entry = self._infra_contracts.ActiveManifestEntry(
                id=self.issue_id,
                path=f"spec-dock/issues/{self.issue_id}",
                authority=self.issue_authority,
                grants=self.issue_grants,
                promotion_record=promotion_record,
            )
        return self._infra_contracts.ActiveManifestLoadResult(
            manifest=self._infra_contracts.ActiveManifest(initiative=None, epic=None, issue=issue_entry),
            source="agent.active",
            warnings=[],
        )


class TestRuntimeCloseS12:
    def _ports(
        self,
        *,
        repo_root: Path,
        records,
        issue_gateway,
        active_issue_id: str | None = "iss-local-00001",
        active_issue_authority: str | None = "approved",
        active_issue_grants=None,
        active_promotion_record=None,
    ):
        _app_close_node, _app_contracts, app_ports, _cli_bootstrap, _domain_models, _infra_github_cli, infra_contracts = _runtime_modules()
        return app_ports.Ports(
            node_reader=_StubNodeReader(records),
            repo_root=repo_root,
            specdock_dir=repo_root / "spec-dock",
            issue_gateway=issue_gateway,
            active_state_store=_StubActiveStateStore(
                infra_contracts,
                issue_id=active_issue_id,
                issue_authority=active_issue_authority,
                issue_grants=active_issue_grants,
                promotion_record=active_promotion_record,
            ),
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

        with pytest.raises(RuntimeError, match="not linked to a GitHub issue"):
            app_close_node.close_node(
                app_contracts.CloseNodeRequest(
                    target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None)
                ),
                ports,
            )

        assert issue_gateway.view_calls == []
        assert issue_gateway.close_calls == []

    def test_close_node_allows_explicit_issue_target_when_authority_is_proposed(self) -> None:
        app_close_node, app_contracts, _app_ports, _cli_bootstrap, domain_models, _infra_github_cli, infra_contracts = _runtime_modules()
        repo_root = Path("/repo")
        records = [
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
            )
        ]
        issue_gateway = _StubIssueGateway(
            view_snapshots=[_snapshot(domain_models, issue_number=301, state="OPEN")],
            close_snapshot=_snapshot(domain_models, issue_number=301, state="CLOSED"),
        )
        ports = self._ports(
            repo_root=repo_root,
            records=records,
            issue_gateway=issue_gateway,
            active_issue_authority="proposed",
        )

        result = app_close_node.close_node(
            app_contracts.CloseNodeRequest(
                target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None)
            ),
            ports,
        )

        assert result.node_id == "iss-local-00001"
        assert not result.already_closed
        assert issue_gateway.view_calls == [(str(repo_root), 301, "example/repo")]
        assert issue_gateway.close_calls == [(str(repo_root), 301, "example/repo")]

    def test_close_node_allows_explicit_issue_target_when_promotion_record_is_stale(self) -> None:
        app_close_node, app_contracts, _app_ports, _cli_bootstrap, domain_models, _infra_github_cli, infra_contracts = _runtime_modules()
        repo_root = Path("/repo")
        stale_record = {
            "status": "approved",
            "authority": "approved",
            "source_revision": "active:iss-local-00999",
            "approved_revision": "active:iss-local-00999",
            "approved_hash": "active:iss-local-00999",
            "reviewer_target_hash": "active:iss-local-00999",
            "promotion_decision": "runtime_active_selection",
        }
        records = [
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
            )
        ]
        issue_gateway = _StubIssueGateway(
            view_snapshots=[_snapshot(domain_models, issue_number=301, state="OPEN")],
            close_snapshot=_snapshot(domain_models, issue_number=301, state="CLOSED"),
        )
        ports = self._ports(
            repo_root=repo_root,
            records=records,
            issue_gateway=issue_gateway,
            active_promotion_record=stale_record,
        )

        result = app_close_node.close_node(
            app_contracts.CloseNodeRequest(
                target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None)
            ),
            ports,
        )

        assert result.node_id == "iss-local-00001"
        assert not result.already_closed
        assert issue_gateway.view_calls == [(str(repo_root), 301, "example/repo")]
        assert issue_gateway.close_calls == [(str(repo_root), 301, "example/repo")]

    def test_close_node_allows_explicit_issue_target_when_target_is_not_active(self) -> None:
        app_close_node, app_contracts, _app_ports, _cli_bootstrap, domain_models, _infra_github_cli, infra_contracts = _runtime_modules()
        repo_root = Path("/repo")
        records = [
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
            )
        ]
        issue_gateway = _StubIssueGateway(
            view_snapshots=[_snapshot(domain_models, issue_number=301, state="OPEN")],
            close_snapshot=_snapshot(domain_models, issue_number=301, state="CLOSED"),
        )
        ports = self._ports(
            repo_root=repo_root,
            records=records,
            issue_gateway=issue_gateway,
            active_issue_id="iss-local-00002",
        )

        result = app_close_node.close_node(
            app_contracts.CloseNodeRequest(
                target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None)
            ),
            ports,
        )

        assert result.node_id == "iss-local-00001"
        assert not result.already_closed
        assert issue_gateway.view_calls == [(str(repo_root), 301, "example/repo")]
        assert issue_gateway.close_calls == [(str(repo_root), 301, "example/repo")]

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

            with pytest.raises(RuntimeError, match="gh issue close failed"):
                app_close_node.close_node(
                    app_contracts.CloseNodeRequest(
                        target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None)
                    ),
                    ports,
                )

            assert issue_dir.is_dir()
            assert (issue_dir / "requirement.md").is_file()
            assert issue_gateway.close_calls == [(str(repo_root), 301, "example/repo")]

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

        assert result.already_closed
        assert result.node_id == "iss-local-00001"
        assert result.node_kind == "issue"
        assert result.github_issue_number == 301
        assert result.issue_snapshot.state == "CLOSED"
        assert issue_gateway.close_calls == []

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

        assert result.already_closed
        assert result.issue_snapshot.state == "CLOSED"
        assert len(issue_gateway.view_calls) == 2
        assert issue_gateway.close_calls == [(str(repo_root), 301, "example/repo")]

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

        assert not result.already_closed
        assert result.node_kind == "epic"
        assert result.github_issue_number == 201
        assert issue_gateway.close_calls == [(str(repo_root), 201, "example/repo")]

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

        assert not result.already_closed
        assert result.node_kind == "initiative"
        assert result.github_issue_number == 101
        assert issue_gateway.close_calls == [(str(repo_root), 101, "example/repo")]

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

            with pytest.raises(RuntimeError, match="not linked to a GitHub issue"):
                app_close_node.close_node(
                    app_contracts.CloseNodeRequest(
                        target=app_contracts.TargetRef(kind="node_id", node_id="init-local-00001", github_issue_number=None)
                    ),
                    ports,
                )

            assert init_dir.is_dir()
            assert issue_gateway.view_calls == []
            assert issue_gateway.close_calls == []

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
            active_state_store=_StubActiveStateStore(infra_contracts, issue_id="iss-local-00001"),
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

        assert result.node_id == "iss-local-00001"
        assert issue_gateway.view_calls == [(str(repo_root), 301, "example/repo")]

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

        with pytest.raises(RuntimeError, match=r"Ambiguous github\.issue_number=301"):
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

        with pytest.raises(RuntimeError, match=r"No node found for github\.issue_number=301 in repo scope"):
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
        assert callable(runtime.use_cases.close_node)
        with pytest.raises(RuntimeError, match="No nodes found"):
            runtime.use_cases.close_node(
                app_contracts.CloseNodeRequest(
                    target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None)
                )
            )

    def test_bootstrap_issue_gateway_forwards_issue_close(self) -> None:
        _app_close_node, _app_contracts, _app_ports, cli_bootstrap, _domain_models, _infra_github_cli, _infra_contracts = _runtime_modules()
        gateway = cli_bootstrap._IssueGateway()
        with _patch_object(cli_bootstrap.infra_github_cli, "issue_close", return_value="closed") as issue_close:
            result = gateway.issue_close(Path("/repo"), 301, repo_slug="example/repo")

        assert result == "closed"
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

        with _patch_object(infra_github_cli, "ensure_gh_available"), _patch_object(
            infra_github_cli, "issue_view_snapshot_raw", return_value={"number": 301, "state": "CLOSED", "title": "Issue 301", "labels": [], "updatedAt": "t", "url": "https://github.com/example/repo/issues/301"}
        ) as issue_view_snapshot_raw, _patch_object(infra_github_cli.subprocess, "run", side_effect=_fake_run):
            raw = infra_github_cli.issue_close_raw(repo_root, issue_number=301, repo_slug="example/repo")

        assert raw["state"] == "CLOSED"
        assert calls == [(["gh", "issue", "close", "301", "--repo", "example/repo"], str(repo_root))]
        issue_view_snapshot_raw.assert_called_once_with(repo_root, issue_number=301, repo_slug="example/repo")

    def test_issue_close_raw_raises_with_close_command_context(self) -> None:
        _app_close_node, _app_contracts, _app_ports, _cli_bootstrap, _domain_models, infra_github_cli, _infra_contracts = _runtime_modules()
        repo_root = Path("/repo")

        with _patch_object(infra_github_cli, "ensure_gh_available"), _patch_object(
            infra_github_cli.subprocess,
            "run",
            side_effect=infra_github_cli.subprocess.CalledProcessError(
                returncode=1,
                cmd=["gh", "issue", "close", "301"],
                stderr="boom",
            ),
        ), pytest.raises(RuntimeError, match="gh failed: gh issue close 301"):
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

        with pytest.raises(RuntimeError, match="close failed"):
            app_close_node.close_node(
                app_contracts.CloseNodeRequest(
                    target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None)
                ),
                ports,
            )
