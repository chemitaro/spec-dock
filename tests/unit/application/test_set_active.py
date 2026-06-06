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
        from spec_dock_runtime.application import contracts as app_contracts
        from spec_dock_runtime.application import ports as app_ports
        from spec_dock_runtime.application import set_active as app_set_active
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.infra import contracts as infra_contracts
    finally:
        sys.path.pop(0)
    return app_contracts, app_ports, app_set_active, domain_models, infra_contracts


class _StubNodeReader:
    def __init__(self, records):
        self.records = list(records)

    def load_node_records(self):
        return list(self.records)


class _StubDepsTopologyReader:
    def __init__(self, issue_depends_on_map=None):
        self.issue_depends_on_map = dict(issue_depends_on_map or {})

    def load_issue_depends_on_map(self, specdock_dir, graph):
        _app_contracts, _app_ports, _app_set_active, _domain_models, infra_contracts = _runtime_modules()
        return infra_contracts.DepsTopologyLoadResult(
            issue_depends_on_map=dict(self.issue_depends_on_map),
            warnings=[],
        )


class _StubDerivedStateReader:
    def __init__(self, statuses=None):
        self.statuses = dict(statuses or {})

    def load_cached_issue_status_by_id(self, specdock_dir):
        return dict(self.statuses)

    def load_cached_issue_last_sync_at_by_id(self, specdock_dir):
        return {}


class _StubActiveStateStore:
    def __init__(self, manifest=None):
        _app_contracts, _app_ports, _app_set_active, _domain_models, infra_contracts = _runtime_modules()
        self.manifest = manifest
        self.written = []
        self.applied = []
        self.patched = []
        self.snapshot = infra_contracts.ActiveStateSnapshot(
            manifest=manifest,
            context_pack_text=None,
            active_json_text=None,
            managed_agent_state={},
        )

    def load_active_manifest(self, specdock_dir):
        _app_contracts, _app_ports, _app_set_active, _domain_models, infra_contracts = _runtime_modules()
        return infra_contracts.ActiveManifestLoadResult(
            manifest=self.manifest,
            source="agent.active" if self.manifest is not None else "none",
            warnings=[],
        )

    def load_active_manifest_no_migrate(self, specdock_dir):
        return self.load_active_manifest(specdock_dir)

    def load_active_issue_id(self, specdock_dir):
        return self.manifest.issue.id if self.manifest is not None and self.manifest.issue is not None else None

    def snapshot_current_state(self, specdock_dir):
        return self.snapshot

    def write_active_manifest(self, specdock_dir, manifest):
        self.manifest = manifest
        self.written.append(manifest)
        return manifest

    def apply_active_pointers(self, specdock_dir, manifest, rendered_context_pack):
        self.applied.append((manifest, rendered_context_pack))

    def patch_agent_state_active_fields(self, specdock_dir, manifest):
        self.patched.append(manifest)

    def restore_previous_state(self, specdock_dir, snapshot):
        self.manifest = snapshot.manifest


class _StubIssueGateway:
    def __init__(self, snapshots):
        self.snapshots = list(snapshots)
        self.issue_index_calls = []

    def issue_index(self, repo_root, *, limit):
        self.issue_index_calls.append((repo_root, limit))
        return list(self.snapshots)

    def issue_view_snapshot(self, repo_root, issue_number, *, repo_slug=None):
        raise RuntimeError("not used")


class _StubGitGateway:
    def __init__(self, *, current_branch="main", existing_branches=(), valid_ref=True):
        self.current_branch = current_branch
        self.existing_branches = set(existing_branches)
        self.valid_ref = valid_ref
        self.calls = []

    def origin_github_repo_slug(self, repo_root):
        return "example/repo"

    def check_ref_format_branch(self, repo_root, branch):
        self.calls.append(("check_ref_format_branch", branch))
        return self.valid_ref

    def require_clean_working_tree(self, repo_root):
        self.calls.append(("require_clean_working_tree", None))

    def current_branch_or_none(self, repo_root):
        self.calls.append(("current_branch_or_none", None))
        return self.current_branch

    def local_branch_exists(self, repo_root, branch):
        self.calls.append(("local_branch_exists", branch))
        return branch in self.existing_branches

    def checkout_branch(self, repo_root, branch):
        self.calls.append(("checkout_branch", branch))
        self.current_branch = branch

    def create_and_checkout_branch(self, repo_root, branch):
        self.calls.append(("create_and_checkout_branch", branch))
        self.current_branch = branch


