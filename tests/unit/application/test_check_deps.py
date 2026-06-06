import sys
import unittest
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
        from spec_dock_runtime.application import check_deps as app_check_deps
        from spec_dock_runtime.application import contracts as app_contracts
        from spec_dock_runtime.application import ports as app_ports
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.infra import contracts as infra_contracts
    finally:
        sys.path.pop(0)
    return app_check_deps, app_contracts, app_ports, domain_models, infra_contracts


class _StubNodeReader:
    def __init__(self, records):
        self.records = list(records)

    def load_node_records(self):
        return list(self.records)


class _StubDepsTopologyReader:
    def __init__(self, issue_depends_on_map, warnings=None):
        self.issue_depends_on_map = {
            issue_id: list(depends_on)
            for issue_id, depends_on in issue_depends_on_map.items()
        }
        self.warnings = list(warnings or [])

    def load_issue_depends_on_map(self, specdock_dir, graph):
        _app_check_deps, _app_contracts, _app_ports, _domain_models, infra_contracts = _runtime_modules()
        return infra_contracts.DepsTopologyLoadResult(
            issue_depends_on_map=dict(self.issue_depends_on_map),
            warnings=list(self.warnings),
        )


class _StubDerivedStateReader:
    def __init__(self, statuses=None, last_sync_at=None):
        self.statuses = dict(statuses or {})
        self.last_sync_at = dict(last_sync_at or {})

    def load_cached_issue_status_by_id(self, specdock_dir):
        return dict(self.statuses)

    def load_cached_issue_last_sync_at_by_id(self, specdock_dir):
        return dict(self.last_sync_at)


class _StubIssueGateway:
    def __init__(self, snapshots=None, *, fail_index=False):
        self.snapshots = list(snapshots or [])
        self.fail_index = fail_index
        self.issue_index_calls = []
        self.issue_view_calls = []

    def issue_index(self, repo_root, *, limit):
        self.issue_index_calls.append((repo_root, limit))
        if self.fail_index:
            raise RuntimeError("gh failed")
        return list(self.snapshots)

    def issue_view_snapshot(self, repo_root, issue_number, *, repo_slug=None):
        self.issue_view_calls.append((repo_root, issue_number, repo_slug))
        raise RuntimeError("gh view failed")


