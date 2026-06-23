import sys
from pathlib import Path
from types import SimpleNamespace


import pytest


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
    github_repo_owner: str | None = None,
    github_repo_name: str | None = None,
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
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
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
        self.calls = 0

    def load_issue_depends_on_map(self, specdock_dir, graph):
        del specdock_dir, graph
        self.calls += 1
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
    def __init__(self, *, fail: bool = False, snapshots=None, foreign_snapshots=None):
        self.fail = fail
        self.snapshots = list(snapshots or [])
        self.foreign_snapshots = dict(foreign_snapshots or {})
        self.calls = []
        self.view_calls = []

    def issue_index(self, repo_root, *, limit):
        self.calls.append((str(repo_root), int(limit)))
        if self.fail:
            raise RuntimeError("gh issue list failed")
        return list(self.snapshots)

    def issue_view_snapshot(self, repo_root, issue_number, *, repo_slug=None):
        self.view_calls.append((str(repo_root), int(issue_number), repo_slug))
        if self.fail:
            raise RuntimeError("gh issue view failed")
        key = (str(repo_slug or ""), int(issue_number))
        snapshot = self.foreign_snapshots.get(key)
        if snapshot is None:
            raise RuntimeError(f"gh issue view failed: {repo_slug}#{issue_number}")
        return snapshot


class _StubGitGateway:
    def __init__(self, *, origin_repo_slug: str | None = None):
        self.calls = []
        self.raise_on_require_clean = None
        self.current_branch = "main"
        self.existing = set()
        self.invalid_refs = set()
        self.origin_repo_slug = origin_repo_slug

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

    def origin_github_repo_slug(self, repo_root):
        self.calls.append(("origin_github_repo_slug", str(repo_root)))
        return self.origin_repo_slug


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