class TestSetActiveApplication(unittest.TestCase):
    def _records(self, infra_contracts):
        root = Path("/repo/spec-dock/initiatives/init-00101-auth-platform")
        epic = root / "epics" / "epic-00201-jwt-auth"
        dep = epic / "issues" / "iss-00301-dep-issue"
        target = epic / "issues" / "iss-00302-target-issue"
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
                github_repo_owner="example",
                github_repo_name="repo",
            ),
            infra_contracts.StoredMetaRecord(
                kind="epic",
                id="epic-00201",
                title="JWT auth",
                slug="jwt-auth",
                path=epic.as_posix(),
                parent_id="init-00101",
                initiative_id="init-00101",
                epic_id=None,
                github_issue_number=201,
                meta_path=(epic / ".meta.json").as_posix(),
                github_repo_owner="example",
                github_repo_name="repo",
            ),
            infra_contracts.StoredMetaRecord(
                kind="issue",
                id="iss-00301",
                title="Dep issue",
                slug="dep-issue",
                path=dep.as_posix(),
                parent_id="epic-00201",
                initiative_id="init-00101",
                epic_id="epic-00201",
                github_issue_number=301,
                meta_path=(dep / ".meta.json").as_posix(),
                github_repo_owner="example",
                github_repo_name="repo",
            ),
            infra_contracts.StoredMetaRecord(
                kind="issue",
                id="iss-00302",
                title="Target issue",
                slug="target-issue",
                path=target.as_posix(),
                parent_id="epic-00201",
                initiative_id="init-00101",
                epic_id="epic-00201",
                github_issue_number=302,
                meta_path=(target / ".meta.json").as_posix(),
                github_repo_owner="example",
                github_repo_name="repo",
            ),
        ]

    def _ports(
        self,
        app_ports,
        infra_contracts,
        *,
        active_store=None,
        deps=None,
        derived_state_reader=None,
        issue_gateway=None,
        git_gateway=None,
    ):
        return app_ports.Ports(
            node_reader=_StubNodeReader(self._records(infra_contracts)),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
            active_state_store=active_store or _StubActiveStateStore(),
            deps_topology_reader=_StubDepsTopologyReader(deps),
            derived_state_reader=derived_state_reader,
            issue_gateway=issue_gateway,
            git_gateway=git_gateway,
        )

    def _request(self, app_contracts, *, target, use_github=False, force=False, checkout=False):
        return app_contracts.SetActiveRequest(
            target=target,
            use_github=use_github,
            force=force,
            checkout=checkout,
            issue_limit=10000,
        )

    def _node_id_target(self, app_contracts, node_id):
        return app_contracts.TargetRef(kind="node_id", node_id=node_id, github_issue_number=None)

    def _github_target(self, app_contracts, issue_number, *, owner=None, repo=None):
        return app_contracts.TargetRef(
            kind="github_issue",
            node_id=None,
            github_issue_number=issue_number,
            github_repo_owner=owner,
            github_repo_name=repo,
        )

    def _snapshot(self, domain_models, issue_number, state):
        return domain_models.IssueSnapshot(
            issue_number=issue_number,
            state=state,
            title=f"Issue {issue_number}",
            labels=[],
            updated_at="2026-06-05T00:00:00Z",
            url=f"https://github.com/example/repo/issues/{issue_number}",
            repo_owner="example",
            repo_name="repo",
        )

    def test_set_active_resolves_id_and_repo_scoped_github_target_without_cli(self) -> None:
        app_contracts, app_ports, app_set_active, _domain_models, infra_contracts = _runtime_modules()
        active_store = _StubActiveStateStore()
        ports = self._ports(app_ports, infra_contracts, active_store=active_store)

        by_id = app_set_active.set_active(
            self._request(app_contracts, target=self._node_id_target(app_contracts, "iss-302"), force=True),
            ports,
        )
        self.assertEqual(by_id.selection.issue_id, "iss-00302")
        self.assertEqual(active_store.written[-1].issue.id, "iss-00302")
        self.assertEqual(active_store.written[-1].issue.path, "spec-dock/initiatives/init-00101-auth-platform/epics/epic-00201-jwt-auth/issues/iss-00302-target-issue")

        by_github = app_set_active.set_active(
            self._request(
                app_contracts,
                target=self._github_target(app_contracts, 301, owner="example", repo="repo"),
                force=True,
            ),
            ports,
        )
        self.assertEqual(by_github.selection.issue_id, "iss-00301")

    def test_set_active_deps_guard_blocks_without_writing_and_force_writes_with_warning_without_cli(self) -> None:
        app_contracts, app_ports, app_set_active, _domain_models, infra_contracts = _runtime_modules()
        active_store = _StubActiveStateStore()
        ports = self._ports(
            app_ports,
            infra_contracts,
            active_store=active_store,
            deps={"iss-00302": ["iss-00301"]},
            derived_state_reader=_StubDerivedStateReader({"iss-00301": "open", "iss-00302": "open"}),
        )

        with self.assertRaisesRegex(RuntimeError, "active set blocked"):
            app_set_active.set_active(
                self._request(app_contracts, target=self._node_id_target(app_contracts, "iss-00302")),
                ports,
            )
        self.assertEqual(active_store.written, [])

        forced = app_set_active.set_active(
            self._request(app_contracts, target=self._node_id_target(app_contracts, "iss-00302"), force=True),
            ports,
        )
        self.assertEqual(forced.selection.issue_id, "iss-00302")
        self.assertIn("deps_blocked", "\n".join(forced.warnings))
        self.assertEqual(active_store.written[-1].issue.id, "iss-00302")

    def test_set_active_github_uses_live_issue_state_and_no_github_uses_cache_without_cli(self) -> None:
        app_contracts, app_ports, app_set_active, domain_models, infra_contracts = _runtime_modules()
        gateway = _StubIssueGateway(
            [
                self._snapshot(domain_models, 301, "CLOSED"),
                self._snapshot(domain_models, 302, "OPEN"),
            ]
        )
        active_store = _StubActiveStateStore()
        ports = self._ports(
            app_ports,
            infra_contracts,
            active_store=active_store,
            deps={"iss-00302": ["iss-00301"]},
            derived_state_reader=_StubDerivedStateReader({"iss-00301": "open", "iss-00302": "open"}),
            issue_gateway=gateway,
        )

        live = app_set_active.set_active(
            self._request(
                app_contracts,
                target=self._node_id_target(app_contracts, "iss-00302"),
                use_github=True,
            ),
            ports,
        )
        self.assertEqual(live.selection.issue_id, "iss-00302")
        self.assertEqual(gateway.issue_index_calls, [(Path("/repo"), 10000)])

        cache_only_store = _StubActiveStateStore()
        cache_only_ports = self._ports(
            app_ports,
            infra_contracts,
            active_store=cache_only_store,
            deps={"iss-00302": ["iss-00301"]},
            derived_state_reader=_StubDerivedStateReader({"iss-00301": "done", "iss-00302": "open"}),
            issue_gateway=_StubIssueGateway([]),
        )
        cache_only = app_set_active.set_active(
            self._request(app_contracts, target=self._node_id_target(app_contracts, "iss-00302")),
            cache_only_ports,
        )
        self.assertEqual(cache_only.selection.issue_id, "iss-00302")
        self.assertEqual(cache_only_ports.issue_gateway.issue_index_calls, [])

    def test_set_active_checkout_uses_git_gateway_branch_decision_without_cli_git(self) -> None:
        app_contracts, app_ports, app_set_active, _domain_models, infra_contracts = _runtime_modules()
        git_gateway = _StubGitGateway(existing_branches={"iss-00302-target-issue"})
        ports = self._ports(app_ports, infra_contracts, git_gateway=git_gateway)

        result = app_set_active.set_active(
            self._request(
                app_contracts,
                target=self._node_id_target(app_contracts, "iss-00302"),
                force=True,
                checkout=True,
            ),
            ports,
        )

        self.assertEqual(result.branch.desired, "iss-00302-target-issue")
        self.assertIn(("require_clean_working_tree", None), git_gateway.calls)
        self.assertIn(("checkout_branch", "iss-00302-target-issue"), git_gateway.calls)
        self.assertNotIn(("create_and_checkout_branch", "iss-00302-target-issue"), git_gateway.calls)


if __name__ == "__main__":
    unittest.main()
