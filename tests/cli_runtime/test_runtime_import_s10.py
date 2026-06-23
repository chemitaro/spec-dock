import json
import os
from pathlib import Path
import sys
import tempfile

import pytest

_UNSET = object()


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime import app as runtime_app
        from spec_dock_runtime.application import (
            contracts as app_contracts,
            import_node as app_import_node,
            ports as app_ports,
        )
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.infra import artifact_writer as infra_artifact_writer, contracts as infra_contracts
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
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
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
            github_data = {"issue_number": int(record.github_issue_number)}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                github_data["repo_owner"] = record.github_repo_owner
                github_data["repo_name"] = record.github_repo_name
            data["github"] = github_data
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

    def issue_view_minimal(self, repo_root, issue_number, *, repo_slug=None):
        self.view_calls.append((str(repo_root), int(issue_number), repo_slug))
        return self._domain_models.IssueSnapshot(
            issue_number=int(issue_number),
            state="OPEN",
            title=f"Issue {issue_number}",
            labels=[],
            updated_at="2026-03-12T00:00:00Z",
            url=f"https://example.invalid/issues/{issue_number}",
        )

    def issue_view_snapshot(self, repo_root, issue_number, *, repo_slug=None):
        return self.issue_view_minimal(repo_root, issue_number, repo_slug=repo_slug)


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


class _StubGitGateway:
    def __init__(self, origin_slug):
        self.origin_slug = origin_slug
        self.origin_calls = []

    def origin_github_repo_slug(self, repo_root):
        self.origin_calls.append(str(repo_root))
        return self.origin_slug


class _FailingArtifactWriter:
    def write(self, specdock_dir, bundle):
        del specdock_dir, bundle
        raise RuntimeError("artifact write failed")


