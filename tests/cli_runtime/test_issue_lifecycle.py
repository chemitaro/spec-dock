import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

import pytest

from tests.cli_runtime.harness import CliRuntimeHarness, main


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application import (
            contracts as app_contracts,
            issue_lifecycle as app_issue_lifecycle,
            ports as app_ports,
        )
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.infra import contracts as infra_contracts
    finally:
        sys.path.pop(0)
    return app_contracts, app_issue_lifecycle, app_ports, domain_models, infra_contracts


class _StubNodeReader:
    def load_node_records(self):
        return []


class _StubActiveStateStore:
    def __init__(
        self,
        infra_contracts,
        *,
        issue_authority="approved",
        issue_grants=None,
        promotion_record=None,
        fail_write=False,
    ) -> None:
        self._infra_contracts = infra_contracts
        self.issue_authority = issue_authority
        self.issue_grants = (
            tuple(issue_grants)
            if issue_grants is not None
            else (
                "review_input",
                "planning_input",
                "design_baseline",
                "implementation_start",
                "issue_ready",
                "issue_finish",
                "phase_completion",
            )
        )
        self.promotion_record = promotion_record or {
            "status": "approved",
            "authority": "approved",
            "source_revision": "active:iss-00101",
            "approved_revision": "active:iss-00101",
            "approved_hash": "active:iss-00101",
            "reviewer_target_hash": "active:iss-00101",
            "promotion_decision": "main_orchestrator_promotion",
        }
        self.fail_write = fail_write
        self.write_calls = []
        self.restore_calls = []
        self.pointer_calls = []
        self.patch_calls = []

    def load_active_manifest(self, specdock_dir: Path):
        del specdock_dir
        return self._infra_contracts.ActiveManifestLoadResult(
            manifest=self._infra_contracts.ActiveManifest(
                initiative=None,
                epic=None,
                issue=self._infra_contracts.ActiveManifestEntry(
                    id="iss-00101",
                    path="spec-dock/initiatives/init-00001/epics/epic-00002/issues/iss-00101",
                    authority=self.issue_authority,
                    grants=self.issue_grants,
                    promotion_record=self.promotion_record,
                ),
            ),
            source="agent.active",
            warnings=[],
        )

    def snapshot_current_state(self, specdock_dir: Path):
        return self._infra_contracts.ActiveStateSnapshot(
            manifest=self.load_active_manifest(specdock_dir).manifest,
            context_pack_text="previous context",
            active_json_text="{}",
            managed_agent_state={},
        )

    def write_active_manifest(self, specdock_dir: Path, manifest):
        del specdock_dir
        self.write_calls.append(manifest)
        if self.fail_write:
            raise RuntimeError("write active failed")
        self.issue_authority = manifest.issue.authority if manifest.issue is not None else None
        self.issue_grants = manifest.issue.grants if manifest.issue is not None else ()
        self.promotion_record = manifest.issue.promotion_record if manifest.issue is not None else None
        return manifest

    def apply_active_pointers(self, specdock_dir: Path, manifest, rendered_context_pack: str):
        del specdock_dir
        self.pointer_calls.append((manifest, rendered_context_pack))

    def patch_agent_state_active_fields(self, specdock_dir: Path, manifest):
        del specdock_dir
        self.patch_calls.append(manifest)

    def restore_previous_state(self, specdock_dir: Path, snapshot) -> None:
        del specdock_dir
        self.restore_calls.append(snapshot)