class TestCheckDepsApplication(unittest.TestCase):
    def _records(self, infra_contracts):
        root = Path("/repo/spec-dock/initiatives/init-00101-auth-platform")
        epic_dir = root / "epics" / "epic-00201-jwt-auth"
        dep_dir = epic_dir / "issues" / "iss-00301-dep-issue"
        target_dir = epic_dir / "issues" / "iss-00302-target-issue"
        return [
            infra_contracts.StoredMetaRecord(
                kind="initiative",
                id="init-00101",
                title="Auth platform",
                slug="auth-platform",
                path=root.as_posix(),
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=101,
                meta_path=(root / ".meta.json").as_posix(),
            ),
            infra_contracts.StoredMetaRecord(
                kind="epic",
                id="epic-00201",
                title="JWT auth",
                slug="jwt-auth",
                path=epic_dir.as_posix(),
                parent_id="init-00101",
                initiative_id="init-00101",
                epic_id=None,
                github_issue_number=201,
                meta_path=(epic_dir / ".meta.json").as_posix(),
            ),
            infra_contracts.StoredMetaRecord(
                kind="issue",
                id="iss-00301",
                title="Dep issue",
                slug="dep-issue",
                path=dep_dir.as_posix(),
                parent_id="epic-00201",
                initiative_id="init-00101",
                epic_id="epic-00201",
                github_issue_number=301,
                meta_path=(dep_dir / ".meta.json").as_posix(),
            ),
            infra_contracts.StoredMetaRecord(
                kind="issue",
                id="iss-00302",
                title="Target issue",
                slug="target-issue",
                path=target_dir.as_posix(),
                parent_id="epic-00201",
                initiative_id="init-00101",
                epic_id="epic-00201",
                github_issue_number=302,
                meta_path=(target_dir / ".meta.json").as_posix(),
            ),
        ]

    def _external_records(self, infra_contracts):
        root = Path("/repo/spec-dock/initiatives/init-00102-external-deps")
        epic_dir = root / "epics" / "epic-00202-external-epic"
        issue_one_dir = epic_dir / "issues" / "iss-00401-external-issue-one"
        issue_two_dir = epic_dir / "issues" / "iss-00402-external-issue-two"
        return [
            infra_contracts.StoredMetaRecord(
                kind="initiative",
                id="init-00102",
                title="External deps",
                slug="external-deps",
                path=root.as_posix(),
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=102,
                meta_path=(root / ".meta.json").as_posix(),
            ),
            infra_contracts.StoredMetaRecord(
                kind="epic",
                id="epic-00202",
                title="External epic",
                slug="external-epic",
                path=epic_dir.as_posix(),
                parent_id="init-00102",
                initiative_id="init-00102",
                epic_id=None,
                github_issue_number=202,
                meta_path=(epic_dir / ".meta.json").as_posix(),
            ),
            infra_contracts.StoredMetaRecord(
                kind="issue",
                id="iss-00401",
                title="External issue one",
                slug="external-issue-one",
                path=issue_one_dir.as_posix(),
                parent_id="epic-00202",
                initiative_id="init-00102",
                epic_id="epic-00202",
                github_issue_number=401,
                meta_path=(issue_one_dir / ".meta.json").as_posix(),
            ),
            infra_contracts.StoredMetaRecord(
                kind="issue",
                id="iss-00402",
                title="External issue two",
                slug="external-issue-two",
                path=issue_two_dir.as_posix(),
                parent_id="epic-00202",
                initiative_id="init-00102",
                epic_id="epic-00202",
                github_issue_number=402,
                meta_path=(issue_two_dir / ".meta.json").as_posix(),
            ),
        ]

    def _request(self, app_contracts, *, use_github, node_id="iss-00302"):
        return app_contracts.CheckDepsRequest(
            target=app_contracts.TargetRef(
                kind="node_id",
                node_id=node_id,
                github_issue_number=None,
            ),
            use_github=use_github,
            issue_limit=10000,
        )

    def _ports(
        self,
        app_ports,
        infra_contracts,
        *,
        derived_state_reader=None,
        issue_gateway=None,
        deps=None,
        records=None,
    ):
        if records is None:
            records = self._records(infra_contracts)
        return app_ports.Ports(
            node_reader=_StubNodeReader(records),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
            derived_state_reader=derived_state_reader,
            issue_gateway=issue_gateway,
            deps_topology_reader=_StubDepsTopologyReader(deps or {"iss-00302": ["iss-00301"]}),
        )

    def _snapshot(self, domain_models, issue_number, state, *, updated_at="2026-06-05T00:00:00Z"):
        return domain_models.IssueSnapshot(
            issue_number=issue_number,
            state=state,
            title=f"Issue {issue_number}",
            labels=[],
            updated_at=updated_at,
            url=f"https://github.com/example/repo/issues/{issue_number}",
        )

    def test_no_github_uses_cached_status_and_last_sync_without_fetching_github(self) -> None:
        app_check_deps, app_contracts, app_ports, _domain_models, infra_contracts = _runtime_modules()
        issue_gateway = _StubIssueGateway(fail_index=True)
        ports = self._ports(
            app_ports,
            infra_contracts,
            derived_state_reader=_StubDerivedStateReader(
                statuses={"iss-00301": "done", "iss-00302": "open"},
                last_sync_at={"iss-00301": "2026-06-05T01:00:00Z", "iss-00302": "2026-06-05T02:00:00Z"},
            ),
            issue_gateway=issue_gateway,
        )

        result = app_check_deps.check_deps(self._request(app_contracts, use_github=False), ports)

        self.assertTrue(result.inspection.evaluation.ready)
        self.assertEqual(result.inspection.evaluation.blockers, [])
        self.assertEqual(result.inspection.node_states["iss-00301"].status, "done")
        self.assertEqual(result.inspection.issue_statuses["iss-00302"].source, "cache")
        self.assertTrue(result.inspection.issue_statuses["iss-00302"].stale)
        self.assertEqual(result.inspection.issue_statuses["iss-00302"].last_sync_at, "2026-06-05T02:00:00Z")
        self.assertEqual(issue_gateway.issue_index_calls, [])

    def test_effective_depends_on_merges_parents_and_dedups_without_cli(self) -> None:
        app_check_deps, app_contracts, app_ports, _domain_models, infra_contracts = _runtime_modules()
        ports = self._ports(
            app_ports,
            infra_contracts,
            records=self._records(infra_contracts) + self._external_records(infra_contracts),
            derived_state_reader=_StubDerivedStateReader(
                statuses={
                    "iss-00301": "open",
                    "iss-00302": "open",
                    "iss-00401": "open",
                },
            ),
            deps={
                "init-00101": ["iss-00401"],
                "epic-00201": ["iss-00401"],
                "iss-00302": ["iss-00301"],
            },
        )

        result = app_check_deps.check_deps(self._request(app_contracts, use_github=False), ports)

        self.assertEqual(result.inspection.effective_depends_on, ["iss-00301", "iss-00401"])
        self.assertEqual(result.inspection.node_states["iss-00302"].effective_depends_on, ["iss-00301", "iss-00401"])
        self.assertEqual(result.inspection.evaluation.blockers, ["iss-00301", "iss-00401"])

    def test_effective_depends_on_merges_epic_and_initiative_without_cli(self) -> None:
        app_check_deps, app_contracts, app_ports, _domain_models, infra_contracts = _runtime_modules()
        ports = self._ports(
            app_ports,
            infra_contracts,
            records=self._records(infra_contracts) + self._external_records(infra_contracts),
            derived_state_reader=_StubDerivedStateReader(
                statuses={
                    "iss-00301": "open",
                    "iss-00302": "open",
                    "iss-00401": "open",
                    "iss-00402": "open",
                },
            ),
            deps={
                "init-00101": ["iss-00401"],
                "epic-00201": ["iss-00402"],
            },
        )

        result = app_check_deps.check_deps(
            self._request(app_contracts, use_github=False, node_id="epic-00201"),
            ports,
        )

        self.assertEqual(result.inspection.effective_depends_on, ["iss-00401", "iss-00402"])
        self.assertEqual(result.inspection.evaluation.blockers, ["iss-00401", "iss-00402"])

    def test_no_github_missing_cache_defaults_to_unknown_and_blocks(self) -> None:
        app_check_deps, app_contracts, app_ports, _domain_models, infra_contracts = _runtime_modules()
        ports = self._ports(
            app_ports,
            infra_contracts,
            derived_state_reader=_StubDerivedStateReader(),
        )

        result = app_check_deps.check_deps(self._request(app_contracts, use_github=False), ports)

        self.assertFalse(result.inspection.evaluation.ready)
        self.assertEqual(result.inspection.evaluation.guard_reason, "unknown")
        self.assertEqual(result.inspection.evaluation.blockers, ["iss-00301"])
        self.assertEqual(result.inspection.node_states["iss-00301"].status, "unknown")
        self.assertEqual(result.inspection.issue_statuses["iss-00301"].source, "cache")
        self.assertIsNone(result.inspection.issue_statuses["iss-00301"].last_sync_at)

    def test_github_index_incomplete_warns_and_leaves_missing_dependency_unknown(self) -> None:
        app_check_deps, app_contracts, app_ports, domain_models, infra_contracts = _runtime_modules()
        issue_gateway = _StubIssueGateway(
            [
                self._snapshot(domain_models, 101, "OPEN"),
                self._snapshot(domain_models, 201, "OPEN"),
                self._snapshot(domain_models, 302, "OPEN"),
            ]
        )
        ports = self._ports(app_ports, infra_contracts, issue_gateway=issue_gateway)

        result = app_check_deps.check_deps(self._request(app_contracts, use_github=True), ports)

        self.assertIn("gh_index_incomplete", result.warnings)
        self.assertNotIn("gh_fetch_failed", result.warnings)
        self.assertFalse(result.inspection.evaluation.ready)
        self.assertEqual(result.inspection.evaluation.guard_reason, "unknown")
        self.assertEqual(result.inspection.evaluation.blockers, ["iss-00301"])
        self.assertEqual(result.inspection.node_states["iss-00301"].status, "unknown")
        self.assertEqual(issue_gateway.issue_index_calls, [(Path("/repo"), 10000)])

    def test_github_fetch_failure_warns_and_blocks_on_unknown_dependency(self) -> None:
        app_check_deps, app_contracts, app_ports, _domain_models, infra_contracts = _runtime_modules()
        issue_gateway = _StubIssueGateway(fail_index=True)
        ports = self._ports(app_ports, infra_contracts, issue_gateway=issue_gateway)

        result = app_check_deps.check_deps(self._request(app_contracts, use_github=True), ports)

        self.assertIn("gh_fetch_failed", result.warnings)
        self.assertFalse(result.inspection.evaluation.ready)
        self.assertEqual(result.inspection.evaluation.guard_reason, "unknown")
        self.assertEqual(result.inspection.evaluation.blockers, ["iss-00301"])
        self.assertEqual(result.inspection.issue_statuses["iss-00301"].source, "unknown")
        self.assertEqual(issue_gateway.issue_index_calls, [(Path("/repo"), 10000)])

    def test_github_snapshots_drive_ready_and_blocked_states_without_cli(self) -> None:
        app_check_deps, app_contracts, app_ports, domain_models, infra_contracts = _runtime_modules()
        ready_ports = self._ports(
            app_ports,
            infra_contracts,
            issue_gateway=_StubIssueGateway(
                [
                    self._snapshot(domain_models, 101, "OPEN"),
                    self._snapshot(domain_models, 201, "OPEN"),
                    self._snapshot(domain_models, 301, "CLOSED", updated_at="2026-06-05T03:00:00Z"),
                    self._snapshot(domain_models, 302, "OPEN"),
                ]
            ),
        )

        ready = app_check_deps.check_deps(self._request(app_contracts, use_github=True), ready_ports)

        self.assertTrue(ready.inspection.evaluation.ready)
        self.assertEqual(ready.inspection.evaluation.blockers, [])
        self.assertEqual(ready.inspection.node_states["iss-00301"].status, "done")
        self.assertEqual(ready.inspection.issue_statuses["iss-00301"].source, "github")
        self.assertEqual(ready.inspection.issue_statuses["iss-00301"].last_sync_at, "2026-06-05T03:00:00Z")

        blocked_ports = self._ports(
            app_ports,
            infra_contracts,
            issue_gateway=_StubIssueGateway(
                [
                    self._snapshot(domain_models, 101, "OPEN"),
                    self._snapshot(domain_models, 201, "OPEN"),
                    self._snapshot(domain_models, 301, "OPEN"),
                    self._snapshot(domain_models, 302, "OPEN"),
                ]
            ),
        )

        blocked = app_check_deps.check_deps(self._request(app_contracts, use_github=True), blocked_ports)

        self.assertFalse(blocked.inspection.evaluation.ready)
        self.assertEqual(blocked.inspection.evaluation.guard_reason, "blocked")
        self.assertEqual(blocked.inspection.evaluation.blockers, ["iss-00301"])
        self.assertEqual(blocked.inspection.node_states["iss-00301"].status, "ready")
