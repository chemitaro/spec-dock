from dataclasses import fields, replace
from pathlib import Path
import sys

import pytest


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application import (
            contracts as app_contracts,
            ports as app_ports,
            set_active as app_set_active,
        )
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.infra import contracts as infra_contracts
    finally:
        sys.path.pop(0)
    return app_contracts, app_ports, app_set_active, domain_models, infra_contracts


def _snapshot_paths(paths):
    out = {}
    for path in paths:
        if path.is_symlink():
            out[path] = ("symlink", path.readlink().as_posix())
        elif path.is_file():
            out[path] = ("file", path.read_bytes())
        elif path.is_dir():
            out[path] = ("directory", None)
        else:
            out[path] = ("missing", None)
    return out


class _StubNodeReader:
    def __init__(self, records):
        self.records = list(records)

    def load_node_records(self):
        return list(self.records)


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


class _FailFastPort:
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        self.calls.append(name)
        raise AssertionError(f"selection-only active set must not call {name}")


class _PhaseFailingActiveStateStore:
    def __init__(self, active_store, fail_phase):
        self.active_store = active_store
        self.fail_phase = fail_phase

    def load_active_manifest(self, specdock_dir):
        return self.active_store.load_active_manifest(specdock_dir)

    def snapshot_current_state(self, specdock_dir):
        return self.active_store.snapshot_current_state(specdock_dir)

    def write_active_manifest(self, specdock_dir, manifest):
        written = self.active_store.write_active_manifest(specdock_dir, manifest)
        if self.fail_phase == "manifest":
            raise RuntimeError("injected manifest failure")
        return written

    def apply_active_pointers(self, specdock_dir, manifest, rendered_context_pack):
        self.active_store.apply_active_pointers(specdock_dir, manifest, rendered_context_pack)
        if self.fail_phase == "pointers":
            raise RuntimeError("injected pointer failure")

    def patch_agent_state_active_fields(self, specdock_dir, manifest):
        self.active_store.patch_agent_state_active_fields(specdock_dir, manifest)
        if self.fail_phase == "managed":
            raise RuntimeError("injected managed state failure")

    def restore_previous_state(self, specdock_dir, snapshot):
        self.active_store.restore_previous_state(specdock_dir, snapshot)


class _DirectoryPhaseFailingActiveStateStore:
    def __init__(self, active_store, fail_phase, directory_paths):
        self.active_store = active_store
        self.fail_phase = fail_phase
        self.directory_paths = list(directory_paths)

    def snapshot_current_state(self, specdock_dir):
        return self.active_store.snapshot_current_state(specdock_dir)

    def write_active_manifest(self, specdock_dir, manifest):
        for path in self.directory_paths:
            self.active_store._unlink_any(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"corrupted")
        if self.fail_phase == "manifest":
            raise RuntimeError("injected manifest failure")
        return manifest

    def apply_active_pointers(self, specdock_dir, manifest, rendered_context_pack):
        if self.fail_phase == "pointers":
            raise RuntimeError("injected pointer failure")

    def patch_agent_state_active_fields(self, specdock_dir, manifest):
        if self.fail_phase == "managed":
            raise RuntimeError("injected managed state failure")

    def restore_previous_state(self, specdock_dir, snapshot):
        self.active_store.restore_previous_state(specdock_dir, snapshot)


