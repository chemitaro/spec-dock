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
        from spec_dock_runtime.application import contracts as app_contracts
        from spec_dock_runtime.application import ports as app_ports
        from spec_dock_runtime.application import set_active as app_set_active
        from spec_dock_runtime.infra import contracts as infra_contracts
    finally:
        sys.path.pop(0)
    return app_contracts, app_ports, app_set_active, infra_contracts


def _record(
    infra_contracts,
    *,
    kind: str,
    node_id: str,
    parent_id: str | None,
    initiative_id: str | None,
    epic_id: str | None,
    github_issue_number: int | None,
) -> object:
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=node_id,
        slug=node_id,
        path=f"/repo/spec-dock/{kind}s/{node_id}",
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=f"/repo/spec-dock/{kind}s/{node_id}/.meta.json",
    )


class _StubNodeReader:
    def __init__(self, records):
        self.records = list(records)

    def load_node_records(self):
        return list(self.records)


class _StubDepsTopologyReader:
    def __init__(self, infra_contracts, issue_depends_on_map, warnings=None):
        self._infra_contracts = infra_contracts
        self._issue_depends_on_map = dict(issue_depends_on_map)
        self._warnings = list(warnings or [])

    def load_issue_depends_on_map(self, specdock_dir, graph):
        del specdock_dir, graph
        return self._infra_contracts.DepsTopologyLoadResult(
            issue_depends_on_map=dict(self._issue_depends_on_map),
            warnings=list(self._warnings),
        )


class _StubDerivedStateReader:
    def __init__(self, statuses):
        self.statuses = dict(statuses)

    def load_cached_issue_status_by_id(self, specdock_dir):
        del specdock_dir
        return dict(self.statuses)


class _StubIssueGateway:
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return []


class _StubGitGateway:
    def __init__(self):
        self.calls = []
        self.raise_on_require_clean = None
        self.current_branch = "main"
        self.existing = set()
        self.invalid_refs = set()

    def require_clean_working_tree(self, repo_root):
        self.calls.append(("require_clean_working_tree", str(repo_root)))
        if self.raise_on_require_clean is not None:
            raise RuntimeError(self.raise_on_require_clean)

    def current_branch_or_none(self, repo_root):
        self.calls.append(("current_branch_or_none", str(repo_root)))
        return self.current_branch

    def local_branch_exists(self, repo_root, branch):
        self.calls.append(("local_branch_exists", str(repo_root), branch))
        return branch in self.existing

    def checkout_branch(self, repo_root, branch):
        self.calls.append(("checkout_branch", str(repo_root), branch))

    def create_and_checkout_branch(self, repo_root, branch):
        self.calls.append(("create_and_checkout_branch", str(repo_root), branch))

    def check_ref_format_branch(self, repo_root, branch):
        self.calls.append(("check_ref_format_branch", str(repo_root), branch))
        return branch not in self.invalid_refs


class _StubActiveStateStore:
    def __init__(self, infra_contracts):
        self._infra_contracts = infra_contracts
        self.calls = []
        self.raise_on_patch = False
        self.raise_on_restore = False
        self.last_patch_manifest = "__unset__"
        self._loaded = infra_contracts.ActiveManifestLoadResult(
            manifest=None,
            source="none",
            warnings=[],
        )

    def load_active_manifest(self, specdock_dir):
        self.calls.append(("load_active_manifest", str(specdock_dir)))
        return self._loaded

    def load_active_manifest_no_migrate(self, specdock_dir):
        self.calls.append(("load_active_manifest_no_migrate", str(specdock_dir)))
        return self._loaded

    def load_active_issue_id(self, specdock_dir):
        self.calls.append(("load_active_issue_id", str(specdock_dir)))
        return None

    def snapshot_current_state(self, specdock_dir):
        self.calls.append(("snapshot_current_state", str(specdock_dir)))
        return self._infra_contracts.ActiveStateSnapshot(
            manifest=self._loaded.manifest,
            context_pack_text="old-context",
            active_json_text=None,
            managed_agent_state={},
        )

    def write_active_manifest(self, specdock_dir, manifest):
        self.calls.append(("write_active_manifest", str(specdock_dir), manifest))
        return manifest

    def apply_active_pointers(self, specdock_dir, manifest, rendered_context_pack):
        self.calls.append(("apply_active_pointers", str(specdock_dir), manifest, rendered_context_pack))

    def patch_agent_state_active_fields(self, specdock_dir, manifest):
        self.calls.append(("patch_agent_state_active_fields", str(specdock_dir), manifest))
        self.last_patch_manifest = manifest
        if self.raise_on_patch:
            raise RuntimeError("patch failed")

    def restore_previous_state(self, specdock_dir, snapshot):
        self.calls.append(("restore_previous_state", str(specdock_dir), snapshot))
        if self.raise_on_restore:
            raise RuntimeError("restore failed")


