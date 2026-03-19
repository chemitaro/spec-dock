import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

_REQUIRED_NODE_DOCS = ("requirement.md", "design.md", "plan.md", "report.md")


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


def _sample_records(infra_contracts, *, repo_root: Path = Path("/repo")):
    specdock_dir = repo_root / "spec-dock"
    return [
        infra_contracts.StoredMetaRecord(
            kind="initiative",
            id="init-local-00001",
            title="Auth Platform",
            slug="auth-platform",
            path=(specdock_dir / "initiatives" / "init-local-00001-auth-platform").as_posix(),
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=101,
            meta_path=(
                specdock_dir / "initiatives" / "init-local-00001-auth-platform" / ".meta.json"
            ).as_posix(),
        ),
        infra_contracts.StoredMetaRecord(
            kind="epic",
            id="epic-local-00001",
            title="JWT Auth",
            slug="jwt-auth",
            path=(
                specdock_dir
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
            ).as_posix(),
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=201,
            meta_path=(
                specdock_dir
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / ".meta.json"
            ).as_posix(),
        ),
        infra_contracts.StoredMetaRecord(
            kind="issue",
            id="iss-local-00001",
            title="Dependency",
            slug="dependency",
            path=(
                specdock_dir
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-dependency"
            ).as_posix(),
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
            meta_path=(
                specdock_dir
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-dependency"
                / ".meta.json"
            ).as_posix(),
        ),
        infra_contracts.StoredMetaRecord(
            kind="issue",
            id="iss-local-00002",
            title="Target",
            slug="target",
            path=(
                specdock_dir
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00002-target"
            ).as_posix(),
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=302,
            meta_path=(
                specdock_dir
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00002-target"
                / ".meta.json"
            ).as_posix(),
        ),
    ]


