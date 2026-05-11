import contextlib
import io
import json
import shutil
import sys
import tempfile
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
        from spec_dock_runtime.application import contracts as app_contracts
        from spec_dock_runtime.application import delete_node as app_delete_node
        from spec_dock_runtime.application import ports as app_ports
        from spec_dock_runtime.cli import dispatch as cli_dispatch
        from spec_dock_runtime.cli import parser as cli_parser
        from spec_dock_runtime.cli import registry as cli_registry
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.infra import contracts as infra_contracts
    finally:
        sys.path.pop(0)
    return app_contracts, app_delete_node, app_ports, cli_dispatch, cli_parser, cli_registry, domain_models, infra_contracts


def _record(
    infra_contracts,
    *,
    repo_root: Path,
    kind: str,
    node_id: str,
    parent_id: str | None,
    initiative_id: str | None,
    epic_id: str | None,
    github_issue_number: int | None,
    github_repo_owner: str | None = None,
    github_repo_name: str | None = None,
    initiative_node_id: str = "init-local-00001",
    epic_node_id: str = "epic-local-00001",
) -> object:
    if kind == "initiative":
        node_dir = repo_root / "spec-dock" / "initiatives" / f"{node_id}-title"
    elif kind == "epic":
        node_dir = (
            repo_root
            / "spec-dock"
            / "initiatives"
            / f"{initiative_node_id}-title"
            / "epics"
            / f"{node_id}-title"
        )
    else:
        node_dir = (
            repo_root
            / "spec-dock"
            / "initiatives"
            / f"{initiative_node_id}-title"
            / "epics"
            / f"{epic_node_id}-title"
            / "issues"
            / f"{node_id}-title"
        )
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=node_id,
        slug="title",
        path=node_dir.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(node_dir / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )


def _issue_snapshot(domain_models, *, issue_number: int, state: str, owner: str, repo: str):
    return domain_models.IssueSnapshot(
        issue_number=issue_number,
        state=state,
        title=f"Issue {issue_number}",
        labels=[],
        updated_at="2026-04-09T00:00:00Z",
        url=f"https://github.com/{owner}/{repo}/issues/{issue_number}",
        repo_owner=owner,
        repo_name=repo,
    )


class _StubNodeReader:
    def __init__(self, records):
        self._records = list(records)

    def load_node_records(self):
        return list(self._records)


class _RaisingNodeReader:
    def __init__(self, message: str):
        self._message = message

    def load_node_records(self):
        raise RuntimeError(self._message)


class _StubDepsTopologyReader:
    def __init__(self, infra_contracts, dep_map):
        self._infra_contracts = infra_contracts
        self._dep_map = dict(dep_map)

    def load_issue_depends_on_map(self, specdock_dir, graph):
        del specdock_dir, graph
        return self._infra_contracts.DepsTopologyLoadResult(issue_depends_on_map=dict(self._dep_map), warnings=[])


class _FailingDepsTopologyReader:
    def __init__(self, message: str):
        self._message = message

    def load_issue_depends_on_map(self, specdock_dir, graph):
        del specdock_dir, graph
        raise RuntimeError(self._message)


class _StubIssueGateway:
    def __init__(self, *, domain_models, view_states=None, close_failures=None):
        self._domain_models = domain_models
        self._view_states = dict(view_states or {})
        self._close_failures = set(close_failures or set())
        self.view_calls = []
        self.close_calls = []

    def issue_view_snapshot(self, repo_root, issue_number, *, repo_slug=None):
        slug = str(repo_slug or "").strip().lower()
        number = int(issue_number)
        self.view_calls.append((str(repo_root), slug, number))
        state = self._view_states.get((slug, number), "OPEN")
        owner, _sep, repo = slug.partition("/")
        return _issue_snapshot(
            self._domain_models,
            issue_number=number,
            state=state,
            owner=owner or "example",
            repo=repo or "repo",
        )

    def issue_close(self, repo_root, issue_number, *, repo_slug=None):
        slug = str(repo_slug or "").strip().lower()
        number = int(issue_number)
        self.close_calls.append((str(repo_root), slug, number))
        key = (slug, number)
        if key in self._close_failures:
            raise RuntimeError(f"close failed: {slug}#{number}")
        self._view_states[key] = "CLOSED"
        owner, _sep, repo = slug.partition("/")
        return _issue_snapshot(
            self._domain_models,
            issue_number=number,
            state="CLOSED",
            owner=owner or "example",
            repo=repo or "repo",
        )


class _StubActiveStateStore:
    def __init__(self, infra_contracts, manifest):
        self._infra_contracts = infra_contracts
        self._manifest = manifest
        self.calls = []

    def load_active_manifest(self, specdock_dir):
        self.calls.append(("load_active_manifest", str(specdock_dir)))
        del specdock_dir
        return self._infra_contracts.ActiveManifestLoadResult(
            manifest=self._manifest,
            source="agent.active",
            warnings=[],
        )

    def load_active_manifest_no_migrate(self, specdock_dir):
        return self.load_active_manifest(specdock_dir)

    def load_active_issue_id(self, specdock_dir):
        del specdock_dir
        if self._manifest is None or self._manifest.issue is None:
            return None
        return self._manifest.issue.id

    def write_active_manifest(self, specdock_dir, manifest):
        self.calls.append(("write_active_manifest", str(specdock_dir), manifest))
        self._manifest = manifest
        return manifest

    def apply_active_pointers(self, specdock_dir, manifest, rendered_context_pack):
        self.calls.append(("apply_active_pointers", str(specdock_dir), manifest, rendered_context_pack))

    def patch_agent_state_active_fields(self, specdock_dir, manifest):
        self.calls.append(("patch_agent_state_active_fields", str(specdock_dir), manifest))

    def snapshot_current_state(self, specdock_dir):
        self.calls.append(("snapshot_current_state", str(specdock_dir)))
        return self._infra_contracts.ActiveStateSnapshot(
            manifest=self._manifest,
            context_pack_text="snapshot",
            active_json_text=None,
            managed_agent_state={},
        )

    def restore_previous_state(self, specdock_dir, snapshot):
        self.calls.append(("restore_previous_state", str(specdock_dir), snapshot))


