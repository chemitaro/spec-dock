import json
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
        from spec_dock_runtime import app as runtime_app
        from spec_dock_runtime.application import contracts as app_contracts
        from spec_dock_runtime.application import import_node as app_import_node
        from spec_dock_runtime.application import ports as app_ports
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.infra import artifact_writer as infra_artifact_writer
        from spec_dock_runtime.infra import contracts as infra_contracts
        from spec_dock_runtime.presentation import cli_text as presentation_cli_text
    finally:
        sys.path.pop(0)
    return (
        runtime_app,
        app_contracts,
        app_import_node,
        app_ports,
        domain_models,
        infra_artifact_writer,
        infra_contracts,
        presentation_cli_text,
    )


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
    github_issue_number: int | None,
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
        meta_path=(path / ".meta.json").as_posix(),
    )


class _DummyClock:
    def today(self):
        return "2026-03-12"


class _NodeStore:
    def __init__(self, records):
        self.records = list(records)

    def load(self):
        return list(self.records)

    def append(self, record):
        self.records.append(record)


class _StubNodeReader:
    def __init__(self, store):
        self.store = store

    def load_node_records(self):
        return self.store.load()


class _StubNodeRepo:
    def __init__(self, store, events=None):
        self.store = store
        self.events = events if events is not None else []

    def load_node_records(self, specdock_dir):
        del specdock_dir
        return self.store.load()

    def write_meta(self, dest_dir, record):
        self.events.append("write_meta")
        dest_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "schema_version": 1,
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
            "parent_id": record.parent_id,
            "initiative_id": record.initiative_id,
            "epic_id": record.epic_id,
        }
        if record.github_issue_number is not None:
            data["github"] = {"issue_number": int(record.github_issue_number)}
        (dest_dir / ".meta.json").write_text(json.dumps(data), encoding="utf-8")
        self.store.append(record)


class _StubTemplateScaffolder:
    def __init__(self, events=None):
        self.events = events if events is not None else []

    def render_text(self, text, replacements):
        rendered = text
        for key, value in replacements.items():
            rendered = rendered.replace(key, value)
        return rendered

    def load_template_text(self, src_path):
        return src_path.read_text(encoding="utf-8")

    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        self.events.append("copy_scaffolded_tree")
        created = []
        for src_path in sorted(src_dir.rglob("*"), key=lambda p: p.as_posix()):
            if src_path.is_dir():
                continue
            rel = src_path.relative_to(src_dir)
            dest_path = dest_dir / rel
            if dest_path.exists():
                raise RuntimeError(f"Destination already exists: {dest_path}")
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            text = src_path.read_text(encoding="utf-8")
            dest_path.write_text(self.render_text(text, replacements), encoding="utf-8")
            created.append(dest_path)
        return created

    def write_text(self, dest_path, text):
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(text, encoding="utf-8")


class _StubIssueGateway:
    def __init__(self, domain_models):
        self._domain_models = domain_models
        self.view_calls = []

    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return []

    def issue_create(self, repo_root, title, body):
        del repo_root, title, body
        raise AssertionError("issue_create must not be used in import flow")

    def issue_view_minimal(self, repo_root, issue_number):
        self.view_calls.append((str(repo_root), int(issue_number)))
        return self._domain_models.IssueSnapshot(
            issue_number=int(issue_number),
            state="OPEN",
            title=f"Issue {issue_number}",
            labels=[],
            updated_at="2026-03-12T00:00:00Z",
            url=f"https://example.invalid/issues/{issue_number}",
        )


class _StubActiveStateStore:
    def __init__(self, infra_contracts, manifest):
        self._infra_contracts = infra_contracts
        self._manifest = manifest
        self.calls = []

    def load_active_manifest(self, specdock_dir):
        self.calls.append(("load_active_manifest", str(specdock_dir)))
        return self._infra_contracts.ActiveManifestLoadResult(
            manifest=self._manifest,
            source="agent.active" if self._manifest is not None else "none",
            warnings=[],
        )

    def load_active_manifest_no_migrate(self, specdock_dir):
        self.calls.append(("load_active_manifest_no_migrate", str(specdock_dir)))
        return self._infra_contracts.ActiveManifestLoadResult(
            manifest=self._manifest,
            source="agent.active" if self._manifest is not None else "none",
            warnings=[],
        )

    def load_active_issue_id(self, specdock_dir):
        del specdock_dir
        if self._manifest is None or self._manifest.issue is None:
            return None
        return self._manifest.issue.id

    def write_active_manifest(self, specdock_dir, manifest):
        del specdock_dir
        self._manifest = manifest
        return manifest

    def apply_active_pointers(self, specdock_dir, manifest, rendered_context_pack):
        del specdock_dir, manifest, rendered_context_pack

    def patch_agent_state_active_fields(self, specdock_dir, manifest):
        del specdock_dir, manifest

    def snapshot_current_state(self, specdock_dir):
        del specdock_dir
        raise AssertionError("snapshot_current_state should not be called in import flow")

    def restore_previous_state(self, specdock_dir, snapshot):
        del specdock_dir, snapshot
        raise AssertionError("restore_previous_state should not be called in import flow")


