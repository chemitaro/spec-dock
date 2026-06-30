from pathlib import Path
import sys


def _workflow_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.domain import runbook, workflow_state
    finally:
        sys.path.pop(0)
    return runbook, workflow_state


def test_lite_candidate_with_standard_authority_does_not_reduce_obligations() -> None:
    runbook_module, workflow_state = _workflow_modules()
    state = workflow_state.WorkflowState(
        kind="ready",
        active_issue_id="iss-00301",
        reason_code="assurance_valid",
        artifact_readiness="substantive",
        authority=workflow_state.RunbookAuthority(
            authorized_profile="standard",
            lite_candidate=True,
            obligation_source="authorized_profile",
        ),
    )

    runbook = runbook_module.compile_runbook("issue-execution", state)

    assert runbook.authority.obligation_source == "authorized_profile"
    assert runbook.authority.authorized_profile == "standard"
    assert runbook.authority.lite_candidate is True
    assert runbook.next_action == "execute-approved-plan"
    assert runbook.may_execute_approved_plan is True
    assert runbook.contract_source == "spec-dock/active/issue/plan.md"
    assert runbook.evidence_ledger == "spec-dock/active/issue/report.md"
    joined = "\n".join([*runbook.commands, *runbook.notes, *runbook.stop_conditions]).lower()
    assert "lite procedure" not in joined
    assert "lite-only" not in joined


def test_requirement_sentinels_keep_requirement_scaffold_until_replaced() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    text = (
        "---\n"
        "種別: 要件定義書（Issue）\n"
        '状態: "approved"\n'
        "---\n\n"
        "# Requirement\n\n"
        "## 目的\n"
        "- Concrete objective.\n\n"
        "#### シナリオ SC-XXX:\n"
        "- Concrete scenario text is present, but the generated sentinel remains.\n"
    )

    assert workflow_state.classify_requirement_text(text) == "scaffold"