class TestSetActiveApplication:
    def _records(self, infra_contracts):
        root = Path("/repo/spec-dock/initiatives/init-00101-auth-platform")
        epic = root / "epics" / "epic-00201-jwt-auth"
        empty_a = root / "epics" / "epic-00202-empty-a"
        empty_b = root / "epics" / "epic-00203-empty-b"
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
                kind="epic",
                id="epic-00202",
                title="Empty A",
                slug="empty-a",
                path=empty_a.as_posix(),
                parent_id="init-00101",
                initiative_id="init-00101",
                epic_id=None,
                github_issue_number=202,
                meta_path=(empty_a / ".meta.json").as_posix(),
                github_repo_owner="example",
                github_repo_name="repo",
            ),
            infra_contracts.StoredMetaRecord(
                kind="epic",
                id="epic-00203",
                title="Empty B",
                slug="empty-b",
                path=empty_b.as_posix(),
                parent_id="init-00101",
                initiative_id="init-00101",
                epic_id=None,
                github_issue_number=203,
                meta_path=(empty_b / ".meta.json").as_posix(),
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
        issue_gateway=None,
        git_gateway=None,
        specdock_dir=Path("/repo/spec-dock"),
    ):
        return app_ports.Ports(
            node_reader=_StubNodeReader(self._records(infra_contracts)),
            repo_root=Path("/repo"),
            specdock_dir=specdock_dir,
            active_state_store=active_store or _StubActiveStateStore(),
            issue_gateway=issue_gateway,
            git_gateway=git_gateway,
        )

    def _request(self, app_contracts, *, target):
        return app_contracts.SetActiveRequest(target=target)

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
        ports = self._ports(
            app_ports,
            infra_contracts,
            active_store=active_store,
        )

        by_id = app_set_active.set_active(
            self._request(app_contracts, target=self._node_id_target(app_contracts, "iss-302")),
            ports,
        )
        assert by_id.selection.issue_id == "iss-00302"
        assert active_store.written[-1].issue.id == "iss-00302"
        assert (
            active_store.written[-1].issue.path
            == "spec-dock/initiatives/init-00101-auth-platform/epics/epic-00201-jwt-auth/issues/iss-00302-target-issue"
        )

        by_github = app_set_active.set_active(
            self._request(
                app_contracts,
                target=self._github_target(app_contracts, 301, owner="example", repo="repo"),
            ),
            ports,
        )
        assert by_github.selection.issue_id == "iss-00301"

    @pytest.mark.parametrize("selector", ["node_id", "github_issue", "repo_github_issue"])
    def test_set_active_all_selectors_avoid_readiness_github_and_git_ports(self, selector) -> None:
        app_contracts, app_ports, app_set_active, _domain_models, infra_contracts = _runtime_modules()
        active_store = _StubActiveStateStore()
        deps_spy = _FailFastPort()
        derived_spy = _FailFastPort()
        issue_spy = _FailFastPort()
        git_spy = _FailFastPort()
        ports = self._ports(
            app_ports,
            infra_contracts,
            active_store=active_store,
            issue_gateway=issue_spy,
            git_gateway=git_spy,
        )
        object.__setattr__(ports, "deps_topology_reader", deps_spy)
        object.__setattr__(ports, "derived_state_reader", derived_spy)

        target = {
            "node_id": self._node_id_target(app_contracts, "iss-00302"),
            "github_issue": self._github_target(app_contracts, 302),
            "repo_github_issue": self._github_target(app_contracts, 302, owner="example", repo="repo"),
        }[selector]
        result = app_set_active.set_active(
            self._request(
                app_contracts,
                target=target,
            ),
            ports,
        )

        assert result.selection.issue_id == "iss-00302"
        assert result.branch is None
        assert result.warnings == []
        assert active_store.written[-1].issue.id == "iss-00302"
        assert deps_spy.calls == []
        assert derived_spy.calls == []
        assert issue_spy.calls == []
        assert git_spy.calls == []

    def test_repo_scoped_github_target_infers_single_unscoped_legacy_node_without_git(self) -> None:
        app_contracts, app_ports, app_set_active, _domain_models, infra_contracts = _runtime_modules()
        records = [
            replace(record, github_repo_owner=None, github_repo_name=None) if record.id == "iss-00302" else record
            for record in self._records(infra_contracts)
        ]
        active_store = _StubActiveStateStore()
        git_spy = _FailFastPort()
        ports = app_ports.Ports(
            node_reader=_StubNodeReader(records),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
            active_state_store=active_store,
            git_gateway=git_spy,
        )

        result = app_set_active.set_active(
            self._request(
                app_contracts,
                target=self._github_target(app_contracts, 302, owner="example", repo="repo"),
            ),
            ports,
        )

        assert result.selection.issue_id == "iss-00302"
        assert git_spy.calls == []

    @pytest.mark.parametrize("match_count", [0, 2])
    def test_repo_scoped_github_target_reports_not_found_or_ambiguous_without_writing(self, match_count) -> None:
        app_contracts, app_ports, app_set_active, _domain_models, infra_contracts = _runtime_modules()
        records = self._records(infra_contracts)
        issue_records = [record for record in records if record.kind == "issue"]
        if match_count == 2:
            replacements = {
                record.id: replace(
                    record,
                    github_issue_number=999,
                    github_repo_owner=None,
                    github_repo_name=None,
                )
                for record in issue_records
            }
            records = [replacements.get(record.id, record) for record in records]
        active_store = _StubActiveStateStore()
        git_spy = _FailFastPort()
        ports = app_ports.Ports(
            node_reader=_StubNodeReader(records),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
            active_state_store=active_store,
            git_gateway=git_spy,
        )

        expected = "No node found" if match_count == 0 else "Ambiguous"
        with pytest.raises(RuntimeError, match=expected):
            app_set_active.set_active(
                self._request(
                    app_contracts,
                    target=self._github_target(app_contracts, 999, owner="example", repo="repo"),
                ),
                ports,
            )

        assert active_store.written == []
        assert git_spy.calls == []

    def test_active_manifest_and_context_pack_are_structural_only(self) -> None:
        app_contracts, app_ports, app_set_active, _domain_models, infra_contracts = _runtime_modules()
        assert [field.name for field in fields(infra_contracts.ActiveManifestEntry)] == ["id", "path"]

        active_store = _StubActiveStateStore()
        ports = self._ports(app_ports, infra_contracts, active_store=active_store)
        app_set_active.set_active(
            self._request(app_contracts, target=self._node_id_target(app_contracts, "iss-00302")),
            ports,
        )

        assert active_store.applied[-1][1]

    @pytest.mark.parametrize("fail_phase", ["manifest", "pointers", "managed"])
    @pytest.mark.parametrize("projection_exists", [True, False])
    @pytest.mark.parametrize("legacy_kind", ["crlf_files", "symlinks"])
    def test_commit_active_state_rolls_back_every_write_phase_to_legacy_snapshot(
        self, tmp_path, fail_phase, projection_exists, legacy_kind
    ) -> None:
        app_contracts, app_ports, app_set_active, _domain_models, infra_contracts = _runtime_modules()
        del app_contracts
        from spec_dock_runtime.infra import active_store as infra_active_store

        repo_root = tmp_path
        specdock_dir = repo_root / "spec-dock"
        for layer in ("initiative", "epic", "issue"):
            (specdock_dir / "system" / "active-none" / layer).mkdir(parents=True)
        old_issue_dir = specdock_dir / "issues" / "iss-00001-old"
        old_issue_dir.mkdir(parents=True)
        legacy_dir = specdock_dir / ".work"
        legacy_dir.mkdir(parents=True)
        legacy_active = (
            b'{"schema_version":2,"initiative":null,"epic":null,'
            b'"issue":{"id":"iss-00001","path":"spec-dock/issues/iss-00001-old",'
            b'"authority":"approved","grants":["implementation_start"]}}\r\n'
        )
        legacy_current = b'{"issue":{"id":"iss-legacy-current"}}\r\n'
        legacy_sources = legacy_dir / "snapshots"
        if legacy_kind == "crlf_files":
            (legacy_dir / "active.json").write_bytes(legacy_active)
            (legacy_dir / "current.json").write_bytes(legacy_current)
        else:
            legacy_sources.mkdir()
            (legacy_sources / "active-source.json").write_bytes(legacy_active)
            (legacy_sources / "current-source.json").write_bytes(legacy_current)
            (legacy_dir / "active.json").symlink_to("snapshots/active-source.json")
            (legacy_dir / "current.json").symlink_to("snapshots/current-source.json")
        old_manifest = infra_active_store.load_active_manifest(specdock_dir).manifest
        if projection_exists:
            infra_active_store.apply_active_pointers(specdock_dir, old_manifest, "# old context\n")
        agent_dir = specdock_dir / ".agent"
        agent_dir.mkdir(parents=True, exist_ok=True)
        for name in ("index-all.json", "tree-all.json", "index.json", "tree.json"):
            (agent_dir / name).write_text('{"active":{"old":true}}\n', encoding="utf-8")

        watched = [
            legacy_dir / "active.json",
            legacy_dir / "current.json",
            legacy_sources / "active-source.json",
            legacy_sources / "current-source.json",
            agent_dir / "active.json",
            *(agent_dir / name for name in ("index-all.json", "tree-all.json", "index.json", "tree.json")),
            specdock_dir / "active",
            *(specdock_dir / "active" / name for name in ("initiative", "epic", "issue", "context-pack.md")),
        ]

        before = _snapshot_paths(watched)
        new_manifest = infra_contracts.ActiveManifest(
            initiative=None,
            epic=None,
            issue=infra_contracts.ActiveManifestEntry(id="iss-00002", path="spec-dock/issues/iss-00002-new"),
        )
        store = _PhaseFailingActiveStateStore(infra_active_store, fail_phase)
        ports = app_ports.Ports(
            node_reader=_StubNodeReader([]),
            repo_root=repo_root,
            specdock_dir=specdock_dir,
            active_state_store=store,
        )

        with pytest.raises(
            RuntimeError, match=f"injected {fail_phase[:-1] if fail_phase == 'pointers' else fail_phase}"
        ):
            app_set_active.commit_active_state(
                persisted_manifest=new_manifest,
                patch_manifest=new_manifest,
                ports=ports,
                context_pack_text="# new context\n",
            )

        assert _snapshot_paths(watched) == before

    @pytest.mark.parametrize("fail_phase", ["manifest", "pointers", "managed"])
    @pytest.mark.parametrize("agent_kind", ["crlf_file", "symlink"])
    def test_commit_active_state_rolls_back_agent_manifest_verbatim(self, tmp_path, fail_phase, agent_kind) -> None:
        _app_contracts, app_ports, app_set_active, _domain_models, infra_contracts = _runtime_modules()
        from spec_dock_runtime.infra import active_store as infra_active_store

        specdock_dir = tmp_path / "spec-dock"
        for layer in ("initiative", "epic", "issue"):
            (specdock_dir / "system" / "active-none" / layer).mkdir(parents=True)
        agent_dir = specdock_dir / ".agent"
        agent_dir.mkdir(parents=True)
        active_bytes = (
            b'{"schema_version":2,"initiative":null,"epic":null,'
            b'"issue":{"id":"iss-00001","path":"spec-dock/issues/iss-00001-old"}}\r\n'
        )
        active_source = agent_dir / "snapshots" / "active-source.json"
        active_path = agent_dir / "active.json"
        if agent_kind == "crlf_file":
            active_path.write_bytes(active_bytes)
        else:
            active_source.parent.mkdir()
            active_source.write_bytes(active_bytes)
            active_path.symlink_to("snapshots/active-source.json")
        old_manifest = infra_active_store.load_active_manifest(specdock_dir).manifest
        infra_active_store.apply_active_pointers(specdock_dir, old_manifest, "# old context\n")

        watched = [active_path, active_source]
        before = _snapshot_paths(watched)
        new_manifest = infra_contracts.ActiveManifest(
            initiative=None,
            epic=None,
            issue=infra_contracts.ActiveManifestEntry(id="iss-00002", path="spec-dock/issues/iss-00002-new"),
        )
        ports = app_ports.Ports(
            node_reader=_StubNodeReader([]),
            repo_root=tmp_path,
            specdock_dir=specdock_dir,
            active_state_store=_PhaseFailingActiveStateStore(infra_active_store, fail_phase),
        )

        with pytest.raises(
            RuntimeError, match=f"injected {fail_phase[:-1] if fail_phase == 'pointers' else fail_phase}"
        ):
            app_set_active.commit_active_state(
                persisted_manifest=new_manifest,
                patch_manifest=new_manifest,
                ports=ports,
                context_pack_text="# new context\n",
            )

        assert _snapshot_paths(watched) == before

    @pytest.mark.parametrize(
        ("managed_name", "via_symlink"),
        [
            ("active.json", False),
            ("index.json", False),
            ("tree.json", True),
        ],
    )
    def test_commit_active_state_rejects_hard_linked_managed_json_before_mutation(
        self, tmp_path, managed_name, via_symlink
    ) -> None:
        _app_contracts, app_ports, app_set_active, _domain_models, infra_contracts = _runtime_modules()
        from spec_dock_runtime.infra import active_store as infra_active_store

        specdock_dir = tmp_path / "spec-dock"
        for layer in ("initiative", "epic", "issue"):
            (specdock_dir / "system" / "active-none" / layer).mkdir(parents=True)
        agent_dir = specdock_dir / ".agent"
        agent_dir.mkdir(parents=True)
        active_bytes = b'{"schema_version":2,"initiative":null,"epic":null,"issue":null}\n'
        (agent_dir / "active.json").write_bytes(active_bytes)
        managed_bytes = b'{"active":null,"nodes":{"iss-00001":{"status":"done"}}}\n'
        for name in ("index-all.json", "tree-all.json", "index.json", "tree.json"):
            (agent_dir / name).write_bytes(managed_bytes)
        infra_active_store.apply_active_pointers(specdock_dir, None, "# old context\n")

        managed_path = agent_dir / managed_name
        external_dir = tmp_path / "outside"
        external_dir.mkdir()
        if via_symlink:
            target_path = external_dir / "managed-target.json"
            target_path.write_bytes(managed_path.read_bytes())
            managed_path.unlink()
            managed_path.symlink_to(target_path)
        else:
            target_path = managed_path
        external_alias = external_dir / "external-alias.json"
        external_alias.hardlink_to(target_path)

        watched = [
            agent_dir / "active.json",
            *(agent_dir / name for name in ("index-all.json", "tree-all.json", "index.json", "tree.json")),
            specdock_dir / "active",
            *(specdock_dir / "active" / name for name in ("initiative", "epic", "issue", "context-pack.md")),
            external_alias,
        ]
        before = _snapshot_paths(watched)
        alias_bytes = external_alias.read_bytes()
        new_manifest = infra_contracts.ActiveManifest(
            initiative=None,
            epic=None,
            issue=infra_contracts.ActiveManifestEntry(id="iss-00002", path="spec-dock/issues/iss-00002-new"),
        )
        ports = app_ports.Ports(
            node_reader=_StubNodeReader([]),
            repo_root=tmp_path,
            specdock_dir=specdock_dir,
            active_state_store=infra_active_store,
        )

        with pytest.raises(RuntimeError) as exc_info:
            app_set_active.commit_active_state(
                persisted_manifest=new_manifest,
                patch_manifest=new_manifest,
                ports=ports,
                context_pack_text="# new context\n",
            )

        diagnostic = str(exc_info.value)
        assert "multiple hard links" in diagnostic
        assert f".agent/{managed_name}" in diagnostic
        assert external_alias.as_posix() not in diagnostic
        assert external_dir.as_posix() not in diagnostic
        assert external_alias.read_bytes() == alias_bytes
        assert _snapshot_paths(watched) == before

    @pytest.mark.parametrize("managed_kind", ["single_link_file", "single_link_symlink"])
    def test_commit_active_state_accepts_single_link_managed_json(self, tmp_path, managed_kind) -> None:
        _app_contracts, app_ports, app_set_active, _domain_models, infra_contracts = _runtime_modules()
        from spec_dock_runtime.infra import active_store as infra_active_store

        specdock_dir = tmp_path / "spec-dock"
        for layer in ("initiative", "epic", "issue"):
            (specdock_dir / "system" / "active-none" / layer).mkdir(parents=True)
        agent_dir = specdock_dir / ".agent"
        agent_dir.mkdir(parents=True)
        active_path = agent_dir / "active.json"
        active_target = agent_dir / "active-target.json"
        active_bytes = b'{"schema_version":2,"initiative":null,"epic":null,"issue":null}\n'
        if managed_kind == "single_link_file":
            active_path.write_bytes(active_bytes)
        else:
            active_target.write_bytes(active_bytes)
            active_path.symlink_to(active_target.name)
        for name in ("index-all.json", "tree-all.json", "index.json", "tree.json"):
            (agent_dir / name).write_text('{"active":null}\n', encoding="utf-8")
        infra_active_store.apply_active_pointers(specdock_dir, None, "# old context\n")

        new_manifest = infra_contracts.ActiveManifest(
            initiative=None,
            epic=None,
            issue=infra_contracts.ActiveManifestEntry(id="iss-00002", path="spec-dock/issues/iss-00002-new"),
        )
        ports = app_ports.Ports(
            node_reader=_StubNodeReader([]),
            repo_root=tmp_path,
            specdock_dir=specdock_dir,
            active_state_store=infra_active_store,
        )

        written = app_set_active.commit_active_state(
            persisted_manifest=new_manifest,
            patch_manifest=new_manifest,
            ports=ports,
            context_pack_text="# new context\n",
        )

        assert written.issue is not None
        assert written.issue.id == "iss-00002"
        assert infra_active_store.load_active_manifest(specdock_dir).manifest == new_manifest
        if managed_kind == "single_link_symlink":
            assert active_path.is_symlink()

    @pytest.mark.parametrize("fail_phase", ["manifest", "pointers", "managed"])
    def test_commit_active_state_rolls_back_root_symlink_and_external_projection(self, tmp_path, fail_phase) -> None:
        _app_contracts, app_ports, app_set_active, _domain_models, infra_contracts = _runtime_modules()
        from spec_dock_runtime.infra import active_store as infra_active_store

        specdock_dir = tmp_path / "spec-dock"
        for layer in ("initiative", "epic", "issue"):
            (specdock_dir / "system" / "active-none" / layer).mkdir(parents=True)
        agent_dir = specdock_dir / ".agent"
        agent_dir.mkdir(parents=True)
        (agent_dir / "active.json").write_bytes(b'{"schema_version":2,"initiative":null,"epic":null,"issue":null}\r\n')
        external_active = tmp_path / "external-active"
        external_active.mkdir()
        active_dir = specdock_dir / "active"
        active_dir.symlink_to("../external-active", target_is_directory=True)
        for layer in ("initiative", "epic", "issue"):
            (external_active / layer).symlink_to(f"../old-{layer}")
        (external_active / "context-pack.md").write_bytes(b"# old context\r\n")
        (external_active / "unmanaged.bin").write_bytes(b"\x00old\xff")

        watched = [
            active_dir,
            external_active,
            *(external_active / layer for layer in ("initiative", "epic", "issue")),
            external_active / "context-pack.md",
            external_active / "current-runbook.json",
            external_active / "unmanaged.bin",
            agent_dir / "active.json",
        ]
        before = _snapshot_paths(watched)
        new_manifest = infra_contracts.ActiveManifest(initiative=None, epic=None, issue=None)
        ports = app_ports.Ports(
            node_reader=_StubNodeReader([]),
            repo_root=tmp_path,
            specdock_dir=specdock_dir,
            active_state_store=_PhaseFailingActiveStateStore(infra_active_store, fail_phase),
        )

        with pytest.raises(
            RuntimeError, match=f"injected {fail_phase[:-1] if fail_phase == 'pointers' else fail_phase}"
        ):
            app_set_active.commit_active_state(
                persisted_manifest=new_manifest,
                patch_manifest=new_manifest,
                ports=ports,
                context_pack_text="# new context\n",
            )

        assert _snapshot_paths(watched) == before

    @pytest.mark.parametrize("fail_phase", ["manifest", "pointers", "managed"])
    @pytest.mark.parametrize("managed_kind", ["crlf_files", "dangling_symlinks", "existing_symlinks"])
    def test_commit_active_state_rolls_back_all_managed_agent_files_verbatim(
        self, tmp_path, fail_phase, managed_kind
    ) -> None:
        _app_contracts, app_ports, app_set_active, _domain_models, infra_contracts = _runtime_modules()
        from spec_dock_runtime.infra import active_store as infra_active_store

        specdock_dir = tmp_path / "spec-dock"
        for layer in ("initiative", "epic", "issue"):
            (specdock_dir / "system" / "active-none" / layer).mkdir(parents=True)
        agent_dir = specdock_dir / ".agent"
        agent_dir.mkdir(parents=True)
        (agent_dir / "active.json").write_text(
            '{"schema_version":2,"initiative":null,"epic":null,"issue":null}\n',
            encoding="utf-8",
        )
        infra_active_store.apply_active_pointers(specdock_dir, None, "# old context\n")

        managed_names = ("index-all.json", "tree-all.json", "index.json", "tree.json")
        external_dir = tmp_path / "external-managed"
        external_dir.mkdir()
        managed_paths = [agent_dir / name for name in managed_names]
        target_paths = [external_dir / name for name in managed_names]
        for path, target in zip(managed_paths, target_paths, strict=True):
            old_bytes = f'{{"active":{{"old":true}},"name":"{path.name}"}}\r\n'.encode()
            if managed_kind == "crlf_files":
                path.write_bytes(old_bytes)
            elif managed_kind == "dangling_symlinks":
                path.symlink_to(target)
            else:
                target.write_bytes(old_bytes)
                path.symlink_to(target)
        unmanaged_path = external_dir / "unmanaged.bin"
        unmanaged_path.write_bytes(b"\x00unmanaged\xff")

        watched = [*managed_paths, *target_paths, unmanaged_path]
        before = _snapshot_paths(watched)
        new_manifest = infra_contracts.ActiveManifest(initiative=None, epic=None, issue=None)
        ports = app_ports.Ports(
            node_reader=_StubNodeReader([]),
            repo_root=tmp_path,
            specdock_dir=specdock_dir,
            active_state_store=_PhaseFailingActiveStateStore(infra_active_store, fail_phase),
        )

        with pytest.raises(
            RuntimeError, match=f"injected {fail_phase[:-1] if fail_phase == 'pointers' else fail_phase}"
        ):
            app_set_active.commit_active_state(
                persisted_manifest=new_manifest,
                patch_manifest=new_manifest,
                ports=ports,
                context_pack_text="# new context\n",
            )

        assert _snapshot_paths(watched) == before

    @pytest.mark.parametrize("fail_phase", ["manifest", "pointers", "managed"])
    def test_commit_active_state_rolls_back_directory_path_trees_verbatim(self, tmp_path, fail_phase) -> None:
        _app_contracts, app_ports, app_set_active, _domain_models, infra_contracts = _runtime_modules()
        from spec_dock_runtime.infra import active_store as infra_active_store

        specdock_dir = tmp_path / "spec-dock"
        agent_dir = specdock_dir / ".agent"
        legacy_dir = specdock_dir / ".work"
        directory_paths = [
            agent_dir / "active.json",
            legacy_dir / "active.json",
            legacy_dir / "current.json",
            *(agent_dir / name for name in ("index-all.json", "tree-all.json", "index.json", "tree.json")),
        ]
        watched: list[Path] = []
        for index, path in enumerate(directory_paths):
            nested = path / "nested"
            nested.mkdir(parents=True)
            raw_path = nested / "raw.bin"
            raw_path.write_bytes(b"\x00old\r\n" + bytes([index]))
            link_path = path / "link"
            link_path.symlink_to("nested/raw.bin")
            empty_path = path / "empty"
            empty_path.mkdir()
            watched.extend((path, nested, raw_path, link_path, empty_path))

        before = _snapshot_paths(watched)
        new_manifest = infra_contracts.ActiveManifest(initiative=None, epic=None, issue=None)
        store = _DirectoryPhaseFailingActiveStateStore(infra_active_store, fail_phase, directory_paths)
        ports = app_ports.Ports(
            node_reader=_StubNodeReader([]),
            repo_root=tmp_path,
            specdock_dir=specdock_dir,
            active_state_store=store,
        )

        with pytest.raises(
            RuntimeError, match=f"injected {fail_phase[:-1] if fail_phase == 'pointers' else fail_phase}"
        ):
            app_set_active.commit_active_state(
                persisted_manifest=new_manifest,
                patch_manifest=new_manifest,
                ports=ports,
                context_pack_text="# new context\n",
            )

        assert _snapshot_paths(watched) == before