def _materialize_required_artifacts(records) -> None:
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        meta_path = Path(record.meta_path)
        meta_path.write_text(
            json.dumps({"id": record.id, "kind": record.kind}, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        for doc_name in _REQUIRED_NODE_DOCS:
            (node_dir / doc_name).write_text(f"# {doc_name}\n", encoding="utf-8")


def _issue_status_snapshot(
    domain_models,
    *,
    issue_id: str,
    effective_status: str,
    source: str,
    github_number: int | None,
    authority: str | None = None,
    stale: bool | None = None,
    last_sync_at: str | None = None,
):
    resolved_authority = authority
    if resolved_authority is None:
        resolved_authority = "local" if github_number is None else "github"
    resolved_stale = stale
    if resolved_stale is None:
        resolved_stale = source == "cache"
    return domain_models.IssueStatusSnapshot(
        issue_id=issue_id,
        authority=resolved_authority,
        effective_status=effective_status,
        source=source,
        stale=resolved_stale,
        last_sync_at=last_sync_at,
        github_number=github_number,
    )


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
    def __init__(self, snapshots=None, fail=False, foreign_snapshots=None):
        self.snapshots = list(snapshots or [])
        self.fail = fail
        self.foreign_snapshots = dict(foreign_snapshots or {})
        self.view_calls: list[tuple[str, int, str | None]] = []

    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        if self.fail:
            raise RuntimeError("gh failed")
        return list(self.snapshots)

    def issue_view_snapshot(self, repo_root, issue_number, *, repo_slug=None):
        if self.fail:
            raise RuntimeError("gh failed")
        key = (str(repo_slug or ""), int(issue_number))
        self.view_calls.append((str(repo_root), int(issue_number), repo_slug))
        snapshot = self.foreign_snapshots.get(key)
        if snapshot is None:
            raise RuntimeError(f"gh failed: {repo_slug}#{issue_number}")
        return snapshot


class _StubActiveStateStore:
    def __init__(self, issue_id):
        self.issue_id = issue_id

    def load_active_issue_id(self, specdock_dir):
        del specdock_dir
        return self.issue_id


class _StubGitGateway:
    def __init__(self, repo_slug: str | None):
        self.repo_slug = repo_slug

    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return self.repo_slug


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
        self.assertEqual(context_gh.issue_statuses["iss-local-00001"].authority, "github")
        self.assertEqual(context_gh.issue_statuses["iss-local-00001"].effective_status, "done")
        self.assertEqual(context_gh.issue_statuses["iss-local-00001"].source, "github")
        self.assertFalse(context_gh.issue_statuses["iss-local-00001"].stale)
        self.assertEqual(context_gh.issue_statuses["iss-local-00001"].last_sync_at, "t")

        context_cache = app_status_context.resolve_issue_status_context(
            graph,
            github_enabled=False,
            issue_snapshots=snapshots,
            cached_issue_status_by_id={"iss-local-00001": "open"},
        )
        self.assertEqual(context_cache.issue_statuses["iss-local-00001"].effective_status, "open")
        self.assertEqual(context_cache.issue_statuses["iss-local-00001"].source, "cache")
        self.assertTrue(context_cache.issue_statuses["iss-local-00001"].stale)

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

    def test_check_deps_prefers_foreign_repo_snapshot_for_foreign_linked_issue(self) -> None:
        (
            _runtime_app,
            app_check_deps,
            app_contracts,
            app_ports,
            _app_status_context,
            _app_validate_tree,
            domain_models,
            infra_contracts,
            _presentation_cli_text,
            _presentation_json_state,
        ) = _runtime_modules()
        records = [
            infra_contracts.StoredMetaRecord(
                kind="initiative",
                id="init-local-00001",
                title="Auth Platform",
                slug="auth-platform",
                path="spec-dock/initiatives/init-local-00001-auth-platform",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=101,
                meta_path="spec-dock/initiatives/init-local-00001-auth-platform/.meta.json",
            ),
            infra_contracts.StoredMetaRecord(
                kind="epic",
                id="epic-local-00001",
                title="JWT Auth",
                slug="jwt-auth",
                path="spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=201,
                meta_path="spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/.meta.json",
            ),
            infra_contracts.StoredMetaRecord(
                kind="issue",
                id="iss-local-00001",
                title="Foreign issue",
                slug="foreign-issue",
                path=(
                    "spec-dock/initiatives/init-local-00001-auth-platform/"
                    "epics/epic-local-00001-jwt-auth/issues/iss-local-00001-foreign-issue"
                ),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=123,
                meta_path=(
                    "spec-dock/initiatives/init-local-00001-auth-platform/"
                    "epics/epic-local-00001-jwt-auth/issues/iss-local-00001-foreign-issue/.meta.json"
                ),
                github_repo_owner="other",
                github_repo_name="repo",
            ),
        ]
        issue_gateway = _StubIssueGateway(
            snapshots=[
                domain_models.IssueSnapshot(
                    issue_number=123,
                    state="OPEN",
                    title="Current repo #123",
                    labels=[],
                    updated_at="2026-03-18T00:00:00Z",
                    url="https://github.com/current/repo/issues/123",
                    repo_owner="current",
                    repo_name="repo",
                )
            ],
            foreign_snapshots={
                ("other/repo", 123): domain_models.IssueSnapshot(
                    issue_number=123,
                    state="CLOSED",
                    title="Foreign #123",
                    labels=[],
                    updated_at="2026-03-18T01:23:45Z",
                    url="https://github.com/other/repo/issues/123",
                    repo_owner="other",
                    repo_name="repo",
                )
            },
        )
        ports = app_ports.Ports(
            node_reader=_StubNodeReader(records),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
            derived_state_reader=_StubDerivedStateReader({"iss-local-00001": "open"}),
            issue_gateway=issue_gateway,
            active_state_store=_StubActiveStateStore(None),
            deps_topology_reader=_StubDepsTopologyReader({"iss-local-00001": []}),
        )

        result = app_check_deps.check_deps(
            app_contracts.CheckDepsRequest(
                target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
                use_github=True,
                issue_limit=10000,
            ),
            ports,
        )

        status = result.inspection.issue_statuses["iss-local-00001"]
        self.assertEqual(status.source, "github")
        self.assertEqual(status.effective_status, "done")
        self.assertFalse(status.stale)
        self.assertEqual(issue_gateway.view_calls, [("/repo", 123, "other/repo")])
        self.assertNotIn("gh_index_incomplete", result.warnings)

    def test_check_deps_skips_same_repo_repo_scoped_view_fetch_when_index_contains_key(self) -> None:
        (
            _runtime_app,
            app_check_deps,
            app_contracts,
            app_ports,
            _app_status_context,
            _app_validate_tree,
            domain_models,
            infra_contracts,
            _presentation_cli_text,
            _presentation_json_state,
        ) = _runtime_modules()
        records = [
            infra_contracts.StoredMetaRecord(
                kind="initiative",
                id="init-local-00001",
                title="Auth Platform",
                slug="auth-platform",
                path="spec-dock/initiatives/init-local-00001-auth-platform",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=None,
                meta_path="spec-dock/initiatives/init-local-00001-auth-platform/.meta.json",
            ),
            infra_contracts.StoredMetaRecord(
                kind="epic",
                id="epic-local-00001",
                title="JWT Auth",
                slug="jwt-auth",
                path="spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
                meta_path="spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/.meta.json",
            ),
            infra_contracts.StoredMetaRecord(
                kind="issue",
                id="iss-local-00001",
                title="Current scoped #123",
                slug="current-scoped-123",
                path=(
                    "spec-dock/initiatives/init-local-00001-auth-platform/"
                    "epics/epic-local-00001-jwt-auth/issues/iss-local-00001-current-scoped-123"
                ),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=123,
                meta_path=(
                    "spec-dock/initiatives/init-local-00001-auth-platform/"
                    "epics/epic-local-00001-jwt-auth/issues/iss-local-00001-current-scoped-123/.meta.json"
                ),
                github_repo_owner="current",
                github_repo_name="repo",
            ),
        ]
        issue_gateway = _StubIssueGateway(
            snapshots=[
                domain_models.IssueSnapshot(
                    issue_number=123,
                    state="OPEN",
                    title="Current repo #123",
                    labels=[],
                    updated_at="2026-03-19T00:00:00Z",
                    url="https://github.com/current/repo/issues/123",
                    repo_owner="current",
                    repo_name="repo",
                )
            ],
            foreign_snapshots={},
        )
        ports = app_ports.Ports(
            node_reader=_StubNodeReader(records),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
            derived_state_reader=_StubDerivedStateReader({"iss-local-00001": "open"}),
            issue_gateway=issue_gateway,
            active_state_store=_StubActiveStateStore(None),
            deps_topology_reader=_StubDepsTopologyReader({"iss-local-00001": []}),
            git_gateway=_StubGitGateway("current/repo"),
        )

        result = app_check_deps.check_deps(
            app_contracts.CheckDepsRequest(
                target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
                use_github=True,
                issue_limit=10000,
            ),
            ports,
        )

        status = result.inspection.issue_statuses["iss-local-00001"]
        self.assertEqual(status.source, "github")
        self.assertEqual(status.effective_status, "open")
        self.assertEqual(issue_gateway.view_calls, [])
        self.assertNotIn("gh_fetch_failed", result.warnings)

    def test_check_deps_falls_back_to_same_repo_repo_scoped_view_when_index_missing_key(self) -> None:
        (
            _runtime_app,
            app_check_deps,
            app_contracts,
            app_ports,
            _app_status_context,
            _app_validate_tree,
            domain_models,
            infra_contracts,
            _presentation_cli_text,
            _presentation_json_state,
        ) = _runtime_modules()
        records = [
            infra_contracts.StoredMetaRecord(
                kind="initiative",
                id="init-local-00001",
                title="Auth Platform",
                slug="auth-platform",
                path="spec-dock/initiatives/init-local-00001-auth-platform",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=None,
                meta_path="spec-dock/initiatives/init-local-00001-auth-platform/.meta.json",
            ),
            infra_contracts.StoredMetaRecord(
                kind="epic",
                id="epic-local-00001",
                title="JWT Auth",
                slug="jwt-auth",
                path="spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
                meta_path="spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/.meta.json",
            ),
            infra_contracts.StoredMetaRecord(
                kind="issue",
                id="iss-local-00001",
                title="Current scoped #123",
                slug="current-scoped-123",
                path=(
                    "spec-dock/initiatives/init-local-00001-auth-platform/"
                    "epics/epic-local-00001-jwt-auth/issues/iss-local-00001-current-scoped-123"
                ),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=123,
                meta_path=(
                    "spec-dock/initiatives/init-local-00001-auth-platform/"
                    "epics/epic-local-00001-jwt-auth/issues/iss-local-00001-current-scoped-123/.meta.json"
                ),
                github_repo_owner="current",
                github_repo_name="repo",
            ),
        ]
        issue_gateway = _StubIssueGateway(
            snapshots=[],
            foreign_snapshots={
                ("current/repo", 123): domain_models.IssueSnapshot(
                    issue_number=123,
                    state="CLOSED",
                    title="Current repo #123",
                    labels=[],
                    updated_at="2026-03-19T00:01:00Z",
                    url="https://github.com/current/repo/issues/123",
                    repo_owner="current",
                    repo_name="repo",
                )
            },
        )
        ports = app_ports.Ports(
            node_reader=_StubNodeReader(records),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
            derived_state_reader=_StubDerivedStateReader({"iss-local-00001": "open"}),
            issue_gateway=issue_gateway,
            active_state_store=_StubActiveStateStore(None),
            deps_topology_reader=_StubDepsTopologyReader({"iss-local-00001": []}),
            git_gateway=_StubGitGateway("current/repo"),
        )

        result = app_check_deps.check_deps(
            app_contracts.CheckDepsRequest(
                target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
                use_github=True,
                issue_limit=10000,
            ),
            ports,
        )

        status = result.inspection.issue_statuses["iss-local-00001"]
        self.assertEqual(status.source, "github")
        self.assertEqual(status.effective_status, "done")
        self.assertEqual(issue_gateway.view_calls, [("/repo", 123, "current/repo")])
        self.assertNotIn("gh_fetch_failed", result.warnings)
        self.assertNotIn("gh_index_incomplete", result.warnings)

    def test_check_deps_github_uses_current_repo_slug_for_unscoped_current_issue_and_keeps_foreign_same_number(self) -> None:
        (
            _runtime_app,
            app_check_deps,
            app_contracts,
            app_ports,
            _app_status_context,
            _app_validate_tree,
            domain_models,
            infra_contracts,
            _presentation_cli_text,
            presentation_json_state,
        ) = _runtime_modules()
        records = [
            infra_contracts.StoredMetaRecord(
                kind="initiative",
                id="init-local-00001",
                title="Auth Platform",
                slug="auth-platform",
                path="spec-dock/initiatives/init-local-00001-auth-platform",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=None,
                meta_path="spec-dock/initiatives/init-local-00001-auth-platform/.meta.json",
            ),
            infra_contracts.StoredMetaRecord(
                kind="epic",
                id="epic-local-00001",
                title="JWT Auth",
                slug="jwt-auth",
                path="spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
                meta_path="spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/.meta.json",
            ),
            infra_contracts.StoredMetaRecord(
                kind="issue",
                id="iss-local-00001",
                title="Current unscoped #123",
                slug="current-unscoped-123",
                path=(
                    "spec-dock/initiatives/init-local-00001-auth-platform/"
                    "epics/epic-local-00001-jwt-auth/issues/iss-local-00001-current-unscoped-123"
                ),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=123,
                meta_path=(
                    "spec-dock/initiatives/init-local-00001-auth-platform/"
                    "epics/epic-local-00001-jwt-auth/issues/iss-local-00001-current-unscoped-123/.meta.json"
                ),
            ),
            infra_contracts.StoredMetaRecord(
                kind="issue",
                id="iss-local-00002",
                title="Foreign #123",
                slug="foreign-123",
                path=(
                    "spec-dock/initiatives/init-local-00001-auth-platform/"
                    "epics/epic-local-00001-jwt-auth/issues/iss-local-00002-foreign-123"
                ),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=123,
                meta_path=(
                    "spec-dock/initiatives/init-local-00001-auth-platform/"
                    "epics/epic-local-00001-jwt-auth/issues/iss-local-00002-foreign-123/.meta.json"
                ),
                github_repo_owner="other",
                github_repo_name="repo",
            ),
            infra_contracts.StoredMetaRecord(
                kind="issue",
                id="iss-local-00003",
                title="Target",
                slug="target",
                path=(
                    "spec-dock/initiatives/init-local-00001-auth-platform/"
                    "epics/epic-local-00001-jwt-auth/issues/iss-local-00003-target"
                ),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=None,
                meta_path=(
                    "spec-dock/initiatives/init-local-00001-auth-platform/"
                    "epics/epic-local-00001-jwt-auth/issues/iss-local-00003-target/.meta.json"
                ),
            ),
        ]
        issue_gateway = _StubIssueGateway(
            snapshots=[
                domain_models.IssueSnapshot(
                    issue_number=123,
                    state="OPEN",
                    title="Current #123",
                    labels=[],
                    updated_at="2026-03-19T00:00:00Z",
                    url="https://github.com/current/repo/issues/123",
                    repo_owner="current",
                    repo_name="repo",
                )
            ],
            foreign_snapshots={
                ("other/repo", 123): domain_models.IssueSnapshot(
                    issue_number=123,
                    state="CLOSED",
                    title="Foreign #123",
                    labels=[],
                    updated_at="2026-03-19T00:01:00Z",
                    url="https://github.com/other/repo/issues/123",
                    repo_owner="other",
                    repo_name="repo",
                )
            },
        )
        ports = app_ports.Ports(
            node_reader=_StubNodeReader(records),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
            derived_state_reader=_StubDerivedStateReader({}),
            issue_gateway=issue_gateway,
            active_state_store=_StubActiveStateStore(None),
            deps_topology_reader=_StubDepsTopologyReader(
                {
                    "iss-local-00001": [],
                    "iss-local-00002": [],
                    "iss-local-00003": ["iss-local-00001", "iss-local-00002"],
                }
            ),
            git_gateway=_StubGitGateway("current/repo"),
        )
        result = app_check_deps.check_deps(
            app_contracts.CheckDepsRequest(
                target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00003", github_issue_number=None),
                use_github=True,
                issue_limit=10000,
            ),
            ports,
        )
        self.assertFalse(result.inspection.evaluation.ready)
        self.assertEqual(result.inspection.evaluation.guard_reason, "blocked")
        self.assertEqual(result.inspection.evaluation.blockers, ["iss-local-00001"])
        self.assertEqual(issue_gateway.view_calls, [("/repo", 123, "other/repo")])
        self.assertEqual(result.warnings, [])

        payload = json.loads(presentation_json_state.render_deps_check_json(result))
        self.assertFalse(payload["ready"])
        self.assertEqual(payload["blockers"], ["iss-local-00001"])
        self.assertEqual(payload["nodes"]["iss-local-00001"]["state"], "ready")
        self.assertEqual(payload["nodes"]["iss-local-00001"]["source"], "github")
        self.assertEqual(payload["nodes"]["iss-local-00001"]["effective_status"], "open")
        self.assertEqual(payload["nodes"]["iss-local-00002"]["state"], "done")
        self.assertEqual(payload["nodes"]["iss-local-00002"]["source"], "github")
        self.assertEqual(payload["nodes"]["iss-local-00002"]["effective_status"], "done")

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
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            records = _sample_records(infra_contracts, repo_root=repo_root)
            _materialize_required_artifacts(records)
            deps_reader = _StubDepsTopologyReader(
                {"iss-local-00001": ["iss-local-00002"], "iss-local-00002": ["iss-local-00001"]}
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=repo_root / "spec-dock",
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
            issue_statuses={
                "iss-local-00001": _issue_status_snapshot(
                    domain_models,
                    issue_id="iss-local-00001",
                    effective_status="open",
                    source="cache",
                    github_number=301,
                    last_sync_at="2026-03-17T12:34:56Z",
                ),
                "iss-local-00002": _issue_status_snapshot(
                    domain_models,
                    issue_id="iss-local-00002",
                    effective_status="open",
                    source="cache",
                    github_number=302,
                    last_sync_at="2026-03-17T12:34:56Z",
                ),
            },
        )
        result = app_contracts.DepsCheckResult(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00002", github_issue_number=None),
            inspection=inspection,
            warnings=["gh_fetch_failed"],
        )

        text = presentation_cli_text.render_deps_check_text(result)
        self.assertIn("spec-dock: blocked (deps check)", text.stderr_lines[0])
        self.assertIn("authority=github", text.stderr_lines[0])
        self.assertIn("effective_status=open", text.stderr_lines[0])
        self.assertIn("source=cache", text.stderr_lines[0])
        self.assertIn("stale=true", text.stderr_lines[0])
        self.assertIn("last_sync_at=2026-03-17T12:34:56Z", text.stderr_lines[0])
        self.assertEqual(text.warnings, ["gh_fetch_failed"])

        payload = json.loads(presentation_json_state.render_deps_check_json(result))
        self.assertEqual(payload["target"], "iss-local-00002")
        self.assertEqual(payload["blockers"], ["iss-local-00001"])
        self.assertEqual(payload["target_status"]["source"], "cache")
        self.assertTrue(payload["target_status"]["stale"])
        self.assertEqual(payload["target_status"]["last_sync_at"], "2026-03-17T12:34:56Z")
        self.assertEqual(payload["nodes"]["iss-local-00001"]["source"], "cache")
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
            issue_statuses={
                "iss-local-00002": _issue_status_snapshot(
                    domain_models,
                    issue_id="iss-local-00002",
                    effective_status="open",
                    source="cache",
                    github_number=302,
                    last_sync_at="2026-03-17T12:34:56Z",
                )
            },
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
            self.assertIn("authority=github", stderr_lines[1])
            self.assertIn("effective_status=open", stderr_lines[1])
            self.assertIn("source=cache", stderr_lines[1])
            self.assertIn("stale=true", stderr_lines[1])
            self.assertIn("last_sync_at=2026-03-17T12:34:56Z", stderr_lines[1])
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
                issue_statuses={
                    "iss-00123": _issue_status_snapshot(
                        domain_models,
                        issue_id="iss-00123",
                        authority="github",
                        effective_status="open",
                        source="github",
                        stale=False,
                        last_sync_at="2026-03-17T12:34:56Z",
                        github_number=123,
                    )
                },
            ),
            warnings=[],
        )

        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_application_check_deps = cli_bootstrap.application_check_deps
        original_render_deps_check_text = runtime_app._render_deps_check_text
        original_render_deps_check_json = runtime_app._render_deps_check_json
        try:
            runtime_app._find_specdock_dir = lambda: Path("/repo/spec-dock")
            cli_bootstrap.application_check_deps = lambda req, ports: ready_result
            runtime_app._render_deps_check_text = presentation_cli_text.render_deps_check_text
            runtime_app._render_deps_check_json = presentation_json_state.render_deps_check_json

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = runtime_app.main(["deps", "check", "#123"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(stderr.getvalue().strip(), "")
            ready_line = stdout.getvalue().strip()
            self.assertIn("spec-dock: ok (deps check)", ready_line)
            self.assertIn("authority=github", ready_line)
            self.assertIn("effective_status=open", ready_line)
            self.assertIn("source=github", ready_line)
            self.assertIn("stale=false", ready_line)
            self.assertIn("last_sync_at=2026-03-17T12:34:56Z", ready_line)

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
            runtime_app._render_deps_check_text = original_render_deps_check_text
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