class TestRuntimeImportS10:
    def _prepare_templates(self, specdock_dir: Path) -> None:
        initiative_dir = specdock_dir / "templates" / "initiative"
        epic_dir = specdock_dir / "templates" / "epic"
        issue_dir = specdock_dir / "templates" / "issue"
        rules_docs = {
            specdock_dir / "docs" / "rules" / "initiative" / "discussions.md": "# initiative discussions rules\n",
            specdock_dir / "docs" / "rules" / "initiative" / "epics.md": "# initiative epics rules\n",
            specdock_dir / "docs" / "rules" / "epic" / "discussions.md": "# epic discussions rules\n",
            specdock_dir / "docs" / "rules" / "epic" / "issues.md": "# epic issues rules\n",
            specdock_dir / "docs" / "rules" / "issue" / "discussions.md": "# issue discussions rules\n",
        }
        for path in (initiative_dir, epic_dir, issue_dir):
            path.mkdir(parents=True, exist_ok=True)
        for path, text in rules_docs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        (initiative_dir / "README.md").write_text(
            "initiative=<INIT_ID> title=<INIT_TITLE> github=<GITHUB_ISSUE_NUMBER_OR_URL>\n",
            encoding="utf-8",
        )
        (epic_dir / "README.md").write_text(
            "epic=<EPIC_ID> init=<INIT_ID> title=<EPIC_TITLE> github=<GITHUB_ISSUE_NUMBER_OR_URL>\n",
            encoding="utf-8",
        )
        (issue_dir / "README.md").write_text(
            ("issue=<ISS_ID> epic=<EPIC_ID> init=<INIT_ID> title=<ISS_TITLE> github=<GITHUB_ISSUE_NUMBER_OR_URL>\n"),
            encoding="utf-8",
        )
        for template_dir, token in (
            (initiative_dir, "<INIT_ID>"),
            (epic_dir, "<EPIC_ID>"),
            (issue_dir, "<ISS_ID>"),
        ):
            (template_dir / "requirement.md").write_text(f"# requirement {token}\n", encoding="utf-8")
            (template_dir / "design.md").write_text(f"# design {token}\n", encoding="utf-8")
            (template_dir / "plan.md").write_text(f"# plan {token}\n", encoding="utf-8")
            (template_dir / "report.md").write_text(f"# report {token}\n", encoding="utf-8")

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

    def _materialize_required_artifacts(self, records) -> None:
        for record in records:
            node_dir = Path(record.path)
            node_dir.mkdir(parents=True, exist_ok=True)
            (node_dir / "requirement.md").write_text(f"# requirement: {record.id}\n", encoding="utf-8")
            (node_dir / "design.md").write_text(f"# design: {record.id}\n", encoding="utf-8")
            (node_dir / "plan.md").write_text(f"# plan: {record.id}\n", encoding="utf-8")
            (node_dir / "report.md").write_text(f"# report: {record.id}\n", encoding="utf-8")

            meta = {
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
                github = {"issue_number": int(record.github_issue_number)}
                if record.github_repo_owner is not None and record.github_repo_name is not None:
                    github["repo_owner"] = record.github_repo_owner
                    github["repo_name"] = record.github_repo_name
                meta["github"] = github
            (node_dir / ".meta.json").write_text(json.dumps(meta), encoding="utf-8")

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
        issue_gateway=None,
        git_gateway=_UNSET,
    ):
        self._materialize_required_artifacts(store.load())
        resolved_git_gateway = _StubGitGateway("current/repo") if git_gateway is _UNSET else git_gateway
        return app_ports.Ports(
            node_reader=_StubNodeReader(store),
            node_repo=_StubNodeRepo(store, events=events),
            template_scaffolder=_StubTemplateScaffolder(events=events),
            issue_gateway=issue_gateway or _StubIssueGateway(domain_models),
            active_state_store=_StubActiveStateStore(infra_contracts, active_manifest),
            deps_topology_reader=_StubDepsTopologyReader(infra_contracts),
            derived_state_reader=_StubDerivedStateReader(),
            artifact_writer=artifact_writer,
            clock=_DummyClock(),
            git_gateway=resolved_git_gateway,
            repo_root=specdock_dir.parent,
            specdock_dir=specdock_dir,
        )

    def test_release_create_lock_compat_for_import_old_call_signature(self) -> None:
        (
            _runtime_app,
            _app_contracts,
            app_import_node,
            _app_ports,
            _domain_models,
            _infra_artifact_writer,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            specdock_dir = Path(tmp) / "spec-dock"
            lock_path = specdock_dir / "system" / ".runtime" / "create.lock"
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_payload = (
                "token=holder\npid=222\nuser=lock-holder\ncreated_unix=9999999999\ncreated_iso=2099-01-01T00:00:00Z\n"
            )
            lock_path.write_text(lock_payload, encoding="utf-8")

            with pytest.raises(RuntimeError) as raised:
                app_import_node._release_create_lock(lock_path, "other")

            message = str(raised.value)
            runtime_cmd = str((specdock_dir / "scripts" / "spec-dock").resolve())
            assert "reason=ownership_mismatch" in message
            assert f"{runtime_cmd} doctor" in message
            assert lock_path.exists()

            lock_path.write_text(lock_payload, encoding="utf-8")
            app_import_node._release_create_lock(lock_path, "holder")
            assert not lock_path.exists()

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

            assert result.node.id == "iss-00123"
            assert result.node.parent_id == "epic-local-00001"
            assert result.node.github_issue_number == 123
            assert ports.issue_gateway.view_calls == [(str(specdock_dir.parent), 123, "current/repo")]
            calls = [name for name, _path in ports.active_state_store.calls]
            assert "load_active_manifest_no_migrate" in calls
            assert "load_active_manifest" not in calls

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

            assert result.node.parent_id == "epic-local-00001"
            assert captured["child_kind"] == "issue"
            assert captured["active"].initiative_id is None
            assert captured["active"].epic_id is None
            assert captured["active"].issue_id == "iss-local-00009"
            active_manifest_calls = [name for name, _path in ports.active_state_store.calls]
            # S01H contract: 1st read is a cheap precheck, 2nd read is lock-side final parent re-resolution.
            assert active_manifest_calls == ["load_active_manifest_no_migrate", "load_active_manifest_no_migrate"]

    def test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression(self) -> None:
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
            second_epic_dir = Path(records[0].path) / "epics" / "epic-local-00002-session-rotation"
            records.append(
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00002",
                    title="Session rotation",
                    path=second_epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                )
            )
            store = _NodeStore(records)
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

            captured = {"resolve_calls": 0}
            original_resolve = app_import_node.resolve_parent_from_active
            original_sync = app_import_node.sync_after_import

            def _drifting_resolve(graph, child_kind, active):
                del graph, active
                assert child_kind == "issue"
                captured["resolve_calls"] += 1
                if captured["resolve_calls"] == 1:
                    return "epic-local-00001"
                return "epic-local-00002"

            app_import_node.resolve_parent_from_active = _drifting_resolve
            app_import_node.sync_after_import = lambda _ports: self._dummy_sync_result(app_contracts, domain_models)
            try:
                result = app_import_node.import_issue(
                    app_contracts.ImportNodeRequest(
                        issue_number=777,
                        title="Parent drift import",
                        slug=None,
                        parent_id=None,
                    ),
                    ports,
                )
            finally:
                app_import_node.resolve_parent_from_active = original_resolve
                app_import_node.sync_after_import = original_sync

            assert captured["resolve_calls"] == 2
            assert result.node.parent_id == "epic-local-00002"
            assert result.node.initiative_id == "init-local-00001"
            assert "/epic-local-00002-session-rotation/" in result.node.path.as_posix()
            assert [name for name, _path in ports.active_state_store.calls] == [
                "load_active_manifest_no_migrate",
                "load_active_manifest_no_migrate",
            ]
            assert ports.issue_gateway.view_calls == [(str(specdock_dir.parent), 777, "current/repo")]

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

            with pytest.raises(RuntimeError, match="already linked"):
                app_import_node.import_issue(
                    app_contracts.ImportNodeRequest(
                        issue_number=123,
                        title="Imported issue",
                        slug=None,
                        parent_id="epic-local-00001",
                    ),
                    ports,
                )

            assert events == []
            assert ports.issue_gateway.view_calls == []

    def test_import_import_race_revalidation_no_write_regression(self) -> None:
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
            events: list[str] = []
            issue_gateway = _StubIssueGateway(domain_models)
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                store=store,
                domain_models=domain_models,
                infra_contracts=infra_contracts,
                active_manifest=self._active_manifest(infra_contracts),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                events=events,
                issue_gateway=issue_gateway,
            )

            raced_record = _record(
                infra_contracts,
                kind="issue",
                node_id="iss-00555",
                title="Race winner import",
                path=Path(store.load()[1].path) / "issues" / "iss-00555-race-winner-import",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=555,
            )
            injected = {"done": False}
            original_issue_view = issue_gateway.issue_view_minimal

            def _issue_view_with_race(repo_root, issue_number, *, repo_slug=None):
                if not injected["done"]:
                    self._materialize_required_artifacts([raced_record])
                    store.append(raced_record)
                    injected["done"] = True
                return original_issue_view(repo_root, issue_number, repo_slug=repo_slug)

            issue_gateway.issue_view_minimal = _issue_view_with_race

            with pytest.raises(RuntimeError, match="already linked"):
                app_import_node.import_issue(
                    app_contracts.ImportNodeRequest(
                        issue_number=555,
                        title="Imported issue",
                        slug=None,
                        parent_id="epic-local-00001",
                    ),
                    ports,
                )

            assert injected["done"]
            assert events == []
            assert issue_gateway.view_calls == [(str(specdock_dir.parent), 555, "current/repo")]
            assert sum(1 for record in store.load() if record.id == "iss-00555") == 1

    def test_import_rejects_foreign_repo_before_github_read_lock_and_race_revalidation_writes(
        self,
    ) -> None:
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
            events: list[str] = []
            issue_gateway = _StubIssueGateway(domain_models)
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                store=store,
                domain_models=domain_models,
                infra_contracts=infra_contracts,
                active_manifest=self._active_manifest(infra_contracts),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                events=events,
                issue_gateway=issue_gateway,
                git_gateway=_StubGitGateway("current/repo"),
            )

            raced_record = _record(
                infra_contracts,
                kind="issue",
                node_id="iss-00123",
                title="Race winner new issue",
                path=Path(store.load()[1].path) / "issues" / "iss-00123-race-winner-new-issue",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=123,
            )
            injected = {"done": False}
            lock_calls: list[str] = []
            original_issue_view = issue_gateway.issue_view_minimal
            original_acquire_create_lock = app_import_node._acquire_create_lock

            def _issue_view_with_race(repo_root, issue_number, *, repo_slug=None):
                if not injected["done"]:
                    self._materialize_required_artifacts([raced_record])
                    store.append(raced_record)
                    injected["done"] = True
                return original_issue_view(repo_root, issue_number, repo_slug=repo_slug)

            def _unexpected_acquire_create_lock(lock_specdock_dir):
                lock_calls.append(str(lock_specdock_dir))
                raise AssertionError("_acquire_create_lock must not run for foreign URL rejection")

            issue_gateway.issue_view_minimal = _issue_view_with_race
            app_import_node._acquire_create_lock = _unexpected_acquire_create_lock

            try:
                with pytest.raises(RuntimeError, match="single-repo GitHub-backed identity"):
                    app_import_node.import_issue(
                        app_contracts.ImportNodeRequest(
                            issue_number=123,
                            title="Imported foreign issue",
                            slug=None,
                            parent_id="epic-local-00001",
                            target_repo_owner="other",
                            target_repo_name="repo",
                            allow_foreign_url=True,
                        ),
                        ports,
                    )
            finally:
                app_import_node._acquire_create_lock = original_acquire_create_lock

            assert not injected["done"]
            assert lock_calls == []
            assert issue_gateway.view_calls == []
            assert events == []
            assert sum(1 for record in store.load() if record.id == "iss-00123") == 0
            assert sum(1 for record in store.load() if record.id == "iss-local-00001") == 0

    def test_import_initiative_and_epic_reject_foreign_repo_without_writes(self) -> None:
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

        cases = (
            (
                "initiative",
                app_import_node.import_initiative,
                app_contracts.ImportNodeRequest(
                    issue_number=123,
                    title="Imported initiative",
                    slug=None,
                    parent_id=None,
                    target_repo_owner="other",
                    target_repo_name="repo",
                    allow_foreign_url=True,
                ),
            ),
            (
                "epic",
                app_import_node.import_epic,
                app_contracts.ImportNodeRequest(
                    issue_number=124,
                    title="Imported epic",
                    slug=None,
                    parent_id="init-local-00001",
                    target_repo_owner="other",
                    target_repo_name="repo",
                    allow_foreign_url=True,
                ),
            ),
        )

        for _kind, runner, request in cases:
            with tempfile.TemporaryDirectory() as tmp:
                specdock_dir = Path(tmp) / "spec-dock"
                self._prepare_templates(specdock_dir)
                store = _NodeStore(self._base_records(infra_contracts, specdock_dir))
                events: list[str] = []
                issue_gateway = _StubIssueGateway(domain_models)
                git_gateway = _StubGitGateway("current/repo")
                ports = self._ports(
                    app_ports,
                    specdock_dir=specdock_dir,
                    store=store,
                    domain_models=domain_models,
                    infra_contracts=infra_contracts,
                    active_manifest=self._active_manifest(infra_contracts),
                    artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                    events=events,
                    issue_gateway=issue_gateway,
                    git_gateway=git_gateway,
                )

                with pytest.raises(RuntimeError, match="single-repo GitHub-backed identity"):
                    runner(request, ports)

                assert issue_gateway.view_calls == []
                assert events == []
                assert git_gateway.origin_calls == [str(specdock_dir.parent)]
                assert len(store.load()) == 2

    def test_import_numeric_target_rejects_when_current_repo_unknown_without_writes(self) -> None:
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
        cases = (
            (
                "initiative",
                app_import_node.import_initiative,
                app_contracts.ImportNodeRequest(
                    issue_number=123,
                    title="Imported initiative",
                    slug=None,
                    parent_id=None,
                    target_repo_owner=None,
                    target_repo_name=None,
                    allow_foreign_url=False,
                ),
                "init-00123",
            ),
            (
                "epic",
                app_import_node.import_epic,
                app_contracts.ImportNodeRequest(
                    issue_number=124,
                    title="Imported epic",
                    slug=None,
                    parent_id="init-local-00001",
                    target_repo_owner=None,
                    target_repo_name=None,
                    allow_foreign_url=False,
                ),
                "epic-00124",
            ),
            (
                "issue",
                app_import_node.import_issue,
                app_contracts.ImportNodeRequest(
                    issue_number=125,
                    title="Imported issue",
                    slug=None,
                    parent_id="epic-local-00001",
                    target_repo_owner=None,
                    target_repo_name=None,
                    allow_foreign_url=False,
                ),
                "iss-00125",
            ),
        )

        for _kind, runner, request, expected_node_id in cases:
            with tempfile.TemporaryDirectory() as tmp:
                specdock_dir = Path(tmp) / "spec-dock"
                self._prepare_templates(specdock_dir)
                store = _NodeStore(self._base_records(infra_contracts, specdock_dir))
                events: list[str] = []
                issue_gateway = _StubIssueGateway(domain_models)
                git_gateway = _StubGitGateway(None)
                ports = self._ports(
                    app_ports,
                    specdock_dir=specdock_dir,
                    store=store,
                    domain_models=domain_models,
                    infra_contracts=infra_contracts,
                    active_manifest=self._active_manifest(infra_contracts),
                    artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                    events=events,
                    issue_gateway=issue_gateway,
                    git_gateway=git_gateway,
                )

                original_resolve_parent_for_import = app_import_node.resolve_parent_for_import
                original_build_linked_create_request = app_import_node.build_linked_create_request
                original_plan_node_creation = app_import_node.plan_node_creation

                def _unexpected_resolve_parent_for_import(*args, **kwargs):
                    del args, kwargs
                    raise AssertionError("resolve_parent_for_import should not run before numeric repo-scope guard")

                def _unexpected_build_linked_create_request(*args, **kwargs):
                    del args, kwargs
                    raise AssertionError("build_linked_create_request should not run before numeric repo-scope guard")

                def _unexpected_plan_node_creation(*args, **kwargs):
                    del args, kwargs
                    raise AssertionError("plan_node_creation should not run before numeric repo-scope guard")

                app_import_node.resolve_parent_for_import = _unexpected_resolve_parent_for_import
                app_import_node.build_linked_create_request = _unexpected_build_linked_create_request
                app_import_node.plan_node_creation = _unexpected_plan_node_creation
                try:
                    with pytest.raises(
                        RuntimeError, match="Current GitHub repo scope could not be resolved from origin"
                    ):
                        runner(request, ports)
                finally:
                    app_import_node.resolve_parent_for_import = original_resolve_parent_for_import
                    app_import_node.build_linked_create_request = original_build_linked_create_request
                    app_import_node.plan_node_creation = original_plan_node_creation

                assert events == []
                assert issue_gateway.view_calls == []
                assert git_gateway.origin_calls == [str(specdock_dir.parent)]
                assert sum(1 for record in store.load() if record.id == expected_node_id) == 0

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

            collision = Path(records[1].path) / "issues" / "iss-00124-add-refresh-token" / "README.md"
            collision.parent.mkdir(parents=True, exist_ok=True)
            collision.write_text("existing", encoding="utf-8")

            with pytest.raises(RuntimeError, match="Destination already exists"):
                app_import_node.import_issue(
                    app_contracts.ImportNodeRequest(
                        issue_number=124,
                        title="Add refresh token",
                        slug=None,
                        parent_id="epic-local-00001",
                    ),
                    ports,
                )

            assert events == []
            assert ports.issue_gateway.view_calls == []
            assert not (collision.parent / ".meta.json").exists()

    def test_no_write_preflight_collision_with_active_parent_fallback_regression(self) -> None:
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
                events=events,
            )

            collision = Path(records[1].path) / "issues" / "iss-00124-add-refresh-token" / "README.md"
            collision.parent.mkdir(parents=True, exist_ok=True)
            collision.write_text("existing", encoding="utf-8")

            with pytest.raises(RuntimeError, match="Destination already exists"):
                app_import_node.import_issue(
                    app_contracts.ImportNodeRequest(
                        issue_number=124,
                        title="Add refresh token",
                        slug=None,
                        parent_id=None,
                    ),
                    ports,
                )

            assert events == []
            assert ports.issue_gateway.view_calls == []
            assert [name for name, _path in ports.active_state_store.calls] == ["load_active_manifest_no_migrate"]
            assert not (collision.parent / ".meta.json").exists()

    def test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read(self) -> None:
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
        cases = (
            (
                "initiative",
                app_import_node.import_initiative,
                app_contracts.ImportNodeRequest(
                    issue_number=123,
                    title="Imported initiative",
                    slug=None,
                    parent_id=None,
                    target_repo_owner=None,
                    target_repo_name=None,
                    allow_foreign_url=False,
                ),
                123,
            ),
            (
                "epic",
                app_import_node.import_epic,
                app_contracts.ImportNodeRequest(
                    issue_number=124,
                    title="Imported epic",
                    slug=None,
                    parent_id="init-local-00001",
                    target_repo_owner=None,
                    target_repo_name=None,
                    allow_foreign_url=False,
                ),
                124,
            ),
            (
                "issue",
                app_import_node.import_issue,
                app_contracts.ImportNodeRequest(
                    issue_number=125,
                    title="Imported issue",
                    slug=None,
                    parent_id="epic-local-00001",
                    target_repo_owner=None,
                    target_repo_name=None,
                    allow_foreign_url=False,
                ),
                125,
            ),
        )

        for _kind, runner, request, issue_number in cases:
            with tempfile.TemporaryDirectory() as tmp:
                specdock_dir = Path(tmp) / "spec-dock"
                self._prepare_templates(specdock_dir)
                store = _NodeStore(self._base_records(infra_contracts, specdock_dir))
                issue_gateway = _StubIssueGateway(domain_models)
                ports = self._ports(
                    app_ports,
                    specdock_dir=specdock_dir,
                    store=store,
                    domain_models=domain_models,
                    infra_contracts=infra_contracts,
                    active_manifest=self._active_manifest(infra_contracts),
                    artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                    issue_gateway=issue_gateway,
                    git_gateway=_StubGitGateway("current/repo"),
                )

                result = runner(request, ports)

                assert issue_gateway.view_calls == [(str(specdock_dir.parent), issue_number, "current/repo")]
                assert result.node.github_repo_owner == "current"
                assert result.node.github_repo_name == "repo"
                created_record = store.load()[-1]
                assert created_record.github_repo_owner == "current"
                assert created_record.github_repo_name == "repo"

    def test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present(self) -> None:
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
            issue_gateway = _StubIssueGateway(domain_models)
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                store=store,
                domain_models=domain_models,
                infra_contracts=infra_contracts,
                active_manifest=self._active_manifest(infra_contracts),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                issue_gateway=issue_gateway,
                git_gateway=_StubGitGateway("current/repo"),
            )

            result = app_import_node.import_issue(
                app_contracts.ImportNodeRequest(
                    issue_number=123,
                    title="Imported issue",
                    slug=None,
                    parent_id="epic-local-00001",
                    target_repo_owner="current",
                    target_repo_name="repo",
                    allow_foreign_url=True,
                ),
                ports,
            )

            assert result.node.id == "iss-00123"
            assert issue_gateway.view_calls == [(str(specdock_dir.parent), 123, "current/repo")]
            assert result.node.github_repo_owner == "current"
            assert result.node.github_repo_name == "repo"
            created_record = store.load()[-1]
            assert created_record.github_repo_owner == "current"
            assert created_record.github_repo_name == "repo"

    def test_import_issue_rejects_foreign_repo_without_opt_in(self) -> None:
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
            issue_gateway = _StubIssueGateway(domain_models)
            git_gateway = _StubGitGateway("example/repo")
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                store=store,
                domain_models=domain_models,
                infra_contracts=infra_contracts,
                active_manifest=self._active_manifest(infra_contracts),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                issue_gateway=issue_gateway,
                git_gateway=git_gateway,
            )

            with pytest.raises(RuntimeError, match="single-repo GitHub-backed identity"):
                app_import_node.import_issue(
                    app_contracts.ImportNodeRequest(
                        issue_number=123,
                        title="Imported issue",
                        slug=None,
                        parent_id="epic-local-00001",
                        target_repo_owner="other",
                        target_repo_name="repo",
                        allow_foreign_url=False,
                    ),
                    ports,
                )

            assert issue_gateway.view_calls == []
            assert git_gateway.origin_calls == [str(specdock_dir.parent)]
            assert sum(1 for record in store.load() if record.kind == "issue") == 0

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

            assert result.post_import_sync.artifact_failure is None
            assert result.post_import_sync.write_result is not None
            write_result = result.post_import_sync.write_result
            assert write_result.index_all_path == "spec-dock/.agent/index-all.json"
            assert write_result.index_todo_path == "spec-dock/.agent/index.json"
            assert write_result.tree_all_path == "spec-dock/.agent/tree-all.json"
            assert write_result.tree_todo_path == "spec-dock/.agent/tree.json"
            assert write_result.tree_all_puml_path == "spec-dock/tree-all.puml"
            assert write_result.tree_todo_puml_path == "spec-dock/tree.puml"
            assert write_result.deps_issues_json_path == "spec-dock/.agent/deps-issues.json"
            assert write_result.deps_issues_puml_path == "spec-dock/deps-issues.puml"
            assert write_result.dashboard_md_path == "spec-dock/dashboard.md"

            index_all_path = repo_root / write_result.index_all_path
            tree_all_path = repo_root / write_result.tree_all_path
            assert index_all_path.exists()
            assert tree_all_path.exists()

            index_all = json.loads(index_all_path.read_text(encoding="utf-8"))
            tree_all = json.loads(tree_all_path.read_text(encoding="utf-8"))
            assert "iss-00321" in index_all["nodes"]
            assert "iss-00321" in json.dumps(tree_all, ensure_ascii=False)

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

            assert result.post_import_sync.artifact_failure is not None
            assert result.post_import_sync.artifact_failure.status == "failed_partial_or_stale"
            assert "artifact write failed" in result.post_import_sync.artifact_failure.reason
            assert (result.node.path / ".meta.json").exists()

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
                return original_execute(plan, ports_arg)

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

            assert len(calls) == 1
            assert calls[0][0] == "iss-00909"
            assert result.node.id == "iss-00909"
            rules_link = result.node.path / "discussions" / "rules.md"
            rules_target = specdock_dir / "docs" / "rules" / "issue" / "discussions.md"
            assert rules_link.is_symlink(), f"missing imported rules symlink: {rules_link}"
            assert rules_link.resolve() == rules_target.resolve()
            assert str(rules_link.readlink()) == os.path.relpath(rules_target, start=rules_link.parent)
            assert list(result.node.path.rglob("new-*")) == []

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
        assert text.stdout_lines == [
            (
                "spec-dock: ok (import issue) "
                "id=iss-00123 epic=epic-local-00001 initiative=init-local-00001 "
                "path=spec-dock/initiatives/init-local-00001-auth/epics/epic-local-00001-jwt/"
                "issues/iss-00123-imported-issue github=#123"
            )
        ]
        assert text.warnings == ["gh_index_incomplete"]

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
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
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
                target_repo_owner=None,
                target_repo_name=None,
                allow_foreign_url=False,
                epic_id="epic-local-00001",
            ),
            use_cases,
        )

        assert len(calls) == 1
        assert calls[0].issue_number == 123
        assert calls[0].parent_id == "epic-local-00001"
        assert outcome.exit_code == 0
        assert "spec-dock: ok (import issue)" in "\n".join(outcome.text.stdout_lines)

    def test_import_command_returns_nonzero_when_post_sync_artifact_failure_exists(self) -> None:
        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
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
                path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001/epics/epic-local-00001/issues/iss-00123-imported-issue"
                ),
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
                target_repo_owner=None,
                target_repo_name=None,
                allow_foreign_url=False,
                epic_id="epic-local-00001",
            ),
            _UseCases(),
        )
        assert outcome.exit_code == 1
        assert "import_post_sync_failed" in outcome.text.warnings
