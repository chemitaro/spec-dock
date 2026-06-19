import contextlib
import errno
import io
import json
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

_REQUIRED_NODE_DOCS = ("requirement.md", "design.md", "plan.md", "report.md")


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


def _presentation_json_state_module():
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
        from spec_dock_runtime.presentation import json_state as presentation_json_state
    finally:
        sys.path.pop(0)
    return presentation_json_state


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


class _StubNodeRepo:
    def __init__(self):
        self.backfill_calls: list[tuple[str, str, str]] = []

    def backfill_github_repo_scope(self, meta_path, *, repo_owner: str, repo_name: str):
        self.backfill_calls.append((str(meta_path), str(repo_owner), str(repo_name)))
        return True


class _FailingBackfillNodeRepo:
    def backfill_github_repo_scope(self, meta_path, *, repo_owner: str, repo_name: str):
        del meta_path, repo_owner, repo_name
        raise AssertionError("bulk sync must not invoke backfill_github_repo_scope")


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

    def load_node_dependency_resolutions(self, specdock_dir, graph):
        del specdock_dir, graph
        return {
            node_id: [
                self._infra_contracts.DirectDependencyResolution(
                    raw_ref=depends_on_id,
                    resolved_node_id=depends_on_id,
                )
                for depends_on_id in depends_on
            ]
            for node_id, depends_on in self._issue_depends_on_map.items()
        }


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
        self.index_calls: list[tuple[str, int]] = []
        self.view_calls: list[tuple[str, int, str | None]] = []

    def issue_index(self, repo_root, *, limit):
        self.index_calls.append((str(repo_root), int(limit)))
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


class _CapturingFailingArtifactWriter:
    def __init__(self, reason):
        self.reason = reason
        self.bundle = None

    def write(self, specdock_dir, bundle):
        del specdock_dir
        self.bundle = bundle
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