class TestIssueLifecycleApplication:
    def test_issue_finish_blocks_proposed_or_missing_grant_active_issue_before_close(self) -> None:
        app_contracts, app_issue_lifecycle, app_ports, _domain_models, infra_contracts = _runtime_modules()
        original_close_node = app_issue_lifecycle.close_node
        close_calls = []
        try:

            def fake_close_node(req, ports):
                close_calls.append((req, ports))
                raise AssertionError("close_node must not run when authority gate fails")

            app_issue_lifecycle.close_node = fake_close_node

            cases = (
                (
                    "proposed",
                    "proposed",
                    (
                        "review_input",
                        "planning_input",
                        "design_baseline",
                        "implementation_start",
                        "issue_ready",
                        "issue_finish",
                        "phase_completion",
                    ),
                    "authority_not_approved",
                ),
                (
                    "missing grant",
                    "approved",
                    ("review_input", "planning_input"),
                    "missing_required_grant",
                ),
                ("missing metadata", None, (), "missing_authority"),
            )
            for _label, authority, grants, reason in cases:
                close_calls.clear()
                with tempfile.TemporaryDirectory() as tmp:
                    repo_root = Path(tmp)
                    ports = app_ports.Ports(
                        node_reader=_StubNodeReader(),
                        repo_root=repo_root,
                        specdock_dir=repo_root / "spec-dock",
                        active_state_store=_StubActiveStateStore(
                            infra_contracts,
                            issue_authority=authority,
                            issue_grants=grants,
                        ),
                    )
                    with pytest.raises(RuntimeError) as raised:
                        app_issue_lifecycle.issue_finish(app_contracts.IssueFinishRequest(), ports)

                message = str(raised.value)
                assert "issue finish blocked: authority gate failed" in message
                assert reason in message
                assert "required_grant: issue_finish" in message
                assert close_calls == []
        finally:
            app_issue_lifecycle.close_node = original_close_node

    def test_issue_finish_blocks_promotion_record_for_different_issue_before_close(self) -> None:
        app_contracts, app_issue_lifecycle, app_ports, _domain_models, infra_contracts = _runtime_modules()
        original_close_node = app_issue_lifecycle.close_node
        close_calls = []
        try:

            def fake_close_node(req, ports):
                close_calls.append((req, ports))
                raise AssertionError("close_node must not run when promotion record is stale")

            app_issue_lifecycle.close_node = fake_close_node
            stale_record = {
                "status": "approved",
                "authority": "approved",
                "source_revision": "active:iss-00999",
                "approved_revision": "active:iss-00999",
                "approved_hash": "active:iss-00999",
                "reviewer_target_hash": "active:iss-00999",
                "promotion_decision": "main_orchestrator_promotion",
            }
            with tempfile.TemporaryDirectory() as tmp:
                repo_root = Path(tmp)
                ports = app_ports.Ports(
                    node_reader=_StubNodeReader(),
                    repo_root=repo_root,
                    specdock_dir=repo_root / "spec-dock",
                    active_state_store=_StubActiveStateStore(
                        infra_contracts,
                        promotion_record=stale_record,
                    ),
                )
                with pytest.raises(RuntimeError) as raised:
                    app_issue_lifecycle.issue_finish(app_contracts.IssueFinishRequest(), ports)

            message = str(raised.value)
            assert "issue finish blocked: authority gate failed" in message
            assert "promotion_record_not_bound_to_active_entry" in message
            assert "expected_revision=active:iss-00101" in message
            assert close_calls == []
        finally:
            app_issue_lifecycle.close_node = original_close_node

    def test_issue_finish_blocks_unresolved_evidence_adoption_ledger_before_close(self) -> None:
        app_contracts, app_issue_lifecycle, app_ports, _domain_models, infra_contracts = _runtime_modules()
        original_close_node = app_issue_lifecycle.close_node
        close_calls = []
        runtime_record = {
            "status": "approved",
            "authority": "approved",
            "source_revision": "active:iss-00101",
            "approved_revision": "active:iss-00101",
            "approved_hash": "active:iss-00101",
            "reviewer_target_hash": "active:iss-00101",
            "promotion_decision": "runtime_active_selection",
        }
        try:

            def fake_close_node(req, ports):
                close_calls.append((req, ports))
                raise AssertionError("close_node must not run when EAL gate fails")

            app_issue_lifecycle.close_node = fake_close_node
            with tempfile.TemporaryDirectory() as tmp:
                repo_root = Path(tmp)
                issue_dir = (
                    repo_root
                    / "spec-dock"
                    / "initiatives"
                    / "init-00001"
                    / "epics"
                    / "epic-00002"
                    / "issues"
                    / "iss-00101"
                )
                issue_dir.mkdir(parents=True)
                (issue_dir / "report.md").write_text(
                    "\n".join([
                        "## 証跡採用台帳（Evidence Adoption Ledger）",
                        "",
                        "| ID | adoption_status | target_artifact | next_action |",
                        "|---|---|---|---|",
                        "| EAL-009 | blocked | design.md | resolve reviewer evidence |",
                        "",
                        "## Other",
                    ])
                    + "\n",
                    encoding="utf-8",
                )
                store = _StubActiveStateStore(infra_contracts, promotion_record=runtime_record)
                ports = app_ports.Ports(
                    node_reader=_StubNodeReader(),
                    repo_root=repo_root,
                    specdock_dir=repo_root / "spec-dock",
                    active_state_store=store,
                )
                with pytest.raises(RuntimeError) as raised:
                    app_issue_lifecycle.issue_finish(app_contracts.IssueFinishRequest(), ports)

            message = str(raised.value)
            assert "issue finish blocked: Evidence Adoption Ledger" in message
            assert "blocking_entry_id: EAL-009" in message
            assert "resolve reviewer evidence" in message
            assert close_calls == []
            assert store.write_calls == []
            assert store.promotion_record["promotion_decision"] == "runtime_active_selection"
        finally:
            app_issue_lifecycle.close_node = original_close_node

    def test_issue_finish_blocks_localized_eal_header_before_close(self) -> None:
        app_contracts, app_issue_lifecycle, app_ports, _domain_models, infra_contracts = _runtime_modules()
        original_close_node = app_issue_lifecycle.close_node
        close_calls = []
        try:

            def fake_close_node(req, ports):
                close_calls.append((req, ports))
                raise AssertionError("close_node must not run when localized EAL gate fails")

            app_issue_lifecycle.close_node = fake_close_node
            with tempfile.TemporaryDirectory() as tmp:
                repo_root = Path(tmp)
                issue_dir = (
                    repo_root
                    / "spec-dock"
                    / "initiatives"
                    / "init-00001"
                    / "epics"
                    / "epic-00002"
                    / "issues"
                    / "iss-00101"
                )
                issue_dir.mkdir(parents=True)
                (issue_dir / "report.md").write_text(
                    "\n".join([
                        "## 証跡採用台帳（Evidence Adoption Ledger）",
                        "",
                        "| ID | 採用状態（adoption_status） | 対象（target） | 次アクション（next_action） |",
                        "|---|---|---|---|",
                        "| EAL-011 | stale | plan.md | refresh localized evidence |",
                        "",
                        "## Other",
                    ])
                    + "\n",
                    encoding="utf-8",
                )
                ports = app_ports.Ports(
                    node_reader=_StubNodeReader(),
                    repo_root=repo_root,
                    specdock_dir=repo_root / "spec-dock",
                    active_state_store=_StubActiveStateStore(infra_contracts),
                )
                with pytest.raises(RuntimeError) as raised:
                    app_issue_lifecycle.issue_finish(app_contracts.IssueFinishRequest(), ports)

            message = str(raised.value)
            assert "issue finish blocked: Evidence Adoption Ledger" in message
            assert "blocking_entry_id: EAL-011" in message
            assert "evidence_ledger_stale" in message
            assert "refresh localized evidence" in message
            assert close_calls == []
        finally:
            app_issue_lifecycle.close_node = original_close_node

    def test_issue_finish_blocks_proposed_or_missing_metadata_delegated_artifacts_before_close(self) -> None:
        app_contracts, app_issue_lifecycle, app_ports, _domain_models, infra_contracts = _runtime_modules()
        original_close_node = app_issue_lifecycle.close_node
        close_calls = []
        runtime_record = {
            "status": "approved",
            "authority": "approved",
            "source_revision": "active:iss-00101",
            "approved_revision": "active:iss-00101",
            "approved_hash": "active:iss-00101",
            "reviewer_target_hash": "active:iss-00101",
            "promotion_decision": "runtime_active_selection",
        }
        try:

            def fake_close_node(req, ports):
                close_calls.append((req, ports))
                raise AssertionError("close_node must not run when delegated artifact gate fails")

            app_issue_lifecycle.close_node = fake_close_node
            cases = (
                (
                    "proposed",
                    "---\n"
                    "status: draft\n"
                    "authority: proposed\n"
                    "grants: [review_input, planning_input]\n"
                    "owner_role: main-orchestrator\n"
                    "draft_author_role: system-architect\n"
                    "approval: pending-main-promotion\n"
                    "source_revision: rev-1\n"
                    "approved_revision: rev-1\n"
                    "approved_hash: hash-1\n"
                    "manifest_hash: manifest-hash\n"
                    "permission_profile_name: spec-dock-da\n"
                    "permission_profile_hash: profile-hash\n"
                    "write_session_invocation_hash: session-hash\n"
                    "probe_run_id: probe-1\n"
                    "positive_probe_result: pass\n"
                    "---\n# Design\n",
                    "authority_not_approved",
                ),
                (
                    "missing metadata",
                    "---\nauthority: approved\nmanifest_hash: manifest-hash\n---\n# Design\n",
                    "incomplete_draft_metadata",
                ),
            )
            for _label, artifact_text, expected_reason in cases:
                close_calls.clear()
                with tempfile.TemporaryDirectory() as tmp:
                    repo_root = Path(tmp)
                    issue_dir = (
                        repo_root
                        / "spec-dock"
                        / "initiatives"
                        / "init-00001"
                        / "epics"
                        / "epic-00002"
                        / "issues"
                        / "iss-00101"
                    )
                    issue_dir.mkdir(parents=True)
                    (issue_dir / "design.md").write_text(artifact_text, encoding="utf-8")
                    store = _StubActiveStateStore(infra_contracts, promotion_record=runtime_record)
                    ports = app_ports.Ports(
                        node_reader=_StubNodeReader(),
                        repo_root=repo_root,
                        specdock_dir=repo_root / "spec-dock",
                        active_state_store=store,
                    )
                    with pytest.raises(RuntimeError) as raised:
                        app_issue_lifecycle.issue_finish(app_contracts.IssueFinishRequest(), ports)

                message = str(raised.value)
                assert "issue finish blocked: delegated artifact authority gate failed" in message
                assert expected_reason in message
                assert "design.md" in message
                assert close_calls == []
                assert store.write_calls == []
                assert store.promotion_record["promotion_decision"] == "runtime_active_selection"
        finally:
            app_issue_lifecycle.close_node = original_close_node

    def test_active_issue_lifecycle_gate_blocks_unresolved_eal_for_non_finish_purposes(self) -> None:
        _app_contracts, app_issue_lifecycle, app_ports, _domain_models, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = (
                repo_root / "spec-dock" / "initiatives" / "init-00001" / "epics" / "epic-00002" / "issues" / "iss-00101"
            )
            issue_dir.mkdir(parents=True)
            (issue_dir / "report.md").write_text(
                "\n".join([
                    "## Evidence Adoption Ledger",
                    "",
                    "| id | adoption_status | target_artifact | next_action |",
                    "|---|---|---|---|",
                    "| EAL-010 | stale | plan.md | refresh adopted evidence |",
                    "",
                    "## Other",
                ])
                + "\n",
                encoding="utf-8",
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(),
                repo_root=repo_root,
                specdock_dir=repo_root / "spec-dock",
                active_state_store=_StubActiveStateStore(infra_contracts),
            )

            cases = (
                ("implementation_start", "implementation start"),
                ("issue_ready", "issue ready"),
                ("phase_completion", "phase completion"),
            )
            for required_grant, command_label in cases:
                with pytest.raises(RuntimeError) as raised:
                    app_issue_lifecycle.require_active_issue_lifecycle_gate(
                        ports,
                        required_grant=required_grant,
                        purpose=required_grant,
                        command_label=command_label,
                    )
                message = str(raised.value)
                assert f"{command_label} blocked: Evidence Adoption Ledger" in message
                assert "blocking_entry_id: EAL-010" in message
                assert "refresh adopted evidence" in message

    def test_issue_finish_transition_persistence_failure_rolls_back_before_close(self) -> None:
        app_contracts, app_issue_lifecycle, app_ports, _domain_models, infra_contracts = _runtime_modules()
        original_close_node = app_issue_lifecycle.close_node
        close_calls = []
        runtime_record = {
            "status": "approved",
            "authority": "approved",
            "source_revision": "active:iss-00101",
            "approved_revision": "active:iss-00101",
            "approved_hash": "active:iss-00101",
            "reviewer_target_hash": "active:iss-00101",
            "promotion_decision": "runtime_active_selection",
        }
        try:

            def fake_close_node(req, ports):
                close_calls.append((req, ports))
                raise AssertionError("close_node must not run when transition persistence fails")

            app_issue_lifecycle.close_node = fake_close_node
            with tempfile.TemporaryDirectory() as tmp:
                repo_root = Path(tmp)
                store = _StubActiveStateStore(infra_contracts, promotion_record=runtime_record, fail_write=True)
                ports = app_ports.Ports(
                    node_reader=_StubNodeReader(),
                    repo_root=repo_root,
                    specdock_dir=repo_root / "spec-dock",
                    active_state_store=store,
                )
                with pytest.raises(RuntimeError) as raised:
                    app_issue_lifecycle.issue_finish(app_contracts.IssueFinishRequest(), ports)

            message = str(raised.value)
            assert "issue finish failed while persisting finish transition" in message
            assert "write active failed" in message
            assert len(store.write_calls) == 1
            assert len(store.restore_calls) == 1
            assert close_calls == []
            assert store.promotion_record["promotion_decision"] == "runtime_active_selection"
        finally:
            app_issue_lifecycle.close_node = original_close_node

    def test_lifecycle_authority_gate_blocks_non_finish_purposes(self) -> None:
        _app_contracts, app_issue_lifecycle, _app_ports, _domain_models, infra_contracts = _runtime_modules()
        issue_entry = infra_contracts.ActiveManifestEntry(
            id="iss-00101",
            path="spec-dock/initiatives/init-00001/epics/epic-00002/issues/iss-00101",
            authority="proposed",
            grants=(
                "review_input",
                "planning_input",
                "design_baseline",
                "implementation_start",
                "issue_ready",
                "issue_finish",
                "phase_completion",
            ),
            promotion_record={
                "status": "approved",
                "authority": "approved",
                "source_revision": "active:iss-00101",
                "approved_revision": "active:iss-00101",
                "approved_hash": "active:iss-00101",
                "reviewer_target_hash": "active:iss-00101",
                "promotion_decision": "main_orchestrator_promotion",
            },
        )

        cases = (
            ("implementation_start", "implementation start"),
            ("issue_ready", "issue ready"),
            ("phase_completion", "phase completion"),
        )
        for required_grant, command_label in cases:
            with pytest.raises(RuntimeError) as raised:
                app_issue_lifecycle.require_lifecycle_authority(
                    issue_entry,
                    required_grant=required_grant,
                    purpose=required_grant,
                    command_label=command_label,
                )
            message = str(raised.value)
            assert f"{command_label} blocked: authority gate failed" in message
            assert "authority_not_approved" in message
            assert f"required_grant: {required_grant}" in message

    def test_lifecycle_authority_gate_uses_requested_non_finish_grant(self) -> None:
        _app_contracts, app_issue_lifecycle, _app_ports, _domain_models, infra_contracts = _runtime_modules()
        issue_entry = infra_contracts.ActiveManifestEntry(
            id="iss-00101",
            path="spec-dock/initiatives/init-00001/epics/epic-00002/issues/iss-00101",
            authority="approved",
            grants=("review_input", "planning_input", "issue_finish"),
            promotion_record={
                "status": "approved",
                "authority": "approved",
                "source_revision": "active:iss-00101",
                "approved_revision": "active:iss-00101",
                "approved_hash": "active:iss-00101",
                "reviewer_target_hash": "active:iss-00101",
                "promotion_decision": "runtime_active_selection",
            },
        )

        with pytest.raises(RuntimeError) as raised:
            app_issue_lifecycle.require_lifecycle_authority(
                issue_entry,
                required_grant="phase_completion",
                purpose="phase_completion",
                command_label="phase completion",
            )

        message = str(raised.value)
        assert "phase completion blocked: authority gate failed" in message
        assert "missing_required_grant" in message
        assert "required_grant: phase_completion" in message

    def test_issue_finish_clear_active_failure_includes_recovery_guidance(self) -> None:
        app_contracts, app_issue_lifecycle, app_ports, domain_models, infra_contracts = _runtime_modules()
        original_close_node = app_issue_lifecycle.close_node
        original_clear_active = app_issue_lifecycle.clear_active
        original_post_mutation_sync = app_issue_lifecycle.post_mutation_sync
        try:
            for already_closed in (False, True):
                close_calls = []
                sync_calls = []

                def fake_close_node(req, ports, *, close_calls=close_calls, already_closed=already_closed):
                    close_calls.append((req, ports))
                    assert not req.run_post_sync
                    return app_contracts.CloseNodeResult(
                        node_id="iss-00101",
                        node_kind="issue",
                        github_issue_number=101,
                        issue_snapshot=domain_models.IssueSnapshot(
                            issue_number=101,
                            state="CLOSED",
                            title="First issue",
                            labels=[],
                            updated_at="2026-05-05T00:00:00Z",
                            url="https://github.com/example/repo/issues/101",
                        ),
                        already_closed=already_closed,
                        warnings=[],
                    )

                def fake_clear_active(req, ports):
                    del req, ports
                    raise RuntimeError("clear active failed")

                def fake_post_mutation_sync(ports, *, sync_calls=sync_calls):
                    sync_calls.append(ports)
                    return app_contracts.PostMutationSyncOutcome.skipped("test")

                app_issue_lifecycle.close_node = fake_close_node
                app_issue_lifecycle.clear_active = fake_clear_active
                app_issue_lifecycle.post_mutation_sync = fake_post_mutation_sync

                with tempfile.TemporaryDirectory() as tmp:
                    repo_root = Path(tmp)
                    ports = app_ports.Ports(
                        node_reader=_StubNodeReader(),
                        repo_root=repo_root,
                        specdock_dir=repo_root / "spec-dock",
                        active_state_store=_StubActiveStateStore(infra_contracts),
                    )
                    with pytest.raises(RuntimeError) as raised:
                        app_issue_lifecycle.issue_finish(app_contracts.IssueFinishRequest(), ports)

                message = str(raised.value)
                assert len(close_calls) == 1
                assert sync_calls == []
                assert "issue finish failed after GitHub close/already-closed step" in message
                assert "GitHub issue #101 may have been closed successfully" in message
                assert "may already have been closed" in message
                assert "Active selection was not cleared." in message
                assert "Derived artifacts may remain stale" in message
                assert "spec-dock/scripts/spec-dock active show" in message
                assert "spec-dock/scripts/spec-dock issue finish" in message
                assert "spec-dock/scripts/spec-dock active set <issue-id> --checkout" in message
                assert "manual active recovery" in message
                assert "clear active failed" in message
        finally:
            app_issue_lifecycle.close_node = original_close_node
            app_issue_lifecycle.clear_active = original_clear_active
            app_issue_lifecycle.post_mutation_sync = original_post_mutation_sync

    def test_issue_finish_suppresses_internal_close_sync_and_runs_lifecycle_sync_once(self) -> None:
        app_contracts, app_issue_lifecycle, app_ports, domain_models, infra_contracts = _runtime_modules()
        original_close_node = app_issue_lifecycle.close_node
        original_clear_active = app_issue_lifecycle.clear_active
        original_post_mutation_sync = app_issue_lifecycle.post_mutation_sync
        close_calls = []
        clear_calls = []
        sync_calls = []
        post_sync = app_contracts.PostMutationSyncOutcome.skipped("test lifecycle sync")
        try:

            def fake_close_node(req, ports):
                close_calls.append((req, ports))
                assert not req.run_post_sync
                return app_contracts.CloseNodeResult(
                    node_id="iss-00101",
                    node_kind="issue",
                    github_issue_number=101,
                    issue_snapshot=domain_models.IssueSnapshot(
                        issue_number=101,
                        state="CLOSED",
                        title="First issue",
                        labels=[],
                        updated_at="2026-05-05T00:00:00Z",
                        url="https://github.com/example/repo/issues/101",
                    ),
                    already_closed=False,
                    warnings=[],
                )

            def fake_clear_active(req, ports):
                clear_calls.append((req, ports))
                return app_contracts.ActiveClearResult(cleared=True, previous=None, warnings=[])

            def fake_post_mutation_sync(ports):
                sync_calls.append(ports)
                return post_sync

            app_issue_lifecycle.close_node = fake_close_node
            app_issue_lifecycle.clear_active = fake_clear_active
            app_issue_lifecycle.post_mutation_sync = fake_post_mutation_sync

            with tempfile.TemporaryDirectory() as tmp:
                repo_root = Path(tmp)
                ports = app_ports.Ports(
                    node_reader=_StubNodeReader(),
                    repo_root=repo_root,
                    specdock_dir=repo_root / "spec-dock",
                    active_state_store=_StubActiveStateStore(infra_contracts),
                )
                result = app_issue_lifecycle.issue_finish(app_contracts.IssueFinishRequest(), ports)

            assert len(close_calls) == 1
            assert len(clear_calls) == 1
            assert len(sync_calls) == 1
            assert result.post_sync is post_sync
            assert result.active_cleared
        finally:
            app_issue_lifecycle.close_node = original_close_node
            app_issue_lifecycle.clear_active = original_clear_active
            app_issue_lifecycle.post_mutation_sync = original_post_mutation_sync