class _StubDepsTopologyReader:
    def __init__(self, infra_contracts):
        self._infra_contracts = infra_contracts

    def load_issue_depends_on_map(self, specdock_dir, graph):
        del specdock_dir, graph
        return self._infra_contracts.DepsTopologyLoadResult(issue_depends_on_map={}, warnings=[])


class _StubDerivedStateReader:
    def load_cached_issue_status_by_id(self, specdock_dir):
        del specdock_dir
        return {}


class _FailingArtifactWriter:
    def write(self, specdock_dir, bundle):
        del specdock_dir, bundle
        raise RuntimeError("artifact write failed")


class TestRuntimeImportS10(unittest.TestCase):
    def _prepare_templates(self, specdock_dir: Path) -> None:
        initiative_dir = specdock_dir / "templates" / "initiative"
        epic_dir = specdock_dir / "templates" / "epic"
        issue_dir = specdock_dir / "templates" / "issue"
        for path in (initiative_dir, epic_dir, issue_dir):
            path.mkdir(parents=True, exist_ok=True)
        (initiative_dir / "README.md").write_text(
            "initiative=<INIT_ID> title=<INIT_TITLE> github=<GITHUB_ISSUE_NUMBER_OR_URL>\n",
            encoding="utf-8",
        )
        (epic_dir / "README.md").write_text(
            "epic=<EPIC_ID> init=<INIT_ID> title=<EPIC_TITLE> github=<GITHUB_ISSUE_NUMBER_OR_URL>\n",
            encoding="utf-8",
        )
        (issue_dir / "README.md").write_text(
            (
                "issue=<ISS_ID> epic=<EPIC_ID> init=<INIT_ID> "
                "title=<ISS_TITLE> github=<GITHUB_ISSUE_NUMBER_OR_URL>\n"
            ),
            encoding="utf-8",
        )

    def _base_records(self, infra_contracts, specdock_dir: Path):
        init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
        epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
        return [
            _record(
                infra_contracts,
                kind="initiative",
                node_id="init-local-00001",
                title="Auth platform",
                path=init_dir,
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                kind="epic",
                node_id="epic-local-00001",
                title="JWT auth",
                path=epic_dir,
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
            ),
        ]

    def _active_manifest(self, infra_contracts, *, initiative_id=None, epic_id=None, issue_id=None):
        def _entry(node_id):
            if node_id is None:
                return None
            return infra_contracts.ActiveManifestEntry(id=node_id, path=f"spec-dock/path/{node_id}")

        return infra_contracts.ActiveManifest(
            initiative=_entry(initiative_id),
            epic=_entry(epic_id),
            issue=_entry(issue_id),
        )

    def _dummy_sync_result(self, app_contracts, domain_models):
        return app_contracts.SyncCommandResult(
            state=app_contracts.SyncStateResult(
                graph=domain_models.SpecGraph(nodes_by_id={}),
                active=None,
                issue_statuses={},
                progress=domain_models.ProgressMap(by_node_id={}, counts={}),
                deps_state=domain_models.DepsState(nodes=[], warnings=[]),
                deps_eval_by_id={},
                generated_at="2026-03-12T00:00:00Z",
                warnings=[],
                deps_preflight_error=None,
            ),
            write_result=None,
            active_update=None,
            artifact_failure=None,
        )

    def _ports(
        self,
        app_ports,
        *,
        specdock_dir: Path,
        store,
        domain_models,
        infra_contracts,
        active_manifest,
        artifact_writer,
        events=None,
    ):
        return app_ports.Ports(
            node_reader=_StubNodeReader(store),
            node_repo=_StubNodeRepo(store, events=events),
            template_scaffolder=_StubTemplateScaffolder(events=events),
            issue_gateway=_StubIssueGateway(domain_models),
            active_state_store=_StubActiveStateStore(infra_contracts, active_manifest),
            deps_topology_reader=_StubDepsTopologyReader(infra_contracts),
            derived_state_reader=_StubDerivedStateReader(),
            artifact_writer=artifact_writer,
            clock=_DummyClock(),
            repo_root=specdock_dir.parent,
            specdock_dir=specdock_dir,
        )

    def test_parent_fallback_regression(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_import_node,
            app_ports,
            domain_models,
            infra_artifact_writer,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            specdock_dir = Path(tmp) / "spec-dock"
            self._prepare_templates(specdock_dir)
            store = _NodeStore(self._base_records(infra_contracts, specdock_dir))
            manifest = self._active_manifest(
                infra_contracts,
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
            )
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                store=store,
                domain_models=domain_models,
                infra_contracts=infra_contracts,
                active_manifest=manifest,
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
            )

            result = app_import_node.import_issue(
                app_contracts.ImportNodeRequest(
                    issue_number=123,
                    title="Add refresh token",
                    slug=None,
                    parent_id=None,
                ),
                ports,
            )

            self.assertEqual(result.node.id, "iss-00123")
            self.assertEqual(result.node.parent_id, "epic-local-00001")
            self.assertEqual(result.node.github_issue_number, 123)
            calls = [name for name, _path in ports.active_state_store.calls]
            self.assertIn("load_active_manifest_no_migrate", calls)
            self.assertNotIn("load_active_manifest", calls)

    def test_load_active_manifest_chain_regression(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_import_node,
            app_ports,
            domain_models,
            _infra_artifact_writer,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            specdock_dir = Path(tmp) / "spec-dock"
            self._prepare_templates(specdock_dir)
            records = self._base_records(infra_contracts, specdock_dir)
            issue_dir = Path(records[1].path) / "issues" / "iss-local-00009-refresh-token"
            records.append(
                _record(
                    infra_contracts,
                    kind="issue",
                    node_id="iss-local-00009",
                    title="Refresh token",
                    path=issue_dir,
                    parent_id="epic-local-00001",
                    initiative_id="init-local-00001",
                    epic_id="epic-local-00001",
                    github_issue_number=None,
                )
            )
            store = _NodeStore(records)
            manifest = self._active_manifest(infra_contracts, issue_id="iss-local-00009")
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                store=store,
                domain_models=domain_models,
                infra_contracts=infra_contracts,
                active_manifest=manifest,
                artifact_writer=_FailingArtifactWriter(),
            )

            captured = {}
            original_resolve = app_import_node.resolve_parent_from_active
            original_sync = app_import_node.sync_after_import

            def _fake_resolve(graph, child_kind, active):
                del graph
                captured["child_kind"] = child_kind
                captured["active"] = active
                return "epic-local-00001"

            app_import_node.resolve_parent_from_active = _fake_resolve
            app_import_node.sync_after_import = lambda _ports: self._dummy_sync_result(app_contracts, domain_models)
            try:
                result = app_import_node.import_issue(
                    app_contracts.ImportNodeRequest(
                        issue_number=456,
                        title="Imported issue",
                        slug=None,
                        parent_id=None,
                    ),
                    ports,
                )
            finally:
                app_import_node.resolve_parent_from_active = original_resolve
                app_import_node.sync_after_import = original_sync

            self.assertEqual(result.node.parent_id, "epic-local-00001")
            self.assertEqual(captured["child_kind"], "issue")
            self.assertEqual(captured["active"].initiative_id, None)
            self.assertEqual(captured["active"].epic_id, None)
            self.assertEqual(captured["active"].issue_id, "iss-local-00009")
            self.assertEqual([name for name, _path in ports.active_state_store.calls], ["load_active_manifest_no_migrate"])

    def test_duplicate_guard_no_write_regression(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_import_node,
            app_ports,
            domain_models,
            infra_artifact_writer,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            specdock_dir = Path(tmp) / "spec-dock"
            self._prepare_templates(specdock_dir)
            records = self._base_records(infra_contracts, specdock_dir)
            records.append(
                _record(
                    infra_contracts,
                    kind="issue",
                    node_id="iss-00123",
                    title="Existing imported issue",
                    path=Path(records[1].path) / "issues" / "iss-00123-existing-imported-issue",
                    parent_id="epic-local-00001",
                    initiative_id="init-local-00001",
                    epic_id="epic-local-00001",
                    github_issue_number=123,
                )
            )
            store = _NodeStore(records)
            events: list[str] = []
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                store=store,
                domain_models=domain_models,
                infra_contracts=infra_contracts,
                active_manifest=self._active_manifest(infra_contracts),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                events=events,
            )

            with self.assertRaisesRegex(RuntimeError, "already linked"):
                app_import_node.import_issue(
                    app_contracts.ImportNodeRequest(
                        issue_number=123,
                        title="Imported issue",
                        slug=None,
                        parent_id="epic-local-00001",
                    ),
                    ports,
                )

            self.assertEqual(events, [])
            self.assertEqual(ports.issue_gateway.view_calls, [])

    def test_no_write_preflight_collision_regression(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_import_node,
            app_ports,
            domain_models,
            infra_artifact_writer,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            specdock_dir = Path(tmp) / "spec-dock"
            self._prepare_templates(specdock_dir)
            records = self._base_records(infra_contracts, specdock_dir)
            store = _NodeStore(records)
            events: list[str] = []
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                store=store,
                domain_models=domain_models,
                infra_contracts=infra_contracts,
                active_manifest=self._active_manifest(infra_contracts),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                events=events,
            )

            collision = (
                Path(records[1].path) / "issues" / "iss-00124-add-refresh-token" / "README.md"
            )
            collision.parent.mkdir(parents=True, exist_ok=True)
            collision.write_text("existing", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "Destination already exists"):
                app_import_node.import_issue(
                    app_contracts.ImportNodeRequest(
                        issue_number=124,
                        title="Add refresh token",
                        slug=None,
                        parent_id="epic-local-00001",
                    ),
                    ports,
                )

            self.assertEqual(events, [])
            self.assertEqual(ports.issue_gateway.view_calls, [])
            self.assertFalse((collision.parent / ".meta.json").exists())

    def test_import_then_sync_artifact_path_name_content_regression(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_import_node,
            app_ports,
            domain_models,
            infra_artifact_writer,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)
            store = _NodeStore(self._base_records(infra_contracts, specdock_dir))
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                store=store,
                domain_models=domain_models,
                infra_contracts=infra_contracts,
                active_manifest=self._active_manifest(infra_contracts),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
            )

            result = app_import_node.import_issue(
                app_contracts.ImportNodeRequest(
                    issue_number=321,
                    title="Import then sync",
                    slug=None,
                    parent_id="epic-local-00001",
                ),
                ports,
            )

            self.assertIsNone(result.post_import_sync.artifact_failure)
            self.assertIsNotNone(result.post_import_sync.write_result)
            write_result = result.post_import_sync.write_result
            self.assertEqual(write_result.index_all_path, "spec-dock/.agent/index-all.json")
            self.assertEqual(write_result.index_todo_path, "spec-dock/.agent/index.json")
            self.assertEqual(write_result.tree_all_path, "spec-dock/.agent/tree-all.json")
            self.assertEqual(write_result.tree_todo_path, "spec-dock/.agent/tree.json")
            self.assertEqual(write_result.tree_all_puml_path, "spec-dock/tree-all.puml")
            self.assertEqual(write_result.tree_todo_puml_path, "spec-dock/tree.puml")
            self.assertEqual(write_result.deps_issues_json_path, "spec-dock/.agent/deps-issues.json")
            self.assertEqual(write_result.deps_issues_puml_path, "spec-dock/deps-issues.puml")
            self.assertEqual(write_result.dashboard_md_path, "spec-dock/dashboard.md")

            index_all_path = repo_root / write_result.index_all_path
            tree_all_path = repo_root / write_result.tree_all_path
            self.assertTrue(index_all_path.exists())
            self.assertTrue(tree_all_path.exists())

            index_all = json.loads(index_all_path.read_text(encoding="utf-8"))
            tree_all = json.loads(tree_all_path.read_text(encoding="utf-8"))
            self.assertIn("iss-00321", index_all["nodes"])
            self.assertIn("iss-00321", json.dumps(tree_all, ensure_ascii=False))

    def test_post_import_sync_negative_path_regression(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_import_node,
            app_ports,
            domain_models,
            _infra_artifact_writer,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            specdock_dir = Path(tmp) / "spec-dock"
            self._prepare_templates(specdock_dir)
            store = _NodeStore(self._base_records(infra_contracts, specdock_dir))
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                store=store,
                domain_models=domain_models,
                infra_contracts=infra_contracts,
                active_manifest=self._active_manifest(infra_contracts),
                artifact_writer=_FailingArtifactWriter(),
            )

            result = app_import_node.import_issue(
                app_contracts.ImportNodeRequest(
                    issue_number=222,
                    title="Import with failing sync",
                    slug=None,
                    parent_id="epic-local-00001",
                ),
                ports,
            )

            self.assertIsNotNone(result.post_import_sync.artifact_failure)
            self.assertEqual(result.post_import_sync.artifact_failure.status, "failed_partial_or_stale")
            self.assertIn("artifact write failed", result.post_import_sync.artifact_failure.reason)
            self.assertTrue((result.node.path / ".meta.json").exists())

    def test_execute_create_plan_reuse_seam(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_import_node,
            app_ports,
            domain_models,
            infra_artifact_writer,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            specdock_dir = Path(tmp) / "spec-dock"
            self._prepare_templates(specdock_dir)
            store = _NodeStore(self._base_records(infra_contracts, specdock_dir))
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                store=store,
                domain_models=domain_models,
                infra_contracts=infra_contracts,
                active_manifest=self._active_manifest(infra_contracts),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
            )

            calls = []
            original_execute = app_import_node.execute_create_plan
            original_sync = app_import_node.sync_after_import

            def _fake_execute(plan, ports_arg):
                calls.append((plan.meta.id, ports_arg))
                return [Path(plan.meta.path) / "README.md", Path(plan.meta.meta_path)]

            app_import_node.execute_create_plan = _fake_execute
            app_import_node.sync_after_import = lambda _ports: self._dummy_sync_result(app_contracts, domain_models)
            try:
                result = app_import_node.import_issue(
                    app_contracts.ImportNodeRequest(
                        issue_number=909,
                        title="Reuse execute plan",
                        slug=None,
                        parent_id="epic-local-00001",
                    ),
                    ports,
                )
            finally:
                app_import_node.execute_create_plan = original_execute
                app_import_node.sync_after_import = original_sync

            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0][0], "iss-00909")
            self.assertEqual(result.node.id, "iss-00909")

    def test_renderer_text_regression(self) -> None:
        (
            _runtime_app,
            app_contracts,
            _app_import_node,
            _app_ports,
            domain_models,
            _infra_artifact_writer,
            _infra_contracts,
            presentation_cli_text,
        ) = _runtime_modules()
        post_sync = app_contracts.SyncCommandResult(
            state=app_contracts.SyncStateResult(
                graph=domain_models.SpecGraph(nodes_by_id={}),
                active=None,
                issue_statuses={},
                progress=domain_models.ProgressMap(by_node_id={}, counts={}),
                deps_state=domain_models.DepsState(nodes=[], warnings=[]),
                deps_eval_by_id={},
                generated_at="2026-03-12T00:00:00Z",
                warnings=["gh_index_incomplete"],
                deps_preflight_error=None,
            ),
            write_result=None,
            active_update=None,
            artifact_failure=None,
        )
        node = app_contracts.SpecNode(
            kind="issue",
            id="iss-00123",
            title="Imported issue",
            slug="imported-issue",
            path=Path(
                "/repo/spec-dock/initiatives/init-local-00001-auth/epics/epic-local-00001-jwt/issues/iss-00123-imported-issue"
            ),
            meta_path=Path(
                "/repo/spec-dock/initiatives/init-local-00001-auth/epics/epic-local-00001-jwt/issues/iss-00123-imported-issue/.meta.json"
            ),
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=123,
        )
        result = app_contracts.ImportNodeResult(
            node=node,
            imported_issue=domain_models.IssueSnapshot(
                issue_number=123,
                state="OPEN",
                title="Imported issue",
                labels=[],
                updated_at="2026-03-12T00:00:00Z",
                url="https://example.invalid/issues/123",
            ),
            post_import_sync=post_sync,
            warnings=[],
        )
        text = presentation_cli_text.render_import_text(result)
        self.assertEqual(
            text.stdout_lines,
            [
                (
                    "spec-dock: ok (import issue) "
                    "id=iss-00123 epic=epic-local-00001 initiative=init-local-00001 "
                    "path=spec-dock/initiatives/init-local-00001-auth/epics/epic-local-00001-jwt/"
                    "issues/iss-00123-imported-issue github=#123"
                )
            ],
        )
        self.assertEqual(text.warnings, ["gh_index_incomplete"])

    def test_command_import_issue_smoke(self) -> None:
        (
            _runtime_app,
            app_contracts,
            _app_import_node,
            _app_ports,
            domain_models,
            _infra_artifact_writer,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()

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
            from spec_dock_runtime.commands import import_cmd
        finally:
            sys.path.pop(0)

        calls = []

        def _unexpected(_req):
            raise AssertionError("unexpected use case call")

        def _fake_import(req):
            calls.append(req)
            return app_contracts.ImportNodeResult(
                node=app_contracts.SpecNode(
                    kind="issue",
                    id="iss-00123",
                    title=req.title,
                    slug="imported-issue",
                    path=Path(
                        "/repo/spec-dock/initiatives/init-local-00001-auth/epics/epic-local-00001-jwt/issues/iss-00123-imported-issue"
                    ),
                    meta_path=Path(
                        "/repo/spec-dock/initiatives/init-local-00001-auth/epics/epic-local-00001-jwt/issues/iss-00123-imported-issue/.meta.json"
                    ),
                    parent_id="epic-local-00001",
                    initiative_id="init-local-00001",
                    epic_id="epic-local-00001",
                    github_issue_number=req.issue_number,
                ),
                imported_issue=domain_models.IssueSnapshot(
                    issue_number=req.issue_number,
                    state="OPEN",
                    title=req.title,
                    labels=[],
                    updated_at="2026-03-12T00:00:00Z",
                    url=f"https://example.invalid/issues/{req.issue_number}",
                ),
                post_import_sync=self._dummy_sync_result(app_contracts, domain_models),
                warnings=[],
            )

        use_cases = app_contracts.UseCases(
            create_initiative=_unexpected,
            create_epic=_unexpected,
            create_issue=_unexpected,
            create_discussion_doc=_unexpected,
            import_initiative=_unexpected,
            import_epic=_unexpected,
            import_issue=_fake_import,
            set_active=_unexpected,
            show_active=_unexpected,
            clear_active=_unexpected,
            sync=_unexpected,
            check_deps=_unexpected,
            validate_tree=_unexpected,
        )
        outcome = import_cmd._run_import_issue(
            import_cmd.ImportIssueArgs(
                issue_number=123,
                title="Imported issue",
                slug=None,
                epic_id="epic-local-00001",
            ),
            use_cases,
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].issue_number, 123)
        self.assertEqual(calls[0].parent_id, "epic-local-00001")
        self.assertEqual(outcome.exit_code, 0)
        self.assertIn("spec-dock: ok (import issue)", "\n".join(outcome.text.stdout_lines))

    def test_import_command_returns_nonzero_when_post_sync_artifact_failure_exists(self) -> None:
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
            from spec_dock_runtime.commands import import_cmd
            from spec_dock_runtime.domain import models as domain_models
        finally:
            sys.path.pop(0)

        post_sync = app_contracts.SyncCommandResult(
            state=app_contracts.SyncStateResult(
                graph=domain_models.SpecGraph(nodes_by_id={}),
                active=None,
                issue_statuses={},
                progress=domain_models.ProgressMap(by_node_id={}, counts={}),
                deps_state=domain_models.DepsState(nodes=[], warnings=[]),
                deps_eval_by_id={},
                generated_at="2026-03-12T00:00:00Z",
                warnings=[],
                deps_preflight_error=None,
            ),
            write_result=None,
            active_update=None,
            artifact_failure=app_contracts.ArtifactWriteFailure(
                status="failed_partial_or_stale",
                reason="artifact write failed",
            ),
        )
        import_result = app_contracts.ImportNodeResult(
            node=app_contracts.SpecNode(
                kind="issue",
                id="iss-00123",
                title="Imported issue",
                slug="imported-issue",
                path=Path("/repo/spec-dock/initiatives/init-local-00001/epics/epic-local-00001/issues/iss-00123-imported-issue"),
                meta_path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001/epics/epic-local-00001/issues/iss-00123-imported-issue/.meta.json"
                ),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=123,
            ),
            imported_issue=domain_models.IssueSnapshot(
                issue_number=123,
                state="OPEN",
                title="Imported issue",
                labels=[],
                updated_at="2026-03-12T00:00:00Z",
                url="https://example.invalid/issues/123",
            ),
            post_import_sync=post_sync,
            warnings=[],
        )

        class _UseCases:
            def import_issue(self, req):
                del req
                return import_result

        outcome = import_cmd._run_import_issue(
            import_cmd.ImportIssueArgs(
                issue_number=123,
                title="Imported issue",
                slug=None,
                epic_id="epic-local-00001",
            ),
            _UseCases(),
        )
        self.assertEqual(outcome.exit_code, 1)
        self.assertIn("import_post_sync_failed", outcome.text.warnings)


if __name__ == "__main__":
    unittest.main()