class TestRuntimeActiveS06(unittest.TestCase):
    def _ports(self, *, issue_depends_on_map, statuses, git_gateway=None, active_state_store=None):
        app_contracts, app_ports, _app_set_active, infra_contracts = _runtime_modules()
        del app_contracts
        records = [
            _record(
                infra_contracts,
                kind="initiative",
                node_id="init-local-00001",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                kind="epic",
                node_id="epic-local-00001",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                kind="issue",
                node_id="iss-local-00001",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                kind="issue",
                node_id="iss-local-00002",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=None,
            ),
        ]
        return app_ports.Ports(
            node_reader=_StubNodeReader(records),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
            deps_topology_reader=_StubDepsTopologyReader(infra_contracts, issue_depends_on_map),
            derived_state_reader=_StubDerivedStateReader(statuses),
            issue_gateway=_StubIssueGateway(),
            git_gateway=git_gateway or _StubGitGateway(),
            active_state_store=active_state_store or _StubActiveStateStore(infra_contracts),
        )

    def test_set_active_blocked_without_force_fails_before_snapshot(self) -> None:
        app_contracts, _app_ports, app_set_active, _infra_contracts = _runtime_modules()
        ports = self._ports(
            issue_depends_on_map={"iss-local-00001": ["iss-local-00002"], "iss-local-00002": []},
            statuses={"iss-local-00001": "open", "iss-local-00002": "open"},
        )
        req = app_contracts.SetActiveRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
            force=False,
            checkout=False,
            use_github=False,
            issue_limit=10000,
        )
        with self.assertRaisesRegex(RuntimeError, "active set blocked"):
            app_set_active.set_active(req, ports)
        calls = [name for name, *_rest in ports.active_state_store.calls]
        self.assertNotIn("snapshot_current_state", calls)
        self.assertNotIn("write_active_manifest", calls)

    def test_set_active_non_issue_unknown_without_blockers_is_blocked(self) -> None:
        app_contracts, _app_ports, app_set_active, _infra_contracts = _runtime_modules()
        ports = self._ports(
            issue_depends_on_map={"iss-local-00001": [], "iss-local-00002": []},
            statuses={},
        )
        req = app_contracts.SetActiveRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="init-local-00001", github_issue_number=None),
            force=False,
            checkout=False,
            use_github=False,
            issue_limit=10000,
        )
        with self.assertRaisesRegex(RuntimeError, r"active set blocked.*guard_reason=unknown"):
            app_set_active.set_active(req, ports)
        calls = [name for name, *_rest in ports.active_state_store.calls]
        self.assertNotIn("snapshot_current_state", calls)
        self.assertNotIn("write_active_manifest", calls)

    def test_set_active_force_commits_and_order_is_authoritative(self) -> None:
        app_contracts, _app_ports, app_set_active, _infra_contracts = _runtime_modules()
        ports = self._ports(
            issue_depends_on_map={"iss-local-00001": ["iss-local-00002"], "iss-local-00002": []},
            statuses={"iss-local-00001": "open", "iss-local-00002": "open"},
        )
        req = app_contracts.SetActiveRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
            force=True,
            checkout=False,
            use_github=False,
            issue_limit=10000,
        )
        result = app_set_active.set_active(req, ports)
        self.assertTrue(result.manifest_written)
        self.assertTrue(result.pointer_updated)
        self.assertIn("deps_blocked", result.warnings[0])
        calls = [name for name, *_rest in ports.active_state_store.calls]
        self.assertEqual(
            calls[-4:],
            [
                "snapshot_current_state",
                "write_active_manifest",
                "apply_active_pointers",
                "patch_agent_state_active_fields",
            ],
        )

    def test_set_active_checkout_pre_step7_failure_has_no_rollback(self) -> None:
        app_contracts, _app_ports, app_set_active, _infra_contracts = _runtime_modules()
        git_gateway = _StubGitGateway()
        git_gateway.raise_on_require_clean = "Working tree is not clean"
        ports = self._ports(
            issue_depends_on_map={"iss-local-00001": [], "iss-local-00002": []},
            statuses={"iss-local-00001": "open", "iss-local-00002": "open"},
            git_gateway=git_gateway,
        )
        req = app_contracts.SetActiveRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
            force=True,
            checkout=True,
            use_github=False,
            issue_limit=10000,
        )
        with self.assertRaisesRegex(RuntimeError, "Working tree is not clean"):
            app_set_active.set_active(req, ports)
        calls = [name for name, *_rest in ports.active_state_store.calls]
        self.assertNotIn("snapshot_current_state", calls)
        self.assertNotIn("restore_previous_state", calls)

    def test_set_active_patch_failure_rolls_back(self) -> None:
        app_contracts, _app_ports, app_set_active, _infra_contracts = _runtime_modules()
        active_store = _StubActiveStateStore(_runtime_modules()[3])
        active_store.raise_on_patch = True
        ports = self._ports(
            issue_depends_on_map={"iss-local-00001": [], "iss-local-00002": []},
            statuses={"iss-local-00001": "open", "iss-local-00002": "done"},
            active_state_store=active_store,
        )
        req = app_contracts.SetActiveRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
            force=False,
            checkout=False,
            use_github=False,
            issue_limit=10000,
        )
        with self.assertRaisesRegex(RuntimeError, "patch failed"):
            app_set_active.set_active(req, ports)
        calls = [name for name, *_rest in active_store.calls]
        self.assertIn("restore_previous_state", calls)

    def test_clear_active_uses_patch_manifest_none(self) -> None:
        app_contracts, _app_ports, app_set_active, infra_contracts = _runtime_modules()
        active_store = _StubActiveStateStore(infra_contracts)
        active_store._loaded = infra_contracts.ActiveManifestLoadResult(
            manifest=infra_contracts.ActiveManifest(
                initiative=infra_contracts.ActiveManifestEntry("init-local-00001", "spec-dock/initiatives/init-local-00001"),
                epic=infra_contracts.ActiveManifestEntry("epic-local-00001", "spec-dock/initiatives/init-local-00001/epics/epic-local-00001"),
                issue=infra_contracts.ActiveManifestEntry(
                    "iss-local-00001",
                    "spec-dock/initiatives/init-local-00001/epics/epic-local-00001/issues/iss-local-00001",
                ),
            ),
            source="agent.active",
            warnings=[],
        )
        ports = self._ports(
            issue_depends_on_map={"iss-local-00001": [], "iss-local-00002": []},
            statuses={"iss-local-00001": "open", "iss-local-00002": "done"},
            active_state_store=active_store,
        )
        result = app_set_active.clear_active(app_contracts.ClearActiveRequest(), ports)
        self.assertTrue(result.cleared)
        self.assertEqual(result.previous.issue_id, "iss-local-00001")
        self.assertIsNone(active_store.last_patch_manifest)


if __name__ == "__main__":
    unittest.main()