class TestCliIssueLifecycle(CliRuntimeHarness):
    def _commit_all(self, target: Path, message: str) -> None:
        self._run_git(target, ["add", "-A"])
        self._run_git(
            target,
            ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", message],
        )

    def _prepare_clean_repo_with_two_issues(self, target: Path) -> None:
        assert main(["init", str(target)]) == 0
        self._init_origin_repo(target)
        self._run_git(
            target,
            ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
        )
        self._create_same_repo_linked_hierarchy(target, issue_issue_number=101, issue_title="First issue")
        self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Second issue", "--github-issue", "102"])
        self._commit_all(target, "spec tree")

    def _make_gh_stub(
        self,
        bin_dir: Path,
        *,
        states: dict[int, str],
        fail_view_numbers: set[int] | None = None,
        fail_close_numbers: set[int] | None = None,
    ) -> Path:
        state_path = bin_dir / "gh-state.json"
        log_path = bin_dir / "gh-calls.log"
        all_states = {1: "OPEN", 2: "OPEN", **states}
        payload = {
            str(number): {
                "number": int(number),
                "state": state,
                "title": f"Issue {number}",
                "labels": [],
                "updatedAt": "2026-05-05T00:00:00Z",
                "url": f"https://github.com/example/repo/issues/{number}",
            }
            for number, state in all_states.items()
        }
        state_path.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")
        fail_numbers = sorted(int(number) for number in (fail_view_numbers or set()))
        fail_close = sorted(int(number) for number in (fail_close_numbers or set()))
        gh_path = bin_dir / "gh"
        gh_path.write_text(
            (
                "#!/usr/bin/env python3\n"
                "import json\n"
                "import sys\n"
                "from pathlib import Path\n\n"
                f"STATE_PATH = Path({state_path.as_posix()!r})\n"
                f"LOG_PATH = Path({log_path.as_posix()!r})\n"
                f"FAIL_VIEW = {fail_numbers!r}\n"
                f"FAIL_CLOSE = {fail_close!r}\n"
                "args = sys.argv[1:]\n"
                "state = json.loads(STATE_PATH.read_text(encoding='utf-8'))\n"
                "LOG_PATH.write_text(LOG_PATH.read_text(encoding='utf-8') + ' '.join(args) + '\\n' if LOG_PATH.exists() else ' '.join(args) + '\\n', encoding='utf-8')\n"
                "if args[:2] == ['issue', 'list']:\n"
                "    print(json.dumps(list(state.values())))\n"
                "    raise SystemExit(0)\n"
                "if args[:2] == ['issue', 'view']:\n"
                "    number = int(args[2])\n"
                "    if number in FAIL_VIEW:\n"
                "        print(f'view failed: {number}', file=sys.stderr)\n"
                "        raise SystemExit(1)\n"
                "    print(json.dumps(state[str(number)]))\n"
                "    raise SystemExit(0)\n"
                "if args[:2] == ['issue', 'close']:\n"
                "    number = int(args[2])\n"
                "    if number in FAIL_CLOSE:\n"
                "        print(f'close failed: {number}', file=sys.stderr)\n"
                "        raise SystemExit(1)\n"
                "    item = state[str(number)]\n"
                "    item['state'] = 'CLOSED'\n"
                "    STATE_PATH.write_text(json.dumps(state) + '\\n', encoding='utf-8')\n"
                "    raise SystemExit(0)\n"
                "print(f'unexpected gh args: {args}', file=sys.stderr)\n"
                "raise SystemExit(99)\n"
            ),
            encoding="utf-8",
        )
        gh_path.chmod(0o755)
        return state_path

    def _active_issue_id(self, target: Path) -> str | None:
        active_path = target / "spec-dock" / ".agent" / "active.json"
        if not active_path.exists():
            return None
        active = json.loads(active_path.read_text(encoding="utf-8"))
        issue = active.get("issue")
        if not isinstance(issue, dict):
            return None
        return issue.get("id")

    def _active_issue_pointer_text(self, target: Path) -> str:
        issue_pointer = target / "spec-dock" / "active" / "issue"
        if issue_pointer.is_symlink():
            return str(issue_pointer.readlink())
        path_file = issue_pointer.with_name("issue.path")
        if path_file.is_file():
            return path_file.read_text(encoding="utf-8").strip()
        return ""

    def _active_issue_promotion_decision(self, target: Path) -> str | None:
        active_path = target / "spec-dock" / ".agent" / "active.json"
        if not active_path.exists():
            return None
        active = json.loads(active_path.read_text(encoding="utf-8"))
        issue = active.get("issue")
        if not isinstance(issue, dict):
            return None
        promotion_record = issue.get("promotion_record")
        if not isinstance(promotion_record, dict):
            return None
        value = promotion_record.get("promotion_decision")
        return value if isinstance(value, str) else None

    def test_issue_start_sets_active_and_checks_out_issue_branch(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["issue", "start", "--id", "iss-00101"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok (issue start)" in p.stdout
            assert "issue=iss-00101" in p.stdout
            assert "spec-dock: ok (issue checkout) branch=iss-00101-first-issue" in p.stdout
            assert self._active_issue_id(target) == "iss-00101"
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            issue = active["issue"]
            assert issue["authority"] == "approved"
            assert "issue_finish" in issue["grants"]
            assert issue["promotion_record"]["approved_hash"] == issue["promotion_record"]["reviewer_target_hash"]
            context_pack = (target / "spec-dock" / "active" / "context-pack.md").read_text(encoding="utf-8")
            assert "- issue: authority=approved" in context_pack
            assert "issue ready" in context_pack
            assert "issue_finish" in context_pack
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "iss-00101-first-issue"

    def test_issue_start_rejects_non_issue_node(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["issue", "start", "--id", "epic-00002"], env=test_env)
            assert p.returncode != 0, p.stdout + p.stderr
            assert "issue start only accepts issue nodes" in p.stderr
            assert self._active_issue_id(target) is None

    def test_issue_start_blocks_different_open_issue_from_active_issue_branch(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["issue", "start", "101"], env=test_env)
            before = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")
            before_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()

            p = self._run_runtime_capture(target, ["issue", "start", "102"], env=test_env)
            assert p.returncode != 0, p.stdout + p.stderr
            assert "issue start blocked: unfinished active issue branch" in p.stderr
            assert "current active issue: iss-00101" in p.stderr
            assert "current branch: iss-00101-first-issue" in p.stderr
            assert "requested issue: iss-00102" in p.stderr
            assert "github state: OPEN" in p.stderr
            assert "issue finish" in p.stderr
            assert "issue start iss-00102 -f" in p.stderr
            assert "active set iss-00102 --checkout" in p.stderr
            assert (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8") == before
            after_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert after_branch == before_branch

    def test_direct_active_set_checkout_bypasses_issue_lifecycle_guard(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00102-second-issue"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta.pop("github", None)
            self._write_json_force(issue_meta, meta)
            self._commit_all(target, "make second issue locally ready")
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["issue", "start", "101"], env=test_env)
            self._commit_all(target, "active first issue")
            active_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert active_branch == "iss-00101-first-issue"
            assert self._active_issue_id(target) == "iss-00101"

            p = self._run_runtime_capture(target, ["active", "set", "iss-00102", "--checkout"])

            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok (active set)" in p.stdout
            assert "issue start blocked" not in p.stderr
            assert self._active_issue_id(target) == "iss-00102"
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "iss-00102-second-issue"

    def test_issue_start_allows_different_issue_from_closed_active_issue_branch(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["issue", "start", "101"], env=test_env)
            self._commit_all(target, "active closed issue")
            active_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert active_branch == "iss-00101-first-issue"
            assert self._active_issue_id(target) == "iss-00101"
            self._make_gh_stub(bin_dir, states={101: "CLOSED", 102: "OPEN"})

            p = self._run_runtime_capture(target, ["issue", "start", "102"], env=test_env)

            assert p.returncode == 0, p.stdout + p.stderr
            assert "issue start blocked" not in p.stderr
            assert "spec-dock: ok (issue start)" in p.stdout
            assert "issue=iss-00102" in p.stdout
            assert self._active_issue_id(target) == "iss-00102"
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "iss-00102-second-issue"

    def test_issue_start_blocks_when_active_issue_github_state_unknown(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["issue", "start", "101"], env=test_env)
            before = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")
            before_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()

            unknown_bin_dir = Path(bin_tmp)
            self._make_gh_stub(unknown_bin_dir, states={101: "OPEN", 102: "OPEN"}, fail_view_numbers={101})
            p = self._run_runtime_capture(target, ["issue", "start", "102"], env=test_env)

            assert p.returncode != 0, p.stdout + p.stderr
            assert "issue start blocked: unfinished active issue branch" in p.stderr
            assert "github state: UNKNOWN" in p.stderr
            assert "Next commands:" in p.stderr
            assert "spec-dock/scripts/spec-dock issue finish" in p.stderr
            assert "spec-dock/scripts/spec-dock issue start iss-00102 -f" in p.stderr
            assert "spec-dock/scripts/spec-dock active set iss-00102 --checkout" in p.stderr
            assert (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8") == before
            after_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert after_branch == before_branch

    def test_issue_start_force_bypasses_only_lifecycle_guard_not_dependency_guard(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00102-second-issue"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["depends_on"] = ["iss-00101"]
            self._write_json_force(issue_meta, meta)
            self._commit_all(target, "add dependency")

            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["issue", "start", "101"], env=test_env)
            self._commit_all(target, "active first issue")

            p = self._run_runtime_capture(target, ["issue", "start", "102", "-f"], env=test_env)
            assert p.returncode != 0, p.stdout + p.stderr
            assert "active set blocked" in p.stderr
            assert "spec-dock: ok (issue start)" not in p.stdout
            assert self._active_issue_id(target) == "iss-00101"
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "iss-00101-first-issue"

    def test_issue_start_force_does_not_bypass_node_level_dependency_guard(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "1", "--title", "Empty blocker", "--github-issue", "202"],
            )
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00102-second-issue"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["depends_on"] = ["epic-00202"]
            self._write_json_force(issue_meta, meta)
            self._commit_all(target, "add node dependency")

            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN", 202: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["issue", "start", "101"], env=test_env)
            self._commit_all(target, "active first issue")

            p = self._run_runtime_capture(target, ["issue", "start", "102", "--force"], env=test_env)
            assert p.returncode != 0, p.stdout + p.stderr
            assert "active set blocked" in p.stderr
            assert "epic-00202" in p.stderr
            assert "spec-dock: ok (issue start)" not in p.stdout
            assert self._active_issue_id(target) == "iss-00101"
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "iss-00101-first-issue"

    def test_issue_start_rejects_legacy_force_short_options(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            uppercase = self._run_runtime_capture(target, ["issue", "start", "102", "-F"])
            old_t = self._run_runtime_capture(target, ["issue", "start", "102", "-t"])

            assert uppercase.returncode != 0, uppercase.stdout + uppercase.stderr
            assert "unrecognized arguments: -F" in uppercase.stderr
            assert old_t.returncode != 0, old_t.stdout + old_t.stderr
            assert "unrecognized arguments: -t" in old_t.stderr

    def test_issue_start_force_switches_when_dependency_ready_and_warns(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["issue", "start", "101"], env=test_env)
            self._commit_all(target, "active first issue")

            p = self._run_runtime_capture(target, ["issue", "start", "--github-issue", "102", "--force"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok (issue start)" in p.stdout
            assert "issue=iss-00102" in p.stdout
            assert "issue start forced=true" in p.stderr
            assert self._active_issue_id(target) == "iss-00102"
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "iss-00102-second-issue"

    def test_issue_start_from_main_and_same_issue_restart_do_not_trigger_guard(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            initial_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()

            first = self._run_runtime_capture(target, ["issue", "start", "101"], env=test_env)
            assert first.returncode == 0, first.stdout + first.stderr
            self._commit_all(target, "active first issue")
            issue_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            same = self._run_runtime_capture(target, ["issue", "start", "101"], env=test_env)
            assert same.returncode == 0, same.stdout + same.stderr
            assert "issue start blocked" not in same.stderr
            same_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert same_branch == issue_branch
            self._commit_all(target, "same issue restart")

            self._run_git(target, ["checkout", initial_branch])
            main_start = self._run_runtime_capture(target, ["issue", "start", "102"], env=test_env)
            assert main_start.returncode == 0, main_start.stdout + main_start.stderr
            assert "issue start blocked" not in main_start.stderr
            assert self._active_issue_id(target) == "iss-00102"

    def test_issue_start_from_non_issue_branch_allows_switching_open_active_issue(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            first = self._run_runtime_capture(target, ["issue", "start", "101"], env=test_env)
            assert first.returncode == 0, first.stdout + first.stderr
            self._commit_all(target, "active first issue")
            self._run_git(target, ["checkout", "-b", "maintenance-check"])

            p = self._run_runtime_capture(target, ["issue", "start", "102"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr
            assert "issue start blocked" not in p.stderr
            assert "spec-dock: ok (issue start)" in p.stdout
            assert self._active_issue_id(target) == "iss-00102"
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "iss-00102-second-issue"

    def test_issue_start_then_finish_closes_open_issue_and_clears_active(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            state_path = self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            started = self._run_runtime_capture(target, ["issue", "start", "--id", "iss-00101"], env=test_env)
            assert started.returncode == 0, started.stdout + started.stderr
            assert "spec-dock: ok (issue start)" in started.stdout
            assert "issue=iss-00101" in started.stdout
            assert "spec-dock: ok (issue checkout) branch=iss-00101-first-issue" in started.stdout
            assert self._active_issue_id(target) == "iss-00101"
            assert self._active_issue_promotion_decision(target) == "runtime_active_selection"
            started_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert started_branch == "iss-00101-first-issue"
            list_count_before_finish = (bin_dir / "gh-calls.log").read_text(encoding="utf-8").count("issue list")

            finished = self._run_runtime_capture(target, ["issue", "finish"], env=test_env)

            assert finished.returncode == 0, finished.stdout + finished.stderr
            assert "spec-dock: ok (issue finish)" in finished.stdout
            assert "issue=iss-00101" in finished.stdout
            assert "github=#101" in finished.stdout
            assert "active_cleared=true" in finished.stdout
            assert "already_closed=false" in finished.stdout
            assert self._active_issue_id(target) is None
            assert "system/active-none/issue" in self._active_issue_pointer_text(target)
            finished_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert finished_branch == "iss-00101-first-issue"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            assert state["101"]["state"] == "CLOSED"
            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            assert index_all["nodes"]["iss-00101"]["status"] == "done"
            log = (bin_dir / "gh-calls.log").read_text(encoding="utf-8")
            assert log.count("issue list") == list_count_before_finish + 1

    def test_issue_finish_closes_open_issue_and_clears_active(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=101, issue_title="First issue")
            self._run_runtime(target, ["active", "set", "--id", "iss-00101", "--force"])
            assert self._active_issue_promotion_decision(target) == "runtime_active_selection"
            bin_dir = Path(bin_tmp)
            state_path = self._make_gh_stub(bin_dir, states={101: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["issue", "finish"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok (issue finish)" in p.stdout
            assert "issue=iss-00101" in p.stdout
            assert "github=#101" in p.stdout
            assert "active_cleared=true" in p.stdout
            assert "already_closed=false" in p.stdout
            assert self._active_issue_id(target) is None
            state = json.loads(state_path.read_text(encoding="utf-8"))
            assert state["101"]["state"] == "CLOSED"

    def test_issue_finish_active_set_synthetic_approval_closes_open_issue_and_clears_active(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=101, issue_title="First issue")
            self._run_runtime(target, ["active", "set", "--id", "iss-00101", "--force"])
            bin_dir = Path(bin_tmp)
            state_path = self._make_gh_stub(bin_dir, states={101: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["issue", "finish"], env=test_env)

            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok (issue finish)" in p.stdout
            assert "issue=iss-00101" in p.stdout
            assert "github=#101" in p.stdout
            assert "active_cleared=true" in p.stdout
            assert "already_closed=false" in p.stdout
            assert self._active_issue_id(target) is None
            state = json.loads(state_path.read_text(encoding="utf-8"))
            assert state["101"]["state"] == "CLOSED"

    def test_issue_finish_already_closed_clears_active(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=101, issue_title="First issue")
            self._run_runtime(target, ["active", "set", "--id", "iss-00101", "--force"])
            assert self._active_issue_promotion_decision(target) == "runtime_active_selection"
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "CLOSED"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["issue", "finish"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr
            assert "already_closed=true" in p.stdout
            assert self._active_issue_id(target) is None
            assert "system/active-none/issue" in self._active_issue_pointer_text(target)
            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            assert index_all["nodes"]["iss-00101"]["status"] == "done"
            log = (bin_dir / "gh-calls.log").read_text(encoding="utf-8")
            assert log.count("issue list") == 1

    def test_issue_finish_failures_leave_active_unchanged(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            no_active = self._run_runtime_capture(target, ["issue", "finish"])
            assert no_active.returncode != 0, no_active.stdout + no_active.stderr
            assert "issue finish requires an active issue" in no_active.stderr
            assert "Recovery:" in no_active.stderr
            assert "issue start <issue>" in no_active.stderr
            assert "active set <issue> --checkout" in no_active.stderr
            assert self._active_issue_id(target) is None

            self._create_same_repo_linked_hierarchy(target, issue_issue_number=101, issue_title="First issue")
            linked_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00101-first-issue"
                / ".meta.json"
            )
            linked_meta = json.loads(linked_meta_path.read_text(encoding="utf-8"))
            unlinked_meta = dict(linked_meta)
            unlinked_meta.pop("github", None)
            self._write_json_force(linked_meta_path, unlinked_meta)
            self._run_runtime(target, ["active", "set", "--id", "iss-00101", "--force"])
            assert self._active_issue_promotion_decision(target) == "runtime_active_selection"
            no_link = self._run_runtime_capture(target, ["issue", "finish"])
            assert no_link.returncode != 0, no_link.stdout + no_link.stderr
            assert "issue finish failed while closing GitHub issue" in no_link.stderr
            assert "Active selection was not cleared." in no_link.stderr
            assert "Recovery:" in no_link.stderr
            assert "spec-dock/scripts/spec-dock issue finish" in no_link.stderr
            assert "spec-dock/scripts/spec-dock active show" in no_link.stderr
            assert "Node is not linked to a GitHub issue" in no_link.stderr
            assert self._active_issue_id(target) == "iss-00101"
            assert self._active_issue_promotion_decision(target) == "issue_finish_lifecycle_transition"

            active_path = target / "spec-dock" / ".agent" / "active.json"
            stale_active = json.loads(active_path.read_text(encoding="utf-8"))
            stale_active["issue"]["id"] = "iss-00999"
            self._write_json_force(active_path, stale_active)
            node_not_found = self._run_runtime_capture(target, ["issue", "finish"])
            assert node_not_found.returncode != 0, node_not_found.stdout + node_not_found.stderr
            assert "issue finish blocked: authority gate failed" in node_not_found.stderr
            assert "promotion_record_not_bound_to_active_entry" in node_not_found.stderr
            assert "required_grant: issue_finish" in node_not_found.stderr
            assert "Recovery:" in node_not_found.stderr
            assert "obtain a fresh approved promotion record" in node_not_found.stderr
            assert "issue start <issue>" not in node_not_found.stderr
            assert "expected_revision=active:iss-00999" in node_not_found.stderr
            assert self._active_issue_id(target) == "iss-00999"

            self._write_json_force(linked_meta_path, linked_meta)
            self._run_runtime(target, ["active", "set", "--id", "iss-00101", "--force"])
            assert self._active_issue_promotion_decision(target) == "runtime_active_selection"
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN"}, fail_view_numbers={101})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            close_failure = self._run_runtime_capture(target, ["issue", "finish"], env=test_env)
            assert close_failure.returncode != 0, close_failure.stdout + close_failure.stderr
            assert "issue finish failed while closing GitHub issue" in close_failure.stderr
            assert "Active selection was not cleared." in close_failure.stderr
            assert "Recovery:" in close_failure.stderr
            assert "spec-dock/scripts/spec-dock issue finish" in close_failure.stderr
            assert "spec-dock/scripts/spec-dock active show" in close_failure.stderr
            assert "view failed: 101" in close_failure.stderr
            assert self._active_issue_id(target) == "iss-00101"
            assert self._active_issue_promotion_decision(target) == "issue_finish_lifecycle_transition"
            assert "issue list" not in (bin_dir / "gh-calls.log").read_text(encoding="utf-8")

            self._make_gh_stub(bin_dir, states={101: "OPEN"}, fail_close_numbers={101})
            close_command_failure = self._run_runtime_capture(target, ["issue", "finish"], env=test_env)
            assert close_command_failure.returncode != 0, close_command_failure.stdout + close_command_failure.stderr
            assert "issue finish failed while closing GitHub issue" in close_command_failure.stderr
            assert "Active selection was not cleared." in close_command_failure.stderr
            assert "Recovery:" in close_command_failure.stderr
            assert "spec-dock/scripts/spec-dock issue finish" in close_command_failure.stderr
            assert "spec-dock/scripts/spec-dock active show" in close_command_failure.stderr
            assert "close failed: 101" in close_command_failure.stderr
            assert self._active_issue_id(target) == "iss-00101"
            assert self._active_issue_promotion_decision(target) == "issue_finish_lifecycle_transition"
            assert "issue list" not in (bin_dir / "gh-calls.log").read_text(encoding="utf-8")
