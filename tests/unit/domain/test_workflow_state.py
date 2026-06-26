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
    assert runbook.next_action == "execution-ready"
    joined = "\n".join([*runbook.commands, *runbook.notes, *runbook.stop_conditions]).lower()
    assert "lite procedure" not in joined
    assert "lite-only" not in joined


def test_draft_requirement_frontmatter_is_not_substantive() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    readiness = workflow_state.classify_requirement_text(
        "---\n"
        "種別: 要件定義書（Issue）\n"
        '状態: "draft"\n'
        "---\n\n"
        "# Requirement\n\n"
        "## 目的\n"
        "- Concrete requirement text has been written.\n"
    )

    assert readiness == "scaffold"


def test_context_packet_failure_runbook_points_to_packet_repair() -> None:
    runbook_module, workflow_state = _workflow_modules()
    state = workflow_state.WorkflowState(
        kind="blocked",
        active_issue_id="iss-00301",
        reason_code="context-packet-write-failure",
        artifact_readiness="substantive",
        authority=workflow_state.STRICT_LEGACY_AUTHORITY,
    )

    runbook = runbook_module.compile_runbook("issue-execution", state)

    assert runbook.next_action == "context-packet-repair-required"
    joined = "\n".join([*runbook.commands, *runbook.notes, *runbook.stop_conditions])
    assert "context-packets" in joined
    assert ".agent/runbooks" not in joined
