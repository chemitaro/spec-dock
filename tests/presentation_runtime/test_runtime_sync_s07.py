import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

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
        from spec_dock_runtime.application import contracts as app_contracts
        from spec_dock_runtime.application import ports as app_ports
        from spec_dock_runtime.application import sync_state as app_sync_state
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.infra import artifact_writer as infra_artifact_writer
        from spec_dock_runtime.infra import contracts as infra_contracts
        from spec_dock_runtime.presentation import cli_text as presentation_cli_text
    finally:
        sys.path.pop(0)
    return (
        runtime_app,
        app_contracts,
        app_ports,
        app_sync_state,
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


class _StubNodeReader:
    def __init__(self, records):
        self._records = list(records)

    def load_node_records(self):
        return list(self._records)


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
        self._statuses = dict(statuses)

    def load_cached_issue_status_by_id(self, specdock_dir):
        del specdock_dir
        return dict(self._statuses)


class _StubIssueGateway:
    def __init__(self, snapshots=None, fail=False, foreign_snapshots=None):
        self._snapshots = list(snapshots or [])
        self._fail = fail
        self._foreign_snapshots = dict(foreign_snapshots or {})
        self.view_calls: list[tuple[str, int, str | None]] = []

    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        if self._fail:
            raise RuntimeError("gh fetch failed")
        return list(self._snapshots)

    def issue_view_snapshot(self, repo_root, issue_number, *, repo_slug=None):
        if self._fail:
            raise RuntimeError("gh fetch failed")
        key = (str(repo_slug or ""), int(issue_number))
        self.view_calls.append((str(repo_root), int(issue_number), repo_slug))
        snapshot = self._foreign_snapshots.get(key)
        if snapshot is None:
            raise RuntimeError(f"gh fetch failed: {repo_slug}#{issue_number}")
        return snapshot


class _StubClock:
    def now_iso(self):
        return "2026-03-12T00:00:00Z"


class _StubGitGateway:
    def __init__(self, branch, repo_slug: str | None = "current/repo"):
        self._branch = branch
        self._repo_slug = repo_slug

    def current_branch_or_none(self, repo_root):
        del repo_root
        return self._branch

    def origin_github_repo_slug(self, repo_root):
        del repo_root
        if self._repo_slug is None:
            raise RuntimeError("origin not configured")
        return self._repo_slug


class _StubActiveStateStore:
    def __init__(self, infra_contracts, events):
        self._infra_contracts = infra_contracts
        self.events = events
        self._manifest = None

    def load_active_manifest(self, specdock_dir):
        self.events.append("active.load.migrate")
        return self._infra_contracts.ActiveManifestLoadResult(
            manifest=self._manifest,
            source="none",
            warnings=[],
        )

    def load_active_manifest_no_migrate(self, specdock_dir):
        self.events.append("active.load.no_migrate")
        return self._infra_contracts.ActiveManifestLoadResult(
            manifest=self._manifest,
            source="none",
            warnings=[],
        )

    def load_active_issue_id(self, specdock_dir):
        del specdock_dir
        if self._manifest is None or self._manifest.issue is None:
            return None
        return self._manifest.issue.id

    def snapshot_current_state(self, specdock_dir):
        self.events.append("active.snapshot")
        return self._infra_contracts.ActiveStateSnapshot(
            manifest=self._manifest,
            context_pack_text=None,
            active_json_text=None,
            managed_agent_state={},
        )

    def write_active_manifest(self, specdock_dir, manifest):
        self.events.append("active.write")
        self._manifest = manifest
        return manifest

    def apply_active_pointers(self, specdock_dir, manifest, rendered_context_pack):
        del specdock_dir, manifest, rendered_context_pack
        self.events.append("active.apply")

    def patch_agent_state_active_fields(self, specdock_dir, manifest):
        del specdock_dir, manifest
        self.events.append("active.patch")

    def restore_previous_state(self, specdock_dir, snapshot):
        del specdock_dir
        self.events.append("active.restore")
        self._manifest = snapshot.manifest


class _FailingArtifactWriter:
    def __init__(self, events, reason):
        self.events = events
        self.reason = reason

    def write(self, specdock_dir, bundle):
        del specdock_dir, bundle
        self.events.append("artifact.write")
        raise RuntimeError(self.reason)


class _SpyArtifactWriter:
    def __init__(self):
        self.called = False

    def write(self, specdock_dir, bundle):
        del specdock_dir, bundle
        self.called = True
        raise AssertionError("artifact writer should not be called")


class _LegacySyncRunner:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def run_sync(self, req, *, active_manifest_mode="migrate"):
        self.calls.append((req, active_manifest_mode))
        return self.result


class TestRuntimeSyncS07(unittest.TestCase):
    def _materialize_required_artifacts(self, records) -> None:
        for record in records:
            node_dir = Path(record.path)
            node_dir.mkdir(parents=True, exist_ok=True)
            Path(record.meta_path).write_text(
                json.dumps({"id": record.id, "kind": record.kind}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            for doc_name in _REQUIRED_NODE_DOCS:
                (node_dir / doc_name).write_text(f"# {doc_name}\n", encoding="utf-8")

    def _records(self, infra_contracts, repo_root: Path):
        base = repo_root / "spec-dock" / "initiatives" / "init-local-00001-auth"
        epic = base / "epics" / "epic-local-00001-core"
        iss1 = epic / "issues" / "iss-local-00001-api"
        iss2 = epic / "issues" / "iss-local-00002-db"
        records = [
            _record(
                infra_contracts,
                kind="initiative",
                node_id="init-local-00001",
                title="Auth",
                path=base,
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=101,
            ),
            _record(
                infra_contracts,
                kind="epic",
                node_id="epic-local-00001",
                title="Core",
                path=epic,
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=201,
            ),
            _record(
                infra_contracts,
                kind="issue",
                node_id="iss-local-00001",
                title="API",
                path=iss1,
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=301,
            ),
            _record(
                infra_contracts,
                kind="issue",
                node_id="iss-local-00002",
                title="DB",
                path=iss2,
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=302,
            ),
        ]
        self._materialize_required_artifacts(records)
        return records

    def _request(self, app_contracts, *, force=False, update_active=False):
        return app_contracts.SyncRequest(
            force=force,
            github_enabled=False,
            issue_limit=10000,
            update_active_from_branch=update_active,
        )

    def test_sync_use_case_writes_artifacts_and_paths(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            _domain_models,
            infra_artifact_writer,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
            events: list[str] = []
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": ["iss-local-00002"], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader(
                    {"iss-local-00001": "open", "iss-local-00002": "done"}
                ),
                issue_gateway=_StubIssueGateway([]),
                active_state_store=_StubActiveStateStore(infra_contracts, events),
                git_gateway=_StubGitGateway("main"),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                clock=_StubClock(),
            )

            result = app_sync_state.sync(self._request(app_contracts), ports)
            self.assertIsNone(result.artifact_failure)
            self.assertIsNotNone(result.write_result)
            self.assertEqual(result.state.generated_at, "2026-03-12T00:00:00Z")
            self.assertEqual(
                result.write_result.index_all_path,
                "spec-dock/.agent/index-all.json",
            )
            self.assertEqual(
                result.write_result.dashboard_md_path,
                "spec-dock/dashboard.md",
            )

            index_todo = json.loads((specdock_dir / ".agent" / "index.json").read_text(encoding="utf-8"))
            index_all = json.loads((specdock_dir / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            tree_todo = json.loads((specdock_dir / ".agent" / "tree.json").read_text(encoding="utf-8"))
            tree_all = json.loads((specdock_dir / ".agent" / "tree-all.json").read_text(encoding="utf-8"))
            self.assertTrue(index_todo["deps"]["valid"])
            self.assertIsNone(index_todo["deps"]["error"])
            self.assertIn("iss-local-00001", index_todo["nodes"])
            self.assertNotIn("iss-local-00002", index_todo["nodes"])
            self.assertIn("iss-local-00002", index_all["nodes"])

            def _index_paths(payload: dict[str, object]) -> list[str]:
                nodes = payload.get("nodes")
                if not isinstance(nodes, dict):
                    return []
                paths: list[str] = []
                for item in nodes.values():
                    if isinstance(item, dict) and isinstance(item.get("path"), str):
                        paths.append(item["path"])
                return paths

            def _tree_paths(tree_payload: dict[str, object]) -> list[str]:
                out: list[str] = []
                roots = tree_payload.get("tree")
                if not isinstance(roots, list):
                    return out
                for initiative in roots:
                    if not isinstance(initiative, dict):
                        continue
                    init_path = initiative.get("path")
                    if isinstance(init_path, str):
                        out.append(init_path)
                    for epic in initiative.get("epics", []):
                        if not isinstance(epic, dict):
                            continue
                        epic_path = epic.get("path")
                        if isinstance(epic_path, str):
                            out.append(epic_path)
                        for issue in epic.get("issues", []):
                            if isinstance(issue, dict) and isinstance(issue.get("path"), str):
                                out.append(issue["path"])
                return out

            node_paths = (
                _index_paths(index_all)
                + _index_paths(index_todo)
                + _tree_paths(tree_all)
                + _tree_paths(tree_todo)
            )
            self.assertTrue(node_paths)
            for node_path in node_paths:
                self.assertTrue(node_path.startswith("spec-dock/"), node_path)
                self.assertFalse(Path(node_path).is_absolute(), node_path)
                self.assertFalse(node_path.startswith(repo_root.as_posix()), node_path)

            deps_issues = json.loads((specdock_dir / ".agent" / "deps-issues.json").read_text(encoding="utf-8"))
            self.assertTrue(deps_issues["deps"]["valid"])
            self.assertIn("iss-local-00001", deps_issues["nodes"])
            self.assertNotIn("iss-local-00002", deps_issues["nodes"])

            tree_puml = (specdock_dir / "tree.puml").read_text(encoding="utf-8")
            deps_puml = (specdock_dir / "deps-issues.puml").read_text(encoding="utf-8")
            dashboard = (specdock_dir / "dashboard.md").read_text(encoding="utf-8")
            self.assertIn("@startuml", tree_puml)
            self.assertIn("@startuml", deps_puml)
            self.assertIn("## Ready", dashboard)

    def test_sync_deps_cycle_fail_fast_regression(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            _domain_models,
            _infra_artifact_writer,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {
                        "iss-local-00001": ["iss-local-00002"],
                        "iss-local-00002": ["iss-local-00001"],
                    },
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main"),
                clock=_StubClock(),
            )
            with self.assertRaisesRegex(RuntimeError, "Dependency cycle detected"):
                app_sync_state.collect_sync_state(self._request(app_contracts), ports)

    def test_sync_force_placeholder_and_deps_error_regression(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            _domain_models,
            infra_artifact_writer,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {
                        "iss-local-00001": ["iss-local-00002"],
                        "iss-local-00002": ["iss-local-00001"],
                    },
                ),
                derived_state_reader=_StubDerivedStateReader(
                    {"iss-local-00001": "open", "iss-local-00002": "open"}
                ),
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main"),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                clock=_StubClock(),
            )

            result = app_sync_state.sync(self._request(app_contracts, force=True), ports)
            self.assertIsNone(result.artifact_failure)
            self.assertIsNotNone(result.write_result)
            self.assertEqual(result.state.warnings, ["deps_preflight_failed"])

            index = json.loads((specdock_dir / ".agent" / "index.json").read_text(encoding="utf-8"))
            self.assertFalse(index["deps"]["valid"])
            self.assertIn("Dependency cycle detected", str(index["deps"]["error"]))

            deps_issues = json.loads((specdock_dir / ".agent" / "deps-issues.json").read_text(encoding="utf-8"))
            self.assertFalse(deps_issues["deps"]["valid"])
            self.assertIn("Dependency cycle detected", str(deps_issues["deps"]["error"]))

            tree_puml = (specdock_dir / "tree.puml").read_text(encoding="utf-8")
            deps_puml = (specdock_dir / "deps-issues.puml").read_text(encoding="utf-8")
            dashboard = (specdock_dir / "dashboard.md").read_text(encoding="utf-8")
            for text in (tree_puml, deps_puml, dashboard):
                self.assertIn("DEPS_DISABLED", text)
                self.assertIn("sync --force", text)

    def test_sync_prefers_foreign_repo_snapshot_for_foreign_linked_issue(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            domain_models,
            infra_artifact_writer,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
            records[2] = _record(
                infra_contracts,
                kind="issue",
                node_id="iss-local-00001",
                title="API",
                path=Path(records[2].path),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=301,
                github_repo_owner="other",
                github_repo_name="repo",
            )
            issue_gateway = _StubIssueGateway(
                snapshots=[
                    domain_models.IssueSnapshot(
                        issue_number=301,
                        state="OPEN",
                        title="Current repo #301",
                        labels=[],
                        updated_at="2026-03-18T00:00:00Z",
                        url="https://github.com/current/repo/issues/301",
                        repo_owner="current",
                        repo_name="repo",
                    ),
                    domain_models.IssueSnapshot(
                        issue_number=302,
                        state="OPEN",
                        title="Current repo #302",
                        labels=[],
                        updated_at="2026-03-18T00:00:00Z",
                        url="https://github.com/current/repo/issues/302",
                        repo_owner="current",
                        repo_name="repo",
                    ),
                ],
                foreign_snapshots={
                    ("other/repo", 301): domain_models.IssueSnapshot(
                        issue_number=301,
                        state="CLOSED",
                        title="Foreign #301",
                        labels=["bugfix"],
                        updated_at="2026-03-18T02:00:00Z",
                        url="https://github.com/other/repo/issues/301",
                        repo_owner="other",
                        repo_name="repo",
                    )
                },
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader(
                    {"iss-local-00001": "open", "iss-local-00002": "open"}
                ),
                issue_gateway=issue_gateway,
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main"),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                clock=_StubClock(),
            )

            result = app_sync_state.sync(
                app_contracts.SyncRequest(
                    force=False,
                    github_enabled=True,
                    issue_limit=10000,
                    update_active_from_branch=False,
                ),
                ports,
            )
            self.assertIsNone(result.artifact_failure)
            status = result.state.issue_statuses["iss-local-00001"]
            self.assertEqual(status.source, "github")
            self.assertEqual(status.effective_status, "done")
            self.assertEqual(issue_gateway.view_calls, [(str(repo_root), 301, "other/repo")])

            index_all = json.loads((specdock_dir / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            issue_payload = index_all["nodes"]["iss-local-00001"]["github"]
            self.assertEqual(issue_payload["url"], "https://github.com/other/repo/issues/301")
            self.assertEqual(issue_payload["state"], "CLOSED")
            self.assertEqual(issue_payload["repo_owner"], "other")
            self.assertEqual(issue_payload["repo_name"], "repo")

    def test_sync_does_not_mix_snapshots_when_current_and_foreign_share_same_issue_number(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            domain_models,
            infra_artifact_writer,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
            records[3] = _record(
                infra_contracts,
                kind="issue",
                node_id="iss-local-00002",
                title="DB",
                path=Path(records[3].path),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=301,
                github_repo_owner="other",
                github_repo_name="repo",
            )
            issue_gateway = _StubIssueGateway(
                snapshots=[
                    domain_models.IssueSnapshot(
                        issue_number=301,
                        state="OPEN",
                        title="Current repo #301",
                        labels=[],
                        updated_at="2026-03-18T00:00:00Z",
                        url="https://github.com/current/repo/issues/301",
                        repo_owner="current",
                        repo_name="repo",
                    ),
                ],
                foreign_snapshots={
                    ("other/repo", 301): domain_models.IssueSnapshot(
                        issue_number=301,
                        state="CLOSED",
                        title="Foreign #301",
                        labels=["bugfix"],
                        updated_at="2026-03-18T02:00:00Z",
                        url="https://github.com/other/repo/issues/301",
                        repo_owner="other",
                        repo_name="repo",
                    )
                },
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader(
                    {"iss-local-00001": "open", "iss-local-00002": "open"}
                ),
                issue_gateway=issue_gateway,
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main"),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                clock=_StubClock(),
            )

            result = app_sync_state.sync(
                app_contracts.SyncRequest(
                    force=False,
                    github_enabled=True,
                    issue_limit=10000,
                    update_active_from_branch=False,
                ),
                ports,
            )
            self.assertIsNone(result.artifact_failure)
            self.assertEqual(issue_gateway.view_calls, [(str(repo_root), 301, "other/repo")])

            current_status = result.state.issue_statuses["iss-local-00001"]
            foreign_status = result.state.issue_statuses["iss-local-00002"]
            self.assertEqual(current_status.source, "github")
            self.assertEqual(current_status.effective_status, "open")
            self.assertEqual(foreign_status.source, "github")
            self.assertEqual(foreign_status.effective_status, "done")
            self.assertEqual(
                result.state.github_snapshot_by_repo_and_issue_number[("current/repo", 301)].url,
                "https://github.com/current/repo/issues/301",
            )
            self.assertEqual(
                result.state.github_snapshot_by_repo_and_issue_number[("other/repo", 301)].url,
                "https://github.com/other/repo/issues/301",
            )

            index_all = json.loads((specdock_dir / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            current_payload = index_all["nodes"]["iss-local-00001"]["github"]
            foreign_payload = index_all["nodes"]["iss-local-00002"]["github"]
            self.assertEqual(current_payload["url"], "https://github.com/current/repo/issues/301")
            self.assertEqual(current_payload["state"], "OPEN")
            self.assertEqual(foreign_payload["url"], "https://github.com/other/repo/issues/301")
            self.assertEqual(foreign_payload["state"], "CLOSED")

    def test_sync_does_not_apply_foreign_snapshot_to_current_unscoped_issue_when_current_snapshot_missing(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            domain_models,
            infra_artifact_writer,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
            records[3] = _record(
                infra_contracts,
                kind="issue",
                node_id="iss-local-00002",
                title="DB",
                path=Path(records[3].path),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=301,
                github_repo_owner="other",
                github_repo_name="repo",
            )
            issue_gateway = _StubIssueGateway(
                snapshots=[
                    domain_models.IssueSnapshot(
                        issue_number=302,
                        state="OPEN",
                        title="Current repo #302",
                        labels=[],
                        updated_at="2026-03-18T00:00:00Z",
                        url="https://github.com/current/repo/issues/302",
                        repo_owner="current",
                        repo_name="repo",
                    ),
                ],
                foreign_snapshots={
                    ("other/repo", 301): domain_models.IssueSnapshot(
                        issue_number=301,
                        state="CLOSED",
                        title="Foreign #301",
                        labels=["bugfix"],
                        updated_at="2026-03-18T02:00:00Z",
                        url="https://github.com/other/repo/issues/301",
                        repo_owner="other",
                        repo_name="repo",
                    )
                },
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader(
                    {"iss-local-00001": "open", "iss-local-00002": "open"}
                ),
                issue_gateway=issue_gateway,
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main"),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                clock=_StubClock(),
            )

            result = app_sync_state.sync(
                app_contracts.SyncRequest(
                    force=False,
                    github_enabled=True,
                    issue_limit=10000,
                    update_active_from_branch=False,
                ),
                ports,
            )
            self.assertIsNone(result.artifact_failure)
            self.assertIn("gh_index_incomplete", result.state.warnings)
            self.assertEqual(issue_gateway.view_calls, [(str(repo_root), 301, "other/repo")])

            current_status = result.state.issue_statuses["iss-local-00001"]
            foreign_status = result.state.issue_statuses["iss-local-00002"]
            self.assertEqual(current_status.source, "unknown")
            self.assertEqual(current_status.effective_status, "unknown")
            self.assertEqual(foreign_status.source, "github")
            self.assertEqual(foreign_status.effective_status, "done")

            index_all = json.loads((specdock_dir / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            current_payload = index_all["nodes"]["iss-local-00001"]["github"]
            foreign_payload = index_all["nodes"]["iss-local-00002"]["github"]
            self.assertEqual(current_payload["issue_number"], 301)
            self.assertNotIn("url", current_payload)
            self.assertNotIn("state", current_payload)
            self.assertEqual(foreign_payload["url"], "https://github.com/other/repo/issues/301")
            self.assertEqual(foreign_payload["state"], "CLOSED")

    def test_sync_prefers_foreign_repo_snapshot_for_foreign_linked_initiative_and_epic(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            domain_models,
            infra_artifact_writer,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
            records[0] = _record(
                infra_contracts,
                kind="initiative",
                node_id="init-local-00001",
                title="Auth",
                path=Path(records[0].path),
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=101,
                github_repo_owner="upstream",
                github_repo_name="product",
            )
            records[1] = _record(
                infra_contracts,
                kind="epic",
                node_id="epic-local-00001",
                title="Core",
                path=Path(records[1].path),
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=201,
                github_repo_owner="upstream",
                github_repo_name="product",
            )
            issue_gateway = _StubIssueGateway(
                snapshots=[
                    domain_models.IssueSnapshot(
                        issue_number=101,
                        state="OPEN",
                        title="Current repo #101",
                        labels=[],
                        updated_at="2026-03-18T00:00:00Z",
                        url="https://github.com/current/repo/issues/101",
                        repo_owner="current",
                        repo_name="repo",
                    ),
                    domain_models.IssueSnapshot(
                        issue_number=201,
                        state="OPEN",
                        title="Current repo #201",
                        labels=[],
                        updated_at="2026-03-18T00:00:00Z",
                        url="https://github.com/current/repo/issues/201",
                        repo_owner="current",
                        repo_name="repo",
                    ),
                    domain_models.IssueSnapshot(
                        issue_number=301,
                        state="OPEN",
                        title="Current repo #301",
                        labels=[],
                        updated_at="2026-03-18T00:00:00Z",
                        url="https://github.com/current/repo/issues/301",
                        repo_owner="current",
                        repo_name="repo",
                    ),
                    domain_models.IssueSnapshot(
                        issue_number=302,
                        state="OPEN",
                        title="Current repo #302",
                        labels=[],
                        updated_at="2026-03-18T00:00:00Z",
                        url="https://github.com/current/repo/issues/302",
                        repo_owner="current",
                        repo_name="repo",
                    ),
                ],
                foreign_snapshots={
                    ("upstream/product", 101): domain_models.IssueSnapshot(
                        issue_number=101,
                        state="CLOSED",
                        title="Foreign init #101",
                        labels=["roadmap"],
                        updated_at="2026-03-18T01:00:00Z",
                        url="https://github.com/upstream/product/issues/101",
                        repo_owner="upstream",
                        repo_name="product",
                    ),
                    ("upstream/product", 201): domain_models.IssueSnapshot(
                        issue_number=201,
                        state="CLOSED",
                        title="Foreign epic #201",
                        labels=["backend"],
                        updated_at="2026-03-18T01:10:00Z",
                        url="https://github.com/upstream/product/issues/201",
                        repo_owner="upstream",
                        repo_name="product",
                    ),
                },
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader(
                    {"iss-local-00001": "open", "iss-local-00002": "open"}
                ),
                issue_gateway=issue_gateway,
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main"),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                clock=_StubClock(),
            )

            result = app_sync_state.sync(
                app_contracts.SyncRequest(
                    force=False,
                    github_enabled=True,
                    issue_limit=10000,
                    update_active_from_branch=False,
                ),
                ports,
            )
            self.assertIsNone(result.artifact_failure)
            self.assertEqual(
                issue_gateway.view_calls,
                [
                    (str(repo_root), 101, "upstream/product"),
                    (str(repo_root), 201, "upstream/product"),
                ],
            )

            index_all = json.loads((specdock_dir / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            init_payload = index_all["nodes"]["init-local-00001"]["github"]
            epic_payload = index_all["nodes"]["epic-local-00001"]["github"]
            self.assertEqual(init_payload["url"], "https://github.com/upstream/product/issues/101")
            self.assertEqual(init_payload["state"], "CLOSED")
            self.assertEqual(epic_payload["url"], "https://github.com/upstream/product/issues/201")
            self.assertEqual(epic_payload["state"], "CLOSED")

    def test_sync_keeps_local_issue_snapshot_when_foreign_repo_uses_same_issue_number(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            domain_models,
            infra_artifact_writer,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
            records[0] = _record(
                infra_contracts,
                kind="initiative",
                node_id="init-local-00001",
                title="Auth",
                path=Path(records[0].path),
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=301,
                github_repo_owner="upstream",
                github_repo_name="product",
            )
            issue_gateway = _StubIssueGateway(
                snapshots=[
                    domain_models.IssueSnapshot(
                        issue_number=201,
                        state="OPEN",
                        title="Current repo #201",
                        labels=[],
                        updated_at="2026-03-18T00:00:00Z",
                        url="https://github.com/current/repo/issues/201",
                        repo_owner="current",
                        repo_name="repo",
                    ),
                    domain_models.IssueSnapshot(
                        issue_number=301,
                        state="OPEN",
                        title="Current repo #301",
                        labels=[],
                        updated_at="2026-03-18T00:00:00Z",
                        url="https://github.com/current/repo/issues/301",
                        repo_owner="current",
                        repo_name="repo",
                    ),
                    domain_models.IssueSnapshot(
                        issue_number=302,
                        state="OPEN",
                        title="Current repo #302",
                        labels=[],
                        updated_at="2026-03-18T00:00:00Z",
                        url="https://github.com/current/repo/issues/302",
                        repo_owner="current",
                        repo_name="repo",
                    ),
                ],
                foreign_snapshots={
                    ("upstream/product", 301): domain_models.IssueSnapshot(
                        issue_number=301,
                        state="CLOSED",
                        title="Foreign #301",
                        labels=["roadmap"],
                        updated_at="2026-03-18T01:00:00Z",
                        url="https://github.com/upstream/product/issues/301",
                        repo_owner="upstream",
                        repo_name="product",
                    ),
                },
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader(
                    {"iss-local-00001": "open", "iss-local-00002": "open"}
                ),
                issue_gateway=issue_gateway,
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main"),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                clock=_StubClock(),
            )

            result = app_sync_state.sync(
                app_contracts.SyncRequest(
                    force=False,
                    github_enabled=True,
                    issue_limit=10000,
                    update_active_from_branch=False,
                ),
                ports,
            )
            self.assertIsNone(result.artifact_failure)
            self.assertEqual(issue_gateway.view_calls, [(str(repo_root), 301, "upstream/product")])
            issue_status = result.state.issue_statuses["iss-local-00001"]
            self.assertEqual(issue_status.source, "github")
            self.assertEqual(issue_status.effective_status, "open")

            index_all = json.loads((specdock_dir / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            issue_payload = index_all["nodes"]["iss-local-00001"]["github"]
            initiative_payload = index_all["nodes"]["init-local-00001"]["github"]
            self.assertEqual(issue_payload["url"], "https://github.com/current/repo/issues/301")
            self.assertEqual(issue_payload["state"], "OPEN")
            self.assertEqual(initiative_payload["url"], "https://github.com/upstream/product/issues/301")
            self.assertEqual(initiative_payload["state"], "CLOSED")

    def test_sync_does_not_fallback_to_same_number_other_repo_snapshot_in_json(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            domain_models,
            infra_artifact_writer,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
            records[2] = _record(
                infra_contracts,
                kind="issue",
                node_id="iss-local-00001",
                title="API",
                path=Path(records[2].path),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=301,
                github_repo_owner="other",
                github_repo_name="repo",
            )
            issue_gateway = _StubIssueGateway(
                snapshots=[
                    domain_models.IssueSnapshot(
                        issue_number=301,
                        state="OPEN",
                        title="Current repo #301",
                        labels=[],
                        updated_at="2026-03-18T00:00:00Z",
                        url="https://github.com/current/repo/issues/301",
                        repo_owner="current",
                        repo_name="repo",
                    ),
                    domain_models.IssueSnapshot(
                        issue_number=302,
                        state="OPEN",
                        title="Current repo #302",
                        labels=[],
                        updated_at="2026-03-18T00:00:00Z",
                        url="https://github.com/current/repo/issues/302",
                        repo_owner="current",
                        repo_name="repo",
                    ),
                ],
                foreign_snapshots={},
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader(
                    {"iss-local-00001": "open", "iss-local-00002": "open"}
                ),
                issue_gateway=issue_gateway,
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main"),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                clock=_StubClock(),
            )

            result = app_sync_state.sync(
                app_contracts.SyncRequest(
                    force=False,
                    github_enabled=True,
                    issue_limit=10000,
                    update_active_from_branch=False,
                ),
                ports,
            )
            self.assertIsNone(result.artifact_failure)
            self.assertIn("gh_fetch_failed", result.state.warnings)
            self.assertEqual(issue_gateway.view_calls, [(str(repo_root), 301, "other/repo")])
            issue_status = result.state.issue_statuses["iss-local-00001"]
            self.assertEqual(issue_status.source, "unknown")
            self.assertEqual(issue_status.effective_status, "unknown")

            index_all = json.loads((specdock_dir / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            issue_payload = index_all["nodes"]["iss-local-00001"]["github"]
            self.assertEqual(issue_payload["issue_number"], 301)
            self.assertEqual(issue_payload["repo_owner"], "other")
            self.assertEqual(issue_payload["repo_name"], "repo")
            self.assertNotIn("url", issue_payload)
            self.assertNotIn("state", issue_payload)
            self.assertNotIn("updated_at", issue_payload)
            self.assertNotIn("labels", issue_payload)

    def test_sync_active_update_then_artifact_failure_is_non_atomic(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            _domain_models,
            _infra_artifact_writer,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
            events: list[str] = []
            active_store = _StubActiveStateStore(infra_contracts, events)
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": ["iss-local-00002"], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader(
                    {"iss-local-00001": "open", "iss-local-00002": "done"}
                ),
                active_state_store=active_store,
                git_gateway=_StubGitGateway("feature/iss-local-00001-implement"),
                artifact_writer=_FailingArtifactWriter(events, "disk full"),
                clock=_StubClock(),
            )

            result = app_sync_state.sync(
                self._request(app_contracts, force=False, update_active=True),
                ports,
            )
            self.assertIsNotNone(result.artifact_failure)
            self.assertEqual(result.artifact_failure.status, "failed_partial_or_stale")
            self.assertEqual(result.artifact_failure.reason, "disk full")
            self.assertIsNotNone(result.active_update)
            self.assertTrue(result.active_update.applied)
            self.assertEqual(result.state.active.issue_id, "iss-local-00001")
            self.assertIn("active.write", events)
            self.assertIn("artifact.write", events)
            self.assertLess(events.index("active.write"), events.index("artifact.write"))

    def test_sync_artifact_failure_contract_when_active_not_updated(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            _domain_models,
            _infra_artifact_writer,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": ["iss-local-00002"], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader(
                    {"iss-local-00001": "open", "iss-local-00002": "done"}
                ),
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("feature/iss-local-00001-implement"),
                artifact_writer=_FailingArtifactWriter([], "read-only fs"),
                clock=_StubClock(),
            )
            result = app_sync_state.sync(self._request(app_contracts), ports)
            self.assertIsNotNone(result.artifact_failure)
            self.assertEqual(result.artifact_failure.status, "failed_partial_or_stale")
            self.assertEqual(result.artifact_failure.reason, "read-only fs")
            self.assertIsNone(result.active_update)

    def test_sync_prewrite_failure_contract_is_failed_before_write(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            _domain_models,
            _infra_artifact_writer,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
            spy_writer = _SpyArtifactWriter()
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": ["iss-local-00002"], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader(
                    {"iss-local-00001": "open", "iss-local-00002": "done"}
                ),
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("feature/iss-local-00001-implement"),
                artifact_writer=spy_writer,
                clock=_StubClock(),
            )

            original_render_dashboard = app_sync_state.render_dashboard
            app_sync_state.render_dashboard = lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("render failed"))
            try:
                result = app_sync_state.sync(self._request(app_contracts), ports)
            finally:
                app_sync_state.render_dashboard = original_render_dashboard

            self.assertFalse(spy_writer.called)
            self.assertIsNotNone(result.artifact_failure)
            self.assertEqual(result.artifact_failure.status, "failed_before_write")
            self.assertEqual(result.artifact_failure.reason, "render failed")

    def test_render_sync_text_regression(self) -> None:
        (
            _runtime_app,
            app_contracts,
            _app_ports,
            _app_sync_state,
            domain_models,
            _infra_artifact_writer,
            _infra_contracts,
            presentation_cli_text,
        ) = _runtime_modules()

        state = app_contracts.SyncStateResult(
            graph=domain_models.SpecGraph(nodes_by_id={}),
            active=None,
            issue_statuses={},
            progress=domain_models.ProgressMap(by_node_id={}, counts={}),
            deps_state=domain_models.DepsState(nodes=[], warnings=[]),
            deps_eval_by_id={},
            generated_at="2026-03-12T00:00:00Z",
            warnings=["warn-1", "warn-2"],
            deps_preflight_error=None,
        )
        success = presentation_cli_text.render_sync_text(
            app_contracts.SyncCommandResult(
                state=state,
                write_result=app_contracts.ArtifactWriteResult(
                    index_all_path="spec-dock/.agent/index-all.json",
                    index_todo_path="spec-dock/.agent/index.json",
                    tree_all_path="spec-dock/.agent/tree-all.json",
                    tree_todo_path="spec-dock/.agent/tree.json",
                    tree_all_puml_path="spec-dock/tree-all.puml",
                    tree_todo_puml_path="spec-dock/tree.puml",
                    deps_issues_json_path="spec-dock/.agent/deps-issues.json",
                    deps_issues_puml_path="spec-dock/deps-issues.puml",
                    dashboard_md_path="spec-dock/dashboard.md",
                ),
                active_update=app_contracts.ActiveUpdateOutcome(applied=False, reason="no match"),
                artifact_failure=None,
            )
        )
        self.assertIn("spec-dock/.agent/index-all.json", success.stdout_lines[0])
        self.assertEqual(
            success.stderr_lines,
            ["spec-dock: sync: active unchanged (no match)"],
        )
        self.assertEqual(success.warnings, ["warn-1", "warn-2"])

        failed = presentation_cli_text.render_sync_text(
            app_contracts.SyncCommandResult(
                state=state,
                write_result=None,
                active_update=app_contracts.ActiveUpdateOutcome(applied=True, reason="matched"),
                artifact_failure=app_contracts.ArtifactWriteFailure(
                    status="failed_partial_or_stale",
                    reason="io failed",
                ),
            )
        )
        self.assertIn("status=failed_partial_or_stale", failed.stderr_lines[0])
        self.assertIn("stale", failed.stderr_lines[1])

    def test_sync_exit_behavior_regression(self) -> None:
        (
            runtime_app,
            app_contracts,
            _app_ports,
            _app_sync_state,
            domain_models,
            _infra_artifact_writer,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()

        delegated_state = app_contracts.SyncStateResult(
            graph=domain_models.SpecGraph(nodes_by_id={}),
            active=None,
            issue_statuses={},
            progress=domain_models.ProgressMap(by_node_id={}, counts={}),
            deps_state=domain_models.DepsState(nodes=[], warnings=[]),
            deps_eval_by_id={},
            generated_at="2026-03-12T00:00:00Z",
            warnings=[],
            deps_preflight_error=None,
        )

        def _build_use_cases(sync_impl):
            return app_contracts.UseCases(
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
                sync=sync_impl,
                check_deps=lambda req: None,  # type: ignore[return-value]
                validate_tree=lambda req: None,  # type: ignore[return-value]
            )

        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_build_runtime = runtime_app._cli_build_runtime
        runtime_app._find_specdock_dir = lambda: Path("/repo/spec-dock")
        self.assertFalse(hasattr(runtime_app, "_sync"))
        try:
            runtime_app._cli_build_runtime = lambda _specdock_dir: SimpleNamespace(
                use_cases=_build_use_cases(
                    lambda _req: app_contracts.SyncCommandResult(
                        state=delegated_state,
                        write_result=None,
                        active_update=None,
                        artifact_failure=None,
                    )
                )
            )
            out = io.StringIO()
            err = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                exit_code_ok = runtime_app.main(["sync"])
            self.assertEqual(exit_code_ok, 0)

            runtime_app._cli_build_runtime = lambda _specdock_dir: SimpleNamespace(
                use_cases=_build_use_cases(lambda _req: (_ for _ in ()).throw(RuntimeError("sync failed")))
            )
            out = io.StringIO()
            err = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                exit_code_ng = runtime_app.main(["sync"])
            self.assertEqual(exit_code_ng, 1)
            self.assertIn("error: sync failed", err.getvalue())
        finally:
            runtime_app._find_specdock_dir = original_find_specdock_dir
            runtime_app._cli_build_runtime = original_build_runtime

    def test_legacy_delegated_sync_smoke(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            domain_models,
            _infra_artifact_writer,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()

        delegated_state = app_contracts.SyncStateResult(
            graph=domain_models.SpecGraph(nodes_by_id={}),
            active=None,
            issue_statuses={},
            progress=domain_models.ProgressMap(by_node_id={}, counts={}),
            deps_state=domain_models.DepsState(nodes=[], warnings=[]),
            deps_eval_by_id={},
            generated_at="2026-03-12T00:00:00Z",
            warnings=[],
            deps_preflight_error=None,
        )
        delegated_result = app_contracts.SyncCommandResult(
            state=delegated_state,
            write_result=None,
            active_update=None,
            artifact_failure=None,
        )
        runner = _LegacySyncRunner(delegated_result)
        ports = app_ports.Ports(
            node_reader=_StubNodeReader([]),
            repo_root=Path("/repo"),
            sync_legacy_runner=runner,
        )
        req = self._request(app_contracts)
        result = app_sync_state.sync(req, ports)
        self.assertIs(result, delegated_result)
        self.assertEqual(len(runner.calls), 1)
        self.assertEqual(runner.calls[0][1], "migrate")

        app_sync_state.sync_after_import(ports)
        self.assertEqual(len(runner.calls), 2)
        sync_after_req, mode = runner.calls[1]
        self.assertEqual(mode, "no_migrate")
        self.assertFalse(sync_after_req.update_active_from_branch)
