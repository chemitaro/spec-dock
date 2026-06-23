import json
from pathlib import Path
import sys

import pytest


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application import (
            check_deps as app_check_deps,
            contracts as app_contracts,
            ports as app_ports,
        )
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
    def __init__(self, issue_depends_on_map, warnings=None, node_depends_on_map=None, dependency_contexts=None):
        self.issue_depends_on_map = {
            issue_id: list(depends_on) for issue_id, depends_on in issue_depends_on_map.items()
        }
        self.warnings = list(warnings or [])
        self.node_depends_on_map = {
            node_id: list(depends_on) for node_id, depends_on in (node_depends_on_map or {}).items()
        }
        self.dependency_contexts = {
            issue_id: list(contexts) for issue_id, contexts in (dependency_contexts or {}).items()
        }

    def load_issue_depends_on_map(self, specdock_dir, graph):
        _app_check_deps, _app_contracts, _app_ports, _domain_models, infra_contracts = _runtime_modules()
        return infra_contracts.DepsTopologyLoadResult(
            issue_depends_on_map=dict(self.issue_depends_on_map),
            warnings=list(self.warnings),
            dependency_contexts_by_issue_id=dict(self.dependency_contexts),
        )

    def load_node_dependency_resolutions(self, specdock_dir, graph):
        _app_check_deps, _app_contracts, _app_ports, _domain_models, infra_contracts = _runtime_modules()
        return {
            node_id: [
                infra_contracts.DirectDependencyResolution(raw_ref=dep_id, resolved_node_id=dep_id)
                for dep_id in depends_on
            ]
            for node_id, depends_on in self.node_depends_on_map.items()
        }


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


