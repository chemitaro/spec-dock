import io
import json
import sys
import tempfile
from pathlib import Path


import contextlib
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
        from spec_dock_runtime.application import set_active as app_set_active
        from spec_dock_runtime.infra import active_store as infra_active_store
        from spec_dock_runtime.infra import contracts as infra_contracts
        from spec_dock_runtime.presentation import cli_text as presentation_cli_text
    finally:
        sys.path.pop(0)

    return (
        runtime_app,
        app_contracts,
        app_ports,
        app_set_active,
        infra_active_store,
        infra_contracts,
        presentation_cli_text,
    )


class _StubNodeReader:
    def load_node_records(self):
        return []


class _StubActiveStateStore:
    def __init__(self, load_result):
        self._load_result = load_result
        self.calls_load = 0
        self.calls_no_migrate = 0

    def load_active_manifest(self, specdock_dir):
        del specdock_dir
        self.calls_load += 1
        return self._load_result

    def load_active_manifest_no_migrate(self, specdock_dir):
        del specdock_dir
        self.calls_no_migrate += 1
        raise AssertionError("load_active_manifest_no_migrate must not be used in S05 active show")


class TestRuntimeActiveS05:
    def test_render_context_pack_states_entry_default_and_escalation_contract(self) -> None:
        (
            _runtime_app,
            _app_contracts,
            _app_ports,
            _app_set_active,
            infra_active_store,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()

        manifest = infra_contracts.ActiveManifest(
            initiative=infra_contracts.ActiveManifestEntry(
                id="init-local-00001",
                path="spec-dock/initiatives/init-local-00001-alpha",
            ),
            epic=infra_contracts.ActiveManifestEntry(
                id="epic-local-00001",
                path="spec-dock/initiatives/init-local-00001-alpha/epics/epic-local-00001-beta",
            ),
            issue=infra_contracts.ActiveManifestEntry(
                id="iss-local-00001",
                path=(
                    "spec-dock/initiatives/init-local-00001-alpha/epics/"
                    "epic-local-00001-beta/issues/iss-local-00001-gamma"
                ),
            ),
        )

        text = infra_active_store._render_context_pack(manifest)

        assert "- entry: `spec-dock/.agent/active.json`" in text
        assert "- default working set: `spec-dock/.agent/index.json`" in text
        assert "- default dependency view: `spec-dock/.agent/deps-issues.json`" in text
        assert "- escalation only: `spec-dock/.agent/index-all.json`" in text
        assert "- Start with `spec-dock/.agent/active.json`." in text
        assert "- For normal work, read `spec-dock/.agent/index.json` and `spec-dock/.agent/deps-issues.json`." in text
        assert "- Read `spec-dock/.agent/index-all.json` only when full-history context is needed." in text
        assert "human guidance" in text
        assert "not the sole source of truth" in text
        assert "- `spec-dock/active/issue/report.md`" in text
        assert "## Authority" in text
        assert "- source: `spec-dock/.agent/active.json`" in text
        assert "proposed or missing authority cannot authorize implementation" in text
        assert "issue ready" in text
        assert "- issue: authority=missing, grants=[]" in text
        assert "- issue: authoritative_input=none, downstream_block=missing_authority" in text

    def test_context_pack_marks_proposed_active_artifact_non_authoritative(self) -> None:
        _runtime_app, _app_contracts, _app_ports, app_set_active, infra_active_store, infra_contracts, _cli = _runtime_modules()
        manifest = infra_contracts.ActiveManifest(
            initiative=None,
            epic=None,
            issue=infra_contracts.ActiveManifestEntry(
                id="iss-local-00001",
                path="spec-dock/initiatives/init-local-00001/epics/epic-local-00001/issues/iss-local-00001",
                authority="proposed",
                grants=("review_input", "planning_input", "implementation_start", "issue_finish"),
                promotion_record={
                    "status": "approved",
                    "authority": "approved",
                    "source_revision": "active:iss-local-00001",
                    "approved_revision": "active:iss-local-00001",
                    "approved_hash": "active:iss-local-00001",
                    "reviewer_target_hash": "active:iss-local-00001",
                    "promotion_decision": "main_orchestrator_promotion",
                },
            ),
        )

        for rendered in (infra_active_store._render_context_pack(manifest), app_set_active.build_context_pack_text(manifest)):
            assert "- issue: authority=proposed" in rendered
            assert "- issue: authoritative_input=none" in rendered
            assert "downstream_block=authority_not_approved" in rendered

    def test_context_pack_blocks_authoritative_input_when_scope_report_has_unresolved_eal(self) -> None:
        _runtime_app, _app_contracts, _app_ports, app_set_active, infra_active_store, infra_contracts, _cli = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_rel = Path("spec-dock/initiatives/init-local-00001/epics/epic-local-00001/issues/iss-local-00001")
            issue_dir = repo_root / issue_rel
            issue_dir.mkdir(parents=True)
            (issue_dir / "report.md").write_text(
                "\n".join(
                    [
                        "# Report",
                        "",
                        "## Evidence Adoption Ledger",
                        "",
                        "| ID | adoption_status | target_artifact | next_action |",
                        "|---|---|---|---|",
                        "| EAL-030 | blocked | plan.md | resolve plan evidence |",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            manifest = infra_contracts.ActiveManifest(
                initiative=None,
                epic=None,
                issue=infra_contracts.ActiveManifestEntry(
                    id="iss-local-00001",
                    path=issue_rel.as_posix(),
                    authority="approved",
                    grants=("implementation_start", "issue_finish"),
                    promotion_record={
                        "status": "approved",
                        "authority": "approved",
                        "source_revision": "active:iss-local-00001",
                        "approved_revision": "active:iss-local-00001",
                        "approved_hash": "active:iss-local-00001",
                        "reviewer_target_hash": "active:iss-local-00001",
                        "promotion_decision": "main_orchestrator_promotion",
                    },
                ),
            )

            for rendered in (
                infra_active_store._render_context_pack(manifest, repo_root=repo_root),
                app_set_active.build_context_pack_text(manifest, repo_root=repo_root),
            ):
                assert "- issue: authority=approved" in rendered
                assert "- issue: authoritative_input=none" in rendered
                assert "downstream_block=evidence_ledger_blocked" in rendered
                assert "blocking_entry_id=EAL-030" in rendered

    def test_sync_auto_update_from_branch_writes_authority_context_pack(self) -> None:
        app_contracts, app_ports = _runtime_modules()[1:3]
        infra_contracts = _runtime_modules()[5]
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

        class _GitGateway:
            def current_branch_or_none(self, repo_root):
                del repo_root
                return "iss-local-00001-authority"

            def origin_github_repo_slug(self, repo_root):
                del repo_root
                return None

        class _ActiveStateStore:
            def __init__(self):
                self.written_manifest = None
                self.rendered_context_pack = None

            def snapshot_current_state(self, specdock_dir):
                del specdock_dir
                return infra_contracts.ActiveStateSnapshot(
                    manifest=None,
                    context_pack_text=None,
                    active_json_text=None,
                    managed_agent_state={},
                )

            def write_active_manifest(self, specdock_dir, manifest):
                del specdock_dir
                self.written_manifest = manifest
                return manifest

            def apply_active_pointers(self, specdock_dir, manifest, rendered_context_pack):
                del specdock_dir, manifest
                self.rendered_context_pack = rendered_context_pack

            def patch_agent_state_active_fields(self, specdock_dir, manifest):
                del specdock_dir, manifest

            def restore_previous_state(self, specdock_dir, snapshot):
                del specdock_dir, snapshot

        nodes_by_id = {
            "init-local-00001": domain_models.SpecNode(
                kind="initiative",
                id="init-local-00001",
                title="initiative",
                slug="initiative",
                path=Path("/repo/spec-dock/initiatives/init-local-00001-initiative"),
                meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-initiative/.meta.json"),
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=None,
            ),
            "epic-local-00001": domain_models.SpecNode(
                kind="epic",
                id="epic-local-00001",
                title="epic",
                slug="epic",
                path=Path("/repo/spec-dock/initiatives/init-local-00001-initiative/epics/epic-local-00001-epic"),
                meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-initiative/epics/epic-local-00001-epic/.meta.json"),
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
            ),
            "iss-local-00001": domain_models.SpecNode(
                kind="issue",
                id="iss-local-00001",
                title="issue",
                slug="issue",
                path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-initiative/epics/"
                    "epic-local-00001-epic/issues/iss-local-00001-issue"
                ),
                meta_path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-initiative/epics/"
                    "epic-local-00001-epic/issues/iss-local-00001-issue/.meta.json"
                ),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=None,
            ),
        }
        state = app_contracts.SyncStateResult(
            graph=domain_models.SpecGraph(nodes_by_id=nodes_by_id),
            active=None,
            issue_statuses={},
            progress=domain_models.ProgressMap(by_node_id={}, counts={"total": 0, "done": 0, "open": 0, "unknown": 0}),
            deps_state=domain_models.DepsState(nodes=[], warnings=[]),
            deps_eval_by_id={},
            generated_at="2026-05-24T00:00:00+00:00",
            warnings=[],
            deps_preflight_error=None,
            repo_root=Path("/repo"),
        )
        active_state_store = _ActiveStateStore()
        ports = app_ports.Ports(
            node_reader=_StubNodeReader(),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
            git_gateway=_GitGateway(),
            active_state_store=active_state_store,
        )

        next_state, outcome = app_sync_state.maybe_auto_update_from_branch(state, ports)

        assert outcome is not None
        assert outcome is not None
        assert outcome.applied
        assert next_state.active.issue_id == "iss-local-00001"
        assert active_state_store.written_manifest is not None
        assert active_state_store.written_manifest is not None
        assert active_state_store.written_manifest.issue is not None
        assert active_state_store.written_manifest.issue.authority == "approved"
        assert "issue_ready" in active_state_store.written_manifest.issue.grants
        assert active_state_store.rendered_context_pack is not None
        assert active_state_store.rendered_context_pack is not None
        assert "issue ready" in active_state_store.rendered_context_pack
        assert "- issue: authority=approved" in active_state_store.rendered_context_pack

    def test_show_active_reads_agent_manifest_into_active_view_result(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_ports,
            app_set_active,
            _infra_active_store,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()

        manifest = infra_contracts.ActiveManifest(
            initiative=infra_contracts.ActiveManifestEntry(
                id="init-local-00001",
                path="spec-dock/initiatives/init-local-00001-auth-platform",
            ),
            epic=infra_contracts.ActiveManifestEntry(
                id="epic-local-00001",
                path="spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth",
            ),
            issue=infra_contracts.ActiveManifestEntry(
                id="iss-local-00001",
                path=(
                    "spec-dock/initiatives/init-local-00001-auth-platform/epics/"
                    "epic-local-00001-jwt-auth/issues/iss-local-00001-add-refresh-token"
                ),
            ),
        )
        load_result = infra_contracts.ActiveManifestLoadResult(
            manifest=manifest,
            source="agent.active",
            warnings=[],
        )
        active_store = _StubActiveStateStore(load_result)
        ports = app_ports.Ports(
            node_reader=_StubNodeReader(),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
            active_state_store=active_store,
        )

        result = app_set_active.show_active(app_contracts.ShowActiveRequest(), ports)

        assert result.source == "agent.active"
        assert result.warnings == []
        assert result.initiative.id == "init-local-00001"
        assert result.epic.id == "epic-local-00001"
        assert result.issue.id == "iss-local-00001"
        assert active_store.calls_load == 1
        assert active_store.calls_no_migrate == 0

    def test_load_active_manifest_legacy_priority_and_no_write_back(self) -> None:
        (
            _runtime_app,
            _app_contracts,
            _app_ports,
            _app_set_active,
            infra_active_store,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()

        with tempfile.TemporaryDirectory() as tmp:
            specdock_dir = Path(tmp) / "spec-dock"
            agent_dir = specdock_dir / ".agent"
            work_dir = specdock_dir / ".work"
            agent_dir.mkdir(parents=True, exist_ok=True)
            work_dir.mkdir(parents=True, exist_ok=True)

            legacy_active_path = work_dir / "active.json"
            legacy_current_path = work_dir / "current.json"
            legacy_active = {
                "initiative": {"id": "init-local-00001", "path": "spec-dock/initiatives/init-local-00001-alpha"},
                "epic": {"id": "epic-local-00001", "path": "spec-dock/initiatives/init-local-00001-alpha/epics/epic-local-00001-beta"},
                "issue": {"id": "iss-local-00001", "path": "spec-dock/initiatives/init-local-00001-alpha/epics/epic-local-00001-beta/issues/iss-local-00001-gamma"},
            }
            legacy_current = {
                "initiative": {"id": "init-local-99999", "path": "spec-dock/initiatives/init-local-99999-ignored"},
                "epic": None,
                "issue": None,
            }
            legacy_active_path.write_text(json.dumps(legacy_active, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            legacy_current_path.write_text(
                json.dumps(legacy_current, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            before_active = legacy_active_path.read_text(encoding="utf-8")
            before_current = legacy_current_path.read_text(encoding="utf-8")

            result = infra_active_store.load_active_manifest(specdock_dir)

            assert result.source == "legacy.work.active"
            assert result.warnings == []
            assert result.manifest is not None
            assert result.manifest is not None
            assert result.manifest.initiative.id == "init-local-00001"
            assert result.manifest.epic.id == "epic-local-00001"
            assert result.manifest.issue.id == "iss-local-00001"

            assert not (agent_dir / "active.json").exists()
            assert legacy_active_path.read_text(encoding="utf-8") == before_active
            assert legacy_current_path.read_text(encoding="utf-8") == before_current

    def test_load_active_manifest_all_null_agent_manifest_is_valid_and_no_legacy_fallback(self) -> None:
        (
            _runtime_app,
            _app_contracts,
            _app_ports,
            _app_set_active,
            infra_active_store,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()

        with tempfile.TemporaryDirectory() as tmp:
            specdock_dir = Path(tmp) / "spec-dock"
            agent_dir = specdock_dir / ".agent"
            work_dir = specdock_dir / ".work"
            agent_dir.mkdir(parents=True, exist_ok=True)
            work_dir.mkdir(parents=True, exist_ok=True)

            agent_active_path = agent_dir / "active.json"
            legacy_active_path = work_dir / "active.json"
            agent_active_path.write_text(
                json.dumps(
                    {
                        "initiative": None,
                        "epic": None,
                        "issue": None,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            legacy_active_path.write_text(
                json.dumps(
                    {
                        "initiative": {"id": "init-local-stale", "path": "spec-dock/initiatives/init-local-stale"},
                        "epic": {"id": "epic-local-stale", "path": "spec-dock/initiatives/init-local-stale/epics/epic-local-stale"},
                        "issue": {
                            "id": "iss-local-stale",
                            "path": "spec-dock/initiatives/init-local-stale/epics/epic-local-stale/issues/iss-local-stale",
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            before_legacy = legacy_active_path.read_text(encoding="utf-8")

            result = infra_active_store.load_active_manifest(specdock_dir)

            assert result.source == "agent.active"
            assert result.warnings == []
            assert result.manifest is not None
            assert result.manifest is not None
            assert result.manifest.initiative is None
            assert result.manifest.epic is None
            assert result.manifest.issue is None
            assert legacy_active_path.read_text(encoding="utf-8") == before_legacy

    def test_legacy_absolute_agent_manifest_is_readable_and_not_rewritten(self) -> None:
        (
            _runtime_app,
            _app_contracts,
            _app_ports,
            _app_set_active,
            infra_active_store,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            agent_dir = specdock_dir / ".agent"
            active_dir = specdock_dir / "active"
            init_dir = specdock_dir / "initiatives" / "init-local-00001-alpha"
            epic_dir = init_dir / "epics" / "epic-local-00001-beta"
            issue_dir = epic_dir / "issues" / "iss-local-00001-gamma"
            issue_dir.mkdir(parents=True, exist_ok=True)
            agent_dir.mkdir(parents=True, exist_ok=True)

            active_json_path = agent_dir / "active.json"
            active_json_path.write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "initiative": {"id": "init-local-00001", "path": init_dir.as_posix()},
                        "epic": {"id": "epic-local-00001", "path": epic_dir.as_posix()},
                        "issue": {"id": "iss-local-00001", "path": issue_dir.as_posix()},
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            before = active_json_path.read_text(encoding="utf-8")

            result = infra_active_store.load_active_manifest(specdock_dir)
            assert result.source == "agent.active"
            assert result.manifest is not None
            assert result.manifest is not None
            assert result.manifest.issue is not None
            assert result.manifest.issue.path == issue_dir.as_posix()

            infra_active_store.apply_active_pointers(
                specdock_dir,
                result.manifest,
                "# Context Pack (generated)\n",
            )

            issue_pointer = active_dir / "issue"
            if issue_pointer.is_symlink():
                assert issue_pointer.resolve() == issue_dir.resolve()
            else:
                path_file = active_dir / "issue.path"
                assert path_file.is_file()
                resolved = (active_dir / path_file.read_text(encoding="utf-8").strip()).resolve()
                assert resolved == issue_dir.resolve()

            assert active_json_path.read_text(encoding="utf-8") == before

    def test_legacy_absolute_agent_manifest_path_remaps_to_current_repo_when_possible(self) -> None:
        (
            _runtime_app,
            _app_contracts,
            _app_ports,
            _app_set_active,
            infra_active_store,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            agent_dir = specdock_dir / ".agent"
            active_dir = specdock_dir / "active"
            init_rel = Path("spec-dock/initiatives/init-local-00001-alpha")
            epic_rel = init_rel / "epics" / "epic-local-00001-beta"
            issue_rel = epic_rel / "issues" / "iss-local-00001-gamma"
            issue_dir = repo_root / issue_rel
            issue_dir.mkdir(parents=True, exist_ok=True)
            agent_dir.mkdir(parents=True, exist_ok=True)

            old_root = Path("/moved/from/old-repo")
            active_json_path = agent_dir / "active.json"
            active_json_path.write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "initiative": {"id": "init-local-00001", "path": (old_root / init_rel).as_posix()},
                        "epic": {"id": "epic-local-00001", "path": (old_root / epic_rel).as_posix()},
                        "issue": {"id": "iss-local-00001", "path": (old_root / issue_rel).as_posix()},
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            before = active_json_path.read_text(encoding="utf-8")

            result = infra_active_store.load_active_manifest(specdock_dir)
            assert result.source == "agent.active"
            assert result.manifest is not None
            assert result.manifest is not None

            infra_active_store.apply_active_pointers(
                specdock_dir,
                result.manifest,
                "# Context Pack (generated)\n",
            )

            issue_pointer = active_dir / "issue"
            if issue_pointer.is_symlink():
                assert issue_pointer.resolve() == issue_dir.resolve()
            else:
                path_file = active_dir / "issue.path"
                assert path_file.is_file()
                resolved = (active_dir / path_file.read_text(encoding="utf-8").strip()).resolve()
                assert resolved == issue_dir.resolve()

            assert active_json_path.read_text(encoding="utf-8") == before

    def test_legacy_absolute_agent_manifest_prefers_trailing_specdock_segment(self) -> None:
        (
            _runtime_app,
            _app_contracts,
            _app_ports,
            _app_set_active,
            infra_active_store,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            agent_dir = specdock_dir / ".agent"
            active_dir = specdock_dir / "active"
            init_rel = Path("spec-dock/initiatives/init-local-00001-alpha")
            epic_rel = init_rel / "epics" / "epic-local-00001-beta"
            issue_rel = epic_rel / "issues" / "iss-local-00001-gamma"
            issue_dir = repo_root / issue_rel
            issue_dir.mkdir(parents=True, exist_ok=True)
            agent_dir.mkdir(parents=True, exist_ok=True)

            legacy_root_with_specdock_name = Path("/old/spec-dock")
            active_json_path = agent_dir / "active.json"
            active_json_path.write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "initiative": {
                            "id": "init-local-00001",
                            "path": (legacy_root_with_specdock_name / init_rel).as_posix(),
                        },
                        "epic": {
                            "id": "epic-local-00001",
                            "path": (legacy_root_with_specdock_name / epic_rel).as_posix(),
                        },
                        "issue": {
                            "id": "iss-local-00001",
                            "path": (legacy_root_with_specdock_name / issue_rel).as_posix(),
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            result = infra_active_store.load_active_manifest(specdock_dir)
            assert result.source == "agent.active"
            assert result.manifest is not None
            assert result.manifest is not None

            infra_active_store.apply_active_pointers(
                specdock_dir,
                result.manifest,
                "# Context Pack (generated)\n",
            )

            issue_pointer = active_dir / "issue"
            if issue_pointer.is_symlink():
                assert issue_pointer.resolve() == issue_dir.resolve()
            else:
                path_file = active_dir / "issue.path"
                assert path_file.is_file()
                resolved = (active_dir / path_file.read_text(encoding="utf-8").strip()).resolve()
                assert resolved == issue_dir.resolve()

    def test_legacy_absolute_agent_manifest_outside_repo_falls_back_to_placeholder(self) -> None:
        (
            _runtime_app,
            _app_contracts,
            _app_ports,
            _app_set_active,
            infra_active_store,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            agent_dir = specdock_dir / ".agent"
            active_dir = specdock_dir / "active"
            placeholder_issue_dir = specdock_dir / "system" / "active-none" / "issue"
            placeholder_epic_dir = specdock_dir / "system" / "active-none" / "epic"
            placeholder_init_dir = specdock_dir / "system" / "active-none" / "initiative"
            placeholder_issue_dir.mkdir(parents=True, exist_ok=True)
            placeholder_epic_dir.mkdir(parents=True, exist_ok=True)
            placeholder_init_dir.mkdir(parents=True, exist_ok=True)
            agent_dir.mkdir(parents=True, exist_ok=True)

            with tempfile.TemporaryDirectory() as outside_tmp:
                outside_root = Path(outside_tmp)
                outside_init = outside_root / "outside-init"
                outside_epic = outside_root / "outside-epic"
                outside_issue = outside_root / "outside-issue"
                outside_init.mkdir(parents=True, exist_ok=True)
                outside_epic.mkdir(parents=True, exist_ok=True)
                outside_issue.mkdir(parents=True, exist_ok=True)

                active_json_path = agent_dir / "active.json"
                active_json_path.write_text(
                    json.dumps(
                        {
                            "schema_version": 2,
                            "initiative": {"id": "init-local-00001", "path": outside_init.as_posix()},
                            "epic": {"id": "epic-local-00001", "path": outside_epic.as_posix()},
                            "issue": {"id": "iss-local-00001", "path": outside_issue.as_posix()},
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )

                result = infra_active_store.load_active_manifest(specdock_dir)
                assert result.source == "agent.active"
                assert result.manifest is not None
                assert result.manifest is not None

                infra_active_store.apply_active_pointers(
                    specdock_dir,
                    result.manifest,
                    "# Context Pack (generated)\n",
                )

            issue_pointer = active_dir / "issue"
            if issue_pointer.is_symlink():
                assert issue_pointer.resolve() == placeholder_issue_dir.resolve()
            else:
                path_file = active_dir / "issue.path"
                assert path_file.is_file()
                resolved = (active_dir / path_file.read_text(encoding="utf-8").strip()).resolve()
                assert resolved == placeholder_issue_dir.resolve()

    def test_render_active_show_text_regression(self) -> None:
        (
            _runtime_app,
            app_contracts,
            _app_ports,
            _app_set_active,
            _infra_active_store,
            _infra_contracts,
            presentation_cli_text,
        ) = _runtime_modules()

        result = app_contracts.ActiveViewResult(
            initiative=app_contracts.ActiveViewEntry(
                id="init-local-00001",
                path="spec-dock/initiatives/init-local-00001-alpha",
            ),
            epic=app_contracts.ActiveViewEntry(
                id="epic-local-00001",
                path="spec-dock/initiatives/init-local-00001-alpha/epics/epic-local-00001-beta",
            ),
            issue=app_contracts.ActiveViewEntry(
                id="iss-local-00001",
                path=(
                    "spec-dock/initiatives/init-local-00001-alpha/epics/"
                    "epic-local-00001-beta/issues/iss-local-00001-gamma"
                ),
            ),
            source="agent.active",
            warnings=["active_manifest_legacy_shape_normalized"],
        )
        text = presentation_cli_text.render_active_show_text(result)
        assert text.stdout_lines == [
                "initiative: init-local-00001 (spec-dock/initiatives/init-local-00001-alpha)",
                "epic: epic-local-00001 (spec-dock/initiatives/init-local-00001-alpha/epics/epic-local-00001-beta)",
                (
                    "issue: iss-local-00001 "
                    "(spec-dock/initiatives/init-local-00001-alpha/epics/epic-local-00001-beta/issues/iss-local-00001-gamma)"
                ),
            ]
        assert text.stderr_lines == []
        assert text.warnings == ["active_manifest_legacy_shape_normalized"]

        none_result = app_contracts.ActiveViewResult(
            initiative=app_contracts.ActiveViewEntry(id=None, path=None),
            epic=app_contracts.ActiveViewEntry(id=None, path=None),
            issue=app_contracts.ActiveViewEntry(id=None, path=None),
            source="none",
            warnings=[],
        )
        none_text = presentation_cli_text.render_active_show_text(none_result)
        assert none_text.stdout_lines == [
                "spec-dock: active: (not set)",
                "fallback: spec-dock/active/{initiative,epic,issue} -> spec-dock/system/active-none/{initiative,epic,issue}",
                "next: spec-dock/scripts/spec-dock active set <target>",
            ]
        assert none_text.stderr_lines == []

    def test_active_show_main_uses_use_case_and_returns_zero(self) -> None:
        (
            runtime_app,
            app_contracts,
            _app_ports,
            _app_set_active,
            _infra_active_store,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        from spec_dock_runtime.cli import bootstrap as cli_bootstrap

        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_application_show_active = cli_bootstrap.application_show_active
        original_load_active_manifest_no_migrate = runtime_app._load_active_manifest_no_migrate

        runtime_app._find_specdock_dir = lambda: Path("/repo/spec-dock")
        cli_bootstrap.application_show_active = lambda _req, _ports: app_contracts.ActiveViewResult(
            initiative=app_contracts.ActiveViewEntry(id=None, path=None),
            epic=app_contracts.ActiveViewEntry(id=None, path=None),
            issue=app_contracts.ActiveViewEntry(id=None, path=None),
            source="none",
            warnings=["active_show_warning"],
        )
        runtime_app._load_active_manifest_no_migrate = (
            lambda _specdock_dir: (_ for _ in ()).throw(
                AssertionError("active show path must not call _load_active_manifest_no_migrate")
            )
        )
        try:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = runtime_app.main(["active", "show"])
        finally:
            runtime_app._find_specdock_dir = original_find_specdock_dir
            cli_bootstrap.application_show_active = original_application_show_active
            runtime_app._load_active_manifest_no_migrate = original_load_active_manifest_no_migrate

        assert exit_code == 0
        assert stdout.getvalue() == (
                "spec-dock: active: (not set)\n"
                "fallback: spec-dock/active/{initiative,epic,issue} -> spec-dock/system/active-none/{initiative,epic,issue}\n"
                "next: spec-dock/scripts/spec-dock active set <target>\n"
            )
        assert "spec-dock: (warn) active_show_warning" in stderr.getvalue()
