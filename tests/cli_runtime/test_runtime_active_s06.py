from pathlib import Path
import sys

import pytest


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application import (
            contracts as app_contracts,
            ports as app_ports,
            set_active as app_set_active,
        )
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


class _StubGitGateway:
    def __init__(self, *, origin_repo_slug: str | None = None):
        self.calls = []
        self.current_branch = "main"
        self.origin_repo_slug = origin_repo_slug

    def current_branch_or_none(self, repo_root):
        self.calls.append(("current_branch_or_none", str(repo_root)))
        return self.current_branch

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
        git_gateway=None,
        active_state_store=None,
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
            git_gateway=git_gateway or _StubGitGateway(),
            active_state_store=active_state_store or _StubActiveStateStore(infra_contracts),
        )

    def test_set_active_non_issue_target_writes_selection(self) -> None:
        app_contracts, _app_ports, app_set_active, _infra_contracts = _runtime_modules()
        ports = self._ports()
        req = app_contracts.SetActiveRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="init-local-00001", github_issue_number=None),
        )
        result = app_set_active.set_active(req, ports)
        assert result.manifest_written
        assert result.selection.initiative_id == "init-local-00001"
        assert result.selection.epic_id is None
        assert result.selection.issue_id is None

    def test_sync_branch_inference_propagates_current_repo_slug(self) -> None:
        app_contracts, _app_ports, _app_set_active, infra_contracts = _runtime_modules()
        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
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

    def test_set_active_patch_failure_rolls_back(self) -> None:
        app_contracts, _app_ports, app_set_active, _infra_contracts = _runtime_modules()
        active_store = _StubActiveStateStore(_runtime_modules()[3])
        active_store.raise_on_patch = True
        ports = self._ports(
            active_state_store=active_store,
        )
        req = app_contracts.SetActiveRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
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
                initiative=infra_contracts.ActiveManifestEntry(
                    "init-local-00001", "spec-dock/initiatives/init-local-00001"
                ),
                epic=infra_contracts.ActiveManifestEntry(
                    "epic-local-00001", "spec-dock/initiatives/init-local-00001/epics/epic-local-00001"
                ),
                issue=infra_contracts.ActiveManifestEntry(
                    "iss-local-00001",
                    "spec-dock/initiatives/init-local-00001/epics/epic-local-00001/issues/iss-local-00001",
                ),
            ),
            source="agent.active",
            warnings=[],
        )
        ports = self._ports(
            active_state_store=active_store,
        )
        result = app_set_active.clear_active(app_contracts.ClearActiveRequest(), ports)
        assert result.cleared
        assert result.previous.issue_id == "iss-local-00001"
        assert active_store.last_patch_manifest is None