class TestCheckDepsApplication:
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

    def _empty_epic_records(self, infra_contracts):
        root = Path("/repo/spec-dock/initiatives/init-00103-empty-containers")
        epic_one_dir = root / "epics" / "epic-00203-empty-one"
        epic_two_dir = root / "epics" / "epic-00204-empty-two"
        return [
            infra_contracts.StoredMetaRecord(
                kind="initiative",
                id="init-00103",
                title="Empty containers",
                slug="empty-containers",
                path=root.as_posix(),
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=103,
                meta_path=(root / ".meta.json").as_posix(),
            ),
            infra_contracts.StoredMetaRecord(
                kind="epic",
                id="epic-00203",
                title="Empty one",
                slug="empty-one",
                path=epic_one_dir.as_posix(),
                parent_id="init-00103",
                initiative_id="init-00103",
                epic_id=None,
                github_issue_number=203,
                meta_path=(epic_one_dir / ".meta.json").as_posix(),
            ),
            infra_contracts.StoredMetaRecord(
                kind="epic",
                id="epic-00204",
                title="Empty two",
                slug="empty-two",
                path=epic_two_dir.as_posix(),
                parent_id="init-00103",
                initiative_id="init-00103",
                epic_id=None,
                github_issue_number=204,
                meta_path=(epic_two_dir / ".meta.json").as_posix(),
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
        dependency_contexts=None,
        specdock_dir=Path("/repo/spec-dock"),
    ):
        if records is None:
            records = self._records(infra_contracts)
        return app_ports.Ports(
            node_reader=_StubNodeReader(records),
            repo_root=Path("/repo"),
            specdock_dir=specdock_dir,
            derived_state_reader=derived_state_reader,
            issue_gateway=issue_gateway,
            deps_topology_reader=_StubDepsTopologyReader(
                deps or {"iss-00302": ["iss-00301"]},
                dependency_contexts=dependency_contexts,
            ),
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

        assert result.inspection.evaluation.ready
        assert result.inspection.evaluation.blockers == []
        assert result.inspection.node_states["iss-00301"].status == "done"
        assert result.inspection.issue_statuses["iss-00302"].source == "cache"
        assert result.inspection.issue_statuses["iss-00302"].stale
        assert result.inspection.issue_statuses["iss-00302"].last_sync_at == "2026-06-05T02:00:00Z"
        assert issue_gateway.issue_index_calls == []

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

        assert result.inspection.effective_depends_on == ["iss-00301", "iss-00401"]
        assert result.inspection.node_states["iss-00302"].effective_depends_on == ["iss-00301", "iss-00401"]
        assert result.inspection.evaluation.blockers == ["iss-00301", "iss-00401"]

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

        assert result.inspection.effective_depends_on == ["iss-00401", "iss-00402"]
        assert result.inspection.evaluation.blockers == ["iss-00401", "iss-00402"]

    def test_deps_check_fails_raw_node_preflight_before_empty_container_ready(self) -> None:
        app_check_deps, app_contracts, app_ports, _domain_models, infra_contracts = _runtime_modules()
        ports = app_ports.Ports(
            node_reader=_StubNodeReader(self._empty_epic_records(infra_contracts)),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
            derived_state_reader=_StubDerivedStateReader(),
            deps_topology_reader=_StubDepsTopologyReader(
                {},
                node_depends_on_map={
                    "epic-00203": ["epic-00204"],
                    "epic-00204": ["epic-00203"],
                },
            ),
        )

        with pytest.raises(RuntimeError, match="Dependency cycle detected"):
            app_check_deps.check_deps(
                self._request(app_contracts, use_github=False, node_id="epic-00203"),
                ports,
            )

    def test_no_github_missing_cache_defaults_to_unknown_and_blocks(self) -> None:
        app_check_deps, app_contracts, app_ports, _domain_models, infra_contracts = _runtime_modules()
        ports = self._ports(
            app_ports,
            infra_contracts,
            derived_state_reader=_StubDerivedStateReader(),
        )

        result = app_check_deps.check_deps(self._request(app_contracts, use_github=False), ports)

        assert not result.inspection.evaluation.ready
        assert result.inspection.evaluation.guard_reason == "unknown"
        assert result.inspection.evaluation.blockers == ["iss-00301"]
        assert result.inspection.node_states["iss-00301"].status == "unknown"
        assert result.inspection.issue_statuses["iss-00301"].source == "cache"
        assert result.inspection.issue_statuses["iss-00301"].last_sync_at is None

    def test_github_index_incomplete_warns_and_leaves_missing_dependency_unknown(self) -> None:
        app_check_deps, app_contracts, app_ports, domain_models, infra_contracts = _runtime_modules()
        issue_gateway = _StubIssueGateway([
            self._snapshot(domain_models, 101, "OPEN"),
            self._snapshot(domain_models, 201, "OPEN"),
            self._snapshot(domain_models, 302, "OPEN"),
        ])
        ports = self._ports(app_ports, infra_contracts, issue_gateway=issue_gateway)

        result = app_check_deps.check_deps(self._request(app_contracts, use_github=True), ports)

        assert "gh_index_incomplete" in result.warnings
        assert "gh_fetch_failed" not in result.warnings
        assert not result.inspection.evaluation.ready
        assert result.inspection.evaluation.guard_reason == "unknown"
        assert result.inspection.evaluation.blockers == ["iss-00301"]
        assert result.inspection.node_states["iss-00301"].status == "unknown"
        assert issue_gateway.issue_index_calls == [(Path("/repo"), 10000)]

    def test_github_fetch_failure_warns_and_blocks_on_unknown_dependency(self) -> None:
        app_check_deps, app_contracts, app_ports, _domain_models, infra_contracts = _runtime_modules()
        issue_gateway = _StubIssueGateway(fail_index=True)
        ports = self._ports(app_ports, infra_contracts, issue_gateway=issue_gateway)

        result = app_check_deps.check_deps(self._request(app_contracts, use_github=True), ports)

        assert "gh_fetch_failed" in result.warnings
        assert not result.inspection.evaluation.ready
        assert result.inspection.evaluation.guard_reason == "unknown"
        assert result.inspection.evaluation.blockers == ["iss-00301"]
        assert result.inspection.issue_statuses["iss-00301"].source == "unknown"
        assert issue_gateway.issue_index_calls == [(Path("/repo"), 10000)]

    def test_github_snapshots_drive_ready_and_blocked_states_without_cli(self) -> None:
        app_check_deps, app_contracts, app_ports, domain_models, infra_contracts = _runtime_modules()
        ready_ports = self._ports(
            app_ports,
            infra_contracts,
            issue_gateway=_StubIssueGateway([
                self._snapshot(domain_models, 101, "OPEN"),
                self._snapshot(domain_models, 201, "OPEN"),
                self._snapshot(domain_models, 301, "CLOSED", updated_at="2026-06-05T03:00:00Z"),
                self._snapshot(domain_models, 302, "OPEN"),
            ]),
        )

        ready = app_check_deps.check_deps(self._request(app_contracts, use_github=True), ready_ports)

        assert ready.inspection.evaluation.ready
        assert ready.inspection.evaluation.blockers == []
        assert ready.inspection.node_states["iss-00301"].status == "done"
        assert ready.inspection.issue_statuses["iss-00301"].source == "github"
        assert ready.inspection.issue_statuses["iss-00301"].last_sync_at == "2026-06-05T03:00:00Z"

        blocked_ports = self._ports(
            app_ports,
            infra_contracts,
            issue_gateway=_StubIssueGateway([
                self._snapshot(domain_models, 101, "OPEN"),
                self._snapshot(domain_models, 201, "OPEN"),
                self._snapshot(domain_models, 301, "OPEN"),
                self._snapshot(domain_models, 302, "OPEN"),
            ]),
        )

        blocked = app_check_deps.check_deps(self._request(app_contracts, use_github=True), blocked_ports)

        assert not blocked.inspection.evaluation.ready
        assert blocked.inspection.evaluation.guard_reason == "blocked"
        assert blocked.inspection.evaluation.blockers == ["iss-00301"]
        assert blocked.inspection.node_states["iss-00301"].status == "ready"

    def test_deps_check_passes_empty_open_high_level_context_to_readiness(self) -> None:
        app_check_deps, app_contracts, app_ports, domain_models, infra_contracts = _runtime_modules()
        records = self._records(infra_contracts) + self._empty_epic_records(infra_contracts)
        context = infra_contracts.DepsDependencyContext(
            source_node_id="iss-00302",
            source_issue_id="iss-00302",
            target_node_id="epic-00203",
            target_node_kind="epic",
            target_issue_ids=(),
            expansion="empty",
        )
        ports = self._ports(
            app_ports,
            infra_contracts,
            records=records,
            deps={"iss-00302": []},
            dependency_contexts={"iss-00302": [context]},
            issue_gateway=_StubIssueGateway([
                self._snapshot(domain_models, 103, "OPEN"),
                self._snapshot(domain_models, 203, "OPEN"),
                self._snapshot(domain_models, 302, "OPEN"),
            ]),
        )

        result = app_check_deps.check_deps(self._request(app_contracts, use_github=True), ports)

        assert not result.inspection.evaluation.ready
        assert result.inspection.evaluation.guard_reason == "blocked"
        assert result.inspection.evaluation.blockers == ["epic-00203"]
        assert result.inspection.evaluation.issue_blockers == []
        assert [(b.node_id, b.reason, b.state, b.state_source) for b in result.inspection.evaluation.node_blockers] == [
            ("epic-00203", "empty_open", "open", "github")
        ]
        assert [
            (b.dependency_disposition, b.disposition_basis) for b in result.inspection.evaluation.node_blockers
        ] == [("blocking", "empty_open_container")]

    def test_deps_check_exposes_satisfied_closed_high_level_context(self) -> None:
        app_check_deps, app_contracts, app_ports, domain_models, infra_contracts = _runtime_modules()
        records = self._records(infra_contracts) + self._empty_epic_records(infra_contracts)
        context = infra_contracts.DepsDependencyContext(
            source_node_id="iss-00302",
            source_issue_id="iss-00302",
            target_node_id="epic-00203",
            target_node_kind="epic",
            target_issue_ids=(),
            expansion="empty",
        )
        ports = self._ports(
            app_ports,
            infra_contracts,
            records=records,
            deps={"iss-00302": []},
            dependency_contexts={"iss-00302": [context]},
            issue_gateway=_StubIssueGateway([
                self._snapshot(domain_models, 103, "OPEN"),
                self._snapshot(domain_models, 203, "CLOSED"),
                self._snapshot(domain_models, 302, "OPEN"),
            ]),
        )

        result = app_check_deps.check_deps(self._request(app_contracts, use_github=True), ports)

        assert result.inspection.evaluation.ready
        assert result.inspection.evaluation.blockers == []
        assert result.inspection.evaluation.node_blockers == []
        assert [(c.target_node_id, c.expansion) for c in result.inspection.evaluation.satisfied_dependencies] == [
            ("epic-00203", "empty")
        ]
        assert [
            (c.dependency_disposition, c.disposition_basis) for c in result.inspection.evaluation.satisfied_dependencies
        ] == [("satisfied", "lifecycle_closed")]

    def test_deps_check_exposes_satisfied_open_high_level_context_when_descendants_done(self) -> None:
        app_check_deps, app_contracts, app_ports, domain_models, infra_contracts = _runtime_modules()
        records = self._records(infra_contracts) + self._external_records(infra_contracts)
        context = infra_contracts.DepsDependencyContext(
            source_node_id="iss-00302",
            source_issue_id="iss-00302",
            target_node_id="epic-00202",
            target_node_kind="epic",
            target_issue_ids=("iss-00401", "iss-00402"),
            expansion="expanded",
        )
        ports = self._ports(
            app_ports,
            infra_contracts,
            records=records,
            deps={"iss-00302": ["iss-00401", "iss-00402"]},
            dependency_contexts={"iss-00302": [context]},
            issue_gateway=_StubIssueGateway([
                self._snapshot(domain_models, 102, "OPEN"),
                self._snapshot(domain_models, 202, "OPEN"),
                self._snapshot(domain_models, 302, "OPEN"),
                self._snapshot(domain_models, 401, "CLOSED"),
                self._snapshot(domain_models, 402, "CLOSED"),
            ]),
        )

        result = app_check_deps.check_deps(self._request(app_contracts, use_github=True), ports)

        assert result.inspection.evaluation.ready
        assert result.inspection.evaluation.blockers == []
        assert result.inspection.evaluation.node_blockers == []
        assert [
            (c.target_node_id, c.expansion, c.dependency_disposition, c.disposition_basis)
            for c in result.inspection.evaluation.satisfied_dependencies
        ] == [("epic-00202", "expanded", "satisfied", "all_descendant_issues_done")]

    def test_no_github_uses_cached_high_level_github_state_from_sync_artifact(self, tmp_path) -> None:
        app_check_deps, app_contracts, app_ports, _domain_models, infra_contracts = _runtime_modules()
        specdock_dir = tmp_path / "spec-dock"
        agent_dir = specdock_dir / ".agent"
        agent_dir.mkdir(parents=True)
        (agent_dir / "index-all.json").write_text(
            json.dumps({
                "nodes": {
                    "epic-00203": {
                        "type": "epic",
                        "github": {"issue_number": 203, "state": "CLOSED", "updated_at": "2026-06-05T00:00:00Z"},
                    }
                }
            }),
            encoding="utf-8",
        )
        records = self._records(infra_contracts) + self._empty_epic_records(infra_contracts)
        context = infra_contracts.DepsDependencyContext(
            source_node_id="iss-00302",
            source_issue_id="iss-00302",
            target_node_id="epic-00203",
            target_node_kind="epic",
            target_issue_ids=(),
            expansion="empty",
        )
        ports = self._ports(
            app_ports,
            infra_contracts,
            records=records,
            deps={"iss-00302": []},
            dependency_contexts={"iss-00302": [context]},
            derived_state_reader=_StubDerivedStateReader(
                statuses={"iss-00302": "open"},
                last_sync_at={"iss-00302": "2026-06-05T02:00:00Z"},
            ),
            issue_gateway=_StubIssueGateway(fail_index=True),
            specdock_dir=specdock_dir,
        )

        result = app_check_deps.check_deps(self._request(app_contracts, use_github=False), ports)

        assert result.inspection.evaluation.ready
        assert result.inspection.evaluation.node_blockers == []
        assert [(c.target_node_id, c.expansion) for c in result.inspection.evaluation.satisfied_dependencies] == [
            ("epic-00203", "empty")
        ]

    def test_github_linked_empty_high_level_dependency_without_cache_fails_unknown(self) -> None:
        app_check_deps, app_contracts, app_ports, _domain_models, infra_contracts = _runtime_modules()
        records = [
            *self._records(infra_contracts),
            infra_contracts.StoredMetaRecord(
                kind="epic",
                id="epic-00203",
                title="Linked empty epic",
                slug="linked-empty-epic",
                path="/repo/spec-dock/initiatives/init-00101-auth-platform/epics/epic-00203-linked-empty-epic",
                parent_id="init-00101",
                initiative_id="init-00101",
                epic_id=None,
                github_issue_number=203,
                meta_path="/repo/spec-dock/initiatives/init-00101-auth-platform/epics/epic-00203-linked-empty-epic/.meta.json",
            ),
        ]
        context = infra_contracts.DepsDependencyContext(
            source_node_id="iss-00302",
            source_issue_id="iss-00302",
            target_node_id="epic-00203",
            target_node_kind="epic",
            target_issue_ids=(),
            expansion="empty",
        )
        ports = self._ports(
            app_ports,
            infra_contracts,
            records=records,
            deps={"iss-00302": []},
            dependency_contexts={"iss-00302": [context]},
            derived_state_reader=_StubDerivedStateReader(statuses={"iss-00302": "open"}),
            issue_gateway=_StubIssueGateway(fail_index=True),
        )

        result = app_check_deps.check_deps(self._request(app_contracts, use_github=False), ports)

        assert not result.inspection.evaluation.ready
        assert result.inspection.evaluation.guard_reason == "unknown"
        assert [(b.node_id, b.reason, b.state, b.state_source) for b in result.inspection.evaluation.node_blockers] == [
            ("epic-00203", "empty_unknown", "unknown", "none")
        ]
        assert [
            (b.dependency_disposition, b.disposition_basis) for b in result.inspection.evaluation.node_blockers
        ] == [("indeterminate", "empty_unknown_container")]

    def test_local_empty_high_level_dependency_preserves_open_status(self) -> None:
        app_check_deps, app_contracts, app_ports, _domain_models, infra_contracts = _runtime_modules()
        records = [
            *self._records(infra_contracts),
            infra_contracts.StoredMetaRecord(
                kind="epic",
                id="epic-local-00203",
                title="Local empty epic",
                slug="local-empty-epic",
                path="/repo/spec-dock/initiatives/init-00101-auth-platform/epics/epic-local-00203-local-empty-epic",
                parent_id="init-00101",
                initiative_id="init-00101",
                epic_id=None,
                github_issue_number=None,
                meta_path="/repo/spec-dock/initiatives/init-00101-auth-platform/epics/epic-local-00203-local-empty-epic/.meta.json",
            ),
        ]
        context = infra_contracts.DepsDependencyContext(
            source_node_id="iss-00302",
            source_issue_id="iss-00302",
            target_node_id="epic-local-00203",
            target_node_kind="epic",
            target_issue_ids=(),
            expansion="empty",
        )
        ports = self._ports(
            app_ports,
            infra_contracts,
            records=records,
            deps={"iss-00302": []},
            dependency_contexts={"iss-00302": [context]},
            derived_state_reader=_StubDerivedStateReader(statuses={"iss-00302": "open"}),
            issue_gateway=_StubIssueGateway(fail_index=True),
        )

        result = app_check_deps.check_deps(self._request(app_contracts, use_github=False), ports)

        assert not result.inspection.evaluation.ready
        assert result.inspection.evaluation.guard_reason == "blocked"
        assert [(b.node_id, b.reason, b.state, b.state_source) for b in result.inspection.evaluation.node_blockers] == [
            ("epic-local-00203", "empty_open", "open", "local")
        ]

    def test_local_high_level_default_open_does_not_mask_done_descendant_aggregate(self) -> None:
        app_check_deps, app_contracts, app_ports, _domain_models, infra_contracts = _runtime_modules()
        runtime_scripts_dir = (
            Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime.domain.tree import build_graph
        finally:
            sys.path.pop(0)
        records = [
            *self._records(infra_contracts),
            infra_contracts.StoredMetaRecord(
                kind="epic",
                id="epic-local-00203",
                title="Local epic",
                slug="local-epic",
                path="/repo/spec-dock/initiatives/init-00101-auth-platform/epics/epic-local-00203-local-epic",
                parent_id="init-00101",
                initiative_id="init-00101",
                epic_id=None,
                github_issue_number=None,
                meta_path="/repo/spec-dock/initiatives/init-00101-auth-platform/epics/epic-local-00203-local-epic/.meta.json",
            ),
            infra_contracts.StoredMetaRecord(
                kind="issue",
                id="iss-local-00401",
                title="Local child",
                slug="local-child",
                path="/repo/spec-dock/initiatives/init-00101-auth-platform/epics/epic-local-00203-local-epic/issues/iss-local-00401-local-child",
                parent_id="epic-local-00203",
                initiative_id="init-00101",
                epic_id="epic-local-00203",
                github_issue_number=401,
                meta_path="/repo/spec-dock/initiatives/init-00101-auth-platform/epics/epic-local-00203-local-epic/issues/iss-local-00401-local-child/.meta.json",
            ),
        ]
        context = infra_contracts.DepsDependencyContext(
            source_node_id="iss-00302",
            source_issue_id="iss-00302",
            target_node_id="epic-local-00203",
            target_node_kind="epic",
            target_issue_ids=("iss-local-00401",),
            expansion="expanded",
        )
        ports = self._ports(
            app_ports,
            infra_contracts,
            records=records,
            deps={"iss-00302": ["iss-local-00401"]},
            dependency_contexts={"iss-00302": [context]},
            derived_state_reader=_StubDerivedStateReader({"iss-local-00401": "done"}),
            issue_gateway=_StubIssueGateway(fail_index=True),
        )

        result = app_check_deps.check_deps(self._request(app_contracts, use_github=False), ports)

        assert result.inspection.evaluation.node_blockers == []
        assert [(c.target_node_id, c.expansion) for c in result.inspection.evaluation.satisfied_dependencies] == [
            ("epic-local-00203", "expanded")
        ]
        assert [
            (c.dependency_disposition, c.disposition_basis) for c in result.inspection.evaluation.satisfied_dependencies
        ] == [("satisfied", "all_descendant_issues_done")]

        graph = build_graph([app_check_deps._to_spec_node_seed(record) for record in records])
        high_level_statuses = app_check_deps.resolve_high_level_status_context(
            graph,
            issue_statuses=result.inspection.issue_statuses,
        )
        assert high_level_statuses["epic-local-00203"].state == "done"
        assert high_level_statuses["epic-local-00203"].source == "descendant_aggregate"
