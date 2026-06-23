from pathlib import Path
import sys
import tempfile


def _authority_module():
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
        from spec_dock_runtime.domain import authority
    finally:
        sys.path.pop(0)
    return authority


class TestAuthorityGate:
    def _approved_record(self):
        authority = _authority_module()
        return authority.approved_runtime_promotion_record(node_id="iss-00101")

    def _approved_lifecycle_record(self):
        record = self._approved_record()
        record["promotion_decision"] = "main_orchestrator_promotion"
        return record

    def test_approved_authority_with_exact_grant_passes(self) -> None:
        authority = _authority_module()
        result = authority.evaluate_authority_gate(
            authority="approved",
            grants=authority.approved_runtime_grants(),
            promotion_record=self._approved_lifecycle_record(),
            required_grant="issue_finish",
            purpose="issue_finish",
        )
        assert result.ok
        assert result.reason == "ok"

    def test_active_synthetic_approval_cannot_satisfy_lifecycle_grants(self) -> None:
        authority = _authority_module()
        for grant in ("implementation_start", "issue_ready", "issue_finish", "phase_completion"):
            case = f"grant={grant}"
            result = authority.evaluate_authority_gate(
                authority="approved",
                grants=authority.approved_runtime_grants(),
                promotion_record=self._approved_record(),
                required_grant=grant,
                purpose=grant,
            )
            assert not result.ok, case
            assert result.reason == "active_synthetic_approval_not_lifecycle_approval", case

    def test_active_synthetic_approval_can_satisfy_input_grants(self) -> None:
        authority = _authority_module()
        for grant in ("review_input", "planning_input", "design_baseline"):
            case = f"grant={grant}"
            result = authority.evaluate_authority_gate(
                authority="approved",
                grants=authority.approved_runtime_grants(),
                promotion_record=self._approved_record(),
                required_grant=grant,
                purpose=grant,
            )
            assert result.ok, case
            assert result.reason == "ok", case

    def test_issue_finish_transition_helpers_are_finish_scoped_and_bound(self) -> None:
        authority = _authority_module()

        record = authority.approved_issue_finish_transition_promotion_record(node_id="iss-00101")

        assert record["status"] == "approved"
        assert record["authority"] == "approved"
        assert record["promotion_decision"] == "issue_finish_lifecycle_transition"
        for field in ("source_revision", "approved_revision", "approved_hash", "reviewer_target_hash"):
            assert record[field] == "active:iss-00101", f"field={field}"
        assert authority.approved_issue_finish_transition_grants() == (
            "review_input",
            "planning_input",
            "design_baseline",
            "issue_finish",
        )

    def test_issue_finish_transition_token_only_satisfies_issue_finish(self) -> None:
        authority = _authority_module()

        finish_result = authority.evaluate_authority_gate(
            authority="approved",
            grants=authority.approved_issue_finish_transition_grants(),
            promotion_record=authority.approved_issue_finish_transition_promotion_record(node_id="iss-00101"),
            required_grant="issue_finish",
            purpose="issue_finish",
        )

        assert finish_result.ok
        assert finish_result.reason == "ok"

        for grant in ("implementation_start", "issue_ready", "phase_completion"):
            case = f"grant={grant}"
            result = authority.evaluate_authority_gate(
                authority="approved",
                grants=authority.approved_issue_finish_transition_grants(),
                promotion_record=authority.approved_issue_finish_transition_promotion_record(node_id="iss-00101"),
                required_grant=grant,
                purpose=grant,
            )
            assert not result.ok, case
            assert result.reason in ("finish_transition_not_valid_for_required_grant", "missing_required_grant"), case

    def test_missing_authority_metadata_fails_closed(self) -> None:
        authority = _authority_module()
        result = authority.evaluate_authority_gate(
            authority=None,
            grants=authority.approved_runtime_grants(),
            promotion_record=self._approved_record(),
            required_grant="issue_finish",
            purpose="issue_finish",
        )
        assert not result.ok
        assert result.reason == "missing_authority"

    def test_proposed_authority_cannot_satisfy_lifecycle_grant(self) -> None:
        authority = _authority_module()
        result = authority.evaluate_authority_gate(
            authority="proposed",
            grants=authority.approved_runtime_grants(),
            promotion_record=self._approved_record(),
            required_grant="implementation_start",
            purpose="implementation_start",
        )
        assert not result.ok
        assert result.reason == "authority_not_approved"

    def test_missing_exact_grant_fails_closed(self) -> None:
        authority = _authority_module()
        result = authority.evaluate_authority_gate(
            authority="approved",
            grants=("review_input", "planning_input"),
            promotion_record=self._approved_record(),
            required_grant="issue_finish",
            purpose="issue_finish",
        )
        assert not result.ok
        assert result.reason == "missing_required_grant"

    def test_wildcard_grant_fails_closed(self) -> None:
        authority = _authority_module()
        result = authority.evaluate_authority_gate(
            authority="approved",
            grants=("review_input", "grants.*"),
            promotion_record=self._approved_record(),
            required_grant="review_input",
            purpose="review_input",
        )
        assert not result.ok
        assert result.reason == "invalid_grants"

    def test_stale_promotion_record_fails_closed(self) -> None:
        authority = _authority_module()
        record = self._approved_record()
        record["reviewer_target_hash"] = "stale"
        result = authority.evaluate_authority_gate(
            authority="approved",
            grants=authority.approved_runtime_grants(),
            promotion_record=record,
            required_grant="issue_finish",
            purpose="issue_finish",
        )
        assert not result.ok
        assert result.reason == "stale_promotion_hash"

    def test_missing_promotion_decision_fails_closed(self) -> None:
        authority = _authority_module()
        record = self._approved_record()
        del record["promotion_decision"]
        result = authority.evaluate_authority_gate(
            authority="approved",
            grants=authority.approved_runtime_grants(),
            promotion_record=record,
            required_grant="issue_finish",
            purpose="issue_finish",
        )
        assert not result.ok
        assert result.reason == "incomplete_promotion_record"
        assert "missing=promotion_decision" in result.details

    def test_stale_promotion_revision_fails_closed(self) -> None:
        authority = _authority_module()
        record = self._approved_record()
        record["approved_revision"] = "stale"
        result = authority.evaluate_authority_gate(
            authority="approved",
            grants=authority.approved_runtime_grants(),
            promotion_record=record,
            required_grant="issue_finish",
            purpose="issue_finish",
        )
        assert not result.ok
        assert result.reason == "stale_promotion_revision"

    def test_promotion_record_must_match_expected_active_revision(self) -> None:
        authority = _authority_module()
        result = authority.evaluate_authority_gate(
            authority="approved",
            grants=authority.approved_runtime_grants(),
            promotion_record=self._approved_lifecycle_record(),
            required_grant="issue_finish",
            purpose="issue_finish",
            expected_revision="active:iss-00999",
        )
        assert not result.ok
        assert result.reason == "promotion_record_not_bound_to_active_entry"

    def test_issue_finish_transition_record_must_match_expected_active_revision(self) -> None:
        authority = _authority_module()

        revision_result = authority.evaluate_authority_gate(
            authority="approved",
            grants=authority.approved_issue_finish_transition_grants(),
            promotion_record=authority.approved_issue_finish_transition_promotion_record(node_id="iss-00101"),
            required_grant="issue_finish",
            purpose="issue_finish",
            expected_revision="active:iss-00999",
        )
        assert not revision_result.ok
        assert revision_result.reason == "promotion_record_not_bound_to_active_entry"

        record = authority.approved_issue_finish_transition_promotion_record(node_id="iss-00101")
        record["approved_hash"] = "active:iss-00999"
        record["reviewer_target_hash"] = "active:iss-00999"
        hash_result = authority.evaluate_authority_gate(
            authority="approved",
            grants=authority.approved_issue_finish_transition_grants(),
            promotion_record=record,
            required_grant="issue_finish",
            purpose="issue_finish",
            expected_revision="active:iss-00101",
        )
        assert not hash_result.ok
        assert hash_result.reason == "promotion_hash_not_bound_to_active_entry"

    def test_draft_artifact_metadata_requires_all_delegated_authoring_fields(self) -> None:
        authority = _authority_module()
        metadata = self._approved_artifact_metadata(authority)
        del metadata["manifest_hash"]

        result = authority.validate_draft_artifact_metadata(metadata)

        assert not result.ok
        assert result.reason == "incomplete_draft_metadata"
        assert "missing=manifest_hash" in result.details

    def test_proposed_artifact_metadata_cannot_authorize_implementation(self) -> None:
        authority = _authority_module()
        metadata = self._approved_artifact_metadata(authority)
        metadata["status"] = "draft"
        metadata["authority"] = "proposed"

        result = authority.validate_draft_artifact_metadata(metadata)

        assert not result.ok
        assert result.reason == "authority_not_approved"

    def test_approved_authority_requires_approved_status(self) -> None:
        authority = _authority_module()
        metadata = self._approved_artifact_metadata(authority)
        metadata["status"] = "draft"

        result = authority.validate_draft_artifact_metadata(metadata)

        assert not result.ok
        assert result.reason == "status_not_approved"
        assert "status=draft" in result.details

    def test_approved_artifact_requires_positive_probe_result(self) -> None:
        authority = _authority_module()
        metadata = self._approved_artifact_metadata(authority)
        del metadata["positive_probe_result"]

        result = authority.validate_draft_artifact_metadata(metadata, purpose="implementation_start")

        assert not result.ok
        assert result.reason == "incomplete_draft_metadata"
        assert "missing=positive_probe_result" in result.details

    def test_approved_artifact_rejects_non_pass_positive_probe_result(self) -> None:
        authority = _authority_module()
        for probe_result in ("fail", "failed", ""):
            case = f"positive_probe_result={probe_result!r}"
            metadata = self._approved_artifact_metadata(authority)
            metadata["positive_probe_result"] = probe_result

            result = authority.validate_draft_artifact_metadata(metadata, purpose="implementation_start")

            assert not result.ok, case
            assert result.reason == "positive_probe_not_passed", case
            assert f"positive_probe_result={probe_result}" in result.details, case

    def test_approved_artifact_accepts_pass_positive_probe_result(self) -> None:
        authority = _authority_module()
        metadata = self._approved_artifact_metadata(authority)
        metadata["positive_probe_result"] = "pass"

        result = authority.validate_draft_artifact_metadata(metadata, purpose="implementation_start")

        assert result.ok
        assert result.reason == "ok"

    def test_approved_artifact_requires_exact_grants_and_promotion_record(self) -> None:
        authority = _authority_module()
        metadata = self._approved_artifact_metadata(authority)
        metadata["grants"] = ["review_input", "planning_input"]

        result = authority.validate_draft_artifact_metadata(metadata)

        assert not result.ok
        assert result.reason == "missing_required_grant"

        metadata = self._approved_artifact_metadata(authority)
        del metadata["promotion_record"]
        result = authority.validate_draft_artifact_metadata(metadata)
        assert not result.ok
        assert result.reason == "missing_promotion_record"

    def test_active_synthetic_approval_is_not_artifact_approval(self) -> None:
        authority = _authority_module()
        metadata = self._approved_artifact_metadata(authority)
        metadata["promotion_record"] = authority.approved_runtime_promotion_record(node_id="iss-00101")

        result = authority.validate_draft_artifact_metadata(metadata)

        assert not result.ok
        assert result.reason == "active_synthetic_approval_not_artifact_approval"

    def test_unresolved_evidence_adoption_ledger_blocks_lifecycle_purposes(self) -> None:
        authority = _authority_module()
        entries = [
            {
                "id": "EAL-009",
                "adoption_status": "blocked",
                "target_artifact": "design.md",
                "next_action": "resolve reviewer evidence",
            }
        ]

        for purpose in ("draft_promotion", "implementation_start", "issue_ready", "issue_finish", "phase_completion"):
            case = f"purpose={purpose}"
            result = authority.evaluate_evidence_adoption_ledger_gate(
                entries,
                target_artifact="design.md",
                purpose=purpose,
            )
            assert not result.ok, case
            assert result.reason == "evidence_ledger_blocked", case
            assert result.blocking_entry_id == "EAL-009", case
            assert result.required_next_action == "resolve reviewer evidence", case

    def test_stale_evidence_adoption_ledger_returns_blocking_entry_id(self) -> None:
        authority = _authority_module()
        result = authority.evaluate_evidence_adoption_ledger_gate(
            [{"id": "EAL-010", "adoption_status": "stale", "target_artifact": "plan.md"}],
            target_artifact="plan.md",
            purpose="issue_finish",
        )

        assert not result.ok
        assert result.reason == "evidence_ledger_stale"
        assert result.blocking_entry_id == "EAL-010"

    def test_delegated_markdown_artifact_with_proposed_authority_is_blocked(self) -> None:
        authority = _authority_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "design.md"
            path.write_text(
                "\n".join(
                    [
                        "---",
                        "status: draft",
                        "authority: proposed",
                        "grants: [review_input, planning_input]",
                        "owner_role: main-orchestrator",
                        "draft_author_role: system-architect",
                        "approval: pending-main-promotion",
                        "source_revision: rev-1",
                        "approved_revision: rev-1",
                        "approved_hash: hash-1",
                        "manifest_hash: manifest-hash",
                        "permission_profile_name: spec-dock-da",
                        "permission_profile_hash: profile-hash",
                        "write_session_invocation_hash: session-hash",
                        "probe_run_id: probe-1",
                        "positive_probe_result: pass",
                        "---",
                        "# Design",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = authority.validate_delegated_authority_artifact(path, purpose="implementation_start")

        assert not result.ok
        assert result.reason == "authority_not_approved"
        assert "purpose=implementation_start" in result.details

    def test_delegated_bottom_metadata_with_proposed_authority_is_blocked_for_downstream_purposes(self) -> None:
        authority = _authority_module()
        downstream_purposes = (
            "implementation_start",
            "issue_ready",
            "issue_finish",
            "phase_completion",
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plan.md"
            path.write_text(
                "\n".join(
                    [
                        "# Plan",
                        "",
                        "## Implementation",
                        "",
                        "- ordinary content",
                        "",
                        "## Delegated Draft Pilot Metadata",
                        "",
                        "- status=approved",
                        "- authority=proposed",
                        "- grants=review_input,planning_input",
                        "- owner_role=main-orchestrator",
                        "- draft_author_role=implementation-planner",
                        "- approval=pending-main-promotion",
                        "- source_revision=rev-1",
                        "- approved_revision=none",
                        "- approved_hash=none",
                        "- manifest_hash=manifest-hash",
                        "- permission_profile_name=spec-dock-da",
                        "- permission_profile_hash=profile-hash",
                        "- write_session_invocation_hash=session-hash",
                        "- probe_run_id=probe-1",
                        "- positive_probe_result=pass",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            metadata = authority.delegated_authority_metadata_from_markdown(path)
            assert metadata is not None
            assert metadata["authority"] == "proposed"
            assert metadata["grants"] == ["review_input", "planning_input"]
            for purpose in downstream_purposes:
                case = f"purpose={purpose}"
                result = authority.validate_delegated_authority_artifact(path, purpose=purpose)
                assert not result.ok, case
                assert result.reason == "authority_not_approved", case
                assert f"purpose={purpose}" in result.details, case

    def test_approved_bottom_metadata_with_dotted_promotion_record_authorizes_implementation_start(self) -> None:
        authority = _authority_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plan.md"
            path.write_text(
                "\n".join(
                    [
                        "# Plan",
                        "",
                        "## Delegated Draft Pilot Metadata",
                        "",
                        "- status=approved",
                        "- authority=approved",
                        "- grants=implementation_start,issue_ready,issue_finish,phase_completion",
                        "- owner_role=main-orchestrator",
                        "- draft_author_role=implementation-planner",
                        "- approval=fresh-reviewer-pass",
                        "- source_revision=rev-1",
                        "- approved_revision=rev-1",
                        "- approved_hash=hash-1",
                        "- manifest_hash=manifest-hash",
                        "- permission_profile_name=spec-dock-da",
                        "- permission_profile_hash=profile-hash",
                        "- write_session_invocation_hash=session-hash",
                        "- probe_run_id=probe-1",
                        "- positive_probe_result=pass",
                        "- promotion_record.status=approved",
                        "- promotion_record.authority=approved",
                        "- promotion_record.source_revision=rev-1",
                        "- promotion_record.approved_revision=rev-1",
                        "- promotion_record.approved_hash=hash-1",
                        "- promotion_record.reviewer_target_hash=hash-1",
                        "- promotion_record.promotion_decision=fresh_reviewer_promotion",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            metadata = authority.delegated_authority_metadata_from_markdown(path)
            assert metadata is not None
            assert isinstance(metadata["promotion_record"], dict)
            assert metadata["promotion_record"]["status"] == "approved"
            result = authority.validate_delegated_authority_artifact(path, purpose="implementation_start")

        assert result.ok
        assert result.reason == "ok"

    def test_artifact_metadata_uses_purpose_specific_lifecycle_grant(self) -> None:
        authority = _authority_module()
        metadata = self._approved_artifact_metadata(authority)
        metadata["grants"] = ["issue_finish"]

        finish_result = authority.validate_draft_artifact_metadata(metadata, purpose="issue_finish")
        implementation_result = authority.validate_draft_artifact_metadata(
            metadata,
            purpose="implementation_start",
        )

        assert finish_result.ok
        assert finish_result.reason == "ok"
        assert not implementation_result.ok
        assert implementation_result.reason == "missing_required_grant"

    def test_evidence_ledger_gate_normalizes_markdown_code_span_statuses(self) -> None:
        authority = _authority_module()
        entries = [
            {
                "id": "`EAL-777`",
                "adoption_status": "`blocked`",
                "target_artifact": "`design.md`",
                "next_action": "`resolve reviewer evidence`",
            }
        ]

        result = authority.evaluate_evidence_adoption_ledger_gate(
            entries,
            target_artifact="design.md",
            purpose="validate",
        )

        assert not result.ok
        assert result.reason == "evidence_ledger_blocked"
        assert result.blocking_entry_id == "EAL-777"
        assert result.required_next_action == "resolve reviewer evidence"

    def test_proposed_bottom_metadata_with_downstream_grants_remains_non_authoritative(self) -> None:
        authority = _authority_module()
        downstream_purposes = (
            "implementation_start",
            "issue_ready",
            "issue_finish",
            "phase_completion",
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plan.md"
            path.write_text(
                "\n".join(
                    [
                        "# Plan",
                        "",
                        "## Delegated Draft Pilot Metadata",
                        "",
                        "- status=draft",
                        "- authority=proposed",
                        "- grants=implementation_start,issue_ready,issue_finish,phase_completion",
                        "- owner_role=main-orchestrator",
                        "- draft_author_role=implementation-planner",
                        "- approval=pending-main-promotion",
                        "- source_revision=rev-1",
                        "- approved_revision=none",
                        "- approved_hash=none",
                        "- manifest_hash=manifest-hash",
                        "- permission_profile_name=spec-dock-da",
                        "- permission_profile_hash=profile-hash",
                        "- write_session_invocation_hash=session-hash",
                        "- probe_run_id=probe-1",
                        "- positive_probe_result=pass",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            for purpose in downstream_purposes:
                case = f"purpose={purpose}"
                result = authority.validate_delegated_authority_artifact(path, purpose=purpose)
                assert not result.ok, case
                assert result.reason == "authority_not_approved", case
                assert f"purpose={purpose}" in result.details, case

    def test_delegated_markdown_artifact_with_missing_metadata_is_blocked(self) -> None:
        authority = _authority_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plan.md"
            path.write_text(
                "---\nauthority: approved\nmanifest_hash: manifest-hash\n---\n# Plan\n",
                encoding="utf-8",
            )

            result = authority.validate_delegated_authority_artifact(path, purpose="validate")

        assert not result.ok
        assert result.reason == "incomplete_draft_metadata"
        assert "missing=status" in result.details

    def test_non_utf8_delegated_markdown_artifact_is_structured_gate_failure(self) -> None:
        authority = _authority_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plan.md"
            path.write_bytes(b"---\nauthority: approved\n---\n# invalid \xff\n")

            result = authority.validate_delegated_authority_artifact(path, purpose="issue_finish")

        assert not result.ok
        assert result.reason == "delegated_authority_artifact_non_utf8"
        assert "purpose=issue_finish" in result.details
        assert f"path={path.as_posix()}" in result.details

    def _approved_artifact_metadata(self, authority):
        return {
            "status": "approved",
            "authority": "approved",
            "grants": ["implementation_start"],
            "owner_role": "main-orchestrator",
            "draft_author_role": "system-architect",
            "approval": "fresh-reviewer-pass",
            "source_revision": "rev-1",
            "approved_revision": "rev-1",
            "approved_hash": "hash-1",
            "manifest_hash": "manifest-hash",
            "permission_profile_name": "spec-dock-da",
            "permission_profile_hash": "profile-hash",
            "write_session_invocation_hash": "session-hash",
            "probe_run_id": "probe-1",
            "positive_probe_result": "pass",
            "promotion_record": {
                "status": "approved",
                "authority": "approved",
                "source_revision": "rev-1",
                "approved_revision": "rev-1",
                "approved_hash": "hash-1",
                "reviewer_target_hash": "hash-1",
                "promotion_decision": "fresh_reviewer_promotion",
            },
        }