class TestRuntimeActiveS06:
    def _ports(
        self,
        *,
        issue_depends_on_map,
        statuses,
        git_gateway=None,
        active_state_store=None,
        issue_gateway=None,
        records=None,
    ):
        app_contracts, app_ports, _app_set_active, infra_contracts = _runtime_modules()
        del app_contracts
        if records is None:
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
            issue_gateway=issue_gateway or _StubIssueGateway(),
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
        with pytest.raises(RuntimeError, match="active set blocked"):
            app_set_active.set_active(req, ports)
        assert ports.deps_topology_reader.calls == 1
        calls = [name for name, *_rest in ports.active_state_store.calls]
        assert "snapshot_current_state" not in calls
        assert "write_active_manifest" not in calls

    def test_set_active_non_issue_local_only_without_blockers_is_ready(self) -> None:
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
        result = app_set_active.set_active(req, ports)
        assert result.manifest_written
        assert result.selection.initiative_id == "init-local-00001"
        assert result.selection.epic_id is None
        assert result.selection.issue_id is None

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
        assert result.manifest_written
        assert result.pointer_updated
        assert "deps_blocked" in result.warnings[0]
        calls = [name for name, *_rest in ports.active_state_store.calls]
        assert calls[-4:] == [
                "snapshot_current_state",
                "write_active_manifest",
                "apply_active_pointers",
                "patch_agent_state_active_fields",
            ]
        write_calls = [call for call in ports.active_state_store.calls if call[0] == "write_active_manifest"]
        assert len(write_calls) == 1
        written_manifest = write_calls[0][2]
        for entry in (written_manifest.initiative, written_manifest.epic, written_manifest.issue):
            assert entry is not None
            assert entry is not None
            assert entry.path is not None
            assert entry.path is not None
            assert entry.path.startswith("spec-dock/"), entry.path
            assert not Path(entry.path).is_absolute(), entry.path

    def test_set_active_absorbs_github_issue_index_failure_as_warning(self) -> None:
        app_contracts, _app_ports, app_set_active, _infra_contracts = _runtime_modules()
        issue_gateway = _StubIssueGateway(fail=True)
        ports = self._ports(
            issue_depends_on_map={"iss-local-00001": [], "iss-local-00002": []},
            statuses={},
            issue_gateway=issue_gateway,
        )
        req = app_contracts.SetActiveRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
            force=True,
            checkout=False,
            use_github=True,
            issue_limit=10000,
        )
        result = app_set_active.set_active(req, ports)
        assert result.manifest_written
        assert result.selection.issue_id == "iss-local-00001"
        assert "gh_fetch_failed" in result.warnings
        assert not any(w.startswith("deps_blocked:") for w in result.warnings)
        assert issue_gateway.calls == [("/repo", 10000)]

    def test_set_active_github_resolves_current_unscoped_issue_with_current_repo_slug(self) -> None:
        app_contracts, _app_ports, app_set_active, infra_contracts = _runtime_modules()
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
                github_issue_number=123,
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
            _record(
                infra_contracts,
                kind="issue",
                node_id="iss-local-00003",
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=123,
                github_repo_owner="other",
                github_repo_name="repo",
            ),
        ]
        issue_gateway = _StubIssueGateway(
            snapshots=[
                SimpleNamespace(
                    issue_number=123,
                    state="OPEN",
                    title="current #123",
                    labels=[],
                    updated_at="2026-03-19T00:00:00Z",
                    url="https://github.com/current/repo/issues/123",
                    repo_owner="current",
                    repo_name="repo",
                )
            ],
            foreign_snapshots={
                ("other/repo", 123): SimpleNamespace(
                    issue_number=123,
                    state="CLOSED",
                    title="foreign #123",
                    labels=[],
                    updated_at="2026-03-19T00:00:01Z",
                    url="https://github.com/other/repo/issues/123",
                    repo_owner="other",
                    repo_name="repo",
                )
            },
        )
        ports = self._ports(
            issue_depends_on_map={
                "iss-local-00001": [],
                "iss-local-00002": ["iss-local-00001"],
                "iss-local-00003": [],
            },
            statuses={},
            issue_gateway=issue_gateway,
            git_gateway=_StubGitGateway(origin_repo_slug="current/repo"),
            records=records,
        )
        req = app_contracts.SetActiveRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00002", github_issue_number=None),
            force=False,
            checkout=False,
            use_github=True,
            issue_limit=10000,
        )
        with pytest.raises(RuntimeError) as cm:
            app_set_active.set_active(req, ports)
        message = str(cm.value)
        assert "guard_reason=blocked" in message
        assert "guard_reason=unknown" not in message
        assert issue_gateway.calls == [("/repo", 10000)]
        assert issue_gateway.view_calls == [("/repo", 123, "other/repo")]

    def test_set_active_skips_same_repo_repo_scoped_view_fetch_when_index_contains_key(self) -> None:
        app_contracts, _app_ports, app_set_active, infra_contracts = _runtime_modules()
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
                github_issue_number=123,
                github_repo_owner="current",
                github_repo_name="repo",
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
        issue_gateway = _StubIssueGateway(
            snapshots=[
                SimpleNamespace(
                    issue_number=123,
                    state="OPEN",
                    title="current #123",
                    labels=[],
                    updated_at="2026-03-19T00:00:00Z",
                    url="https://github.com/current/repo/issues/123",
                    repo_owner="current",
                    repo_name="repo",
                )
            ],
            foreign_snapshots={},
        )
        ports = self._ports(
            issue_depends_on_map={"iss-local-00001": [], "iss-local-00002": []},
            statuses={},
            issue_gateway=issue_gateway,
            git_gateway=_StubGitGateway(origin_repo_slug="current/repo"),
            records=records,
        )
        req = app_contracts.SetActiveRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
            force=False,
            checkout=False,
            use_github=True,
            issue_limit=10000,
        )
        result = app_set_active.set_active(req, ports)
        assert result.manifest_written
        assert result.selection.issue_id == "iss-local-00001"
        assert issue_gateway.calls == [("/repo", 10000)]
        assert issue_gateway.view_calls == []
        assert "gh_fetch_failed" not in result.warnings

    def test_set_active_falls_back_to_same_repo_repo_scoped_view_when_index_missing_key(self) -> None:
        app_contracts, _app_ports, app_set_active, infra_contracts = _runtime_modules()
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
                github_issue_number=123,
                github_repo_owner="current",
                github_repo_name="repo",
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
        issue_gateway = _StubIssueGateway(
            snapshots=[],
            foreign_snapshots={
                ("current/repo", 123): SimpleNamespace(
                    issue_number=123,
                    state="OPEN",
                    title="current #123",
                    labels=[],
                    updated_at="2026-03-19T00:00:01Z",
                    url="https://github.com/current/repo/issues/123",
                    repo_owner="current",
                    repo_name="repo",
                )
            },
        )
        ports = self._ports(
            issue_depends_on_map={"iss-local-00001": [], "iss-local-00002": []},
            statuses={},
            issue_gateway=issue_gateway,
            git_gateway=_StubGitGateway(origin_repo_slug="current/repo"),
            records=records,
        )
        req = app_contracts.SetActiveRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
            force=False,
            checkout=False,
            use_github=True,
            issue_limit=10000,
        )
        result = app_set_active.set_active(req, ports)
        assert result.manifest_written
        assert result.selection.issue_id == "iss-local-00001"
        assert issue_gateway.calls == [("/repo", 10000)]
        assert issue_gateway.view_calls == [("/repo", 123, "current/repo")]
        assert "gh_fetch_failed" not in result.warnings

    def test_set_active_falls_back_to_current_repo_view_for_unscoped_linked_initiative_when_index_missing_key(self) -> None:
        app_contracts, _app_ports, app_set_active, infra_contracts = _runtime_modules()
        records = [
            _record(
                infra_contracts,
                kind="initiative",
                node_id="init-local-00001",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=101,
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
        ]
        issue_gateway = _StubIssueGateway(
            snapshots=[],
            foreign_snapshots={
                ("current/repo", 101): SimpleNamespace(
                    issue_number=101,
                    state="OPEN",
                    title="current #101",
                    labels=[],
                    updated_at="2026-03-23T00:00:00Z",
                    url="https://github.com/current/repo/issues/101",
                    repo_owner="current",
                    repo_name="repo",
                )
            },
        )
        ports = self._ports(
            issue_depends_on_map={"iss-local-00001": []},
            statuses={},
            issue_gateway=issue_gateway,
            git_gateway=_StubGitGateway(origin_repo_slug="current/repo"),
            records=records,
        )
        req = app_contracts.SetActiveRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="init-local-00001", github_issue_number=None),
            force=False,
            checkout=False,
            use_github=True,
            issue_limit=10000,
        )
        result = app_set_active.set_active(req, ports)
        assert result.manifest_written
        assert result.selection.initiative_id == "init-local-00001"
        assert issue_gateway.calls == [("/repo", 10000)]
        assert issue_gateway.view_calls == [("/repo", 101, "current/repo")]
        assert "gh_fetch_failed" not in result.warnings

    def test_set_active_github_prefers_foreign_snapshot_under_same_number_collision(self) -> None:
        app_contracts, _app_ports, app_set_active, infra_contracts = _runtime_modules()
        records = [
            _record(
                infra_contracts,
                kind="initiative",
                node_id="init-local-00001",
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=101,
                github_repo_owner="upstream",
                github_repo_name="product",
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
                github_issue_number=123,
                github_repo_owner="other",
                github_repo_name="repo",
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
        issue_gateway = _StubIssueGateway(
            snapshots=[
                SimpleNamespace(
                    issue_number=101,
                    state="OPEN",
                    title="current repo #101",
                    labels=[],
                    updated_at="2026-03-18T00:00:00Z",
                    url="https://github.com/current/repo/issues/101",
                    repo_owner="current",
                    repo_name="repo",
                ),
                SimpleNamespace(
                    issue_number=123,
                    state="OPEN",
                    title="current repo #123",
                    labels=[],
                    updated_at="2026-03-18T00:00:00Z",
                    url="https://github.com/current/repo/issues/123",
                    repo_owner="current",
                    repo_name="repo",
                )
            ],
            foreign_snapshots={
                ("upstream/product", 101): SimpleNamespace(
                    issue_number=101,
                    state="OPEN",
                    title="foreign init #101",
                    labels=[],
                    updated_at="2026-03-18T00:10:00Z",
                    url="https://github.com/upstream/product/issues/101",
                    repo_owner="upstream",
                    repo_name="product",
                ),
                ("other/repo", 123): SimpleNamespace(
                    issue_number=123,
                    state="CLOSED",
                    title="foreign #123",
                    labels=[],
                    updated_at="2026-03-18T01:00:00Z",
                    url="https://github.com/other/repo/issues/123",
                    repo_owner="other",
                    repo_name="repo",
                )
            },
        )
        ports = self._ports(
            issue_depends_on_map={"iss-local-00001": [], "iss-local-00002": ["iss-local-00001"]},
            statuses={},
            issue_gateway=issue_gateway,
            records=records,
        )
        req = app_contracts.SetActiveRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00002", github_issue_number=None),
            force=False,
            checkout=False,
            use_github=True,
            issue_limit=10000,
        )
        result = app_set_active.set_active(req, ports)

        assert result.manifest_written
        assert result.selection.issue_id == "iss-local-00002"
        assert issue_gateway.calls == [("/repo", 10000)]
        assert issue_gateway.view_calls == [
                ("/repo", 123, "other/repo"),
                ("/repo", 101, "upstream/product"),
            ]
        assert not any(w.startswith("deps_blocked:") for w in result.warnings)
        assert "gh_fetch_failed" not in result.warnings

    def test_sync_branch_inference_propagates_current_repo_slug(self) -> None:
        app_contracts, _app_ports, _app_set_active, infra_contracts = _runtime_modules()
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
            from spec_dock_runtime.application import sync_state as app_sync_state
            from spec_dock_runtime.domain import models as domain_models
        finally:
            sys.path.pop(0)

        git_gateway = _StubGitGateway(origin_repo_slug="current/repo")
        git_gateway.current_branch = "123-fix-login"
        ports = self._ports(
            issue_depends_on_map={"iss-local-00001": [], "iss-local-00002": []},
            statuses={},
            git_gateway=git_gateway,
            active_state_store=_StubActiveStateStore(infra_contracts),
        )
        state = app_contracts.SyncStateResult(
            graph=domain_models.SpecGraph(nodes_by_id={}),
            active=None,
            issue_statuses={},
            progress=domain_models.ProgressMap(
                by_node_id={},
                counts={"total": 0, "done": 0, "open": 0, "unknown": 0},
            ),
            deps_state=domain_models.DepsState(nodes=[], warnings=[]),
            deps_eval_by_id={},
            generated_at="2026-03-23T00:00:00+00:00",
            warnings=[],
            deps_preflight_error=None,
            repo_root=Path("/repo"),
        )

        observed: dict[str, str | None] = {}
        original_infer = app_sync_state.infer_active_node_from_branch

        def _fake_infer(graph, *, branch, current_repo_slug=None):
            del graph
            observed["branch"] = branch
            observed["current_repo_slug"] = current_repo_slug
            return (None, "no branch match")

        app_sync_state.infer_active_node_from_branch = _fake_infer
        try:
            next_state, outcome = app_sync_state.maybe_auto_update_from_branch(state, ports)
        finally:
            app_sync_state.infer_active_node_from_branch = original_infer

        assert next_state is state
        assert outcome is not None
        assert outcome is not None
        assert not outcome.applied
        assert outcome.reason == "no branch match"
        assert observed == {"branch": "123-fix-login", "current_repo_slug": "current/repo"}

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
        with pytest.raises(RuntimeError, match="Working tree is not clean"):
            app_set_active.set_active(req, ports)
        calls = [name for name, *_rest in ports.active_state_store.calls]
        assert "snapshot_current_state" not in calls
        assert "restore_previous_state" not in calls

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
        with pytest.raises(RuntimeError, match="patch failed"):
            app_set_active.set_active(req, ports)
        calls = [name for name, *_rest in active_store.calls]
        assert "restore_previous_state" in calls

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
        assert result.cleared
        assert result.previous.issue_id == "iss-local-00001"
        assert active_store.last_patch_manifest is None
