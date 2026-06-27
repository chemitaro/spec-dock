import contextlib
from dataclasses import replace
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

import pytest

_REQUIRED_NODE_DOCS = ("requirement.md", "design.md", "plan.md", "report.md")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: object) -> None:
    _write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def _materialize_node(node_dir: Path, meta: dict[str, object]) -> None:
    node_dir.mkdir(parents=True, exist_ok=True)
    _write_json(node_dir / ".meta.json", meta)
    for doc_name in _REQUIRED_NODE_DOCS:
        _write_text(node_dir / doc_name, f"# {doc_name}\n")


def _run_runtime_capture(target: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    script = target / "spec-dock" / "scripts" / "spec-dock"
    assert script.is_file(), f"runtime script missing: {script}"
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=str(target),
        capture_output=True,
        text=True,
    )


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime import app as runtime_app
        from spec_dock_runtime.application import (
            check_deps as app_check_deps,
            contracts as app_contracts,
            ports as app_ports,
            status_context as app_status_context,
            validate_tree as app_validate_tree,
        )
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.infra import contracts as infra_contracts
        from spec_dock_runtime.presentation import (
            cli_text as presentation_cli_text,
            json_state as presentation_json_state,
        )
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
            meta_path=(specdock_dir / "initiatives" / "init-local-00001-auth-platform" / ".meta.json").as_posix(),
        ),
        infra_contracts.StoredMetaRecord(
            kind="epic",
            id="epic-local-00001",
            title="JWT Auth",
            slug="jwt-auth",
            path=(
                specdock_dir / "initiatives" / "init-local-00001-auth-platform" / "epics" / "epic-local-00001-jwt-auth"
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
    def __init__(self, issue_depends_on_map, warnings=None, raw_node_depends_on_map=None):
        self.issue_depends_on_map = dict(issue_depends_on_map)
        self.warnings = list(warnings or [])
        self.raw_node_depends_on_map = {
            node_id: list(depends_on) for node_id, depends_on in dict(raw_node_depends_on_map or {}).items()
        }
        self.calls = 0
        self.raw_calls = 0

    def load_issue_depends_on_map(self, specdock_dir, graph):
        del specdock_dir, graph
        self.calls += 1
        _, _, _, _, _, _, _, infra_contracts, _, _ = _runtime_modules()
        return infra_contracts.DepsTopologyLoadResult(
            issue_depends_on_map=dict(self.issue_depends_on_map),
            warnings=list(self.warnings),
        )

    def load_node_dependency_resolutions(self, specdock_dir, graph):
        del specdock_dir, graph
        self.raw_calls += 1
        _, _, _, _, _, _, _, infra_contracts, _, _ = _runtime_modules()
        return {
            node_id: [
                infra_contracts.DirectDependencyResolution(
                    raw_ref=dep_id,
                    resolved_node_id=dep_id,
                )
                for dep_id in depends_on
            ]
            for node_id, depends_on in self.raw_node_depends_on_map.items()
        }


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


class TestRuntimeDepsS04:
    def test_cli_deps_check_json_blocks_empty_high_level_source_direct_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            from spec_dock.cli import main

            assert main(["init", str(repo_root)]) == 0
            marker = {"managed": True, "do_not_edit": True, "edit_via": "spec-dock"}
            timestamp = "2026-06-27T00:00:00+09:00"
            initiatives_dir = repo_root / "spec-dock" / "initiatives"
            _materialize_node(
                initiatives_dir / "init-local-00001-source-initiative",
                {
                    "schema_version": 1,
                    "type": "initiative",
                    "id": "init-local-00001",
                    "title": "Source initiative",
                    "slug": "source-initiative",
                    "created_at": timestamp,
                    "updated_at": timestamp,
                    "parent_id": None,
                    "initiative_id": None,
                    "epic_id": None,
                    "depends_on": ["epic-local-00001"],
                    "_spec_dock": marker,
                },
            )
            _materialize_node(
                initiatives_dir / "init-local-00002-target-initiative",
                {
                    "schema_version": 1,
                    "type": "initiative",
                    "id": "init-local-00002",
                    "title": "Target initiative",
                    "slug": "target-initiative",
                    "created_at": timestamp,
                    "updated_at": timestamp,
                    "parent_id": None,
                    "initiative_id": None,
                    "epic_id": None,
                    "depends_on": [],
                    "_spec_dock": marker,
                },
            )
            _materialize_node(
                initiatives_dir / "init-local-00002-target-initiative" / "epics" / "epic-local-00001-target-epic",
                {
                    "schema_version": 1,
                    "type": "epic",
                    "id": "epic-local-00001",
                    "title": "Target epic",
                    "slug": "target-epic",
                    "created_at": timestamp,
                    "updated_at": timestamp,
                    "parent_id": "init-local-00002",
                    "initiative_id": "init-local-00002",
                    "epic_id": None,
                    "depends_on": [],
                    "_spec_dock": marker,
                },
            )

            result = _run_runtime_capture(
                repo_root,
                ["deps", "check", "--id", "init-local-00001", "--no-github", "--json"],
            )

        assert result.returncode == 3, result.stdout + result.stderr
        assert result.stderr == ""
        payload = json.loads(result.stdout)
        assert payload["target"] == "init-local-00001"
        assert payload["ready"] is False
        assert payload["effective_depends_on"] == []
        assert payload["blockers"] == ["epic-local-00001"]
        assert payload["dependency_contexts"] == []
        assert payload["direct_node_dependencies"] == [
            {
                "source_node_id": "init-local-00001",
                "source_node_kind": "initiative",
                "target_node_id": "epic-local-00001",
                "target_node_kind": "epic",
                "target_issue_ids": [],
                "expansion": "empty",
                "lifecycle_state": "open",
                "lifecycle_source": "local",
                "dependency_disposition": "blocking",
                "disposition_basis": "empty_open_container",
            }
        ]

    def test_cli_deps_check_json_blocks_epic_source_direct_node_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            from spec_dock.cli import main

            assert main(["init", str(repo_root)]) == 0
            marker = {"managed": True, "do_not_edit": True, "edit_via": "spec-dock"}
            timestamp = "2026-06-27T00:00:00+09:00"
            initiatives_dir = repo_root / "spec-dock" / "initiatives"
            _materialize_node(
                initiatives_dir / "init-local-00001-source-initiative",
                {
                    "schema_version": 1,
                    "type": "initiative",
                    "id": "init-local-00001",
                    "title": "Source initiative",
                    "slug": "source-initiative",
                    "created_at": timestamp,
                    "updated_at": timestamp,
                    "parent_id": None,
                    "initiative_id": None,
                    "epic_id": None,
                    "depends_on": [],
                    "_spec_dock": marker,
                },
            )
            _materialize_node(
                initiatives_dir / "init-local-00001-source-initiative" / "epics" / "epic-local-00001-source-epic",
                {
                    "schema_version": 1,
                    "type": "epic",
                    "id": "epic-local-00001",
                    "title": "Source epic",
                    "slug": "source-epic",
                    "created_at": timestamp,
                    "updated_at": timestamp,
                    "parent_id": "init-local-00001",
                    "initiative_id": "init-local-00001",
                    "epic_id": None,
                    "depends_on": ["epic-local-00002"],
                    "_spec_dock": marker,
                },
            )
            _materialize_node(
                initiatives_dir / "init-local-00002-target-initiative",
                {
                    "schema_version": 1,
                    "type": "initiative",
                    "id": "init-local-00002",
                    "title": "Target initiative",
                    "slug": "target-initiative",
                    "created_at": timestamp,
                    "updated_at": timestamp,
                    "parent_id": None,
                    "initiative_id": None,
                    "epic_id": None,
                    "depends_on": [],
                    "_spec_dock": marker,
                },
            )
            _materialize_node(
                initiatives_dir / "init-local-00002-target-initiative" / "epics" / "epic-local-00002-target-epic",
                {
                    "schema_version": 1,
                    "type": "epic",
                    "id": "epic-local-00002",
                    "title": "Target epic",
                    "slug": "target-epic",
                    "created_at": timestamp,
                    "updated_at": timestamp,
                    "parent_id": "init-local-00002",
                    "initiative_id": "init-local-00002",
                    "epic_id": None,
                    "depends_on": [],
                    "_spec_dock": marker,
                },
            )

            result = _run_runtime_capture(
                repo_root,
                ["deps", "check", "--id", "epic-local-00001", "--no-github", "--json"],
            )

        assert result.returncode == 3, result.stdout + result.stderr
        assert result.stderr == ""
        payload = json.loads(result.stdout)
        assert payload["target"] == "epic-local-00001"
        assert payload["ready"] is False
        assert payload["effective_depends_on"] == []
        assert payload["blockers"] == ["epic-local-00002"]
        assert payload["dependency_contexts"] == []
        assert payload["direct_node_dependencies"] == [
            {
                "source_node_id": "epic-local-00001",
                "source_node_kind": "epic",
                "target_node_id": "epic-local-00002",
                "target_node_kind": "epic",
                "target_issue_ids": [],
                "expansion": "empty",
                "lifecycle_state": "open",
                "lifecycle_source": "local",
                "dependency_disposition": "blocking",
                "disposition_basis": "empty_open_container",
            }
        ]

    def test_cli_deps_check_json_keeps_non_empty_source_direct_status_separate(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            from spec_dock.cli import main

            assert main(["init", str(repo_root)]) == 0
            marker = {"managed": True, "do_not_edit": True, "edit_via": "spec-dock"}
            timestamp = "2026-06-27T00:00:00+09:00"
            initiatives_dir = repo_root / "spec-dock" / "initiatives"
            _materialize_node(
                initiatives_dir / "init-local-00001-source-initiative",
                {
                    "schema_version": 1,
                    "type": "initiative",
                    "id": "init-local-00001",
                    "title": "Source initiative",
                    "slug": "source-initiative",
                    "created_at": timestamp,
                    "updated_at": timestamp,
                    "parent_id": None,
                    "initiative_id": None,
                    "epic_id": None,
                    "depends_on": ["epic-local-00002"],
                    "_spec_dock": marker,
                },
            )
            _materialize_node(
                initiatives_dir / "init-local-00001-source-initiative" / "epics" / "epic-local-00001-source-epic",
                {
                    "schema_version": 1,
                    "type": "epic",
                    "id": "epic-local-00001",
                    "title": "Source epic",
                    "slug": "source-epic",
                    "created_at": timestamp,
                    "updated_at": timestamp,
                    "parent_id": "init-local-00001",
                    "initiative_id": "init-local-00001",
                    "epic_id": None,
                    "depends_on": [],
                    "_spec_dock": marker,
                },
            )
            _materialize_node(
                initiatives_dir
                / "init-local-00001-source-initiative"
                / "epics"
                / "epic-local-00001-source-epic"
                / "issues"
                / "iss-local-00001-source-issue",
                {
                    "schema_version": 1,
                    "type": "issue",
                    "id": "iss-local-00001",
                    "title": "Source issue",
                    "slug": "source-issue",
                    "created_at": timestamp,
                    "updated_at": timestamp,
                    "parent_id": "epic-local-00001",
                    "initiative_id": "init-local-00001",
                    "epic_id": "epic-local-00001",
                    "depends_on": [],
                    "_spec_dock": marker,
                },
            )
            _materialize_node(
                initiatives_dir / "init-local-00002-target-initiative",
                {
                    "schema_version": 1,
                    "type": "initiative",
                    "id": "init-local-00002",
                    "title": "Target initiative",
                    "slug": "target-initiative",
                    "created_at": timestamp,
                    "updated_at": timestamp,
                    "parent_id": None,
                    "initiative_id": None,
                    "epic_id": None,
                    "depends_on": [],
                    "_spec_dock": marker,
                },
            )
            _materialize_node(
                initiatives_dir / "init-local-00002-target-initiative" / "epics" / "epic-local-00002-target-epic",
                {
                    "schema_version": 1,
                    "type": "epic",
                    "id": "epic-local-00002",
                    "title": "Target epic",
                    "slug": "target-epic",
                    "created_at": timestamp,
                    "updated_at": timestamp,
                    "parent_id": "init-local-00002",
                    "initiative_id": "init-local-00002",
                    "epic_id": None,
                    "depends_on": [],
                    "_spec_dock": marker,
                },
            )
            _materialize_node(
                initiatives_dir
                / "init-local-00002-target-initiative"
                / "epics"
                / "epic-local-00002-target-epic"
                / "issues"
                / "iss-local-00002-target-issue",
                {
                    "schema_version": 1,
                    "type": "issue",
                    "id": "iss-local-00002",
                    "title": "Target issue",
                    "slug": "target-issue",
                    "created_at": timestamp,
                    "updated_at": timestamp,
                    "parent_id": "epic-local-00002",
                    "initiative_id": "init-local-00002",
                    "epic_id": "epic-local-00002",
                    "depends_on": [],
                    "_spec_dock": marker,
                },
            )

            result = _run_runtime_capture(
                repo_root,
                ["deps", "check", "--id", "init-local-00001", "--no-github", "--json"],
            )

        assert result.returncode == 3, result.stdout + result.stderr
        assert result.stderr == ""
        payload = json.loads(result.stdout)
        assert payload["target"] == "init-local-00001"
        assert payload["ready"] is False
        assert payload["effective_depends_on"] == ["iss-local-00002"]
        assert payload["blockers"] == ["epic-local-00002", "iss-local-00002"]
        assert payload["dependency_contexts"] == [
            {
                "source_node_id": "init-local-00001",
                "source_issue_id": "iss-local-00001",
                "target_node_id": "epic-local-00002",
                "target_node_kind": "epic",
                "target_issue_ids": ["iss-local-00002"],
                "expansion": "expanded",
                "lifecycle_state": "open",
                "lifecycle_source": "descendant_aggregate",
                "dependency_disposition": "blocking",
                "disposition_basis": "descendant_issue_open",
            }
        ]
        assert payload["direct_node_dependencies"] == [
            {
                "source_node_id": "init-local-00001",
                "source_node_kind": "initiative",
                "target_node_id": "epic-local-00002",
                "target_node_kind": "epic",
                "target_issue_ids": ["iss-local-00002"],
                "expansion": "expanded",
                "lifecycle_state": "open",
                "lifecycle_source": "descendant_aggregate",
                "dependency_disposition": "blocking",
                "disposition_basis": "descendant_issue_open",
            }
        ]

    def test_cli_sync_no_github_writes_index_all_raw_direct_edges_for_high_level_source(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            from spec_dock.cli import main

            assert main(["init", str(repo_root)]) == 0
            marker = {"managed": True, "do_not_edit": True, "edit_via": "spec-dock"}
            timestamp = "2026-06-27T00:00:00+09:00"
            initiatives_dir = repo_root / "spec-dock" / "initiatives"
            _materialize_node(
                initiatives_dir / "init-local-00001-source-initiative",
                {
                    "schema_version": 1,
                    "type": "initiative",
                    "id": "init-local-00001",
                    "title": "Source initiative",
                    "slug": "source-initiative",
                    "created_at": timestamp,
                    "updated_at": timestamp,
                    "parent_id": None,
                    "initiative_id": None,
                    "epic_id": None,
                    "depends_on": ["epic-local-00001"],
                    "_spec_dock": marker,
                },
            )
            _materialize_node(
                initiatives_dir / "init-local-00002-target-initiative",
                {
                    "schema_version": 1,
                    "type": "initiative",
                    "id": "init-local-00002",
                    "title": "Target initiative",
                    "slug": "target-initiative",
                    "created_at": timestamp,
                    "updated_at": timestamp,
                    "parent_id": None,
                    "initiative_id": None,
                    "epic_id": None,
                    "depends_on": [],
                    "_spec_dock": marker,
                },
            )
            _materialize_node(
                initiatives_dir / "init-local-00002-target-initiative" / "epics" / "epic-local-00001-target-epic",
                {
                    "schema_version": 1,
                    "type": "epic",
                    "id": "epic-local-00001",
                    "title": "Target epic",
                    "slug": "target-epic",
                    "created_at": timestamp,
                    "updated_at": timestamp,
                    "parent_id": "init-local-00002",
                    "initiative_id": "init-local-00002",
                    "epic_id": None,
                    "github": {"issue_number": 201},
                    "depends_on": [],
                    "_spec_dock": marker,
                },
            )

            result = _run_runtime_capture(
                repo_root,
                ["sync", "--no-github", "--no-update-active"],
            )

            agent_dir = repo_root / "spec-dock" / ".agent"
            index_all = json.loads((agent_dir / "index-all.json").read_text(encoding="utf-8"))
            index_todo = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            deps_issues = json.loads((agent_dir / "deps-issues.json").read_text(encoding="utf-8"))

            assert result.returncode == 0, result.stdout + result.stderr
            assert result.stderr == ""
            expected_raw_edges = [
                {
                    "from": "init-local-00001",
                    "from_kind": "initiative",
                    "to": "epic-local-00001",
                    "to_kind": "epic",
                    "relation": "raw_direct",
                }
            ]
            assert index_all["deps"]["raw_direct_edges"] == expected_raw_edges
            assert "raw_direct_edges" not in index_todo
            assert "raw_direct_edges" not in index_todo["deps"]
            assert "raw_direct_edges" not in deps_issues
            assert "raw_direct_edges" not in deps_issues["deps"]

            index_all["nodes"]["epic-local-00001"]["github"] = {
                "number": None,
                "state": "closed",
                "updated_at": "2026-06-27T00:00:00+09:00",
                "url": None,
            }
            _write_json(agent_dir / "index-all.json", index_all)

            closed_result = _run_runtime_capture(
                repo_root,
                ["sync", "--no-github", "--no-update-active"],
            )
            closed_index_all = json.loads((agent_dir / "index-all.json").read_text(encoding="utf-8"))
            closed_index_todo = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            closed_deps_issues = json.loads((agent_dir / "deps-issues.json").read_text(encoding="utf-8"))
            closed_deps_raw_puml = (repo_root / "spec-dock" / "deps-raw.puml").read_text(encoding="utf-8")
            source_meta = json.loads(
                (initiatives_dir / "init-local-00001-source-initiative" / ".meta.json").read_text(encoding="utf-8")
            )
            target_meta = json.loads(
                (
                    initiatives_dir
                    / "init-local-00002-target-initiative"
                    / "epics"
                    / "epic-local-00001-target-epic"
                    / ".meta.json"
                ).read_text(encoding="utf-8")
            )

            assert closed_result.returncode == 0, closed_result.stdout + closed_result.stderr
            assert closed_result.stderr == ""
            assert closed_index_all["nodes"]["epic-local-00001"]["github"]["state"] == "CLOSED"
            assert closed_index_all["deps"]["raw_direct_edges"] == expected_raw_edges
            assert "raw_direct_edges" not in closed_index_todo
            assert "raw_direct_edges" not in closed_index_todo["deps"]
            assert "raw_direct_edges" not in closed_deps_issues
            assert "raw_direct_edges" not in closed_deps_issues["deps"]
            assert "Nepic_local_00001 --> Ninit_local_00001 : raw_direct" not in closed_deps_raw_puml
            assert 'note "No raw direct dependencies to render" as Empty' in closed_deps_raw_puml
            assert source_meta["depends_on"] == ["epic-local-00001"]
            assert target_meta["depends_on"] == []

    def test_collect_sync_state_reads_shared_topology_map(self) -> None:
        (
            _runtime_app,
            _app_check_deps,
            app_contracts,
            app_ports,
            _app_status_context,
            _app_validate_tree,
            _domain_models,
            infra_contracts,
            _presentation_cli_text,
            _presentation_json_state,
        ) = _runtime_modules()
        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime.application import sync_state as app_sync_state
        finally:
            sys.path.pop(0)

        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            records = [
                replace(
                    record,
                    github_repo_owner="current",
                    github_repo_name="repo",
                )
                for record in _sample_records(infra_contracts, repo_root=repo_root)
            ]
            _materialize_required_artifacts(records)
            deps_reader = _StubDepsTopologyReader({
                "iss-local-00001": [],
                "iss-local-00002": ["iss-local-00001"],
            })
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=repo_root / "spec-dock",
                derived_state_reader=_StubDerivedStateReader({"iss-local-00001": "open", "iss-local-00002": "open"}),
                issue_gateway=_StubIssueGateway([]),
                deps_topology_reader=deps_reader,
            )

            state = app_sync_state.collect_sync_state(
                app_contracts.SyncRequest(
                    force=False,
                    github_enabled=False,
                    issue_limit=10000,
                    update_active_from_branch=False,
                ),
                ports,
            )

        assert deps_reader.calls == 1
        assert state.issue_depends_on_map.get("iss-local-00002") == ["iss-local-00001"]
        assert any(
            node.node_id == "iss-local-00002" and node.effective_depends_on == ["iss-local-00001"]
            for node in state.deps_state.nodes
        )
        assert state.deps_preflight_error is None

    def test_collect_sync_state_carries_raw_direct_dependencies(self) -> None:
        (
            _runtime_app,
            _app_check_deps,
            app_contracts,
            app_ports,
            _app_status_context,
            _app_validate_tree,
            _domain_models,
            infra_contracts,
            _presentation_cli_text,
            _presentation_json_state,
        ) = _runtime_modules()
        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime.application import sync_state as app_sync_state
        finally:
            sys.path.pop(0)

        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            records = _sample_records(infra_contracts, repo_root=repo_root)
            _materialize_required_artifacts(records)
            deps_reader = _StubDepsTopologyReader(
                {
                    "iss-local-00001": [],
                    "iss-local-00002": ["iss-local-00001"],
                },
                raw_node_depends_on_map={
                    "iss-local-00001": [],
                    "iss-local-00002": ["iss-local-00001"],
                },
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=repo_root / "spec-dock",
                derived_state_reader=_StubDerivedStateReader({"iss-local-00001": "open", "iss-local-00002": "open"}),
                issue_gateway=_StubIssueGateway([]),
                deps_topology_reader=deps_reader,
            )

            state = app_sync_state.collect_sync_state(
                app_contracts.SyncRequest(
                    force=False,
                    github_enabled=False,
                    issue_limit=10000,
                    update_active_from_branch=False,
                ),
                ports,
            )

        assert deps_reader.raw_calls == 1
        assert state.raw_node_depends_on_map == {
            "iss-local-00002": ["iss-local-00001"],
        }

    def test_artifact_bundle_requires_explicit_deps_raw_artifact(self) -> None:
        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime.presentation import contracts as presentation_contracts
        finally:
            sys.path.pop(0)

        with pytest.raises(TypeError):
            presentation_contracts.ArtifactBundle(
                index=presentation_contracts.IndexArtifact(
                    all_json_text="{}",
                    todo_json_text="{}",
                ),
                tree=presentation_contracts.TreeArtifact(
                    all_json_text="{}",
                    todo_json_text="{}",
                    all_puml_text="@startuml\n@enduml\n",
                    todo_puml_text="@startuml\n@enduml\n",
                ),
                deps_issues=presentation_contracts.DepsIssuesArtifact(
                    json_text="{}",
                    puml_text="@startuml\n@enduml\n",
                ),
                dashboard=presentation_contracts.DashboardArtifact(markdown_text=""),
            )

    def test_collect_sync_state_keeps_raw_parent_dependencies_out_of_readiness_map(self) -> None:
        (
            _runtime_app,
            _app_check_deps,
            app_contracts,
            app_ports,
            _app_status_context,
            _app_validate_tree,
            _domain_models,
            infra_contracts,
            _presentation_cli_text,
            _presentation_json_state,
        ) = _runtime_modules()
        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime.application import sync_state as app_sync_state
        finally:
            sys.path.pop(0)

        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            records = _sample_records(infra_contracts, repo_root=repo_root)
            records.append(
                infra_contracts.StoredMetaRecord(
                    kind="epic",
                    id="epic-local-00002",
                    title="Password Auth",
                    slug="password-auth",
                    path=(
                        repo_root
                        / "spec-dock"
                        / "initiatives"
                        / "init-local-00001-auth-platform"
                        / "epics"
                        / "epic-local-00002-password-auth"
                    ).as_posix(),
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=202,
                    meta_path=(
                        repo_root
                        / "spec-dock"
                        / "initiatives"
                        / "init-local-00001-auth-platform"
                        / "epics"
                        / "epic-local-00002-password-auth"
                        / ".meta.json"
                    ).as_posix(),
                )
            )
            _materialize_required_artifacts(records)
            deps_reader = _StubDepsTopologyReader(
                {
                    "iss-local-00001": [],
                    "iss-local-00002": [],
                },
                raw_node_depends_on_map={
                    "epic-local-00002": ["epic-local-00001"],
                },
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=repo_root / "spec-dock",
                derived_state_reader=_StubDerivedStateReader({"iss-local-00001": "open", "iss-local-00002": "open"}),
                issue_gateway=_StubIssueGateway([]),
                deps_topology_reader=deps_reader,
            )

            state = app_sync_state.collect_sync_state(
                app_contracts.SyncRequest(
                    force=False,
                    github_enabled=False,
                    issue_limit=10000,
                    update_active_from_branch=False,
                ),
                ports,
            )

        assert state.raw_node_depends_on_map == {
            "epic-local-00002": ["epic-local-00001"],
        }
        assert state.issue_depends_on_map == {
            "iss-local-00001": [],
            "iss-local-00002": [],
        }
        assert all(node.effective_depends_on == [] for node in state.deps_state.nodes)

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
        assert context_gh.issue_statuses["iss-local-00001"].authority == "github"
        assert context_gh.issue_statuses["iss-local-00001"].effective_status == "done"
        assert context_gh.issue_statuses["iss-local-00001"].source == "github"
        assert not context_gh.issue_statuses["iss-local-00001"].stale
        assert context_gh.issue_statuses["iss-local-00001"].last_sync_at == "t"

        context_cache = app_status_context.resolve_issue_status_context(
            graph,
            github_enabled=False,
            issue_snapshots=snapshots,
            cached_issue_status_by_id={"iss-local-00001": "open"},
        )
        assert context_cache.issue_statuses["iss-local-00001"].effective_status == "open"
        assert context_cache.issue_statuses["iss-local-00001"].source == "cache"
        assert context_cache.issue_statuses["iss-local-00001"].stale

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
            derived_state_reader=_StubDerivedStateReader({"iss-local-00001": "open", "iss-local-00002": "open"}),
            issue_gateway=_StubIssueGateway([]),
            active_state_store=_StubActiveStateStore("iss-local-00002"),
            deps_topology_reader=_StubDepsTopologyReader({
                "iss-local-00001": [],
                "iss-local-00002": ["iss-local-00001"],
            }),
        )
        result = app_check_deps.check_deps(
            app_contracts.CheckDepsRequest(
                target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00002", github_issue_number=None),
                use_github=False,
                issue_limit=10000,
            ),
            ports,
        )
        assert not result.inspection.evaluation.ready
        assert result.inspection.evaluation.blockers == ["iss-local-00001"]
        assert result.warnings == []

        cycle_ports = app_ports.Ports(
            node_reader=_StubNodeReader(records),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
            derived_state_reader=_StubDerivedStateReader({}),
            issue_gateway=_StubIssueGateway([]),
            active_state_store=_StubActiveStateStore(None),
            deps_topology_reader=_StubDepsTopologyReader({
                "iss-local-00001": ["iss-local-00002"],
                "iss-local-00002": ["iss-local-00001"],
            }),
        )
        with pytest.raises(RuntimeError):
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
        assert status.source == "github"
        assert status.effective_status == "done"
        assert not status.stale
        assert issue_gateway.view_calls == [("/repo", 123, "other/repo")]
        assert "gh_index_incomplete" not in result.warnings

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
        assert status.source == "github"
        assert status.effective_status == "open"
        assert issue_gateway.view_calls == []
        assert "gh_fetch_failed" not in result.warnings

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
        assert status.source == "github"
        assert status.effective_status == "done"
        assert issue_gateway.view_calls == [("/repo", 123, "current/repo")]
        assert "gh_fetch_failed" not in result.warnings
        assert "gh_index_incomplete" not in result.warnings

    def test_check_deps_falls_back_to_current_repo_view_for_unscoped_linked_epic_when_index_missing_key(self) -> None:
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
                github_issue_number=201,
                meta_path="spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/.meta.json",
            ),
            infra_contracts.StoredMetaRecord(
                kind="issue",
                id="iss-local-00001",
                title="Target",
                slug="target",
                path=(
                    "spec-dock/initiatives/init-local-00001-auth-platform/"
                    "epics/epic-local-00001-jwt-auth/issues/iss-local-00001-target"
                ),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=None,
                meta_path=(
                    "spec-dock/initiatives/init-local-00001-auth-platform/"
                    "epics/epic-local-00001-jwt-auth/issues/iss-local-00001-target/.meta.json"
                ),
            ),
        ]
        issue_gateway = _StubIssueGateway(
            snapshots=[],
            foreign_snapshots={
                ("current/repo", 201): domain_models.IssueSnapshot(
                    issue_number=201,
                    state="CLOSED",
                    title="Current repo #201",
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
                target=app_contracts.TargetRef(kind="node_id", node_id="epic-local-00001", github_issue_number=None),
                use_github=True,
                issue_limit=10000,
            ),
            ports,
        )

        target_status = result.inspection.issue_statuses["epic-local-00001"]
        assert target_status.source == "github"
        assert target_status.effective_status == "done"
        assert not target_status.stale
        assert issue_gateway.view_calls == [("/repo", 201, "current/repo")]
        assert "gh_fetch_failed" not in result.warnings
        assert "gh_index_incomplete" not in result.warnings

    def test_check_deps_github_uses_current_repo_slug_for_unscoped_current_issue_and_keeps_foreign_same_number(
        self,
    ) -> None:
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
            deps_topology_reader=_StubDepsTopologyReader({
                "iss-local-00001": [],
                "iss-local-00002": [],
                "iss-local-00003": ["iss-local-00001", "iss-local-00002"],
            }),
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
        assert not result.inspection.evaluation.ready
        assert result.inspection.evaluation.guard_reason == "blocked"
        assert result.inspection.evaluation.blockers == ["iss-local-00001"]
        assert issue_gateway.view_calls == [("/repo", 123, "other/repo")]
        assert result.warnings == []

        payload = json.loads(presentation_json_state.render_deps_check_json(result))
        assert not payload["ready"]
        assert payload["blockers"] == ["iss-local-00001"]
        assert payload["nodes"]["iss-local-00001"]["state"] == "ready"
        assert payload["nodes"]["iss-local-00001"]["source"] == "github"
        assert payload["nodes"]["iss-local-00001"]["effective_status"] == "open"
        assert payload["nodes"]["iss-local-00002"]["state"] == "done"
        assert payload["nodes"]["iss-local-00002"]["source"] == "github"
        assert payload["nodes"]["iss-local-00002"]["effective_status"] == "done"

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
            records = [
                replace(
                    record,
                    github_repo_owner="current",
                    github_repo_name="repo",
                )
                for record in _sample_records(infra_contracts, repo_root=repo_root)
            ]
            _materialize_required_artifacts(records)
            deps_reader = _StubDepsTopologyReader({
                "iss-local-00001": ["iss-local-00002"],
                "iss-local-00002": ["iss-local-00001"],
            })
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=repo_root / "spec-dock",
                deps_topology_reader=deps_reader,
            )
            result = app_validate_tree.validate_tree(app_contracts.ValidateTreeRequest(), ports)
            assert deps_reader.calls == 1
            assert result.report.errors
            assert "Dependency cycle detected" in result.report.errors[0]

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
        assert "spec-dock: blocked (deps check)" in text.stderr_lines[0]
        assert "authority=github" in text.stderr_lines[0]
        assert "effective_status=open" in text.stderr_lines[0]
        assert "source=cache" in text.stderr_lines[0]
        assert "stale=true" in text.stderr_lines[0]
        assert "last_sync_at=2026-03-17T12:34:56Z" in text.stderr_lines[0]
        assert text.warnings == ["gh_fetch_failed"]

        payload = json.loads(presentation_json_state.render_deps_check_json(result))
        assert payload["target"] == "iss-local-00002"
        assert payload["blockers"] == ["iss-local-00001"]
        assert payload["target_status"]["source"] == "cache"
        assert payload["target_status"]["stale"]
        assert payload["target_status"]["last_sync_at"] == "2026-03-17T12:34:56Z"
        assert payload["nodes"]["iss-local-00001"]["source"] == "cache"
        assert payload["warnings"] == ["gh_fetch_failed"]

    def test_legacy_deps_path_delegates_and_exit_codes(self) -> None:
        (
            runtime_app,
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

            assert exit_code == 3
            assert stdout.getvalue() == ""
            stderr_lines = [line for line in stderr.getvalue().splitlines() if line.strip()]
            assert stderr_lines[0].startswith("spec-dock: (warn) gh_fetch_failed")
            assert "spec-dock: blocked (deps check)" in stderr_lines[1]
            assert "authority=github" in stderr_lines[1]
            assert "effective_status=open" in stderr_lines[1]
            assert "source=cache" in stderr_lines[1]
            assert "stale=true" in stderr_lines[1]
            assert "last_sync_at=2026-03-17T12:34:56Z" in stderr_lines[1]
            assert calls["req"].target.kind == "node_id"
            assert calls["req"].target.node_id == "iss-local-1"
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
            assert exit_code == 0
            assert stderr.getvalue().strip() == ""
            ready_line = stdout.getvalue().strip()
            assert "spec-dock: ok (deps check)" in ready_line
            assert "authority=github" in ready_line
            assert "effective_status=open" in ready_line
            assert "source=github" in ready_line
            assert "stale=false" in ready_line
            assert "last_sync_at=2026-03-17T12:34:56Z" in ready_line

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = runtime_app.main(["deps", "check", "#123", "--json"])
            assert exit_code == 0
            assert stderr.getvalue().strip() == ""
            payload = json.loads(stdout.getvalue())
            assert payload["target"] == "iss-00123"
            assert payload["ready"]
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
            assert exit_code == 1
            assert "error: boom" in stderr.getvalue()
        finally:
            runtime_app._find_specdock_dir = original_find_specdock_dir
            cli_bootstrap.application_check_deps = original_application_check_deps

    def test_legacy_deps_path_rejects_non_canonical_url_like_target(self) -> None:
        (runtime_app, *_) = _runtime_modules()
        from spec_dock_runtime.cli import bootstrap as cli_bootstrap

        calls = {"count": 0}
        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_application_check_deps = cli_bootstrap.application_check_deps
        try:
            runtime_app._find_specdock_dir = lambda: Path("/repo/spec-dock")

            def _fake_check_deps(req, ports):
                del req, ports
                calls["count"] += 1
                raise AssertionError("application_check_deps must not run for invalid target")

            cli_bootstrap.application_check_deps = _fake_check_deps

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = runtime_app.main(["deps", "check", "git@github.com:owner/repo/issues/123"])

            assert exit_code == 1
            assert stdout.getvalue().strip() == ""
            assert "Invalid target" in stderr.getvalue()
            assert calls["count"] == 0
        finally:
            runtime_app._find_specdock_dir = original_find_specdock_dir
            cli_bootstrap.application_check_deps = original_application_check_deps

    def test_legacy_deps_add_path_delegates_and_exit_code_zero(self) -> None:
        (
            runtime_app,
            _app_check_deps,
            app_contracts,
            _app_ports,
            _app_status_context,
            _app_validate_tree,
            _domain_models,
            _infra_contracts,
            _presentation_cli_text,
            _presentation_json_state,
        ) = _runtime_modules()
        from spec_dock_runtime.cli import bootstrap as cli_bootstrap

        calls: dict[str, object] = {}
        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_application_mutate_deps = cli_bootstrap.application_mutate_deps
        try:
            runtime_app._find_specdock_dir = lambda: Path("/repo/spec-dock")

            def _fake_mutate_deps(req, ports):
                calls["req"] = req
                calls["ports"] = ports
                return app_contracts.MutateDepsResult(
                    action="add",
                    from_id="iss-local-00001",
                    to_id="iss-local-00002",
                    result="updated",
                    warnings=[],
                )

            cli_bootstrap.application_mutate_deps = _fake_mutate_deps

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = runtime_app.main(["deps", "add", "--from", "iss-local-00001", "--to", "iss-local-00002"])

            assert exit_code == 0
            assert stderr.getvalue().strip() == ""
            assert (
                stdout.getvalue().strip()
                == "spec-dock: ok (deps add) from=iss-local-00001 to=iss-local-00002 result=updated"
            )
            req = calls["req"]
            assert req.action == "add"
            assert req.from_id == "iss-local-00001"
            assert req.to_id == "iss-local-00002"
        finally:
            runtime_app._find_specdock_dir = original_find_specdock_dir
            cli_bootstrap.application_mutate_deps = original_application_mutate_deps

    def test_legacy_deps_add_path_renders_unchanged_result(self) -> None:
        (
            runtime_app,
            _app_check_deps,
            app_contracts,
            _app_ports,
            _app_status_context,
            _app_validate_tree,
            _domain_models,
            _infra_contracts,
            _presentation_cli_text,
            _presentation_json_state,
        ) = _runtime_modules()
        from spec_dock_runtime.cli import bootstrap as cli_bootstrap

        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_application_mutate_deps = cli_bootstrap.application_mutate_deps
        try:
            runtime_app._find_specdock_dir = lambda: Path("/repo/spec-dock")

            def _fake_mutate_deps(req, ports):
                del req, ports
                return app_contracts.MutateDepsResult(
                    action="add",
                    from_id="iss-local-00001",
                    to_id="iss-local-00002",
                    result="unchanged",
                    warnings=[],
                )

            cli_bootstrap.application_mutate_deps = _fake_mutate_deps

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = runtime_app.main(["deps", "add", "--from", "iss-local-00001", "--to", "iss-local-00002"])

            assert exit_code == 0
            assert stderr.getvalue().strip() == ""
            assert (
                stdout.getvalue().strip()
                == "spec-dock: ok (deps add) from=iss-local-00001 to=iss-local-00002 result=unchanged"
            )
        finally:
            runtime_app._find_specdock_dir = original_find_specdock_dir
            cli_bootstrap.application_mutate_deps = original_application_mutate_deps

    def test_legacy_deps_remove_path_delegates_and_exit_code_zero(self) -> None:
        (
            runtime_app,
            _app_check_deps,
            app_contracts,
            _app_ports,
            _app_status_context,
            _app_validate_tree,
            _domain_models,
            _infra_contracts,
            _presentation_cli_text,
            _presentation_json_state,
        ) = _runtime_modules()
        from spec_dock_runtime.cli import bootstrap as cli_bootstrap

        calls: dict[str, object] = {}
        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_application_mutate_deps = cli_bootstrap.application_mutate_deps
        try:
            runtime_app._find_specdock_dir = lambda: Path("/repo/spec-dock")

            def _fake_mutate_deps(req, ports):
                calls["req"] = req
                calls["ports"] = ports
                return app_contracts.MutateDepsResult(
                    action="remove",
                    from_id="iss-local-00001",
                    to_id="iss-local-00002",
                    result="updated",
                    warnings=[],
                )

            cli_bootstrap.application_mutate_deps = _fake_mutate_deps

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = runtime_app.main(["deps", "remove", "--from", "iss-local-00001", "--to", "iss-local-00002"])

            assert exit_code == 0
            assert stderr.getvalue().strip() == ""
            assert (
                stdout.getvalue().strip()
                == "spec-dock: ok (deps remove) from=iss-local-00001 to=iss-local-00002 result=updated"
            )
            req = calls["req"]
            assert req.action == "remove"
            assert req.from_id == "iss-local-00001"
            assert req.to_id == "iss-local-00002"
        finally:
            runtime_app._find_specdock_dir = original_find_specdock_dir
            cli_bootstrap.application_mutate_deps = original_application_mutate_deps

    def test_legacy_deps_add_path_renders_typed_error_contract(self) -> None:
        (
            runtime_app,
            _app_check_deps,
            app_contracts,
            _app_ports,
            _app_status_context,
            _app_validate_tree,
            _domain_models,
            _infra_contracts,
            _presentation_cli_text,
            _presentation_json_state,
        ) = _runtime_modules()
        from spec_dock_runtime.cli import bootstrap as cli_bootstrap

        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_application_mutate_deps = cli_bootstrap.application_mutate_deps
        try:
            runtime_app._find_specdock_dir = lambda: Path("/repo/spec-dock")

            def _fake_mutate_deps(req, ports):
                del req, ports
                raise app_contracts.MutateDepsError(
                    action="add",
                    from_id="iss-local-00001",
                    to_id="iss-local-00002",
                    code="write_failed",
                    detail="write_failed[replace]: simulated replace failure",
                )

            cli_bootstrap.application_mutate_deps = _fake_mutate_deps

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = runtime_app.main(["deps", "add", "--from", "iss-local-00001", "--to", "iss-local-00002"])

            assert exit_code == 1
            assert stdout.getvalue().strip() == ""
            assert (
                "spec-dock: error (deps add) from=iss-local-00001 to=iss-local-00002 code=write_failed"
                in stderr.getvalue()
            )
            assert "- write_failed[replace]: simulated replace failure" in stderr.getvalue()
        finally:
            runtime_app._find_specdock_dir = original_find_specdock_dir
            cli_bootstrap.application_mutate_deps = original_application_mutate_deps

    def test_fs_repo_atomic_replace_failure_preserves_original_meta_json(self) -> None:
        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime.infra import fs_repo
        finally:
            sys.path.pop(0)

        with tempfile.TemporaryDirectory() as tmp:
            node_dir = (
                Path(tmp)
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth"
                / "epics"
                / "epic-local-00001-main"
                / "issues"
                / "iss-local-00001-target"
            )
            node_dir.mkdir(parents=True, exist_ok=True)
            meta_path = node_dir / ".meta.json"
            meta_path.write_text(
                json.dumps({"id": "iss-local-00001", "type": "issue", "depends_on": []}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            original = meta_path.read_text(encoding="utf-8")

            original_replace = fs_repo.os.replace
            try:

                def _failing_replace(src, dst):
                    del src, dst
                    raise OSError("simulated replace failure")

                fs_repo.os.replace = _failing_replace
                with pytest.raises(RuntimeError) as ctx:
                    fs_repo.add_issue_dependency(meta_path, "iss-local-00002")
            finally:
                fs_repo.os.replace = original_replace

            assert "write_failed" in str(ctx.value)
            assert meta_path.read_text(encoding="utf-8") == original
            tmp_files = [p for p in node_dir.iterdir() if ".meta.json.tmp-" in p.name]
            assert tmp_files == []

    def test_fs_repo_atomic_replace_failure_preserves_original_meta_json_on_remove(self) -> None:
        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime.infra import fs_repo
        finally:
            sys.path.pop(0)

        with tempfile.TemporaryDirectory() as tmp:
            node_dir = (
                Path(tmp)
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth"
                / "epics"
                / "epic-local-00001-main"
                / "issues"
                / "iss-local-00001-target"
            )
            node_dir.mkdir(parents=True, exist_ok=True)
            meta_path = node_dir / ".meta.json"
            meta_path.write_text(
                json.dumps(
                    {
                        "id": "iss-local-00001",
                        "type": "issue",
                        "depends_on": ["iss-local-00002"],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            original = meta_path.read_text(encoding="utf-8")

            original_replace = fs_repo.os.replace
            try:

                def _failing_replace(src, dst):
                    del src, dst
                    raise OSError("simulated replace failure")

                fs_repo.os.replace = _failing_replace
                with pytest.raises(RuntimeError) as ctx:
                    fs_repo.remove_issue_dependency(meta_path, "iss-local-00002")
            finally:
                fs_repo.os.replace = original_replace

            assert "write_failed" in str(ctx.value)
            assert meta_path.read_text(encoding="utf-8") == original
            tmp_files = [p for p in node_dir.iterdir() if ".meta.json.tmp-" in p.name]
            assert tmp_files == []

    def test_fs_repo_remove_issue_dependency_supports_shorthand_matching_refs(self) -> None:
        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime.infra import fs_repo
        finally:
            sys.path.pop(0)

        with tempfile.TemporaryDirectory() as tmp:
            node_dir = (
                Path(tmp)
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth"
                / "epics"
                / "epic-local-00001-main"
                / "issues"
                / "iss-local-00001-target"
            )
            node_dir.mkdir(parents=True, exist_ok=True)
            meta_path = node_dir / ".meta.json"
            meta_path.write_text(
                json.dumps(
                    {
                        "id": "iss-local-00001",
                        "type": "issue",
                        "depends_on": [
                            "iss-local-00002",
                            302,
                            "302",
                            "example/repo#302",
                            "https://github.com/example/repo/issues/302",
                            "iss-local-00003",
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            fs_repo.remove_issue_dependency(
                meta_path,
                "iss-local-00002",
                matching_refs=[
                    302,
                    "302",
                    "example/repo#302",
                    "https://github.com/example/repo/issues/302",
                ],
            )

            payload = json.loads(meta_path.read_text(encoding="utf-8"))
            assert payload.get("depends_on") == ["iss-local-00003"]

    def test_fs_repo_atomic_write_preserves_existing_read_bits(self) -> None:
        if os.name != "posix":
            pytest.skip("POSIX permission bits are required for this test")

        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime.infra import fs_repo
        finally:
            sys.path.pop(0)

        with tempfile.TemporaryDirectory() as tmp:
            node_dir = (
                Path(tmp)
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth"
                / "epics"
                / "epic-local-00001-main"
                / "issues"
                / "iss-local-00001-target"
            )
            node_dir.mkdir(parents=True, exist_ok=True)
            meta_path = node_dir / ".meta.json"
            meta_path.write_text(
                json.dumps({"id": "iss-local-00001", "type": "issue", "depends_on": []}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            meta_path.chmod(0o444)
            expected_mode = stat.S_IMODE(meta_path.stat().st_mode)

            fs_repo.add_issue_dependency(meta_path, "iss-local-00002")

            written = json.loads(meta_path.read_text(encoding="utf-8"))
            assert written.get("depends_on") == ["iss-local-00002"]
            assert stat.S_IMODE(meta_path.stat().st_mode) == expected_mode

    def test_fs_repo_atomic_unlock_failure_maps_to_write_failed(self) -> None:
        if os.name != "posix":
            pytest.skip("POSIX permission bits are required for this test")

        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime.infra import fs_repo
        finally:
            sys.path.pop(0)

        with tempfile.TemporaryDirectory() as tmp:
            node_dir = (
                Path(tmp)
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth"
                / "epics"
                / "epic-local-00001-main"
                / "issues"
                / "iss-local-00001-target"
            )
            node_dir.mkdir(parents=True, exist_ok=True)
            meta_path = node_dir / ".meta.json"
            meta_path.write_text(
                json.dumps({"id": "iss-local-00001", "type": "issue", "depends_on": []}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            meta_path.chmod(0o444)
            before = meta_path.read_text(encoding="utf-8")

            original_chmod = fs_repo.Path.chmod
            try:

                def _failing_chmod(self, mode, *args, **kwargs):
                    if self == meta_path and (mode & 0o200):
                        raise OSError("simulated unlock failure")
                    return original_chmod(self, mode, *args, **kwargs)

                fs_repo.Path.chmod = _failing_chmod
                with pytest.raises(RuntimeError) as ctx:
                    fs_repo.add_issue_dependency(meta_path, "iss-local-00002")
            finally:
                fs_repo.Path.chmod = original_chmod

            assert "write_failed[unlock]" in str(ctx.value)
            assert meta_path.read_text(encoding="utf-8") == before

    def test_fs_repo_atomic_non_oserror_write_failure_maps_to_write_failed_and_restores_readonly(self) -> None:
        if os.name != "posix":
            pytest.skip("POSIX permission bits are required for this test")

        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime.infra import fs_repo
        finally:
            sys.path.pop(0)

        with tempfile.TemporaryDirectory() as tmp:
            node_dir = (
                Path(tmp)
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth"
                / "epics"
                / "epic-local-00001-main"
                / "issues"
                / "iss-local-00001-target"
            )
            node_dir.mkdir(parents=True, exist_ok=True)
            meta_path = node_dir / ".meta.json"
            meta_path.write_text(
                json.dumps({"id": "iss-local-00001", "type": "issue", "depends_on": []}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            meta_path.chmod(0o444)
            expected_mode = stat.S_IMODE(meta_path.stat().st_mode)
            before = meta_path.read_text(encoding="utf-8")

            original_write_json = fs_repo.write_json
            try:

                def _failing_write_json(path, payload):
                    if path != meta_path and path.parent == meta_path.parent and ".meta.json.tmp-" in path.name:
                        raise TypeError("simulated non-oserror write failure")
                    return original_write_json(path, payload)

                fs_repo.write_json = _failing_write_json
                with pytest.raises(RuntimeError) as ctx:
                    fs_repo.add_issue_dependency(meta_path, "iss-local-00002")
            finally:
                fs_repo.write_json = original_write_json

            assert "write_failed[write_temp]" in str(ctx.value)
            assert "simulated non-oserror write failure" in str(ctx.value)
            assert meta_path.read_text(encoding="utf-8") == before
            assert stat.S_IMODE(meta_path.stat().st_mode) == expected_mode
            tmp_files = [p for p in node_dir.iterdir() if ".meta.json.tmp-" in p.name]
            assert tmp_files == []

    def test_fs_repo_atomic_lock_failure_maps_to_write_failed_lock_and_preserves_original(self) -> None:
        if os.name != "posix":
            pytest.skip("POSIX permission bits are required for this test")

        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime.infra import fs_repo
        finally:
            sys.path.pop(0)

        with tempfile.TemporaryDirectory() as tmp:
            node_dir = (
                Path(tmp)
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth"
                / "epics"
                / "epic-local-00001-main"
                / "issues"
                / "iss-local-00001-target"
            )
            node_dir.mkdir(parents=True, exist_ok=True)
            meta_path = node_dir / ".meta.json"
            meta_path.write_text(
                json.dumps({"id": "iss-local-00001", "type": "issue", "depends_on": []}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            before = meta_path.read_text(encoding="utf-8")

            original_chmod = fs_repo.Path.chmod
            try:

                def _failing_chmod(self, mode, *args, **kwargs):
                    if (
                        self != meta_path
                        and self.parent == meta_path.parent
                        and ".meta.json.tmp-" in self.name
                        and (mode & 0o222) == 0
                    ):
                        raise OSError("simulated lock failure")
                    return original_chmod(self, mode, *args, **kwargs)

                fs_repo.Path.chmod = _failing_chmod
                with pytest.raises(RuntimeError) as ctx:
                    fs_repo.add_issue_dependency(meta_path, "iss-local-00002")
            finally:
                fs_repo.Path.chmod = original_chmod

            assert "write_failed[lock]" in str(ctx.value)
            assert meta_path.read_text(encoding="utf-8") == before
            tmp_files = [p for p in node_dir.iterdir() if ".meta.json.tmp-" in p.name]
            assert tmp_files == []

    def test_fs_repo_atomic_mkstemp_failure_maps_to_write_failed_write_temp(self) -> None:
        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime.infra import fs_repo
        finally:
            sys.path.pop(0)

        with tempfile.TemporaryDirectory() as tmp:
            node_dir = (
                Path(tmp)
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth"
                / "epics"
                / "epic-local-00001-main"
                / "issues"
                / "iss-local-00001-target"
            )
            node_dir.mkdir(parents=True, exist_ok=True)
            meta_path = node_dir / ".meta.json"
            meta_path.write_text(
                json.dumps({"id": "iss-local-00001", "type": "issue", "depends_on": []}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            before = meta_path.read_text(encoding="utf-8")

            original_mkstemp = fs_repo.tempfile.mkstemp
            try:

                def _failing_mkstemp(*args, **kwargs):
                    del args, kwargs
                    raise OSError("simulated mkstemp failure")

                fs_repo.tempfile.mkstemp = _failing_mkstemp
                with pytest.raises(RuntimeError) as ctx:
                    fs_repo.add_issue_dependency(meta_path, "iss-local-00002")
            finally:
                fs_repo.tempfile.mkstemp = original_mkstemp

            assert "write_failed[write_temp]" in str(ctx.value)
            assert meta_path.read_text(encoding="utf-8") == before
            tmp_files = [p for p in node_dir.iterdir() if ".meta.json.tmp-" in p.name]
            assert tmp_files == []

    def test_fs_repo_atomic_stat_failure_maps_to_write_failed(self) -> None:
        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime.infra import fs_repo
        finally:
            sys.path.pop(0)

        with tempfile.TemporaryDirectory() as tmp:
            node_dir = (
                Path(tmp)
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth"
                / "epics"
                / "epic-local-00001-main"
                / "issues"
                / "iss-local-00001-target"
            )
            node_dir.mkdir(parents=True, exist_ok=True)
            meta_path = node_dir / ".meta.json"
            meta_path.write_text(
                json.dumps({"id": "iss-local-00001", "type": "issue", "depends_on": []}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            before = meta_path.read_text(encoding="utf-8")

            original_exists = fs_repo.Path.exists
            original_stat = fs_repo.Path.stat
            try:

                def _forced_exists(self):
                    if self == meta_path:
                        return True
                    return original_exists(self)

                def _failing_stat(self, *args, **kwargs):
                    if self == meta_path:
                        raise OSError("simulated stat failure")
                    return original_stat(self, *args, **kwargs)

                fs_repo.Path.exists = _forced_exists
                fs_repo.Path.stat = _failing_stat
                with pytest.raises(RuntimeError) as ctx:
                    fs_repo.add_issue_dependency(meta_path, "iss-local-00002")
            finally:
                fs_repo.Path.exists = original_exists
                fs_repo.Path.stat = original_stat

            assert "write_failed[stat]" in str(ctx.value)
            assert meta_path.read_text(encoding="utf-8") == before