class _StubNodeRepository:
    def __init__(self):
        self.delete_calls = []

    def remove_issue_dependency(self, meta_path, to_id, *, matching_refs=None):
        meta_file = Path(meta_path)
        payload = json.loads(meta_file.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise RuntimeError(f"Invalid .meta.json (expected object): {meta_file}")
        depends_on_raw = payload.get("depends_on")
        if depends_on_raw is None:
            depends_on = []
        elif isinstance(depends_on_raw, list):
            depends_on = list(depends_on_raw)
        else:
            raise RuntimeError(f"Invalid .meta.json schema: {meta_file}: depends_on must be a list")
        to_id_text = str(to_id)
        matching_ref_values = list(matching_refs or [])
        payload["depends_on"] = [
            dep
            for dep in depends_on
            if str(dep) != to_id_text and not any(dep == ref for ref in matching_ref_values)
        ]
        meta_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def delete_tree(self, node_path):
        self.delete_calls.append(str(node_path))


class _DeletingNodeRepository(_StubNodeRepository):
    def delete_tree(self, node_path):
        super().delete_tree(node_path)
        path = Path(node_path)
        if path.exists():
            shutil.rmtree(path)


class TestRuntimeDeleteS13(unittest.TestCase):
    def _new_repo_root(self) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        return Path(temp_dir.name)

    def _records(self, infra_contracts, repo_root: Path, *, with_github_links: bool = False):
        github_owner = "example" if with_github_links else None
        github_repo = "repo" if with_github_links else None
        init_issue_number = 11 if with_github_links else None
        epic_issue_number = 22 if with_github_links else None
        issue_56_number = 56 if with_github_links else None
        issue_57_number = 57 if with_github_links else None
        return [
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="initiative",
                node_id="init-local-00001",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=init_issue_number,
                github_repo_owner=github_owner,
                github_repo_name=github_repo,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00001",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=epic_issue_number,
                github_repo_owner=github_owner,
                github_repo_name=github_repo,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00056",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=issue_56_number,
                github_repo_owner=github_owner,
                github_repo_name=github_repo,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00057",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=issue_57_number,
                github_repo_owner=github_owner,
                github_repo_name=github_repo,
            ),
        ]

    def _ports(
        self,
        *,
        records,
        dep_map=None,
        deps_topology_reader=None,
        active_manifest=None,
        repo_root=None,
        issue_gateway=None,
        node_repo=None,
        active_state_store=None,
        node_reader=None,
    ):
        app_contracts, _app_delete_node, app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        del app_contracts
        if repo_root is None:
            repo_root = Path("/repo")
        for record in records:
            Path(record.path).mkdir(parents=True, exist_ok=True)
            Path(record.meta_path).write_text("{}", encoding="utf-8")
        resolved_deps_topology_reader = deps_topology_reader or _StubDepsTopologyReader(
            infra_contracts,
            dep_map or {},
        )
        return app_ports.Ports(
            node_reader=node_reader or _StubNodeReader(records),
            repo_root=repo_root,
            specdock_dir=repo_root / "spec-dock",
            deps_topology_reader=resolved_deps_topology_reader,
            active_state_store=active_state_store or _StubActiveStateStore(infra_contracts, active_manifest),
            issue_gateway=issue_gateway,
            node_repo=node_repo,
        )

    def _request(self, app_contracts, **overrides):
        payload = {
            "positional_target": None,
            "node_id": None,
            "github_issue": None,
            "recursive": False,
            "force": False,
            "confirmed": False,
            "json_output": False,
        }
        payload.update(overrides)
        return app_contracts.DeleteNodeRequest(**payload)

    def test_selector_missing_returns_invalid_selector_combination(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        ports = self._ports(records=self._records(infra_contracts, repo_root), repo_root=repo_root)
        result = app_delete_node.delete_node(self._request(app_contracts), ports)
        self.assertEqual(result.status, "invalid_selector_combination")

    def test_selector_multiple_returns_invalid_selector_combination(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        ports = self._ports(records=self._records(infra_contracts, repo_root), repo_root=repo_root)
        result = app_delete_node.delete_node(
            self._request(app_contracts, positional_target="iss-local-00056", node_id="iss-local-00056"),
            ports,
        )
        self.assertEqual(result.status, "invalid_selector_combination")

    def test_malformed_github_issue_returns_invalid_selector_syntax(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        ports = self._ports(records=self._records(infra_contracts, repo_root), repo_root=repo_root)
        result = app_delete_node.delete_node(self._request(app_contracts, github_issue="#56"), ports)
        self.assertEqual(result.status, "invalid_selector_syntax")

    def test_node_id_exact_match_resolve(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root_pos = self._new_repo_root()
        ports_pos = self._ports(records=self._records(infra_contracts, repo_root_pos), repo_root=repo_root_pos)
        result_pos = app_delete_node.delete_node(
            self._request(app_contracts, positional_target="iss-local-00056", confirmed=True),
            ports_pos,
        )
        self.assertEqual(result_pos.status, "ok")
        self.assertEqual(result_pos.target_id, "iss-local-00056")
        self.assertEqual(result_pos.deleted_node_ids, ["iss-local-00056"])
        self.assertEqual(result_pos.remaining_node_ids, [])

        repo_root_id = self._new_repo_root()
        ports_id = self._ports(records=self._records(infra_contracts, repo_root_id), repo_root=repo_root_id)
        result_id = app_delete_node.delete_node(
            self._request(app_contracts, node_id="iss-local-00056", confirmed=True),
            ports_id,
        )
        self.assertEqual(result_id.status, "ok")
        self.assertEqual(result_id.target_id, "iss-local-00056")
        self.assertEqual(result_id.deleted_node_ids, ["iss-local-00056"])
        self.assertEqual(result_id.remaining_node_ids, [])

    def test_github_issue_selector_is_normalized(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = self._records(infra_contracts, repo_root, with_github_links=True)
        issue_gateway = _StubIssueGateway(
            domain_models=domain_models,
            view_states={("example/repo", 56): "OPEN"},
        )
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            issue_gateway=issue_gateway,
        )
        result = app_delete_node.delete_node(
            self._request(app_contracts, github_issue="00056", confirmed=True),
            ports,
        )
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.target_id, "iss-local-00056")
        self.assertEqual(result.deleted_node_ids, ["iss-local-00056"])
        self.assertEqual(result.remaining_node_ids, [])
        self.assertFalse(Path(records[2].path).exists())
        self.assertEqual(issue_gateway.close_calls, [(str(repo_root), "example/repo", 56)])

    def test_ambiguous_target_for_github_issue(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = self._records(infra_contracts, repo_root, with_github_links=True) + [
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00002",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=56,
                github_repo_owner="example",
                github_repo_name="repo",
            )
        ]
        ports = self._ports(records=records, repo_root=repo_root)
        result = app_delete_node.delete_node(self._request(app_contracts, github_issue="56", confirmed=True), ports)
        self.assertEqual(result.status, "ambiguous_target")
        self.assertIn("epic-local-00002", result.offending_node_ids)
        self.assertIn("iss-local-00056", result.offending_node_ids)

    def test_unrelated_invalid_id_record_is_ignored(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = self._records(infra_contracts, repo_root) + [
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="not-a-canonical-id",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=99,
            )
        ]
        ports = self._ports(records=records, repo_root=repo_root)
        result = app_delete_node.delete_node(
            self._request(app_contracts, node_id="iss-local-00056", confirmed=True),
            ports,
        )
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.target_id, "iss-local-00056")
        self.assertEqual(result.deleted_node_ids, ["iss-local-00056"])
        self.assertEqual(result.remaining_node_ids, [])

    def test_preflight_precedence_confirmation_before_recursive_active_deps(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        manifest = infra_contracts.ActiveManifest(
            initiative=infra_contracts.ActiveManifestEntry(id="init-local-00001", path="spec-dock/initiatives/x"),
            epic=None,
            issue=None,
        )
        repo_root = self._new_repo_root()
        ports = self._ports(
            records=self._records(infra_contracts, repo_root),
            dep_map={"iss-local-00056": ["iss-local-00057"], "iss-local-00057": []},
            active_manifest=manifest,
            repo_root=repo_root,
        )
        result = app_delete_node.delete_node(
            self._request(app_contracts, node_id="init-local-00001", confirmed=False, recursive=False),
            ports,
        )
        self.assertEqual(result.status, "confirmation_required")

    def test_active_conflict(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        manifest = infra_contracts.ActiveManifest(
            initiative=None,
            epic=None,
            issue=infra_contracts.ActiveManifestEntry(id="iss-local-00056", path="spec-dock/initiatives/x"),
        )
        repo_root = self._new_repo_root()
        ports = self._ports(
            records=self._records(infra_contracts, repo_root),
            active_manifest=manifest,
            repo_root=repo_root,
        )
        result = app_delete_node.delete_node(
            self._request(app_contracts, node_id="iss-local-00056", confirmed=True),
            ports,
        )
        self.assertEqual(result.status, "active_conflict")

    def test_dependency_conflict(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        ports = self._ports(
            records=self._records(infra_contracts, repo_root),
            dep_map={"iss-local-00056": ["iss-local-00057"], "iss-local-00057": []},
            repo_root=repo_root,
        )
        result = app_delete_node.delete_node(
            self._request(app_contracts, node_id="iss-local-00056", confirmed=True),
            ports,
        )
        self.assertEqual(result.status, "dependency_conflict")

    def test_dependency_topology_load_failure_returns_metadata_validation_failed_and_skips_local_delete(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = self._records(infra_contracts, repo_root, with_github_links=True)
        node_repo = _StubNodeRepository()
        issue_gateway = _StubIssueGateway(
            domain_models=domain_models,
            view_states={("example/repo", 56): "OPEN"},
        )
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            issue_gateway=issue_gateway,
            node_repo=node_repo,
            deps_topology_reader=_FailingDepsTopologyReader("deps topology broken"),
        )

        result = app_delete_node.delete_node(
            self._request(
                app_contracts,
                node_id="iss-local-00056",
                confirmed=True,
                force=True,
            ),
            ports,
        )

        self.assertEqual(result.status, "metadata_validation_failed")
        self.assertEqual(result.target_id, "iss-local-00056")
        self.assertEqual(result.deleted_node_ids, [])
        self.assertEqual(result.remaining_node_ids, [])
        self.assertEqual(result.offending_node_ids, [])
        self.assertEqual([item.code for item in result.validation_reasons], ["metadata_validation_failed"])
        self.assertEqual(result.validation_reasons[0].node_id, "iss-local-00056")
        self.assertIn("deps topology broken", result.validation_reasons[0].message)
        self.assertIsNotNone(result.remote_close)
        assert result.remote_close is not None
        self.assertEqual(result.remote_close.closed, [])
        self.assertEqual(result.remote_close.noop_already_closed, [])
        self.assertEqual(result.remote_close.failed, [])
        self.assertEqual(result.remote_close.skipped_not_attempted, [])
        self.assertEqual(issue_gateway.close_calls, [])
        self.assertEqual(node_repo.delete_calls, [])
        self.assertTrue(Path(records[2].path).exists())

    def test_parent_dependency_conflict_without_force_stops_before_local_delete_mutation(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = [
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="initiative",
                node_id="init-local-00001",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00001",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00056",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00002",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00058",
                parent_id="epic-local-00002",
                initiative_id="init-local-00001",
                epic_id="epic-local-00002",
                github_issue_number=None,
                initiative_node_id="init-local-00001",
                epic_node_id="epic-local-00002",
            ),
        ]
        node_repo = _StubNodeRepository()
        ports = self._ports(
            records=records,
            dep_map={"iss-local-00058": ["iss-local-00056"]},
            repo_root=repo_root,
            node_repo=node_repo,
        )

        result = app_delete_node.delete_node(
            self._request(
                app_contracts,
                node_id="epic-local-00001",
                confirmed=True,
                recursive=True,
            ),
            ports,
        )

        self.assertEqual(result.status, "dependency_conflict")
        self.assertEqual(result.target_id, "epic-local-00001")
        self.assertEqual(result.deleted_node_ids, [])
        self.assertEqual(result.remaining_node_ids, [])
        self.assertEqual([item.code for item in result.validation_reasons], ["dependency_conflict"])
        self.assertEqual(node_repo.delete_calls, [])
        self.assertTrue(Path(records[1].path).exists())
        self.assertTrue(Path(records[2].path).exists())
        self.assertTrue(Path(records[3].path).exists())
        self.assertTrue(Path(records[4].path).exists())
        active_calls = [call[0] for call in ports.active_state_store.calls]
        self.assertNotIn("snapshot_current_state", active_calls)

    def test_subtree_internal_dependency_is_not_conflict(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        ports = self._ports(
            records=self._records(infra_contracts, repo_root),
            dep_map={"iss-local-00056": ["iss-local-00057"], "iss-local-00057": []},
            repo_root=repo_root,
        )
        result = app_delete_node.delete_node(
            self._request(
                app_contracts,
                node_id="epic-local-00001",
                confirmed=True,
                recursive=True,
                force=True,
            ),
            ports,
        )
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.target_id, "epic-local-00001")
        self.assertEqual(result.deleted_node_ids, ["iss-local-00056", "iss-local-00057", "epic-local-00001"])
        self.assertEqual(result.remaining_node_ids, [])
        self.assertIsNotNone(result.remote_close)
        assert result.remote_close is not None
        self.assertEqual(result.remote_close.closed, [])
        self.assertEqual(result.remote_close.noop_already_closed, [])
        self.assertEqual(result.remote_close.failed, [])
        self.assertEqual(result.remote_close.skipped_not_attempted, [])

    def test_missing_recursive_for_parent(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        ports = self._ports(records=self._records(infra_contracts, repo_root), repo_root=repo_root)
        result = app_delete_node.delete_node(
            self._request(app_contracts, node_id="epic-local-00001", confirmed=True),
            ports,
        )
        self.assertEqual(result.status, "recursive_required")

    def test_missing_target_path(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = self._records(infra_contracts, repo_root)
        ports = self._ports(records=records, repo_root=repo_root)
        shutil.rmtree(Path(records[2].path))
        result = app_delete_node.delete_node(
            self._request(app_contracts, node_id="iss-local-00056", confirmed=True),
            ports,
        )
        self.assertEqual(result.status, "target_not_found")

    def test_missing_yes(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        ports = self._ports(records=self._records(infra_contracts, repo_root), repo_root=repo_root)
        result = app_delete_node.delete_node(self._request(app_contracts, node_id="iss-local-00056"), ports)
        self.assertEqual(result.status, "confirmation_required")

    def test_force_does_not_override_missing_target_recursive_yes(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        ports = self._ports(records=self._records(infra_contracts, repo_root), repo_root=repo_root)

        result_missing_target = app_delete_node.delete_node(
            self._request(app_contracts, node_id="iss-local-99999", confirmed=True, force=True),
            ports,
        )
        self.assertEqual(result_missing_target.status, "target_not_found")

        result_missing_recursive = app_delete_node.delete_node(
            self._request(app_contracts, node_id="epic-local-00001", confirmed=True, force=True),
            ports,
        )
        self.assertEqual(result_missing_recursive.status, "recursive_required")

        result_missing_yes = app_delete_node.delete_node(
            self._request(app_contracts, node_id="iss-local-00056", force=True, confirmed=False),
            ports,
        )
        self.assertEqual(result_missing_yes.status, "confirmation_required")

    def test_force_positive_path_overrides_active_and_dependency_conflict(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        manifest = infra_contracts.ActiveManifest(
            initiative=None,
            epic=None,
            issue=infra_contracts.ActiveManifestEntry(id="iss-local-00056", path="spec-dock/initiatives/x"),
        )
        repo_root = self._new_repo_root()
        ports = self._ports(
            records=self._records(infra_contracts, repo_root),
            dep_map={"iss-local-00056": ["iss-local-00057"], "iss-local-00057": []},
            active_manifest=manifest,
            repo_root=repo_root,
        )
        result = app_delete_node.delete_node(
            self._request(app_contracts, node_id="iss-local-00056", force=True, confirmed=True),
            ports,
        )
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.target_id, "iss-local-00056")
        self.assertEqual(result.deleted_node_ids, ["iss-local-00056"])
        self.assertEqual(result.remaining_node_ids, [])

    def test_issue_recursive_flag_is_accepted_noop(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        ports = self._ports(records=self._records(infra_contracts, repo_root), repo_root=repo_root)
        result = app_delete_node.delete_node(
            self._request(app_contracts, node_id="iss-local-00056", recursive=True, confirmed=True),
            ports,
        )
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.deleted_node_ids, ["iss-local-00056"])
        self.assertEqual(result.remaining_node_ids, [])

    def test_would_match_target_invalid_metadata_returns_metadata_validation_failed(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = self._records(infra_contracts, repo_root)
        ports = self._ports(records=records, repo_root=repo_root)
        Path(records[2].meta_path).unlink()
        result = app_delete_node.delete_node(
            self._request(app_contracts, node_id="iss-local-00056", confirmed=True),
            ports,
        )
        self.assertEqual(result.status, "metadata_validation_failed")
        self.assertEqual(result.target_id, "iss-local-00056")
        self.assertEqual(result.offending_node_ids, ["iss-local-00056"])
        self.assertIsNotNone(result.remote_close)
        assert result.remote_close is not None
        self.assertEqual(result.remote_close.closed, [])
        self.assertEqual(result.remote_close.noop_already_closed, [])
        self.assertEqual(result.remote_close.failed, [])
        self.assertEqual(result.remote_close.skipped_not_attempted, [])

    def test_target_local_metadata_load_failure_is_normalized_before_graph_build(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = self._records(infra_contracts, repo_root)
        target_meta_path = Path(records[2].meta_path)
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            node_reader=_RaisingNodeReader(f"Invalid JSON: {target_meta_path}: broken payload"),
        )
        target_meta_path.parent.mkdir(parents=True, exist_ok=True)
        target_meta_path.write_text("{invalid-json", encoding="utf-8")
        result = app_delete_node.delete_node(
            self._request(app_contracts, node_id="iss-local-00056", confirmed=True),
            ports,
        )
        self.assertEqual(result.status, "metadata_validation_failed")
        self.assertEqual(result.target_id, "iss-local-00056")
        self.assertEqual(result.offending_node_ids, ["iss-local-00056"])
        self.assertEqual(
            [(reason.node_id, reason.code) for reason in result.validation_reasons],
            [("iss-local-00056", "metadata_validation_failed")],
        )
        assert result.remote_close is not None
        self.assertEqual(result.remote_close.closed, [])
        self.assertEqual(result.remote_close.noop_already_closed, [])
        self.assertEqual(result.remote_close.failed, [])
        self.assertEqual(result.remote_close.skipped_not_attempted, [])

    def test_target_local_metadata_load_failure_uses_error_path_when_directory_match_is_ambiguous(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = self._records(infra_contracts, repo_root)
        ports = self._ports(records=records, repo_root=repo_root)
        target_meta_path = Path(records[2].meta_path)
        target_meta_path.parent.mkdir(parents=True, exist_ok=True)
        target_meta_path.write_text("{invalid-json", encoding="utf-8")
        duplicate_dir = target_meta_path.parent.parent / f"{records[2].id}-shadow"
        duplicate_dir.mkdir(parents=True, exist_ok=True)
        (duplicate_dir / ".meta.json").write_text("{}\n", encoding="utf-8")
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            node_reader=_RaisingNodeReader(f"Invalid JSON: {target_meta_path}: broken payload"),
        )
        target_meta_path.write_text("{invalid-json", encoding="utf-8")

        result = app_delete_node.delete_node(
            self._request(app_contracts, node_id="iss-local-00056", confirmed=True),
            ports,
        )
        self.assertEqual(result.status, "metadata_validation_failed")
        self.assertEqual(result.target_id, "iss-local-00056")
        self.assertEqual(result.offending_node_ids, ["iss-local-00056"])
        self.assertEqual(
            [(reason.node_id, reason.code) for reason in result.validation_reasons],
            [("iss-local-00056", "metadata_validation_failed")],
        )
        assert result.remote_close is not None
        self.assertEqual(result.remote_close.closed, [])
        self.assertEqual(result.remote_close.noop_already_closed, [])
        self.assertEqual(result.remote_close.failed, [])
        self.assertEqual(result.remote_close.skipped_not_attempted, [])

    def test_target_local_metadata_load_failure_ignores_non_canonical_duplicate_like_directory(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = self._records(infra_contracts, repo_root)
        target_meta_path = Path(records[2].meta_path)
        target_meta_path.parent.mkdir(parents=True, exist_ok=True)
        target_meta_path.write_text("{invalid-json", encoding="utf-8")
        non_canonical_dir = (
            repo_root
            / "spec-dock"
            / "initiatives"
            / "stale-sandbox"
            / "issues"
            / f"{records[2].id}-shadow"
        )
        non_canonical_dir.mkdir(parents=True, exist_ok=True)
        (non_canonical_dir / ".meta.json").write_text("{}\n", encoding="utf-8")
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            node_reader=_RaisingNodeReader("load node records failed"),
        )
        target_meta_path.write_text("{invalid-json", encoding="utf-8")

        result = app_delete_node.delete_node(
            self._request(app_contracts, node_id="iss-local-00056", confirmed=True),
            ports,
        )
        self.assertEqual(result.status, "metadata_validation_failed")
        self.assertEqual(result.target_id, "iss-local-00056")
        self.assertEqual(result.offending_node_ids, ["iss-local-00056"])
        self.assertEqual(
            [(reason.node_id, reason.code) for reason in result.validation_reasons],
            [("iss-local-00056", "metadata_validation_failed")],
        )
        assert result.remote_close is not None
        self.assertEqual(result.remote_close.closed, [])
        self.assertEqual(result.remote_close.noop_already_closed, [])
        self.assertEqual(result.remote_close.failed, [])
        self.assertEqual(result.remote_close.skipped_not_attempted, [])

    def test_parent_recursive_delete_fails_with_subtree_metadata_validation_errors(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = [
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="initiative",
                node_id="init-local-00001",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00001",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00056",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=56,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00057",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=57,
            ),
        ]
        records[2] = infra_contracts.StoredMetaRecord(
            kind=records[2].kind,
            id=records[2].id,
            title=records[2].title,
            slug=records[2].slug,
            path=records[2].path,
            parent_id=records[2].parent_id,
            initiative_id=records[2].initiative_id,
            epic_id=records[2].epic_id,
            github_issue_number=records[2].github_issue_number,
            meta_path=records[2].meta_path,
            github_repo_owner="example",
            github_repo_name=None,
        )
        records[3] = infra_contracts.StoredMetaRecord(
            kind=records[3].kind,
            id=records[3].id,
            title=records[3].title,
            slug=records[3].slug,
            path=records[3].path,
            parent_id=records[3].parent_id,
            initiative_id=records[3].initiative_id,
            epic_id=records[3].epic_id,
            github_issue_number=0,
            meta_path=records[3].meta_path,
            github_repo_owner="example",
            github_repo_name="repo",
        )
        ports = self._ports(records=records, repo_root=repo_root)
        result = app_delete_node.delete_node(
            self._request(
                app_contracts,
                node_id="epic-local-00001",
                confirmed=True,
                recursive=True,
            ),
            ports,
        )
        self.assertEqual(result.status, "metadata_validation_failed")
        self.assertEqual(result.target_id, "epic-local-00001")
        self.assertEqual(result.offending_node_ids, ["iss-local-00056", "iss-local-00057"])
        self.assertEqual([reason.node_id for reason in result.validation_reasons], ["iss-local-00056", "iss-local-00057"])
        self.assertIsNotNone(result.remote_close)
        assert result.remote_close is not None
        self.assertEqual(result.remote_close.closed, [])
        self.assertEqual(result.remote_close.noop_already_closed, [])
        self.assertEqual(result.remote_close.failed, [])
        self.assertEqual(result.remote_close.skipped_not_attempted, [])

    def test_parent_recursive_delete_aborts_local_delete_when_remote_close_barrier_fails(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = [
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="initiative",
                node_id="init-local-00001",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=2,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00001",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=3,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00056",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=3,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00057",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=1,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00058",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=9,
            ),
        ]
        records[0] = infra_contracts.StoredMetaRecord(**{**records[0].__dict__, "github_repo_owner": "alpha", "github_repo_name": "repo"})
        records[1] = infra_contracts.StoredMetaRecord(**{**records[1].__dict__, "github_repo_owner": "alpha", "github_repo_name": "repo"})
        records[2] = infra_contracts.StoredMetaRecord(**{**records[2].__dict__, "github_repo_owner": "alpha", "github_repo_name": "repo"})
        records[3] = infra_contracts.StoredMetaRecord(**{**records[3].__dict__, "github_repo_owner": "beta", "github_repo_name": "repo"})
        records[4] = infra_contracts.StoredMetaRecord(**{**records[4].__dict__, "github_repo_owner": "gamma", "github_repo_name": "repo"})
        issue_gateway = _StubIssueGateway(
            domain_models=domain_models,
            view_states={
                ("alpha/repo", 2): "CLOSED",
                ("alpha/repo", 3): "OPEN",
                ("beta/repo", 1): "OPEN",
                ("gamma/repo", 9): "OPEN",
            },
            close_failures={("beta/repo", 1)},
        )
        node_repo = _StubNodeRepository()
        active_store = _StubActiveStateStore(infra_contracts, manifest=None)
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            issue_gateway=issue_gateway,
            node_repo=node_repo,
            active_state_store=active_store,
        )
        result = app_delete_node.delete_node(
            self._request(
                app_contracts,
                node_id="init-local-00001",
                confirmed=True,
                recursive=True,
            ),
            ports,
        )
        self.assertEqual(result.status, "remote_close_failed")
        self.assertEqual(result.target_id, "init-local-00001")
        self.assertEqual(result.deleted_node_ids, [])
        self.assertIsNotNone(result.remote_close)
        assert result.remote_close is not None
        self.assertEqual(result.remote_close.closed, ["alpha/repo#3"])
        self.assertEqual(result.remote_close.noop_already_closed, ["alpha/repo#2"])
        self.assertEqual(result.remote_close.failed, ["beta/repo#1"])
        self.assertEqual(result.remote_close.skipped_not_attempted, ["gamma/repo#9"])
        self.assertEqual(
            issue_gateway.view_calls,
            [
                (str(repo_root), "alpha/repo", 2),
                (str(repo_root), "alpha/repo", 3),
                (str(repo_root), "beta/repo", 1),
            ],
        )
        self.assertEqual(
            issue_gateway.close_calls,
            [
                (str(repo_root), "alpha/repo", 3),
                (str(repo_root), "beta/repo", 1),
            ],
        )
        self.assertEqual(node_repo.delete_calls, [])
        self.assertIn(("load_active_manifest", str(repo_root / "spec-dock")), active_store.calls)

    def test_all_required_remote_closes_succeed_before_local_delete_starts(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = self._records(infra_contracts, repo_root, with_github_links=True)
        records[0] = infra_contracts.StoredMetaRecord(**{**records[0].__dict__, "github_repo_owner": "zeta", "github_repo_name": "repo"})
        records[1] = infra_contracts.StoredMetaRecord(**{**records[1].__dict__, "github_repo_owner": "alpha", "github_repo_name": "repo"})
        records[2] = infra_contracts.StoredMetaRecord(**{**records[2].__dict__, "github_repo_owner": "alpha", "github_repo_name": "repo"})
        records[3] = infra_contracts.StoredMetaRecord(**{**records[3].__dict__, "github_repo_owner": "beta", "github_repo_name": "repo"})
        events: list[str] = []

        class _EventIssueGateway(_StubIssueGateway):
            def issue_view_snapshot(self, repo_root, issue_number, *, repo_slug=None):
                slug = str(repo_slug or "").strip().lower()
                events.append(f"view:{slug}#{int(issue_number)}")
                return super().issue_view_snapshot(repo_root, issue_number, repo_slug=repo_slug)

            def issue_close(self, repo_root, issue_number, *, repo_slug=None):
                slug = str(repo_slug or "").strip().lower()
                events.append(f"close:{slug}#{int(issue_number)}")
                return super().issue_close(repo_root, issue_number, repo_slug=repo_slug)

        class _EventDeletingNodeRepo(_DeletingNodeRepository):
            def delete_tree(self, node_path):
                events.append(f"delete:{Path(node_path).name}")
                super().delete_tree(node_path)

        issue_gateway = _EventIssueGateway(
            domain_models=domain_models,
            view_states={
                ("alpha/repo", 22): "OPEN",
                ("alpha/repo", 56): "OPEN",
                ("beta/repo", 57): "OPEN",
                ("zeta/repo", 11): "OPEN",
            },
        )
        node_repo = _EventDeletingNodeRepo()
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            issue_gateway=issue_gateway,
            node_repo=node_repo,
        )
        result = app_delete_node.delete_node(
            self._request(
                app_contracts,
                node_id="init-local-00001",
                confirmed=True,
                recursive=True,
            ),
            ports,
        )
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.target_id, "init-local-00001")
        self.assertEqual(
            result.deleted_node_ids,
            ["iss-local-00056", "iss-local-00057", "epic-local-00001", "init-local-00001"],
        )
        self.assertEqual(result.remaining_node_ids, [])
        self.assertEqual(
            issue_gateway.close_calls,
            [
                (str(repo_root), "alpha/repo", 22),
                (str(repo_root), "alpha/repo", 56),
                (str(repo_root), "beta/repo", 57),
                (str(repo_root), "zeta/repo", 11),
            ],
        )
        close_events = [event for event in events if event.startswith("close:")]
        delete_events = [event for event in events if event.startswith("delete:")]
        self.assertEqual(
            close_events,
            [
                "close:alpha/repo#22",
                "close:alpha/repo#56",
                "close:beta/repo#57",
                "close:zeta/repo#11",
            ],
        )
        self.assertEqual(
            delete_events,
            [
                "delete:iss-local-00056-title",
                "delete:iss-local-00057-title",
                "delete:epic-local-00001-title",
                "delete:init-local-00001-title",
            ],
        )
        first_delete_index = events.index(delete_events[0])
        last_close_index = max(events.index(event) for event in close_events)
        self.assertGreater(first_delete_index, last_close_index)

    def test_recursive_epic_delete_succeeds_with_remote_close_barrier(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = self._records(infra_contracts, repo_root, with_github_links=True)
        issue_gateway = _StubIssueGateway(
            domain_models=domain_models,
            view_states={
                ("example/repo", 22): "OPEN",
                ("example/repo", 56): "OPEN",
                ("example/repo", 57): "OPEN",
            },
        )
        node_repo = _DeletingNodeRepository()
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            issue_gateway=issue_gateway,
            node_repo=node_repo,
        )
        result = app_delete_node.delete_node(
            self._request(
                app_contracts,
                node_id="epic-local-00001",
                confirmed=True,
                recursive=True,
            ),
            ports,
        )

        self.assertEqual(result.status, "ok")
        self.assertEqual(result.target_id, "epic-local-00001")
        self.assertEqual(result.deleted_node_ids, ["iss-local-00056", "iss-local-00057", "epic-local-00001"])
        self.assertEqual(result.remaining_node_ids, [])
        self.assertEqual(
            issue_gateway.close_calls,
            [
                (str(repo_root), "example/repo", 22),
                (str(repo_root), "example/repo", 56),
                (str(repo_root), "example/repo", 57),
            ],
        )
        self.assertFalse(Path(records[1].path).exists())
        self.assertFalse(Path(records[2].path).exists())
        self.assertFalse(Path(records[3].path).exists())
        self.assertTrue(Path(records[0].path).exists())

    def test_recursive_delete_order_is_deepest_first_and_same_depth_lexical(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = [
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="initiative",
                node_id="init-local-00001",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00020",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00010",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00090",
                parent_id="epic-local-00020",
                initiative_id="init-local-00001",
                epic_id="epic-local-00020",
                github_issue_number=None,
                initiative_node_id="init-local-00001",
                epic_node_id="epic-local-00020",
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00080",
                parent_id="epic-local-00010",
                initiative_id="init-local-00001",
                epic_id="epic-local-00010",
                github_issue_number=None,
                initiative_node_id="init-local-00001",
                epic_node_id="epic-local-00010",
            ),
        ]
        node_repo = _DeletingNodeRepository()
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            node_repo=node_repo,
        )
        result = app_delete_node.delete_node(
            self._request(
                app_contracts,
                node_id="init-local-00001",
                confirmed=True,
                recursive=True,
            ),
            ports,
        )

        self.assertEqual(result.status, "ok")
        self.assertEqual(
            result.deleted_node_ids,
            [
                "iss-local-00080",
                "iss-local-00090",
                "epic-local-00010",
                "epic-local-00020",
                "init-local-00001",
            ],
        )
        self.assertEqual(result.remaining_node_ids, [])

    def test_parent_recursive_local_delete_partial_failure_reports_progress(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = self._records(infra_contracts, repo_root)

        class _FailOnParentDeleteRepo(_StubNodeRepository):
            def delete_tree(self, node_path):
                super().delete_tree(node_path)
                path = Path(node_path)
                if path.name == "epic-local-00001-title":
                    raise RuntimeError("simulated epic delete failure")
                if path.exists():
                    shutil.rmtree(path)

        node_repo = _FailOnParentDeleteRepo()
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            node_repo=node_repo,
        )
        result = app_delete_node.delete_node(
            self._request(
                app_contracts,
                node_id="epic-local-00001",
                confirmed=True,
                recursive=True,
                force=True,
            ),
            ports,
        )

        self.assertEqual(result.status, "local_delete_partial_failure")
        self.assertEqual(result.target_id, "epic-local-00001")
        self.assertEqual(result.deleted_node_ids, ["iss-local-00056", "iss-local-00057"])
        self.assertEqual(result.remaining_node_ids, ["epic-local-00001"])
        self.assertEqual(result.active_restore_result, "not_needed")
        self.assertEqual(result.dependency_scrub_failures, [])
        self.assertIn("local_delete_failed", result.warnings)
        self.assertGreaterEqual(len(result.recovery_guidance), 4)
        self.assertIn(
            "./spec-dock/scripts/spec-dock delete --id epic-local-00001 --recursive --force --yes",
            result.recovery_guidance[-1],
        )
        self.assertTrue(Path(records[1].path).exists())
        self.assertFalse(Path(records[2].path).exists())
        self.assertFalse(Path(records[3].path).exists())

    def test_parent_recursive_local_delete_partial_failure_counts_deleted_when_raise_after_removal(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = self._records(infra_contracts, repo_root)

        class _FailAfterRemovingParentRepo(_StubNodeRepository):
            def delete_tree(self, node_path):
                super().delete_tree(node_path)
                path = Path(node_path)
                if path.exists():
                    shutil.rmtree(path)
                if path.name == "epic-local-00001-title":
                    raise RuntimeError("simulated epic delete failure after removal")

        node_repo = _FailAfterRemovingParentRepo()
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            node_repo=node_repo,
        )
        result = app_delete_node.delete_node(
            self._request(
                app_contracts,
                node_id="epic-local-00001",
                confirmed=True,
                recursive=True,
            ),
            ports,
        )

        self.assertEqual(result.status, "local_delete_partial_failure")
        self.assertEqual(result.target_id, "epic-local-00001")
        self.assertEqual(result.deleted_node_ids, ["iss-local-00056", "iss-local-00057", "epic-local-00001"])
        self.assertEqual(result.remaining_node_ids, [])
        self.assertEqual(result.active_restore_result, "not_needed")
        self.assertEqual(result.dependency_scrub_failures, [])
        self.assertIn("local_delete_failed", result.warnings)
        self.assertGreaterEqual(len(result.recovery_guidance), 4)
        self.assertIn("active restore was not needed for the partially deleted target", result.recovery_guidance[0])
        self.assertFalse(Path(records[1].path).exists())
        self.assertFalse(Path(records[2].path).exists())
        self.assertFalse(Path(records[3].path).exists())

    def test_forced_parent_delete_dependency_scrub_success_scrubs_surviving_parent_and_issue_deps(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = [
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="initiative",
                node_id="init-local-00001",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00001",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00056",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00057",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00002",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00058",
                parent_id="epic-local-00002",
                initiative_id="init-local-00001",
                epic_id="epic-local-00002",
                github_issue_number=None,
                initiative_node_id="init-local-00001",
                epic_node_id="epic-local-00002",
            ),
        ]
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            dep_map={"iss-local-00058": ["iss-local-00056"]},
            node_repo=_DeletingNodeRepository(),
        )

        init_meta = Path(records[0].path) / ".meta.json"
        init_meta.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "depends_on": ["epic-local-00001", "iss-local-00058", "epic-local-00002"],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        epic_meta = Path(records[4].path) / ".meta.json"
        epic_meta.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "depends_on": ["iss-local-00056", "iss-local-00058"],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        issue_meta = Path(records[5].path) / ".meta.json"
        issue_meta.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "depends_on": ["iss-local-00056", "iss-local-00058", "epic-local-00001"],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        result = app_delete_node.delete_node(
            self._request(
                app_contracts,
                node_id="epic-local-00001",
                confirmed=True,
                recursive=True,
                force=True,
            ),
            ports,
        )

        self.assertEqual(result.status, "ok")
        self.assertEqual(result.target_id, "epic-local-00001")
        self.assertEqual(result.deleted_node_ids, ["iss-local-00056", "iss-local-00057", "epic-local-00001"])
        self.assertEqual(result.remaining_node_ids, [])
        self.assertEqual(result.active_restore_result, "not_needed")
        self.assertEqual(result.dependency_scrub_failures, [])
        self.assertEqual(json.loads(init_meta.read_text(encoding="utf-8"))["depends_on"], ["iss-local-00058", "epic-local-00002"])
        self.assertEqual(json.loads(epic_meta.read_text(encoding="utf-8"))["depends_on"], ["iss-local-00058"])
        self.assertEqual(json.loads(issue_meta.read_text(encoding="utf-8"))["depends_on"], ["iss-local-00058"])
        self.assertFalse(Path(records[1].path).exists())
        self.assertFalse(Path(records[2].path).exists())
        self.assertFalse(Path(records[3].path).exists())
        self.assertTrue(Path(records[4].path).exists())
        self.assertTrue(Path(records[5].path).exists())

    def test_forced_parent_delete_dependency_scrub_supports_numeric_scoped_and_url_refs_with_survivor_context_resolution(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = [
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="initiative",
                node_id="init-local-00001",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00001",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00056",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=56,
                github_repo_owner="example",
                github_repo_name="repo",
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00057",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=57,
                github_repo_owner="example",
                github_repo_name="repo",
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00059",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=56,
                github_repo_owner="other",
                github_repo_name="repo",
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00002",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00058",
                parent_id="epic-local-00002",
                initiative_id="init-local-00001",
                epic_id="epic-local-00002",
                github_issue_number=58,
                github_repo_owner="example",
                github_repo_name="repo",
                initiative_node_id="init-local-00001",
                epic_node_id="epic-local-00002",
            ),
        ]
        issue_gateway = _StubIssueGateway(
            domain_models=domain_models,
            view_states={
                ("example/repo", 56): "CLOSED",
                ("example/repo", 57): "CLOSED",
                ("other/repo", 56): "CLOSED",
            },
        )
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            dep_map={"iss-local-00058": ["iss-local-00056", "iss-local-00057"]},
            node_repo=_DeletingNodeRepository(),
            issue_gateway=issue_gateway,
        )

        survivor_meta = Path(records[6].path) / ".meta.json"
        survivor_meta.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "depends_on": [
                        "57",
                        "56",
                        "example/repo#56",
                        "https://github.com/other/repo/issues/56",
                        "iss-local-00058",
                        "https://github.com/missing/repo/issues/56",
                        "example/repo#999",
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        result = app_delete_node.delete_node(
            self._request(
                app_contracts,
                node_id="epic-local-00001",
                confirmed=True,
                recursive=True,
                force=True,
            ),
            ports,
        )

        self.assertEqual(result.status, "ok")
        self.assertEqual(result.target_id, "epic-local-00001")
        self.assertEqual(
            result.deleted_node_ids,
            ["iss-local-00056", "iss-local-00057", "iss-local-00059", "epic-local-00001"],
        )
        self.assertEqual(result.remaining_node_ids, [])
        self.assertEqual(result.active_restore_result, "not_needed")
        self.assertEqual(result.dependency_scrub_failures, [])
        self.assertEqual(
            json.loads(survivor_meta.read_text(encoding="utf-8"))["depends_on"],
            [
                "https://github.com/other/repo/issues/56",
                "iss-local-00058",
                "https://github.com/missing/repo/issues/56",
                "example/repo#999",
            ],
        )
        self.assertFalse(Path(records[1].path).exists())
        self.assertFalse(Path(records[2].path).exists())
        self.assertFalse(Path(records[3].path).exists())
        self.assertFalse(Path(records[4].path).exists())
        self.assertTrue(Path(records[5].path).exists())
        self.assertTrue(Path(records[6].path).exists())

    def test_forced_parent_delete_dependency_scrub_keeps_ambiguous_numeric_refs_for_survivor_context(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = [
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="initiative",
                node_id="init-local-00001",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00001",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00056",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=56,
                github_repo_owner="example",
                github_repo_name="repo",
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00057",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=57,
                github_repo_owner="example",
                github_repo_name="repo",
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00059",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=56,
                github_repo_owner="other",
                github_repo_name="repo",
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00002",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00058",
                parent_id="epic-local-00002",
                initiative_id="init-local-00001",
                epic_id="epic-local-00002",
                github_issue_number=58,
                github_repo_owner="example",
                github_repo_name="repo",
                initiative_node_id="init-local-00001",
                epic_node_id="epic-local-00002",
            ),
        ]
        issue_gateway = _StubIssueGateway(
            domain_models=domain_models,
            view_states={
                ("example/repo", 56): "CLOSED",
                ("example/repo", 57): "CLOSED",
                ("other/repo", 56): "CLOSED",
            },
        )
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            dep_map={"iss-local-00058": ["iss-local-00056", "iss-local-00059"]},
            node_repo=_DeletingNodeRepository(),
            issue_gateway=issue_gateway,
        )

        survivor_meta = Path(records[6].path) / ".meta.json"
        survivor_meta.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "depends_on": [
                        "56",
                        "example/repo#56",
                        "https://github.com/other/repo/issues/56",
                        "iss-local-00058",
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        result = app_delete_node.delete_node(
            self._request(
                app_contracts,
                node_id="epic-local-00001",
                confirmed=True,
                recursive=True,
                force=True,
            ),
            ports,
        )

        self.assertEqual(result.status, "ok")
        self.assertEqual(result.target_id, "epic-local-00001")
        self.assertEqual(
            result.deleted_node_ids,
            ["iss-local-00056", "iss-local-00057", "iss-local-00059", "epic-local-00001"],
        )
        self.assertEqual(result.remaining_node_ids, [])
        self.assertEqual(result.active_restore_result, "not_needed")
        self.assertEqual(result.dependency_scrub_failures, [])
        self.assertEqual(
            json.loads(survivor_meta.read_text(encoding="utf-8"))["depends_on"],
            [
                "56",
                "iss-local-00058",
            ],
        )
        self.assertFalse(Path(records[1].path).exists())
        self.assertFalse(Path(records[2].path).exists())
        self.assertFalse(Path(records[3].path).exists())
        self.assertFalse(Path(records[4].path).exists())
        self.assertTrue(Path(records[5].path).exists())
        self.assertTrue(Path(records[6].path).exists())

    def test_forced_parent_delete_dependency_scrub_failure_returns_partial_failure(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = [
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="initiative",
                node_id="init-local-00001",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00001",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00056",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00057",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="epic",
                node_id="epic-local-00002",
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                repo_root=repo_root,
                kind="issue",
                node_id="iss-local-00058",
                parent_id="epic-local-00002",
                initiative_id="init-local-00001",
                epic_id="epic-local-00002",
                github_issue_number=None,
                initiative_node_id="init-local-00001",
                epic_node_id="epic-local-00002",
            ),
        ]
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            dep_map={"iss-local-00058": ["iss-local-00056"]},
            node_repo=_DeletingNodeRepository(),
        )
        survivor_meta = Path(records[5].path) / ".meta.json"
        survivor_meta.write_text("{invalid-json", encoding="utf-8")

        result = app_delete_node.delete_node(
            self._request(
                app_contracts,
                node_id="epic-local-00001",
                confirmed=True,
                recursive=True,
                force=True,
            ),
            ports,
        )

        self.assertEqual(result.status, "local_delete_partial_failure")
        self.assertEqual(result.target_id, "epic-local-00001")
        self.assertEqual(result.deleted_node_ids, ["iss-local-00056", "iss-local-00057", "epic-local-00001"])
        self.assertEqual(result.remaining_node_ids, [])
        self.assertEqual(result.active_restore_result, "not_needed")
        self.assertEqual(
            [(item.node_id, item.edge_target_id) for item in result.dependency_scrub_failures],
            [("iss-local-00058", "iss-local-00056")],
        )
        self.assertIn("dependency_scrub_failed", result.warnings)
        self.assertTrue(any("dependency_scrub_failures" in line for line in result.recovery_guidance))
        self.assertFalse(Path(records[1].path).exists())
        self.assertFalse(Path(records[2].path).exists())
        self.assertFalse(Path(records[3].path).exists())
        self.assertTrue(Path(records[4].path).exists())
        self.assertTrue(Path(records[5].path).exists())

    def test_issue_target_remote_close_runs_before_local_delete_and_success_payload_is_fixed(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = self._records(infra_contracts, repo_root, with_github_links=True)
        events: list[str] = []

        class _EventIssueGateway(_StubIssueGateway):
            def issue_close(self, repo_root, issue_number, *, repo_slug=None):
                slug = str(repo_slug or "").strip().lower()
                events.append(f"close:{slug}#{int(issue_number)}")
                return super().issue_close(repo_root, issue_number, repo_slug=repo_slug)

        class _EventNodeRepo(_StubNodeRepository):
            def delete_tree(self, node_path):
                events.append(f"delete:{Path(node_path).as_posix()}")
                super().delete_tree(node_path)

        issue_gateway = _EventIssueGateway(
            domain_models=domain_models,
            view_states={("example/repo", 56): "OPEN"},
        )
        node_repo = _EventNodeRepo()
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            issue_gateway=issue_gateway,
            node_repo=node_repo,
        )
        result = app_delete_node.delete_node(
            self._request(app_contracts, node_id="iss-local-00056", confirmed=True),
            ports,
        )

        self.assertEqual(result.status, "ok")
        self.assertEqual(result.target_id, "iss-local-00056")
        self.assertEqual(result.deleted_node_ids, ["iss-local-00056"])
        self.assertEqual(result.remaining_node_ids, [])
        self.assertEqual(result.active_restore_result, "not_needed")
        self.assertIsNotNone(result.remote_close)
        assert result.remote_close is not None
        self.assertEqual(result.remote_close.closed, ["example/repo#56"])
        self.assertEqual(result.remote_close.noop_already_closed, [])
        self.assertEqual(result.remote_close.failed, [])
        self.assertEqual(result.remote_close.skipped_not_attempted, [])
        self.assertEqual(node_repo.delete_calls, [records[2].path])
        self.assertTrue(events)
        self.assertTrue(events[-1].startswith("delete:"))
        close_events = [event for event in events if event.startswith("close:")]
        self.assertEqual(close_events, ["close:example/repo#56"])

    def test_issue_target_delete_succeeds_when_remote_issue_is_already_closed(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = self._records(infra_contracts, repo_root, with_github_links=True)
        issue_gateway = _StubIssueGateway(
            domain_models=domain_models,
            view_states={("example/repo", 56): "CLOSED"},
        )
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            issue_gateway=issue_gateway,
        )

        result = app_delete_node.delete_node(
            self._request(app_contracts, node_id="iss-local-00056", confirmed=True),
            ports,
        )

        self.assertEqual(result.status, "ok")
        self.assertEqual(result.target_id, "iss-local-00056")
        self.assertEqual(result.deleted_node_ids, ["iss-local-00056"])
        self.assertEqual(result.remaining_node_ids, [])
        self.assertIsNotNone(result.remote_close)
        assert result.remote_close is not None
        self.assertEqual(result.remote_close.closed, [])
        self.assertEqual(result.remote_close.noop_already_closed, ["example/repo#56"])
        self.assertEqual(result.remote_close.failed, [])
        self.assertEqual(result.remote_close.skipped_not_attempted, [])
        self.assertEqual(issue_gateway.close_calls, [])
        self.assertFalse(Path(records[2].path).exists())

    def test_issue_target_remote_close_failed_does_not_call_local_delete(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = self._records(infra_contracts, repo_root, with_github_links=True)
        issue_gateway = _StubIssueGateway(
            domain_models=domain_models,
            view_states={("example/repo", 56): "OPEN"},
            close_failures={("example/repo", 56)},
        )
        node_repo = _StubNodeRepository()
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            issue_gateway=issue_gateway,
            node_repo=node_repo,
        )

        result = app_delete_node.delete_node(
            self._request(app_contracts, node_id="iss-local-00056", confirmed=True),
            ports,
        )

        self.assertEqual(result.status, "remote_close_failed")
        self.assertEqual(result.target_id, "iss-local-00056")
        self.assertEqual(result.deleted_node_ids, [])
        self.assertIsNotNone(result.remote_close)
        assert result.remote_close is not None
        self.assertEqual(result.remote_close.closed, [])
        self.assertEqual(result.remote_close.noop_already_closed, [])
        self.assertEqual(result.remote_close.failed, ["example/repo#56"])
        self.assertEqual(result.remote_close.skipped_not_attempted, [])
        self.assertEqual(node_repo.delete_calls, [])
        self.assertTrue(Path(records[2].path).exists())

    def test_issue_target_local_delete_failure_after_remote_close_returns_partial_failure(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = self._records(infra_contracts, repo_root, with_github_links=True)

        class _FailingDeleteNodeRepo(_StubNodeRepository):
            def delete_tree(self, node_path):
                super().delete_tree(node_path)
                raise RuntimeError("simulated local delete failure")

        issue_gateway = _StubIssueGateway(
            domain_models=domain_models,
            view_states={("example/repo", 56): "OPEN"},
        )
        node_repo = _FailingDeleteNodeRepo()
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            issue_gateway=issue_gateway,
            node_repo=node_repo,
        )
        result = app_delete_node.delete_node(
            self._request(app_contracts, node_id="iss-local-00056", confirmed=True),
            ports,
        )

        self.assertEqual(result.status, "local_delete_partial_failure")
        self.assertEqual(result.target_id, "iss-local-00056")
        self.assertEqual(result.deleted_node_ids, [])
        self.assertEqual(result.remaining_node_ids, ["iss-local-00056"])
        self.assertEqual(result.active_restore_result, "not_needed")
        self.assertEqual(result.dependency_scrub_failures, [])
        self.assertIn("local_delete_failed", result.warnings)
        self.assertGreaterEqual(len(result.recovery_guidance), 4)
        self.assertIn("active restore was not needed", result.recovery_guidance[0])
        self.assertIn("validate", result.recovery_guidance[1])
        self.assertIn("./spec-dock/scripts/spec-dock sync", result.recovery_guidance[2])
        self.assertIn(
            "./spec-dock/scripts/spec-dock delete --id iss-local-00056 --yes",
            result.recovery_guidance[-1],
        )
        self.assertIsNotNone(result.remote_close)
        assert result.remote_close is not None
        self.assertEqual(result.remote_close.closed, ["example/repo#56"])
        self.assertEqual(result.remote_close.noop_already_closed, [])
        self.assertEqual(result.remote_close.failed, [])
        self.assertEqual(result.remote_close.skipped_not_attempted, [])
        self.assertEqual(issue_gateway.close_calls, [(str(repo_root), "example/repo", 56)])
        self.assertEqual(node_repo.delete_calls, [records[2].path])
        self.assertTrue(Path(records[2].path).exists())

    def test_issue_target_local_delete_failure_json_exit_code_is_non_zero(self) -> None:
        app_contracts, app_delete_node, _app_ports, cli_dispatch, cli_parser, cli_registry, domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = self._records(infra_contracts, repo_root, with_github_links=True)

        class _FailingDeleteNodeRepo(_StubNodeRepository):
            def delete_tree(self, node_path):
                super().delete_tree(node_path)
                raise RuntimeError("simulated local delete failure")

        issue_gateway = _StubIssueGateway(
            domain_models=domain_models,
            view_states={("example/repo", 56): "OPEN"},
        )
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            issue_gateway=issue_gateway,
            node_repo=_FailingDeleteNodeRepo(),
        )
        use_cases = app_contracts.UseCases(
            create_initiative=lambda req: None,  # type: ignore[return-value]
            create_epic=lambda req: None,  # type: ignore[return-value]
            create_issue=lambda req: None,  # type: ignore[return-value]
            create_discussion_doc=lambda req: None,  # type: ignore[return-value]
            import_initiative=lambda req: None,  # type: ignore[return-value]
            import_epic=lambda req: None,  # type: ignore[return-value]
            import_issue=lambda req: None,  # type: ignore[return-value]
            set_active=lambda req: None,  # type: ignore[return-value]
            show_active=lambda req: None,  # type: ignore[return-value]
            clear_active=lambda req: None,  # type: ignore[return-value]
            sync=lambda req: None,  # type: ignore[return-value]
            check_deps=lambda req: None,  # type: ignore[return-value]
            validate_tree=lambda req: None,  # type: ignore[return-value]
            delete_node=lambda req: app_delete_node.delete_node(req, ports),
        )
        registry = cli_registry.build_registry()
        parser = cli_parser.build_parser(registry)
        ns = parser.parse_args(["delete", "--id", "iss-local-00056", "--yes", "--json"])
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = cli_dispatch.dispatch(ns, registry, use_cases)

        self.assertEqual(exit_code, 1)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["status"], "local_delete_partial_failure")
        self.assertEqual(payload["target_id"], "iss-local-00056")
        self.assertEqual(payload["deleted_node_ids"], [])
        self.assertEqual(payload["remaining_node_ids"], ["iss-local-00056"])
        self.assertEqual(payload["remote_close"]["closed"], ["example/repo#56"])
        self.assertEqual(payload["active_restore_result"], "not_needed")
        self.assertEqual(payload["dependency_scrub_failures"], [])
        self.assertIn("recovery_guidance", payload)
        self.assertEqual(stderr.getvalue(), "")

    def test_forced_issue_delete_clears_active_when_target_is_active(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = self._records(infra_contracts, repo_root, with_github_links=True)
        manifest = infra_contracts.ActiveManifest(
            initiative=infra_contracts.ActiveManifestEntry(id="init-local-00001", path="spec-dock/initiatives/x"),
            epic=infra_contracts.ActiveManifestEntry(id="epic-local-00001", path="spec-dock/initiatives/x"),
            issue=infra_contracts.ActiveManifestEntry(id="iss-local-00056", path="spec-dock/initiatives/x"),
        )
        active_store = _StubActiveStateStore(infra_contracts, manifest)
        issue_gateway = _StubIssueGateway(
            domain_models=domain_models,
            view_states={("example/repo", 56): "OPEN"},
        )
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            issue_gateway=issue_gateway,
            active_state_store=active_store,
        )
        result = app_delete_node.delete_node(
            self._request(
                app_contracts,
                node_id="iss-local-00056",
                confirmed=True,
                force=True,
            ),
            ports,
        )

        self.assertEqual(result.status, "ok")
        self.assertEqual(result.target_id, "iss-local-00056")
        self.assertEqual(result.deleted_node_ids, ["iss-local-00056"])
        self.assertEqual(result.remaining_node_ids, [])
        self.assertEqual(result.active_restore_result, "cleared")
        write_calls = [call for call in active_store.calls if call[0] == "write_active_manifest"]
        self.assertTrue(write_calls)
        written_manifest = write_calls[-1][2]
        self.assertIsNotNone(written_manifest)
        self.assertIsNone(written_manifest.initiative)
        self.assertIsNone(written_manifest.epic)
        self.assertIsNone(written_manifest.issue)

    def test_forced_issue_delete_repairs_active_from_snapshot_when_clear_fails(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = self._records(infra_contracts, repo_root)
        manifest = infra_contracts.ActiveManifest(
            initiative=infra_contracts.ActiveManifestEntry(id="init-local-00001", path="spec-dock/initiatives/x"),
            epic=infra_contracts.ActiveManifestEntry(id="epic-local-00001", path="spec-dock/initiatives/x"),
            issue=infra_contracts.ActiveManifestEntry(id="iss-local-00056", path="spec-dock/initiatives/x"),
        )

        class _FailingClearThenRepairStore(_StubActiveStateStore):
            def write_active_manifest(self, specdock_dir, manifest):
                if manifest.initiative is None and manifest.epic is None and manifest.issue is None:
                    raise RuntimeError("failed to persist empty active manifest")
                return super().write_active_manifest(specdock_dir, manifest)

        active_store = _FailingClearThenRepairStore(infra_contracts, manifest)
        issue_gateway = _StubIssueGateway(
            domain_models=domain_models,
            view_states={},
        )
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            issue_gateway=issue_gateway,
            active_state_store=active_store,
        )
        result = app_delete_node.delete_node(
            self._request(
                app_contracts,
                node_id="iss-local-00056",
                confirmed=True,
                force=True,
            ),
            ports,
        )

        self.assertEqual(result.status, "local_delete_partial_failure")
        self.assertEqual(result.target_id, "iss-local-00056")
        self.assertEqual(result.deleted_node_ids, ["iss-local-00056"])
        self.assertEqual(result.remaining_node_ids, [])
        self.assertEqual(result.active_restore_result, "restored")
        self.assertIn("active_clear_failed", result.warnings)
        self.assertNotIn("active_restore_failed", result.warnings)
        self.assertTrue(result.recovery_guidance)
        self.assertIn("best-effort active repair was applied", result.recovery_guidance[0])
        self.assertIsNotNone(result.remote_close)
        assert result.remote_close is not None
        self.assertEqual(result.remote_close.closed, [])
        self.assertEqual(result.remote_close.noop_already_closed, [])
        self.assertEqual(result.remote_close.failed, [])
        self.assertEqual(result.remote_close.skipped_not_attempted, [])
        self.assertIn(("snapshot_current_state", str(repo_root / "spec-dock")), active_store.calls)
        write_calls = [call for call in active_store.calls if call[0] == "write_active_manifest"]
        self.assertTrue(write_calls)
        self.assertIsNotNone(write_calls[-1][2].initiative)
        self.assertIsNotNone(write_calls[-1][2].epic)
        self.assertIsNone(write_calls[-1][2].issue)
        self.assertFalse(Path(records[2].path).exists())

    def test_forced_issue_delete_returns_partial_failure_when_clear_active_fails_after_local_delete(self) -> None:
        app_contracts, app_delete_node, _app_ports, _cli_dispatch, _cli_parser, _cli_registry, domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        records = self._records(infra_contracts, repo_root, with_github_links=True)
        manifest = infra_contracts.ActiveManifest(
            initiative=infra_contracts.ActiveManifestEntry(id="init-local-00001", path="spec-dock/initiatives/x"),
            epic=infra_contracts.ActiveManifestEntry(id="epic-local-00001", path="spec-dock/initiatives/x"),
            issue=infra_contracts.ActiveManifestEntry(id="iss-local-00056", path="spec-dock/initiatives/x"),
        )

        class _FailingClearActiveStore(_StubActiveStateStore):
            def write_active_manifest(self, specdock_dir, manifest):
                del specdock_dir, manifest
                raise RuntimeError("failed to persist active manifest")

        active_store = _FailingClearActiveStore(infra_contracts, manifest)
        issue_gateway = _StubIssueGateway(
            domain_models=domain_models,
            view_states={("example/repo", 56): "OPEN"},
        )
        ports = self._ports(
            records=records,
            repo_root=repo_root,
            issue_gateway=issue_gateway,
            active_state_store=active_store,
        )

        result = app_delete_node.delete_node(
            self._request(
                app_contracts,
                node_id="iss-local-00056",
                confirmed=True,
                force=True,
            ),
            ports,
        )

        self.assertEqual(result.status, "local_delete_partial_failure")
        self.assertEqual(result.target_id, "iss-local-00056")
        self.assertEqual(result.deleted_node_ids, ["iss-local-00056"])
        self.assertEqual(result.remaining_node_ids, [])
        self.assertEqual(result.active_restore_result, "restore_failed")
        self.assertIn("active_restore_failed", result.warnings)
        self.assertTrue(result.recovery_guidance)
        self.assertIn("active repair failed after local delete", result.recovery_guidance[0])
        self.assertIsNotNone(result.remote_close)
        assert result.remote_close is not None
        self.assertEqual(result.remote_close.closed, ["example/repo#56"])
        self.assertEqual(result.remote_close.noop_already_closed, [])
        self.assertEqual(result.remote_close.failed, [])
        self.assertEqual(result.remote_close.skipped_not_attempted, [])
        self.assertFalse(Path(records[2].path).exists())

    def test_delete_command_positional_selector_wiring_and_json_exit_code(self) -> None:
        app_contracts, _app_delete_node, _app_ports, cli_dispatch, cli_parser, cli_registry, _domain_models, _infra_contracts = (
            _runtime_modules()
        )
        captured = {}

        def _delete(req):
            captured["request"] = req
            return app_contracts.DeleteNodeResult(
                status="dependency_conflict",
                target_id="iss-local-00056",
                deleted_node_ids=[],
                remaining_node_ids=[],
                remote_close=None,
                offending_node_ids=["iss-local-00057"],
                validation_reasons=[
                    app_contracts.DeleteValidationReason(
                        node_id="iss-local-00056",
                        code="dependency_conflict",
                        message="dependency edge crosses delete subtree boundary",
                    )
                ],
                active_restore_result=None,
                recovery_guidance=[],
                dependency_scrub_failures=[],
                warnings=[],
            )

        use_cases = app_contracts.UseCases(
            create_initiative=lambda req: None,  # type: ignore[return-value]
            create_epic=lambda req: None,  # type: ignore[return-value]
            create_issue=lambda req: None,  # type: ignore[return-value]
            create_discussion_doc=lambda req: None,  # type: ignore[return-value]
            import_initiative=lambda req: None,  # type: ignore[return-value]
            import_epic=lambda req: None,  # type: ignore[return-value]
            import_issue=lambda req: None,  # type: ignore[return-value]
            set_active=lambda req: None,  # type: ignore[return-value]
            show_active=lambda req: None,  # type: ignore[return-value]
            clear_active=lambda req: None,  # type: ignore[return-value]
            sync=lambda req: None,  # type: ignore[return-value]
            check_deps=lambda req: None,  # type: ignore[return-value]
            validate_tree=lambda req: None,  # type: ignore[return-value]
            delete_node=_delete,
        )

        registry = cli_registry.build_registry()
        parser = cli_parser.build_parser(registry)
        ns = parser.parse_args(["delete", "iss-local-00056", "--yes", "--json"])
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = cli_dispatch.dispatch(ns, registry, use_cases)

        self.assertEqual(exit_code, 1)
        request = captured["request"]
        self.assertEqual(request.positional_target, "iss-local-00056")
        self.assertTrue(request.confirmed)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["status"], "dependency_conflict")
        self.assertEqual(set(payload.keys()), {"status", "target_id", "offending_node_ids", "validation_reasons"})
        self.assertEqual(stderr.getvalue(), "")

    def test_delete_json_field_matrix_for_blocker_statuses(self) -> None:
        app_contracts, _app_delete_node, _app_ports, cli_dispatch, cli_parser, cli_registry, _domain_models, _infra_contracts = (
            _runtime_modules()
        )
        statuses = [
            "invalid_selector_combination",
            "invalid_selector_syntax",
            "target_not_found",
            "ambiguous_target",
            "active_conflict",
            "dependency_conflict",
            "recursive_required",
            "confirmation_required",
        ]
        registry = cli_registry.build_registry()
        parser = cli_parser.build_parser(registry)

        for status in statuses:
            def _delete(_req, status=status):
                return app_contracts.DeleteNodeResult(
                    status=status,
                    target_id="iss-local-00056",
                    deleted_node_ids=[],
                    remaining_node_ids=[],
                    remote_close=app_contracts.DeleteRemoteCloseBuckets(
                        closed=[],
                        noop_already_closed=[],
                        failed=[],
                        skipped_not_attempted=[],
                    ),
                    offending_node_ids=["iss-local-00057"],
                    validation_reasons=[
                        app_contracts.DeleteValidationReason(
                            node_id="iss-local-00056",
                            code=status,
                            message=status,
                        )
                    ],
                    active_restore_result="not_needed",
                    recovery_guidance=["noop"],
                    dependency_scrub_failures=[
                        app_contracts.DeleteDependencyScrubFailure(
                            node_id="iss-local-00056",
                            edge_target_id="iss-local-00057",
                        )
                    ],
                    warnings=[],
                )

            use_cases = app_contracts.UseCases(
                create_initiative=lambda req: None,  # type: ignore[return-value]
                create_epic=lambda req: None,  # type: ignore[return-value]
                create_issue=lambda req: None,  # type: ignore[return-value]
                create_discussion_doc=lambda req: None,  # type: ignore[return-value]
                import_initiative=lambda req: None,  # type: ignore[return-value]
                import_epic=lambda req: None,  # type: ignore[return-value]
                import_issue=lambda req: None,  # type: ignore[return-value]
                set_active=lambda req: None,  # type: ignore[return-value]
                show_active=lambda req: None,  # type: ignore[return-value]
                clear_active=lambda req: None,  # type: ignore[return-value]
                sync=lambda req: None,  # type: ignore[return-value]
                check_deps=lambda req: None,  # type: ignore[return-value]
                validate_tree=lambda req: None,  # type: ignore[return-value]
                delete_node=_delete,
            )

            ns = parser.parse_args(["delete", "--id", "iss-local-00056", "--yes", "--json"])
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = cli_dispatch.dispatch(ns, registry, use_cases)

            self.assertEqual(exit_code, 1, status)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["status"], status)
            self.assertEqual(
                set(payload.keys()),
                {"status", "target_id", "offending_node_ids", "validation_reasons"},
            )
            self.assertEqual(stderr.getvalue(), "")

    def test_delete_json_field_matrix_for_ok_status_with_ordering(self) -> None:
        app_contracts, _app_delete_node, _app_ports, cli_dispatch, cli_parser, cli_registry, _domain_models, _infra_contracts = (
            _runtime_modules()
        )

        def _ok(_req):
            return app_contracts.DeleteNodeResult(
                status="ok",
                target_id="iss-local-00056",
                deleted_node_ids=["iss-local-00056"],
                remaining_node_ids=[],
                remote_close=app_contracts.DeleteRemoteCloseBuckets(
                    closed=["example/repo#56"],
                    noop_already_closed=[],
                    failed=[],
                    skipped_not_attempted=[],
                ),
                offending_node_ids=[],
                validation_reasons=[],
                active_restore_result="not_needed",
                recovery_guidance=[],
                dependency_scrub_failures=[],
                warnings=[],
            )

        use_cases = app_contracts.UseCases(
            create_initiative=lambda req: None,  # type: ignore[return-value]
            create_epic=lambda req: None,  # type: ignore[return-value]
            create_issue=lambda req: None,  # type: ignore[return-value]
            create_discussion_doc=lambda req: None,  # type: ignore[return-value]
            import_initiative=lambda req: None,  # type: ignore[return-value]
            import_epic=lambda req: None,  # type: ignore[return-value]
            import_issue=lambda req: None,  # type: ignore[return-value]
            set_active=lambda req: None,  # type: ignore[return-value]
            show_active=lambda req: None,  # type: ignore[return-value]
            clear_active=lambda req: None,  # type: ignore[return-value]
            sync=lambda req: None,  # type: ignore[return-value]
            check_deps=lambda req: None,  # type: ignore[return-value]
            validate_tree=lambda req: None,  # type: ignore[return-value]
            delete_node=_ok,
        )
        registry = cli_registry.build_registry()
        parser = cli_parser.build_parser(registry)
        ns = parser.parse_args(["delete", "--id", "iss-local-00056", "--yes", "--json"])
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = cli_dispatch.dispatch(ns, registry, use_cases)

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(
            list(payload.keys()),
            ["status", "target_id", "deleted_node_ids", "remaining_node_ids", "remote_close", "active_restore_result"],
        )
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["deleted_node_ids"], ["iss-local-00056"])
        self.assertEqual(payload["remaining_node_ids"], [])
        self.assertEqual(payload["remote_close"]["closed"], ["example/repo#56"])
        self.assertEqual(payload["active_restore_result"], "not_needed")
        self.assertEqual(stderr.getvalue(), "")

    def test_delete_json_field_matrix_for_metadata_validation_failed_and_remote_close_failed(self) -> None:
        app_contracts, _app_delete_node, _app_ports, cli_dispatch, cli_parser, cli_registry, _domain_models, _infra_contracts = (
            _runtime_modules()
        )
        registry = cli_registry.build_registry()
        parser = cli_parser.build_parser(registry)

        def _metadata_failed(_req):
            return app_contracts.DeleteNodeResult(
                status="metadata_validation_failed",
                target_id="epic-local-00001",
                deleted_node_ids=[],
                remaining_node_ids=[],
                remote_close=app_contracts.DeleteRemoteCloseBuckets(
                    closed=[],
                    noop_already_closed=[],
                    failed=[],
                    skipped_not_attempted=[],
                ),
                offending_node_ids=["iss-local-00056"],
                validation_reasons=[
                    app_contracts.DeleteValidationReason(
                        node_id="iss-local-00056",
                        code="metadata_validation_failed",
                        message="metadata invalid",
                    )
                ],
                active_restore_result=None,
                recovery_guidance=[],
                dependency_scrub_failures=[],
                warnings=[],
            )

        use_cases_metadata_failed = app_contracts.UseCases(
            create_initiative=lambda req: None,  # type: ignore[return-value]
            create_epic=lambda req: None,  # type: ignore[return-value]
            create_issue=lambda req: None,  # type: ignore[return-value]
            create_discussion_doc=lambda req: None,  # type: ignore[return-value]
            import_initiative=lambda req: None,  # type: ignore[return-value]
            import_epic=lambda req: None,  # type: ignore[return-value]
            import_issue=lambda req: None,  # type: ignore[return-value]
            set_active=lambda req: None,  # type: ignore[return-value]
            show_active=lambda req: None,  # type: ignore[return-value]
            clear_active=lambda req: None,  # type: ignore[return-value]
            sync=lambda req: None,  # type: ignore[return-value]
            check_deps=lambda req: None,  # type: ignore[return-value]
            validate_tree=lambda req: None,  # type: ignore[return-value]
            delete_node=_metadata_failed,
        )

        ns_metadata = parser.parse_args(["delete", "--id", "epic-local-00001", "--yes", "--json"])
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = cli_dispatch.dispatch(ns_metadata, registry, use_cases_metadata_failed)

        self.assertEqual(exit_code, 1)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(
            set(payload.keys()),
            {"status", "target_id", "offending_node_ids", "validation_reasons", "remote_close"},
        )
        self.assertEqual(payload["status"], "metadata_validation_failed")
        self.assertEqual(stderr.getvalue(), "")

        def _remote_close_failed(_req):
            return app_contracts.DeleteNodeResult(
                status="remote_close_failed",
                target_id="epic-local-00001",
                deleted_node_ids=[],
                remaining_node_ids=[],
                remote_close=app_contracts.DeleteRemoteCloseBuckets(
                    closed=["alpha/repo#22"],
                    noop_already_closed=[],
                    failed=["beta/repo#57"],
                    skipped_not_attempted=["zeta/repo#99"],
                ),
                offending_node_ids=[],
                validation_reasons=[],
                active_restore_result="restored",
                recovery_guidance=["retry"],
                dependency_scrub_failures=[],
                warnings=[],
            )

        use_cases_remote_failed = app_contracts.UseCases(
            create_initiative=lambda req: None,  # type: ignore[return-value]
            create_epic=lambda req: None,  # type: ignore[return-value]
            create_issue=lambda req: None,  # type: ignore[return-value]
            create_discussion_doc=lambda req: None,  # type: ignore[return-value]
            import_initiative=lambda req: None,  # type: ignore[return-value]
            import_epic=lambda req: None,  # type: ignore[return-value]
            import_issue=lambda req: None,  # type: ignore[return-value]
            set_active=lambda req: None,  # type: ignore[return-value]
            show_active=lambda req: None,  # type: ignore[return-value]
            clear_active=lambda req: None,  # type: ignore[return-value]
            sync=lambda req: None,  # type: ignore[return-value]
            check_deps=lambda req: None,  # type: ignore[return-value]
            validate_tree=lambda req: None,  # type: ignore[return-value]
            delete_node=_remote_close_failed,
        )

        ns_remote = parser.parse_args(["delete", "--id", "epic-local-00001", "--yes", "--json"])
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = cli_dispatch.dispatch(ns_remote, registry, use_cases_remote_failed)

        self.assertEqual(exit_code, 1)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(
            set(payload.keys()),
            {"status", "target_id", "remote_close", "deleted_node_ids"},
        )
        self.assertEqual(payload["status"], "remote_close_failed")
        self.assertEqual(stderr.getvalue(), "")

    def test_delete_json_field_matrix_for_local_delete_partial_failure(self) -> None:
        app_contracts, _app_delete_node, _app_ports, cli_dispatch, cli_parser, cli_registry, _domain_models, _infra_contracts = (
            _runtime_modules()
        )
        registry = cli_registry.build_registry()
        parser = cli_parser.build_parser(registry)

        def _local_partial_failure(_req):
            return app_contracts.DeleteNodeResult(
                status="local_delete_partial_failure",
                target_id="iss-local-00056",
                deleted_node_ids=["iss-local-00056"],
                remaining_node_ids=[],
                remote_close=app_contracts.DeleteRemoteCloseBuckets(
                    closed=["example/repo#56"],
                    noop_already_closed=[],
                    failed=[],
                    skipped_not_attempted=[],
                ),
                offending_node_ids=[],
                validation_reasons=[],
                active_restore_result="restored",
                recovery_guidance=["run validate"],
                dependency_scrub_failures=[],
                warnings=[],
            )

        use_cases = app_contracts.UseCases(
            create_initiative=lambda req: None,  # type: ignore[return-value]
            create_epic=lambda req: None,  # type: ignore[return-value]
            create_issue=lambda req: None,  # type: ignore[return-value]
            create_discussion_doc=lambda req: None,  # type: ignore[return-value]
            import_initiative=lambda req: None,  # type: ignore[return-value]
            import_epic=lambda req: None,  # type: ignore[return-value]
            import_issue=lambda req: None,  # type: ignore[return-value]
            set_active=lambda req: None,  # type: ignore[return-value]
            show_active=lambda req: None,  # type: ignore[return-value]
            clear_active=lambda req: None,  # type: ignore[return-value]
            sync=lambda req: None,  # type: ignore[return-value]
            check_deps=lambda req: None,  # type: ignore[return-value]
            validate_tree=lambda req: None,  # type: ignore[return-value]
            delete_node=_local_partial_failure,
        )

        ns = parser.parse_args(["delete", "--id", "iss-local-00056", "--yes", "--json"])
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = cli_dispatch.dispatch(ns, registry, use_cases)

        self.assertEqual(exit_code, 1)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(
            set(payload.keys()),
            {
                "status",
                "target_id",
                "deleted_node_ids",
                "remaining_node_ids",
                "remote_close",
                "active_restore_result",
                "recovery_guidance",
                "dependency_scrub_failures",
            },
        )
        self.assertEqual(payload["status"], "local_delete_partial_failure")
        self.assertEqual(payload["deleted_node_ids"], ["iss-local-00056"])
        self.assertEqual(payload["active_restore_result"], "restored")
        self.assertEqual(stderr.getvalue(), "")

    def test_issue_delete_success_path_returns_ok_and_cli_success_text(self) -> None:
        app_contracts, app_delete_node, _app_ports, cli_dispatch, cli_parser, cli_registry, _domain_models, infra_contracts = (
            _runtime_modules()
        )
        repo_root = self._new_repo_root()
        ports = self._ports(records=self._records(infra_contracts, repo_root), repo_root=repo_root)
        result = app_delete_node.delete_node(
            self._request(app_contracts, node_id="iss-local-00056", confirmed=True),
            ports,
        )
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.deleted_node_ids, ["iss-local-00056"])
        self.assertEqual(result.remaining_node_ids, [])

        use_cases = app_contracts.UseCases(
            create_initiative=lambda req: None,  # type: ignore[return-value]
            create_epic=lambda req: None,  # type: ignore[return-value]
            create_issue=lambda req: None,  # type: ignore[return-value]
            create_discussion_doc=lambda req: None,  # type: ignore[return-value]
            import_initiative=lambda req: None,  # type: ignore[return-value]
            import_epic=lambda req: None,  # type: ignore[return-value]
            import_issue=lambda req: None,  # type: ignore[return-value]
            set_active=lambda req: None,  # type: ignore[return-value]
            show_active=lambda req: None,  # type: ignore[return-value]
            clear_active=lambda req: None,  # type: ignore[return-value]
            sync=lambda req: None,  # type: ignore[return-value]
            check_deps=lambda req: None,  # type: ignore[return-value]
            validate_tree=lambda req: None,  # type: ignore[return-value]
            delete_node=lambda _req: result,
        )
        registry = cli_registry.build_registry()
        parser = cli_parser.build_parser(registry)
        ns = parser.parse_args(["delete", "--id", "iss-local-00056", "--yes"])
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = cli_dispatch.dispatch(ns, registry, use_cases)
        self.assertEqual(exit_code, 0)
        self.assertIn("ok (delete) target=iss-local-00056", stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")