class TestRuntimeSyncS07:
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
                github_issue_number=None,
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
                github_issue_number=None,
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

    def _write_discussion_doc(
        self,
        scope_dir: Path,
        filename: str,
        *,
        front_matter_lines: list[str] | None,
    ) -> Path:
        discussions_dir = scope_dir / "discussions"
        discussions_dir.mkdir(parents=True, exist_ok=True)
        path = discussions_dir / filename
        parts: list[str] = []
        if front_matter_lines is not None:
            parts.extend(["---", *front_matter_lines, "---", ""])
        parts.extend([f"# {filename}", ""])
        path.write_text("\n".join(parts), encoding="utf-8")
        return path

    def _write_valid_adr_doc(
        self,
        scope_dir: Path,
        filename: str,
        *,
        doc_id: str,
        scope_id: str,
    ) -> Path:
        return self._write_discussion_doc(
            scope_dir,
            filename,
            front_matter_lines=[
                "種別: ADR（Architecture Decision Record）",
                f'ID: "{doc_id}"',
                'タイトル: "ADR"',
                '状態: "draft"',
                '作成者: "Tester"',
                '最終更新: "2026-03-29"',
                f'親: ["{scope_id}"]',
            ],
        )

    def _expected_sync_artifact_relpaths(self) -> set[str]:
        return {
            ".agent/index-all.json",
            ".agent/index.json",
            ".agent/tree-all.json",
            ".agent/tree.json",
            "tree-all.puml",
            "tree.puml",
            ".agent/deps-issues.json",
            "deps-issues.puml",
            "dashboard.md",
        }

    def test_collect_adr_mirror_sources_filters_to_valid_multi_scope_adr_inputs(self) -> None:
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
            initiative_dir = Path(records[0].path)
            epic_dir = Path(records[1].path)
            issue_api_dir = Path(records[2].path)
            issue_db_dir = Path(records[3].path)
            initiative_doc = self._write_valid_adr_doc(
                initiative_dir,
                "20260312t010203z-adr-init-decision.md",
                doc_id="20260312t010203z-adr",
                scope_id="init-local-00001",
            )
            epic_doc = self._write_valid_adr_doc(
                epic_dir,
                "20260312t010204z-adr-epic-decision.md",
                doc_id="20260312t010204z-adr",
                scope_id="epic-local-00001",
            )
            issue_doc = self._write_valid_adr_doc(
                issue_api_dir,
                "20260312t010205z-01-adr-issue-decision.md",
                doc_id="20260312t010205z-01-adr",
                scope_id="iss-local-00001",
            )
            self._write_valid_adr_doc(
                initiative_dir,
                "001-adr-legacy-decision.md",
                doc_id="001-adr",
                scope_id="init-local-00001",
            )
            self._write_discussion_doc(
                epic_dir,
                "20260312t010206z-adr-malformed-frontmatter.md",
                front_matter_lines=[
                    "種別: ADR（Architecture Decision Record）",
                    'タイトル: "Missing id and parent"',
                ],
            )
            self._write_discussion_doc(
                issue_api_dir,
                "notes.md",
                front_matter_lines=[
                    "種別: ADR（Architecture Decision Record）",
                    'ID: "20260312t010207z-adr"',
                    '親: ["iss-local-00001"]',
                ],
            )
            self._write_discussion_doc(
                issue_db_dir,
                "20260312t010208z-adr-parent-mismatch.md",
                front_matter_lines=[
                    "種別: ADR（Architecture Decision Record）",
                    'ID: "20260312t010208z-adr"',
                    'タイトル: "Mismatch"',
                    '状態: "draft"',
                    '作成者: "Tester"',
                    '最終更新: "2026-03-29"',
                    '親: ["epic-local-00001"]',
                ],
            )
            self._write_discussion_doc(
                issue_db_dir,
                "20260312t010209z-disc-not-an-adr.md",
                front_matter_lines=[
                    "種別: ADR（Architecture Decision Record）",
                    'ID: "20260312t010209z-disc"',
                    '親: ["iss-local-00002"]',
                ],
            )
            self._write_discussion_doc(
                issue_db_dir,
                "20260312t010210z-adr-malformed-kind.md",
                front_matter_lines=[
                    "種別: ADRoops",
                    'ID: "20260312t010210z-adr"',
                    'タイトル: "Malformed kind"',
                    '状態: "draft"',
                    '作成者: "Tester"',
                    '最終更新: "2026-03-29"',
                    '親: ["iss-local-00002"]',
                ],
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main"),
                clock=_StubClock(),
            )

            state = app_sync_state.collect_sync_state(self._request(app_contracts), ports)
            sources = app_sync_state._collect_adr_mirror_sources(state.graph)

            assert {source.source_path for source in sources} == {initiative_doc, epic_doc, issue_doc}
            assert {source.basename for source in sources} == {
                    "20260312t010203z-adr-init-decision.md",
                    "20260312t010204z-adr-epic-decision.md",
                    "20260312t010205z-01-adr-issue-decision.md",
            }

    def test_sync_fails_before_write_on_adr_mirror_basename_collision_and_preserves_adrs(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            _domain_models,
            _infra_artifact_writer,
            infra_contracts,
            presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
            initiative_dir = Path(records[0].path)
            issue_api_dir = Path(records[2].path)
            basename = "20260312t010203z-adr-shared-decision.md"
            self._write_valid_adr_doc(
                initiative_dir,
                basename,
                doc_id="20260312t010203z-adr",
                scope_id="init-local-00001",
            )
            self._write_valid_adr_doc(
                issue_api_dir,
                basename,
                doc_id="20260312t010203z-adr",
                scope_id="iss-local-00001",
            )
            adrs_dir = specdock_dir / "adrs"
            adrs_dir.mkdir(parents=True, exist_ok=True)
            sentinel = adrs_dir / "keep.txt"
            sentinel.write_text("keep-me\n", encoding="utf-8")
            spy_writer = _SpyArtifactWriter()
            events: list[str] = []
            active_store = _StubActiveStateStore(infra_contracts, events)
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                active_state_store=active_store,
                git_gateway=_StubGitGateway("feature/iss-local-00001-implement"),
                artifact_writer=spy_writer,
                clock=_StubClock(),
            )

            result = app_sync_state.sync(self._request(app_contracts, update_active=True), ports)

            assert not spy_writer.called
            assert result.artifact_failure is not None
            assert result.artifact_failure.status == "failed_before_write"
            assert "ADR mirror basename collision" in result.artifact_failure.reason
            assert basename in result.artifact_failure.reason
            assert result.active_update is None
            assert result.state.active is None
            assert sentinel.read_text(encoding="utf-8") == "keep-me\n"
            assert sorted(path.name for path in adrs_dir.iterdir()) == ["keep.txt"]
            assert events == ["active.load.migrate"]
            rendered = presentation_cli_text.render_sync_text(result)
            assert "failed (sync)" in rendered.stderr_lines[0]
            assert "ADR mirror basename collision" in rendered.stderr_lines[0]

    def test_sync_builds_flat_adr_mirror_symlinks_on_success(self) -> None:
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
            initiative_dir = Path(records[0].path)
            issue_api_dir = Path(records[2].path)
            initiative_doc = self._write_valid_adr_doc(
                initiative_dir,
                "20260312t010203z-adr-init-decision.md",
                doc_id="20260312t010203z-adr",
                scope_id="init-local-00001",
            )
            issue_doc = self._write_valid_adr_doc(
                issue_api_dir,
                "20260312t010205z-01-adr-issue-decision.md",
                doc_id="20260312t010205z-01-adr",
                scope_id="iss-local-00001",
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main"),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                clock=_StubClock(),
            )

            result = app_sync_state.sync(self._request(app_contracts), ports)

            assert result.artifact_failure is None
            adrs_dir = specdock_dir / "adrs"
            assert adrs_dir.is_dir()
            assert sorted(path.name for path in adrs_dir.iterdir()) == [initiative_doc.name, issue_doc.name]
            for source in (initiative_doc, issue_doc):
                link_path = adrs_dir / source.name
                assert link_path.is_symlink(), f"missing ADR mirror symlink: {link_path}"
                assert not os.readlink(link_path).startswith("/"), os.readlink(link_path)
                assert link_path.resolve() == source.resolve()

    def test_sync_warns_and_succeeds_with_empty_adrs_when_symlinks_are_unsupported(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            _domain_models,
            infra_artifact_writer,
            infra_contracts,
            presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
            initiative_dir = Path(records[0].path)
            self._write_valid_adr_doc(
                initiative_dir,
                "20260312t010203z-adr-init-decision.md",
                doc_id="20260312t010203z-adr",
                scope_id="init-local-00001",
            )
            adrs_dir = specdock_dir / "adrs"
            adrs_dir.mkdir(parents=True, exist_ok=True)
            (adrs_dir / "stale.txt").write_text("stale\n", encoding="utf-8")
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main"),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                clock=_StubClock(),
            )
            original_symlink = app_sync_state.os.symlink
            app_sync_state.os.symlink = lambda src, dst: (_ for _ in ()).throw(
                OSError(errno.ENOSYS, "symlink unsupported")
            )
            try:
                result = app_sync_state.sync(self._request(app_contracts), ports)
            finally:
                app_sync_state.os.symlink = original_symlink

            assert result.artifact_failure is None
            assert result.write_result is not None
            assert "adr_mirror_symlink_unsupported" in result.state.warnings
            index_todo = json.loads((specdock_dir / ".agent" / "index.json").read_text(encoding="utf-8"))
            index_all = json.loads((specdock_dir / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            assert "adr_mirror_symlink_unsupported" in index_todo["warnings"]
            assert "adr_mirror_symlink_unsupported" in index_all["warnings"]
            assert adrs_dir.is_dir()
            assert list(adrs_dir.iterdir()) == []
            rendered = presentation_cli_text.render_sync_text(result)
            assert "adr_mirror_symlink_unsupported" in rendered.warnings

    def test_sync_failure_keeps_symlink_unsupported_warning_in_result_state(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            _domain_models,
            infra_artifact_writer,
            infra_contracts,
            presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
            initiative_dir = Path(records[0].path)
            self._write_valid_adr_doc(
                initiative_dir,
                "20260312t010203z-adr-init-decision.md",
                doc_id="20260312t010203z-adr",
                scope_id="init-local-00001",
            )
            writer = infra_artifact_writer.FileArtifactWriter()
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main"),
                artifact_writer=writer,
                clock=_StubClock(),
            )
            write_calls: list[Path] = []
            original_write_text = infra_artifact_writer._write_text
            fail_after_successes = 3

            def _partial_write_then_fail(path: Path, text: str) -> None:
                if len(write_calls) >= fail_after_successes:
                    raise RuntimeError("read-only fs")
                original_write_text(path, text)
                write_calls.append(path)

            infra_artifact_writer._write_text = _partial_write_then_fail
            original_symlink = app_sync_state.os.symlink
            app_sync_state.os.symlink = lambda src, dst: (_ for _ in ()).throw(
                OSError(errno.ENOSYS, "symlink unsupported")
            )
            try:
                result = app_sync_state.sync(self._request(app_contracts), ports)
            finally:
                infra_artifact_writer._write_text = original_write_text
                app_sync_state.os.symlink = original_symlink

            assert result.write_result is None
            assert result.artifact_failure is not None
            assert result.artifact_failure.status == "failed_partial_or_stale"
            assert result.artifact_failure.reason == "read-only fs"
            persisted_paths = {path.relative_to(specdock_dir).as_posix() for path in write_calls}
            expected_paths = self._expected_sync_artifact_relpaths()
            assert persisted_paths
            assert persisted_paths.issubset(expected_paths)
            assert persisted_paths != expected_paths
            assert expected_paths - persisted_paths
            persisted_index_paths = [
                path for path in write_calls if path.relative_to(specdock_dir).as_posix() in
                {".agent/index-all.json", ".agent/index.json"}
            ]
            for persisted_index_path in persisted_index_paths:
                payload = json.loads(persisted_index_path.read_text(encoding="utf-8"))
                assert "adr_mirror_symlink_unsupported" in payload["warnings"]
            assert "adr_mirror_symlink_unsupported" in result.state.warnings
            rendered = presentation_cli_text.render_sync_text(result)
            assert rendered.warnings == result.state.warnings

    def test_sync_active_update_render_failure_preserves_symlink_warning_and_reports_non_atomic(
        self,
    ) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            _domain_models,
            _infra_artifact_writer,
            infra_contracts,
            presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
            initiative_dir = Path(records[0].path)
            self._write_valid_adr_doc(
                initiative_dir,
                "20260312t010203z-adr-init-decision.md",
                doc_id="20260312t010203z-adr",
                scope_id="init-local-00001",
            )
            events: list[str] = []
            spy_writer = _SpyArtifactWriter()
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                active_state_store=_StubActiveStateStore(infra_contracts, events),
                git_gateway=_StubGitGateway("feature/iss-local-00001-implement"),
                artifact_writer=spy_writer,
                clock=_StubClock(),
            )

            original_symlink = app_sync_state.os.symlink
            original_render_dashboard = app_sync_state.render_dashboard
            app_sync_state.os.symlink = lambda src, dst: (_ for _ in ()).throw(
                OSError(errno.ENOSYS, "symlink unsupported")
            )
            app_sync_state.render_dashboard = lambda *args, **kwargs: (_ for _ in ()).throw(
                RuntimeError("render failed")
            )
            try:
                result = app_sync_state.sync(
                    self._request(app_contracts, force=False, update_active=True),
                    ports,
                )
            finally:
                app_sync_state.os.symlink = original_symlink
                app_sync_state.render_dashboard = original_render_dashboard

            assert not spy_writer.called
            assert result.write_result is None
            assert result.artifact_failure is not None
            assert result.artifact_failure.status == "failed_partial_or_stale"
            assert result.artifact_failure.reason == "render failed"
            assert result.active_update is not None
            assert result.active_update.applied
            assert result.state.active.issue_id == "iss-local-00001"
            assert "active.write" in events
            assert "adr_mirror_symlink_unsupported" in result.state.warnings
            rendered = presentation_cli_text.render_sync_text(result)
            assert rendered.warnings == result.state.warnings
            assert "failed (sync)" in rendered.stderr_lines[0]
            assert "status=failed_partial_or_stale" in rendered.stderr_lines[0]
            assert "adr_mirror_symlink_unsupported" in rendered.warnings

    def test_sync_symlink_probe_preserves_existing_repo_files_with_legacy_probe_name(self) -> None:
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
            initiative_dir = Path(records[0].path)
            doc = self._write_valid_adr_doc(
                initiative_dir,
                "20260312t010203z-adr-init-decision.md",
                doc_id="20260312t010203z-adr",
                scope_id="init-local-00001",
            )
            legacy_probe_path = specdock_dir / ".spec-dock-symlink-probe"
            legacy_probe_path.write_text("user data\n", encoding="utf-8")
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main"),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                clock=_StubClock(),
            )

            result = app_sync_state.sync(self._request(app_contracts), ports)

            assert result.artifact_failure is None
            assert legacy_probe_path.read_text(encoding="utf-8") == "user data\n"
            mirror_path = specdock_dir / "adrs" / doc.name
            assert mirror_path.is_symlink()
            assert mirror_path.resolve() == doc.resolve()

    def test_sync_recovers_dangling_adrs_symlink_before_probe_and_rebuilds_mirror(self) -> None:
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
            initiative_dir = Path(records[0].path)
            doc = self._write_valid_adr_doc(
                initiative_dir,
                "20260312t010203z-adr-init-decision.md",
                doc_id="20260312t010203z-adr",
                scope_id="init-local-00001",
            )
            adrs_dir = specdock_dir / "adrs"
            try:
                os.symlink("missing-generated-adrs-dir", adrs_dir)
            except OSError as error:
                if app_sync_state._is_environment_symlink_unsupported(error):
                    pytest.skip("symlinks not supported in test environment")
                raise
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main"),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                clock=_StubClock(),
            )

            result = app_sync_state.sync(self._request(app_contracts), ports)

            assert result.artifact_failure is None
            assert result.write_result is not None
            assert adrs_dir.is_dir()
            assert not adrs_dir.is_symlink()
            assert sorted(path.name for path in adrs_dir.iterdir()) == [doc.name]
            mirror_path = adrs_dir / doc.name
            assert mirror_path.is_symlink()
            assert mirror_path.resolve() == doc.resolve()

    def test_sync_treats_live_adrs_symlink_as_unsafe_for_probe_and_replaces_it(self) -> None:
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
            initiative_dir = Path(records[0].path)
            doc = self._write_valid_adr_doc(
                initiative_dir,
                "20260312t010203z-adr-init-decision.md",
                doc_id="20260312t010203z-adr",
                scope_id="init-local-00001",
            )
            managed_target_dir = repo_root / "managed-adrs-target"
            managed_target_dir.mkdir(parents=True, exist_ok=True)
            preserved = managed_target_dir / "preserve.txt"
            preserved.write_text("keep-me\n", encoding="utf-8")
            adrs_dir = specdock_dir / "adrs"
            try:
                os.symlink(managed_target_dir, adrs_dir)
            except OSError as error:
                if app_sync_state._is_environment_symlink_unsupported(error):
                    pytest.skip("symlinks not supported in test environment")
                raise
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main"),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                clock=_StubClock(),
            )
            symlink_calls: list[tuple[str, Path]] = []
            original_symlink = app_sync_state.os.symlink

            def _recording_symlink(src, dst):
                dst_path = Path(dst)
                symlink_calls.append((str(src), dst_path))
                return original_symlink(src, dst)

            app_sync_state.os.symlink = _recording_symlink
            try:
                result = app_sync_state.sync(self._request(app_contracts), ports)
            finally:
                app_sync_state.os.symlink = original_symlink

            assert result.artifact_failure is None
            assert result.write_result is not None
            assert len(symlink_calls) >= 2
            probe_path = symlink_calls[0][1]
            mirror_path = adrs_dir / doc.name
            assert probe_path.parent == specdock_dir
            assert probe_path.name.startswith(".spec-dock-adr-mirror-probe-")
            assert not probe_path.exists()
            assert symlink_calls[1][1] == mirror_path
            assert adrs_dir.is_dir()
            assert not adrs_dir.is_symlink()
            assert mirror_path.is_symlink()
            assert mirror_path.resolve() == doc.resolve()
            assert managed_target_dir.is_dir()
            assert sorted(path.name for path in managed_target_dir.iterdir()) == ["preserve.txt"]
            assert preserved.read_text(encoding="utf-8") == "keep-me\n"
            assert not (managed_target_dir / doc.name).exists()

    def test_resolve_adr_mirror_probe_location_falls_back_when_adrs_is_not_a_directory(self) -> None:
        (
            _runtime_app,
            _app_contracts,
            _app_ports,
            app_sync_state,
            _domain_models,
            _infra_artifact_writer,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            specdock_dir = Path(td) / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            adrs_path = specdock_dir / "adrs"
            adrs_path.write_text("not a directory\n", encoding="utf-8")

            location = app_sync_state._resolve_adr_mirror_probe_location(specdock_dir)

            assert location.probe_dir == specdock_dir
            assert not location.remove_probe_dir_after

    def test_sync_uses_specdock_dir_for_probe_when_existing_adrs_dir_is_not_probe_writable(self) -> None:
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
            initiative_dir = Path(records[0].path)
            doc = self._write_valid_adr_doc(
                initiative_dir,
                "20260312t010203z-adr-init-decision.md",
                doc_id="20260312t010203z-adr",
                scope_id="init-local-00001",
            )
            adrs_dir = specdock_dir / "adrs"
            adrs_dir.mkdir(parents=True, exist_ok=True)
            os.chmod(adrs_dir, 0o555)
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main"),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                clock=_StubClock(),
            )
            symlink_calls: list[tuple[str, Path]] = []
            original_symlink = app_sync_state.os.symlink

            def _read_only_generated_adrs_probe(src, dst):
                dst_path = Path(dst)
                symlink_calls.append((str(src), dst_path))
                if (
                    dst_path.parent == adrs_dir
                    and dst_path.name.startswith(".spec-dock-adr-mirror-probe-")
                ):
                    raise PermissionError(errno.EPERM, "operation not permitted")
                return original_symlink(src, dst)

            app_sync_state.os.symlink = _read_only_generated_adrs_probe
            try:
                result = app_sync_state.sync(self._request(app_contracts), ports)
            finally:
                app_sync_state.os.symlink = original_symlink
                if adrs_dir.exists() and not adrs_dir.is_symlink():
                    os.chmod(adrs_dir, 0o755)

            assert result.artifact_failure is None
            assert result.write_result is not None
            assert len(symlink_calls) >= 2
            probe_path = symlink_calls[0][1]
            mirror_path = adrs_dir / doc.name
            assert probe_path.parent == specdock_dir
            assert probe_path.name.startswith(".spec-dock-adr-mirror-probe-")
            assert not probe_path.exists()
            assert symlink_calls[1][1] == mirror_path
            assert adrs_dir.is_dir()
            assert mirror_path.is_symlink()
            assert mirror_path.resolve() == doc.resolve()

    def test_sync_ignores_non_utf8_timestamp_adr_candidates(self) -> None:
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
            initiative_dir = Path(records[0].path)
            valid_doc = self._write_valid_adr_doc(
                initiative_dir,
                "20260312t010203z-adr-init-decision.md",
                doc_id="20260312t010203z-adr",
                scope_id="init-local-00001",
            )
            invalid_doc = initiative_dir / "discussions" / "20260312t010204z-adr-invalid-encoding.md"
            invalid_doc.write_bytes(b"\xff\xfe\x00bad utf-8")
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main"),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                clock=_StubClock(),
            )

            result = app_sync_state.sync(self._request(app_contracts), ports)

            assert result.artifact_failure is None
            adrs_dir = specdock_dir / "adrs"
            assert sorted(path.name for path in adrs_dir.iterdir()) == [valid_doc.name]
            assert not (adrs_dir / invalid_doc.name).exists()

    def test_sync_leaves_empty_adrs_without_warning_when_no_adr_sources_exist(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            _domain_models,
            infra_artifact_writer,
            infra_contracts,
            presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
            adrs_dir = specdock_dir / "adrs"
            adrs_dir.mkdir(parents=True, exist_ok=True)
            (adrs_dir / "stale.txt").write_text("stale\n", encoding="utf-8")
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main"),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                clock=_StubClock(),
            )
            original_symlink = app_sync_state.os.symlink
            app_sync_state.os.symlink = lambda src, dst: (_ for _ in ()).throw(
                OSError(errno.ENOSYS, "symlink unsupported")
            )
            try:
                result = app_sync_state.sync(self._request(app_contracts), ports)
            finally:
                app_sync_state.os.symlink = original_symlink

            assert result.artifact_failure is None
            assert result.write_result is not None
            assert adrs_dir.is_dir()
            assert list(adrs_dir.iterdir()) == []
            assert "adr_mirror_symlink_unsupported" not in result.state.warnings
            rendered = presentation_cli_text.render_sync_text(result)
            assert "adr_mirror_symlink_unsupported" not in rendered.warnings

    def test_sync_keeps_symlink_probe_failures_hard_when_not_classified_as_unsupported(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            _domain_models,
            infra_artifact_writer,
            infra_contracts,
            presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
            initiative_dir = Path(records[0].path)
            self._write_valid_adr_doc(
                initiative_dir,
                "20260312t010203z-adr-init-decision.md",
                doc_id="20260312t010203z-adr",
                scope_id="init-local-00001",
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main"),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                clock=_StubClock(),
            )
            original_symlink = app_sync_state.os.symlink
            app_sync_state.os.symlink = lambda src, dst: (_ for _ in ()).throw(
                PermissionError(errno.EPERM, "operation not permitted")
            )
            try:
                result = app_sync_state.sync(self._request(app_contracts), ports)
            finally:
                app_sync_state.os.symlink = original_symlink

            assert result.artifact_failure is not None
            assert result.artifact_failure.status == "failed_before_write"
            assert "operation not permitted" in result.artifact_failure.reason
            assert "adr_mirror_symlink_unsupported" not in result.state.warnings
            rendered = presentation_cli_text.render_sync_text(result)
            assert "failed (sync)" in rendered.stderr_lines[0]

    def test_sync_active_update_probe_failure_is_non_atomic(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            _domain_models,
            _infra_artifact_writer,
            infra_contracts,
            presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
            initiative_dir = Path(records[0].path)
            self._write_valid_adr_doc(
                initiative_dir,
                "20260312t010203z-adr-init-decision.md",
                doc_id="20260312t010203z-adr",
                scope_id="init-local-00001",
            )
            events: list[str] = []
            active_store = _StubActiveStateStore(infra_contracts, events)
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                active_state_store=active_store,
                git_gateway=_StubGitGateway("feature/iss-local-00001-implement"),
                artifact_writer=_SpyArtifactWriter(),
                clock=_StubClock(),
            )
            original_symlink = app_sync_state.os.symlink
            app_sync_state.os.symlink = lambda src, dst: (_ for _ in ()).throw(
                PermissionError(errno.EPERM, "operation not permitted")
            )
            try:
                result = app_sync_state.sync(
                    self._request(app_contracts, force=False, update_active=True),
                    ports,
                )
            finally:
                app_sync_state.os.symlink = original_symlink

            assert result.write_result is None
            assert result.artifact_failure is not None
            assert result.artifact_failure.status == "failed_partial_or_stale"
            assert "operation not permitted" in result.artifact_failure.reason
            assert result.active_update is not None
            assert result.active_update.applied
            assert "active.write" in events
            assert "adr_mirror_symlink_unsupported" not in result.state.warnings
            rendered = presentation_cli_text.render_sync_text(result)
            assert "failed (sync)" in rendered.stderr_lines[0]
            assert "adr_mirror_symlink_unsupported" not in rendered.warnings

    def test_sync_keeps_actual_adr_mirror_symlink_failures_hard_after_probe_success(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            _domain_models,
            infra_artifact_writer,
            infra_contracts,
            presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
            initiative_dir = Path(records[0].path)
            basename = "20260312t010203z-adr-init-decision.md"
            self._write_valid_adr_doc(
                initiative_dir,
                basename,
                doc_id="20260312t010203z-adr",
                scope_id="init-local-00001",
            )
            adrs_dir = specdock_dir / "adrs"
            mirror_path = adrs_dir / basename
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main"),
                artifact_writer=infra_artifact_writer.FileArtifactWriter(),
                clock=_StubClock(),
            )
            symlink_calls: list[tuple[str, Path]] = []
            original_symlink = app_sync_state.os.symlink

            def _fail_only_actual_mirror_link(src, dst):
                dst_path = Path(dst)
                symlink_calls.append((str(src), dst_path))
                if len(symlink_calls) == 1:
                    return original_symlink(src, dst)
                raise PermissionError(errno.EPERM, "operation not permitted")

            app_sync_state.os.symlink = _fail_only_actual_mirror_link
            try:
                result = app_sync_state.sync(self._request(app_contracts), ports)
            finally:
                app_sync_state.os.symlink = original_symlink

            probe_path = symlink_calls[0][1]
            assert [path.name for _, path in symlink_calls] == [probe_path.name, mirror_path.name]
            assert probe_path.parent == adrs_dir
            assert probe_path.name.startswith(".spec-dock-adr-mirror-probe-")
            assert not probe_path.exists()
            assert not mirror_path.exists()
            assert result.write_result is None
            assert result.artifact_failure is not None
            assert result.artifact_failure.status == "failed_partial_or_stale"
            assert "operation not permitted" in result.artifact_failure.reason
            assert "adr_mirror_symlink_unsupported" not in result.state.warnings
            rendered = presentation_cli_text.render_sync_text(result)
            assert "adr_mirror_symlink_unsupported" not in rendered.warnings
            assert "failed (sync)" in rendered.stderr_lines[0]

    def test_is_environment_symlink_unsupported_covers_remaining_classified_branches(self) -> None:
        (
            _runtime_app,
            _app_contracts,
            _app_ports,
            app_sync_state,
            _domain_models,
            _infra_artifact_writer,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()

        sentinel = object()
        original_codes = {
            name: getattr(app_sync_state.errno, name, sentinel)
            for name in ("EOPNOTSUPP", "ENOTSUP")
        }
        app_sync_state.errno.EOPNOTSUPP = 9001
        app_sync_state.errno.ENOTSUP = 9002
        try:
            for case_label, error in (
                (
                    "EOPNOTSUPP",
                    OSError(app_sync_state.errno.EOPNOTSUPP, "symlink unsupported"),
                ),
                (
                    "ENOTSUP",
                    OSError(app_sync_state.errno.ENOTSUP, "symlink unsupported"),
                ),
            ):
                assert app_sync_state._is_environment_symlink_unsupported(error), case_label
        finally:
            for name, value in original_codes.items():
                if value is sentinel:
                    delattr(app_sync_state.errno, name)
                else:
                    setattr(app_sync_state.errno, name, value)

        class _WindowsPrivilegeError(OSError):
            @property
            def winerror(self):
                return 1314

        assert app_sync_state._is_environment_symlink_unsupported(
            _WindowsPrivilegeError(errno.EPERM, "privilege not held")
        ), "winerror_1314"

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
            assert result.artifact_failure is None
            assert result.write_result is not None
            assert result.state.generated_at == "2026-03-12T00:00:00Z"
            assert result.write_result.index_all_path == "spec-dock/.agent/index-all.json"
            assert result.write_result.dashboard_md_path == "spec-dock/dashboard.md"
            assert result.write_result.deps_raw_puml_path == "spec-dock/deps-raw.puml"

            index_todo = json.loads((specdock_dir / ".agent" / "index.json").read_text(encoding="utf-8"))
            index_all = json.loads((specdock_dir / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            tree_todo = json.loads((specdock_dir / ".agent" / "tree.json").read_text(encoding="utf-8"))
            tree_all = json.loads((specdock_dir / ".agent" / "tree-all.json").read_text(encoding="utf-8"))
            deps_raw_puml = (specdock_dir / "deps-raw.puml").read_text(encoding="utf-8")
            assert index_todo["projection"] == "current-future"
            assert "source" not in index_todo
            assert index_all["projection"] == "full-history"
            assert "source" not in index_all
            assert index_todo["deps"]["valid"]
            assert index_todo["deps"]["error"] is None
            assert "iss-local-00001" in index_todo["nodes"]
            assert "iss-local-00002" not in index_todo["nodes"]
            assert "iss-local-00002" in index_all["nodes"]
            assert "@startuml" in deps_raw_puml
            assert "iss-local-00001" in deps_raw_puml
            assert "iss-local-00002" in deps_raw_puml

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
            assert node_paths
            for node_path in node_paths:
                assert node_path.startswith("spec-dock/"), node_path
                assert not Path(node_path).is_absolute(), node_path
                assert not node_path.startswith(repo_root.as_posix()), node_path

            deps_issues = json.loads((specdock_dir / ".agent" / "deps-issues.json").read_text(encoding="utf-8"))
            assert deps_issues["projection"] == "issue-readiness-with-dependency-context"
            assert deps_issues["source"] == {"sync_state": "readiness_evaluation", "schema_version": 2}
            assert deps_issues["deps"]["valid"]
            assert "iss-local-00001" in deps_issues["nodes"]
            assert "iss-local-00002" not in deps_issues["nodes"]

            tree_puml = (specdock_dir / "tree.puml").read_text(encoding="utf-8")
            deps_puml = (specdock_dir / "deps-issues.puml").read_text(encoding="utf-8")
            dashboard = (specdock_dir / "dashboard.md").read_text(encoding="utf-8")
            assert "@startuml" in tree_puml
            assert "@startuml" in deps_puml
            assert "## Ready" in dashboard

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
            with pytest.raises(RuntimeError, match="Dependency cycle detected"):
                app_sync_state.collect_sync_state(self._request(app_contracts), ports)

    def _assert_sync_force_placeholder_and_deps_error_regression(self) -> None:
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
            assert result.artifact_failure is None
            assert result.write_result is not None
            assert result.state.warnings == ["deps_preflight_failed"]

            index = json.loads((specdock_dir / ".agent" / "index.json").read_text(encoding="utf-8"))
            assert index["projection"] == "current-future"
            assert "source" not in index
            assert not index["deps"]["valid"]
            assert "Dependency cycle detected" in str(index["deps"]["error"])

            index_all = json.loads((specdock_dir / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            assert index_all["projection"] == "full-history"
            assert "source" not in index_all
            assert not index_all["deps"]["valid"]
            assert "Dependency cycle detected" in str(index_all["deps"]["error"])

            deps_issues = json.loads((specdock_dir / ".agent" / "deps-issues.json").read_text(encoding="utf-8"))
            assert deps_issues["projection"] == "issue-readiness-with-dependency-context"
            assert deps_issues["source"] == {"sync_state": "readiness_evaluation", "schema_version": 2}
            assert not deps_issues["deps"]["valid"]
            assert "Dependency cycle detected" in str(deps_issues["deps"]["error"])

            tree_puml = (specdock_dir / "tree.puml").read_text(encoding="utf-8")
            deps_puml = (specdock_dir / "deps-issues.puml").read_text(encoding="utf-8")
            deps_raw_puml = (specdock_dir / "deps-raw.puml").read_text(encoding="utf-8")
            dashboard = (specdock_dir / "dashboard.md").read_text(encoding="utf-8")
            for text in (tree_puml, deps_puml, deps_raw_puml, dashboard):
                assert "DEPS_DISABLED" in text
                assert "sync --force" in text
            assert '\\"' not in dashboard
            assert "\\\\" not in dashboard

    def test_sync_force_placeholder_and_deps_error_regression(self) -> None:
        self._assert_sync_force_placeholder_and_deps_error_regression()

    def test_issue_71_runtime_bundle_sync_force_degraded_path(self) -> None:
        self._assert_sync_force_placeholder_and_deps_error_regression()

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
            assert result.artifact_failure is None
            status = result.state.issue_statuses["iss-local-00001"]
            assert status.source == "github"
            assert status.effective_status == "done"
            assert issue_gateway.view_calls == [(str(repo_root), 301, "other/repo")]

            index_all = json.loads((specdock_dir / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            issue_payload = index_all["nodes"]["iss-local-00001"]["github"]
            assert issue_payload["url"] == "https://github.com/other/repo/issues/301"
            assert issue_payload["state"] == "CLOSED"
            assert issue_payload["repo_owner"] == "other"
            assert issue_payload["repo_name"] == "repo"

    def test_sync_skips_same_repo_repo_scoped_view_fetch_when_index_contains_key(self) -> None:
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
                github_repo_owner="current",
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
                ]
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
            assert result.artifact_failure is None
            assert issue_gateway.view_calls == []
            status = result.state.issue_statuses["iss-local-00001"]
            assert status.source == "github"
            assert status.effective_status == "open"

    def test_sync_falls_back_to_same_repo_repo_scoped_view_fetch_when_index_missing_key(self) -> None:
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
                github_repo_owner="current",
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
                    ("current/repo", 301): domain_models.IssueSnapshot(
                        issue_number=301,
                        state="CLOSED",
                        title="Current repo #301 via fallback",
                        labels=["bugfix"],
                        updated_at="2026-03-18T02:00:00Z",
                        url="https://github.com/current/repo/issues/301",
                        repo_owner="current",
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
            assert result.artifact_failure is None
            assert issue_gateway.view_calls == [(str(repo_root), 301, "current/repo")]
            status = result.state.issue_statuses["iss-local-00001"]
            assert status.source == "github"
            assert status.effective_status == "done"

    @pytest.mark.parametrize("force", [False, True], ids=["force_false", "force_true"])
    @pytest.mark.parametrize(
        ("repo_owner", "repo_name"),
        [
            pytest.param("current", None, id="missing_repo_name"),
            pytest.param(None, "repo", id="missing_repo_owner"),
            pytest.param("   ", "repo", id="blank_repo_owner"),
            pytest.param("current", "   ", id="blank_repo_name"),
        ],
    )
    def test_sync_fails_preflight_for_malformed_partial_repo_scope_linkage(
        self,
        force,
        repo_owner,
        repo_name,
    ) -> None:
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
                github_repo_owner=repo_owner,
                github_repo_name=repo_name,
            )
            records[3] = _record(
                infra_contracts,
                kind="issue",
                node_id="iss-local-00002",
                title="DB",
                path=Path(records[3].path),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=None,
            )
            issue_gateway = _StubIssueGateway(snapshots=[])
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

            with pytest.raises(
                RuntimeError,
                match="preflight validate failed: issue has invalid github linkage",
            ):
                app_sync_state.sync(
                    app_contracts.SyncRequest(
                        force=force,
                        github_enabled=True,
                        issue_limit=10000,
                        update_active_from_branch=False,
                    ),
                    ports,
                )
            assert issue_gateway.index_calls == []
            assert issue_gateway.view_calls == []

    def test_sync_falls_back_to_current_repo_view_for_unscoped_linked_epic_when_index_missing_key(self) -> None:
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

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth"
            epic_dir = init_dir / "epics" / "epic-local-00001-core"
            issue_dir = epic_dir / "issues" / "iss-local-00001-api"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth",
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
                    title="Core",
                    path=epic_dir,
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
                    path=issue_dir,
                    parent_id="epic-local-00001",
                    initiative_id="init-local-00001",
                    epic_id="epic-local-00001",
                    github_issue_number=None,
                ),
            ]
            self._materialize_required_artifacts(records)

            issue_gateway = _StubIssueGateway(
                snapshots=[],
                foreign_snapshots={
                    ("current/repo", 201): domain_models.IssueSnapshot(
                        issue_number=201,
                        state="CLOSED",
                        title="Current repo #201 via fallback",
                        labels=["done"],
                        updated_at="2026-03-23T00:00:00Z",
                        url="https://github.com/current/repo/issues/201",
                        repo_owner="current",
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
                    {"iss-local-00001": []},
                ),
                derived_state_reader=_StubDerivedStateReader({"iss-local-00001": "open"}),
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
            assert result.artifact_failure is None
            assert issue_gateway.view_calls == [(str(repo_root), 201, "current/repo")]
            epic_status = result.state.issue_statuses["epic-local-00001"]
            assert epic_status.source == "github"
            assert epic_status.effective_status == "done"
            assert not epic_status.stale
            assert "gh_fetch_failed" not in result.state.warnings

    def test_sync_mixed_same_repo_and_foreign_repo_scoped_targets_keeps_foreign_fetch(self) -> None:
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
                github_repo_owner="current",
                github_repo_name="repo",
            )
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
                        labels=[],
                        updated_at="2026-03-18T02:00:00Z",
                        url="https://github.com/other/repo/issues/301",
                        repo_owner="other",
                        repo_name="repo",
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
            assert result.artifact_failure is None
            assert issue_gateway.view_calls == [(str(repo_root), 301, "other/repo")]
            current_status = result.state.issue_statuses["iss-local-00001"]
            foreign_status = result.state.issue_statuses["iss-local-00002"]
            assert current_status.source == "github"
            assert current_status.effective_status == "open"
            assert foreign_status.source == "github"
            assert foreign_status.effective_status == "done"

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
            assert result.artifact_failure is None
            assert issue_gateway.view_calls == [(str(repo_root), 301, "other/repo")]

            current_status = result.state.issue_statuses["iss-local-00001"]
            foreign_status = result.state.issue_statuses["iss-local-00002"]
            assert current_status.source == "github"
            assert current_status.effective_status == "open"
            assert foreign_status.source == "github"
            assert foreign_status.effective_status == "done"
            assert (
                result.state.github_snapshot_by_repo_and_issue_number[("current/repo", 301)].url
                == "https://github.com/current/repo/issues/301"
            )
            assert (
                result.state.github_snapshot_by_repo_and_issue_number[("other/repo", 301)].url
                == "https://github.com/other/repo/issues/301"
            )

            index_all = json.loads((specdock_dir / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            current_payload = index_all["nodes"]["iss-local-00001"]["github"]
            foreign_payload = index_all["nodes"]["iss-local-00002"]["github"]
            assert current_payload["url"] == "https://github.com/current/repo/issues/301"
            assert current_payload["state"] == "OPEN"
            assert foreign_payload["url"] == "https://github.com/other/repo/issues/301"
            assert foreign_payload["state"] == "CLOSED"

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
            assert result.artifact_failure is None
            assert "gh_index_incomplete" in result.state.warnings
            assert "gh_fetch_failed" in result.state.warnings
            assert issue_gateway.view_calls == [
                    (str(repo_root), 301, "current/repo"),
                    (str(repo_root), 301, "other/repo"),
            ]

            current_status = result.state.issue_statuses["iss-local-00001"]
            foreign_status = result.state.issue_statuses["iss-local-00002"]
            assert current_status.source == "unknown"
            assert current_status.effective_status == "unknown"
            assert foreign_status.source == "github"
            assert foreign_status.effective_status == "done"

            index_all = json.loads((specdock_dir / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            current_payload = index_all["nodes"]["iss-local-00001"]["github"]
            foreign_payload = index_all["nodes"]["iss-local-00002"]["github"]
            assert current_payload["issue_number"] == 301
            assert "url" not in current_payload
            assert "state" not in current_payload
            assert foreign_payload["url"] == "https://github.com/other/repo/issues/301"
            assert foreign_payload["state"] == "CLOSED"

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
            assert result.artifact_failure is None
            assert issue_gateway.view_calls == [
                    (str(repo_root), 101, "upstream/product"),
                    (str(repo_root), 201, "upstream/product"),
            ]

            index_all = json.loads((specdock_dir / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            init_payload = index_all["nodes"]["init-local-00001"]["github"]
            epic_payload = index_all["nodes"]["epic-local-00001"]["github"]
            assert init_payload["url"] == "https://github.com/upstream/product/issues/101"
            assert init_payload["state"] == "CLOSED"
            assert epic_payload["url"] == "https://github.com/upstream/product/issues/201"
            assert epic_payload["state"] == "CLOSED"

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
            assert result.artifact_failure is None
            assert issue_gateway.view_calls == [(str(repo_root), 301, "upstream/product")]
            issue_status = result.state.issue_statuses["iss-local-00001"]
            assert issue_status.source == "github"
            assert issue_status.effective_status == "open"

            index_all = json.loads((specdock_dir / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            issue_payload = index_all["nodes"]["iss-local-00001"]["github"]
            initiative_payload = index_all["nodes"]["init-local-00001"]["github"]
            assert issue_payload["url"] == "https://github.com/current/repo/issues/301"
            assert issue_payload["state"] == "OPEN"
            assert initiative_payload["url"] == "https://github.com/upstream/product/issues/301"
            assert initiative_payload["state"] == "CLOSED"

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
            assert result.artifact_failure is None
            assert "gh_fetch_failed" in result.state.warnings
            assert issue_gateway.view_calls == [(str(repo_root), 301, "other/repo")]
            issue_status = result.state.issue_statuses["iss-local-00001"]
            assert issue_status.source == "unknown"
            assert issue_status.effective_status == "unknown"

            index_all = json.loads((specdock_dir / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            issue_payload = index_all["nodes"]["iss-local-00001"]["github"]
            assert issue_payload["issue_number"] == 301
            assert issue_payload["repo_owner"] == "other"
            assert issue_payload["repo_name"] == "repo"
            assert "url" not in issue_payload
            assert "state" not in issue_payload
            assert "updated_at" not in issue_payload
            assert "labels" not in issue_payload

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
            assert result.artifact_failure is not None
            assert result.artifact_failure.status == "failed_partial_or_stale"
            assert result.artifact_failure.reason == "disk full"
            assert result.active_update is not None
            assert result.active_update.applied
            assert result.state.active.issue_id == "iss-local-00001"
            assert "active.write" in events
            assert "artifact.write" in events
            assert events.index("active.write") < events.index("artifact.write")

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
            assert result.artifact_failure is not None
            assert result.artifact_failure.status == "failed_partial_or_stale"
            assert result.artifact_failure.reason == "read-only fs"
            assert result.active_update is None

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

            assert not spy_writer.called
            assert result.artifact_failure is not None
            assert result.artifact_failure.status == "failed_before_write"
            assert result.artifact_failure.reason == "render failed"

    def test_sync_prewrite_render_failure_keeps_symlink_warning_in_failed_before_write_result(
        self,
    ) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            _domain_models,
            _infra_artifact_writer,
            infra_contracts,
            presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
            initiative_dir = Path(records[0].path)
            self._write_valid_adr_doc(
                initiative_dir,
                "20260312t010203z-adr-init-decision.md",
                doc_id="20260312t010203z-adr",
                scope_id="init-local-00001",
            )
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

            original_symlink = app_sync_state.os.symlink
            original_render_dashboard = app_sync_state.render_dashboard
            app_sync_state.os.symlink = lambda src, dst: (_ for _ in ()).throw(
                OSError(errno.ENOSYS, "symlink unsupported")
            )
            app_sync_state.render_dashboard = lambda *args, **kwargs: (_ for _ in ()).throw(
                RuntimeError("render failed")
            )
            try:
                result = app_sync_state.sync(self._request(app_contracts), ports)
            finally:
                app_sync_state.os.symlink = original_symlink
                app_sync_state.render_dashboard = original_render_dashboard

            assert not spy_writer.called
            assert result.artifact_failure is not None
            assert result.artifact_failure.status == "failed_before_write"
            assert result.artifact_failure.reason == "render failed"
            assert "adr_mirror_symlink_unsupported" in result.state.warnings
            rendered = presentation_cli_text.render_sync_text(result)
            assert "adr_mirror_symlink_unsupported" in rendered.warnings

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
                    deps_raw_puml_path="spec-dock/deps-raw.puml",
                    dashboard_md_path="spec-dock/dashboard.md",
                ),
                active_update=app_contracts.ActiveUpdateOutcome(applied=False, reason="no match"),
                artifact_failure=None,
            )
        )
        assert "spec-dock/.agent/index-all.json" in success.stdout_lines[0]
        assert success.stderr_lines == ["spec-dock: sync: active unchanged (no match)"]
        assert success.warnings == ["warn-1", "warn-2"]

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
        assert "status=failed_partial_or_stale" in failed.stderr_lines[0]
        assert "stale" in failed.stderr_lines[1]

    def test_deps_issues_does_not_include_historical_satisfied_high_level_context(self) -> None:
        (
            _runtime_app,
            app_contracts,
            _app_ports,
            _app_sync_state,
            domain_models,
            _infra_artifact_writer,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        presentation_json_state = _presentation_json_state_module()

        def _node(
            kind: str,
            node_id: str,
            title: str,
            *,
            parent_id: str | None = None,
            initiative_id: str | None = None,
            epic_id: str | None = None,
        ):
            path = Path(f"/repo/spec-dock/{node_id}")
            return domain_models.SpecNode(
                kind=kind,
                id=node_id,
                title=title,
                slug=node_id,
                path=path,
                meta_path=path / ".meta.json",
                parent_id=parent_id,
                initiative_id=initiative_id,
                epic_id=epic_id,
                github_issue_number=None,
            )

        def _status(issue_id: str, effective_status: str):
            return domain_models.IssueStatusSnapshot(
                issue_id=issue_id,
                authority="derived",
                effective_status=effective_status,
                source="local",
                stale=False,
                last_sync_at="2026-06-18T00:00:00Z",
                github_number=None,
            )

        state = app_contracts.SyncStateResult(
            graph=domain_models.SpecGraph(
                nodes_by_id={
                    "init-00101": _node("initiative", "init-00101", "Init"),
                    "epic-00201": _node(
                        "epic",
                        "epic-00201",
                        "Open epic",
                        parent_id="init-00101",
                        initiative_id="init-00101",
                    ),
                    "epic-00202": _node(
                        "epic",
                        "epic-00202",
                        "Closed historical epic",
                        parent_id="init-00101",
                        initiative_id="init-00101",
                    ),
                    "iss-00301": _node(
                        "issue",
                        "iss-00301",
                        "Current issue",
                        parent_id="epic-00201",
                        initiative_id="init-00101",
                        epic_id="epic-00201",
                    ),
                    "iss-00302": _node(
                        "issue",
                        "iss-00302",
                        "Historical done issue",
                        parent_id="epic-00201",
                        initiative_id="init-00101",
                        epic_id="epic-00201",
                    ),
                    "iss-00303": _node(
                        "issue",
                        "iss-00303",
                        "Open issue with done dependency",
                        parent_id="epic-00201",
                        initiative_id="init-00101",
                        epic_id="epic-00201",
                    ),
                }
            ),
            active=None,
            issue_statuses={
                "iss-00301": _status("iss-00301", "open"),
                "iss-00302": _status("iss-00302", "done"),
                "iss-00303": _status("iss-00303", "open"),
            },
            progress=domain_models.ProgressMap(by_node_id={}, counts={}),
            deps_state=domain_models.DepsState(nodes=[], warnings=[]),
            deps_eval_by_id={
                "iss-00301": domain_models.DepsEvaluation(
                    ready=False,
                    guard_reason="blocked",
                    blockers=["epic-00201"],
                    blockers_top=[],
                    closure=[],
                    node_blockers=[
                        domain_models.DepsNodeBlocker(
                            node_id="epic-00201",
                            reason="empty_open",
                            state="open",
                            state_source="github",
                            source_issue_id="iss-00301",
                            lifecycle_state="open",
                            lifecycle_source="github",
                            dependency_disposition="blocking",
                            disposition_basis="empty_open_container",
                        )
                    ],
                ),
                "iss-00302": domain_models.DepsEvaluation(
                    ready=True,
                    guard_reason="ready",
                    blockers=[],
                    blockers_top=[],
                    closure=[],
                    satisfied_dependencies=[
                        domain_models.DepsDependencyContext(
                            source_node_id="iss-00302",
                            source_issue_id="iss-00302",
                            target_node_id="epic-00202",
                            target_node_kind="epic",
                            target_issue_ids=(),
                            expansion="empty",
                            lifecycle_state="closed",
                            lifecycle_source="github",
                            dependency_disposition="satisfied",
                            disposition_basis="lifecycle_closed",
                        )
                    ],
                ),
                "iss-00303": domain_models.DepsEvaluation(
                    ready=True,
                    guard_reason="ready",
                    blockers=[],
                    blockers_top=[],
                    closure=[],
                ),
            },
            generated_at="2026-06-18T00:00:00Z",
            warnings=[],
            deps_preflight_error=None,
            dependency_contexts_by_issue_id={
                "iss-00301": [
                    domain_models.DepsDependencyContext(
                        source_node_id="epic-00201",
                        source_issue_id="iss-00301",
                        target_node_id="epic-00201",
                        target_node_kind="epic",
                        target_issue_ids=(),
                        expansion="empty",
                        lifecycle_state="open",
                        lifecycle_source="github",
                        dependency_disposition="blocking",
                        disposition_basis="empty_open_container",
                    )
                ],
                "iss-00303": [
                    domain_models.DepsDependencyContext(
                        source_node_id="iss-00303",
                        source_issue_id="iss-00303",
                        target_node_id="iss-00302",
                        target_node_kind="issue",
                        target_issue_ids=("iss-00302",),
                        expansion="issue",
                    )
                ],
            },
            high_level_statuses_by_node_id={
                "epic-00201": domain_models.DepsHighLevelStatus(
                    node_id="epic-00201",
                    state="open",
                    source="github",
                ),
                "epic-00202": domain_models.DepsHighLevelStatus(
                    node_id="epic-00202",
                    state="closed",
                    source="github",
                )
            },
        )

        payload = json.loads(presentation_json_state.render_deps_issues_artifact(state).json_text)

        assert set(payload["nodes"]) == {"epic-00201", "iss-00301", "iss-00303"}
        assert "iss-00302" not in payload["nodes"]
        assert [
            (edge["from"], edge["to"], edge["state"], edge["relation"])
            for edge in payload["edges"]
        ] == [("iss-00301", "epic-00201", "blocking", "raw_direct")]
        assert payload["dependency_contexts"] == [
            {
                "source_node_id": "epic-00201",
                "source_issue_id": "iss-00301",
                "target_node_id": "epic-00201",
                "target_node_kind": "epic",
                "target_issue_ids": [],
                "expansion": "empty",
                "lifecycle_state": "open",
                "lifecycle_source": "github",
                "dependency_disposition": "blocking",
                "disposition_basis": "empty_open_container",
            },
            {
                "source_node_id": "iss-00302",
                "source_issue_id": "iss-00302",
                "target_node_id": "epic-00202",
                "target_node_kind": "epic",
                "target_issue_ids": [],
                "expansion": "empty",
                "lifecycle_state": "closed",
                "lifecycle_source": "github",
                "dependency_disposition": "satisfied",
                "disposition_basis": "lifecycle_closed",
            },
            {
                "source_node_id": "iss-00303",
                "source_issue_id": "iss-00303",
                "target_node_id": "iss-00302",
                "target_node_kind": "issue",
                "target_issue_ids": ["iss-00302"],
                "expansion": "issue",
                "lifecycle_state": "done",
                "lifecycle_source": "local",
                "dependency_disposition": "satisfied",
                "disposition_basis": "local_done",
            },
        ]

    def test_deps_check_json_includes_lifecycle_and_disposition_context(self) -> None:
        (
            _runtime_app,
            app_contracts,
            _app_ports,
            _app_sync_state,
            domain_models,
            _infra_artifact_writer,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        presentation_json_state = _presentation_json_state_module()

        inspection = domain_models.TargetDepsInspection(
            target_id=domain_models.NodeId("iss-00301"),
            evaluation=domain_models.DepsEvaluation(
                ready=False,
                guard_reason="blocked",
                blockers=[],
                blockers_top=[],
                closure=[],
                node_blockers=[
                    domain_models.DepsNodeBlocker(
                        node_id="epic-00201",
                        reason="empty_open",
                        state="open",
                        state_source="github",
                        source_issue_id="iss-00301",
                        lifecycle_state="open",
                        lifecycle_source="github",
                        dependency_disposition="blocking",
                        disposition_basis="empty_open_container",
                    )
                ],
                satisfied_dependencies=[
                    domain_models.DepsDependencyContext(
                        source_node_id="iss-00301",
                        source_issue_id="iss-00301",
                        target_node_id="epic-00202",
                        target_node_kind="epic",
                        target_issue_ids=(),
                        expansion="empty",
                        lifecycle_state="closed",
                        lifecycle_source="github",
                        dependency_disposition="satisfied",
                        disposition_basis="lifecycle_closed",
                    )
                ],
            ),
            node_states={
                "iss-00301": domain_models.DepsNodeState(
                    node_id="iss-00301",
                    status="open",
                    ready=False,
                    blockers_top=[],
                    effective_depends_on=["epic-00201", "epic-00202"],
                )
            },
            effective_depends_on=["epic-00201", "epic-00202"],
            warnings=[],
            issue_statuses={
                "iss-00301": domain_models.IssueStatusSnapshot(
                    issue_id="iss-00301",
                    authority="derived",
                    effective_status="open",
                    source="local",
                    stale=False,
                    last_sync_at="2026-06-18T00:00:00Z",
                    github_number=None,
                )
            },
        )
        result = app_contracts.DepsCheckResult(
            target=app_contracts.TargetRef(
                kind="id",
                node_id="iss-00301",
                github_issue_number=None,
            ),
            inspection=inspection,
            warnings=[],
        )

        payload = json.loads(presentation_json_state.render_deps_check_json(result))

        assert payload["schema_version"] == 2
        assert {
            "schema_version",
            "target",
            "target_status",
            "ready",
            "effective_depends_on",
            "blockers",
            "issue_blockers",
            "node_blockers",
            "satisfied_dependencies",
            "nodes",
            "warnings",
        } <= set(payload)
        assert payload["node_blockers"] == [
            {
                "node_id": "epic-00201",
                "reason": "empty_open",
                "state": "open",
                "state_source": "github",
                "source_issue_id": "iss-00301",
                "lifecycle_state": "open",
                "lifecycle_source": "github",
                "dependency_disposition": "blocking",
                "disposition_basis": "empty_open_container",
            }
        ]
        assert payload["satisfied_dependencies"] == [
            {
                "source_node_id": "iss-00301",
                "source_issue_id": "iss-00301",
                "target_node_id": "epic-00202",
                "target_node_kind": "epic",
                "target_issue_ids": [],
                "expansion": "empty",
                "lifecycle_state": "closed",
                "lifecycle_source": "github",
                "dependency_disposition": "satisfied",
                "disposition_basis": "lifecycle_closed",
            }
        ]

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
        assert not hasattr(runtime_app, "_sync")
        try:
            runtime_app._cli_build_runtime = lambda _specdock_dir, **_kwargs: SimpleNamespace(
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
            assert exit_code_ok == 0

            runtime_app._cli_build_runtime = lambda _specdock_dir, **_kwargs: SimpleNamespace(
                use_cases=_build_use_cases(
                    lambda _req: app_contracts.SyncCommandResult(
                        state=app_contracts.SyncStateResult(
                            graph=delegated_state.graph,
                            active=delegated_state.active,
                            issue_statuses=delegated_state.issue_statuses,
                            progress=delegated_state.progress,
                            deps_state=delegated_state.deps_state,
                            deps_eval_by_id=delegated_state.deps_eval_by_id,
                            generated_at=delegated_state.generated_at,
                            warnings=["adr_mirror_symlink_unsupported"],
                            deps_preflight_error=delegated_state.deps_preflight_error,
                        ),
                        write_result=None,
                        active_update=None,
                        artifact_failure=None,
                    )
                )
            )
            out = io.StringIO()
            err = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                exit_code_warn = runtime_app.main(["sync"])
            assert exit_code_warn == 0
            assert "adr_mirror_symlink_unsupported" in err.getvalue()

            runtime_app._cli_build_runtime = lambda _specdock_dir, **_kwargs: SimpleNamespace(
                use_cases=_build_use_cases(lambda _req: (_ for _ in ()).throw(RuntimeError("sync failed")))
            )
            out = io.StringIO()
            err = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                exit_code_ng = runtime_app.main(["sync"])
            assert exit_code_ng == 1
            assert "error: sync failed" in err.getvalue()
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
        assert result is delegated_result
        assert len(runner.calls) == 1
        assert runner.calls[0][1] == "migrate"

        app_sync_state.sync_after_import(ports)
        assert len(runner.calls) == 2
        sync_after_req, mode = runner.calls[1]
        assert mode == "no_migrate"
        assert not sync_after_req.update_active_from_branch

    def test_sync_github_keeps_lone_unscoped_legacy_linkage_without_backfill(self) -> None:
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
            self._materialize_required_artifacts(records)
            node_repo = _StubNodeRepo()
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                node_repo=node_repo,
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                issue_gateway=_StubIssueGateway([]),
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main", repo_slug="current/repo"),
                clock=_StubClock(),
            )

            state = app_sync_state.collect_sync_state(
                app_contracts.SyncRequest(
                    force=False,
                    github_enabled=True,
                    issue_limit=10000,
                    update_active_from_branch=False,
                ),
                ports,
            )
            assert "iss-local-00001" in state.graph.nodes_by_id
            assert node_repo.backfill_calls == []

    def _s06_sync_result(self, app_contracts, domain_models, *, warnings=None, artifact_failure=None):
        return app_contracts.SyncCommandResult(
            state=app_contracts.SyncStateResult(
                graph=domain_models.SpecGraph(nodes_by_id={}),
                active=None,
                issue_statuses={},
                progress=domain_models.ProgressMap(by_node_id={}, counts={}),
                deps_state=domain_models.DepsState(nodes=[], warnings=[]),
                deps_eval_by_id={},
                generated_at="2026-03-12T00:00:00Z",
                warnings=list(warnings or []),
                deps_preflight_error=None,
            ),
            write_result=None
            if artifact_failure is not None
            else app_contracts.ArtifactWriteResult(
                index_all_path="spec-dock/.agent/index-all.json",
                index_todo_path="spec-dock/.agent/index.json",
                tree_all_path="spec-dock/.agent/tree-all.json",
                tree_todo_path="spec-dock/.agent/tree.json",
                tree_all_puml_path="spec-dock/tree-all.puml",
                tree_todo_puml_path="spec-dock/tree.puml",
                deps_issues_json_path="spec-dock/.agent/deps-issues.json",
                deps_issues_puml_path="spec-dock/deps-issues.puml",
                deps_raw_puml_path="spec-dock/deps-raw.puml",
                dashboard_md_path="spec-dock/dashboard.md",
            ),
            active_update=None,
            artifact_failure=artifact_failure,
        )

    def _s06_issue_node(self, app_contracts):
        return app_contracts.SpecNode(
            kind="issue",
            id="iss-00093",
            title="Automatic sync",
            slug="automatic-sync",
            path=Path(
                "/repo/spec-dock/initiatives/init-local-00001/epics/epic-local-00001/issues/iss-00093-automatic-sync"
            ),
            meta_path=Path(
                "/repo/spec-dock/initiatives/init-local-00001/epics/epic-local-00001/issues/iss-00093-automatic-sync/.meta.json"
            ),
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=93,
        )

    def _s06_delete_result(self, app_contracts, *, post_sync):
        return app_contracts.DeleteNodeResult(
            status="ok",
            target_id="iss-00093",
            deleted_node_ids=["iss-00093"],
            remaining_node_ids=[],
            remote_close=app_contracts.DeleteRemoteCloseBuckets(
                closed=[],
                noop_already_closed=["iss-00093"],
                failed=[],
                skipped_not_attempted=[],
            ),
            offending_node_ids=[],
            validation_reasons=[],
            active_restore_result="not_needed",
            recovery_guidance=[],
            dependency_scrub_failures=[],
            warnings=[],
            post_sync=post_sync,
        )

    def test_tc_s06_001_new_post_sync_exception_is_nonzero_with_mutation_success_guidance(self) -> None:
        (
            _runtime_app,
            app_contracts,
            _app_ports,
            _app_sync_state,
            _domain_models,
            _infra_artifact_writer,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        from spec_dock_runtime.commands import new as new_cmd

        post_sync = app_contracts.PostMutationSyncOutcome.from_exception(RuntimeError("sync exploded"))
        result = app_contracts.CreateNodeResult(
            node=self._s06_issue_node(app_contracts),
            created_paths=[],
            warnings=[],
            post_sync=post_sync,
        )

        class _UseCases:
            def create_issue(self, req):
                del req
                return result

        outcome = new_cmd._run_new_issue(
            new_cmd.NewIssueArgs(
                epic_id="epic-local-00001",
                title="Automatic sync",
                slug=None,
                create_github_issue=False,
                github_issue_number=93,
            ),
            _UseCases(),
        )

        assert outcome.exit_code == 1
        assert "spec-dock: ok (new issue)" in "\n".join(outcome.text.stdout_lines)
        assert "spec-dock: failed (new issue auto-sync) id=iss-00093" in outcome.text.stderr_lines
        assert any("mutation succeeded" in line for line in outcome.text.stderr_lines)
        assert any("sync` to refresh" in line for line in outcome.text.stderr_lines)

    def test_tc_s06_002_deps_fatal_github_warning_is_post_sync_failure_guidance(self) -> None:
        (
            _runtime_app,
            app_contracts,
            _app_ports,
            _app_sync_state,
            domain_models,
            _infra_artifact_writer,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        from spec_dock_runtime.commands import deps as deps_cmd

        post_sync = app_contracts.PostMutationSyncOutcome.from_sync_result(
            self._s06_sync_result(app_contracts, domain_models, warnings=["gh_fetch_failed"])
        )
        result = app_contracts.MutateDepsResult(
            action="add",
            from_id="iss-00093",
            to_id="iss-00094",
            result="updated",
            warnings=[],
            post_sync=post_sync,
        )

        class _UseCases:
            def mutate_deps(self, req):
                del req
                return result

        outcome = deps_cmd._run_deps_add(
            deps_cmd.DepsMutationArgs(from_id="iss-00093", to_id="iss-00094"),
            _UseCases(),
        )

        assert outcome.exit_code == 1
        assert "spec-dock: ok (deps add)" in "\n".join(outcome.text.stdout_lines)
        assert "spec-dock: ok (deps add auto-sync)" not in outcome.text.stdout_lines
        assert "spec-dock: failed (deps add auto-sync) from=iss-00093 to=iss-00094" in \
            outcome.text.stderr_lines
        assert any("GitHub issue state fetch was incomplete" in line for line in outcome.text.stderr_lines)
        assert outcome.text.warnings == ["gh_fetch_failed"]

        success_result = app_contracts.MutateDepsResult(
            action="add",
            from_id="iss-00093",
            to_id="iss-00094",
            result="updated",
            warnings=[],
            post_sync=app_contracts.PostMutationSyncOutcome.from_sync_result(
                self._s06_sync_result(app_contracts, domain_models)
            ),
        )
        skip_result = app_contracts.MutateDepsResult(
            action="add",
            from_id="iss-00093",
            to_id="iss-00094",
            result="unchanged",
            warnings=[],
            post_sync=app_contracts.PostMutationSyncOutcome.skipped("unchanged"),
        )

        class _SuccessUseCases:
            def mutate_deps(self, req):
                del req
                return success_result

        class _SkipUseCases:
            def mutate_deps(self, req):
                del req
                return skip_result

        success_outcome = deps_cmd._run_deps_add(
            deps_cmd.DepsMutationArgs(from_id="iss-00093", to_id="iss-00094"),
            _SuccessUseCases(),
        )
        skip_outcome = deps_cmd._run_deps_add(
            deps_cmd.DepsMutationArgs(from_id="iss-00093", to_id="iss-00094"),
            _SkipUseCases(),
        )

        assert success_outcome.exit_code == 0
        assert "spec-dock: ok (deps add auto-sync)" in success_outcome.text.stdout_lines
        assert skip_outcome.exit_code == 0
        assert "spec-dock: skipped (deps add auto-sync) reason=unchanged" in \
            skip_outcome.text.stdout_lines

    def test_tc_s06_003_delete_json_includes_post_sync_outcome_and_failure_exit(self) -> None:
        (
            _runtime_app,
            app_contracts,
            _app_ports,
            _app_sync_state,
            domain_models,
            _infra_artifact_writer,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        from spec_dock_runtime.commands import delete as delete_cmd

        success = app_contracts.PostMutationSyncOutcome.from_sync_result(
            self._s06_sync_result(app_contracts, domain_models)
        )
        non_fatal_warning = app_contracts.PostMutationSyncOutcome.from_sync_result(
            self._s06_sync_result(app_contracts, domain_models, warnings=["gh_index_incomplete"])
        )
        failure = app_contracts.PostMutationSyncOutcome.from_sync_result(
            self._s06_sync_result(app_contracts, domain_models, warnings=["gh_fetch_failed"])
        )
        delete_args = delete_cmd.DeleteArgs(
            positional_target="iss-00093",
            node_id=None,
            github_issue=None,
            recursive=False,
            force=False,
            confirmed=True,
            json_output=True,
        )

        outer = self

        class _UseCases:
            def __init__(self, post_sync):
                self.post_sync = post_sync

            def delete_node(self, req):
                del req
                return outer._s06_delete_result(app_contracts, post_sync=self.post_sync)

        success_outcome = delete_cmd._run_delete(delete_args, _UseCases(success))
        success_payload = json.loads(success_outcome.text.stdout_lines[0])
        assert success_outcome.exit_code == 0
        assert success_payload["post_sync"]["status"] == "success"
        assert not success_payload["post_sync"]["failed"]

        warning_outcome = delete_cmd._run_delete(delete_args, _UseCases(non_fatal_warning))
        warning_payload = json.loads(warning_outcome.text.stdout_lines[0])
        assert warning_outcome.exit_code == 0
        assert warning_payload["post_sync"]["status"] == "success"
        assert not warning_payload["post_sync"]["failed"]
        assert warning_payload["post_sync"]["warnings"] == ["gh_index_incomplete"]
        assert warning_payload["post_sync"]["fatal_warnings"] == []

        failure_outcome = delete_cmd._run_delete(delete_args, _UseCases(failure))
        failure_payload = json.loads(failure_outcome.text.stdout_lines[0])
        assert failure_outcome.exit_code == 1
        assert failure_payload["post_sync"]["status"] == "failed"
        assert failure_payload["post_sync"]["fatal_warnings"] == ["gh_fetch_failed"]
        assert any("mutation succeeded" in line for line in failure_payload["post_sync"]["recovery_guidance"])

    def test_tc_s06_004_mutation_parser_help_exposes_no_auto_sync_opt_out(self) -> None:
        (
            _runtime_app,
            _app_contracts,
            _app_ports,
            _app_sync_state,
            _domain_models,
            _infra_artifact_writer,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        from spec_dock_runtime.cli import parser as cli_parser
        from spec_dock_runtime.cli import registry as cli_registry

        parser = cli_parser.build_parser(cli_registry.build_registry())
        help_commands = [
            ["new", "initiative", "--help"],
            ["new", "epic", "--help"],
            ["new", "issue", "--help"],
            ["deps", "add", "--help"],
            ["deps", "remove", "--help"],
            ["delete", "--help"],
            ["close", "--help"],
            ["issue", "finish", "--help"],
        ]
        help_by_command: dict[tuple[str, ...], str] = {}
        for argv in help_commands:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                with pytest.raises(SystemExit) as cm:
                    parser.parse_args(argv)
            assert cm.value.code == 0
            help_by_command[tuple(argv)] = stdout.getvalue()

        help_text = "\n".join(help_by_command.values())
        assert "--no-auto-sync" not in help_text
        assert "--disable-auto-sync" not in help_text
        assert "no_auto_sync" not in help_text

        deps_add_help = " ".join(help_by_command[("deps", "add", "--help")].split())
        deps_remove_help = " ".join(help_by_command[("deps", "remove", "--help")].split())
        assert "Existing initiative, epic, or issue node id for dependency source" in deps_add_help
        assert "Existing initiative, epic, or issue node id for dependency target" in deps_add_help
        assert "Existing initiative, epic, or issue node id for dependency source" in deps_remove_help
        assert "Existing initiative, epic, or issue node id for dependency target" in deps_remove_help
        assert "Issue node id for dependency source" not in deps_add_help
        assert "Issue node id for dependency target" not in deps_add_help
        assert "Issue node id for dependency source" not in deps_remove_help
        assert "Issue node id for dependency target" not in deps_remove_help

    def test_sync_github_bulk_does_not_use_backfill_path_even_with_issue_index(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_sync_state,
            domain_models,
            _infra_artifact_writer,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            specdock_dir = repo_root / "spec-dock"
            specdock_dir.mkdir(parents=True, exist_ok=True)
            records = self._records(infra_contracts, repo_root)
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
                ]
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                node_repo=_FailingBackfillNodeRepo(),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                issue_gateway=issue_gateway,
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main", repo_slug="current/repo"),
                clock=_StubClock(),
            )

            collector_called = False
            had_attr = hasattr(app_sync_state, "collect_safe_current_repo_backfill_node_ids")
            original_collector = getattr(app_sync_state, "collect_safe_current_repo_backfill_node_ids", None)

            def _patched_collector(*args, **kwargs):
                del args, kwargs
                nonlocal collector_called
                collector_called = True
                return ["iss-local-00001"]

            app_sync_state.collect_safe_current_repo_backfill_node_ids = _patched_collector
            try:
                state = app_sync_state.collect_sync_state(
                    app_contracts.SyncRequest(
                        force=False,
                        github_enabled=True,
                        issue_limit=10000,
                        update_active_from_branch=False,
                    ),
                    ports,
                )
            finally:
                if had_attr:
                    app_sync_state.collect_safe_current_repo_backfill_node_ids = original_collector
                else:
                    delattr(app_sync_state, "collect_safe_current_repo_backfill_node_ids")

            assert "iss-local-00001" in state.graph.nodes_by_id
            assert len(issue_gateway.index_calls) == 1
            assert not collector_called

    def test_sync_github_keeps_foreign_coexistence_only_legacy_unscoped_without_backfill(self) -> None:
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
            foreign_issue_dir = (
                specdock_dir
                / "initiatives"
                / "init-local-00001-auth"
                / "epics"
                / "epic-local-00001-core"
                / "issues"
                / "iss-local-00003-foreign"
            )
            records.append(
                _record(
                    infra_contracts,
                    kind="issue",
                    node_id="iss-local-00003",
                    title="Foreign 301",
                    path=foreign_issue_dir,
                    parent_id="epic-local-00001",
                    initiative_id="init-local-00001",
                    epic_id="epic-local-00001",
                    github_issue_number=301,
                    github_repo_owner="other",
                    github_repo_name="repo",
                )
            )
            self._materialize_required_artifacts(records)
            node_repo = _StubNodeRepo()
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                node_repo=node_repo,
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": [], "iss-local-00003": []},
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                issue_gateway=_StubIssueGateway([]),
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main", repo_slug="current/repo"),
                clock=_StubClock(),
            )

            state = app_sync_state.collect_sync_state(
                app_contracts.SyncRequest(
                    force=False,
                    github_enabled=True,
                    issue_limit=10000,
                    update_active_from_branch=False,
                ),
                ports,
            )
            assert "iss-local-00001" in state.graph.nodes_by_id
            assert node_repo.backfill_calls == []

    def test_collect_sync_state_force_hard_fails_for_partial_scope_backfill_candidates(self) -> None:
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
            partial_scope_issue_dir = (
                specdock_dir
                / "initiatives"
                / "init-local-00001-auth"
                / "epics"
                / "epic-local-00001-core"
                / "issues"
                / "iss-local-00003-partial-scope"
            )
            records.append(
                _record(
                    infra_contracts,
                    kind="issue",
                    node_id="iss-local-00003",
                    title="Partial scope #301",
                    path=partial_scope_issue_dir,
                    parent_id="epic-local-00001",
                    initiative_id="init-local-00001",
                    epic_id="epic-local-00001",
                    github_issue_number=301,
                    github_repo_owner="current",
                    github_repo_name=None,
                )
            )
            self._materialize_required_artifacts(records)
            node_repo = _StubNodeRepo()
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                node_repo=node_repo,
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": [], "iss-local-00003": []},
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                issue_gateway=_StubIssueGateway([]),
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main", repo_slug="current/repo"),
                clock=_StubClock(),
            )

            with pytest.raises(RuntimeError, match="preflight validate failed: issue has invalid github linkage"):
                app_sync_state.collect_sync_state(
                    app_contracts.SyncRequest(
                        force=True,
                        github_enabled=True,
                        issue_limit=10000,
                        update_active_from_branch=False,
                    ),
                    ports,
                )
            assert node_repo.backfill_calls == []

    def test_collect_sync_state_force_hard_fails_for_partial_scope_when_another_validation_error_exists(self) -> None:
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
                github_repo_owner="current",
                github_repo_name=None,
            )
            records[3] = _record(
                infra_contracts,
                kind="issue",
                node_id="iss-local-1",
                title="DB",
                path=Path(records[3].path),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=302,
            )
            node_repo = _StubNodeRepo()
            issue_gateway = _StubIssueGateway([])
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                node_repo=node_repo,
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-1": []},
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                issue_gateway=issue_gateway,
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main", repo_slug="current/repo"),
                clock=_StubClock(),
            )

            with pytest.raises(RuntimeError, match="preflight validate failed: issue has invalid github linkage"):
                app_sync_state.collect_sync_state(
                    app_contracts.SyncRequest(
                        force=True,
                        github_enabled=True,
                        issue_limit=10000,
                        update_active_from_branch=False,
                    ),
                    ports,
                )
            assert node_repo.backfill_calls == []
            assert issue_gateway.index_calls == []
            assert issue_gateway.view_calls == []

    def test_sync_github_skips_backfill_when_current_repo_slug_is_unknown(self) -> None:
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
            node_repo = _StubNodeRepo()
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                node_repo=node_repo,
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                deps_topology_reader=_StubDepsTopologyReader(
                    infra_contracts,
                    {"iss-local-00001": [], "iss-local-00002": []},
                ),
                derived_state_reader=_StubDerivedStateReader({}),
                issue_gateway=_StubIssueGateway([]),
                active_state_store=_StubActiveStateStore(infra_contracts, []),
                git_gateway=_StubGitGateway("main", repo_slug=None),
                clock=_StubClock(),
            )

            state = app_sync_state.collect_sync_state(
                app_contracts.SyncRequest(
                    force=False,
                    github_enabled=True,
                    issue_limit=10000,
                    update_active_from_branch=False,
                ),
                ports,
            )
            assert "iss-local-00001" in state.graph.nodes_by_id
            assert node_repo.backfill_calls == []
